"""
Wrapper module for Fish Audio S2 Pro TTS API.

Sends text to a locally-running Fish Audio server and receives WAV audio.
No GPU needed in this process — inference runs on the separate server.

Usage:
    from modules.tts_fish_api import FishTTSClient

    client = FishTTSClient()
    audio_bytes = client.synthesize("Cześć, jak się masz?")
"""

import io
import json
import wave
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np

from constants import console

# Fish Audio S2 Pro API defaults
FISH_API_BASE_URL: str = "http://127.0.0.1:8855"
FISH_SAMPLE_RATE: int = 44_100
FISH_REQUEST_TIMEOUT: int = 300  # 5 min — matches server-side timeout


class FishTTSClient:
    """HTTP client for Fish Audio S2 Pro TTS API."""

    def __init__(
        self,
        base_url: str = FISH_API_BASE_URL,
        voice: Optional[str] = None,
        temperature: float = 0.8,
    ) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.voice: Optional[str] = voice
        self.temperature: float = temperature
        self._check_server()

    def _check_server(self) -> None:
        """Verify the Fish Audio server is reachable."""
        try:
            req = Request(f"{self.base_url}/health")
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("status") != "ok":
                    console.print(
                        f"Fish Audio API health check: {data}",
                        style="red_bold",
                    )
        except (URLError, OSError) as exc:
            raise ConnectionError(
                f"Nie można połączyć z Fish Audio API ({self.base_url}). "
                f"Upewnij się, że serwer działa.\n{exc}"
            ) from exc

    def get_voices(self) -> List[Dict[str, str]]:
        """Fetch available voice profiles from the server.

        Returns:
            List of dicts with 'name', 'audio_format', 'transcript'.
        """
        req = Request(f"{self.base_url}/voices")
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("voices", [])

    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize text to int16 audio array.

        Args:
            text: Polish text to synthesize.

        Returns:
            1-D numpy int16 array of audio samples.

        Raises:
            RuntimeError: If the API returns an error.
        """
        text = text.strip()
        if not text:
            return np.array([], dtype=np.int16)

        payload: Dict = {
            "text": text,
            "format": "wav",
            "temperature": self.temperature,
        }
        if self.voice:
            payload["voice"] = self.voice

        body = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{self.base_url}/tts",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=FISH_REQUEST_TIMEOUT) as resp:
                wav_bytes = resp.read()
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Fish Audio API error {exc.code}: {error_body}"
            ) from exc

        return self._wav_bytes_to_int16(wav_bytes)

    @staticmethod
    def _wav_bytes_to_int16(wav_bytes: bytes) -> np.ndarray:
        """Convert WAV bytes to int16 numpy array."""
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            sample_width = wf.getsampwidth()

        if sample_width == 2:
            return np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 4:
            # 32-bit → 16-bit
            arr = np.frombuffer(frames, dtype=np.int32)
            return (arr >> 16).astype(np.int16)
        else:
            return np.frombuffer(frames, dtype=np.int16)

    @staticmethod
    def get_sample_rate_from_wav(wav_bytes: bytes) -> int:
        """Extract sample rate from WAV bytes."""
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            return wf.getframerate()

    @staticmethod
    def get_voices_static(base_url: str = FISH_API_BASE_URL) -> List[Dict[str, str]]:
        """Fetch voices without creating a full client instance."""
        req = Request(f"{base_url.rstrip('/')}/voices")
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("voices", [])
