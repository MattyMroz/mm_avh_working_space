# Engine Standard v4

Standard dla concrete engines i API providers w `mangashift/services/*/engines/`. Każdy wpis w `_REGISTRY` ma być klonowalnym package, niezależnie od tego, czy runtime używa ONNX Runtime, PyTorch, native DLL, GGUF/llama.cpp, ComfyUI czy zewnętrznego API.

> **v5 (2026-07-05, FALA 8):** `ModelFactory` (`runtime/factory.py`) skasowany. Silnik tworzy
> `create_engine(config)` z rejestru domeny (`services/<domena>/engines/__init__.py`);
> `RuntimeManager.acquire(spec, *, build, config_overrides)` przyjmuje `build` - lambdę
> wołającą `create_engine`. Katalog (`ModelSpec`) nie ma pól `service_path`/`config_path`/
> `default_config` - silnik zna swoją klasę z rejestru domeny, nie z catalog. `model_id`
> przychodzi na configu domeny (od frontu) i idzie wprost do configu silnika w `create_engine`.
>
> **v4 (2026-07-04):** epik "serwer=wykonawca, front decyduje" - `variant` skasowany jako
> byt (kanon 6 bytów, nie 7); `model_id` jedynym selektorem modelu, WYMAGANY na configu
> silnika. Silnik nigdy sam nie wybiera `engine_id`/`model_id` - front decyduje, serwis
> waliduje i wykonuje. Źródło: `docs/brainstorms/2026-07-04-epik-serwer-wykonawca-front-decyduje-plan.md`.
>
> **v3 (2026-07-02):** ujednolicone nazewnictwo bytów-identyfikatorów. Kanon: `engine_id`
> zastępuje wcześniejsze `engine_name`/`MODEL_ID`(dla silnika); wprowadzone `resource_name`,
> `variant`, `provider_model_id`. Źródło: `docs/brainstorms/2026-07-02-nazewnictwo-bytow-ideacja.md`.

## Słownik bytów

Nazewnictwo identyfikatorów (`engine_id`, `model_id`, `resource_name`,
`engine_family`, `provider_model_id`, `label`) i granice - patrz **[naming-glossary.md](naming-glossary.md)**.
Ten standard egzekwuje trzy granice stamtąd: `engine_id` nie wchodzi do `models/`;
`engine_id` ≠ `model_id` (ilustruj na `hi_sam` 1:N, nie `magi_v3`); `label` tylko we froncie.
`variant` jest bytem skasowanym (epik "serwer=wykonawca, front decyduje") - nie używać w nowym kodzie.

## Cel

- Każdy engine/provider ma taki sam przewidywalny kształt folderu.
- Runtime-specific kod jest oddzielony od lifecycle/service facade.
- Ciężkie importy są lazy i nie spowalniają importu domeny.
- Fizyczne pliki modeli są wyłącznie w catalog/resolver boundary.
- Publiczne metody i funkcje engine package są typowane i udokumentowane.

## Drzewo Engine Package

Docelowy shape (`{engine_id}` = klucz z `_REGISTRY`, np. `hi_sam`, `paddle_ocr`):

```text
mangashift/services/{domain}/engines/{engine_id}/
├── __init__.py          # publiczny import surface engine'a, lazy exports
├── constants.py         # stałe algorytmiczne silnika (bez wyboru modelu - model_id wstrzykuje factory), bez fizycznych asset filenames
├── config.py            # config runtime engine'a/provider'a
├── service.py           # lifecycle, orkiestracja, mapowanie resultów
├── types.py             # typy lokalne engine'a/provider'a
├── preprocessing.py     # optional: preprocessing prywatny dla engine'a
├── postprocessing.py    # optional: postprocessing prywatny dla engine'a
├── onnx_backend.py      # required, gdy engine ma ONNX runtime
├── torch_backend.py     # required, gdy engine ma nietrywialny PyTorch runtime
├── gguf_backend.py      # required, gdy engine odpala GGUF/llama.cpp runtime
├── native_backend.py    # required, gdy engine ładuje DLL/native runtime
├── api_backend.py       # optional, gdy provider ma osobną warstwę klienta API
└── README.md            # optional: tylko runtime gotchas
```

