# Wzorzec TTS z EchoReader — analiza jako materiał dla rejestru silników mm_avh

Raport mapuje serwis TTS z projektu **EchoReader** (`C:\Users\MattyMroz\Desktop\PROJECTS\EchoReader\echoreader\services\tts`) jako potencjalny wzorzec do przebudowy TTS w mm_avh (dziś: `subtitle_to_speech.py` 1196 linii + `tts_elevenbytes.py` 617 linii — god-files pełne if/elif per silnik). EchoReader ma trzy silniki, które mm_avh potrzebuje: **edge**, **elevenlabs**, **sapi5**.

**Uwaga metodologiczna / szczera na wstępie:** przeczytano każdy plik w folderze. Wniosek kluczowy, zanim wejdziemy w szczegóły: EchoReader **NIE** jest czystym rejestrem silników w stylu MangaShift. To hybryda — ma bardzo dobrą warstwę bazową (`TTSProvider` ABC) i per-silnikowy podział na foldery, **ale dispatch odbywa się przez `if/elif job.backend == "edge"/"sapi5"/"elevenlabs"`** w `manager.py`. Czyli dokładnie ten anty-wzorzec, od którego mm_avh chce uciec. To trzeba nazwać wprost i tego jednego elementu **nie kopiować** — resztę tak.

---

## 1. Struktura folderu `services/tts/`

```
services/tts/
├── README.md               — dokumentacja: 3 backendy, kolejka, ffmpeg time-stretch
├── __init__.py             — re-export wszystkich providerów + funkcji API (płaski publiczny interfejs)
├── base.py                 — [KLUCZOWE] TTSProvider (ABC) + play_audio_bytes_sync() helper
├── manager.py              — [KLUCZOWE, ale problem] TTSManager: singleton, kolejka, wątek
│                             odtwarzania, DISPATCH PRZEZ if/elif (nie rejestr!)
├── edge/
│   ├── __init__.py         — re-export EdgeTTSProvider, edge_synthesize, list_edge_voices, patcher
│   ├── service.py          — edge_synthesize() (func API) + EdgeTTSProvider (class API)
│   ├── constants.py        — EDGE_TTS_DEFAULT_RATE="+40%", DEFAULT_VOLUME="+0%"
│   ├── patcher.py          — patch_edge_tts_bitrate(): podmienia 48k→96k w pakiecie edge_tts
│   └── voices.py           — EdgeVoiceCatalog: 322+ głosów z Bing API, cache lokalny + dataclass EdgeVoice
├── elevenlabs/
│   ├── __init__.py         — re-export ElevenLabsTTSProvider + funkcje kluczy API + list_voices/models
│   ├── service.py          — [GŁÓWNE dla mm_avh] elevenlabs_synthesize() + provider + zarządzanie
│   │                         kluczem API (DPAPI/base64) + cache głosów (TTL 5 min) + ElevenLabsVoice
│   └── constants.py        — DEFAULT_MODEL="eleven_flash_v2_5", OUTPUT_FORMAT, VOICE_SETTINGS dict
└── sapi5/
    ├── __init__.py         — re-export Sapi5TTSProvider, sapi5_synthesize, sapi5_list_voices
    ├── service.py          — sapi5_synthesize() przez win32com COM + fallback balcon.exe (Ivona)
    └── constants.py        — SAPI5_VOICES (alias→nazwa), SAPI5_DEFAULTS (voice→(rate,volume))
```

**Zasada organizacji:** jeden silnik = jeden podfolder. Każdy podfolder ma **ten sam szkielet**: `__init__.py` (re-export), `service.py` (implementacja), `constants.py` (domyślne wartości). To identyczne z regułą MangaShift `engines/<silnik>/`. Różnica: brak wspólnego folderu `engines/` — silniki leżą bezpośrednio w `tts/`, i **brak pliku-rejestru** (`engines/__init__.py` z `_REGISTRY`).

**Dualne API w każdym silniku** — to charakterystyczna decyzja EchoReader:
- **Function API** (`edge_synthesize`, `elevenlabs_synthesize`, `sapi5_synthesize`) — preferowane, używane przez `TTSManager`.
- **Class API** (`EdgeTTSProvider`, `ElevenLabsTTSProvider`, `Sapi5TTSProvider`) — dziedziczy po `TTSProvider` ABC, "backward compat for orchestrator". To cienki wrapper wokół funkcji.

