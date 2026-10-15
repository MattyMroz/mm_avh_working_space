# Runtime Lifecycle - How VRAM Management Works in Practice

> Praktyczny przewodnik po `mangashift.runtime`. Pokazuje co się dzieje
> krok po kroku, gdy ładujemy/zwalniamy modele, jakie są typowe scenariusze
> i jak debugować problemy z VRAM.
>
> **Decyzja architektoniczna (źródło prawdy):** refcount-only, bez heurystyk LRU - fail-fast
> (ten dokument jest źródłem prawdy; uzasadnienie w FAQ poniżej).
> **Reference env vars / CLI / API:** [runtime-backends.md](runtime-backends.md#runtime-vram-management)

## Spis treści

- [Trzy operacje życia modelu](#trzy-operacje-życia-modelu)
- [Sekwencja `acquire()` krok po kroku](#sekwencja-acquire-krok-po-kroku)
- [Sekwencja release przy wyjściu z `with`](#sekwencja-release-przy-wyjściu-z-with)
- [Świętość #1 - VRAM oddany po pipeline](#świętość-1--vram-oddany-po-pipeline)
- [Scenariusze użycia](#scenariusze-użycia)
- [Co runtime NIE robi (świadomie)](#co-runtime-nie-robi-świadomie)
- [Tiery (informacyjne)](#tiery-informacyjne)
- [OOM handling i `InsufficientVramError`](#oom-handling-i-insufficientvramerror)
- [Concurrency (`Semaphore`)](#concurrency-semaphore)
- [LLama server (osobny tracking)](#llama-server-osobny-tracking)
- [Debugowanie](#debugowanie)
- [FAQ](#faq)
- [Linki](#linki)

## Dwie operacje życia modelu

Runtime eksponuje dwa wzorce użycia. Wszystko inne jest implementacją wewnętrzną.

> 🚨 **`acquire_many` (ensemble atomowy) NIE ISTNIEJE w kodzie** - `RuntimeManager` ma tylko
> `acquire` (pojedynczy spec). Zaległość: issue #188.

### 1. Pojedynczy model (`acquire`)

```python
from mangashift.runtime import get_runtime
from mangashift.models.catalog import find_model_spec
from mangashift.services.detection.engines import create_engine

runtime = get_runtime()
spec = find_model_spec("magi_v3")

with runtime.acquire(spec, build=lambda: create_engine(config)) as service:
    detections = service.detect(image)
# Po wyjściu z `with` refcount-- → jeśli 0, model jest zwolniony.
```

`build` to lambda tworząca serwis silnika (typowo `create_engine(config)` z rejestru domeny)
wywoływana TYLKO przy cache miss - na trafienie cache `acquire` zwraca istniejącą instancję
i `build` się nie odpala. `config_overrides` (opcjonalny) identyfikuje wariant załadowanej instancji.

### 2. Ręczny escape hatch (`release` / `release_all`)

```python
runtime.release("magi_v3")              # noop jeśli refcount > 0
runtime.release("magi_v3", force=True)  # unload mimo aktywnych ref
runtime.release_all()                   # zwolnij wszystkie idle (refcount == 0)
runtime.release_all(force=True)         # zwolnij absolutnie wszystko
```

> 💡 **Reguła:** w produkcyjnym kodzie zawsze preferuj `with acquire(...)`.
> Bezpośrednie `release` to escape hatch dla CLI/API i sytuacji awaryjnych.

## Sekwencja `acquire()` krok po kroku

Co się dzieje wewnątrz `acquire(spec)` od momentu wejścia w `with` do
otrzymania serwisu:

```text
with runtime.acquire(spec) as service:
        │
        ▼
   ┌────────────────────────────────────────────┐
   │ 1. _ensure_loaded(spec)                    │
   │    ├─ already in self._loaded?             │
   │    │   └─ yes → reuse, jump to step 6      │
   │    └─ no  → continue                       │
   │                                            │
   │ 2. verify_sha256(spec, manifest)           │
   │    └─ ModelIntegrityError jeśli mismatch   │
   │       (skip jeśli MANGASHIFT_SKIP_CHECKSUM)│
   │                                            │
    │ 3. fits(spec, free_mb, hardware_tier)      │
   │    └─ False → InsufficientVramError(       │
   │              suggestion=build_release_…)   │
   │                                            │
   │ 4. build()  (lambda z create_engine)       │
   │    └─ ModelLoadError jeśli backend padnie  │
   │                                            │
   │ 5. self._loaded[id] = LoadedModel(         │
   │       service, refcount=0, loaded_at=…)    │
   │                                            │
   │ 6. loaded.refcount += 1                    │
   │    loaded.last_used = time.time()          │
   │    loaded.use_count += 1                   │
   │                                            │
   │ 7. telemetry.emit("acquire", {...})        │
   │                                            │
   │ 8. yield loaded.service                    │
   └────────────────────────────────────────────┘
```

**Kluczowe niezmienniki:**

- Każdy `acquire` dokładnie raz inkrementuje `refcount`.
- `_ensure_loaded` nigdy nie wywołuje `release` cudzych modeli - runtime
  jest fail-fast, nie wybawia caller'a magicznym evictionem.
- Telemetria jest opt-in (`MANGASHIFT_VRAM_TELEMETRY=on`), normalnie noop.

## Sekwencja release przy wyjściu z `with`

Wyjście z bloku `with` (normalne lub przez wyjątek) zawsze trafia do
`finally` w `_acquire_cm`:

```text
exit `with` block
        │
        ▼
   ┌────────────────────────────────────────────┐
   │ 1. _release_one(model_id, force=False)     │
   │    └─ loaded.refcount -= 1                 │
   │                                            │
   │ 2. if loaded.refcount == 0:                │
   │       _unload(model_id, reason="release")  │
   │                                            │
   │ 3. _unload steps:                          │
   │    a) service.close()  (best-effort)       │
   │    b) ort_cleanup()    (jeśli ONNX)        │
   │    c) gc.collect()                         │
   │    d) cleanup_cuda_cache()                 │
   │    e) telemetry.emit("release", {...})     │
   │                                            │
   │ 4. del self._loaded[model_id]              │
   └────────────────────────────────────────────┘
```

**Świętość #12** - agresywny ONNX cleanup po każdym release wymusza zwrot
device memory do alokatora ORT, nie tylko spadek refcount Pythona.

## Świętość #1 - VRAM oddany po pipeline

Ta zasada jest **obligatoryjna** i wymuszona przez pipeline:

```python
# mangashift/pipeline/pipeline.py - ProcessingPipeline.process()
def process(self, job: Any) -> ProcessingResult:
    try:
        return self._execute(job)
    finally:
        if self._runtime is not None:
            with contextlib.suppress(Exception):
                self._runtime.release_all()
```

Niezależnie od tego, czy `_execute` przejdzie czysto, czy crashuje
w środku - `release_all()` w `finally` gwarantuje, że VRAM wraca do
baseline. To jest twardy kontrakt runtime → pipeline.

**Walidacja empiryczna (real GPU):**

```bash
uv run python scripts/runtime/smoke_e2e.py --pipeline-mode
```

Smoke mierzy NVML allocated przed/po, asercja: `delta_mb < tolerance`.

## Scenariusze użycia

| Scenariusz | Co się dzieje | Peak VRAM |
|---|---|---|
| Pojedyncza inferencja | `acquire` → run → release | `size(model)` |
| Pipeline 5 sekwencyjnych modeli | każdy `with acquire` per krok | `max(model_i)` |
| Ensemble (wiele modeli naraz, np. detekcja) | osobny `with acquire` per model, zagnieżdżone | `sum(models)` (brak atomowego `acquire_many`, patrz wyżej) |
| 2× ten sam model w pipeline | refcount++ na drugim `acquire` | `size(model)` |
| OOM przy load | `InsufficientVramError(suggestion=…)` | - |
| Concurrent API requests | `Semaphore(1)` szereguje | jak pojedyncza |
| OS pressure (opt-in) | `OSPressureMonitor` → `release_all` | - |
| Manual reset | `runtime release-all --force` | 0 |

### Pipeline 5 sekwencyjnych modeli

```python
for spec in [classifier, detector, ocr, refiner, renderer]:
    with runtime.acquire(spec) as service:
        result = service.run(payload)
        payload = result
# Każdy krok zwalnia model przed wejściem w następny → peak = max(model_i),
# a nie sum().
```

### 2× ten sam model w pipeline

```python
with runtime.acquire(magi) as detector_a:
    raw = detector_a.detect(img)
    with runtime.acquire(magi) as detector_b:
        # refcount == 2; ten sam service object
        assert detector_a is detector_b
        sub = detector_b.detect(crop(img))
    # refcount == 1; nadal loaded
# refcount == 0; unload
```

### OOM przy load

`fits()` jest jedynym admission gate. Gdy zwraca `False`, runtime rzuca
`InsufficientVramError` z gotową rekomendacją (patrz sekcja
[OOM handling](#oom-handling-i-insufficientvramerror)).

### Concurrent API requests

Świętość #11: pipeline serializowany. Patrz sekcja
[Concurrency](#concurrency-semaphore).

### OS pressure (opt-in)

`MANGASHIFT_OS_PRESSURE_RESPONSE=on` startuje wątek daemon, który czyta
RAM/swap pressure i przy progu wywołuje `runtime.release_all()`.
Domyślnie wyłączone - opt-in dla self-hosted produkcji.

## Co runtime NIE robi (świadomie)

| Anty-feature | Dlaczego brak | Co zrobić zamiast |
|---|---|---|
| LRU eviction | Nieprzewidywalność, ukryte koszty, debugging horror | Caller wybiera kogo `release` na podstawie `InsufficientVramError.suggestion` |
| Sticky / pinned models | Heurystyka maskująca błąd designu | Trzymaj model w długim `with acquire` na poziomie service'u |
| Auto-quality downgrade | "Magia" - caller traci kontrolę nad jakością | Caller wybiera klasę rozmiaru modelu jawnie przy `acquire` |
| Auto-retry przy OOM | Race conditions, infinite loops | Catch `InsufficientVramError`, release wskazane modele, retry ręcznie |
| Kill `llama-server` | Świętość #7 - external subprocess poza scope refcount | Manage llama-server przez `mangashift.models.llama_runtime` osobno |

> 📚 Pełne uzasadnienie decyzji refcount-only: sekcja FAQ poniżej.

## Klasy i tiery informacyjne

`HardwareTier` i `ModelSizeClass` są **informacyjne** - używane przez
`fits()` jako inputy, ale runtime nie steruje evictionem na ich podstawie.

### `HardwareTier`

| Tier | VRAM range | Komentarz |
|---|---|---|
| `CPU` | brak GPU | fallback, część modeli niedostępna |
| `LOW` | < 6 GB | ograniczony katalog, tylko TINY/SMALL |
| `MID` | 6–12 GB | większość workflow działa |
| `HIGH` | 12–24 GB | wszystko prócz ULTRA ensemble |
| `ULTRA` | ≥ 24 GB | bez ograniczeń, ensemble OK |

Detekcja: `detect_budget(nvml=…)` przy starcie `RuntimeManager`. Wynik
jest immutable (`VRAMBudget`).

### `ModelSizeClass`

| Size class | Peak VRAM | Przykłady |
|---|---|---|
| `TINY` | < 1 GB | classifier, ordering helpers |
| `SMALL` | 1–4 GB | ctbd_v2, drobne OCR |
| `MEDIUM` | 4–8 GB | magi_v2, mask refinement |
| `LARGE` | 8–16+ GB | magi_v3, sam_tss_h_hiertext, flux_klein |

`fits(spec, free_mb, hardware_tier)` to pojedynczy admission test:
`free_mb >= spec.peak_vram_mb` (z drobnymi marginesami zależnie od tieru
hardware'u).

## OOM handling i `InsufficientVramError`

```python
from mangashift.runtime.errors import InsufficientVramError

try:
    with runtime.acquire(spec) as service:
        result = service.run(image)
except InsufficientVramError as exc:
    # exc.peak_mb / exc.free_mb / exc.loaded / exc.suggestion
    logger.warning("OOM: {}", exc)
    # Suggestion: "Release ['sam_tss_h_hiertext', 'magi_v3'] to free ~5400 MB"
    for loaded in exc.loaded:
        if loaded.model_id in ("sam_tss_h_hiertext", "magi_v3"):
            runtime.release(loaded.model_id, force=True)
    # Retry świadomie po cleanupie
    with runtime.acquire(spec) as service:
        result = service.run(image)
```

`build_release_suggestion()` jest greedy: sortuje załadowane modele po
`peak_vram_mb` malejąco i wybiera najmniejszy zestaw, który po release
pokryje deficyt. To sugestia, nie automatyzacja - caller decyduje czy
faktycznie zwalniać.

## Concurrency (`Semaphore`)

**Świętość #11**: pipeline jest serializowany przez `Semaphore(1)` w
`mangashift.api.main`:

```python
def _serialize_pipeline_runner(runner: PipelineRunner) -> PipelineRunner:
    sem = asyncio.Semaphore(1)
    async def serialized(job, uow):
        async with sem:
            await runner(job, uow)
    return serialized
```

**Dlaczego nie concurrent:**

- VRAM nie skaluje się z liczbą równoległych pipeline'ów - każdy ładuje
  ten sam zestaw modeli.
- Race condition w `acquire/release` gdyby dwa joby ścigały się o ten
  sam model.
- Fail-fast (kolejka requestów) > niedeterministyczny OOM mid-pipeline.

API kolejkuje, klient czeka. Throughput skaluje się przez wiele instancji
procesu, nie przez wątki w jednej.

## LLama server (osobny tracking)

Świętość #7: `release_all()` **NIGDY** nie zabija `llama-server`. Jest
to external subprocess (HTTP API), tracked osobno w
`runtime.types.LlamaServerStatus`:

```python
status = runtime.status()
if status.llama_server is not None:
    print(status.llama_server.url, status.llama_server.healthy)
```

Lifecycle llama-server'a żyje w `mangashift.models.llama_runtime` -
osobny manager, osobny start/stop. `RuntimeManager.release_all()` go
ignoruje, bo nie zaalokował go w `_loaded` dict.

## Debugowanie

### CLI

```bash
mangashift runtime status                # tabela: id, refcount, vram, loaded_at
mangashift runtime status --json         # do skryptów / monitoring
mangashift runtime cleanup               # gc + ort_cleanup, bez unload
mangashift runtime release-all [--force] # zwolnij idle (lub wszystko z --force)
mangashift runtime defrag                # release_all(force) + cleanup
mangashift runtime unload <id> [--force] # punktowe zwolnienie
```

### REST (admin only)

```text
GET  /api/v1/runtime/status
POST /api/v1/runtime/release-all   body: {"force": bool}
POST /api/v1/runtime/unload/{id}   body: {"force": bool}
POST /api/v1/runtime/cleanup
```

### Telemetria (opt-in)

```bash
export MANGASHIFT_VRAM_TELEMETRY=on
# Eventy → logs/runtime.log.jsonl:
#   runtime/load, runtime/acquire, runtime/release,
#   runtime/release_all, runtime/cleanup
```

Każdy event niesie `model_id`, `refcount`, `free_mb`, czasem `peak_mb`.
Pozwala na audyt: *czy refcount wraca do zera po pipeline?*

### Smoke E2E (real GPU)

```bash
uv run python scripts/runtime/smoke_e2e.py --all-tiny      # walidacja TINY
uv run python scripts/runtime/smoke_e2e.py --pipeline-mode # świętość #1
```

Smoke jest jedynym automatycznym testem, który dotyka prawdziwego GPU
i NVML - CI/jednostki używają stubowanego `VRAMBudget`.

### Common issues

| Symptom | Przyczyna | Fix |
|---|---|---|
| VRAM rośnie po pipeline | brak `release_all` w `finally` | sprawdź `pipeline/pipeline.py::process` |
| `ModelIntegrityError` | mismatch SHA-256 vs `external/model_hashes.json` | re-pull modelu lub dev-only `MANGASHIFT_SKIP_CHECKSUM=1` |
| `InsufficientVramError` | faktycznie brak VRAM | release sugerowanych modeli lub mniejsza klasa rozmiaru |
| ORT memory leak | sesja ONNX nie zwolniona (np. crash przed `_unload`) | `mangashift runtime cleanup` lub `defrag` |
| `release_all` bez efektu | refcount > 0 (model w użyciu) | dodaj `--force`, ale sprawdź czemu nie zwolniony |

## FAQ

**Q: Czy mogę trzymać model w VRAM między requestami?**
A: Tak - używaj `runtime.acquire()` w długoplażyjącym kontekście
(np. service-level singleton z `__enter__`/`__exit__` w lifecycle
serwisu), nie per-request. Refcount zachowa model.

**Q: Co jeśli pipeline crashuje w środku?**
A: `try/finally release_all()` w `ProcessingPipeline.process()`
gwarantuje cleanup nawet przy `Exception`. Jeśli crash zabije proces -
GPU memory wraca naturalnie po terminacji.

**Q: Czemu nie ma LRU eviction?**
A: Świadoma decyzja - fail-fast >
magia. LRU dodaje nieprzewidywalność (kiedy konkretnie evict?), ukryte
koszty (re-load nieoczekiwany dla caller'a) i debugging horror
(reproducibility).

**Q: Jak dodać nowy model?**
A: Patrz [model-system.md](model-system.md). Po dodaniu spec do catalog
i hash do `external/model_hashes.json`, działa z `runtime.acquire(spec)`
automatycznie.

**Q: Mogę użyć runtime poza pipeline (np. w skrypcie)?**
A: Tak - `from mangashift.runtime import get_runtime`, potem
`with get_runtime().acquire(spec) as service:`. Pamiętaj o `with`
(albo `try/finally release`) - bez tego refcount wycieknie.

**Q: Co z multi-GPU?**
A: Obecny runtime jest single-GPU (device 0). NVML detekcja patrzy na
device 0, factory tworzy modele na `cuda:0`. Multi-GPU sharding to
przyszłość, nie scope tego runtime.

**Q: Jak sprawdzić, czy refcount wycieka?**
A: Włącz telemetrię (`MANGASHIFT_VRAM_TELEMETRY=on`), policz
`acquire` vs `release` per `model_id` w `logs/runtime.log.jsonl`.
Jeśli `acquire_count > release_count` po pipeline → leak.

## Linki

- [runtime-backends.md - env vars, CLI, API reference](runtime-backends.md)
- [model-system.md - model specs, catalog, tiers](model-system.md)
- [scripts/runtime/smoke_e2e.py](../scripts/runtime/smoke_e2e.py)
- [mangashift/runtime/manager.py](../mangashift/runtime/manager.py)
- [mangashift/pipeline/pipeline.py](../mangashift/pipeline/pipeline.py)
