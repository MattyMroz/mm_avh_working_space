# Wzorzec architektoniczny MangaShift dla mm_avh

Raport referencyjny — mapuje strukturę projektu MangaShift (`C:\Users\MattyMroz\Desktop\PROJECTS\MangaShift`) jako materiał wyjściowy do przebudowy mm_avh (terminalowy CLI: ekstrakcja MKV → napisy → TTS lektor → merge). mm_avh ma być **prostszy** niż MangaShift: bez bazy danych, bez API/HTTP, bez frontendu, bez workera webowego, bez multi-userów.

Uwaga metodologiczna: dla dużych folderów (`external/` — ok. 6900 plików, `workspace/` — ok. 19500 plików) zbadano strukturę katalogów na 2-3 poziomach głębokości, nie enumerowano zawartości plików roboczych.

---

## 1. Pełne drzewo MangaShift

### 1.1 Root (`C:\Users\MattyMroz\Desktop\PROJECTS\MangaShift\`)

```
MangaShift/
├── .agents/, .claude/, .codex/, .superpowers/   — konfiguracja narzędzi AI-assist, nieistotne dla architektury
├── .github/                                     — CI workflows
├── .venv/, .uv-cache/, node_modules/            — środowiska/cache, standardowe
├── .pre-commit-config.yaml                      — hooki lint/format przed commitem
├── .env / .env.example                          — sekrety/config lokalny (dotenv)
├── .python-version                              — pin wersji Pythona dla uv/pyenv
├── main.py                                      — UWAGA: to NIE jest prawdziwy punkt wejścia aplikacji;
│                                                   to demo-skrypt wypisujący zainstalowane pakiety (rich/torch/numpy
│                                                   smoke test). Prawdziwy entry point to `mangashift` CLI
│                                                   (Typer app) zarejestrowany w pyproject.toml [project.scripts]
│                                                   → mangashift/cli/main.py:main
├── alembic.ini                                  — konfiguracja migracji DB (Alembic + SQLAlchemy) — [webowe/DB]
├── conftest.py                                  — globalny pytest hook: auto-tag testów markerem `unit`
│                                                   jeśli brak markera pyramid (unit/integration/e2e)
├── pyproject.toml                               — 27 tys. znaków: [project], [project.scripts] (entry pointy CLI),
│                                                   [project.optional-dependencies] (torch cpu/cu118/cu121 jako
│                                                   uv conflicts-groups), [tool.uv] (indeksy, workspace, sources),
│                                                   [tool.importlinter] (9 kontraktów architektonicznych — wymusza
│                                                   granice warstw), [tool.ruff], [tool.mypy], [tool.pytest],
│                                                   [tool.coverage]
├── uv.lock                                      — lockfile (3 MB — bardzo duży graf zależności ML)
├── ground_truth.json, coverage.json, tc.log     — artefakty audytów/testów, nieistotne architektonicznie
├── external/                                    — [KLUCZOWE] zewnętrzne binaria/modele/kod/fonty poza src (§4)
├── workspace/                                   — [KLUCZOWE] dane robocze runtime, oddzielone od kodu (§4)
├── scripts/                                     — [KLUCZOWE] skrypty pomocnicze/dev, uporządkowane wg celu (§4)
├── mangashift/                                  — właściwy pakiet źródłowy (§1.2)
├── frontend/                                    — [webowe — pominięte] SPA (Bun+Vite+React+Tauri), osobny projekt JS
├── comfyui/                                     — zvendorowany submodule ComfyUI (do inpaintingu FLUX) — narzędzie
│                                                   zewnętrzne uruchamiane jako subprocess, nie część architektury mangashift/
├── docs/                                        — dokumentacja: architecture/, guides/, services/, product/, reference/,
│                                                   archive/, brainstorms/, legal/, superpowers/ — standardy i decyzje projektowe
├── datasets/                                    — skrypty download/upload datasetów HF (README, data/, *.py) — nieistotne dla mm_avh
├── notebooks/                                   — Jupyter/Colab notebooki eksperymentalne (Hi-SAM, testy) — R&D, poza architekturą runtime
├── knowledge/                                   — pojedynczy plik `testing-mangashift.md`, notatki wiedzy projektowej
├── logs/                                        — zrotowane pliki logów aplikacji (*.jsonl / *.jsonl.zip) — runtime output, nie kod
├── test_examples/                                — luźne skrypty przykładowe/testowe (1.jpg, test.py) — R&D
└── tests/                                        — właściwy katalog testów (osobno od mangashift/models/tests itp.)
```

### 1.2 `mangashift/` (pakiet źródłowy)

```
mangashift/
├── bootstrap.py         — [KLUCZOWE] composition root: bootstrap() spina Settings → RuntimeManager →
│                           DB engine/sessionmaker → SecretsStore w jeden obiekt AppServices (§5)
├── errors.py             — bazowe klasy wyjątków aplikacji (hierarchia błędów wspólna dla wszystkich modułów)
├── cli/                  — [NAJWAŻNIEJSZE dla mm_avh] Typer CLI — punkt wejścia (§3, §5)
├── services/              — [NAJWAŻNIEJSZE] logika domenowa per-funkcja (tts, translation, ocr, detection...) (§3)
├── config/                — [KLUCZOWE] Settings (pydantic-settings), model_storage, llama_runtime (§5)
├── setup/                 — [KLUCZOWE] bootstrap środowiska: wizard, doctor (health-checks), config wizard (§5)
├── platform/              — [KLUCZOWE] wykrywanie OS/GPU/ścieżek/zależności (§5)
├── runtime/ (+llama/, vram/) — cykl życia modeli AI: refcounted manager, VRAM budget/policy, llama.cpp server (§6)
├── models/                — katalog modeli AI (catalog.py = registry 27 modeli, resolver = model_id → plik) (§7)
├── pipeline/               — kroki przetwarzania (step registry), woła services (§8); pipeline/persistence/ = DB-backed [pominięte]
├── input/                  — moduł wejścia: loaders/extractors/chunking/joiner/validators dla source pages
├── events/                 — broadcaster/emitters/protocols — event bus do raportowania postępu (np. dla frontend/WebSocket)
├── utils/                  — logger/, rich_console/, timer/, device.py, safe_fs.py, safe_path.py, secrets.py, _retry.py
├── db/                     — [webowe/DB — pominięte] SQLAlchemy models, migrations (alembic_db), repositories, uow.py
├── storage/                — [webowe/DB — pominięte, ALE storage/workspace.py wart obejrzenia — wzorzec resolve_workspace_root()]
├── retention/               — [webowe/DB — pominięte] scheduler.py, tasks.py — czyszczenie starych danych z bazy
├── api/                     — [HTTP/FastAPI — pominięte] REST routers, schemas, middleware, deps
├── worker/                  — [web/orchestracja — pominięte] job_worker.py — konsument kolejki zadań async
└── usecases/                 — [web/orchestracja — pominięte] warstwa use-case nad db/repositories (bubbles.py, chapters.py,
                                 export_cbz.py, jobs.py, pipeline.py, projects.py, users.py...) — orkiestracja wielu
                                 requestów HTTP/DB w jedną operację biznesową
```

