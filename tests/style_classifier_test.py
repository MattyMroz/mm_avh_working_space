"""Regression tests for the style classifier (modules/style_classifier.py).

Check agreement with ground truth collected in ``temp/ground_truth/`` (182 ASS
files classified by agents reading the content). Threshold: >=98% agreement
plus no regression on key cases (Fuji TS -> ZNAK after dedup, Default -> DIALOG,
English OP -> ZNAK, animation deduplication).

Standalone script in the project style (no pytest). Run:
    uv run tests/style_classifier_test.py
Exit 0 = OK, exit 1 = regression.

Requires data in ``temp/`` (dataset_ass/ + ground_truth/). Missing data -> SKIP.
"""

from __future__ import annotations

import glob
import json
import os
import sys
from typing import Final

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pysubs2 import SSAEvent, SSAFile

from modules.style_classifier import Category, classify_styles, dedup_animation

ROOT: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASS_DIR: Final[str] = os.path.join(ROOT, "temp", "dataset_ass")
GT_DIR: Final[str] = os.path.join(ROOT, "temp", "ground_truth")

MIN_AGREEMENT: Final[float] = 0.98
"""Required agreement ratio with ground truth."""


def _make_event(start: int, end: int, style: str, text: str) -> SSAEvent:
    """Build a Dialogue SSAEvent."""
    return SSAEvent(start=start, end=end, style=style, text=text, type="Dialogue")


def _load_ground_truth() -> dict[str, dict[str, str]]:
    """Load ground truth as {ass_file: {style: category}}; songs map to ZNAK."""
    gt: dict[str, dict[str, str]] = {}
    for fp in glob.glob(os.path.join(GT_DIR, "pack_*.json")):
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        for fn, styles in data.items():
            gt[fn] = {
                st: ("DIALOG" if info["cat"] == "DIALOG" else "SIGN")
                for st, info in styles.items()
            }
    return gt


def test_dedup_collapses_animation() -> bool:
    """Dense-in-time repeated text collapses to one; spaced dialogue is kept."""
    subs = SSAFile()
    # 50 frames of "TYTUŁ" every 40ms is animation -> collapses to 1.
    for i in range(50):
        subs.events.append(_make_event(start=i * 40, end=i * 40 + 40, style="TS", text="TYTUŁ"))
    # "Cześć" three times at distant moments stays as 3 lines.
    for t in (10_000, 30_000, 60_000):
        subs.events.append(_make_event(start=t, end=t + 1000, style="Default", text="Cześć"))

    deduped, removed = dedup_animation(list(subs.events))
    ts_kept = sum(1 for e in deduped if e.style == "TS")
    dlg_kept = sum(1 for e in deduped if e.style == "Default")

    ok = ts_kept == 1 and dlg_kept == 3 and removed == 49
    print(
        f"  [dedup] TS kept={ts_kept} (want 1), Default kept={dlg_kept} (want 3), "
        f"removed={removed} -> {'OK' if ok else 'FAIL'}"
    )
    return ok


def test_regression_vs_ground_truth() -> bool:
    """Classifier agreement with ground truth is >= MIN_AGREEMENT (excluding uncertain)."""
    gt = _load_ground_truth()
    if not gt or not os.path.isdir(ASS_DIR):
        print("  [regression] SKIP -- missing temp/dataset_ass or temp/ground_truth")
        return True

    ok = total = uncertain = 0
    silent_narrator = []  # GT=DIALOG but heuristic=ZNAK (the worst outcome).
    for ass in sorted(glob.glob(os.path.join(ASS_DIR, "*.ass"))):
        base = os.path.basename(ass)
        if base not in gt:
            continue
        try:
            subs = SSAFile.load(ass, encoding="utf-8")
        except Exception:
            continue
        for v in classify_styles(subs):
            truth = gt[base].get(v.style)
            if truth is None:
                continue
            if v.category is Category.UNCERTAIN:
                uncertain += 1
                continue
            total += 1
            heuristic = v.category.value
            if heuristic == truth:
                ok += 1
            elif truth == "DIALOG":
                silent_narrator.append((base, v.style, v.line_count))

    agreement = ok / total if total else 0.0
    print(
        f"  [regression] agreed {ok}/{total} = {agreement * 100:.1f}% "
        f"(threshold {MIN_AGREEMENT * 100:.0f}%), uncertain={uncertain}, "
        f"silent_narrator={len(silent_narrator)}"
    )
    passed = agreement >= MIN_AGREEMENT
    if not passed:
        for base, style, count in silent_narrator[:10]:
            print(f"      SILENT NARRATOR: {base[:40]} / {style} ({count} lines)")
    return passed


def main() -> int:
    """Run all checks; return 0 on success, 1 on regression."""
    print("== Style classifier test ==")
    results = [
        test_dedup_collapses_animation(),
        test_regression_vs_ground_truth(),
    ]
    if all(results):
        print("ALL OK")
        return 0
    print("REGRESSION -- test failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