---

## 2. Rejestr silników — GDZIE i JAK (i dlaczego to NIE jest prawdziwy rejestr)

**Nie ma rejestru string→klasa.** Dispatch to `if/elif` w dwóch miejscach `manager.py`:

Miejsce 1 — publiczne API to **trzy osobne metody** (nie jedna `play(engine_id, ...)`):
```python
def play_edge(self, text, voice="pl-PL-ZofiaNeural", rate="+40%", volume="+0%", playback_speed=1.0): ...
def play_sapi5(self, text, voice="Zosia", rate=None, volume=None, playback_speed=1.0): ...
def play_elevenlabs(self, text, voice_id="", model_id="eleven_flash_v2_5", stability=None, ...): ...
```

Miejsce 2 — `_process_job()` rozgałęzia po stringu `job.backend`:
```python
if job.backend == "edge":
    audio_bytes = self._synthesize_edge(job)
elif job.backend == "sapi5":
    audio_bytes = self._synthesize_sapi5(job)
elif job.backend == "elevenlabs":
    audio_bytes = self._synthesize_elevenlabs(job)
else:
    logger.warning("Unknown TTS backend: {}", job.backend)
    return
```

Plus są trzy osobne metody `_synthesize_edge/_synthesize_sapi5/_synthesize_elevenlabs`, każda z własną logiką timeoutów. **To jest dokładnie ten god-manager z if-ami per silnik, który mm_avh ma dziś i chce wywalić.** Dodanie 4. silnika w EchoReader = nowa metoda `play_X` + nowa gałąź `elif` + nowa metoda `_synthesize_X` + nowe pola w `_TTSJob`. To 4 miejsca do dotknięcia — anty-wzorzec.

**Jedyny element zbliżony do rejestru** to `__init__.py` na poziomie `tts/`, który re-eksportuje wszystko płasko. To nie rejestr, to fasada importów.

**Wniosek:** wzorzec dispatchu EchoReader = odrzucić. Wzorzec bazowej klasy + per-silnikowych folderów = wziąć. MangaShift ma lepszy dispatch (patrz §8).

---

## 3. Wspólny interfejs / bazowa klasa — `base.py`

To jest najlepsza część EchoReader i warta skopiowania niemal 1:1. Krótki, czysty ABC:

```python
from abc import ABC, abstractmethod

class TTSProvider(ABC):
    """Base class for text-to-speech providers."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to raw audio bytes (WAV/MP3)."""

    @abstractmethod
    async def speak(self, text: str) -> None:
        """Synthesize and play text directly."""

    @abstractmethod
    def get_name(self) -> str:
        """Return provider name."""

    @abstractmethod
    def stop(self) -> None:
        """Stop any ongoing playback."""
```

Plus wolna funkcja-helper w tym samym pliku (odtwarzanie audio wspólne dla wszystkich silników):
```python
def play_audio_bytes_sync(audio_bytes: bytes) -> None:
    """Play audio bytes synchronously using sounddevice + soundfile. Works with WAV and MP3."""
    # walidacja rozmiaru → sf.read(BytesIO) → sd.stop()/sd.play()/sd.wait()
```

**Kontrakt silnika:** `synthesize(text) -> bytes` (async, zwraca surowe audio MP3/WAV), `speak(text)` (async, syntetyzuje + gra), `get_name() -> str`, `stop()`. Metoda `synthesize` jest kluczowa — reszta to wygoda.

**Ocena kontraktu dla mm_avh:** kontrakt EchoReader jest zorientowany na **odtwarzanie na żywo** (`speak`, `stop`, playback przez sounddevice). mm_avh **nie odtwarza** — mm_avh **zapisuje audio do pliku** (lektor do zmergowania z wideo). Czyli z tego kontraktu mm_avh potrzebuje głównie `synthesize(text) -> bytes` (albo `synthesize_to_file(text, path)`), a `speak`/`stop`/`play_audio_bytes_sync` są zbędne. To istotna różnica domenowa — patrz §7 i §8.

Warto zauważyć: `Sapi5TTSProvider.synthesize` zwraca `bytes` (czyta WAV z pliku i kasuje), ale wewnętrznie `sapi5_synthesize` zwraca **ścieżkę do pliku WAV**. Czyli EchoReader też operuje na plikach pod spodem — bo SAPI5/balcon piszą do pliku. To dobra wskazówka dla mm_avh (który i tak chce pliki).