---

## 2. Tabela: folder → rola → odpowiednik w mm_avh

| Folder MangaShift | Rola w MangaShift | Odpowiednik w mm_avh | Potrzebne w terminalówce? |
|---|---|---|---|
| `external/` | Zewnętrzne binaria, kod referencyjny, fonty, modele AI + manifest integralności (`model_hashes.json`) | `mm_avh/bin/` (ffmpeg, mkvtoolnix, espeak/piper itd.) | **Tak, uproszczone** — bez `code/` (badawczy vendoring), zostaje `bin/` + ewentualnie `models/` jeśli mm_avh użyje lokalnych modeli TTS/STT. Manifest integralności (hash pliku) wart skopiowania w minimalnej formie. |
| `workspace/` | Dane robocze runtime: input/output/cache/tmp/logs/exports, oddzielone od kodu | `mm_avh/working_space/` | **Tak** — dokładnie to mm_avh już chce zrobić; wzorzec podfolderów (`input/`, `output/`, `cache/`, `tmp/`, `logs/`) jest bezpośrednio przenośny. |
| `scripts/` | Skrypty pomocnicze dev: audits, examples, maintenance, probes, runtime (smoke/measure), smoke, tests | `mm_avh/temp/` (dziś chaos) → docelowo `mm_avh/scripts/` | **Tak, mocno uproszczone** — mm_avh nie potrzebuje `probes/`, `audits/production_audit/` (to R&D dla wielu modeli AI). Wystarczy 2-3 podfoldery: `maintenance/` (jednorazowe skrypty), `smoke/` (szybki e2e test). |
| `cli/` | Typer app: `main.py` (rejestr subcommand), `run_cmd.py`, `admin_cmd.py`, `models_cmd.py`, `runtime_cmd.py`, `llm_cmd.py`, `wizard_runner.py` | mm_avh już ma `start.py` jako główny punkt wejścia | **Tak, ale mm_avh zostaje przy pojedynczym `start.py`** — nie trzeba osobnego pakietu `cli/` z wieloma plikami subcommand, chyba że liczba komend/flag urośnie. Wzorzec "cienki plik main.py rejestrujący subkomendy" jest wart naśladowania jeśli `start.py` zacznie puchnąć. |
| `services/` | Logika domenowa per-funkcja: `tts/`, `translation/`, `ocr/`, `detection/`, `inpainting/`, `text_render/`, `image_processing/`, `video_render/`, `video_sequence/`, `secrets/` | `mm_avh/services/` (nowy katalog zamiast płaskich modułów) | **Tak, to najważniejsza rekomendacja** — mm_avh ma dziś god-files (np. `subtitle_to_speech.py` 1196 linii); rozbicie na `services/tts/`, `services/subtitles/`, `services/extraction/`, `services/merge/` z registry per-silnik to bezpośrednie lekarstwo. |
| `config/` | `Settings` (pydantic-settings, env+`.env`), `model_storage.py`, `llama_runtime.py` | `mm_avh/config/` | **Tak, ale bardzo uproszczone** — jeden plik `settings.py` z `BaseSettings`, bez osobnych plików per runtime backend (mm_avh nie ma llama.cpp servera). |
| `setup/` + `doctor_checks/` | Wizard konfiguracyjny + 15 health-checków (Python, uv, GPU, torch/CUDA match, modele, dysk, HF auth, porty API...) | `mm_avh/setup/` (nowy) | **Tak, mocno uproszczone** — mm_avh potrzebuje góra 4-5 checków: ffmpeg/mkvtoolnix na PATH, model TTS obecny, miejsce na dysku, Python OK. Bez checków API/portów/DB/GPU-CUDA-match (chyba że TTS lokalny wymaga GPU). |
| `platform/` | Wykrywanie GPU (`gpu_detect.py`), instalator torch (`torch_installer.py`), preflight checks (`checks.py`: uv/python/disk/network/proxy/lockfile), typy (`types.py`), comfyui_paths.py | `mm_avh/platform/` (nowy, mały) | **Uproszczone** — mm_avh potrzebuje wykrywania OS (Windows/Linux ścieżki binarek) i ewentualnie GPU tylko jeśli lokalny TTS/STT tego wymaga. Bez torch_installer (chyba że mm_avh instaluje ciężkie zależności ML). |
| `models/` | Katalog modeli AI: `catalog.py` (27 modeli, registry), `resolver.py` (model_id → plik), `downloader.py`, `core/` (integrity, config, engine) | `mm_avh/models/` (jeśli lokalny TTS/STT z wagami) | **Uproszczone/opcjonalne** — potrzebne tylko jeśli mm_avh używa lokalnych modeli (np. Whisper, lokalny TTS). Jeśli tylko API-based (ElevenLabs, edge-tts), ten folder w ogóle niepotrzebny. |
| `runtime/` (+`vram/`, `llama/`) | Refcounted lifecycle manager modeli AI: acquire/release, VRAM budget/policy/pooling, NVML, llama.cpp server manager | — | **Przerost dla mm_avh** — patrz §6, ocena szczera poniżej. Ładowanie 1 modelu sekwencyjnie na raz nie potrzebuje refcount+VRAM policy engine. |
| `pipeline/` | Step registry — kroki (`detection/`, `ocr/`, `translation/`, `tts/`, `inpainting/`, `sequence/`) wołają services, `core/` (runner, composition, step_registry) | `mm_avh/pipeline/` (opcjonalnie) | **Idea warta naśladowania, ale bez ceremonii** — mm_avh ma liniowy pipeline (ekstrakcja→napisy→tts→merge), niekoniecznie potrzebuje generycznego step-registry z `_proto_step_registry.py`, `waving.py`, `scope_resolver.py`. Prosta sekwencja funkcji z jasnymi granicami wystarczy. |
| `input/` | Loaders/extractors/chunking/joiner/validators dla source pages (manga) | częściowo pokrywa się z tym, co robi już `mm_avh` (ekstrakcja MKV) | Koncepcyjnie tak, ale nazewnictwo/domena inna — mm_avh ma już własny moduł ekstrakcji. |
| `events/` | Broadcaster/emitters do raportowania postępu (dla frontendu/WebSocket) | mm_avh już ma paski postępu (live) | **Nie w tej formie** — mm_avh nie potrzebuje event-bus/broadcaster dla WebSocket; wystarczy bezpośrednie wywołanie funkcji progress callback (już działa wg ostatnich commitów). |
| `utils/` | `logger/`, `rich_console/`, `timer/`, `device.py`, `safe_fs.py`, `safe_path.py`, `secrets.py` | mm_avh już to ma (branch `feature/utils-migration`) | Już zaadresowane, bez zmian. |
| `db/`, `storage/`, `retention/` | SQLAlchemy models/migrations/repositories/UoW, filesystem storage abstrakcja, retention scheduler | — | **[webowe/DB — pominięte, bo mm_avh to terminalówka]** |
| `api/` | FastAPI routers/schemas/middleware | — | **[HTTP — pominięte]** |
| `worker/`, `usecases/` | Async job worker + use-case orkiestracja nad wieloma requestami | — | **[web/orchestracja webowa — pominięte]** |
| `frontend/` | Bun+Vite+React+Tauri SPA | — | **[webowe/frontend — pominięte]** |

