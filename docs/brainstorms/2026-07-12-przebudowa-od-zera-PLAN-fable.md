# plan strategiczny: przebudowa mm_avh od zera (fable)

> data: 2026-07-12 | greenfield, nowy branch | pisany niezależnie, bez czytania planu Sola
> fundament: spec 2026-07-12 + poprawki usera + audyt 00-09 + standardy mangashift-architecture-ref

---

## A) werdykt architektoniczny

Nowy projekt to **jeden pakiet Pythona `mm_avh/`** zamiast dzisiejszych luźnych folderów
(`modules/`, `data/`, `constants.py`). W środku trzy poziomy: **panel** (interakcja z userem),
**pipeline** (liniowy przebieg: ekstrakcja → refaktor → tłumaczenie → lektor → merge)
i **serwisy** (właściwa robota). Rejestr silników wchodzi TYLKO tam, gdzie user realnie wybiera
spośród kilku opcji: TTS (4 silniki) i tłumaczenie (2 silniki). Ekstrakcja, refaktor napisów,
merge i render to zwykłe moduły — jedna implementacja, zero ceremonii.

Z MangaShift bierzemy dokładnie cztery rzeczy: (1) rejestr `engine_id → klasa` z lazy importem,
(2) cienką fasadę per domena, która nie zna żadnego konkretnego silnika, (3) jedną funkcję
`bootstrap()` składającą config + wykryte ścieżki w jeden obiekt, (4) lekki `doctor` z jednolitym
formatem checków. Odrzucamy jako przerost (potwierdzone audytem 06): runtime/vram, llama, katalog
modeli, generyczny step-registry pipeline'u, event bus, db/api/worker/usecases oraz async jako
domyślny styl. mm_avh przetwarza jeden plik na raz — pipeline to funkcja wołająca kolejno kilka
kroków, nie DAG.

Najważniejsze cięcie projektowe, które rozwiązuje god-file `subtitle_to_speech.py` (1196 linii):
dziś silnik TTS jest zmieszany z rzeczami, które są WSPÓLNE dla wszystkich silników — składaniem
toru audio wg timingu napisów, atempo/volume i miksem z oryginalną ścieżką do EAC3. W nowej
architekturze silnik odpowiada wyłącznie za "tekst → audio", a timeline, post-processing i mixer
to trzy wspólne moduły obok rejestru. To naturalnie rozbija 1810 linii TTS na małe kawałki,
bez wymyślania sztucznych abstrakcji.

`utils/` pozostaje rdzeniem usera: wchodzi do nowej struktury przez przeniesienie 1:1
(bez przepisywania treści), a rozbudowa to wyłącznie NOWE pliki obok — w tym `rich_console/`
z MangaShift, którego migracja już trwa na branchu `feature/utils-migration` i który staje się
warstwą wizualną panelu.

## B) rozstrzygnięcia decyzji

**ui stack: prompt_toolkit + rich.** Zgadzam się z badaniem 09 — i to nie z rozpędu. Wizja usera
to płynący REPL (banner, Enter działa, `/` pokazuje podpowiedzi inline) — dokładnie model
Claude Code. prompt_toolkit daje inline autocomplete natywnie (`complete_while_typing` + własny
completer reagujący tylko na `/`), rich renderuje banner/panele/tabele/progress — i user już ma
gotowy pakiet 150+ styli. Textual odpada: to framework pełnoekranowej apki okienkowej, jego
palette to modal na Ctrl+P, a nie inline `/` — więcej nauki, dalej od wizji. Jedna zasada
współżycia obu bibliotek: rich rysuje tylko wtedy, gdy prompt_toolkit nie trzyma prompta
(sekwencyjnie, nigdy na tej samej klatce).

**config: dataclass + jeden json, bez pydantic.** Apka na 1 usera z kilkunastoma polami ustawień
nie potrzebuje pydantic-settings ani env_prefix per silnik. `Settings` to dataclass ze slots
z metodami load/save na `settings.json` (gitignored, auto-zapis z panelu `/settings`). Defaulty
żyją w kodzie, walidacja wartości żyje w panelu (tam gdzie user je wpisuje). To zastępuje
dzisiejszy god-file `data/settings.py` (684 linie), który miesza model danych z interaktywnym UI.

