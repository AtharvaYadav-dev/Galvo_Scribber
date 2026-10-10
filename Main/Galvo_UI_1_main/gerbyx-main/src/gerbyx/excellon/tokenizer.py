"""
Line-based tokenizer for Excellon drill files.
Yields (token_kind, raw_line, parsed_fields) — coordinates stay as raw strings
for zero-suppression handling in the parser.
"""
from __future__ import annotations
import re
from typing import Any, Dict, Generator, Tuple

TK_HEADER_START = "header_start"
TK_HEADER_END   = "header_end"
TK_UNITS        = "units"
TK_FMAT         = "fmat"
TK_TOOL_DEF     = "tool_def"
TK_TOOL_SEL     = "tool_select"
TK_DRILL        = "drill"
TK_SLOT_G85     = "slot_g85"
TK_ROUTE_G00    = "route_g00"
TK_ROUTE_G01    = "route_g01"
TK_ROUTE_G02    = "route_g02"
TK_ROUTE_G03    = "route_g03"
TK_DRILL_MODE   = "drill_mode"
TK_ABS_MODE     = "abs_mode"
TK_INC_MODE     = "inc_mode"
TK_REPEAT       = "repeat"
TK_PROG_END     = "prog_end"
TK_FILE_END     = "file_end"
TK_COMMENT      = "comment"
TK_UNKNOWN      = "unknown"

_TOOL_DEF_RE = re.compile(
    r"^T(\d+)C([\d\.]+)"
    r"(?:F([\d\.]+))?(?:S(\d+))?(?:B([\d\.]+))?(?:H([\d\.]+))?(?:Z([\d\.]+))?",
    re.IGNORECASE,
)
_TOOL_SEL_RE  = re.compile(r"^T(\d+)$", re.IGNORECASE)
_REPEAT_RE    = re.compile(r"^R(\d+)(?:X([+-]?[\d\.]+))?(?:Y([+-]?[\d\.]+))?", re.IGNORECASE)
_UNITS_RE     = re.compile(r"^(METRIC|INCH)(?:,(LZ|TZ))?(?:,([\d]+\.[\d]+))?", re.IGNORECASE)
_FMAT_RE      = re.compile(r"^(?:FMAT|VER),(\d+)", re.IGNORECASE)
_G85_FULL_RE  = re.compile(
    r"X([+-]?[\d\.]+)Y([+-]?[\d\.]+)G85X([+-]?[\d\.]+)Y([+-]?[\d\.]+)", re.IGNORECASE
)
_G85_SHORT_RE = re.compile(r"^G85X([+-]?[\d\.]+)Y([+-]?[\d\.]+)", re.IGNORECASE)
_X_RE = re.compile(r"X([+-]?[\d\.]+)", re.IGNORECASE)
_Y_RE = re.compile(r"Y([+-]?[\d\.]+)", re.IGNORECASE)
_A_RE = re.compile(r"A([+-]?[\d\.]+)", re.IGNORECASE)
_R_ARC_RE = re.compile(r"(?<![A-Z])R([+-]?[\d\.]+)(?!\d)", re.IGNORECASE)
_I_RE = re.compile(r"I([+-]?[\d\.]+)", re.IGNORECASE)
_J_RE = re.compile(r"J([+-]?[\d\.]+)", re.IGNORECASE)


