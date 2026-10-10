"""
Auto-detection of Excellon coordinate format.

Implements the same strategy as KiCad's excellon_read_drill_file.cpp:
  1. Read declared format from the header (units, zero-suppression, coord digits).
  2. Collect all raw *integer* coordinate strings from the body.
  3. Try every candidate format: 2.3 / 2.4 / 3.3 / 3.4 / 4.2.
  4. Score each by PCB plausibility (span, absolute bounds).
  5. Return the best format + a warning when it differs from the declared one.

Usage::

    from gerbyx.excellon.coord_format_detector import detect_coord_format

    best_fmt, warning, reason = detect_coord_format(text)
    # best_fmt  : (int_digits, dec_digits) or None
    # warning   : str or None (non-empty when auto-corrected)
    # reason    : human-readable diagnostic string
"""
from __future__ import annotations

import re
import math
from typing import List, Optional, Tuple

# ────────────────────────────────────────── candidate formats to probe
# (integer_digits, decimal_digits) — order matters: first qualifying wins ties
CANDIDATE_FORMATS: List[Tuple[int, int]] = [
    (2, 3),   # 2.3  – most common metric small/mid boards, INCH FMAT,2 default
    (2, 4),   # 2.4  – metric higher resolution
    (3, 3),   # 3.3  – FMAT,2 metric default per spec
    (3, 4),   # 3.4  – metric sub-micron
    (4, 2),   # 4.2  – less common
]

# ────────────────────────────────────────── PCB plausibility limits
_PCB_MAX_COORD_MM: float = 500.0   # single coordinate upper bound (mm)
_PCB_MIN_COORD_MM: float = -10.0   # small negative offset origin allowed
_PCB_MAX_SPAN_MM: float  = 500.0   # board dimension upper bound (mm)
_PCB_MIN_SPAN_MM: float  =   0.5   # ignore boards < 0.5 mm (degenerate)

# ────────────────────────────────────────── regexps
_UNITS_DECL_RE = re.compile(
    r"^(METRIC|INCH)(?:,(LZ|TZ))?(?:,([\d]+\.[\d]+))?",
    re.IGNORECASE | re.MULTILINE,
)
_HEADER_END_RE = re.compile(r"^%\s*$", re.MULTILINE)

# Integer X/Y coordinate: NOT followed by a decimal digit (avoids decimal coords)
_RAW_X_RE = re.compile(r"X([+-]?\d+)(?!\.\d)", re.IGNORECASE)
_RAW_Y_RE = re.compile(r"Y([+-]?\d+)(?!\.\d)", re.IGNORECASE)

# Detects explicit decimal coordinate anywhere on a line
_DECIMAL_COORD_RE = re.compile(r"[XY][+-]?\d+\.\d", re.IGNORECASE)

# Lines that look like tool definitions (TnCd.ddd) — skip these
_TOOL_DEF_RE = re.compile(r"^T\d+C[\d.]+", re.IGNORECASE)


# ────────────────────────────────────────── helpers

def _apply_zero_sup(
    raw: str,
    int_d: int,
    dec_d: int,
    zero_sup: str,
) -> Optional[float]:
    """Decode a raw integer coordinate string using a candidate (int_d, dec_d) format."""
    sign = 1
    s = raw
    if s.startswith("+"):
        s = s[1:]
    elif s.startswith("-"):
        sign = -1
        s = s[1:]

    if not s.isdigit():
        return None

    total = int_d + dec_d
    # Integer Excellon coordinates cannot have more digits than the candidate
    # fixed-width format; accepting longer strings would silently truncate data.
    if len(s) > total:
        return None

    if zero_sup == "L":
        s = s.zfill(total)       # leading zeros suppressed -> pad LEFT
    else:
        s = s.ljust(total, "0")  # trailing zeros suppressed -> pad RIGHT

    try:
        int_part = s[:int_d]
        dec_part = s[int_d : int_d + dec_d] or "0"
        return sign * float(f"{int_part}.{dec_part}")
    except (ValueError, IndexError):
        return None


