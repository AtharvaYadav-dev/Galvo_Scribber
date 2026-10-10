"""Tests for ExcellonProcessor: direct Shapely geometry construction."""
import math
import pytest
from shapely.geometry import Polygon

from gerbyx.excellon.state import ExcellonState, INCH_TO_MM
from gerbyx.excellon.primitives import DrillHit, SlotG85, RouteSegment
from gerbyx.excellon.processor import ExcellonProcessor


# ─────────────────────────────────────────────────────────── helpers

def make_state(input_units="MM", output_units="MM", arc_tol=0.01, max_segs=128):
    s = ExcellonState(output_units=output_units)
    s.input_units = input_units
    s.arc_tolerance_mm = arc_tol
    s.max_arc_segments = max_segs
    return s


def make_drill(x_mm, y_mm, dia_mm, output_units="MM"):
    factor = 1.0 if output_units == "MM" else (1.0 / INCH_TO_MM)
    return DrillHit(
        x=x_mm * factor,
        y=y_mm * factor,
        x_mm=x_mm,
        y_mm=y_mm,
        tool_number=1,
        diameter_mm=dia_mm,
        diameter_out=dia_mm * factor,
        plating="PTH",
        output_units=output_units,
        source_cmd="X050000Y050000",
    )


def make_slot(x_start, y_start, x_end, y_end, dia_mm=1.0):
    return SlotG85(
        x_start=x_start, y_start=y_start,
        x_end=x_end, y_end=y_end,
        x_start_mm=x_start, y_start_mm=y_start,
        x_end_mm=x_end, y_end_mm=y_end,
        tool_number=1,
        diameter_mm=dia_mm,
        diameter_out=dia_mm,
    )


def make_route_line(x_start, y_start, x_end, y_end, dia_mm=2.0):
    return RouteSegment(
        segment_type="line",
        x_start=x_start, y_start=y_start,
        x_end=x_end, y_end=y_end,
        x_start_mm=x_start, y_start_mm=y_start,
        x_end_mm=x_end, y_end_mm=y_end,
        tool_number=1,
        diameter_mm=dia_mm,
        diameter_out=dia_mm,
    )


def make_arc_seg(arc_tol=None, max_segs=None):
    return RouteSegment(
        segment_type="arc_cw",
        x_start=0.0, y_start=10.0, x_end=10.0, y_end=0.0,
        x_start_mm=0.0, y_start_mm=10.0, x_end_mm=10.0, y_end_mm=0.0,
        arc_center_x=0.0, arc_center_y=0.0,
        arc_center_x_mm=0.0, arc_center_y_mm=0.0,
        arc_radius_mm=10.0, arc_angle_deg=-90.0,
        tool_number=1, diameter_mm=2.0, diameter_out=2.0,
        arc_tolerance_mm=arc_tol,
        max_arc_segments=max_segs,
    )


# ─────────────────────────────────────────────────────── DrillHit geometry

