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
