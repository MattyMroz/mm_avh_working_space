# Service Standard v6

Standard dla domain facades w `mangashift/services/`. Ten dokument opisuje warstwę usługową widoczną dla orchestratora i przyszłego REST API. Concrete engines i API providers mają osobny kontrakt w [docs/engine-standard.md](engine-standard.md), a fizyczne pliki modeli należą do [docs/model-asset-standard.md](model-asset-standard.md).

> **v6 (2026-07-02):** ujednolicone nazewnictwo bytów. Serwis wybiera silnik przez
> `engine_id` (nie `engine`/`provider`/`engine_name`). Słownik i granice: **[naming-glossary.md](naming-glossary.md)**.

## Cel

- Domain service ma być cienką, asynchroniczną fasadą nad engine/provider registry.
- Kod usług nie zna HTTP, FastAPI ani `Request`/`Response`.
- Ciężkie runtime dependency są lazy, czyli importowane dopiero przy tworzeniu lub inicjalizacji engine'u.
- Serwis lokalny/GPU nie blokuje event loop: blokujące wywołania idą przez `asyncio.to_thread()`.
- Publiczny kontrakt jest typowany i udokumentowany: każda publiczna funkcja/metoda ma type hints i docstring.

## Drzewo Domeny

Każda aktywna domena w `mangashift/services/{domain}/` ma mieć taki rdzeń:

```text
mangashift/services/{domain}/
├── __init__.py          # publiczny import surface domeny
├── _portable.py         # deklaracja przenośności i runtime dependency
├── constants.py         # stałe domenowe, bez fizycznych nazw plików modeli
├── config.py            # config fasady domeny
├── errors.py            # wyjątki domenowe
├── protocols.py         # Protocol dla engine/provider używany przez fasadę
├── service.py           # async facade używana przez orchestrator/API
├── types.py             # DTO/result/value objects domeny
└── engines/
    └── __init__.py      # lazy registry concrete engines/providers (klucz = engine_id, SSOT)
```

Dozwolone są foldery i pliki specyficzne dla domeny, jeśli nie stają się ukrytym globalnym shared layerem:

```text
mangashift/services/{domain}/
├── utils/               # helpers prywatne dla tej domeny
├── steps/               # jawne kroki pipeline domeny
├── provider.py          # kontrakt API providerów, gdy Protocol w protocols.py nie wystarcza
├── context.py           # kontekst domeny, np. translation memory
├── glossary.py          # słownik/glossary domeny
├── prompts.py           # prompty domenowe
└── validation.py        # walidacja domenowego outputu
```

Nie dodawaj nowych `mangashift/services/_shared.py` ani cross-domain helperów. Jeśli kod jest wspólny tylko dla jednej domeny, zostaje pod tą domeną. Jeśli jest wspólny systemowo, powinien trafić do jawnej warstwy typu `mangashift/models`, `mangashift/utils` albo osobnego modułu domenowego z testami.

## Role Plików

`__init__.py`:
- re-exportuje publiczne klasy domeny,
- nie importuje ciężkich runtime dependencies,
- nie tworzy engine'ów ani klientów API.

`_portable.py`:
- opisuje, co trzeba zabrać, żeby domena działała poza repo,
- zawiera `ENGINE_DEPS` albo równoważną mapę dependency,
- wymienia optional extras/groups z `pyproject.toml`, gdy domena ich wymaga,
- dokumentuje runtime caveats typu DLL, GGUF server, ComfyUI, CUDA.

`constants.py`:
- trzyma tylko stałe domenowe: limity, tryby, nazwy logiczne, timeouty,
- każda publiczna stała ma `Final[...]` i krótki docstring pod spodem,
- nie trzyma `MODEL_FILENAME`, `ONNX_FILENAME`, hashy, ścieżek HF ani `external/models`.

`config.py`:
- definiuje konfigurację fasady domeny,
- dla lokalnych/GPU domen może używać `@dataclass(slots=True)`,
- dla API/providerów może używać Pydantic settings,
- config domeny PRZYJMUJE wybór silnika od wywołującego (front przez pipeline/API) polem `engine_id`; pole jest WYMAGANE - bez defaultu; szczegóły runtime engine'a należą do `engines/{engine_id}/config.py`,
- pole `engine_id` typowane przez `Literal`/typ DERIVED z `_REGISTRY` domeny - nie przepisywać listy silników ręcznie,
- serwis NIE MA fallbacku `engine_id` - brak wartości przy konstrukcji configu to domenowy `ConfigError` (np. `InpaintingConfigError`, `DetectionConfigError`). (Dependency Rule bez zmian: serwis nie importuje wartości z engine.)

