# Runtime Backends — V3 Policy

Źródło prawdy dla delivery, backendów i profili runtime w V3. Cel: prosty system, jawne profile, zero ukrytych instalacji i zero automatycznego ratowania VRAM kosztem czytelności.

## Zasady

- **Production default:** ONNX, GGUF albo native runtime.
- **Torch:** przejściowo dla exportu, testów referencyjnych, fallbacków i dev spike'ów.
- **ComfyUI:** tylko lab/dev dla Mateusza, nie production dependency.
- **Startup aplikacji:** nigdy nie uruchamia `uv sync`, downloadu runtime ani auto-update.
- **Setup:** jedyne miejsce, które może instalować zależności, pobierać modele i przygotowywać runtime.
- **Błędy:** fail-fast z jasnym komunikatem zamiast ukrytych retry, auto-eviction i magicznego zmniejszania jakości.
- **Modułowość:** engine wybiera backend; core nie importuje ciężkich bibliotek na module load.

## Profile Delivery

| Profil | Cel | Torch? | ComfyUI? | Domyślne backendi |
|---|---|---:|---:|---|
| `core` | importy, CLI, config, katalog, API contracts | Nie | Nie | Brak ciężkiego runtime |
| `runtime-onnx` | production CV/OCR/inpainting/upscaling | Nie | Nie | ONNX Runtime CUDA/CPU |
| `runtime-gguf` | selected VLM/LLM/OCR | Nie | Nie | `llama.cpp` pinned cache |
| `runtime-native` | proprietary/native engines | Nie | Nie | DLL/native bundle |
| `torch-cu128` / `torch-models` | dev, fallback, export, parity tests | Tak | Nie | PyTorch CUDA 12.8 |
| `lab-comfy` | lokalne eksperymenty Mateusza | Tak | Tak | ComfyUI/dev engines |
| `export-spike` | ONNX/GGUF conversion work | Tak | Opcjonalnie | Torch + export tooling |

Aktualny W0 zostawia `uv sync` jako RTX/cu128-friendly default przez grupę `local-dev`, bo to odblokowuje codzienny dev Mateusza. Production/installer ma osobny profil `production` i extra `production`, oba bez Torcha i ComfyUI.

## Decyzja: Dev vs Installer

Torch ma zostać dostępny lokalnie dla Mateusza, bo jest potrzebny do testowania nowych rzeczy, exportu ONNX/GGUF, parity checks i spike'ów. To nie znaczy, że Torch ma być częścią głównego programu.

| Tryb | Co instalujemy | Po co |
|---|---|---|
| Local dev Mateusza | `core` + `local-dev` = `production` + `gradio-ui` + `torch-models` + `cuda-runtime` | Testy, eksperymenty, export, fallback, porównania jakości |
| Installer / production app | `core` + `production` = API/DB/image/media/text/TTS + ONNX/GGUF/native | Normalne użycie programu bez Torcha |
| CI core | `core` | Importy, lint, typy, testy bez ML runtime |
| CI production smoke | `core` + `runtime-onnx` + `runtime-gguf` | Sprawdzenie, że główny program nie wymaga Torcha |

Wniosek: `uv sync` zostaje dev-friendly i instaluje `torch-cu128`, ale build/install głównej aplikacji używa profilu bez Torcha.

Aktualny dev default:

```bash
uv sync
```

Aktualny explicit CPU Torch profile dla testu resolvera:

```bash
uv sync --no-default-groups --extra cpu --dry-run
```

Aktualny core-only torchless dry-run:

```bash
uv sync --no-default-groups --dry-run
```

Aktualny production ONNX dry-run bez Torcha:

```bash
uv sync --no-default-groups --group production --dry-run
```

Aktualny wheel/install extra dla aplikacji bez Torcha:

```bash
uv pip install "mangashift[production]"
```

## Aktualny Pyproject Split

`pyproject.toml` ma lekki `project.dependencies` oraz jawne feature extras i dependency groups. Grupy `production` oraz extra `production` są torchless; grupa `local-dev` składa pełny lokalny stack Mateusza z CUDA Torch.