---

## 4. Każdy silnik osobno

### 4.1 Edge (`edge/service.py`) — najprostszy

Czysto async, funkcja + klasa:
```python
async def edge_synthesize(text, voice="pl-PL-ZofiaNeural", rate="+40%", volume="+0%") -> bytes:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    audio_chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
    return b"".join(audio_chunks)
```
- **Woła:** bibliotekę `edge_tts` (online, streaming async), import na górze pliku.
- **Config:** tylko dwie stałe (`rate`, `volume`) w `constants.py`. Zero kluczy API.
- **Extra:** `patcher.py` — hack podmieniający stałą bitrate 48k→96k w źródle pakietu `edge_tts` (modyfikuje `communicate.py` w site-packages!). `voices.py` — katalog 322 głosów z Bing API z lokalnym cache. Oba to bonusy, nie rdzeń.
- **Async/sync:** natywnie async.

### 4.2 ElevenLabs (`elevenlabs/service.py`) — GŁÓWNY dla mm_avh, najbogatszy

Rdzeń syntezy (sync SDK, wołany z wątku/executora):
```python
def elevenlabs_synthesize(
    text, voice_id,
    model_id="eleven_flash_v2_5",
    api_key=None,
    stability=None, similarity_boost=None, style=None, use_speaker_boost=None,
    output_format="mp3_44100_128",
) -> bytes:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    client = _get_client(api_key)                      # ElevenLabs(api_key=...), ValueError gdy brak klucza

    from elevenlabs import VoiceSettings
    defaults = ELEVENLABS_VOICE_SETTINGS               # {stability:0.5, similarity_boost:0.75, style:0.0, use_speaker_boost:True}
    voice_settings = VoiceSettings(
        stability=stability if stability is not None else defaults["stability"],
        similarity_boost=similarity_boost if similarity_boost is not None else defaults["similarity_boost"],
        style=style if style is not None else defaults["style"],
        use_speaker_boost=use_speaker_boost if use_speaker_boost is not None else defaults["use_speaker_boost"],
    )
    try:
        audio_iterator = client.text_to_speech.convert(
            text=text, voice_id=voice_id, model_id=model_id,
            voice_settings=voice_settings, output_format=output_format,
        )
        audio_chunks = [c for c in audio_iterator if isinstance(c, bytes)]
        if not audio_chunks:
            raise RuntimeError(f"ElevenLabs returned no audio for voice_id={voice_id}")
        return b"".join(audio_chunks)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"ElevenLabs synthesis failed: {exc}") from exc
```

- **Woła:** oficjalny SDK `elevenlabs` (sync `client.text_to_speech.convert`, zwraca iterator chunków bytes). **Uwaga:** to SDK, nie ręczne `requests`/`httpx` na endpoint. mm_avh w `tts_elevenbytes.py` prawdopodobnie woła API ręcznie — tu jest gotowy SDK-wrapper.
- **voice_settings:** dataclass `VoiceSettings` z 4 polami; defaulty w `constants.py` (`ELEVENLABS_VOICE_SETTINGS`), nadpisywane per-wywołanie gdy user poda wartość. Wzorzec "None → default" jest czysty.
- **Retry:** **BRAK retry/backoff.** Jeden strzał, wyjątek → `RuntimeError`. To luka — dla produkcyjnego lektora ElevenLabs (rate limity 429, chwilowe 5xx) mm_avh będzie chciał retry z backoffem, którego tu nie ma.
- **Obsługa błędów:** `ValueError` (pusty tekst / brak klucza) przepuszczany; reszta owinięta w `RuntimeError`. Prosto, ale bez rozróżnienia 401/429/5xx.
- **Klucze API:** trójstopniowo (`load_api_key`): (1) env `ELEVENLABS_API_KEY`, (2) plik szyfrowany Windows DPAPI (`workspace/temp/elevenlabs_key.enc`), (3) fallback base64 (`.b64`). `save_api_key`/`delete_api_key`/`has_api_key`/`validate_api_key` (ten robi lekki `client.voices.get_all()`).
- **Cache głosów:** `elevenlabs_list_voices()` cachuje listę do JSON (TTL 300s), fallback na cache gdy API padnie. Dataclass `ElevenLabsVoice` (voice_id, name, category, labels, preview_url) z `display_name` do UI.
- **Modele:** `elevenlabs_list_models()` zwraca statyczną listę 4 modeli (eleven_v3, flash_v2_5, turbo_v2_5, multilingual_v2) z opisami po polsku.
- **Async/sync:** rdzeń **sync**; klasa `ElevenLabsTTSProvider.synthesize` opakowuje w `loop.run_in_executor`.