`errors.py`:
- definiuje wyjątki domenowe dziedziczące po bazowym błędzie MangaShift,
- nie mapuje błędów na HTTP status codes,
- nie łapie broad exceptions tylko po to, żeby ukryć realny problem.

`protocols.py`:
- definiuje minimalny kontrakt engine/provider używany przez `service.py`,
- używa `Protocol`, nie wymusza dziedziczenia, jeśli structural typing wystarcza,
- nie importuje concrete engine packages.

`service.py`:
- jest cienką fasadą domeny,
- ma async lifecycle: `initialize()`, `cleanup()`, `__aenter__()`, `__aexit__()`,
- ma jedną lub kilka publicznych metod pracy domeny, np. `detect()`, `recognize()`, `inpaint()`, `upscale()`, `synthesize()`,
- tworzy concrete engine/provider przez lazy registry,
- blokujące lokalne runtime wywołuje przez `asyncio.to_thread()`,
- nie importuje FastAPI/Starlette i nie zna HTTP.

`types.py`:
- trzyma domenowe result/value objects,
- resulty używają jednoznacznych pól `processing_time_ms` i `init_time_ms`,
- property typu `is_success` mają docstring i return type,
- DTO domeny nie są request/response schema dla REST API.

`engines/__init__.py`:
- trzyma `_REGISTRY` - **SSOT zestawu `engine_id` domeny** (klucze = engine_id),
- importuje concrete engine/provider lazy przez `importlib`,
- entries są 3-elementowe: module path, class name, config class name albo `None`,
- nie importuje Torch/ORT/native/GGUF backendów na module import path,
- pipeline/API/front NIE przepisują tej listy - derivują ją (import kluczy, `get_args`, OpenAPI codegen),
- każda domena eksportuje `available_engine_ids() -> tuple[str, ...]` (zwraca klucze `_REGISTRY`) i `create_engine(config) -> Engine`; `create_engine` rzuca domenowy `ConfigError` na pusty/nieznany `engine_id` - bez wyjątku dla LLM (ten sam kontrakt).

## Kontrakt Fasady

Minimalny shape fasady domeny:

```python
from __future__ import annotations

from typing import Self


class DomainService:
    """Async domain facade over lazy concrete engines."""

    __slots__ = ("_engine", "config")

    def __init__(self, config: DomainConfig) -> None:
        """Create service facade without loading heavy runtime dependencies."""

    @property
    def name(self) -> str:
        """Human-readable service or active engine name."""

    @property
    def is_available(self) -> bool:
        """Whether the active engine/provider is ready."""

    async def initialize(self, **kwargs: object) -> None:
        """Create and initialize the concrete engine/provider."""

    async def cleanup(self) -> None:
        """Release engine/provider resources."""

    async def __aenter__(self) -> Self:
        """Initialize the service for async context-manager usage."""

    async def __aexit__(self, *_exc: object) -> None:
        """Clean up the service after async context-manager usage."""
```

Sync context managers i sync methods są dozwolone tylko jako backward compatibility. Nowy kod orchestration/API powinien używać async API.

`config: DomainConfig` jest wymagany - brak `| None = None`. `None` jako sentinel jest
dozwolony wyłącznie w testach/smoke, gdzie test jawnie buduje minimalny config i przekazuje
go do konstruktora; produkcyjny kod (pipeline/API) zawsze przekazuje kompletny config.

## Kto wybiera silnik

Serwer jest **wykonawcą**, nie decydentem. Front (przez pipeline/API request) niesie
`engine_id` + `model_id` + wszystkie parametry decyzyjne. Odpowiedzialności per warstwa:

- **front** - jedyne miejsce z wartościami domyślnymi silnika/modelu/parametrów
  (`frontend/src/features/pipeline/config/default-pipeline-config.ts`),
- **API/pipeline** - waliduje KOMPLETNOŚĆ configu z requestu (422 przy brakującym polu),
  nie dostarcza defaultów,
- **serwis** - waliduje `engine_id`/`model_id` wobec `_REGISTRY` domeny i wykonuje pracę
  (`create_engine(config)`); przy braku/nieznanym `engine_id` rzuca domenowy `ConfigError`.

ZERO defaultów silnika w API, w pipeline, w serwisie ani w engine code. Jeśli config
dotarł do serwisu bez `engine_id`/`model_id`, to fail-loud (`ConfigError`), nie fallback.

## Async i REST API

Serwis jest gotowy do podpięcia pod REST API, gdy spełnia te warunki:

- publiczna fasada ma async `initialize()`, `cleanup()` i async primary method,
- lokalne/GPU/blocking engine calls są odpalane przez `asyncio.to_thread()`,
- service layer nie importuje `fastapi` ani `starlette`,
- błędy pozostają domenowe i mogą być mapowane dopiero w `mangashift/api`,
- config i result objects są jawnie typowane,
- lazy initialization nie ładuje modeli na sam import modułu.

