# Plan implementacji przebudowy `mm_avh_working_space` od zera

> Data: 2026-07-12
> Tryb: greenfield, nowy branch
> Cel: terminalowy CLI Windows-first, Python 3.10+, `uv`, funkcjonalnie zgodny z obecną aplikacją
> Autor planu: gpt-5.6-sol (xhigh) | na podstawie spec + audytu + wzorców

## 1. Werdykt architektoniczny

Nowa aplikacja będzie małym pakietem `mm_avh/` z płynącym panelem REPL, liniowym pipeline’em i dwoma rejestrami: TTS oraz tłumaczenia. Ekstrakcja, refaktor napisów, wybór ścieżek, heurystyka stylów, miks, merge i render pozostają zwykłymi modułami.

Nie kopiujemy z MangaShift:

- runtime’u i zarządzania VRAM;
- katalogu modeli i downloadera Hugging Face;
- DB, API, workera i event busa;
- generycznego DAG-a kroków;
- async jako domyślnego stylu;
- rozbudowanego systemu configów per runtime.

Przed pierwszym commitem nowego kodu trzeba zamrozić zachowanie obecnej aplikacji na jednym realnym MKV. Greenfield bez takiej bramki bardzo łatwo da kod ładniejszy, ale funkcjonalnie uboższy.

## 2. Rozstrzygnięte decyzje

| Obszar | Decyzja | Uzasadnienie |
|---|---|---|
| UI | `prompt_toolkit` + `rich` + istniejący `utils/rich_console` | `prompt_toolkit` daje inline autocomplete po `/`, historię i edycję linii. `rich` oraz gotowe style, auto-highlight i paski zostają rendererem. Textual wymusza pełnoekranowy model, event loop i dodatkową pracę dla inline `/`; jest przerostem. |
| Config | JSON + dataclass + `/settings` | Jedna osoba i kilkanaście pól nie uzasadniają `pydantic-settings`. `@dataclass(slots=True)`, prosta walidacja i atomowy zapis JSON wystarczą. |
| Klucze API | `.env`, systemowe env ma pierwszeństwo | Bez DPAPI, szyfrowania i secret store. `.env` jest gitignored, `.env.example` nie zawiera wartości. Panel pokazuje tylko „ustawiony/brak”. |
| Binarki | First-run setup, cache w `bin/`, manifest SHA-256 | Binarki nie trafiają do Git. Windows pobiera przypięte archiwa tylko, gdy narzędzi brakuje. Linux korzysta przede wszystkim z `PATH`. |

### Decyzja o binarkach

- Zostają `mkvextract` i `mkvmerge`. Nie dokładamy `pymkv2`, bo nadal wymaga tych samych programów.
- Zostają `ffmpeg` i `ffprobe`. Migracja audio na PyAV nie należy do greenfield parity, a render MP4 nadal wymaga `libx264` i `libass`.
- `mkvinfo`, `mkvpropedit` i `espeak-ng` nie są wymaganiami runtime.
- `balcon` zostaje jako opcjonalny silnik Windows-only. Nie blokuje startu na Linuxie.
- `stylish_tts` nie jest pobierany ani rejestrowany.
- `bootstrap()` nie korzysta z sieci przy każdym starcie. Pobieranie jest wykonywane tylko przy braku narzędzi lub przez `/setup`.
- Błąd pobierania nie blokuje panelu. `/doctor` pokazuje problem, natomiast Enter kończy się czytelnym błędem preflight.

## 3. Twarde granice implementacji

1. `utils/` jest zamrożone. Obecne moduły są używane bez przepisywania, nawet jeśli audyt wskazuje dług. `rich_console/` jest dokładany jako kopia 1:1 z uzgodnionego źródła.
2. Nowy kod ma type hints w każdej funkcji i jawne `-> None`.
3. Dataclassy używają `slots=True`; niemutowalne wyniki także `frozen=True`.
4. Nowy kod używa `Dict`, `List`, `Optional`, `Set`, `Tuple` z `typing`.
5. Kod skopiowany 1:1 do `utils/` jest wyjątkiem i nie jest formatowany.
6. Komentarze opisują tylko nieoczywistą przyczynę, ograniczenie narzędzia lub kontrakt bezpieczeństwa. Bez checklist, emotikon, komentarzy opisujących oczywisty kod i zakomentowanych bloków.
7. Publiczny przebieg jest synchroniczny.
8. `ThreadPoolExecutor` jest dopuszczony dla ekstrakcji wielu MKV i blokujących batchów TTS.
9. Natywne async API uruchamiają jeden event loop na cały batch, nigdy `asyncio.run()` per linia.
10. Rejestr istnieje tylko dla TTS i tłumaczenia.
11. `engine_id` jest stabilnym kluczem `snake_case`; `provider_model_id` oznacza model zewnętrznego dostawcy; `label` należy do CLI.
12. `Path` i `AppPaths` zastępują `getcwd()`, `[2:]` na ścieżkach i zahardkodowaną nazwę repo.
13. Warstwa domenowa nie używa `sys.exit()`. Rzuca wyjątki domenowe obsługiwane przez CLI.
14. Pliki źródłowe są usuwane dopiero po sprawdzeniu kodu wyjścia i walidacji wyniku.
15. Błąd jednego odcinka nie kasuje jego cache ani danych potrzebnych do wznowienia.

## 4. Zakres zgodności funkcjonalnej

### 4.1 TTS

