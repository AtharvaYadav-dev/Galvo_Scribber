"""
Excellon parser: state machine HEADER -> DRILL_BODY -> ROUTE_BODY.

Coordinate zero-suppression is resolved here where full context (units,
format, suppression mode) is available.
"""
from __future__ import annotations
import math
import re
from typing import Any, Dict, Generator, List, Optional, Tuple

from ..logger import warning, debug, info
from .state import ExcellonState, ToolDefinition, INCH_TO_MM, MM_TO_INCH
from .primitives import DrillHit, SlotG85, RouteSegment
from .tokenizer import (
    TK_HEADER_START, TK_HEADER_END, TK_UNITS, TK_FMAT,
    TK_TOOL_DEF, TK_TOOL_SEL, TK_DRILL, TK_SLOT_G85,
    TK_ROUTE_G00, TK_ROUTE_G01, TK_ROUTE_G02, TK_ROUTE_G03,
    TK_DRILL_MODE, TK_ABS_MODE, TK_INC_MODE, TK_REPEAT,
    TK_PROG_END, TK_FILE_END, TK_COMMENT, TK_UNKNOWN,
)

# Vendor plating keywords found in comments
_PTH_KEYWORDS  = re.compile(r'\bPTH\b',  re.IGNORECASE)
_NPTH_KEYWORDS = re.compile(r'\bNPTH\b', re.IGNORECASE)
_VIA_KEYWORDS  = re.compile(r'\bVIA\b',  re.IGNORECASE)


def _parse_coord_format_hint(value: Any) -> Tuple[int, int]:
    """Parse coord format hints like "2.3", "23", (2, 3)."""
    if isinstance(value, tuple) and len(value) == 2:
        int_d, dec_d = int(value[0]), int(value[1])
    elif isinstance(value, str):
        v = value.strip()
        m = re.match(r"^(\d)\s*[.,xX:]\s*(\d)$", v)
        if m:
            int_d, dec_d = int(m.group(1)), int(m.group(2))
        elif re.match(r"^\d{2}$", v):
            int_d, dec_d = int(v[0]), int(v[1])
        else:
            raise ValueError(
                f"Invalid coord format hint '{value}'. Use forms like '2.3', '23', or (2,3)."
            )
    else:
        raise ValueError(
            f"Invalid coord format hint type: {type(value).__name__}. "
            "Use string '2.3'/'23' or tuple (2,3)."
        )

    if int_d <= 0 or dec_d <= 0:
        raise ValueError("Coordinate format digits must be positive")
    return int_d, dec_d