**klucze api: .env, bez szyfrowania.** Dziś klucze leżą gołe w `settings.json`, a klucz proxy
ElevenBytes jest zahardkodowany w `tts_elevenbytes.py` (sekret w repo — do wycięcia). Nowa zasada:
wszystkie sekrety w `.env` (gitignored) + `.env.example` z nazwami pól. DPAPI/szyfrowanie to
przerost dla maszyny jednego usera. Zmienna środowiskowa wygrywa nad `.env` — standard.

**binarki: zostają lokalnie w bin/, poza gitem, bez pobierania przy starcie.** Pobieranie przy
starcie (wzór MangaShift external/) wymaga hostowania, wersjonowania i hashy — opłaca się przy
27 modelach AI, nie przy dwóch narzędziach, które nie zmieniają się latami. Decyzja: `bin/`
w całości gitignored (naprawić 218 przypadkowo trackowanych plików przez `git rm -r --cached`),
`doctor` sprawdza obecność i mówi wprost skąd pobrać, opcjonalny skrypt
`scripts/maintenance/fetch_bins.py` na wypadek świeżej maszyny — kiedyś, nie teraz.
Skład `bin/` po sprzątaniu: **mkvtoolnix** (mkvextract+mkvmerge — nieusuwalne, brak zamiennika),
**ffmpeg** (audio tor + wypalanie mp4), **balabolka/balcon** (dopóki silnik żyje w rejestrze).
Usuwamy: stylish_tts (567 MB), espeak-ng, martwe stałe mkvinfo/mkvpropedit. Migracja toru audio
na PyAV (badanie 07) to świadomie ODŁOŻONA opcja — greenfield ma robić to samo co dziś, nie
wymieniać sprawdzonego ffmpeg przy okazji.

**silniki — stan faktyczny (zweryfikowany w kodzie, bez wymysłów):**
- TTS: **elevenbytes** (proxy ElevenLabs, warianty v2/v3 = endpointy run6/run7, voice_settings
  tylko v3) — główny; **edge** (edge-tts, głosy Zofia/Marek jako parametr, przenośny);
  **harpo** (pyttsx3/SAPI, głos Zosia Harpo, Windows-only); **balcon** (balcon.exe/SAPI,
  głos IVONA Agnieszka, Windows-only, do lamusa ale zostaje w rejestrze). Balcon == SAPI5 —
  jeden silnik, nie dwa. Google TTS nie istnieje i nie powstaje.
- tłumaczenie: **google** (googletrans) i **deepl** (DeepL API). DeepL desktop = martwy kod
  (nieosiągalny z fasady, bug w pętli replace) — nie przenosimy. OpenAI nie istnieje tutaj.
- warianty (v2/v3, Zofia/Marek) to OPCJE silnika w Settings, nie osobne wpisy rejestru.
  Etykieta polska ("TTS - ElevenBytes...") żyje tylko w UI; rejestr zna krótkie `engine_id`.

## C) struktura folderów docelowa

