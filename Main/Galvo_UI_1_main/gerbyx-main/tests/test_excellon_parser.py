"""Tests for Excellon parser: coordinate resolution, zero-suppression, primitives."""
from pathlib import Path
from gerbyx.excellon.state import ExcellonState
from gerbyx.excellon.parser import ExcellonParser
from gerbyx.excellon.tokenizer import tokenize_excellon
from gerbyx.excellon.primitives import DrillHit, SlotG85, RouteSegment


# ───────────────────────────────────────────────── helpers

def parse(text, output_units="MM", hint_units=None):
    state = ExcellonState(output_units=output_units)
    parser = ExcellonParser(state, hint_units=hint_units)
    parser.parse(tokenize_excellon(text))
    return parser, state


# ───────────────────────────────────────────────── coord resolution unit tests

class TestCoordResolution:
    """Test _resolve_coord with all zero-suppression modes."""

    def _make_parser(self, zs, int_d, dec_d, units="MM"):
        state = ExcellonState()
        state.input_units = units
        state.zero_suppression = zs
        state.coord_format = (int_d, dec_d)
        return ExcellonParser(state)

    def test_lz_3_3_metric(self):
        p = self._make_parser("L", 3, 3)
        # 62.4 mm → "062400" with LZ → file stores "62400" (leading zero removed)
        assert abs(p._resolve_coord("62400") - 62.4) < 1e-6

    def test_lz_with_leading_zero_in_file(self):
        p = self._make_parser("L", 3, 3)
        # Full 6-digit: "062400" → 062.400 = 62.4
        assert abs(p._resolve_coord("062400") - 62.4) < 1e-6

    def test_tz_3_3_metric(self):
        p = self._make_parser("T", 3, 3)
        # 62.4 mm with TZ → file stores "062" (trailing zeros removed)
        assert abs(p._resolve_coord("062") - 62.0) < 1e-6

    def test_lz_2_4_inch(self):
        p = self._make_parser("L", 2, 4, units="INCH")
        # 1.2345" → "12345" with LZ
        assert abs(p._resolve_coord("12345") - 1.2345) < 1e-6

    def test_explicit_decimal_always_parsed_as_is(self):
        p = self._make_parser("L", 3, 3)
        assert abs(p._resolve_coord("62.4") - 62.4) < 1e-6

    def test_negative_coord(self):
        p = self._make_parser("L", 3, 3)
        assert abs(p._resolve_coord("-062400") - (-62.4)) < 1e-6


# ───────────────────────────────────────────────── full parse tests

class TestParserHeader:
    def test_units_metric_parsed(self):
        _, state = parse("M48\nMETRIC,LZ\n%\nM30")
        assert state.input_units == "MM"
        assert state.zero_suppression == "L"

    def test_units_inch_parsed(self):
        _, state = parse("M48\nINCH,LZ\n%\nM30")
        assert state.input_units == "INCH"

    def test_fmat_version(self):
        _, state = parse("M48\nFMAT,2\nMETRIC,LZ\n%\nM30")
        assert state.fmat_version == 2

    def test_tool_definition(self):
        _, state = parse("M48\nMETRIC,LZ\nT1C0.800\n%\nM30")
        assert 1 in state.tools
        assert abs(state.tools[1].diameter_mm - 0.8) < 1e-6

    def test_tool_def_inch_converts_to_mm(self):
        _, state = parse("M48\nINCH,LZ\nT1C0.031\n%\nM30")
        assert 1 in state.tools
        expected_mm = 0.031 * 25.4
        assert abs(state.tools[1].diameter_mm - expected_mm) < 1e-4