def _score_format(
    coords: List[float],
    lim_min: float,
    lim_max: float,
    span_min: float,
    span_max: float,
) -> float:
    """Return a plausibility score for a decoded coordinate set.

    * < 0 : disqualified (out-of-range or degenerate)
    * >=0 : valid; higher values prefer compact, non-degenerate PCB extents
    """
    if not coords:
        return 0.0

    for v in coords:
        if v < lim_min or v > lim_max:
            return -1000.0   # any value outside PCB range -> reject

    mn, mx = min(coords), max(coords)
    span = mx - mn

    if len(coords) > 1:
        if span > span_max:
            return -1000.0   # board too large -> reject
        if span < span_min:
            return -0.5      # near-zero span -> weak

    # Prefer spans close to a typical PCB size using log-distance so both
    # very tiny and near-limit boards score lower than mid-size boards.
    typical_span = max(span_min * 4.0, span_max * 0.15)
    span_ratio = max(span, 1e-9) / max(typical_span, 1e-9)
    span_shape = 1.0 - min(abs(math.log10(span_ratio)) / 2.0, 1.0)

    # Keep a small occupancy term so extremely tiny spans are de-prioritized.
    occupancy = min(max(span, 0.0) / max(span_max, 1e-9), 1.0)
    return 1.0 + 0.80 * span_shape + 0.20 * occupancy


# ────────────────────────────────────────── public API