def _parse_xy(s: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    m = _X_RE.search(s)
    if m:
        result["x"] = m.group(1)
    m = _Y_RE.search(s)
    if m:
        result["y"] = m.group(1)
    return result


def _parse_arc(s: str) -> Dict[str, Any]:
    result = _parse_xy(s)
    m = _A_RE.search(s)
    if m:
        result["a"] = m.group(1)          # A-style radius
    else:
        m = _R_ARC_RE.search(s)
        if m:
            result["a"] = m.group(1)      # R-style radius (treated same as A)
    m = _I_RE.search(s)
    if m:
        result["i"] = m.group(1)          # I/J center-offset style
    m = _J_RE.search(s)
    if m:
        result["j"] = m.group(1)
    return result


def tokenize_excellon(
    text: str,
) -> Generator[Tuple[str, str, Dict[str, Any]], None, None]:
    """
    Tokenise an Excellon drill file line by line.
    Yields (token_kind, raw_line, parsed_fields).
    """
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith(";"):
            yield (TK_COMMENT, raw_line, {"text": line[1:].strip()})
            continue

        if line == "M48":
            yield (TK_HEADER_START, raw_line, {})
            continue

        if line in ("%", "M95", "M95,"):
            yield (TK_HEADER_END, raw_line, {})
            continue

        if line in ("M30", "M00", "M0"):
            yield (TK_PROG_END, raw_line, {})
            continue

        if line == "M02":
            yield (TK_FILE_END, raw_line, {})
            continue

        line_upper = line.upper()

        m = _FMAT_RE.match(line)
        if m:
            yield (TK_FMAT, raw_line, {"version": int(m.group(1))})
            continue

        m = _UNITS_RE.match(line)
        if m:
            units = m.group(1).upper()
            zs_raw = m.group(2)
            fmt_str = m.group(3)
            fields: Dict[str, Any] = {"units": units}
            if zs_raw:
                fields["zero_suppression"] = "L" if zs_raw.upper() == "LZ" else "T"
            if fmt_str:
                parts = fmt_str.split(".")
                fields["coord_format"] = (len(parts[0]), len(parts[1]))
            yield (TK_UNITS, raw_line, fields)
            continue

        m = _TOOL_DEF_RE.match(line)
        if m:
            fields = {"tool": int(m.group(1)), "diameter": m.group(2)}
            if m.group(3): fields["feed"]    = float(m.group(3))
            if m.group(4): fields["speed"]   = int(m.group(4))
            if m.group(5): fields["retract"] = float(m.group(5))
            if m.group(6): fields["depth"]   = float(m.group(6))
            yield (TK_TOOL_DEF, raw_line, fields)
            continue

        m = _G85_FULL_RE.search(line)
        if m:
            yield (TK_SLOT_G85, raw_line, {
                "x1": m.group(1), "y1": m.group(2),
                "x2": m.group(3), "y2": m.group(4),
                "from_current": False,
            })
            continue

        m = _G85_SHORT_RE.match(line)
        if m:
            yield (TK_SLOT_G85, raw_line, {
                "x2": m.group(1), "y2": m.group(2),
                "from_current": True,
            })
            continue

        if line_upper.startswith("G00"):
            yield (TK_ROUTE_G00, raw_line, _parse_xy(line[3:]))
            continue

        if line_upper.startswith("G01"):
            yield (TK_ROUTE_G01, raw_line, _parse_xy(line[3:]))
            continue

        if line_upper.startswith("G02"):
            yield (TK_ROUTE_G02, raw_line, _parse_arc(line[3:]))
            continue

        if line_upper.startswith("G03"):
            yield (TK_ROUTE_G03, raw_line, _parse_arc(line[3:]))
            continue

        if line_upper.startswith("G05"):
            yield (TK_DRILL_MODE, raw_line, {})
            continue

        if line_upper.startswith(("G81", "G82", "G83")):
            yield (TK_DRILL, raw_line, _parse_xy(line[3:]))
            continue

        if line_upper.startswith("G90"):
            yield (TK_ABS_MODE, raw_line, {})
            continue

        if line_upper.startswith("G91"):
            yield (TK_INC_MODE, raw_line, {})
            continue

        m = _REPEAT_RE.match(line)
        if m:
            yield (TK_REPEAT, raw_line, {
                "count": int(m.group(1)),
                "dx": m.group(2),
                "dy": m.group(3),
            })
            continue

        m = _TOOL_SEL_RE.match(line)
        if m:
            yield (TK_TOOL_SEL, raw_line, {"tool": int(m.group(1))})
            continue

        if line_upper.startswith(("X", "Y")):
            yield (TK_DRILL, raw_line, _parse_xy(line))
            continue

        yield (TK_UNKNOWN, raw_line, {"text": line})

