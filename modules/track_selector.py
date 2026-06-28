"""Auto-pick the original audio and source subtitle track from MKV metadata.

Drive Pillar 2 of MM_AVH's auto dub pipeline: instead of asking the user for
track IDs, choose one audio track (the original, played under the narrator) and
one subtitle track (translated to Polish, then voiced) straight from mkvmerge
metadata -- no guessing, the answer is in the language, the track name and the
line count. Validated against 206 MKV files with agent-read ground truth.

Subtitle ranking prefers Polish, then English, then the rest: the output is
Polish either way, but translating from English beats touching a ready Polish
track. "Signs/songs/forced" tracks carry only typesetting, not full dialogue, so
a name penalty drops them below any complete track. Audio ranking prefers the
original language (Japanese, then English, then Chinese), nudged by the default
track flag.

Track dicts follow ``modules.mkvtoolnix._parse_track_data`` but the per-track
line count (mkvmerge ``properties.num_index_entries``) is not in that shape, so
``num_lines`` is read as an optional field used only to break a language tie.

Example:
    from modules.track_selector import select_audio_track, select_subtitle_track

    audio_id = select_audio_track(tracks)
    subtitle_id = select_subtitle_track(tracks)
"""

from __future__ import annotations

import re
from typing import Final

# ── Language priorities (lowercase ISO 639-2/B or -1, as mkvmerge emits) ─────
_SUB_LANG_WEIGHT: Final[dict[str, int]] = {
    "pol": 100,
    "pl": 100,
    "eng": 50,
    "en": 50,
}
"""Subtitle language weight; languages absent here fall back to the default."""

_SUB_LANG_DEFAULT: Final[int] = 10
"""Weight for any subtitle language outside ``_SUB_LANG_WEIGHT``."""

_AUDIO_LANG_WEIGHT: Final[dict[str, int]] = {
    "jpn": 100,
    "ja": 100,
    "eng": 40,
    "en": 40,
    "chi": 30,
    "zho": 30,
    "chs": 30,
    "cht": 30,
}
"""Audio language weight; languages absent here fall back to the default."""

_AUDIO_LANG_DEFAULT: Final[int] = 20
"""Weight for any audio language outside ``_AUDIO_LANG_WEIGHT``."""

# ── Scoring weights ──────────────────────────────────────────────────────────
_SIGNS_PENALTY: Final[int] = -200
"""Penalty for a subtitle whose name marks it as signs/songs-only.

Large enough to disqualify a signs-only track outright: even top-priority
Polish (100) drops below any full track of any language, so the narrator is
never handed mere typesetting when real dialogue exists in another language.
"""

_DEFAULT_BONUS: Final[int] = 10
"""Bonus for an audio track flagged as the container's default."""

_LINES_DIVISOR: Final[float] = 1000.0
"""Scale for the line-count tie-breaker, keeping it below the language step."""

# A name advertising on-screen signs, OP/ED songs or a forced (signs-only) track
# rather than the full dialogue. Matched against the track name only -- the
# ``forced`` *property* flag is unreliable, since complete dialogue tracks are
# sometimes shipped flagged forced.
_RE_SIGNS: Final[re.Pattern[str]] = re.compile(r"sign|song|forced", re.I)


def _track_name(track: dict) -> str:
    """Return the track's display name from whichever field is present.

    Accept the dataset shape (``name``), the flat mkvmerge shape
    (``track_name``), and the raw mkvmerge JSON shape where mkvmerge nests
    metadata inside ``properties`` -- fall through all three so both test
    fixtures and live production data work with one code path.

    Args:
        track: A single track dict.

    Returns:
        The track name, or an empty string if none is set.
    """
    return (
        track.get("track_name")
        or track.get("name")
        or track.get("properties", {}).get("track_name")
        or ""
    )


def _track_language(track: dict) -> str:
    """Return the track's ISO 639 language tag from whichever field is present.

    mkvmerge nests ``language`` inside ``properties`` in its raw JSON output;
    the dataset uses a flat ``lang`` key.  Try both, then fall back to the
    nested location so that live mkvmerge data is handled without any
    pre-processing step.

    Args:
        track: A single track dict.

    Returns:
        The language code (lowercased), or an empty string if none is set.
    """
    return (
        track.get("language")
        or track.get("lang")
        or track.get("properties", {}).get("language")
        or ""
    ).lower()