| Nowy `engine_id` | Zachowanie | Platforma | Migracja starej wartości |
|---|---|---|---|
| `sapi5` | Harpo/Zosia przez SAPI | Windows | `TTS - Zosia - Harpo` |
| `balcon` | `balcon.exe`, Ivona/Agnieszka | Windows | `TTS - Agnieszka - Ivona` |
| `edge` | `edge-tts`, głos przez `voice_id` | Windows/Linux | Zofia i Marek |
| `gtts` | Google TTS po live-smoke | Windows/Linux | nowy stabilny klucz |
| `elevenbytes` | obecny proxy-client v6/v7 | Windows/Linux | oba wpisy ElevenBytes |
| `elevenlabs` | oficjalny SDK z EchoReader | Windows/Linux | nowy wpis |

`edge` nie ma dwóch klas tylko dlatego, że ma dwa głosy. `elevenbytes` nie ma dwóch klas tylko dlatego, że ma endpoint v6/v7. Są to parametry silnika, nie osobne silniki.

Wspólna warstwa poza silnikami zachowuje:

- odrzucanie pustych napisów;
- czyszczenie tekstu;
- cache klipów i wznowienie po przerwaniu;
- raport błędów per linia;
- ograniczoną współbieżność;
- dekodowanie i resampling;
- wstawianie ciszy według timingów SRT;
- RF64 dla dużych WAV;
- `atempo` i zmianę głośności;
- miks z oryginalnym audio;
- konwersję do EAC3;
- fallback pomiaru długości dużego WAV.

Istotne rozróżnienie: obecny aktywny ElevenBytes używa prywatnego proxy `teamsp.org`, natomiast EchoReader korzysta z oficjalnego SDK ElevenLabs. Żeby nie zgubić działającej funkcji, oba powinny istnieć równolegle do czasu testu zgodności i decyzji użytkownika.

### 4.2 Tłumaczenie

| `engine_id` | Status | Uwagi |
|---|---|---|
| `google` | obowiązkowy parity | Zachowuje fallback batch → linie → pojedynczo. |
| `deepl` | obowiązkowy parity | Oficjalne API, klucz z `.env`. |
| `openai` | wymagany przez spec, live-test opt-in | Oficjalny klient i `provider_model_id`; bez tokenu sesji ChatGPT. |

DeepL Desktop nie wchodzi do rejestru: jest dziś nieosiągalny z publicznego dispatchu, ma błąd w `replace()` i zależy od kruchego sterowania GUI.

Wspólny kod tłumaczenia odpowiada za:

- usuwanie tagów ASS/HTML i `\h`;
- markery nowych linii;
- deduplikację identycznych fraz;
- batchowanie;
- kontrolę liczby odpowiedzi;
- fallback przy rozjeździe cardinality;
- przypisanie jednego tłumaczenia do wszystkich duplikatów;
- mapowanie SRT → ASS po `(start, end)`;
- pomijanie rysunków wektorowych.

### 4.3 Pipeline

```text
discover
→ extract
→ refactor/split
→ translate
→ numbers (manual)
→ TTS
→ alt SRT→ASS
→ merge/render
→ cleanup tylko sukcesów
```

Tryby wyjścia:

- `player_files`;
- `merge_mkv`;
- `burn_mp4`.

Nie powstaje registry kroków ani rendererów. `PipelineRunner.run()` zapisuje kolejność wprost, a `OutputMode` jest zwykłym `Enum`.

## 5. Docelowa struktura folderów

```text
mm_avh_working_space/
├── start.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── config/
│   └── settings.json
├── bin/
│   ├── README.md
│   ├── manifest.json
│   ├── windows-x86_64/
│   └── linux-x86_64/
├── working_space/
│   ├── input/
│   ├── output/
│   ├── temp/
│   │   ├── main_subs/
│   │   └── alt_subs/
│   ├── cache/
│   └── smoke/
├── mm_avh/
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── errors.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── completer.py
│   │   ├── settings_panel.py
│   │   └── views.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── paths.py
│   │   ├── secrets.py
│   │   ├── store.py
│   │   └── migration.py
│   ├── setup/
│   │   ├── __init__.py
│   │   ├── binaries.py
│   │   └── doctor.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── media/
│   │   │   ├── __init__.py
│   │   │   ├── extraction.py
│   │   │   ├── tracks.py
│   │   │   ├── subtitles.py
│   │   │   ├── style_classifier.py
│   │   │   ├── audio.py
│   │   │   ├── merge.py
│   │   │   └── render.py
│   │   ├── tts/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   ├── types.py
│   │   │   ├── service.py
│   │   │   ├── subtitle_batch.py
│   │   │   ├── timeline.py
│   │   │   ├── postprocess.py
│   │   │   └── engines/
│   │   │       ├── __init__.py
│   │   │       ├── sapi5/
│   │   │       ├── balcon/
│   │   │       ├── edge/
│   │   │       ├── gtts/
│   │   │       ├── elevenbytes/
│   │   │       └── elevenlabs/
│   │   └── translation/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── config.py
│   │       ├── errors.py
│   │       ├── types.py
│   │       ├── text.py
│   │       ├── batching.py
│   │       ├── service.py
│   │       └── engines/
│   │           ├── __init__.py
│   │           ├── google/
│   │           ├── deepl/
│   │           └── openai/
│   └── pipeline/
│       ├── __init__.py
│       ├── models.py
│       └── runner.py
├── utils/
│   ├── cool_animation.py
│   ├── execution_timer.py
│   ├── number_in_words.py
│   ├── text_chunker.py
│   └── rich_console/
├── scripts/
│   ├── maintenance/
│   └── smoke/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── smoke/
└── docs/
```

