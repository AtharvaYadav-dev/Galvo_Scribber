"""
Excellon geometric primitives.

Each primitive stores:
  - Coordinates in OUTPUT units (ready for geometry construction)
  - Coordinates/diameter in mm (golden truth, always present in meta)
  - Full provenance metadata
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DrillHit:
    """
    A single drill hit: conceptually just a circle.
    Position is in output_units; the mm fields are always present as golden truth.
    """
    # Position in output_units
    x: float
    y: float
    # Always in mm
    x_mm: float
    y_mm: float
    # Tool info
    tool_number: int
    diameter_mm: float          # always mm — golden truth
    diameter_out: float         # in output_units
    # Provenance
    plating: str = "unknown"    # PTH | NPTH | VIA | unknown
    input_units: str = "MM"
    output_units: str = "MM"
    converted: bool = False
    conversion_factor: float = 1.0
    source_cmd: str = ""
    level_polarity: str = "dark"
    # Tool metadata (forwarded from ToolDefinition)
    feed_rate: Optional[float] = None
    spindle_speed: Optional[int] = None


@dataclass
class SlotG85:
    """
    Canned slot (G85): a straight slot from start to end with given tool diameter.
    Geometrically: convex hull of two circles at the endpoints.
    """
    # Endpoints in output_units
    x_start: float
    y_start: float
    x_end: float
    y_end: float
    # Always in mm
    x_start_mm: float
    y_start_mm: float
    x_end_mm: float
    y_end_mm: float
    # Tool info
    tool_number: int
    diameter_mm: float
    diameter_out: float
    # Provenance
    plating: str = "unknown"
    input_units: str = "MM"
    output_units: str = "MM"
    converted: bool = False
    conversion_factor: float = 1.0
    source_cmd: str = ""
    level_polarity: str = "dark"
    feed_rate: Optional[float] = None
    spindle_speed: Optional[int] = None


@dataclass
class RouteSegment:
    """
    A single routed segment: either a linear cut (G01) or an arc cut (G02/G03).

    For arcs:
      arc_center_x/y are in output_units.
      arc_center_x_mm/y_mm are always in mm.
      arc_radius_mm is always in mm.
      arc_angle_deg is the signed sweep angle (negative = CW, positive = CCW).
    """
    segment_type: str               # "line" | "arc_cw" | "arc_ccw"
    # Endpoints in output_units
    x_start: float
    y_start: float
    x_end: float
    y_end: float
    # Always in mm
    x_start_mm: float
    y_start_mm: float
    x_end_mm: float
    y_end_mm: float
    # Tool info
    tool_number: int
    diameter_mm: float
    diameter_out: float
    # Arc-specific (None for line segments)
    arc_center_x: Optional[float] = None       # output_units
    arc_center_y: Optional[float] = None       # output_units
    arc_center_x_mm: Optional[float] = None    # always mm
    arc_center_y_mm: Optional[float] = None    # always mm
    arc_radius_mm: Optional[float] = None      # always mm
    arc_angle_deg: Optional[float] = None      # sweep angle (degrees)
    # Provenance
    plating: str = "unknown"
    input_units: str = "MM"
    output_units: str = "MM"
    converted: bool = False
    conversion_factor: float = 1.0
    source_cmd: str = ""
    level_polarity: str = "dark"
    feed_rate: Optional[float] = None
    spindle_speed: Optional[int] = None
    # Set by processor after segmentation
    arc_tolerance_mm: Optional[float] = None
    segments_used: Optional[int] = None
    max_arc_segments: Optional[int] = None