class TestParserDrills:
    def test_basic_drill_metric(self):
        src = """M48
METRIC,LZ
T1C0.800
%
T1
X062400Y060750
M30"""
        parser, state = parse(src)
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert len(drills) == 1
        # X062400 with LZ 3.3: "062400" → 062.400 = 62.4 mm
        assert abs(drills[0].x_mm - 62.4) < 1e-3
        assert abs(drills[0].y_mm - 60.75) < 1e-3

    def test_drill_inch_output_mm(self):
        """Inch file → output in MM (default)."""
        src = """M48
INCH,LZ
T1C0.031
%
T1
X02457Y02392
M30"""
        parser, state = parse(src, output_units="MM")
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert len(drills) == 1
        # X02457 with INCH,LZ,(2,3): total=5, zfill(5)="02457" → "02.457" = 2.457"
        # → mm = 2.457 * 25.4 = 62.4078 mm
        expected_mm = 2.457 * 25.4
        assert abs(drills[0].x_mm - expected_mm) < 0.01
        # Output should be in mm
        assert abs(drills[0].x - drills[0].x_mm) < 1e-6
        assert drills[0].converted is True

    def test_drill_inch_output_inch(self):
        """Inch file → output in INCH."""
        src = """M48
INCH,LZ
T1C0.031
%
T1
X02457Y02392
M30"""
        parser, state = parse(src, output_units="INCH")
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert len(drills) == 1
        # X02457 with INCH,LZ,(2,3): "02.457" = 2.457"
        assert abs(drills[0].x - 2.457) < 0.001
        assert drills[0].output_units == "INCH"

    def test_hint_units_overrides_ambiguous(self):
        """File with no unit declaration + --units hint."""
        src = "M48\nFMAT,2\nT1C0.8\n%\nT1\nX062400Y060750\nM30"
        parser, state = parse(src, hint_units="MM")
        assert state.units_forced is True
        assert state.input_units == "MM"

    def test_multiple_drills(self):
        src = """M48
METRIC,LZ
T1C0.800
%
T1
X062400Y060750
X062400Y077600
X100800Y060750
M30"""
        parser, _ = parse(src)
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert len(drills) == 3

    def test_plating_pth_from_comment(self):
        src = "M48\nMETRIC,LZ\nT1C0.800\n%\n;PTH\nT1\nX050000Y050000\nM30"
        parser, _ = parse(src)
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert drills[0].plating == "PTH"

    def test_plating_npth_from_comment(self):
        src = "M48\nMETRIC,LZ\nT1C0.800\n%\n;NPTH\nT1\nX050000Y050000\nM30"
        parser, _ = parse(src)
        drills = [p for p in parser.primitives if isinstance(p, DrillHit)]
        assert drills[0].plating == "NPTH"


class TestParserAutoDetectCoordFormat:
    def test_autodetect_eagle_metric_tz_uses_3_3_lz(self):
        """drill_1_16.xln: autodetector must pick (3,3) + LZ (pad-left).

        EAGLE writes METRIC,TZ,000.000 following the Excellon spec convention
        where TZ = trailing zeros present = leading zeros suppressed = pad left.
        The code's default KiCad convention (TZ = trailing zeros suppressed =
        pad right) is wrong for this file; the autodetector must detect and
        apply the correct LZ decode direction.
        """
        p = Path(__file__).parent.parent / "data" / "excellon_samples" / "drill_1_16.xln"
        text = p.read_text(encoding="utf-8", errors="replace")

        state = ExcellonState(output_units="MM")
        parser = ExcellonParser(state)
        parser.parse(tokenize_excellon(text))

        drills = [d for d in parser.primitives if isinstance(d, DrillHit)]
        xs = [d.x_mm for d in drills]
        ys = [d.y_mm for d in drills]

        # Correct format and ZS direction
        assert state.coord_format == (3, 3), f"Expected (3,3), got {state.coord_format}"
        assert state.zero_suppression == "L", f"Expected LZ (pad-left), got {state.zero_suppression!r}"

        # Board bounding box must be plausible (roughly 72 × 74 mm for this PCB)
        assert max(xs) - min(xs) < 200, f"Board width {max(xs)-min(xs):.1f} mm — format mismatch?"
        assert max(ys) - min(ys) < 200, f"Board height {max(ys)-min(ys):.1f} mm — format mismatch?"

    def test_autodetect_eagle_t1_corner_holes_correct(self):
        """T1 (3.0 mm) corner mounting holes must land near the PCB corners.

        With correct (3,3) LZ decoding the four T1 holes are at approximately:
          (3.334, 3.334), (72.787, 3.334), (3.334, 74.771), (72.787, 74.771) mm.
        With the old (2,3) TZ decoding, the two near-origin holes were decoded
        as ~33.34 mm instead of ~3.334 mm — 10× too large.
        """
        p = Path(__file__).parent.parent / "data" / "excellon_samples" / "drill_1_16.xln"
        text = p.read_text(encoding="utf-8", errors="replace")

        state = ExcellonState(output_units="MM")
        parser = ExcellonParser(state)
        parser.parse(tokenize_excellon(text))

        t1_holes = [d for d in parser.primitives
                    if isinstance(d, DrillHit) and d.tool_number == 1]
        assert len(t1_holes) == 4, f"Expected 4 T1 holes, got {len(t1_holes)}"

        # Near-origin corner hole(s): X3334 Y3334 → 3.334, 3.334 mm
        t1_xs = sorted(d.x_mm for d in t1_holes)
        t1_ys = sorted(d.y_mm for d in t1_holes)
        tol = 0.01   # ±10 µm
        assert abs(t1_xs[0] - 3.334) < tol, f"Near-origin X wrong: {t1_xs[0]:.4f} mm (expected 3.334 mm)"
        assert abs(t1_ys[0] - 3.334) < tol, f"Near-origin Y wrong: {t1_ys[0]:.4f} mm (expected 3.334 mm)"
        # Far corner
        assert abs(t1_xs[-1] - 72.787) < tol, f"Far-corner X wrong: {t1_xs[-1]:.4f} mm (expected 72.787 mm)"
        assert abs(t1_ys[-1] - 74.771) < tol, f"Far-corner Y wrong: {t1_ys[-1]:.4f} mm (expected 74.771 mm)"

    def test_autodetect_can_be_disabled(self):
        p = Path(__file__).parent.parent / "data" / "excellon_samples" / "drill_1_16.xln"
        text = p.read_text(encoding="utf-8", errors="replace")

        state = ExcellonState(output_units="MM")
        parser = ExcellonParser(state, auto_detect_coord_format=False)
        parser.parse(tokenize_excellon(text))

        drills = [d for d in parser.primitives if isinstance(d, DrillHit)]
        xs = [d.x_mm for d in drills]
        assert state.coord_format == (3, 3)
        assert max(xs) > 500

    def test_user_hint_disables_autodetect(self):
        p = Path(__file__).parent.parent / "data" / "excellon_samples" / "drill_1_16.xln"
        text = p.read_text(encoding="utf-8", errors="replace")

        state = ExcellonState(output_units="MM")
        parser = ExcellonParser(
            state,
            hint_coord_format="3.3",
            auto_detect_coord_format=True,
            source_text=text,
        )
        parser.parse(tokenize_excellon(text))

        drills = [d for d in parser.primitives if isinstance(d, DrillHit)]
        xs = [d.x_mm for d in drills]
        assert state.coord_format == (3, 3)
        assert max(xs) > 500