`utils/` zostaje top-level, aby nie przenosić ani nie przepisywać kodu użytkownika. `pyproject.toml` pakuje zarówno `mm_avh`, jak i `utils`.

## 6. Bramka zgodności przed etapem 1

Przed usunięciem starego kodu trzeba uruchomić jego kontrolowany run. Plik wskazuje `MM_AVH_SMOKE_MKV`; sam MKV pozostaje poza Git.

Zapisywane kontrakty:

1. `mkvmerge --identify`: ścieżki, języki, kodeki, flagi.
2. ID ścieżek wybranych przez auto-mode.
3. Rozszerzenia i rozmiary ekstrakcji.
4. Liczba zdarzeń ASS przed i po split.
5. Wybrane style oraz wynik deduplikacji animacji.
6. Próbki tagów, newline’ów i markerów tłumaczenia.
7. Liczba wywołań API dla powtórzonego tekstu.
8. Parametry WAV/EAC3 i czas z tolerancją 100 ms.
9. Metadane końcowego MKV/MP4.
10. Pliki zachowane/usunięte po sukcesie i błędzie merge.

Do repo trafiają tylko tekstowe oczekiwania i metadane, nie audio ani wideo.

## 7. Kluczowe wzorce

### 7.1 Bazowy kontrakt TTS

`mm_avh/services/tts/base.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class SynthesisRequest:
    text: str
    voice_id: Optional[str] = None
    provider_model_id: Optional[str] = None
    output_format: str = "mp3_44100_128"


class TtsEngine(ABC):
    engine_id: str

    @abstractmethod
    def synthesize(self, request: SynthesisRequest) -> bytes:
        """Zwraca audio pojedynczej wypowiedzi."""

    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdza wymagania silnika bez wykonywania syntezy."""

    def close(self) -> None:
        """Zwalnia zasoby silnika."""
```

### 7.2 Config i registry TTS

`mm_avh/services/tts/config.py`:

```python
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TtsConfig:
    engine_options: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def options_for(self, engine_id: str) -> Dict[str, Any]:
        return dict(self.engine_options.get(engine_id, {}))
```

`mm_avh/services/tts/engines/__init__.py`:

```python
import importlib
from typing import Dict, Final, Tuple, Type, cast

from mm_avh.services.tts.base import TtsEngine
from mm_avh.services.tts.config import TtsConfig
from mm_avh.services.tts.errors import TtsConfigError


_REGISTRY: Final[Dict[str, Tuple[str, str, str]]] = {
    "sapi5": (
        "mm_avh.services.tts.engines.sapi5",
        "Sapi5Engine",
        "Sapi5Config",
    ),
    "balcon": (
        "mm_avh.services.tts.engines.balcon",
        "BalconEngine",
        "BalconConfig",
    ),
    "edge": (
        "mm_avh.services.tts.engines.edge",
        "EdgeEngine",
        "EdgeConfig",
    ),
    "gtts": (
        "mm_avh.services.tts.engines.gtts",
        "GoogleTtsEngine",
        "GoogleTtsConfig",
    ),
    "elevenbytes": (
        "mm_avh.services.tts.engines.elevenbytes",
        "ElevenBytesEngine",
        "ElevenBytesConfig",
    ),
    "elevenlabs": (
        "mm_avh.services.tts.engines.elevenlabs",
        "ElevenLabsEngine",
        "ElevenLabsConfig",
    ),
}


def available_engine_ids() -> Tuple[str, ...]:
    return tuple(_REGISTRY)


def create_engine(config: TtsConfig, *, engine_id: str) -> TtsEngine:
    if engine_id not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise TtsConfigError(
            f"Nieznany silnik TTS: {engine_id!r}. Dostępne: {available}"
        )

    module_path, engine_cls_name, config_cls_name = _REGISTRY[engine_id]
    module = importlib.import_module(module_path)
    engine_cls = cast(Type[TtsEngine], getattr(module, engine_cls_name))
    config_cls = getattr(module, config_cls_name)
    engine_config = config_cls(**config.options_for(engine_id))
    return engine_cls(engine_config)
```

Registry jest jedynym miejscem znającym zestaw implementacji. Labelki UI, migracja starych stringów i domyślne ustawienie per OS pozostają poza nim.

### 7.3 ElevenLabs z retry/backoff

`mm_avh/services/tts/engines/elevenlabs/service.py`:

```python
from dataclasses import dataclass
from random import uniform
from time import sleep
from typing import Any, Final, Optional, Set

from mm_avh.services.tts.base import SynthesisRequest, TtsEngine
from mm_avh.services.tts.errors import TtsConfigError, TtsSynthesisError


RETRY_STATUS_CODES: Final[Set[int]] = {429, 500, 502, 503, 504}
MIN_AUDIO_BYTES: Final[int] = 1024


@dataclass(slots=True)
class ElevenLabsConfig:
    api_key: str
    voice_id: str
    provider_model_id: str = "eleven_flash_v2_5"
    output_format: str = "mp3_44100_128"
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True
    max_retries: int = 5
    backoff_base_seconds: float = 1.0
    backoff_cap_seconds: float = 16.0


class ElevenLabsEngine(TtsEngine):
    engine_id = "elevenlabs"

    def __init__(self, config: ElevenLabsConfig) -> None:
        if not config.api_key:
            raise TtsConfigError("Brak ELEVENLABS_API_KEY")
        if not config.voice_id:
            raise TtsConfigError("Brak voice_id dla ElevenLabs")
        self._config = config
        self._client: Optional[Any] = None

    def is_available(self) -> bool:
        return bool(self._config.api_key and self._config.voice_id)

    def synthesize(self, request: SynthesisRequest) -> bytes:
        if not request.text.strip():
            raise TtsSynthesisError("Tekst TTS jest pusty")

        for attempt in range(self._config.max_retries):
            try:
                return self._synthesize_once(request)
            except Exception as exc:
                last_attempt = attempt + 1 == self._config.max_retries
                if last_attempt or not self._is_retryable(exc):
                    raise TtsSynthesisError(
                        f"ElevenLabs nie wygenerował audio: {exc}"
                    ) from exc

                delay = min(
                    self._config.backoff_cap_seconds,
                    self._config.backoff_base_seconds * (2 ** attempt),
                )
                sleep(delay + uniform(0.0, 0.25))

        raise TtsSynthesisError("ElevenLabs wyczerpał próby syntezy")

    def _synthesize_once(self, request: SynthesisRequest) -> bytes:
        from elevenlabs import ElevenLabs, VoiceSettings

        if self._client is None:
            self._client = ElevenLabs(api_key=self._config.api_key)

        settings = VoiceSettings(
            stability=self._config.stability,
            similarity_boost=self._config.similarity_boost,
            style=self._config.style,
            use_speaker_boost=self._config.use_speaker_boost,
        )
        chunks = self._client.text_to_speech.convert(
            text=request.text,
            voice_id=request.voice_id or self._config.voice_id,
            model_id=(
                request.provider_model_id
                or self._config.provider_model_id
            ),
            voice_settings=settings,
            output_format=(
                request.output_format
                or self._config.output_format
            ),
        )
        audio = b"".join(
            chunk for chunk in chunks if isinstance(chunk, bytes)
        )
        if len(audio) < MIN_AUDIO_BYTES:
            raise TtsSynthesisError(
                "ElevenLabs zwrócił puste lub ucięte audio"
            )
        return audio

    @staticmethod
    def _status_code(exc: Exception) -> Optional[int]:
        status_code = getattr(exc, "status_code", None)
        if isinstance(status_code, int):
            return status_code

        response = getattr(exc, "response", None)
        response_code = getattr(response, "status_code", None)
        return response_code if isinstance(response_code, int) else None

    @classmethod
    def _is_retryable(cls, exc: Exception) -> bool:
        status_code = cls._status_code(exc)
        if status_code in RETRY_STATUS_CODES:
            return True

        name = type(exc).__name__.lower()
        return "timeout" in name or "connection" in name
```

`mm_avh/services/tts/engines/elevenlabs/__init__.py`:

```python
from mm_avh.services.tts.engines.elevenlabs.service import (
    ElevenLabsConfig,
    ElevenLabsEngine,
)

__all__ = ["ElevenLabsConfig", "ElevenLabsEngine"]
```

Retry obejmuje tylko 429, przejściowe 5xx, timeout i błąd połączenia. Błędy 400/401/403 kończą się od razu.

### 7.4 Fasada TTS bez dispatchu per silnik

`mm_avh/services/tts/service.py`:

```python
from pathlib import Path
from typing import Dict

from mm_avh.services.tts.base import SynthesisRequest, TtsEngine
from mm_avh.services.tts.config import TtsConfig
from mm_avh.services.tts.engines import create_engine
from mm_avh.services.tts.errors import TtsUnavailableError


class TtsService:
    def __init__(self, config: TtsConfig) -> None:
        self._config = config
        self._engines: Dict[str, TtsEngine] = {}

    def synthesize_to_file(
        self,
        request: SynthesisRequest,
        output_path: Path,
        *,
        engine_id: str,
    ) -> Path:
        engine = self._engine(engine_id)
        if not engine.is_available():
            raise TtsUnavailableError(
                f"Silnik TTS {engine_id!r} jest niedostępny"
            )

        audio = engine.synthesize(request)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        part_path = output_path.with_suffix(output_path.suffix + ".part")
        part_path.write_bytes(audio)
        part_path.replace(output_path)
        return output_path

    def close(self) -> None:
        for engine in self._engines.values():
            engine.close()
        self._engines.clear()

    def _engine(self, engine_id: str) -> TtsEngine:
        engine = self._engines.get(engine_id)
        if engine is None:
            engine = create_engine(self._config, engine_id=engine_id)
            self._engines[engine_id] = engine
        return engine
```

Jedyny `if` dotyczy cache instancji, nie wyboru implementacji.

### 7.5 `bootstrap()`

`mm_avh/bootstrap.py`:

```python
from dataclasses import dataclass

from dotenv import load_dotenv
from rich.console import Console

from mm_avh.config.models import AppSettings
from mm_avh.config.paths import AppPaths, resolve_paths
from mm_avh.config.secrets import Secrets
from mm_avh.config.store import JsonSettingsStore
from utils.rich_console.console import console


@dataclass(slots=True)
class AppContext:
    paths: AppPaths
    settings: AppSettings
    secrets: Secrets
    settings_store: JsonSettingsStore
    console: Console


def bootstrap() -> AppContext:
    paths = resolve_paths()
    paths.ensure_runtime_directories()
    load_dotenv(dotenv_path=paths.env_file, override=False)

    settings_store = JsonSettingsStore(paths.settings_file)
    settings = settings_store.load()
    secrets = Secrets.from_environment()

    return AppContext(
        paths=paths,
        settings=settings,
        secrets=secrets,
        settings_store=settings_store,
        console=console,
    )
```

