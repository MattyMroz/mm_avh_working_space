# Standard fabryki silników: engines/__init__.py

> Plik `services/<domena>/engines/__init__.py` wygląda KROPKA W KROPKĘ tak samo
> w każdej domenie. Różnice są dozwolone TYLKO w miejscach oznaczonych
> `[WYMUSZONE]` i tylko z powodów wymienionych w tabeli odstępstw.

Relacja do innych standardów:

- [engine-identity-standard.md](engine-identity-standard.md) - CO jest w pliku (EngineId + `_REGISTRY` = jedno źródło prawdy). Ten dokument uszczegóławia JAK plik wygląda (kolejność, nazwy, guard). Przy rozjeździe szkieletu wygrywa ten dokument.
- [engine-standard.md](engine-standard.md) - kształt pakietu pojedynczego silnika (`engines/<engine_id>/`).

## Decyzje kanoniczne

1. **Kolejność sekcji** (jedna, bez wyjątków): docstring → `from __future__` → importy stdlib → importy projektu → `__all__` → `logger` → `if TYPE_CHECKING` → `<Domena>EngineId` → `_REGISTRY` → `available_engine_ids()` → `create_engine()` → extras domeny.
2. **`__all__` na górze**, zaraz po importach, przed `logger`. Powód: 5/7 plików już tak ma, czytelnik widzi publiczny interfejs od razu. Kolejność w liście: `["<Domena>EngineId", "available_engine_ids", "create_engine"]` + extras na końcu (tak ma dziś 7/7 plików).
3. **Zmienna lokalna zawsze `engine_id`** (kanon bytów). Nigdy `name`.
4. **`available_engine_ids()` PRZED `create_engine()`**. Powód: mała funkcja przy danych które opakowuje; 4/7 już tak ma.
5. **`import importlib` top-level** (stdlib, tani). Nie w ciele funkcji.
6. **`<Domena>ConfigError` importowany top-level.** Wszystkie `services/<domena>/errors.py` to liście (importują tylko `mangashift.errors`) - komentarze "lazy: avoid circular" w ocr/inpainting/llm/image_processing to fikcja.
7. **`logger = get_logger(__name__)` + `logger.debug(...)` po konstrukcji** w każdej domenie (translation i llm dziś nie mają).
8. **Guard w create_engine** - dokładnie ten wzorzec, mypy narrowuje lokalną zmienną, zero `cast`:

   ```python
   engine_id = config.engine
   if not engine_id:
       msg = "<domena>.engine is required"
       raise <Domena>ConfigError(msg)
   if engine_id not in _REGISTRY:
       available = ", ".join(sorted(_REGISTRY))
       msg = f"Unknown <domena> engine: {engine_id!r}. Available: {available}"
       raise <Domena>ConfigError(msg)
   ```

   Komunikat zawsze `", ".join(sorted(_REGISTRY))` (nie `{sorted(_REGISTRY)}` - repr listy). Zawsze "engine", nie "provider" (llm dziś pisze "Unknown LLM provider").
9. **`_REGISTRY` typowany `Final[dict[<Domena>EngineId, tuple[str, str, str]]]`** - trzecia pozycja to zawsze `str` (translation/llm dziś mają `str | None`, ale żadna wartość nie jest None). Opis registry = JEDEN komentarz nad definicją (nie docstring pod nią, nie oba):

   ```python
   # engine_id -> (module_path, service_class, config_ref)
   ```

   Semantyka `config_ref`: nazwa klasy configu silnika eksportowanej z modułu silnika. Wyjątek tts: nazwa atrybutu sub-configu na `TtsConfig` (patrz odstępstwa). `create_engine` może go nie czytać (wtedy unpack do `_config_cls_name`) - element zostaje, bo test inwariantów wymusza 3-krotkę i dokumentuje typ configu silnika.
10. **Nazwy przy unpacku**: `module_path, service_cls_name, config_cls_name` (tts: `config_attr`). Klasa po getattr: `engine_cls` (nie `engine_class`).
11. **Docstringi kanoniczne** (bez em-dash, zgodnie ze stylem repo):
    - moduł: `"""<Domena> engine factory: registry-based engine construction."""` + linia `Entry point: ...`.
    - Literal: `"""Registry keys of <domena> engines; higher layers import this, never respell it."""` (już jednolity w 6/7).
    - available: `"""Return the registered <domena> engine ids (single source of truth)."""`.

## Kanoniczny szablon (kopiuj to)