def _track_default(track: dict) -> bool:
    """Return whether the track is flagged as the container default.

    mkvmerge nests ``default_track`` inside ``properties`` in its raw JSON;
    the dataset uses a flat ``default`` key.  Check both locations.

    Args:
        track: A single track dict.

    Returns:
        True if any default-flag field is truthy.
    """
    return bool(
        track.get("default_track")
        or track.get("default")
        or track.get("properties", {}).get("default_track")
    )


def _is_signs_only(track: dict) -> bool:
    """Tell whether a subtitle track carries only signs/songs, not dialogue."""
    return bool(_RE_SIGNS.search(_track_name(track)))


def _lines_bonus(track: dict) -> float:
    """Return the line-count tie-breaker, or 0.0 when the count is unknown.

    Accept the dataset shapes (``num_lines`` / ``lines``) and the raw mkvmerge
    JSON shape where mkvmerge stores the count as ``properties.num_index_entries``
    -- fall through all three so both fixtures and live data resolve correctly.

    Args:
        track: A single track dict, optionally with a line-count field.

    Returns:
        ``lines / _LINES_DIVISOR``, or 0.0 if no usable count is present.
    """
    lines = track.get("num_lines")
    if lines is None:
        lines = track.get("lines")
    if lines is None:
        lines = track.get("properties", {}).get("num_index_entries")
    if lines is None:
        return 0.0
    return lines / _LINES_DIVISOR


def score_subtitle_track(track: dict) -> float:
    """Score a subtitle track for use as the translation source.

    Combine the language weight (Polish > English > rest) with a penalty for
    signs/songs-only tracks and a small line-count bonus that breaks ties within
    a language. Higher is better.

    Args:
        track: A subtitle track dict (``language``/``lang``, name, line count).

    Returns:
        The track's score; the caller picks the maximum.
    """
    lang = _track_language(track)
    score = float(_SUB_LANG_WEIGHT.get(lang, _SUB_LANG_DEFAULT))
    if _is_signs_only(track):
        score += _SIGNS_PENALTY
    return score + _lines_bonus(track)


def score_audio_track(track: dict) -> float:
    """Score an audio track for use as the original under the narrator.

    Combine the language weight (Japanese > English > Chinese > rest) with a
    bonus for the container's default track. Higher is better.

    Args:
        track: An audio track dict (``language``/``lang``, optional default flag).

    Returns:
        The track's score; the caller picks the maximum.
    """
    lang = _track_language(track)
    score = float(_AUDIO_LANG_WEIGHT.get(lang, _AUDIO_LANG_DEFAULT))
    if _track_default(track):
        score += _DEFAULT_BONUS
    return score


def select_subtitle_track(tracks: list[dict]) -> int | None:
    """Pick the subtitle track to translate and voice, by metadata alone.

    Keep only subtitle tracks, score each (see ``score_subtitle_track``) and
    return the id of the highest. Ties resolve toward the lower id, matching the
    file order mkvmerge reports.

    Args:
        tracks: All tracks of the MKV, mixed types.

    Returns:
        The chosen subtitle track's id, or None if the file has no subtitles.
    """
    subtitles = [t for t in tracks if t.get("type") == "subtitles"]
    if not subtitles:
        return None
    best = max(subtitles, key=lambda t: (score_subtitle_track(t), -t["id"]))
    return best["id"]


def select_audio_track(tracks: list[dict]) -> int | None:
    """Pick the original audio track for the narrator, by metadata alone.

    Keep only audio tracks, score each (see ``score_audio_track``) and return
    the id of the highest. Ties resolve toward the lower id, matching the file
    order mkvmerge reports.

    Args:
        tracks: All tracks of the MKV, mixed types.

    Returns:
        The chosen audio track's id, or None if the file has no audio.
    """
    audio = [t for t in tracks if t.get("type") == "audio"]
    if not audio:
        return None
    best = max(audio, key=lambda t: (score_audio_track(t), -t["id"]))
    return best["id"]