`resolve_paths()` wyprowadza root z `MM_AVH_HOME` albo lokalizacji pakietu, nie z bieżącego katalogu procesu.

### 7.6 Panel CLI

`mm_avh/cli/completer.py`:

```python
from typing import Dict, Iterator

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


COMMANDS: Dict[str, str] = {
    "/auto": "Uruchom cały pipeline bez pytań",
    "/manual": "Uruchom pipeline z decyzjami użytkownika",
    "/settings": "Otwórz ustawienia z auto-zapisem",
    "/doctor": "Sprawdź środowisko i binarki",
    "/help": "Pokaż dostępne komendy",
    "/exit": "Zakończ program",
}


class SlashCompleter(Completer):
    def get_completions(
        self,
        document: Document,
        complete_event: object,
    ) -> Iterator[Completion]:
        text = document.text_before_cursor.lstrip()
        if not text.startswith("/"):
            return

        for command, description in COMMANDS.items():
            if command.startswith(text):
                yield Completion(
                    command,
                    start_position=-len(text),
                    display_meta=description,
                )
```

`mm_avh/cli/app.py`:

```python
from dataclasses import replace

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from mm_avh.bootstrap import AppContext
from mm_avh.cli.completer import SlashCompleter
from mm_avh.cli.settings_panel import open_settings_panel
from mm_avh.cli.views import show_banner, show_help
from mm_avh.pipeline.runner import PipelineRunner
from mm_avh.setup.doctor import render_doctor


def run_cli(context: AppContext, runner: PipelineRunner) -> None:
    show_banner(context.console)
    session = PromptSession(
        history=FileHistory(
            str(context.paths.command_history_file)
        ),
        completer=SlashCompleter(),
        complete_while_typing=True,
        bottom_toolbar=(
            "Enter = auto | /help = komendy | Ctrl+C = wyjście"
        ),
    )

    while True:
        try:
            line = session.prompt("mm_avh > ").strip()
        except (EOFError, KeyboardInterrupt):
            context.console.print("\n[yellow]Zakończono.[/]")
            return

        if line == "":
            runner.run_auto()
        elif line == "/auto":
            context.settings = replace(
                context.settings,
                auto_mode=True,
            )
            context.settings_store.save(context.settings)
            runner.run_auto()
        elif line == "/manual":
            context.settings = replace(
                context.settings,
                auto_mode=False,
            )
            context.settings_store.save(context.settings)
            runner.run_manual()
        elif line == "/settings":
            context.settings = open_settings_panel(context)
        elif line == "/doctor":
            render_doctor(context)
        elif line == "/help":
            show_help(context.console)
        elif line == "/exit":
            return
        elif line.startswith("/"):
            context.console.print(
                f"[red]Nieznana komenda:[/] {line}"
            )
        else:
            context.console.print(
                "[dim]Wpisz /help albo naciśnij Enter.[/]"
            )
```

Rich nie uruchamia `Live` podczas aktywnego promptu. Progress rozpoczyna się dopiero po zakończeniu `session.prompt()`.

## 8. Etapy implementacji

## Etap 1 — szkielet, `utils`, config, bootstrap i panel

### Cel

Uruchamialna aplikacja `uv run mm-avh` z:

- bannerem;
- autocomplete `/`;
- historią;
- `/help`;
- `/settings`;
- `/doctor`;
- `/auto`;
- `/manual`;
- Enter=auto.

Pipeline wykonuje jeszcze tylko discovery/preflight i jawnie raportuje, że kroki domenowe nie są podłączone.

### Pliki

- `start.py`: delegacja do `mm_avh.cli.main.main`.
- `mm_avh/bootstrap.py`: `AppContext`, `bootstrap()`.
- `mm_avh/errors.py`: `AppError`, `ConfigurationError`, `ExternalToolError`, `PipelineError`.
- `mm_avh/config/models.py`:
  - `AppSettings`;
  - `validate_settings(settings: AppSettings) -> None`;
  - pola: tryb, engine IDs, batch size, voice/model, speed, volume, post-processing, output, CRF, preset.
- `mm_avh/config/paths.py`:
  - `AppPaths`;
  - `resolve_app_root() -> Path`;
  - `resolve_paths() -> AppPaths`;
  - `resolve_binary(...) -> Optional[Path]`;
  - `platform_key() -> str`.
- `mm_avh/config/secrets.py`:
  - `Secrets.from_environment() -> Secrets`.
- `mm_avh/config/store.py`:
  - `load() -> AppSettings`;
  - `save(settings: AppSettings) -> None`;
  - atomowy `.tmp` → `replace`.
- `mm_avh/config/migration.py`:
  - migracja starego `settings.json`;
  - mapowanie labeli;
  - przeniesienie sekretów do `.env` bez logowania wartości.
- `mm_avh/cli/main.py`, `app.py`, `completer.py`, `views.py`, `settings_panel.py`.
- `mm_avh/setup/doctor.py`:
  - `DoctorCheck`;
  - check Python, workspace, dysk, MKVToolNix, FFmpeg, klucze, input.
- `.env.example`.
- `[project.scripts] mm-avh = "mm_avh.cli.main:main"`.
- `utils/rich_console/` jako kopia 1:1.
- testy configu, CLI i bootstrapu.

