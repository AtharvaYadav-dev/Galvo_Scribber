"""Tests for Excellon coordinate format auto-detector and its integration."""
from pathlib import Path


from gerbyx.excellon.coord_format_detector import detect_coord_format
from gerbyx.dispatcher import process_file
from gerbyx.excellon.primitives import DrillHit

DATA = Path(__file__).parent.parent / "data" / "excellon_samples"


# ──────────────────────────────────────────────────── unit tests for detector

class TestDetectCoordFormat:

    def test_eagle_metric_tz_wrong_declared(self):
        """drill_1_16.xln declares METRIC,TZ,000.000 (3.3/TZ convention).
        EAGLE follows the Excellon spec: TZ = trailing zeros present = leading
        zeros suppressed = pad LEFT to decode.  The autodetector must discover
        that (3,3) with pad-left (LZ decode) gives plausible PCB coordinates,
        and return that combination with a warning about the ZS direction change.
        """
        text = (DATA / "drill_1_16.xln").read_text(encoding="utf-8", errors="replace")
        fmt, warning, reason, best_zs = detect_coord_format(text)
        assert fmt == (3, 3), f"Expected (3,3), got {fmt}. {reason}"
        assert best_zs == "L", f"Expected LZ (pad-left) decoding, got {best_zs!r}"
        assert warning is not None, "Expected a mismatch warning (ZS direction changed)"
        assert "TZ" in warning or "LZ" in warning, f"Warning should mention TZ/LZ: {warning}"

    def test_eagle_like_mixed_4_5_digits_does_not_select_4_2(self):
        """Regression: Eagle-like 4/5-digit coords should not drift to 4.2.

        The dataset mirrors values like:
        2540, 41005, 40323, 2223
        which are plausible with LZ decode as ~2.540/41.005 etc.
        """
        src = (
            "M48\n"
            "METRIC,TZ,000.000\n"
            "T1C0.350\n"
            "%\n"
            "T1\n"
            "X2540Y41005\n"
            "X40323Y2223\n"
            "X45402Y45402\n"
            "M30\n"
        )

        fmt, warning, reason, best_zs = detect_coord_format(src)
        assert best_zs == "L", f"Expected LZ decode, got {best_zs!r}. {reason}"
        assert fmt != (4, 2), f"4.2 must not win for this Eagle-like pattern. {reason}"
        assert fmt in {(2, 3), (3, 3)}, f"Unexpected format {fmt}. {reason}"

    def test_kicad_metric_lz_correct(self):
        """kicad_metric_drill.drl: METRIC,LZ, no explicit digit format → (3,3), no warning."""
        text = (DATA / "kicad_metric_drill.drl").read_text(encoding="utf-8", errors="replace")
        fmt, warning, reason, best_zs = detect_coord_format(text)
        assert fmt == (3, 3), f"Expected (3,3), got {fmt}. {reason}"
        assert warning is None, f"Unexpected warning: {warning}"

    def test_kicad_inch_lz(self):
        """kicad_inch_drill.drl: INCH,LZ → best format should be (2,3)."""
        text = (DATA / "kicad_inch_drill.drl").read_text(encoding="utf-8", errors="replace")
        fmt, warning, reason, best_zs = detect_coord_format(text)
        assert fmt == (2, 3), f"Expected (2,3), got {fmt}. {reason}"

    def test_decimal_coords_skipped(self):
        """Files with all-decimal coordinates → detection skipped, no warning."""
        src = (
            "M48\nMETRIC\nT1C0.8\n%\n"
            "T1\nX73.114Y-67.536\nX86.368Y-55.142\nM30\n"
        )
        fmt, warning, reason, best_zs = detect_coord_format(src)
        assert warning is None
        assert "decimal" in reason.lower()

    def test_ambiguous_units_no_crash(self):
        """File with no unit declaration must not raise, returns a format."""
        text = (DATA / "ambiguous_units.drl").read_text(encoding="utf-8", errors="replace")
        fmt, warning, reason, best_zs = detect_coord_format(text)
        assert fmt is not None

    def test_reason_contains_all_candidates(self):
        """reason string must list all five candidate formats."""
        text = (DATA / "drill_1_16.xln").read_text(encoding="utf-8", errors="replace")
        _, _, reason, _ = detect_coord_format(text)
        for expected in ("2.3", "2.4", "3.3", "3.4", "4.2"):
            assert expected in reason, f"Missing {expected} in reason: {reason}"