---

## 3. Wzorzec serwis + engine registry

To najważniejszy wzorzec do przeniesienia. Zilustrowany na `services/tts/`.

### 3.1 Szkielet struktury plików (jedna domena)

```
mangashift/services/tts/
├── __init__.py
├── _config_base.py       — bazowa klasa ProviderConfig (wspólna dla wszystkich silników)
├── config.py              — TtsConfig — facade config, zawiera pola per-silnik (supertonic, elevenbytes, edge, elevenlabs)
├── constants.py
├── converter.py            — konwersja formatu audio (ensure_output_format)
├── errors.py                — TtsError, TtsConfigError, TtsEngineError
├── output.py                 — audio_filename(), ensure_output_dir()
├── protocols.py               — TtsSynthesisOptionsProvider Protocol
├── provider.py                 — TtsProvider Protocol (interfejs, który MUSI spełnić każdy silnik)
├── service.py                  — TtsService — jedyny publiczny fasadowy obiekt (§3.2)
├── types.py                     — AudioResult, TtsJob, VoiceInfo, BatchReport, EngineOptions...
└── engines/
    ├── __init__.py              — REJESTR: engine_id → (module_path, class_name, config_attr) (§3.3)
    ├── edge/                     — jeden konkretny silnik = jeden podfolder
    │   ├── __init__.py
    │   ├── config.py              — EdgeConfig(ProviderConfig), env_prefix="TTS_EDGE_"
    │   ├── constants.py
    │   ├── options.py              — EdgeSynthesisOptions + walidacja opcji specyficznych dla silnika
    │   ├── service.py               — EdgeTtsService — implementacja TtsProvider
    │   └── types.py
    ├── elevenbytes/  (ten sam szkielet)
    ├── elevenlabs/   (ten sam szkielet)
    └── supertonic/   (ten sam szkielet + onnx_backend.py, pre/postprocessing.py — bo to lokalny model ONNX)
```

Ten sam szkielet powtarza się identycznie w `services/translation/engines/{google,deepl,llm}/` — **to jest reguła, nie wyjątek**: każda domena (tts, translation, ocr, detection, inpainting) ma `engines/__init__.py` jako registry + jeden podfolder na silnik.

### 3.2 Rejestr — "zero if-ów per silnik"

Kod rejestru (`mangashift/services/tts/engines/__init__.py`), pełny — 85 linii, kluczowa część:

```python
TtsEngineId = Literal["supertonic", "elevenbytes", "edge", "elevenlabs"]

_REGISTRY: Final[dict[TtsEngineId, tuple[str, str, str]]] = {
    "supertonic": ("mangashift.services.tts.engines.supertonic", "SupertonicService", "supertonic"),
    "elevenbytes": ("mangashift.services.tts.engines.elevenbytes", "ElevenBytesService", "elevenbytes"),
    "edge": ("mangashift.services.tts.engines.edge", "EdgeTtsService", "edge"),
    "elevenlabs": ("mangashift.services.tts.engines.elevenlabs", "ElevenLabsService", "elevenlabs"),
}
# klucz: engine_id → (ścieżka modułu, nazwa klasy, atrybut configu na TtsConfig)

def available_engine_ids() -> tuple[TtsEngineId, ...]:
    return tuple(_REGISTRY)

def create_engine(config: TtsConfig, *, engine_id: str) -> TtsProvider:
    if engine_id not in _REGISTRY:
        raise TtsConfigError(f"Unknown TTS engine: {engine_id!r}. Available: {sorted(_REGISTRY)}")
    module_path, class_name, config_attr = _REGISTRY[engine_id]
    engine_config = getattr(config, config_attr)          # np. config.edge -> EdgeConfig
    module = importlib.import_module(module_path)           # lazy import — silnik ładowany dopiero gdy potrzebny
    engine_cls = getattr(module, class_name)
    return engine_cls(engine_config)
```

