# plan strategiczny: AniShift (pakiet `anishift`) — runda 3

> data: 2026-07-12 | autor: Fable | zastępuje odrzucony plan z rundy 2
> zasada nadrzędna: **recykling MangaShift w 100%** — struktura, nazewnictwo, wzorce.
> repo: obecne (3 gwiazdki zostają), przebudowa na nowym branchu. nazwy `mm_avh` i `working_space` znikają z nowego kodu.

---

## A) werdykt architektoniczny — jak AniShift recyklinguje MangaShift

AniShift to siostra MangaShift: ten sam szkielet, mniejsze ciało. Bierzemy z MangaShift **wprost i bez wymyślania**: układ root (`external/` na binarki, `workspace/` na dane robocze, `scripts/` na skrypty dev, pakiet źródłowy obok), pakiet w układzie `cli/ + config/ + setup/ + platform/ + services/ + pipeline/ + bootstrap.py + errors.py`, wzorzec serwisu domenowego (fasada `service.py` + `config.py` + `errors.py` + `protocols.py` + `types.py`), rejestr silników `services/<domena>/engines/__init__.py` z `_REGISTRY` i lazy importem (kropka w kropkę wg engine-factory-standard), `setup/doctor.py` z jednolitym `CheckResult`, `bootstrap()` jako jedno miejsce składania zależności, `resolve_workspace_root()` z env-override, wejście przez Typer w `cli/main.py` zarejestrowane w `[project.scripts]`, manifest hashy dla `external/` wzorem `model_hashes.json`, oraz gotowe `utils/rich_console` i `utils/logger` (już sprawdzone w MangaShift).

Odchudzamy (ta sama idea, mniejsza ceremonia): doctor jako jeden plik zamiast pakietu `doctor_checks/` (checków będzie 6-8, nie 15); `platform/` bez `gpu_detect`/`torch_installer` — zostaje tylko wykrywanie OS i resolucja binarek; pipeline jako liniowy runner zamiast generycznego step-registry (jeden przebieg, nie DAG); fasady serwisów sync-first zamiast async (MangaShift jest async bo obsługuje REST — AniShift przetwarza jeden folder w terminalu; async zostaje wewnątrz silników, które realnie równoleglą: elevenbytes batch, edge); `resolve_workspace_root()` ląduje w `config/` zamiast osobnej warstwy `storage/`.

Pomijamy jako przerost potwierdzony audytem 06: `db/`, `api/`, `worker/`, `usecases/`, `frontend/`, `events/`, `retention/`, `runtime/` z VRAM/refcount/llama, `models/` (katalog 27 modeli AI — AniShift nie ma lokalnych modeli), `input/` w rozumieniu MangaShift. To nie jest "uproszczona wersja tych warstw" — tych warstw po prostu nie ma, bo nie ma serwera, bazy ani modeli.

Z obecnego mm_avh bierzemy wyłącznie dwie rzeczy: **logikę działania pipeline** (co robią moduły — ekstrakcja, refaktor napisów, tłumaczenie z dedupem, TTS z torem audio, składanie; wraz z niedawnymi poprawkami pasków postępu) oraz **`utils/` w całości, nietykalne**. Konwencje, nazewnictwo i strukturę obecnego repo — wyrzucamy.

---

## B) rozstrzygnięcia decyzji

### ui
**prompt_toolkit + rich**, zgodnie z badaniem 09. Textual odpada (pełnoekranowy framework, palette na Ctrl+P zamiast inline `/` — dalej od wizji Claude Code). Sam rich nie umie interaktywnego inputu. Recykling z MangaShift: pakiet `cli/` w kształcie MangaShift (cienki `main.py` na Typer + rejestracja komend, wpis w `[project.scripts]`, `load_dotenv` na starcie) — `anishift` bez argumentów odpala interaktywny shell (banner + REPL), `anishift doctor` / `anishift setup` jako subkomendy. Sam REPL (Enter=auto, `/komendy` z inline autocomplete, historia) to prompt_toolkit; rendering (banner, panele, progress) to rich przez `utils/rich_console` przeniesiony z MangaShift (150+ styli, ProgressBarManager — gotowy kod usera).