def detect_coord_format(
    text: str,
) -> Tuple[Optional[Tuple[int, int]], Optional[str], str, str]:
    """
    Analyse an Excellon file text and auto-detect the best coordinate format.

    Mimics the heuristic used by KiCad's ``excellon_read_drill_file.cpp`` but
    also probes **both** zero-suppression directions (LZ / TZ) for every
    candidate format.  This handles the two conflicting Excellon conventions:

    * **Spec / EAGLE** convention: ``TZ`` = trailing zeros are present in the
      data → leading zeros are the suppressed ones → decode by padding LEFT.
    * **KiCad / common** convention: ``TZ`` = trailing zeros are suppressed →
      decode by padding RIGHT.

    Probing both directions ensures the correct decode is found regardless of
    which convention the generating tool uses.

    Parameters
    ----------
    text : full Excellon file content as a string.

    Returns
    -------
    best_format   : ``(int_digits, dec_digits)`` tuple, or ``None`` if
                    coordinates all have explicit decimal points or no data found.
    warning_msg   : a non-empty warning string when the deduced format/ZS
                    differs from the one declared in the header; ``None`` otherwise.
    reason        : human-readable diagnostic (scores for each candidate).
    best_zs       : effective zero-suppression direction: ``"L"`` (pad left /
                    leading-zeros suppressed) or ``"T"`` (pad right / trailing-
                    zeros suppressed).
    """
    # 1. Parse header declared values
    declared_units = "MM"
    declared_zs    = "L"      # FMAT,2 default: LZ (leading zeros suppressed)
    declared_format: Optional[Tuple[int, int]] = None

    m = _UNITS_DECL_RE.search(text)
    if m:
        u = m.group(1).upper()
        declared_units = "MM" if u in ("METRIC", "MM") else "INCH"
        if m.group(2):
            declared_zs = "L" if m.group(2).upper() == "LZ" else "T"
        if m.group(3):
            parts = m.group(3).split(".")
            declared_format = (len(parts[0]), len(parts[1]))

    # 2. Find body (after header-end "%")
    hdr_end = _HEADER_END_RE.search(text)
    body = text[hdr_end.end():] if hdr_end else text

    # 3. Collect raw integer coordinate strings
    raw_int_coords: List[str] = []
    any_decimal = False

    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(";") or _TOOL_DEF_RE.match(s):
            continue
        if _DECIMAL_COORD_RE.search(s):
            any_decimal = True
        else:
            for mo in _RAW_X_RE.finditer(s):
                raw_int_coords.append(mo.group(1))
            for mo in _RAW_Y_RE.finditer(s):
                raw_int_coords.append(mo.group(1))

    # Decimal-point coords: parser reads them as plain float -> no detection needed
    if any_decimal and not raw_int_coords:
        return (
            declared_format,
            None,
            "All coordinates have explicit decimal point — format inference skipped",
            declared_zs,
        )

    if not raw_int_coords:
        return (
            declared_format,
            None,
            "No integer coordinate data found in body",
            declared_zs,
        )

    # 4. PCB limits in declared units
    if declared_units == "INCH":
        lim_max  = _PCB_MAX_COORD_MM / 25.4
        lim_min  = _PCB_MIN_COORD_MM / 25.4
        span_max = _PCB_MAX_SPAN_MM  / 25.4
        span_min = _PCB_MIN_SPAN_MM  / 25.4
    else:
        lim_max  = _PCB_MAX_COORD_MM
        lim_min  = _PCB_MIN_COORD_MM
        span_max = _PCB_MAX_SPAN_MM
        span_min = _PCB_MIN_SPAN_MM

    # 5. Score each candidate format under BOTH zero-suppression directions.
    #    Some tools (e.g. EAGLE) follow the Excellon spec convention where
    #    "TZ" means *trailing zeros are present* (leading zeros suppressed →
    #    pad left to decode), while others (KiCad) use the opposite meaning.
    #    Trying both directions lets us recover the correct decode regardless
    #    of which convention the generating tool used.
    _ScoreEntry = Tuple[Tuple[int, int], str, float]   # (fmt, zs, score)
    scores: List[_ScoreEntry] = []
    best_format: Optional[Tuple[int, int]] = None
    best_zs_out: str = declared_zs
    best_score = -9999.0
    declared_best_score = -9999.0
    declared_best_zs = declared_zs

    for int_d, dec_d in CANDIDATE_FORMATS:
        for zs_try in ("L", "T"):
            decoded: List[float] = []
            ok = True
            for raw in raw_int_coords:
                val = _apply_zero_sup(raw, int_d, dec_d, zs_try)
                if val is None:
                    ok = False
                    break
                decoded.append(val)

            if not ok:
                scores.append(((int_d, dec_d), zs_try, -9999.0))
                continue

            score = _score_format(decoded, lim_min, lim_max, span_min, span_max)

            # Tiny tie-breaking preference for the declared format so that when
            # two (format, zs) pairs decode identically (common for files where
            # all coordinates have the same number of digits) we pick the one
            # the file actually declared.
            if declared_format is not None and (int_d, dec_d) == declared_format:
                score += 0.01
                if score > declared_best_score:
                    declared_best_score = score
                    declared_best_zs = zs_try

            scores.append(((int_d, dec_d), zs_try, score))

            if score > best_score:
                best_score = score
                best_format = (int_d, dec_d)
                best_zs_out = zs_try

    # Prefer declared format when it remains plausible and close to the best
    # candidate. This avoids over-promoting wide-int formats (e.g. 4.2) on
    # Eagle-like mixed 4/5-digit coordinate sets.
    if (
        declared_format is not None
        and declared_best_score >= 0
        and best_format is not None
        and best_format != declared_format
        and (best_score - declared_best_score) <= 0.35
    ):
        best_format = declared_format
        best_zs_out = declared_best_zs
        best_score = declared_best_score

    reason = "scores: " + ", ".join(
        f"{f[0]}.{f[1]}/{zs}={s:.2f}" for f, zs, s in scores
    )

    # 6. Fallback when nothing qualifies
    if best_format is None or best_score < 0:
        fallback = declared_format or ((3, 3) if declared_units == "MM" else (2, 3))
        return (
            fallback,
            None,
            f"No format scored positively (best={best_score:.2f}); "
            f"using fallback {fallback[0]}.{fallback[1]}. {reason}",
            declared_zs,
        )

    # 7. Warning when auto-deduced values differ from declared
    fmt_changed = declared_format is not None and declared_format != best_format
    zs_changed  = best_zs_out != declared_zs

    warning_out: Optional[str] = None
    if fmt_changed or zs_changed:
        decl_parts: List[str] = []
        if declared_format is not None:
            decl_parts.append(f"format {declared_format[0]}.{declared_format[1]}")
        decl_parts.append(f"{'LZ' if declared_zs == 'L' else 'TZ'}")
        best_parts = [
            f"{best_format[0]}.{best_format[1]}",
            f"{'LZ' if best_zs_out == 'L' else 'TZ'}",
        ]
        warning_out = (
            f"Excellon header declares {' / '.join(decl_parts)} but coordinates "
            f"best match {' / '.join(best_parts)}. "
            f"Using deduced {' / '.join(best_parts)}."
        )

    return best_format, warning_out, reason, best_zs_out

