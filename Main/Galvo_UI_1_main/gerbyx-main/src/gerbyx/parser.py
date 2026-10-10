from typing import Generator, Tuple, Optional
import re

from .processor import GerberProcessor
from .aperture import parse_aperture_def
from .format import parse_format_spec
from .units import parse_units
from .layer_polarity import parse_layer_polarity
from .macro import Macro, parse_macro_start, parse_macro_body
from .blocks import ApertureBlock, parse_ab_start, is_ab_end
from .step_repeat import StepRepeat
from .logger import debug, info, warning, is_debug_enabled

# Pre-compiled regex patterns for performance
_G_CODE_PATTERN = re.compile(r'G(\d{2})')
_COORD_PATTERN = re.compile(r'([XYIJ])([+-]?[\d\.]+)')
_D_CODE_PATTERN = re.compile(r'D(\d+)')
_MACRO_PRIMITIVE_PATTERN = re.compile(r'^\d')

# Command lookup table for fast prefix matching
_PARAM_PREFIXES = {'ADD', 'AB', 'AM', 'LP', 'TA', 'TO', 'TF', 'SR'}
_PARAM_COMMANDS = {'FS', 'MO', 'AD', 'LP', 'TF', 'TA', 'TO', 'TD', 'AB', 'AM', 'SR'}

