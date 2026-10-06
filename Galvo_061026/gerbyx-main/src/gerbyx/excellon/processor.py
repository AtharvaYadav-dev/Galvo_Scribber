"""
Excellon processor: converts typed primitives to Shapely geometries.

Mirrors the GerberProcessor.geometries API::

    proc = ExcellonProcessor(state)
    proc.process(parser.primitives)   # load & cache
    geoms = proc.geometries           # [shapely Polygon, ...]

Low-level stateless access::

    geoms = proc.to_geometries(primitives)
"""
from __future__ import annotations
import math
from typing import List, Optional, Tuple

from shapely.geometry import LineString, Point, Polygon

from .state import ExcellonState, MM_TO_INCH
from .primitives import DrillHit, SlotG85, RouteSegment


class ExcellonProcessor:
    """
    Renders Excellon primitives to Shapely geometries.

    Mirrors the GerberProcessor interface:

    * ``proc.process(primitives)`` — load primitives and invalidate cache.
    * ``proc.geometries``          — cached list of Shapely geometries (lazy).
    * ``proc.to_geometries(primitives)`` — stateless helper (no cache).

    Geometry model (aligned with Gerber pipeline):

    +-----------------------+-------------------------------------------+
    | Primitive             | Shapely geometry                          |
    +=======================+===========================================+
    | DrillHit              | ``Point(x, y).buffer(r)``                 |
    +-----------------------+-------------------------------------------+
    | SlotG85               | ``LineString([start, end]).buffer(r)``    |
    +-----------------------+-------------------------------------------+
    | RouteSegment (line)   | ``LineString([start, end]).buffer(r)``    |
    +-----------------------+-------------------------------------------+
    | RouteSegment (arc)    | discretised arc → ``LineString.buffer(r)``|
    +-----------------------+-------------------------------------------+
    """

    #: Fixed quad-segs for drill circles (circles don't need adaptive segs)
    DRILL_CIRCLE_RESOLUTION = 64

    def __init__(self, state: ExcellonState):
        self.state = state
        self._primitives: List = []
        self._geometries_cache: Optional[List] = None

    # ------------------------------------------------------------------ public

    def process(self, primitives: List) -> None:
        """Load *primitives* into the processor and invalidate the geometry cache.

        Must be called before accessing :attr:`geometries`.
        Mirrors the incremental command-dispatch of ``GerberProcessor``.
        """
        self._primitives = list(primitives)
        self._geometries_cache = None

    @property
    def geometries(self) -> List:
        """Cached list of Shapely geometries built from the loaded primitives.

        Returns an empty list when :meth:`process` has not been called yet.
        """
        if self._geometries_cache is None:
            self._geometries_cache = self.to_geometries(self._primitives)
        return self._geometries_cache

    def to_geometries(self, primitives: List) -> List:
        """Convert *primitives* directly to Shapely geometry objects (stateless).

        Each primitive maps to one Shapely ``Polygon``:

        * :class:`~.primitives.DrillHit`    → ``Point.buffer(r)``
        * :class:`~.primitives.SlotG85`     → ``LineString.buffer(r, round)``
        * :class:`~.primitives.RouteSegment` → ``LineString.buffer(r, round)``
          (arc segments are adaptively discretised before buffering)
        """
        geoms = []
        for p in primitives:
            shape = self._primitive_to_shape(p)
            if shape is not None and not shape.is_empty:
                geoms.append(shape)
        return geoms

    # -------------------------------------------------------- geometry builders

    def _primitive_to_shape(self, p):
        if isinstance(p, DrillHit):
            return self._drill_shape(p)
        elif isinstance(p, SlotG85):
            return self._slot_shape(p)
        elif isinstance(p, RouteSegment):
            return self._route_shape(p)
        return None

    def _drill_shape(self, drill: DrillHit) -> Polygon:
        """Drill hit → Point buffered by tool radius."""
        r = drill.diameter_out / 2.0
        return Point(drill.x, drill.y).buffer(
            r, quad_segs=self.DRILL_CIRCLE_RESOLUTION // 4
        )

    def _slot_shape(self, slot: SlotG85) -> Polygon:
        """Slot G85 → LineString buffered by tool radius (capsule)."""
        r = slot.diameter_out / 2.0
        line = LineString([(slot.x_start, slot.y_start), (slot.x_end, slot.y_end)])
        return line.buffer(r, cap_style="round", quad_segs=8)

    def _route_shape(self, seg: RouteSegment) -> Polygon:
        """Route segment → LineString buffered by tool radius.

        For arc segments the arc is first discretised with adaptive
        chord-height segmentation, then the resulting polyline is buffered.
        """
        r = seg.diameter_out / 2.0

        if seg.segment_type == "line":
            line = LineString([(seg.x_start, seg.y_start), (seg.x_end, seg.y_end)])
        else:
            clockwise = seg.segment_type == "arc_cw"
            cx, cy = seg.arc_center_x, seg.arc_center_y

            if cx is None or cy is None:
                # No centre computed — degrade to straight line
                line = LineString([(seg.x_start, seg.y_start), (seg.x_end, seg.y_end)])
            else:
                tol_mm = seg.arc_tolerance_mm or self.state.arc_tolerance_mm
                tol_out = (
                    tol_mm * MM_TO_INCH
                    if self.state.output_units == "INCH"
                    else tol_mm
                )
                max_segs = seg.max_arc_segments or self.state.max_arc_segments

                arc_pts, _ = self._adaptive_arc_points(
                    seg.x_start, seg.y_start,
                    seg.x_end, seg.y_end,
                    cx, cy,
                    clockwise,
                    tol_out,
                    max_segs,
                )
                line = (
                    LineString(arc_pts)
                    if len(arc_pts) >= 2
                    else LineString([(seg.x_start, seg.y_start), (seg.x_end, seg.y_end)])
                )

        return line.buffer(r, cap_style="round", quad_segs=4)

    # --------------------------------------------------------- arc helpers

    def _adaptive_arc_points(
        self,
        sx: float, sy: float,
        ex: float, ey: float,
        cx: float, cy: float,
        clockwise: bool,
        tolerance: float,
        max_segs: int,
    ) -> Tuple[List[Tuple[float, float]], int]:
        """Generate arc polyline points using chord-height adaptive segmentation.

        Returns ``(points, n_segments_used)``.

        The segment count satisfies::

            n ≥ angle_span / (2 · arccos(1 − tolerance / radius))

        and is clamped to *max_segs*.
        """
        r = math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)
        if r < 1e-9:
            return [(sx, sy), (ex, ey)], 1

        start_angle = math.atan2(sy - cy, sx - cx)
        end_angle   = math.atan2(ey - cy, ex - cx)

        if clockwise:
            if end_angle > start_angle:
                end_angle -= 2 * math.pi
        else:
            if end_angle < start_angle:
                end_angle += 2 * math.pi

        angle_span = abs(end_angle - start_angle)
        if angle_span < 1e-9:
            return [(sx, sy), (ex, ey)], 1

        if tolerance > 0 and r > 0:
            ratio = min(tolerance / r, 1.0)
            if ratio >= 1.0:
                n = 2
            else:
                angle_per_seg = 2.0 * math.acos(1.0 - ratio)
                n = max(2, math.ceil(angle_span / angle_per_seg))
        else:
            n = max_segs

        n = min(n, max_segs)

        points = []
        for i in range(n + 1):
            t = i / n
            angle = start_angle + t * (end_angle - start_angle)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        return points, n
