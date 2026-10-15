# 🗂️ Services Index — MangaShift

> **Standard:** `docs/service-standard.md` v2.0
> **Ostatnia aktualizacja:** 2026-04-22

---

## Serwisy produkcyjne (6) + 1 scaffold

| Serwis | Silniki | Zgodność v2.0 | Status | Przewodnik |
|--------|---------|---------------|--------|------------|
| **detection** | 7 (RT-DETR, CTD, Hi-SAM, Magi, MBS, MTS, AnimeText) | 13/13 | ✅ stable | [services/detection/adding-engines.md](../services/detection/adding-engines.md) |
| **ocr** | 3 (OneOcr, PaddleOCR-Manga, PaddleOCR-1.5) | 13/13 | ✅ stable | [services/ocr/adding-engines.md](../services/ocr/adding-engines.md) |
| **inpainting** | 2 (LaMa, Flux-Klein) | 13/13 | ✅ stable | [services/inpainting/adding-engines.md](../services/inpainting/adding-engines.md) |
| **image_processing** | 1 (Spandrel upscaler) | 13/13 | ✅ stable | [services/image_processing/adding-engines.md](../services/image_processing/adding-engines.md) |
| **translation** | 2 providers (Gemini API, geminicli2api) | 13/13 | ✅ stable | [services/translation/adding-engines.md](../services/translation/adding-engines.md) |
| **tts** | 3 providers (Edge, ElevenBytes, ElevenLabs) | 13/13 | ✅ stable | [services/tts/adding-engines.md](../services/tts/adding-engines.md) |
| **video_generation** | 0 | 0/13 | 🟡 scaffold | — (stub, do dokończenia) |

---

## Jak czytać zgodność 13/13

Każdy serwis jest audytowany przeciwko 13 bramkom ze standardu:

| # | Bramka | Co sprawdzamy |
|---|--------|---------------|
| G1 | `_portable.py` | `REQUIRED_DEPS`, `ENGINE_DEPS`, `OPTIONAL_DEPS`, `PORTABLE_MODULES`, `MIN_PYTHON` |
| G2 | Config | `@dataclass(frozen=True, slots=True)` + `from_dict()` lub `**kwargs` |
| G3 | Errors | Hierarchia `{Domain}Error` → `ConfigError`/`EngineError`/`RuntimeError` |
| G4 | Protocols | `{Domain}Engine(EngineInfo, Protocol)` + `@runtime_checkable` |
| G5 | Types | `@dataclass(slots=True)` result z `processing_time_ms` + `init_time_ms` |
| G6 | Service (async) | `{Domain}Service` z `async def initialize/process/cleanup` |
| G7 | Service (sync bridge) | `__enter__`/`__exit__` oparty o `asyncio.run()` |
| G8 | `engines/__init__.py` | `_REGISTRY: dict[str, tuple[str, str, str]]` 3-tuple |
| G9 | Factory | `create_engine(config)` z lazy `importlib.import_module` |
| G10 | FakeEngine | W `tests/fakes.py` — spełnia Protocol, `isinstance()` check pass |
| G11 | Timing Pattern v2.0 | `time.perf_counter() * 1000` → `processing_time_ms` + `init_time_ms` |
| G12 | Testy | ≥ 8 testów (unit + integration), `-q --no-cov` pass |
| G13 | Dokumentacja | `adding-engines.md` + docstringi Google-style |

---

## Powiązane dokumenty

- [service-standard.md](service-standard.md) — pełny standard v2.0 + wzorce
- [runtime-backends.md](runtime-backends.md) — profile runtime V3, backend matrix i fail-fast policy
- [model-system.md](model-system.md) — jak pobierać wagi dla silników
- [api.md](../guides/api.md) — jak silniki wychodzą do klientów przez FastAPI

---

## Kolejność dodawania silnika (TL;DR)

1. Utwórz pakiet `engines/{nazwa}/` z `engine.py`, `config.py`, `__init__.py`
2. Zaimplementuj `{Domain}Engine` Protocol (G4)
3. Config z `from_dict()` albo `**kwargs` (G2)
4. Zarejestruj w `engines/__init__.py` → `_REGISTRY` 3-tuple (G8)
5. Dodaj do `_portable.py` → `ENGINE_DEPS[name] = [...]` (G1)
6. Dodaj `FakeEngine` w `tests/fakes.py` (G10)
7. Napisz ≥ 8 testów — unit (fake) + integration (real jeśli środowisko pozwala) (G12)
8. Zweryfikuj timing: `processing_time_ms` i `init_time_ms` ustawione (G11)
9. Uruchom `uv run pytest tests/services/test_{serwis}.py -q --no-cov` → 0 fail
10. `uv run mypy mangashift/` + `uv run ruff check` → czysto

> Szczegóły per serwis w `services/{nazwa}/adding-engines.md`.