### 4.3 SAPI5 (`sapi5/service.py`) — najbardziej złożony technicznie (Windows COM)

- **Woła:** bezpośrednio COM przez `win32com.client.Dispatch("SAPI.SpVoice")` — **nie** pyttsx3 (świadomie odrzucony: pyttsx3 `runAndWait` wiesza się na Windows po rapid stop/start). Synteza do pliku WAV przez `SpFileStream`.
- **Wątek COM:** jeden `SpVoice` na jednym trwałym wątku (`ThreadPoolExecutor(max_workers=1)`), `pythoncom.CoInitialize()` na tym wątku. Singleton na poziomie modułu (`_pool`, `_voice`, `_voices_cache`).
- **Fallback balcon.exe:** głosy Ivona (Agnieszka) wieszają COM na Win10/11 → wykrywane (`_needs_balcon`) i syntetyzowane przez subprocess `balcon.exe` (Balabolka CLI).
- **Recovery:** timeout 90s → porzucenie puli i reinit COM; `WaitUntilDone` z timeoutem + purge kolejki mowy przy zawieszeniu.
- **Config:** `SAPI5_VOICES` (alias "Zosia"→pełna nazwa COM), `SAPI5_DEFAULTS` (voice→(rate_wpm, volume)). Konwersja WPM→SAPI rate (`_wpm_to_sapi_rate`).
- **Async/sync:** rdzeń **sync** (COM jest sync), wołany przez pool; klasa opakowuje w executor.

---

## 5. Config / ustawienia

**Brak pydantic, brak jednej klasy Settings.** Config w EchoReader jest rozproszony i minimalistyczny:

| Element | Gdzie | Forma |
|---|---|---|
| Defaulty per silnik | `<silnik>/constants.py` | zwykłe stałe modułowe (`str`, `dict`) |
| Parametry syntezy | argumenty funkcji `*_synthesize(...)` | przekazywane per-wywołanie, `None` → default z constants |
| Klucz API ElevenLabs | `load_api_key()` | env → DPAPI plik → base64 plik (priorytet env) |
| voice_settings ElevenLabs | `ELEVENLABS_VOICE_SETTINGS` dict + arg override | dict w constants, nadpisywany argumentami |
| Głosy | argument `voice`/`voice_id` | string, z aliasami (SAPI5) lub ShortName (edge) |

To jest **prostsze niż MangaShift** (który używa `pydantic-settings` z `env_prefix` per silnik i klasą `ProviderConfig`). EchoReader nie ma `EdgeConfig(ProviderConfig)` — ma po prostu `EDGE_TTS_DEFAULT_RATE = "+40%"`. Dla mm_avh to plus: mniej ceremonii. Minus: brak walidacji typów i brak jednego miejsca na config silnika (parametry wędrują przez sygnatury funkcji).

Dane trwałe (klucz, cache głosów) lądują w `workspace/temp/` — ścieżka zaszyta na sztywno (`Path("workspace/temp")`), bez `resolve_workspace_root()` jak w MangaShift.

---

## 6. Fasada / serwis — jak woła się TTS z zewnątrz

Fasadą jest **`TTSManager`** (singleton `tts_manager` na dole `manager.py`). To **gruba** fasada, nie cienka — robi bardzo dużo:

- **Kolejka** (`queue.Queue`, max 5) + jeden trwały wątek odtwarzania (`_playback_loop`).
- **Generation counter** do anulowania (stop bumpuje generację, stare joby są skipowane).
- **Semafor** (max 2 równoległe syntezy) przeciw wyczerpaniu zasobów.
- **Rate limiter** (min 80ms między enqueue).
- **Persistent asyncio event loop** na osobnym wątku dla edge (async) — most sync↔async przez `asyncio.run_coroutine_threadsafe`.
- **Odtwarzanie** przez sounddevice + **time-stretching przez ffmpeg** (atempo, 0.5–3.0x, przez pipe stdin/stdout).
- **Crash protection** — łapie wszystkie wyjątki, thread excepthook, "NEVER crashes the app".