Nazwa folderu engine'a = jego `engine_id`. Nie używaj tu `resource_name` (kebab) ani `model_id` -
folder to package Pythona (snake_case), tożsamy z kluczem `_REGISTRY`.

Vendor/internal subtrees są dozwolone, jeśli są całkowicie prywatne dla engine'a:

```text
engines/{engine_id}/
├── models/              # vendored model architecture/private code
├── utils/               # helpers tylko dla tego engine'a
└── assets/              # małe niemodelowe pliki pomocnicze, jeśli naprawdę potrzebne
```

Nie twórz zależności typu `engine_a.service -> engine_b.preprocessing`. Jeśli helper jest potrzebny w dwóch engine'ach tej samej domeny, wybierz jawnie jedno z dwóch:

- przenieś helper do domenowego `utils/`, jeśli engine'i są przenoszone razem z domeną,
- skopiuj mały helper lokalnie, jeśli engine package ma być przenośny samodzielnie.

## Role Plików

`__init__.py`:
- wystawia `__all__`,
- re-exportuje service/config/types,
- używa lazy exports dla backend classes,
- nie importuje `torch_backend`, `onnx_backend`, `gguf_backend`, `native_backend` na top-level.

`constants.py`:
- trzyma `DEFAULT_BACKEND`, `SUPPORTED_BACKENDS`, rozmiary wejść, thresholdy, label maps, prompt constants,
- KASACJA wzorca `variant → model_id`: engine nie mapuje wariantów na `model_id` - `model_id` przychodzi z configu domeny (od frontu) przez `create_engine(config)` w rejestrze domeny, silnik go tylko przyjmuje,
- trzyma `provider_model_id` catalog (`DEFAULT_PROVIDER_MODEL_ID`, `SUPPORTED_PROVIDER_MODEL_IDS`) dla API providerów,
- publiczne stałe mają `Final[...]` i krótki docstring,
- nie trzyma nazw plików modeli, hashy, HF paths, `resource_name` fizycznych ścieżek ani `external/models`.

`config.py`:
- opisuje runtime choices konkretnego engine'a,
- trzyma pole `model_id: str` (WYMAGANE, `field(kw_only=True)`, bez defaultu) - jedyny selektor modelu; KASACJA pola `variant` (żaden engine nie ma już `variant`/`model_variant`/`model_shortcut`),
- `model_id` przekazuje `create_engine(config)` z configu domeny (`config.model_id`, od frontu), engine go nie wyprowadza z niczego innego,
- waliduje zakresy thresholdów i backendy,
- `__post_init__()` ma docstring, jeśli robi walidację,
- nie odpala ciężkich modeli,
- nie zna fizycznych asset filenames.

`service.py`:
- implementuje Protocol oczekiwany przez domain facade,
- ma sync lifecycle engine'a: `initialize()`, `cleanup()` i publiczną metodę pracy,
- dla lokalnych runtime mapuje wynik backendu na domenowy lub engine-local result,
- importuje backend classes lazy w lifecycle/helperach,
- nie zawiera dużej logiki ORT/Torch/native, jeśli istnieje backend file.

`types.py`:
- trzyma engine-local result/value objects,
- result ma `processing_time_ms` i opcjonalnie `init_time_ms`,
- gdy result nosi identyfikator, używa właściwego bytu ze słownika (`model_id` dla wpisu katalogu, `provider_model_id` dla modelu API) - NIE generycznego `model_name`,
- property typu `is_success` mają docstring i return type,
- nie dubluje domenowych DTO, jeśli domenowe `types.py` wystarcza.

