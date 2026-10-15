# Standard tożsamości silnika (engine identity)

> Jedna architektura dla WSZYSTKICH domen silników. Jedna tablica prawdy per domena.
> Dodajesz silnik → edytujesz JEDEN plik. Reszta importuje.

## Zasada nadrzędna

Każda domena silników ma **DOKŁADNIE JEDNO** źródło prawdy o swoich silnikach:
plik `services/<domena>/engines/__init__.py`. W tym pliku, obok siebie, leżą dwie rzeczy:

1. `<Domena>EngineId` - typ (lista dozwolonych `engine_id`), idzie do frontu przez OpenAPI.
2. `_REGISTRY` - mapa `engine_id → (moduł, klasa serwisu, klasa configu)`, runtime.

Klucze `_REGISTRY` są **typowane** przez `<Domena>EngineId`, więc mypy nie pozwoli na
rozjazd. Wyższe warstwy (config serwisu, pipeline, api) **importują** `<Domena>EngineId` -
nigdy nie przepisują listy silników.

## Wzorzec kanoniczny (kopiuj to)

```python
# services/<domena>/engines/__init__.py
from __future__ import annotations

from typing import Final, Literal

__all__ = ["available_engine_ids", "create_engine", "<Domena>EngineId"]

<Domena>EngineId = Literal["engine_a", "engine_b"]
"""Dozwolone engine_id tej domeny."""

_REGISTRY: Final[dict[<Domena>EngineId, tuple[str, str, str]]] = {
    "engine_a": ("mangashift.services.<domena>.engines.engine_a", "EngineAService", "EngineAConfig"),
    "engine_b": ("mangashift.services.<domena>.engines.engine_b", "EngineBService", "EngineBConfig"),
}


def available_engine_ids() -> tuple[<Domena>EngineId, ...]:
    """Zarejestrowane engine_id - jedyne źródło prawdy."""
    return tuple(_REGISTRY)


def create_engine(config: <Domena>Config) -> <Domena>Engine:
    engine_id = config.engine
    if engine_id not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise <Domena>ConfigError(f"Unknown engine: {engine_id!r}. Available: {available}")
    module_path, service_cls, config_cls = _REGISTRY[engine_id]
    ...
```

```python
# services/<domena>/config.py  - NIE definiuje listy, IMPORTUJE typ
from mangashift.services.<domena>.engines import <Domena>EngineId

@dataclass(slots=True)
class <Domena>Config:
    engine: <Domena>EngineId
    device: Literal["cuda", "cpu"] = "cuda"
```

```python
# pipeline/<domena>/types.py  - też IMPORTUJE, nie przepisuje
from mangashift.services.<domena>.engines import <Domena>EngineId
```

## Przepływ danych (jeden kierunek)

```
FRONT (user wybiera silnik)
  │  POST { "engine": "engine_a" }        generated.ts zna typ "engine_a"|"engine_b"
  ▼                                              ▲ codegen z OpenAPI
API schema ──import──┐                           │
pipeline/types ──────┼──► <Domena>EngineId ──────┘   (JEDNO źródło typu)
config serwisu ──────┘         ▲
                               │ leży OBOK
                    _REGISTRY (tablica prawdy) ──► create_engine ──► konkretny silnik
```

- **Powstaje** we froncie (user klika).
- **Typ** = `<Domena>EngineId` w `services/<domena>/engines/__init__.py`.
- **Tablica prawdy** = `_REGISTRY` w tym samym pliku.
- **Front** dostaje typ za darmo (Literal → OpenAPI enum → `generated.ts`).
- **Walidacja** = `create_engine` odrzuca nieznany `engine_id` (błąd, nigdy ciche podstawienie).

## Docelowy stan per domena

| Domena | `<Domena>EngineId` + `_REGISTRY` w | Uwaga |
|---|---|---|
| ocr | `services/ocr/engines/__init__.py` | standard |
| inpainting | `services/inpainting/engines/__init__.py` | standard |
| tts | `services/tts/engines/__init__.py` | standard |
| translation | `services/translation/engines/__init__.py` | `TranslationEngineId` = silniki (`google`, `deepl`, `llm`). `copy_original` to tryb pipeline (brak silnika), żyje osobno w `pipeline/translation/types.py` |
| llm | `services/llm/engines/__init__.py` | standard (`LlmEngineId`) |
| image_processing | `services/image_processing/engines/__init__.py` | standard (`UpscaleEngineId`) |
| detection | `services/detection/engines/__init__.py` | wariant "domena fuzji": `DetectionEngineId` + `ENGINE_REGISTRY` leżą w tym samym pliku co reszta domen, ale `DetectionEngineSpec` niesie dodatkowo `engine_family` i mapper (`engine_mapper()`), bo detekcja fuzuje kilka silników naraz zamiast wybierać jeden. Mappery żyją per-silnik w `services/detection/engines/<engine>/mapper.py` |

Detekcja NIE jest wyjątkiem co do LOKALIZACJI (rejestr żyje w `services/`, jak wszędzie) -
różni się TYLKO rozszerzonym payloadem rejestru. Zasada ta sama wszędzie:
`<Domena>EngineId` + registry obok siebie, jedno źródło, wyższe warstwy importują.

## Dodanie nowego silnika (docelowo)

1. Napisz klasę silnika w `services/<domena>/engines/<nowy>/`.
2. Dopisz `engine_id` do `_REGISTRY` **i** do `<Domena>EngineId` w JEDNYM pliku (`engines/__init__.py`).
3. Koniec. Config, pipeline, api, front (po codegen) dostają go automatycznie.

Sync test (`set(get_args(<Domena>EngineId)) == set(available_engine_ids())`) pilnuje, że
Literal i registry się nie rozjadą (jedyne czego mypy nie złapie: literówka w Literal bez
wpisu w registry).

## Byty tożsamości (nie mylić)

| byt | co znaczy | gdzie żyje |
|---|---|---|
| `engine_id` | który silnik uruchomić | `_REGISTRY` serwisu (ten dokument) |
| `model_id` | wpis w `MODEL_CATALOG` | `models/` (osobny system: model-system.md) |
| `resource_name` | fizyczny bundle na dysku | `models/` |
| `provider_model_id` | model API u dostawcy (LLM/TTS) | constants silnika |
| `label` | tekst dla człowieka (UI) | **tylko frontend** |

`engine_id` (ten dokument) ≠ `model_id` (`models/`). Silnik może obsługiwać wiele modeli;
wybór modelu to osobny przepływ (`model_id`, front → `model_id_by_engine`).
