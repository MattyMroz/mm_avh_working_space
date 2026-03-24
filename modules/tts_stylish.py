"""
Wrapper module for STylish-TTS-Pl — Polish neural TTS model.

Loads model from local checkpoints in bin/stylish_tts/ and uses
portable espeak-ng from bin/espeak-ng/ for phonemization.

Usage:
    from modules.tts_stylish import StylishTTS

    tts = StylishTTS()
    audio_int16 = tts.synthesize("Cześć, jak się masz?")
"""

import os
import sys
import wave
from os import path
from typing import List, Optional

import numpy as np
import torch

from constants import (
    ESPEAK_NG_FOLDER,
    STYLISH_TTS_FOLDER,
    STYLISH_TTS_CONFIG_PATH,
    STYLISH_TTS_CHECKPOINT_DIR,
    console,
)

# Sample rate of the STylish-TTS-Pl model
STYLISH_SAMPLE_RATE: int = 24_000


def _setup_paths() -> None:
    """Add STylish-TTS-Pl source directories to sys.path for model imports."""
    paths_to_add = [
        STYLISH_TTS_FOLDER,
        path.join(STYLISH_TTS_FOLDER, 'models'),
        path.join(STYLISH_TTS_FOLDER, 'stylish_lib'),
    ]
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)


def _setup_espeak() -> None:
    """Set env vars so phonemizer finds the portable espeak-ng."""
    os.environ['ESPEAK_DATA_PATH'] = ESPEAK_NG_FOLDER
    # phonemizer needs espeak-ng.exe on PATH
    if ESPEAK_NG_FOLDER not in os.environ.get('PATH', ''):
        os.environ['PATH'] = ESPEAK_NG_FOLDER + ';' + os.environ.get('PATH', '')
    # Some phonemizer versions check this env var for the shared library
    lib_path = path.join(ESPEAK_NG_FOLDER, 'libespeak-ng.dll')
    if path.isfile(lib_path):
        os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = lib_path


class StylishTTS:
    """Wrapper around STylish-TTS-Pl for single-call synthesis."""

    def __init__(self, device: Optional[str] = None) -> None:
        _setup_espeak()
        _setup_paths()

        self.device: str = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_model()

    def _load_model(self) -> None:
        """Build model, load checkpoint shards, init phonemizer."""
        from config_loader import load_model_config_yaml
        from models.models import build_model
        from models.export_model import ExportModel
        from text_utils import TextCleaner

        console.print("Ładowanie STylish-TTS-Pl...", style='blue_bold')

        model_config = load_model_config_yaml(STYLISH_TTS_CONFIG_PATH)
        self._text_cleaner = TextCleaner(model_config.symbol)

        model_dict = build_model(model_config)

        for idx, key in enumerate(model_dict.keys()):
            ckpt_name = 'pytorch_model.bin' if idx == 0 else f'pytorch_model_{idx}.bin'
            ckpt_path = path.join(STYLISH_TTS_CHECKPOINT_DIR, ckpt_name)
            state_dict = torch.load(ckpt_path, map_location=self.device, weights_only=True)
            model_dict[key].load_state_dict(state_dict)
            model_dict[key].to(self.device).eval()

        self._model = ExportModel(**model_dict, device=self.device).eval()

        import phonemizer
        self._phonemizer = phonemizer.backend.EspeakBackend(
            language='pl', preserve_punctuation=True, with_stress=True,
        )

        console.print("STylish-TTS-Pl załadowany.", style='green_bold')

    def synthesize(self, text: str, speed: float = 1.0) -> np.ndarray:
        """Synthesize Polish text to int16 audio at 24 kHz.

        Args:
            text: Polish text to synthesize.
            speed: Playback speed multiplier (0.5–2.0).

        Returns:
            1-D numpy int16 array of audio samples at 24 kHz.
        """
        text = text.strip().replace('"', '')
        if not text:
            return np.array([], dtype=np.int16)

        phonemes_list = self._phonemizer.phonemize([text])
        if not phonemes_list or not phonemes_list[0]:
            return np.array([], dtype=np.int16)

        phoneme_ids = self._text_cleaner(phonemes_list[0])
        if not phoneme_ids:
            return np.array([], dtype=np.int16)

        tokens = torch.tensor(phoneme_ids).unsqueeze(0).to(self.device)
        texts = torch.zeros([1, tokens.shape[1] + 2], dtype=torch.long, device=self.device)
        texts[0, 1:tokens.shape[1] + 1] = tokens
        text_lengths = torch.tensor([tokens.shape[1] + 2], device=self.device)

        with torch.no_grad():
            outputs = self._model(texts, text_lengths)

        if outputs.numel() == 0:
            return np.array([], dtype=np.int16)

        audio = torch.tanh(outputs).cpu().numpy().squeeze()

        if audio.ndim == 0:
            audio = np.array([audio.item()])
        elif audio.ndim > 1:
            audio = audio.flatten()

        if audio.size == 0:
            return np.array([], dtype=np.int16)

        audio_int16: np.ndarray = (audio * 32767).astype(np.int16)

        if speed != 1.0 and 0.5 <= speed <= 2.0:
            import librosa
            audio_float = audio_int16.astype(np.float32) / 32768.0
            audio_float = librosa.effects.time_stretch(audio_float, rate=speed)
            audio_int16 = (audio_float * 32767).astype(np.int16)

        return audio_int16

    def synthesize_long(self, text: str, speed: float = 1.0, max_chunk: int = 120) -> np.ndarray:
        """Synthesize longer text by splitting into sentence chunks.

        Args:
            text: Polish text (can be multiple sentences).
            speed: Playback speed multiplier.
            max_chunk: Max characters per chunk.

        Returns:
            1-D numpy int16 array of concatenated audio at 24 kHz.
        """
        chunks = self._split_text(text, max_chunk)
        if not chunks:
            return np.array([], dtype=np.int16)

        segments: List[np.ndarray] = []
        silence = np.zeros(int(STYLISH_SAMPLE_RATE * 0.05), dtype=np.int16)

        for i, chunk in enumerate(chunks):
            audio = self.synthesize(chunk, speed)
            if len(audio) > 0:
                segments.append(audio)
                if i < len(chunks) - 1:
                    segments.append(silence)

        if not segments:
            return np.array([], dtype=np.int16)

        return np.concatenate(segments)

    @staticmethod
    def _split_text(text: str, max_length: int = 120) -> List[str]:
        """Split text on sentence boundaries."""
        sentences: List[str] = []
        current = ''
        for char in text:
            current += char
            if char in '.?!;':
                if current.strip():
                    sentences.append(current.strip())
                current = ''
        if current.strip():
            sentences.append(current.strip())

        result: List[str] = []
        for sentence in sentences:
            if len(sentence) <= max_length:
                result.append(sentence)
            else:
                words = sentence.split()
                chunk = ''
                for word in words:
                    if len(chunk + ' ' + word) <= max_length:
                        chunk += ' ' + word if chunk else word
                    else:
                        if chunk:
                            result.append(chunk)
                        chunk = word
                if chunk:
                    result.append(chunk)

        return [s for s in result if s.strip()]

    def save_wav(self, audio: np.ndarray, output_path: str) -> None:
        """Save int16 audio array to a mono WAV file at 24 kHz."""
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(STYLISH_SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
