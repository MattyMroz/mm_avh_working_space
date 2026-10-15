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