Efekt: dodanie nowego silnika TTS = dodać jeden wpis do `_REGISTRY` + jeden podfolder `engines/<nowy>/` implementujący `TtsProvider`. **Zero zmian w `service.py`, zero `if engine_id == "..."` w kodzie wywołującym.** Lazy import (`importlib.import_module`) oznacza, że ciężkie zależności (np. torch dla supertonic) nie są importowane, dopóki dany silnik nie zostanie wybrany — istotne, bo `edge`/`elevenlabs` (czysto sieciowe) startują natychmiast bez ładowania ONNX runtime.

`TtsService` (fasada, `service.py`, 406 linii) nie zna żadnego konkretnego silnika — woła wyłącznie `create_engine(config, engine_id=...)` i cache'uje zbudowane instancje w `self._engines: list[TtsProvider]`. Silniki budowane leniwie (`_ensure_engine`) przy pierwszym użyciu danego `engine_id`.

### 3.3 Przykład konkretnego silnika (`edge/service.py`, 250 linii)

Implementuje Protocol `TtsProvider`: `engine_id`, `engine_type`, `is_available`, `vram_mb`, `synthesize()`, `list_voices()`, `load_model()`/`unload_model()` (no-op dla API-silników), `close()`. Import biblioteki (`edge_tts`) dzieje się wewnątrz metody, nie na górze pliku — dodatkowy poziom lazy-loadingu.

Config silnika (`edge/config.py`) dziedziczy po wspólnym `ProviderConfig` i ustawia własny `env_prefix` (`TTS_EDGE_`) — każdy silnik ma osobną przestrzeń zmiennych środowiskowych, bez kolizji.

### 3.4 Dlaczego to pasuje do mm_avh

