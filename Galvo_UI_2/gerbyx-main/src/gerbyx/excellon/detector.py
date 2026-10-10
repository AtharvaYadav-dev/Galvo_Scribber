"""
Excellon format detector: score-based heuristic to distinguish Excellon drill
files from Gerber files (or other text).

Returns a DetectionResult with a format name, confidence score (0-1),
and a hints dict that the parser can use (e.g. guessed units).
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

# Excellon-specific markers
_EXCELLON_STRONG = [
    (r"^M48\b",                         4),   # header start
    (r"^T\d+C[\d\.]+",                  3),   # tool definition
    (r"^(?:METRIC|INCH)(?:,(?:LZ|TZ))?",3),  # unit declaration
    (r"^(?:FMAT|VER),\d",               2),   # format version
    (r"G85",                            3),   # canned slot
    (r"^M30\b",                         2),   # program end
    (r"^M95\b",                         2),   # header end (alt)
]

_EXCELLON_MEDIUM = [
    (r"^G00[XY]",                       2),   # route reposition
    (r"^G05\b",                         2),   # drill mode
    (r";PTH\b|;NPTH\b",                 2),   # KiCad plating comments
    (r"^T\d+$",                         1),   # bare tool select (ambiguous)
    (r"^X[\d\+\-]+Y[\d\+\-]+$",         1),   # coord-only drill line
]

# Gerber-specific markers (if present, lower Excellon confidence)
_GERBER_MARKERS = [
    (r"^%FS",    -4),   # format spec
    (r"^%MO",    -4),   # units (Gerber style)
    (r"^%ADD",   -4),   # aperture definition
    (r"^G36\b",  -3),   # region start
    (r"^G37\b",  -3),   # region end
    (r"^M02\b",  -1),   # end of file (shared but Gerber also uses it)
]

# Excellon file extensions
_DRL_EXTENSIONS = {".drl", ".xln", ".exc", ".ncd", ".drd", ".drll"}


@dataclass
class DetectionResult:
    format: str                         # "excellon" | "gerber" | "unknown"
    confidence: float                   # 0.0 – 1.0
    hints: Dict[str, Optional[str]] = field(default_factory=dict)
    reason: str = ""


def detect_format(
    text: str,
    path: Optional[str] = None,
) -> DetectionResult:
    """
    Analyse file content (and optionally the path/extension) to determine
    whether it is an Excellon or Gerber file.

    Returns a DetectionResult.  Confidence >= 0.5 is considered a positive match.
    """
    lines = text.splitlines()
    sample = lines[:80]           # inspect first 80 lines for speed

    score = 0
    hints: Dict[str, Optional[str]] = {}

    for line in sample:
        s = line.strip()
        if not s:
            continue

        for pattern, weight in _EXCELLON_STRONG:
            if re.search(pattern, s, re.IGNORECASE | re.MULTILINE):
                score += weight
                break

        for pattern, weight in _EXCELLON_MEDIUM:
            if re.search(pattern, s, re.IGNORECASE | re.MULTILINE):
                score += weight
                break

        for pattern, weight in _GERBER_MARKERS:
            if re.search(pattern, s, re.IGNORECASE | re.MULTILINE):
                score += weight   # weight is negative
                break

        # Collect unit hints from INCH/METRIC declaration
        m = re.match(r"^(METRIC|INCH)(?:,(LZ|TZ))?", s, re.IGNORECASE)
        if m:
            hints["units"] = m.group(1).upper()
            if m.group(2):
                hints["zero_suppression"] = (
                    "L" if m.group(2).upper() == "LZ" else "T"
                )

    # Bonus from file extension
    if path:
        ext = Path(path).suffix.lower()
        if ext in _DRL_EXTENSIONS:
            score += 3
        elif ext in {".gbr", ".ger", ".grb", ".gtl", ".gbl", ".gts",
                     ".gbs", ".gto", ".gbo", ".gm1", ".gko"}:
            score -= 3

    # Normalise to 0-1 against a realistic max (≈ 20)
    confidence = max(0.0, min(1.0, score / 20.0))

    # Gerber vs Excellon decision
    # If strong Gerber markers found (score very negative) → gerber
    if score <= -3:
        return DetectionResult(
            format="gerber",
            confidence=min(1.0, abs(score) / 20.0),
            hints=hints,
            reason=f"score={score}: strong Gerber markers present",
        )

    if confidence >= 0.3:
        return DetectionResult(
            format="excellon",
            confidence=confidence,
            hints=hints,
            reason=f"score={score}",
        )

    return DetectionResult(
        format="unknown",
        confidence=confidence,
        hints=hints,
        reason=f"score={score}: insufficient evidence",
    )