### `/settings`

- Tabela bieżących wartości.
- Edycja jednego pola.
- Enter zachowuje wartość.
- `/back` wraca.
- Po zmianie: `dataclasses.replace()`, walidacja, atomowy zapis.
- Sekrety są tylko statusem „ustawiony/brak”.

### Testy

- Round-trip JSON.
- Brakujące/dodatkowe pola.
- Uszkodzony JSON.
- Walidacja zakresów.
- Autocomplete wyłącznie po `/`.
- CLI sterowany testowym stdin.
- Realny MKV: `/doctor` wykrywa plik i niczego nie modyfikuje.
- Wizualny test Windows Terminal.

### Definition of Done

- `uv run mm-avh` działa niezależnie od CWD.
- Enter wykonuje preflight bez tracebacka.
- `/settings` zapisuje JSON.
- Sekrety nie trafiają do JSON i logów.
- Istniejące pliki `utils/` nie zostały zmienione.
- Nowy kod przechodzi `ruff`, `mypy` i testy na Pythonie 3.10.

## Etap 2 — registry TTS i rozbicie god-files

### Cel

Zastąpić `subtitle_to_speech.py` i `tts_elevenbytes.py` silnikami oraz wspólnym batch/timeline/audio.

Po etapie aplikacja z istniejącego SRT i wyekstrahowanego audio produkuje zsynchronizowany WAV/EAC3.

### Pliki i sygnatury

- `tts/base.py`: `SynthesisRequest`, `TtsEngine`.
- `tts/config.py`:
  - `TtsConfig`;
  - `build_tts_config(settings, secrets) -> TtsConfig`.
- `tts/types.py`:
  - `SubtitleClip`;
  - `SynthesizedClip`;
  - `TtsItemResult`;
  - `TtsRunResult`.
- `tts/errors.py`.
- `tts/engines/__init__.py`.
- `engines/sapi5/service.py`:
  - `Sapi5Config`;
  - `Sapi5Engine.synthesize(...) -> bytes`.
- `engines/balcon/service.py`:
  - `BalconConfig`;
  - `BalconEngine.synthesize(...) -> bytes`.
- `engines/edge/service.py`:
  - `EdgeConfig`;
  - jeden event loop na batch.
- `engines/gtts/service.py`.
- `engines/elevenbytes/`:
  - port proxy v6/v7;
  - cache/resume;
  - klucz z `.env`;
  - raport błędów.
- `engines/elevenlabs/`: oficjalny SDK.
- `tts/service.py`: cienka fasada.
- `tts/subtitle_batch.py`:
  - `load_subtitle_clips(path: Path) -> List[SubtitleClip]`;
  - `clean_tts_text(text: str) -> str`;
  - `synthesize_subtitles(...) -> TtsRunResult`.
- `tts/timeline.py`:
  - `decode_clip(...) -> AudioSamples`;
  - `assemble_timeline(...) -> Path`.
- `tts/postprocess.py`:
  - `build_atempo_chain(speed: float) -> List[str]`;
  - `apply_audio_filters(...) -> Path`.
- `media/audio.py`:
  - `probe_duration(...) -> float`;
  - `mix_lector_with_source(...) -> Path`;
  - `convert_to_eac3(...) -> Path`.

### Testy

- Lazy import wszystkich silników.
- Nieznany engine i brak klucza.
- Retry dla 429/5xx/timeout.
- Brak retry dla 400/401/403.
- `atempo` dla wartości granicznych.
- Timeline: luki, nakładanie, pusty klip, resampling.
- Fake engine: cache hit i resume.
- Realny MKV: 10–20 linii Edge i ElevenBytes.
- Tolerancja timingów ±100 ms.
- Live ElevenLabs tylko z `RUN_LIVE_TTS_TESTS=1`.
- Windows-only odsłuch znaków `ąęłóśćźżń`.

### Definition of Done

- Nowy pakiet nie importuje starych god-files.
- Wszystkie silniki mają registry smoke-test.
- Fasada nie zna konkretnych klas.
- `.part` nie jest traktowany jako gotowe audio.
- Cache zostaje po błędzie.
- WAV/EAC3 przechodzi `ffprobe` i test timingów.

## Etap 3 — media i jawny pipeline

### Cel

Przenieść ekstrakcję, track selection, refaktor, merge i render do typowanych modułów. Podłączyć pełny przebieg dla MKV z polskimi napisami.

### Pliki i sygnatury

- `media/extraction.py`:
  - `TrackInfo`, `MediaInfo`, `ExtractionResult`;
  - `identify(source: Path) -> MediaInfo`;
  - `extract(...) -> ExtractionResult`;
  - `extract_many(...) -> List[ExtractionResult]`.
- `media/tracks.py`:
  - zachowane wagi;
  - `score_subtitle_track(...) -> float`;
  - `score_audio_track(...) -> float`;
  - `select_*() -> Optional[TrackInfo]`.
- `media/style_classifier.py`:
  - zachowane progi i algorytm;
  - bez strojenia;
  - bez registry.
- `media/subtitles.py`:
  - `split_ass(...) -> SubtitleSplitResult`;
  - `select_styles_manual(...)`;
  - `select_styles_auto(...)`;
  - `ass_to_srt`;
  - `move_srt`;
  - `txt_to_srt`;
  - `convert_numbers_in_srt`;
  - `srt_to_ass`.
- `media/merge.py`:
  - `merge_to_mkv(...) -> Path`.