class TestDrillGeometry:
    def test_returns_polygon(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_drill(50.0, 60.0, 0.8)])
        assert len(geoms) == 1
        assert isinstance(geoms[0], Polygon)

    def test_not_empty(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_drill(10.0, 10.0, 1.0)])
        assert not geoms[0].is_empty

    def test_area_matches_pi_r_squared(self):
        """Buffered circle area ≈ π·r² (within 1% for 16-segment approximation)."""
        proc = ExcellonProcessor(make_state())
        cx, cy, dia = 0.0, 0.0, 2.0
        geoms = proc.to_geometries([make_drill(cx, cy, dia)])
        r = dia / 2.0
        expected_area = math.pi * r * r
        assert abs(geoms[0].area - expected_area) / expected_area < 0.01

    def test_centroid_matches_drill_position(self):
        proc = ExcellonProcessor(make_state())
        cx, cy = 15.0, 25.0
        geoms = proc.to_geometries([make_drill(cx, cy, 1.0)])
        centroid = geoms[0].centroid
        assert abs(centroid.x - cx) < 0.01
        assert abs(centroid.y - cy) < 0.01

    def test_radius_from_bounds(self):
        """Bounding box half-width/height ≈ tool radius."""
        proc = ExcellonProcessor(make_state())
        cx, cy, dia = 10.0, 20.0, 2.0
        geoms = proc.to_geometries([make_drill(cx, cy, dia)])
        bounds = geoms[0].bounds   # (minx, miny, maxx, maxy)
        half_width  = (bounds[2] - bounds[0]) / 2.0
        half_height = (bounds[3] - bounds[1]) / 2.0
        r = dia / 2.0
        assert abs(half_width  - r) < 0.01
        assert abs(half_height - r) < 0.01

    def test_multiple_drills(self):
        proc = ExcellonProcessor(make_state())
        drills = [make_drill(x, 0.0, 1.0) for x in [0.0, 10.0, 20.0]]
        geoms = proc.to_geometries(drills)
        assert len(geoms) == 3

    def test_inch_output_units(self):
        """Drill rendered in INCH output units: area must match inch diameter.

        make_drill() expects dia_mm in mm; we convert 0.031" → mm so that
        diameter_out (= dia_mm / 25.4) comes out to 0.031 inches.
        """
        proc = ExcellonProcessor(make_state(output_units="INCH"))
        dia_inch = 0.031
        dia_mm = dia_inch * INCH_TO_MM          # → mm golden truth
        # x_mm/y_mm are also supplied as mm so make_drill divides by INCH_TO_MM
        d = make_drill(1.0 * INCH_TO_MM, 2.0 * INCH_TO_MM, dia_mm, output_units="INCH")
        geoms = proc.to_geometries([d])
        r = dia_inch / 2.0
        expected_area = math.pi * r * r
        assert abs(geoms[0].area - expected_area) / expected_area < 0.01


# ─────────────────────────────────────────────────────── SlotG85 geometry

class TestSlotGeometry:
    def test_returns_polygon(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_slot(0.0, 0.0, 10.0, 0.0)])
        assert len(geoms) == 1
        assert isinstance(geoms[0], Polygon)

    def test_not_empty(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_slot(0.0, 0.0, 10.0, 0.0)])
        assert not geoms[0].is_empty

    def test_capsule_extends_beyond_endpoints(self):
        """Buffered line extends beyond both endpoints by the tool radius."""
        proc = ExcellonProcessor(make_state())
        dia = 2.0
        geoms = proc.to_geometries([make_slot(0.0, 0.0, 10.0, 0.0, dia_mm=dia)])
        bounds = geoms[0].bounds   # (minx, miny, maxx, maxy)
        r = dia / 2.0
        assert bounds[0] < -r + 0.01         # extends left of x=0
        assert bounds[2] > 10.0 + r - 0.01  # extends right of x=10

    def test_capsule_width_matches_diameter(self):
        """Slot along X: vertical extent (height) ≈ tool diameter."""
        proc = ExcellonProcessor(make_state())
        dia = 2.0
        geoms = proc.to_geometries([make_slot(0.0, 0.0, 10.0, 0.0, dia_mm=dia)])
        bounds = geoms[0].bounds
        height = bounds[3] - bounds[1]
        assert abs(height - dia) < 0.05

    def test_zero_length_slot_becomes_circle(self):
        """Zero-length slot (start == end) degrades to a circle."""
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_slot(5.0, 5.0, 5.0, 5.0, dia_mm=1.0)])
        assert len(geoms) == 1
        assert not geoms[0].is_empty


# ─────────────────────────────────────────── RouteSegment geometry

class TestRouteLineGeometry:
    def test_returns_polygon(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_route_line(0.0, 0.0, 80.0, 0.0)])
        assert len(geoms) == 1
        assert isinstance(geoms[0], Polygon)

    def test_width_matches_diameter(self):
        """Horizontal route: height of bounding box ≈ tool diameter."""
        proc = ExcellonProcessor(make_state())
        dia = 2.0
        geoms = proc.to_geometries([make_route_line(0.0, 0.0, 80.0, 0.0, dia_mm=dia)])
        bounds = geoms[0].bounds
        height = bounds[3] - bounds[1]
        assert abs(height - dia) < 0.1

    def test_extends_beyond_endpoints(self):
        """Buffered line with round cap extends past start and end."""
        proc = ExcellonProcessor(make_state())
        dia = 2.0
        r = dia / 2.0
        geoms = proc.to_geometries([make_route_line(0.0, 0.0, 80.0, 0.0, dia_mm=dia)])
        bounds = geoms[0].bounds
        assert bounds[0] < -r + 0.1
        assert bounds[2] > 80.0 + r - 0.1