Dla przyszłego FastAPI router powinien wyglądać jak cienka delegacja:

```text
HTTP request
└── router/schema validation
    └── await DomainService.primary_method(...)
        └── domain engine/provider
```

Router nie powinien znać runtime backendu, ścieżek modeli ani detali cleanupu.

## Typowanie i docstringi

Obowiązuje standard Python z `.github/skills/python`:

- `from __future__ import annotations` w każdym module,
- każda publiczna funkcja/metoda ma adnotacje argumentów i return type,
- `-> None` jest jawne, nie pomijane,
- puste kolekcje i wartości startujące jako `None` mają adnotację zmiennej,
- publiczne atrybuty klas/dataclasses są typowane,
- publiczne stałe używają `Final[...]`,
- każda publiczna funkcja/metoda ma Google-style docstring, nawet jeśli jest krótka,
- typów nie powtarzamy w docstringu, bo są w sygnaturze.

Dla nowych i edytowanych plików usługowych preferuj jawne adnotacje zmiennych także wtedy, gdy poprawiają czytelność review:

```python
retries: int = 3
items: list[str] = []
engine: OcrEngine | None = None
```

## Granica Modeli

Nazwy bytów wg [naming-glossary.md](naming-glossary.md). Serwis operuje na identyfikatorach
semantycznych, nie na fizycznych plikach.

Service code może znać:

- `engine_id` - który silnik uruchomić, PRZYJĘTY od wywołującego (wybór z `_REGISTRY`, nie zgadnięty przez serwis),
- `model_id` - który wpis katalogu, WYMAGANY na configu silnika, niesiony na configu domeny (od frontu) i przekazywany do configu silnika przez `create_engine(config)` (rejestr domeny), nie wyprowadzany z żadnego innego pola (`variant` jako byt skasowany),
- backend/runtime mode,
- thresholdy i stałe algorytmiczne.

Service code nie może znać:

- fizycznych nazw plików modeli,
- hashy,
- ścieżek Hugging Face,
- `external/models/...`,
- `MODEL_FILENAME`, `ONNX_FILENAME`, `PT_ASSET_PATH`, `ONNX_ASSET_PATH`,
- fizycznego `resource_name` jako ścieżki (resolver mapuje `model_id` → bundle).

`engine_id` vs `model_id` - nie mylić: front WYBIERA oba i wysyła w request; serwis WALIDUJE
`engine_id` wobec `_REGISTRY` i wykonuje, `model_id` idzie wprost na config silnika (wymagane
pole, patrz [engine-standard.md](engine-standard.md)). Jeden `engine_id` może obsłużyć wiele
`model_id` (Hi-SAM: `hi_sam` → `hi_sam_{b,l,h}`, selektor = `model_id` z requestu, nie z serwisu).
Serwis nie zakłada `engine_id == model_id` (to prawda tylko dla degeneratów jak `magi_v3` - nie wzorzec).

Fizyczne assety są w `mangashift/models/catalog.py` i rozwiązywane przez resolver.

## Testy Wymagane Dla Usług

Minimalne guardraile:

- shape domen: `tests/services/test_service_structure_invariants.py`,
- shape engine/provider packages: `tests/services/test_engine_structure_invariants.py`,
- jakość publicznego kontraktu i REST readiness: `tests/services/test_service_contract_invariants.py`,
- config boundary tests: `tests/services/test_engine_configs.py`,
- catalog/service contract: `tests/models/test_catalog_service_contract.py`,
- smoke/parity tests dla runtime, gdy backend da się uruchomić bez realnych modeli albo z mockami.

Allowlisty w invariant tests są dozwolone tylko dla jawnego długu migracyjnego. Nowy kod nie powinien dopisywać się do allowlisty bez nazwania długu w [docs/services/inventory.md](../services/inventory.md).

## Definition of Done

Zmiana w service layer jest skończona, gdy:

1. Publiczne metody mają docstringi i type hints.
2. Serwis pozostaje async-ready i HTTP-agnostic.
3. Blokujący runtime nie blokuje event loop.
4. Engine/provider jest tworzony przez lazy registry; wybór silnika = `engine_id` (zero `engine`/`provider`/`engine_name`).
5. Identyfikatory zgodne z [naming-glossary.md](naming-glossary.md); zestaw `engine_id` derived z `_REGISTRY`, nie przepisany.
6. Fizyczne modele zostają w catalog/resolver boundary.
7. Targeted tests przechodzą.
8. `uv run pytest --no-cov tests/services -q` przechodzi po zmianach w usługach.

Translation jest aktualnie poza nowym quality gate, bo serwis jest przeznaczony do przepisania. Docelowo po rewrite ma wrócić pod ten sam standard.