```
mm_avh_working_space/
├── start.py                    # cienki entry: bootstrap() + panel (zostaje dla run_mm_avh.bat)
├── pyproject.toml              # pakiet mm_avh, zależności, narzędzia
├── .env / .env.example         # sekrety (gitignored / wzorzec)
├── settings.json               # ustawienia usera (gitignored, auto-zapis z /settings)
│
├── mm_avh/                     # cały nowy kod w jednym pakiecie
│   ├── bootstrap.py            # bootstrap() -> AppContext (settings + ścieżki + OS)
│   ├── errors.py               # wspólna hierarchia wyjątków
│   ├── config/
│   │   ├── settings.py         # Settings (dataclass slots) + load/save json
│   │   ├── paths.py            # resolve_workspace_root(), ścieżki bin/ per-OS
│   │   └── secrets.py          # klucze z env/.env
│   ├── cli/
│   │   ├── panel.py            # pętla REPL (PromptSession, dispatch komend)
│   │   ├── commands.py         # rejestr /komend (nazwa → opis → handler)
│   │   ├── completer.py        # SlashCompleter (inline autocomplete po "/")
│   │   ├── banner.py           # ASCII banner (na bazie utils/cool_animation)
│   │   └── settings_panel.py   # /settings: rich panel + edycja + auto-zapis
│   ├── pipeline/
│   │   └── runner.py           # run_auto() / run_manual() — liniowa sekwencja kroków
│   ├── services/
│   │   ├── extraction/         # zwykły moduł (bez rejestru)
│   │   │   ├── mkv_info.py     # mkvmerge --identify → lista ścieżek
│   │   │   ├── track_selector.py  # heurystyka wyboru ścieżek (przeniesiona)
│   │   │   └── extractor.py    # mkvextract + live progress
│   │   ├── subtitles/          # zwykły moduł
│   │   │   ├── refactor.py     # split ASS main/alt (ręczny + auto)
│   │   │   ├── convert.py      # ass→srt, txt→srt, czyszczenie tagów
│   │   │   ├── merge_back.py   # srt→ass po tłumaczeniu (mapowanie po start/end)
│   │   │   ├── numbers.py      # liczby→słowa w SRT (woła utils/number_in_words)
│   │   │   └── style_classifier.py  # hak: przeniesiony 1:1, NIE przepisywany
│   │   ├── translation/        # REJESTR (jest wybór)
│   │   │   ├── service.py      # fasada: translate_srt(file, engine_id, settings)
│   │   │   ├── base.py         # kontrakt silnika (translate_batch)
│   │   │   ├── dedup.py        # dedup fraz + znaczniki newline + czyszczenie ASS/HTML
│   │   │   └── engines/
│   │   │       ├── __init__.py # rejestr: engine_id → (moduł, klasa)
│   │   │       ├── google/     # service.py, constants.py
│   │   │       └── deepl/      # service.py, constants.py
│   │   ├── tts/                # REJESTR (jest wybór)
│   │   │   ├── service.py      # fasada: generate_lector(srt, engine_id, settings)
│   │   │   ├── base.py         # kontrakt silnika TTS
│   │   │   ├── timeline.py     # składanie toru WAV wg timingu (cisza+chunki, RF64)
│   │   │   ├── postprocess.py  # atempo chain + volume (ffmpeg)
│   │   │   ├── mixer.py        # miks lektor+oryginał (+7dB) → EAC3
│   │   │   └── engines/
│   │   │       ├── __init__.py # rejestr
│   │   │       ├── elevenbytes/  # client.py (dziś tts_elevenbytes.py), service.py, constants.py
│   │   │       ├── edge/         # service.py, constants.py
│   │   │       ├── harpo/        # service.py, constants.py (pyttsx3, win-only)
│   │   │       └── balcon/       # service.py, constants.py (balcon.exe, win-only)
│   │   └── merge/              # zwykły moduł
│   │       ├── mkv_merge.py    # finalny MKV (wideo+lektor+napisy)
│   │       └── burn_mp4.py     # wypalanie napisów do mp4 (x264, wymaga ffmpeg.exe)
│   ├── media/
│   │   └── tools.py            # jedno miejsce wywołań ffmpeg/mkvextract/mkvmerge (subprocess)
│   └── setup/
│       └── doctor.py           # CheckResult + run_doctor() (5-7 checków)
│
├── utils/                      # NIETYKALNE — przeniesione 1:1, rozbudowa = nowe pliki obok
│   ├── number_in_words.py, text_chunker.py, execution_timer.py, cool_animation.py
│   └── rich_console/           # migracja z MangaShift (już w toku na branchu)
│
├── bin/                        # binarki, CAŁKOWICIE poza gitem
│   ├── mkvtoolnix/  ├── ffmpeg/  └── balabolka/
├── working_space/              # dane usera (gitignored poza .gitkeep struktury)
│   ├── output/  └── temp/ (main_subs/, alt_subs/)
├── scripts/
│   ├── maintenance/            # jednorazowe (w tym convert_eac3_to_mp3.py z working_space)
│   └── smoke/                  # ręczny test e2e na 1 pliku MKV
├── tests/                      # tylko realne testy; eksperymenty → scripts/ lub kosz
└── docs/
```

