"""
Excellon drill file parser for gerbyx.

Parallel pipeline to the Gerber parser — no shared code with Gerber processing.
Public API mirrors GerberParser/GerberProcessor pattern.
"""

from .state import ExcellonState, ToolDefinition, INCH_TO_MM, MM_TO_INCH
from .primitives import DrillHit, SlotG85, RouteSegment
from .tokenizer import tokenize_excellon
from .parser import ExcellonParser
from .processor import ExcellonProcessor
from .detector import detect_format, DetectionResult
from .coord_format_detector import detect_coord_format, CANDIDATE_FORMATS

__all__ = [
    "ExcellonState",
    "ToolDefinition",
    "INCH_TO_MM",
    "MM_TO_INCH",
    "DrillHit",
    "SlotG85",
    "RouteSegment",
    "tokenize_excellon",
    "ExcellonParser",
    "ExcellonProcessor",
    "detect_format",
    "DetectionResult",
    "detect_coord_format",
    "CANDIDATE_FORMATS",
]

