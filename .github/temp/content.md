# 📂 MM_AVH — Content Map

## 🎯 Przegląd projektu

**MM_AVH (Multimedia Magic – Audio Visual Heaven)** to kompleksowe narzędzie do automatycznego przetwarzania wideo anime:

- 🎬 Ekstrakcji audio i napisów z plików MKV
- 🌍 Tłumaczenia napisów (Google Translate, DeepL, ChatGPT)
- 🎤 Generowania lektora/narracji za pomocą TTS (Text-to-Speech)
- 📚 Tworzenia audiobooków z plików SRT/TXT
- 🎥 Scalania i eksportu (MKV, MP4 z hardcoded napisami)

**Stack:** Python 3.14+, pydub, edge-tts, pyttsx3, googletrans, deepl, nltk, pydantic, rich

---

## 📁 Struktura katalogów

```
mm_avh_working_space/
├── .github/                          # VS Code Copilot + konfiguracja
│   ├── copilot-instructions.md       # Baseline dla AI agentów
│   ├── agents/                       # Persony agentów
│   ├── instructions/                 # Reguły per typ pliku
│   ├── skills/                       # Reusable workflow
│   └── prompts/                      # Template'y poleceń
├── bin/                              # Binaria (FFmpeg, MKVToolNix, Balabolka)
│   ├── balabolka/                    # TTS silnik (systemowy, Windows)
│   ├── ffmpeg/                       # Konwersja audio/video
│   └── mkvtoolnix/                   # Przetwarzanie MKV
├── data/                             # Konfiguracja i ustawienia
│   ├── config.py                     # Menu opcji (translator, voice, output)
│   ├── settings.py                   # Manager ustawień (UI + JSON I/O)
│   └── settings.json                 # Plik ustawień użytkownika
├── modules/                          # Rdzenie funkcjonalności
│   ├── mkvtoolnix.py                 # Parser JSON + wrapper MKV Tools
│   ├── mkv_processing.py             # Merge/burn MKV i MP4
│   ├── subtitle.py                   # Konwersja: ASS↔SRT, split, number→words
│   ├── subtitle_to_speech.py         # Wrapper 4 TTS (Edge, pyttsx3, Balabolka)
│   └── translator.py                 # Wrapper 4 translatory (Google, DeepL, ChatGPT)
├── utils/                            # Narzędzia pomocnicze
│   ├── cool_animation.py             # ASCII animacja na starcie
│   ├── execution_timer.py            # Context manager do mierzenia czasu
│   ├── number_in_words.py            # Konwersja liczb → polski tekstem
│   └── text_chunker.py               # Chunker tekstu dla TTS (WordBreaker, CharBreaker)
├── tests/                            # Skrypty test/dev
│   ├── tts_*.py                      # Testowanie różnych TTS engine'ów
│   ├── translator_test.py            # Test tłumaczenia
│   ├── MM_AVH_pre.py                 # Poprzedni prototyp
│   └── ...
├── working_space/                    # 🔥 Folder roboczy użytkownika
│   ├── [input files]                 # MKV, TXT, SRT → wrzucić tu
│   ├── temp/                         # Pliki tymczasowe (audio, subs temp)
│   │   ├── main_subs/                # Główne napisy (przetłumaczone)
│   │   └── alt_subs/                 # Alternatywne napisy (np. śpiew)
│   └── output/                       # ✅ Wyniki (audio, napisy, MKV, MP4)
├── assets/                           # Media statyczne
│   └── img/                          # Screenshoty, GIF demo
├── .gitignore                        # Ignoruje temp, venv, exe
├── constants.py                      # Ścieżki, style rich Console
├── start.py                          # 🚀 PUNKT WEJŚCIA — orchestrator
├── run_mm_avh.bat                    # Batch launcher (uv run start.py)
├── pyproject.toml                    # Zależności, metadata
├── uv.lock                           # Lock file dla uv package manager
└── README.md                         # Dokumentacja użytkownika
```

---

## 📄 Szczegóły plików

### `start.py`