| Profil | Dependencies / grupy | Decyzja |
|---|---|---|
| `core` | `loguru`, `packaging`, `pydantic`, `pydantic-settings`, `rich`, `typer`, `platformdirs`, `pyyaml`, `psutil`, `tenacity`, `tqdm`, `requests`, `httpx`, `aiohttp`, `hf-xet` | Zostają bazą programu |
| `api-server` | `fastapi`, `uvicorn[standard]`, `python-multipart`, `sse-starlette`, `prometheus-client` | Osobny profil produkcyjny |
| `db` | `sqlalchemy`, `aiosqlite`, `alembic`, `uuid6` | Osobny profil produkcyjny |
| `image-core` | `numpy`, `opencv-python`, `pillow`, `scipy`, `scikit-image`, `pyclipper`, `shapely`, `pandas`, `pdf2image`, `natsort`, `matplotlib`, `albumentations` | Wspólne przetwarzanie obrazów, bez Torcha |
| `runtime-onnx` | `onnxruntime-gpu`, `onnxscript`, `nvidia-cublas-cu12`, `nvidia-cuda-runtime-cu12`, `nvidia-cudnn-cu12`, `nvidia-cufft-cu12` | Production ML runtime dla ONNX, **Torch-free CUDA przez NVIDIA cu12 wheels** |
| `runtime-gguf` | Brak Python ML wheel; używa pinned `llama.cpp` binary cache | GGUF runtime nie powinien ciągnąć Torcha |
| `runtime-native` | Native/DLL bundles przez model catalog | OneOCR i podobne wyjątki native |
| `production` | `api-server`, `db`, `image-core`, `media`, `runtime-onnx`, `runtime-gguf`, `runtime-native`, `text-runtime`, `llm`, `tts` | Repo/install profile dla produkcyjnej aplikacji bez Torcha |
| `torch-cu128` / `cuda-runtime` | `torch`, `torchvision`, `nvidia-cublas-cu12`, `nvidia-cudnn-cu12` | Dev/test/export/fallback dla Mateusza, nie główny installer |
| `torch-models` | `accelerate`, `kornia`, `pytorch-metric-learning`, `segmentation-models-pytorch`, `spandrel`, `timm`, `torchsde`, `ultralytics` | Przejściowe PT engines, export i parity; docelowo redukować po migracji ONNX/GGUF |
| `lab-comfy` | `comfy-kitchen`, `comfy-aimdo`, ComfyUI submodule/path deps | Tylko lokalny lab/dev |
| `tts` | `edge-tts`, opcjonalnie `elevenlabs` | Osobny feature, niezależny od ML runtime |
| `media` | `av`, `static-ffmpeg` | Osobny feature dla audio/video/exportu |
| `archives` | `pikepdf`, `py7zr`, `rarfile` | Już osobne extra; zostawić jako feature |
| `gradio-ui` | `gradio` | Dev/demo UI, nie core installer |
| `local-dev` | `production`, `gradio-ui`, `torch-models`, `cuda-runtime` | Domyślny `uv sync` na workstation Mateusza |
| `spike` | `cuda-runtime` plus tymczasowe deps dodawane świadomie per eksperyment | Tylko konwersje i research |

Aktualny edit `pyproject.toml` wyniósł z base także API, DB, image stack, media, text runtime, translation AI i TTS. Base zostaje import-light; `uv sync` nadal jest lokalnym profilem CUDA przez `local-dev`, a installer dostaje `mangashift[production]` bez Torcha.

## Build vs Install vs Run

| Etap | Co ma się dziać | Czego nie wolno robić |
|---|---|---|
| Build wheel | Pakować kod `mangashift` | Vendorować Torch/ComfyUI do artefaktu |
| Install/setup | Wybrać profil i zainstalować deps | Mieszać profile bez jawnej decyzji |
| Run | Użyć przygotowanego env/cache | Uruchamiać `uv sync`, auto-download lub auto-update |
| Doctor | Sprawdzić profil i runtime | Wymagać Torcha w profilu ONNX-only |

Jeśli coś instaluje się przy starcie, to jest błąd workflow. W dev powodem bywa `uv run`, bo robi auto-sync. Preferowany run path ma omijać auto-sync i używać przygotowanego środowiska.

## Torch-free CUDA dla ONNX (production runtime)

Production user nie ma instalować Torcha tylko po to, żeby ORT widział `cublasLt64_12.dll`. Profil `runtime-onnx` ciągnie zestaw NVIDIA cu12 wheels, które dostarczają wszystkie wymagane DLL niezależnie od Torcha:

