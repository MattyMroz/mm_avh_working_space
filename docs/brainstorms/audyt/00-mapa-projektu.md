# 00 — Mapa projektu mm_avh_working_space

> Widok z lotu ptaka: cała struktura repo, co gdzie leży, co jest kodem/danymi/cache/śmieciami.
> Uzupełnienie audytów szczegółowych (01-05), które opisują wnętrze plików .py.

---

## 1. Drzewo projektu

```
mm_avh_working_space/
├── constants.py                  # kod — ścieżki do bin/, WORKING_SPACE, stałe globalne
├── start.py                      # kod — punkt wejścia CLI (główny orkiestrator pipeline'u)
├── run_mm_avh.bat                # kod — launcher Windows (uv run start.py)
├── pyproject.toml, uv.lock       # config — zależności (uv), Python >=3.14
├── .python-version, .gitattributes, .gitignore, LICENSE, README.md   # config/meta
│
├── bin/                          # VENDORED — binaria zewnętrzne, 762 pliki, ~1.13 GB
│   ├── ffmpeg/        (391M)     # vendored binarka — konwersja A/V
│   ├── mkvtoolnix/    (149M)     # vendored binarka — ekstrakcja/merge MKV
│   ├── espeak-ng/     (24M)      # vendored binarka — synteza fonemów TTS
│   ├── balabolka/     (1.2M)     # vendored binarka — TTS SAPI
│   └── stylish_tts/   (567M)     # VENDORED KOD .py + wagi modelu — patrz sekcja 4, DO USUNIĘCIA
│
├── data/                         # config + cache (wymieszane), 138 plików
│   ├── config.py, settings.py    # kod — konfiguracja aplikacji
│   ├── settings.json             # DANE WRAŻLIWE — prawdziwe klucze API, gitignored ✅
│   └── .mypy_cache/               # ŚMIECI — cache mypy, NIETYPOWO leży wewnątrz data/
│
├── docs/                         # dokumentacja, 15 plików
│   ├── brainstorms/               # ideacje (2026-06/07) + audyt/ (ten raport i sąsiednie)
│   ├── content.md
│   └── superpowers/plans/
│
├── modules/                      # RDZEŃ APLIKACJI — kod produkcyjny, 8 plików .py
│   ├── mkvtoolnix.py, mkv_processing.py, track_selector.py   # ekstrakcja/merge MKV
│   ├── subtitle.py, translator.py, style_classifier.py       # napisy/tłumaczenie
│   ├── subtitle_to_speech.py, tts_elevenbytes.py             # TTS/lektor
│   └── .mypy_cache/, __pycache__/  # ŚMIECI — reszta "1032 plików" to cache, nie kod
│
├── temp/                         # ROBOCZE SKRYPTY + DANE ML, 217 plików — CAŁY FOLDER gitignored
│   ├── analyze_dataset.py, dataset_build.py, dataset_build_c.py,
│   │   compare_gt.py, make_full_report.py, run_subtitle_slice.py   # skrypty eksperymentalne (nie w modules/)
│   ├── dataset_ass/     (~190 plików .ass)   # dane treningowe/testowe (napisy)
│   ├── ground_truth/    (20 plików .json)    # dane referencyjne do ewaluacji
│   ├── brain_storm/     (2 pliki .md)        # notatki
│   └── *.wav, dataset.json, manifest*.jsonl  # artefakty robocze
│
├── tests/                        # testy + eksperymenty, 299 plików (realnie ~20 .py)
│   ├── *_test.py (translator, tts_*, track_selector, style_classifier, srt_to_ass...)
│   ├── translator-gpt-*_alt.py, chat.py, MM_AVH_pre.py, pylint_tests.py   # skrypty eksperymentalne, nie pytest
│   ├── input/, output/            # dane testowe I/O
│   └── .mypy_cache/, __pycache__/ # ŚMIECI
│
├── utils/                        # kod pomocniczy, 8 plików (4 realne + cache)
│   ├── cool_animation.py, execution_timer.py, number_in_words.py, text_chunker.py
│   └── __pycache__/
│
├── working_space/                # DANE RUNTIME UŻYTKOWNIKA — 704 pliki, gitignored (poza strukturą)
│   ├── ANIME/, as/                # pliki robocze: .mkv, .eac3, .ass, .mp3 per odcinek anime
│   ├── audio/                     # gotowe audiobooki/lektoraty (86, KRK, ORV, SM, The Apothecary Diaries...)
│   ├── output/, temp/              # foldery pipeline'u (main_subs/, alt_subs/)
│   ├── bugs/                       # nagrania z wykrytymi błędami do debugowania
│   ├── convert_eac3_to_mp3.py      # KOD w folderze DANYCH — nietypowe
│   ├── KRK_028.srt, *.mkv luzem w root   # pliki robocze leżące bezpośrednio w working_space/
│   ├── desktop.ini, "Anime — skrót .lnk" # śmieci Windows Explorer (ikony/skróty)
│   └── .mypy_cache/                # ŚMIECI — cache mypy nawet tutaj
│
├── assets/                       # 1 plik — img/mm_avh_working_space.gif (demo README)
│
├── .agents/, .claude/, .github/  # konfiguracja narzędzi (Claude Code, CI)
├── .venv/                        # ŚMIECI — 32121 plików, virtualenv, gitignored
└── .mypy_cache/, .ruff_cache/, .uv-cache/, .uv-tools/, __pycache__/  # ŚMIECI w ROOT — cache narzędzi
```