`preprocessing.py` i `postprocessing.py`:
- trzymają małe, testowalne funkcje specyficzne dla engine'a,
- nie importują innych engine'ów,
- mają type hints i docstringi dla publicznych funkcji.

`onnx_backend.py`:
- tworzy ORT sessions,
- rozwiązuje pliki przez catalog/resolver (po `model_id` albo `resource_name`, jawnie),
- ukrywa szczegóły providerów ORT,
- nie zawiera domain facade logic.

`torch_backend.py`:
- ładuje PyTorch model i wykonuje inference,
- trzyma PyTorch imports lazy, jeśli import na top-level wymaga ciężkiego runtime,
- nie robi fallbacków API-level.

`gguf_backend.py`:
- zarządza llama.cpp/llama-server runtime,
- rozdziela start/stop procesu od pojedynczego requestu,
- opisuje porty, timeouty i cleanup w docstringach albo README runtime gotchas.

`native_backend.py`:
- ładuje DLL/native library,
- trzyma całą granicę `ctypes`/native calls w jednym miejscu,
- wystawia mały, typowany interfejs dla `service.py`.

`api_backend.py`:
- trzyma klienta zewnętrznego API,
- używa `provider_model_id` (nie `model_name`) jako nazwy modelu wołanego u dostawcy,
- nie zna `engine_id` domeny nadrzędnej (to wie serwis).

`README.md`:
- jest tylko dla realnych gotchas: skąd DLL, jaki serwer, jakie ograniczenie platformy,
- nie kopiuje tego standardu,
- nie zastępuje testów.

## Registry Contract

Każda domena ma lazy registry w `services/{domain}/engines/__init__.py`. **To jest jedyne
źródło prawdy o zestawie `engine_id` domeny** - Literale, frozensety i typy w pipeline/API
mają być DERIVED z tego rejestru (import), nigdy przepisywane ręcznie.

```python
from __future__ import annotations

from typing import Final

# Klucz = engine_id. To jest SSOT zestawu silników domeny.
_REGISTRY: Final[dict[str, tuple[str, str, str | None]]] = {
    "hi_sam": (
        "mangashift.services.detection.engines.hi_sam",
        "HiSamService",
        "HiSamConfig",
    ),
}
```

Reguły:

- klucz rejestru to `engine_id` (snake_case), nie label i nie `resource_name`,
- registry entry zawsze ma 3 elementy (trzeci = config class lub `None`),
- module path wskazuje package engine'a/provider'a, nie losowy flat file,
- factory importuje package dopiero przy tworzeniu engine'a,
- nie wolno importować runtime backendów na import path registry,
- zestaw `engine_id` NIE jest duplikowany jako osobny `Literal`/`frozenset` w pipeline -
  pipeline waliduje przez import z tego rejestru (`get_args`/klucze `_REGISTRY`),
- rejestr = źródło prawdy o DOSTĘPNYCH silnikach (walidacja + OpenAPI/front, przez
  `available_engine_ids()`); WYBÓR aktywnego `engine_id` należy do frontu - silnik/serwis
  nigdy nie zgaduje, tylko sprawdza żądany `engine_id` wobec tego rejestru.

## Backend Contract

Production local vision engines mają preferować ONNX, jeśli catalog ma asset ONNX. Dla takich engine'ów package powinien mieć `onnx_backend.py` i `torch_backend.py`, chyba że engine ma jawny wyjątek single-runtime.

Jawne wyjątki single-runtime:

- OneOCR: native DLL/runtime,
- Flux Klein: lab-only ComfyUI/Torch,
- API providers: zewnętrzne API, bez lokalnego model backendu.

Single-runtime nie znaczy „bez standardu”. Nadal obowiązuje package clone, config, service, types, constants i testy.

## Async Relationship

Engine/provider package może być sync albo async zależnie od runtime:

- local GPU/CPU engines zwykle są sync,
- domain facade owija je przez `asyncio.to_thread()`,
- API providers mogą być async-native,
- nie odpalaj `asyncio.run()` wewnątrz engine'a,
- nie twórz fire-and-forget tasks bez właściciela i cleanupu.

REST API podpina się do domain facade, nie bezpośrednio do engine'a.

## Typowanie i docstringi

W engine/provider package obowiązuje:

- każdy publiczny moduł ma `from __future__ import annotations`,
- każda publiczna funkcja/metoda ma type hints i return type,
- każda publiczna funkcja/metoda ma docstring,
- `__enter__`, `__exit__`, `__aenter__`, `__aexit__` w kodzie usługowym też mają docstring,
- `__post_init__` ma docstring, jeśli waliduje config,
- publiczne dataclass fields są typowane,
- puste kolekcje, `None` start values i cache fields mają jawne adnotacje,
- publiczne stałe mają `Final[...]` i docstring.

Minimalny styl:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

DEFAULT_BACKEND: Final[str] = "onnx"
"""Default runtime backend for production inference."""


@dataclass(slots=True)
class ExampleConfig:
    """Runtime configuration for Example engine."""

    backend: str = DEFAULT_BACKEND

    def __post_init__(self) -> None:
        """Validate backend selection."""
```

## Model Asset Boundary

Engine package może przechowywać identyfikatory semantyczne, ale nie fizyczne pliki i nie
wybór modelu. `model_id` jest zawsze WYMAGANYM polem configu, przekazywanym przez
`create_engine(config)` (rejestr domeny, `services/<domena>/engines/__init__.py`) z configu
domeny (`config.model_id`, wybrany przez front) - engine nigdy sam nie wybiera ani nie
wyprowadza `model_id` z innego pola. `variant` jako byt jest skasowany (epik "serwer=wykonawca,
front decyduje"): `model_id` jest jedynym selektorem.

Dwa wzorce zależnie od kardynalności engine → model_id (**wzorzec B**, tak wyglądają po epiku
lama/spandrel/hi_sam):

**Engine 1:N** (hostuje wiele `model_id`, np. Hi-SAM `hi_sam_b/l/h`) - allow-list `model_id → cecha`:

```python
# constants.py - model_id → cecha silnika (allow-list, NIE wybór)
HI_SAM_MODELS: Final[dict[str, ModelType]] = {
    "hi_sam_b": "vit_b",
    "hi_sam_l": "vit_l",
    "hi_sam_h": "vit_h",
}
"""Catalog model id → ViT backbone. The engine derives the backbone from the
model id so the two can never disagree; also the accepted-id allow-list."""
```

```python
# config.py - model_id wymagany, bez defaultu, wstrzyknięty przez factory
@dataclass(slots=True)
class HiSamConfig:
    model_id: str = field(kw_only=True)

    def __post_init__(self) -> None:
        if not self.model_id:
            raise DetectionConfigError("model_id is required")
        if self.model_id not in HI_SAM_MODELS:
            raise DetectionConfigError(f"Unknown Hi-SAM model_id: {self.model_id!r}")
