"""Regression test for SubtitleRefactor.srt_to_ass (modules/subtitle.py).

Reproduce the merge bug (Pillar 4 of auto mode): translated side-captions are
mapped from SRT back into the original ASS. The old code mapped by a running
counter, which drifted whenever decorated events or drawing lines consumed the
counter without inserting text. The fix maps by (start, end) timing, which is
invariant across ass->srt->translation.

Synthetic scenario, no real files needed:
    * "Tokyo"                  (1000-2000)  plain caption
    * "{\\pos(960,200)}Lab"     (3000-4000)  caption with a positioning tag
    * "m 0 0 l 186 0 l 186 76" (3000-4000)  vector drawing, SAME timing (clash!)
    * "Station"                (5000-6000)  plain caption
The SRT holds three translations keyed by time. We assert the tag is preserved,
the drawing is left untouched, and nothing drifts despite the timing clash.

Standalone script in the project style (no pytest). Run:
    .venv\\Scripts\\python.exe tests\\srt_to_ass_test.py
Exit 0 = OK, exit 1 = regression.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from typing import Final

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pysubs2 import SSAEvent, SSAFile

from modules.subtitle import SubtitleRefactor

STYLE: Final[str] = "Sign"
FILENAME: Final[str] = "episode.srt"


def _build_ass(path: str) -> None:
    """Write a 4-event ASS file: plain, tagged, drawing (timing clash), plain."""
    subs = SSAFile()
    subs.styles[STYLE] = subs.styles["Default"]
    subs.events = [
        SSAEvent(start=1000, end=2000, style=STYLE,
                 text="Tokyo", type="Dialogue"),
        SSAEvent(start=3000, end=4000, style=STYLE,
                 text="{\\pos(960,200)}Lab", type="Dialogue"),
        SSAEvent(start=3000, end=4000, style=STYLE,
                 text="m 0 0 l 186 0 l 186 76", type="Dialogue"),
        SSAEvent(start=5000, end=6000, style=STYLE,
                 text="Station", type="Dialogue"),
    ]
    with open(path, "w", encoding="utf-8") as file:
        file.write(subs.to_string(format_="ass"))


def _build_srt(path: str) -> None:
    """Write the SRT with three translations keyed only by timing."""
    subs = SSAFile()
    subs.events = [
        SSAEvent(start=1000, end=2000, text="Tokio"),
        SSAEvent(start=3000, end=4000, text="Laboratorium"),
        SSAEvent(start=5000, end=6000, text="Stacja"),
    ]
    with open(path, "w", encoding="utf-8") as file:
        file.write(subs.to_string(format_="srt"))


def _event_text(events: list[SSAEvent], start: int, end: int, contains: str) -> str:
    """Return the text of the event at (start, end) whose text contains a marker."""
    for event in events:
        if event.start == start and event.end == end and contains in event.text:
            return event.text
    return ""


def test_merge_by_timing() -> bool:
    """Translations land on the right events despite a tag and a timing clash."""
    test_dir = tempfile.mkdtemp(prefix="srt_to_ass_")
    try:
        # Input (alt-subs) and output live in separate folders, as in the real
        # pipeline: srt_to_ass deletes the source .ass when done, so a shared
        # folder would wipe the freshly written result.
        alt_dir = os.path.join(test_dir, "alt_subs")
        out_dir = os.path.join(test_dir, "output")
        os.makedirs(alt_dir)
        os.makedirs(out_dir)

        srt_path = os.path.join(alt_dir, FILENAME)
        ass_path = os.path.join(alt_dir, FILENAME.replace(".srt", ".ass"))
        out_path = os.path.join(out_dir, FILENAME.replace(".srt", ".ass"))

        _build_ass(ass_path)
        _build_srt(srt_path)

        # srt_to_ass reads from working_space_temp_alt_subs and writes to
        # working_space_output. The alt-subs path is a slotless class attribute
        # (read-only per instance), so patch it on the class and restore after.
        original_alt = SubtitleRefactor.working_space_temp_alt_subs
        SubtitleRefactor.working_space_temp_alt_subs = alt_dir
        try:
            refactor = SubtitleRefactor(FILENAME)
            refactor.working_space_output = out_dir
            refactor.srt_to_ass()
        finally:
            SubtitleRefactor.working_space_temp_alt_subs = original_alt

        result = SSAFile.load(out_path, encoding="utf-8")
        events = result.events

        tokyo = _event_text(events, 1000, 2000, "Tok")
        lab = _event_text(events, 3000, 4000, "Lab")
        drawing = _event_text(events, 3000, 4000, "m 0 0")
        station = _event_text(events, 5000, 6000, "Sta")

        checks = [
            ("Tokyo -> Tokio", tokyo == "Tokio"),
            ("tag preserved + translated",
             lab == "{\\pos(960,200)}Laboratorium"),
            ("drawing untouched", drawing == "m 0 0 l 186 0 l 186 76"),
            ("Station -> Stacja", station == "Stacja"),
        ]

        ok = True
        for label, passed in checks:
            print(f"  [merge] {label}: {'OK' if passed else 'FAIL'}")
            ok = ok and passed
        if not ok:
            print(f"      got Tokyo   = {tokyo!r} (want 'Tokio')")
            print(f"      got Lab     = {lab!r} "
                  f"(want '{{\\pos(960,200)}}Laboratorium')")
            print(f"      got drawing = {drawing!r} "
                  f"(want 'm 0 0 l 186 0 l 186 76')")
            print(f"      got Station = {station!r} (want 'Stacja')")
        return ok
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main() -> int:
    """Run all checks; return 0 on success, 1 on regression."""
    print("== srt_to_ass test ==")
    results = [
        test_merge_by_timing(),
    ]
    if all(results):
        print("ALL OK")
        return 0
    print("REGRESSION -- test failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