Uwaga do `utils/`: przenosimy pliki bez zmiany treści; jeśli samo przeniesienie wymusi poprawkę
linii importu — to jedyna dozwolona zmiana. `cool_animation` używa dziś `constants` — banner
w `cli/banner.py` opakuje go tak, żeby nie ruszać środka.

## D) etapy

Zasada nadrzędna: **stary kod żyje nietknięty do końca etapu 4.** Nowy pakiet rośnie obok,
a smoke-test porównuje wynik nowego z wynikiem starego na tym samym pliku MKV. Dopiero gdy
przebieg auto jest zielony, etap 5 wycina stare. Zero okresu "nic nie działa".

### etap 0 — punkt odniesienia (pół godziny, zanim cokolwiek powstanie)

Cel: mieć wzorzec "co znaczy działa", zanim zaczniemy porównywać.
- wybrać 1 krótki plik MKV testowy, przepuścić przez OBECNY kod (auto), zachować wyniki
  (eac3, ass, finalny mkv) w `scripts/smoke/baseline/`
- spisać w `scripts/smoke/README.md` kroki odpalenia i oczekiwane pliki wynikowe
DoD: baseline istnieje i wiadomo jak go odtworzyć.

### etap 1 — szkielet + config + panel

Cel: pakiet `mm_avh/` startuje, banner + `/komendy` z autocomplete działają, ustawienia
czytają się i zapisują, doctor mówi czego brakuje. Pipeline jeszcze niepodpięty (Enter
odpowiada komunikatem).

pliki (bez ciał — tylko co gdzie):
- `pyproject.toml` — pakiet, zależności (dochodzi prompt_toolkit)
- `mm_avh/config/paths.py` — `resolve_workspace_root()`, `bin_paths()` per-OS, stałe podfolderów
- `mm_avh/config/settings.py` — `Settings` (dataclass slots: tryb auto/manual, tts_engine,
  tts opcje per silnik, translator, translated_line_count, output_mode...), `load()`, `save()`
- `mm_avh/config/secrets.py` — `load_secrets()` (deepl_api_key, elevenbytes_key z .env)
- `mm_avh/errors.py` — `MmAvhError` + podklasy per domena
- `mm_avh/bootstrap.py` — `bootstrap() -> AppContext`
- `mm_avh/setup/doctor.py` — `CheckResult`, `run_doctor()`: ffmpeg? mkvextract/mkvmerge?
  klucze? struktura working_space? OS (balcon tylko Windows)?
- `mm_avh/cli/banner.py`, `commands.py`, `completer.py`, `panel.py`, `settings_panel.py`
  — komendy startowe: `/help`, `/settings`, `/auto`, `/manual`, `/doctor`, `/exit`; Enter = stub
- `start.py` — nowy, cienki (stary tymczasowo jako `start_old.py`)
- dokończenie migracji `utils/rich_console/` (branch już to zaczął)

zależności: brak (fundament). jak przetestować: odpalić, wpisać `/se` → dropdown, zmienić
ustawienie → sprawdzić `settings.json`, `/doctor` na maszynie z binarkami i bez.
DoD: panel w pełni nawigowalny, ustawienia trwałe, tryb auto/manual zapamiętany.

### etap 2 — rejestr TTS (rozbicie god-file, największy zysk)

Cel: 4 działające silniki za jednym kontraktem; `subtitle_to_speech.py` przestaje być potrzebny.

kontrakt (słowami): silnik dostaje sparsowane napisy i katalog roboczy, oddaje **tor lektora
jako WAV**. Domyślna droga w klasie bazowej: syntezuj per linia → wspólny `timeline.py` skleja
wg timingu. Balcon nadpisuje całość, bo natywnie renderuje cały plik za jednym wywołaniem —
to jego specyfika, nie powód do łamania kontraktu. Retry/backoff, cache mp3 (resume po crashu)
i adaptacyjny cooldown ElevenBytes zostają WEWNĄTRZ silnika elevenbytes — to jego cechy, nie
frameworka.