| Pakiet | Zawiera | Powód |
|---|---|---|
| `nvidia-cublas-cu12` | `cublas64_12.dll`, `cublasLt64_12.dll` | Wymagane przez ORT CUDA EP dla GEMM |
| `nvidia-cuda-runtime-cu12` | `cudart64_12.dll` | Runtime CUDA |
| `nvidia-cudnn-cu12` | `cudnn*9.dll` | Convolution / RNN kernels |
| `nvidia-cufft-cu12` | `cufft64_11.dll` (+ tranzytywnie `nvjitlink`) | FFT — wymagane przez ORT 1.18+ |

Bootstrap żyje w `mangashift/runtime/onnx_cuda.py` jako `prepare_onnxruntime_cuda()`. Funkcja jest **idempotentna** i **Torch-free** (nie importuje torch). Każdy ONNX backend wywołuje ją **przed** `import onnxruntime as ort` w swoim init path. Co robi:

1. Iteruje listę dystrybucji `nvidia-*-cu12` przez `importlib.metadata.distribution(name).files`. To omija problem z namespace package `nvidia.*`, który nie współpracuje z `importlib.resources.files()`.
2. Filtruje pliki po sufiksie (`.dll`, `.so`, `.dylib`) i deduplikuje katalogi nadrzędne.
3. Rejestruje katalogi przez `os.add_dll_directory` (Windows) i prependuje do `PATH` (Linux + Windows fallback).
4. Wywołuje `ort.preload_dlls(cuda=True, cudnn=True, msvc=True)` jeśli ORT 1.18+ ma to API.

Architektura **bez fallbacku**: każdy ONNX backend po utworzeniu sesji **weryfikuje** `session.get_providers()` i podnosi `DetectionModelError` jeśli `CUDAExecutionProvider` nie jest aktywny dla deklarowanego device='cuda'. Stara polityka cichego CPU fallback to bug, nie feature.

Empiryczna walidacja Torch-free w fresh venv (`uv pip install "mangashift[production]"`):
- Magi v3 ONNX init: 5 sesji na CUDA EP, 5623 ms, `'torch' in sys.modules == False`.
- Pozostałe ONNX backends (manga_text_segmentation, ctd, anime_text, hi_sam, lama, spandrel, comic_text_detector): bootstrap aktywny, CUDA EP egzekwowany.

## Magi v3 ONNX — wymóg light torch dep

Magi v3 wykorzystuje **Florence-2** (Microsoft VLM). Florence-2 processor (`processing_florence2.py`, `trust_remote_code=True`) ma `import torch` na top-level pliku — bez torcha się nie załaduje. Postprocess generated tokens → boxes/quads też operuje na `torch.Tensor`.

Implementacja: cała logika beam search Magi ONNX żyje w `mangashift/services/detection/engines/magi_v3/_onnx_inference.py` (port ze spike). 5 sesji ORT robi GPU compute, torch jest używany tylko do Florence processor i postprocess. Parity 100% potwierdzony empirycznie (Torch vs ONNX: identyczne `panels`, `texts`, `characters`, `tails` na base/00.png).

Wniosek dla production usera:

```bash
# Magi działa, GPU compute przez ORT, light CPU torch dep
uv pip install "mangashift[production,cpu]"
```

`cpu` extra dokłada `torch + torchvision` z indexu `pytorch-cpu` (~200 MB) zamiast pełnego CUDA torch (~3 GB). ORT robi heavy GPU compute przez nvidia cu12 wheels z `runtime-onnx`, torch CPU jest tylko helperem dla Florence processor i postprocess.

Pozostałe ONNX backendy (CTD, manga_text_segmentation, hi_sam, lama, anime_text, spandrel, comic_text_detector) działają zupełnie torch-free.

Trade-off wydajności: implementacja używa **CUDA IOBinding beam search** z pre-allocated ping-pong buffers dla self-cache. Wszystkie tensory zostają na GPU między beam steps (zero CPU↔GPU memcpy w pętli). Numpy fallback path zachowany dla CPU-only test scenarios.

Wydajność (RTX 5090, fp16, base/00.png, beam=3, 1024 max tokens):

| Faza | ONNX | Torch | Komentarz |
|---|---|---|---|
| `initialize()` (load + JIT warmup) | ~17 s | ~8 s | ONNX warmuje wszystkie kernele CUDA podczas init |
| **Każdy `detect()` (warm)** | **~2.5 s** | **~3 s** | ONNX 0.8× — szybszy niż Torch |
| Time-to-first-result | ~19.5 s | ~12 s | one-time różnica |
| Pipeline 50 stron | ~140 s | ~160 s | ONNX wygrywa dzięki szybszemu warm |

