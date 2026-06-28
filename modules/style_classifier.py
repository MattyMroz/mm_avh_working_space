"""Classify ASS subtitle styles as DIALOG vs SIGN for auto narration mode.

Split ASS styles into those meant for the narrator (DIALOG) and those skipped
(SIGN: on-screen signs, OP/ED songs, notes). Validated on 206 files with
agent-read ground truth: ~99% agreement, ~99% weighted by line count.

The key mechanism is ANIMATION DEDUPLICATION: typesetting is often rendered
frame by frame (the same text repeated hundreds of times within a fraction of a
second, e.g. an animated title repeated x766). Such text counts as a single
occurrence -- the narrator would read it once, not hundreds of times. Without
this, line-count metrics would confuse animation with dialogue.

Example:
    from pysubs2 import SSAFile

    from modules.style_classifier import Category, classify_styles

    subs = SSAFile.load("subtitles.ass")
    results = classify_styles(subs)
    dialog_styles = [r.style for r in results if r.category is Category.DIALOG]
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pysubs2 import SSAEvent, SSAFile

# ── ASS tag signatures in the raw line text ─────────────────────────────────
# Match a literal backslash via chr(92) so the pattern survives Python 3.14's
# stricter handling of invalid escape sequences in string literals.
_BACKSLASH: Final[str] = chr(92)
_RE_DRAW: Final[re.Pattern[str]] = re.compile(_BACKSLASH + _BACKSLASH + r"p[1-9]")
_RE_POS: Final[re.Pattern[str]] = re.compile(
    _BACKSLASH + _BACKSLASH + r"(pos|move|clip|frz|fad|org|t\()"
)
_RE_KARA: Final[re.Pattern[str]] = re.compile(_BACKSLASH + _BACKSLASH + r"[kK][fo]?[0-9]")
_RE_PUNCT: Final[re.Pattern[str]] = re.compile(r'[.!?…»"]')

# ── Style-name signatures (supporting, not decisive on their own) ───────────
_RE_SONG: Final[re.Pattern[str]] = re.compile(
    r"\bop\b|\bed\b|opening|ending|song|lyric|piosenk|karaoke|insert.?song|theme", re.I
)
_RE_NOTE: Final[re.Pattern[str]] = re.compile(
    r"disclaimer|\bnote\b|notka|przypis|tln|t/n|credit|copyright", re.I
)
_RE_SIGN: Final[re.Pattern[str]] = re.compile(
    r"sign|znak|kartka|title|next_ep|acquired|chyron|chapter|^ts$|typeset|caption.?box|box$", re.I
)
_RE_DLG: Final[re.Pattern[str]] = re.compile(
    r"default|main|dialog|narrat|italic|flashback|tirets|thought|mysli|myśli|alter|overlap", re.I
)

# ── Animation deduplication thresholds ──────────────────────────────────────
_DEDUP_MIN_REPEAT: Final[int] = 5
"""Minimum repeats of identical text to consider it animation."""

_DEDUP_WINDOW_MS: Final[int] = 2000
"""Median start gap below this (in ms) marks dense-in-time animation."""

# ── Style classification thresholds ─────────────────────────────────────────
_DRAW_SIGN_RATIO: Final[float] = 0.30
"""Vector-drawing line ratio above which a style is a sign (shape)."""

_KARA_SONG_RATIO: Final[float] = 0.30
"""Karaoke line ratio above which a style is an OP/ED song."""

_DLG_MAX_POS_RATIO: Final[float] = 0.50
"""Max positioning ratio for the confident-dialogue-variant shortcut."""

_SCORE_DIALOG: Final[float] = 0.55
"""Score at or above which a style is classified as DIALOG."""

_SCORE_SIGN: Final[float] = 0.25
"""Score at or below which a style is classified as SIGN."""


class Category(Enum):
    """Subtitle style category for auto mode."""

    DIALOG = "DIALOG"
    """Speech, narration or thoughts -- read by the narrator."""

    SIGN = "SIGN"
    """On-screen sign, song or note -- skipped."""

    UNCERTAIN = "UNCERTAIN"
    """Heuristic is unsure -- left for dry-run or user decision."""


@dataclass(slots=True, frozen=True)
class StyleVerdict:
    """Classification verdict for a single style.

    Attributes:
        style: ASS style name.
        category: Assigned category.
        confidence: Confidence 0.0-1.0; low values are dry-run candidates.
        line_count: Line count after animation deduplication.
        raw_line_count: Line count before deduplication.
    """

    style: str
    category: Category
    confidence: float
    line_count: int
    raw_line_count: int


@dataclass(slots=True)
class _StyleMetrics:
    """Per-style metric accumulator.

    Attributes:
        n: Deduplicated line count.
        raw_n: Line count before deduplication.
        pos: Lines carrying positioning/animation tags.
        draw: Lines carrying vector-drawing tags.
        kara: Lines carrying karaoke tags.
        punct: Lines containing sentence punctuation.
        txt: Total plain-text character count.
    """

    n: int = 0
    raw_n: int = 0
    pos: int = 0
    draw: int = 0
    kara: int = 0
    punct: int = 0
    txt: int = 0


def dedup_animation(events: list[SSAEvent]) -> tuple[list[SSAEvent], int]:
    """Collapse typesetting animation: repeated text in a tight window into one.

    Frame-by-frame animation is the same ``plaintext`` repeated many times in a
    small time window (often interleaved with ``\\p`` drawing lines of the same
    style). One occurrence is kept (read once). Ordinary dialogue, where someone
    says "CO?!" two or three times at distant moments, is not merged.

    Args:
        events: Dialogue lines from the ASS file.

    Returns:
        Tuple of the kept lines and the count removed as animation.
    """
    by_key: dict[tuple[str, str], list[SSAEvent]] = defaultdict(list)
    for event in events:
        by_key[(event.style, event.plaintext.strip())].append(event)

    keep: list[SSAEvent] = []
    removed = 0
    for (_style, text), group in by_key.items():
        if len(group) >= _DEDUP_MIN_REPEAT and text:
            starts = sorted(e.start for e in group)
            diffs = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
            median_gap = sorted(diffs)[len(diffs) // 2] if diffs else 0
            if median_gap < _DEDUP_WINDOW_MS:
                keep.append(min(group, key=lambda e: e.start))
                removed += len(group) - 1
                continue
        keep.extend(group)
    return keep, removed


def _classify_metrics(metrics: _StyleMetrics, style: str, total: int) -> tuple[Category, float]:
    """Classify a style from its deduplicated metrics.

    Args:
        metrics: Accumulated style metrics (post-deduplication).
        style: Style name, used for name-based rules.
        total: Total deduplicated line count in the file, for the share ratio.

    Returns:
        Tuple of the category and the confidence.
    """
    n = metrics.n
    pos, draw, kara, punct = metrics.pos / n, metrics.draw / n, metrics.kara / n, metrics.punct / n
    avg, frac = metrics.txt / n, metrics.n / total

    # Hard SIGN rules.
    if draw > _DRAW_SIGN_RATIO:
        return Category.SIGN, 0.95
    if kara > _KARA_SONG_RATIO:
        return Category.SIGN, 0.95
    if _RE_SONG.search(style):
        return Category.SIGN, 0.9
    if _RE_NOTE.search(style):
        return Category.SIGN, 0.9

    # Confident dialogue variant with no positioning/drawing -- read it.
    if _RE_DLG.search(style) and pos < _DLG_MAX_POS_RATIO and draw == 0:
        return Category.DIALOG, 0.85

    # Weighted scoring for everything else.
    score = 0.0
    if frac >= 0.20:
        score += 0.35
    if pos < 0.40:
        score += 0.25
    if punct > 0.30:
        score += 0.20
    if avg >= 12:
        score += 0.10
    if _RE_DLG.search(style):
        score += 0.15
    if _RE_SIGN.search(style):
        score -= 0.25
    if pos > 0.60:
        score -= 0.30

    if score >= _SCORE_DIALOG:
        return Category.DIALOG, round(min(score, 0.99), 2)
    if score <= _SCORE_SIGN:
        return Category.SIGN, round(min(1 - score, 0.95), 2)
    return Category.UNCERTAIN, 0.5


def classify_styles(subs: SSAFile) -> list[StyleVerdict]:
    """Classify every subtitle style in an ASS file as DIALOG/SIGN.

    Deduplicate animation, accumulate per-style metrics, then classify. The
    result is sorted by descending line count (most significant styles first).

    Args:
        subs: Loaded subtitle file (pysubs2).

    Returns:
        One verdict per style used in Dialogue lines.
    """
    events = [e for e in subs.events if e.type == "Dialogue"]
    if not events:
        return []

    deduped, _ = dedup_animation(events)
    total = len(deduped)

    metrics: dict[str, _StyleMetrics] = defaultdict(_StyleMetrics)
    for event in events:
        metrics[event.style].raw_n += 1
    for event in deduped:
        entry = metrics[event.style]
        entry.n += 1
        if _RE_POS.search(event.text):
            entry.pos += 1
        if _RE_DRAW.search(event.text):
            entry.draw += 1
        if _RE_KARA.search(event.text):
            entry.kara += 1
        plain = event.plaintext
        entry.txt += len(plain)
        if _RE_PUNCT.search(plain):
            entry.punct += 1

    verdicts: list[StyleVerdict] = []
    for style, entry in sorted(metrics.items(), key=lambda kv: -kv[1].n):
        if entry.n == 0:
            continue
        category, confidence = _classify_metrics(entry, style, total)
        verdicts.append(
            StyleVerdict(
                style=style,
                category=category,
                confidence=confidence,
                line_count=entry.n,
                raw_line_count=entry.raw_n,
            )
        )
    return verdicts


def select_dialog_styles(subs: SSAFile) -> list[str]:
    """Return the names of styles classified as DIALOG (for the narrator).

    Convenient shortcut for ``split_ass`` in auto mode. UNCERTAIN styles are
    treated as DIALOG: the user would rather hear a line than miss it, and edge
    cases are reviewed in dry-run anyway.

    Args:
        subs: Loaded subtitle file.

    Returns:
        Names of styles to be read by the narrator.
    """
    return [
        v.style
        for v in classify_styles(subs)
        if v.category in (Category.DIALOG, Category.UNCERTAIN)
    ]