mm_avh realistycznie użyje 2-3 silników TTS (np. edge-tts, ElevenLabs, może lokalny piper) i może 1-2 silniki STT/napisów (Whisper lokalny, może API). Rejestr string→klasa z lazy importem to jest dokładnie tyle złożoności, ile potrzeba — nie trzeba kopiować całej reszty (Protocol classes, `TtsSynthesisOptionsProvider`, batch processing z semaforami, voice cache TTL) jeśli mm_avh nie ma takich wymagań (np. brak potrzeby cache'owania listy głosów na 5 minut, bo to nie serwer obsługujący wielu userów).

---

## 4. Wzorzec external/ + workspace/ + scripts/

### 4.1 `external/` — zewnętrzne zasoby poza kodem źródłowym

```
external/
├── README.md              — dokumentacja HF publish scope + 11-regułowa konwencja nazewnicza modeli
├── model_hashes.json       — manifest integralności: schema_version, per-zasobowy SHA256, rozmiar, format (onnx/pt/gguf/comfy/native)
├── bin/
│   └── llama.cpp/           — skompilowane binarki narzędzi zewnętrznych
├── code/                     — [research-only, jawnie wykluczone z publikacji] kopie referencyjnych repo (IOPaint, koharu,
│                               manga-image-translator...) do podglądu implementacji, NIE importowane przez mangashift/
├── fonts/                     — czcionki używane przy renderowaniu tekstu (Bubble Sans.otf)
└── models/
    ├── detection/, inpainting/, ocr/, tts/, upscaling/   — modele pogrupowane per kategoria zadania
    └── (każdy model: podfolder per-format: pt/, onnx/, gguf/, safetensors/, src/.gitkeep)
```

Kluczowa zasada z README: **kebab-case, format-per-subfolder, drop hash z nazwy upstream (wersjonowanie przez manifest, nie nazwę pliku)**. `model_hashes.json` (schema v2) grupuje zasoby po ścieżce i formacie, z polem `main_sha256` per zasób — runtime (`mangashift/runtime/manager.py`, `_MODEL_HASHES_PATH`) czyta ten plik do weryfikacji integralności przed załadowaniem modelu (`checksum.py`: `load_manifest`, `verify_sha256`).

**Dla mm_avh**: `external/` → `mm_avh/bin/` z podfolderami per-narzędzie (`bin/ffmpeg/`, `bin/mkvtoolnix/`, `bin/espeak/` czy podobnie). Manifest integralności (`bin_hashes.json` z SHA256 per binarka) jest tani do zaimplementowania i wart skopiowania — chroni przed cichym uszkodzeniem/podmianą binarki. `code/` (badawczy vendoring konkurencyjnych repo) i rozbudowany `models/` z 27 wagami AI to nie jest wzorzec do kopiowania 1:1 — mm_avh potrzebuje co najwyżej 3-4 binarki + ewentualnie 1 model TTS/STT lokalny.

### 4.2 `workspace/` — dane robocze runtime

```
workspace/
├── input/            — pliki wejściowe (podfoldery per typ/źródło: manga/, manhwa/, uploads/, examples/, test/...)
├── output/             — wyniki przetwarzania, MOCNO rozgałęzione (40+ podfolderów — każdy eksperyment/test miał
│                         własny podfolder output/<nazwa_eksperymentu>/ — to organiczny narost, nie projektowany wzorzec)
├── projects/            — trwałe "projekty" użytkownika (odpowiednik sesji/zadania)
├── cache/                — cache międzysesyjny
├── debug/                 — artefakty debugowania (np. inpaint_frames/)
├── mask_artifacts/, raw_masks/  — dane binarne specyficzne dla domeny (maski AI) — nieistotne dla mm_avh
├── exports/                — finalne eksporty użytkownika
├── logs/                    — logi per-sesja (osobne od root /logs — to raczej runtime-specific)
├── tmp/                      — pliki tymczasowe, czyszczone
└── mangashift.db*             — plik SQLite (baza dev) — [webowe/DB, nieistotne dla mm_avh]
```

Resolucja root workspace (`mangashift/storage/workspace.py`, wzorzec wart 1:1 kopiowania):

```python
ENV_WORKSPACE_ROOT: Final[str] = "MANGASHIFT_WORKSPACE_ROOT"
DEFAULT_SUBDIRS: Final[tuple[str, ...]] = ("input", "projects", "exports", "cache", "tmp")

def resolve_workspace_root() -> Path:
    """Precedence: env var override, else <repo_root>/workspace inferred from module location."""
    override = _read_env_override()
    if override is not None:
        return override
    return _infer_repo_workspace()  # szuka pyproject.toml w parents, żeby ustalić repo root
```

**Dla mm_avh**: `workspace/` → `mm_avh/working_space/`. Wart skopiowania: (1) env-var override (`MM_AVH_WORKSPACE_ROOT`) + fallback na inferencję z lokalizacji pliku, (2) płaska, mała lista `DEFAULT_SUBDIRS` (mm_avh potrzebuje realnie: `input/`, `output/`, `tmp/`, `cache/`, `logs/` — **nie** 40+ eksperymentalnych podfolderów `output/<nazwa>/`, to jest patologia narosła w MangaShift przez lata eksperymentów R&D, nie wzorzec do naśladowania). Ostrzeżenie: `workspace/output/` w MangaShift jest przykładem **czego unikać** — brak dyscypliny sprzątania zostawił dziesiątki jednorazowych folderów eksperymentalnych.

### 4.3 `scripts/` — skrypty pomocnicze/dev

```
scripts/
├── README.md
├── model_manager.py, bench_detection_visual.py, ... — luźne skrypty top-level (mieszanka, brak pełnej dyscypliny)
├── audits/production_audit/        — audyty jakości produkcyjnej
├── examples/processing_pipeline/    — przykłady użycia pipeline
├── maintenance/                      — skrypty jednorazowe/utrzymaniowe: audit_models.py, rename_external_models.py,
│                                       reorganize_external_models.py, sync_hf_repo.py, fresh_install_smoke.ps1
├── probes/                            — eksperymenty R&D: experiments/, inpainting/, ocr/, onnx_export_spike/,
│                                        processing_pipeline/, tools/, vram_benchmarks/, legacy/
├── runtime/                            — measure.py, smoke_e2e.py — pomiary wydajności runtime
├── smoke/                               — install_smoke.ps1/.sh — smoke test instalacji
└── tests/smoke/                          — testy typu smoke (osobno od głównego tests/)
```

**Ocena szczera**: `scripts/` w MangaShift samo w sobie nie jest wzorem porządku — jest mieszanką (root ma luźne pliki obok podfolderów), `probes/` to typowy śmietnik eksperymentów R&D nagromadzony przez miesiące. Wartość dla mm_avh to **sama zasada podziału wg celu** (maintenance vs smoke vs examples), nie kopiowanie tej konkretnej struktury. Dla mm_avh sugerowany minimalny podział: `scripts/maintenance/` (jednorazowe migracje/naprawy) + `scripts/smoke/` (szybki ręczny test e2e) — bez `probes/`, `audits/`, `examples/` dopóki nie pojawi się realna potrzeba.

---

## 5. Wzorzec bootstrap/config/setup

### 5.1 Start aplikacji

Prawdziwy punkt wejścia to **nie** `main.py` (root) — to demo-skrypt (`_print_banner`, test pakietów rich/torch/numpy). Faktyczny entry point rejestrowany w `pyproject.toml [project.scripts]` wskazuje na `mangashift/cli/main.py:main`:

```python
app: typer.Typer = typer.Typer(name="mangashift", help="...", no_args_is_help=True)

_register_run(app, _console)      # mangashift run — exec Python w venv bez uv sync
_register_llm(app, _console)      # mangashift llm — subkomendy LLM
admin_cmd.register(app, _console)  # mangashift setup/doctor/config
runtime_cmd.register(app, _console) # mangashift runtime — status modeli
models_cmd.register(app, _console)  # mangashift models — list/verify/pull/fix/sync

def main() -> None:
    from dotenv import load_dotenv
    load_dotenv(override=False)   # .env ładowany, ale shell env wygrywa (production safety)
    app()
```

Rejestracja subcommand dzieje się przez `register(app, console)` wywoływane raz na module-level — każdy plik `*_cmd.py` eksportuje funkcję `register`, żadnego globalnego stanu.

### 5.2 Config — `Settings` przez pydantic-settings

`mangashift/config/settings.py` — pojedyncza klasa `Settings(BaseSettings)`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",
                                       case_sensitive=False, extra="ignore")
    debug: bool = Field(default=False)
    mask_artifact_root: Path = Field(default_factory=lambda: _default_under_workspace("mask_artifacts"))
    use_gpu: bool = Field(default=True)

    def model_post_init(self, __context):
        if self.debug_persist_raw_masks:
            self.raw_mask_root.mkdir(parents=True, exist_ok=True)