### config i klucze
Wzorem MangaShift dwie warstwy, obie proste:
- **klucze API i env**: `.env` + `Settings` (pydantic-settings, prefix `ANISHIFT_`) w `anishift/config/settings.py` — dokładnie jak `mangashift/config/settings.py`. Bez szyfrowania (apka jednego usera, tak samo trzyma to MangaShift). `.env.example` w repo, `.env` gitignored.
- **preferencje panelu** (tryb auto/manual, wybrany silnik tłumaczenia i TTS, głos, tempo, głośność, output): `workspace/settings.json`, czytane/zapisywane przez `anishift/config/user_settings.py`, auto-zapis z `/settings`. To odpowiednik `setup/config.py` MangaShift (trwały config poza `.env`), tylko w JSON i w workspace zamiast APPDATA — plik ma być widoczny i edytowalny ręcznie.
- configi per domena: dataclass slots z wymaganym `engine_id` (jak domain-configi MangaShift), zero defaultów silnika w serwisie — default trzyma warstwa ustawień (panel), serwis tylko waliduje i wykonuje ("front decyduje, serwer wykonuje" — u nas frontem jest panel/CLI).

### ffmpeg: biblioteka (PyAV) czy .exe? → **.exe**
Rozważone na poważnie (badanie 07): PyAV pokrywa natywnie cały tor audio (eac3, mp3, atempo, amix, probe), ale **nie pokrywa** renderu mp4 (libx264 jest GPL — nie ma go w wheelach PyPI) ani wypalania napisów (libass). Czyli PyAV nie usuwa binarki — najwyżej zmniejsza liczbę wywołań, za cenę **dwóch stacków audio/wideo naraz** (graf filtrów PyAV + subprocess ffmpeg), przepisania sprawdzonych łańcuchów filtrów (atempo-chain, amix, `-rf64 auto` dla WAV>4GB — realne ryzyko regresji na wielogodzinnym lektorze) i nowej powierzchni testów w środku przebudowy. MangaShift trzyma narzędzia zewnętrzne jako binarki w `external/bin` i woła subprocesem — robimy tak samo. **Decyzja: ffmpeg zostaje jednym `.exe` w `external/bin/ffmpeg/` dla całego toru audio i wideo.** Migracja toru audio na PyAV zapisana jako możliwa przyszła optymalizacja — nie w tej przebudowie.

### mkvtoolnix: .exe czy biblioteka? → **.exe, tylko 2 pliki**
Brak dojrzałego natywnego zamiennika (badanie 07: `pymkv2` i tak wymaga `mkvmerge.exe`, `python-matroska` ma 4★ i zero wydań — nie na serce pipeline). Zostają **`mkvextract` + `mkvmerge`** w `external/bin/mkvtoolnix/`; info o ścieżkach robi `mkvmerge --identify --identification-format json` jak dziś. `mkvinfo`, `mkvpropedit`, `espeak-ng` — martwe, nie przenosimy.