`initialize()` automatycznie wywołuje warmup pass (1× dummy detect na czarnym 768×768 obrazku) żeby ORT zJIT-ował wszystkie kernele CUDA przed pierwszym user-visible `detect()` — eliminuje 15 s "cold spike" przy pierwszej detekcji.

## Target Backend Matrix

| Obszar | Target production | Przejściowo dozwolone | Docelowa decyzja |
|---|---|---|---|
| Inpainting LaMa | ONNX | PT reference/fallback | ONNX default, PT tylko parity/export |
| Detection RT-DETR/AnimeText/MBS/MTS/CTD | ONNX | PT reference/fallback | ONNX default po parity gate |
| Hi-SAM/MAGI | ONNX albo GGUF jeśli realnie sensowne | PT reference/fallback | Migrować po potwierdzeniu jakości |
| OCR Paddle Manga | ONNX | PT preprocessing/reference, jeśli nazwane | ONNX-first bez ukrytego PT inference |
| OCR PaddleOCR-VL 1.5 | GGUF | Brak | `llama.cpp` pinned runtime (HTTP klient) |
| OCR OneOCR | Native DLL | Brak | Native exception |
| Upscaling | ONNX | Spandrel PT fallback/lab | Production bez ComfyUI importów |
| Flux | GGUF/native/diffusers future | ComfyUI lab | Deferred, nie blokuje V3 |

## Co Upraszczamy

| Obszar | Było | Ma być |
|---|---|---|
| VRAM manager | globalny manager, eviction, profile, retry | explicit error: brakuje VRAM albo backendu |
| Model tiers | decyzje runtime i eviction | metadata informacyjne, nie scheduler |
| Engine loading | top-level import ciężkich bibliotek | lazy import tylko w engine/profile |
| Fallbacki | ciche przełączanie lub auto-retry | jawny config i jasny błąd |
| ComfyUI | może wyciec przez import | tylko `lab-comfy` |
| Torch install | base dependency | profil dev/export/fallback |

## Kolejność Zmian

1. **Import audit gate:** lista modułów, które blokują `core` bez Torcha.
2. **Core lazy imports:** usunąć top-level `import torch` z `orchestrator`, `runtime` i shared configów.
3. **Fail-fast runtime:** zastąpić auto-eviction/retry prostymi błędami runtime.
4. **Pyproject split:** przenieść ciężkie deps z base do profili `production`, `local-dev`, `torch-models`, `lab-comfy`, `spike`.
5. **Doctor profiles:** `doctor --profile runtime-onnx` nie wymaga Torcha; `doctor --profile runtime-torch-cu128` sprawdza CUDA torch.
6. **Catalog assets:** jeden model może mieć `onnx`, `gguf`, `pt`, `native` assets z osobnym SHA256.
7. **Engine waves:** LaMa ONNX -> detection ONNX -> OCR ONNX/GGUF/native -> upscaling ONNX -> ComfyUI lab boundary.

## Acceptance Gates

- `python -c "import mangashift"` działa w profilu bez Torcha.
- `python -c "import mangashift.models"` działa w profilu bez Torcha.

## Environment Variables — Production Hardening

MangaShift nie pobiera modeli ML przy starcie aplikacji. Setup robi to świadomie. Dla 100% offline zachowania w runtime:

| Zmienna | Wartość | Co robi |
|---|---|---|
| `YOLO_OFFLINE` | `1` | Wyłącza wszystkie network calls Ultralytics (update check, font download, hub) |
| `YOLO_AUTOINSTALL` | `0` | Wyłącza auto `pip install` brakujących deps przy `from ultralytics import YOLO` |
| `HF_HUB_OFFLINE` | `1` | Wyłącza Hugging Face Hub network access — używa wyłącznie cache |
| `TRANSFORMERS_OFFLINE` | `1` | To samo dla biblioteki `transformers` |
| `LOGGER_MODE` | `SILENT` / `DEV` / `PROD` | Tryby logowania mangashift (patrz `mangashift/utils/logger.py`) |

`mangashift setup` ustawia `YOLO_OFFLINE=1` i `YOLO_AUTOINSTALL=0` w środowisku (ultralytics importowane lazy w detection engines). Jeśli aplikacja jest deployowana z mountowanym workspace, te zmienne **muszą** być exportowane przed startem.

## ComfyUI — Opt-in Only

ComfyUI nie jest production dependency. Nie ma go w `[production]` extra ani w `local-dev` group.

