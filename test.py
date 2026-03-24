from __future__ import annotations

from pathlib import Path

import requests
from requests import Response
from requests.exceptions import HTTPError


def main() -> None:
    """Call the ReadLover synthesize endpoint and save the response as WAV."""
    response: Response = requests.post(
        "https://api.readlover.app/v1/synthesize",
        headers={
            "Authorization": "Bearer rl_live_62ea460b836adbbf44a4d33648120f94b9ac2ca7e22e6f95",
            "Content-Type": "application/json",
        },
        json={
            "text": "To jest testowy tekst do syntezy. Sprawdzamy, czy wszystko działa poprawnie.",
            "speaker_id": 6,
            "language_id": 4,
            "espeak_language": "pl",
            "preset": "neutral",
            "n_steps": 64,
            "temperature": 0.8,
            "cfg_strength": 3.0,
            "dur_noise_scale": 0.667,
            "length_scale": 1.0,
        },
        timeout=120,
    )

    try:
        response.raise_for_status()
    except HTTPError:
        print(f"HTTP {response.status_code}")
        print(response.text)
        raise

    output_path = Path("sample.wav")
    output_path.write_bytes(response.content)
    print(f"Saved audio to {output_path.resolve()}")


if __name__ == "__main__":
    main()