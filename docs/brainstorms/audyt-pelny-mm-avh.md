# 📚 PEŁNY AUDYT PROJEKTU mm_avh_working_space

> Wygenerowano: 2026-07-12 | 6 subagentów Sonnet równolegle (1 kartograf + 5 audytorów per obszar)
> Zakres: rdzeń produkcyjny (start.py, constants.py, data/, modules/, utils/). Pominięto: bin/, .venv/, cache.
> Cel: baza pod plan refaktoryzacji na styl MangaShift (docs/architecture/).
> Metoda: skrupulatny spis KAŻDEJ klasy/funkcji/metody/stałej + diagnoza per plik. Zweryfikowano grepem — 0 pominięć.

## 📊 pokrycie (zweryfikowane grepem class/def)

| obszar | pliki | klasy | funkcje/metody |
|--------|-------|-------|----------------|
| root + config | start.py, constants.py, data/config.py, data/settings.py | 2 | 55 |
| ekstrakcja/merge | mkvtoolnix, mkv_processing, track_selector | 2 | 29 |
| napisy | subtitle, translator, style_classifier | 5 | 37 |
| TTS | subtitle_to_speech, tts_elevenbytes | 8 | 67 |
| utils | cool_animation, execution_timer, number_in_words, text_chunker | 6 | 41 |
| **RAZEM** | **16 plików .py** | **23 klasy** | **~229 funkcji/metod** |

## 🗂️ spis treści

- [00 — mapa projektu (struktura, śmieci, rozjazd z MangaShift)](#część-00--mapa-projektu)
- [01 — root + config](#część-01--root--config)
- [02 — modules: ekstrakcja i merge](#część-02--modules-ekstrakcja-i-merge)
- [03 — modules: napisy](#część-03--modules-napisy)
- [04 — modules: TTS](#część-04--modules-tts)
- [05 — utils](#część-05--utils)

---


# CZĘŚĆ 00 — mapa projektu

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

---


# CZĘŚĆ 01 — root + config

# RAPORT AUDYTU — obszar: root + config

---

## 📦 obszar: root + config — pliki: `start.py`, `constants.py`, `data/config.py`, `data/settings.py`

**Rola obszaru w projekcie:** To warstwa wejściowa i konfiguracyjna całego pipeline'u
(ekstrakcja MKV → refaktor napisów → tłumaczenie → TTS → merge). `start.py` jest
punktem wejścia CLI i orkiestratorem kroków (odpowiednik "pipeline" w architekturze
MangaShift, tylko proceduralny — brak warstwy serwisu). `constants.py` definiuje
wszystkie ścieżki na dysku (working_space, bin/*) oraz globalny obiekt konsoli `rich`
z motywem kolorów. `data/config.py` to statyczny rejestr opcji do wyboru w menu
(tłumacze, głosy TTS, wyjścia). `data/settings.py` to dataclass `Settings` +
interaktywny kreator ustawień, który czyta/pisze `data/settings.json`.

**Zależności zewnętrzne obszaru:** `rich` (Console, Progress, Theme, Text),
`natsort`, `pydub.AudioSegment` (konfigurowana w `constants.py` do użycia lokalnego
ffmpeg), stdlib (`concurrent.futures`, `msvcrt.getch`, `os`, `shutil`, `threading`,
`json`, `dataclasses`). Wewnętrznie: `start.py` importuje z `constants`, `data.settings`,
`modules.mkvtoolnix`, `modules.subtitle`, `modules.subtitle_to_speech`,
`modules.translator`, `modules.mkv_processing`, `utils.cool_animation`,
`utils.execution_timer`. `data/settings.py` importuje `constants` i `data.config`,
oraz lazy-importuje `modules.tts_elevenbytes.TTS` wewnątrz jednej metody.

---

## 📄 plik: `start.py` (591 linii)

### przeznaczenie
Punkt wejścia programu (`if __name__ == '__main__'`) i jednocześnie cały "pipeline"
w formie sekwencji wywołań funkcji modułowych — brak klasy Pipeline, brak kroków jako
obiektów. Odpowiada za: utworzenie katalogów roboczych, wyświetlenie logo, aktualizację
ustawień, ekstrakcję ścieżek z MKV (równolegle), refaktoryzację napisów do formatu
standardowego, tłumaczenie, opcjonalną konwersję liczb na słowa, generowanie audio TTS,
przetwarzanie plików wyjściowych (merge/burn) i czyszczenie katalogów tymczasowych.
Obsługuje dwa tryby: interaktywny (pytania T/N) i automatyczny (`settings.auto_mode`).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `sys` | stdlib | `sys.exit(0)` przy przerwaniu |
| `ThreadPoolExecutor, as_completed` | concurrent.futures | równoległa ekstrakcja MKV |
| `StringIO` | io | bufor na log podprocesu w trybie auto (per-plik konsola) |
| `getch` | msvcrt | czekanie na klawisz na końcu programu (Windows-only) |
| `cpu_count, listdir, makedirs, path` | os | listowanie plików, tworzenie katalogów, limit workerów |
| `rmtree` | shutil | czyszczenie katalogów temp |
| `Lock` | threading | ochrona współdzielonego `already_polish` w wątkach |
| `Dict, List, Set` | typing | adnotacje typów |
| `natsorted` | natsort | naturalne sortowanie nazw plików (odc. 2 przed odc. 10) |
| `Console` | rich.console | dodatkowa konsola-bufor per-wątek w trybie auto |
| `BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn` | rich.progress | pasek postępu ekstrakcji w trybie auto |
| `Text` | rich.text | konwersja zbuforowanego ANSI-logu na obiekt rich |
| `WORKING_SPACE`, `WORKING_SPACE_OUTPUT`, `WORKING_SPACE_TEMP`, `WORKING_SPACE_TEMP_MAIN_SUBS`, `WORKING_SPACE_TEMP_ALT_SUBS`, `CONSOLE_THEME`, `console` | constants | ścieżki robocze + globalna konsola/motyw |
| `Settings` | data.settings | ustawienia użytkownika |
| `MkvToolNix` | modules.mkvtoolnix | ekstrakcja ścieżek audio/napisów z MKV |
| `SubtitleRefactor` | modules.subtitle | konwersje formatów napisów |
| `SubtitleToSpeech` | modules.subtitle_to_speech | generowanie audio TTS z SRT |
| `SubtitleTranslator` | modules.translator | tłumaczenie SRT |
| `MKVProcessing` | modules.mkv_processing | scalanie/wypalanie plików wyjściowych |
| `CoolAnimation` | utils.cool_animation | animacja logo startowego |
| `execution_timer` | utils.execution_timer | dekorator mierzący czas `main()` |

### stałe / zmienne modułowe
Brak stałych modułowych — plik zawiera wyłącznie funkcje. Jedyna zmienna na poziomie
`if __name__`: `directories: List[str]` (linia 579) — lokalna lista katalogów do
utworzenia przed startem.

### klasy
Brak klas w tym pliku.

### funkcje modułowe

##### `check_and_create_directories(directories: List[str])` (linia 36)
- **Co robi:** Iteruje po liście ścieżek, tworzy każdy katalog, który jeszcze nie istnieje.
- **Przyjmuje:** `directories` — lista ścieżek katalogów.
- **Zwraca:** `None` (brak adnotacji zwrotu mimo `# ✅` sugerującego "sprawdzone").
- **Efekty uboczne:** tworzy katalogi na dysku (`makedirs`).
- **Woła:** `path.exists`, `makedirs`.
- **Wyjątki:** brak obsługi — `makedirs` może rzucić `OSError` przy race condition/braku uprawnień.
- **Uwagi:** brak adnotacji zwrotu `-> None`; niespójne z resztą pliku, gdzie część funkcji ma jawne `-> None`.

##### `display_logo()` (linia 48)
- **Co robi:** Tworzy `CoolAnimation`, odtwarza animację logo, drukuje baner tekstowy.
- **Przyjmuje:** nic.
- **Zwraca:** `None` (brak adnotacji).
- **Efekty uboczne:** print do konsoli, potencjalnie animacja czasowa (zależna od `CoolAnimation.display`, poza obszarem audytu).
- **Woła:** `CoolAnimation()`, `.display()`, `console.print`.
- **Wyjątki:** brak obsługi.
- **Uwagi:** brak `-> None`.

##### `ask_user(question: str) -> bool` (linia 58)
- **Co robi:** Wyświetla pytanie i czeka na odpowiedź T/Y jako `True`.
- **Przyjmuje:** `question` — treść pytania.
- **Zwraca:** `bool` — `True` gdy user wpisał `t`/`y` (case-insensitive), inaczej `False`.
- **Efekty uboczne:** blokujący `input()`; przy `EOFError`/`KeyboardInterrupt` drukuje komunikat i `sys.exit(0)` — **kończy cały proces**, nie tylko funkcję.
- **Woła:** `console.print`, `input`, `sys.exit`.
- **Wyjątki:** łapie `EOFError`, `KeyboardInterrupt` i zamienia je w `sys.exit(0)`.
- **Uwagi:** funkcja centralna wołana przez niemal każdą funkcję pytającą — silne sprzężenie stylu I/O w całym pliku (brak abstrakcji "prompter").

##### `update_settings() -> Settings` (linia 76)
- **Co robi:** Pyta użytkownika czy zmienić ustawienia; jeśli tak, uruchamia kreator i zapisuje do pliku; zawsze zwraca świeżo wczytane ustawienia z dysku.
- **Przyjmuje:** nic.
- **Zwraca:** `Settings` — aktualny stan po ewentualnej zmianie.
- **Efekty uboczne:** może nadpisać `data/settings.json`; drukuje komunikaty.
- **Woła:** `ask_user`, `Settings.change_settings_save_to_file`, `Settings.load_from_file`.
- **Wyjątki:** propaguje wyjątki z wywoływanych metod.
- **Uwagi:** docstring wyjaśnia świadomą decyzję projektową (prompt ustawień zawsze widoczny, nawet w auto_mode) — dobra dokumentacja intencji, rzadka w tym pliku.

##### `extract_tracks_from_mkv(auto: bool = False) -> Set[str]` (linia 96)
- **Co robi:** W trybie manualnym pyta o zgodę i ekstrahuje ścieżki równolegle bez paska postępu, zbierając logi błędów per-plik; w trybie auto deleguje do `_extract_tracks_auto` (pasek postępu). Zwraca zbiór nazw bazowych plików, których napisy są już PL (do pominięcia tłumaczenia).
- **Przyjmuje:** `auto` — czy pominąć pytanie i użyć trybu automatycznego.
- **Zwraca:** `Set[str]` nazw plików (bez `.mkv`) z już-polskimi napisami.
- **Efekty uboczne:** operacje na plikach przez `MkvToolNix`; wypisuje błędy do konsoli; uruchamia wątki (`ThreadPoolExecutor`).
- **Woła:** `ask_user`, `get_mkv_files`, `natsorted`, `_parallelism`, `MkvToolNix(...)`, `mkv.get_mkv_info()`, `mkv.mkv_extract_track(...)`, `_extract_tracks_auto`.
- **Wyjątki:** łapie `Exception` per-task wewnątrz `_extract_one` (linia 138) i loguje, nie przerywa całości — reszta plików kontynuuje.
- **Uwagi:** zagnieżdżona funkcja `_extract_one` (linia 124) domyka `polish_lock` i `already_polish` przez closure — brak type-hinta na `-> None` w deklaracji jest OK (jest), ale wzorzec closure+Lock powtórzony 1:1 w `_extract_tracks_auto` — duplikacja logiki równoległości (dwie prawie identyczne implementacje "ekstrahuj równolegle").

##### `_extract_tracks_auto(sorted_files: List[str]) -> Set[str]` (linia 145)
- **Co robi:** Ekstrahuje wszystkie pliki MKV równolegle z żywym paskiem postępu `rich.Progress`; każdy wątek pisze do własnego bufora `StringIO`/`Console`, żeby uniknąć przeplatania logów, a po zakończeniu zadania wypisuje bufor na docelową konsolę.
- **Przyjmuje:** `sorted_files` — nazwy plików MKV w kolejności wyświetlania.
- **Zwraca:** `Set[str]` — nazwy bazowe z już-polskimi napisami.
- **Efekty uboczne:** wątki, pisanie do konsoli przez `progress.console.print`, callback aktualizujący pasek (`progress.update`).
- **Woła:** `Progress(...)`, `_parallelism`, `progress.add_task`, `_task_label`, `ThreadPoolExecutor`, wewnętrzną `_extract_one(filename, task_id)` (linia 166), `Text.from_ansi`.
- **Wyjątki:** łapie `Exception` per-task (linia 196), loguje przez `progress.console.print`, nie przerywa reszty.
- **Uwagi:** duplikat wzorca równoległości z `extract_tracks_from_mkv` (różni się tylko obecnością paska postępu i buforowania) — kandydat do wspólnej funkcji pomocniczej `_run_parallel(files, worker_fn)`. Callback `lambda pct: progress.update(task_id, completed=pct)` (linia 174) tworzy domknięcie w pętli przez `pool.submit` — poprawne, bo `task_id` jest przekazywany jako argument, nie łapany przez referencję z pętli.

##### `_task_label(filename: str, width: int = 40) -> str` (linia 203)
- **Co robi:** Buduje etykietę paska postępu — usuwa rozszerzenie `.mkv` i przycina do `width` znaków z wielokropkiem `…`.
- **Przyjmuje:** `filename` — nazwa pliku; `width` — maks. długość etykiety (domyślnie 40).
- **Zwraca:** `str` — etykieta gotowa do wyświetlenia.
- **Efekty uboczne:** brak.
- **Woła:** nic zewnętrznego.
- **Wyjątki:** brak.
- **Uwagi:** magic number `40` jako domyślna szerokość — nieskonfigurowalne globalnie, ale lokalnie uzasadnione (jedna linia paska postępu).

##### `get_mkv_files(directory: str) -> List[str]` (linia 218)
- **Co robi:** Zwraca listę plików `.mkv` w podanym katalogu (nierekurencyjnie).
- **Przyjmuje:** `directory` — ścieżka katalogu.
- **Zwraca:** `List[str]` nazw plików.
- **Efekty uboczne:** odczyt systemu plików.
- **Woła:** `listdir`, `path.isfile`, `path.join`.
- **Wyjątki:** `FileNotFoundError`/`OSError` jeśli katalog nie istnieje — nieobsłużone tutaj (ale `check_and_create_directories` tworzy katalogi wcześniej w `__main__`).
- **Uwagi:** filtr rozszerzenia zahardkodowany `'.mkv'` — brak wsparcia dla `.mp4` mimo że `process_output_files` (linia 502) już to rozróżnia gdzie indziej.

##### `refactor_subtitles(auto: bool = False)` (linia 232)
- **Co robi:** Zbiera pliki napisów z katalogu temp (9 rozszerzeń), sortuje naturalnie i refaktoryzuje każdy.
- **Przyjmuje:** `auto` — czy klasyfikator ASS/SSA ma dzielić style automatycznie.
- **Zwraca:** brak adnotacji (`None`).
- **Efekty uboczne:** operacje na plikach przez `refactor_subtitle_file`.
- **Woła:** `get_files_with_extensions`, `natsorted`, `refactor_subtitle_file`.
- **Wyjątki:** propaguje z `refactor_subtitle_file`.
- **Uwagi:** lista rozszerzeń (linia 240-244) jest lokalną stałą wewnątrz funkcji, nie modułową — powinna być stałą na poziomie modułu lub w `constants.py`, bo opisuje domenową wiedzę "jakie formaty napisów obsługujemy".

##### `get_files_with_extensions(directory: str, extensions: List[str]) -> List[str]` (linia 253)
- **Co robi:** Zwraca pliki z katalogu pasujące do dowolnego z podanych rozszerzeń.
- **Przyjmuje:** `directory`, `extensions` — lista sufiksów.
- **Zwraca:** `List[str]`.
- **Efekty uboczne:** odczyt systemu plików.
- **Woła:** `listdir`, `path.isfile`, `path.join`, `any`.
- **Wyjątki:** brak obsługi.
- **Uwagi:** generyczna, dobrze napisana funkcja pomocnicza.

##### `refactor_subtitle_file(filename: str, auto: bool = False)` (linia 273)
- **Co robi:** Rozpoznaje typ pliku po rozszerzeniu i wywołuje odpowiednie kroki `SubtitleRefactor` (split ASS/SSA→SRT, przeniesienie SRT, konwersja TXT→SRT z magicznymi parametrami chunkowania).
- **Przyjmuje:** `filename`; `auto` — tryb automatyczny dla podziału stylów ASS/SSA.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** operacje plikowe przez `SubtitleRefactor`.
- **Woła:** `SubtitleRefactor(filename)`, `.split_ass(auto_mode=auto)`, `.ass_to_srt()`, `.move_srt()`, `.txt_to_srt(chunk_limit=250, sentence_length=750, split_method='word')`.
- **Wyjątki:** propaguje z `SubtitleRefactor`.
- **Uwagi:** seria niezależnych `if` (nie `elif`) na rozszerzeniu — dokładnie wzorzec "if-y per typ" krytykowany w architekturze MangaShift (tam: rejestr silników zamiast if-ów). Magic numbers `250`, `750` niewyjaśnione w miejscu wywołania (brak komentarza czemu akurat te wartości) i niewyciągnięte do stałej/configu.

##### `translate_subtitles(settings: Settings, auto: bool = False, already_polish: Set[str] | None = None)` (linia 294)
- **Co robi:** W trybie manualnym pyta o zgodę i pyta plik po pliku; w trybie auto tłumaczy wszystko poza plikami już oznaczonymi jako polskie.
- **Przyjmuje:** `settings` — ustawienia tłumacza; `auto`; `already_polish` — zbiór nazw bazowych do pominięcia.
- **Zwraca:** brak adnotacji (`None`).
- **Efekty uboczne:** print, operacje tłumaczenia (sieciowe — Google/DeepL).
- **Woła:** `ask_user`, `get_srt_files`, `ask_to_translate_files`, `translate_files`.
- **Wyjątki:** propaguje.
- **Uwagi:** składnia `Set[str] | None` (PEP 604) miesza się z resztą pliku używającą `typing.Optional`/`typing.List` — niespójny styl adnotacji w jednym pliku (np. `data/settings.py` też miesza `Optional[str]` z `tuple[str, str, str, str]` w jednej metodzie, patrz niżej).

##### `get_srt_files(directory: str) -> List[str]` (linia 330)
- **Co robi:** Zwraca posortowaną naturalnie listę plików `.srt` w katalogu.
- **Przyjmuje:** `directory`.
- **Zwraca:** `List[str]`.
- **Efekty uboczne:** odczyt dysku.
- **Woła:** `listdir`, `path.isfile`, `natsorted`.
- **Wyjątki:** brak obsługi.
- **Uwagi:** funkcjonalnie nakłada się częściowo z `get_files_with_extensions` (ta druga generyczna, ta — specjalizowana i z sortowaniem wbudowanym) — dwa różne API do bardzo podobnej rzeczy.

##### `ask_to_translate_files(files: List[str]) -> dict` (linia 346)
- **Co robi:** Pyta użytkownika per plik, czy go przetłumaczyć, buduje mapę plik→bool.
- **Przyjmuje:** `files`.
- **Zwraca:** `dict` (typ zwrotu nieopisany generykiem — powinno być `Dict[str, bool]`, tak jak analogiczna `ask_to_generate_audio_files` niżej).
- **Efekty uboczne:** print, `input` przez `ask_user`.
- **Woła:** `console.print`, `ask_user`.
- **Wyjątki:** propaguje z `ask_user` (w tym `sys.exit`).
- **Uwagi:** typ zwrotu `dict` zamiast `Dict[str, bool]` — niespójność z analogiczną funkcją audio (linia 444) w tym samym pliku.

##### `translate_files(files_to_translate: dict, settings: Settings)` (linia 369)
- **Co robi:** Dla każdego pliku oznaczonego do tłumaczenia woła tłumacza na głównym katalogu napisów, a jeśli istnieje odpowiednik w katalogu alt_subs — tłumaczy też tam.
- **Przyjmuje:** `files_to_translate` — mapa plik→bool; `settings`.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** zapisuje przetłumaczone pliki (sieciowe wywołania tłumacza).
- **Woła:** `SubtitleTranslator()`, `.translate_srt(filename, WORKING_SPACE_TEMP_MAIN_SUBS, settings)`, `path.exists`, `path.join`, ponownie `.translate_srt(...)` dla alt_subs.
- **Wyjątki:** propaguje z `SubtitleTranslator`.
- **Uwagi:** parametr `dict` bez generyków (jak wyżej).

##### `convert_numbers_to_words()` (linia 390)
- **Co robi:** Pyta użytkownika o zgodę na konwersję liczb→słowa, jeśli tak — pobiera pliki SRT i konwertuje.
- **Przyjmuje:** nic.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** print, modyfikacja plików SRT.
- **Woła:** `ask_user`, `get_srt_files`, `convert_numbers_in_files`.
- **Wyjątki:** propaguje.
- **Uwagi:** krok pomijany całkowicie w auto_mode (patrz `main()`, linia 567) — świadoma decyzja użytkownika udokumentowana komentarzem w `main`.

##### `convert_numbers_in_files(files: List[str])` (linia 402)
- **Co robi:** Dla każdego pliku pyta osobno o zgodę i konwertuje liczby na słowa przez `SubtitleRefactor`.
- **Przyjmuje:** `files`.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** print, zapis plików.
- **Woła:** `console.print`, `ask_user`, `SubtitleRefactor(filename)`, `.convert_numbers_in_srt()`.
- **Wyjątki:** propaguje.
- **Uwagi:** brak.

##### `generate_audio_for_subtitles(settings: Settings, auto: bool = False) -> None` (linia 420)
- **Co robi:** W trybie manualnym pyta o zgodę i per-plik; w auto generuje audio dla wszystkich plików SRT bez pytań.
- **Przyjmuje:** `settings`; `auto`.
- **Zwraca:** `None` (jawnie adnotowane).
- **Efekty uboczne:** generowanie plików audio (TTS, potencjalnie sieciowe dla ElevenLabs/Edge).
- **Woła:** `ask_user`, `get_srt_files`, `ask_to_generate_audio_files`, `generate_audio_files`.
- **Wyjątki:** propaguje.
- **Uwagi:** brak.

##### `ask_to_generate_audio_files(files: List[str]) -> Dict[str, bool]` (linia 444)
- **Co robi:** Pyta użytkownika per plik, czy generować audio.
- **Przyjmuje:** `files`.
- **Zwraca:** `Dict[str, bool]`.
- **Efekty uboczne:** print, `input`.
- **Woła:** `console.print`, `ask_user`.
- **Wyjątki:** propaguje.
- **Uwagi:** wzorcowo taka sama funkcja jak `ask_to_translate_files`, ale z lepszym typem zwrotu — dowód niespójności wewnątrz pliku.

##### `generate_audio_files(files_to_generate_audio: Dict[str, bool], settings: Settings) -> None` (linia 466)
- **Co robi:** Dla każdego pliku oznaczonego `True` tworzy `SubtitleToSpeech` i generuje audio.
- **Przyjmuje:** `files_to_generate_audio`; `settings`.
- **Zwraca:** `None`.
- **Efekty uboczne:** generowanie plików audio na dysku.
- **Woła:** `SubtitleToSpeech(filename)`, `.generate_audio(settings)`.
- **Wyjątki:** propaguje.
- **Uwagi:** zmienna `audio_generator: SubtitleToSpeech` deklarowana z adnotacją przed pętlą (linia 474) — niepotrzebna przedwczesna deklaracja typu (Python i tak wywnioskuje typ przy przypisaniu w pętli); stylistyczny szum.

##### `refactor_alt_subtitles()` (linia 481)
- **Co robi:** Konwertuje wszystkie alternatywne napisy (katalog alt_subs) z SRT do ASS.
- **Przyjmuje:** nic.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** zapis plików ASS.
- **Woła:** `get_srt_files`, `natsorted`, `SubtitleRefactor(filename)`, `.srt_to_ass()`.
- **Wyjątki:** propaguje.
- **Uwagi:** brak pytania użytkownika (bezwarunkowy krok w obu trybach) — niespójne z resztą pipeline'u, gdzie prawie każdy krok ma prompt; brak komentarza wyjaśniającego czemu ten krok jest zawsze wykonywany.

##### `process_output_files(settings: Settings)` (linia 492)
- **Co robi:** Grupuje pliki wyjściowe po nazwie bazowej (bez `.mkv`/`.mp4`), dla każdej grupy niepustej uruchamia `MKVProcessing` ze stałym `crf_value='18'` i `preset_value='medium'`.
- **Przyjmuje:** `settings`.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** merge/burn plików wyjściowych (ffmpeg/mkvmerge), potencjalnie długotrwałe operacje I/O.
- **Woła:** `listdir(WORKING_SPACE_OUTPUT)`, `path.splitext`, `MKVProcessing(filename=..., crf_value=..., preset_value=...)`, `.process_mkv(settings)`.
- **Wyjątki:** brak obsługi — błąd przetwarzania jednego pliku przerwie całą pętlę (w przeciwieństwie do ekstrakcji, gdzie błędy per-plik są izolowane przez `try/except` w wątkach).
- **Uwagi:** `crf_value='18'` i `preset_value='medium'` są zahardkodowane jako magic values wprost w kodzie (linie 511-512), mimo komentarza z linkiem do dokumentacji ffmpeg (507-509) tłumaczącego zakres wartości — powinny być w `constants.py` lub `Settings`, użytkownik nie ma opcji ich zmienić mimo że reszta pipeline'u jest bardzo konfigurowalna (patrz `Settings` z 15 polami). To wyraźna niespójność: TTS ma rozbudowaną konfigurację per-silnik, a encoding wyjściowy — żadnej.

##### `clear_temp_folders()` (linia 516)
- **Co robi:** Usuwa i odtwarza katalogi tymczasowe (temp, main_subs, alt_subs).
- **Przyjmuje:** nic.
- **Zwraca:** brak adnotacji.
- **Efekty uboczne:** `rmtree` + `makedirs` — nieodwracalne kasowanie plików tymczasowych.
- **Woła:** `rmtree(folder, ignore_errors=True)`, `makedirs(folder, exist_ok=True)`.
- **Wyjątki:** `ignore_errors=True` tłumi błędy `rmtree` cicho — brak logowania czy czyszczenie się faktycznie powiodło.
- **Uwagi:** cichy `ignore_errors=True` to potencjalny code smell — jeśli katalog jest zablokowany (np. przez otwarty plik), użytkownik nie dowie się, że temp nie został wyczyszczony.

##### `_parallelism(item_count: int, cap: int) -> int` (linia 527)
- **Co robi:** Wylicza liczbę workerów jako `max(1, min(item_count, cores, cap))` — nie więcej niż liczba elementów, rdzeni CPU ani zadanego capu.
- **Przyjmuje:** `item_count` — liczba elementów do przetworzenia; `cap` — górny limit właściwy dla danego etapu.
- **Zwraca:** `int` w zakresie `[1, min(item_count, cpu_count, cap)]`.
- **Efekty uboczne:** brak.
- **Woła:** `cpu_count()`.
- **Wyjątki:** brak (broni się przed `cpu_count() is None` przez `or 1`).
- **Uwagi:** dobrze udokumentowana, czysta funkcja pomocnicza — wzorcowy fragment pliku. Jedyne miejsce w `start.py` z pełnym docstringiem Google-style + wyjaśnieniem "dlaczego".

##### `main()` (linia 545, dekorowana `@execution_timer`)
- **Co robi:** Orkiestruje cały pipeline sekwencyjnie: logo → ustawienia → (jeśli auto: komunikat) → ekstrakcja → refaktor napisów → tłumaczenie → (opcjonalnie) konwersja liczb → generowanie audio → refaktor alt-napisów → przetwarzanie wyjścia → czyszczenie temp.
- **Przyjmuje:** nic.
- **Zwraca:** brak adnotacji (`None`).
- **Efekty uboczne:** cała reszta programu — pisze pliki, drukuje, generuje audio, koduje wideo.
- **Woła:** `display_logo`, `update_settings`, `console.print`, `extract_tracks_from_mkv`, `refactor_subtitles`, `translate_subtitles`, `convert_numbers_to_words`, `generate_audio_for_subtitles`, `refactor_alt_subtitles`, `process_output_files`, `clear_temp_folders`.
- **Wyjątki:** nie łapie nic sam — deleguje do `try/except` w bloku `__main__`.
- **Uwagi:** to jest de facto "pipeline" projektu, ale bez żadnej struktury kroków (brak listy kroków, brak możliwości włączenia/wyłączenia kroku programowo poza `auto`/interaktywnym pytaniem) — w porównaniu do MangaShift (`STEP_REGISTRY`, kroki jako klocki) to płaska sekwencja wywołań, całkowicie przeciwna zasadzie "pipeline układa z rejestru kroków".

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** Spójny wzorzec "ask → jeśli tak → wykonaj" dla każdego kroku; dobra izolacja błędów w ekstrakcji równoległej (`try/except Exception` per-task, reszta kontynuuje); `_parallelism` to czysta, dobrze udokumentowana funkcja; jasny podział auto/manual przez pojedynczy parametr `auto` przekazywany explicite (nie globalny stan); docstringi Google-style z sensownym opisem "dlaczego" w kluczowych miejscach (`update_settings`, `_extract_tracks_auto`, `_parallelism`).
- **⚠️ dług techniczny / code smells:**
  - Duplikacja logiki "ekstrahuj równolegle z ThreadPoolExecutor + Lock" między `extract_tracks_from_mkv` (linia 96-142) i `_extract_tracks_auto` (linia 145-200) — dwie osobne implementacje tego samego wzorca.
  - Niespójne typy zwrotu: `dict` bez generyków (`ask_to_translate_files:346`, `translate_files:369`) vs `Dict[str, bool]` (`ask_to_generate_audio_files:444`).
  - Brakujące adnotacje `-> None` w wielu funkcjach (`check_and_create_directories:36`, `display_logo:48`, `refactor_subtitles:232`, `refactor_subtitle_file:273`, `translate_subtitles:294`, `convert_numbers_to_words:390`, `convert_numbers_in_files:402`, `refactor_alt_subtitles:481`, `process_output_files:492`, `clear_temp_folders:516`, `main:545`) vs jawne `-> None` gdzie indziej (`generate_audio_for_subtitles:420`, `generate_audio_files:466`).
  - Magic values: `crf_value='18'`, `preset_value='medium'` zahardkodowane w `process_output_files:511-512`; `chunk_limit=250, sentence_length=750` w `refactor_subtitle_file:289-291`; `width: int = 40` w `_task_label:203`; cap `6` powtórzony dwukrotnie jako literal (`extract_tracks_from_mkv:131`, `_extract_tracks_auto:181`) zamiast stałej nazwanej.
  - `ignore_errors=True` w `clear_temp_folders:523` cicho tłumi błędy czyszczenia bez logowania.
  - `process_output_files:492-513` nie ma obsługi wyjątków per-plik (w przeciwieństwie do ekstrakcji) — jeden zepsuty plik przerywa cały merge wszystkich pozostałych.
  - Komentarze-znaczniki `# ✅` przy części definicji funkcji (np. linie 36, 48, 76, 96, 232, 390, 420, 481, 544) — niejasne pochodzenie/znaczenie, wyglądają jak ręczne checklisty z code review pozostawione w kodzie produkcyjnym; szum.
  - Mieszanie `Set[str] | None` (PEP 604, linia 295) z `Optional[...]`/`typing.List` gdzie indziej w tym samym pliku — niespójna konwencja adnotacji typów.
  - `ask_user:58` przy przerwaniu wywołuje `sys.exit(0)` głęboko zagnieżdżone w funkcji pomocniczej wołanej z kilkunastu miejsc — twarde wyjście z procesu ukryte w funkcji I/O, nie w warstwie top-level; utrudnia testowanie i reużycie w innym kontekście (np. GUI).
- **❌ niespójności ze stylem MangaShift:** Brak jakiejkolwiek warstwy serwisu/fasady — `main()` woła bezpośrednio funkcje modułowe, które z kolei bezpośrednio konstruują klasy z `modules.*` (`MkvToolNix`, `SubtitleRefactor`, `SubtitleToSpeech`, `SubtitleTranslator`, `MKVProcessing`) — brak dependency injection, wszystko tworzone inline. Brak rejestru kroków pipeline'u (MangaShift: `STEP_REGISTRY`, dodanie kroku = pakiet + wpis); tu dodanie nowego kroku pipeline'u wymaga edycji ciała `main()`. Zero-if-ów-per-silnik złamane w `refactor_subtitle_file:273-291` (seria `if` po rozszerzeniu pliku zamiast rejestru/dispatch tablicy). Brak jednego źródła prawdy dla "jakie rozszerzenia napisów obsługujemy" — lista w `refactor_subtitles:240-244` jest lokalna, nieeksportowana, nie do współdzielenia z inną częścią kodu.
- **🔗 sprzężenia:** Silne sprzężenie z modułami `modules.*` przez bezpośrednią konstrukcję klas (brak interfejsu/rejestru pośredniczącego) — zmiana konstruktora dowolnej z klas `MkvToolNix`/`SubtitleRefactor`/`SubtitleToSpeech`/`SubtitleTranslator`/`MKVProcessing` wymaga zmiany w `start.py`. Sprzężenie ze strukturą katalogów przez importowane stałe z `constants.py` (dobre — jedno źródło ścieżek). `ask_user` sprzęga cały plik z blokującym `input()` i globalnym `sys.exit` — nie da się łatwo zaadaptować do trybu nieinteraktywnego (skryptowego) bez przechodzenia przez `auto_mode`.

---

## 📄 plik: `constants.py` (133 linie, z czego ~24 to zakomentowany kod martwy)

### przeznaczenie
Moduł czysto deklaratywny — definiuje globalne stałe ścieżek (working_space, bin/mkvtoolnix,
bin/balabolka, bin/ffmpeg, bin/espeak-ng), konfiguruje `pydub.AudioSegment` do użycia
lokalnego ffmpeg **przed** jakimkolwiek innym importem `pydub` w projekcie, oraz tworzy
globalny obiekt `console: Console` z niestandardowym motywem kolorów `rich` używanym
w całym projekcie jako jedyne narzędzie do wypisywania tekstu. Importowany niemal
wszędzie (`from constants import ... console`).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `getcwd, pardir, path, environ` | os | budowa ścieżek względem katalogu roboczego, manipulacja `PATH` |
| `Console` | rich.console | globalny obiekt konsoli |
| `Theme` | rich.theme | definicja motywu kolorów |
| `AudioSegment` | pydub | konfiguracja globalnych ścieżek do binarki ffmpeg/ffprobe |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `SETTINGS_PATH` | 32 | `str` | `<cwd>/data/settings.json` — plik ustawień |
| `WORKING_SPACE` | 35 | `str` | `<cwd>/working_space` — katalog roboczy główny |
| `WORKING_SPACE_OUTPUT` | 36 | `str` | `<WORKING_SPACE>/output` |
| `WORKING_SPACE_TEMP` | 37 | `str` | `<WORKING_SPACE>/temp` |
| `WORKING_SPACE_TEMP_MAIN_SUBS` | 38 | `str` | `<WORKING_SPACE_TEMP>/main_subs` |
| `WORKING_SPACE_TEMP_ALT_SUBS` | 39 | `str` | `<WORKING_SPACE_TEMP>/alt_subs` |
| `MKVTOOLNIX_FOLDER` | 42-45 | `str` | `<parent_of_cwd>/mm_avh_working_space/bin/mkvtoolnix` |
| `MKV_EXTRACT_PATH` | 46 | `str` | ścieżka do `mkvextract.exe` |
| `MKV_MERGE_PATH` | 47 | `str` | ścieżka do `mkvmerge.exe` |
| `MKV_INFO_PATH` | 48 | `str` | ścieżka do `mkvinfo.exe` |
| `MKV_PROPEDIT_PATH` | 49 | `str` (brak jawnej adnotacji, w odróżnieniu od reszty) | ścieżka do `mkvpropedit.exe` |
| `BALABOLKA_FOLDER` | 52-55 | `str` | `<parent_of_cwd>/mm_avh_working_space/bin/balabolka` |
| `FFMPEG_FOLDER` | 56-59 | `str` | `<parent_of_cwd>/mm_avh_working_space/bin/ffmpeg/bin` |
| `BALABOLKA_PATH` | 60 | `str` | ścieżka do `balcon.exe` |
| `FFMPEG_PATH` | 61 | `str` | ścieżka do `ffmpeg.exe` |
| `FFPROBE_PATH` | 62 | `str` | ścieżka do `ffprobe.exe` |
| `ESPEAK_NG_FOLDER` | 65-68 | `str` | `<parent_of_cwd>/mm_avh_working_space/bin/espeak-ng` |
| `CONSOLE_THEME` | 83-107 | `Theme` | 23 style kolorów rich (purple/pink/red/brown/orange/yellow/green/blue/white/normal/black × bold/italic + `repr.number`) |
| `console` | 108 | `Console` | globalna instancja konsoli z `color_system="truecolor"` i `theme=CONSOLE_THEME` |

### klasy
Brak.

### funkcje modułowe
Brak — cały plik to top-level definicje i efekty uboczne importu (konfiguracja `PATH`
i `AudioSegment`, linie 72-80).

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** Jedno źródło prawdy dla ścieżek projektu — cały projekt importuje stałe stąd zamiast rozsypywać `path.join` po plikach. Świadomy, udokumentowany komentarzem trik kolejności importu (`FFMPEG_FOLDER` musi trafić do `PATH` i skonfigurować `AudioSegment` **przed** jakimkolwiek innym importem `pydub`, linie 70-76) — realny problem inżynierski rozwiązany poprawnie, choć kruchy (zależny od kolejności importów w całym projekcie).
- **⚠️ dług techniczny / code smells:**
  - 24 linie zakomentowanego martwego kodu (linie 110-133) — seria `console.print(...)` demonstrujących każdy styl z motywu + `input()` — pozostałość z developmentu/debugowania motywu, nigdy nieusunięta.
  - `MKVTOOLNIX_FOLDER`, `BALABOLKA_FOLDER`, `FFMPEG_FOLDER`, `ESPEAK_NG_FOLDER` budują ścieżkę przez `path.abspath(path.join(getcwd(), pardir))` + z powrotem `'mm_avh_working_space'` (linie 42-45, 52-55, 56-59, 65-68) — czterokrotnie powtórzony identyczny wzorzec zamiast jednej funkcji pomocniczej `_bin_path(*parts)`; ryzykowne założenie, że CWD zawsze jest wewnątrz katalogu `mm_avh_working_space` i że katalog nadrzędny + ta sama nazwa dają poprawną ścieżkę — działa tylko jeśli proces jest uruchamiany z konkretnego CWD.
  - `MKV_PROPEDIT_PATH` (linia 49) nie ma adnotacji typu `: str`, w przeciwieństwie do wszystkich sąsiednich stałych — drobna niespójność stylistyczna.
  - Konfiguracja `pydub.AudioSegment` jako efekt uboczny importu modułu stałych (linie 77-80) miesza odpowiedzialność "definicje ścieżek" z "konfiguracja zewnętrznej biblioteki" — moduł nazwany `constants.py` robi więcej niż nazwa sugeruje.
  - `environ['PATH'] = FFMPEG_FOLDER + ';' + environ.get('PATH', '')` (linia 73) na stałe modyfikuje zmienną środowiskową procesu globalnie przy każdym imporcie — trudne do przetestowania w izolacji (brak możliwości np. dwóch różnych konfiguracji ffmpeg w jednym procesie).
- **❌ niespójności ze stylem MangaShift:** Brak — plik jest z natury "rejestrem stałych" (najbliższy odpowiednik "jednego źródła prawdy" dla ścieżek), co samo w sobie jest zgodne z zasadą MangaShift. Największe odstępstwo to mieszanie efektu ubocznego (konfiguracja pydub, mutacja `os.environ`) z czystą definicją stałych — w architekturze warstwowej MangaShift efekty uboczne inicjalizacji należałyby raczej do jawnej funkcji `bootstrap()`/`configure()` wołanej explicite z punktu wejścia, nie do samego importu modułu stałych.
- **🔗 sprzężenia:** Cały projekt zależy od tego modułu (import `console`, `WORKING_SPACE*`, `SETTINGS_PATH` w `start.py`, `data/settings.py` i prawdopodobnie w `modules/*`, `utils/*` poza obszarem audytu). Zmiana struktury katalogów `bin/*` wymaga zmiany tylko tutaj — dobre scentralizowanie. Ryzykowne sprzężenie z układem katalogów na dysku (zakłada strukturę `<parent>/mm_avh_working_space/bin/...` niezależnie od faktycznej nazwy repozytorium/klonu — jeśli ktoś sklonuje repo pod inną nazwą folderu, `MKVTOOLNIX_FOLDER` i pozostałe będą wskazywać w złe miejsce, bo `'mm_avh_working_space'` jest zahardkodowane jako string, nie wyprowadzone z rzeczywistej nazwy CWD).

---

## 📄 plik: `data/config.py` (190 linii)

### przeznaczenie
Statyczny rejestr opcji konfiguracyjnych wyświetlanych w interaktywnym menu ustawień
(`data/settings.py`): lista tłumaczy, opcji liczby tłumaczonych linii, aktorów głosowych
TTS z ich parametrami domyślnymi, konfiguracji post-processingu FFmpeg oraz opcji
wyjściowych. Odpowiednik "katalogu" w architekturze MangaShift, ale bez typowanych
Literali obok — tylko dane, żadnej logiki wyboru.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `dataclass` | dataclasses | dekorator `@dataclass(slots=True)` na `Config` |
| `Any, List, Dict` | typing | adnotacje zwrotów metod statycznych |

### stałe / zmienne modułowe
Brak stałych modułowych — wszystkie dane są zwracane inline z metod statycznych (nie
wyodrębnione do stałych modułowych, mimo że są w pełni statyczne i niezależne od stanu).

### klasy

#### `class Config` (linia 19) — `@dataclass(slots=True)`, bez pól
**Cel:** Kontener na statyczne metody zwracające listy opcji konfiguracyjnych — pełni
rolę "rejestru danych" dla kreatora ustawień. Użycie `@dataclass(slots=True)` na klasie
bez żadnych pól instancyjnych jest nietypowe — klasa nigdy nie jest instancjowana
(wszystkie metody to `@staticmethod`), więc `slots=True` nie ma efektu (brak pól do
ograniczenia przez `__slots__`).
**Pola:** brak — klasa nie deklaruje żadnych pól dataclass.

**Metody:**

##### `get_translators() -> List[Dict[str, str]]` (linia 31, `@staticmethod`)
- **Co robi:** Zwraca statyczną listę dwóch dostępnych tłumaczy (Google Translate, DeepL API).
- **Przyjmuje:** nic.
- **Zwraca:** `List[Dict[str, str]]` — lista słowników `{'name': ...}`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** dane zahardkodowane inline w ciele metody zamiast jako stała modułowa `TRANSLATORS: List[...]` — utrudnia import samej listy bez wołania metody; brak typowanego `Literal['Google Translate', 'DeepL API']` obok (zasada MangaShift: "typowane Literały obok rejestrów").

##### `get_translation_options() -> List[Dict[str, str]]` (linia 48, `@staticmethod`)
- **Co robi:** Zwraca listę 10 opcji liczby tłumaczonych linii na raz: `'10'`...`'100'` co 10.
- **Przyjmuje:** nic.
- **Zwraca:** `List[Dict[str, str]]`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** wartości jako stringi liczb (`'10'`, nie `10`) — spójne z resztą projektu, gdzie `Settings.translated_line_count` też jest `Optional[str]`, ale semantycznie to liczba; brak walidacji zakresu gdzie indziej niż to menu (użytkownik nie może wpisać własnej wartości spoza listy, bo `_set_option` w `settings.py` waliduje tylko indeks/nazwę z tej listy).

##### `get_voice_actors() -> List[Dict[str, Any]]` (linia 72, `@staticmethod`)
- **Co robi:** Zwraca listę 6 silników TTS (Zosia-Harpo, Agnieszka-Ivona, Zofia-Edge, Marek-Edge, ElevenBytes v2, ElevenBytes v3) z opisem zakresu `speed`/`volume` po polsku i wartościami domyślnymi jako stringi.
- **Przyjmuje:** nic.
- **Zwraca:** `List[Dict[str, Any]]` — każdy wpis: `name`, `description` (dict speed/volume opisowy), `default_options` (dict z domyślnymi wartościami).
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** To jest **jedyny rejestr silników TTS w całym projekcie** — dokładnie ten typ danych, który w MangaShift żyłby w `services/tts/engines/__init__.py` jako `ENGINE_REGISTRY` + `Literal` obok. Tutaj: nazwa silnika to goły string powtórzony w wielu miejscach (`data/settings.py` porównuje `tts == 'TTS - Zosia - Harpo'` stringiem, `Config.get_voice_actors()` zwraca ten sam string) — brak jednego typowanego źródła nazw silników, więc literówka w jednym miejscu nie zostanie złapana statycznie. Walidacja zakresów `speed`/`volume` (np. "-10 do 10" dla Ivony) jest zakodowana **osobno** jako logika w `Settings._is_valid_speed`/`_is_valid_volume` (`data/settings.py:192-231`) — czysty przykład "if-ów per silnik" w miejscu, gdzie architektura MangaShift wymagałaby dispatch przez rejestr (np. każdy wpis silnika niósłby własną funkcję walidującą albo `(min, max)` jako dane, nie hardkodowane granice w kodzie warunkowym).

##### `get_post_processing() -> Dict[str, str]` (linia 158, `@staticmethod`)
- **Co robi:** Zwraca opisy i domyślne wartości dla post-processingu FFmpeg (tempo/głośność), niezależnego od silnika TTS.
- **Przyjmuje:** nic.
- **Zwraca:** `Dict[str, str]` z kluczami `description_speed`, `description_volume`, `default_pp_speed`, `default_pp_volume`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** jedyna metoda z pełnym docstringiem wyjaśniającym "dlaczego" (niezależność od modelu TTS) — reszta metod ma tylko opis "co". Struktura zwrotu (płaski dict z description_*/default_* zamiast zagnieżdżonego jak w `get_voice_actors`) jest niespójna z resztą klasy — inny kształt danych dla koncepcyjnie podobnej rzeczy (opis + wartość domyślna).

##### `get_output() -> List[Dict[str, str]]` (linia 176, `@staticmethod`)
- **Co robi:** Zwraca 3 opcje wyjściowe (odtwarzanie w MM_AVH_Players, scalanie do MKV, wypalanie do MP4).
- **Przyjmuje:** nic.
- **Zwraca:** `List[Dict[str, str]]`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** nazwy opcji to pełne zdania po polsku używane jednocześnie jako etykieta UI i jako wartość porównywana w logice (`modules.mkv_processing`, poza obszarem audytu) — miesza rolę "label" (frontowa, zmienna) z rolą "identyfikator" (powinien być stabilny klucz/enum), łamiąc zasadę MangaShift "label żyje TYLKO na froncie, identyfikator jest stabilny".

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** Jedno miejsce z pełną listą opcji konfiguracyjnych (translators, TTS, output) — nie są rozproszone po kodzie. Użycie `@dataclass(slots=True)` sugeruje świadomość wzorca MangaShift, choć zastosowane niepoprawnie (patrz niżej). Dobra dokumentacja modułu na górze pliku z przykładem użycia.
- **⚠️ dług techniczny / code smells:**
  - `@dataclass(slots=True)` na klasie bez pól i bez instancjonowania (linia 18-19) — dekorator bez efektu, myląca sygnalizacja intencji; klasa działa identycznie jak zwykła klasa z samymi `@staticmethod`.
  - Dane hardkodowane inline w ciałach metod zamiast jako stałe modułowe (`get_translators`, `get_translation_options`, `get_voice_actors`, `get_output`) — utrudnia import/reużycie samej listy bez wywołania metody, zwłaszcza że metody nie przyjmują żadnych argumentów (czysto statyczne dane).
  - Niespójny kształt zwrotu między `get_voice_actors` (zagnieżdżone `description`/`default_options`) i `get_post_processing` (płaski dict `description_speed`/`default_pp_speed`) dla koncepcyjnie tej samej idei "opis + wartość domyślna".
  - Nazwy silników TTS i opcji wyjścia to gołe stringi bez `Literal` obok — zero ochrony przed literówką na poziomie typów.
- **❌ niespójności ze stylem MangaShift:** Brak typowanych `Literal` obok rejestru (zasada MangaShift: "typowane Literały obok rejestrów"), np. `Literal['TTS - Zosia - Harpo', 'TTS - Agnieszka - Ivona', ...]` nigdzie nie istnieje — cała identyfikacja silnika opiera się na dopasowaniu gołych stringów w `data/settings.py`. Walidacja zakresów speed/volume per silnik żyje w `Settings` (`_is_valid_speed`/`_is_valid_volume`) jako seria `if tts == '...'`, zamiast być danymi przy silniku w tym rejestrze — to dokładnie "if-y per silnik", których MangaShift się pozbywa przez rejestr + dispatch. Etykieta (`name`) pełni podwójną rolę: UI label + identyfikator porównywany w logice — MangaShift rozdziela to jawnie (id stabilny vs `label` tylko frontowy).
- **🔗 sprzężenia:** Silne sprzężenie z `data/settings.py`, który woła każdą z metod `Config.get_*` i porównuje zwracane stringi `name` bezpośrednio w logice warunkowej. Dodanie nowego silnika TTS wymaga zmian w **dwóch** miejscach: tu (wpis w `get_voice_actors`) i w `data/settings.py` (`_is_valid_speed`, `_is_valid_volume`, ewentualnie `_get_elevenbytes_voice` jeśli specjalny przypadek) — czyli więcej niż "2 miejsca" z wzorca MangaShift, i to bez rejestru/Literala pilnującego spójności.

---

## 📄 plik: `data/settings.py` (684 linie)

### przeznaczenie
Definiuje dataclass `Settings` przechowujący całą konfigurację użytkownika (tłumacz,
klucz API DeepL, silnik TTS i jego parametry, ustawienia głosu ElevenLabs v3,
post-processing FFmpeg, opcję wyjścia, tryb automatyczny) oraz kompletny interaktywny
kreator ustawień (seria metod `_get_*`/`_is_valid_*`) budujący nową instancję `Settings`
przez serię promptów w konsoli, z zapisem/odczytem do/z `data/settings.json`. Wołany
z `start.py` przez `update_settings()`.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `asdict, dataclass` | dataclasses | serializacja `Settings`→dict do JSON; dekorator klasy |
| `decoder, dump, load` | json | odczyt/zapis pliku ustawień, łapanie `JSONDecodeError` |
| `Any, Dict, List, Optional, Tuple` | typing | adnotacje typów |
| `SETTINGS_PATH, console` | constants | domyślna ścieżka pliku + globalna konsola |
| `Config` | data.config | źródło list opcji do promptów |
| `TTS as ElevenBytesTTS` | modules.tts_elevenbytes (lazy, wewnątrz metody) | listowanie/dodawanie głosów ElevenLabs |

### stałe / zmienne modułowe
Brak stałych modułowych na poziomie pliku — wszystkie "stałe domyślne" (`_V3_DEFAULT_*`)
są atrybutami klasowymi `Settings` (patrz niżej), nie modułowymi.

### klasy

#### `class Settings` (linia 37) — `@dataclass(slots=True)`
**Cel:** Jedyny nośnik konfiguracji użytkownika w projekcie; zarówno model danych
(pola), jak i cała logika interaktywnego kreatora ustawień (metody `_get_*`) —
klasa łączy w sobie rolę "modelu" i "serwisu/kreatora", co jest mieszaniem
odpowiedzialności.

**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `translator` | `Optional[str]` | `None` | nazwa wybranego tłumacza (np. `'Google Translator'`) |
| `deepl_api_key` | `Optional[str]` | `None` | klucz API DeepL (jeśli wybrano DeepL) |
| `translated_line_count` | `Optional[str]` | `None` | liczba linii tłumaczonych na raz, jako string |
| `tts` | `Optional[str]` | `None` | nazwa wybranego silnika TTS |
| `tts_speed` | `Optional[str]` | `None` | prędkość głosu (format zależny od silnika) lub `'auto'` |
| `tts_volume` | `Optional[str]` | `None` | głośność głosu (format zależny od silnika) lub `'auto'` |
| `elevenbytes_voice` | `Optional[str]` | `None` | alias/voice_id wybranego głosu ElevenLabs |
| `elevenbytes_stability` | `Optional[str]` | `None` | parametr `stability` ElevenLabs v3 (string 0.0-1.0) |
| `elevenbytes_similarity_boost` | `Optional[str]` | `None` | parametr `similarity_boost` v3 |
| `elevenbytes_style` | `Optional[str]` | `None` | parametr `style` v3 |
| `elevenbytes_speaker_boost` | `Optional[str]` | `None` | `'true'`/`'false'` jako string, nie `bool` |
| `pp_speed` | `Optional[str]` | `None` | tempo post-processingu FFmpeg (`atempo`, 0.5-3.0) |
| `pp_volume` | `Optional[str]` | `None` | zmiana głośności w dB post-processingu |
| `output` | `Optional[str]` | `None` | wybrana opcja wyjścia (etykieta z `Config.get_output`) |
| `auto_mode` | `bool` | `False` | czy pipeline działa bez pytań |

**Metody:**

##### `load_from_file(cls, settings_path: str = SETTINGS_PATH) -> 'Settings'` (linia 86, `@classmethod`)
- **Co robi:** Wczytuje ustawienia z pliku JSON; przy braku pliku lub błędnym formacie zwraca zestaw domyślny (lokalna funkcja `get_default_settings`), inaczej mapuje pola z `dict` na `Settings`, dobierając wartość domyślną dla `pp_speed`/`pp_volume` z `Config.get_post_processing()` gdy klucz brakuje w pliku.
- **Przyjmuje:** `settings_path` — ścieżka do JSON (domyślnie `SETTINGS_PATH`).
- **Zwraca:** `Settings`.
- **Efekty uboczne:** odczyt pliku, `console.print` przy błędzie.
- **Woła:** wewnętrzną `get_default_settings()` (linia 101), `open`, `load`, `Config.get_post_processing()`.
- **Wyjątki:** łapie `FileNotFoundError` i `decoder.JSONDecodeError` — oba prowadzą do zwrócenia domyślnych ustawień zamiast rzucenia dalej (mimo że docstring metody (linie 96-98) deklaruje `Raises: FileNotFoundError, decoder.JSONDecodeError` — **dokumentacja niezgodna z rzeczywistym zachowaniem**, bo wyjątki są tu łapane, nie propagowane).
- **Uwagi:** bug w docstringu (Raises sekcja kłamie); zagnieżdżona funkcja `get_default_settings` (linia 101) nie ustawia pól `elevenbytes_*`, `auto_mode` — polegają na domyślnych z definicji dataclass (`None`/`False`), co jest OK, ale niejawne.

##### `_set_option(prompt: str, options: List[Dict[str, Any]]) -> Optional[str]` (linia 149, `@staticmethod`)
- **Co robi:** Generyczny prompt wyboru z listy — wypisuje numerowaną listę (z opcjonalnymi podopcjami lub opisem speed/volume), czyta input, obsługuje wybór przez numer (`'3'`), podpunkt (`'3.1'`) lub dokładną nazwę tekstową.
- **Przyjmuje:** `prompt` — nagłówek; `options` — lista słowników z `name` i opcjonalnie `suboptions`/`description`.
- **Zwraca:** `Optional[str]` — nazwa wybranej opcji, albo `None` przy niepoprawnym wyborze.
- **Efekty uboczne:** `console.print` (wielokrotnie), `input()`.
- **Woła:** `console.print`, `input`, `enumerate`.
- **Wyjątki:** `ValueError` możliwy z `map(int, choice.split('.'))` przy np. `'a.b'` — **nieobsłużony**, wywali cały prompt niekontrolowanym wyjątkiem zamiast łagodnego komunikatu "niepoprawny wybór".
- **Uwagi:** ta jedna metoda obsługuje jednocześnie dwa różne kształty danych opcji (`suboptions` dla struktur zagnieżdżonych, `description` dla TTS) — rozgałęzienie `if/elif` na kształt danych (linie 164-172) zamiast jednolitego interfejsu opcji; kruche parsowanie `choice.split('.')` bez walidacji liczby części (np. `'1.2.3'` też przejdzie przez `map(int, ...)` i rzuci `ValueError` przy rozpakowaniu do dwóch zmiennych).

##### `_is_valid_speed(speed: str, tts: Optional[str]) -> bool` (linia 192, `@staticmethod`)
- **Co robi:** Waliduje format prędkości głosu w zależności od nazwy silnika TTS (goły string porównywany `if tts == '...'`).
- **Przyjmuje:** `speed` — wartość do walidacji; `tts` — nazwa silnika.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `int(speed)`, string methods (`.startswith`, `.isdigit`, `.endswith`).
- **Wyjątki:** `int(speed)` może rzucić `ValueError` przy niepoprawnym stringu — **nieobsłużone wewnątrz tej metody** (łapane dopiero przez wołającego `_get_tts_speed`, patrz niżej — ale niespójnie, bo funkcja sama deklaruje się jako walidator zwracający `bool`, nie coś co rzuca).
- **Uwagi:** klasyczny przykład "if-ów per silnik" krytykowany w architekturze MangaShift — dodanie nowego silnika TTS wymaga dopisania kolejnego `if tts == 'Nowy Silnik'` tutaj. Reguły walidacji (zakresy) są zduplikowane koncepcyjnie z opisami tekstowymi w `Config.get_voice_actors` (np. "od -10 do 10" w opisie i `-10 <= int(speed) <= 10` tutaj) — dwa miejsca do synchronizacji ręcznie przy zmianie zakresu.

##### `_is_valid_volume(volume: str, tts: Optional[str]) -> bool` (linia 213, `@staticmethod`)
- **Co robi:** Analogicznie do `_is_valid_speed`, ale dla głośności (różne zakresy: 0-1 float dla Harpo, -100..100 int dla Ivony, procent ze znakiem dla Edge).
- **Przyjmuje:** `volume`, `tts`.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `float(volume)`, `int(volume)`, string methods.
- **Wyjątki:** `ValueError` możliwy z `float`/`int` — nieobsłużone tutaj.
- **Uwagi:** ten sam problem "if-ów per silnik" co `_is_valid_speed` — te dwie metody razem to blok kodu, który idealnie pasowałby jako dane (`(validator_fn, min, max)`) przy wpisie silnika w `Config.get_voice_actors`, zamiast osobnej logiki warunkowej tutaj.

##### `_get_translator(settings: Optional['Settings']) -> Optional[str]` (linia 234, `@staticmethod`)
- **Co robi:** Prosi o wybór tłumacza; przy niepoprawnym wyborze (`None` z `_set_option`) pada z powrotem na poprzednią wartość z `settings`.
- **Przyjmuje:** `settings` — poprzednie ustawienia (do fallbacku) lub `None`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print/input przez `_set_option`.
- **Woła:** `Settings._set_option`, `Config.get_translators`.
- **Wyjątki:** propaguje z `_set_option`.
- **Uwagi:** wzorzec "spróbuj ustawić, w razie błędu fallback na stare" powtórzony niemal identycznie w kilku metodach `_get_*` (`_get_translated_line_count`, `_get_tts`, `_get_output`) — kandydat do wspólnej funkcji generycznej `_prompt_with_fallback(prompt, options, current_value)`.

##### `_get_deepl_api_key(settings: Optional['Settings']) -> Optional[str]` (linia 252, `@staticmethod`)
- **Co robi:** Pyta czy ustawić klucz DeepL; jeśli tak, czyta klucz z inputu (pusty → fallback do poprzedniej wartości); jeśli nie, zachowuje poprzednią wartość.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print, input.
- **Woła:** `console.print`, `input`.
- **Wyjątki:** brak jawnej obsługi.
- **Uwagi:** to jedyna metoda pytająca T/N ręcznie inline (`input().lower() in ('t', 'y')`, linia 266) zamiast przez wspólny `ask_user` ze `start.py` — duplikacja logiki pytania tak/nie w dwóch miejscach projektu z lekko różną implementacją (tu brak obsługi `EOFError`/`KeyboardInterrupt`, w przeciwieństwie do `start.ask_user`).

##### `_get_translated_line_count(settings: Optional['Settings']) -> Optional[str]` (linia 281, `@staticmethod`)
- **Co robi:** Prosi o wybór liczby linii tłumaczonych na raz z listy `Config.get_translation_options()`.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print/input przez `_set_option`.
- **Woła:** `Settings._set_option`, `Config.get_translation_options`.
- **Wyjątki:** propaguje.
- **Uwagi:** komentarz w docstringu `(Optional[str] future maybe change)` (linia 289) — jawny TODO/niepewność pozostawiona w kodzie.

##### `_get_tts(settings: Optional['Settings']) -> Optional[str]` (linia 299, `@staticmethod`)
- **Co robi:** Prosi o wybór silnika TTS z listy `Config.get_voice_actors()`.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print/input przez `_set_option`.
- **Woła:** `Settings._set_option`, `Config.get_voice_actors`.
- **Wyjątki:** propaguje.
- **Uwagi:** brak.

##### `_get_default_speed_volume(tts: Optional[str]) -> Tuple[Optional[str], Optional[str]]` (linia 317, `@staticmethod`)
- **Co robi:** Wyszukuje wybrany silnik w `Config.get_voice_actors()` i zwraca jego domyślne `speed`/`volume`.
- **Przyjmuje:** `tts` — nazwa silnika.
- **Zwraca:** `Tuple[Optional[str], Optional[str]]` — `(default_speed, default_volume)`, `(None, None)` gdy nie znaleziono.
- **Efekty uboczne:** brak.
- **Woła:** `Config.get_voice_actors`, `next(...)`.
- **Wyjątki:** brak.
- **Uwagi:** liniowe przeszukiwanie listy przez `next(...)` przy każdym wywołaniu zamiast np. dict po nazwie — nieistotne wydajnościowo przy 6 elementach, ale sygnalizuje brak indeksowanego rejestru.

##### `_get_tts_speed(tts: Optional[str], default_speed: Optional[str]) -> Optional[str]` (linia 339, `@staticmethod`)
- **Co robi:** Pyta o prędkość głosu; jeśli wpisana wartość przechodzi `_is_valid_speed` i nie jest pusta, używa jej, inaczej fallback na `default_speed`.
- **Przyjmuje:** `tts`, `default_speed`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print, input.
- **Woła:** `console.print`, `input`, `Settings._is_valid_speed`.
- **Wyjątki:** łapie `ValueError` (linia 358) — ale `_is_valid_speed` sam może rzucić `ValueError` z `int(speed)` wewnątrz warunku `if`, co ten `try` łapie poprawnie (przypadkowo działający, ale nieoczywisty przepływ: walidator rzuca, wołający łapie).
- **Uwagi:** wzorzec "walidator rzucający wyjątek zamiast zwracać `False`" jest mylący, bo `_is_valid_speed` deklaruje zwrot `bool`, a w praktyce dla części silników (np. pusty string, litery) rzuci `ValueError` zanim zdąży zwrócić `bool`.

##### `_get_tts_volume(tts: Optional[str], default_volume: Optional[str]) -> Optional[str]` (linia 365, `@staticmethod`)
- **Co robi:** Analogicznie do `_get_tts_speed`, dla głośności.
- **Przyjmuje:** `tts`, `default_volume`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print, input.
- **Woła:** `console.print`, `input`, `Settings._is_valid_volume`.
- **Wyjątki:** łapie `ValueError`.
- **Uwagi:** duplikat struktury `_get_tts_speed` — dwie niemal identyczne metody różniące się tylko nazwą walidatora i tekstem promptu; kandydat do parametryzacji jedną funkcją `_get_tts_param(tts, default, validator, prompt_text)`.

##### `_get_elevenbytes_voice(settings: Optional['Settings']) -> Optional[str]` (linia 392, `@staticmethod`)
- **Co robi:** Lazy-importuje `modules.tts_elevenbytes.TTS`, listuje dostępne głosy, pozwala wybrać istniejący lub dodać nowy przez `voice_id` wpisany ręcznie (z zapisem przez `ElevenBytesTTS.add_voice`).
- **Przyjmuje:** `settings` — do fallbacku przy błędzie/anulowaniu.
- **Zwraca:** `Optional[str]` — alias wybranego głosu.
- **Efekty uboczne:** import modułu na żądanie; `console.print`, `input`; **zapis nowego głosu do trwałego magazynu** przez `ElevenBytesTTS.add_voice` (efekt uboczny poza plikiem settings.py, w module TTS).
- **Woła:** `TTS.list_voices()`, `TTS.add_voice(alias, voice_name, voice_id)`, `console.print`, `input`.
- **Wyjątki:** łapie `Exception` szeroko przy imporcie (linia 396) i drukuje komunikat błędu, zwracając fallback — **gołe `except Exception`** bez rozróżnienia typu błędu (ImportError vs inne).
- **Uwagi:** jedyna metoda w klasie robiąca lazy import wewnątrz funkcji (uzasadnione — unika zależności cyklicznej/kosztownej przy starcie), ale to też oznacza, że `Settings` zna szczegóły `modules.tts_elevenbytes` (przełamanie warstwy: model konfiguracji wie o konkretnym silniku TTS) — bezpośrednie naruszenie zasady MangaShift "serwis nieświadomy konkretnych silników"; tu nawet **model danych** (nie serwis) zna konkretny silnik.

##### `_prompt_float_0_1(description: str, verb: str, current: str, default: str) -> str` (linia 443, `@staticmethod`)
- **Co robi:** Generyczny prompt dla wartości zmiennoprzecinkowej 0.0-1.0 (ElevenLabs v3), z zachowaniem obecnej wartości przy pustym Enter.
- **Przyjmuje:** `description` — pełna etykieta PL; `verb` — krótki rzeczownik do linii "Wpisz ...:"; `current` — obecna wartość; `default` — wartość fabryczna.
- **Zwraca:** `str` — wybrana, obecna lub domyślna wartość.
- **Efekty uboczne:** print, input.
- **Woła:** `console.print`, `input`, `float(choice)`.
- **Wyjątki:** łapie `ValueError` z `float(choice)` (linia 462) i pada na `default`.
- **Uwagi:** dobrze napisana generyczna funkcja pomocnicza — rzadki przykład reużywalnej abstrakcji w tym pliku (użyta 3x w `_get_elevenbytes_v3_settings`).

**Atrybuty klasowe (stałe fabryczne, nie pola dataclass):**
| nazwa | linia | wartość | cel |
|-------|-------|---------|-----|
| `_V3_DEFAULT_STABILITY` | 468 | `'0.5'` | domyślna stabilność głosu ElevenLabs v3 |
| `_V3_DEFAULT_SIMILARITY` | 469 | `'0.75'` | domyślne podobieństwo do głosu v3 |
| `_V3_DEFAULT_STYLE` | 470 | `'0.0'` | domyślna ekspresja stylu v3 |
| `_V3_DEFAULT_BOOST` | 471 | `'true'` | domyślne wzmocnienie mówcy v3 |

Uwaga: te 4 stałe są zdefiniowane **wewnątrz ciała klasy dataclass, między metodami**
(po `_prompt_float_0_1`, przed `_get_elevenbytes_v3_settings`) — nietypowe umiejscowienie
(zwykle stałe klasowe idą na górze klasy, zaraz po polach); ponieważ klasa ma
`slots=True`, te przypisania stają się zwykłymi atrybutami klasy (class variables),
nie polami dataclass (nie mają adnotacji typu, więc `@dataclass` je ignoruje jako pola) —
działa poprawnie, ale umiejscowienie w środku listy metod utrudnia odnalezienie.

##### `_get_elevenbytes_v3_settings(settings: Optional['Settings']) -> tuple[str, str, str, str]` (linia 474, `@staticmethod`)
- **Co robi:** Odczytuje obecne wartości (lub fabryczne domyślne) dla 4 parametrów głosu ElevenLabs v3, prosi o każdy po kolei (3 przez `_prompt_float_0_1`, jeden T/N ręcznie), zwraca krotkę 4 stringów.
- **Przyjmuje:** `settings` — poprzednie ustawienia.
- **Zwraca:** `tuple[str, str, str, str]` — `(stability, similarity_boost, style, speaker_boost)`.
- **Efekty uboczne:** print, input.
- **Woła:** `Settings._prompt_float_0_1` ×3, `console.print`, `input`.
- **Wyjątki:** brak jawnej obsługi (deleguje do `_prompt_float_0_1`).
- **Uwagi:** adnotacja zwrotu `tuple[str, str, str, str]` (PEP 585, lowercase) vs reszta pliku używająca `Tuple[...]` z `typing` (np. `_get_default_speed_volume` linia 317) — niespójność stylu adnotacji w obrębie tej samej klasy. Logika T/N dla `speaker_boost` (linie 498-504) duplikuje wzorzec parsowania T/N zamiast reużyć wspólnej funkcji (trzeci wariant parsowania tak/nie w projekcie, obok `ask_user` w `start.py` i inline w `_get_deepl_api_key`).

##### `_get_auto_mode(settings: Optional['Settings']) -> bool` (linia 509, `@staticmethod`)
- **Co robi:** Pyta o włączenie trybu automatycznego (T/N/Enter=bez zmiany), pokazując obecną wartość.
- **Przyjmuje:** `settings`.
- **Zwraca:** `bool`.
- **Efekty uboczne:** print, input.
- **Woła:** `console.print`, `input`.
- **Wyjątki:** brak.
- **Uwagi:** czwarty wariant parsowania T/N w projekcie (`choice in ('t', 'y')` / `choice in ('n',)` / fallback current) — ten akceptuje też pusty input jako "bez zmiany" (poprawne zachowanie, ale znowu zduplikowana logika zamiast wspólnej funkcji `_prompt_yes_no_keep(current)`.

##### `_is_valid_pp_speed(speed: str) -> bool` (linia 526, `@staticmethod`)
- **Co robi:** Waliduje, czy wartość tempa post-processingu mieści się w 0.5-3.0.
- **Przyjmuje:** `speed`.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `float(speed)`.
- **Wyjątki:** łapie `ValueError` wewnętrznie i zwraca `False` — **w przeciwieństwie do `_is_valid_speed`/`_is_valid_volume`, które NIE łapią `ValueError`** — niespójność wzorca walidacji między starszymi metodami (TTS) a nowszymi (post-processing) w tym samym pliku.
- **Uwagi:** dobra, samodzielna, bezpieczna implementacja — wzorcowa w porównaniu do `_is_valid_speed`.

##### `_is_valid_pp_volume(volume: str) -> bool` (linia 535, `@staticmethod`)
- **Co robi:** Waliduje, czy wartość głośności post-processingu jest liczbą (dB, bez ograniczenia zakresu).
- **Przyjmuje:** `volume`.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `float(volume)`.
- **Wyjątki:** łapie `ValueError` wewnętrznie.
- **Uwagi:** brak górnego/dolnego ograniczenia (dowolna liczba przechodzi) — celowe (dB nie ma naturalnego zakresu), ale niezaznaczone komentarzem.

##### `_get_pp_speed(settings: Optional['Settings']) -> Optional[str]` (linia 544, `@staticmethod`)
- **Co robi:** Pyta o tempo post-processingu (atempo), pokazując obecną i domyślną wartość; puste wejście zachowuje obecną, niepoprawne pada na domyślną.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print, input.
- **Woła:** `Config.get_post_processing`, `console.print`, `input`, `Settings._is_valid_pp_speed`.
- **Wyjątki:** brak (walidator już bezpieczny).
- **Uwagi:** brak.

##### `_get_pp_volume(settings: Optional['Settings']) -> Optional[str]` (linia 562, `@staticmethod`)
- **Co robi:** Analogicznie do `_get_pp_speed`, dla głośności w dB.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print, input.
- **Woła:** `Config.get_post_processing`, `console.print`, `input`, `Settings._is_valid_pp_volume`.
- **Wyjątki:** brak.
- **Uwagi:** `_get_pp_speed`/`_get_pp_volume` to niemal identyczna struktura co `_get_translator`/`_get_output` itd. — ten sam wzorzec "prompt z fallbackiem" reimplementowany po raz kolejny zamiast jednej generycznej funkcji parametryzowanej walidatorem i tekstami.

##### `_get_output(settings: Optional['Settings']) -> Optional[str]` (linia 579, `@staticmethod`)
- **Co robi:** Prosi o wybór opcji wyjścia z `Config.get_output()`.
- **Przyjmuje:** `settings`.
- **Zwraca:** `Optional[str]`.
- **Efekty uboczne:** print/input przez `_set_option`.
- **Woła:** `Settings._set_option`, `Config.get_output`.
- **Wyjątki:** propaguje.
- **Uwagi:** brak.

##### `get_user_settings(settings_path: str = SETTINGS_PATH) -> Optional['Settings']` (linia 597, `@staticmethod`)
- **Co robi:** Orkiestruje cały kreator ustawień: wczytuje poprzednie ustawienia, po kolei woła każdą metodę `_get_*` w ustalonej kolejności (tłumacz → klucz DeepL → liczba linii → TTS → prędkość/głośność [pomijane dla silników z `'auto'`] → ustawienia ElevenBytes/v3 jeśli dotyczy → post-processing → output → auto_mode), zwraca nową, kompletną instancję `Settings`.
- **Przyjmuje:** `settings_path`.
- **Zwraca:** `Optional[str]` w sygnaturze... a właściwie `Optional['Settings']` — zawsze zwraca konkretny obiekt `Settings` (nigdy faktycznie `None` w obecnej implementacji), adnotacja `Optional` jest zbędna/myląca.
- **Efekty uboczne:** cała sekwencja printów/inputów pozostałych metod; brak zapisu do pliku (to robi dopiero `change_settings_save_to_file`).
- **Woła:** `Settings.load_from_file`, `_get_translator`, `_get_deepl_api_key`, `_get_translated_line_count`, `_get_tts`, `_get_default_speed_volume`, `console.print`, `_get_tts_speed`/`_get_tts_volume` (warunkowo, pomijane gdy `default_speed == 'auto'`), `_get_elevenbytes_voice` (warunkowo), `_get_elevenbytes_v3_settings` (warunkowo, tylko v3), `_get_pp_speed`, `_get_pp_volume`, `_get_output`, `_get_auto_mode`.
- **Wyjątki:** propaguje ze wszystkich wywoływanych metod.
- **Uwagi:** rozróżnienie silnika ElevenBytes odbywa się przez porównanie stringów `tts in ('TTS - ElevenBytes (ElevenLabs v2)', 'TTS - ElevenBytes (ElevenLabs v3)')` (linie 621-624) i osobno `tts == 'TTS - ElevenBytes (ElevenLabs v3)'` (linia 625) — twarde stringi silników rozsiane w logice metody zamiast stałych/Literali; to metoda **najbardziej dotknięta** brakiem rejestru silników — cała gałąź logiki `is_elevenbytes`/`is_elevenbytes_v3` byłaby zbędna, gdyby `Config.get_voice_actors()` niósł flagę `supports_voice_settings_v3: bool` przy wpisie silnika.

##### `change_settings_save_to_file(settings_path: str = SETTINGS_PATH) -> None` (linia 670, `@staticmethod`)
- **Co robi:** Woła `get_user_settings`, asserts że wynik nie jest `None`, zapisuje jako JSON (indent=4) do pliku.
- **Przyjmuje:** `settings_path`.
- **Zwraca:** `None`.
- **Efekty uboczne:** **zapisuje/nadpisuje plik na dysku** (`data/settings.json` domyślnie).
- **Woła:** `Settings.get_user_settings`, `asdict`, `open`, `dump`.
- **Wyjątki:** `assert settings is not None` (linia 681) — `AssertionError` w trybie zoptymalizowanym (`python -O`) zostanie **wyciszony** (asserty są usuwane przy `-O`), co w teorii mogłoby prowadzić do `NoneType has no attribute` gdzie indziej, choć w praktyce `get_user_settings` obecnie zawsze zwraca obiekt; `open`/`dump` mogą rzucić `OSError`/`TypeError` nieobsłużone.
- **Uwagi:** użycie `assert` do kontroli przepływu na granicy publicznego zapisu do pliku jest krucha praktyka — powinno być jawne `if settings is None: raise RuntimeError(...)`.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** `Settings` jako `@dataclass(slots=True)` z jasno wypisanymi polami jest poprawnym, nowoczesnym wzorcem (zgodnym z MangaShift). Kreator ustawień konsekwentnie stosuje wzorzec "Enter = zachowaj obecną wartość, niepoprawna wartość = domyślna" w nowszych metodach (`_prompt_float_0_1`, `_get_pp_speed`, `_get_pp_volume`, `_get_auto_mode`) — dobre UX. `load_from_file` odpornie obsługuje brak pliku i zepsuty JSON. Rozszerzalność JSON (brakujące klucze dostają wartości domyślne przy odczycie) chroni przed złamaniem kompatybilności starych plików ustawień.
- **⚠️ dług techniczny / code smells:**
  - Czterokrotna (co najmniej) duplikacja logiki parsowania odpowiedzi tak/nie: `start.ask_user` (poza tym plikiem), `_get_deepl_api_key:266`, `_get_elevenbytes_v3_settings:498-504` (speaker_boost), `_get_auto_mode:519-522` — cztery różne miejsca z lekko odmienną implementacją tego samego pytania T/N.
  - Duplikacja struktury `_get_tts_speed`/`_get_tts_volume` (linie 339-389) — niemal identyczny kod różniący się tylko nazwą walidatora i tekstem.
  - Niespójna obsługa `ValueError` w walidatorach: `_is_valid_speed`/`_is_valid_volume` **nie łapią** `ValueError` (muszą być łapane przez wołającego), podczas gdy `_is_valid_pp_speed`/`_is_valid_pp_volume` **łapią** je wewnętrznie i zwracają `bool` bezpiecznie — dwa różne kontrakty API dla funkcji o tej samej nazwie-wzorcu `_is_valid_*`.
  - Mieszanie stylu adnotacji generyków: `Tuple[Optional[str], Optional[str]]` (linia 317, `typing.Tuple`) vs `tuple[str, str, str, str]` (linia 476, wbudowany `tuple`) w tej samej klasie.
  - Bug w docstringu `load_from_file` (linie 96-98): deklaruje `Raises: FileNotFoundError, decoder.JSONDecodeError`, ale metoda oba te wyjątki **łapie** i zwraca domyślne ustawienia zamiast je propagować.
  - `assert settings is not None` (linia 681) jako kontrola przepływu w metodzie zapisującej plik na dysk — krucha praktyka, znika przy `python -O`.
  - Gołe `except Exception` w `_get_elevenbytes_voice:396` przy imporcie modułu TTS — połyka wszystkie błędy (w tym literówki w kodzie modułu `tts_elevenbytes`) pod jednym komunikatem.
  - Stałe `_V3_DEFAULT_*` (linie 468-471) umieszczone w środku ciała klasy między metodami zamiast na górze przy polach — utrudnia odnalezienie.
  - `_set_option:149-189` obsługuje dwa niezwiązane kształty opcji (`suboptions` vs `description`) w jednej funkcji przez `if/elif` na obecność klucza — brak jednolitego kontraktu "opcji".
- **❌ niespójności ze stylem MangaShift:** Najbardziej złamany plik w tym obszarze pod względem "serwis nieświadomy silników". `_is_valid_speed`/`_is_valid_volume` (linie 192-231) to podręcznikowy przykład if-ów per silnik zamiast danych w rejestrze. `_get_elevenbytes_voice` (linia 392) — **model konfiguracji** (`Settings`, teoretycznie warstwa danych) bezpośrednio importuje i woła konkretny moduł silnika TTS (`modules.tts_elevenbytes`), czyli sprzężenie modelu z konkretną implementacją silnika — w MangaShift taka wiedza żyłaby wyłącznie w serwisie/rejestrze TTS, nigdy w klasie ustawień. `get_user_settings` (linie 620-644) rozgałęzia się na podstawie gołych stringów nazw silników (`is_elevenbytes`, `is_elevenbytes_v3`) zamiast pytać rejestr o zdolności silnika (np. `engine.supports_voice_settings_v3`). Brak jednego źródła prawdy: nazwa silnika `'TTS - Zosia - Harpo'` itd. jest zapisana jako string identyczny w trzech miejscach (`data/config.py` w `get_voice_actors`, i tutaj wielokrotnie w porównaniach) bez wspólnego `Literal`/enuma, który złapałby rozjazd statycznie.
- **🔗 sprzężenia:** Silne sprzężenie z `data/config.py` (każda metoda `_get_*` woła odpowiedni `Config.get_*`). Sprzężenie z `constants.SETTINGS_PATH`/`console`. Nietypowe, warstwo-łamiące sprzężenie z `modules.tts_elevenbytes` (lazy import wewnątrz metody modelu danych) — zmiana API `TTS.list_voices()`/`TTS.add_voice()` w module TTS złamie `Settings` bez żadnego ostrzeżenia na poziomie typów (import jest lazy, więc błąd ujawni się dopiero w runtime przy wyborze tego silnika). Każda zmiana nazwy silnika TTS w `Config.get_voice_actors()` (np. literówka albo rebranding etykiety) cicho rozjeżdża się z porównaniami stringów w `Settings`, bez żadnego mechanizmu wykrywającego to statycznie (brak testu synchronizacji, brak `Literal`).

---

## 🧭 podsumowanie obszaru

**Główne odpowiedzialności:** Ten obszar dostarcza (1) punkt wejścia i sekwencyjny
"pipeline" bez struktury kroków (`start.py`), (2) scentralizowane stałe ścieżek i
globalną konsolę z motywem kolorów (`constants.py`), (3) statyczny, niehermetyzowany
rejestr opcji konfiguracyjnych (`data/config.py`), oraz (4) model+kreator ustawień
użytkownika z persystencją JSON (`data/settings.py`). Razem stanowią warstwę
"wejście + konfiguracja", którą reszta projektu (moduły `modules/*`) konsumuje.

**Największe problemy (ranking):**
1. **Brak rejestru silników TTS z danymi walidacji.** `_is_valid_speed`/`_is_valid_volume` w `data/settings.py:192-231` to seria `if tts == '...'` — dodanie/usunięcie/zmiana nazwy silnika TTS wymaga edycji minimum 3 plików bez żadnej ochrony statycznej (`data/config.py` dane, `data/settings.py` walidacja, `data/settings.py` gałęzie ElevenBytes) — najbardziej kosztowny i najbardziej ryzykowny (ciche literówki) dług w całym obszarze.
2. **`Settings` (model danych) importuje konkretny silnik TTS** (`modules.tts_elevenbytes`, linia 395) — złamanie warstwy modelu; najpoważniejsze pojedyncze naruszenie zasady "serwis/model nieświadomy silników" z architektury MangaShift.
3. **`start.py::main()` to płaska sekwencja wywołań, nie rejestr kroków** — brak możliwości włączenia/wyłączenia/reorderowania kroku pipeline'u bez edycji kodu; brak izolacji błędów na poziomie kroku (`process_output_files` nie łapie wyjątków per-plik, w przeciwieństwie do ekstrakcji).
4. **Duplikacja wzorców** — dwie implementacje "ekstrahuj równolegle" w `start.py`, cztery implementacje "zapytaj T/N", dwie identyczne struktury `_get_tts_speed`/`_get_tts_volume` i `_get_pp_speed`/`_get_pp_volume` w `data/settings.py`.
5. **Niespójności typowania i dokumentacji** — mieszanie `typing.Tuple`/wbudowany `tuple`, brakujące `-> None`, `dict` bez generyków obok `Dict[str, bool]`, błędny docstring `Raises` w `load_from_file`.
6. **Magic values bez konfigurowalności** — `crf_value='18'`/`preset_value='medium'` w `start.py:511-512` zahardkodowane mimo rozbudowanej konfigurowalności reszty pipeline'u.
7. **Kruchość ścieżek w `constants.py`** — zahardkodowana nazwa folderu `'mm_avh_working_space'` w budowie ścieżek `bin/*` zamiast wyprowadzenia jej z rzeczywistego CWD.

**Kandydaci do refaktoru na styl MangaShift:**
- `data/config.py::get_voice_actors()` → przekształcić w prawdziwy rejestr silników TTS (`ENGINE_REGISTRY: Dict[VoiceEngineId, VoiceEngineSpec]`) z `Literal VoiceEngineId` obok, gdzie `VoiceEngineSpec` niesie nie tylko opis/domyślne, ale też funkcję/zakres walidacji i flagę `supports_v3_voice_settings` — eliminuje if-y w `data/settings.py::_is_valid_speed/_is_valid_volume` i gałęzie `is_elevenbytes*` w `get_user_settings`.
- `start.py::main()` → zamienić na listę kroków (nawet prosta lista `tuple[str, Callable]` byłaby postępem) zamiast wklepanej sekwencji, żeby błąd w jednym kroku nie wymagał grzebania w ciele `main`.
- Cztery warianty "zapytaj T/N" → jedna funkcja `ask_yes_no(prompt, default=None)` reużywana wszędzie (w tym w `data/settings.py`, które dziś ma własną, słabszą kopię w `_get_deepl_api_key`).
- `_get_tts_speed`/`_get_tts_volume` oraz `_get_pp_speed`/`_get_pp_volume` → sparametryzować jedną funkcją generyczną.
- `_set_option` → rozdzielić na dwie funkcje (prosty wybór z listy vs wybór z podopcjami) zamiast jednej z rozgałęzieniem na kształt danych.

**Pliki/funkcje martwe lub podejrzane:**
- `constants.py:110-133` — 24 linie w pełni zakomentowanego kodu demonstracyjnego (`console.print` dla każdego stylu + `input()`) — martwy kod do usunięcia.
- Znaczniki `# ✅` przy definicjach funkcji w `start.py` (linie 36, 48, 76, 96, 232, 390, 420, 481, 544) — niejasne pochodzenie, prawdopodobnie pozostałość checklisty code-review, nieużywane przez żadne narzędzie w repo (brak linter/CI reguły która by je czytała, brak wzmianek w innych plikach obszaru).
- `Config` w `data/config.py` — `@dataclass(slots=True)` bez pól i bez instancjonowania; dekorator efektywnie martwy (nie robi nic, co zwykła klasa by nie robiła).
- `get_user_settings` (linia 597) zadeklarowane jako `-> Optional['Settings']`, ale w praktyce nigdy nie zwraca `None` w obecnej implementacji — `Optional` w sygnaturze jest myląca/nieaktualna.

---


# CZĘŚĆ 02 — modules: ekstrakcja i merge

# RAPORT AUDYTU — modules: ekstrakcja i merge MKV

---

## 📦 obszar: ekstrakcja i merge MKV — pliki: `modules/mkvtoolnix.py`, `modules/mkv_processing.py`, `modules/track_selector.py`

**Rola obszaru w projekcie:** Ten zestaw plików obsługuje dwa końce potoku (ekstrakcja → napisy → TTS → merge): na wejściu `mkvtoolnix.py` + `track_selector.py` odpytują plik MKV o metadane ścieżek i wyciągają audio/napisy do plików tymczasowych (ręcznie lub automatycznie, Filar 2 pipeline'u auto-dub); na wyjściu `mkv_processing.py` scala wygenerowany lektor (.eac3) i napisy (.srt/.ass) z powrotem do kontenera MKV albo wypala je do MP4 przez FFmpeg. `track_selector.py` jest czystym modułem decyzyjnym (bez I/O) używanym przez `mkvtoolnix.py` w trybie auto.

**Zależności zewnętrzne obszaru:** `rich.console.Console` (kolorowy log), `subprocess.Popen/call` (uruchamianie `mkvextract.exe`, `mkvmerge.exe`, `mkvinfo.exe`, `ffmpeg.exe`), `json.loads` (parsowanie JSON z mkvmerge `--identify`), `re` (regex postępu i sanityzacji nazw plików), `shlex.quote` (escapowanie ścieżki napisów dla filtra FFmpeg). Wewnętrznie: `constants` (ścieżki binarek i working space, globalny `console`), `data.settings.Settings` (obiekt ustawień usera — pole `output` steruje trybem `MKVProcessing.process_mkv`), `modules.track_selector` (import w `mkvtoolnix.py` do trybu auto). Wywoływane z `start.py` (funkcje `_extract_one` w dwóch wariantach — manualnym i auto z live progress-barem — oraz `process_output_files`).

---

## 📄 plik: `modules/mkvtoolnix.py` (496 linii)

### przeznaczenie
Owija narzędzia z pakietu MKVToolNix (`mkvmerge --identify`, `mkvextract tracks`) w jedną klasę `MkvToolNix`. Odpowiada za: (1) odpytanie metadanych ścieżek MKV i wypisanie ich w konsoli, (2) ekstrakcję wybranych ścieżek audio/napisów do plików tymczasowych — ręcznie (prompt na `input()`) albo automatycznie (delegacja do `track_selector`), z opcjonalnym live progresem. Wołany z `start.py` w pętli po plikach `.mkv` w `WORKING_SPACE`, raz per plik, w osobnym wątku (ThreadPoolExecutor).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | `_PROGRESS_RE` — regex `Postęp: N%` / `Progress: N%` z stdout mkvextract |
| `sys` | stdlib | `sys.exit()` przy braku binarki lub błędzie subprocessu |
| `Popen, PIPE, CalledProcessError` | subprocess | uruchamianie mkvmerge/mkvextract, przechwyt stdout/stderr |
| `loads` | json | parsowanie JSON z `mkvmerge --identify` |
| `Any, Callable, Dict, List, Optional, Set` | typing | adnotacje typów |
| `path, stat` | os | budowa ścieżek, sprawdzanie rozmiaru pliku (cache guard) |
| `dataclass, field` | dataclasses | definicja `MkvToolNix` jako `@dataclass(slots=True)` |
| `Console` | rich.console | typ pola `console`, kolorowy log |
| `WORKING_SPACE, WORKING_SPACE_OUTPUT, WORKING_SPACE_TEMP, MKV_EXTRACT_PATH, MKV_MERGE_PATH, MKV_INFO_PATH, MKV_PROPEDIT_PATH, console` | constants | domyślne wartości pól dataclass + globalny logger |
| `select_audio_track, select_subtitle_track` | modules.track_selector | dobór ścieżek w trybie auto |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `MIN_EXTRACTED_BYTES` | 41 | `int` | `1024` — próg poniżej którego wyekstrahowany plik jest uznany za obcięty/śmieciowy i wymuszana jest ponowna ekstrakcja (cache guard w `mkv_extract_track`) |
| `_PROGRESS_RE` | 43 | `re.Pattern` | `r'(?:Postęp|Progress):\s*(\d+)%'` — parsuje procent postępu ze stdout mkvextract (PL/EN warianty komunikatu) |

### klasy

#### `class MkvToolNix` (linia 47) — `@dataclass(slots=True)`
**Cel:** Reprezentuje jedną operację na jednym pliku MKV — trzyma ścieżki robocze i do binarek, stan `subtitle_already_target_lang` wykryty podczas auto-selekcji, oraz udostępnia metody odpytania i ekstrakcji.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `filename` | `str` | — (wymagane) | nazwa pliku MKV do przetworzenia (bez ścieżki katalogu) |
| `working_space` | `str` | `WORKING_SPACE` | katalog, w którym leży plik wejściowy |
| `working_space_output` | `str` | `WORKING_SPACE_OUTPUT` | katalog wyjściowy (niewykorzystywany bezpośrednio w tym pliku poza polem) |
| `working_space_temp` | `str` | `WORKING_SPACE_TEMP` | katalog docelowy dla wyekstrahowanych ścieżek |
| `mkv_extract_path` | `str` | `MKV_EXTRACT_PATH` | ścieżka do `mkvextract.exe` |
| `mkv_merge_path` | `str` | `MKV_MERGE_PATH` | ścieżka do `mkvmerge.exe` (używana też do identyfikacji, nie tylko merge) |
| `mkv_info_path` | `str` | `MKV_INFO_PATH` | ścieżka do `mkvinfo.exe` (tylko sprawdzana w `_check_executables`, nigdy realnie wywoływana — `get_mkv_info` używa `mkv_merge_path --identify`) |
| `mkv_propedit_path` | `str` | `MKV_PROPEDIT_PATH` | ścieżka do `mkvpropedit.exe` — pole zdefiniowane, ale **nigdzie w klasie nieużywane** |
| `subtitle_already_target_lang` | `bool` | `False` | flaga ustawiana w `_auto_select_tracks`; sygnalizuje wywołującemu (`start.py`), że wybrane napisy są już PL i tłumaczenie można pominąć |
| `console` | `Console` | `field(default=console)` | logger; nadpisywalny per-instancja (np. bufor `StringIO` w trybie auto z live progresem w `start.py:168-171`) — jedyna forma DI w tym module |

**Metody:**

##### `_check_executables(self) -> None` (linia 77)
- **Co robi:** Sprawdza istnienie trzech plików wykonywalnych (`mkv_extract_path`, `mkv_merge_path`, `mkv_info_path`) na dysku.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** przy braku pliku — drukuje błąd i **`sys.exit()`** (twarde zakończenie całego procesu, nie tylko tej operacji).
- **Woła:** `os.path.exists`.
- **Wyjątki:** nie rzuca; ubija proces przez `sys.exit()`.
- **Uwagi:** `mkv_propedit_path` nie jest w tej liście mimo że istnieje jako pole — niespójność, martwe pole niżej.

##### `get_mkv_info(self) -> dict` (linia 90)
- **Co robi:** Uruchamia `mkvmerge --identify --identification-format json` na pliku, parsuje JSON, wypisuje tabelę ścieżek do konsoli i zwraca surowy dict.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `dict` — pełny JSON z mkvmerge (klucze `container`, `tracks`, `chapters`, `attachments`...); pusty `{}` gdy `returncode != 0`.
- **Efekty uboczne:** subprocess (`Popen`), print do konsoli; przy `FileNotFoundError`/`CalledProcessError` — `sys.exit()`.
- **Woła:** `self._check_executables()`, `self._get_mkv_info_command()`, `self._parse_tracks_data()`, `self._print_mkv_info()`.
- **Wyjątki:** łapie `FileNotFoundError`, `CalledProcessError` → exit; przy `returncode != 0` bez wyjątku loguje błąd stderr i **zwraca `{}`** (niespójne z gałęzią wyjątku, która robi `sys.exit()` — dwa różne zachowania błędu w jednej metodzie).
- **Uwagi:** brak walidacji, że `data['tracks']` w ogóle istnieje przed wywołaniem `_parse_tracks_data` — możliwy `KeyError` nieobsłużony.

##### `_get_mkv_info_command(self) -> List[str]` (linia 117)
- **Co robi:** Buduje listę argumentów CLI dla `mkvmerge --identify`.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `List[str]` — `[mkv_merge_path, '--ui-language', 'en', '--identify', '--identification-format', 'json', path.join(working_space, filename)]`.
- **Efekty uboczne:** brak.
- **Woła:** `os.path.join`.
- **Wyjątki:** brak.
- **Uwagi:** `--ui-language en` na stałe — wymuszony angielski output narzędzia niezależnie od locale usera (celowe, bo JSON i tak jest parsowany programowo).

##### `_parse_tracks_data(self, data: dict) -> List[dict]` (linia 134)
- **Co robi:** Iteruje `data['tracks']`, mapuje każdy przez `_parse_track_data`, sortuje po `id`.
- **Przyjmuje:** `data` — surowy JSON z mkvmerge.
- **Zwraca:** posortowaną listę uproszczonych dictów track.
- **Efekty uboczne:** brak.
- **Woła:** `self._parse_track_data()`.
- **Wyjątki:** `KeyError` jeśli brak `'tracks'` w `data` (nieobsłużony).

##### `_parse_track_data(self, track: dict) -> dict` (linia 152)
- **Co robi:** Spłaszcza jeden track z surowego JSON mkvmerge do uproszczonego dicta: `id`, `type`, `codec_id`, `language`, `language_ietf`, `properties` (string, nie dict).
- **Przyjmuje:** `track` — jeden element `data['tracks']`.
- **Zwraca:** `dict` z sześcioma kluczami.
- **Efekty uboczne:** brak.
- **Woła:** `self._get_track_properties()`.
- **Wyjątki:** `KeyError` jeśli brak `track['properties']`.
- **Uwagi:** to jest ten "spłaszczony" kształt, który `track_selector.py` musi rozpoznawać obok surowego kształtu mkvmerge (patrz `track_selector.py:16-19` — trzy warianty kształtu tracka obsługiwane naraz przez helpery `_track_name`/`_track_language`/itd.).

##### `_get_track_properties(properties: dict) -> str` (linia 175, `@staticmethod`)
- **Co robi:** Zwraca jedną "właściwość" ścieżki do wyświetlenia: wymiary obrazu dla wideo, częstotliwość próbkowania dla audio, albo `'None'`.
- **Przyjmuje:** `properties` — dict `properties` pojedynczej ścieżki.
- **Zwraca:** `str`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** czysto kosmetyczna funkcja (tylko do wypisania w tabeli), nazwa `'None'` (string) jest myląca względem Pythonowego `None`.

##### `_print_mkv_info(self, tracks_data: List[dict]) -> None` (linia 192)
- **Co robi:** Drukuje nagłówek i tabelę ścieżek (ID/TYPE/CODEK/LANG/LANG_IETF/PROPERTIES) do konsoli z formatowaniem `rich`.
- **Przyjmuje:** `tracks_data` — wynik `_parse_tracks_data`.
- **Zwraca:** `None`.
- **Efekty uboczne:** wypisuje do `self.console`.
- **Woła:** `self.console.print()` wielokrotnie.
- **Wyjątki:** brak.
- **Uwagi:** formatowanie przez f-stringi z szerokościami pól na sztywno (`:2`, `:10`, `:20` itd.) — łamie się przy długich nazwach kodeków/języków (bez przycinania).

##### `mkv_extract_track(self, data: Dict[str, Any], auto_mode: bool = False, progress_callback: Optional[Callable[[int], None]] = None) -> None` (linia 217)
- **Co robi:** Główna metoda ekstrakcji. Wybiera zbiór track ID (manualnie przez prompt albo automatycznie przez `track_selector`), dla każdego: liczy nazwę wyjściową na bazie rozszerzenia kodeka, pomija ekstrakcję jeśli plik cache już istnieje i ma sensowny rozmiar, inaczej uruchamia `mkvextract` — z live progresem (callback) albo buforowanym stdout (tryb manualny/domyślny).
- **Przyjmuje:** `data` — JSON z `get_mkv_info()`; `auto_mode` — czy pomijać prompt; `progress_callback` — opcjonalny callback `int -> None` wywoływany z aktualnym procentem.
- **Zwraca:** `None`.
- **Efekty uboczne:** subprocess (`Popen`), zapis plików na dysk (przez mkvextract), print do konsoli, rekurencyjne wywołanie samej siebie przy błędnym ID w trybie manualnym.
- **Woła:** `self._auto_select_tracks()` / `self._prompt_tracks_to_extract()`, `self._get_format_extension()`, `self._get_extract_command()`, `self._extract_with_progress()` (gałąź progress), `self.mkv_extract_track(data)` (rekurencja przy błędzie, tylko manual).
- **Wyjątki:** łapie `(IndexError, KeyError)` przy nieprawidłowym ID ścieżki → log + rekurencja (tylko gdy `not auto_mode`); w auto_mode błąd jest po prostu połknięty bez re-prompt (komentarz w kodzie tłumaczy dlaczego — deterministyczny wybór zapętliłby się w nieskończoność).
- **Uwagi:** **duplikacja logiki** — ta metoda ma własną pętlę parsowania linii `output.replace('\r','\n').splitlines()` (linie 275-285) niemal identyczną koncepcyjnie do `_extract_with_progress`, tylko bez callbacku. Rekurencja bez limitu głębokości przy powtarzających się błędnych ID w trybie manualnym (teoretyczne ryzyko stack overflow przy bardzo upartym userze, w praktyce nieistotne bo user wpisuje ręcznie). `codec_id` odczytywany bez `.get()` (linia 247, `track['properties']['codec_id']`) podczas gdy `_parse_track_data` używa `.get('codec_id', '')` — niespójne podejście do brakujących kluczy w obrębie tego samego pliku.

##### `_extract_with_progress(self, command: List[str], progress_callback: Callable[[int], None]) -> None` (linia 299)
- **Co robi:** Uruchamia `mkvextract`, czyta stdout znak-po-znaku (żeby złapać `\r`-owe nadpisania linii postępu), parsuje `_PROGRESS_RE` i wywołuje callback na każdą zmianę procentu; na końcu wymusza `progress_callback(100)`.
- **Przyjmuje:** `command` — gotowa komenda CLI; `progress_callback` — callback procentu.
- **Zwraca:** `None`.
- **Efekty uboczne:** subprocess, wielokrotne wywołania `progress_callback` (side effect na obiekcie z `start.py`, np. `rich.progress.Progress.update`).
- **Woła:** `Popen`, `process.stdout.read(1)` w pętli, `_PROGRESS_RE.search`.
- **Wyjątki:** `assert process.stdout is not None` — może rzucić `AssertionError` (nietypowe dla logiki biznesowej, ale tu celowe dla mypy/type narrowing).
- **Uwagi:** czytanie po jednym znaku (`read(1)`) jest wydajnościowo podejrzane (syscall per znak) — dla krótkich linii statusu to akceptowalne, ale to rozwiązanie "działa, nie jest eleganckie".

##### `_prompt_tracks_to_extract(self, data: Dict[str, Any]) -> Set[int]` (linia 333)
- **Co robi:** Pętla `while True` pytająca usera o ID ścieżek do wyciągnięcia, aż wciśnie Enter na pustym wejściu; waliduje zakres i typ.
- **Przyjmuje:** `data` — JSON z `get_mkv_info()` (używane tylko do policzenia `len(data['tracks'])`).
- **Zwraca:** `Set[int]` wybranych ID.
- **Efekty uboczne:** blokujący `input()`, print do konsoli.
- **Woła:** `input()`.
- **Wyjątki:** łapie `ValueError` (np. `int('abc')`) → log i kontynuacja pętli (bez `break`, więc user musi spróbować ponownie).
- **Uwagi:** nieskończona pętla bez wyjścia awaryjnego poza pustym Enterem — zgodne z resztą CLI-owego stylu projektu.

##### `_auto_select_tracks(self, data: Dict[str, Any]) -> Set[int]` (linia 366)
- **Co robi:** Deleguje wybór ścieżki audio i napisów do `modules.track_selector` (`select_audio_track`, `select_subtitle_track`), loguje decyzję, i ustawia `self.subtitle_already_target_lang` na podstawie języka wybranych napisów (`pol`/`pl`).
- **Przyjmuje:** `data` — JSON z `get_mkv_info()`.
- **Zwraca:** `Set[int]` — zbiór 0, 1 lub 2 track ID.
- **Efekty uboczne:** mutuje `self.subtitle_already_target_lang`; print do konsoli.
- **Woła:** `select_audio_track(tracks)`, `select_subtitle_track(tracks)`, `self._track_language()`.
- **Wyjątki:** brak jawnej obsługi — jeśli `data['tracks']` brakuje, `KeyError` propaguje się do `mkv_extract_track`, gdzie akurat `KeyError` jest łapany (przypadkowo poprawne zachowanie, nie zaprojektowane).
- **Uwagi:** logika biznesowa (progi językowe "już PL") owinięta bezpośrednio w tej metodzie zamiast być częścią `track_selector` — rozjazd odpowiedzialności: `track_selector.py` deklaruje się jako "no I/O, pure scoring", ale test "czy język to PL" (semantycznie blisko `_SUB_LANG_WEIGHT`) leży tutaj, zduplikowany koncepcyjnie.

##### `_track_language(tracks: List[dict], track_id: int | None) -> str` (linia 402, `@staticmethod`)
- **Co robi:** Wyszukuje ścieżkę o danym `id` w liście i zwraca jej język (najpierw płaski klucz `language`, potem `properties.language`), albo `'—'`.
- **Przyjmuje:** `tracks` — surowe tracki z mkvmerge; `track_id` — szukane ID lub `None`.
- **Zwraca:** `str`.
- **Efekty uboczne:** brak.
- **Woła:** nic zewnętrznego.
- **Wyjątki:** brak (używa `.get()` wszędzie).
- **Uwagi:** duplikuje logikę `track_selector._track_language` (tam też jest fallback `language`/`properties.language`, plus dodatkowo `lang` i `.lower()`) — dwie osobne implementacje tej samej idei w dwóch plikach tego samego obszaru.

##### `_get_format_extension(codec_id: str) -> str` (linia 423, `@staticmethod`)
- **Co robi:** Mapuje `codec_id` mkvmerge (np. `A_AC3`, `S_TEXT/ASS`) na rozszerzenie pliku (np. `ac3`, `ass`) przez słownik `format_dict` zdefiniowany lokalnie w ciele metody (34 wpisy).
- **Przyjmuje:** `codec_id` — string identyfikatora kodeka.
- **Zwraca:** `str` — rozszerzenie, domyślnie `'mkv'` gdy nierozpoznany.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** `format_dict` budowany od nowa przy każdym wywołaniu metody (nie jest stałą modułową/klasową) — drobny narzut wydajnościowy, ale głównie code smell: 34-elementowy słownik powinien być stałą na poziomie modułu (jak `_PROGRESS_RE`), nie lokalną zmienną w metodzie.

##### `_get_extract_command(self, track_id: int, out_file: str) -> List[str]` (linia 479)
- **Co robi:** Buduje komendę CLI dla `mkvextract tracks <plik> <id>:<out_file>`.
- **Przyjmuje:** `track_id` — ID ścieżki; `out_file` — docelowa ścieżka pliku.
- **Zwraca:** `List[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `os.path.join`.
- **Wyjątki:** brak.
- **Uwagi:** brak.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** cache guard (linie 254-261) unika kosztownej re-ekstrakcji; `_extract_with_progress` daje realny live-progress przez znak-po-znak parsing `\r`; separacja trybu manual/auto jest czytelna na poziomie publicznego API (`auto_mode` + `progress_callback`); dataclass ze `slots=True` (linia 46) — zgodne ze stylem MangaShift.
- **⚠️ dług techniczny / code smells:**
  - Duplikacja logiki progresu: parsing linii w `mkv_extract_track` (`mkvtoolnix.py:275-285`) obok pełnoprawnej `_extract_with_progress` (`mkvtoolnix.py:299-331`) — dwie ścieżki robiące podobne rzeczy różnymi metodami.
  - Duplikacja `_track_language` między `mkvtoolnix.py:402-421` i `track_selector.py:103-122` — dwa źródła prawdy dla tej samej reguły (fallback `language`→`properties.language`).
  - `format_dict` budowany za każdym razem od nowa wewnątrz `_get_format_extension` (`mkvtoolnix.py:434-475`) zamiast być stałą modułową.
  - Niespójna obsługa braku klucza: `track['properties']['codec_id']` (linia 247, rzuci `KeyError`) vs `properties.get('codec_id', '')` (linia 167) w tym samym pliku.
  - Niespójna obsługa błędu w `get_mkv_info`: gałąź `returncode != 0` loguje i zwraca `{}` (linia 111-115), a gałąź wyjątku robi `sys.exit()` (linia 112-114) — dwa różne poziomy fatalności dla koncepcyjnie podobnego "coś poszło nie tak".
  - `sys.exit()` wewnątrz metody instancyjnej (`_check_executables:88`, `get_mkv_info:114`) — biblioteka/moduł ubija cały proces Pythona zamiast rzucać wyjątek domenowy; utrudnia testowanie i reużycie w innym kontekście (np. batch bez przerywania całego runu).
  - `mkv_propedit_path` (pole, linia 73) zdefiniowane, ale nigdzie w klasie nieużywane — martwy kod / niespełniona obietnica funkcjonalności (mkvpropedit nigdy nie jest wołany).
  - `mkv_info_path` (pole, linia 72) sprawdzany w `_check_executables`, ale faktyczna komenda identyfikacji używa `mkv_merge_path --identify` (linia 125) — `mkvinfo.exe` nigdy realnie nie jest uruchamiany, tylko sprawdzana jego obecność.
  - Rekurencja bez limitu w `mkv_extract_track` (linia 293) przy powtarzających się błędach w trybie manualnym.
  - `_extract_with_progress` czyta stdout znak-po-znaku (`read(1)`, linia 318-327) — nietypowe, kosztowne rozwiązanie zamiast buforowanego readline.
- **❌ niespójności ze stylem MangaShift:** brak warstwy serwis/rejestr — `MkvToolNix` miesza w jednej klasie: budowanie komend CLI, parsowanie JSON, prompt usera, logikę wyboru plików wyjściowych i obsługę procesu; zero rozbicia na "silnik ekstrakcji" (execution) vs "serwis" (orkiestracja) vs "rejestr formatów" (mapa kodek→rozszerzenie jest zahardkodowana lokalnie zamiast być osobnym, typowanym rejestrem `Literal`/dict na poziomie modułu, obok którego mogłaby żyć walidacja). `sys.exit()` w środku logiki domenowej łamie zasadę "serwis nieświadomy efektów ubocznych wywołania" z architektury MangaShift — tam warstwy niższe zwracają błędy/rzucają wyjątki, a decyzję "przerwać proces" podejmuje najwyższa warstwa (CLI/API), nie biblioteka. Brak dependency injection dla `track_selector` (import na sztywno na górze pliku, `mkvtoolnix.py:37`) — działa, bo `track_selector` jest czysto funkcyjny i bezstanowy, ale nie ma abstrakcji pozwalającej podmienić strategię wyboru ścieżek bez edycji tego pliku.
- **🔗 sprzężenia:** silne sprzężenie z `constants.py` (6 stałych ścieżek importowanych na sztywno jako defaulty pól) — zmiana układu katalogów w `constants.py` wymaga zgodności nazw pól tutaj. Sprzężenie z `modules/track_selector.py` przez bezpośredni import funkcji (nie przez rejestr/interfejs) — podmiana strategii wyboru ścieżek wymaga edycji tego pliku. Konsument `start.py` polega na mutowalnym polu `subtitle_already_target_lang` odczytywanym *po* wywołaniu `mkv_extract_track` — niejawny kontrakt (kolejność wywołań ma znaczenie, nic tego nie wymusza typowo).

---

## 📄 plik: `modules/mkv_processing.py` (248 linii)

### przeznaczenie
Odpowiada za etap wyjściowy potoku: scalenie oryginalnego MKV z wygenerowanym plikiem lektora (`.eac3`) i/lub napisami (`.srt`/`.ass`) z powrotem w jeden plik — albo jako nowy kontener MKV (`mkvmerge`), albo jako wypalone MP4 (FFmpeg, hardsub + transkodowanie). Trzecia opcja to zwykłe przeniesienie plików bez łączenia. Wołany z `start.py:process_output_files` — raz per "bazowa nazwa pliku" znaleziona w katalogu output.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | sanityzacja nazwy pliku w `mkv_burn_to_mp4` (usuwanie znaków niebędących alfanumerykiem/kropką) |
| `suppress` | contextlib | `with suppress(Exception): call(command)` — połyka **każdy** wyjątek z wywołania FFmpeg |
| `dataclass` | dataclasses | definicja `MKVProcessing` jako `@dataclass(slots=True)` |
| `listdir, path, remove, rename` | os | operacje na plikach/katalogach |
| `quote` | shlex | escapowanie ścieżki pliku napisów w filtrze `-vf subtitles=...` |
| `move` | shutil | przenoszenie plików między working_space a working_space_output |
| `Popen, call` | subprocess | uruchamianie `mkvmerge` (Popen) i `ffmpeg` (call) |
| `List, Dict, Callable, Optional` | typing | adnotacje typów |
| `WORKING_SPACE, WORKING_SPACE_OUTPUT, MKV_MERGE_PATH, FFMPEG_PATH, console` | constants | domyślne ścieżki + globalny logger (używany bezpośrednio, nie przez `self.console` — różnica względem `mkvtoolnix.py`) |
| `Settings` | data.settings | pole `settings.output`决yduje którą metodę przetwarzania odpalić |

### stałe / zmienne modułowe
Brak stałych modułowych w tym pliku (wszystkie wartości domyślne są polami dataclass).

### klasy

#### `class MKVProcessing` (linia 32) — `@dataclass(slots=True)`
**Cel:** Reprezentuje operację post-processingu jednego "bazowego" pliku (nazwa bez rozszerzenia) — łączy MKV z lektorem/napisami albo wypala do MP4, zależnie od wyboru w `Settings.output`.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `filename` | `str` | — (wymagane) | bazowa nazwa pliku (bez rozszerzenia) do przetworzenia |
| `working_space` | `str` | `WORKING_SPACE` | katalog źródłowy z oryginalnym `.mkv` |
| `working_space_output` | `str` | `WORKING_SPACE_OUTPUT` | katalog z wygenerowanymi napisami/lektorem i miejsce zapisu wyniku |
| `mkv_merge_path` | `str` | `MKV_MERGE_PATH` | ścieżka do `mkvmerge.exe` |
| `ffmpeg_path` | `str` | `FFMPEG_PATH` | ścieżka do `ffmpeg.exe` |
| `crf_value` | `str` | `'18'` | wartość CRF (jakość) dla FFmpeg x264 |
| `preset_value` | `str` | `'ultrafast'` | preset szybkości enkodowania FFmpeg (nadpisywany przez wołającego na `'medium'` w `start.py:512`) |

**Metody:**

##### `process_mkv(self, settings: Settings) -> None` (linia 67)
- **Co robi:** Mapuje wartość `settings.output` (string wybrany przez usera w menu ustawień) na jedną z trzech metod przetwarzania przez lokalny słownik `options`, i ją wywołuje.
- **Przyjmuje:** `settings` — obiekt `Settings` z polem `output` (jeden z trzech dokładnych stringów: `'Oglądam w MM_AVH_Players (wynik: napisy i audio)'`, `'Scal do mkv'`, `'Wypal do mp4'`).
- **Zwraca:** `None`.
- **Efekty uboczne:** print do `console` (globalny, nie `self.console`); wywołuje wybraną metodę.
- **Woła:** jedną z: `self.move_files_to_working_space`, `self.mkv_merge`, `self.mkv_burn_to_mp4`.
- **Wyjątki:** brak jawnej obsługi — jeśli `settings.output` nie pasuje do żadnego klucza, `process_method` jest `None` i **nic się nie dzieje po cichu** (brak logu o nieznanej opcji).
- **Uwagi:** dispatch przez string-matching na dokładny tekst menu (`'Oglądam w MM_AVH_Players (wynik: napisy i audio)'`) — kruche powiązanie z `data/config.py` (opcje menu) i `data/settings.py`; literówka lub zmiana tekstu w jednym miejscu cicho wyłącza tę gałąź bez błędu.

##### `move_files_to_working_space(self) -> None` (linia 90)
- **Co robi:** Dla plików w `working_space_output`, których nazwa zaczyna się od `self.filename`, przenosi je do `working_space` (nadpisując istniejące).
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** usuwa pliki w `working_space` (jeśli już istnieją) i przenosi pliki z output do working_space.
- **Woła:** `os.listdir`, `os.path.exists`, `os.remove`, `shutil.move`.
- **Wyjątki:** brak jawnej obsługi (np. `PermissionError` przy zajętym pliku propaguje się w górę).
- **Uwagi:** `filename.startswith(self.filename)` — potencjalny false-positive gdy jeden plik bazowy jest prefiksem innego (np. `odc1` i `odc10`) — dopasuje pliki obu, jeśli nazwy bazowe kolidują prefiksowo.

##### `mkv_merge(self) -> None` (linia 103)
- **Co robi:** Buduje i uruchamia komendę `mkvmerge` łączącą oryginalny `.mkv` z opcjonalnym `.eac3` (lektor) i opcjonalnym `.srt`/`.ass` (napisy), z ustawionymi nazwami ścieżek i flagami języka/domyślności; usuwa pliki źródłowe po scaleniu.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** subprocess (`Popen`, blokujące `communicate()`), zapis pliku wynikowego w `working_space_output`, usunięcie plików tymczasowych napisów/lektora.
- **Woła:** `os.path.join`, `os.path.exists`, `Popen(...).communicate()`, `self._remove_files()`.
- **Wyjątki:** brak jawnej obsługi subprocessu (błąd mkvmerge nie jest sprawdzany — `process.returncode` ignorowany).
- **Uwagi:** jeśli wejściowy `.mkv` nie istnieje — early return z logiem (linia 110-113), ale **brak sprawdzenia returncode** po `Popen` — plik wyjściowy może nie powstać, a `_remove_files` i tak posprząta źródła, tracąc dane bez ostrzeżenia. Priorytet `.srt` nad `.ass` w warunku `if/elif` (linia 129-134) — celowy, ale niedokumentowany wprost jako reguła.

##### `mkv_burn_to_mp4(self) -> None` (linia 141)
- **Co robi:** Tymczasowo zmienia nazwę pliku wejściowego na "bezpieczną" (tylko alfanumeryki i kropki, przez regex), buduje komendę FFmpeg (wybraną w `_prepare_command`), uruchamia ją, przenosi wynik do finalnej nazwy, przywraca oryginalną nazwę pliku wejściowego, i czyści pliki tymczasowe.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** dwukrotny `rename()` pliku źródłowego (tam i z powrotem), subprocess FFmpeg, `remove()`/`rename()` na plikach wynikowych, usunięcie plików tymczasowych.
- **Woła:** `os.path.exists`, `re.sub`, `os.rename`, `os.path.join`, `self._prepare_command()`, `subprocess.call()` (w `suppress(Exception)`), `self._remove_files()`.
- **Wyjątki:** `call(command)` owinięty w `with suppress(Exception)` (linia 170-171) — **każdy błąd FFmpeg jest całkowicie połknięty**, w tym błędne argumenty, brak pliku wejściowego czy crash procesu; funkcja idzie dalej tak jakby się udało.
- **Uwagi:** **Bug/ryzyko realne**: jeśli `rename` na linii 154-155 powiedzie się, ale FFmpeg zawiedzie (połknięte przez `suppress`), a proces/skrypt przerwie się przed linią 180-181 (np. Ctrl+C, wyjątek poza blokiem suppress, awaria zasilania) — oryginalny plik `.mkv` zostaje trwale pod zsanityzowaną nazwą, desynchronizując stan working_space. Podwójny rename to nietrwała operacja bez transakcyjności/finally. Regex sanityzacji (linia 152) `r'[^A-Za-z0-9.]+'` usuwa też polskie znaki diakrytyczne z nazw plików — celowe (FFmpeg + shlex na Windows), ale nieudokumentowane w docstringu.

##### `_remove_files(self, files: List[str]) -> None` (linia 185)
- **Co robi:** Usuwa każdy plik z listy, jeśli istnieje.
- **Przyjmuje:** `files` — lista ścieżek.
- **Zwraca:** `None`.
- **Efekty uboczne:** usuwa pliki z dysku.
- **Woła:** `os.path.exists`, `os.remove`.
- **Wyjątki:** brak obsługi (np. plik zablokowany przez inny proces propaguje wyjątek).
- **Uwagi:** brak.

##### `_prepare_command(self, new_filename: str, output_file: str, lector_file: str, subtitle_file_srt: str, subtitle_file_ass: str) -> List[str]` (linia 198)
- **Co robi:** Buduje komendę FFmpeg zależnie od tego, które kombinacje plików (napisy SRT/ASS, lektor) istnieją — 4 gałęzie: napisy+lektor (transkoduj wideo x264 + wypal napisy + zmapuj audio lektora), tylko lektor (kopiuj wideo, zmapuj audio), tylko napisy (transkoduj + wypal, kopiuj audio), żadne z nich (pusta komenda + tylko output).
- **Przyjmuje:** pięć ścieżek plików (string).
- **Zwraca:** `List[str]` — komenda FFmpeg gotowa do `subprocess.call`.
- **Efekty uboczne:** brak (czysta budowa listy, mimo że wykonuje `path.exists` — I/O odczytu).
- **Woła:** `os.path.exists`, `shlex.quote`, `str.replace`.
- **Wyjątki:** brak jawnej.
- **Uwagi:** **magic slicing `[2:]`** powtórzone 5 razy (linie 217, 222, 226, 230, 239, 243, 246) — `.replace("\\", "/")[2:]` obcina pierwsze dwa znaki ścieżki (typowo `C:` z dysku Windows) żeby zrobić ścieżkę względną/uniksową dla filtra FFmpeg; działa tylko gdy working_space jest na dysku z jednoliterową literą dysku — **kruche, niezadokumentowane założenie**, złamie się np. dla ścieżek UNC (`\\server\share`) albo gdyby ścieżka nie zaczynała się od `X:`. Duplikacja bloku `if srt: ... elif ass: ...` (subtitle path + `-vf subtitles=`) powtórzona identycznie w dwóch gałęziach (linie 220-227 i 237-244) — kandydat do wydzielenia pomocniczej funkcji.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** trzy tryby wyjścia jasno rozdzielone na trzy metody publiczne; `_prepare_command` centralizuje całą logikę budowy komendy FFmpeg w jednym miejscu (łatwo przetestować w izolacji, mimo że dziś nie jest testowana); dataclass ze `slots=True`.
- **⚠️ dług techniczny / code smells:**
  - `with suppress(Exception): call(command)` (`mkv_processing.py:170-171`) — połyka WSZYSTKIE wyjątki z FFmpeg, w tym crash, brak pliku, złe argumenty; brak logu błędu, brak sprawdzenia exit code.
  - Brak sprawdzenia `returncode` po `Popen(...).communicate()` w `mkv_merge` (linia 136-137) — cichy błąd mkvmerge nie jest wykrywany, a pliki źródłowe (lektor/napisy) są mimo to usuwane (linia 139) — potencjalna utrata danych wejściowych bez wyprodukowania wyjścia.
  - Podwójny `rename()` bez bloku `try/finally` w `mkv_burn_to_mp4` (linie 154-155, 180-181) — okno na desynchronizację nazwy pliku przy przerwaniu w trakcie.
  - Magic slicing `[2:]` na ścieżkach (`mkv_processing.py:217,222,226,230,239,243,246`) — zależność od Windows-owej litery dysku, bez komentarza wyjaśniającego, bez stałej/helpera.
  - Dispatch po dokładnym tekście stringa menu w `process_mkv` (linia 76-80) zamiast po enumie/Literalu — kruche, ciche milczenie przy niedopasowaniu.
  - Duplikacja bloku wyboru napisów SRT/ASS w `_prepare_command` (linie 220-227 vs 237-244).
  - `console` używany bezpośrednio jako globalny singleton (import z `constants`, nie `self.console`) — niespójne z `mkvtoolnix.py`, gdzie `console` jest polem instancji nadpisywalnym (tam DI częściowo istnieje, tutaj nie istnieje wcale) — utrudnia np. przechwycenie logu do bufora per-wątek tak jak robi to `start.py` dla `MkvToolNix`.
- **❌ niespójności ze stylem MangaShift:** brak DI dla loggera (na sztywno zaimportowany globalny `console`, w przeciwieństwie do `mkvtoolnix.py`) — dwa pliki tego samego obszaru robią to inaczej, co samo w sobie jest niespójnością wewnątrz-obszarową, nie tylko względem MangaShift. Brak jednego źródła prawdy dla "trybu wyjścia" — string z menu (`data/config.py`) jest jednocześnie kluczem dispatcha w `process_mkv` zamiast być osobnym, typowanym `Literal`/enumem obok rejestru trzech metod (analogicznie do wzorca "rejestr silników" z MangaShift: `{OutputMode.MERGE: self.mkv_merge, ...}`). Logika budowy komendy FFmpeg (`_prepare_command`) miesza w sobie I/O (`path.exists`) z czystą konstrukcją listy argumentów — w architekturze MangaShift byłby to podział na "sprawdzenie dostępnych wejść" (warstwa wyżej) i "budowa komendy z gotowego zestawu flag" (czysta funkcja, łatwo testowalna).
- **🔗 sprzężenia:** silne sprzężenie z dokładnym tekstem opcji menu w `data/settings.py`/`data/config.py` (string matching w `process_mkv`); zależność od Windows (litera dysku w `_prepare_command`) czyni ten kod nieprzenośnym na inne systemy plików bez zmian; zależność od konwencji nazewnictwa plików (`filename + '.mkv'`, `filename + '.eac3'`, `filename + '.srt'/'.ass'`) ustalanej gdzie indziej w potoku (TTS/napisy) — zmiana konwencji nazw w innym module cicho zepsuje to łączenie.

---

## 📄 plik: `modules/track_selector.py` (248 linii)

### przeznaczenie
Czysty, bezstanowy moduł scoringowy (brak I/O, brak klas) do automatycznego wyboru "właściwej" ścieżki audio i ścieżki napisów z metadanych MKV, bez pytania usera. Napędza Filar 2 potoku auto-dub: audio ma być oryginalnym językiem (pod lektorem), napisy mają być źródłem do tłumaczenia na polski. Wołany wyłącznie z `mkvtoolnix.py::_auto_select_tracks` (linie 382-383). Ma dedykowany test jednostkowy (`tests/track_selector_test.py`, 222 linie, 9 funkcji testowych, w tym `test_regression_vs_validated_picks` — regresja względem ręcznie zwalidowanego zbioru 206 plików MKV, zgodnie z docstringiem modułu, linia 7).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `from __future__ import annotations` | — | lazy evaluation adnotacji typów (pozwala na `dict[str, int]` i `int \| None` bez `from typing import ...` na Pythonie <3.10 w adnotacjach, choć plik i tak zakłada 3.10+ przez `int \| None`) |
| `re` | stdlib | `_RE_SIGNS` — regex wykrywający "signs/song/forced" w nazwie ścieżki |
| `Final` | typing | oznaczenie stałych modułowych jako niemutowalnych (deklaratywnie, nie egzekwowane w runtime) |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `_SUB_LANG_WEIGHT` | 33 | `Final[dict[str, int]]` | `{"pol":100, "pl":100, "eng":50, "en":50}` — waga języka napisów: PL najwyżej, potem EN |
| `_SUB_LANG_DEFAULT` | 41 | `Final[int]` | `10` — waga dla języka spoza `_SUB_LANG_WEIGHT` |
| `_AUDIO_LANG_WEIGHT` | 44 | `Final[dict[str, int]]` | `{"jpn":100,"ja":100,"eng":40,"en":40,"chi":30,"zho":30,"chs":30,"cht":30}` — waga języka audio: JP > EN > CH |
| `_AUDIO_LANG_DEFAULT` | 56 | `Final[int]` | `20` — waga dla języka audio spoza listy |
| `_SIGNS_PENALTY` | 60 | `Final[int]` | `-200` — kara za napisy "signs-only"; wystarczająco duża by zdyskwalifikować nawet PL (100-200=-100) wobec dowolnej pełnej ścieżki w innym języku |
| `_DEFAULT_BONUS` | 68 | `Final[int]` | `10` — bonus dla ścieżki audio oznaczonej jako domyślna w kontenerze |
| `_LINES_DIVISOR` | 71 | `Final[float]` | `1000.0` — dzielnik do przeskalowania liczby linii na mały tie-breaker (poniżej progu językowego) |
| `_RE_SIGNS` | 78 | `Final[re.Pattern[str]]` | `re.compile(r"sign\|song\|forced", re.I)` — dopasowywany tylko do nazwy ścieżki, nie do flagi `forced` (bo flaga bywa zawodna — udokumentowane w komentarzu 76-78) |

### funkcje modułowe (poza klasami)

##### `_track_name(track: dict) -> str` (linia 81)
- **Co robi:** Zwraca nazwę wyświetlaną ścieżki, próbując po kolei trzy możliwe kształty danych: `track_name` (płaski, mkvmerge znormalizowany), `name` (kształt datasetu testowego), `properties.track_name` (surowy JSON mkvmerge).
- **Przyjmuje:** `track` — dowolny dict reprezentujący ścieżkę.
- **Zwraca:** `str`, pusty string gdy nic nie znaleziono.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak (same `.get()`).
- **Uwagi:** obsługa trzech kształtów naraz to świadomy kompromis (opisany w docstringu modułu, linia 16-19) między kształtem danych testowych a produkcyjnym JSON-em z mkvmerge.

##### `_track_language(track: dict) -> str` (linia 103)
- **Co robi:** Zwraca kod języka ścieżki (lowercased), próbując `language`, `lang`, `properties.language`.
- **Przyjmuje:** `track` — dict ścieżki.
- **Zwraca:** `str`, pusty gdy brak.
- **Efekty uboczne:** brak.
- **Woła:** `str.lower()`.
- **Wyjątki:** brak.
- **Uwagi:** analogiczna do `MkvToolNix._track_language` (`mkvtoolnix.py:402-421`), ale nie identyczna (ta wersja dodatkowo sprawdza `lang` i zawsze `.lower()`uje) — duplikat koncepcyjny, patrz uwaga w sekcji `mkvtoolnix.py`.

##### `_track_default(track: dict) -> bool` (linia 125)
- **Co robi:** Sprawdza czy ścieżka jest oznaczona jako domyślna kontenera, próbując `default_track`, `default`, `properties.default_track`.
- **Przyjmuje:** `track` — dict ścieżki.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `bool()`.
- **Wyjątki:** brak.
- **Uwagi:** brak.

##### `_is_signs_only(track: dict) -> bool` (linia 144)
- **Co robi:** Sprawdza czy nazwa ścieżki wskazuje na "tylko napisy do znaków/piosenek" (nie pełny dialog).
- **Przyjmuje:** `track` — dict ścieżki napisów.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `_track_name()`, `_RE_SIGNS.search()`.
- **Wyjątki:** brak.
- **Uwagi:** działa tylko na nazwie ścieżki, celowo ignoruje flagę `forced` — udokumentowane, świadoma decyzja projektowa.

##### `_lines_bonus(track: dict) -> float` (linia 149)
- **Co robi:** Liczy tie-breaker na bazie liczby linii/wpisów indeksu, próbując `num_lines`, `lines`, `properties.num_index_entries`.
- **Przyjmuje:** `track` — dict ścieżki, opcjonalnie z licznikiem linii.
- **Zwraca:** `float` — `lines / 1000.0`, albo `0.0` gdy nieznane.
- **Efekty uboczne:** brak.
- **Woła:** nic zewnętrznego.
- **Wyjątki:** brak.
- **Uwagi:** `num_index_entries` z mkvmerge to przybliżenie liczby linii, nie dokładna wartość — udokumentowane w docstringu modułu (linia 18) jako świadomy kompromis kształtu danych.

##### `score_subtitle_track(track: dict) -> float` (linia 172)
- **Co robi:** Liczy łączny wynik ścieżki napisów: waga języka + kara signs-only + bonus liczby linii.
- **Przyjmuje:** `track` — dict pojedynczej ścieżki napisów.
- **Zwraca:** `float`.
- **Efekty uboczne:** brak.
- **Woła:** `_track_language()`, `_SUB_LANG_WEIGHT.get()`, `_is_signs_only()`, `_lines_bonus()`.
- **Wyjątki:** brak.
- **Uwagi:** publiczna funkcja (brak `_` prefiksu) — eksponowana do testów i potencjalnego reużycia.

##### `score_audio_track(track: dict) -> float` (linia 192)
- **Co robi:** Liczy łączny wynik ścieżki audio: waga języka + bonus domyślności.
- **Przyjmuje:** `track` — dict pojedynczej ścieżki audio.
- **Zwraca:** `float`.
- **Efekty uboczne:** brak.
- **Woła:** `_track_language()`, `_AUDIO_LANG_WEIGHT.get()`, `_track_default()`.
- **Wyjątki:** brak.
- **Uwagi:** publiczna funkcja, symetryczna do `score_subtitle_track`.

##### `select_subtitle_track(tracks: list[dict]) -> int | None` (linia 211)
- **Co robi:** Filtruje ścieżki typu `"subtitles"`, wybiera tę o najwyższym `score_subtitle_track`, remisy rozstrzyga na korzyść niższego `id` (kolejność w pliku).
- **Przyjmuje:** `tracks` — pełna lista ścieżek MKV (mieszane typy).
- **Zwraca:** `int | None` — ID wybranej ścieżki, `None` gdy brak napisów.
- **Efekty uboczne:** brak.
- **Woła:** `score_subtitle_track()`, wbudowany `max()` z kluczem `(score, -id)`.
- **Wyjątki:** `KeyError` jeśli element listy nie ma klucza `'id'` (nieobsłużone, ale zgodne z kontraktem — `mkvtoolnix._parse_track_data` zawsze dodaje `id`).
- **Uwagi:** publiczne API modułu, jedyny punkt wejścia dla napisów, wołany z `mkvtoolnix.py:383`.

##### `select_audio_track(tracks: list[dict]) -> int | None` (linia 231)
- **Co robi:** Filtruje ścieżki typu `"audio"`, wybiera tę o najwyższym `score_audio_track`, remisy na korzyść niższego `id`.
- **Przyjmuje:** `tracks` — pełna lista ścieżek MKV.
- **Zwraca:** `int | None` — ID wybranej ścieżki, `None` gdy brak audio.
- **Efekty uboczne:** brak.
- **Woła:** `score_audio_track()`, `max()`.
- **Wyjątki:** `KeyError` jak wyżej, nieobsłużone.
- **Uwagi:** publiczne API modułu, wołany z `mkvtoolnix.py:382`.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** wzorcowy plik w całym obszarze pod względem stylu MangaShift — czysto funkcyjny, brak I/O, brak klas/stanu, stałe scoringu wydzielone i nazwane (`Final`), dobrze udokumentowany docstring modułu tłumaczący *dlaczego* (nie tylko *co*), realny test regresyjny na 206 plikach (`tests/track_selector_test.py`). Obsługa trzech kształtów danych (dataset/flat/raw mkvmerge) jest świadoma i jednolicie zaimplementowana we wszystkich czterech helperach (`_track_name`, `_track_language`, `_track_default`, `_lines_bonus`) — nie ma tu przypadkowej niespójności, wzorzec jest powtórzony identycznie.
- **⚠️ dług techniczny / code smells:** brak walidacji `track['id']` przed użyciem w `select_subtitle_track`/`select_audio_track` (linie 227, 247) — `KeyError` przy malformed input nie jest przechwytywany lokalnie (choć w praktyce zawsze przechodzi przez `mkvtoolnix._parse_track_data`, które gwarantuje `id`). Cztery niemal identyczne funkcje "spróbuj kilka kształtów kluczy" (`_track_name`, `_track_language`, `_track_default`, `_lines_bonus`) mogłyby być jedną sparametryzowaną funkcją `_get_field(track, *keys, nested_key)`, ale obecna forma jest czytelna i to drobny, kosmetyczny smell.
- **❌ niespójności ze stylem MangaShift:** brak istotnych — ten plik już realizuje ducha "jedno źródło prawdy per pytanie" (scoring i dobór w jednym miejscu, stałe wagi jawnie nazwane obok logiki). Jedyny drobny minus: `_track_language` tutaj duplikuje logikę `MkvToolNix._track_language` w `mkvtoolnix.py` zamiast być jedynym źródłem prawdy dla tego pytania w całym obszarze — MangaShift nazwałby to "dwa źródła odpowiedzi na to samo pytanie" w obrębie jednego obszaru funkcjonalnego.
- **🔗 sprzężenia:** luźne — jedyny konsument to `mkvtoolnix.py::_auto_select_tracks`, kontrakt wejścia to kształt słownika (nie typowany `TypedDict`/dataclass, tylko luźny `dict`), co jest źródłem właśnie tej wielowariantowej obsługi kluczy opisanej wyżej. Brak sprzężenia z `constants.py`, `Settings` czy jakimkolwiek I/O — najbardziej izolowany plik obszaru.

---

## 🧭 podsumowanie obszaru

**Główne odpowiedzialności:** Obszar pokrywa oba "brzegi" potoku MKV: (1) identyfikacja i ekstrakcja ścieżek źródłowych z pliku wejściowego (`mkvtoolnix.py` + `track_selector.py`, ręcznie lub automatycznie z live progresem), (2) scalenie/wypalenie gotowego lektora i napisów z powrotem do kontenera wyjściowego (`mkv_processing.py`, trzy tryby: przenieś/scal MKV/wypal MP4). `track_selector.py` jest logicznym rdzeniem trybu auto — czysta funkcja scoringu bez efektów ubocznych, oddzielona od reszty.

**Największe problemy (ranking):**
1. **`with suppress(Exception)` wokół całego wywołania FFmpeg** w `mkv_processing.py:170-171` — połyka realne błędy transkodowania/wypalania napisów bez logu, bez sprawdzenia exit code; w połączeniu z brakiem sprawdzenia `returncode` po `mkvmerge` (`mkv_processing.py:136-137`) tworzy realne ryzyko cichej utraty danych (pliki źródłowe usuwane niezależnie od sukcesu operacji).
2. **Nietransakcyjny podwójny `rename()`** w `mkv_burn_to_mp4` (`mkv_processing.py:154-155, 180-181`) bez `try/finally` — przerwanie w trakcie zostawia plik pod zsanityzowaną nazwą.
3. **`sys.exit()` wewnątrz logiki domenowej** klasy `MkvToolNix` (`mkvtoolnix.py:88, 114`) — ubija cały proces zamiast sygnalizować błąd przez wyjątek/zwrot, utrudnia reużycie i testowanie w izolacji.
4. **Duplikacja `_track_language`** między `mkvtoolnix.py:402-421` i `track_selector.py:103-122` — dwa źródła prawdy dla tego samego pytania w obrębie jednego obszaru.
5. **Magic slicing `[2:]` na ścieżkach Windows** w `_prepare_command` (`mkv_processing.py:217-246`, 6 wystąpień) — niezadokumentowana zależność od litery dysku, kruche na innych układach ścieżek.
6. **Dispatch po dokładnym tekście menu** w `MKVProcessing.process_mkv` (`mkv_processing.py:76-82`) — string matching zamiast typowanego klucza, ciche milczenie przy niedopasowaniu.

**Kandydaci do refaktoru na styl MangaShift:**
- `MKVProcessing.process_mkv` → zamiana dict `{tekst_menu: metoda}` na rejestr z typowanym `Literal`/enumem `OutputMode` obok stałej `_OUTPUT_HANDLERS`, zgodnie z wzorcem "rejestr obok typu" z MangaShift (Literal + mapa leżą linijka pod linijką w jednym pliku).
- `MkvToolNix._get_format_extension` → wydzielenie `format_dict` (34 wpisy, dziś budowany od zera przy każdym wywołaniu) jako stałą modułową `Final[dict[str, str]]`, analogicznie do wzorca "katalog" w MangaShift (jedna lista-prawda, czytana, nie budowana za każdym razem).
- Ujednolicenie loggera: `MkvToolNix` ma DI przez pole `console` (dobre), `MKVProcessing` używa globalnego `console` na sztywno — ujednolicić na wzorzec DI z `mkvtoolnix.py`.
- Konsolidacja `_track_language` do jednego miejsca (np. przenieść wersję z `track_selector.py` jako jedyne źródło prawdy, `mkvtoolnix.py` niech z niej korzysta) — usuwa duplikat, obszar zyskuje "jedno źródło prawdy per pytanie".
- Zastąpienie `sys.exit()` w `MkvToolNix` wyjątkiem domenowym (np. `MkvToolsMissingError`) łapanym na poziomie `start.py` — pozwala bibliotece być reużywalną i testowalną bez ubijania procesu.

**Pliki/funkcje martwe lub podejrzane:**
- `MkvToolNix.mkv_propedit_path` (pole, `mkvtoolnix.py:73`) — zdefiniowane, nigdzie nieużywane w klasie; `mkvpropedit.exe` nigdy nie jest wołany.
- `MkvToolNix.mkv_info_path` (pole, `mkvtoolnix.py:72`) — sprawdzany w `_check_executables`, ale realna identyfikacja idzie przez `mkv_merge_path --identify`; `mkvinfo.exe` nigdy faktycznie nie jest uruchamiany mimo istnienia dedykowanej ścieżki i sprawdzenia jej obecności.
- `MKVProcessing.working_space_output` bezpośrednio jako pole (nieużywane samodzielnie poza kompozycją ścieżek) — nie jest martwe, ale warto zauważyć że `mkvtoolnix.py` ma analogiczne pole `working_space_output` również praktycznie nieużywane wewnątrz tego pliku (ekstrakcja pisze tylko do `working_space_temp`).

---


# CZĘŚĆ 03 — modules: napisy

# 📦 obszar: modules: napisy (refaktor/tłumaczenie/klasyfikacja stylu) — pliki: `modules/subtitle.py`, `modules/translator.py`, `modules/style_classifier.py`

**Rola obszaru w projekcie:** ten zestaw plików odpowiada za środkowy odcinek potoku
ekstrakcja→napisy→TTS→merge: podział wyekstrahowanych napisów ASS na tor "dialog" (do
czytania przez lektora) i "sign/OP-ED" (do zachowania jako napisy), konwersję
ASS↔SRT↔TXT, tłumaczenie napisów SRT na polski (Google/DeepL API/DeepL desktop) oraz
scalenie przetłumaczonego SRT z powrotem do oryginalnego ASS. `style_classifier.py`
dostarcza heurystykę klasyfikacji stylów używaną przez `subtitle.py` w trybie
automatycznym (`auto_mode`).

**Zależności zewnętrzne obszaru:** `pysubs2` (SSAFile/SSAEvent — parsowanie ASS),
`pysrt` (SubRipFile — parsowanie SRT), `googletrans` (Translator, tłumaczenie Google),
`deepl` (Translator, DeepL API), `pyautogui` + `pyperclip` (automatyzacja GUI DeepL
desktop), `re`, `asyncio`, `dataclasses`, `enum`, `collections.defaultdict`. Wewnętrzne:
`constants` (ścieżki working_space, `console`), `data.settings.Settings`,
`utils.number_in_words.NumberInWords`, `utils.text_chunker.chunk_text`. Wołane z
`start.py` (`SubtitleRefactor`, `SubtitleTranslator`) — `style_classifier` jest wołany
tylko pośrednio, przez lazy-import wewnątrz `subtitle.py:186`.

---

## 📄 plik: `modules/subtitle.py` (515 linii)

### przeznaczenie
Definiuje jedyną klasę `SubtitleRefactor`, fasadę operacji na plikach napisów w obrębie
jednego pliku roboczego (`self.filename`). Obsługuje cały cykl: podział ASS na
main/alt wg stylu (ręczny lub automatyczny przez `style_classifier`), konwersję
ASS→SRT, przenoszenie gotowych SRT, generowanie SRT z surowego TXT (np. transkryptu),
zamianę liczb na słowa w SRT, oraz scalenie przetłumaczonego SRT z powrotem do ASS
(`srt_to_ass`). Wołany z `start.py` w kilku miejscach potoku (ekstrakcja→podział,
tłumaczenie→scalenie).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | regexy do vector-drawing, tagów ASS, HTML |
| `suppress` | contextlib | tłumienie `ValueError` przy parsowaniu wyboru użytkownika |
| `dataclass` | dataclasses | dekorator klasy `SubtitleRefactor` |
| `makedirs, path, remove, stat` | os | zarządzanie plikami/katalogami |
| `move` | shutil | przenoszenie plików |
| `List, Tuple` | typing | adnotacje typów (styl mieszany ze starym `typing.List/Tuple` i nowym `list[...]`) |
| `load, SSAEvent, SSAFile` | pysubs2 | wczytywanie/tworzenie zdarzeń i plików napisów |
| `WORKING_SPACE*`, `console` | constants | ścieżki katalogów roboczych + kolorowy log |
| `NumberInWords` | utils.number_in_words | konwersja liczb na słowa (PL) |
| `chunk_text` | utils.text_chunker | dzielenie tekstu na fragmenty wg limitu znaków/słów |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `_BACKSLASH` | 53 | `str` | `chr(92)` — literalny backslash budowany programowo, by uniknąć problemu z escape'ami w Pythonie 3.14 |
| `_RE_DRAW_PATH` | 55 | `re.Pattern` | `\b[mn] -?\d+` — wykrywa komendy rysowania wektorowego (np. `m 0 0 l 186 0`) |
| `_RE_DRAW_TAG` | 58 | `re.Pattern` | `\\p[1-9]` (budowany z `_BACKSLASH*2`) — wykrywa tag ASS `\p1`-`\p9` (tryb rysowania) |

### klasy

#### `class SubtitleRefactor` (linia 62) — `@dataclass(slots=True)`
**Cel:** fasada operacji na jednym pliku napisów; łączy w sobie split/convert/translate-merge dla jednego `filename`.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `filename` | `str` | — | nazwa pliku napisów przetwarzanego przez instancję |
| `working_space` | `str` | `WORKING_SPACE` | katalog główny roboczy |
| `working_space_output` | `str` | `WORKING_SPACE_OUTPUT` | katalog wyjściowy |
| `working_space_temp` | `str` | `WORKING_SPACE_TEMP` | katalog tymczasowy |
| `working_space_temp_main_subs` | brak adnotacji typu (linia 86) | `WORKING_SPACE_TEMP_ALT_SUBS` **(!)** | katalog dla napisów "main" (dialog) — patrz uwaga niżej, wartość domyślna jest błędna |
| `working_space_temp_alt_subs` | brak adnotacji typu (linia 87) | `WORKING_SPACE_TEMP_ALT_SUBS` | katalog dla napisów "alt" (sign) |

⚠️ **Bug: `working_space_temp_main_subs` i `working_space_temp_alt_subs` (linie 86-87) nie mają
adnotacji typu** — w `@dataclass(slots=True)` pole bez adnotacji typu NIE staje się polem
dataclass (nie trafia do `__init__`, `__repr__`, ani do `__slots__`), tylko zwykłym atrybutem
klasy (class variable) współdzielonym przez wszystkie instancje. Sprawdzone: `working_space_temp_main_subs = WORKING_SPACE_TEMP_MAIN_SUBS` to **przypisanie wartości `WORKING_SPACE_TEMP_MAIN_SUBS`**, ale bez `: str` przed `=` — dataclass go pomija jako pole. W praktyce działa dziś przypadkiem (bo są to stałe globalne, a nie per-instancja), ale to niespójne z resztą klasy i podatne na ciche błędy przy próbie nadpisania per-instancja (patrz `tests/srt_to_ass_test.py:100-101`, które nadpisują `SubtitleRefactor.working_space_temp_alt_subs` jako atrybut klasy — działa tylko dlatego, że to nie jest prawdziwe pole dataclass).

**Metody:**

##### `split_ass(self, auto_mode: bool = False) -> None` (linia 89)
- **Co robi:** Orkiestruje podział pliku ASS na dwa pliki (main/alt) na podstawie wybranych stylów — ręcznie lub automatycznie.
- **Przyjmuje:** `auto_mode` — gdy `True`, style dobiera `style_classifier` zamiast pytać usera.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy katalogi, zapisuje 2 pliki ASS, usuwa plik źródłowy, drukuje do konsoli.
- **Woła:** `self._create_directories()`, `self._load_subs()`, `self._get_styles()`, `self._auto_select_styles()` lub (`self._display_styles()` + `self._select_styles()`), `self._move_subs_to_main()`, `self._split_subs()`, `self._copy_metadata_and_styles()`, `self._save_subs()`, `self._remove_source_file()`.
- **Wyjątki:** brak jawnej obsługi — propaguje wyjątki z wołanych metod (np. `FileNotFoundError` z `_load_subs`).
- **Uwagi:** god-method — 10 kroków sekwencyjnych bez żadnej abstrakcji pośredniej (brak np. klasy `SplitResult`).

##### `_create_directories(self) -> None` (linia 117)
- **Co robi:** Tworzy katalogi `working_space_temp_main_subs`/`_alt_subs`, jeśli nie istnieją.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `os.makedirs` (I/O na dysku).
- **Woła:** `path.exists`, `makedirs`.
- **Wyjątki:** brak przechwytywania (np. `OSError` przy braku uprawnień).

##### `_load_subs(self) -> SSAFile` (linia 126)
- **Co robi:** Wczytuje plik napisów (`self.filename`) z katalogu temp jako `SSAFile`.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `SSAFile`.
- **Efekty uboczne:** otwiera plik (I/O).
- **Woła:** `open`, `SSAFile.from_file`.
- **Wyjątki:** `FileNotFoundError`, błędy parsowania pysubs2 — niełapane.

##### `_get_styles(self, subs: SSAFile) -> List[str]` (linia 133)
- **Co robi:** Zwraca listę unikalnych nazw stylów użytych w zdarzeniach (kolejność pierwszego wystąpienia).
- **Przyjmuje:** `subs` — załadowany plik napisów.
- **Zwraca:** `List[str]`.
- **Efekty uboczne:** brak.
- **Woła:** iteruje `subs`.
- **Wyjątki:** brak.
- **Uwagi:** O(n·m) — sprawdzenie `style not in styles` na liście zamiast setu; przy dużej liczbie unikalnych stylów nieoptymalne, choć w praktyce liczba stylów jest mała (single-digit/kilkanaście).

##### `_display_styles(self, styles: List[str]) -> None` (linia 143)
- **Co robi:** Wypisuje numerowaną listę stylów do konsoli (interaktywny tryb ręczny).
- **Przyjmuje:** `styles`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `console.print` (I/O terminala).
- **Woła:** `console.print`.
- **Wyjątki:** brak.

##### `_select_styles(self, styles: List[str]) -> List[str]` (linia 154)
- **Co robi:** Pętla `input()` — użytkownik wybiera numery stylów do zachowania jako dialog; ENTER kończy.
- **Przyjmuje:** `styles`.
- **Zwraca:** `List[str]` wybranych nazw stylów.
- **Efekty uboczne:** blokujące `input()`, `console.print`.
- **Woła:** `input`, `suppress(ValueError)`.
- **Wyjątki:** `ValueError` z `int(selection)` jest tłumiony (`suppress`) — niepoprawny numer po prostu pomijany bez komunikatu dla użytkownika (cichy fail).
- **Uwagi:** brak górnego limitu iteracji — pętla `while True` bez wyjścia poza pusty input; to zamierzone (UX), ale brak walidacji błędnego wpisu jest cichy.

##### `_auto_select_styles(self, subs: SSAFile, styles: List[str]) -> List[str]` (linia 171)
- **Co robi:** Automatyczny odpowiednik `_display_styles`+`_select_styles` — klasyfikuje style przez `style_classifier.classify_styles`, drukuje dry-run (ikona + kategoria + pewność + liczba linii, z adnotacją deduplikacji animacji), zwraca style DIALOG+UNCERTAIN.
- **Przyjmuje:** `subs` — załadowany plik; `styles` — lista nazw stylów (parametr **nieużywany w ciele funkcji** — wynik bazuje wyłącznie na `classify_styles(subs)`, `styles` jest martwym argumentem).
- **Zwraca:** `List[str]` wybranych nazw stylów (DIALOG + UNCERTAIN).
- **Efekty uboczne:** `console.print` (log dry-run).
- **Woła:** lazy `from modules.style_classifier import Category, classify_styles` (linia 186), `classify_styles(subs)`.
- **Wyjątki:** brak jawnej obsługi.
- **Uwagi:** import wewnątrz metody zamiast na górze pliku — celowy (unika cyklicznej zależności / kosztu importu przy trybie ręcznym), ale niespójny ze standardowym stylem importów na górze modułu. Parametr `styles` martwy — code smell (niepotrzebny argument w sygnaturze).

##### `_move_subs_to_main(self) -> None` (linia 212)
- **Co robi:** Gdy user nie wybrał żadnego stylu, przenosi cały plik napisów bez podziału do katalogu `main_subs`.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `console.print`, `makedirs`, `shutil.move` (przenosi plik).
- **Woła:** `console.print`, `makedirs`, `path.join`, `move`.
- **Wyjątki:** `FileNotFoundError`/`OSError` z `move` niełapane.

##### `_split_subs(self, subs: SSAFile, selected_styles: List[str]) -> Tuple[SSAFile, SSAFile]` (linia 225)
- **Co robi:** Rozdziela zdarzenia `subs` na dwa nowe `SSAFile` wg przynależności stylu do `selected_styles`.
- **Przyjmuje:** `subs`, `selected_styles`.
- **Zwraca:** krotkę `(main_subs, alt_subs)`.
- **Efekty uboczne:** brak (czysta transformacja w pamięci).
- **Woła:** `SSAFile()`, `.append`.
- **Wyjątki:** brak.

##### `_copy_metadata_and_styles(self, subs, main_subs, alt_subs, selected_styles) -> None` (linia 240)
- **Co robi:** Kopiuje `info` (metadane) i definicje stylów (`.styles`) z `subs` do `main_subs`/`alt_subs`, dzieląc style wg przynależności do `selected_styles`.
- **Przyjmuje:** `subs`, `main_subs`, `alt_subs`, `selected_styles`.
- **Zwraca:** `None`.
- **Efekty uboczne:** mutuje `main_subs`/`alt_subs` in place.
- **Woła:** brak zewnętrznych wywołań poza operacjami na słownikach `.styles`.
- **Wyjątki:** brak.
- **Uwagi:** ⚠️ **duplikacja kodu 1:1 z `_save_subs` (linie 268-281)** — ten sam blok kopiowania `info` i stylów jest przepisany identycznie w obu metodach. `_copy_metadata_and_styles` jest zresztą wołana w `split_ass` (linia 110) **przed** `_save_subs`, która i tak powtarza całą pracę — de facto podwójne, zbędne wykonanie tej samej logiki.

##### `_save_subs(self, main_subs, alt_subs, subs, selected_styles) -> None` (linia 259)
- **Co robi:** Zapisuje `main_subs`/`alt_subs` do plików `.ass` w odpowiednich katalogach; po drodze **powtarza** kopiowanie metadanych/stylów (patrz wyżej).
- **Przyjmuje:** `main_subs`, `alt_subs`, `subs`, `selected_styles`.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje 2 pliki na dysk.
- **Woła:** `path.join`, `open`, `.to_string(format_='ass')`.
- **Wyjątki:** `OSError` przy zapisie niełapany.
- **Uwagi:** duplikacja z `_copy_metadata_and_styles` — patrz wyżej; martwa/zbędna praca.

##### `_remove_source_file(self) -> None` (linia 289)
- **Co robi:** Usuwa oryginalny plik napisów z katalogu temp po podziale.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `os.remove` (I/O, nieodwracalne).
- **Woła:** `remove`, `path.join`.
- **Wyjątki:** `FileNotFoundError` niełapany.

##### `ass_to_srt(self) -> None` (linia 295)
- **Co robi:** Dla obu katalogów (main/alt) konwertuje `self.filename` z ASS na SRT, usuwając tagi HTML z wyniku.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje nowy plik `.srt` obok istniejącego `.ass` (nie usuwa oryginału ASS); `console.print()` pusty na końcu.
- **Woła:** `path.exists`, `SSAFile.load`, `SSAFile()`, `.insert`, `.to_string(format_='srt')`, `re.sub`, `open`.
- **Wyjątki:** błędy parsowania pysubs2 niełapane.
- **Uwagi:** `console.print()` bez argumentu na końcu (linia 319) — tylko pusta linia w logu, niejasny cel.

##### `move_srt(self) -> None` (linia 321)
- **Co robi:** Przenosi plik SRT z katalogu temp do `main_subs`, usuwając po drodze tagi pozycjonowania ASS (`{\an\d+}`) z treści.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapis nowego pliku, `os.remove` źródła.
- **Woła:** `path.exists`, `makedirs`, `open` (odczyt+zapis), `re.sub`, `remove`.
- **Wyjątki:** `FileNotFoundError` niełapany.

##### `txt_to_srt(self, chunk_limit: int = 750, sentence_length: int = 0, split_method: str = 'word') -> None` (linia 345)
- **Co robi:** Konwertuje plik TXT na SRT: normalizuje białe znaki, dzieli tekst na chunki (`chunk_text`), opcjonalnie grupuje chunki w dłuższe napisy do `sentence_length`, zapisuje jako SRT (czas 0), usuwa TXT i woła `move_srt()`.
- **Przyjmuje:** `chunk_limit` — maks. długość pojedynczego chunka; `sentence_length` — maks. długość zgrupowanego napisu (0 = brak grupowania); `split_method` — `'word'`/`'char'`.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje SRT, usuwa TXT, mutuje `self.filename` (zamienia `.txt`→`.srt`), woła `self.move_srt()`.
- **Woła:** `chunk_text`, wewnętrzną funkcję zagnieżdżoną `add_chunk_to_caption(chunk)` (closure na `current_caption`/`captions` przez `nonlocal`), `SSAFile()`, `SSAEvent`, `remove`, `self.move_srt()`.
- **Wyjątki:** brak jawnej obsługi.
- **Uwagi:** ⚠️ TODO jawnie w kodzie (linia 344): `# TODO: dodać deklaracje typów i zmowyfikowac instrukcjie na górze itp.` (literówka w komentarzu: "zmowyfikowac"). Sygnatura ma nietypową kolejność parametrów względem docstringa (`chunk_limit` nie był udokumentowany w oryginalnym docstringu modułu z linii 20, który wspominał `sentence_length` jako jedyny argument — dokumentacja modułu jest przestarzała względem realnej sygnatury). Domyślny `sentence_length=0` semantycznie oznacza "brak przetwarzania", co jest niejawne (magic value 0 jako flaga trybu).

##### `convert_numbers_in_srt(self) -> None` (linia 411)
- **Co robi:** Wczytuje SRT z `main_subs`, zamienia liczby na słowa (PL) w każdej linii przez `NumberInWords`, zapisuje z powrotem.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** nadpisuje plik SRT, `console.print` logów/błędów.
- **Woła:** `load` (pysubs2), `NumberInWords()`, `.convert_numbers_in_text`, `subs.save`.
- **Wyjątki:** łapie `IndexError` per-linia (loguje i pomija tę linię) — reszta wyjątków propaguje.
- **Uwagi:** gołe łapanie tylko `IndexError` — jeśli `NumberInWords` rzuci coś innego (np. `ValueError`), cała metoda się wywali bez kontekstu.

##### `_is_vector_drawing(text: str) -> bool` (linia 434, `@staticmethod`)
- **Co robi:** Sprawdza, czy tekst zdarzenia ASS to rysunek wektorowy (komenda draw-path lub tag `\p1`-`\p9`) — takie linie nie mają tłumaczenia.
- **Przyjmuje:** `text` — surowy tekst zdarzenia ASS.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `_RE_DRAW_PATH.search`, `_RE_DRAW_TAG.search`.
- **Wyjątki:** brak.

##### `srt_to_ass(self) -> None` (linia 445)
- **Co robi:** Najważniejsza metoda scaleniowa — wstrzykuje przetłumaczone linie SRT z powrotem do oryginalnego pliku ASS, mapując po `(start, end)` zamiast po pozycji/indeksie (odporne na przesunięcia linii między konwersjami). Jeśli plik ASS nie istnieje (np. tor `alt`, który od razu był SRT), zamiast tego tworzy nowy ASS z samego SRT i przenosi wynik do katalogu output.
- **Przyjmuje:** nic poza `self` (operuje na `self.filename`).
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje plik wynikowy w `working_space_output`, usuwa pliki źródłowe SRT/ASS, `console.print`.
- **Woła:** `stat`, `load` (pysrt), `SSAFile.load`, `self._is_vector_drawing`, `ass_subs.save`, `SSAEvent`, `move`, `remove`.
- **Wyjątki:** brak jawnej obsługi (m.in. `stat` rzuci `FileNotFoundError`, jeśli plik SRT nie istnieje — funkcja zakłada, że zawsze istnieje).
- **Uwagi:** early-return na pustym pliku SRT (linia 458-459: `if stat(srt_file_path).st_size == 0: return`) — pozostawia oryginalny plik ASS bez tłumaczenia po cichu, bez logu/ostrzeżenia że coś zostało pominięte. Logika mapowania `(start, end)→queue tekstów` (linie 471-474) jest sprytna i dobrze skomentowana — to jeden z niewielu fragmentów z realnym uzasadnieniem inżynierskim w komentarzach.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** mapowanie SRT→ASS po `(start, end)` zamiast po indeksie (linie 465-474) jest odporne na desynchronizację; `_is_vector_drawing` poprawnie chroni linie graficzne przed nadpisaniem tłumaczeniem; komentarze przy regexach (`_BACKSLASH`, linie 50-58) tłumaczą niestandardowe obejście dla Python 3.14 zamiast zostawiać zagadkę.
- **⚠️ dług techniczny / code smells:**
  - `subtitle.py:86-87` — pola `working_space_temp_main_subs`/`_alt_subs` bez adnotacji typu w `@dataclass(slots=True)` → nie są prawdziwymi polami dataclass, tylko class-var; niespójne z resztą klasy i mylące.
  - `subtitle.py:240-287` — duplikacja logiki kopiowania metadanych/stylów między `_copy_metadata_and_styles` i `_save_subs` (identyczny blok wykonywany dwa razy w `split_ass`).
  - `subtitle.py:171-210` — `_auto_select_styles` ma martwy parametr `styles` (nieużywany w ciele).
  - `subtitle.py:344` — jawny `# TODO` z literówką, świadectwo niedokończonej pracy.
  - `subtitle.py:165-169` — `suppress(ValueError)` cicho połyka błędny numer wyboru bez komunikatu zwrotnego dla użytkownika.
  - `subtitle.py:421-427` — gołe łapanie wyłącznie `IndexError`, inne wyjątki z `NumberInWords` wywalają całą metodę.
  - Mieszanie `typing.List/Tuple` (stary styl) z adnotacjami bez importu (`list[SSAEvent]` nigdzie tu, ale w `style_classifier.py` już nowy styl) — niespójność międzyplikowa w tym samym obszarze.
  - `split_ass` (linia 89) to god-method o 10 sekwencyjnych krokach bez żadnej pośredniej struktury danych.
- **❌ niespójności ze stylem MangaShift:**
  - Brak podziału na warstwy serwis/rejestr/pipeline — `SubtitleRefactor` jest jednocześnie "serwisem" i "pipeline'em": zna wszystkie kroki na sztywno, nie ma rejestru operacji ani wstrzykiwanych zależności.
  - Zero dependency injection — `console`, ścieżki `WORKING_SPACE*` importowane bezpośrednio z modułu `constants`, a nie wstrzykiwane; testowanie wymaga podmiany atrybutów klasowych (`tests/srt_to_ass_test.py:100-101` nadpisuje `SubtitleRefactor.working_space_temp_alt_subs` globalnie na czas testu — dokładnie ten smell, przed którym broni DI).
  - Brak rejestru/fasady dla "sposobów podziału stylu" (ręczny vs auto) — to `if auto_mode: ... else: ...` (linia 101-105) zamiast strategii wybieranej przez rejestr, co jest odwrotnością zasady "zero if-ów per silnik" z MangaShift.
  - `_auto_select_styles` woła `style_classifier` przez lazy-import wewnątrz metody zamiast przez jawnie wstrzykiwaną zależność/interfejs — sprzeczne z "jedno źródło prawdy" (import ukryty w środku logiki, trudny do namierzenia bez czytania całej metody).
- **🔗 sprzężenia:** ciasno powiązany z `constants.py` (5 stałych ścieżek), z `pysubs2`/`pysrt` API (format-specific `.to_string(format_='ass'/'srt')`), z `style_classifier.classify_styles` (przez lazy-import), z `utils.number_in_words.NumberInWords` i `utils.text_chunker.chunk_text`. Zmiana struktury katalogów w `constants.py` złamie klasę wprost (brak abstrakcji nad ścieżkami). `start.py` tworzy `SubtitleRefactor(filename)` w 3 miejscach (linie 282, 414, 488) — każda zmiana konstruktora/API wymaga aktualizacji wywołań w `start.py`.

---

## 📄 plik: `modules/translator.py` (342 linie)

### przeznaczenie
Definiuje klasę `SubtitleTranslator` z metodami tłumaczącymi pliki SRT na polski trzema
kanałami: Google Translate (`googletrans`), DeepL API, DeepL desktop (automatyzacja GUI
przez `pyautogui`/`pyperclip`). `translate_srt` jest fasadą wybierającą metodę na
podstawie `Settings.translator`. Wołany z `start.py` po podziale/konwersji napisów, przed
scaleniem `srt_to_ass`.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | czyszczenie tagów ASS/HTML z tekstu przed tłumaczeniem, normalizacja whitespace po tłumaczeniu |
| `asyncio.run` | stdlib (as `asyncio_run`) | uruchomienie async API `googletrans` synchronicznie |
| `dataclass` | dataclasses | dekorator klasy |
| `environ, path` | os | odczyt `%APPDATA%`, budowanie ścieżek |
| `call` | subprocess | uruchomienie instalatora/launchera DeepL desktop przez Zero Install |
| `sleep` | time | opóźnienia w automatyzacji GUI |
| `Dict, List` | typing | adnotacje typów (styl `typing.Dict/List`, nie `dict/list`) |
| `deepl` | pakiet zewn. | `deepl.Translator` — DeepL API |
| `pyautogui` | pakiet zewn. | sterowanie myszą/klawiaturą dla DeepL desktop |
| `pyperclip` | pakiet zewn. | schowek systemowy (kopiuj/wklej do DeepL desktop) |
| `pysrt` | pakiet zewn. | parsowanie/zapis plików SRT |
| `googletrans.Translator` | pakiet zewn. | tłumaczenie przez Google Translate (nieoficjalne API) |
| `WORKING_SPACE_TEMP_MAIN_SUBS`, `WORKING_SPACE_TEMP_ALT_SUBS`, `console` | constants | ścieżki domyślne pól dataclass + log |
| `Settings` | data.settings | odczyt konfiguracji tłumacza (`translator`, `deepl_api_key`, `translated_line_count`) |

### stałe / zmienne modułowe
Brak stałych modułowych (poza importami) — wszystkie stałe znacznikowe (`ZWSP`,
`SEPARATOR`, `NEWLINE_MARKER` itp.) są zdefiniowane lokalnie wewnątrz metod, nie na
poziomie modułu.

### klasy

#### `class SubtitleTranslator` (linia 45) — `@dataclass(slots=True)`
**Cel:** fasada trzech silników tłumaczeniowych + metoda wyboru na podstawie ustawień użytkownika.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `working_space_temp_main_subs` | `str` | `WORKING_SPACE_TEMP_MAIN_SUBS` | katalog głównych napisów (dialog) |
| `working_space_temp_alt_subs` | `str` | `WORKING_SPACE_TEMP_ALT_SUBS` | katalog alternatywnych napisów (sign) |

Uwaga: w przeciwieństwie do `subtitle.py`, tu oba pola MAJĄ poprawną adnotację typu `str` — spójne z dataclass. Jednak w praktyce **żadna z metod klasy nie używa tych pól** — wszystkie metody tłumaczące są `@staticmethod` i przyjmują `dir_path` jako parametr; pola `working_space_temp_*` są martwe (nieużywane nigdzie w pliku poza deklaracją).

**Metody:**

##### `_clean_subtitle_text(text: str) -> str` (linia 71, `@staticmethod`)
- **Co robi:** Usuwa tagi override ASS (`{...}`), resztkowe tagi HTML (`<...>`) i zamienia twardą spację ASS (`\h`) na zwykłą; zachowuje realne znaki nowej linii.
- **Przyjmuje:** `text` — surowa linia napisu.
- **Zwraca:** `str` oczyszczony.
- **Efekty uboczne:** brak.
- **Woła:** `re.sub` ×2, `str.replace`.
- **Wyjątki:** brak.

##### `translate_google(filename: str, dir_path: str, translated_line_count: int, is_combined_with_gpt: bool = False) -> pysrt.SubRipFile` (linia 91, `@staticmethod`)
- **Co robi:** Tłumaczy plik SRT przez Google Translate. Deduplikuje unikalne frazy (tłumaczy każdą raz, nawet jeśli powtarza się setki razy), koduje newline'y znacznikiem z zero-width space, tłumaczy w batchach o rozmiarze `translated_line_count`, z 3-poziomowym fallbackiem przy niezgodności liczby linii po tłumaczeniu wsadowym.
- **Przyjmuje:** `filename`, `dir_path`, `translated_line_count`, `is_combined_with_gpt` (opcjonalnie — zapisuje do pliku `_translated_temp.srt` i zwraca `subs` zamiast nadpisywać oryginał).
- **Zwraca:** `pysrt.SubRipFile` (gdy `is_combined_with_gpt=True`); w przeciwnym razie funkcja **nie ma jawnego `return`** mimo deklarowanego typu zwrotu — zwraca `None` niejawnie (niespójność sygnatury z realnym zachowaniem).
- **Efekty uboczne:** zapisuje plik SRT na dysk (poza gałęzią `is_combined_with_gpt`), wykonuje sieciowe wywołania tłumaczące (async przez `asyncio_run` per batch — blokujące, sekwencyjne).
- **Woła:** zagnieżdżone funkcje `_translate_async` (linia 105, async), `translate_sync` (linia 110), `_clean_translation` (linia 120), `_translate_unique` (linia 135); `pysrt.open`, `subs.save`.
- **Wyjątki:** brak jawnej obsługi błędów sieciowych/API — `Translator().translate()` może rzucić wyjątek `googletrans` niełapany.
- **Uwagi:** ⚠️ deklarowany zwrot `-> pysrt.SubRipFile`, ale gałąź bez `is_combined_with_gpt` nie zwraca nic (kończy się `subs.save(...)` bez `return`) — niezgodność typu. `asyncio_run` wołany w pętli per-batch (linia 141, wewnątrz `_translate_unique`) zamiast raz na całość — tworzy nowy event loop za każdym razem, kosztowne i niepotrzebnie skomplikowane wobec w pełni synchronicznego API DeepL w sąsiedniej metodzie. Trzypoziomowy fallback (separator→newline→pojedynczo) to solidna obrona przed niedopasowaniem liczby linii, ale komplikuje czytelność i jest **niemal 1:1 zduplikowany** względem `translate_deepl_api` (różni się głównie separatorem i wywołaniem API — patrz duplikacja niżej).

##### `translate_deepl_api(filename: str, dir_path: str, translated_line_count: int, deepl_api_key: str) -> None` (linia 180, `@staticmethod`)
- **Co robi:** Tłumaczy SRT przez DeepL API tym samym schematem deduplikacji unikalnych fraz + batching co `translated_line_count`, z innym zestawem znaczników (`◍◍◍◍`, `@@\n`).
- **Przyjmuje:** `filename`, `dir_path`, `translated_line_count`, `deepl_api_key`.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje plik SRT, wywołuje DeepL API (sieć).
- **Woła:** zagnieżdżone `_clean_translation` (linia 197), `_translate_unique` (linia 203); `pysrt.open`, `deepl.Translator(deepl_api_key)`, `translator.translate_text`, `subs.save`.
- **Wyjątki:** brak jawnej obsługi (błędy autoryzacji/limitu DeepL propagują się niełapane).
- **Uwagi:** ⚠️ **duplikacja ~80% kodu z `translate_google`** — identyczny wzorzec: `_clean_subtitle_text`, deduplikacja unikalnych fraz przez `dict.fromkeys`, budowa `translation_map`, pętla `for sub, marked in zip(...)`. Różni się tylko separatorami znacznikowymi i wywołaniem silnika. Klasyczny kandydat do wydzielenia wspólnej funkcji `_translate_via(engine_fn, ...)` z silnikiem jako parametrem — dokładnie wzorzec "rejestr silników, zero duplikacji per silnik" z MangaShift, którego tu brakuje.

##### `translate_deepl_desktop(filename: str, dir_path: str, translated_line_count: int) -> None` (linia 238, `@staticmethod`)
- **Co robi:** Uruchamia desktopową aplikację DeepL przez Zero Install, następnie automatyzuje GUI (`pyautogui`) — klika, wkleja tekst przez schowek, czeka, kopiuje wynik ze schowka; robi to per grupa linii (`translated_line_count`); na końcu usuwa stopki reklamowe DeepL z wynikowego pliku.
- **Przyjmuje:** `filename`, `dir_path`, `translated_line_count`.
- **Zwraca:** `None`.
- **Efekty uboczne:** uruchamia zewnętrzny proces (`subprocess.call`), steruje myszą/klawiaturą całego systemu (`pyautogui`), modyfikuje schowek systemowy, zapisuje plik.
- **Woła:** `call`, `sleep`, zagnieżdżoną `auto_steps()` (linia 255), `pysrt.open`, `pyperclip.copy/paste`, `pyautogui.moveTo/click/hotkey`, `subs.save`, `open`/`write` (usuwanie stopek).
- **Wyjątki:** brak jawnej obsługi — cała metoda jest zasadniczo bez żadnej odporności na błędy (np. `pyperclip.paste()` może zwrócić stary/pusty tekst, jeśli GUI się nie zdąży — kod tylko sprawdza `if translated_text:` bez retry ani timeoutu adaptacyjnego).
- **Uwagi:** ⚠️ **bug logiczny w pętli przypisań (linie 285-288):**
  ```python
  for sub, trans_text in zip(group, translated_text.split(" @@\n")):
      sub.text = trans_text.replace(" ◍◍◍◍, ", ",\n")
      sub.text = trans_text.replace(" ◍◍◍◍ ", "\n")
      sub.text = trans_text.replace(" ◍◍◍◍", "")
  ```
  trzy kolejne przypisania do `sub.text` z `trans_text` (nie z poprzedniego wyniku!) — każde przypisanie NADPISUJE poprzednie zamiast je łańcuchować; efektywnie liczy się tylko ostatnia linia (`.replace(" ◍◍◍◍", "")`), pierwsze dwa `replace` są martwym kodem — bug, nie tylko code smell. W `translate_google`/`translate_deepl_api` analogiczna funkcja `_clean_translation` poprawnie łańcuchuje (`t.replace(...).replace(...).replace(...)`), więc to wygląda na regresję/niedopatrzenie przy kopiowaniu logiki do tej metody. Automatyzacja GUI (`pyautogui`) to też fundamentalnie kruche podejście (zależne od rozdzielczości ekranu, fokusu okna, czasu ładowania) — brak jakiejkolwiek walidacji sukcesu kroku.

##### `translate_srt(self, filename: str, dir_path: str, settings: Settings) -> None` (linia 307)
- **Co robi:** Fasada wyboru silnika tłumaczenia na podstawie `settings.translator` (string) — mapuje nazwę na funkcję przez słownik `translator_functions`.
- **Przyjmuje:** `self`, `filename`, `dir_path`, `settings` — obiekt `Settings` z polami `translator`, `translated_line_count`, `deepl_api_key`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `console.print` logów, deleguje do wybranej metody statycznej (I/O plikowe + sieciowe jak wyżej).
- **Woła:** zagnieżdżone domknięcia `_translate_google` (linia 324), `_translate_deepl_api` (linia 327) — oba tylko przekierowują do odpowiednich `@staticmethod`; słownik `translator_functions` (linia 331) jako mini-rejestr.
- **Wyjątki:** brak — gdy `translator` nie pasuje do żadnego klucza, loguje błąd i **cicho nic nie robi** (nie tłumaczy, nie rzuca wyjątku) — plik pozostaje nieprzetłumaczony bez jawnej sygnalizacji błędu do wywołującego kodu.
- **Uwagi:** ⚠️ **`translate_deepl_desktop` jest całkowicie pominięty w `translator_functions`** (linie 331-334) — mimo że jest to w pełni zaimplementowana metoda klasy, `translate_srt` nigdy jej nie wywoła, niezależnie od wartości `settings.translator`. To albo martwy kod (`translate_deepl_desktop` nieosiągalny przez normalny przepływ), albo brakujący wpis w rejestrze (bug). Sam mechanizm `translator_functions` jako słownik-rejestr (linia 331-334) to jednak **najbliższy w całym obszarze wzorzec zbliżony do "rejestru silników" MangaShift** — mały krok w dobrą stronę, niedokończony (brakujący wpis, wciąż statyczny słownik zdefiniowany lokalnie zamiast modułowego rejestru).

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** deduplikacja unikalnych fraz przed tłumaczeniem (`dict.fromkeys`, linie 165, 228) — realna optymalizacja kosztu/czasu przy powtarzających się liniach; `_clean_subtitle_text` poprawnie separuje odpowiedzialność czyszczenia tekstu od tłumaczenia; `translator_functions` (linia 331) to zalążek podejścia rejestrowego.
- **⚠️ dług techniczny / code smells:**
  - `translator.py:91-233` — ~80% duplikacji kodu między `translate_google` i `translate_deepl_api` (ta sama struktura: clean→mark→dedup→batch→translate→unmark→zip-assign), różniącej się głównie znacznikami i wywołaniem silnika.
  - `translator.py:170,177` — brak jawnego `return` w gałęzi bez `is_combined_with_gpt`, mimo deklarowanego `-> pysrt.SubRipFile`.
  - `translator.py:285-288` — bug: trzy kolejne przypisania do `sub.text` nadpisują się zamiast łańcuchować `.replace()` — pierwsze dwie linie martwe, functionally no-op.
  - `translator.py:331-334` — `translate_deepl_desktop` brakuje w rejestrze `translator_functions` — metoda nieosiągalna z `translate_srt`.
  - `translator.py:141` — `asyncio_run` (nowy event loop) wołany w pętli per-batch zamiast raz — kosztowne, niespójne z resztą kodu synchronicznego.
  - `translator.py:67-68` — pola `working_space_temp_main_subs/_alt_subs` w dataclass są martwe (żadna metoda ich nie czyta — wszystkie tłumaczące metody są `@staticmethod` z własnym `dir_path`).
  - `translator.py:336-341` — brak jawnego wyjątku/błędu przy nieznanym `translator` — cichy no-op zamiast rzucenia błędu lub logowania na poziomie ostrzeżenia krytycznego.
- **❌ niespójności ze stylem MangaShift:**
  - Brak rejestru silników w osobnym module (`services/<domena>/engines/__init__.py` w duchu MangaShift) — tu rejestr to lokalny słownik wewnątrz metody instancyjnej (linia 331), niedostępny do introspekcji z zewnątrz, nie eksportowany, nieaktualny (brakujący wpis).
  - Brak typowanego Literal dla nazw tłumaczy — `settings.translator` to goły `str` porównywany z hardkodowanymi stringami (`'Google Translate'`, `'DeepL API'`) zarówno tu, jak i w `data/settings.py` (`Config.get_translators()`), bez wspólnego źródła prawdy typów.
  - Silniki tłumaczeniowe nie implementują wspólnego interfejsu/protokołu — każda metoda ma inną sygnaturę (`translate_google` ma dodatkowy `is_combined_with_gpt`, `translate_deepl_api` ma `deepl_api_key`, `translate_deepl_desktop` nie ma żadnego z nich) — utrudnia jednolite wołanie przez rejestr bez ręcznych domknięć (stąd `_translate_google`/`_translate_deepl_api` jako adaptery w liniach 324-329).
  - Zero dependency injection — `deepl.Translator`, `googletrans.Translator`, `pyautogui` tworzone/wołane bezpośrednio wewnątrz metod, brak abstrakcji nad "silnikiem tłumaczącym", więc nie da się podmienić/mockować bez monkey-patchingu w testach.
- **🔗 sprzężenia:** z `data.settings.Settings` (pola `translator`, `deepl_api_key`, `translated_line_count`) i pośrednio z `data/config.py` (`Config.get_translators()` definiuje dostępne nazwy tłumaczy, które muszą zgadzać się z kluczami `translator_functions` — dwa miejsca prawdy, które się już rozjechały, patrz `translate_deepl_desktop`). Zależność od zewnętrznych bibliotek trzecich stron bez warstwy abstrakcji (`googletrans` to nieoficjalne, niestabilne API Google — całe ryzyko wycieka bezpośrednio do klasy domenowej).

---

## 📄 plik: `modules/style_classifier.py` (295 linii)

### przeznaczenie
Samodzielny moduł heurystycznej klasyfikacji stylów ASS na `DIALOG`/`SIGN`/`UNCERTAIN`
dla trybu automatycznego podziału napisów. Nie zależy od reszty `modules/` (poza
typowaniem `SSAFile`/`SSAEvent` z `pysubs2` pod `TYPE_CHECKING`) — wołany wyłącznie
przez `subtitle.py:186` (lazy-import) i bezpośrednio w testach
(`tests/style_classifier_test.py`). Kluczowy mechanizm: deduplikacja animacji
(powtarzającego się tekstu w krótkim oknie czasowym) przed liczeniem metryk per styl.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `from __future__ import annotations` | stdlib | leniwe adnotacje typów, pozwala używać `list[...]`/`tuple[...]` bez importu z `typing` w runtime |
| `re` | stdlib | regexy sygnatur tagów ASS i nazw stylów |
| `defaultdict` | collections | akumulacja metryk per styl i grupowanie zdarzeń przy deduplikacji |
| `dataclass` | dataclasses | dekorator `StyleVerdict`, `_StyleMetrics` |
| `Enum` | enum | `Category` |
| `TYPE_CHECKING, Final` | typing | `TYPE_CHECKING` do importu tylko dla type-checkerów; `Final` na stałych modułowych |
| `SSAEvent, SSAFile` | pysubs2 (pod `TYPE_CHECKING`) | wyłącznie adnotacje typów, nie importowane w runtime |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `_BACKSLASH` | 37 | `Final[str]` | `chr(92)` — literalny backslash, ten sam trik co w `subtitle.py:53` |
| `_RE_DRAW` | 38 | `Final[re.Pattern[str]]` | `\\p[1-9]` — tag rysowania wektorowego |
| `_RE_POS` | 39-41 | `Final[re.Pattern[str]]` | `\\(pos\|move\|clip\|frz\|fad\|org\|t\()` — tagi pozycjonowania/animacji |
| `_RE_KARA` | 42 | `Final[re.Pattern[str]]` | `\\[kK][fo]?[0-9]` — tagi karaoke |
| `_RE_PUNCT` | 43 | `Final[re.Pattern[str]]` | `[.!?…»"]` — interpunkcja zdaniowa (sygnał dialogu) |
| `_RE_SONG` | 46-48 | `Final[re.Pattern[str]]` | regex (case-insensitive) nazw stylów sugerujących piosenkę/OP/ED |
| `_RE_NOTE` | 49-51 | `Final[re.Pattern[str]]` | regex nazw stylów sugerujących notki/przypisy/creditsy |
| `_RE_SIGN` | 52-54 | `Final[re.Pattern[str]]` | regex nazw stylów sugerujących on-screen sign/tytuł/rozdział |
| `_RE_DLG` | 55-57 | `Final[re.Pattern[str]]` | regex nazw stylów sugerujących dialog/narrację/myśli |
| `_DEDUP_MIN_REPEAT` | 60 | `Final[int]` | `5` — min. liczba powtórzeń identycznego tekstu, by uznać za animację |
| `_DEDUP_WINDOW_MS` | 63 | `Final[int]` | `2000` — mediana odstępu (ms) poniżej której powtórzenia uznaje się za "gęste w czasie" (animacja) |
| `_DRAW_SIGN_RATIO` | 67 | `Final[float]` | `0.30` — próg udziału linii rysunkowych, powyżej którego styl to SIGN |
| `_KARA_SONG_RATIO` | 70 | `Final[float]` | `0.30` — próg udziału linii karaoke, powyżej którego styl to SONG/SIGN |
| `_DLG_MAX_POS_RATIO` | 73 | `Final[float]` | `0.50` — maks. udział pozycjonowania dla "pewnego" skrótu DIALOG po nazwie stylu |
| `_SCORE_DIALOG` | 76 | `Final[float]` | `0.55` — próg wyniku ważonego, od którego styl to DIALOG |
| `_SCORE_SIGN` | 79 | `Final[float]` | `0.25` — próg wyniku ważonego, poniżej/równo którego styl to SIGN |

### klasy

#### `class Category(Enum)` (linia 83)
**Cel:** enumeruje trzy możliwe werdykty klasyfikacji stylu.
**Wartości:**
| wartość | linia | cel |
|---------|-------|-----|
| `DIALOG` | 86 | mowa/narracja/myśli — czytane przez lektora |
| `SIGN` | 89 | on-screen sign/piosenka/notka — pomijane |
| `UNCERTAIN` | 92 | heurystyka niepewna — do dry-run/decyzji użytkownika |

#### `class StyleVerdict` (linia 96) — `@dataclass(slots=True, frozen=True)`
**Cel:** niemutowalny wynik klasyfikacji pojedynczego stylu.
**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `style` | `str` | — | nazwa stylu ASS |
| `category` | `Category` | — | przypisana kategoria |
| `confidence` | `float` | — | pewność 0.0-1.0 |
| `line_count` | `int` | — | liczba linii po deduplikacji animacji |
| `raw_line_count` | `int` | — | liczba linii przed deduplikacją |

#### `class _StyleMetrics` (linia 115) — `@dataclass(slots=True)`
**Cel:** wewnętrzny akumulator metryk per styl podczas przetwarzania (mutowalny, prywatny — prefiks `_`).
**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `n` | `int` | `0` | liczba linii po deduplikacji |
| `raw_n` | `int` | `0` | liczba linii przed deduplikacją |
| `pos` | `int` | `0` | liczba linii z tagami pozycjonowania/animacji |
| `draw` | `int` | `0` | liczba linii z tagami rysowania wektorowego |
| `kara` | `int` | `0` | liczba linii z tagami karaoke |
| `punct` | `int` | `0` | liczba linii z interpunkcją zdaniową |
| `txt` | `int` | `0` | suma długości czystego tekstu (znaki) |

### funkcje modułowe

##### `dedup_animation(events: list[SSAEvent]) -> tuple[list[SSAEvent], int]` (linia 138)
- **Co robi:** Grupuje zdarzenia wg klucza `(style, plaintext)`; jeśli grupa ma ≥`_DEDUP_MIN_REPEAT` wystąpień identycznego tekstu i mediana odstępu czasowego między nimi < `_DEDUP_WINDOW_MS`, zostawia tylko jedno (najwcześniejsze) wystąpienie jako reprezentanta animacji. W przeciwnym razie zachowuje wszystkie (zwykłe powtórzenia dialogowe, np. "CO?!" powiedziane 3 razy w różnych momentach).
- **Przyjmuje:** `events` — lista zdarzeń Dialogue z pliku ASS.
- **Zwraca:** krotkę `(keep, removed)` — lista zachowanych zdarzeń i liczba usuniętych jako duplikaty animacji.
- **Efekty uboczne:** brak (czysta funkcja).
- **Woła:** `defaultdict(list)`, sortowanie (`sorted`), obliczenie mediany różnic czasowych ręcznie (linie 161-162, bez `statistics.median`).
- **Wyjątki:** brak.
- **Uwagi:** mediana liczona ręcznie przez `sorted(diffs)[len(diffs)//2]` zamiast `statistics.median` — działa poprawnie dla nieparzystej/parzystej liczby elementów w sensie "dolnej mediany", drobne odejście od biblioteki standardowej bez wyraźnego powodu (mikro-code-smell, nie bug).

##### `_classify_metrics(metrics: _StyleMetrics, style: str, total: int) -> tuple[Category, float]` (linia 171)
- **Co robi:** Klasyfikuje pojedynczy styl na podstawie zebranych metryk — najpierw twarde reguły SIGN (dużo rysunku/karaoke, nazwa sugeruje piosenkę/notkę), potem skrót "pewny dialog" (nazwa dialogowa + mało pozycjonowania + brak rysunku), na końcu ważone punktowanie (frac/pos/punct/avg/nazwa) porównywane z progami `_SCORE_DIALOG`/`_SCORE_SIGN`.
- **Przyjmuje:** `metrics` — akumulator dla stylu; `style` — nazwa (do reguł nazwowych); `total` — łączna liczba zdeduplikowanych linii w pliku (do liczenia `frac`, udziału stylu).
- **Zwraca:** krotkę `(Category, confidence: float)`.
- **Efekty uboczne:** brak (czysta funkcja).
- **Woła:** regexy modułowe (`_RE_SONG.search`, `_RE_NOTE.search`, `_RE_DLG.search`, `_RE_SIGN.search`), `round`, `min`.
- **Wyjątki:** brak jawnej, ale **dzieli przez `n`** w linii 183 (`metrics.pos / n` itd.) bez sprawdzenia `n == 0` — jeśli wywołane z `metrics.n == 0`, rzuci `ZeroDivisionError`. Wywołujący (`classify_styles`, linia 262) chroni przed tym przez `if entry.n == 0: continue` tuż przed wywołaniem — więc w praktyce bezpieczne, ale funkcja sama w sobie nie jest odporna na błędne użycie (niejawny kontrakt wymagający `n > 0`).
- **Uwagi:** logika progowa (magic numbers 0.20/0.40/0.30/12/0.15/-0.25/-0.30) jest w pełni wyjaśniona nazwanymi stałymi modułowymi tylko częściowo — część progów w scoringu ważonym (linie 202-215: `0.20`, `0.40`, `0.30`, `12`, `0.15`, `-0.25`, `-0.30`) jest **wpisana bezpośrednio jako literały w ciele funkcji**, bez odpowiadających stałych `Final` — niespójne względem reguł twardych (`_DRAW_SIGN_RATIO` itd.), które są wyekstrahowane. To rozwadnia "jedno źródło prawdy dla progów" wewnątrz tego samego pliku.

##### `classify_styles(subs: SSAFile) -> list[StyleVerdict]` (linia 224)
- **Co robi:** Punkt wejścia klasyfikacji całego pliku — filtruje zdarzenia typu `Dialogue`, deduplikuje animację, liczy metryki per styl (surowe i zdeduplikowane), klasyfikuje każdy styl przez `_classify_metrics`, zwraca posortowaną (malejąco wg `line_count`) listę werdyktów.
- **Przyjmuje:** `subs` — załadowany `SSAFile` (pysubs2).
- **Zwraca:** `list[StyleVerdict]`, pusta lista jeśli brak zdarzeń Dialogue.
- **Efekty uboczne:** brak (czysta funkcja, nie mutuje `subs`).
- **Woła:** `dedup_animation`, `defaultdict(_StyleMetrics)`, regexy modułowe (`_RE_POS`, `_RE_DRAW`, `_RE_KARA`, `_RE_PUNCT`), `_classify_metrics`, `sorted`.
- **Wyjątki:** brak jawnej obsługi (choć wejście jest zaufane — `SSAFile` z pysubs2 ma gwarantowaną strukturę).
- **Uwagi:** to jest **jedyny publiczny punkt wejścia realnie wołany produkcyjnie** (przez `subtitle.py:191`); dobrze udokumentowany docstringiem z przykładem użycia (linie 225-235, spójny ze stylem modułu).

##### `select_dialog_styles(subs: SSAFile) -> list[str]` (linia 277)
- **Co robi:** Wygodny skrót zwracający tylko nazwy stylów DIALOG+UNCERTAIN (te same kryteria co `_auto_select_styles` w `subtitle.py`).
- **Przyjmuje:** `subs`.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `classify_styles(subs)`.
- **Wyjątki:** brak.
- **Uwagi:** ⚠️ **martwy kod / zduplikowana logika** — funkcja nie jest wołana przez `subtitle.py`, który **duplikuje** dokładnie tę samą logikę selekcji (`DIALOG`+`UNCERTAIN`) ręcznie inline w `_auto_select_styles` (`subtitle.py:197`: `read = v.category in (Category.DIALOG, Category.UNCERTAIN)`) zamiast wołać `select_dialog_styles`. Funkcja istnieje wyłącznie jako publiczne API modułu (deklarowana w docstringu modułu jako wzorcowy przykład użycia, linia 20), ale w rzeczywistym potoku jest martwa — jedyny konsument to prawdopodobnie testy/przyszli użytkownicy zewnętrzni tego modułu.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** najlepszy plik w obszarze pod względem stylu — `@dataclass(slots=True, frozen=True)` dla wyniku (`StyleVerdict`), stałe modułowe z `Final` i opisowymi docstringami "atrybutowymi" (linie 61-80), separacja czystych funkcji bez efektów ubocznych, `from __future__ import annotations` + `TYPE_CHECKING` dla lekkiego importu, walidowany heurystyką opisaną w nagłówku modułu (206 plików, ~99% zgodności — deklaracja weryfikacji empirycznej). To jedyny plik obszaru, który wygląda na pisany współcześnie wg dojrzalszych konwencji niż reszta `modules/`.
- **⚠️ dług techniczny / code smells:**
  - `style_classifier.py:183` — `_classify_metrics` dzieli przez `n` bez ochrony przed `n == 0`; bezpieczne dziś tylko dzięki guardowi u wywołującego (`classify_styles:262`), ale funkcja nie jest samoobronna — ukryty kontrakt.
  - `style_classifier.py:202-215` — część progów scoringu ważonego to nienazwane literały (`0.20`, `0.40`, `12` itd.) obok w pełni nazwanych stałych `Final` dla reguł twardych — niespójne wewnątrz jednego pliku.
  - `style_classifier.py:277-294` (`select_dialog_styles`) — martwy kod względem realnego potoku; `subtitle.py` duplikuje jej logikę inline zamiast go wywołać.
  - `style_classifier.py:161-162` — ręczne liczenie mediany zamiast `statistics.median`.
- **❌ niespójności ze stylem MangaShift:**
  - Brak dependency injection nie dotyczy tego pliku bezpośrednio (moduł jest bezstanowy/funkcyjny), ale progi klasyfikacji (`_SCORE_DIALOG`, `_DEDUP_MIN_REPEAT` itd.) są zahardkodowane na poziomie modułu bez mechanizmu konfiguracji/rejestru — w duchu MangaShift byłyby to np. wartości w jednym miejscu prawdy z możliwością nadpisania per-profil (nie ma potrzeby tego zmieniać teraz, ale brak jakiejkolwiek warstwy konfiguracji to różnica filozoficzna).
  - `Category` jako `Enum` (nie `Literal` + rejestr) — spójne wewnętrznie, ale nie łączy się z żadnym systemem typów współdzielonym z resztą projektu (np. nie ma odpowiednika w `data/settings.py`/`data/config.py`, gdzie tłumacze/TTS są zwykłymi stringami) — czyli sam plik jest dobry, ale nie podnosi całego projektu do wspólnego wzorca.
- **🔗 sprzężenia:** minimalne i jednokierunkowe — zależy tylko od typów `pysubs2` (pod `TYPE_CHECKING`, więc nawet nie w runtime). Jedyny konsument w kodzie produkcyjnym to `subtitle.py:186-191` przez lazy-import. Zmiana sygnatury `classify_styles`/`StyleVerdict` złamie `subtitle.py:_auto_select_styles` (odczytuje `v.category`, `v.style`, `v.confidence`, `v.line_count`, `v.raw_line_count` — wszystkie pola `StyleVerdict`) oraz `tests/style_classifier_test.py`.

---

## 🧭 podsumowanie obszaru

- **Główne odpowiedzialności:** podział ASS na tor dialog/sign (ręczny + automatyczny przez
  heurystykę), konwersje formatów napisów (ASS↔SRT↔TXT), tłumaczenie SRT trzema silnikami
  (Google/DeepL API/DeepL desktop) i scalenie przetłumaczonych linii z powrotem do ASS po
  znaczniku czasowym.

- **Największe problemy (ranking):**
  1. **Bug funkcjonalny w `translator.py:285-288`** — trzy kolejne przypisania do `sub.text`
     w `translate_deepl_desktop` nadpisują się zamiast łańcuchować `.replace()`; efektywnie
     tylko ostatni `.replace(" ◍◍◍◍", "")` ma znaczenie, znaczniki newline/przecinek nigdy
     nie są prawidłowo odtwarzane w tym silniku.
  2. **`translate_deepl_desktop` nieosiągalna z `translate_srt`** (`translator.py:331-334`) —
     rejestr `translator_functions` nie ma dla niej wpisu; w pełni zaimplementowana metoda
     jest martwa z perspektywy realnego przepływu sterowanego przez `Settings`.
  3. **Duplikacja logiki tłumaczenia ~80%** między `translate_google` i `translate_deepl_api`
     (`translator.py:91-233`) — dwa niemal identyczne bloki różniące się głównie znacznikami
     i wywołaniem API; brak wspólnej abstrakcji "silnika tłumaczącego".
  4. **Duplikacja kopiowania metadanych/stylów** w `subtitle.py` między
     `_copy_metadata_and_styles` (240-257) i `_save_subs` (268-281) — ta sama praca wykonana
     dwukrotnie w `split_ass`.
  5. **Błąd w definicji dataclass** `subtitle.py:86-87` — pola bez adnotacji typu w
     `@dataclass(slots=True)` po cichu nie stają się polami instancji.
  6. Brak jakiejkolwiek wspólnej abstrakcji/interfejsu dla "silnika tłumaczącego" — utrudnia
     dodanie nowego dostawcy tłumaczeń bez kopiowania całej logiki deduplikacji/batchowania.

- **Kandydaci do refaktoru na styl MangaShift:**
  - `translator.py` — wydzielić rejestr silników tłumaczeniowych (moduł `engines/__init__.py`
    w duchu MangaShift) z jednolitym interfejsem `translate(text_batch) -> list[str]`;
    wspólną logikę deduplikacji/batchowania/markerów przenieść do jednej funkcji fasadowej
    przyjmującej silnik jako zależność (DI), eliminując duplikat Google/DeepL.
  - `subtitle.py` — `SubtitleRefactor.split_ass` rozbić na strategię wyboru stylów
    (ręczna/automatyczna) jako osobne, wymienne obiekty zamiast `if auto_mode`; usunąć
    duplikat `_copy_metadata_and_styles`/`_save_subs`.
  - `style_classifier.py` — najbliżej stylu docelowego już dziś (dataclass+slots+frozen,
    stałe `Final`, czyste funkcje); do dociągnięcia: dokończyć ekstrakcję progów scoringu do
    nazwanych stałych, dodać guard na `n == 0` w `_classify_metrics`.
  - Cały obszar: brak wspólnego, typowanego Literal dla nazw tłumaczy/silników współdzielonego
    między `translator.py` i `data/settings.py`/`data/config.py` — dziś to gołe stringi
    porównywane w kilku miejscach niezależnie, klasyczny przypadek "jednego pytania z wieloma
    odpowiedziami" zamiast jednego źródła prawdy.

- **Pliki/funkcje martwe lub podejrzane:**
  - `style_classifier.py:277` `select_dialog_styles` — nieużywana w kodzie produkcyjnym,
    logika duplikowana ręcznie w `subtitle.py:_auto_select_styles`.
  - `translator.py:238` `translate_deepl_desktop` — nieosiągalna z `translate_srt` (brak
    wpisu w rejestrze `translator_functions`), efektywnie martwa mimo pełnej implementacji.
  - `translator.py:67-68` pola `working_space_temp_main_subs`/`_alt_subs` w
    `SubtitleTranslator` — zadeklarowane w dataclass, nigdy nieużywane przez żadną metodę.
  - `subtitle.py:171` parametr `styles` w `_auto_select_styles` — przyjmowany, nigdy
    nieużywany w ciele metody.
  - `tests/translator-gpt-no-re-ask_alt.py`, `tests/translator-gpt-re-ask_alt.py` — poza
    przydzielonym zakresem audytu, ale grep pokazał odwołania do `SubtitleTranslator.translate_chat_gpt`/`translate_google_gpt`, których **nie ma** w obecnym `modules/translator.py` — sugeruje to nieaktualne/eksperymentalne testy wobec zastanego stanu modułu (wart odnotowania dla zespołu, spoza zakresu tego raportu).

---


# CZĘŚĆ 04 — modules: TTS

# RAPORT AUDYTU — modules: TTS (synteza mowy / lektor)

---

## 📦 obszar: TTS (synteza mowy / lektor) — pliki: `modules/subtitle_to_speech.py`, `modules/tts_elevenbytes.py`

**Rola obszaru w projekcie:** ten obszar zamienia napisy (SRT/ASS po refaktorze/tłumaczeniu)
na ścieżkę audio lektora. `subtitle_to_speech.py` to fasada wywoływana z `start.py`
(`generate_audio_files` → `SubtitleToSpeech(filename).generate_audio(settings)`) — dispatchuje do
jednego z 5 silników TTS (Harpo/pyttsx3, Balabolka, Edge online x2 głosy, ElevenBytes v6/v7),
generuje WAV zsynchronizowany z timingiem napisów, opcjonalnie post-processuje (atempo/volume
przez FFmpeg) i na końcu miksuje ścieżkę lektora z istniejącą ścieżką audio (`merge_tts_audio`)
do formatu EAC3 gotowego do wgrania z powrotem do MKV. `tts_elevenbytes.py` to samodzielna
biblioteka klienta HTTP do prywatnego proxy ElevenLabs (`teamsp.org/xi/run6.php` / `run7.php`),
używana wyłącznie przez `srt_to_wav_elevenbytes` w pierwszym pliku.

**Zależności zewnętrzne obszaru:** `pyttsx3` (silnik Harpo/SAPI), `pysrt` (parsowanie SRT),
`edge_tts.Communicate` (Microsoft Edge TTS online), `pydub.AudioSegment`/`mediainfo` (dekodowanie
mp3, długość plików), `httpx.AsyncClient` (ElevenBytes), `soundfile`, `numpy`, `scipy.signal`
(resampling PCM w ścieżce ElevenBytes), FFmpeg (subprocess `call`/`subprocess_run`) do atempo/
volume/mix/eac3-encode, `natsort`, `async_timeout`. Wewnętrznie: `constants` (ścieżki working_space,
`BALABOLKA_PATH`, `FFMPEG_PATH`, `console`), `data.settings.Settings` (konfiguracja TTS
wybrana przez usera w CLI), `modules.tts_elevenbytes.TTS`/`VoiceSettings` (import lokalny wewnątrz
`srt_to_wav_elevenbytes`).

---

## 📄 plik: `modules/subtitle_to_speech.py` (1196 linii)

### przeznaczenie
Jedyna klasa `SubtitleToSpeech` (dataclass ze slots) obsługująca cały krok "napisy → audio
lektora" w potoku CLI. Wywoływana przez `start.py:477` per plik napisów. Jedna instancja =
jeden plik SRT. Zawiera 5 alternatywnych ścieżek syntezy (per silnik TTS), wspólną logikę
post-processingu prędkości/głośności (FFmpeg atempo), oraz logikę mergowania finalnego audio
lektora z istniejącą ścieżką dźwiękową w EAC3.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `dataclass` | dataclasses | dekorator klasy `SubtitleToSpeech` |
| `listdir, path, remove, stat` | os | operacje na plikach/katalogach |
| `call, subprocess_run as PIPE` | subprocess | odpalanie FFmpeg (blokujące) |
| `Thread` | threading | równoległe odtwarzanie Balabolki i parsowania napisów |
| `sleep` | time | throttling w `process_subtitle` (Balabolka) |
| `sys` | stdlib | wykrycie win32, `sys.stdout.reconfigure` |
| `wave` | stdlib | ręczne pisanie/czytanie nagłówków WAV PCM |
| `Dict, List, Optional` | typing | adnotacje typów (styl mieszany — część kodu ma `str \| None`) |
| `pyttsx3` | pyttsx3 | silnik Harpo (offline SAPI) |
| `pysrt` | pysrt | parsowanie plików `.srt` |
| `Communicate` | edge_tts | silnik Edge (online, streaming mp3) |
| `AudioSegment` | pydub | dekodowanie mp3 → raw PCM (Edge) |
| `mediainfo` | pydub.utils | odczyt długości pliku (ffprobe wrapper) |
| `WORKING_SPACE*`, `BALABOLKA_PATH`, `FFMPEG_PATH`, `console` | constants | ścieżki i globalny obiekt konsoli rich |
| `Settings` | data.settings | typ configu przekazywany do `generate_audio` |
| `create_task, gather, run, Semaphore, sleep as asyncio_sleep, TimeoutError` | asyncio | async batch syntezy Edge |
| `timeout as timeout_scope` | async_timeout | timeout per-request Edge |
| `natsorted` | natsort | sortowanie plików mp3 wg numeru naturalnego |
| lokalny `import re, sys, time as _time, Path as _Path, numpy as np` (413+) | wewn. `srt_to_wav_elevenbytes` | czyszczenie tekstu, ścieżki, czas, tablice PCM |
| `TTS as ElevenBytesTTS, VoiceSettings` | modules.tts_elevenbytes | lokalny import wewnątrz `srt_to_wav_elevenbytes` |
| `soundfile as sf` | wewn. import w `srt_to_wav_elevenbytes` (l.646) | dekodowanie mp3 → int16 PCM bez ffmpeg |
| `ThreadPoolExecutor, as_completed`, `threading` | wewn. import (l.527-528) | równoległa synteza ElevenBytes |
| `resample_poly`, `Fraction` | wewn. import w `_decode_mp3` | resampling gdy sample rate ≠ 44100 |
| `shutil as _shutil` | wewn. import (l.739) | czyszczenie cache mp3 po sukcesie |
| `os` (ponowny import, l.727) | wewn. import w `srt_to_wav_elevenbytes` | usunięcie pliku `.pcm` — duplikat już zaimportowanego `os.path/remove` |

### stałe / zmienne modułowe
Brak stałych na poziomie modułu — wszystkie "stałe" (np. `ELEVENBYTES_SAMPLE_RATE`,
`HARD_TIMEOUT_S`, `CONCURRENCY`, `INLINE_RETRIES`, `MASS_FAIL_RATIO`) są zdefiniowane lokalnie
wewnątrz metody `srt_to_wav_elevenbytes` (linie 440-441, 534-540) — patrz sekcja diagnozy
(magic values zamknięte w metodzie zamiast na poziomie modułu/klasy).

### klasy

#### `class SubtitleToSpeech` (linia 61) — `@dataclass(slots=True)`, nie dziedziczy
**Cel:** fasada + implementacja wszystkich silników TTS dla jednego pliku napisów.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `filename` | `str` | — (wymagane) | nazwa pliku SRT w `working_space_temp_main_subs` do przetworzenia |
| `working_space` | `str` | `WORKING_SPACE` | katalog roboczy (nieużywany bezpośrednio w metodach poza referencją) |
| `working_space_output` | `str` | `WORKING_SPACE_OUTPUT` | katalog docelowy plików `.eac3` |
| `working_space_temp` | `str` | `WORKING_SPACE_TEMP` | katalog tymczasowy (istniejąca ścieżka audio do zmiksowania) |
| `working_space_temp_main_subs` | `str` | `WORKING_SPACE_TEMP_MAIN_SUBS` | katalog z plikami napisów głównych i wygenerowanym audio |
| `working_space_temp_alt_subs` | `str` | `WORKING_SPACE_TEMP_ALT_SUBS` | zadeklarowane pole, **nieużywane w żadnej metodzie pliku** |
| `balabolka_path` | `str` | `BALABOLKA_PATH` | ścieżka do `balcon.exe` |
| `ffmpeg_path` | `str` | `FFMPEG_PATH` | ścieżka do `ffmpeg.exe`, używana w ~10 miejscach |
| `_pp_speed` | `float` | `1.0` | mnożnik prędkości post-processingu (atempo), ustawiany w `generate_audio` z `settings.pp_speed` |

**Metody:**

##### `ansi_srt(self) -> None` (linia 105)
- **Co robi:** wczytuje plik SRT (UTF-8, fallback ANSI przy `UnicodeDecodeError`) i nadpisuje go w kodowaniu ANSI (`errors="ignore"`) — wymagane przez silniki Harpo/Balabolka działające na Windows SAPI.
- **Przyjmuje:** brak argumentów poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** nadpisuje plik `self.filename` w `working_space_temp_main_subs` (transkodowanie in-place, nieodwracalne — nie ma kopii oryginału); drukuje przez `console.print`.
- **Woła:** brak wywołań innych metod.
- **Wyjątki:** `UnicodeDecodeError` łapany jawnie; inne błędy IO (np. plik nie istnieje) propagują się.
- **Uwagi:** wołana bezwarunkowo przez 3 z 5 silników (Harpo, Balabolka, Edge, ElevenBytes) nawet gdy silnik i tak nie potrzebuje ANSI (Edge/ElevenBytes czyta tekst z `pysrt`, który już go zdekodował) — utrata polskich znaków w pliku źródłowym dla silników online jest zbędnym efektem ubocznym, bo `errors="ignore"` może wyciąć diakrytyki.

##### `srt_to_wav_harpo(self, tts_speed: str, tts_volume: str) -> None` (linia 126)
- **Co robi:** orkiestruje pełną ścieżkę Harpo: ANSI-konwersja → inicjalizacja silnika pyttsx3 → parsowanie SRT → generowanie WAV → sprzątanie pliku tymczasowego.
- **Przyjmuje:** `tts_speed` (rate SAPI), `tts_volume` (0.0-1.0).
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy `<filename>.wav` w `working_space_temp_main_subs`; usuwa `working_space_temp/temp.wav`.
- **Woła:** `self.ansi_srt()`, `self._init_engine()`, `self._generate_wav_file()`.
- **Wyjątki:** `FileNotFoundError` z `remove()` jeśli `temp.wav` nie powstał (np. pusty plik napisów — choć guard `_subtitle_is_empty` w `generate_audio` powinien to wyłapać wcześniej).
- **Uwagi:** brak.

##### `_init_engine(self, tts_speed: str, tts_volume: str) -> pyttsx3.Engine` (linia 143)
- **Co robi:** tworzy silnik pyttsx3, szuka głosu `'Vocalizer Expressive Zosia Harpo 22kHz'` po nazwie i go ustawia; ustawia rate/volume.
- **Przyjmuje:** `tts_speed` (rzutowane na `int`), `tts_volume` (rzutowane na `float`).
- **Zwraca:** zainicjalizowany `pyttsx3.Engine`.
- **Efekty uboczne:** brak poza stanem silnika.
- **Woła:** `pyttsx3.init()`.
- **Wyjątki:** `ValueError` przy nieparsowalnym `tts_speed`/`tts_volume`.
- **Uwagi:** nazwa głosu zahardkodowana (`plik:157`) — wymaga zainstalowanego konkretnego głosu SAPI na maszynie; brak obsługi przypadku "głos nie znaleziony" (silnik po prostu zostaje na domyślnym głosie bez ostrzeżenia).

##### `_generate_wav_file(self, engine, subtitles, output_file) -> None` (linia 163)
- **Co robi:** dla każdego napisu syntetyzuje audio do pliku tymczasowego, opcjonalnie stosuje atempo (`_pp_speed`), dopełnia ciszą do właściwego czasu startu i dopisuje ramki do wynikowego WAV.
- **Przyjmuje:** `engine` (pyttsx3), `subtitles` (`pysrt.SubRipFile`), `output_file` (ścieżka WAV).
- **Zwraca:** `None`.
- **Efekty uboczne:** otwiera/zapisuje `output_file` w trybie `wb`; drukuje przez `print()` (nie `console.print` — niespójny kanał logowania) każdy napis w formacie SRT.
- **Woła:** `self._save_subtitle_to_wav()`, `self._pp_speed_file()`, `self._add_empty_frame_if_needed()`, `self._add_subtitle_to_wav()`.
- **Wyjątki:** propaguje błędy `wave`/`pyttsx3`.
- **Uwagi:** hardkody formatu audio: mono, 16-bit, 22500 Hz (`plik:173-175`) — niezgodne z rzeczywistym `22kHz` głosu z nazwy (22500 vs 22050), drobna niespójność nazw/wartości.

##### `_save_subtitle_to_wav(self, engine, text: str) -> None` (linia 187)
- **Co robi:** syntetyzuje pojedynczy napis do stałego pliku `working_space_temp/temp.wav`.
- **Przyjmuje:** `engine`, `text`.
- **Zwraca:** `None`.
- **Efekty uboczne:** nadpisuje `temp.wav` (blokujące `engine.runAndWait()`).
- **Woła:** `engine.save_to_file`, `engine.runAndWait`.
- **Wyjątki:** brak jawnej obsługi.
- **Uwagi:** stała nazwa pliku `"temp.wav"` — nie thread-safe, ale metoda jest wołana sekwencyjnie w pętli, więc OK w obecnym użyciu.

##### `_add_empty_frame_if_needed(self, wav_file, start_time: float) -> None` (linia 199)
- **Co robi:** wstawia ciszę (zera) do WAV jeśli czas startu napisu jest późniejszy niż aktualna długość nagranego audio — synchronizacja timeline.
- **Przyjmuje:** otwarty `wave.Wave_write`, `start_time` w sekundach.
- **Zwraca:** `None`.
- **Efekty uboczne:** `wav_file.writeframes()`.
- **Woła:** brak.
- **Wyjątki:** brak.
- **Uwagi:** zakłada mono 16-bit (`* 2` bajty/próbkę) — hardkod powielony w kilku miejscach pliku (`plik:213`, analogicznie w ElevenBytes flow `plik:707`).

##### `_add_subtitle_to_wav(self, wav_file) -> None` (linia 216)
- **Co robi:** dogrywa zawartość `temp.wav` do głównego pliku WAV.
- **Przyjmuje:** otwarty `wave.Wave_write`.
- **Zwraca:** `None`.
- **Efekty uboczne:** czyta `working_space_temp/temp.wav`.
- **Woła:** brak.
- **Wyjątki:** `FileNotFoundError` jeśli `temp.wav` nie istnieje.
- **Uwagi:** brak.

##### `srt_to_wav_balabolka(self, tts_speed: str, tts_volume: str) -> None` (linia 227)
- **Co robi:** uruchamia zewnętrzny proces `balcon.exe` w osobnym wątku (generuje cały WAV naraz), równolegle "odgrywa" log konsoli przez `process_subtitle` per napis, czeka na zakończenie wątku, opcjonalnie stosuje per-napisowy atempo na już gotowym WAV.
- **Przyjmuje:** `tts_speed`, `tts_volume`.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy `<filename>.wav`; odpala proces zewnętrzny przez `Thread(target=call, ...)`.
- **Woła:** `self.ansi_srt()`, `self._prepare_balabolka_command()`, `self.process_subtitle()` (w pętli), `self._pp_speed_whole_wav()`.
- **Wyjątki:** brak jawnej obsługi błędu procesu (`call()` zwraca kod wyjścia, ale jest ignorowany).
- **Uwagi:** `command_thread` służy tylko do "nieblokującego" odpalenia procesu, ale zaraz potem kod robi `command_thread.join()` po pętli — czyli i tak czeka synchronicznie; równoległość z pętlą `process_subtitle` (samym printem+`sleep(0.02)`) to czysto kosmetyczny "live log", nie realna równoległość obliczeniowa.

##### `_prepare_balabolka_command(self, balcon_path, file_path, output_wav_path, tts_speed, tts_volume) -> List[str]` (linia 258)
- **Co robi:** buduje listę argumentów CLI dla `balcon.exe`.
- **Zwraca:** listę stringów (argv).
- **Efekty uboczne:** brak.
- **Woła:** brak.
- **Uwagi:** głos `"IVONA 2 Agnieszka"` zahardkodowany (`plik:277`); `"-fr", "48"` (framerate) też hardkod niezależny od realnego `framerate` używanego gdzie indziej (24000/22500/44100 w innych ścieżkach) — brak jednego źródła prawdy dla sample rate.

##### `process_subtitle(self, subtitle: pysrt.SubRipItem) -> None` (linia 282)
- **Co robi:** drukuje pojedynczy napis w formacie SRT-like i śpi 20 ms (throttling wizualny logu).
- **Zwraca:** `None`.
- **Efekty uboczne:** `print()`, `sleep(0.02)`.
- **Woła:** brak.
- **Uwagi:** publiczna metoda (brak `_` prefixu) mimo że to czysto pomocnicza funkcja logowania — niespójna konwencja nazewnictwa prywatności względem reszty klasy.

##### `async generate_speech(self, subtitle, voice: str, output_file: str, rate: str, volume: str) -> None` (linia 296)
- **Co robi:** woła `edge_tts.Communicate` i strumieniuje chunk'i audio do pliku mp3.
- **Zwraca:** `None`.
- **Efekty uboczne:** zapisuje `output_file`.
- **Woła:** `Communicate(...).stream()`.
- **Wyjątki:** propaguje błędy sieciowe `edge_tts`.
- **Uwagi:** brak walidacji pustego tekstu (choć wołający filtruje wyżej pośrednio przez pętlę po wszystkich napisach, nie po `len(text)>=N`, w przeciwieństwie do ElevenBytes flow).

##### `async generate_wav_files(self, subtitles, voice: str, rate: str, volume: str) -> List[str]` (linia 314)
- **Co robi:** generuje pliki mp3 dla wszystkich napisów równolegle (semafor=1 → de facto sekwencyjnie!), z retry (do 3 prób) i timeoutem 30s per request.
- **Przyjmuje:** `subtitles`, `voice`, `rate`, `volume`.
- **Zwraca:** listę ścieżek mp3 posortowaną `natsorted`.
- **Efekty uboczne:** tworzy N plików `<basename>_<i>.mp3`.
- **Woła:** zagnieżdżoną `generate_with_retry()` → `self.generate_speech()`.
- **Wyjątki:** re-raise po wyczerpaniu prób (`plik:348`); łapie `except (TimeoutError, Exception)` — **martwy warunek**: `TimeoutError` jest podklasą `Exception`, więc pierwszy człon krotki jest zbędny (code smell).
- **Uwagi:** zawiera zagnieżdżoną funkcję `generate_with_retry` (linia 334) — patrz niżej jako osobna funkcja lokalna. `Semaphore(1)` (`plik:331`) neguje ideę "generate_wav_files" jako batch równoległy — komentarz mówi "zmniejszam liczbę równoległych połączeń", czyli świadomy downgrade do sekwencyjnego wykonania po wcześniejszych problemach ze stabilnością Edge TTS.

###### `generate_with_retry(subtitle, output_file, max_retries: int = 3) -> None` (linia 334, zagnieżdżona w `generate_wav_files`)
- **Co robi:** owija `generate_speech` w semafor + timeout + retry z rosnącym backoffem.
- **Przyjmuje:** `subtitle`, `output_file`, `max_retries`.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy plik audio; `console.print` przy ostatecznej porażce.
- **Woła:** `self.generate_speech()`.
- **Wyjątki:** re-raise na ostatniej próbie.
- **Uwagi:** sprawdza `path.exists(output_file) and stat(output_file).st_size > 0` po sukcesie, ale w razie sukcesu **nie ma `return` przerywającego pętlę retry poprawnie widocznie** — w rzeczywistości `return` jest (`plik:341`), OK.

##### `merge_audio_files(self, mp3_files: List[str], subtitles, dir_path: str) -> None` (linia 361)
- **Co robi:** łączy listę plików mp3 (Edge) w jeden WAV zgodnie z timingiem napisów, dekodując przez pydub i wstawiając ciszę między klipami.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy `<basename>.wav`; usuwa poszczególne pliki mp3 po zużyciu.
- **Woła:** `AudioSegment.from_file()`, `self._add_empty_frame_if_needed()`.
- **Wyjątki:** propaguje błędy dekodowania pydub/ffmpeg.
- **Uwagi:** framerate WAV zahardkodowany na `24000` (`plik:374`) — inny niż Harpo (22500) i ElevenBytes (44100); brak jednego źródła prawdy dla sample rate per silnik.

##### `srt_to_wav_edge_online(self, tts: str, tts_speed: str, tts_volume: str) -> None` (linia 389)
- **Co robi:** mapuje nazwę TTS na głos Edge (`"pl-PL-ZofiaNeural"`/`"pl-PL-MarekNeural"`), odpala event loop (`asyncio.run` przez alias `run`) na `generate_wav_files`, opcjonalnie atempo per plik mp3, i mergeuje.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy finalny WAV przez `merge_audio_files`.
- **Woła:** `self.ansi_srt()`, `run(self.generate_wav_files(...))`, `self._pp_speed_file()`, `self.merge_audio_files()`.
- **Wyjątki:** propaguje błędy asyncio/sieci.
- **Uwagi:** **if-per-silnik na poziomie doboru głosu** (`plik:399`) — string-matching na etykiecie z UI (`"TTS - Zofia - Edge"`) zamiast rejestru głosów; to samo zjawisko co w `generate_audio` (dispatch). Dwie "warianty" Edge (Zofia/Marek) obsługiwane jednym silnikiem sterowanym parametrem `tts`, ale nazwa metody `srt_to_wav_edge_online` nie ujawnia że przyjmuje etykietę UI jako logikę biznesową.

##### `srt_to_wav_elevenbytes(self, tts_speed: str, tts_volume: str, elevenbytes_voice: Optional[str] = None, engine: str = "v6", settings: Optional['Settings'] = None) -> None` (linia 413)
- **Co robi:** najbardziej rozbudowana metoda pliku (~340 linii). Pełny potok: (1) buduje `VoiceSettings` z `Settings` (tylko dla `engine="v7"`), (2) tworzy `ElevenBytesTTS`, (3) czyści tekst napisów (usuwa tagi ASS `{...}`, HTML `<...>`, `\N`/`\n`), (4) sprawdza cache mp3 z poprzednich uruchomień (`_elevenbytes_cache/<idx>.mp3`), (5) syntetyzuje brakujące napisy równolegle przez `ThreadPoolExecutor` (concurrency=85) w rundach z adaptacyjnym cooldownem przy masowych awariach API, aż do skutku lub 5h timeout, (6) dekoduje wszystkie mp3 przez `soundfile` (bez ffmpeg per-chunk), resampluje do 44100 Hz jeśli trzeba, (7) opcjonalnie stosuje atempo równolegle per-chunk, (8) składa surowy PCM z ciszą wg timingu napisów, (9) konwertuje PCM→WAV przez FFmpeg z `-rf64 auto` (obsługa plików >4GB), (10) sprząta cache i plik `.pcm`, (11) zamyka klienta TTS, (12) drukuje podsumowanie.
- **Przyjmuje:** `tts_speed`, `tts_volume` (oba **nieużywane** — deklarowane "for interface consistency", ElevenLabs generuje w naturalnym tempie/głośności), `elevenbytes_voice` (alias lub surowe voice_id), `engine` (`"v6"`/`"v7"`), `settings` (obiekt `Settings`, czytany tylko dla v3 voice_settings).
- **Zwraca:** `None`.
- **Efekty uboczne:** MASA — tworzy katalog cache, pliki mp3, plik `.pcm`, finalny `.wav`; wielokrotne `print`/`console.print`; sieciowe wywołania HTTP przez `tts.synthesize_sync`; odpala FFmpeg dwukrotnie (per-chunk atempo + finalna konwersja PCM→WAV); usuwa katalog cache na końcu.
- **Woła:** `self.ansi_srt()`, `ElevenBytesTTS(...)`, `tts.synthesize_sync()` (przez lokalną `_synth_one`), `self._build_atempo_chain()`, `self._decode_mp3()`/`_atempo_pipe()` (funkcje lokalne), `tts.close_sync()`.
- **Wyjątki:** łapie `Exception` w kilku miejscach (`_synth_one`, dekodowanie mp3, sprzątanie plików) i degraduje do "fail"/pomija — nigdy nie rzuca dalej poza `HARD_TIMEOUT_S` (który tylko przerywa pętlę `while pending`, nie rzuca wyjątku — funkcja kończy się "cicho" nawet przy niepełnym pokryciu, tylko drukując żółte ostrzeżenie).
- **Uwagi:**
  - **God-method** — 340 linii, 3 fazy + summary, mieszanie odpowiedzialności (parsing, cache, networking z retry/backoff, dekodowanie audio, DSP, budowa pliku, sprzątanie) w jednej metodzie klasy.
  - Zagnieżdżone importy w środku metody (`plik:429-434, 527-528, 646, 659-660, 691, 727, 739`) — normalny styl w tym repo (lazy-load ciężkich bibliotek), ale utrudnia czytanie i testowanie.
  - Magic values lokalne: `ELEVENBYTES_SAMPLE_RATE=44100`, `HARD_TIMEOUT_S=5h`, `CONCURRENCY=85`, `INLINE_RETRIES=3`, `INLINE_RETRY_DELAY=1.5`, `MASS_FAIL_RATIO=0.25` — nigdzie niekonfigurowalne z zewnątrz (nie w `Settings`, nie w `constants.py`).
  - Domyślny głos `'dallin'` zahardkodowany jako fallback (`plik:471`) zamiast referencji do `tts_elevenbytes.DEFAULT_VOICE`.
  - `except (TimeoutError, Exception)` nigdzie tu nie występuje, ale analogiczny wzorzec "łap wszystko" pojawia się wielokrotnie — brak rozróżnienia błędów sieciowych/danych/IO.
  - Zawiera 4 funkcje lokalne (`_f`, `_synth_one`, `_decode_mp3`, `_atempo_pipe`) — opisane niżej.

###### `_f(value, fallback)` (linia 456, zagnieżdżona w `srt_to_wav_elevenbytes`)
- **Co robi:** bezpieczny `float()` z fallbackiem przy `TypeError`/`ValueError`.
- **Przyjmuje:** `value` (dowolny), `fallback` (wartość zwracana przy błędzie).
- **Zwraca:** `float`.
- **Uwagi:** brak adnotacji typów (jedyna funkcja lokalna bez type hints); nazwa `_f` nieopisowa.

###### `_synth_one(orig_idx: int, text: str) -> tuple[int, str, bytes | None, str | None, float]` (linia 542)
- **Co robi:** syntetyzuje jeden napis z do 3 próbami inline (delay 1.5s), zwraca krotkę wynikową zamiast rzucać.
- **Przyjmuje:** `orig_idx`, `text`.
- **Zwraca:** `(idx, text, audio|None, error|None, elapsed)`.
- **Efekty uboczne:** blokujący `time.sleep` między próbami; wywołania sieciowe.
- **Woła:** `tts.synthesize_sync()` (zmienna domknięcia `tts` z metody nadrzędnej).
- **Wyjątki:** łapie wszystko (`except Exception`), nigdy nie propaguje.
- **Uwagi:** odpalana w `ThreadPoolExecutor` — 85 wątków jednocześnie wołających synchroniczny wrapper, który sam wewnętrznie odpala coroutine na osobnym persystentnym event loopie (`TTS._run_sync`) — dwie warstwy wątków/loopów nałożone na siebie (patrz też diagnoza pliku 2).

###### `_decode_mp3(mp3_file: _Path)` (linia 650)
- **Co robi:** dekoduje mp3 do mono int16 PCM przy `ELEVENBYTES_SAMPLE_RATE`, z resamplingiem `resample_poly` jeśli plik ma inny sample rate.
- **Przyjmuje:** ścieżkę do pliku mp3.
- **Zwraca:** `np.ndarray` int16 albo `None` przy błędzie/pustym wyniku.
- **Efekty uboczne:** brak (czyste, poza IO odczytu).
- **Woła:** `soundfile.read()`, opcjonalnie `scipy.signal.resample_poly`.
- **Wyjątki:** łapie `Exception` generalnie, zwraca `None`.
- **Uwagi:** brak adnotacji zwracanego typu (`-> np.ndarray | None` nie zadeklarowane, mimo że reszta kodu w tym obszarze jest typowana).

###### `_atempo_pipe(audio_int16)` (linia 668)
- **Co robi:** przepuszcza tablicę PCM przez FFmpeg stdin→stdout z filtrem atempo (bez plików tymczasowych).
- **Przyjmuje:** `np.ndarray` int16.
- **Zwraca:** `np.ndarray` int16 (wynik po atempo).
- **Efekty uboczne:** odpala proces FFmpeg (`subprocess_run` z `check=True`).
- **Woła:** `self._build_atempo_chain()`.
- **Wyjątki:** `subprocess.CalledProcessError` jeśli FFmpeg zwróci błąd (nie łapane lokalnie — propaguje).
- **Uwagi:** brak adnotacji typu zwrotu.

##### `_pp_speed_file(self, file_path: str) -> None` (linia 756)
- **Co robi:** stosuje atempo do pojedynczego pliku audio in-place (przez plik tymczasowy + rename).
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy/usuwa plik `_pp_tmp`; nadpisuje `file_path`.
- **Woła:** `self._build_atempo_chain()`.
- **Wyjątki:** brak jawnej obsługi błędu FFmpeg (jeśli `call()` zawiedzie, `tmp` nie powstanie i funkcja po cichu nic nie zrobi — plik oryginalny zostaje nietknięty, brak logu błędu).
- **Uwagi:** no-op jeśli `_pp_speed == 1.0` lub plik nie istnieje — dobry guard.

##### `_pp_speed_audio(self, audio_int16, sample_rate: int)` (linia 772)
- **Co robi:** stosuje atempo do tablicy numpy przez zapis do pliku tymczasowego WAV, FFmpeg, odczyt z powrotem.
- **Przyjmuje:** `audio_int16` (numpy array), `sample_rate`.
- **Zwraca:** numpy array po atempo (lub oryginał jeśli FFmpeg zawiódł).
- **Efekty uboczne:** tworzy i usuwa `pp_speed_in.wav`/`pp_speed_out.wav` w `working_space_temp`.
- **Woła:** `self._build_atempo_chain()`.
- **Wyjątki:** brak jawnej.
- **Uwagi:** **martwy kod / nieużywana metoda** — brak wywołań tej metody gdziekolwiek w pliku (zweryfikowano grepem: jedyne wystąpienie to definicja). Prawdopodobnie zastąpiona przez `_atempo_pipe` (stdin/stdout, bez plików tymczasowych) w nowszej wersji `srt_to_wav_elevenbytes`, ale stara wersja nie została usunięta. Brak adnotacji zwracanego typu.

##### `_pp_speed_whole_wav(self, wav_path: str, subtitles: pysrt.SubRipFile) -> None` (linia 798)
- **Co robi:** dla silników generujących cały WAV naraz (Balabolka) — tnie WAV na klipy per napis wg granic czasowych, stosuje atempo do każdego klipu osobno przez FFmpeg, składa z powrotem z ciszą wg nowego czasu trwania.
- **Zwraca:** `None`.
- **Efekty uboczne:** nadpisuje `wav_path`; tworzy/usuwa pliki tymczasowe `bal_pp_in.wav`/`bal_pp_out.wav` (sekwencyjnie, w pętli — nie równolegle).
- **Woła:** `self._build_atempo_chain()`.
- **Wyjątki:** brak jawnej.
- **Uwagi:** granice klipów liczone z `subtitle.start` do `next.start` (nie do `subtitle.end`) — czyli klip obejmuje też ciszę między napisami, którą też przyśpiesza atempo; może to być zamierzone (uproszczenie) lub subtelny bug wpływający na końcową synchronizację przy dużych przerwach między liniami.

##### `_build_atempo_chain(speed: float) -> List[str]` (linia 856) — `@staticmethod`
- **Co robi:** buduje łańcuch filtrów `atempo=X` dla FFmpeg, bo pojedynczy filtr `atempo` obsługuje tylko zakres [0.5, 2.0] — dla wartości poza zakresem dzieli/dubluje przez wielokrotne filtry.
- **Przyjmuje:** `speed` (docelowy mnożnik, przycinany do [0.5, 100.0]).
- **Zwraca:** listę stringów filtrów do złączenia przecinkiem.
- **Efekty uboczne:** brak.
- **Woła:** brak.
- **Wyjątki:** brak (matematycznie bezpieczna pętla `while`).
- **Uwagi:** dobra, samodzielna, testowalna funkcja czysta — jeden z niewielu fragmentów pliku bez efektów ubocznych. Używana przez 5 innych metod (`_pp_speed_file`, `_pp_speed_audio`, `_pp_speed_whole_wav`, `_ffmpeg_post_process`, `_atempo_pipe`).

##### `_ffmpeg_post_process(self, input_path: str, output_path: str, tts_speed: str, tts_volume: str) -> None` (linia 880)
- **Co robi:** stosuje speed (atempo) i volume (dB) przez FFmpeg do pliku WAV; jeśli nic do zrobienia — po prostu przenosi plik (`shutil.move`).
- **Przyjmuje:** `input_path`, `output_path`, `tts_speed` (string, `'auto'`/`''` = brak zmiany), `tts_volume` (string, `'auto'`/`''`/`'0'` = brak zmiany).
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy `output_path`, `console.print`.
- **Woła:** `self._build_atempo_chain()`, lokalny import `shutil.move`.
- **Wyjątki:** `ValueError` przy nieparsowalnym `tts_speed`/`tts_volume` (nie w `('auto','')`).
- **Uwagi:** **martwy kod / nieużywana metoda** — brak wywołań w całym pliku (grep potwierdza wyłącznie definicję). Dubluje częściowo logikę `_apply_post_processing` (wołaną realnie z `generate_audio`), ale ta ostatnia robi tylko volume (bo speed jest już aplikowany per-subtitle w trakcie generacji) — czyli `_ffmpeg_post_process` to relikt starszego podejścia "post-process całego pliku na końcu", zastąpiony podejściem "atempo per napis w locie".

##### `merge_tts_audio(self) -> None` (linia 924)
- **Co robi:** dla każdego wygenerowanego pliku audio lektora sprawdza, czy istnieje odpowiadający plik w `working_space_temp` (istniejąca ścieżka audio z ekstrakcji MKV); jeśli tak — miksuje oba (dłuższy jako podstawa, krótszy z boostem +7dB) do EAC3; jeśli nie — po prostu konwertuje audio lektora do EAC3. Chroni przed pustym audio lektora (duration<=0) — wtedy pomija i czyści powiązane pliki.
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy pliki `.eac3` w `working_space_output`; usuwa pliki źródłowe (main_subs, tmp) po zużyciu.
- **Woła:** `self._get_files_dict()` (x2), `self._get_file_duration()`, `self._merge_files()`, `self._convert_to_eac3()`, `self._remove_same_name_files()`.
- **Wyjątki:** brak jawnej obsługi błędów FFmpeg (deleguje do `call()`, ignoruje kod wyjścia).
- **Uwagi:** guard na puste audio (`plik:944-952`) jest dobrym, świeżym zabezpieczeniem (widoczne też w historii commitów — "fix log wypakowywania" itd.).

##### `_get_files_dict(self, directory: str) -> Dict[str, str]` (linia 979)
- **Co robi:** zwraca mapę `{basename_bez_rozszerzenia: nazwa_pliku}` dla plików w katalogu, wykluczając `.srt`/`.ass`.
- **Zwraca:** `Dict[str, str]`.
- **Efekty uboczne:** brak.
- **Woła:** `listdir()`.
- **Wyjątki:** `FileNotFoundError` jeśli katalog nie istnieje.
- **Uwagi:** przy wielu plikach o tej samej nazwie bazowej ale różnych rozszerzeniach (poza wykluczonymi) nadpisuje wpis w słowniku bez ostrzeżenia — cichy silent-overwrite.

##### `_get_file_duration(self, file_path: str) -> float` (linia 992)
- **Co robi:** odczytuje długość pliku audio przez `mediainfo` (ffprobe); przy błędzie/`N/A` (typowe dla RF64/>4GB WAV) fallbackuje na ręczne czytanie nagłówka WAV (`nframes/framerate`); ostatecznie zwraca `0.0` z ostrzeżeniem.
- **Przyjmuje:** `file_path`.
- **Zwraca:** `float` (sekundy, `0.0` jeśli nieznane).
- **Efekty uboczne:** `console.print` przy ostatecznym niepowodzeniu.
- **Woła:** `mediainfo()`, `wave.open()`.
- **Wyjątki:** łapie `(ValueError, TypeError, KeyError)` dla mediainfo i `(wave.Error, OSError, EOFError)` dla fallbacku — dobra, celowa obsługa (udokumentowana w docstringu jako świadomy workaround na limit 4GB WAV).
- **Uwagi:** solidny kawałek kodu, dobrze udokumentowany powód istnienia fallbacku.

##### `_merge_files(self, input_file_1: str, input_file_2: str, output_file: str)` (linia 1030)
- **Co robi:** miksuje dwa pliki audio przez FFmpeg `amix`, dodając +7dB do tego, który NIE jest ścieżką "main_subs" (czyli boostuje ścieżkę lektora względem oryginalnej).
- **Zwraca:** brak adnotacji typu zwrotu (efektywnie `None`).
- **Efekty uboczne:** tworzy `output_file` przez `call()`.
- **Woła:** `call()` (subprocess).
- **Wyjątki:** brak jawnej.
- **Uwagi:** rozpoznawanie, który plik jest "main_subs" po podciągu w ścieżce (`'main_subs' in input_file_1`, `plik:1039`) — kruche powiązanie z nazwą katalogu `WORKING_SPACE_TEMP_MAIN_SUBS`, zamiast jawnego parametru/flagi; `+7dB` to zahardkodowana wartość biznesowa bez możliwości konfiguracji przez `Settings` (w przeciwieństwie do `pp_volume`).

##### `_convert_to_eac3(self, input_file: str, output_file: str)` (linia 1059)
- **Co robi:** konwertuje pojedynczy plik audio do EAC3 przez FFmpeg.
- **Zwraca:** brak adnotacji (efektywnie `None`).
- **Efekty uboczne:** tworzy `output_file`.
- **Woła:** `call()`.
- **Wyjątki:** brak jawnej.
- **Uwagi:** brak.

##### `_remove_same_name_files(self, directory: str, file_name: str)` (linia 1075)
- **Co robi:** usuwa wszystkie pliki w katalogu o danym basename (niezależnie od rozszerzenia).
- **Zwraca:** brak adnotacji (efektywnie `None`).
- **Efekty uboczne:** `remove()` na dysku.
- **Woła:** `listdir()`.
- **Wyjątki:** brak jawnej.
- **Uwagi:** brak.

##### `_subtitle_is_empty(self) -> bool` (linia 1088)
- **Co robi:** sprawdza czy plik napisów jest pusty/nie istnieje/parsuje się do zera wpisów — guard przed próbą syntezy z pustego pliku.
- **Zwraca:** `bool`.
- **Efekty uboczne:** brak.
- **Woła:** `pysrt.open()`.
- **Wyjątki:** łapie `(UnicodeDecodeError, OSError, ValueError)` i traktuje jako "niepusty" (celowe — błąd parsowania ma iść dalej i zawalić się głośno w silniku, nie zostać po cichu pominięty).
- **Uwagi:** dobrze udokumentowany, przemyślany guard (docstring wyjaśnia rationale).

##### `generate_audio(self, settings: Settings)` (linia 1108)
- **Co robi:** główny punkt wejścia fasady. Czyta parametry z `Settings`, ustawia `_pp_speed`, sprawdza czy napisy nie są puste (guard), **dispatchuje po stringu `settings.tts`** do jednej z 5 metod silników, po zakończeniu aplikuje post-processing głośności i merguje audio.
- **Przyjmuje:** `settings: Settings`.
- **Zwraca:** brak adnotacji zwrotu (efektywnie `None`).
- **Efekty uboczne:** cała kaskada efektów ubocznych wybranego silnika + `_apply_post_processing` + `merge_tts_audio`; liczne `console.print`.
- **Woła:** `self._subtitle_is_empty()`, jedną z: `self.srt_to_wav_harpo()`, `self.srt_to_wav_balabolka()`, `self.srt_to_wav_edge_online()`, `self.srt_to_wav_elevenbytes()` (x2, v6/v7), `self._apply_post_processing()`, `self.merge_tts_audio()`.
- **Wyjątki:** propaguje wszystko z wybranego silnika.
- **Uwagi:** **rdzeń niespójności ze stylem MangaShift** — `if/elif` łańcuch po dosłownych stringach etykiet UI (`"TTS - Zosia - Harpo"`, `"TTS - Agnieszka - Ivona"`, `"TTS - Zofia - Edge"`, `"TTS - Marek - Edge"`, `"TTS - ElevenBytes (ElevenLabs v2)"`, `"TTS - ElevenBytes (ElevenLabs v3)"`) zamiast rejestru silników (`plik:1138-1158`); dodanie nowego silnika = edycja tej metody + dopisanie nowej metody `srt_to_wav_*`, dokładnie odwrotność wzorca "serwis nieświadomy silników" z MangaShift. Jeśli `tts` nie pasuje do żadnej gałęzi, metoda po cichu nie robi nic (brak `else`/raise) — silent no-op przy literówce w configu.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:**
  - `_build_atempo_chain` (l.856) — czysta, samodzielna, dobrze przetestowana logicznie funkcja.
  - `_get_file_duration` (l.992) i `_subtitle_is_empty` (l.1088) — dobrze udokumentowane, świadome workaroundy z jasnym uzasadnieniem w docstringu.
  - Guard na puste audio lektora w `merge_tts_audio` (l.944-952) — świeża, sensowna poprawka widoczna też w historii commitów.
  - Cache mp3 w `srt_to_wav_elevenbytes` (resume po crashu) — solidny mechanizm odporności na awarie długich sesji syntezy.
  - Adaptacyjny cooldown przy masowych awariach API (`MASS_FAIL_RATIO`, l.627-639) — rozsądna heurystyka odróżniająca pojedyncze straty od outage'u.
- **⚠️ dług techniczny / code smells:**
  - God-method `srt_to_wav_elevenbytes` — 340 linii, wiele odpowiedzialności (`plik:413-754`).
  - Martwy kod: `_pp_speed_audio` (l.772-796) i `_ffmpeg_post_process` (l.880-922) — brak wywołań w całym pliku, prawdopodobnie relikty po refaktorze na podejście "atempo w locie".
  - Mieszanie kanałów logowania: `print()` (l.178, 293, 486-492, 519-524, 571-578 itd.) vs `console.print` (rich, l.122, 346, 510, 918 itd.) — brak jednego źródła prawdy dla logowania.
  - Duplikacja hardkodów sample rate: 22500 (Harpo, l.175), 24000 (Edge merge, l.374), 44100 (ElevenBytes, l.440) — trzy różne wartości bez wspólnej stałej/rejestru per silnik.
  - `except (TimeoutError, Exception)` (l.344) — pierwszy człon zbędny, `TimeoutError` już jest `Exception`.
  - Gołe/szerokie `except Exception` w wielu miejscach ElevenBytes flow (l.552, 654, 730, 735) — połyka błędy bez rozróżnienia przyczyny.
  - Publiczna metoda `process_subtitle` (l.282) powinna być prywatna (`_process_subtitle`) wg konwencji reszty klasy.
  - Brak adnotacji zwracanego typu w kilku metodach (`_merge_files`, `_convert_to_eac3`, `_remove_same_name_files`, `generate_audio`, `_pp_speed_audio`, `_decode_mp3`, `_atempo_pipe`).
  - Pole dataclass `working_space_temp_alt_subs` (l.100) zadeklarowane, ale nieużywane w żadnej metodzie tego pliku.
  - Magic value `+7dB` w `_merge_files` (l.1044, 1053) niekonfigurowalny, w odróżnieniu od `pp_volume` który jest w `Settings`.
  - String-matching na treści ścieżki pliku (`'main_subs' in input_file_1`, l.1039) jako sposób rozróżnienia roli pliku — kruche.
  - Zagnieżdżone importy rozsiane w środku metod (uzasadnione lazy-loadingiem ciężkich bibliotek jak numpy/soundfile/scipy, ale utrudnia czytelność i nie jest jednolite — część importów jest na górze pliku, część głęboko w metodach).
- **❌ niespójności ze stylem MangaShift:**
  - **Brak rejestru silników TTS.** `generate_audio` (l.1108) to dokładnie ten „if per silnik", którego MangaShift świadomie unika — 6-gałęziowy `if/elif` po dosłownych stringach etykiet UI, zamiast `ENGINE_REGISTRY: dict[EngineId, Callable]` + `Literal` obok. Dodanie 6. silnika TTS wymaga edycji tej metody + `data/settings.py` (gdzie te same stringi są accepted-values) + nowej metody `srt_to_wav_*` — czyli działa dokładnie odwrotnie niż zasada "serwis nieświadomy dodania silnika" z MangaShift (`docelowa-architektura-jedno-zrodlo.md:64-65`).
  - **Etykieta UI = identyfikator biznesowy.** String `"TTS - ElevenBytes (ElevenLabs v3)"` pełni jednocześnie rolę labelki wyświetlanej userowi i klucza dispatchu — w MangaShift to rozdzielone: `engine_id` (kanoniczny klucz) vs `label` (własność frontu, MangaShift: "label żyje TYLKO na froncie").
  - **Brak dataclass/registry dla per-silnikowych parametrów.** Cechy typu "silnik X ma wybór modelu/wersji" (`ENGINES_WITH_MODEL_CHOICE` w MangaShift TTS, notabene wytknięte tam też jako dług, ale świadomy) tutaj nie istnieją wcale jako koncept — `engine="v6"/"v7"` jest przekazywane ręcznie stringiem z `generate_audio` (l.1149, 1156) zamiast czytane z rejestru silnika ElevenBytes.
  - **Brak dependency injection.** `SubtitleToSpeech` importuje `ElevenBytesTTS`/`VoiceSettings` lokalnie wewnątrz metody (l.433) zamiast dostawać silnik jako wstrzykniętą zależność — utrudnia testowanie (nie da się podmienić silnika bez monkeypatchowania modułu).
  - **Brak jednego źródła prawdy dla sample rate/formatu per silnik** — MangaShift stawia na "jedno pytanie = jedno miejsce odpowiedzi"; tu trzy różne sample rate są rozproszone jako literały w trzech różnych metodach.
  - Klasa **jest** dataclassem ze slots (`@dataclass(slots=True)`, l.60) — to jedna zgodność ze stylem MangaShift, ale reszta (fasada+silnik+DSP+merge w jednej klasie) łamie podział warstwowy (serwis/rejestr/pipeline) z docelowej architektury.
- **🔗 sprzężenia:**
  - Ciasno sprzężony z `data.settings.Settings` przez dosłowne nazwy pól i wartości stringowe (`settings.tts` musi dokładnie pasować do etykiet UI) — zmiana etykiety w UI (`start.py`/`data/settings.py`) wymaga równoległej zmiany w `generate_audio`.
  - Sprzężony z układem katalogów `constants.py` (`WORKING_SPACE_TEMP_MAIN_SUBS` itd.) przez zaszyte na sztywno ścieżki i rozpoznawanie ról plików po nazwie katalogu w stringu (`'main_subs' in ...`).
  - Sprzężony z `modules/tts_elevenbytes.py` przez lokalny import wewnątrz metody — zmiana sygnatury `TTS.__init__`/`synthesize_sync` w tamtym pliku natychmiast łamie `srt_to_wav_elevenbytes` bez ostrzeżenia na poziomie importów modułu.
  - Zależność od zainstalowanego na maszynie głosu SAPI (`'Vocalizer Expressive Zosia Harpo 22kHz'`) i binarki `balcon.exe` — środowiskowe, niewidoczne z poziomu kodu (brak walidacji przy starcie).

---

## 📄 plik: `modules/tts_elevenbytes.py` (617 linii)

### przeznaczenie
Samodzielna biblioteka kliencka do prywatnego proxy ElevenLabs (`teamsp.org/xi/run6.php` i
`run7.php`) — jedna zależność zewnętrzna (`httpx`). Udostępnia async i sync API do syntezy
pojedynczego tekstu, zapisu do pliku i batch processingu z retry/backoff/concurrency control.
Napisany jako biblioteka ogólnego przeznaczenia (ma własny changelog-style docstring z
przykładami użycia, l.1-32), ale w praktyce ma jednego konsumenta w repo:
`modules/subtitle_to_speech.py:433` (lokalny import w `srt_to_wav_elevenbytes`). Osobny plik,
osobna warstwa — czystszy architektonicznie niż `subtitle_to_speech.py`.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `from __future__ import annotations` | — | leniwe adnotacje typów (`str \| None` bez importu `Optional`) |
| `asyncio` | stdlib | semafor, event loop, `gather`, `run_coroutine_threadsafe` |
| `concurrent.futures` | stdlib | `Future`, `TimeoutError` w `_run_sync` |
| `logging` | stdlib | logger `"elevenbytes"` z `NullHandler` |
| `shutil` | stdlib | `shutil.which("ffmpeg")` fallback w `_convert_audio` |
| `threading` | stdlib | wątek dla persystentnego event loopa (`_ensure_sync_loop`) |
| `subprocess` | stdlib | wywołanie ffmpeg w `_convert_audio` |
| `tempfile` | stdlib | pliki tymczasowe do konwersji formatu |
| `time` | stdlib | znaczniki czasu (`perf_counter`, `strftime`) |
| `dataclass, field` | dataclasses | `VoiceSettings`, `SynthResult`, `BatchReport` |
| `Path` | pathlib | operacje na ścieżkach plików |
| `httpx` | httpx | klient HTTP async z retries transportu |

### stałe / zmienne modułowe
| nazwa | linia | typ | wartość / cel |
|-------|-------|-----|---------------|
| `log` | 49 | `logging.Logger` | logger biblioteki z `NullHandler` (nie zaśmieca stdout hosta), `propagate=False` |
| `API_KEY` | 55 | `str` | zahardkodowany klucz API proxy (`"wqpwgoGhADAwIdb1JRNTAEBgg="`) — **sekret w repo** |
| `API_URL_V6` | 56 | `str` | endpoint silnika v6 (ElevenLabs v2, bez voice_settings) |
| `API_URL_V7` | 57 | `str` | endpoint silnika v7 (ElevenLabs v3, + voice_settings) |
| `API_URL` | 58 | `str` | alias wstecznej kompatybilności = `API_URL_V6` (**czy realnie używany? patrz uwagi niżej**) |
| `ENGINE_URLS` | 59 | `dict[str, str]` | mapa `"v6"/"v7"` → URL — **to jest jedyny prawdziwy "rejestr silników"** w całym obszarze TTS |
| `DEFAULT_ENGINE` | 60 | `str` | `"v6"` |
| `MAX_CHARS` | 61 | `int` | 5000 — limit długości tekstu |
| `MIN_CHARS` | 62 | `int` | 2 — minimalna długość tekstu |
| `MIN_AUDIO_BYTES` | 63 | `int` | 1024 — próg "audio nie jest za małe/puste" |
| `DEFAULT_VOICE` | 64 | `str` | `"dallin"` |
| `DEFAULT_CONCURRENCY` | 65 | `int` | 100 |
| `DEFAULT_TIMEOUT` | 66 | `float` | 30.0s |
| `DEFAULT_MAX_RETRIES` | 67 | `int` | 100 (bardzo wysoki default) |
| `RETRY_BACKOFF_BASE` | 68 | `float` | 2.0 (mnożnik backoffu) |
| `RETRY_STATUS_CODES` | 69 | `frozenset[int]` | `{403, 429, 500, 502, 503, 504}` |
| `SUPPORTED_FORMATS` | 70 | `frozenset[str]` | `{"mp3", "wav", "ogg", "flac"}` |
| `VOICES` | 75-79 | `dict[str, tuple[str, str]]` | rejestr głosów: alias → (display_name, voice_id); mutowalny w runtime przez `add_voice`/`remove_voice` |

### klasy

#### `class VoiceSettings` (linia 86) — `@dataclass(frozen=True, slots=True)`
**Cel:** parametry `voice_settings` ElevenLabs v3, wysyłane tylko przez silnik v7.

**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `stability` | `float` | `0.5` | stabilność głosu (0.0 Creative — 1.0 Robust) |
| `similarity_boost` | `float` | `0.75` | wierność wobec oryginalnego głosu |
| `style` | `float` | `0.0` | wyolbrzymienie stylu |
| `use_speaker_boost` | `bool` | `True` | wzmocnienie podobieństwa do mówcy |

**Metody:**

##### `as_form(self) -> dict[str, str]` (linia 103)
- **Co robi:** serializuje pola do form-data zgodnego z frontendem `run7` (bool jako `'true'/'false'` string).
- **Zwraca:** `dict[str, str]`.
- **Efekty uboczne:** brak.
- **Woła:** brak.
- **Wyjątki:** brak.
- **Uwagi:** czysta funkcja, brak zastrzeżeń.

#### `class SynthResult` (linia 117) — `@dataclass(frozen=True, slots=True)`
**Cel:** wynik pojedynczej syntezy w ramach batcha.

**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `index` | `int` | — | pozycja w batchu |
| `text` | `str` | — | oryginalny tekst |
| `audio` | `bytes \| None` | — | dane audio (None przy błędzie) |
| `ok` | `bool` | — | sukces/porażka |
| `error` | `str \| None` | `None` | opis błędu |
| `elapsed` | `float` | `0.0` | czas trwania w sekundach |
| `retries` | `int` | `0` | **zadeklarowane, ale nigdzie niezapisywane realną wartością** — `_batch_item` nie liczy retryów i nie przekazuje tego pola przy tworzeniu `SynthResult` (l.530-533, 535-538), więc zawsze zostaje na `0` mimo że `_request_with_retry` wewnętrznie robi retry. |

#### `class BatchReport` (linia 129) — `@dataclass(slots=True)`
**Cel:** raport zbiorczy z `synthesize_batch`.

**Pola:**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `results` | `list[SynthResult]` | `field(default_factory=list)` | lista wyników, posortowana po `index` |
| `wall_time` | `float` | `0.0` | całkowity czas ściany batcha |

**Metody:**

##### `total(self) -> int` (linia 137) — `@property`
- **Co robi:** liczba wszystkich wyników. **Zwraca:** `len(self.results)`. Bez efektów ubocznych.

##### `ok_count(self) -> int` (linia 141) — `@property`
- **Co robi:** liczba sukcesów. **Zwraca:** sumę `r.ok`. Bez efektów ubocznych.

##### `fail_count(self) -> int` (linia 145) — `@property`
- **Co robi:** liczba porażek (`total - ok_count`). Bez efektów ubocznych.

##### `summary(self) -> str` (linia 148)
- **Co robi:** formatuje czytelne podsumowanie `"X/Y OK | Z FAIL | Wall: Ns"`.
- **Zwraca:** `str`.
- **Woła:** `self.total`, `self.ok_count`, `self.fail_count`.
- **Uwagi:** czysta, bez zastrzeżeń.

#### `class TTSError(Exception)` (linia 159)
**Cel:** bazowy wyjątek biblioteki. Bez ciała poza docstringiem.

#### `class TTSValidationError(TTSError)` (linia 163)
**Cel:** błąd walidacji inputu (tekst za długi/krótki, zły format, zły engine). Bez ciała.

#### `class TTSAPIError(TTSError)` (linia 167)
**Cel:** błąd API po wyczerpaniu retryów lub timeout event loopu. Bez ciała.

#### `class TTS` (linia 171) — zwykła klasa (nie dataclass), async context manager
**Cel:** główny serwis klienta ElevenBytes. Odpowiada za cały cykl życia połączenia HTTP,
walidację, retry, konwersję formatu, batch i sync/async wrappery.

**Pola instancji (ustawiane w `__init__`, nie jako dataclass fields):**
| pole | typ | cel |
|------|-----|-----|
| `_api_url` | `str` | rozwiązany URL endpointu (`_resolve_engine(engine)`) |
| `_settings` | `VoiceSettings` | domyślne voice_settings (v7) |
| `_default_voice` | `str` | domyślny alias/voice_id |
| `_output_dir` | `Path \| None` | katalog domyślny na pliki audio |
| `_max_retries` | `int` | max prób per request |
| `_concurrency` | `int` | limit równoległości |
| `_sem` | `asyncio.Semaphore \| None` | leniwie inicjalizowany semafor (bindowany do event loopu) |
| `_client` | `httpx.AsyncClient` | klient HTTP z nagłówkami udającymi przeglądarkę |
| `_sync_loop` | `asyncio.AbstractEventLoop \| None` | persystentny event loop dla sync API |
| `_sync_thread` | `threading.Thread \| None` | wątek trzymający `_sync_loop` |

**Metody:**

##### `__init__(self, default_voice=DEFAULT_VOICE, output_dir=None, engine=DEFAULT_ENGINE, settings=None, concurrency=DEFAULT_CONCURRENCY, max_retries=DEFAULT_MAX_RETRIES, timeout=DEFAULT_TIMEOUT) -> None` (linia 187)
- **Co robi:** inicjalizuje klienta HTTP z transportem retry=2 (dodatkowa warstwa retry NIŻEJ niż logika w `_request_with_retry`), spoofowanymi nagłówkami przeglądarki (`User-Agent`, `Referer: https://teamsp.org/xi/tts.html`, `Origin`), rozwiązuje URL silnika.
- **Przyjmuje:** 7 parametrów konfiguracyjnych (opisane w docstringu klasy, l.176-185).
- **Zwraca:** `None`.
- **Efekty uboczne:** tworzy `httpx.AsyncClient` (otwiera connection pool).
- **Woła:** `self._resolve_engine()`.
- **Wyjątki:** `TTSValidationError` jeśli `engine` nieznany.
- **Uwagi:** nagłówki maskujące się pod przeglądarkę Chrome/Windows (`plik:209-217`) sugerują, że proxy `teamsp.org` blokuje/utrudnia dostęp automatom — to działanie "obchodzenia" ochrony API strony trzeciej (nieautoryzowanej wprost przez ElevenLabs), spójne z faktem że `API_KEY` jest zahardkodowanym sekretem współdzielonym w kodzie.

##### `_get_sem(self) -> asyncio.Semaphore` (linia 223)
- **Co robi:** leniwie tworzy/odtwarza semafor bindowany do aktualnie działającego event loopu — chroni przed użyciem semafora stworzonego na innym (już zamkniętym) loopie przy wielokrotnych wywołaniach `_run_sync`.
- **Zwraca:** `asyncio.Semaphore`.
- **Efekty uboczne:** mutuje `self._sem`.
- **Woła:** `asyncio.get_running_loop()`.
- **Wyjątki:** `RuntimeError` jeśli brak działającego event loopu (wywołane poza async context).
- **Uwagi:** dostęp do prywatnego atrybutu `self._sem._loop` (l.226) — sprzężenie z implementacją wewnętrzną `asyncio.Semaphore` (oznaczone `# type: ignore[attr-defined]`), świadomy hack, ale krucha zależność od wersji Pythona/asyncio.

##### `_resolve_engine(engine: str) -> str` (linia 230) — `@staticmethod`
- **Co robi:** mapuje `"v6"/"v7"` na URL z `ENGINE_URLS`.
- **Zwraca:** `str` (URL).
- **Wyjątki:** `TTSValidationError` przy nieznanym silniku.
- **Uwagi:** to jest **jedyny prawdziwy rejestr silników w całym obszarze TTS** — najbliższy wzorcowi MangaShift (`dict` jako jedno źródło prawdy + walidacja), choć bez towarzyszącego `Literal["v6", "v7"]` typu obok (MangaShift wymaga pary rejestr+Literal "linijka pod linijką").

##### `_build_payload(self, text: str, voice_id: str, settings: VoiceSettings | None) -> dict[str, str]` (linia 239)
- **Co robi:** buduje form-data requestu; dołącza `voice_settings` (przez `as_form()`) tylko gdy aktywny endpoint to v7.
- **Zwraca:** `dict[str, str]`.
- **Woła:** `(settings or self._settings).as_form()`.
- **Uwagi:** **to jest if-per-silnik**, ale zamknięty w jednym, małym, jawnym miejscu (`if self._api_url == API_URL_V7`, l.247) — różni się jakościowo od wzorca w `subtitle_to_speech.py`: tu decyzja dotyczy TYLKO kształtu payloadu (dane), nie doboru całej ścieżki kodu/klasy. Bliżej wzorca MangaShift "rejestr + mały if" niż "if-drzewo per silnik".

##### `async synthesize(self, text: str, voice: str | None = None, fmt: str = "mp3", settings: VoiceSettings | None = None) -> bytes` (linia 253)
- **Co robi:** waliduje tekst/format, rozwiązuje voice_id, wysyła request pod semaforem, opcjonalnie konwertuje z mp3 do innego formatu.
- **Przyjmuje:** `text`, `voice` (alias lub raw ID), `fmt`, `settings` (override per-call).
- **Zwraca:** `bytes` (audio).
- **Efekty uboczne:** żądanie sieciowe; ewentualne odpalenie ffmpeg przy konwersji formatu.
- **Woła:** `self._validate_text()`, `self._validate_format()`, `self._resolve_voice()`, `self._get_sem()`, `self._request_with_retry()`, `self._convert_audio()`.
- **Wyjątki:** `TTSValidationError`, `TTSAPIError`.
- **Uwagi:** publiczne, główne API async.

##### `async synthesize_to_file(self, text, voice=None, path=None, fmt=None) -> Path` (linia 289)
- **Co robi:** jak `synthesize`, ale zapisuje wynik na dysk; auto-generuje nazwę pliku (`tts_<timestamp>.<fmt>`) jeśli `path` nie podane; jeśli `path` to sama nazwa (bez katalogu) i jest ustawiony `output_dir` — umieszcza tam.
- **Zwraca:** `Path` zapisanego pliku.
- **Efekty uboczne:** `mkdir(parents=True)`, `write_bytes()`.
- **Woła:** `self.synthesize()`, `self._auto_path()`.
- **Wyjątki:** propaguje z `synthesize`; błędy IO przy zapisie.
- **Uwagi:** brak.

##### `async synthesize_batch(self, texts: list[str], voice=None, save_dir=None, fmt="mp3") -> BatchReport` (linia 321)
- **Co robi:** syntetyzuje listę tekstów równolegle (przez `asyncio.gather`), opcjonalnie zapisuje każdy plik do `save_dir`.
- **Zwraca:** `BatchReport`.
- **Efekty uboczne:** ewentualny zapis N plików; `log.info` po zakończeniu.
- **Woła:** `self._validate_format()`, `self._batch_item()` (x N), `asyncio.gather()`.
- **Wyjątki:** `TTSValidationError` z walidacji formatu na wejściu (błędy per-item są łapane wewnątrz `_batch_item`, nie propagują).
- **Uwagi:** brak.

##### `async close(self) -> None` (linia 359)
- **Co robi:** zamyka klienta HTTP (`self._client.aclose()`).
- **Zwraca:** `None`. **Woła:** `self._client.aclose()`. **Wyjątki:** brak jawnej.

##### `synthesize_sync(self, text, voice=None, fmt="mp3", settings=None) -> bytes` (linia 365)
- **Co robi:** sync wrapper na `synthesize` przez `_run_sync`.
- **Woła:** `self._run_sync(self.synthesize(...))`.
- **Uwagi:** `# type: ignore[return-value]` — `_run_sync` zwraca `object`, więc typowanie jest osłabione tutaj celowo.

##### `synthesize_to_file_sync(self, text, voice=None, path=None, fmt=None) -> Path` (linia 370)
- **Co robi:** sync wrapper na `synthesize_to_file`. **Woła:** `self._run_sync(...)`.

##### `synthesize_batch_sync(self, texts, voice=None, save_dir=None, fmt="mp3") -> BatchReport` (linia 380)
- **Co robi:** sync wrapper na `synthesize_batch`. **Woła:** `self._run_sync(...)`.

##### `close_sync(self) -> None` (linia 390)
- **Co robi:** zamyka klienta i persystentny event loop sync-API. Jeśli `_sync_loop` istnieje i nie jest zamknięty — planuje `close()` na tym loopie przez `run_coroutine_threadsafe`, czeka na wynik (timeout 10s), zatrzymuje loop, joinuje wątek (timeout 5s), zamyka loop. W przeciwnym razie próbuje `asyncio.run(self.close())` w nowym, tymczasowym loopie, połykając wszelkie wyjątki.
- **Zwraca:** `None`.
- **Efekty uboczne:** zatrzymanie wątku/event loopu; zamknięcie connection poola.
- **Woła:** `self.close()` pośrednio, `asyncio.run_coroutine_threadsafe`, `Thread.join`.
- **Wyjątki:** `except Exception: pass` w gałęzi fallback (l.404-405) — cichy połykacz błędów.
- **Uwagi:** brak.

##### `async __aenter__(self) -> TTS` (linia 409)
- **Co robi:** zwraca `self` — wsparcie `async with`. Bez efektów ubocznych.

##### `async __aexit__(self, *exc: object) -> None` (linia 412)
- **Co robi:** woła `self.close()` przy wyjściu z bloku `async with`.

##### `list_voices() -> dict[str, tuple[str, str]]` (linia 417) — `@staticmethod`
- **Co robi:** zwraca kopię (`dict(VOICES)`) rejestru głosów. **Zwraca:** `dict[str, tuple[str,str]]`.
- **Uwagi:** dobra praktyka — zwraca kopię, nie referencję do modułowego `VOICES`, więc wołający nie może przypadkiem zmutować rejestru.

##### `add_voice(alias: str, name: str, voice_id: str) -> None` (linia 423) — `@staticmethod`
- **Co robi:** dodaje/nadpisuje wpis w module-level `VOICES`.
- **Efekty uboczne:** **mutuje globalny stan modułu** — wszystkie instancje `TTS` w procesie dzielą ten sam rejestr głosów; brak thread-lock mimo że biblioteka jest jawnie wielowątkowa/wieloasync (potencjalny race przy równoczesnym `add_voice`/odczycie z wielu wątków, choć w praktyce mało prawdopodobne bo GIL + rzadkość wywołań).
- **Uwagi:** brak walidacji duplikatu/formatu `voice_id`.

##### `remove_voice(alias: str) -> None` (linia 434) — `@staticmethod`
- **Co robi:** usuwa wpis z `VOICES` (`dict.pop(alias, None)` — bezpieczne, brak błędu przy nieistniejącym aliasie).

##### `default_voice(self) -> str` (linia 438) — `@property`
- **Co robi:** getter `self._default_voice`.

##### `default_voice(self, alias: str) -> None` (linia 443) — `@default_voice.setter`
- **Co robi:** setter `self._default_voice = alias` — **brak walidacji, że `alias` istnieje w `VOICES`** (choć to zamierzone, bo `_resolve_voice` i tak traktuje nieznany alias jako raw voice_id).

##### `_validate_text(text: str) -> None` (linia 448) — `@staticmethod`
- **Co robi:** sprawdza typ (`isinstance(text, str)`), długość w `[MIN_CHARS, MAX_CHARS]`.
- **Wyjątki:** `TTSValidationError` z opisowym komunikatem.
- **Uwagi:** solidna, prosta walidacja.

##### `async _request_with_retry(self, text: str, voice_id: str, settings: VoiceSettings | None = None) -> bytes` (linia 457)
- **Co robi:** POST z retry + exponential backoff (capped na 5.0s) na `RETRY_STATUS_CODES`; osobno łapie `httpx.TimeoutException` z tym samym backoffem; rzuca dalej `httpx.HTTPStatusError` (nieretryowalne kody); po sukcesie sprawdza minimalny rozmiar odpowiedzi.
- **Przyjmuje:** `text`, `voice_id`, opcjonalny override `settings`.
- **Zwraca:** `bytes` (surowe mp3).
- **Efekty uboczne:** żądania HTTP; `log.warning` per retry.
- **Woła:** `self._build_payload()`, `self._client.post()`.
- **Wyjątki:** `TTSAPIError` (za mało danych w odpowiedzi lub wyczerpanie prób), re-raise `httpx.HTTPStatusError`.
- **Uwagi:** pusta linia w środku bloku try (`plik:484`) — kosmetyczny drobiazg. Pętla `for attempt in range(1, max_retries+1)` z `DEFAULT_MAX_RETRIES=100` domyślnie — bardzo dużo prób nim padnie `TTSAPIError`; w praktyce `subtitle_to_speech.py` nadpisuje to na `max_retries=2` (l.471 w tamtym pliku) świadomie, bo retry jest tam realizowany na wyższej warstwie (rundy).

##### `async _batch_item(self, index, text, voice, out_dir, fmt="mp3", settings=None) -> SynthResult` (linia 506)
- **Co robi:** pojedynczy element batcha; łapie wszystkie wyjątki i zwraca `SynthResult(ok=False, ...)` zamiast przerywać cały `gather`.
- **Zwraca:** `SynthResult`.
- **Efekty uboczne:** ewentualny zapis pliku do `out_dir`.
- **Woła:** `self._validate_text()`, `self._resolve_voice()`, `self._get_sem()`, `self._request_with_retry()`, `self._convert_audio()`.
- **Wyjątki:** żadne nie propagują — `except Exception as exc` łapie wszystko.
- **Uwagi:** jak wspomniano przy `SynthResult` — pole `retries` nigdy nie jest tu wypełniane realną liczbą prób.

##### `_resolve_voice(alias_or_id: str) -> str` (linia 540) — `@staticmethod`
- **Co robi:** mapuje alias na `voice_id` przez `VOICES`; nieznany alias zwraca bez zmian (traktowany jako surowe ID).
- **Zwraca:** `str`.
- **Uwagi:** brak walidacji formatu ID (np. długości) — celowe uproszczenie (przerzuca walidację na API zdalne).

##### `_validate_format(fmt: str) -> None` (linia 547) — `@staticmethod`
- **Co robi:** sprawdza czy `fmt` należy do `SUPPORTED_FORMATS`.
- **Wyjątki:** `TTSValidationError`.

##### `_convert_audio(mp3_data: bytes, target_fmt: str) -> bytes` (linia 554) — `@staticmethod`
- **Co robi:** konwertuje mp3→docelowy format przez ffmpeg (najpierw próbuje `imageio_ffmpeg.get_ffmpeg_exe()`, potem `shutil.which("ffmpeg")`); pisze do pliku tymczasowego, konwertuje, czyta wynik, sprząta oba pliki tymczasowe w `finally`.
- **Zwraca:** `bytes`.
- **Efekty uboczne:** tworzy i usuwa pliki tymczasowe (`tempfile.NamedTemporaryFile`); odpala subprocess ffmpeg.
- **Woła:** `subprocess.run()`.
- **Wyjątki:** `TTSError` (brak ffmpeg lub błąd konwersji z `stderr`).
- **Uwagi:** dobry wzorzec `try/finally` z `unlink(missing_ok=True)` — nie zostawia śmieci nawet przy błędzie.

##### `_auto_path(self, fmt: str = "mp3") -> Path` (linia 591)
- **Co robi:** generuje nazwę pliku `tts_<YYYYmmdd_HHMMSS>.<fmt>`; jeśli `output_dir` ustawiony, tworzy katalog i zwraca pełną ścieżkę.
- **Zwraca:** `Path`.
- **Efekty uboczne:** `mkdir(parents=True, exist_ok=True)` jeśli `output_dir` ustawiony.
- **Uwagi:** znacznik czasu z dokładnością do sekund — przy dwóch wywołaniach w tej samej sekundzie bez `path`/`fmt` różnicujących nastąpi nadpisanie pliku (rzadki, ale realny edge case przy batchu bez `save_dir`).

##### `_ensure_sync_loop(self) -> asyncio.AbstractEventLoop` (linia 599)
- **Co robi:** leniwie tworzy i uruchamia persystentny event loop w osobnym daemon-wątku (do wielokrotnego użycia przez sync API bez narzutu tworzenia nowego loopu za każdym razem).
- **Zwraca:** `asyncio.AbstractEventLoop`.
- **Efekty uboczne:** tworzy `asyncio.new_event_loop()`, uruchamia `Thread(daemon=True)`.
- **Woła:** brak.
- **Uwagi:** wzorzec "event loop w tle" — poprawny, ale wymaga dyscypliny wołania `close_sync()` żeby nie zostawić wiszącego wątku daemon (co przy `daemon=True` i tak nie zablokuje zamknięcia procesu, ale jest zasobowym leakiem podczas długiego działania).

##### `_run_sync(self, coro: object) -> object` (linia 609)
- **Co robi:** odpala coroutine na persystentnym event loopie z osobnego wątku i czeka na wynik z timeoutem 3600s (1h).
- **Przyjmuje:** `coro` (coroutine, typowane jako `object` — luźno).
- **Zwraca:** wynik coroutine (typowany jako `object` — wołający musi rzutować, stąd `# type: ignore[return-value]` w wrapperach).
- **Efekty uboczne:** blokuje wątek wołający do wyniku lub timeoutu.
- **Woła:** `self._ensure_sync_loop()`, `asyncio.run_coroutine_threadsafe()`.
- **Wyjątki:** `TTSAPIError` po `concurrent.futures.TimeoutError` (z jawnym `future.cancel()` przed rzuceniem).
- **Uwagi:** typowanie `object`/`object` zamiast generyków (`TypeVar`) to świadome uproszczenie kosztem precyzji typów — wywołujące metody muszą to obchodzić przez `# type: ignore`.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:**
  - Czysta warstwa: jeden plik, jedna zewnętrzna zależność (`httpx`), jasno wydzielone: config (stałe), dataclassy wyników, hierarchia wyjątków, serwis.
  - Wszystkie dataclassy poprawnie używają `slots=True` i `frozen=True` tam gdzie sensowne (`VoiceSettings`, `SynthResult` — immutable wyniki), zgodnie ze stylem MangaShift.
  - `ENGINE_URLS` (l.59) + `_resolve_engine` (l.230) to najbliższy wzorcowi MangaShift fragment całego obszaru TTS — rejestr `dict` + walidacja z czytelnym komunikatem błędu.
  - Solidna obsługa retry/backoff/timeout na poziomie HTTP (`_request_with_retry`), oddzielona od logiki wyższego poziomu (rundy w `subtitle_to_speech.py`).
  - `_convert_audio` — poprawny wzorzec `try/finally` sprzątający pliki tymczasowe.
  - Async + sync API konsekwentnie rozdzielone (`synthesize` vs `synthesize_sync` przez wspólny `_run_sync`), dobra reużywalność.
  - Docstring modułu (l.1-32) z przykładami użycia — rzadkość w tym repo, ułatwia onboarding.
- **⚠️ dług techniczny / code smells:**
  - `API_KEY` zahardkodowany w kodzie źródłowym (`plik:55`) — sekret w repo, nie w zmiennej środowiskowej/configu; ryzyko wycieku przy publikacji/współdzieleniu repo.
  - `API_URL` (l.58) zadeklarowany jako "default endpoint (wsteczna kompatybilność)", ale **nieużywany nigdzie w klasie `TTS`** — `_resolve_engine`/`ENGINE_URLS` obsługują dobór URL; `API_URL` to martwa stała zostawiona dla ewentualnych zewnętrznych konsumentów modułu, których w repo nie ma.
  - `SynthResult.retries` (l.126) — pole zawsze `0`, nigdy nie wypełniane rzeczywistą liczbą prób z `_request_with_retry` (retry tam się dzieje, ale liczba prób nie jest zwracana na zewnątrz do `_batch_item`).
  - `add_voice`/`remove_voice` mutują globalny, dzielony między instancjami stan modułu `VOICES` bez synchronizacji (brak locka) — nieszkodliwe przy obecnym jednowątkowym wzorcu użycia w repo, ale ryzykowne jako publiczne API biblioteki ogólnego przeznaczenia.
  - Dostęp do prywatnego atrybutu `asyncio.Semaphore._loop` (l.226) — sprzężenie z wewnętrzną implementacją stdlib, oznaczone `type: ignore`, krucha zależność międzywersyjna.
  - `_run_sync` typowany jako `object -> object` zamiast generyków — osłabia bezpieczeństwo typów w całym sync API (3 metody muszą stosować `# type: ignore[return-value]`).
  - `DEFAULT_MAX_RETRIES = 100` (l.67) to bardzo wysoka wartość domyślna — bez świadomego nadpisania przez wołającego (jak robi `subtitle_to_speech.py:471` z `max_retries=2`) pojedynczy nieudany request może wykonać do 100 prób z narastającym (choć cappowanym na 5s) backoffem.
- **❌ niespójności ze stylem MangaShift:**
  - `_build_payload` (l.239-249) zawiera mały if per-silnik (`if self._api_url == API_URL_V7`) — to jest zaakceptowalny wzorzec wg samego dokumentu MangaShift (mały if do kształtu payloadu, nie do wyboru całej klasy/ścieżki), ale wciąż warto odnotować że **nie ma go w rejestrze** — decyzja "które pola dodać" jest wpisana w logikę serwisu zamiast być właściwością samego wpisu w `ENGINE_URLS`/osobnej strukturze per-engine (np. `dict[str, EngineSpec]` gdzie `EngineSpec` miałby pole `supports_voice_settings: bool`). To jest dokładnie analogiczny dług do `ENGINES_WITH_MODEL_CHOICE` opisanego w dokumencie wzorcowym jako "zdolność silnika trzymana w niewłaściwym miejscu" (`docelowa-architektura-jedno-zrodlo.md:222-223`).
  - Brak `Literal["v6", "v7"]` towarzyszącego `ENGINE_URLS` — MangaShift wymaga pary "rejestr (mapa runtime) + Literal (typ statyczny) obok siebie w tym samym pliku"; tutaj jest tylko strona runtime, typ silnika to gołe `str` (`engine: str = DEFAULT_ENGINE` w `__init__`, l.191).
  - Poza tym plik jest architektonicznie najbliższy wzorcowi spośród całego obszaru TTS — nie ma tu god-function, nie ma if-drzewa per silnik na poziomie wyboru implementacji (tylko na poziomie kształtu jednego requestu).
- **🔗 sprzężenia:**
  - Zależny od zewnętrznego, nieoficjalnego proxy `teamsp.org` (nie bezpośrednio od ElevenLabs) — jeśli proxy zmieni kontrakt API/wymaga innych nagłówków, cały moduł przestaje działać bez ostrzeżenia kompilacji; brak testów kontraktowych.
  - Współdzielony, mutowalny globalny stan `VOICES` między wszystkimi instancjami `TTS` w procesie — `subtitle_to_speech.py` nie korzysta z `add_voice`, ale każdy przyszły kod robiący to wpłynie na wszystkie równoległe instancje.
  - Jedyny konsument w repo (`subtitle_to_speech.py:433`) importuje klasę lokalnie zamiast przez DI — zmiana publicznego API `TTS`/`VoiceSettings` (np. rename parametru) cicho łamie wywołującego, wykrywalne tylko w runtime, nie przy imporcie modułu.

---

## 🧭 podsumowanie obszaru

- **Główne odpowiedzialności:** zamiana napisów na audio lektora przez jeden z 5 silników TTS
  (offline SAPI/Harpo, offline Balabolka/Ivona, online Edge x2 głosy, online ElevenBytes
  v2/v3 przez prywatne proxy), synchronizacja czasowa z timingiem napisów, opcjonalny
  post-processing prędkości/głośności (FFmpeg atempo/volume), finalny miks ścieżki lektora
  z istniejącą ścieżką audio do EAC3 gotowego do wgrania z powrotem do MKV.

- **Największe problemy (ranking):**
  1. **Brak rejestru silników TTS w `subtitle_to_speech.py`** (`generate_audio`, l.1108-1158)
     — 6-gałęziowy `if/elif` po dosłownych etykietach UI zamiast `dict[EngineId, Callable]` +
     `Literal` obok. To jest centralna niespójność ze stylem docelowym MangaShift w całym
     obszarze audytowanym.
  2. **God-method `srt_to_wav_elevenbytes`** (340 linii, `subtitle_to_speech.py:413-754`) —
     miesza parsowanie, cache, sieć z retry/backoff, DSP (resampling, atempo), budowę pliku
     i sprzątanie w jednej metodzie; brak podziału na warstwy serwis/pipeline z docelowej
     architektury.
  3. **Martwy kod** — `_pp_speed_audio` (l.772-796) i `_ffmpeg_post_process` (l.880-922) w
     `subtitle_to_speech.py` nie są nigdzie wołane; `API_URL` (l.58) w `tts_elevenbytes.py`
     nieużywany.
  4. **Rozproszone, sprzeczne hardkody sample rate** (22500/24000/44100 Hz) i inne magic
     values (`+7dB` w merge, `'IVONA 2 Agnieszka'`, nazwa głosu SAPI) bez jednego źródła
     prawdy per silnik.
  5. **Sekret (`API_KEY`) zahardkodowany w kodzie źródłowym** (`tts_elevenbytes.py:55`).
  6. **Niespójne kanały logowania** (`print()` vs `console.print`) w `subtitle_to_speech.py`.

- **Kandydaci do refaktoru na styl MangaShift:**
  - Wprowadzić `ENGINE_REGISTRY: dict[TtsEngineId, TtsEngineSpec]` (analogicznie do
    `services/<domena>/engines/__init__.py` w MangaShift) z towarzyszącym
    `Literal["harpo", "balabolka", "edge_zofia", "edge_marek", "elevenbytes_v6", "elevenbytes_v7"]`
    zamiast obecnych stringów-etykiet UI jako identyfikatorów biznesowych w `Settings.tts`.
  - Rozdzielić `label` (do wyświetlenia w CLI) od `engine_id` (klucz dispatchu) — dziś to ten
    sam string (`"TTS - Zosia - Harpo"` pełni obie role).
  - Rozbić `srt_to_wav_elevenbytes` na mniejsze, nazwane kroki (np. osobne funkcje/metody:
    czyszczenie tekstu, cache lookup, runda syntezy, budowa timeline PCM, konwersja WAV) —
    część już istnieje jako funkcje lokalne (`_synth_one`, `_decode_mp3`, `_atempo_pipe`), ale
    są zagnieżdżone zamiast być metodami/funkcjami modułowymi testowalnymi osobno.
  - `tts_elevenbytes.py` jest już najbliżej wzorca (rejestr `ENGINE_URLS` + serwis) — dobry
    punkt wyjścia/wzór stylu dla refaktoru reszty obszaru; brakuje mu tylko towarzyszącego
    `Literal` i przeniesienia `API_KEY` do configu/env.
  - Ujednolicić sample rate i inne stałe per silnik w jednym miejscu (np. jako pole w
    przyszłym `TtsEngineSpec`, nie jako rozproszone literały).

- **Pliki/funkcje martwe lub podejrzane:**
  - `SubtitleToSpeech._pp_speed_audio` (`subtitle_to_speech.py:772`) — brak wywołań.
  - `SubtitleToSpeech._ffmpeg_post_process` (`subtitle_to_speech.py:880`) — brak wywołań.
  - `SubtitleToSpeech.working_space_temp_alt_subs` (pole dataclass, `subtitle_to_speech.py:100`)
    — brak użycia w metodach tego pliku.
  - `tts_elevenbytes.API_URL` (`tts_elevenbytes.py:58`) — brak użycia poza deklaracją.
  - `SynthResult.retries` (`tts_elevenbytes.py:126`) — pole nigdy nie wypełniane rzeczywistą
    wartością (zawsze `0`).

---


# CZĘŚĆ 05 — utils

# RAPORT AUDYTU — utils (narzędzia pomocnicze)

---

## 📦 obszar: utils — pliki: `cool_animation.py`, `execution_timer.py`, `number_in_words.py`, `text_chunker.py`

**Rola obszaru w projekcie:** Zestaw czterech niezależnych narzędzi pomocniczych używanych
w różnych miejscach potoku ekstrakcja→napisy→TTS→merge: `cool_animation.py` i `execution_timer.py`
to narzędzia UX/diagnostyczne wołane z `start.py` (logo aplikacji, pomiar czasu wykonania),
a `number_in_words.py` i `text_chunker.py` to narzędzia przetwarzania tekstu wołane z
`modules/subtitle.py` przy przygotowywaniu napisów pod TTS (zamiana cyfr na słowa, dzielenie
tekstu na fragmenty mieszczące się w limicie silnika TTS).

**Zależności zewnętrzne obszaru:** `rich.console.Console` (execution_timer), `six.u`
(number_in_words — martwa zależność Python2/3, patrz niżej), `re`, `dataclasses`, `datetime`,
`time`, `threading`, `os`, `sys`, `typing` (biblioteka standardowa). Brak zależności
wewnątrzprojektowych (moduły w `utils/` nie importują niczego z `modules/` ani `start.py`) —
to jedyny obszar w projekcie spełniający zasadę MangaShift „moduły przenośne bez zależności
od projektu". Konsumenci: `start.py` (linie 32-33, 52, 544) i `modules/subtitle.py`
(linie 47-48, 368, 390, 420, 423).

---

## 📄 plik: `utils/cool_animation.py` (146 linii)

### przeznaczenie
Definiuje klasę `CoolAnimation` — efekt animacji tekstowej w terminalu (naprzemienna zmiana
wielkości liter + wirujący znak `|/-\`), używany jako logo/ekran powitalny aplikacji.
Wołany z `start.py:52` (`mm_avh_logo: CoolAnimation = CoolAnimation()`), blokuje wątek główny
do naciśnięcia Entera przez użytkownika. Nie jest częścią logiki biznesowej — czysto
kosmetyczny element startowy CLI.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `name`, `system` | os | wykrycie platformy (`nt`) i czyszczenie ekranu (`cls`/`clear`) |
| `sys` | stdlib | `sys.stdout.write` do pisania animacji bez nowej linii |
| `Thread` | threading | odpalenie `check_input` w tle, żeby nasłuchiwać Enter bez blokowania animacji |
| `sleep` | time | odstępy między klatkami animacji (0.075 s) |
| `List` | typing | adnotacja typu listy znaków |

### stałe / zmienne modułowe
Brak stałych modułowych — wszystko jest polem instancji.

### klasy

#### `class CoolAnimation` (linia 37) — zwykła klasa (nie dataclass, brak slots, brak dziedziczenia)
**Cel:** Wyświetla zapętloną animację tekstową w terminalu aż do wciśnięcia klawisza przez użytkownika.

**Pola (ustawiane w `__init__`, nie dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `load_str` | `str` | `"multimedia magic   audio visual heaven"` | tekst bazowy animacji |
| `ls_len` | `int` | `len(load_str)` | długość tekstu, używana jako modulo w pętli |
| `animation` | `str` | `"\|/-\\"` | zestaw znaków „spinnera" |
| `stop_animation` | `bool` | `False` | flaga sterująca pętlą `while` w `display()` |
| `show_border` | `bool` | `True` | czy otoczyć tekst ramką `╚═══ ... ═══╝` |
| `middle_offset` | `int` | `-2` | przesunięcie pozycji wstawienia znaku spinnera względem środka stringa |
| `use_animation` | `bool` | `True` | czy w ogóle wstawiać znak spinnera |

**Metody:**

##### `__init__(self, load_str: str = "multimedia magic   audio visual heaven", show_border: bool = True, middle_offset: int = -2, use_animation: bool = True) -> None` (linia 78)
- **Co robi:** Inicjalizuje wszystkie pola instancji wartościami z argumentów.
- **Przyjmuje:** `load_str` — tekst do animowania; `show_border` — flaga ramki;
  `middle_offset` — offset pozycji spinnera; `use_animation` — flaga włączająca spinner.
- **Zwraca:** `None`.
- **Efekty uboczne:** brak (czysta inicjalizacja pól).
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** docstring klasy (linia 64-66) deklaruje domyślny `middle_offset: int = 2`,
  a rzeczywisty kod ma `-2` (linia 79) — rozjazd dokumentacja/kod (drobna niespójność,
  nie błąd funkcjonalny).

##### `check_input(self) -> None` (linia 88)
- **Co robi:** Blokująco czeka na wejście z klawiatury (`input()`); po jego otrzymaniu lub
  przy `EOFError`/`KeyboardInterrupt` ustawia `stop_animation = True`.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** mutuje `self.stop_animation`; blokuje wątek, w którym jest odpalona
  (uruchamiana jako osobny wątek daemon z `display()`).
- **Woła:** wbudowane `input()`.
- **Wyjątki:** łapie `EOFError` i `KeyboardInterrupt` — w obu przypadkach traktuje jak sygnał
  zatrzymania (brak logowania, ciche przechwycenie).
- **Uwagi:** brak walidacji treści wejścia — dowolny Enter/EOF zatrzymuje animację.

##### `display(self) -> None` (linia 98)
- **Co robi:** Czyści ekran, odpala `check_input` w wątku daemon, po czym w pętli `while not
  self.stop_animation` co 150 ms (2×`sleep(0.075)`) zamienia wielkość jednej litery na
  przeciwną (cykliczne przejście po `load_str`), wstawia obracający się znak spinnera na
  pozycji `środek + middle_offset`, opcjonalnie owija tekst ramką i wypisuje go w miejscu
  (`\r` + kody ANSI koloru) na stdout. Po zakończeniu pętli ponownie czyści ekran.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None`.
- **Efekty uboczne:** `system("cls"/"clear")` (wywołanie procesu systemowego), pisze do
  `sys.stdout`, mutuje `self.load_str` (nadpisuje go wynikiem `res` w każdej iteracji —
  efekt uboczny na stanie obiektu), odpala wątek `Thread`.
- **Woła:** `self.check_input` (w wątku), `system()`, `sys.stdout.write()`.
- **Wyjątki:** brak jawnej obsługi; `load_str_list[i]` może rzucić `IndexError`, jeśli
  `ls_len` i faktyczna długość `load_str` się rozjadą (patrz uwaga niżej).
- **Uwagi (bug):** linia 138 `self.load_str = res` nadpisuje `load_str` łańcuchem `res`,
  który ma tę samą długość co oryginał — więc `ls_len` pozostaje poprawny; ryzyko jest
  czysto teoretyczne, ale to niepotrzebna mutacja stanu (funkcja mogłaby operować na
  zmiennej lokalnej). `count_time` (linia 107, 142) jest liczony, ale nigdy nie używany —
  martwa zmienna. Format ANSI `"\033[1;37m"` i `"\033[0m"` to magic values bez nazwanych
  stałych. `system("cls")`/`system("clear")` powtórzone identycznie w liniach 102-105 i
  143-146 — duplikacja (mogłaby być osobną metodą `_clear_screen`).

### funkcje modułowe (poza klasami)
Brak — cała logika jest w klasie.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** moduł samodzielny (zero zależności od reszty
  projektu), jasno opisany docstring modułowy z przykładami użycia, sensowne typowanie
  sygnatur metod (`-> None`).
- **⚠️ dług techniczny / code smells:** duplikacja czyszczenia ekranu (`cool_animation.py:102-105`
  vs `143-146`); martwa zmienna `count_time` (`cool_animation.py:107,142`); magic values ANSI
  (`cool_animation.py:133,136`); mutacja `self.load_str` wewnątrz pętli renderującej zamiast
  zmiennej lokalnej (`cool_animation.py:138`); rozjazd docstringa i domyślnej wartości
  `middle_offset` (`cool_animation.py:65` vs `79`); brak testów (cała logika czasowa/I-O
  utrudnia testowanie, ale nic nie jest wydzielone do testowalnej postaci).
- **❌ niespójności ze stylem MangaShift:** brak `@dataclass(slots=True)` mimo że klasa jest
  czystym kontenerem konfiguracji + logiki (idealny kandydat na dataclass, wzorowany np.
  na `execution_timer.py`); brak podziału odpowiedzialności — jedna metoda `display()` robi
  naraz: czyszczenie ekranu, zarządzanie wątkiem, transformację tekstu, renderowanie i pętlę
  sterującą (god-method, ~45 linii); brak dependency injection (bezpośrednie wywołania
  `system()`/`sys.stdout` zamiast wstrzykniętego „renderera").
- **🔗 sprzężenia:** zero sprzężeń z resztą projektu poza punktem wejścia w `start.py:32,52`
  (`from utils.cool_animation import CoolAnimation`). Zmiana sygnatury `display()` złamie
  tylko `start.py`.

---

## 📄 plik: `utils/execution_timer.py` (130 linii)

### przeznaczenie
Dostarcza `ExecutionTimer` — context manager (i towarzyszącą funkcję dekoratorową
`execution_timer`) do mierzenia i ładnego wypisywania czasu wykonania bloku kodu z dokładnością
do nanosekund, z użyciem `rich` do kolorowania. Używany w `start.py:544` jako dekorator na
funkcji `main()` — jedyne miejsce użycia w projekcie.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `datetime` | datetime | znaczniki czasu startu/końca (`start_date`, `end_date`) |
| `perf_counter_ns` | time | precyzyjny pomiar czasu wykonania w nanosekundach |
| `dataclass` | dataclasses | dekorator klasy `ExecutionTimer` |
| `Console` | rich.console | kolorowe wypisywanie raportu czasu na konsolę |

### stałe / zmienne modułowe
Brak stałych modułowych.

### klasy

#### `class ExecutionTimer` (linia 24) — `@dataclass(slots=True)`
**Cel:** Context manager mierzący czas wykonania bloku kodu (start/koniec/czas trwania) i
wypisujący sformatowany raport przez `rich.Console`.

**Pola (dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `start_date` | `datetime` | `None` | znacznik daty/czasu startu (ustawiany w `__post_init__`) |
| `end_date` | `datetime` | `None` | znacznik daty/czasu końca (ustawiany w `__exit__`) |
| `start_time_ns` | `int` | `None` | licznik `perf_counter_ns()` na starcie |
| `end_time_ns` | `int` | `None` | licznik `perf_counter_ns()` na końcu |
| `console` | `Console` | `Console()` | instancja rich Console do wypisywania |

**Metody:**

##### `__post_init__(self)` (linia 36)
- **Co robi:** Ustawia `start_date` i `start_time_ns` natychmiast po konstrukcji obiektu
  (czyli zanim wejdzie się w blok `with`).
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None` (niejawnie).
- **Efekty uboczne:** mutuje `self.start_date`, `self.start_time_ns`.
- **Woła:** `datetime.now()`, `perf_counter_ns()`.
- **Wyjątki:** brak.
- **Uwagi:** oznacza to, że pomiar czasu zaczyna się w momencie konstrukcji obiektu,
  a nie w momencie wejścia do `__enter__` — jeśli ktoś tworzy instancję wcześniej i wchodzi
  w `with` później, pomiar będzie zawyżony. W obecnym użyciu (`with ExecutionTimer():`)
  to nieistotne, bo konstrukcja i `__enter__` następują natychmiast po sobie.

##### `__enter__(self) -> 'ExecutionTimer'` (linia 40)
- **Co robi:** Zwraca samego siebie jako obiekt kontekstu.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `self`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak.

##### `__exit__(self, exc_type, exc_val, exc_tb)` (linia 43)
- **Co robi:** Zapisuje `end_date`/`end_time_ns` i wypisuje raport przez `display_time()`.
- **Przyjmuje:** standardowe argumenty protokołu context managera (typy niejawne — brak
  adnotacji, mimo że reszta pliku jest otypowana).
- **Zwraca:** `None` (niejawnie — co oznacza, że wyjątki z bloku `with` NIE są tłumione,
  bo `__exit__` bez `return True` propaguje wyjątek dalej).
- **Efekty uboczne:** mutuje `self.end_date`, `self.end_time_ns`; wypisuje na konsolę.
- **Woła:** `self.display_time()`.
- **Wyjątki:** łapie `AttributeError` i w takim wypadku robi `print('An error occurred:
  __exit__')` zamiast `self.console.print` — niespójność stylu logowania (goły `print` obok
  reszty korzystającej z `rich`). Gołe `except AttributeError` bez re-raise/loggera to code
  smell — połyka błąd cicho, mogąc ukryć prawdziwy problem w `display_time()`.

##### `current_datetime(date: datetime) -> str` (linia 51, `@staticmethod`)
- **Co robi:** Formatuje obiekt `datetime` do stringa `YYYY-MM-DD HH:MM:SS` z tagami
  kolorów rich (`[yellow]...[white bold]...`).
- **Przyjmuje:** `date` — obiekt `datetime` do sformatowania.
- **Zwraca:** `str` z markupem rich.
- **Efekty uboczne:** brak.
- **Woła:** nic zewnętrznego (tylko formatowanie f-string).
- **Wyjątki:** brak jawnych; rzuci, jeśli `date` jest `None` (możliwe, bo pole domyślnie
  `None` — patrz uwaga o typach niżej).

##### `calculate_duration(self) -> str` (linia 60)
- **Co robi:** Liczy różnicę `end_time_ns - start_time_ns` i rozbija ją na godziny, minuty,
  sekundy, milisekundy, mikrosekundy, nanosekundy, zwracając sformatowany string z markupem rich.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `str` w formacie `HH:MM:SS:ms:µs:ns`.
- **Efekty uboczne:** brak.
- **Woła:** `divmod()` wielokrotnie.
- **Wyjątki:** `TypeError`, jeśli `end_time_ns`/`start_time_ns` są nadal `None`
  (np. wywołanie metody przed `__exit__`).
- **Uwagi:** `map(int, divmod(...))` jest zbędne — `divmod` na `int` już zwraca `int`
  (martwy/nadmiarowy kod, linie 67-69).

##### `calculate_duration_alt(self) -> tuple[float, ...]` (linia 77)
- **Co robi:** Alternatywne liczenie czasu trwania — zwraca krotkę (godziny, minuty,
  sekundy) jako wartości zmiennoprzecinkowe (bez rozbicia na jednostki dyskretne).
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `tuple[float, float, float]` — `(hours_alt, minutes_alt, seconds_alt)`.
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** `TypeError`, jeśli czasy są `None`.
- **Uwagi:** duplikuje logikę `calculate_duration()` (ta sama różnica `end_time_ns -
  start_time_ns` liczona ponownie) — dwie metody liczące to samo w różnych formatach,
  zamiast jednej metody bazowej + formatowania. Nazwa `_alt` sugeruje tymczasowy/dodany
  później charakter (code smell nazewniczy).

##### `display_time(self)` (linia 90)
- **Co robi:** Składa pełny raport (start, koniec, czas trwania w formacie HH:MM:SS:ms:µs:ns
  oraz w godzinach/minutach/sekundach jako float) i wypisuje go linia po linii przez
  `self.console.print`.
- **Przyjmuje:** nic poza `self`.
- **Zwraca:** `None` (brak adnotacji zwrotu — niespójność typowania w tym samym pliku,
  gdzie inne metody mają `-> str`).
- **Efekty uboczne:** 9 wywołań `self.console.print` (I/O na konsolę).
- **Woła:** `self.current_datetime()` (×2), `self.calculate_duration()`,
  `self.calculate_duration_alt()`.
- **Wyjątki:** propaguje wyjątki z wołanych metod.
- **Uwagi:** literalny string `'YYYY-MM-DD {duration}'` w linii 110 — `duration` już
  zawiera tylko `HH:MM:SS:ms:µs:ns` (bez daty), więc etykieta „YYYY-MM-DD" przed nim jest
  myląca/błędna (kopiuj-wklej z linii formatującej nagłówek, niedopasowana treść — drobny bug
  kosmetyczny w wyświetlanym tekście).

### funkcje modułowe (poza klasami)

##### `execution_timer(func)` (linia 120)
- **Co robi:** Dekorator funkcyjny opakowujący dowolną funkcję w `with ExecutionTimer():`,
  tak by przy każdym wywołaniu funkcji zmierzyć i wypisać czas jej wykonania.
- **Przyjmuje:** `func` — dowolna funkcja (brak adnotacji typu, brak `*args`/`**kwargs`
  otypowania, brak `functools.wraps` — metadane oryginalnej funkcji, jak `__name__` i
  docstring, giną po udekorowaniu).
- **Zwraca:** `wrapper` — funkcję opakowującą.
- **Efekty uboczne:** brak bezpośrednich (deleguje do `ExecutionTimer`).
- **Woła:** `ExecutionTimer()` jako context manager, następnie `func(*args, **kwargs)`.
- **Wyjątki:** propaguje wyjątki z `func`.
- **Uwagi:** brak `functools.wraps(func)` na `wrapper` (linia 125) — standardowy brakujący
  element przy pisaniu dekoratorów w Pythonie; powoduje utratę `__name__`/`__doc__` funkcji
  udekorowanej (widoczne np. w introspekcji, debuggerze, `help()`).

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** JEDYNY plik w tym obszarze zgodny ze stylem
  MangaShift — `@dataclass(slots=True)` (`execution_timer.py:23`), sensowne typowanie
  większości sygnatur, jasny podział na metody pomocnicze (`current_datetime`,
  `calculate_duration`, `calculate_duration_alt`, `display_time`), poprawna implementacja
  protokołu context managera.
- **⚠️ dług techniczny / code smells:** goły `except AttributeError` z cichym `print`
  zamiast `console.print`/loggera (`execution_timer.py:48-49`); duplikacja logiki liczenia
  czasu trwania w dwóch metodach (`calculate_duration` linia 60 i `calculate_duration_alt`
  linia 77); zbędne `map(int, divmod(...))` na wartościach już całkowitych
  (`execution_timer.py:67-69`); błędny/mylący literał `'YYYY-MM-DD {duration}'`
  (`execution_timer.py:110`); brak `functools.wraps` w dekoratorze
  (`execution_timer.py:120-130`); pola dataclass typowane jako `datetime`/`int` ale z
  defaultem `None` bez `Optional[...]`/`| None` w adnotacji (`execution_timer.py:30-33`) —
  niezgodność z faktycznym typem (mypy by to złapał, tu nic nie pilnuje).
- **❌ niespójności ze stylem MangaShift:** pole `console: Console = Console()` jako
  domyślna wartość dataclass (`execution_timer.py:34`) tworzy nową instancję `Console` przy
  każdym wywołaniu (nie jest to `mutable default` w klasycznym sensie Pythona dzięki
  `@dataclass`, ale to hardkodowana zależność zamiast dependency injection — MangaShift
  wymaga DI, tu `Console` powinna być wstrzykiwalna z zewnątrz, żeby dało się przekierować
  wyjście w testach). Brak testów jednostkowych dla logiki liczenia czasu (łatwo testowalna,
  ale nic nie istnieje).
- **🔗 sprzężenia:** sprzężony z `rich.console.Console` (twardy import, brak abstrakcji);
  jedyny konsument to `start.py:33,544` przez dekorator `@execution_timer` na `main()`.
  Zmiana sygnatury dekoratora złamie punkt wejścia aplikacji.

---

## 📄 plik: `utils/number_in_words.py` (270 linii)

### przeznaczenie
Dostarcza klasę `NumberInWords` konwertującą liczby (int/float/str) na słowny zapis w języku
polskim (liczebniki, kwoty w złotych/groszach, odmiana rzeczowników wg liczby). Używana w
`modules/subtitle.py:47,420,423` do zamiany cyfr w tekście napisów na słowa przed
przepuszczeniem przez silnik TTS (silniki TTS często źle wymawiają cyfry).

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | dzielenie tekstu na tokeny w `convert_numbers_in_text` |
| `dataclass`, `field` | dataclasses | dekorator klasy i domyślne fabryki list |
| `List`, `Union` | typing | adnotacje typów |
| `u` | six | funkcja no-op konwersji do unicode (relikt Python 2) |

### stałe / zmienne modułowe
Brak stałych modułowych — wszystkie tablice liczebników są polami dataclass (patrz niżej).

### klasy

#### `class NumberInWords` (linia 57) — `@dataclass` (BEZ `slots=True`)
**Cel:** Kontener tablic liczebników polskich + metody konwertujące liczby na słowa.

**Pola (dataclass, wszystkie `field(default_factory=lambda: [...])`):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `UNITS` | `list` | 10 elementów `["", "jeden", ..., "dziewięć"]` | jednostki 0-9 |
| `TENS` | `list` | 10 elementów `["", "dziesięć", ..., "dziewięćdziesiąt"]` | dziesiątki (wielokrotności 10) |
| `TEENS` | `list` | 10 elementów `["dziesięć", ..., "dziewiętnaście"]` | liczby 10-19 (nastki) |
| `HUNDREDS` | `list` | 10 elementów `["", "sto", ..., "dziewięćset"]` | setki |
| `BIG` | `list` | lista list `[["x","x","x"], ["tysiąc","tysiące","tysięcy"], ...]` | nazwy rzędów wielkości (tysiąc/milion/miliard/bilion) w 3 formach gramatycznych |
| `ZLOTYS` | `list` | `["złoty", "złote", "złotych"]` | formy odmiany „złoty" |
| `GROSZES` | `list` | `["grosz", "grosze", "groszy"]` | formy odmiany „grosz" |

**Metody:**

##### `_number_in_words_3digits(self, number: int) -> str` (linia 99)
- **Co robi:** Konwertuje liczbę 0-999 na słowa polskie (setki + dziesiątki/nastki + jednostki).
- **Przyjmuje:** `number` — liczba całkowita, zakładana w zakresie 0-999 (brak walidacji
  zakresu).
- **Zwraca:** `str` — słowny zapis, np. `123` → `"sto dwadzieścia trzy"`.
- **Efekty uboczne:** brak.
- **Woła:** nic zewnętrznego (indeksuje `self.HUNDREDS`, `self.TEENS`, `self.TENS`, `self.UNITS`).
- **Wyjątki:** `IndexError`, jeśli `number` poza zakresem 0-999 (np. `number=1500` da
  `hundred = (1500//100)%10 = 5` — działa przez modulo, ale semantycznie błędnie dla liczb
  ≥1000 — funkcja jest prywatna i zakłada, że wywołujący (`number_in_words`) już podzielił
  liczbę na trójki, więc w praktyce nie jest wołana poza zakresem).
- **Uwagi:** nazwa z prefiksem `_` sugeruje prywatność, konwencja zachowana.

##### `_case(self, number: int) -> int` (linia 119)
- **Co robi:** Zwraca indeks gramatycznej formy liczby mnogiej (0=liczba pojedyncza,
  1=forma „2-4", 2=forma „5+/11-19") wg reguł polskiej odmiany rzeczowników przy liczebnikach.
- **Przyjmuje:** `number` — liczba całkowita.
- **Zwraca:** `int` — 0, 1 lub 2 (indeks do tablic typu `ZLOTYS`/`GROSZES`/`BIG[i]`).
- **Efekty uboczne:** brak.
- **Woła:** nic.
- **Wyjątki:** brak jawnych.
- **Uwagi:** logika w jednej złożonej wyrażeniowej instrukcji (linia 126) — czytelna, ale
  gęsta; brak testów jednostkowych weryfikujących poprawność gramatyczną (np. `_case(11)` czy
  `_case(112)` — przypadki "nastek" w liczbach złożonych).

##### `number_in_words(self, number: Union[int, float, str]) -> str` (linia 128)
- **Co robi:** Główna metoda konwersji — przyjmuje liczbę w dowolnej z 3 postaci, obsługuje
  część całkowitą i dziesiętną (separator `.` lub `,`), dzieli część całkowitą na trójki
  cyfr, konwertuje każdą trójkę i dokleja odpowiedni rząd wielkości (tysiąc/milion/...),
  rekurencyjnie konwertuje część dziesiętną po słowie „przecinek".
- **Przyjmuje:** `number` — `int`, `float` lub `str` (string obsługuje bardzo długie liczby,
  gdzie `float` straciłby precyzję — udokumentowane w docstringu modułu, linia 21).
- **Zwraca:** `str` — pełny słowny zapis liczby.
- **Efekty uboczne:** brak.
- **Woła:** `self._number_in_words_3digits()`, `self._case()`, rekurencyjnie samą siebie
  (`self.number_in_words()` dla części dziesiętnej, linia 172).
- **Wyjątki:** `ValueError`, jeśli `number` (jako string) nie da się sparsować przez
  `int()`/`split()` (np. wielokrotne kropki, nieliczbowe znaki); `IndexError`, jeśli liczba
  ma więcej niż 5 grup trójkowych (tj. ≥10^15, poza zakresem `BIG` — który ma tylko 5
  elementów: x/tysiąc/milion/miliard/bilion, linia 84-91) — funkcja wywali się na liczbach
  ≥ bilion bilionów... a właściwie już przy grupie nr 5 (10^15) rzuci `IndexError` na
  `self.BIG[5]`, mimo że docstring modułu (linia 21-22) reklamuje wsparcie liczb 30-cyfrowych.
- **Uwagi (bug potencjalny):** deklarowane w docstringu wsparcie dla liczb do 30 cyfr
  (15+15 wokół przecinka) jest sprzeczne z faktycznym zakresem `BIG` (5 rzędów = do 10^15-1)
  — przy realnie długich liczbach kod rzuci wyjątek. W praktyce dla napisów anime (liczby w
  dialogach) to nie problem, ale komentarz wprowadza w błąd.

##### `thing_in_words(self, number: int, thing: List[str]) -> str` (linia 175)
- **Co robi:** Łączy słowny zapis liczby z poprawną odmianą rzeczownika (np. „pięć jabłek").
- **Przyjmuje:** `number` — liczba; `thing` — lista 3 form odmiany rzeczownika
  `[pojedyncza, 2-4, 5+]`.
- **Zwraca:** `str` — liczba słownie + odmieniony rzeczownik.
- **Efekty uboczne:** brak.
- **Woła:** `self.number_in_words()`, `self._case()`.
- **Wyjątki:** `IndexError`, jeśli `thing` ma mniej niż 3 elementy.

##### `amount_in_words(self, number: float, fmt: int = 0) -> str` (linia 188)
- **Co robi:** Konwertuje kwotę pieniężną (złote + grosze) na słowa; grosze albo jako
  `"xx/100"` (fmt=0), albo słownie odmienione (fmt≠0).
- **Przyjmuje:** `number` — kwota jako float; `fmt` — tryb formatowania groszy
  (0 = cyfrowo, inaczej = słownie).
- **Zwraca:** `str` — pełny zapis kwoty.
- **Efekty uboczne:** brak.
- **Woła:** `self.thing_in_words()` (×2 lub ×1), `self.number_in_words()` pośrednio.
- **Wyjątki:** brak jawnych; błędy zaokrąglenia float mogą teoretycznie dać `lgroszes=100`
  przy wartościach granicznych (`int(number*100+0.5) % 100` — modulo neutralizuje przypadek
  100, więc to zabezpieczone, ale niejawnie).
- **Uwagi:** `fmt: int = 0` jako flaga boolean-jak-int to magic value bez nazwanej stałej/enum
  (np. `fmt=1` nieudokumentowane jako konkretna liczba w sygnaturze — tylko w docstringu).

##### `convert_numbers_in_text(self, text: str) -> str` (linia 206)
- **Co robi:** Przechodzi znak po znaku przez cały tekst, wykrywa sekwencje cyfr (w tym
  z separatorami dziesiętnymi `.`/`,` między cyframi), konwertuje je na słowa przez
  `number_in_words()`, zachowując resztę tekstu (interpunkcję, litery) bez zmian. Obsługuje
  przypadki typu `69.2_3` (wielokrotne znaki specjalne w „liczbie") przez rozbicie na części.
- **Przyjmuje:** `text` — dowolny tekst z ewentualnymi liczbami.
- **Zwraca:** `str` — tekst z liczbami zamienionymi na słowa.
- **Efekty uboczne:** brak (funkcja czysta, buduje nowy string).
- **Woła:** `self.number_in_words()` wielokrotnie, `re.split()`.
- **Wyjątki:** propaguje `ValueError`/`IndexError` z `number_in_words()` przy zdegenerowanych
  wejściach.
- **Uwagi:** to najbardziej złożona funkcja w pliku — zagnieżdżone pętle `for`/`for...else`
  (linia 219-228, konstrukcja `for...else` używana jako „nie znaleziono duplikatu znaku
  specjalnego" — subtelna, mało czytelna technika Pythona), lista `special_chars`
  zdefiniowana lokalnie przy każdym wywołaniu zamiast jako stała modułowa/klasowa (linia
  212-213, ~30 elementów — powinna być `ClassVar`/stała modułowa, bo tworzenie tej listy przy
  każdym wywołaniu to niepotrzebny narzut i duplikacja danych). Zmienna `number_in_words`
  (linie 222,230,242,262) przesłania nazwę metody `self.number_in_words` w lokalnym scope —
  mylący shadowing nazw (nie powoduje bugu bo to zmienna lokalna, ale utrudnia czytanie i
  grep). Docstring metody sam przyznaje: „Yes is not perfect, but it works in most cases. If
  you want grammatical correctness use AI." (linia 208) — świadomie udokumentowany dług.

### funkcje modułowe (poza klasami)
Brak — cała logika w klasie `NumberInWords`.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** bogaty, dobrze udokumentowany docstring modułowy
  z przykładami (linie 1-47); logika liczebników polskich (przypadki gramatyczne, rzędy
  wielkości) jest kompletna i poprawnie oddaje reguły języka polskiego; `@dataclass` zamiast
  ręcznego `__init__` dla tablic.
- **⚠️ dług techniczny / code smells:** import `from six import u` — relikt kompatybilności
  Python 2/3 (`number_in_words.py:53`), w Python 3 `u("tekst")` jest tożsame z `"tekst"` —
  całkowicie zbędna zależność zewnętrzna (`six`) do funkcji no-op, powinna zostać usunięta;
  lista `special_chars` tworzona od nowa przy każdym wywołaniu `convert_numbers_in_text`
  zamiast być stałą (`number_in_words.py:212-213`); zmienna lokalna `number_in_words`
  przesłaniająca nazwę metody (`number_in_words.py:222,230,242,262`); niespójność między
  reklamowanym zakresem (30 cyfr, docstring linia 21) a faktycznym limitem `BIG` (5 rzędów,
  `number_in_words.py:84-91`) — potencjalny `IndexError` przy bardzo dużych liczbach;
  konstrukcja `for...else` (linia 219-228) obniżająca czytelność; brak walidacji zakresu w
  `_number_in_words_3digits` (linia 99) — funkcja milcząco zakłada poprawne wejście.
- **❌ niespójności ze stylem MangaShift:** `@dataclass` bez `slots=True` (jedyny plik obok
  `text_chunker.py`, gdzie klasa mogłaby być bezstanowa — te tablice liczebników to de facto
  stałe, nie stan instancji; MangaShift wymagałby albo `slots=True`, albo wyniesienia tablic
  poza klasę jako moduły stałe, skoro nigdy się nie zmieniają między instancjami); mieszanie
  odpowiedzialności — jedna klasa robi zarówno „słownikowanie" liczb, jak i parsowanie
  całego wolnego tekstu (`convert_numbers_in_text`) — w MangaShift byłby to osobny
  „tokenizer" wstrzykiwany do serwisu konwersji, nie metoda w tej samej klasie co czyste
  funkcje liczbowe.
- **🔗 sprzężenia:** zależność zewnętrzna od `six` tylko dla funkcji no-op — łatwa do
  usunięcia bez zmiany zachowania. Jedyny konsument: `modules/subtitle.py:47,420,423`
  (`from utils.number_in_words import NumberInWords`, `number_in_words =
  NumberInWords()`, `number_in_words.convert_numbers_in_text(sub.text)`). Zmiana sygnatury
  `convert_numbers_in_text` złamie pipeline generowania napisów pod TTS.

---

## 📄 plik: `utils/text_chunker.py` (177 linii)

### przeznaczenie
Dostarcza narzędzia dzielenia długiego tekstu na mniejsze fragmenty (chunki) wg limitu
znaków lub słów, respektując granice akapitów/zdań/fraz/słów (żeby nie ciąć w środku zdania).
Używane w `modules/subtitle.py:48,368,390` (funkcja `chunk_text`) do dzielenia tekstu napisów
na fragmenty mieszczące się w limicie wejściowym silnika TTS. Zawiera też blok
`if __name__ == '__main__':` z przykładowym tekstem demo — plik służy zarówno jako biblioteka,
jak i skrypt testowy uruchamialny bezpośrednio.

### importy (co i po co)
| import | źródło | użyty do czego |
|--------|--------|----------------|
| `re` | stdlib | wyrażenia regularne do dzielenia tekstu na akapity/zdania/frazy/słowa |

### stałe / zmienne modułowe
Brak stałych modułowych — wszystkie parametry (limity, wzorce) są przekazywane jako
argumenty konstruktorów lub zapisane inline w regexach.

### klasy

#### `class LatinPunctuator` (linia 4) — zwykła klasa, brak `__init__` (bezstanowa)
**Cel:** Dostarcza metody dzielenia tekstu na akapity/zdania/frazy/słowa wg reguł
interpunkcyjnych (głównie zachodnich/łacińskich, ale regexy zawierają też znaki CJK:
`『』「」„”«»〈〉`).

**Metody:**

##### `getParagraphs(self, text)` (linia 5)
- **Co robi:** Dzieli tekst na akapity po sekwencjach ≥2 znaków nowej linii (z opcjonalnymi
  białymi znakami między nimi).
- **Przyjmuje:** `text` — dowolny string (brak adnotacji typu — cały plik nie ma type hints,
  w przeciwieństwie do pozostałych 3 plików obszaru).
- **Zwraca:** `list[str]` — lista akapitów z zachowanymi separatorami (rekombinacja).
- **Efekty uboczne:** brak.
- **Woła:** `re.split()`, `self._recombine()`.
- **Wyjątki:** brak jawnych.

##### `getSentences(self, text)` (linia 8)
- **Co robi:** Dzieli tekst na zdania po `.`/`!`/`?`/`…` + białym znaku, z listą wyjątków
  skrótów (`Mr`, `Dr`, `Assn`, `Capt` itd.), żeby nie ciąć po skrócie.
- **Przyjmuje:** `text` — string.
- **Zwraca:** `list[str]` — lista zdań.
- **Efekty uboczne:** brak.
- **Woła:** `re.split()`, `self._recombine()` (z drugim argumentem `nonPunc` — regexem
  wyjątków skrótów).
- **Wyjątki:** brak jawnych.
- **Uwagi:** lista skrótów (linia 10) jest hardkodowana inline w regexie — angielskie skróty
  (`Mr`, `Dr`, `Capt`, `Gov`...) w projekcie polskojęzycznym (napisy PL) — prawdopodobnie
  martwy/nieadekwatny fragment przeniesiony z jakiejś biblioteki anglojęzycznej bez
  dostosowania do polskich skrótów (`p.`, `godz.`, `ul.`, `itd.` nie są tu uwzględnione).

##### `getPhrases(self, sentence)` (linia 12)
- **Co robi:** Dzieli zdanie na frazy po przecinkach/średnikach/dwukropkach/myślnikach/
  cudzysłowach różnych systemów pisma/nawiasach/wielokropku/gwiazdce/apostrofie.
- **Przyjmuje:** `sentence` — string (pojedyncze zdanie).
- **Zwraca:** `list[str]` — lista fraz.
- **Efekty uboczne:** brak.
- **Woła:** `re.split()`, `self._recombine()`.
- **Wyjątki:** brak jawnych.
- **Uwagi:** regex (linia 14) zawiera zduplikowany wzorzec cudzysłowu `"..."` obok `"` —
  potencjalna redundancja we wzorcu (trudna do jednoznacznej oceny bez testów regresowych,
  ale sugeruje kopiuj-wklej bez czyszczenia).

##### `getWords(self, sentence)` (linia 16)
- **Co robi:** Dzieli frazę na słowa i znaki interpunkcyjne/białe jako osobne tokeny,
  łącząc niepunktacyjne separatory (spacje, myślniki) z poprzednim tokenem zamiast
  zostawiać je osobno.
- **Przyjmuje:** `sentence` — string.
- **Zwraca:** `list[str]` — lista tokenów (słowa + doklejone separatory).
- **Efekty uboczne:** brak.
- **Woła:** `re.split()`, `re.match()` w pętli.
- **Wyjątki:** brak jawnych.
- **Uwagi:** ręczna pętla `while i < len(tokens)` z krokiem `i += 2` (linia 22-30) do obsługi
  naprzemiennych grup przechwyconych przez `re.split()` z grupą — działa, ale nieoczywiste
  bez komentarza wyjaśniającego dlaczego krok wynosi 2 (para: token + separator). Regex
  w linii 26 używa mieszanych cudzysłowów `„"` (prosty i typograficzny) niespójnie
  z linią 19 (`„"`) — możliwa literówka między wariantami znaków Unicode, trudna do
  wychwycenia wzrokowo.

##### `_recombine(self, tokens, nonPunc=None)` (linia 33)
- **Co robi:** Pomocnicza metoda składająca z powrotem pary (część, separator) zwrócone
  przez `re.split()` z grupą przechwytującą; jeśli podano `nonPunc` (regex wyjątków) i
  poprzedni fragment pasuje do wzorca wyjątku, dokleja bieżącą część do poprzedniej zamiast
  traktować jako nowy element (używane do obsługi skrótów w `getSentences`).
- **Przyjmuje:** `tokens` — lista naprzemiennych (treść, separator) z `re.split`; `nonPunc`
  — opcjonalny wzorzec regex określający, kiedy NIE traktować podziału jako granicy.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `re.match()` (pośrednio przez `nonPunc` sprawdzane jako `in`/dopasowanie —
  a właściwie `result[-1] in nonPunc` (linia 38) używa operatora `in` na wzorcu regex jako
  na sekwencji, co jest podejrzane: `nonPunc` to string wzorca regex, a `in` sprawdza
  podłańcuch, NIE dopasowanie regex — to wygląda na bug: powinno być `re.search(nonPunc,
  result[-1])`, a jest zwykłe sprawdzanie podciągu tekstu wzorca regex w tekście wyniku.
- **Wyjątki:** brak jawnych.
- **Uwagi (bug):** linia 38 `if nonPunc and result and result[-1] in nonPunc:` — `nonPunc`
  jest surowym stringiem regexu (przekazywanym z `getSentences`, linia 10), a `in` na
  stringu sprawdza wystąpienie podciągu, nie dopasowanie wzorca. To prawdopodobnie
  niedziałająca zgodnie z zamierzeniem logika wykrywania skrótów — wymaga weryfikacji
  testem, bo obecna implementacja raczej nigdy nie trafia w warunek tak, jak sugeruje
  nazwa `nonPunc` (wzorzec regex ze znakami specjalnymi typu `\b`, `\w`, `\.` nigdy nie
  wystąpi jako dosłowny podciąg w tekście wynikowym).

#### `class WordBreaker` (linia 45) — zwykła klasa z `__init__`
**Cel:** Dzieli tekst na fragmenty wg limitu liczby SŁÓW, zachowując granice zdań/fraz i
łącząc krótkie frazy w grupy do limitu.

**Pola (ustawiane w `__init__`, nie dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `wordLimit` | brak adnotacji | wymagany arg | maksymalna liczba słów w jednym fragmencie |
| `punctuator` | brak adnotacji | wymagany arg | instancja `LatinPunctuator` (dependency injection przez konstruktor) |

**Metody:**

##### `__init__(self, wordLimit, punctuator)` (linia 46)
- **Co robi:** Zapisuje limit słów i instancję punktatora.
- **Przyjmuje:** `wordLimit` — limit; `punctuator` — obiekt z metodami `getSentences`/
  `getPhrases`/`getWords`.
- **Zwraca:** `None` (niejawnie).
- **Efekty uboczne:** brak poza przypisaniem pól.
- **Woła:** nic.
- **Wyjątki:** brak.
- **Uwagi:** to jedyne miejsce w całym obszarze `utils`, gdzie widać wzorzec zbliżony do
  dependency injection (wstrzyknięcie `punctuator` zamiast tworzenia go wewnątrz) — pozytywny
  wyjątek, choć bez typowania i bez interfejsu/protokołu formalizującego kontrakt.

##### `breakText(self, text)` (linia 50)
- **Co robi:** Dzieli cały tekst na zdania, a potem każde zdanie na fragmenty wg limitu słów,
  spłaszczając wynik do jednej listy.
- **Przyjmuje:** `text` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getSentences()`, `self.breakSentence()` (w list comprehension).
- **Wyjątki:** brak jawnych.

##### `breakParagraph(self, text)` (linia 53)
- **Co robi:** Dzieli akapit na frazy (bez dalszego łączenia wg limitu).
- **Przyjmuje:** `text` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getPhrases()`.
- **Wyjątki:** brak jawnych.
- **Uwagi:** nazwa sugeruje analogię do `CharBreaker.breakParagraph`, ale semantyka inna —
  tu nie ma łączenia wg limitu (`merge`), tylko goły podział na frazy — niespójność API
  między `WordBreaker` i `CharBreaker` mimo bardzo podobnych nazw metod (myląca asymetria).

##### `breakSentence(self, sentence)` (linia 56)
- **Co robi:** Dzieli zdanie na frazy i grupuje je (`merge`) do limitu słów, rekursywnie
  dzieląc frazy przekraczające limit przez `breakPhrase`.
- **Przyjmuje:** `sentence` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getPhrases()`, `self.merge()`, (pośrednio) `self.breakPhrase()`.
- **Wyjątki:** brak jawnych.

##### `breakPhrase(self, phrase)` (linia 59)
- **Co robi:** Dzieli frazę na pojedyncze słowa i łączy je w grupy o rozmiarze
  `min(len(words)//2, wordLimit)` — czyli mniej więcej „pół na pół" ograniczone limitem.
- **Przyjmuje:** `phrase` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getWords()`.
- **Wyjątki:** `ZeroDivisionError` niemożliwy (nie ma dzielenia przez zmienną), ale
  `splitPoint` może wyjść `0`, jeśli `words` ma 1 element i `wordLimit` ≥ 1 — wtedy
  `words[:0]` da pustą listę doklejaną do wyniku (`result.append('')`) w pętli `while
  words:` — potencjalna pętla nieskończona lub puste elementy w wyniku (linia 61-65: jeśli
  `splitPoint == 0`, `words[splitPoint:]` zwraca to samo `words` bez zmian → **nieskończona
  pętla `while words:`**, bo `words` nigdy się nie zmniejsza). To realny bug przy
  `len(words) < 2` i `wordLimit >= 1` po `min()`... a właściwie trzeba dokładnie: `splitPoint
  = min(len(words)//2, wordLimit)`; dla `len(words)=1`, `len(words)//2=0`, więc
  `splitPoint=0` niezależnie od `wordLimit` → **zawieszenie programu** dla pojedynczego
  bardzo długiego słowa/frazy jednosłownej przekraczającej limit. To poważny bug (wisienka:
  ścieżka do jego wywołania wymaga frazy z 1 „słowem" według `getWords`, co może się zdarzyć
  dla długiego ciągu bez separatorów).

##### `merge(self, parts, breakPart)` (linia 68)
- **Co robi:** Grupuje listę części (`parts`) w większe fragmenty tak, by żaden nie
  przekroczył `wordLimit` słów; części same przekraczające limit są rekursywnie dzielone
  przez przekazaną funkcję `breakPart`.
- **Przyjmuje:** `parts` — lista stringów; `breakPart` — funkcja/metoda do dalszego dzielenia
  zbyt dużej części (przekazywana jako callback — kolejny ślad wzorca strategii/DI).
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak zewnętrznych; wewnętrznie używa domkniętej funkcji `flush()`
  (linia 72) z `nonlocal group`.
- **Woła:** `self.punctuator.getWords()` (do liczenia `wordCount`), `breakPart()`, lokalna
  `flush()`.
- **Wyjątki:** brak jawnych (poza propagacją z `breakPart`).
- **Uwagi:** wzorzec akumulatora przez słownik `group = {'parts': [], 'wordCount': 0}` zamiast
  dataclass/namedtuple — działa, ale mniej czytelne niż typowana struktura.

##### `flush()` (linia 72, zagnieżdżona w `merge`)
- **Co robi:** Domyka bieżącą grupę części w jeden string i dodaje do wyniku, resetuje grupę.
- **Przyjmuje:** nic (domknięcie nad `result`, `group` z `merge`).
- **Zwraca:** `None`.
- **Efekty uboczne:** mutuje `result` (przez `nonlocal` domknięcia zewnętrznego — a właściwie
  `result.append` nie wymaga `nonlocal`, ale przypisanie `group = {...}` wymaga `nonlocal
  group`, linia 73).
- **Woła:** nic.
- **Wyjątki:** brak.

#### `class CharBreaker` (linia 93) — zwykła klasa z `__init__`
**Cel:** Dzieli tekst na fragmenty wg limitu liczby ZNAKÓW, hierarchicznie: akapity → zdania →
frazy → słowa → surowe cięcie znaków jako ostateczność. Jest to klasa faktycznie używana
przez `chunk_text()` przy `method='char'` (domyślna metoda).

**Pola (ustawiane w `__init__`, nie dataclass):**
| pole | typ | default | cel |
|------|-----|---------|-----|
| `charLimit` | brak adnotacji | wymagany arg | maksymalna liczba znaków w fragmencie |
| `punctuator` | brak adnotacji | wymagany arg | instancja `LatinPunctuator` |
| `paragraphCombineThreshold` | brak adnotacji | `None` | opcjonalny osobny limit łączenia akapitów (jeśli `None`, używa `charLimit`) |

**Metody:**

##### `__init__(self, charLimit, punctuator, paragraphCombineThreshold=None)` (linia 94)
- **Co robi:** Zapisuje limit znaków, punktator i opcjonalny próg łączenia akapitów.
- **Przyjmuje:** jak w tabeli pól wyżej.
- **Zwraca:** `None` (niejawnie).
- **Efekty uboczne:** brak poza przypisaniem.
- **Woła:** nic.
- **Wyjątki:** brak.

##### `breakText(self, text)` (linia 99)
- **Co robi:** Punkt wejścia — dzieli tekst na akapity i łączy je (`merge`) wg
  `paragraphCombineThreshold`, rekursywnie dzieląc zbyt duże akapity przez `breakParagraph`.
- **Przyjmuje:** `text` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getParagraphs()`, `self.merge()`, (pośrednio) `self.breakParagraph`.
- **Wyjątki:** brak jawnych.

##### `breakParagraph(self, text)` (linia 102)
- **Co robi:** Dzieli akapit na zdania i łączy je wg `charLimit`, rekursywnie dzieląc zbyt
  duże zdania przez `breakSentence`.
- **Przyjmuje:** `text` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getSentences()`, `self.merge()`.
- **Wyjątki:** brak jawnych.

##### `breakSentence(self, sentence)` (linia 105)
- **Co robi:** Dzieli zdanie na frazy i łączy je wg `charLimit`, rekursywnie dzieląc zbyt
  duże frazy przez `breakPhrase`.
- **Przyjmuje:** `sentence` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getPhrases()`, `self.merge()`.
- **Wyjątki:** brak jawnych.

##### `breakPhrase(self, phrase)` (linia 108)
- **Co robi:** Dzieli frazę na słowa i łączy je wg `charLimit`, rekursywnie dzieląc zbyt
  długie słowa przez `breakWord`.
- **Przyjmuje:** `phrase` — string.
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** `self.punctuator.getWords()`, `self.merge()`.
- **Wyjątki:** brak jawnych.

##### `breakWord(self, word)` (linia 111)
- **Co robi:** Ostateczność — tnie słowo na kawałki o dokładnej długości `charLimit`
  (surowe cięcie bez poszanowania jakiejkolwiek granicy językowej).
- **Przyjmuje:** `word` — string (pojedyncze „słowo", może być bardzo długie).
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak.
- **Woła:** nic (czyste krojenie stringa w pętli).
- **Wyjątki:** brak — w przeciwieństwie do `WordBreaker.breakPhrase`, tu nie ma dzielenia
  przez zero/przez `len//2`, tylko proste krojenie o stały krok, więc nie ma analogicznego
  bugu nieskończonej pętli (pętla `while word:` zawsze skraca `word` o `charLimit` znaków na
  iterację, gwarantując zbieżność, o ile `charLimit >= 1`; przy `charLimit == 0` byłaby
  nieskończona pętla — brak walidacji tego przypadku brzegowego).

##### `merge(self, parts, breakPart, combineThreshold=None)` (linia 118)
- **Co robi:** Analogicznie do `WordBreaker.merge`, ale liczy znaki zamiast słów; grupuje
  części do `combineThreshold` (lub `charLimit`, jeśli nie podano), dzieląc zbyt duże części
  przez `breakPart`.
- **Przyjmuje:** `parts` — lista stringów; `breakPart` — callback do dalszego dzielenia;
  `combineThreshold` — opcjonalny odrębny próg łączenia (używany tylko przy akapitach z
  `paragraphCombineThreshold`).
- **Zwraca:** `list[str]`.
- **Efekty uboczne:** brak zewnętrznych, wewnętrznie korzysta z domkniętej `flush()`.
- **Woła:** `breakPart()`, lokalna `flush()`.
- **Wyjątki:** brak jawnych.
- **Uwagi:** duplikacja logiki niemal identycznej jak `WordBreaker.merge` (linia 68-90) —
  różnica tylko w liczeniu jednostek (słowa vs znaki) i nazwach pól słownika (`wordCount` vs
  `charCount`) — silny kandydat do wspólnej klasy bazowej/generic (DRY złamane między dwiema
  klasami w tym samym pliku).

##### `flush()` (linia 122, zagnieżdżona w `merge`)
- **Co robi:** Jak w `WordBreaker.flush` — domyka grupę do wyniku i resetuje.
- **Przyjmuje:** nic (domknięcie).
- **Zwraca:** `None`.
- **Efekty uboczne:** mutuje `group['parts']`/`group['charCount']` bezpośrednio (bez
  `nonlocal group` — bo tu nie podmienia się cały słownik `group`, tylko mutuje jego klucze
  in-place, w przeciwieństwie do `WordBreaker.flush`, gdzie `group = {...}` wymaga
  `nonlocal`). Subtelna niespójność implementacyjna między dwoma niemal identycznymi
  metodami `flush` w tym samym pliku (`text_chunker.py:72-76` vs `122-126`) — jedna
  przypisuje nowy słownik, druga mutuje istniejący — dwa różne style dla tej samej operacji.

### funkcje modułowe (poza klasami)

##### `chunk_text(text, method='char', limit=750)` (linia 144)
- **Co robi:** Fasada/funkcja fabryczna — tworzy `LatinPunctuator` i odpowiedni breaker
  (`CharBreaker` lub `WordBreaker`) wg parametru `method`, po czym dzieli tekst.
- **Przyjmuje:** `text` — string do podzielenia; `method` — `'char'` lub `'word'` (string,
  nie enum/Literal — brak walidacji dozwolonych wartości); `limit` — limit znaków/słów
  (domyślnie 750).
- **Zwraca:** `list[str]` przy poprawnym `method`; **`None` niejawnie, jeśli `method` nie
  jest ani `'char'` ani `'word'`** (brak gałęzi `else`/`raise` — cichy błąd, linia 144-149).
- **Efekty uboczne:** tworzy nowe instancje `LatinPunctuator` i breakera przy każdym
  wywołaniu (brak cache'owania/wstrzykiwania).
- **Woła:** `LatinPunctuator()`, `CharBreaker(...).breakText()` lub `WordBreaker(...).breakText()`.
- **Wyjątki:** brak jawnych — ale niepoprawny `method` prowadzi do zwrócenia `None` zamiast
  listy, co może wywołać `TypeError`/`AttributeError` u wywołującego dalej w łańcuchu
  (`modules/subtitle.py:368,390` iteruje po wyniku — `None` rozwaliłoby pętlę `for`).
- **Uwagi (bug/code smell):** brak walidacji `method` — to jest jedyny publiczny punkt wejścia
  do całego modułu i nie broni się przed literówką w argumencie.

##### `main()` (linia 152)
- **Co robi:** Funkcja demonstracyjna — definiuje przykładowy tekst (fragment „The
  Beginning After The End" po angielsku, mimo że reszta projektu jest polskojęzyczna),
  dzieli go metodą `'char'` z limitem 100 i metodą `'word'` z limitem 100, wypisuje chunki
  przez `print()`.
- **Przyjmuje:** nic.
- **Zwraca:** `None` (niejawnie).
- **Efekty uboczne:** `print()` na stdout.
- **Woła:** `chunk_text()` ×2.
- **Wyjątki:** brak jawnych.
- **Uwagi:** uruchamiana tylko przez `if __name__ == '__main__':` (linia 176-177) — kod
  demonstracyjny/testowy pozostawiony w pliku produkcyjnym zamiast w osobnym pliku
  testów/przykładów; przykładowy tekst jest po angielsku w polskim projekcie AVH — sugeruje
  że moduł został zaadaptowany z zewnętrznej biblioteki/gista bez pełnego dostosowania.

### 🔍 diagnoza pliku
- **✅ co działa dobrze / mocne strony:** sensowna hierarchiczna strategia dzielenia tekstu
  (akapit→zdanie→fraza→słowo→znak) z rekursywnym „spadaniem" do drobniejszej granicy tylko
  gdy trzeba; `WordBreaker.__init__`/`CharBreaker.__init__` wstrzykują `punctuator` przez
  konstruktor zamiast tworzyć go wewnątrz — to jedyny fragment obszaru zbliżony do
  dependency injection; jest realnie używany w produkcyjnym pipeline (`modules/subtitle.py`).
- **⚠️ dług techniczny / code smells:** CAŁKOWITY brak typowania (jedyny plik obszaru bez
  ani jednej adnotacji typu — `text_chunker.py` w całości); podejrzany/prawdopodobnie
  niedziałający warunek `result[-1] in nonPunc` w `_recombine`
  (`text_chunker.py:38` — sprawdzanie podciągu zamiast dopasowania regex); poważny
  potencjalny bug nieskończonej pętli w `WordBreaker.breakPhrase` dla frazy jednosłownej
  (`text_chunker.py:59-66`, `splitPoint = min(len(words)//2, wordLimit)` daje 0 przy
  `len(words)==1`, więc `words[splitPoint:]` nigdy się nie zmniejsza); `chunk_text()` cicho
  zwraca `None` dla nieobsłużonej wartości `method` zamiast rzucić (`text_chunker.py:144-149`);
  duplikacja niemal identycznej metody `merge`+`flush` między `WordBreaker`
  (`text_chunker.py:68-90`) i `CharBreaker` (`text_chunker.py:118-141`) — różni się tylko
  jednostką liczenia; niespójny styl `flush()` między dwiema klasami (`nonlocal group` z
  przypisaniem vs mutacja in-place, `text_chunker.py:72-76` vs `122-126`); kod
  demo/przykładowy (`main()`, angielski tekst) zaszyty w pliku produkcyjnym zamiast w
  testach; lista angielskich skrótów w `getSentences` nieadekwatna do polskiego tekstu
  (`text_chunker.py:10`); zduplikowany fragment cudzysłowu w regexie `getPhrases`
  (`text_chunker.py:14`).
- **❌ niespójności ze stylem MangaShift:** zero typowania w całym pliku — całkowite
  zerwanie z zasadą typowania obowiązującą w MangaShift; klasy `WordBreaker`/`CharBreaker`
  nie są dataclassami mimo że są czystymi kontenerami konfiguracji + logiki (podobnie jak
  `CoolAnimation`); duplikacja `merge`/`flush` między klasami to podręcznikowy przypadek na
  wspólną klasę bazową/mixin — łamie „jedno źródło prawdy per pytanie" (pytanie „jak grupować
  części do limitu" ma dwie osobne, rozjeżdżające się odpowiedzi); `LatinPunctuator` jest
  bezstanowa, ale nie jest ani modułem funkcji, ani dataclassem — pośrednia forma bez
  wyraźnego uzasadnienia.
- **🔗 sprzężenia:** moduł sam w sobie jest przenośny (zero zależności od reszty projektu),
  ale wewnętrznie mocno sprzężony: `WordBreaker`/`CharBreaker` wymagają konkretnie obiektu
  zgodnego z interfejsem `LatinPunctuator` (brak formalnego protokołu/ABC — kontrakt
  niejawny, wymuszony tylko przez duck typing). Jedyny konsument zewnętrzny: funkcja
  `chunk_text` wołana z `modules/subtitle.py:48,368,390`. Ewentualny `None` z `chunk_text`
  przy błędnym `method` propagowałby się do `modules/subtitle.py` i tam prawdopodobnie
  wywalił iterację — cichy błąd międzymodułowy.

---

## 🧭 podsumowanie obszaru

- **Główne odpowiedzialności:** obszar `utils` grupuje cztery niezależne, przenośne narzędzia
  bez wspólnego mianownika architektonicznego poza katalogiem: (1) kosmetyczna animacja
  startowa CLI, (2) pomiar czasu wykonania z ładnym raportem `rich`, (3) konwersja liczb na
  polskie słowa (kluczowe dla jakości TTS — silniki źle czytają cyfry), (4) dzielenie
  długiego tekstu napisów na fragmenty pod limit wejściowy silnika TTS. Wszystkie cztery są
  faktycznie używane w produkcyjnym potoku (`start.py`, `modules/subtitle.py`) — brak
  martwych plików na poziomie modułu.

- **Największe problemy (ranking):**
  1. **Potencjalna nieskończona pętla** w `WordBreaker.breakPhrase`
     (`text_chunker.py:59-66`) dla frazy jednosłownej przekraczającej limit — realne ryzyko
     zawieszenia procesu TTS na konkretnym wejściu tekstowym; wymaga weryfikacji testem i
     poprawki (`splitPoint = max(1, min(...))`).
  2. **Podejrzana logika `result[-1] in nonPunc`** w `LatinPunctuator._recombine`
     (`text_chunker.py:38`) — wygląda na nigdy niedziałający mechanizm wykrywania skrótów
     zdań (regex traktowany jak podciąg), co oznacza, że `getSentences` może źle dzielić
     zdania po skrótach typu „Mr." mimo pozornej ochrony w kodzie.
  3. **Cichy `None` z `chunk_text()`** przy błędnym `method` (`text_chunker.py:144-149`) —
     brak walidacji na jedynym publicznym wejściu modułu, błąd ujawni się dopiero głęboko
     w `modules/subtitle.py`.
  4. **Zerowe typowanie `text_chunker.py`** — w projekcie, gdzie pozostałe 3 pliki mają
     adnotacje typów, ten plik wygląda na żywcem wklejony z zewnętrznego źródła (regexy z
     angielskimi skrótami, angielski tekst demo w `main()` sugerują pochodzenie spoza
     projektu) bez adaptacji stylu.
  5. **Zbędna zależność `six`** w `number_in_words.py:53` — funkcja `u()` jest no-opem
     w Python 3, zależność powinna zostać usunięta bez zmiany zachowania.
  6. Drobniejsze: duplikacja `merge`/`flush` (`text_chunker.py`), duplikacja logiki czasu
     w `execution_timer.py` (`calculate_duration` vs `_alt`), martwa zmienna `count_time`
     w `cool_animation.py:107,142`, brak `functools.wraps` w dekoratorze
     `execution_timer.py:120`.

- **Kandydaci do refaktoru na styl MangaShift:**
  - `CoolAnimation` → `@dataclass(slots=True)` + wydzielenie renderowania z pętli sterującej
    (rozbicie `display()` na mniejsze metody: `_clear_screen`, `_render_frame`).
  - `NumberInWords` → dodać `slots=True` albo wynieść tablice liczebników poza klasę jako
    stałe modułowe (nie są stanem instancji, nigdy się nie zmieniają) + usunąć `six`.
  - `text_chunker.py` → dodać pełne typowanie; wydzielić wspólną logikę `merge`/`flush`
    z `WordBreaker`/`CharBreaker` do wspólnej klasy bazowej lub funkcji generycznej
    parametryzowanej „funkcją liczącą jednostki" (słowa vs znaki); zdefiniować formalny
    protokół/ABC dla `LatinPunctuator`, żeby kontrakt dependency injection był jawny
    (`Protocol` z metodami `getParagraphs`/`getSentences`/`getPhrases`/`getWords`); dodać
    `raise ValueError` w `chunk_text()` dla nieznanego `method`.
  - `ExecutionTimer` → jedyny plik już zgodny z dataclass+slots; do poprawy: DI dla
    `Console` (wstrzykiwana zamiast tworzona domyślnie), scalenie dwóch metod liczenia
    czasu trwania, `functools.wraps` w dekoratorze.

- **Pliki/funkcje martwe lub podejrzane:**
  - `cool_animation.py:107,142` — zmienna `count_time` liczona, nigdy nie odczytywana.
  - `text_chunker.py:152-177` (`main()` + blok `if __name__`) — kod demonstracyjny w module
    produkcyjnym, nieużywany przez resztę projektu (żaden import nie odwołuje się do `main`).
  - `text_chunker.py:38` — warunek `nonPunc` w `_recombine`, podejrzenie o niedziałającą
    logikę (patrz wyżej) — wymaga testu jednostkowego, żeby potwierdzić, czy skróty
    (`Mr.`, `Dr.` itd.) faktycznie są chronione przed dzieleniem zdania.
  - `number_in_words.py:53` (`from six import u`) — zależność bez realnej funkcji w Python 3.

---