```bash
# Lab/dev opt-in (Mateusz workstation)
uv sync --group lab-comfy
```

Lab profile dodaje `comfy-kitchen`, `comfy-aimdo` i ComfyUI submodule path deps. Production install nigdy nie ciągnie ComfyUI, nawet tranzytywnie.

## Gated HF Repositories

Niektóre modele wymagają autentykacji HF i akceptacji warunków:

| Model | Repo | Status | Notatka |
|---|---|---|---|
| `flux_klein_9b` | `aoxo/Flux.1_Klein_9b` | Gated (HF 403) | Wymaga `huggingface-cli login` + zaakceptowania licencji w UI HF |
| `flux_klein_4b` | `aoxo/Flux.1_Klein_4b` | Public | OK |
| `magi_v3` | `ragavsachdeva/magi-v3` | Gated | Research access, akceptacja w UI HF |

Workflow dla gated modeli:

1. `huggingface-cli login` — paste write/read token z HF settings.
2. Wejdź na repo w UI HF, zaakceptuj license/terms.
3. Uruchom `mangashift models pull <id>` — registry użyje cached HF token.

Doctor check `huggingface_auth` wykrywa brak tokenu, ale nie sprawdza per-repo gating — błąd 403 pojawi się dopiero przy `models pull` z jasnym komunikatem.
- `doctor --profile runtime-onnx` wymaga ONNX Runtime, nie Torcha.
- Production service startup nie wykonuje `uv sync`, downloadu ani update runtime.
- Engine z brakującym backendiem rzuca jasny błąd z nazwą wymaganego profilu.
- Testy są podzielone na `core`, `runtime-onnx`, `runtime-torch`, `lab-comfy`.

## Decyzja V3

Nie utrwalamy obecnych engine'ów jako stałe `torch-only`. Traktujemy je jako **transitional**: każdy production engine ma docelowo przejść na ONNX, GGUF albo native runtime. Torch zostaje tylko tam, gdzie pomaga dowieźć konwersję, porównanie jakości albo lokalny research.



## Runtime VRAM Management

Runtime jest **explicit, refcount-based** — bez heurystyk, bez auto-evict, bez auto-quality-downgrade. RuntimeManager zarządza VRAM przez wyraźne `acquire`/`release` z `release_all` jako jedynym kompleksowym sweepem. Zachowuje się **fail-fast** zgodnie z preferencjami właściciela repo.

### Runtime invariants

| # | Zasada | Komentarz |
|---|---|---|
| 1 | VRAM **MUSI** wrócić do baseline po pipeline | post-pipeline `release_all` + `cleanup` jest obligatoryjny |
| 7 | `release_all` **NIE MOŻE** zabić `llama-server` | external subprocess jest poza scope refcount |
| 11 | Pipeline serializowany `Semaphore(1)` | `mangashift.api.main` opakowuje `pipeline_runner` |
| 12 | Aggressive ONNX cleanup | `ort_cleanup()` po każdym `release` i w `cleanup()` |
| 13 | Checksum verify on load | `MANGASHIFT_SKIP_CHECKSUM` dla dev |
| 14 | OS pressure response opt-in | `MANGASHIFT_OS_PRESSURE_RESPONSE` dla self-hosted produkcji |

### Zmienne środowiskowe

| Zmienna | Default | Działanie |
|---|---|---|
| `MANGASHIFT_VRAM_TELEMETRY` | `off` | `on`/`1`/`true` włącza emisję `runtime/*` zdarzeń telemetrii. |
| `MANGASHIFT_SKIP_CHECKSUM` | unset | Truthy (`1`/`on`/`true`/`yes`) pomija weryfikację SHA-256 — wyłącznie dev. |
| `MANGASHIFT_OS_PRESSURE_RESPONSE` | unset | Truthy włącza `OSPressureMonitor` (wątek daemon, `release_all` przy stresie OS). |

### CLI surface

```bash
mangashift runtime status [--json]
mangashift runtime unload <model_id> [--force]
mangashift runtime release-all [--force]
mangashift runtime cleanup
mangashift runtime defrag
```

### API surface

```text
GET  /api/v1/runtime/status        - admin only
POST /api/v1/runtime/release-all   - admin only, body: {"force": bool}
POST /api/v1/runtime/unload/{id}   - admin only, body: {"force": bool}
POST /api/v1/runtime/cleanup       - admin only
```

Praktyczny how-to + decyzja architektoniczna (refcount-only): [runtime-lifecycle.md](runtime-lifecycle.md).