---

## 2. Tabela: folder → charakter → git → rekomendacja

| Folder | Co to | Plików | Charakter | W git? | Rekomendacja |
|---|---|---|---|---|---|
| `modules/` | Rdzeń aplikacji (8 modułów pipeline'u) | 8 (+cache) | kod produkcyjny | tak (8 plików) | zostaje |
| `utils/` | Pomocnicze funkcje (animacje, timer, liczby, chunker) | 4 (+cache) | kod produkcyjny | tak (4) | zostaje — w trakcie migracji z MangaShift (patrz brief 2026-07-08) |
| `data/` | Config + settings + settings.json (klucze API) | 3 realne | config + sekrety | częściowo (`config.py`, `settings.py` tak; `settings.json` gitignored) | zostaje; **usunąć `data/.mypy_cache/`** (cache nie powinien tam leżeć) |
| `docs/` | Dokumentacja, brainstormy, audyty | 15 | dokumentacja | tak | zostaje |
| `tests/` | Testy + skrypty eksperymentalne + I/O | ~20 realnych .py | mieszane: testy / eksperymenty / dane | tak (22 wg git) | zostaje, ale wymaga segregacji (patrz sekcja 3) |
| `temp/` | Skrypty robocze ML + dataset + ground truth | 217 | robocze/eksperymentalne + dane | **NIE — cały folder w `.gitignore`** | do przeglądu: skrypty realnie użyteczne → przenieść do `tests/` lub `scripts/`; dane (`dataset_ass/`, `ground_truth/`) → rozważyć osobne miejsce poza repo lub jawne oznaczenie jako fixtures |
| `working_space/` | Dane runtime użytkownika (I/O pipeline'u) | 704 | dane robocze usera | częściowo — tylko struktura folderów (`.gitkeep`) jest w gitignore-wyjątkach, reszta ignorowana | zostaje jako koncept, ale **posprzątać** — patrz sekcja 3 (luźne pliki, .py, .lnk, desktop.ini) |
| `bin/` | Vendored binaria (ffmpeg, mkvtoolnix, espeak-ng, balabolka, stylish_tts) | 762 | vendored/binary | **NIE — cały folder w `.gitignore`** | ffmpeg/mkvtoolnix/espeak-ng/balabolka zostają (potrzebne runtime); **`stylish_tts/` do usunięcia** (user tak zdecydował) |
| `assets/` | Obraz demo do README | 1 | statyczny zasób | tak | zostaje |
| `.venv/` | Virtualenv | 32121 | środowisko | nie (gitignored) | zostaje jako lokalny artefakt, nic do zrobienia |
| `.mypy_cache/`, `.ruff_cache/`, `.uv-cache/`, `.uv-tools/`, `__pycache__/` (root) | Cache narzędzi | — | cache | nie (gitignored) | OK, ale rozrzucone kopie w `data/`, `modules/`, `tests/`, `working_space/` warto scentralizować (np. `mypy --cache-dir` wskazane na jedno miejsce w root) |
| `.agents/`, `.claude/` | Konfiguracja Claude Code / skille | — | config narzędzi | `.claude/` gitignored, `.agents/` — do sprawdzenia | bez zmian |
| `.github/` | Configi Copilota | — | config narzędzi | **gitignored explicite** ("internal, not for VCS") | bez zmian |

---

## 3. Pliki leżące NIETYPOWO

1. **`working_space/convert_eac3_to_mp3.py`** — jedyny plik kodu Python leżący w folderze danych runtime. Powinien być w `modules/`, `utils/` albo `temp/`/`scripts/`. Obecne miejsce sugeruje, że ktoś (user) uruchamiał go ad-hoc bezpośrednio przy danych — ale to sprzeczne z resztą architektury (kod zawsze w `modules/`/`utils/`/`tests/`).

2. **Luźne pliki robocze bezpośrednio w `working_space/` (root, nie w podfolderze)**:
   - `KAMUI.---Hes.behind.you.S01E02...mkv`, `KAMUI.Hes.Behind.You.S01E01...mkv` — pliki MKV leżące luzem, nie w `ANIME/` ani `as/`
   - `KRK_028.srt` — pojedynczy plik napisów luzem w root
   - `desktop.ini` — plik systemowy Windows (metadane folderu), nie powinien być tam ręcznie tworzony/utrzymywany, ale to efekt uboczny Explorer, nieszkodliwy
   - `Anime — skrót .lnk` — skrót Windows do innego miejsca na dysku, czysto lokalny artefakt usera, nie ma sensu w repo (i tak gitignored)

3. **`temp/` jako "worker folder" poza modules/tests** — zawiera zarówno skrypty (`analyze_dataset.py`, `dataset_build.py`, `dataset_build_c.py`, `compare_gt.py`, `make_full_report.py`, `run_subtitle_slice.py`) jak i dane (`dataset_ass/` ~190 plików .ass, `ground_truth/` 20 plików json, pliki `.wav`). To de facto trzeci równoległy obszar kodu obok `modules/` i `tests/`, ale cały gitignored — więc te skrypty nie są wersjonowane mimo że wyglądają na trwały dorobek (np. `make_full_report.py`). Ryzyko utraty przy czyszczeniu dysku.

4. **`tests/` miesza pytest-testy z eksperymentami jednorazowymi**: pliki jak `chat.py`, `MM_AVH_pre.py`, `pylint_tests.py`, `translator-gpt-no-re-ask_alt.py`, `translator-gpt-re-ask_alt.py`, `real_esrgan_and_others.py` nie wyglądają na testy automatyczne (brak `test_` prefix/`_test` w typowym sensie pytest, raczej ad-hoc skrypty). Realne testy (`*_test.py`) i eksperymenty są wymieszane w jednym folderze bez rozgraniczenia.

5. **`.mypy_cache/` rozrzucony w 5 różnych miejscach**: root, `data/`, `modules/`, `tests/`, `working_space/`. Sugeruje, że mypy było uruchamiane z różnych katalogów roboczych zamiast jednego skonfigurowanego `cache_dir` w `pyproject.toml`/`mypy.ini`. Warto scentralizować.

6. **`data/settings.json` z prawdziwymi kluczami API** — poprawnie gitignored (potwierdzone w `.gitignore`: `data/settings.json` explicite wykluczony), ale leży obok `config.py`/`settings.py` (kodu), czyli sekret miesza się fizycznie z kodem konfiguracyjnym w tym samym folderze. Działa, bo gitignore to pokrywa, ale warto rozważyć osobny `data/secrets/` lub `.env`.

---

## 4. bin/stylish_tts/ — analiza

Zawartość: `config_loader.py`, `stylish_utils.py`, `text_utils.py`, `model.yml`, foldery `models/` (dyskryminatory + modele), `stylish_lib/` (zagnieżdżony pakiet `stylish_lib/stylish_lib/`), oraz `checkpoint_final/checkpoint_final/` — katalog z wagami wytrenowanego modelu.

- **Rozmiar: 567 MB całość, z czego 566 MB to `checkpoint_final/`** (same wagi modelu TTS).
- Kod .py (~4 pliki widoczne na top-level + to co w `models/`/`stylish_lib/`) to **vendored zewnętrzny kod** silnika TTS (StyleTTS-pochodna architektura, sądząc po nazwie), nie autorski kod projektu — brak tu żadnej integracji ze stylem `modules/`, to samodzielny pakiet wklejony do `bin/`.
- Cały `bin/` (w tym `stylish_tts/`) jest **gitignored** — więc te 567 MB nigdy nie trafiły do repo, żyją tylko lokalnie na dysku usera.
- **Potwierdzenie**: to dobry kandydat do usunięcia zgodnie z decyzją usera — jest to (a) niewersjonowane, (b) ogromne pod względem rozmiaru dyskowego, (c) osobny wendorowany model TTS niepowiązany z resztą architektury `modules/tts_elevenbytes.py` (co sugeruje nazwa modułu — projekt już ma inny silnik TTS jako główny). Usunięcie nie wpłynie na git history (nic tam nie było trackowane), tylko zwolni ~567 MB lokalnie.

---

## 5. Rozjazd ze stylem MangaShift

MangaShift (`C:\Users\MattyMroz\Desktop\PROJECTS\MangaShift\mangashift/`) prezentuje warstwową architekturę pakietu Python z jasnym podziałem odpowiedzialności:

```
mangashift/
├── api/            # warstwa HTTP (routers, schemas, middleware)
├── cli/            # warstwa CLI
├── config/         # konfiguracja
├── db/             # baza danych (modele, migracje, repozytoria, uow)
├── events/         # event bus
├── input/          # ingest/loading danych wejściowych
├── models/         # katalog modeli ML (rejestr wag)
├── pipeline/       # kroki pipeline'u per domena (detection/inpainting/ocr/translation/tts)
├── platform/       # detekcja GPU/sprzętu
├── retention/      # sprzątanie/retencja danych
├── runtime/        # zarządzanie runtime (CUDA, llama, VRAM)
├── services/       # fasady domenowe + rejestry silników (services/<domena>/engines/)
├── setup/          # wizard instalacyjny, doctor (diagnostyka)
├── storage/        # warstwa dostępu do plików/workspace
├── usecases/       # warstwa use-case (logika biznesowa, orkiestracja)
├── utils/          # bogate narzędzia (rich_console/, logger/, timer/, safe_fs, safe_path...)
└── worker/         # worker w tle (job queue)
```

Kluczowe różnice wobec mm_avh:

1. **Jeden pakiet Python (`mangashift/`) vs płaskie top-level foldery.** W mm_avh `modules/`, `utils/`, `data/`, `tests/` leżą jako niezależne top-level foldery bez wspólnego pakietu-parasola — nie ma jednego `mm_avh/` z podpakietami. To utrudnia jednoznaczne importy i rozgraniczenie warstw.

2. **Brak warstwy `services/` z rejestrem silników.** W mm_avh `modules/tts_elevenbytes.py`, `modules/translator.py` itd. to płaskie moduły-worki (każdy robi wszystko dla swojej domeny) zamiast fasada + rejestr silników jak w MangaShift (`services/<domena>/engines/__init__.py`). Gdyby mm_avh chciał kiedyś dodać drugi silnik TTS obok elevenbytes (np. ten z `bin/stylish_tts` — zanim go usunięto), obecna struktura wymusiłaby edycję wnętrza `tts_elevenbytes.py`, a nie dodanie wpisu do rejestru.

3. **Brak `usecases/` (warstwy orkiestracji use-case).** `start.py` w mm_avh pełni rolę zarówno CLI, jak i orkiestratora pipeline'u (22 KB w jednym pliku root) — w MangaShift ta odpowiedzialność byłaby rozbita między `cli/run_cmd.py` (cienki CLI) i `usecases/pipeline.py` (logika).

4. **`utils/` w mm_avh jest płaski i ubogi** (4 pliki) vs MangaShift `utils/` ma podfoldery `rich_console/`, `logger/`, `timer/` — to dokładnie przedmiot toczącej się migracji (`docs/brainstorms/2026-07-08-migracja-utils-i-paski-postepu-brief.md`), czyli świadomie identyfikowany dług.

5. **`storage/`/`input/` (workspace jako warstwa abstrakcji) vs `working_space/` jako gołe dane.** MangaShift ma `storage/workspace.py` i `input/workspace.py` — kod zarządzający workspace jako abstrakcją (ścieżki, czyszczenie, walidacja). W mm_avh `working_space/` to czysto dane bez żadnej warstwy kodu nad nim (poza zabłąkanym `convert_eac3_to_mp3.py`) — brak odpowiednika `storage/`.

6. **Brak `docs/architecture/`** w mm_avh — MangaShift ma dedykowany folder na dokumenty architektoniczne (`docs/architecture/docelowa-architektura-jedno-zrodlo.md` to przykład). W mm_avh dokumentacja architektoniczna nie istnieje jeszcze jako osobna kategoria w `docs/` (jest `brainstorms/` i `superpowers/plans/`, ale nie `architecture/`).

**Wniosek:** mm_avh jest obecnie w fazie "skryptowego CLI" — płaska struktura odpowiadająca mniejszej skali projektu, podczas gdy MangaShift to dojrzały, wielowarstwowy system z rozdzieloną odpowiedzialnością (API/CLI/usecases/services/pipeline). Nie jest to błąd per se (mm_avh jest dużo mniejszym projektem), ale jeśli projekt ma rosnąć (więcej silników TTS/tłumaczeń), obecny brak warstwy `services/`+rejestr i mieszanie CLI z logiką w `start.py` będzie pierwszym miejscem bólu.

---

## 6. .gitignore — co ignorowane, co nie

Sprawdzone w `.gitignore` (project-specific rules na końcu pliku):

- **`bin/`** — cały folder ignorowany (słusznie, to duże wendorowane binarki, w tym `stylish_tts/` 567 MB).
- **`temp/`** — cały folder ignorowany (skrypty i dane robocze wymienione w sekcji 3 pkt 3 — **ryzyko**: przydatne skrypty jak `make_full_report.py` nie są wersjonowane).
- **`working_space/**`** z wyjątkami tylko dla struktury folderów (`.gitkeep` w `output/`, `temp/`, `temp/main_subs/`, `temp/alt_subs/`) — poprawnie zaprojektowane, żeby trzymać szkielet folderów bez zaśmiecania repo danymi użytkownika. Potwierdzone: żadne z plików wymienionych w sekcji 3 (MKV, srt, .lnk, desktop.ini, convert_eac3_to_mp3.py) nie trafiają do gita.
- **`.claude/`** — explicite ignorowany z komentarzem "źródło prawdy tam" (czyli synchronizowane z zewnętrznym repo agentów).
- **`.github/`** — explicite ignorowany ("internal, not for VCS").
- **`data/settings.json`** — explicite ignorowany (sekrety/klucze API), potwierdzone że to jedyny plik z `data/` tak potraktowany — `data/config.py` i `data/settings.py` (kod) zostają w gicie.
- **Generyczne wzorce** (`*.mkv`, `*.mp3`, `*.srt`, `*.ass`, `*.png`, `*.jpg` itd.) — pokrywają większość typów danych medialnych/binarnych niezależnie od lokalizacji, co jest dodatkowym zabezpieczeniem gdyby ktoś dodał plik multimedialny poza `working_space/`.
- **Braki**: `data/.mypy_cache/`, `modules/.mypy_cache/`, `tests/.mypy_cache/`, `working_space/.mypy_cache/` nie są jawnie wymienione, ale `.mypy_cache/` jako nazwa folderu nie jest w `.gitignore` w ogóle na poziomie generycznym (`.gitignore` ma tylko `.pytest_cache/`, brak wzorca `.mypy_cache/`) — **luka**: gdyby ktoś przez pomyłkę zrobił `git add -A` w złym katalogu, cache mypy mógłby trafić do repo. Weryfikacja `git ls-files` potwierdza, że obecnie nic z `.mypy_cache/` nie jest trackowane (uratowane przez to, że te foldery nie leżą w katalogach jawnie dodawanych), ale warto dodać `.mypy_cache/` do `.gitignore` jako zabezpieczenie.
- **Znaleziono odwrotny przypadek** — `bin/` jest w `.gitignore`, ale mimo to **218 plików z `bin/` jest wersjonowanych w gicie** (`git ls-files bin | wc -l` → 218): m.in. `bin/ffmpeg/LICENSE`, `bin/ffmpeg/README.txt`, `bin/ffmpeg/doc/*.html` (dokumentacja HTML ffmpeg), `bin/balabolka/readme.pol.txt`. To klasyczny efekt "gitignore nie działa retroaktywnie" — te pliki trafiły do repo zanim reguła `bin/` została dodana do `.gitignore`, i git dalej je śledzi mimo ignorowania folderu. Nieszkodliwe rozmiarowo (to tekst/HTML, nie binarki), ale niespójne z intencją "bin/ w całości poza gitem" — do wyczyszczenia przez `git rm -r --cached bin/` jeśli ma być w 100% spójne z `.gitignore`.
- Pozostałe top-level foldery zgodne z oczekiwaniami: `tests` 22, `docs` 11, `modules` 8, `utils` 4, `data` 2 (`config.py`+`settings.py`) — bez niespodzianek.

---

## Podsumowanie kluczowych rekomendacji

1. **Usunąć `bin/stylish_tts/`** (567 MB, vendored model TTS niepowiązany z resztą kodu) — zgodnie z decyzją usera.
2. **Przenieść/uporządkować `working_space/convert_eac3_to_mp3.py`** — kod nie powinien leżeć w folderze danych.
3. **Posprzątać root `working_space/`** — luźne pliki MKV/srt, `.lnk`, `desktop.ini`.
4. **Zdecydować los `temp/`** — cały folder gitignored, ale zawiera potencjalnie wartościowe skrypty (`make_full_report.py`, `analyze_dataset.py` itd.) obok jednorazowych danych ML. Rozdzielić: skrypty → `tests/` lub nowy `scripts/`, dane → zostają lokalne/gitignored.
5. **Rozdzielić `tests/`** na faktyczne testy (`*_test.py`) i eksperymenty jednorazowe (`chat.py`, `*_alt.py`, `MM_AVH_pre.py`) — te drugie pasują bardziej do `temp/` lub osobnego `scripts/experiments/`.
6. **Scentralizować `.mypy_cache/`** (obecnie w 5 miejscach: root, `data/`, `modules/`, `tests/`, `working_space/`) przez jeden `cache_dir` w konfiguracji mypy, i dodać `.mypy_cache/` do `.gitignore` jako zabezpieczenie.
7. **Architektura docelowa**: jeśli projekt ma rosnąć, rozważyć przejście z płaskich top-level folderów na jeden pakiet (`mm_avh/`) z warstwami `services/`+rejestr silników wzorem MangaShift — na razie płaska struktura jest adekwatna do skali, ale to pierwsze miejsce, które ograniczy rozwój (np. dodanie drugiego silnika TTS/tłumaczeń).