class TestRouteArcGeometry:
    def test_returns_polygon(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_arc_seg()])
        assert len(geoms) == 1
        assert isinstance(geoms[0], Polygon)

    def test_not_empty(self):
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([make_arc_seg()])
        assert not geoms[0].is_empty

    def test_higher_tolerance_gives_smaller_area_variation(self):
        """Fine tolerance → more segments → closer to true arc strip."""
        proc_fine   = ExcellonProcessor(make_state(arc_tol=0.001, max_segs=256))
        proc_coarse = ExcellonProcessor(make_state(arc_tol=1.0,   max_segs=128))
        g_fine   = proc_fine.to_geometries([make_arc_seg()])
        g_coarse = proc_coarse.to_geometries([make_arc_seg()])
        assert g_fine[0].area >= g_coarse[0].area * 0.95

    def test_max_arc_segments_respected(self):
        """Arc polygon must be non-empty even with tight segment cap."""
        state = make_state(arc_tol=0.0001, max_segs=5)
        proc = ExcellonProcessor(state)
        geoms = proc.to_geometries([make_arc_seg(arc_tol=0.0001, max_segs=5)])
        assert not geoms[0].is_empty

    def test_arc_no_center_falls_back_to_line(self):
        """Arc with no center_x/y degrades gracefully to a buffered line."""
        seg = RouteSegment(
            segment_type="arc_cw",
            x_start=0.0, y_start=0.0, x_end=10.0, y_end=0.0,
            x_start_mm=0.0, y_start_mm=0.0, x_end_mm=10.0, y_end_mm=0.0,
            arc_center_x=None, arc_center_y=None,
            tool_number=1, diameter_mm=2.0, diameter_out=2.0,
        )
        proc = ExcellonProcessor(make_state())
        geoms = proc.to_geometries([seg])
        assert len(geoms) == 1
        assert not geoms[0].is_empty


# ─────────────────────────────────────── process() + geometries property

class TestProcessAndGeometriesProperty:
    def test_geometries_empty_before_process(self):
        """Before process() is called, geometries returns []."""
        proc = ExcellonProcessor(make_state())
        assert proc.geometries == []

    def test_geometries_populated_after_process(self):
        proc = ExcellonProcessor(make_state())
        proc.process([make_drill(0.0, 0.0, 1.0)])
        assert len(proc.geometries) == 1

    def test_geometries_cached(self):
        """Second access to .geometries returns the same list object."""
        proc = ExcellonProcessor(make_state())
        proc.process([make_drill(0.0, 0.0, 1.0)])
        g1 = proc.geometries
        g2 = proc.geometries
        assert g1 is g2

    def test_process_invalidates_cache(self):
        """Calling process() again with a different list updates geometries."""
        proc = ExcellonProcessor(make_state())
        proc.process([make_drill(0.0, 0.0, 1.0)])
        _ = proc.geometries   # populate cache
        proc.process([make_drill(0.0, 0.0, 1.0), make_drill(5.0, 5.0, 1.0)])
        assert len(proc.geometries) == 2

    def test_mixed_primitives_via_process(self):
        proc = ExcellonProcessor(make_state())
        primitives = [
            make_drill(0.0, 0.0, 1.0),
            make_slot(10.0, 0.0, 20.0, 0.0),
            make_route_line(30.0, 0.0, 50.0, 0.0),
            make_arc_seg(),
        ]
        proc.process(primitives)
        assert len(proc.geometries) == 4
        for g in proc.geometries:
            assert isinstance(g, Polygon)
            assert not g.is_empty