# ──────────────────────────────────────────────────── integration via dispatcher

class TestDispatcherIntegration:

    def test_eagle_xln_bbox_plausible(self):
        """Full pipeline on drill_1_16.xln: bbox must be < 200 mm after auto-correction."""
        result = process_file(
            str(DATA / "drill_1_16.xln"),
            format_hint="excellon",
            output_units="MM",
        )
        drills = [p for p in result.primitives if isinstance(p, DrillHit)]
        assert drills, "No DrillHit primitives parsed"
        xs = [d.x_mm for d in drills]
        ys = [d.y_mm for d in drills]
        width  = max(xs) - min(xs)
        height = max(ys) - min(ys)
        assert width  < 200, f"Board width {width:.1f} mm — format mismatch?"
        assert height < 200, f"Board height {height:.1f} mm — format mismatch?"

    def test_eagle_xln_diameters_correct(self):
        """Drill diameters for drill_1_16.xln must remain correct (0.35 … 3.00 mm)."""
        result = process_file(
            str(DATA / "drill_1_16.xln"),
            format_hint="excellon",
            output_units="MM",
        )
        drills = [p for p in result.primitives if isinstance(p, DrillHit)]
        dias = {round(d.diameter_mm, 3) for d in drills}
        assert 0.35 in dias, f"Expected T13 (0.35 mm) in diameters: {sorted(dias)}"
        assert 3.0  in dias, f"Expected T1  (3.00 mm) in diameters: {sorted(dias)}"

    def test_kicad_metric_unchanged(self):
        """kicad_metric_drill.drl: auto-detection must not change the correct (3,3) format."""
        result = process_file(
            str(DATA / "kicad_metric_drill.drl"),
            format_hint="excellon",
            output_units="MM",
        )
        drills = [p for p in result.primitives if isinstance(p, DrillHit)]
        t1 = next(d for d in drills if d.tool_number == 1)
        # X062400Y060750 with METRIC,LZ,(3,3) → 62.4 mm, 60.75 mm
        assert abs(t1.x_mm - 62.4)  < 0.1, f"x_mm={t1.x_mm:.4f}"
        assert abs(t1.y_mm - 60.75) < 0.1, f"y_mm={t1.y_mm:.4f}"

    def test_kicad_inch_unchanged(self):
        """kicad_inch_drill.drl: coordinates must resolve correctly after auto-detection."""
        result = process_file(
            str(DATA / "kicad_inch_drill.drl"),
            format_hint="excellon",
            output_units="MM",
        )
        drills = [p for p in result.primitives if isinstance(p, DrillHit)]
        t1 = next(d for d in drills if d.tool_number == 1)
        # X02457Y02392 with INCH,LZ,(2,3) → "02457" pad-left-to-5 → "02.457" = 2.457"
        # → 2.457 × 25.4 = 62.4078 mm  (confirmed by check_inch_drill.py in repo)
        expected_x_mm = 2.457 * 25.4
        expected_y_mm = 2.392 * 25.4
        assert abs(t1.x_mm - expected_x_mm) < 0.1, f"x_mm={t1.x_mm:.4f} expected {expected_x_mm:.4f}"
        assert abs(t1.y_mm - expected_y_mm) < 0.1, f"y_mm={t1.y_mm:.4f} expected {expected_y_mm:.4f}"

    def test_user_hint_not_overridden(self):
        """User-supplied hint_coord_format must always win over auto-detection."""
        result = process_file(
            str(DATA / "drill_1_16.xln"),
            format_hint="excellon",
            output_units="MM",
            hint_coord_format="3.3",   # force the wrong format on purpose
        )
        drills = [p for p in result.primitives if isinstance(p, DrillHit)]
        xs = [d.x_mm for d in drills]
        # With forced 3.3 the board is ~880 mm wide
        assert max(xs) > 500, "User hint 3.3 should produce large (wrong) coords"