```python
"""<Domena> engine factory: registry-based engine construction.

Entry point: ``create_engine(config)`` -> concrete ``<Domena>Engine``.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Final, Literal

from mangashift.services.<domena>.errors import <Domena>ConfigError
from mangashift.utils.logger import get_logger

__all__ = ["<Domena>EngineId", "available_engine_ids", "create_engine"]

logger = get_logger(__name__)

if TYPE_CHECKING:
    from mangashift.services.<domena>.config import <Domena>Config
    from mangashift.services.<domena>.protocols import <Domena>Engine

<Domena>EngineId = Literal["engine_a", "engine_b"]
"""Registry keys of <domena> engines; higher layers import this, never respell it."""

# engine_id -> (module_path, service_class, config_ref)
_REGISTRY: Final[dict[<Domena>EngineId, tuple[str, str, str]]] = {
    "engine_a": (
        "mangashift.services.<domena>.engines.engine_a",
        "EngineAService",
        "EngineAConfig",
    ),
}


def available_engine_ids() -> tuple[<Domena>EngineId, ...]:
    """Return the registered <domena> engine ids (single source of truth)."""
    return tuple(_REGISTRY)


def create_engine(config: <Domena>Config) -> <Domena>Engine:
    """Create a <domena> engine for the given config.

    Engines import lazily so heavy runtimes stay off the domain import path.

    Args:
        config: <Domena> configuration; ``config.engine`` selects the registry entry.

    Returns:
        A ``<Domena>Engine`` implementation ready for ``initialize()``.

    Raises:
        <Domena>ConfigError: If ``config.engine`` is empty or unknown.
    """
    engine_id = config.engine                      # [WYMUSZONE: llm czyta config.engine_id - dług pola configu]
    if not engine_id:
        msg = "<domena>.engine is required"
        raise <Domena>ConfigError(msg)
    if engine_id not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        msg = f"Unknown <domena> engine: {engine_id!r}. Available: {available}"
        raise <Domena>ConfigError(msg)
    # [WYMUSZONE: translation ma tu trzeci guard - "llm" wymaga wstrzykniętego completera]

    module_path, service_cls_name, config_cls_name = _REGISTRY[engine_id]
    module = importlib.import_module(module_path)
    engine_cls = getattr(module, service_cls_name)

    # [WYMUSZONE: konstrukcja] - JEDYNY blok różny per domena (sygnatury konstruktorów
    # silników realnie się różnią); patrz tabela "Krok konstrukcji".
    engine: <Domena>Engine = engine_cls(...)
    logger.debug("<Domena> engine created: {} ({})", engine_id, service_cls_name)
    return engine
```

Extras domeny (np. llm `supported_models`) idą PO `create_engine`, na końcu pliku,
a ich nazwy dopisuje się do `__all__` na końcu listy.

## Krok konstrukcji per domena [WYMUSZONE]

| Domena | Konstrukcja | Powód |
|---|---|---|
| ocr | `config_cls = getattr(module, config_cls_name)`; `engine_cls(config=config_cls(device=config.device))` | silnik ma własny config budowany z pól fasady |
| inpainting | jak ocr + introspekcja `fields(config_cls)` forwardująca `model_id`/`mask_dilation_ratio` | LaMa i Flux mają różne pola; introspekcja zamiast per-engine `if` |
| image_processing | `engine_cls(config=config)` (fasadowy `UpscaleConfig`; `SpandrelConfig` to alias - `spandrel/config.py:5`) | silnik konsumuje config fasady wprost |
| tts | `engine_cls(getattr(config, config_attr))` | sub-configi per silnik żyją NA `TtsConfig` (`tts/config.py:87-90`) |
| translation | `engine_cls(config, secret_provider=secret_provider)` | silnik dostaje fasadę + źródło klucza |
| llm | `engine_cls(config)` | silnik czyta `config.providers[engine_id]` sam |

## Odstępstwa wymuszone (zostają, w tym samym szkielecie)