- `media/render.py`:
  - `burn_to_mp4(...) -> Path`.
- `pipeline/models.py`:
  - `EpisodeJob`;
  - `EpisodeResult`;
  - `PipelineRunResult`;
  - `PipelineMode`;
  - `OutputMode`.
- `pipeline/runner.py`:
  - `run_auto() -> PipelineRunResult`;
  - `run_manual() -> PipelineRunResult`;
  - `run(mode: PipelineMode) -> PipelineRunResult`.

### Zachowanie

- Auto wybiera tracki i style.
- Polskie napisy omijają tłumaczenie.
- Obce napisy kończą się stanem `blocked`, nie generują TTS z obcego tekstu.
- Manual zachowuje wszystkie decyzje użytkownika.
- Interakcja istnieje wyłącznie w `cli/`.
- Cleanup działa per odcinek i tylko po sukcesie.

### Testy

- Regresja 206 wyborów tracków.
- Port testów klasyfikatora i `srt_to_ass`.
- Ścieżki ze spacjami, polskimi znakami i UNC.
- Non-zero exit nie usuwa wejść.
- Realny polski MKV dla trzech output modes.
- Przerwanie renderu nie zmienia nazwy źródłowego MKV.

### Definition of Done

- Enter przetwarza polski MKV bez pytań.
- Serwisy nie używają `input()`, `sys.exit()` ani `getcwd()`.
- Nie istnieje `suppress(Exception)` wokół FFmpeg.
- Nie ma kasowania po nieudanym merge.
- Trzy tryby wyjścia przechodzą smoke.

## Etap 4 — registry tłumaczenia, dedup i markery

### Cel

Włączyć pełny pipeline dla napisów obcojęzycznych oraz usunąć duplikację Google/DeepL.

### Pliki i sygnatury

- `translation/base.py`:
  - `translate_batch(...) -> List[str]`;
  - `is_available() -> bool`;
  - `close() -> None`.
- `translation/config.py`.
- `translation/types.py`:
  - `TranslationRequest`;
  - `TranslationItem`;
  - `TranslationReport`.
- `translation/text.py`:
  - `clean_subtitle_text(text: str) -> str`;
  - `mark_newlines(...) -> str`;
  - `restore_markers(...) -> str`.
- `translation/batching.py`:
  - `deduplicate(...) -> DeduplicatedBatch`;
  - `chunks(...) -> List[List[str]]`;
  - `apply_translations(...) -> List[str]`.
- `translation/engines/__init__.py`.
- `engines/google/service.py`.
- `engines/deepl/service.py`.
- `engines/openai/service.py`.
- `translation/service.py`:
  - `translate_srt(...) -> TranslationReport`.
- `pipeline/runner.py`: `_translate()` pomiędzy refactor i TTS.

### Reguły

- Marker jest generowany per run i sprawdzany na kolizję.
- `zip()` nie jest używany bez kontroli liczby wyników.
- Rozjazd cardinality uruchamia mniejszy batch, następnie pojedyncze linie.
- Silnik nie zajmuje się dedupem ani tagami.
- Google uruchamia jeden event loop na cały plik.
- DeepL używa jednego klienta na run.
- OpenAI wymaga jawnego `provider_model_id`.

### Testy

- 1000 takich samych linii → jedna pozycja do API.
- Tagi ASS, HTML, `\h`, newline, pusty tekst, kolizja markera.
- Za mało/za dużo wyników.
- Fake engine + prawdziwy SRT i późniejsze `srt_to_ass`.
- Realny angielski MKV przez Google albo DeepL.
- Polska ścieżka nie wywołuje API.
- Live API wyłącznie z `RUN_LIVE_TRANSLATION_TESTS=1`.

### Definition of Done

- Pełny Enter-auto działa na obcojęzycznym MKV.
- Google i DeepL korzystają z jednego dedup/batching/marker flow.
- Fasada nie zna konkretnych klas.
- ASS zachowuje metadata, style i timing.
- DeepL Desktop i token sesji ChatGPT nie występują w runtime.

## Etap 5 — binarki i sprzątanie repo

### Cel

Oddzielić zmiany architektury od porządków Git/dysku i potwierdzić instalację z czystego clone’a.

### Pliki

- `bin/manifest.json`.
- `bin/README.md`.
- `setup/binaries.py`:
  - `load_manifest(...) -> BinaryManifest`;
  - `ensure_required_binaries(...) -> BinaryStatus`;
  - `download_archive(...) -> Path`;
  - `verify_sha256(...) -> None`;
  - `extract_archive(...) -> None`.
- `scripts/maintenance/update_binary_hashes.py`.
- `scripts/smoke/clean_install.ps1`.
- `scripts/smoke/clean_install.sh`.
- poprawiony `.gitignore`.
- odchudzony `pyproject.toml`.
- testy downloadera i clean install.

### Operacje porządkowe

1. Zapisać wynik `git ls-files bin`.
2. Usunąć binarki z indeksu, ale nie z lokalnego dysku przed testem downloadera.
3. Zweryfikować absolutną ścieżkę `bin/stylish_tts` i dopiero wtedy usunąć.
4. Usunąć `espeak-ng`, `mkvinfo`, `mkvpropedit` po smoke bez nich.
5. Zachować `balcon` jako opcjonalny asset Windows.
6. Przejrzeć każdy skrypt z `temp/`.
7. Przenieść trwałe skrypty do `scripts/maintenance` lub `scripts/smoke`.
8. Nie usuwać automatem prywatnych MKV/SRT z `working_space`.
9. Usunąć ciężkie zależności dopiero po `rg` importów i pełnym smoke.
10. Stary kod usunąć dopiero w ostatnim commicie po golden master parity.