Wywołanie z zewnątrz (fire-and-forget, non-blocking):
```python
from echoreader.services.tts.manager import tts_manager
tts_manager.play_edge("Witaj!", voice="pl-PL-ZofiaNeural")
tts_manager.play_elevenlabs("Witaj!", voice_id="...", model_id="eleven_flash_v2_5")
tts_manager.stop()
```

**Ocena dla mm_avh:** ta fasada jest zaprojektowana pod **interaktywne odtwarzanie na żywo w aplikacji desktopowej** (czytnik e-booków — user klika, tekst ma się natychmiast odezwać, kolejny klik anuluje poprzedni). To zupełnie inny use-case niż mm_avh. mm_avh **wsadowo generuje plik audio z napisów** i zapisuje do zmergowania. Cała maszyneria (kolejka, generation counter, rate limiter, anulowanie, playback, ffmpeg time-stretch, crash-never) jest dla mm_avh **przerostem/nietrafiona** — mm_avh chce: "weź N linijek napisów → wygeneruj N plików audio (ew. równolegle) → sklej". To batch, nie live queue.

---

## 7. Async czy sync?

**Hybryda, zdominowana przez wątki:**
- `TTSProvider.synthesize`/`speak` — sygnatury `async`.
- Edge — natywnie async (`edge_tts.stream()`).
- ElevenLabs, SAPI5 — rdzeń **sync**, opakowany w `run_in_executor` w klasach.
- `TTSManager` — **głównie wątkowy** (threading), z jednym pomocniczym asyncio loop tylko po to, by wołać async edge z wątkowego świata. To most sync↔async, dość skomplikowany (`_ensure_loop`, `run_coroutine_threadsafe`, tracking futures).

Powód async/wątków w EchoReader: **responsywność UI** — `play_*` musi wrócić natychmiast, synteza+odtwarzanie idą w tle, żeby nie zablokować mostu do frontendu.

**Dla mm_avh:** ten powód nie istnieje (brak UI do odblokowania). mm_avh może być **w pełni sync** i to będzie prostsze do debugowania. Jedyne miejsce, gdzie async/równoległość ma realną wartość dla mm_avh: **równoległe zapytania do API ElevenLabs dla wielu linijek napisów naraz** (I/O-bound, przyspiesza generację lektora). Ale to `asyncio.gather` albo `ThreadPoolExecutor` na poziomie batcha — nie wymaga, by cały serwis był async ani by istniał persistent event loop + kolejka + generation counter.

---

## 8. Tabela zbiorcza: silnik → plik → jak woła → config → async/sync

| Silnik | Plik | Jak woła | Config / klucze | Retry | Async/sync | Format wy. |
|---|---|---|---|---|---|---|
| **edge** | `edge/service.py` | `edge_tts.Communicate().stream()` (biblioteka, online) | `constants.py`: rate `+40%`, volume `+0%`. Zero kluczy | brak | natywnie **async** | MP3 |
| **elevenlabs** | `elevenlabs/service.py` | SDK `elevenlabs.ElevenLabs().text_to_speech.convert()` (cloud) | klucz: env→DPAPI→base64; `VOICE_SETTINGS` dict + argi; model `eleven_flash_v2_5` | **brak** | rdzeń **sync**, klasa przez executor | MP3 |
| **sapi5** | `sapi5/service.py` | `win32com` COM `SAPI.SpVoice`→`SpFileStream`; fallback `balcon.exe` (Ivona) | `SAPI5_VOICES` (alias→nazwa), `SAPI5_DEFAULTS` (rate,vol) | reinit COM + retry 1x | rdzeń **sync** (COM), pool | WAV (plik) |
| *(fasada)* | `manager.py` | `if/elif job.backend` + 3 metody `play_*` / `_synthesize_*` | `_TTSJob` dataclass z polami wszystkich silników | — | wątki + 1 asyncio loop | — |

---

## 9. SZKIELET gotowy do naśladowania

Poniżej **czysty destylat** — co z EchoReader wziąć, zestawione tak, by Sol mógł to naśladować. To NIE jest kod EchoReader 1:1 — to EchoReader oczyszczony z anty-wzorca dispatchu (if/elif) i połączony z rejestrem MangaShift.

### 9.1 Bazowa klasa (z EchoReader, uproszczona pod mm_avh — zapis do pliku, nie playback)

