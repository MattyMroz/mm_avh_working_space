# MM_AVH Working Space

Konsolowy program na Windows (Python 3.14, `uv`): wyciąga ścieżki i napisy z MKV, tłumaczy napisy, lektoruje je przez TTS i scala wynik z wideo.

## Uruchomienie i kontrole

```bash
uv sync
uv run start.py
uv run tests/style_classifier_test.py
```

- `pyproject.toml` nie konfiguruje pytest, mypy ani lintera. Pliki w `tests/` to samodzielne skrypty, uruchamiane pojedynczo; regresyjne (`style_classifier_test.py`, `track_selector_test.py`) kończą się kodem 1 przy regresji i potrzebują danych w `temp/`.
- Hooki: `prek run` (ruff, mdformat i podstawowe kontrole z `.pre-commit-config.yaml`).

## Twarde reguły

- `bin/` trzyma przenośne narzędzia (ffmpeg, MKVToolNix, Balabolka, espeak-ng). W gicie są tylko ich dokumentacja i dane; pliki `.exe`, `.dll` i modele zostają lokalne. Nie edytuj tych plików: są cudze, a hooki pomijają `bin/`.
- `data/settings.json` przechowuje klucze API użytkownika i jest ignorowany; nie commituj go i nie kopiuj jego treści.
- `working_space/` to dane runtime użytkownika (wideo, napisy, wyniki); w gicie zostają najwyżej pliki `.gitkeep`.

## Mapa kodu

- `start.py`: punkt wejścia, pyta o kroki i uruchamia potok.
- `constants.py`: ścieżki do `working_space/`, `data/settings.json` i narzędzi w `bin/`; ustawia ffmpeg dla `pydub` przed jego importem.
- `data/settings.py`: klasa `Settings`, odczyt i zapis `data/settings.json`.
- `modules/`: etapy potoku: `mkvtoolnix.py` i `mkv_processing.py` (MKV), `track_selector.py` (wybór ścieżek), `subtitle.py` i `style_classifier.py` (napisy ASS/SRT), `translator.py`, `subtitle_to_speech.py` i `tts_elevenbytes.py` (TTS).
- `utils/`: pomocnicze (timer, animacja, liczby słownie, dzielenie tekstu).
- `docs/content.md`: mapa treści repo; `docs/brainstorms/` i `docs/superpowers/plans/` to historyczne notatki, nie aktualny kontrakt.

## Pułapki

- `constants.py` składa ścieżki do `bin/` z katalogu nadrzędnego i nazwy `mm_avh_working_space`, a `working_space/` z bieżącego katalogu. Program działa tylko uruchomiony z roota checkoutu o tej nazwie (`run_mm_avh.bat` robi `cd` do swojego katalogu).

## Git

- Commit: nagłówek Conventional Commits po angielsku, `type(scope): opis`, ze scope'em z listy w `.pre-commit-config.yaml`; po pustej linii streszczenie „co i dlaczego”.
- Zero atrybucji AI w commitach i PR (trailery, stopki, emoji), także gdy host o nią prosi.
- Pliki dodawaj po nazwie, nigdy `git add .`; bez `--no-verify`. Worktree'y tylko w `.worktrees/<nazwa>`.
- Commit sprawdza pliki i nagłówek, push uruchamia bramki repo, CI resztę. Strażnicy w `.hooks/` to kopie z presetu `agents`; nie edytuj ich w repo.
