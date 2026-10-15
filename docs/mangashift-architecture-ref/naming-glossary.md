# Naming Glossary - kanoniczne nazewnictwo bytów-identyfikatorów

> Jedno źródło prawdy o nazwach. Każdy standard (`engine-standard`, `service-standard`,
> `model-system`, `model-asset-standard`, `pipeline-step-standard`) linkuje TU zamiast
> powtarzać tabelę. Zmiana nazwy bytu = zmiana w tym jednym pliku.
>
> Zatwierdzone przez usera 2026-07-02. Źródło ustaleń:
> `docs/brainstorms/2026-07-02-nazewnictwo-bytow-ideacja.md` (+ `-brief`).
>
> **Update 2026-07-04 (epik "serwer=wykonawca, front decyduje"):** byt `variant` SKASOWANY.
> `model_id` jest jedynym selektorem modelu (kanon = 6 bytów, nie 7). Silnik nigdy nie wybiera
> `model_id` sam - front wysyła go w request, `<domena>Config.model_id` niesie go wprost na
> config silnika (patrz `create_engine(config)` w `services/<domena>/engines/__init__.py`).
> Źródło: `docs/brainstorms/2026-07-04-epik-serwer-wykonawca-front-decyduje-plan.md`.
>
> **Update 2026-07-05 (FALA 8, kasacja `ModelFactory`):** `runtime/factory.py` i klasa
> `ModelFactory` skasowane. Silnik tworzy `create_engine(config)` z rejestru domeny
> (`services/<domena>/engines/__init__.py`); `RuntimeManager.acquire(spec, *, build, config_overrides)`
> przyjmuje `build` - lambda wołająca `create_engine`. Katalog (`ModelSpec`) nie ma już pól
> `service_path`/`config_path`/`default_config` - silnik zna swoją klasę z rejestru domeny, nie z catalog.

## Reguła nadrzędna (DRY, Hunt & Thomas)

Każdy byt ma JEDNĄ, jednoznaczną, autorytatywną nazwę. To samo słowo nie oznacza dwóch
bytów; ten sam byt nie ma dwóch nazw. Zero aliasów kompatybilnych - pełna, spójna nazwa.

## 6 bytów-identyfikatorów

| # | Byt | Kanon | Co znaczy | Przykład | Konwencja | Właściciel (SSOT) |
|---|-----|-------|-----------|----------|-----------|-------------------|
| 1 | silnik | **`engine_id`** | "co uruchomić" - klucz `_REGISTRY`/`ENGINE_REGISTRY` domeny | `paddle_ocr`, `lama`, `flux_2_klein`, `google`, `gemini`, `elevenbytes` | snake_case | `services/{domain}/engines/__init__.py` |
| 2 | model katalogu | **`model_id`** | wpis w `MODEL_CATALOG`; JEDYNY selektor modelu (WYMAGANY, niesiony na configu domeny od frontu, przekazywany do configu silnika w `create_engine`) | `anime_text_x`, `hi_sam_h`, `lama_anime`, `supertonic-3` | snake_case | `mangashift/models/catalog.py` |
| 3 | bundle na dysku | **`resource_name`** | fizyczny katalog assetów | `paddle-ocr`, `hi-sam`, `comic-text-detector`, `big-lama-anime-manga` | kebab-case | `Resource.name` (models/) |
| 4 | rodzina | **`engine_family`** | gruby kubełek silnika | `ctd`, `lama`, `paddle_ocr` | snake_case (Enum) | `EngineFamily` (models/specs.py) |
| 5 | model dostawcy API | **`provider_model_id`** | który model zawołać u zewn. providera | `gemini-2.5-flash`, `gpt-5.4-mini`, `eleven_flash_v2_5` | slug dostawcy | LLM/TTS engine `constants.py` |
| 6 | etykieta UI | **`label`** | tekst silnika/modelu dla człowieka | `Hi-SAM`, `H mask model`, `Dallin - Storyteller` | wolny tekst | **frontend (tylko)** |