```python
# services/tts/base.py
from abc import ABC, abstractmethod
from pathlib import Path

class TtsEngine(ABC):
    """Kontrakt każdego silnika TTS w mm_avh."""

    engine_id: str          # "elevenlabs" | "edge" | "sapi5"

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Zsyntetyzuj tekst do surowego audio (MP3/WAV bytes). Sync."""

    def synthesize_to_file(self, text: str, out_path: Path) -> Path:
        """Domyślna implementacja: synthesize() + zapis. Silnik może nadpisać
        (np. SAPI5, który natywnie pisze do pliku WAV)."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(self.synthesize(text))
        return out_path

    def is_available(self) -> bool:
        """Czy silnik gotowy (klucz API / biblioteka / binarka obecne)."""
        return True
```

Uwaga: mm_avh **nie potrzebuje** `speak()`/`stop()`/`play_audio_bytes_sync()` z EchoReader — to jest playback na żywo, którego mm_avh nie robi. Wyrzucić.

### 9.2 Rejestr (z MangaShift — bo EchoReader go NIE ma; to jego brakujący element)

```python
# services/tts/engines/__init__.py
import importlib
from typing import Final, Literal

TtsEngineId = Literal["elevenlabs", "edge", "sapi5"]

_REGISTRY: Final[dict[str, tuple[str, str]]] = {
    # engine_id → (ścieżka modułu, nazwa klasy)
    "elevenlabs": ("mm_avh.services.tts.engines.elevenlabs", "ElevenLabsEngine"),
    "edge":       ("mm_avh.services.tts.engines.edge", "EdgeEngine"),
    "sapi5":      ("mm_avh.services.tts.engines.sapi5", "Sapi5Engine"),
}

def available_engine_ids() -> tuple[str, ...]:
    return tuple(_REGISTRY)

def create_engine(engine_id: str, config) -> "TtsEngine":
    if engine_id not in _REGISTRY:
        raise ValueError(f"Nieznany silnik TTS: {engine_id!r}. Dostępne: {sorted(_REGISTRY)}")
    module_path, class_name = _REGISTRY[engine_id]
    module = importlib.import_module(module_path)   # lazy import — silnik ładowany dopiero gdy potrzebny
    engine_cls = getattr(module, class_name)
    return engine_cls(config)
```

**Efekt:** dodanie silnika = 1 wpis w `_REGISTRY` + 1 folder `engines/<nowy>/`. Zero if/elif. Zero zmian w fasadzie. Lazy import = `win32com` (SAPI5) ładowany tylko gdy user wybierze SAPI5.

### 9.3 Jeden silnik — ElevenLabs (rdzeń z EchoReader + retry, którego brakuje)

```python
# services/tts/engines/elevenlabs/service.py
from mm_avh.services.tts.base import TtsEngine
from .constants import DEFAULT_MODEL, DEFAULT_OUTPUT_FORMAT, VOICE_SETTINGS

class ElevenLabsEngine(TtsEngine):
    engine_id = "elevenlabs"

    def __init__(self, config) -> None:
        self._api_key = config.api_key
        self._voice_id = config.voice_id
        self._model_id = config.model_id or DEFAULT_MODEL
        # ... stability/similarity_boost/style/use_speaker_boost z config

    def is_available(self) -> bool:
        return bool(self._api_key and self._voice_id)

    def synthesize(self, text: str) -> bytes:
        if not text.strip():
            raise ValueError("Pusty tekst")
        from elevenlabs import ElevenLabs, VoiceSettings   # lazy import
        client = ElevenLabs(api_key=self._api_key)
        settings = VoiceSettings(
            stability=self._stability if self._stability is not None else VOICE_SETTINGS["stability"],
            similarity_boost=self._similarity if self._similarity is not None else VOICE_SETTINGS["similarity_boost"],
            style=self._style if self._style is not None else VOICE_SETTINGS["style"],
            use_speaker_boost=self._speaker_boost if self._speaker_boost is not None else VOICE_SETTINGS["use_speaker_boost"],
        )
        # DODAĆ względem EchoReader: retry z backoffem na 429/5xx (EchoReader tego NIE ma)
        chunks = client.text_to_speech.convert(
            text=text, voice_id=self._voice_id, model_id=self._model_id,
            voice_settings=settings, output_format=DEFAULT_OUTPUT_FORMAT,
        )
        audio = b"".join(c for c in chunks if isinstance(c, bytes))
        if not audio:
            raise RuntimeError(f"ElevenLabs nie zwrócił audio (voice={self._voice_id})")
        return audio
```

