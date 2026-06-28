"""Regression tests for the track selector (modules/track_selector.py).

Two layers: synthetic MKVs that pin the documented rules (audio language order,
subtitle language order, signs-only rejection, line-count tie-break) and a
regression against ``temp/dataset.json`` -- 206 real MKVs whose ``pick_sub`` /
``pick_aud`` were fixed in an earlier validation. Threshold: >=95% agreement on
each of audio and subtitle picks.

Standalone script in the project style (no pytest). Run:
    .venv\\Scripts\\python.exe tests/track_selector_test.py
Exit 0 = OK, exit 1 = regression.

Missing ``temp/dataset.json`` -> the regression layer SKIPs (synthetic still runs).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Final

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.track_selector import select_audio_track, select_subtitle_track

ROOT: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET: Final[str] = os.path.join(ROOT, "temp", "dataset.json")

MIN_AGREEMENT: Final[float] = 0.95
"""Required agreement ratio with the validated picks, per track kind."""


def _sub(id_: int, lang: str, name: str = "", lines: int | None = None) -> dict:
    """Build a subtitle track dict in the dataset shape."""
    return {"id": id_, "type": "subtitles", "lang": lang, "name": name, "lines": lines}


def _aud(id_: int, lang: str, name: str = "", default: bool = False) -> dict:
    """Build an audio track dict in the dataset shape."""
    return {"id": id_, "type": "audio", "lang": lang, "name": name, "default": default}


def test_audio_prefers_japanese() -> bool:
    """Audio picks Japanese over English regardless of order."""
    tracks = [_aud(1, "eng"), _aud(2, "jpn")]
    got = select_audio_track(tracks)
    ok = got == 2
    print(f"  [audio jpn>eng] got id={got} (want 2) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_audio_default_breaks_lang_tie() -> bool:
    """A default track wins only within the same language step, never across it.

    Korean (rest=20) + default still loses to English (40): the language step is
    larger than the default bonus.
    """
    tracks = [_aud(1, "kor", default=True), _aud(2, "eng", default=False)]
    got = select_audio_track(tracks)
    ok = got == 2
    print(f"  [audio eng>kor+default] got id={got} (want 2) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_subtitle_prefers_polish() -> bool:
    """Subtitles pick Polish over English."""
    tracks = [_sub(2, "eng"), _sub(3, "pol")]
    got = select_subtitle_track(tracks)
    ok = got == 3
    print(f"  [sub pol>eng] got id={got} (want 3) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_subtitle_signs_only_rejected() -> bool:
    """A full English track beats a Polish signs-only track via the name penalty.

    The signs penalty must drop even top-priority Polish below any full track, so
    the narrator gets real dialogue (English) over Polish typesetting.
    """
    tracks = [_sub(2, "eng", name="English"), _sub(3, "pol", name="Polish Signs/Songs")]
    got = select_subtitle_track(tracks)
    ok = got == 2
    print(f"  [sub signs rejected] got id={got} (want 2) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_subtitle_signs_only_rejected_same_lang() -> bool:
    """Within one language a full track beats a forced signs-only sibling.

    The attested job of the penalty: English "Forced" signs (id 3) loses to the
    full English track (id 4), even though both share the top available language.
    """
    tracks = [_sub(3, "eng", name="English (Forced)", lines=19), _sub(4, "eng", lines=305)]
    got = select_subtitle_track(tracks)
    ok = got == 4
    print(f"  [sub signs same-lang] got id={got} (want 4) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_subtitle_lines_break_lang_tie() -> bool:
    """Within one language the track with more lines wins."""
    tracks = [_sub(2, "eng", lines=120), _sub(3, "eng", lines=540)]
    got = select_subtitle_track(tracks)
    ok = got == 3
    print(f"  [sub more-lines] got id={got} (want 3) -> {'OK' if ok else 'FAIL'}")
    return ok


def test_empty_returns_none() -> bool:
    """No audio / no subtitles yields None rather than an error."""
    ok = select_audio_track([_sub(1, "pol")]) is None
    ok = select_subtitle_track([_aud(1, "jpn")]) is None and ok
    print(f"  [empty -> None] -> {'OK' if ok else 'FAIL'}")
    return ok


def _to_tracks(entry: dict) -> list[dict]:
    """Tag dataset sub/aud lists with their type into one track list."""
    tracks: list[dict] = []
    for s in entry["subs"]:
        tracks.append({**s, "type": "subtitles"})
    for a in entry["auds"]:
        tracks.append({**a, "type": "audio"})
    return tracks


def test_regression_vs_validated_picks() -> bool:
    """Selector agreement with the validated picks is >= MIN_AGREEMENT for both kinds."""
    if not os.path.isfile(DATASET):
        print("  [regression] SKIP -- missing temp/dataset.json")
        return True

    with open(DATASET, encoding="utf-8") as f:
        mkv = json.load(f)["mkv"]

    sub_ok = sub_total = aud_ok = aud_total = 0
    sub_miss: list[tuple[str, int | None, int]] = []
    aud_miss: list[tuple[str, int | None, int]] = []
    for entry in mkv:
        tracks = _to_tracks(entry)
        name = os.path.basename(entry["path"])

        if entry.get("pick_sub") is not None:
            sub_total += 1
            got = select_subtitle_track(tracks)
            if got == entry["pick_sub"]:
                sub_ok += 1
            else:
                sub_miss.append((name, got, entry["pick_sub"]))

        if entry.get("pick_aud") is not None:
            aud_total += 1
            got = select_audio_track(tracks)
            if got == entry["pick_aud"]:
                aud_ok += 1
            else:
                aud_miss.append((name, got, entry["pick_aud"]))

    sub_rate = sub_ok / sub_total if sub_total else 1.0
    aud_rate = aud_ok / aud_total if aud_total else 1.0
    print(
        f"  [regression] subs {sub_ok}/{sub_total} = {sub_rate * 100:.1f}%, "
        f"auds {aud_ok}/{aud_total} = {aud_rate * 100:.1f}% "
        f"(threshold {MIN_AGREEMENT * 100:.0f}%)"
    )
    passed = sub_rate >= MIN_AGREEMENT and aud_rate >= MIN_AGREEMENT
    if not passed:
        for label, misses in (("SUB", sub_miss), ("AUD", aud_miss)):
            for fn, got, want in misses[:10]:
                print(f"      {label} MISS: {fn[:45]} got={got} want={want}")
    return passed


def main() -> int:
    """Run all checks; return 0 on success, 1 on regression."""
    print("== Track selector test ==")
    results = [
        test_audio_prefers_japanese(),
        test_audio_default_breaks_lang_tie(),
        test_subtitle_prefers_polish(),
        test_subtitle_signs_only_rejected(),
        test_subtitle_signs_only_rejected_same_lang(),
        test_subtitle_lines_break_lang_tie(),
        test_empty_returns_none(),
        test_regression_vs_validated_picks(),
    ]
    if all(results):
        print("ALL OK")
        return 0
    print("REGRESSION -- test failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