| Domena | Odstępstwo | Powód | Werdykt |
|---|---|---|---|
| tts | `create_engine(config, *, engine_id: str)` - dodatkowy param zamiast `config.engine` | `TtsConfig` NIE MA pola `engine`; serwis buduje wiele silników per run (głos per postać), wybór jest per wywołanie (`tts/service.py:105`) | WYMUSZONE. Param przemianować `name` -> `engine_id` i zrobić wymaganym keyword-only (dziś `str \| None = None`, a jedyny caller zawsze podaje) |
| tts | trzeci element registry = nazwa atrybutu (`"edge"`), nie klasy | sub-configi na `TtsConfig` | WYMUSZONE; unpack do `config_attr` |
| translation | `*, secret_provider: SecretProvider \| None = None` | wstrzyknięcie źródła klucza z composition root (BYOK) | WYMUSZONE |
| translation | trzeci guard `if engine_id == "llm": raise` | silnik llm wymaga wstrzykniętego completera; buduje się go wprost i podaje do `TranslationService(engine=...)` | WYMUSZONE; pozycja: po dwóch guardach standardowych |
| llm | `engine_id = config.engine_id` | pole `LlmConfig` nazywa się `engine_id`, nie `engine` (`llm/config.py:68`) | WYMUSZONE do spłaty długu pola configu (patrz Długi) |
| llm | `_OPEN_CATALOG_PROVIDERS` + `supported_models()` | SSOT listy modeli dla front pickera | WYMUSZONE; sekcja extras PO `create_engine` |

Wszystko inne (kolejność funkcji, pozycja `__all__`, `name` vs `engine_id`,
lazy importy errorów/importlib, format komunikatu, docstring vs komentarz przy
registry, `str | None` w typie) to śmieć historyczny - ujednolicić do szablonu.

## Detekcja: wariant "domena fuzji" (FALA 8, wykonane)

`services/detection/engines/__init__.py` wpasowuje się w ten standard - ma
`ENGINE_REGISTRY`, `DetectionEngineId` (Literal), `available_engine_ids()`,
`create_engine(config)` - jak każda inna domena. Różni się TYLKO tym, że niesie
dwie dodatkowe rzeczy, bo detekcja robi FUZJĘ wielu silników naraz (nie jeden
silnik na request):

- `DetectionEngineSpec` (4 pola zamiast 3-krotki): `module_path`, `service_class`,
  `config_class` + `engine_family` (catalog family, którą musi mieć wybrany `model_id`),
- `engine_mapper(engine_id)` - lazy-loaduje mapper wyniku silnika na kanoniczny
  `DetectionPrimitive`; mapper żyje w pakiecie silnika, `services/detection/engines/<engine>/mapper.py`
  (NIE w osobnym `pipeline/detection/mappers/` - ten folder skasowany razem z `ModelFactory`, FALA 8),
- `OPT_IN_ENGINES` + `default_engine_ids()` - detekcja uruchamia wiele silników
  jednocześnie i fuzuje wyniki (`pipeline/detection/fusion/`), więc potrzebuje
  odróżnić "zarejestrowany" od "domyślnie włączony".

To udokumentowany WARIANT standardu, nie bałagan ani wyjątek od reguły "jedno
źródło prawdy": `DetectionEngineId` + `ENGINE_REGISTRY` leżą obok siebie w
JEDNYM pliku, dokładnie jak w pozostałych 7 domenach - z rozszerzonym payloadem
bo domena robi więcej (fuzja zamiast pojedynczego silnika).

## Lista zmian per domena (do szablonu) - WYKONANE (FALA 8)

Ścieżki względem `mangashift/services/`. Historia planu ujednolicenia - stan docelowy
(`engine_id` wymagany w tts, `config.engine_id` w llm, `tuple[str, str, str]` w translation)
jest już w kodzie; sekcja zostaje jako log decyzji, nie jako TODO.

**ocr/engines/__init__.py** (wzorzec bazowy, minimalne zmiany):

- l.13-15: swap - `__all__` przed `logger` (dziś logger l.13, `__all__` l.15).
- l.24 + l.37: podwójny opis `_REGISTRY` (komentarz i docstring) -> tylko komentarz kanoniczny.
- l.61: lazy import `OcrConfigError` -> top-level.
- l.1-4, l.41, l.46-60: docstringi -> kanon (bez em-dash, krótszy create_engine).

**inpainting/engines/__init__.py**:

- l.12: `__all__` rozcina blok importów (import loggera l.14 pod spodem) -> importy razem, `__all__` po nich.
- l.57: lazy import `InpaintingConfigError` ("avoid circular" - fałsz) -> top-level.
- l.25: komentarz registry -> format kanoniczny.
- l.1-4, l.41: docstringi -> kanon. Blok introspekcji l.73-84 zostaje (WYMUSZONE).

**tts/engines/__init__.py**:

- l.56: `name: str | None = None` -> `*, engine_id: str` (wymagany); rename w guardach l.69-74, unpacku l.76 i logu l.85. Caller: `tts/service.py:105` `name=engine_id` -> `engine_id=engine_id`.
- l.79: `import importlib` w funkcji -> top-level.
- l.73: komunikat `{sorted(_REGISTRY)}` -> `", ".join(sorted(_REGISTRY))`.
- l.48: docstring registry -> komentarz kanoniczny (z `config_attr` w opisie).
- l.1-6, l.52: docstringi -> kanon (moduł zachowuje zdanie o named engine bez fallback chain).

**translation/engines/__init__.py**:

- l.83: `__all__` z dołu -> góra (po importach).
- l.42-80: swap kolejności - `available_engine_ids()` przed `create_engine()`.
- l.60: `name` -> `engine_id` (+ guardy l.61-70, unpack l.71, konstrukcja l.74).
- brak loggera -> dodać `logger` + `logger.debug` po konstrukcji.
- l.22: `tuple[str, str, str | None]` -> `tuple[str, str, str]`.
- l.39: docstring registry -> komentarz kanoniczny; l.1-6 docstring modułu -> kanon.

**llm/engines/__init__.py**:

- l.125: `__all__` z dołu -> góra.
- l.62-101: swap - `available_engine_ids()` przed `create_engine()`; extras (l.104-122) zostają na końcu.
- l.78: lazy import `LlmConfigError` -> top-level.
- l.80: `name` -> `engine_id` (pole `config.engine_id` zostaje - dług).
- l.86: "Unknown LLM provider" -> "Unknown llm engine" (kanon komunikatu).
- brak loggera -> dodać.
- l.22: `str | None` -> `str`.
- l.54-59: docstring registry twierdzi "setup wizard and doctor read this map" - NIEAKTUALNE (nikt poza testami inwariantów nie czyta `_REGISTRY`) -> komentarz kanoniczny.

**image_processing/engines/__init__.py**:

- l.53: `import importlib` w funkcji -> top-level.
- l.55: import `UpscalingConfigError` w funkcji -> top-level.
- l.62: komunikat "Unknown engine:" bez domeny + `{sorted(...)}` -> kanon.
- l.65: unpack `_config_class` -> `_config_cls_name`.
- l.1-4 (en-dash), l.34: docstringi -> kanon.

**detection**: patrz sekcja wyżej - wariant "domena fuzji", nie kasacja. Rejestr
(`ENGINE_REGISTRY`) i mappery (`services/detection/engines/<engine>/mapper.py`) są
pełnoprawną, żywą implementacją standardu z rozszerzonym payloadem.

## Długi (odnotowane, POZA zakresem tego standardu)

1. **Pole configu: `engine` (5 domen) vs `engine_id` (llm).** Kanon bytów mówi
   `engine_id`, ale rename pola to kontrakt API/front (OpenAPI -> `generated.ts`),
   nie kosmetyka engines/. Osobne issue, decyzja usera o kierunku; do tego czasu
   llm ma `[WYMUSZONE]` w linii `engine_id = config.engine_id`.
2. **engine-identity-standard.md "Wzorzec kanoniczny"** ma inną kolejność w
   `__all__` i guard bez checku pustego stringa - przy wdrożeniu dopisać tam
   odnośnik do tego dokumentu (szkielet szczegółowy żyje tu).
3. ~~**tts wymagany `engine_id`**~~ - spłacone: `create_engine(config, engine_id=...)`
   w kodzie i w `tests/services/test_tts.py`.

## Czego nie jestem pewny

- Nie grepowałem `tests/services/test_tts.py` pod kątem wywołań
  `create_engine(..., name=None)` / pozycyjnych - przy zmianie sygnatury na
  wymagany keyword sprawdzić i poprawić testy.
- Czytałem tylko fragment `test_engine_structure_invariants.py` - zakładam, że
  `REGISTRY_MODULES` (używane w `_registry_entries`, l.127-144) obejmuje 6 domen
  bez detekcji (detekcja czytana osobno l.301/498/515); zweryfikować przed
  kasacją lustra.
- Guard `if not engine_id` jest martwy tam, gdzie pole configu to czysty
  `Literal` walidowany wcześniej (np. pydantic), ale żywy tam, gdzie pole to
  `str = ""` (`UpscaleConfig.engine`). Zostawiam wszędzie jako defense-in-depth
  o zerowym koszcie - jeśli user woli ciąć, to świadoma decyzja, nie standard.
- Kierunek długu nr 1 (rename `engine` -> `engine_id` wszędzie vs llm ->
  `engine`) celowo nierozstrzygnięty - dotyka kontraktu API i frontu.