`variant` (dawny byt #4) - **SKASOWANY**. Selekcja modelu wewnątrz silnika 1:N (np.
Hi-SAM `hi_sam_{b,l,h}`) idzie teraz wyłącznie przez `model_id`; engine `constants.py` może
trzymać allow-listę `model_id → cecha` (walidacja/wyprowadzenie cechy), ale to nie jest
osobny byt-selektor - front wybiera `model_id` wprost.

## Relacje (kardynalność)

```text
engine_id ──1:N── model_id ──N:1── resource_name
   │
   ├── engine_family (N:1, gruby kubełek)
   │
   └── (dla LLM/TTS-API) ──1:N── provider_model_id
```

- `anime_text` (engine_id) → `anime_text_x` (model_id, wybrany wprost przez front) → `anime-text` (resource_name)
- `hi_sam` (engine_id) → `hi_sam_{b,l,h}` (3 model_id, wybrane wprost przez front) → `hi-sam` (jeden resource_name)
- `gemini` (engine_id) → `{gemini-2.5-flash, gemini-3-flash-preview}` (provider_model_id)

## Trzy granice (egzekwowane)

1. **`engine_id` NIE wchodzi do `models/`.** Katalog (`ModelSpec`) zna `model_id`/`resource_name`/`engine_family` -
   NIE zna `engine_id` ani klasy silnika (to żyje w rejestrze domeny, `services/{domain}/engines/__init__.py`).
   Słowo "engine" w `models/` = `DownloadEngine` (downloader HF), inny byt. `engine_id` żyje w services/pipeline/api/front.
2. **`engine_id` ≠ `model_id`.** Jeden `engine_id` hostuje N `model_id` (wybór robi front, nie silnik). Ilustruj
   standardy na `hi_sam`/`anime_text` (1:N), NIGDY na `magi_v3` (degenerat 1:1 - ukrywa rozłączność bytów).
3. **`label` nie żyje w backendzie.** Backend zna klucze (`engine_id`/`model_id`), nie teksty UI. Etykiety trzyma frontend.

## Byty pokrewne - NIE mylić z powyższymi

- **`description`** (models/catalog) - techniczny opis modelu do CLI/logów (`"RT-DETR v2 - Fast..."`).
  Osobny byt od `label` (UI, krótki, front). Zostaje w catalog.
- **`label` kroku pipeline** (`STEP_REGISTRY` → OpenAPI → front, np. `Detection`, `OCR`) - etykieta
  KROKU, nie silnika. Osobny byt, poza tym słownikiem.
- **module_path/service_class/config_class** (rejestr domeny, `services/{domain}/engines/__init__.py`) -
  import-path do klasy silnika + jego configu. Żyją w rejestrze domeny, NIE w katalogu (`models/`) -
  katalog nie zna klasy silnika, tylko `model_id`/`resource_name`/`engine_family`.

## Anty-nazwy (co znika - nie używać w nowym kodzie)

| Stara nazwa | Znaczyła | → Kanon |
|-------------|----------|---------|
| `engine` / `engine_name` / `_ENGINE` / `provider` (dla silnika) / `ocr_model` | silnik | `engine_id` |
| `MODEL_ID` (gdy == silnik) | silnik | `engine_id` |
| `MODEL_RESOURCE` | bundle | `resource_name` (kebab wszędzie) |
| `variant` / `model_variant` / `model_shortcut` / `DEFAULT_VARIANT` | selektor modelu wewnątrz silnika | `model_id` (byt skasowany, patrz update 2026-07-04) |
| `model_id` w konfigu katalogu | decyzja wyboru zamiast cechy modelu | `ModelSpec` nie ma pola konfiguracyjnego z domyślnymi parametrami silnika - `model_id` żyje na configu domeny (niesiony od frontu), przekazywany do configu silnika w `create_engine` |
| `model_name` (worek: raz model_id, raz engine_id, raz provider_model_id) | zależnie | właściwy byt |
| `default_model` / `DEFAULT_MODEL` | model API | `provider_model_id` |
| `ModelFamily` | rodzina silnika | `EngineFamily` (`models/specs.py`) |