- **Cel:** Główny orchestrator — prowadzi użytkownika przez interaktywny workflow ekstrakcji, tłumaczenia, TTS, scalania.
- **Kluczowe funkcje:**
  - `main()` → Dekorator `@execution_timer`, pełny flow
  - `display_logo()` → ASCII art (moduł CoolAnimation)
  - `ask_user(question)` → Y/N input wrapper
  - `extract_tracks_from_mkv()` → Wyciąga audio/napisy z MKV
  - `refactor_subtitles()` → ASS/SRT/TXT konwersja i split
  - `translate_subtitles(settings)` → Wybór plików i tłumaczenie
  - `convert_numbers_to_words()` → Liczby → polski SŁOWNIE
  - `generate_audio_for_subtitles(settings)` → TTS dla każdego napisu
  - `refactor_alt_subtitles()` → Scalanie alt subtitles z ASS
  - `process_output_files(settings)` → MKV merge / MP4 encode
  - `clear_temp_folders()` → Cleanup temp Dir
  - `update_settings()` → Zmiana ustawień + zapis JSON

### `constants.py`

- **Cel:** Centralizacja ścieżek + konfiguracja rich Console.
- **Kluczowe zmienne:**
  - Ścieżki: `WORKING_SPACE`, `WORKING_SPACE_TEMP`, `WORKING_SPACE_TEMP_MAIN_SUBS`, `WORKING_SPACE_TEMP_ALT_SUBS`, `WORKING_SPACE_OUTPUT`
  - Narzędzia: `MKVTOOLNIX_FOLDER`, `MKV_EXTRACT_PATH`, `MKV_MERGE_PATH`, `MKV_INFO_PATH`, `FFMPEG_PATH`, `FFPROBE_PATH`, `BALABOLKA_PATH`
  - `console` → Rich Console z custom theme (style'e: purple_bold, red_bold, green_bold, itp.)
  - **Ważne:** Inicjalizuje AudioSegment FFmpeg paths PRZED importem pydub w projekcie

### `run_mm_avh.bat`

- **Cel:** Windows launcher — zmienia kodowanie na UTF-8, chdir do repo root, uruchamia `uv run start.py`

### `pyproject.toml`

- **Projekt:** `mm-avh-working-space` v2.0.0
- **Python:** ≥3.14
- **Kluczowe zależności:**
  - **Audio/Video:** `pydub>=0.25.1`, `edge-tts>=7.2.7`, `pyttsx3>=2.99`, `opencv-python>=4.13`, `scipy>=1.17`
  - **Tłumaczenie:** `googletrans>=4.0.2`, `deepl>=1.27`
  - **Napisy:** `pysrt>=1.1.2`, `pysubs2>=1.8`, `pyasstosrt>=1.5`
  - **Utils:** `nltk>=3.9.2`, `numpy>=2.4.1`, `rich>=14.3`, `pydantic>=2.12.5`, `natsort>=8.4`
  - **Inne:** `pyautogui>=0.9.54`, `pyperclip>=1.11`, `async-timeout>=5.0.1`, `six>=1.17`

---

## 🔧 Moduły (modules/)

### `modules/mkvtoolnix.py`

- **Cel:** Wrapper JSON+CLI do MKVToolNix (mkvinfo, mkvextract, mkvmerge, mkvpropedit).
- **Klasa:** `MkvToolNix(filename: str, ...)`
  - `get_mkv_info()` → JSON z info o kontenerze, ścieżkach, tagach
  - `mkv_extract_track(data: dict)` → Ekstraktuje audio i napisy wg. user selection
  - `_parse_tracks_data(data)` → Parser JSON
  - `_print_mkv_info(tracks)` → Pretty print info

### `modules/mkv_processing.py`

- **Cel:** Finalne scalanie/konwersja output: merge do MKV, burn+encode do MP4.
- **Klasa:** `MKVProcessing(filename: str, crf_value='18', preset_value='ultrafast')`
  - `process_mkv(settings)` → Wybiera output: MM_AVH_Players / Scal do mkv / Wypal do mp4
  - `move_files_to_working_space()` → Kopiuje wyniki do working_space
  - `mkv_merge()` → mkvmerge + EAC3 audio + SRT napisy
  - `mkv_burn_to_mp4()` → FFmpeg hardcode napisy do MP4 (CRF 18, preset medium)

### `modules/subtitle.py`

- **Cel:** Konwersja, split i refaktor napisów (ASS↔SRT, liczby→słowa).
- **Klasa:** `SubtitleRefactor(filename: str, ...)`
  - `split_ass()` → Dzieli ASS na main_subs (dialogu) + alt_subs (śpiew/effect)
  - `ass_to_srt()` → ASS → SRT konwersja
  - `move_srt()` → Move SRT → temp/main_subs lub alt_subs
  - `txt_to_srt(sentence_length, chunk_limit, split_method)` → TXT → SRT z auto-chunking
  - `convert_numbers_in_srt()` → Liczby 123 → "sto dwadzieścia trzy"
  - `srt_to_ass()` → Scalanie przetłumaczonych SRT z oryginalnym ASS (update dialogu)

### `modules/subtitle_to_speech.py`

- **Cel:** Generowanie audio z napisów — wrapper dla 4 TTS engine'ów.
- **Klasa:** `SubtitleToSpeech(filename: str, ...)`
  - `ansi_srt()` → Konwersja kodowania UTF-8 → ANSI (dla Harpo/Balabolka)
  - `srt_to_wav_harpo(tts_speed, tts_volume)` → pyttsx3 (Harpo, Zosia)
  - `srt_to_wav_balabolka(...)` → Balabolka CLI (Agnieszka, Marek)
  - `srt_to_wav_edge_online(tts, tts_speed, tts_volume)` → Edge TTS async (Zofia, Marek online)
  - `merge_tts_audio()` → Łączy wygenerowany audio do jednego WAV
  - `generate_audio(settings)` → Dispatcher: wybiera engine i generuje
  - `srt_to_eac3_elevenlabs()` → Manual mode (user załaduje EAC3 z ElevenLabs UI)

### `modules/translator.py`

- **Cel:** Tłumaczenie napisów SRT → polski.
- **Klasa:** `SubtitleTranslator()`
  - `translate_google(...)` → Googletrans batch async
  - `translate_deepl_api(...)` → DeepL API
  - `translate_deepl_desktop(...)` → DeepL desktop (pyautogui + clipboard)
  - `translate_google_gpt(...)` → Google + ChatGPT hybrid
  - `translate_srt(filename, dir_path, settings)` → Router funkcji wg. settings.translator

---

## 📊 Data Layer (data/)

### `data/config.py`

- **Cel:** Statyczne definicje menu wyboru (translatory, TTS voices, output options).
- **Klasa:** `Config` (dataclass)
  - `get_translators()` → Google, DeepL API, DeepL Desktop, ChatGPT
  - `get_translation_options()` → '10', '20', ..., '100' (batch size)
  - `get_voice_actors()` → TTS voice'ów (Harpo/Zosia, Ivona/Agnieszka, Edge/Zofia, itp.)
  - `get_output()` → MM_AVH_Players, Scal do mkv, Wypal do mp4

### `data/settings.py`

- **Cel:** Manager ustawień (UI selection + JSON persistence).
- **Klasa:** `Settings` (dataclass)
  - **Fields:** `translator`, `deepl_api_key`, `chat_gpt_access_token`, `translated_line_count`, `tts`, `tts_speed`, `tts_volume`, `output`
  - `load_from_file(settings_path)` → Load z JSON, fallback defaults
  - `change_settings_save_to_file()` → Interactive menu → JSON

---

## 🛠️ Utils (utils/)

### `utils/cool_animation.py`

- **Cel:** ASCII animacja startup'u (logo MM_AVH z efektem "loadingu").
- **Klasa:** `CoolAnimation(load_str, show_border, middle_offset, use_animation)`

### `utils/execution_timer.py`

- **Cel:** Context manager + dekorator do mierzenia czasu wykonania.
- **Klasa:** `ExecutionTimer`

### `utils/number_in_words.py`

- **Cel:** Konwersja liczb (int/float/str) → polski tekstem.
- **Klasa:** `NumberInWords` (dataclass)
  - `number_in_words(value)` → 12345 → "dwanaście tysięcy trzysta czterdzieści pięć"
  - `convert_numbers_in_text(text)` → Regex find/replace liczby w tekście

### `utils/text_chunker.py`

- **Cel:** Chunking tekstu dla TTS (WordBreaker, CharBreaker, LatinPunctuator).
- **Klasy:** `LatinPunctuator`, `WordBreaker(wordLimit)`, `CharBreaker(charLimit)`

---

## 🗣️ Voice Actors / TTS

| Głos | Engine | Typ | Speed | Vol | Uwagi |
|------|--------|-----|-------|-----|-------|
| Zosia | Harpo (pyttsx3) | Offline/Systemowy | 0-500 wpm | 0-1 | Default SAPI5 |
| Agnieszka | Ivona (Balabolka) | Offline/Systemowy | -10 do 10 | 0-100 | Premium SAPI5 |
| Zofia | Edge TTS | Online (FREE) | -100% do +100% | -100% do +100% | Microsoft cloud |
| Marek | Edge TTS | Online (FREE) | -100% do +100% | -100% do +100% | Microsoft cloud |
| [Custom] | ElevenLabs | Online (MANUAL) | — | — | User załaduje WAV |

---

## 🔄 Pipeline Flow

```
USER START (run_mm_avh.bat / uv run start.py)
│
├─► DISPLAY_LOGO()
│   └─ CoolAnimation
│
├─► UPDATE_SETTINGS()
│   └─ Settings.load_from_file() + optional change
│
├─► EXTRACT_TRACKS_FROM_MKV()
│   ├─ MkvToolNix.get_mkv_info()
│   ├─ User selects tracks (audio, main subs, alt subs)
│   └─ MkvToolNix.mkv_extract_track()
│      Output: working_space/temp/*.wav, *.ass
│
├─► REFACTOR_SUBTITLES()
│   ├─ SubtitleRefactor.split_ass()
│   ├─ SubtitleRefactor.ass_to_srt()
│   └─ SubtitleRefactor.move_srt()
│
├─► TRANSLATE_SUBTITLES(settings)
│   └─ SubtitleTranslator.translate_srt()
│
├─► CONVERT_NUMBERS_TO_WORDS()
│   └─ SubtitleRefactor.convert_numbers_in_srt()
│
├─► GENERATE_AUDIO_FOR_SUBTITLES(settings)
│   └─ SubtitleToSpeech.generate_audio(settings)
│      Routes to: harpo | balabolka | edge | elevenlabs
│
├─► REFACTOR_ALT_SUBTITLES()
│   └─ SubtitleRefactor.srt_to_ass()
│
├─► PROCESS_OUTPUT_FILES(settings)
│   └─ MKVProcessing.process_mkv()
│
├─► CLEAR_TEMP_FOLDERS()
│
└─► END
```

---

## 📋 Zależności (pyproject.toml)

### Audio/Video Processing

- `pydub>=0.25.1` — Audio manipulation (WAV, MP3, EAC3)
- `edge-tts>=7.2.7` — Microsoft Edge TTS (async)
- `pyttsx3>=2.99` — Offline TTS (SAPI5 Windows)
- `opencv-python>=4.13` — CV2 (fallback vision tasks)
- `scipy>=1.17` — Signal processing

### Subtitle Handling

- `pysrt>=1.1.2` — SRT file parsing
- `pysubs2>=1.8` — ASS/SSA file parsing
- `pyasstosrt>=1.5` — ASS→SRT conversion

### Language/Translation

- `googletrans>=4.0.2` — Google Translate (unofficial)
- `deepl>=1.27` — DeepL API (official)
- `nltk>=3.9.2` — Natural Language Toolkit

### UI/Output

- `rich>=14.3` — Rich console output (colors, tables, spinners)
- `pydantic>=2.12.5` — Data validation

### System/Utilities

- `pyautogui>=0.9.54` — GUI automation (DeepL Desktop control)
- `pyperclip>=1.11` — Clipboard I/O
- `natsort>=8.4` — Natural sorting
- `async-timeout>=5.0.1` — Async timeout management
- `numpy>=2.4.1` — Numerical computing

---

## 🏗️ Architektura / Design Patterns

- **Dataclass-based Design** — Wszystkie klasy użytkują `@dataclass(slots=True)`
- **Async/Await** — Edge TTS: async batch download z semaphore + timeout
- **Router Pattern** — `translate_srt()`, `generate_audio()`, `process_mkv()` → route wg. settings
- **Pipeline Orchestration** — `main()` w `start.py` → sekwencyjne wykonanie krok po kroku
- **Fallback Strategy** — Translation chunking → single-by-single; TTS timeout → fallback

---

## 📚 Test Files (tests/)

| Plik | Cel |
|------|-----|
| `tts_test.py` | Unified TTS test |
| `tts_balcon_test.py` | Test Balabolka |
| `tts_google_test.py` | Test pyttsx3 (Google voice) |
| `tts_local_test.py` | Test pyttsx3 offline |
| `tts_online_edge_test_*.py` | Test Edge TTS (v0, v1, v2) |
| `translator_test.py` | Test Google Translate |
| `translator-gpt-*.py` | Test ChatGPT variants |
| `sent_tokenize_test.py` | Test NLTK sentence tokenization |
| `num2words_test.py` | Test konwersji liczb |
| `merge_audio_test.py` | Test Audio merge pydub |
| `pylint_tests.py` | Lint checks |
| `MM_AVH_pre.py` | Prototype starej wersji |
