"""Tests for Excellon tokenizer."""
import pytest
from gerbyx.excellon.tokenizer import (
    tokenize_excellon,
    TK_HEADER_START, TK_HEADER_END, TK_UNITS, TK_FMAT,
    TK_TOOL_DEF, TK_TOOL_SEL, TK_DRILL, TK_SLOT_G85,
    TK_ROUTE_G00, TK_ROUTE_G01, TK_ROUTE_G02, TK_ROUTE_G03,
    TK_DRILL_MODE, TK_PROG_END, TK_COMMENT,
)


def tokens(text):
    return list(tokenize_excellon(text))


class TestHeaderTokens:
    def test_m48_header_start(self):
        toks = tokens("M48")
        assert toks[0][0] == TK_HEADER_START

    def test_percent_header_end(self):
        toks = tokens("M48\n%")
        assert any(t[0] == TK_HEADER_END for t in toks)

    def test_m95_header_end(self):
        toks = tokens("M95")
        assert toks[0][0] == TK_HEADER_END

    def test_metric_lz(self):
        toks = tokens("METRIC,LZ")
        assert toks[0][0] == TK_UNITS
        assert toks[0][2]["units"] == "METRIC"
        assert toks[0][2]["zero_suppression"] == "L"

    def test_inch_tz(self):
        toks = tokens("INCH,TZ")
        assert toks[0][0] == TK_UNITS
        assert toks[0][2]["units"] == "INCH"
        assert toks[0][2]["zero_suppression"] == "T"

    def test_metric_with_format_string(self):
        toks = tokens("METRIC,LZ,000.000")
        assert toks[0][0] == TK_UNITS
        assert toks[0][2]["coord_format"] == (3, 3)

    def test_fmat2(self):
        toks = tokens("FMAT,2")
        assert toks[0][0] == TK_FMAT
        assert toks[0][2]["version"] == 2

    def test_fmat1(self):
        toks = tokens("FMAT,1")
        assert toks[0][0] == TK_FMAT
        assert toks[0][2]["version"] == 1


class TestToolTokens:
    def test_tool_def_simple(self):
        toks = tokens("T1C0.800")
        assert toks[0][0] == TK_TOOL_DEF
        assert toks[0][2]["tool"] == 1
        assert toks[0][2]["diameter"] == "0.800"

    def test_tool_def_with_feed_speed(self):
        toks = tokens("T2C1.000F200S3000")
        assert toks[0][0] == TK_TOOL_DEF
        assert toks[0][2]["feed"] == 200.0
        assert toks[0][2]["speed"] == 3000

    def test_tool_selection(self):
        toks = tokens("T3")
        assert toks[0][0] == TK_TOOL_SEL
        assert toks[0][2]["tool"] == 3


class TestCoordTokens:
    def test_drill_xy(self):
        toks = tokens("X062400Y060750")
        assert toks[0][0] == TK_DRILL
        assert toks[0][2]["x"] == "062400"
        assert toks[0][2]["y"] == "060750"

    def test_drill_decimal(self):
        toks = tokens("X62.4Y60.75")
        assert toks[0][0] == TK_DRILL
        assert toks[0][2]["x"] == "62.4"

    def test_slot_g85_full(self):
        toks = tokens("X050000Y100000G85X150000Y100000")
        assert toks[0][0] == TK_SLOT_G85
        f = toks[0][2]
        assert f["x1"] == "050000"
        assert f["x2"] == "150000"
        assert f["from_current"] is False

    def test_slot_g85_short(self):
        toks = tokens("G85X150000Y100000")
        assert toks[0][0] == TK_SLOT_G85
        f = toks[0][2]
        assert f["x2"] == "150000"
        assert f["from_current"] is True


class TestRoutingTokens:
    def test_g00_reposition(self):
        toks = tokens("G00X010000Y010000")
        assert toks[0][0] == TK_ROUTE_G00
        assert toks[0][2]["x"] == "010000"

    def test_g01_linear(self):
        toks = tokens("G01X090000Y010000")
        assert toks[0][0] == TK_ROUTE_G01

    def test_g02_arc_cw_a_style(self):
        toks = tokens("G02X040000Y040000A25000")
        assert toks[0][0] == TK_ROUTE_G02
        assert toks[0][2]["a"] == "25000"

    def test_g03_arc_ccw_ij_style(self):
        toks = tokens("G03X040000Y040000I10000J0")
        assert toks[0][0] == TK_ROUTE_G03
        assert toks[0][2]["i"] == "10000"
        assert toks[0][2]["j"] == "0"

    def test_g05_drill_mode(self):
        toks = tokens("G05")
        assert toks[0][0] == TK_DRILL_MODE


class TestMiscTokens:
    def test_comment(self):
        toks = tokens(";This is a comment")
        assert toks[0][0] == TK_COMMENT
        assert "comment" in toks[0][2]["text"].lower()

    def test_m30_prog_end(self):
        toks = tokens("M30")
        assert toks[0][0] == TK_PROG_END

    def test_empty_lines_skipped(self):
        toks = tokens("\n\n  \nT1\n\n")
        assert len(toks) == 1