### 9.4 Cienka fasada (czym TTSManager EchoReader NIE jest — on jest gruby)

```python
# services/tts/service.py
from .engines import create_engine

class TtsService:
    def __init__(self, config) -> None:
        self._config = config
        self._cache: dict[str, TtsEngine] = {}

    def _engine(self, engine_id: str) -> TtsEngine:
        if engine_id not in self._cache:
            self._cache[engine_id] = create_engine(engine_id, self._config.for_engine(engine_id))
        return self._cache[engine_id]

    def synthesize_to_file(self, text: str, out_path, *, engine_id: str):
        return self._engine(engine_id).synthesize_to_file(text, out_path)
```

To jest cała fasada — kilkanaście linii, zero if/elif. Batch (wiele linijek) to pętla albo `ThreadPoolExecutor` na tym poziomie, opcjonalnie.

---

## 10. Ocena: EchoReader vs MangaShift jako wzorzec dla mm_avh

**Pytanie usera:** czy EchoReader (mniejszy projekt, bliższy skali mm_avh) daje lepszy/prostszy wzorzec TTS niż ciężki MangaShift? Szczera odpowiedź: **częściowo tak, częściowo nie — i akurat w najważniejszym punkcie (dispatch) MangaShift jest wyraźnie lepszy.**

### Gdzie EchoReader wygrywa (prostota bliższa mm_avh)

1. **Skala i domena** — EchoReader to aplikacja desktopowa jednego usera, nie serwer wielouserowy z DB/API/frontendem. Bliżej mm_avh. Nie ma pokusy "skopiuję na zapas warstwy, których nie potrzebuję".
2. **`base.py` (ABC) jest krótki i czytelny** — 4 metody, plus wolna funkcja-helper. MangaShift ma Protocol + `TtsSynthesisOptionsProvider` + osobne `protocols.py`/`provider.py` — więcej ceremonii. Dla mm_avh 4-metodowy ABC wystarczy.
3. **Config bez pydantic** — zwykłe `constants.py` per silnik + argumenty funkcji. MangaShift ma `ProviderConfig` + `env_prefix` per silnik. Dla mm_avh wersja EchoReader jest lżejsza (choć bez walidacji typów).
4. **Realny, działający kod ElevenLabs przez oficjalny SDK** — gotowy `elevenlabs_synthesize` z voice_settings, cache głosów, zarządzaniem kluczem (DPAPI). mm_avh może to wziąć niemal wprost jako rdzeń swojego głównego silnika. MangaShift ma `elevenbytes`/`elevenlabs`, ale nie widzieliśmy ich kodu — EchoReader daje konkret na stole.

### Gdzie EchoReader przegrywa (i to jest istota pytania o rejestr)

1. **EchoReader NIE MA rejestru silników.** Dispatch to `if/elif job.backend` + 3 osobne metody `play_*` + 3 metody `_synthesize_*`. **To jest dokładnie ten anty-wzorzec, od którego mm_avh ucieka** (dzisiejszy `subtitle_to_speech.py` pełen if-ów per silnik). Kopiowanie `TTSManager` przeniosłoby problem, nie rozwiązało. **Rejestr string→klasa z lazy importem trzeba wziąć z MangaShift** (§9.2) — EchoReader go nie dostarcza.
2. **`TTSManager` to gruba fasada pod zły use-case.** Kolejka + generation counter + rate limiter + persistent asyncio loop + playback + ffmpeg time-stretch + crash-never — to wszystko służy **interaktywnemu odtwarzaniu na żywo** w czytniku. mm_avh robi **batch do pliku**. 80% `manager.py` (890 linii!) jest dla mm_avh nietrafione. Fasada mm_avh powinna mieć kilkanaście linii (§9.4).
3. **Brak retry w ElevenLabs** — produkcyjny lektor uderzy w 429/5xx; EchoReader po prostu rzuca `RuntimeError`. mm_avh musi to dodać.
4. **Async/wątki bez powodu dla mm_avh** — cała hybryda sync/async + most przez event loop istnieje dla responsywności UI. mm_avh nie ma UI; sync jest prostszy.

### Werdykt

**Najlepszy wzorzec dla mm_avh = hybryda, nie wybór jednego projektu:**