pliki:
- `services/tts/base.py` — `TtsEngine` (ABC): `render_track()`, `synthesize_line()`,
  `is_available()`, `engine_id`
- `services/tts/engines/__init__.py` — `_REGISTRY`, `create_engine()`, `available_engine_ids()`
- `services/tts/engines/elevenbytes/client.py` — dzisiejszy `tts_elevenbytes.py` przeniesiony
  (klucz z secrets zamiast hardkodu), `service.py` — batch+cache+cooldown, `constants.py`
- `services/tts/engines/edge/service.py`, `constants.py` — głosy Zofia/Marek jako opcja
- `services/tts/engines/harpo/service.py`, `constants.py`
- `services/tts/engines/balcon/service.py`, `constants.py` — konwersja ANSI tylko tutaj
  (dziś robiona bez potrzeby także dla silników online)
- `services/tts/timeline.py` — cisza+chunki, jeden sample rate per silnik z jego constants,
  RF64 dla >4GB, fallback odczytu długości (przenieść sprawdzone `_get_file_duration`)
- `services/tts/postprocess.py` — `build_atempo_chain()` (przenieść — czysta, dobra), volume
- `services/tts/mixer.py` — miks z oryginałem (+7dB jako stała konfigurowalna), konwersja EAC3,
  guard na puste audio (świeża poprawka — zachować)
- `services/tts/service.py` — fasada `TtsService`: cache instancji, `generate_lector(...)`

zależności: etap 1 (config/secrets/paths). jak przetestować: realny SRT z `working_space`
przez każdy silnik (ElevenBytes i edge obowiązkowo; harpo/balcon smoke "nie wybucha") —
odsłuch + porównanie długości toru z baseline. martwy kod (`_pp_speed_audio`,
`_ffmpeg_post_process`) świadomie NIE jest przenoszony.
DoD: `TtsService.generate_lector(srt, engine_id=...)` daje WAV równoważny dzisiejszemu
dla elevenbytes i edge; dodanie 5. silnika = folder + wpis w rejestrze.

### etap 3 — media pipeline (ekstrakcja → napisy → merge) + spięcie Enter

Cel: pełny przebieg auto działa w nowym kodzie od MKV do finalnego pliku.

pliki:
- `mm_avh/media/tools.py` — `run_ffmpeg()`, `run_mkvextract()`, `run_mkvmerge()` — jedyne
  miejsce subprocess do binarek (ścieżki z paths.py, progress callback)
- `services/extraction/mkv_info.py` — identify → dane ścieżek
- `services/extraction/track_selector.py` — przeniesiona heurystyka (moduł, nie rejestr)
- `services/extraction/extractor.py` — ekstrakcja z live paskiem (zachować świeże poprawki
  kolejności logów z ostatnich commitów)
- `services/subtitles/refactor.py` — split main/alt; naprawa przy okazji przepisania: brak
  adnotacji typów pól dataclass (dzisiejszy cichy bug) i podwójne kopiowanie metadanych
- `services/subtitles/convert.py`, `merge_back.py`, `numbers.py`
- `services/subtitles/style_classifier.py` — kopiowany 1:1 (hak na przyszłość, user zbiera dane)
- `services/merge/mkv_merge.py`, `burn_mp4.py` — dzisiejsze tryby wyjścia zachowane
- `mm_avh/pipeline/runner.py` — `run_auto(ctx)`, `run_manual(ctx)`; krok tłumaczenia woła
  jeszcze STARY `translator.py` (adapter tymczasowy), reszta nowa; Enter w panelu podpięty

zależności: etapy 1-2. jak przetestować: smoke e2e na pliku z etapu 0, diff wyników z baseline
(te same ścieżki wybrane, zgodny finalny plik). tryb manual: pytania per krok działają.
DoD: Enter w panelu przetwarza folder od zera do wyniku jak dzisiejsza apka.