class TestParserSlots:
    def test_slot_g85_full_form(self):
        src = """M48
METRIC,LZ
T1C1.000
%
T1
X050000Y100000G85X150000Y100000
M30"""
        parser, _ = parse(src)
        slots = [p for p in parser.primitives if isinstance(p, SlotG85)]
        assert len(slots) == 1
        s = slots[0]
        assert abs(s.x_start_mm - 50.0) < 1e-3
        assert abs(s.x_end_mm - 150.0) < 1e-3
        assert abs(s.y_start_mm - 100.0) < 1e-3

    def test_slot_g85_short_form(self):
        src = "M48\nMETRIC,LZ\nT1C1.000\n%\nT1\nX050000Y100000\nG85X150000Y100000\nM30"
        parser, _ = parse(src)
        # The X050000Y100000 line is parsed as drill, G85 is a separate slot from current pos
        slots = [p for p in parser.primitives if isinstance(p, SlotG85)]
        assert len(slots) == 1


class TestParserRouting:
    def test_linear_route(self):
        src = """M48
METRIC,LZ
T1C2.000
%
T1
G00X010000Y010000
G01X090000Y010000
G05
M30"""
        parser, _ = parse(src)
        routes = [p for p in parser.primitives if isinstance(p, RouteSegment)]
        assert len(routes) == 1
        assert routes[0].segment_type == "line"

    def test_arc_route_cw(self):
        src = """M48
METRIC,LZ
T1C2.000
%
T1
G00X010000Y010000
G02X090000Y010000A40000
G05
M30"""
        parser, _ = parse(src)
        arcs = [p for p in parser.primitives if isinstance(p, RouteSegment) and "arc" in p.segment_type]
        assert len(arcs) == 1
        assert arcs[0].segment_type == "arc_cw"
        assert arcs[0].arc_radius_mm is not None

    def test_arc_route_ccw(self):
        src = """M48
METRIC,LZ
T1C2.000
%
T1
G00X010000Y010000
G03X090000Y010000A40000
G05
M30"""
        parser, _ = parse(src)
        arcs = [p for p in parser.primitives if isinstance(p, RouteSegment) and "arc" in p.segment_type]
        assert len(arcs) == 1
        assert arcs[0].segment_type == "arc_ccw"


class TestAmbiguousUnits:
    def test_ambiguous_defaults_to_mm_with_warning(self):
        """No METRIC/INCH in header → units_ambiguous=True, defaults to MM."""
        src = "M48\nFMAT,2\nT1C0.8\n%\nT1\nX050000Y050000\nM30"
        _, state = parse(src)
        assert state.units_ambiguous is True
        assert state.input_units == "MM"

