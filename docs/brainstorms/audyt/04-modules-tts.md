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
