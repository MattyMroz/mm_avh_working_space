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
