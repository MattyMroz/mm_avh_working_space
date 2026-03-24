"""Wrapper module for ReadLover (SlopTTS) cloud TTS API.

Sends text to the ReadLover API at ``https://api.readlover.app`` and
receives WAV audio (PCM 16-bit, 44 100 Hz, mono).

Authentication uses a Bearer token passed via the ``Authorization``
header.  Billing telemetry is exposed through response headers
(``X-Remaining-Characters``, ``X-Characters-Used``,
``X-SlopTTS-Audio-Seconds``, ``X-Billing-Mode``).

Usage::

    from modules.tts_readlover import ReadLoverClient

    client = ReadLoverClient(api_key="rl_live_...", speaker_id=6)
    audio_int16 = client.synthesize("Cześć, jak się masz?")
"""

import io
import wave
from typing import Any, Dict, List

import numpy as np
import requests

from constants import console

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

READLOVER_BASE_URL: str = "https://api.readlover.app"
"""Default API base URL for ReadLover (SlopTTS)."""

READLOVER_SAMPLE_RATE: int = 44_100
"""Audio sample rate returned by the API (Hz)."""

READLOVER_REQUEST_TIMEOUT: int = 120
"""HTTP timeout for synthesis requests (seconds)."""

READLOVER_MAX_TEXT_LENGTH: int = 5_000
"""Maximum characters per synthesis request."""

# ---------------------------------------------------------------------------
# Defaults for Polish language
# ---------------------------------------------------------------------------

_DEFAULT_SPEAKER_ID: int = 6  # Polish Voice 1
_DEFAULT_LANGUAGE_ID: int = 4  # Polish
_DEFAULT_ESPEAK_LANGUAGE: str = "pl"
_DEFAULT_PRESET: str = "neutral"
_DEFAULT_LENGTH_SCALE: float = 1.0


class ReadLoverClient:
    """HTTP client for the ReadLover (SlopTTS) cloud TTS API.

    Attributes:
        base_url: API root URL (no trailing slash).
        api_key: Bearer token for authentication.
        speaker_id: Voice ID from ``GET /v1/voices``.
        language_id: Language ID from ``GET /v1/languages``.
        espeak_language: eSpeak language code (e.g. ``"pl"``).
        preset: Synthesis preset — ``"neutral"`` or ``"expressive"``.
        length_scale: Playback pacing (0.1–4.0). Lower → faster.
    """

    def __init__(
        self,
        api_key: str,
        speaker_id: int = _DEFAULT_SPEAKER_ID,
        language_id: int = _DEFAULT_LANGUAGE_ID,
        espeak_language: str = _DEFAULT_ESPEAK_LANGUAGE,
        preset: str = _DEFAULT_PRESET,
        length_scale: float = _DEFAULT_LENGTH_SCALE,
        base_url: str = READLOVER_BASE_URL,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.api_key: str = api_key
        self.speaker_id: int = speaker_id
        self.language_id: int = language_id
        self.espeak_language: str = espeak_language
        self.preset: str = preset
        self.length_scale: float = length_scale

        self._session: requests.Session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
        })

        self._check_server()

    # ------------------------------------------------------------------
    # Health & connectivity
    # ------------------------------------------------------------------

    def _check_server(self) -> None:
        """Verify the ReadLover API is reachable and ready.

        Raises:
            ConnectionError: When the server is unreachable or not ready.
        """
        try:
            resp = self._session.get(
                f"{self.base_url}/healthz",
                timeout=10,
            )
            data = resp.json()
            if not data.get("ready"):
                console.print(
                    f"ReadLover API health check: not ready — {data}",
                    style="red_bold",
                )
        except requests.RequestException as exc:
            raise ConnectionError(
                f"Nie można połączyć z ReadLover API ({self.base_url}). {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Synthesis
    # ------------------------------------------------------------------

    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize *text* into a 1-D int16 audio array.

        The method sends a ``POST /v1/synthesize`` request and parses
        the returned WAV binary.

        Args:
            text: Text to synthesize (max 5 000 chars).

        Returns:
            1-D ``numpy.int16`` array of PCM samples at
            ``READLOVER_SAMPLE_RATE`` Hz.

        Raises:
            requests.HTTPError: On any non-2xx API response.
            RuntimeError: When WAV decoding fails.
        """
        text = text.strip()
        if not text:
            return np.array([], dtype=np.int16)

        payload: Dict[str, Any] = {
            "text": text,
            "speaker_id": self.speaker_id,
            "language_id": self.language_id,
            "espeak_language": self.espeak_language,
            "preset": self.preset,
            "length_scale": self.length_scale,
        }

        resp = self._session.post(
            f"{self.base_url}/v1/synthesize",
            json=payload,
            timeout=READLOVER_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()

        self._log_billing_headers(resp)

        return self._wav_bytes_to_int16(resp.content)

    # ------------------------------------------------------------------
    # Static helpers (no client instance needed)
    # ------------------------------------------------------------------

    @staticmethod
    def get_voices_static(
        api_key: str,
        base_url: str = READLOVER_BASE_URL,
    ) -> List[Dict[str, Any]]:
        """Fetch available voices from the API.

        Args:
            api_key: Bearer token.
            base_url: API root URL.

        Returns:
            List of voice dicts with keys ``id``, ``name``,
            ``language_id``, ``language_name``, ``espeak_language``.
        """
        resp = requests.get(
            f"{base_url.rstrip('/')}/v1/voices",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def get_presets_static(
        api_key: str,
        base_url: str = READLOVER_BASE_URL,
    ) -> Dict[str, Dict[str, float]]:
        """Fetch available synthesis presets.

        Args:
            api_key: Bearer token.
            base_url: API root URL.

        Returns:
            Dict mapping preset name to its parameter values,
            e.g. ``{"neutral": {"cfg_strength": 3.0, ...}}``.
        """
        resp = requests.get(
            f"{base_url.rstrip('/')}/v1/presets",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _wav_bytes_to_int16(wav_bytes: bytes) -> np.ndarray:
        """Parse raw WAV bytes into a 1-D int16 numpy array.

        Handles both 16-bit and 32-bit PCM input.

        Args:
            wav_bytes: Complete WAV file as bytes.

        Returns:
            1-D ``numpy.int16`` array.

        Raises:
            RuntimeError: When the WAV cannot be decoded.
        """
        try:
            buf = io.BytesIO(wav_bytes)
            with wave.open(buf, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                sample_width = wf.getsampwidth()
        except wave.Error as exc:
            raise RuntimeError(
                f"Nie udało się zdekodować WAV z ReadLover API: {exc}"
            ) from exc

        if sample_width == 2:
            return np.frombuffer(frames, dtype=np.int16)
        if sample_width == 4:
            arr = np.frombuffer(frames, dtype=np.int32)
            return (arr >> 16).astype(np.int16)
        # Fallback — try int16 anyway
        return np.frombuffer(frames, dtype=np.int16)

    @staticmethod
    def _log_billing_headers(resp: requests.Response) -> None:
        """Log ReadLover billing telemetry from response headers."""
        remaining = resp.headers.get("X-Remaining-Characters")
        used = resp.headers.get("X-Characters-Used")
        if remaining is not None or used is not None:
            console.print(
                f"ReadLover billing: used={used}, remaining={remaining}",
                style="blue",
            )
