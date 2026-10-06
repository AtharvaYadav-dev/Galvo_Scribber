"""
Format dispatcher: auto-detects Gerber vs Excellon and routes to the
appropriate pipeline.  Returns a unified result regardless of input type.

Both pipelines expose the same public surface:
    result.format       : "gerber" | "excellon"
    result.geometries   : list of Shapely objects
    result.primitives   : list of parsed primitives (Excellon only; [] for Gerber)
    result.state        : ExcellonState (Excellon only, None for Gerber)
    result.detection    : DetectionResult (auto-detect only; None otherwise)
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from .logger import info, debug


# ─────────────────────────────────────────────────────────────────── pipeline


def process_file(
    source: Union[str, Path],
    *,
    output_units: str = "MM",
    hint_units: Optional[str] = None,
    hint_coord_format: Optional[Union[str, Tuple[int, int]]] = None,
    arc_tolerance_mm: float = 0.01,
    max_arc_segments: int = 128,
    format_hint: Optional[Literal["auto", "gerber", "excellon"]] = None,
) -> "ProcessResult":
    """
    Auto-detect format and process a Gerber or Excellon file.

    Parameters
    ----------
    source            : file path (Path / str) or raw text content
    output_units      : desired output coordinate unit ("MM" | "INCH"), default "MM"
    hint_units        : force input unit interpretation ("MM" | "INCH" | None).
                        Only relevant for Excellon; ignored for Gerber.
    hint_coord_format : force Excellon coordinate format (e.g. "2.3", "3.3", (2,3)).
                        Optional; when omitted parser uses file-declared format or defaults.
    arc_tolerance_mm  : chord-height tolerance for arc segmentation (mm).
    max_arc_segments  : hard upper limit on arc polyline segments.
    format_hint       : force format detection ("gerber" | "excellon" | "auto" | None)

    Returns
    -------
    ProcessResult with:
        .format          : "gerber" | "excellon"
        .geometries      : list of Shapely objects  (both pipelines)
        .primitives      : list of DrillHit / SlotG85 / RouteSegment (Excellon only)
        .state           : ExcellonState (Excellon only, None for Gerber)
        .detection       : DetectionResult (auto-detect only, None otherwise)
    """
    # Load text
    if isinstance(source, Path) or (isinstance(source, str) and "\n" not in source and len(source) < 512):
        p = Path(source)
        if p.exists():
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            path_str = str(p)
        else:
            text = str(source)
            path_str = None
    else:
        text = str(source)
        path_str = None

    # Determine format
    fmt = (format_hint or "auto").lower()
    detection = None

    if fmt == "auto":
        from .excellon.detector import detect_format
        detection = detect_format(text, path=path_str)
        debug(lambda: f"Format detection: {detection.format} (confidence={detection.confidence:.2f})")
        fmt = detection.format if detection.format != "unknown" else "gerber"

    if fmt == "excellon":
        return _run_excellon(
            text,
            output_units=output_units,
            hint_units=hint_units,
            hint_coord_format=hint_coord_format,
            arc_tolerance_mm=arc_tolerance_mm,
            max_arc_segments=max_arc_segments,
            detection=detection,
        )
    else:
        return _run_gerber(text)


# ─────────────────────────────────────────────────────── Excellon pipeline


def _run_excellon(
    text: str,
    output_units: str,
    hint_units: Optional[str],
    hint_coord_format: Optional[Union[str, Tuple[int, int]]],
    arc_tolerance_mm: float,
    max_arc_segments: int,
    detection=None,
) -> "ProcessResult":
    from .excellon.state import ExcellonState
    from .excellon.tokenizer import tokenize_excellon
    from .excellon.parser import ExcellonParser
    from .excellon.processor import ExcellonProcessor

    state = ExcellonState(
        output_units=output_units.upper(),
        arc_tolerance_mm=arc_tolerance_mm,
        max_arc_segments=max_arc_segments,
    )

    # Apply hints from detector (e.g. guessed units) before parser sees them
    if detection and detection.hints.get("units") and not hint_units:
        debug(lambda: f"Using detector hint units: {detection.hints['units']}")
    if detection and detection.hints.get("zero_suppression"):
        state.zero_suppression = detection.hints["zero_suppression"]

    parser = ExcellonParser(
        state,
        hint_units=hint_units,
        hint_coord_format=hint_coord_format,
        auto_detect_coord_format=True,
        source_text=text,
    )
    tokens = tokenize_excellon(text)
    parser.parse(tokens)

    proc = ExcellonProcessor(state)
    proc.process(parser.primitives)

    info(f"Excellon pipeline: {len(parser.primitives)} primitives → {len(proc.geometries)} geometries")

    return ProcessResult(
        format="excellon",
        geometries=proc.geometries,
        detection=detection,
        state=state,
        primitives=parser.primitives,
    )


# ─────────────────────────────────────────────────────── Gerber pipeline


def _run_gerber(text: str) -> "ProcessResult":
    from .tokenizer import tokenize_gerber
    from .parser import GerberParser
    from .processor import GerberProcessor

    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(text)
    parser.parse(tokens)
    geometries = processor.geometries

    info(f"Gerber pipeline: {len(geometries)} geometries")

    return ProcessResult(
        format="gerber",
        geometries=geometries,
        detection=None,
        state=None,
        primitives=[],
    )


# ─────────────────────────────────────────────────────── Result container


class ProcessResult:
    """Container for the output of process_file()."""

    def __init__(
        self,
        format: str,
        geometries: list,
        detection,
        state,
        primitives: list,
    ):
        self.format = format
        self.geometries = geometries
        self.detection = detection
        self.state = state          # ExcellonState for Excellon, None for Gerber
        self.primitives = primitives

    def __repr__(self) -> str:
        return (
            f"ProcessResult(format={self.format!r}, "
            f"primitives={len(self.primitives)}, "
            f"geometries={len(self.geometries)})"
        )