```

Wzorzec: env vars + `.env` automatycznie, `Path` z `default_factory` odwołującym się do `resolve_workspace_root()`, katalogi tworzone w `model_post_init` tylko gdy faktycznie potrzebne. Każdy serwis (np. `TtsConfig`) ma **własną** klasę configu z osobnym `env_prefix`, a nie jeden gigantyczny `Settings` — to skalowalny wzorzec unikający jednego pliku 500+ linii z polami wszystkich domen.

### 5.3 Setup — wizard + doctor (health checks)

`mangashift/setup/`: `wizard.py` (interaktywny setup — wybór torch backendu cpu/cuda), `config.py` (`MangaShiftConfig`, `load_config`/`config_path` — trwały config w `%APPDATA%/mangashift/config.toml`, niezależny od `.env`), `doctor.py` (orchestrator), `doctor_checks/` (moduły per-kategoria: `env.py`, `gpu.py`, `models.py`, `api.py`).

`run_doctor()` uruchamia **15 checków współbieżnie** przez `asyncio.gather`, każdy check to czysta async funkcja zwracająca `DoctorCheck` (nie rzuca wyjątków — raportuje `passed=False` + `severity`). Lista checków: wersja Pythona, uv na PATH, lockfile drift, GPU detection, torch/CUDA match, ONNX Runtime CUDA EP, llama binary, integralność modeli (SHA256), miejsce na dysku, HF auth token, ComfyUI subprocess reachable, layout repo (`external/`, `workspace/`), pyproject.toml integrity, port API bindable, orphan models.

Osobno `mangashift/platform/checks.py` ma **inny**, bardziej podstawowy zestaw sync checków (`check_uv_binary`, `check_python_version`, `check_disk_space`, `check_network_reachable`, `check_proxy_env`, `check_no_conflicting_torch`, `check_extra_defined`, `check_lockfile_sync`) — to preflight (przed `uv sync`), doctor to postflight (po instalacji, runtime). Wzorzec: `CheckResult`/`DoctorCheck` to prosty dataclass z `name`, `passed`, `severity`, `message`, `suggestion`, `details` — jednolity format raportowania niezależnie od tego co sprawdzają.

**Dla mm_avh**: wart naśladowania 1:1 — jeden `doctor.py` z listą async (lub sync, mm_avh nie musi być async) checków zwracających jednolity `CheckResult`. Realistyczna lista dla mm_avh: ffmpeg na PATH, mkvtoolnix (mkvextract) na PATH, model TTS/klucz API obecny, miejsce na dysku, working_space/ ma prawidłową strukturę. To może być **jeden plik** `setup/doctor.py` z 5 funkcjami — nie potrzeba `doctor_checks/` jako osobnego pakietu z podziałem na env/gpu/models/api, chyba że lista checków przekroczy ~10.

### 5.4 Platform — wykrywanie środowiska

`mangashift/platform/`: `gpu_detect.py` (wykrywa CUDA/MPS/CPU), `torch_installer.py` (instaluje właściwy wariant torch), `comfyui_paths.py` (ścieżki do zvendorowanego ComfyUI), `types.py` (`TorchBackend` enum, `CheckResult`, `CheckSeverity`).

**Dla mm_avh**: potrzebne tylko jeśli lokalny model TTS/STT wymaga GPU — wtedy proste `platform/gpu_detect.py` (CUDA dostępne tak/nie) wystarczy. `torch_installer.py` i `comfyui_paths.py` to specyfika MangaShift (ciężki multi-backend ML stack) — zbędne dla mm_avh.

### 5.5 Bootstrap — composition root

`mangashift/bootstrap.py`, funkcja `bootstrap(*, debug, use_gpu, settings, db_settings, **overrides) -> AppServices`:

```python
def bootstrap(...) -> AppServices:
    load_dotenv(override=False)
    settings = settings or Settings(**overrides)
    setup_mode(LoggerMode.DEV if settings.debug else LoggerMode.PRODUCTION)
    device = get_device(force_cpu=not settings.use_gpu)
    return AppServices(settings=settings, device=device, db_settings=db_settings or DbSettings())
