# 📂 MM_AVH — Content Map

## 🎯 Przegląd projektu

**MM_AVH (Multimedia Magic – Audio Visual Heaven)** to kompleksowe narzędzie do automatycznego przetwarzania wideo anime:

- 🎬 Ekstrakcji audio i napisów z plików MKV
- 🌍 Tłumaczenia napisów (Google Translate, DeepL, ChatGPT, Gemini)
- 🎤 Generowania lektora/narracji za pomocą TTS (Text-to-Speech) — offline, online (Edge) i neural (StylishTTS / API)
- 📚 Tworzenia audiobooków z plików SRT/TXT
- 🎥 Scalania i eksportu (MKV, MP4 z hardcoded napisami)

**Stack:** Python 3.14+, pydub, edge-tts, pyttsx3, googletrans, deepl, nltk, pydantic, rich oraz neural-TTS (torch, torchaudio, transformers, librosa, phonemizer, safetensors)

---

## 📁 Struktura katalogów

```
mm_avh_working_space/
├── .claude/                          # Claude Code — skille/config syncowane z repo agents (gitignore)
│   ├── skills/                       # Skopiowane skille (płasko): python, git, instructions,
│   │                                 #   ideate, simple, frontend, end, ui-ux-design,
│   │                                 #   make-interfaces-feel-better, social-media
│   ├── agents/                       # orchestrator.md (wspólny subagent)
│   ├── settings.json                 # Hooki + permissiony (merge z base.settings.json)
│   └── statusline.mjs                # Wspólny statusline
├── .github/                          # (okrojony) konfiguracja AI — gitignore w całości
│   └── temp/                         # Robocze pliki (np. brudnopis content.md)
├── bin/                              # Binaria (gitignore) — silniki TTS i narzędzia MKV/FFmpeg
│   ├── balabolka/                    # TTS silnik SAPI5 (systemowy, Windows)
│   ├── espeak-ng/                    # Fonemizacja (G2P) dla neural TTS / phonemizer
│   ├── ffmpeg/                       # Konwersja audio/video
│   ├── mkvtoolnix/                   # Przetwarzanie MKV
│   └── stylish_tts/                  # Model + zasoby neural StylishTTS
├── data/                             # Konfiguracja i ustawienia
│   ├── config.py                     # Menu opcji (translator, voice, post-processing, output)
│   ├── settings.py                   # Manager ustawień (UI + JSON I/O)
│   └── settings.json                 # Plik ustawień użytkownika
├── docs/                             # 📄 Dokumentacja deweloperska (m.in. ten content map)
├── modules/                          # Rdzenie funkcjonalności
│   ├── mkvtoolnix.py                 # Parser JSON + wrapper MKV Tools
│   ├── mkv_processing.py             # Merge/burn MKV i MP4
│   ├── subtitle.py                   # Konwersja: ASS↔SRT, split, number→words
│   ├── subtitle_to_speech.py         # Dispatcher TTS (Harpo, Balabolka, Edge, Stylish, Fish, ReadLover, ElevenLabs)
│   ├── translator.py                 # Wrapper translatorów (Google, DeepL, ChatGPT, Gemini)
│   ├── tts_stylish.py                # Klient lokalnego neural TTS (StylishTTS, torch)
│   ├── tts_fish_api.py               # Klient Fish TTS API (HTTP)
│   ├── tts_readlover.py              # Klient ReadLover API (HTTP, multi-key fallback)
│   └── tts_elevenbytes.py           # Klient ElevenBytes/ElevenLabs-like TTS API
├── utils/                            # Narzędzia pomocnicze
│   ├── cool_animation.py             # ASCII animacja na starcie
│   ├── execution_timer.py            # Context manager + dekorator do mierzenia czasu
│   ├── number_in_words.py            # Konwersja liczb → polski tekstem
│   └── text_chunker.py               # Chunker tekstu dla TTS (WordBreaker, CharBreaker)
├── tests/                            # Skrypty test/dev (input/, output/)
│   ├── tts_*.py                      # Testowanie różnych TTS engine'ów
│   ├── translator_test.py            # Test tłumaczenia
│   ├── MM_AVH_pre.py                 # Poprzedni prototyp
│   └── ...
├── working_space/                    # 🔥 Folder roboczy użytkownika (runtime I/O, gitignore)
│   ├── [input files]                 # MKV, TXT, SRT → wrzucić tu
│   ├── temp/                         # Pliki tymczasowe (audio, subs temp)
│   │   ├── main_subs/                # Główne napisy (przetłumaczone)
│   │   └── alt_subs/                 # Alternatywne napisy (np. śpiew)
│   └── output/                       # ✅ Wyniki (audio, napisy, MKV, MP4)
├── assets/                           # Media statyczne (img/)
├── .gitattributes                    # Reguły atrybutów git (EOL)
├── .gitignore                        # Ignoruje temp, venv, exe, .claude, .github, bin, media
├── .python-version                   # Pin wersji Pythona (uv)
├── LICENSE                           # Licencja
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
- **Custom uv sources:** `torch`/`torchaudio` z indeksu `pytorch-cu128` (CUDA 12.8), `monotonic-align` z gita (resemble-ai)
- **Kluczowe zależności (pełna lista niżej):** klasyczny stack (pydub, edge-tts, pyttsx3, googletrans, deepl, rich, pydantic) **+ neural-TTS stack** (torch, torchaudio, transformers, librosa, phonemizer, safetensors, einops, accelerate, nnaudio, ring-attention-pytorch)

---

## 🔧 Moduły (modules/)

### `modules/mkvtoolnix.py`

- **Cel:** Wrapper JSON+CLI do MKVToolNix (mkvinfo, mkvextract, mkvmerge, mkvpropedit).
- **Klasa:** `MkvToolNix(filename: str, ...)`
  - `get_mkv_info()` → JSON z info o kontenerze, ścieżkach, tagach
  - `mkv_extract_track(data: dict)` → Ekstraktuje audio i napisy wg. user selection
  - (prywatne) `_parse_tracks_data()`, `_print_mkv_info()`, `_check_executables()`, `_get_extract_command()` itd.

### `modules/mkv_processing.py`

- **Cel:** Finalne scalanie/konwersja output: merge do MKV, burn+encode do MP4.
- **Klasa:** `MKVProcessing(filename: str, crf_value='18', preset_value='ultrafast')`
  - `process_mkv(settings)` → Wybiera output: MM_AVH_Players / Scal do mkv / Wypal do mp4
  - `move_files_to_working_space()` → Kopiuje wyniki do working_space
  - `mkv_merge()` → mkvmerge + EAC3 audio + SRT napisy
  - `mkv_burn_to_mp4()` → FFmpeg hardcode napisy do MP4

### `modules/subtitle.py`

- **Cel:** Konwersja, split i refaktor napisów (ASS↔SRT, liczby→słowa).
- **Klasa:** `SubtitleRefactor(filename: str, ...)`
  - `split_ass()` → Dzieli ASS na main_subs (dialog) + alt_subs (śpiew/effect)
  - `ass_to_srt()` → ASS → SRT konwersja
  - `move_srt()` → Move SRT → temp/main_subs lub alt_subs
  - `txt_to_srt(sentence_length, chunk_limit, split_method)` → TXT → SRT z auto-chunking
  - `convert_numbers_in_srt()` → Liczby 123 → "sto dwadzieścia trzy"
  - `srt_to_ass()` → Scalanie przetłumaczonych SRT z oryginalnym ASS (update dialogu)

### `modules/subtitle_to_speech.py`

- **Cel:** Generowanie audio z napisów — **dispatcher dla wszystkich engine'ów TTS** (offline, online, neural, API).
- **Klasa:** `SubtitleToSpeech(filename: str, ...)`
  - `ansi_srt()` → Konwersja kodowania UTF-8 → ANSI (dla Harpo/Balabolka)
  - `srt_to_wav_harpo(tts_speed, tts_volume)` → pyttsx3 (Harpo, Zosia)
  - `srt_to_wav_balabolka(...)` → Balabolka CLI (Agnieszka, Marek)
  - `srt_to_wav_edge_online(tts, tts_speed, tts_volume)` → Edge TTS async (Zofia, Marek online)
  - `srt_to_wav_stylish(...)` → Neural TTS lokalnie (StylishTTS, → `tts_stylish.py`)
  - `srt_to_wav_fish_api(...)` → Fish TTS przez API (→ `tts_fish_api.py`)
  - `srt_to_wav_readlover(...)` → ReadLover przez API (→ `tts_readlover.py`)
  - `srt_to_eac3_elevenlabs()` → Manual mode (user załaduje EAC3 z ElevenLabs UI)
  - `merge_tts_audio()` → Łączy wygenerowane audio do jednego WAV
  - `generate_audio(settings)` → Dispatcher: wybiera engine i generuje

### `modules/translator.py`

- **Cel:** Tłumaczenie napisów SRT → polski.
- **Klasa:** `SubtitleTranslator()`
  - `translate_google(...)` → Googletrans batch async
  - `translate_deepl_api(...)` → DeepL API
  - `translate_deepl_desktop(...)` → DeepL desktop (pyautogui + clipboard)
  - `translate_google_gpt(...)` → Google + ChatGPT hybrid
  - `translate_chat_gpt(...)` → ChatGPT
  - `translate_gemini(...)` → Google Gemini
  - `translate_srt(filename, dir_path, settings)` → Router funkcji wg. settings.translator

### `modules/tts_stylish.py` *(neural, lokalny)*

- **Cel:** Lokalny neural TTS oparty o StylishTTS (torch). Wymaga modelu z `bin/stylish_tts/` i fonemizacji espeak-ng.
- **Funkcje setupu:** `_setup_paths()`, `_setup_espeak()`
- **Klasa:** `StylishTTS`
  - `synthesize(text, speed=1.0)` → np.ndarray
  - `synthesize_long(text, speed=1.0, max_chunk=120)` → chunked synteza długiego tekstu
  - `save_wav(audio, output_path)` → zapis WAV

### `modules/tts_fish_api.py` *(API)*

- **Cel:** Klient HTTP do Fish TTS API.
- **Klasa:** `FishTTSClient`
  - `get_voices()` / statyczne `get_voices_static(base_url)` → lista głosów
  - `synthesize(text)` → np.ndarray
  - statyczne `get_sample_rate_from_wav(wav_bytes)`

### `modules/tts_readlover.py` *(API)*

- **Cel:** Klient HTTP do ReadLover API z fallbackiem między wieloma kluczami API.
- **Funkcja:** `_normalize_api_keys()`
- **Klasa:** `ReadLoverClient`
  - `synthesize(text)` → np.ndarray
  - statyczne `get_voices_static(...)`, `get_presets_static(...)`
  - (prywatne) `_request_with_api_key_fallback()`, `_resolve_speaker_id()`, `_log_billing_headers()` itd.

### `modules/tts_elevenbytes.py` *(API)*

- **Cel:** Klient TTS API w stylu ElevenLabs (sync wrappery wokół async).
- **Klasy pomocnicze:** `SynthResult`, `BatchReport`, hierarchia wyjątków `TTSError`/`TTSValidationError`/`TTSAPIError`
- **Klasa główna:** `TTS`
  - `synthesize_sync(text, voice=None, fmt="mp3")` → bytes
  - `synthesize_to_file_sync(...)`, `synthesize_batch_sync(...)`, `close_sync()`
  - statyczne `list_voices()`, `add_voice(alias, name, voice_id)`, `remove_voice(alias)`
  - property `default_voice`

---

## 📊 Data Layer (data/)

### `data/config.py`

- **Cel:** Statyczne definicje menu wyboru (translatory, TTS voices, post-processing, output).
- **Klasa:** `Config` (dataclass)
  - `get_translators()` → Google, DeepL API, DeepL Desktop, ChatGPT, Gemini
  - `get_translation_options()` → '10', '20', ..., '100' (batch size)
  - `get_voice_actors()` → TTS voice'ów (Harpo/Zosia, Ivona/Agnieszka, Edge/Zofia, Stylish, Fish, ReadLover, ElevenLabs)
  - `get_post_processing()` → opcje post-processingu audio
  - `get_output()` → MM_AVH_Players, Scal do mkv, Wypal do mp4

### `data/settings.py`

- **Cel:** Manager ustawień (UI selection + JSON persistence).
- **Klasa:** `Settings` (dataclass)
  - **Fields:** m.in. `translator`, `deepl_api_key`, `chat_gpt_access_token`, klucze API (Gemini/Fish/ReadLover), `translated_line_count`, `tts`, `tts_speed`, `tts_volume`, `output`
  - `load_from_file(settings_path)` → Load z JSON, fallback defaults
  - `change_settings_save_to_file()` → Interactive menu → JSON

---

## 🛠️ Utils (utils/)

### `utils/cool_animation.py`

- **Cel:** ASCII animacja startup'u (logo MM_AVH z efektem "loadingu").
- **Klasa:** `CoolAnimation(load_str, show_border, middle_offset, use_animation)`

### `utils/execution_timer.py`

- **Cel:** Context manager + dekorator `execution_timer` do mierzenia czasu wykonania.
- **Klasa:** `ExecutionTimer`

### `utils/number_in_words.py`

- **Cel:** Konwersja liczb (int/float/str) → polski tekstem.
- **Klasa:** `NumberInWords` (dataclass)
  - `number_in_words(value)` → 12345 → "dwanaście tysięcy trzysta czterdzieści pięć"
  - `convert_numbers_in_text(text)` → Regex find/replace liczby w tekście

### `utils/text_chunker.py`

- **Cel:** Chunking tekstu dla TTS (WordBreaker, CharBreaker, LatinPunctuator).
- **Klasy:** `LatinPunctuator`, `WordBreaker(wordLimit)`, `CharBreaker(charLimit)`; funkcja `chunk_text()`

---

## 🗣️ Voice Actors / TTS

| Głos | Engine | Typ | Uwagi |
|------|--------|-----|-------|
| Zosia | Harpo (pyttsx3) | Offline/Systemowy | Default SAPI5 |
| Agnieszka | Ivona (Balabolka) | Offline/Systemowy | Premium SAPI5 (CLI) |
| Zofia / Marek | Edge TTS | Online (FREE) | Microsoft cloud, async |
| StylishTTS | torch (lokalnie) | Neural/Offline | Model w `bin/stylish_tts/`, wymaga espeak-ng (G2P) |
| Fish | Fish TTS API | Online (API) | `tts_fish_api.py` |
| ReadLover | ReadLover API | Online (API) | `tts_readlover.py`, fallback wielu kluczy |
| ElevenBytes / [Custom] | ElevenLabs-like API / manual | Online | `tts_elevenbytes.py` lub manualny WAV/EAC3 |

---

## 🔄 Pipeline Flow

```
USER START (run_mm_avh.bat / uv run start.py)
│
├─► DISPLAY_LOGO()                       └─ CoolAnimation
│
├─► UPDATE_SETTINGS()                     └─ Settings.load_from_file() + optional change
│
├─► EXTRACT_TRACKS_FROM_MKV()
│   ├─ MkvToolNix.get_mkv_info()
│   ├─ User selects tracks (audio, main subs, alt subs)
│   └─ MkvToolNix.mkv_extract_track()     Output: working_space/temp/*.wav, *.ass
│
├─► REFACTOR_SUBTITLES()
│   └─ SubtitleRefactor.split_ass() → ass_to_srt() → move_srt()
│
├─► TRANSLATE_SUBTITLES(settings)         └─ SubtitleTranslator.translate_srt()
│
├─► CONVERT_NUMBERS_TO_WORDS()            └─ SubtitleRefactor.convert_numbers_in_srt()
│
├─► GENERATE_AUDIO_FOR_SUBTITLES(settings)
│   └─ SubtitleToSpeech.generate_audio(settings)
│      Routes to: harpo | balabolka | edge | stylish | fish | readlover | elevenlabs
│
├─► REFACTOR_ALT_SUBTITLES()             └─ SubtitleRefactor.srt_to_ass()
│
├─► PROCESS_OUTPUT_FILES(settings)        └─ MKVProcessing.process_mkv()
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
- `opencv-python>=4.13.0.90` — CV2 (fallback vision tasks)
- `scipy>=1.17.0` — Signal processing
- `soundfile>=0.13.1` — Odczyt/zapis audio
- `librosa>=0.11.0` — Analiza audio / resampling
- `audioop-lts>=0.2.2` — audioop dla Pythona 3.13+ (usunięty z stdlib)

### Neural TTS Stack (StylishTTS)

- `torch>=2.10.0`, `torchaudio>=2.10.0` — z indeksu `pytorch-cu128` (CUDA 12.8)
- `transformers>=5.3.0` — modele Hugging Face
- `safetensors>=0.7.0` — wagi modeli
- `accelerate>=1.13.0` — akceleracja inferencji
- `einops>=0.8.2` — operacje tensorowe
- `nnaudio>=0.3.4` — audio frontend
- `ring-attention-pytorch>=0.5.20` — attention
- `phonemizer>=3.3.0` — G2P (espeak-ng backend, `bin/espeak-ng/`)
- `monotonic-align` — alignment (git: resemble-ai)
- `munch` — słowniki z dostępem przez atrybuty (config modeli)
- `matplotlib>=3.10.8` — wizualizacje (debug/training)
- `nvidia-ml-py>=13.590.48` — monitoring GPU

### Subtitle Handling

- `pysrt>=1.1.2` — SRT file parsing
- `pysubs2>=1.8.0` — ASS/SSA file parsing
- `pyasstosrt>=1.5.0` — ASS→SRT conversion

### Language/Translation

- `googletrans>=4.0.2` — Google Translate (unofficial)
- `deepl>=1.27.0` — DeepL API (official)
- `nltk>=3.9.2` — Natural Language Toolkit

### UI/Output

- `rich>=14.3.0` — Rich console output (colors, tables, spinners)
- `pydantic>=2.12.5` — Data validation

### System/Utilities

- `pyautogui>=0.9.54` — GUI automation (DeepL Desktop control)
- `pyperclip>=1.11.0` — Clipboard I/O
- `natsort>=8.4.0` — Natural sorting
- `async-timeout>=5.0.1` — Async timeout management
- `numpy>=2.4.1` — Numerical computing
- `six>=1.17.0` — Py2/3 compat shim
- `types-requests>=2.33.0.20260408` — type stubs

---

## 🏗️ Architektura / Design Patterns

- **Dataclass-based Design** — Wiele klas używa `@dataclass(slots=True)`
- **Async/Await** — Edge TTS i klienci API: async batch z semaphore + timeout
- **Router/Dispatcher Pattern** — `translate_srt()`, `generate_audio()`, `process_mkv()` → route wg. settings
- **Adapter Pattern (TTS)** — jednolity interfejs `SubtitleToSpeech` opakowuje 7 backendów (systemowe, online, neural, API)
- **Pipeline Orchestration** — `main()` w `start.py` → sekwencyjne wykonanie krok po kroku
- **Fallback Strategy** — Translation chunking → single-by-single; TTS timeout → fallback; ReadLover → fallback między kluczami API

---

## 🧰 Konfiguracja narzędziowa (AI / repo)

- **`.claude/`** — skille i konfiguracja Claude Code syncowane z zewnętrznego repo `agents` (źródło prawdy tam, katalog jest gitignore'owany). Skille (płasko): `python`, `git`, `instructions`, `ideate`, `simple`, `frontend`, `end`, `ui-ux-design`, `make-interfaces-feel-better`, `social-media`. Dodatkowo `agents/orchestrator.md`, `settings.json` (hooki + permissiony), `statusline.mjs`.
- **`.github/`** — katalog AI (gitignore w całości); aktualnie zawiera tylko `temp/` z roboczymi plikami.
- **`bin/`** — binaria silników (gitignore): `balabolka`, `espeak-ng`, `ffmpeg`, `mkvtoolnix`, `stylish_tts`.

---

## 📚 Test Files (tests/)

| Plik | Cel |
|------|-----|
| `tts_test.py` | Unified TTS test |
| `tts_balcon_test.py` | Test Balabolka |
| `tts_google_test.py` | Test pyttsx3 (Google voice) |
| `tts_local_test.py` | Test pyttsx3 offline |
| `tts_online_edge_test_0/1/2.py` | Test Edge TTS (warianty) |
| `translator_test.py` | Test Google Translate |
| `translator-gpt-re-ask_alt.py` / `...no-re-ask_alt.py` | Test ChatGPT (warianty re-ask) |
| `chat.py` | Eksperymenty z LLM chat |
| `sent_tokenize_test.py` | Test NLTK sentence tokenization |
| `num2words_test.py` | Test konwersji liczb |
| `merge_audio_test.py` | Test audio merge (pydub) |
| `real_esrgan_and_others.py` | Eksperymenty upscalingu / inne |
| `pylint_tests.py` | Lint checks |
| `MM_AVH_pre.py` | Prototype starej wersji |

> Katalogi pomocnicze: `tests/input/`, `tests/output/`.