### Testy

- Dobry i zły SHA-256.
- Przerwany download.
- Path traversal w archiwum.
- Brak oczekiwanego pliku.
- Clean clone Windows: pierwszy start pobiera, drugi nie używa sieci.
- Clean clone Linux: narzędzia z `PATH`, brak importów Windows-only.
- Pełny smoke realnego MKV.
- `git ls-files bin` pokazuje tylko README i manifest.

### Definition of Done

- Repo nie zawiera binarek, modeli, sekretów, MKV, WAV ani cache.
- `stylish_tts`, `espeak-ng`, `mkvinfo`, `mkvpropedit` nie są wymagane.
- Clean install jest powtarzalny.
- Pełny suite przechodzi przed skasowaniem legacy.
- Sprzątanie jest osobnym commitem od zmian architektury.

## 9. Kolejność commitów

1. `test(contract): capture legacy MKV behavior`
2. `feat(core): add package, paths, JSON config and bootstrap`
3. `feat(cli): add prompt_toolkit REPL and settings panel`
4. `feat(tts): add base contract and lazy registry`
5. `feat(tts): add engines with parity tests`
6. `feat(tts): add batch, timeline and audio finalization`
7. `feat(media): add extraction and track selection`
8. `feat(media): add subtitle refactor and preserved classifier`
9. `feat(media): add merge/render and Polish-input pipeline`
10. `feat(translation): add dedup, markers and registry`
11. `feat(pipeline): enable foreign-subtitle full run`
12. `chore(setup): add binary downloader`
13. `chore(repo): untrack binaries and remove dead assets`
14. `chore(greenfield): remove legacy code after parity gate`

Nie łączymy registry TTS z usuwaniem `stylish_tts` ani poprawką `.gitignore`.

## 10. Strategia testów

- `tests/unit`: config, registry, retry, command builders, markery, dedup, timeline.
- `tests/contract`: stare → nowe zachowanie.
- `tests/integration`: prawdziwe SRT/ASS i kontrolowane atrapy procesów/API.
- `tests/smoke`: lokalny realny MKV i prawdziwe binarki.
- Live API wyłącznie przez jawne flagi.

Polecenia bramkowe:

```powershell
uv run ruff check mm_avh tests
uv run mypy mm_avh
uv run pytest tests/unit tests/contract tests/integration -q
uv run python scripts/smoke/run_real_mkv.py --input $env:MM_AVH_SMOKE_MKV --mode merge_mkv
```

Smoke zapisuje raport JSON z wersjami binarek, `engine_id`, czasami kroków i metadanymi wyniku.

## 11. Ryzyka i niepewności

1. `utils/rich_console` nie leży w obecnym checkoutcie. Przed etapem 1 trzeba wskazać konkretny commit lub katalog źródłowy.
2. Obecny ElevenBytes i oficjalny ElevenLabs mają inne endpointy, klucze i potencjalnie koszty. Plan zachowuje oba do czasu decyzji po live parity.
3. GPT nie jest dziś osiągalny z produkcyjnego `modules/translator.py`. Spec wymaga go, więc nowy `openai` powinien używać oficjalnego API; użytkownik musi wskazać `provider_model_id`.
4. Google TTS jest dziś eksperymentem, nie aktywnym wpisem menu. Trafia do registry z powodu specu, ale nie może zostać domyślny przed testem.
5. SAPI/Ivona zależy od lokalnej instalacji głosów. Testy automatyczne potwierdzą format i timing, nie jakość.
6. Audio nie będzie bit-identyczne między SDK i wersjami FFmpeg. Kryterium parity to metadane i tolerancja timingów.
7. Escaping filtra `subtitles=` na Windows wymaga testów ze spacjami, apostrofami, literą dysku i UNC.
8. `prompt_toolkit` oraz Rich mogą kolidować przy równoległym renderowaniu. Należy utrzymać render sekwencyjny i przetestować wielopaskową ekstrakcję.
9. Brakuje zatwierdzonego małego MKV smoke.
10. Downloader wymaga stabilnych URL-i, hashy i przeglądu licencji.
11. Cleanup `working_space` grozi utratą danych użytkownika. Automatyczne kasowanie luźnych plików jest zakazane.
12. Python 3.10 może ujawnić zależności zakładające 3.14. Test 3.10 musi działać od etapu 1.

## 12. Podsumowanie

Wybrany interfejs to `prompt_toolkit + rich`, ponieważ daje prosty REPL z inline autocomplete i wykorzystuje gotowy `utils/rich_console`. Konfiguracja będzie zwykłym JSON-em edytowanym przez `/settings`, a sekrety pozostaną w `.env` bez szyfrowania. Binarki nie będą commitowane: Windows pobierze przypięte i zweryfikowane SHA-256 archiwa przy first-run setupie, a Linux użyje przede wszystkim `PATH`. Implementacja ma pięć etapów; pierwszym krokiem przed kodem jest zapis golden mastera na realnym MKV, a pierwszym etapem właściwym jest szkielet, config i panel. Największy zysk daje etap 2, czyli rozbicie 1810 linii TTS na registry, silniki i wspólny batch/timeline. Największym ryzykiem jest zachowanie zgodności aktywnego ElevenBytes proxy oraz timingów audio podczas przejścia na nowe granice serwisów.