### etap 4 — rejestr tłumaczenia + dedup

Cel: ostatni stary moduł zastąpiony; wspólny potok dedup likwiduje ~80% duplikacji
google/deepl.

pliki:
- `services/translation/base.py` — kontrakt: `translate_batch(list[str]) -> list[str]`
- `services/translation/dedup.py` — wspólny potok: czyszczenie tagów ASS/HTML → dedup
  unikalnych fraz → znaczniki newline → batch → przywrócenie → 3-poziomowy fallback przy
  niezgodności liczby linii (dziś zduplikowany w obu metodach — tu JEDEN raz)
- `services/translation/engines/__init__.py` — rejestr (google, deepl)
- `services/translation/engines/google/service.py`, `constants.py` — googletrans; jedno
  utworzenie event loopa na plik zamiast per batch (dzisiejszy smell)
- `services/translation/engines/deepl/service.py`, `constants.py` — klucz z secrets
- `services/translation/service.py` — fasada `TranslationService.translate_srt(...)` —
  nieznany engine_id RZUCA błąd (dziś: cichy no-op)
- `pipeline/runner.py` — wymiana adaptera na nową fasadę; usunięcie `start_old.py` z przebiegu

zależności: etap 3. jak przetestować: SRT z powtórkami (1000× ta sama linia) → licznik
realnych zapytań == liczba unikalnych fraz; oba silniki na tym samym pliku; e2e smoke.
DoD: pipeline w 100% na nowym kodzie, DeepL desktop i flaga gpt świadomie nieprzeniesione.

### etap 5 — sprzątanie repo i dysku

Cel: repo odzwierciedla nową architekturę, dysk lżejszy o ~0.6 GB. Osobny etap, bo to praca
git/dyskowa, nie architektura — nie mieszać z kodem.

- usunąć: `bin/stylish_tts/` (567 MB), `bin/espeak-ng/`, stare `modules/`, `data/`,
  `constants.py`, `start_old.py`
- `git rm -r --cached bin/` (218 plików-widm) + `.gitignore`: dopisać `.mypy_cache/`,
  potwierdzić `bin/`, `settings.json`, `.env`
- `working_space/`: luźne MKV/srt/lnk/desktop.ini precz; `convert_eac3_to_mp3.py`
  → `scripts/maintenance/`
- `temp/` (217 plików): wartościowe skrypty → `scripts/`, dane ML zostają lokalnie poza repo
- `tests/`: realne testy zostają i dostają aktualizację importów; eksperymenty (`chat.py`,
  `*_alt.py`, `MM_AVH_pre.py`...) → `scripts/` albo kosz
- scentralizować cache mypy (jeden `cache_dir` w pyproject)
- README: nowy start, struktura, wymagane binarki
DoD: `git status` czysty, świeży klon + binarki + `.env` = działająca apka, smoke zielony.

## E) wzorzec rejestru silników — opisany słowami

Rejestr to **słownik na poziomie pakietu `engines/`**: klucz to krótki, kanoniczny `engine_id`
("elevenbytes", "edge"...), wartość to para "ścieżka modułu + nazwa klasy" zapisana stringami.
Obok słownika żyją dwie funkcje: jedna zwraca listę dostępnych id (dla panelu `/settings` —
lista opcji bierze się z rejestru, nie z ręcznie utrzymywanej listy), druga tworzy silnik:
sprawdza czy id istnieje (jak nie — czytelny błąd z listą dostępnych), importuje moduł
**dopiero w tym momencie** (lazy import — pyttsx3/win32 nie ładują się, gdy user używa
ElevenBytes), bierze klasę po nazwie i buduje instancję z configiem.

Fasada domeny (`TtsService`, `TranslationService`) zna wyłącznie tę funkcję tworzącą. Dostaje
`engine_id` z Settings, buduje silnik przy pierwszym użyciu, trzyma go w małym cache'u instancji
i woła metody kontraktu. Fasada nie zawiera ani jednego `if engine_id == ...` — cała wiedza
"który silnik jak działa" mieszka w folderze tego silnika.

