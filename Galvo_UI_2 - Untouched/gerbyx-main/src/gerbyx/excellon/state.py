"""
Excellon parser state: units, format, tool table, position, mode flags.
All unit conversions are centralised here.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

INCH_TO_MM: float = 25.4
MM_TO_INCH: float = 1.0 / 25.4


@dataclass
class ToolDefinition:
    """A single Excellon tool (drill bit)."""
    number: int
    diameter_input: float           # diameter as parsed (in input_units)
    diameter_mm: float              # always mm — golden truth
    diameter_inch: float            # always inch — golden truth
    feed_rate: Optional[float] = None       # units/min (input units)
    spindle_speed: Optional[int] = None     # RPM
    retract_rate: Optional[float] = None    # units/min
    max_depth: Optional[float] = None       # depth in input units
    plating: str = "unknown"                # PTH | NPTH | VIA | unknown
    hit_count: int = 0                      # incremented by parser


@dataclass
class ExcellonState:
    """
    Full mutable state of the Excellon parser at any point during parsing.

    Unit policy
    -----------
    * input_units  : what the file uses (INCH | MM | None if ambiguous)
    * output_units : what the consumer wants (default MM)
    * Conversion is applied in to_mm() / to_output() / input_to_output().
    * diameter_mm in ToolDefinition is always in mm regardless of output_units.
    """

    # ------------------------------------------------------------------ units
    input_units: Optional[str] = None      # "INCH" | "MM" | None (ambiguous)
    output_units: str = "MM"               # "MM" | "INCH"
    units_ambiguous: bool = False          # set when no unit declaration found
    units_forced: bool = False             # set when user supplied --units

    # --------------------------------------------------------------- format
    fmat_version: int = 2
    # zero_suppression: which zeros ARE suppressed/missing in the raw number
    #   "L" = leading zeros suppressed  (LZ in file)  → pad LEFT  to restore
    #   "T" = trailing zeros suppressed (TZ in file)  → pad RIGHT to restore
    # FMAT,2 modern default is LZ (leading suppressed, keep trailing)
    zero_suppression: str = "L"
    # Set to True when the autodetector has chosen a ZS direction so that the
    # header UNITS line does not overwrite it (see parser._handle_units).
    zero_suppression_forced: bool = False
    # (int_digits, dec_digits) — derived from file header or default
    coord_format: Optional[Tuple[int, int]] = None
    coord_format_forced: bool = False       # set when caller forces --coord-format
    coord_mode: str = "absolute"           # "absolute" | "incremental"

    # --------------------------------------------------------------- tooling
    tools: Dict[int, ToolDefinition] = field(default_factory=dict)
    current_tool: Optional[int] = None
    current_plating_hint: str = "unknown"  # updated by ;PTH ;NPTH comments

    # ------------------------------------------------------------- arc params
    arc_tolerance_mm: float = 0.01         # chord-height tolerance (mm)
    max_arc_segments: int = 128            # hard cap for arc polyline

    # --------------------------------------------------------- current position
    # These are kept in INPUT units during parsing, converted on output
    current_x: float = 0.0
    current_y: float = 0.0

    # ----------------------------------------------------------- state flags
    in_header: bool = False
    in_route_mode: bool = False
    program_ended: bool = False

    # -------------------------------------------------- route segment buffer
    # Each entry is a RouteSegment emitted during routing (appended by parser)
    route_buffer: List = field(default_factory=list)

    # -------------------------------------------------------- unit helpers
    def to_mm(self, value: float) -> float:
        """Convert a value from input_units to mm."""
        if self.input_units == "INCH":
            return value * INCH_TO_MM
        return value  # already MM or unknown (treated as MM)

    def to_output(self, value_mm: float) -> float:
        """Convert a mm value to output_units."""
        if self.output_units == "INCH":
            return value_mm * MM_TO_INCH
        return value_mm

    def input_to_output(self, value: float) -> float:
        """Convert directly from input_units to output_units."""
        return self.to_output(self.to_mm(value))

    @property
    def converted(self) -> bool:
        """True if a unit conversion will actually be applied."""
        if self.input_units is None:
            return False
        return self.input_units != self.output_units

    @property
    def conversion_factor(self) -> float:
        """Multiplicative factor from input_units → output_units."""
        if not self.converted:
            return 1.0
        if self.input_units == "INCH" and self.output_units == "MM":
            return INCH_TO_MM
        if self.input_units == "MM" and self.output_units == "INCH":
            return MM_TO_INCH
        return 1.0

    def effective_coord_format(self) -> Tuple[int, int]:
        """Return coord_format with sensible defaults when not declared."""
        if self.coord_format:
            return self.coord_format
        # Defaults matching the most common real-world usage (FMAT,2)
        if self.input_units == "MM":
            return (3, 3)   # 3 integer, 3 decimal → 6 total chars (MM 3.3)
        else:
            return (2, 3)   # 2 integer, 3 decimal → 5 total chars (INCH 2.3)

    def current_tool_def(self) -> Optional[ToolDefinition]:
        """Return the currently selected tool definition, or None."""
        if self.current_tool is None:
            return None
        return self.tools.get(self.current_tool)
