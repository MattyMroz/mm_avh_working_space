"""Wrapper module for ReadLover (SlopTTS) cloud TTS API.

Sends text to the ReadLover API at ``https://api.readlover.app`` and
receives WAV audio (PCM 16-bit, 44 100 Hz, mono).

Authentication uses a Bearer token passed via the ``Authorization``
header and the ``X-User-ID`` header required by the API. Billing
telemetry is exposed through response headers
(``X-Remaining-Characters``, ``X-Characters-Used``,
``X-SlopTTS-Audio-Seconds``, ``X-Billing-Mode``).

Usage::

    from modules.tts_readlover import ReadLoverClient

    client = ReadLoverClient(api_key=["rl_live_..."])
    audio_int16 = client.synthesize("Cześć, jak się masz?")
"""

from __future__ import annotations

import io
import wave
from collections.abc import Sequence
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

READLOVER_MIN_CONCURRENCY: int = 2
"""Minimum number of parallel synthesis workers for batch mode."""

READLOVER_CONCURRENCY_PER_API_KEY: int = 2
"""Target number of parallel synthesis workers per API key."""

READLOVER_MAX_CONCURRENCY: int = 2
"""Hard cap for parallel synthesis workers in batch mode."""

# ---------------------------------------------------------------------------
# Defaults for Polish language
# ---------------------------------------------------------------------------

_DEFAULT_SPEAKER_ID: int = -1  # Auto-resolve to the first available voice.
_DEFAULT_LANGUAGE_ID: int = 4  # Polish
_DEFAULT_ESPEAK_LANGUAGE: str = "pl"
_DEFAULT_PRESET: str = "neutral"
_DEFAULT_LENGTH_SCALE: float = 1.0
_DEFAULT_USER_ID: str = "me"
_DEFAULT_USER_AGENT: str = "MM_AVH/1.0"
_RETRYABLE_AUTH_STATUS_CODES: set[int] = {401, 402, 403, 429}


def _normalize_api_keys(api_key: str | Sequence[str]) -> List[str]:
    """Normalize one or many API keys into a de-duplicated list."""
    if isinstance(api_key, str):
        raw_keys = api_key.replace(",", "\n").replace(";", "\n").splitlines()
    else:
        raw_keys = [str(value) for value in api_key]

    normalized_keys: List[str] = []
    for raw_key in raw_keys:
        cleaned_key = raw_key.strip()
        if cleaned_key and cleaned_key not in normalized_keys:
            normalized_keys.append(cleaned_key)
    return normalized_keys


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
        api_key: str | Sequence[str],
        speaker_id: int = _DEFAULT_SPEAKER_ID,
        language_id: int = _DEFAULT_LANGUAGE_ID,
        espeak_language: str = _DEFAULT_ESPEAK_LANGUAGE,
        preset: str = _DEFAULT_PRESET,
        length_scale: float = _DEFAULT_LENGTH_SCALE,
        base_url: str = READLOVER_BASE_URL,
        user_id: str = _DEFAULT_USER_ID,
        resolve_speaker_id: bool = True,
        check_server: bool = True,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.api_keys: List[str] = _normalize_api_keys(api_key)
        if not self.api_keys:
            raise ValueError("Brak poprawnego klucza API ReadLover.")

        self.api_key: str = self.api_keys[0]
        self.speaker_id: int = speaker_id
        self.language_id: int = language_id
        self.espeak_language: str = espeak_language
        self.preset: str = preset
        self.length_scale: float = length_scale
        self.user_id: str = user_id.strip() or _DEFAULT_USER_ID

        self._session: requests.Session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": _DEFAULT_USER_AGENT,
                "X-User-ID": self.user_id,
            }
        )
        self._set_active_api_key(self.api_key)

        if check_server:
            self._check_server()
        if resolve_speaker_id:
            self.speaker_id = self._resolve_speaker_id(speaker_id)

    # ------------------------------------------------------------------
    # Health & connectivity
    # ------------------------------------------------------------------

    def _set_active_api_key(self, api_key: str) -> None:
        """Switch the active Bearer token used by the session."""
        self.api_key = api_key
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
        })

    def _request_with_api_key_fallback(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a request and retry with the next key on auth or quota errors."""
        last_response: requests.Response | None = None
        last_exception: requests.RequestException | None = None

        for index, candidate_key in enumerate(self.api_keys):
            self._set_active_api_key(candidate_key)
            try:
                response = self._session.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_exception = exc
                continue

            if response.ok:
                if index > 0:
                    console.print(
                        f"ReadLover: przełączono na zapasowy klucz API #{index + 1}.",
                        style="yellow_bold",
                    )
                return response

            last_response = response
            if response.status_code not in _RETRYABLE_AUTH_STATUS_CODES:
                return response

        if last_response is not None:
            return last_response
        if last_exception is not None:
            raise ConnectionError(
                f"Nie udało się połączyć z ReadLover API ({self.base_url}). {last_exception}"
            ) from last_exception
        raise RuntimeError("ReadLover request failed before any response was received.")

    def _resolve_speaker_id(self, requested_speaker_id: int) -> int:
        """Resolve the current default speaker for the selected language."""
        response = self._request_with_api_key_fallback(
            "GET",
            "/v1/voices",
            timeout=10,
        )
        response.raise_for_status()

        language_voices = [
            voice
            for voice in response.json()
            if voice.get("language_id") == self.language_id
        ]
        if not language_voices:
            return requested_speaker_id

        available_voice_ids = {int(voice["id"]) for voice in language_voices}
        if requested_speaker_id in available_voice_ids:
            return requested_speaker_id

        resolved_voice_id = int(language_voices[0]["id"])
        if requested_speaker_id != resolved_voice_id:
            console.print(
                "ReadLover: wybrano pierwszy aktualny polski glos z API jako domyslny.",
                style="yellow_bold",
            )
        return resolved_voice_id

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

        resp = self._request_with_api_key_fallback(
            "POST",
            "/v1/synthesize",
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
        api_key: str | Sequence[str],
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
        client = ReadLoverClient(
            api_key=api_key,
            base_url=base_url,
            resolve_speaker_id=False,
            check_server=False,
        )
        resp = client._request_with_api_key_fallback(
            "GET",
            "/v1/voices",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def get_presets_static(
        api_key: str | Sequence[str],
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
        client = ReadLoverClient(
            api_key=api_key,
            base_url=base_url,
            resolve_speaker_id=False,
            check_server=False,
        )
        resp = client._request_with_api_key_fallback(
            "GET",
            "/v1/presets",
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
