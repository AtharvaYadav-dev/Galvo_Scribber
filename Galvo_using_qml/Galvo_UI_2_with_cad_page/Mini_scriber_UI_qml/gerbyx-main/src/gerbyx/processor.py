from typing import List, Optional, Tuple, Dict, Literal
import math
import re
from shapely.geometry import Point, LineString, Polygon, MultiPoint, box, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import rotate, translate

from .state import PlotState
from .aperture import Aperture
from .format import FormatSpec
from .units import Units
from .macro import Macro
from .blocks import ApertureBlock
from .step_repeat import StepRepeat
from .logger import debug, info, warning, is_debug_enabled, LogContext

class GerberProcessor:
    """
    Interpreta i comandi Gerber e mantiene lo stato del plotter.
    Genera una lista di geometrie Shapely.
    """
    def __init__(self):
        self.state = PlotState()
        # Gestione Layer per Polarità (LPD/LPC)
        # Ogni layer è un dizionario: {'polarity': 'dark'|'clear', 'shapes': []}
        self.layers: List[Dict] = [{'polarity': 'dark', 'shapes': []}]

        self.current_region_points: List[Tuple[float, float]] = []
        self.macros: Dict[str, Macro] = {}
        self.aperture_blocks: Dict[str, ApertureBlock] = {}
        self.file_attributes: Dict[str, str] = {}
        self.layer_attributes: Dict[str, str] = {}
        self.aperture_attributes: Dict[str, Dict[str, str]] = {}

        # Attributi apertura pendenti (definiti prima di ADD/Select)
        self._pending_aperture_attributes: Dict[str, str] = {}

        # Cache for lazy geometry computation
        self._geometries_cache: Optional[List] = None

        # Cache for aperture shapes (performance optimization)
        self._aperture_shape_cache: Dict[str, any] = {}

        # Batch processing threshold
        self._batch_threshold = 100
        self._pending_shapes = 0

        # Step & Repeat state
        self.step_repeat: Optional[StepRepeat] = None

    def set_step_repeat(self, step_repeat: Optional[StepRepeat]):
        """Set Step & Repeat parameters (SR command)"""
        self.step_repeat = step_repeat
        if step_repeat:
            debug(lambda: f"Step & Repeat enabled: {step_repeat.x_repeat}x{step_repeat.y_repeat}")
        else:
            debug(lambda: "Step & Repeat disabled")

    def set_units(self, units: str):
        self.state.units = Units(units)

    def set_attribute(self, attr_type: Literal['file', 'layer', 'aperture', 'object'], name: str, value: str):
        if attr_type == 'file':
            self.file_attributes[name] = value
        elif attr_type == 'layer':
            self.layer_attributes[name] = value
        elif attr_type == 'object':
            # X3: attributi componente (TO.C, TO.CVal, TO.CMnt, ecc.)
            self.state.object_attributes[name] = value
        elif attr_type == 'aperture':
            if self.state.current_aperture_id:
                # Applica direttamente all'apertura corrente
                if self.state.current_aperture_id not in self.aperture_attributes:
                    self.aperture_attributes[self.state.current_aperture_id] = {}
                self.aperture_attributes[self.state.current_aperture_id][name] = value
            else:
                # Nessuna apertura attiva, salva come pendente per la prossima definizione
                self._pending_aperture_attributes[name] = value

    def delete_attribute(self, attr_type: Literal['file', 'layer', 'aperture', 'object'], name: str):
        """Cancella un attributo specifico (X3: TD.Nome)"""
        if attr_type == 'object':
            self.state.object_attributes.pop(name, None)
        elif attr_type == 'aperture':
            # Modifica: TD cancella solo i pending, NON tocca le aperture già definite
            self._pending_aperture_attributes.pop(name, None)

    def delete_attributes(self, attr_type: Literal['file', 'layer', 'aperture', 'object']):
        """Cancella tutti gli attributi di un tipo (X3: TD)"""
        if attr_type == 'object':
            self.state.object_attributes.clear()
        elif attr_type == 'aperture':
            # Modifica: TD cancella solo i pending.
            self._pending_aperture_attributes.clear()

    def set_format_spec(self, format_spec: FormatSpec):
        self.state.format_spec = format_spec

    def define_aperture(self, aperture: Aperture):
        debug(lambda: f"Defining aperture {aperture.id}: {aperture.type} {aperture.params}")
        self.state.apertures[aperture.id] = aperture

        # Se ci sono attributi pendenti, applicali a questa nuova apertura
        if self._pending_aperture_attributes:
            if aperture.id not in self.aperture_attributes:
                self.aperture_attributes[aperture.id] = {}

            # Copia gli attributi pendenti
            self.aperture_attributes[aperture.id].update(self._pending_aperture_attributes)
            # NOTA: Non cancelliamo i pendenti qui perché in Gerber un attributo TA
            # può applicarsi a tutte le definizioni successive finché non viene cancellato (TD).

    def define_macro(self, macro: Macro):
        debug(lambda: f"Defining macro {macro.name} with {len(macro.body)} primitives")
        self.macros[macro.name] = macro

    def define_aperture_block(self, block: ApertureBlock):
        self.aperture_blocks[block.id] = block
        # Registra anche come apertura "virtuale" per permettere la selezione
        # Usa un tipo speciale 'AB' per distinguerlo
        from .aperture import Aperture
        self.state.apertures[block.id] = Aperture(block.id, 'AB', [])

        # Applica attributi pendenti anche ai blocchi
        if self._pending_aperture_attributes:
            if block.id not in self.aperture_attributes:
                self.aperture_attributes[block.id] = {}
            self.aperture_attributes[block.id].update(self._pending_aperture_attributes)

    def select_aperture(self, aperture_id: str):
        if aperture_id not in self.state.apertures:
            warning(f"Aperture {aperture_id} not defined")
        else:
            debug(lambda: f"Selected aperture {aperture_id}")
        self.state.current_aperture_id = aperture_id

        if self._pending_aperture_attributes and aperture_id:
             if aperture_id not in self.aperture_attributes:
                self.aperture_attributes[aperture_id] = {}
             self.aperture_attributes[aperture_id].update(self._pending_aperture_attributes)

    def set_interpolation_mode(self, mode: str):
        self.state.interpolation_mode = mode

    def set_quadrant_mode(self, mode: str):
        self.state.quadrant_mode = mode

    def set_layer_polarity(self, polarity: str):
        """
        Imposta la polarità del layer corrente (LPD/LPC).
        Crea un nuovo layer se la polarità cambia.
        """
        # polarity è 'DARK' o 'CLEAR' (dal parser)
        pol_key = 'dark' if polarity == 'DARK' else 'clear'

        # Se l'ultimo layer ha la stessa polarità, continuiamo a usarlo.
        # Altrimenti ne creiamo uno nuovo.
        if self.layers[-1]['polarity'] != pol_key:
            # Solo se il layer precedente non è vuoto, altrimenti cambiamo solo la polarità di quello vuoto
            if self.layers[-1]['shapes']:
                self.layers.append({'polarity': pol_key, 'shapes': []})
            else:
                self.layers[-1]['polarity'] = pol_key

        self.state.layer_polarity.mode = polarity

    def start_region(self):
        self.state.region_mode = True
        self.current_region_points = []
        if self.state.current_point:
             self.current_region_points.append(self.state.current_point)

    def end_region(self):
        self.state.region_mode = False
        if len(self.current_region_points) > 2:
            if self.current_region_points[0] != self.current_region_points[-1]:
                self.current_region_points.append(self.current_region_points[0])
            poly = Polygon(self.current_region_points)
            if not poly.is_valid:
                poly = poly.buffer(0)
            self._add_shape(poly)
        self.current_region_points = []

    def _add_shape(self, shape):
        """Aggiunge una forma al layer corrente, applicando Step & Repeat se attivo."""
        if shape and not shape.is_empty:
            if self.step_repeat:
                # Apply Step & Repeat
                for y_idx in range(self.step_repeat.y_repeat):
                    for x_idx in range(self.step_repeat.x_repeat):
                        x_offset = x_idx * self.step_repeat.x_step
                        y_offset = y_idx * self.step_repeat.y_step
                        repeated_shape = translate(shape, xoff=x_offset, yoff=y_offset)
                        self.layers[-1]['shapes'].append(repeated_shape)
                        self._pending_shapes += 1
            else:
                self.layers[-1]['shapes'].append(shape)
                self._pending_shapes += 1

            # Invalida cache quando aggiungiamo nuove shape
            self._geometries_cache = None

    @property
    def geometries(self):
        """
        Restituisce la geometria finale composta applicando le polarità.
        Usa lazy evaluation con cache per performance.
        """
        # Ritorna cache se disponibile
        if self._geometries_cache is not None:
            debug(lambda: "Returning cached geometries")
            return self._geometries_cache

        with LogContext("Computing final geometries", level='DEBUG'):
            # Combina i layer con batch processing
            final_shape = None

            for layer in self.layers:
                if not layer['shapes']:
                    continue

                debug(lambda: f"Processing layer with {len(layer['shapes'])} shapes (polarity: {layer['polarity']})")
                # Batch unary_union per performance
                layer_shape = self._batch_union(layer['shapes'])

                if final_shape is None:
                    if layer['polarity'] == 'dark':
                        final_shape = layer_shape
                else:
                    if layer['polarity'] == 'dark':
                        final_shape = final_shape.union(layer_shape)
                    else:
                        final_shape = final_shape.difference(layer_shape)

            if final_shape is None:
                self._geometries_cache = []
                return self._geometries_cache

            if isinstance(final_shape, (Polygon, LineString, Point)):
                self._geometries_cache = [final_shape]
            elif hasattr(final_shape, 'geoms'):
                self._geometries_cache = list(final_shape.geoms)
            else:
                self._geometries_cache = [final_shape]

            info(f"Generated {len(self._geometries_cache)} final geometries")
            return self._geometries_cache

    def _batch_union(self, shapes):
        """Batch unary_union per ridurre overhead"""
        if len(shapes) == 1:
            return shapes[0]

        # Per liste grandi, unisci in batch per evitare stack overflow
        if len(shapes) > 500:
            debug(lambda: f"Batch union for {len(shapes)} shapes (batch_size=100)")
            batch_size = 100
            batches = []
            for i in range(0, len(shapes), batch_size):
                batch = shapes[i:i+batch_size]
                batches.append(unary_union(batch))
            return unary_union(batches)

        return unary_union(shapes)

    def parse_value(self, value_str: str, is_x: bool = True) -> float:
        fmt = self.state.format_spec
        if not fmt:
            return float(value_str)

        sign = 1
        if value_str.startswith('+'):
            value_str = value_str[1:]
        elif value_str.startswith('-'):
            sign = -1
            value_str = value_str[1:]

        length = len(value_str)
        if is_x:
            decimals = fmt.x_dec
            integers = fmt.x_int
        else:
            decimals = fmt.y_dec
            integers = fmt.y_int

        if '.' in value_str:
            return float(value_str) * sign

        if fmt.zero_omission == 'L':
            if length < decimals:
                value_str = value_str.zfill(decimals + 1)
            val = float(value_str) / (10 ** decimals)
            return val * sign
        elif fmt.zero_omission == 'T':
            total_len = integers + decimals
            if length < total_len:
                value_str = value_str.ljust(total_len, '0')
            val = float(value_str) / (10 ** decimals)
            return val * sign

        return float(value_str) * sign

    def update_point(self, x: Optional[float] = None, y: Optional[float] = None):
        curr_x, curr_y = self.state.current_point
        new_x = x if x is not None else curr_x
        new_y = y if y is not None else curr_y

        if self.state.format_spec and self.state.format_spec.coord_mode == 'I':
            if x is not None: new_x = curr_x + x
            if y is not None: new_y = curr_y + y

        self.state.current_point = (new_x, new_y)
        if self.state.region_mode:
            self.current_region_points.append(self.state.current_point)

    def draw_to(self, x: Optional[float] = None, y: Optional[float] = None, center_offset: Optional[Tuple[float, float]] = None):
        start_point = self.state.current_point
        curr_x, curr_y = start_point
        target_x = x if x is not None else curr_x
        target_y = y if y is not None else curr_y

        if self.state.format_spec and self.state.format_spec.coord_mode == 'I':
            if x is not None: target_x = curr_x + x
            if y is not None: target_y = curr_y + y

        end_point = (target_x, target_y)

        if self.state.interpolation_mode == 'Linear':
            if self.state.region_mode:
                self.current_region_points.append(end_point)
            else:
                aperture = self.state.get_current_aperture()
                if aperture:
                    line = LineString([start_point, end_point])
                    shape = self._create_stroked_shape(line, aperture)
                    self._add_shape(shape)

        elif self.state.interpolation_mode in ['ClockwiseCircular', 'CounterClockwiseCircular']:
            if center_offset:
                i, j = center_offset
                center_x = curr_x + i
                center_y = curr_y + j
                is_full_circle = (start_point == end_point)
                arc_points = self._generate_arc_points(
                    start_point, end_point, (center_x, center_y),
                    self.state.interpolation_mode == 'ClockwiseCircular',
                    is_full_circle=is_full_circle
                )
                if self.state.region_mode:
                    self.current_region_points.extend(arc_points[1:])
                else:
                    aperture = self.state.get_current_aperture()
                    if aperture:
                        line = LineString(arc_points)
                        shape = self._create_stroked_shape(line, aperture)
                        self._add_shape(shape)

        self.state.current_point = end_point

    def flash_at(self, x: Optional[float] = None, y: Optional[float] = None):
        self.update_point(x, y)
        if self.state.region_mode:
            return

        aperture = self.state.get_current_aperture()
        if not aperture:
            return

        # Controlla se è un blocco apertura (AB)
        if self.state.current_aperture_id in self.aperture_blocks:
            block = self.aperture_blocks[self.state.current_aperture_id]
            shape = self._instantiate_aperture_block(block, self.state.current_point)
            if shape:
                self._add_shape(shape)
            return

        # Controlla se è una macro
        if aperture.type not in ['C', 'R', 'O', 'P']:
            macro_name = aperture.type
            if macro_name in self.macros:
                macro_def = self.macros[macro_name]
                shape = self._instantiate_macro(macro_def, aperture.params, self.state.current_point)
                self._add_shape(shape)
            else:
                print(f"Warning: Macro '{macro_name}' not found.")
                warning(f"Macro '{macro_name}' not found")
        else:
            # Apertura standard
            shape = self._create_flashed_shape(Point(self.state.current_point), aperture)
            self._add_shape(shape)

    # --- Macro Interpreter ---

    def _instantiate_aperture_block(self, block: ApertureBlock, location: Tuple[float, float]):
        """Istanzia un blocco apertura nella posizione specificata (X3)"""
        from .parser import GerberParser

        # Crea un processor temporaneo per eseguire i comandi del blocco
        temp_processor = GerberProcessor()
        temp_processor.state = PlotState()
        temp_processor.state.format_spec = self.state.format_spec
        temp_processor.state.units = self.state.units
        temp_processor.state.apertures = self.state.apertures
        temp_processor.macros = self.macros
        temp_processor.state.current_point = (0.0, 0.0)

        # Crea un parser temporaneo
        temp_parser = GerberParser(temp_processor)

        # Esegui i comandi del blocco
        for kind, value in block.tokens:
            if kind == 'param':
                temp_parser._parse_param(value)
            elif kind == 'stmt':
                temp_parser._parse_stmt(value)

        # Ottieni le geometrie generate
        geometries = temp_processor.geometries
        if not geometries:
            return None

        # Unisci tutte le geometrie e trasla alla posizione di flash
        combined = unary_union(geometries)
        translated = translate(combined, xoff=location[0], yoff=location[1])
        return translated

    def _instantiate_macro(self, macro: Macro, params: List[float], location: Tuple[float, float]):
        shapes_add = []
        shapes_sub = []

        for primitive_str in macro.body:
            primitive_str = primitive_str.strip()
            if not primitive_str or primitive_str.startswith('0 '):
                continue

            tokens = primitive_str.split(',')
            code_expr = tokens[0]
            try:
                code = int(self._evaluate_expression(code_expr, params))
            except:
                continue

            evaluated_args = []
            for t in tokens[1:]:
                val = self._evaluate_expression(t, params)
                evaluated_args.append(val)

            prim_shape = self._generate_macro_primitive(code, evaluated_args)

            if prim_shape is None or prim_shape.is_empty:
                continue

            exposure = 1
            if code in [1, 2, 20, 21, 4, 5]:
                if len(evaluated_args) > 0:
                    exposure = int(evaluated_args[0])

            if exposure == 1:
                shapes_add.append(prim_shape)
            else:
                shapes_sub.append(prim_shape)

        if not shapes_add:
            return None

        final_shape = unary_union(shapes_add)

        if shapes_sub:
            sub_shape = unary_union(shapes_sub)
            final_shape = final_shape.difference(sub_shape)

        final_shape = translate(final_shape, xoff=location[0], yoff=location[1])
        return final_shape

    def _evaluate_expression(self, expr: str, params: List[float]) -> float:
        """Valuta espressioni macro in modo sicuro senza eval()."""
        def replace_var(match):
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(params):
                return str(params[idx])
            return "0"

        # Sostituisci variabili $1, $2, etc.
        expr_sub = re.sub(r'\$(\d+)', replace_var, expr)
        # Normalizza operatori
        expr_sub = expr_sub.replace('x', '*').replace('X', '*')
        expr_sub = expr_sub.strip()

        # Quick path for simple numbers, including negatives
        try:
            return float(expr_sub)
        except ValueError:
            pass  # Not a simple number, proceed with full parser

        # Validazione: solo caratteri sicuri
        if not re.match(r'^[\d\.\+\-\*\/\(\)\s]+$', expr_sub):
            print(f"Warning: Invalid characters in macro expression '{expr}'")
            return 0.0

        try:
            return self._safe_eval(expr_sub)
        except Exception as e:
            warning(f"Error evaluating macro expression '{expr}': {e}")
            return 0.0

    def _safe_eval(self, expr: str) -> float:
        """Valuta espressioni matematiche in modo sicuro senza eval()."""
        # Tokenize expression
        tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', expr)
        if not tokens:
            return 0.0

        # Shunting-yard algorithm per convertire in RPN
        output = []
        operators = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        for token in tokens:
            if re.match(r'\d+\.?\d*', token):
                output.append(float(token))
            elif token in precedence:
                while (operators and operators[-1] != '(' and
                       operators[-1] in precedence and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if operators:
                    operators.pop()  # Remove '('

        while operators:
            output.append(operators.pop())

        # Valuta RPN
        stack = []
        for item in output:
            if isinstance(item, float):
                stack.append(item)
            else:
                if len(stack) < 2:
                    return 0.0
                b = stack.pop()
                a = stack.pop()
                if item == '+':
                    stack.append(a + b)
                elif item == '-':
                    stack.append(a - b)
                elif item == '*':
                    stack.append(a * b)
                elif item == '/':
                    stack.append(a / b if b != 0 else 0.0)

        return stack[0] if stack else 0.0

    def _generate_macro_primitive(self, code: int, args: List[float]):
        try:
            if code == 1: # Circle
                dia = args[1]
                x = args[2]
                y = args[3]
                return Point(x, y).buffer(dia / 2)

            elif code == 2 or code == 20: # Vector Line
                w = args[1]
                x1, y1 = args[2], args[3]
                x2, y2 = args[4], args[5]
                rot = args[6]
                line = LineString([(x1, y1), (x2, y2)])
                shape = line.buffer(w/2, cap_style='square')
                if rot != 0:
                    shape = rotate(shape, rot, origin=(0,0))
                return shape

            elif code == 21: # Center Line (Rectangle)
                w = args[1]
                h = args[2]
                cx = args[3]
                cy = args[4]
                rot = args[5]
                rect = box(cx - w/2, cy - h/2, cx + w/2, cy + h/2)
                if rot != 0:
                    rect = rotate(rect, rot, origin=(0,0))
                return rect

            elif code == 4: # Outline
                num_pts = int(args[1])
                coords = []
                idx = 2
                for _ in range(num_pts + 1):
                    if idx + 1 >= len(args) - 1:
                        break
                    coords.append((args[idx], args[idx+1]))
                    idx += 2
                rot = args[-1]
                poly = Polygon(coords)
                if rot != 0:
                    poly = rotate(poly, rot, origin=(0,0))
                return poly

            elif code == 5: # Polygon (Regular)
                vertices = int(args[1])

                # FIX: Avoid division by zero if vertices < 3
                if vertices < 3:
                    print(f"Warning: Polygon aperture has {vertices} vertices, skipping.")
                    return None

                cx = args[2]
                cy = args[3]
                dia = args[4]
                rot = args[5]
                radius = dia / 2
                angle_step = 2 * math.pi / vertices
                points = []
                for i in range(vertices):
                    theta = i * angle_step
                    px = cx + radius * math.cos(theta)
                    py = cy + radius * math.sin(theta)
                    points.append((px, py))
                poly = Polygon(points)
                if rot != 0:
                    poly = rotate(poly, rot, origin=(0,0))
                return poly

            elif code == 7: # Thermal
                cx = args[0]
                cy = args[1]
                inner_dia = args[2]
                outer_dia = args[3]
                gap = args[4]
                rot = args[5]
                outer_circle = Point(cx, cy).buffer(outer_dia/2)
                inner_circle = Point(cx, cy).buffer(inner_dia/2)
                ring = outer_circle.difference(inner_circle)
                L = outer_dia + 1.0
                h_bar = box(cx - L/2, cy - gap/2, cx + L/2, cy + gap/2)
                v_bar = box(cx - gap/2, cy - L/2, cx + gap/2, cy + L/2)
                cross = unary_union([h_bar, v_bar])
                shape = ring.difference(cross)
                if rot != 0:
                    shape = rotate(shape, rot, origin=(0,0))
                return shape

        except Exception as e:
            print(f"Error generating macro primitive {code}: {e}")
            return None

        return None

    # --- End Macro Interpreter ---

    def _generate_arc_points(self, start, end, center, clockwise, num_segments=64, is_full_circle=False):
        sx, sy = start
        ex, ey = end
        cx, cy = center
        r_start = math.sqrt((sx - cx)**2 + (sy - cy)**2)
        r_end = math.sqrt((ex - cx)**2 + (ey - cy)**2)
        radius = (r_start + r_end) / 2.0
        if radius < 1e-9: return [start, end]

        start_angle = math.atan2(sy - cy, sx - cx)
        end_angle = math.atan2(ey - cy, ex - cx)

        if is_full_circle:
            if clockwise: end_angle = start_angle - 2 * math.pi
            else: end_angle = start_angle + 2 * math.pi
        else:
            if clockwise:
                if end_angle > start_angle: end_angle -= 2 * math.pi
            else:
                if end_angle < start_angle: end_angle += 2 * math.pi

        points = []
        angle_diff = end_angle - start_angle
        steps = max(int(abs(angle_diff) * num_segments / (2 * math.pi)) + 1, 2)

        for i in range(steps + 1):
            theta = start_angle + angle_diff * (i / steps)
            px = cx + radius * math.cos(theta)
            py = cy + radius * math.sin(theta)
            points.append((px, py))
        return points

    def _create_stroked_shape(self, line: LineString, aperture: Aperture):
        if aperture.type == 'C':
            radius = aperture.params[0] / 2.0
            return line.buffer(radius, cap_style='round')
        elif aperture.type == 'R':
            w = aperture.params[0]
            h = aperture.params[1] if len(aperture.params) > 1 else w
            polys = []
            coords = list(line.coords)
            for k in range(len(coords) - 1):
                x1, y1 = coords[k]
                x2, y2 = coords[k+1]
                p1 = [(x1 - w/2, y1 - h/2), (x1 + w/2, y1 - h/2), (x1 + w/2, y1 + h/2), (x1 - w/2, y1 + h/2)]
                p2 = [(x2 - w/2, y2 - h/2), (x2 + w/2, y2 - h/2), (x2 + w/2, y2 + h/2), (x2 - w/2, y2 + h/2)]
                segment_poly = MultiPoint(p1 + p2).convex_hull
                polys.append(segment_poly)
            return unary_union(polys)
        return line.buffer(0.001)

    def _create_flashed_shape(self, point: Point, aperture: Aperture):
        # Check cache first
        cache_key = f"{aperture.id}_{aperture.type}_{','.join(map(str, aperture.params))}"
        if cache_key in self._aperture_shape_cache:
            cached_shape = self._aperture_shape_cache[cache_key]
            # Translate cached shape to current point
            return translate(cached_shape, xoff=point.x, yoff=point.y)

        x, y = point.x, point.y
        # Create shape at origin for caching
        shape_at_origin = None

        if aperture.type == 'C':
            radius = aperture.params[0] / 2.0
            shape_at_origin = Point(0, 0).buffer(radius)
        elif aperture.type == 'R':
            w = aperture.params[0]
            h = aperture.params[1] if len(aperture.params) > 1 else w
            shape_at_origin = Polygon([(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)])
        elif aperture.type == 'O':
             w = aperture.params[0]
             h = aperture.params[1] if len(aperture.params) > 1 else w
             if w > h:
                 shape_at_origin = LineString([(-((w-h)/2), 0), ((w-h)/2, 0)]).buffer(h/2)
             else:
                 shape_at_origin = LineString([(0, -(h-w)/2), (0, (h-w)/2)]).buffer(w/2)
        elif aperture.type == 'P':
            # Polygon: diameter, vertices, [rotation], [hole_dia]
            dia = aperture.params[0]
            vertices = int(aperture.params[1])
            rot = aperture.params[2] if len(aperture.params) > 2 else 0.0

            if vertices < 3:
                print(f"Warning: Polygon aperture has {vertices} vertices, skipping.")
                return Point(x, y).buffer(0.001)

            radius = dia / 2
            angle_step = 2 * math.pi / vertices
            points = []
            for i in range(vertices):
                theta = i * angle_step
                px = radius * math.cos(theta)
                py = radius * math.sin(theta)
                points.append((px, py))

            shape_at_origin = Polygon(points)
            if rot != 0:
                shape_at_origin = rotate(shape_at_origin, rot, origin=(0, 0))
        else:
            return Point(x, y).buffer(0.1)

        # Cache shape at origin
        if shape_at_origin:
            self._aperture_shape_cache[cache_key] = shape_at_origin
            # Translate to actual position
            return translate(shape_at_origin, xoff=x, yoff=y)

        return Point(x, y).buffer(0.1)
