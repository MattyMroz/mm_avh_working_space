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