```

**Engine 1:1** (jeden `model_id`, np. `comic_text_detector`, `anime_text`) - pojedynczy `RESOURCE_NAME`:

```python
# constants.py - jeden model, jeden bundle
RESOURCE_NAME: Final[str] = "anime-text"
"""Physical resource name resolved by ``ensure_model_asset``."""
```

```python
# config.py - model_id nadal wymagany (spójne z 1:N), tylko jeden poprawny
model_id: str = field(kw_only=True)
```

- `model_id` to jedyny selektor modelu - zero pól `variant`/`model_variant`/`model_shortcut`
  w żadnym engine.
- Engine 1:1 trzyma płaski `RESOURCE_NAME` (nie zwija się do słownika z jednym wpisem).
  Engine 1:N trzyma allow-list `model_id → cecha` (np. backbone) TYLKO jako walidację i
  wyprowadzenie cechy - nie jako mapowanie wyboru (wybór robi front/request).
- NIGDY nie zwijaj bytów do pojedynczego `MODEL_ID` udającego engine_id.
- API provider trzyma tu `provider_model_id` catalog (nie `model_id` katalogu lokalnego):

```python
DEFAULT_PROVIDER_MODEL_ID: Final[str] = "gemini-2.5-flash"
SUPPORTED_PROVIDER_MODEL_IDS: Final[tuple[str, ...]] = ("gemini-2.5-flash", "gemini-3-flash-preview")
```

Zakazane:

- `MODEL_FILENAME`, `ONNX_FILENAME`, `PT_FILENAME`, `PT_ASSET_PATH`, `ONNX_ASSET_PATH`,
- hash pliku modelu,
- ścieżka Hugging Face,
- ścieżka `external/models/...`,
- fizyczny `resource_name` używany jako ścieżka (resource rozwiązuje resolver po `model_id`).

Pliki modeli pobieraj przez `mangashift.models.resolver.ensure_model_asset()` i dane z `mangashift/models/catalog.py`. Selektorem jest `model_id` (albo jawnie `resource_name`, gdy engine celowo adresuje bundle) - resolver mapuje to na fizyczny katalog.

## Exceptions i cleanup

- Backend łapie konkretne wyjątki runtime, jeśli może dodać sensowny kontekst.
- Broad `except Exception` jest dozwolone tylko na facade/provider boundary z komentarzem, np. cleanup wielu providerów.
- Cleanup powinien być idempotentny.
- Lazy init powinien być idempotentny: drugie `initialize()` nie ładuje modelu od nowa.
- Fallbacki muszą być jawne w configu albo catalogu, nie ukryte w losowym `except`.

## Testy Wymagane Dla Engine

Minimum:

- package shape invariant,
- lazy runtime import invariant,
- config boundary tests (w tym walidacja `model_id` wobec allow-listy silnika, gdy engine jest 1:N),
- asset boundary invariant,
- smoke test factory/registry,
- backend-specific test z mockami, jeśli realny runtime wymaga GPU/modelu,
- parity test dla PT/ONNX, gdy oba backendy mają być production-ready.

Aktualne guardraile:

- `tests/services/test_engine_structure_invariants.py`,
- `tests/services/test_engine_configs.py`,
- `tests/services/test_service_contract_invariants.py`,
- `tests/models/test_catalog_service_contract.py`.

## Definition of Done

Engine/provider jest zgodny ze standardem, gdy:

1. Jest wpisany w `_REGISTRY` pod kluczem = `engine_id` (package path).
2. Ma `__init__.py`, `constants.py`, `config.py`, `service.py`, `types.py`.
3. Backend-specific runtime siedzi w `*_backend.py`.
4. Identyfikatory używają nazw ze słownika (`engine_id`/`model_id`/`resource_name`/`provider_model_id`) - zero `engine_name`/`MODEL_ID`(dla silnika)/`model_name`-worka/`variant` (byt skasowany).
5. Klasa fasady ma sufiks `*Service` (np. `HiSamService`, `PaddleOcrService`) - nigdy `*Engine`, zero aliasów kompatybilnych. `*Engine` w nazwie to tylko `DownloadEngine` (downloader HF w `models/`), inny byt.
6. `config.py` trzyma wymagane pole `model_id: str` (bez defaultu, przekazane przez `create_engine` z configu domeny); engine 1:1 dodatkowo trzyma `RESOURCE_NAME` (płaski), engine 1:N dodatkowo trzyma allow-listę `model_id → cecha` (nie mapę `variant → model_id`).
7. Publiczne metody i funkcje są typowane i mają docstringi.
8. Nie ma fizycznych filenames/path constants w engine code.
9. Import domeny nie ładuje ciężkiego runtime.
10. Targeted tests i service invariant tests przechodzą.