```

`AppServices` (dataclass) w `__post_init__` spina: `RuntimeManager` (model lifecycle), DB engine+sessionmaker (`db.session`), `SecretsStore`, konfiguruje globalny `HubConfig` dla resolvera modeli. Udostępnia fabryki wyższego poziomu (`build_detection_runner()`, `build_automatic_runner()`) które składają pipeline runnery z już-wdrożonych zależności (dependency injection ręczne, bez frameworka DI).

**Dla mm_avh**: wzorzec "jedna funkcja `bootstrap()` zwraca jeden obiekt ze wszystkimi zależnościami" jest wart naśladowania, ale bez DB engine/sessionmaker/SecretsStore-jako-osobnej-warstwy. Minimalna wersja dla mm_avh: `bootstrap() -> AppContext` zawierający `Settings`, wykryte ścieżki binarek, ewentualnie `device` info — kilkanaście linii, nie 209 jak w MangaShift.

---

## 6. Runtime (cykl życia modeli) — co jest przerostem dla mm_avh

`mangashift/runtime/` zarządza modelami AI ładowanymi do VRAM/RAM z refcountingiem:

- `manager.py` — `RuntimeManager.acquire()` (context manager, bump refcount, unload gdy refcount==0), `release()`/`release_all()`, fail-fast static fit check przed załadowaniem (`vram.policy.fits`), rzuca `InsufficientVramError` ze strukturalną sugestią.
- `vram/` — `budget.py` (wykryty budżet VRAM), `policy.py` (czy model się zmieści), `live.py`/`nvml.py` (odczyt na żywo przez NVML), `hardware_tier.py`, `_units.py`.
- `llama/` — osobny podsystem do zarządzania serwerem `llama-server` (binary_resolver, client, manager, registry) — dla lokalnych LLM (Florence-2, Qwen w GGUF).
- `checksum.py` — weryfikacja SHA256 modelu przed użyciem (czyta `external/model_hashes.json`).
- `pressure.py`, `telemetry.py` — monitoring presji pamięci i telemetria ładowania.

**Ocena wprost**: to jest zaprojektowane pod scenariusz "wiele modeli AI (27 w katalogu), różne rozmiary (0MB-29GB), na maszynie z ograniczonym VRAM, gdzie trzeba decydować co się zmieści równocześnie, z automatycznym unload gdy nikt nie trzyma referencji". mm_avh ładuje **jeden model sekwencyjnie na raz** (ekstrakcja → napisy → TTS → merge, kroki liniowe, nie równoległe). Dla takiego przypadku:

- **Przerost, pominąć całkowicie**: refcounting (`acquire`/`release` z licznikiem), `vram/policy.py` (fitting wielu modeli naraz), `vram/live.py`+`nvml.py` (odczyt VRAM na żywo do podejmowania decyzji o współbieżnym ładowaniu), `pressure.py` (presja pamięci przy wielu modelach), `llama/` (cały podsystem serwera LLM — mm_avh nie hostuje lokalnego LLM jako serwera).
- **Warte rozważenia w mikro-formie**: `checksum.py` (weryfikacja integralności binarki/modelu przed użyciem — to tani, jednorazowy check, nie wymaga refcount systemu). Prosty `load_model()`/`unload_model()` bez menadżera — po prostu funkcja, która ładuje model na czas jednego kroku i zwalnia go w `finally`.

Krótko: cały `runtime/manager.py` + `vram/` (ok. 15 plików) sprowadza się dla mm_avh do **kilku linii** — `with contextlib.ExitStack()` albo zwykły `try/finally` wokół załadowania jednego modelu na czas jednego kroku pipeline'u. Nie ma potrzeby żadnej klasy zarządzającej.

---

## 7. Models (katalog modeli AI)

`mangashift/models/catalog.py` — `MODEL_CATALOG: Final[...]` = rejestr 27 `ModelSpec` (detection/ocr/inpainting/upscaling/tts), każdy z `Resource`/`ResourceAsset`/`ResourceFile` opisującym per-format pliki (pt/onnx/gguf/safetensors), SHA256, rozmiar, ścieżkę HF. `resolver.py` mapuje `model_id` → fizyczna ścieżka pliku na dysku, uwzględniając `HubConfig` (repo HF + base_dir) skonfigurowany raz w `bootstrap.py`. `downloader.py` ściąga brakujące wagi z Hugging Face Hub. `core/` zawiera fundamenty: `engine.py` (silnik resolvera), `integrity.py` (weryfikacja hash), `config.py` (`HubConfig`), `errors.py`, `callbacks.py` (progress podczas pobierania), `types.py`.

**Dla mm_avh**: potrzebne tylko jeśli lokalny model (np. Whisper do transkrypcji, lokalny TTS jak Piper) wymaga pobierania wag i weryfikacji. Jeśli tak — wystarczy: jeden mały słownik `model_id -> (url, sha256, local_path)` + funkcja `ensure_model_downloaded(model_id)`. Cały aparat `ModelSpec`/`Resource`/`ResourceAsset`/`ResourceFile` (rozdzielenie na format/wariant/część) to przerost — MangaShift potrzebuje tego bo ma 27 modeli w 5 formatach z multi-part strukturami (np. Hi-SAM ma osobny encoder/decoder per wariant); mm_avh raczej ma 1-3 modele total.

---

## 8. Pipeline (step registry) — idea

`mangashift/pipeline/core/` zawiera generyczny silnik kroków: `step_registry.py`, `runner.py`, `composition.py` (składanie runnera z wstrzykniętych zależności), `context.py` (per-run kontekst), `ordering.py`, `scope_resolver.py`, `protocols.py` (interfejs kroku). Każda domena (`detection/`, `ocr/`, `translation/`, `tts/`, `inpainting/`, `sequence/`) ma własny `step.py` implementujący ten protokół i (w niektórych przypadkach) `persistence.py` do zapisu wyników do DB — **`persistence/` we wszystkich domenach to warstwa webowa/DB, pominięta**.

Idea: krok pipeline'u to cienka warstwa, która (1) bierze dane z poprzedniego kroku, (2) woła odpowiedni `Service` (z §3) z odpowiednim `engine_id`, (3) zwraca ustrukturyzowany wynik do następnego kroku. Sam runner nie zna szczegółów domeny — woła kroki w kolejności zdefiniowanej przez konfigurację presetu.

**Dla mm_avh**: idea "krok = adapter między pipeline a service, service nie wie nic o pipeline" jest dobra i warta zachowania jako zasada projektowa. Natomiast generyczny, konfigurowalny step-registry z `scope_resolver.py`/`waving.py`/`_proto_step_registry.py` (te nazwy sugerują sporo elastyczności pod różne presety/warianty przebiegu) to przerost — mm_avh ma **jedną**, liniową sekwencję (ekstrakcja → transkrypcja/napisy → tłumaczenie(?) → TTS → merge), niekoniecznie potrzebuje w pełni generycznego rejestru kroków z dynamicznym porządkowaniem. Wystarczy moduł `pipeline.py` z funkcją `run(config) -> Result`, która woła kolejno 4-5 funkcji kroków — bez abstrakcji rejestru, dopóki nie pojawi się realna potrzeba wielu wariantów przebiegu.

---

## 9. Pozostałe foldery (krótko)

- `mangashift/input/` — loaders/extractors/chunking/joiner/validators/manager dla źródłowych stron mangi; koncepcyjnie bliskie temu co mm_avh robi przy ekstrakcji z MKV, ale inna domena — nie kopiować 1:1, tylko podejście (osobne pliki `loaders.py`/`validators.py`/`types.py` zamiast jednego god-file).
- `mangashift/events/` — `broadcaster.py`/`emitters.py`/`protocols.py`/`types.py`, event bus do raportowania postępu w stronę frontendu (WebSocket). mm_avh już ma działające paski postępu bez event-busa (patrz commity `8b41011`, `c790cf7` na branchu) — nie replikować.
- `mangashift/utils/` — `logger/`, `rich_console/`, `timer/`, `device.py`, `safe_fs.py`, `safe_path.py`, `secrets.py`, `_retry.py`. mm_avh jest w trakcie migracji własnego `utils/` (branch `feature/utils-migration`) — ten folder MangaShift już był punktem odniesienia, bez zmian w rekomendacji.

Pominięte świadomie (webowe/DB, wypisane dla kompletności):
- `mangashift/db/` — SQLAlchemy models, `alembic_db/` (migracje), `repositories/`, `uow.py` (Unit of Work), `pragmas.py`, `seeds.py`.
- `mangashift/storage/` — `archive.py`, `checksums.py`, `filesystem.py`, `layout.py`, `paths.py`, `protocols.py`, `tokens.py` (poza `workspace.py`, opisanym w §4.2 — ten jeden plik jest wart wzorca).
- `mangashift/retention/` — `scheduler.py`, `tasks.py` — czyszczenie starych rekordów DB.
- `mangashift/api/` — FastAPI: `routers/`, `schemas/`, `middleware/`, `deps/`, `main.py`, `settings.py`.
- `mangashift/worker/` — `job_worker.py`, `__main__.py` — konsument kolejki zadań.
- `mangashift/usecases/` — 18 plików orkiestrujących operacje biznesowe nad `db`/`repositories` (bubbles, chapters, jobs, projects, users...).
- `frontend/` — cały SPA (Bun+Vite+React+Tauri), osobny projekt.
- `comfyui/` — zvendorowany submodule, uruchamiany jako subprocess narzędzie zewnętrzne.
- `docs/`, `datasets/`, `notebooks/`, `knowledge/`, `logs/`, `test_examples/` — dokumentacja, dane treningowe/eksperymenty, notatki, logi runtime, luźne skrypty R&D. Nieistotne architektonicznie dla mm_avh poza samą zasadą "dokumentacja architektury żyje w `docs/architecture/`" (co mm_avh już robi w `docs/brainstorms/`).

---

## 10. Szczera ocena: co pasuje do mm_avh, a co jest przerostem

Autor (user) miał wątpliwość, czy MangaShift nie jest za skomplikowanym wzorcem. **Odpowiedź: tak, w dużej części jest — i to nie przez złe decyzje projektowe, tylko przez inną skalę problemu.** MangaShift to serwer wieloużytkownikowy z bazą danych, REST API, frontendem SPA, 27 modelami AI w 5 formatach na maszynach o różnym VRAM, workerem kolejkowym i retencją danych. mm_avh to jednoosobowy terminalowy skrypt do sekwencyjnego przetwarzania plików wideo. Kopiowanie architektury 1:1 byłoby błędem tej samej natury co dzisiejsze god-files — tylko w drugą stronę (przekombinowanie zamiast niedoinwestowania).

**Warte naśladowania wprost (niska cena, wysoka wartość dla obecnego problemu mm_avh — god-files, chaos w `temp/`):**

1. **`services/<domena>/engines/<silnik>/` + rejestr string→klasa z lazy importem** (§3). To bezpośrednie lekarstwo na `subtitle_to_speech.py` (1196 linii) — rozbicie na `services/tts/service.py` (fasada) + `services/tts/engines/{edge,elevenlabs,...}/service.py` (konkretne implementacje) eliminuje god-file i przyszłe if/elif przy dodawaniu silnika.
2. **`external/` → `bin/`, `workspace/` → `working_space/`, wyraźny podział `scripts/maintenance` vs `scripts/smoke`** (§4). To dokładnie adresuje dzisiejszy problem "chaos w temp/". Wzorzec `resolve_workspace_root()` z env-var override + fallback inferencji z lokalizacji modułu jest tani i solidny — kopiować niemal 1:1.
3. **Jeden plik `setup/doctor.py` z listą checków zwracających jednolity `CheckResult`** (§5.3) — 5-8 checków, nie 15. Tani do napisania, wysoka wartość diagnostyczna przy problemach z brakującym ffmpeg/mkvtoolnix.
4. **`bootstrap()` jako jedna funkcja spinająca config + wykryte ścieżki w jeden obiekt** (§5.5) — bez DB/sessionmaker/SecretsStore, ale sama zasada "jedno miejsce składania zależności zamiast rozproszonych importów" się broni.
5. **Osobna klasa configu per-serwis z własnym `env_prefix`** (§5.2) zamiast jednego rosnącego `Settings` — zapobiega przyszłemu god-file w configu.

**Przerost — jawnie odradzam kopiowanie:**

1. **`runtime/` + `vram/` (refcounting, VRAM budget/policy, NVML live monitoring, pressure)** (§6) — zaprojektowane pod współbieżne ładowanie wielu modeli o nieznanym z góry rozmiarze na maszynie z ograniczonym VRAM. mm_avh ładuje jeden model na krok, sekwencyjnie — to `try/finally` albo `with`, nie klasa zarządzająca z refcountem.
2. **`runtime/llama/`** — cały podsystem serwera llama.cpp (binary_resolver, client, manager, registry) dla lokalnego hostowania LLM. mm_avh nie hostuje LLM jako serwera.
3. **`models/core/` z pełnym `ResourceAsset`/`ResourceFile` per-format/per-część** (§7) — potrzebne przy 27 modelach w 5 formatach z multi-part strukturami. Przy 1-3 modelach mm_avh wystarczy słownik.
4. **Generyczny `pipeline/core/` step-registry z `scope_resolver`/`waving`/`ordering`** (§8) — mm_avh ma jeden liniowy przebieg, nie potrzebuje w pełni konfigurowalnego DAG-a kroków.
5. **`events/` broadcaster/emitter dla WebSocket** — mm_avh nie ma frontendu nasłuchującego zdarzeń; bezpośrednie wywołanie funkcji progress (co już działa) wystarcza.
6. **Async wszędzie jako fasada pod przyszłe REST API** — `TtsService` w MangaShift jest w pełni `async` (semafory, `asyncio.gather` w batch) bo ma obsługiwać równoległe requesty HTTP. mm_avh przetwarza jeden plik na raz w terminalu — sync kod jest prostszy do debugowania i wystarczający; async tylko tam, gdzie faktycznie jest I/O-bound równoległość do wykorzystania (np. równoległe zapytania do API TTS dla wielu linijek napisów), nie jako domyślny styl całego serwisu.
7. **Cały `db/`/`storage/`/`retention`/`usecases`/`worker`/`api`/`frontend`** — oczywiste, ale warto to nazwać wprost: to jest **większość** kodu MangaShift objętościowo, i **żadna** z tych warstw nie ma odpowiednika w mm_avh. Jeśli ktoś czytający ten wzorzec odniesie wrażenie "trzeba to wszystko jakoś odtworzyć uproszczone" — to błędny wniosek. Tych warstw po prostu nie ma, bo terminalowy skrypt jednoużytkownikowy nie ma serwera do obsłużenia.

**Podsumowanie oceny**: z całego MangaShift do mm_avh przenosi się sensownie: strukturę `services/<domena>/engines/<silnik>/` z registry, podział `bin/` + `working_space/` + `scripts/`, lekki `setup/doctor.py`, jedną funkcję `bootstrap()`, i osobne configi per-serwis. To może być zrobione w **jeden-dwa dni pracy** refaktoringu, bo problem mm_avh (8 płaskich modułów, god-files) jest dokładnie tego rodzaju, który rozbicie na `services/` rozwiązuje. Cała reszta MangaShift (runtime/vram, models/core, pipeline/core step-registry, events, i oczywiście db/api/worker/frontend) to odpowiedź na problemy skali i wieloużytkownikowości, których mm_avh nie ma i przez najbliższy czas mieć nie będzie — kopiowanie tego "na zapas" byłoby dokładnie tym błędem premature-abstraction, przed którym warto przestrzec.
