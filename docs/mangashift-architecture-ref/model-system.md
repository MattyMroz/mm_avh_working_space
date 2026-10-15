# 🧩 Model System - Architektura i Przewodnik

> **Moduł:** `mangashift/models/`
> **Status:** ✅ Produkcyjny. Liczba modeli = `len(MODEL_CATALOG)` - patrz katalog, nie utrwalamy jej w dokumencie.
> **Nazewnictwo bytów** (`model_id`, `resource_name`, `engine_family`): [naming-glossary.md](naming-glossary.md). `variant` jest bytem skasowanym (epik "serwer=wykonawca, front decyduje", 2026-07-04) - `model_id` jedynym selektorem modelu.
> **FALA 8 (2026-07-05):** `ModelFactory` skasowany. `ModelSpec` nie ma pól `service_path`/`config_path`/`default_config` - klasa silnika żyje w rejestrze domeny (`services/<domena>/engines/__init__.py`), nie w katalogu.

---

## 📖 Spis treści

- [Przegląd](#-przegląd)
- [Architektura](#-architektura)
- [Jak dodać nowy model](#-jak-dodać-nowy-model)
- [Shared Resources](#-shared-resources)
- [CLI - model_manager](#-cli--model_manager)
- [API - użycie z kodu](#-api--użycie-z-kodu)
- [Obsługiwane formaty wag](#-obsługiwane-formaty-wag)
- [Tiery i VRAM](#-tiery-i-vram)
- [Pliki referencyjne](#-pliki-referencyjne)

---

## 🔭 Przegląd

Model System to **portable, self-contained** moduł odpowiedzialny za:

1. **Katalog** - centralna definicja wszystkich modeli (`MODEL_CATALOG`)
2. **Download** - pobieranie z HuggingFace Hub z progress barem i retry
3. **Integrity** - weryfikacja SHA-256 po pobraniu
4. **Resolution** - lokalne resolve ścieżek do wag
5. **Registry** - high-level API: `AssetRegistry.ensure()`, `AssetRegistry.preflight()`, `find_model_spec()`

Cały moduł jest **przenośny** - zero zależności od reszty projektu (poza `utils.logger` i `utils.rich_console`). Testy żyją wewnątrz modułu: `mangashift/models/tests/`.

---

## 🏗️ Architektura

```
mangashift/models/
├── __init__.py          # Public API - re-eksportuje wszystko (patrz __all__)
├── catalog.py           # MODEL_CATALOG - dict[model_id, ModelSpec], find_model_spec()
├── specs.py             # ModelSpec, EngineFamily, ModelProfile, ModelSizeClass, RuntimeKind, ExecutionTarget
├── assets.py            # AssetRegistry - class-based facade: ensure(), ensure_async(), preflight()
├── resolver.py          # ensure_model()/ensure_model_asset() - download + verify + resolve po model_id
├── downloader.py         # download_model() - async one-shot helper na huggingface_hub.snapshot_download
├── llama_runtime/       # LlamaServerManager, LlamaClient - GGUF/llama-server subprocess runtime
├── core/
│   ├── config.py        # HubConfig - konfiguracja repo i ścieżek
│   ├── engine.py        # DownloadEngine - download single/snapshot
│   ├── types.py         # Resource, IntegrityResult (frozen dataclasses)
│   ├── callbacks.py     # DownloadCallback protocol
│   ├── integrity.py     # check_integrity() - SHA-256 verification
│   └── errors.py        # ModelError, DownloadError, HashMismatchError
└── tests/               # pytest, relative imports
```

**Flow:**
```
AssetRegistry().ensure("comic_text_bubble_detector")
  → catalog.find_model_spec()  # resolve ModelSpec
  → resolver.ensure_model()/ensure_model_asset()
    → core.engine.DownloadEngine.get_path()          # Check local
    → core.engine.DownloadEngine.download_resource()  # Download if missing
    → core.integrity.check_integrity()                # Verify SHA-256
    → return Path
```

---

## 🚀 Jak dodać nowy model

### Krok 1 - Przygotuj wagi

1. Wytrenuj / pobierz model
2. Skonwertuj do obsługiwanego formatu (preferowany: `.safetensors`)
3. Zuploaduj do HuggingFace Hub repo `MattyMroz/MangaShift`:
   - Ścieżka: `models/<resource-name>/model.safetensors`

### Krok 2 - Zbierz hash

```bash
# Opcja A: skrypt CLI
python scripts/model_manager.py hash path/to/model.safetensors

# Opcja B: zbierz hashe dla wszystkich modeli w external/
python scripts/model_manager.py collect-hashes
# → generuje external/model_hashes.json
```

### Krok 3 - Dodaj `EngineFamily` (jeśli nowa rodzina)

W [mangashift/models/specs.py](../mangashift/models/specs.py):

```python
class EngineFamily(Enum):
    MY_MODEL = "my_model_family"

# Dodaj mapping nazwy metody serwisu:
_ENGINE_FAMILY_METHODS = {
    # ...existing...
    EngineFamily.MY_MODEL: "detect",
}
```

### Krok 4 - Dodaj wpis do katalogu

W [mangashift/models/catalog.py](../mangashift/models/catalog.py):

```python
"my_model": ModelSpec(
    model_id="my_model",
    engine_family=EngineFamily.MY_MODEL,
    size_class=ModelSizeClass.SMALL,
    peak_vram_mb=1500,
    description="My Model - short description of what it does",
    resource=Resource(
        name="my-model-resource",
        sha256="abc123def456...",
        required_files=("model.safetensors",),
        size_bytes=1_500_000_000,
    ),
),
```

| Pole | Opis |
|------|------|
| `model_id` | Klucz katalogu = wpis `MODEL_CATALOG`, snake_case (np. `"anime_text_x"`, `"hi_sam_h"`). To NIE jest `engine_id` - jeden silnik może mieć wiele `model_id`. |
| `engine_family` | Enum `EngineFamily` - rodzina modelu i domyślna metoda serwisu (`_ENGINE_FAMILY_METHODS`) |
| `size_class` | `TINY` / `SMALL` / `MEDIUM` / `LARGE` - informacyjna klasa rozmiaru |
| `peak_vram_mb` | Maksymalne zużycie VRAM w MB |
| `profile` | `APP` / `LAB` - czy model jest w katalogu aplikacji, czy tylko w eksperymentach |
| `description` | Techniczny opis modelu (CLI `list --details`, logi). Osobny byt od UI `label` (ten żyje we froncie). |
| `resource` | `Resource` - `name` (= `resource_name`, kebab-case), hash, pliki, rozmiar |

`ModelSpec` NIE zna klasy silnika ani jego configu (brak `service_path`/`config_path`/
`default_config`) - to żyje w rejestrze domeny (`services/<domena>/engines/__init__.py`,
`_REGISTRY`/`ENGINE_REGISTRY`), nie w katalogu. Katalog odpowiada za `model_id`,
`engine_family`, `resource` (assety/hash) i klasy rozmiaru/VRAM - nie za "gdzie jest kod silnika".

### Krok 5 - Stwórz Service + Config, dopisz do rejestru domeny

```
mangashift/services/detection/engines/my_model/
├── __init__.py
├── service.py    # class MyService - implementuje metodę z EngineFamily
└── config.py     # class MyConfig - parametry konfiguracyjne
```

Dopisz `my_model` do `_REGISTRY`/`ENGINE_REGISTRY` w `services/detection/engines/__init__.py`
(module path, service class, config class) - to jedyne miejsce, skąd `create_engine(config)`
wie, jak zbudować silnik. Katalog nie bierze w tym udziału.

### Krok 6 - Zwaliduj

```bash
# Sprawdź czy catalog entry jest poprawny
python scripts/model_manager.py validate-catalog

# Pobierz i zweryfikuj
python scripts/model_manager.py download my-model-resource --type models --progress

# Sprawdź integralność na dysku
python scripts/model_manager.py verify my_model
```

### Krok 7 - Test programowo

```python
from mangashift.models import AssetRegistry, find_model_spec

spec = find_model_spec("my_model")
assert spec is not None

path = AssetRegistry().ensure("my_model")  # auto-download + verify
print(f"Model ready at: {path}")
```

---

## 🔗 Shared Resources

Wiele modeli może korzystać z **tych samych wag**. Schemat:

```python
# Definicja shared resource (raz)
_SHARED_RESOURCE = Resource(
    name="shared-weights",
    sha256="...",
    required_files=("model.safetensors", "config.json"),
    size_bytes=750_000_000,
)

# Użycie w wielu modelach
"model_a": ModelSpec(..., resource=_SHARED_RESOURCE),
"model_b": ModelSpec(..., resource=_SHARED_RESOURCE),
```

**Aktualne shared resources:**

| Resource | Modele | Uwagi |
|----------|--------|-------|
| `hi-sam` | `sam_tss_b_hiertext`, `sam_tss_l_hiertext`, `sam_tss_h_hiertext` | Stroke-only B/L/H, per-model PT + ONNX layout |

---

## 🛠️ CLI - model_manager

Skrypt: [scripts/model_manager.py](../scripts/model_manager.py)

### Przeglądanie

```bash
# Lista wszystkich zasobów na dysku
python scripts/model_manager.py list [--type models|code|all] [--details]

# Skanuj external/ i pokaż co jest dostępne
python scripts/model_manager.py scan

# Pokaż rozmiary na dysku
python scripts/model_manager.py storage

# Pokaż ścieżkę do zasobu
python scripts/model_manager.py path <resource_name> [--type models]
```

### Pobieranie i zarządzanie

```bash
# Pobierz pojedynczy model
python scripts/model_manager.py download <resource_name> --type models [--progress]

# Pobierz wiele modeli (opcjonalnie równolegle)
python scripts/model_manager.py download-multiple <name1> <name2> --type models [--parallel]

# Usuń model z dysku
python scripts/model_manager.py remove <resource_name> [--type models|code]

# Upload do HF
python scripts/model_manager.py upload <resource_name> --type models [-m "commit message"]
```

### Hashing i walidacja

```bash
# Hash pojedynczego pliku
python scripts/model_manager.py hash <file_path>

# Zbierz hashe wszystkich modeli → external/model_hashes.json
python scripts/model_manager.py collect-hashes

# Zweryfikuj integralność na dysku (SHA-256)
python scripts/model_manager.py verify <model_id>

# Waliduj cały katalog (import paths, hashe, shared resources)
python scripts/model_manager.py validate-catalog
```

### Preflight check

```bash
# Sprawdź dostępność modeli (lokalnie/wymaga pobrania)
python scripts/model_manager.py preflight ctbd mts magi_v3
```

---

## 💻 API - użycie z kodu

### High-level (preferowane)

```python
from mangashift.models import AssetRegistry, find_model_spec

# Pobierz model (auto-download jeśli brakuje + verify)
path = AssetRegistry().ensure("comic_text_bubble_detector")

# Sprawdź spec
spec = find_model_spec("comic_text_bubble_detector")
print(spec.size_class, spec.peak_vram_mb)

# Preflight - sprawdź wiele modeli naraz
results = AssetRegistry().preflight(["ctbd", "mts", "magi_v3"])
for model_id, result in results.items():
    print(f"{model_id}: {result.status}")
```

### Custom config

```python
from mangashift.models import AssetRegistry, HubConfig, configure_engine

# Inne repo lub ścieżka
config = HubConfig(
    repo_id="my-org/my-models",
    base_dir=Path("/custom/path"),
)
configure_engine(config)

path = AssetRegistry().ensure("my_model")
```

### Catalog queries

```python
from mangashift.models import (
    MODEL_CATALOG,
    get_models_by_size_class,
    get_shared_resources,
    list_all_models,
    ModelSizeClass,
)

# Wszystkie modele TINY
tiny_models = get_models_by_size_class(ModelSizeClass.TINY)

# Shared resources
shared = get_shared_resources()

# Lista z opisami
for model_id, spec in list_all_models():
    print(f"{model_id}: {spec.description} ({spec.peak_vram_mb} MB)")
```

---

## 📦 Obsługiwane formaty wag

W kolejności priorytetu (engine szuka pierwszego dopasowania):

| Format | Rozszerzenie | Uwagi |
|--------|-------------|-------|
| SafeTensors | `.safetensors` | **Preferowany** - brak ryzyka pickle |
| PyTorch | `.pt` | Standard PyTorch checkpoint |
| PyTorch (legacy) | `.pth` | Starszy format |
| ONNX | `.onnx` | Cross-framework |
| GGUF | `.gguf` | Quantized models (llama.cpp) |
| Binary | `.bin` | Generic binary weights |
| Checkpoint | `.ckpt` | Legacy checkpoint format |
| DLL | `.dll` | OneOCR Windows native |

---

## 📊 Klasy rozmiaru i VRAM

> V3 policy: klasy rozmiaru są metadanymi informacyjnymi. Nie powinny sterować ukrytym auto-eviction, retry ani automatycznym obniżaniem jakości. Jeśli brakuje VRAM albo backendu, runtime ma zwrócić jawny błąd z informacją, którego profilu lub modelu brakuje. Pełna polityka: [runtime-backends.md](runtime-backends.md).

| Size class | Ilość | VRAM range | Zachowanie |
|------|-------|------------|------------|
| **TINY** | 12 | < 1 GB | Informacyjne: lekki model |
| **SMALL** | 8 | 1-3 GB | Informacyjne: typowe wymagania |
| **MEDIUM** | 5 | 3-6 GB | Informacyjne: wymaga mocniejszego GPU |
| **LARGE** | 8 | 6 GB+ | Informacyjne: wymaga high-end GPU albo alternatywnego backendu |

---

## 📁 Pliki referencyjne

| Plik | Rola |
|------|------|
| [mangashift/models/catalog.py](../mangashift/models/catalog.py) | MODEL_CATALOG - `dict[model_id, ModelSpec]`, `find_model_spec()` |
| [mangashift/models/specs.py](../mangashift/models/specs.py) | ModelSpec, EngineFamily, tiery, runtime, `ExecutionTarget` |
| [mangashift/models/assets.py](../mangashift/models/assets.py) | `AssetRegistry` - `ensure()`, `ensure_async()`, `preflight()` |
| [mangashift/models/resolver.py](../mangashift/models/resolver.py) | `ensure_model()`/`ensure_model_asset()` - download + verify + resolve po `model_id` |
| [mangashift/models/downloader.py](../mangashift/models/downloader.py) | `download_model()` - async snapshot_download wrapper |
| [mangashift/models/llama_runtime/](../mangashift/models/llama_runtime/) | `LlamaServerManager`, `LlamaClient` - GGUF/llama-server subprocess runtime |
| [mangashift/models/core/engine.py](../mangashift/models/core/engine.py) | DownloadEngine, progress bar |
| [mangashift/models/core/types.py](../mangashift/models/core/types.py) | Resource, IntegrityResult |
| [mangashift/models/core/config.py](../mangashift/models/core/config.py) | HubConfig |
| [scripts/model_manager.py](../scripts/model_manager.py) | CLI management |