Kontrakt silnika to krótki ABC w `base.py`: parę metod, których pipeline naprawdę potrzebuje
(dla TTS: wyprodukuj tor lektora; dla tłumaczenia: przetłumacz listę fraz), plus
`is_available()` — silnik sam mówi, czy ma warunki do pracy (klucz API jest? binarka jest?
system to Windows?). Tak rejestr załatwia cross-platform bez if-ów po OS w fasadzie: na Linuksie
balcon/harpo po prostu raportują niedostępność i panel ich nie proponuje.

Dodanie nowego silnika = nowy podfolder w `engines/` (service.py + constants.py) implementujący
kontrakt + jeden wpis w słowniku rejestru. Zero zmian w fasadzie, pipeline'u i panelu — panel
sam zobaczy nową opcję, bo listuje rejestr. Etykieta polska do wyświetlenia jest własnością UI
(mapka id → label przy panelu), nie kluczem logiki — dziś string "TTS - Zosia - Harpo" jest
jednocześnie labelką i kluczem dispatchu, i to się kończy.

## F) ryzyka i niepewności (szczerze, na koniec)

1. **Równoważność audio, nie bitowa identyczność.** Nowy timeline składający WAV powstaje na
   bazie trzech dzisiejszych wariantów (Harpo 22500 Hz, Edge 24000, ElevenBytes 44100 — trzy
   różne hardkody). Ujednolicenie "sample rate z constants silnika" może dać minimalnie inny
   wynik niż dziś. Kryterium akceptacji musi być odsłuch + długość toru, nie diff bajtów.
2. **ElevenBytes to proxy poza kontrolą usera.** Cały główny silnik wisi na `teamsp.org` —
   endpoint może się zmienić w trakcie przebudowy i wtedy "nowe nie działa" nie będzie winą
   architektury. Warto od razu testować na małych plikach i nie palić limitów.
3. **Harpo/balcon nie przetestuję maszynowo.** Wymagają zainstalowanych głosów SAPI (Zosia
   Harpo, IVONA Agnieszka). Plan zakłada dla nich tylko "nie wybucha przy braku głosu" —
   realny odsłuch musi zrobić user. Spec i tak mówi: nie testować teraz.
4. **Panel to nowa funkcjonalność, nie przepisanie.** prompt_toolkit + rich na Windows Terminal
   powinny zagrać (IPython/pgcli tak działają), ale zgrzyty renderowania (Live progress vs
   aktywny prompt) wyjdą dopiero w praktyce. Dlatego panel jest w etapie 1 — jak coś zgrzyta,
   dowiadujemy się najwcześniej, jak się da.
5. **Tryb manual ma dziś dużo mikro-interakcji** (wybór ścieżek, wybór stylów, pytania T/Y).
   Łatwo zgubić któryś edge-case przy przenoszeniu do nowego panelu. Smoke z etapu 0 pokrywa
   auto; manual trzeba przeklikać ręcznie z listą dzisiejszych pytań w ręku.
6. **Największy ślepy punkt: working_space jako kontrakt.** Cały pipeline komunikuje się przez
   pliki w konwencji nazw (basename, main_subs/alt_subs, rozpoznawanie roli po podciągu
   ścieżki). Przebudowa zachowuje tę konwencję, ale to najbardziej kruchy element — każda
   rozbieżność nazwy pliku między krokami objawi się dopiero w e2e, nie w teście modułu.
7. **Niepewność co do `googletrans`** — nieoficjalne API, bywa łamane przez Google niezależnie
   od nas. Rejestr przynajmniej izoluje ryzyko do jednego folderu.
8. **Scope creep czai się w etapie 3** — pokusa "przy okazji naprawię X" (PyAV, pyttsx3 zamiast
   balcona, style_classifier). Wszystko to jest jawnie ODŁOŻONE; etap 3 przenosi zachowanie,
   nie ulepsza go. Ulepszenia mają wchodzić jako osobne, małe PR-y po przebudowie.