### balcon → **zostaje .exe, Windows-only przez `is_available()`**
`balcon.exe` (SAPI, głos IVONA 2 Agnieszka) w `external/bin/balabolka/`. To silnik w rejestrze TTS, którego `is_available()` zwraca fałsz poza Windows albo gdy binarki/głosu brak — fasada i pipeline nie mają żadnego if-a na OS (dokładnie jak MangaShift gate'uje silniki per platforma). Migracja balcon→pyttsx3 odłożona (wymaga testu ucha) — harpo (pyttsx3/SAPI Zosia) to i tak osobny, już istniejący silnik biblioteczny.

### dystrybucja binarek → **wzorem external/ MangaShift**
`external/bin/<narzędzie>/` gitignored (koniec z 218 błędnie trackowanymi plikami), w repo tylko `external/README.md` + `external/bin_hashes.json` (odpowiednik `model_hashes.json`: per plik SHA256 + rozmiar + źródłowy URL oficjalnego buildu). `doctor` sprawdza obecność i hash; `anishift setup` pobiera brakujące binarki z oficjalnych URL-i i weryfikuje hashem (na Linux: fallback na narzędzia z PATH — mkvtoolnix i ffmpeg są w każdej dystrybucji).

### silniki (zweryfikowane w kodzie — zero wymysłów)
- **tts**: `elevenbytes` (ElevenLabs proxy v2+v3 — jeden silnik, wybór modelu przez `provider_model_id`, jak nakazuje naming-glossary), `edge` (edge-tts, głosy Zofia/Marek jako opcja głosu, nie osobne silniki), `harpo` (pyttsx3/SAPI, Zosia), `balcon` (balcon.exe/SAPI, Agnieszka, Windows-only). GTTS nie istnieje; sapi5==balcon — nie ma osobnego "sapi5".
- **tłumaczenie**: `google` (googletrans v4, wrapper async→sync), `deepl` (DeepL API). DeepL desktop martwy — nie przenosimy. OpenAI nie istnieje.
- zachowane funkcjonalnie: dedup tłumaczeń (unikalne linie 1×), czyszczenie znaczników ASS, marker nowej linii, retry/backoff elevenbytes, cache elevenbytes, rundy dosyłania nieudanych requestów.

---

## C) struktura folderów (drzewo — nazwy jak MangaShift)

```
<repo root>
├── pyproject.toml               # [project.scripts] anishift = anishift.cli.main:main
├── .env.example                 # klucze: DEEPL, ELEVENBYTES
├── .python-version
├── external/                    # zewnętrzne binarki poza kodem (jak MangaShift external/)
│   ├── README.md                # skąd binarki, konwencja
│   ├── bin_hashes.json          # manifest: SHA256 + rozmiar + URL per plik
│   └── bin/                     # gitignored
│       ├── mkvtoolnix/          # mkvextract, mkvmerge
│       ├── ffmpeg/              # ffmpeg (+ ffprobe)
│       └── balabolka/           # balcon.exe (Windows-only)
├── workspace/                   # dane robocze runtime (jak MangaShift workspace/) — gitignored poza strukturą
│   ├── input/                   # tu wpadają MKV; Enter = przetwórz wszystko
│   ├── output/                  # wyniki dla usera
│   ├── tmp/                     # w tym main_subs/, alt_subs/ (odpowiednik dzisiejszego temp)
│   ├── cache/                   # m.in. cache elevenbytes
│   ├── logs/
│   └── settings.json            # preferencje panelu (auto-zapis z /settings)
├── scripts/
│   ├── maintenance/             # jednorazowe (np. migracja danych z working_space)
│   └── smoke/                   # ręczny test e2e na 1 pliku MKV
├── utils/                       # NIETYKALNE — 1:1 z mm_avh; nowe rzeczy tylko jako nowe pliki obok
│   ├── cool_animation.py
│   ├── execution_timer.py
│   ├── number_in_words.py
│   ├── text_chunker.py
│   ├── rich_console/            # NOWE — przeniesione z MangaShift (style, ProgressBarManager)
│   └── logger/                  # NOWE — przeniesione z MangaShift
├── anishift/                    # pakiet źródłowy (jak mangashift/)
│   ├── __init__.py
│   ├── bootstrap.py             # bootstrap() -> AppContext (settings + ścieżki binarek + workspace)
│   ├── errors.py                # bazowa hierarchia wyjątków
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py              # Typer app: default=shell, subkomendy doctor/setup
│   │   ├── shell.py             # REPL prompt_toolkit: Enter=auto, dispatch /komend
│   │   ├── banner.py            # ASCII banner (używa utils/cool_animation + rich_console)
│   │   ├── commands.py          # rejestr /komend: /help /settings /auto /manual /doctor /exit
│   │   ├── completer.py         # inline autocomplete po "/" (jak Claude Code)
│   │   └── settings_panel.py    # panel /settings (rich), auto-zapis do workspace/settings.json
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Settings (pydantic-settings, .env, prefix ANISHIFT_)
│   │   ├── user_settings.py     # load/save workspace/settings.json (preferencje panelu)
│   │   └── workspace.py         # resolve_workspace_root() + DEFAULT_SUBDIRS (wzór storage/workspace.py)
│   ├── setup/
│   │   ├── __init__.py
│   │   ├── doctor.py            # checki -> CheckResult: binarki+hash, klucze, workspace, python
│   │   └── installer.py         # pobieranie binarek wg bin_hashes.json (anishift setup)
│   ├── platform/
│   │   ├── __init__.py
│   │   └── binaries.py          # resolucja external/bin per OS, fallback PATH na Linux
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── runner.py            # liniowy przebieg: extract → refactor → translate → tts → compose
│   │   └── types.py             # kontekst przebiegu (plik, ścieżki, ustawienia, wyniki kroków)
│   └── services/
│       ├── __init__.py
│       ├── extraction/          # domena bez wyboru silnika = zwykły moduł (bez engines/)
│       │   ├── __init__.py
│       │   ├── service.py       # mkvmerge --identify (json) + mkvextract + live progress
│       │   ├── tracks.py        # auto-wybór ścieżek (logika track_selector)
│       │   ├── types.py
│       │   └── errors.py
│       ├── subtitles/           # refaktor napisów = zwykły moduł
│       │   ├── __init__.py
│       │   ├── service.py       # ASS→SRT, podział main/alt, przygotowanie pod tłumaczenie
│       │   ├── cleanup.py       # czyszczenie znaczników ASS/formatowania
│       │   ├── styles.py        # hak na przyszły style_classifier (odłożone — tylko miejsce)
│       │   ├── types.py
│       │   └── errors.py
│       ├── translation/         # domena z wyborem = fasada + rejestr silników
│       │   ├── __init__.py
│       │   ├── config.py        # TranslationConfig (engine_id wymagany)
│       │   ├── constants.py
│       │   ├── dedup.py         # dedup unikalnych linii + marker \n — zachowane 1:1 funkcjonalnie
│       │   ├── errors.py
│       │   ├── protocols.py     # Protocol tłumacza
│       │   ├── service.py       # fasada: create_engine + przebieg pliku srt
│       │   ├── types.py
│       │   └── engines/
│       │       ├── __init__.py  # _REGISTRY: google, deepl (wzorzec §E)
│       │       ├── google/      # __init__.py, config.py, constants.py, service.py
│       │       └── deepl/       # __init__.py, config.py, constants.py, service.py
│       ├── tts/                 # domena z wyborem = fasada + rejestr silników
│       │   ├── __init__.py
│       │   ├── config.py        # TtsConfig (engine_id wymagany, pola per silnik)
│       │   ├── constants.py
│       │   ├── errors.py
│       │   ├── protocols.py     # Protocol silnika TTS (w tym is_available)
│       │   ├── output.py        # nazwy/miejsca plików wav
│       │   ├── service.py       # fasada: srt → wav lektora przez wybrany silnik
│       │   ├── types.py
│       │   └── engines/
│       │       ├── __init__.py  # _REGISTRY: elevenbytes, edge, harpo, balcon
│       │       ├── elevenbytes/ # __init__, config, constants, service, api_backend, types
│       │       │                #   (batch async, retry, cache, rundy, v2/v3 przez provider_model_id)
│       │       ├── edge/        # __init__, config, constants, service (głosy Zofia/Marek w opcjach)
│       │       ├── harpo/       # __init__, config, constants, service (pyttsx3/SAPI Zosia)
│       │       └── balcon/      # __init__, config, constants, service (balcon.exe, is_available=Windows)
│       ├── audio/               # tor audio ffmpeg = zwykły moduł
│       │   ├── __init__.py
│       │   ├── service.py       # atempo, volume, amix (lektor+oryginał), eac3/mp3, rf64
│       │   ├── types.py
│       │   └── errors.py
│       └── composition/         # składanie wyniku = zwykły moduł
│           ├── __init__.py
│           ├── service.py       # 3 wyjścia: players (napisy+audio) / merge mkv / burn mp4
│           ├── types.py
│           └── errors.py
├── tests/
├── docs/
└── assets/
```

Uwagi do drzewa:
- `extraction`, `subtitles`, `audio`, `composition` **nie mają** `engines/` — nie ma tam wyboru silnika (tak jak MangaShift nie robi rejestru tam, gdzie nie ma silników do wybierania).
- `utils/` zostaje top-level (jak dziś) — nietykalny rdzeń usera; `rich_console/` i `logger/` dochodzą jako nowe podfoldery obok, bez ruszania istniejących 4 plików.
- `style_classifier` NIE wchodzi do przebudowy — `subtitles/styles.py` to tylko zaślepka/hak (user zbiera przykłady).

---

## D) etapy (każdy = działająca apka, zero scope creep)

### etap 1 — fundament: pakiet, utils, config, doctor
**cel:** istnieje pakiet `anishift` uruchamialny przez `uv run anishift`, z configiem, workspace i doktorem — zanim powstanie jakikolwiek pipeline.

pliki:
- `pyproject.toml` (nowy: pakiet anishift, entry point, zależności: rich, prompt_toolkit, typer, pydantic-settings, pysrt, natsort, edge-tts, pyttsx3, googletrans, deepl, pydub…)
- `.env.example`, aktualizacja `.gitignore` (external/bin, workspace, .env)
- `anishift/__init__.py`, `anishift/errors.py`, `anishift/bootstrap.py`
- `anishift/config/__init__.py`, `settings.py`, `user_settings.py`, `workspace.py`
- `anishift/platform/__init__.py`, `binaries.py`
- `anishift/setup/__init__.py`, `doctor.py`
- `anishift/cli/__init__.py`, `main.py` (na razie: banner-stub + subkomenda doctor)
- `utils/rich_console/`, `utils/logger/` (kopiowane z MangaShift; istniejące 4 pliki utils bez zmian)
- `external/README.md`, `external/bin_hashes.json` (szkielet), struktura `external/bin/`
- struktura `workspace/` (gitkeepy)

zależności: brak (start).
jak testować: `uv run anishift doctor` raportuje stan binarek/kluczy/workspace na czysto i na skonfigurowanej maszynie; `bootstrap()` zwraca AppContext w teście jednostkowym.
DoD: pakiet instaluje się przez uv, doctor działa, workspace się sam tworzy, utils przeniesione 1:1 + rich_console/logger działają (import + smoke).

### etap 2 — shell: banner, REPL, /komendy, /settings
**cel:** serce wizji UX — terminalówka "między Claude Code a webem" działa jako pusta skorupa (komendy są, pipeline jeszcze nie).

pliki:
- `anishift/cli/shell.py`, `banner.py`, `commands.py`, `completer.py`, `settings_panel.py`
- rozbudowa `anishift/cli/main.py` (default = shell)
- `anishift/config/user_settings.py` — pełny zapis/odczyt preferencji

zależności: etap 1.
jak testować: ręcznie — banner po starcie; wpisanie `/` pokazuje inline podpowiedzi; `/settings` renderuje panel i zapisuje `workspace/settings.json`; `/auto` i `/manual` przełączają tryb i jest on pamiętany po restarcie; Enter odpowiada komunikatem "pipeline w budowie".
DoD: wszystkie komendy (`/help /settings /auto /manual /doctor /exit`) działają, autocomplete inline działa, ustawienia przeżywają restart.

### etap 3 — ekstrakcja + refaktor napisów
**cel:** Enter zaczyna coś robić: MKV z `workspace/input/` → wyciągnięte ścieżki + napisy przerobione do SRT.

pliki:
- `anishift/services/extraction/__init__.py`, `service.py`, `tracks.py`, `types.py`, `errors.py`
- `anishift/services/subtitles/__init__.py`, `service.py`, `cleanup.py`, `styles.py` (hak), `types.py`, `errors.py`
- `anishift/pipeline/__init__.py`, `runner.py`, `types.py` (kroki 1-2)
- podpięcie Enter=auto w `shell.py`

zależności: etapy 1-2. logika przenoszona z `modules/mkvtoolnix.py`, `track_selector.py`, `subtitle.py` (w tym świeże poprawki live-progress ekstrakcji z ostatnich commitów).
jak testować: realny MKV w `workspace/input/` → w `workspace/tmp/` audio + napisy SRT z czystym tekstem; tryb manual pyta o wybór ścieżek, auto wybiera sam.
DoD: parytet z dzisiejszą ekstrakcją+refaktorem na pliku testowym (te same ścieżki wybrane, ten sam SRT co stary kod), pasek postępu live jak dziś.

### etap 4 — tłumaczenie (pierwszy rejestr silników)
**cel:** działa rejestr wg wzorca §E na mniejszej domenie: google + deepl, z dedupem i czyszczeniem znaczników.

pliki:
- `anishift/services/translation/__init__.py`, `config.py`, `constants.py`, `dedup.py`, `errors.py`, `protocols.py`, `service.py`, `types.py`
- `anishift/services/translation/engines/__init__.py` (rejestr)
- `anishift/services/translation/engines/google/__init__.py`, `config.py`, `constants.py`, `service.py`
- `anishift/services/translation/engines/deepl/__init__.py`, `config.py`, `constants.py`, `service.py`
- `anishift/pipeline/runner.py` — krok 3 (z pominięciem plików już po polsku, jak dziś)

zależności: etap 3. logika z `modules/translator.py`.
jak testować: SRT angielski → polski oboma silnikami; plik z 1000 powtórzeń tej samej linii tłumaczy 1 request; znaczniki ASS nie przechodzą do tłumaczenia; brak klucza deepl = czytelny błąd domenowy, nie traceback.
DoD: parytet wyników z dzisiejszym translatorem na pliku testowym; rejestr przechodzi smoke (nieznany engine_id = ConfigError z listą dostępnych).

### etap 5 — tts + tor audio (największy etap, główny zysk przebudowy)
**cel:** rozbicie god-files `subtitle_to_speech.py` (1196 linii) + `tts_elevenbytes.py` (617 linii) na rejestr 4 silników + osobny tor audio.

pliki:
- `anishift/services/tts/__init__.py`, `config.py`, `constants.py`, `errors.py`, `protocols.py`, `output.py`, `service.py`, `types.py`
- `anishift/services/tts/engines/__init__.py` (rejestr)
- `anishift/services/tts/engines/elevenbytes/__init__.py`, `config.py`, `constants.py`, `service.py`, `api_backend.py`, `types.py`
- `anishift/services/tts/engines/edge/__init__.py`, `config.py`, `constants.py`, `service.py`
- `anishift/services/tts/engines/harpo/__init__.py`, `config.py`, `constants.py`, `service.py`
- `anishift/services/tts/engines/balcon/__init__.py`, `config.py`, `constants.py`, `service.py`
- `anishift/services/audio/__init__.py`, `service.py`, `types.py`, `errors.py`
- `anishift/pipeline/runner.py` — krok 4; `settings_panel.py` — wybór silnika/głosu/tempa

zależności: etap 4. logika z `modules/subtitle_to_speech.py` + `modules/tts_elevenbytes.py` + wzorce EchoReader (klucz API, voice_settings) — ale dispatch przez rejestr, nie if/elif.
jak testować: SRT polski → WAV lektora każdym dostępnym silnikiem; elevenbytes: cache trafia, retry/rundy działają, v2 i v3 przez provider_model_id; balcon widoczny tylko na Windows z zainstalowanym głosem (`is_available`); tor audio: atempo/volume/amix daje ten sam wynik co dziś na próbce.
DoD: pełny lektor elevenbytes na realnym odcinku brzmi/wygląda jak z obecnego kodu; edge i harpo działają; balcon poprawnie gate'owany; żaden plik serwisu nie przekracza ~300 linii.

### etap 6 — składanie + pełne e2e
**cel:** domknięcie pipeline: trzy wyjścia jak dziś (players / merge mkv / burn mp4) i pełny tryb auto od Enter do wyniku.

pliki:
- `anishift/services/composition/__init__.py`, `service.py`, `types.py`, `errors.py`
- `anishift/pipeline/runner.py` — krok 5, pełen przebieg wielu plików (natsorted, równoległość tam gdzie dziś jest)
- `scripts/smoke/run_e2e.ps1` (i krótka notka jak odpalić)

zależności: etap 5. logika z `modules/mkv_processing.py`.
jak testować: smoke e2e — 1 realny odcinek z `workspace/input/` przechodzi Enter→wynik we wszystkich trzech wariantach wyjścia; porównanie z wynikiem starego `start.py` na tym samym pliku.
DoD: happy-path identyczny funkcjonalnie ze starym kodem (tablica prawdy #7); tryb auto nie zadaje żadnego pytania.

### etap 7 — dystrybucja binarek + wyburzenie starego
**cel:** repo po przeprowadzce: binarki zarządzane manifestem, stary kod i bałagan usunięte.

pliki:
- `external/bin_hashes.json` — wypełniony (mkvtoolnix, ffmpeg, balcon: SHA256 + URL)
- `anishift/setup/installer.py` — `anishift setup` pobiera i weryfikuje binarki
- rozszerzenie `doctor.py` o weryfikację hashy
- `scripts/maintenance/migrate_workspace.py` — przeniesienie danych usera z `working_space/` do `workspace/`
- kasacje: `modules/`, `data/`, `start.py`, `constants.py`, `run_mm_avh.bat`, `bin/` (w tym stylish_tts 567MB, espeak-ng), `working_space/`, porządek w `temp/` i `tests/` (realne skrypty → `scripts/maintenance/`)

zależności: etap 6 (nic starego nie kasujemy, dopóki nowe nie ma parytetu).
jak testować: świeży klon repo + `uv sync` + `anishift setup` + `anishift doctor` = zielono; smoke e2e przechodzi; `git status` czysty, żadnych binarek w gicie.
DoD: w repo nie ma śladu nazw `mm_avh` / `working_space` w nowym kodzie; README opisuje AniShift.

---

## E) wzorzec rejestru silników — opis słowny (wg engine-factory-standard i engine-standard MangaShift)

Rejestr istnieje **tylko** w dwóch domenach z realnym wyborem: `tts` i `translation`. Wygląda kropka w kropkę tak samo w obu (to reguła factory-standard: różnice tylko w miejscach wymuszonych):

- plik `services/<domena>/engines/__init__.py` jest **jedynym źródłem prawdy** o zestawie silników domeny. Kolejność sekcji stała: docstring → importy → `__all__` → logger → typ `…EngineId` (Literal z kluczami rejestru) → `_REGISTRY` → `available_engine_ids()` → `create_engine()`.
- `_REGISTRY` to słownik `engine_id → trójka (ścieżka modułu, nazwa klasy serwisu, referencja configu)`. Klucz zawsze snake_case (`elevenbytes`, `edge`, `harpo`, `balcon`; `google`, `deepl`). Żadna inna warstwa nie przepisuje tej listy ręcznie — panel ustawień i pipeline **derywują** dostępne opcje przez `available_engine_ids()`.
- `create_engine(config)` robi guard: pusty `engine_id` → domenowy `ConfigError`; nieznany → `ConfigError` z posortowaną listą dostępnych. Potem `importlib.import_module` (lazy — silnik ładuje się dopiero gdy wybrany; edge-tts/deepl/googletrans nie są importowane na starcie apki) i konstrukcja klasy z configiem silnika.
- fasada `service.py` domeny **nie zna żadnego konkretnego silnika** — woła wyłącznie `create_engine`, cache'uje instancję per engine_id. Zero `if engine_id == …` gdziekolwiek. Dodanie silnika = nowy podfolder + jeden wpis w `_REGISTRY`.
- każdy silnik to pakiet `engines/<engine_id>/` o stałym kształcie: `__init__.py` (re-export), `config.py` (dataclass slots, walidacja w `__post_init__`), `constants.py` (m.in. `provider_model_id` dla dostawców API — elevenbytes trzyma tu katalog modeli v2/v3), `service.py` (implementacja Protocolu domeny), opcjonalnie `types.py` i `api_backend.py` (osobny klient HTTP — elevenbytes). Ciężkie importy wewnątrz metod, nie na górze pliku.
- Protocol domeny (w `protocols.py`) wymaga m.in. `engine_id`, `is_available` i głównej metody pracy. **`is_available` załatwia cross-platform bez if-ów OS w fasadzie**: balcon zwraca fałsz poza Windows lub bez binarki/głosu, harpo bez SAPI — panel pokazuje tylko dostępne silniki, pipeline dostaje czytelny błąd domenowy przy wymuszeniu niedostępnego.
- odstępstwo od MangaShift (świadome, odnotowane): fasady są **sync** (service-standard MangaShift wymaga async, bo stoi pod REST — AniShift nie ma REST). Async żyje tylko wewnątrz silników, które realnie równoleglą requesty (elevenbytes batch, edge) i nie wycieka ponad fasadę.
- wybór silnika: dokładnie zasada "front decyduje, serwer wykonuje" — u AniShift frontem jest panel `/settings` (trzyma defaulty w `workspace/settings.json`), config domeny dostaje `engine_id` wymagany bez defaultu, serwis waliduje wobec rejestru i wykonuje.

---

## F) ryzyka i niepewności

1. **parytet z god-file elevenbytes** — `subtitle_to_speech.py` + `tts_elevenbytes.py` mają dużo zaszytych edge-case'ów (cache per linia, rundy ponawiania, 5h timeout, sample rate 44100, sklejanie mp3→wav przez pipe ffmpeg). Rozbicie na pakiet silnika może zgubić niuans. Mitygacja: przenosić logikę blokami z testem porównawczym na tym samym SRT (etap 5 ma najdłuższy DoD nie bez powodu).
2. **RF64 / WAV > 4GB** — wielogodzinny lektor wymaga `-rf64 auto`; to jeden z powodów decyzji "ffmpeg zostaje .exe". Trzeba to jawnie objąć testem smoke na długim pliku, bo regresja objawia się dopiero przy dużym odcinku/maratonie.
3. **REPL prompt_toolkit to nowa funkcjonalność, nie przepisanie** — inline autocomplete + panel + tryby to jedyna część bez działającego pierwowzoru w mm_avh. Dlatego jest wcześnie (etap 2), osobno i bez pipeline — żeby ryzyko UX nie blokowało reszty.
4. **googletrans v4** — nieoficjalna biblioteka, async pod spodem, bywa krucha na zmiany po stronie Google. Rejestr izoluje ryzyko (deepl jako zapas), ale trzeba przyjąć, że google może paść niezależnie od nas.
5. **balcon/harpo zależą od głosów SAPI zainstalowanych w systemie** — `is_available` musi sprawdzać obecność konkretnego głosu, nie tylko binarki; na maszynie bez IVONA/Zosia silniki mają znikać z panelu, nie wybuchać. pyttsx3 ma znane zawieszki `save_to_file` w pętli — przenosimy istniejące obejście z toru Harpo.
6. **migracja workspace** — `working_space/` ma 704 pliki danych usera (w tym luźne MKV i audiobooki). Skrypt migracyjny musi przenosić, nie kasować; kasacja starego folderu dopiero po ręcznym potwierdzeniu usera.
7. **niepewność decyzyjna, którą wskazuję wprost**: (a) miejsce `settings.json` — wybrałem `workspace/` (widoczność) zamiast APPDATA (wzorzec MangaShift `setup/config.py`); jeśli user woli literalną wierność MangaShift, to jednolinijkowa zmiana ścieżki; (b) Typer jako wejście — wierny recykling MangaShift, ale przy czysto REPL-owej apce można go wyciąć do gołego argv; zostawiłem, bo daje `doctor`/`setup` za darmo; (c) `pydantic-settings` dla `.env` — zgodne z MangaShift, choć tablica prawdy preferuje dataclass slots (te zostają dla configów domen); jeśli zapachnie przerostem, `Settings` da się strywializować do dataclass + os.environ bez ruszania reszty planu.
8. **ślepy punkt**: nie przetestowałem żadnego kodu — plan opiera się na audytach 00-09 i czytaniu źródeł mm_avh/MangaShift. Liczby linii i zachowania silników zweryfikowałem grepem, ale zachowanie runtime (np. czy edge-tts nadal działa z obecnym API Bing) potwierdzi dopiero etap 5.