class ExcellonParser:
    """
    Parses an Excellon token stream and emits typed primitives.

    Usage::

        state = ExcellonState(output_units="MM")
        parser = ExcellonParser(state, hint_units=None)
        parser.parse(tokenize_excellon(source))
        for p in parser.primitives:
            ...
    """

    def __init__(
        self,
        state: ExcellonState,
        hint_units: Optional[str] = None,
        hint_coord_format: Optional[Any] = None,
        auto_detect_coord_format: bool = True,
        source_text: Optional[str] = None,
    ):
        self.state = state
        self._primitives: List = []
        self._last_drill: Optional[Tuple[float, float]] = None   # for R-repeat
        self._auto_detect_coord_format = auto_detect_coord_format
        self._source_text = source_text

        # If caller supplied a forced unit override, apply it immediately
        if hint_units:
            self.state.input_units = hint_units.upper()
            self.state.units_forced = True
            debug(lambda: f"Excellon units forced by caller: {self.state.input_units}")

        # Optional forced coordinate format override (e.g. "2.3", "3.3").
        if hint_coord_format is not None:
            self.state.coord_format = _parse_coord_format_hint(hint_coord_format)
            self.state.coord_format_forced = True
            debug(lambda: f"Excellon coord format forced by caller: {self.state.coord_format}")

    # ------------------------------------------------------------------ public

    @property
    def primitives(self) -> List:
        return self._primitives

    def parse(
        self,
        tokens: Generator[Tuple[str, str, Dict[str, Any]], None, None],
        source_text: Optional[str] = None,
    ) -> None:
        # Optional KiCad-style autodetection. It is skipped when user already
        # forced a coord format via hint_coord_format.
        token_iter = tokens
        if self._auto_detect_coord_format and not self.state.coord_format_forced:
            detect_text = source_text or self._source_text
            if not detect_text:
                # Backward-compatible path: caller may pass only token stream.
                # Materialize tokens once so we can reconstruct text for detection,
                # then parse from the buffered token list.
                token_list = list(tokens)
                token_iter = iter(token_list)
                detect_text = "\n".join(raw for _, raw, _ in token_list)
            if detect_text:
                from .coord_format_detector import detect_coord_format

                best_fmt, warn_msg, reason, best_zs = detect_coord_format(detect_text)
                debug(lambda: f"Coord format detection: {reason}")
                if warn_msg:
                    warning(warn_msg)
                if best_fmt is not None:
                    self.state.coord_format = best_fmt
                    # Reuse the existing "forced" behavior so header-declared
                    # format does not overwrite the detected format.
                    self.state.coord_format_forced = True
                    debug(lambda: f"Auto-selected Excellon coord format: {best_fmt}")
                # Always apply the detected ZS direction and lock it so that
                # the header UNITS line cannot overwrite it.  This is the fix
                # for EAGLE files that declare METRIC,TZ but whose coordinates
                # are actually encoded with leading-zero suppression (pad left).
                self.state.zero_suppression = best_zs
                self.state.zero_suppression_forced = True
                debug(lambda: f"Auto-selected Excellon zero-suppression: {best_zs}")
            else:
                debug(lambda: "Coord format autodetect enabled but no source_text provided")

        info("Starting Excellon parsing")

        for kind, raw, fields in token_iter:
            if self.state.program_ended:
                break

            if kind == TK_COMMENT:
                self._handle_comment(fields, raw)
            elif kind == TK_HEADER_START:
                self.state.in_header = True
                debug(lambda: "Excellon header start (M48)")
            elif kind == TK_HEADER_END:
                self._finalize_header()
            elif kind == TK_UNITS:
                self._handle_units(fields, raw)
            elif kind == TK_FMAT:
                self._handle_fmat(fields)
            elif kind == TK_TOOL_DEF:
                self._handle_tool_def(fields, raw)
            elif kind == TK_TOOL_SEL:
                self._handle_tool_sel(fields, raw)
            elif kind == TK_DRILL:
                self._handle_drill(fields, raw)
            elif kind == TK_SLOT_G85:
                self._handle_slot_g85(fields, raw)
            elif kind == TK_ROUTE_G00:
                self._handle_route_g00(fields, raw)
            elif kind == TK_ROUTE_G01:
                self._handle_route_g01(fields, raw)
            elif kind == TK_ROUTE_G02:
                self._handle_route_arc(fields, raw, clockwise=True)
            elif kind == TK_ROUTE_G03:
                self._handle_route_arc(fields, raw, clockwise=False)
            elif kind == TK_DRILL_MODE:
                self.state.in_route_mode = False
                debug(lambda: "Returned to drill mode (G05)")
            elif kind == TK_ABS_MODE:
                self.state.coord_mode = "absolute"
            elif kind == TK_INC_MODE:
                self.state.coord_mode = "incremental"
            elif kind == TK_REPEAT:
                self._handle_repeat(fields, raw)
            elif kind in (TK_PROG_END, TK_FILE_END):
                self.state.program_ended = True
                debug(lambda: "Excellon program end")
            elif kind == TK_UNKNOWN:
                debug(lambda: f"Unknown Excellon token: {fields.get('text', '')!r}")

        # Post-parse: warn if units never declared
        if self.state.input_units is None and not self.state.units_forced:
            self.state.units_ambiguous = True
            warning(
                "Excellon file has no unit declaration (INCH/METRIC). "
                "Assuming MM. Use --units to override."
            )
            self.state.input_units = "MM"

        info(f"Excellon parsing complete: {len(self._primitives)} primitives")

    # --------------------------------------------------------------- header

    def _finalize_header(self) -> None:
        self.state.in_header = False
        debug(lambda: (
            f"Excellon header end — units={self.state.input_units}, "
            f"zs={self.state.zero_suppression}, fmt={self.state.coord_format}, "
            f"fmat={self.state.fmat_version}"
        ))

    def _handle_units(self, fields: Dict, raw: str) -> None:
        units_raw = fields["units"]  # "METRIC" or "INCH"
        # Normalise: "METRIC" → "MM", "INCH" stays "INCH"
        units = "MM" if units_raw.upper() in ("METRIC", "MM") else "INCH"
        if self.state.units_forced:
            warning(
                f"File declares {units_raw} but --units override is active; "
                f"using {self.state.input_units}"
            )
            # Still apply zero_suppression and coord_format from the line
        else:
            self.state.input_units = units
        if "zero_suppression" in fields:
            if self.state.zero_suppression_forced:
                # Autodetector already determined the correct ZS direction;
                # do not let the header overwrite it.
                if fields["zero_suppression"] != self.state.zero_suppression:
                    warning(
                        f"File declares {'LZ' if fields['zero_suppression'] == 'L' else 'TZ'} "
                        f"zero-suppression but autodetected direction "
                        f"({'LZ' if self.state.zero_suppression == 'L' else 'TZ'}) is active; "
                        f"keeping autodetected value."
                    )
            else:
                self.state.zero_suppression = fields["zero_suppression"]
        if "coord_format" in fields:
            if self.state.coord_format_forced:
                if fields["coord_format"] != self.state.coord_format:
                    warning(
                        f"File declares coord format {fields['coord_format']} but override is active; "
                        f"using {self.state.coord_format}"
                    )
            else:
                self.state.coord_format = fields["coord_format"]
        debug(lambda: (
            f"Units set: {self.state.input_units}, ZS={self.state.zero_suppression}, "
            f"fmt={self.state.coord_format}"
        ))

    def _handle_fmat(self, fields: Dict) -> None:
        self.state.fmat_version = fields["version"]
        # FMAT,2 modern default zero suppression is LZ (leading suppressed)
        if self.state.fmat_version == 2:
            if self.state.zero_suppression == "T":   # only if not explicitly set
                pass   # keep whatever was set; default "L" is set in state.py
        debug(lambda: f"FMAT version: {self.state.fmat_version}")

    def _handle_comment(self, fields: Dict, raw: str) -> None:
        text = fields.get("text", "")
        # Detect vendor plating hints in comments
        if _NPTH_KEYWORDS.search(text):
            self.state.current_plating_hint = "NPTH"
            debug(lambda: "Plating hint: NPTH")
        elif _PTH_KEYWORDS.search(text):
            self.state.current_plating_hint = "PTH"
            debug(lambda: "Plating hint: PTH")
        elif _VIA_KEYWORDS.search(text):
            self.state.current_plating_hint = "VIA"
            debug(lambda: "Plating hint: VIA")

    # --------------------------------------------------------------- tooling

    def _handle_tool_def(self, fields: Dict, raw: str) -> None:
        tool_n = fields["tool"]
        dia_raw = fields["diameter"]
        # Diameter in the tool definition is always explicit (has decimal or not)
        # We parse it as a plain float (tool diameters always have explicit point
        # in practice; if not, treat as input units value directly)
        dia_input = float(dia_raw)
        # Convert to both canonical forms
        if self.state.input_units == "INCH":
            dia_mm   = dia_input * INCH_TO_MM
            dia_inch = dia_input
        else:
            dia_mm   = dia_input
            dia_inch = dia_input * MM_TO_INCH

        tool = ToolDefinition(
            number=tool_n,
            diameter_input=dia_input,
            diameter_mm=dia_mm,
            diameter_inch=dia_inch,
            feed_rate=fields.get("feed"),
            spindle_speed=fields.get("speed"),
            retract_rate=fields.get("retract"),
            max_depth=fields.get("depth"),
            plating=self.state.current_plating_hint,
        )
        self.state.tools[tool_n] = tool
        debug(lambda: f"Tool T{tool_n}: dia={dia_mm:.4f}mm plating={tool.plating}")

    def _handle_tool_sel(self, fields: Dict, raw: str) -> None:
        tool_n = fields["tool"]
        if tool_n == 0:
            self.state.current_tool = None
            self.state.in_route_mode = False
            debug(lambda: "Tool T00: deselect / end routing")
            return
        if tool_n not in self.state.tools:
            warning(f"Tool T{tool_n} used but never defined — diameter unknown")
        self.state.current_tool = tool_n
        debug(lambda: f"Selected T{tool_n}")

    # --------------------------------------------------------------- coordinate resolution

    def _resolve_coord(self, raw: Optional[str]) -> Optional[float]:
        """
        Convert a raw coordinate string to float in INPUT units.

        Rules:
        - If the string contains '.': parse directly as float.
        - Otherwise apply zero-suppression + coord_format.
          LZ (leading zeros suppressed): pad LEFT  to total digits.
          TZ (trailing zeros suppressed): pad RIGHT to total digits.
        """
        if raw is None:
            return None
        if "." in raw:
            return float(raw)

        sign = 1
        s = raw
        if s.startswith("+"):
            s = s[1:]
        elif s.startswith("-"):
            sign = -1
            s = s[1:]

        int_d, dec_d = self.state.effective_coord_format()
        total = int_d + dec_d

        if self.state.zero_suppression == "L":
            # Leading zeros suppressed → pad LEFT
            s = s.zfill(total)
        else:
            # Trailing zeros suppressed → pad RIGHT
            s = s.ljust(total, "0")

        # Insert decimal point
        int_part = s[:int_d]
        dec_part = s[int_d:]
        value = float(f"{int_part}.{dec_part}")
        return value * sign

    def _resolve_xy(
        self,
        raw_x: Optional[str],
        raw_y: Optional[str],
    ) -> Tuple[float, float]:
        """
        Resolve raw X/Y strings to absolute coordinates in INPUT units.
        Missing axis keeps the current position.
        """
        x = self._resolve_coord(raw_x)
        y = self._resolve_coord(raw_y)

        if self.state.coord_mode == "incremental":
            if x is not None:
                x = self.state.current_x + x
            if y is not None:
                y = self.state.current_y + y

        cx = x if x is not None else self.state.current_x
        cy = y if y is not None else self.state.current_y
        return cx, cy

    def _tool_info(self) -> Tuple[int, float, float, float, Optional[float], Optional[int]]:
        """Return (tool_n, dia_mm, dia_out, dia_input, feed, speed) for current tool."""
        tool_n = self.state.current_tool or 0
        tdef = self.state.current_tool_def()
        if tdef is None:
            warning(f"No tool selected / tool T{tool_n} undefined — using 0 diameter")
            return tool_n, 0.0, 0.0, 0.0, None, None
        dia_mm  = tdef.diameter_mm
        dia_out = self.state.to_output(dia_mm)
        return tool_n, dia_mm, dia_out, tdef.diameter_input, tdef.feed_rate, tdef.spindle_speed

    def _make_meta_base(
        self, dia_mm: float, dia_out: float, plating: str, raw: str,
        feed: Optional[float], speed: Optional[int],
    ) -> Dict:
        """Common metadata fields shared across all primitive types."""
        return {
            "plating": plating,
            "input_units": self.state.input_units or "MM",
            "output_units": self.state.output_units,
            "converted": self.state.converted,
            "conversion_factor": self.state.conversion_factor,
            "source_cmd": raw.strip(),
            "diameter_mm": dia_mm,
            "diameter_out": dia_out,
            "feed_rate": feed,
            "spindle_speed": speed,
        }

    # --------------------------------------------------------------- drill

    def _handle_drill(self, fields: Dict, raw: str) -> None:
        if self.state.in_route_mode:
            # In route mode a bare XY line is treated as G01 (linear cut)
            self._handle_route_g01(fields, raw)
            return

        x_in, y_in = self._resolve_xy(fields.get("x"), fields.get("y"))
        self.state.current_x = x_in
        self.state.current_y = y_in

        tool_n, dia_mm, dia_out, _, feed, speed = self._tool_info()
        plating = self._current_plating(tool_n)

        x_mm = self.state.to_mm(x_in)
        y_mm = self.state.to_mm(y_in)
        x_out = self.state.input_to_output(x_in)
        y_out = self.state.input_to_output(y_in)

        prim = DrillHit(
            x=x_out, y=y_out,
            x_mm=x_mm, y_mm=y_mm,
            tool_number=tool_n,
            diameter_mm=dia_mm,
            diameter_out=dia_out,
            plating=plating,
            input_units=self.state.input_units or "MM",
            output_units=self.state.output_units,
            converted=self.state.converted,
            conversion_factor=self.state.conversion_factor,
            source_cmd=raw.strip(),
            feed_rate=feed,
            spindle_speed=speed,
        )
        self._primitives.append(prim)
        self._last_drill = (x_in, y_in)

        tdef = self.state.current_tool_def()
        if tdef:
            tdef.hit_count += 1

    # --------------------------------------------------------------- slot G85

    def _handle_slot_g85(self, fields: Dict, raw: str) -> None:
        from_current = fields.get("from_current", False)

        if from_current:
            x1_in = self.state.current_x
            y1_in = self.state.current_y
        else:
            x1_in, y1_in = self._resolve_xy(fields.get("x1"), fields.get("y1"))

        x2_in, y2_in = self._resolve_xy(fields.get("x2"), fields.get("y2"))
        self.state.current_x = x2_in
        self.state.current_y = y2_in

        tool_n, dia_mm, dia_out, _, feed, speed = self._tool_info()
        plating = self._current_plating(tool_n)

        prim = SlotG85(
            x_start=self.state.input_to_output(x1_in),
            y_start=self.state.input_to_output(y1_in),
            x_end=self.state.input_to_output(x2_in),
            y_end=self.state.input_to_output(y2_in),
            x_start_mm=self.state.to_mm(x1_in),
            y_start_mm=self.state.to_mm(y1_in),
            x_end_mm=self.state.to_mm(x2_in),
            y_end_mm=self.state.to_mm(y2_in),
            tool_number=tool_n,
            diameter_mm=dia_mm,
            diameter_out=dia_out,
            plating=plating,
            input_units=self.state.input_units or "MM",
            output_units=self.state.output_units,
            converted=self.state.converted,
            conversion_factor=self.state.conversion_factor,
            source_cmd=raw.strip(),
            feed_rate=feed,
            spindle_speed=speed,
        )
        self._primitives.append(prim)

        tdef = self.state.current_tool_def()
        if tdef:
            tdef.hit_count += 1

    # --------------------------------------------------------------- routing

    def _handle_route_g00(self, fields: Dict, raw: str) -> None:
        """G00: rapid reposition — enter route mode, no cut."""
        x_in, y_in = self._resolve_xy(fields.get("x"), fields.get("y"))
        self.state.current_x = x_in
        self.state.current_y = y_in
        self.state.in_route_mode = True
        debug(lambda: f"G00 route reposition to ({x_in}, {y_in})")

    def _handle_route_g01(self, fields: Dict, raw: str) -> None:
        """G01: linear route cut."""
        self.state.in_route_mode = True
        x_start_in = self.state.current_x
        y_start_in = self.state.current_y

        x_end_in, y_end_in = self._resolve_xy(fields.get("x"), fields.get("y"))
        self.state.current_x = x_end_in
        self.state.current_y = y_end_in

        tool_n, dia_mm, dia_out, _, feed, speed = self._tool_info()
        plating = self._current_plating(tool_n)

        prim = RouteSegment(
            segment_type="line",
            x_start=self.state.input_to_output(x_start_in),
            y_start=self.state.input_to_output(y_start_in),
            x_end=self.state.input_to_output(x_end_in),
            y_end=self.state.input_to_output(y_end_in),
            x_start_mm=self.state.to_mm(x_start_in),
            y_start_mm=self.state.to_mm(y_start_in),
            x_end_mm=self.state.to_mm(x_end_in),
            y_end_mm=self.state.to_mm(y_end_in),
            tool_number=tool_n,
            diameter_mm=dia_mm,
            diameter_out=dia_out,
            plating=plating,
            input_units=self.state.input_units or "MM",
            output_units=self.state.output_units,
            converted=self.state.converted,
            conversion_factor=self.state.conversion_factor,
            source_cmd=raw.strip(),
            feed_rate=feed,
            spindle_speed=speed,
            arc_tolerance_mm=self.state.arc_tolerance_mm,
            max_arc_segments=self.state.max_arc_segments,
        )
        self._primitives.append(prim)

    def _handle_route_arc(self, fields: Dict, raw: str, clockwise: bool) -> None:
        """G02 (CW) or G03 (CCW) arc route cut."""
        self.state.in_route_mode = True
        x_start_in = self.state.current_x
        y_start_in = self.state.current_y

        x_end_in, y_end_in = self._resolve_xy(fields.get("x"), fields.get("y"))
        self.state.current_x = x_end_in
        self.state.current_y = y_end_in

        tool_n, dia_mm, dia_out, _, feed, speed = self._tool_info()
        plating = self._current_plating(tool_n)

        seg_type = "arc_cw" if clockwise else "arc_ccw"

        # --- Compute arc center and radius ---
        cx_in: Optional[float] = None
        cy_in: Optional[float] = None
        arc_radius_mm: Optional[float] = None
        arc_angle_deg: Optional[float] = None

        has_ij = "i" in fields or "j" in fields
        has_a  = "a" in fields

        if has_ij:
            # Center offset style (like Gerber): center = start + (I, J)
            i_raw = fields.get("i", "0")
            j_raw = fields.get("j", "0")
            i_in = self._resolve_coord(i_raw) or 0.0
            j_in = self._resolve_coord(j_raw) or 0.0
            cx_in = x_start_in + i_in
            cy_in = y_start_in + j_in
            arc_radius_mm = self.state.to_mm(
                math.sqrt((x_start_in - cx_in) ** 2 + (y_start_in - cy_in) ** 2)
            )
        elif has_a:
            # A-style: A is the arc radius (KiCad convention)
            r_raw = fields["a"]
            r_in = abs(float(r_raw))          # negative A = major arc (handled below)
            r_use_major = float(fields["a"]) < 0
            cx_in, cy_in = self._arc_center_from_radius(
                x_start_in, y_start_in,
                x_end_in, y_end_in,
                r_in, clockwise, r_use_major,
            )
            arc_radius_mm = self.state.to_mm(r_in)
        else:
            warning(f"Arc command without A/R or I/J parameters on line: {raw!r}")
            # Fallback: treat as straight line
            prim = RouteSegment(
                segment_type="line",
                x_start=self.state.input_to_output(x_start_in),
                y_start=self.state.input_to_output(y_start_in),
                x_end=self.state.input_to_output(x_end_in),
                y_end=self.state.input_to_output(y_end_in),
                x_start_mm=self.state.to_mm(x_start_in),
                y_start_mm=self.state.to_mm(y_start_in),
                x_end_mm=self.state.to_mm(x_end_in),
                y_end_mm=self.state.to_mm(y_end_in),
                tool_number=tool_n, diameter_mm=dia_mm, diameter_out=dia_out,
                plating=plating,
                input_units=self.state.input_units or "MM",
                output_units=self.state.output_units,
                converted=self.state.converted,
                conversion_factor=self.state.conversion_factor,
                source_cmd=raw.strip(),
            )
            self._primitives.append(prim)
            return

        # Compute sweep angle for meta
        if cx_in is not None:
            start_ang = math.degrees(
                math.atan2(y_start_in - cy_in, x_start_in - cx_in)
            )
            end_ang = math.degrees(
                math.atan2(y_end_in - cy_in, x_end_in - cx_in)
            )
            if clockwise:
                if end_ang > start_ang:
                    end_ang -= 360.0
            else:
                if end_ang < start_ang:
                    end_ang += 360.0
            arc_angle_deg = end_ang - start_ang

        prim = RouteSegment(
            segment_type=seg_type,
            x_start=self.state.input_to_output(x_start_in),
            y_start=self.state.input_to_output(y_start_in),
            x_end=self.state.input_to_output(x_end_in),
            y_end=self.state.input_to_output(y_end_in),
            x_start_mm=self.state.to_mm(x_start_in),
            y_start_mm=self.state.to_mm(y_start_in),
            x_end_mm=self.state.to_mm(x_end_in),
            y_end_mm=self.state.to_mm(y_end_in),
            arc_center_x=(self.state.input_to_output(cx_in) if cx_in is not None else None),
            arc_center_y=(self.state.input_to_output(cy_in) if cy_in is not None else None),
            arc_center_x_mm=(self.state.to_mm(cx_in) if cx_in is not None else None),
            arc_center_y_mm=(self.state.to_mm(cy_in) if cy_in is not None else None),
            arc_radius_mm=arc_radius_mm,
            arc_angle_deg=arc_angle_deg,
            tool_number=tool_n,
            diameter_mm=dia_mm,
            diameter_out=dia_out,
            plating=plating,
            input_units=self.state.input_units or "MM",
            output_units=self.state.output_units,
            converted=self.state.converted,
            conversion_factor=self.state.conversion_factor,
            source_cmd=raw.strip(),
            feed_rate=feed,
            spindle_speed=speed,
            arc_tolerance_mm=self.state.arc_tolerance_mm,
            max_arc_segments=self.state.max_arc_segments,
        )
        self._primitives.append(prim)

    # --------------------------------------------------------------- repeat

    def _handle_repeat(self, fields: Dict, raw: str) -> None:
        count = fields["count"]
        dx_raw = fields.get("dx")
        dy_raw = fields.get("dy")
        dx = self._resolve_coord(dx_raw) if dx_raw else 0.0
        dy = self._resolve_coord(dy_raw) if dy_raw else 0.0

        if self._last_drill is None:
            warning(f"R{count} repeat but no previous drill — skipping")
            return

        base_x, base_y = self._last_drill
        for i in range(1, count + 1):
            nx = base_x + i * dx
            ny = base_y + i * dy
            saved_x, saved_y = self.state.current_x, self.state.current_y
            self.state.current_x = nx
            self.state.current_y = ny
            # Reuse drill handler with synthetic fields
            self._handle_drill({"x": str(nx), "y": str(ny)}, raw + f"[R{i}]")
            # The handler updates current_x/y; restore original for next iteration ref
            # Actually keep the last drilled position as new base for further repeats
            self._last_drill = (nx, ny)

    # --------------------------------------------------------------- helpers

    def _current_plating(self, tool_n: int) -> str:
        """Get plating from tool definition if available, else state hint."""
        tdef = self.state.tools.get(tool_n)
        if tdef and tdef.plating != "unknown":
            return tdef.plating
        return self.state.current_plating_hint

    @staticmethod
    def _arc_center_from_radius(
        sx: float, sy: float,
        ex: float, ey: float,
        radius: float,
        clockwise: bool,
        use_major: bool = False,
    ) -> Tuple[float, float]:
        """
        Compute arc center from start, end, radius and direction.

        Returns the center point for the MINOR arc unless use_major=True.
        For CW arcs: center is on the RIGHT side of the chord.
        For CCW arcs: center is on the LEFT side of the chord.
        """
        dx = ex - sx
        dy = ey - sy
        d = math.sqrt(dx * dx + dy * dy)

        if d < 1e-12:
            return (sx + radius, sy)  # degenerate: same point

        # Clamp radius to be at least d/2
        r = max(abs(radius), d / 2.0 + 1e-9)

        # Midpoint
        mx = (sx + ex) / 2.0
        my = (sy + ey) / 2.0

        # Left-perpendicular unit vector of chord
        px = -dy / d
        py =  dx / d

        # Distance from midpoint to center
        h = math.sqrt(max(0.0, r * r - (d / 2.0) ** 2))

        # Two candidate centers
        c1 = (mx + h * px, my + h * py)   # left of chord
        c2 = (mx - h * px, my - h * py)   # right of chord

        # Cross product (chord) × (c1 - start): positive = c1 is LEFT
        cross1 = dx * (c1[1] - sy) - dy * (c1[0] - sx)

        # Pick the "short-arc" center first
        if clockwise:
            short_center = c2 if cross1 >= 0 else c1
            long_center  = c1 if cross1 >= 0 else c2
        else:
            short_center = c1 if cross1 >= 0 else c2
            long_center  = c2 if cross1 >= 0 else c1

        return long_center if use_major else short_center