class GerberParser:
    def __init__(self, processor: GerberProcessor, validate_x3: bool = False):
        self.processor = processor
        self.current_macro_name: Optional[str] = None
        self.current_macro_body: list[str] = []
        self.current_ab_id: Optional[str] = None
        self.current_ab_tokens: list[Tuple[str, str]] = []
        self.validate_x3 = validate_x3
        self.validator = None

        if validate_x3:
            from .validator import GerberValidator
            self.validator = GerberValidator(strict_x3=True)

    def parse(self, tokens: Generator[Tuple[str, str], None, None]):
        info("Starting Gerber parsing")

        # Converti generator in lista se serve validazione
        if self.validate_x3:
            tokens_list = list(tokens)
            debug(lambda: f"Validating X3 compliance ({len(tokens_list)} tokens)")
            if self.validator:
                is_valid = self.validator.validate(tokens_list)
                if not is_valid:
                    warning("X3 validation failed")
                    print("\n" + self.validator.get_report())
            tokens = iter(tokens_list)

        for kind, value in tokens:
            # X3: alcuni comandi possono essere stmt invece di param
            # Convertiamo ADD, AB, AM, LP, TA, TO, TF in param se sono stmt
            if kind == 'stmt':
                for prefix in _PARAM_PREFIXES:
                    if value.startswith(prefix):
                        kind = 'param'
                        break

            # Gestione Aperture Block (AB)
            if self.current_ab_id:
                if kind == 'param' and is_ab_end(value):
                    self._finalize_ab()
                else:
                    self.current_ab_tokens.append((kind, value))
                continue

            # Gestione Macro in corso
            if self.current_macro_name and kind == 'param':
                is_primitive = _MACRO_PRIMITIVE_PATTERN.match(value) or value.startswith('$')

                if is_primitive:
                    self.current_macro_body.append(parse_macro_body(value))
                    continue
                else:
                    self._finalize_macro()

            elif self.current_macro_name and kind != 'param':
                self._finalize_macro()

            # Parsing normale
            if kind == 'param':
                self._parse_param(value)
            elif kind == 'stmt':
                self._parse_stmt(value)
            elif kind == 'comment':
                pass

        self._finalize_macro()
        self._finalize_ab()

    def _parse_param(self, value: str):
        # NOTA: Non rimuovere l'asterisco globale qui perché FS, MO, AD, LP
        # si aspettano l'asterisco per il loro parsing interno (body = value[2:-1]).

        if value.startswith("AB"):
            if is_ab_end(value):
                pass
            else:
                self.current_ab_id = parse_ab_start(value)
                self.current_ab_tokens = []
            return

        if value.startswith("AM"):
            # X3: %AM*% chiude la macro corrente
            if value == "AM*":
                self._finalize_macro()
                return

            if self.current_macro_name:
                self._finalize_macro()

            if len(value) > 3:
                self.current_macro_name = parse_macro_start(value)
                self.current_macro_body = []
            return

        # Fast command dispatch using first 2 chars
        cmd = value[:2]

        if cmd == "FS": self.processor.set_format_spec(parse_format_spec(value))
        elif cmd == "MO": self.processor.set_units(parse_units(value).code)
        elif cmd == "SR": self._parse_step_repeat(value)
        elif cmd == "AD":
            try:
                self.processor.define_aperture(parse_aperture_def(value))
            except ValueError as e:
                print(f"Error parsing aperture definition '{value}': {e}")
        elif cmd == "LP":
            polarity = parse_layer_polarity(value)
            self.processor.set_layer_polarity(polarity.mode)
        elif cmd == "TF" and value[2] == '.': # File Attributes
            # TF.Name,Val*
            content = value[3:]
            if content.endswith('*'): content = content[:-1]
            parts = content.split(',', 1)
            self.processor.set_attribute('file', parts[0], parts[1] if len(parts) > 1 else "")
        elif cmd == "TA" and value[2] == '.': # Aperture Attributes
            # TA.Name,Val*
            content = value[3:]
            if content.endswith('*'): content = content[:-1]
            parts = content.split(',', 1)
            self.processor.set_attribute('aperture', parts[0], parts[1] if len(parts) > 1 else "")
        elif cmd == "TO" and value[2] == '.': # Object Attributes (Layer/Component - X3)
            # TO.Name,Val*
            content = value[3:]
            if content.endswith('*'): content = content[:-1]
            parts = content.split(',', 1)
            self.processor.set_attribute('object', parts[0], parts[1] if len(parts) > 1 else "")
        elif cmd == "TD": # Delete Attributes (X3)
            if value == "TD*" or value == "TD":
                self.processor.delete_attributes('object')
                self.processor.delete_attributes('aperture')
            elif value[2] == '.':
                # TD.Name*
                content = value[3:]
                if content.endswith('*'): content = content[:-1]
                name = content
                self.processor.delete_attribute('object', name)
                self.processor.delete_attribute('aperture', name)

    def _parse_step_repeat(self, value: str):
        """Parse Step & Repeat command (SR)"""
        # SR...* -> body
        # value qui HA l'asterisco perché non l'abbiamo rimosso in _parse_param
        body = value[2:]
        if body.endswith('*'): body = body[:-1]

        if not body:
            debug(lambda: "Disabling Step & Repeat")
            self.processor.set_step_repeat(None)
            return

        m = re.match(r'X(\d+)Y(\d+)I([\d\.\+\-]+)J([\d\.\+\-]+)', body)
        if not m:
            warning(f"Invalid Step & Repeat format: {value}")
            return

        sr = StepRepeat(
            x_repeat=int(m.group(1)),
            y_repeat=int(m.group(2)),
            x_step=float(m.group(3)),
            y_step=float(m.group(4))
        )
        debug(lambda: f"Step & Repeat: {sr.x_repeat}x{sr.y_repeat}, step=({sr.x_step}, {sr.y_step})")
        self.processor.set_step_repeat(sr)

    def _finalize_macro(self):
        if self.current_macro_name:
            debug(lambda: f"Finalizing macro: {self.current_macro_name} ({len(self.current_macro_body)} primitives)")
            macro = Macro(self.current_macro_name, self.current_macro_body)
            self.processor.define_macro(macro)
            self.current_macro_name = None
            self.current_macro_body = []

    def _finalize_ab(self):
        if self.current_ab_id:
            debug(lambda: f"Finalizing aperture block: {self.current_ab_id} ({len(self.current_ab_tokens)} tokens)")
            ab = ApertureBlock(self.current_ab_id, self.current_ab_tokens)
            self.processor.define_aperture_block(ab)
            self.current_ab_id = None
            self.current_ab_tokens = []

    def _parse_stmt(self, value: str):
        if value.endswith('*'): value = value[:-1]

        # Gestione commenti inline (X3): es. "G75*G04 comment"
        if 'G04' in value:
            # Separa il comando dal commento
            parts = value.split('G04', 1)
            if parts[0].strip():
                value = parts[0].strip()
            else:
                return  # Solo commento, ignora

        self._handle_g_code(value)
        self._handle_coordinates_and_dcode(value)

    def _handle_g_code(self, value: str):
        g_codes = _G_CODE_PATTERN.findall(value)
        for code in g_codes:
            if code == '01': self.processor.set_interpolation_mode('Linear')
            elif code == '02': self.processor.set_interpolation_mode('ClockwiseCircular')
            elif code == '03': self.processor.set_interpolation_mode('CounterClockwiseCircular')
            elif code == '36': self.processor.start_region()
            elif code == '37': self.processor.end_region()
            elif code == '74': self.processor.set_quadrant_mode('Single')
            elif code == '75': self.processor.set_quadrant_mode('Multi')

        # X3: M02 = End of File (obbligatorio)
        if 'M02' in value:
            pass  # Fine file, nessuna azione necessaria

    def _handle_coordinates_and_dcode(self, value: str):
        # Parse all coordinates at once with single regex
        coords = {}
        for match in _COORD_PATTERN.finditer(value):
            char = match.group(1)
            val_str = match.group(2)
            coords[char] = self.processor.parse_value(val_str, is_x=(char in ['X', 'I']))

        x = coords.get('X')
        y = coords.get('Y')
        i = coords.get('I')
        j = coords.get('J')

        d_match = _D_CODE_PATTERN.search(value)
        d_code = int(d_match.group(1)) if d_match else None

        if d_code is not None:
            if d_code == 1:
                center = (i, j) if (i is not None or j is not None) else None
                self.processor.draw_to(x, y, center)
            elif d_code == 2: self.processor.update_point(x, y)
            elif d_code == 3: self.processor.flash_at(x, y)
            elif d_code >= 10:
                self.processor.select_aperture(f"D{d_code}")
                if x is not None or y is not None: self.processor.update_point(x, y)
        elif x is not None or y is not None:
            self.processor.update_point(x, y)
