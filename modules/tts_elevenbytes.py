"""ElevenBytes TTS — produkcyjna biblioteka async/sync.

Jeden plik, jedna zależność (httpx). Retry, concurrency control, batch, walidacja.
Formaty: mp3 (default), wav, ogg, flac (wav/ogg/flac wymaga ffmpeg w PATH lub imageio-ffmpeg).

    async with TTS(output_dir="output/audio") as tts:
        # Pojedyncza synteza — auto-path w output_dir
        audio = await tts.synthesize("Cześć!")
        await tts.synthesize_to_file("Test")           # → output/audio/tts_*.mp3
        await tts.synthesize_to_file("Test", fmt="wav") # → output/audio/tts_*.wav

        # Custom nazwa pliku → trafia do output_dir
        await tts.synthesize_to_file("Test", path="moj.wav")  # → output/audio/moj.wav

        # Full path → ignoruje output_dir
        await tts.synthesize_to_file("Test", path="C:/tmp/cos.mp3")

        # Batch — wiele tekstów równolegle
        results = await tts.synthesize_batch(["Tekst 1", "Tekst 2"], fmt="wav")

        # Dynamiczne głosy
        tts.add_voice("rachel", "Rachel — Calm", "21m00Tcm4TlvDq8ikWAM")
        audio = await tts.synthesize("Hej!", voice="rachel")

        # Raw voice_id bez rejestracji
        audio = await tts.synthesize("Hej!", voice="jakaś_voice_id")

    # Sync:
    tts = TTS(output_dir="output")
    audio = tts.synthesize_sync("Cześć!", fmt="wav")
    tts.close_sync()
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import shutil
import threading
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

log = logging.getLogger("elevenbytes")

# ─── Config ────────────────────────────────────────────────────────────────────

API_KEY: str = "wqpwgoGhADAwIdb1JRNTAEBgg="
API_URL: str = "https://teamsp.org/xi/run6.php"
MAX_CHARS: int = 5000
MIN_CHARS: int = 2
MIN_AUDIO_BYTES: int = 1024
DEFAULT_VOICE: str = "dallin"
DEFAULT_CONCURRENCY: int = 100
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_MAX_RETRIES: int = 100
RETRY_BACKOFF_BASE: float = 2.0
RETRY_STATUS_CODES: frozenset[int] = frozenset({403, 429, 502, 503, 504})
SUPPORTED_FORMATS: frozenset[str] = frozenset({"mp3", "wav", "ogg", "flac"})

# ─── Głosy ElevenLabs ─────────────────────────────────────────────────────────
# alias → (display_name, voice_id)

VOICES: dict[str, tuple[str, str]] = {
    "dallin": ("Dallin — Storyteller", "alFofuDn3cOwyoz1i44T"),
}


# ─── Result types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class SynthResult:
    """Wynik pojedynczej syntezy w batchu."""

    index: int
    text: str
    audio: bytes | None
    ok: bool
    error: str | None = None
    elapsed: float = 0.0
    retries: int = 0


@dataclass(slots=True)
class BatchReport:
    """Raport z batch syntezy."""

    results: list[SynthResult] = field(default_factory=list)
    wall_time: float = 0.0

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def ok_count(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def fail_count(self) -> int:
        return self.total - self.ok_count

    def summary(self) -> str:
        return (
            f"{self.ok_count}/{self.total} OK | "
            f"{self.fail_count} FAIL | "
            f"Wall: {self.wall_time:.1f}s"
        )


# ─── TTS Service ───────────────────────────────────────────────────────────────


class TTSError(Exception):
    """Bazowy wyjątek biblioteki."""


class TTSValidationError(TTSError):
    """Błąd walidacji inputu."""


class TTSAPIError(TTSError):
    """Błąd API po wyczerpaniu retryów."""


class TTS:
    """Async ElevenLabs TTS via ElevenBytes proxy.

    Retry z backoff, concurrency control (semaphore), batch processing.

    Args:
        default_voice: Domyślny głos (alias lub raw voice ID).
        output_dir: Domyślny folder na pliki audio. None = CWD.
        concurrency: Max równoległych requestów (default 20).
        max_retries: Max retryów na 403/429/5xx z exponential backoff.
        timeout: Timeout HTTP w sekundach.
    """

    def __init__(
        self,
        default_voice: str = DEFAULT_VOICE,
        output_dir: str | Path | None = None,
        concurrency: int = DEFAULT_CONCURRENCY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._default_voice = default_voice
        self._output_dir = Path(output_dir) if output_dir else None
        self._max_retries = max_retries
        self._concurrency = concurrency
        self._sem: asyncio.Semaphore | None = None
        transport = httpx.AsyncHTTPTransport(retries=2)
        self._client = httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Referer": "https://teamsp.org/xi/tts.html",
                "Origin": "https://teamsp.org",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
            },
        )
        self._sync_loop: asyncio.AbstractEventLoop | None = None
        self._sync_thread: threading.Thread | None = None

    def _get_sem(self) -> asyncio.Semaphore:
        """Lazy-init semaphore bound to the current running event loop."""
        loop = asyncio.get_running_loop()
        if self._sem is None or self._sem._loop is not loop:  # type: ignore[attr-defined]
            self._sem = asyncio.Semaphore(self._concurrency)
        return self._sem

    # ── Async API ──────────────────────────────────────────────────────────

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        fmt: str = "mp3",
    ) -> bytes:
        """Syntezuj tekst → audio bytes.

        Retry z exponential backoff na 403/429/5xx.
        Concurrency kontrolowana semaforem.

        Args:
            text: Tekst do syntezy (2–5000 znaków).
            voice: Alias głosu lub raw voice ID. None = default.
            fmt: Format wyjściowy: mp3 (default), wav, ogg, flac.

        Returns:
            Surowe bajty audio w wybranym formacie.

        Raises:
            TTSValidationError: Tekst za krótki/długi lub zły format.
            TTSAPIError: API nie odpowiedziało po retryach.
        """
        self._validate_text(text)
        self._validate_format(fmt)
        voice_id = self._resolve_voice(voice or self._default_voice)

        async with self._get_sem():
            mp3_data = await self._request_with_retry(text, voice_id)

        if fmt == "mp3":
            return mp3_data
        return self._convert_audio(mp3_data, fmt)

    async def synthesize_to_file(
        self,
        text: str,
        voice: str | None = None,
        path: str | Path | None = None,
        fmt: str | None = None,
    ) -> Path:
        """Syntezuj tekst → zapisz audio do pliku.

        Args:
            text: Tekst do syntezy.
            voice: Alias głosu lub raw voice ID.
            path: Ścieżka wyjściowa. None = auto w output_dir. Sama nazwa = w output_dir.
            fmt: Format wyjściowy. None = wykryj z rozszerzenia path, default mp3.

        Returns:
            Path do zapisanego pliku.
        """
        if path:
            out = Path(path)
            # Jeśli podana sama nazwa bez katalogu → umieść w output_dir
            if not out.parent.parts and self._output_dir:
                out = self._output_dir / out
            resolved_fmt = fmt or out.suffix.lstrip(".") or "mp3"
        else:
            resolved_fmt = fmt or "mp3"
            out = self._auto_path(resolved_fmt)
        audio = await self.synthesize(text, voice, fmt=resolved_fmt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(audio)
        return out

    async def synthesize_batch(
        self,
        texts: list[str],
        voice: str | None = None,
        save_dir: str | Path | None = None,
        fmt: str = "mp3",
    ) -> BatchReport:
        """Syntezuj wiele tekstów równolegle z concurrency control.

        Args:
            texts: Lista tekstów.
            voice: Głos dla wszystkich (alias lub ID).
            save_dir: Opcjonalny folder — zapisz każdy plik audio.
            fmt: Format wyjściowy: mp3, wav, ogg, flac.

        Returns:
            BatchReport z wynikami per tekst.
        """
        self._validate_format(fmt)
        out_dir = Path(save_dir) if save_dir else None
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)

        t_wall = time.perf_counter()
        tasks = [
            self._batch_item(i, text, voice, out_dir, fmt)
            for i, text in enumerate(texts)
        ]
        results = await asyncio.gather(*tasks)
        wall = time.perf_counter() - t_wall

        report = BatchReport(
            results=sorted(results, key=lambda r: r.index),
            wall_time=wall,
        )
        log.info("Batch done: %s", report.summary())
        return report

    async def close(self) -> None:
        """Zamknij klienta HTTP."""
        await self._client.aclose()

    # ── Sync wrappers ──────────────────────────────────────────────────────

    def synthesize_sync(self, text: str, voice: str | None = None, fmt: str = "mp3") -> bytes:
        """Synchroniczna wersja synthesize()."""
        return self._run_sync(self.synthesize(text, voice, fmt=fmt))  # type: ignore[return-value]

    def synthesize_to_file_sync(
        self,
        text: str,
        voice: str | None = None,
        path: str | Path | None = None,
        fmt: str | None = None,
    ) -> Path:
        """Synchroniczna wersja synthesize_to_file()."""
        return self._run_sync(self.synthesize_to_file(text, voice, path, fmt=fmt))  # type: ignore[return-value]

    def synthesize_batch_sync(
        self,
        texts: list[str],
        voice: str | None = None,
        save_dir: str | Path | None = None,
        fmt: str = "mp3",
    ) -> BatchReport:
        """Synchroniczna wersja synthesize_batch()."""
        return self._run_sync(self.synthesize_batch(texts, voice, save_dir, fmt=fmt))  # type: ignore[return-value]

    def close_sync(self) -> None:
        """Zamknij klienta HTTP i persistent event loop."""
        if self._sync_loop and not self._sync_loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(self.close(), self._sync_loop)
            future.result(timeout=10)
            self._sync_loop.call_soon_threadsafe(self._sync_loop.stop)
            if self._sync_thread:
                self._sync_thread.join(timeout=5)
            self._sync_loop.close()
            self._sync_loop = None
            self._sync_thread = None
        else:
            try:
                asyncio.run(self.close())
            except Exception:
                pass

    # ── Context manager ────────────────────────────────────────────────────

    async def __aenter__(self) -> TTS:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    # ── Utilities ──────────────────────────────────────────────────────────

    @staticmethod
    def list_voices() -> dict[str, tuple[str, str]]:
        """Zwróć dostępne głosy: {alias: (name, voice_id)}."""
        return dict(VOICES)

    @staticmethod
    def add_voice(alias: str, name: str, voice_id: str) -> None:
        """Dynamicznie dodaj głos w runtime.

        Args:
            alias: Krótki alias (np. "rachel").
            name: Wyświetlana nazwa (np. "Rachel — Calm").
            voice_id: ID głosu z ElevenLabs.
        """
        VOICES[alias] = (name, voice_id)

    @staticmethod
    def remove_voice(alias: str) -> None:
        """Usuń głos z rejestru."""
        VOICES.pop(alias, None)

    @property
    def default_voice(self) -> str:
        return self._default_voice

    @default_voice.setter
    def default_voice(self, alias: str) -> None:
        self._default_voice = alias

    # ── Private ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_text(text: str) -> None:
        if not isinstance(text, str):
            raise TTSValidationError(f"text musi być str, dostałem {type(text).__name__}")
        if len(text) < MIN_CHARS:
            raise TTSValidationError(f"Tekst za krótki ({len(text)} zn., min {MIN_CHARS})")
        if len(text) > MAX_CHARS:
            raise TTSValidationError(f"Tekst za długi ({len(text)} zn., max {MAX_CHARS})")

    async def _request_with_retry(self, text: str, voice_id: str) -> bytes:
        """POST z retry + exponential backoff na retryable status codes."""
        last_status = 0
        last_err = ""

        for attempt in range(1, self._max_retries + 1):
            try:
                resp = await self._client.post(
                    API_URL,
                    data={"text": text, "voice": voice_id, "key": API_KEY},
                )
                last_status = resp.status_code

                if resp.status_code in RETRY_STATUS_CODES:
                    wait = min(RETRY_BACKOFF_BASE * attempt, 5.0)
                    last_err = f"HTTP {resp.status_code}"
                    if attempt < self._max_retries:
                        log.warning(
                            "HTTP %d — retry %d/%d, backoff %.0fs",
                            resp.status_code, attempt, self._max_retries, wait,
                        )
                        await asyncio.sleep(wait)
                        continue

                resp.raise_for_status()

                if len(resp.content) < MIN_AUDIO_BYTES:

                    raise TTSAPIError(
                        f"API zwróciło za mało danych ({len(resp.content)} B, min {MIN_AUDIO_BYTES})"
                    )
                return resp.content

            except httpx.TimeoutException:
                last_err = "timeout"
                if attempt < self._max_retries:
                    wait = min(RETRY_BACKOFF_BASE * attempt, 5.0)
                    log.warning("Timeout — retry %d/%d, backoff %.0fs", attempt, self._max_retries, wait)
                    await asyncio.sleep(wait)
                    continue

            except httpx.HTTPStatusError:
                raise

        raise TTSAPIError(
            f"API nie odpowiedziało po {self._max_retries} próbach "
            f"(last: {last_err or last_status})"
        )

    async def _batch_item(
        self,
        index: int,
        text: str,
        voice: str | None,
        out_dir: Path | None,
        fmt: str = "mp3",
    ) -> SynthResult:
        """Pojedynczy element batcha — łapie błędy, nie crashuje całości."""
        t0 = time.perf_counter()
        retries = 0
        try:
            self._validate_text(text)
            voice_id = self._resolve_voice(voice or self._default_voice)

            async with self._get_sem():
                mp3_data = await self._request_with_retry(text, voice_id)

            audio = mp3_data if fmt == "mp3" else self._convert_audio(mp3_data, fmt)

            if out_dir:
                fname = f"{index:04d}.{fmt}"
                (out_dir / fname).write_bytes(audio)

            return SynthResult(
                index=index, text=text, audio=audio,
                ok=True, elapsed=time.perf_counter() - t0,
            )
        except Exception as exc:
            return SynthResult(
                index=index, text=text, audio=None,
                ok=False, error=str(exc), elapsed=time.perf_counter() - t0,
            )

    @staticmethod
    def _resolve_voice(alias_or_id: str) -> str:
        """Alias → voice_id. Nieznany alias traktowany jako raw ID."""
        if alias_or_id in VOICES:
            return VOICES[alias_or_id][1]
        return alias_or_id

    @staticmethod
    def _validate_format(fmt: str) -> None:
        if fmt not in SUPPORTED_FORMATS:
            raise TTSValidationError(
                f"Nieobsługiwany format '{fmt}'. Dozwolone: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )

    @staticmethod
    def _convert_audio(mp3_data: bytes, target_fmt: str) -> bytes:
        """Konwertuj MP3 → target format via ffmpeg (bundled z imageio-ffmpeg)."""
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg = get_ffmpeg_exe()
        except ImportError:
            ffmpeg = shutil.which("ffmpeg")
            if not ffmpeg:
                raise TTSError(
                    "Brak ffmpeg. Zainstaluj: uv add imageio-ffmpeg "
                    "lub dodaj ffmpeg do PATH."
                ) from None

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_in:
            tmp_in.write(mp3_data)
            tmp_in_path = Path(tmp_in.name)

        tmp_out_path = tmp_in_path.with_suffix(f".{target_fmt}")
        try:
            result = subprocess.run(
                [
                    ffmpeg, "-y", "-i", str(tmp_in_path),
                    "-loglevel", "error",
                    str(tmp_out_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise TTSError(f"ffmpeg error: {result.stderr.strip()}")
            return tmp_out_path.read_bytes()
        finally:
            tmp_in_path.unlink(missing_ok=True)
            tmp_out_path.unlink(missing_ok=True)

    def _auto_path(self, fmt: str = "mp3") -> Path:
        ts = time.strftime("%Y%m%d_%H%M%S")
        name = Path(f"tts_{ts}.{fmt}")
        if self._output_dir:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            return self._output_dir / name
        return name

    def _ensure_sync_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create a persistent event loop for sync operations."""
        if self._sync_loop is None or self._sync_loop.is_closed():
            self._sync_loop = asyncio.new_event_loop()
            self._sync_thread = threading.Thread(
                target=self._sync_loop.run_forever, daemon=True,
            )
            self._sync_thread.start()
        return self._sync_loop

    def _run_sync(self, coro: object) -> object:
        """Run async coroutine from sync context using persistent event loop."""
        loop = self._ensure_sync_loop()
        future = asyncio.run_coroutine_threadsafe(coro, loop)  # type: ignore[arg-type]
        try:
            return future.result(timeout=3600.0)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise TTSAPIError("Request timed out after 3600s — event loop blocked")
