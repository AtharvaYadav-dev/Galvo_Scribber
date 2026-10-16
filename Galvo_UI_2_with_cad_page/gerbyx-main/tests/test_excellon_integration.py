"""Integration tests for the Excellon pipeline."""
import pytest
from pathlib import Path

from gerbyx.excellon.state import ExcellonState, INCH_TO_MM
from gerbyx.excellon.tokenizer import tokenize_excellon
from gerbyx.excellon.parser import ExcellonParser
from gerbyx.excellon.processor import ExcellonProcessor
from gerbyx.excellon.primitives import DrillHit, SlotG85, RouteSegment
from gerbyx.excellon.detector import detect_format
from gerbyx.dispatcher import process_file

DATA_DIR = Path(__file__).parent.parent / "data" / "excellon_samples"


def full_pipeline(text, output_units="MM", hint_units=None, arc_tol=0.01, max_segs=128):
    state = ExcellonState(
        output_units=output_units,
        arc_tolerance_mm=arc_tol,
        max_arc_segments=max_segs,
    )
    parser = ExcellonParser(state, hint_units=hint_units)
    parser.parse(tokenize_excellon(text))
    proc = ExcellonProcessor(state)
    proc.process(parser.primitives)
    return parser, state, proc, proc.geometries


class TestDetector:
    def test_detects_metric_drl_as_excellon(self):
        text = "M48\nMETRIC,LZ\nT1C0.800\n%\nT1\nX050000Y050000\nM30"
        r = detect_format(text)
        assert r.format == "excellon"
        assert r.confidence > 0.3

    def test_detects_gerber_as_gerber(self):
        text = "%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,1.0*%\nD10*\nX10000Y10000D03*\nM02*"
        r = detect_format(text)
        assert r.format == "gerber"


class TestInchToMmConversion:
    def test_inch_file_outputs_mm_by_default(self):
        src = """M48
INCH,LZ
T1C0.031
%
T1
X02457Y02392
M30"""
        parser, state, _, _ = full_pipeline(src, output_units="MM")
        assert state.converted is True
        d = [p for p in parser.primitives if isinstance(p, DrillHit)][0]
        assert abs(d.diameter_mm - (0.031 * INCH_TO_MM)) < 0.001

    def test_inch_file_same_coords_as_metric_equivalent(self):
        x_mm = 62.4
        y_mm = 60.75
        x_inch = x_mm / INCH_TO_MM
        y_inch = y_mm / INCH_TO_MM
        x_enc = f"{int(round(x_inch * 1000))}"
        y_enc = f"{int(round(y_inch * 1000))}"
        inch_src = f"M48\nINCH,LZ\nT1C0.031\n%\nT1\nX{x_enc}Y{y_enc}\nM30"
        parser_i, _, _, _ = full_pipeline(inch_src, output_units="MM")
        d = [p for p in parser_i.primitives if isinstance(p, DrillHit)][0]
        assert abs(d.x_mm - x_mm) < 0.1
        assert abs(d.y_mm - y_mm) < 0.1

    def test_coord_format_override_changes_scale(self):
        src = "M48\nINCH,LZ\nT1C0.031\n%\nT1\nX02457Y02392\nM30"
        d_default = process_file(src, output_units="MM", format_hint="excellon").primitives[0]
        d_forced = process_file(
            src,
            output_units="MM",
            format_hint="excellon",
            hint_coord_format="2.4",
        ).primitives[0]
        assert abs(d_default.x_mm - (2.457 * INCH_TO_MM)) < 0.01
        assert abs(d_forced.x_mm - (0.2457 * INCH_TO_MM)) < 0.01


class TestSlotAndRoute:
    def test_slot_g85_geometry(self):
        src = """M48
METRIC,LZ
T1C1.000
%
T1
X050000Y100000G85X150000Y100000
M30"""
        parser, _, _, geoms = full_pipeline(src)
        slots = [p for p in parser.primitives if isinstance(p, SlotG85)]
        assert len(slots) == 1
        assert len(geoms) == 1

    def test_route_line_geometry(self):
        src = """M48
METRIC,LZ
T1C2.000
%
T1
G00X010000Y010000
G01X090000Y010000
G05
M30"""
        parser, _, _, geoms = full_pipeline(src)
        routes = [p for p in parser.primitives if isinstance(p, RouteSegment)]
        assert len(routes) == 1
        assert routes[0].segment_type == "line"
        assert len(geoms) == 1


class TestDispatcher:
    def test_dispatcher_routes_excellon(self):
        src = "M48\nMETRIC,LZ\nT1C0.800\n%\nT1\nX050000Y050000\nM30"
        result = process_file(src, output_units="MM", format_hint="excellon")
        assert result.format == "excellon"
        assert len(result.geometries) > 0

    def test_dispatcher_routes_gerber(self):
        src = "%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,1.0*%\nD10*\nX10000Y10000D03*\nM02*"
        result = process_file(src, format_hint="gerber")
        assert result.format == "gerber"

    @pytest.mark.skipif(not (DATA_DIR / "kicad_inch_drill.drl").exists(), reason="data file missing")
    def test_real_kicad_inch_file_outputs_mm(self):
        result = process_file(DATA_DIR / "kicad_inch_drill.drl", output_units="MM")
        assert result.format == "excellon"
        assert len(result.primitives) > 0
        for p in result.primitives:
            assert p.output_units == "MM"


class TestRealUserExcellonFile:
    @pytest.mark.skipif(not (DATA_DIR / "drill_1_16.xln").exists(), reason="data file missing")
    def test_drill_1_16_file_parses(self):
        result = process_file(DATA_DIR / "drill_1_16.xln", output_units="MM", format_hint="excellon")

        assert result.format == "excellon"
        assert len(result.primitives) == len(result.geometries)
        assert len(result.primitives) > 400

        tool_numbers = {p.tool_number for p in result.primitives}
        assert len(tool_numbers) == 13
        assert 1 in tool_numbers
        assert 13 in tool_numbers

        first = result.primitives[0]
        assert isinstance(first, DrillHit)
        assert first.tool_number == 1
        assert abs(first.diameter_mm - 3.0) < 1e-9