- **Z EchoReader wziąć:** (a) krótki `base.py` ABC jako kontrakt silnika (odchudzony do `synthesize`/`synthesize_to_file`/`is_available` — bez `speak`/`stop`/playback), (b) podział na foldery `<silnik>/service.py + constants.py`, (c) **gotowy kod ElevenLabs przez oficjalny SDK** (voice_settings, cache głosów, zarządzanie kluczem DPAPI/env) — to największa realna wartość, (d) prostotę configu (`constants.py` zamiast pydantic, jeśli mm_avh nie chce walidacji), (e) świadome rozwiązania SAPI5 (COM zamiast pyttsx3, fallback balcon dla Ivony) jeśli mm_avh utrzyma SAPI5.
- **Z MangaShift wziąć:** **rejestr** — `engines/__init__.py` z `_REGISTRY: dict[engine_id, (module_path, class_name)]` + `create_engine()` z lazy importem (§9.2). To jest brakujący element EchoReader i sedno tego, o co prosi mm_avh ("zero if-ów, dodanie silnika = nowy plik + wpis").
- **Odrzucić z EchoReader:** cały `TTSManager` (kolejka/generation/rate-limiter/asyncio-loop/playback/ffmpeg/crash-never), dispatch if/elif, warstwę playback (`speak`/`stop`/`play_audio_bytes_sync`), async-jako-domyślny-styl.
- **Odrzucić z MangaShift:** (jak w raporcie 06) `ProviderConfig`+pydantic per silnik jeśli mm_avh chce lżej, `TtsSynthesisOptionsProvider`, batch z semaforami async, voice cache TTL — chyba że pojawi się realna potrzeba.

Krótko: **EchoReader daje lepszy, gotowy do przeklejenia KOD silników (zwłaszcza ElevenLabs) i lżejszy kontrakt bazowy; MangaShift daje lepszą STRUKTURĘ dispatchu (rejestr).** mm_avh chce dokładnie sumy tych dwóch: silniki à la EchoReader wpięte w rejestr à la MangaShift, z cienką fasadą batch-do-pliku i sync-first (async tylko dla równoległych zapytań do API ElevenLabs, jeśli w ogóle).

---

## 11. Co wziąć 1:1, co zaadaptować (skrót operacyjny)

| Element | Źródło | Akcja |
|---|---|---|
| Rejestr `_REGISTRY` + `create_engine()` lazy import | **MangaShift** | **1:1** (EchoReader tego nie ma) |
| `base.py` ABC (kontrakt silnika) | EchoReader | **Adaptować** — zostaw `synthesize`, dodaj `synthesize_to_file`, usuń `speak`/`stop`/playback |
| Kod ElevenLabs (SDK convert + voice_settings) | EchoReader | **~1:1** + dodać retry/backoff na 429/5xx |
| Zarządzanie kluczem API (env→DPAPI→base64) | EchoReader | **1:1** (ale ścieżkę przez `resolve_workspace_root()`, nie hardcode `workspace/temp`) |
| Cache głosów ElevenLabs (TTL JSON) | EchoReader | **Opcjonalnie** — tylko jeśli mm_avh listuje głosy w UI/CLI |
| Podział `<silnik>/service.py + constants.py` | EchoReader (= MangaShift) | **1:1** |
| Kod SAPI5 (COM + balcon fallback) | EchoReader | **~1:1** jeśli SAPI5 zostaje (do lamusa, ale działa) |
| Kod edge (`edge_tts.stream`) + patcher bitrate | EchoReader | **~1:1**, patcher opcjonalny |
| Config per-silnik z `env_prefix` (pydantic) | MangaShift | **Opcjonalnie** — jeśli mm_avh chce walidacji; inaczej `constants.py` à la EchoReader |
| Cienka fasada `TtsService` (dict cache silników) | MangaShift (idea) + §9.4 | **Adaptować** — kilkanaście linii, batch przez pętlę/executor |
| `TTSManager` (kolejka/playback/asyncio/ffmpeg) | EchoReader | **ODRZUCIĆ** — zły use-case (live playback, nie batch-do-pliku) |
| Dispatch if/elif per backend | EchoReader | **ODRZUCIĆ** — zastąpić rejestrem |
| Async-first + persistent event loop | EchoReader | **ODRZUCIĆ** — mm_avh sync-first |
