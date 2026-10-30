import sys
import os
import math
import time
from PySide6.QtCore import QObject, Signal, Slot, Property, QThread, QTimer

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from core.motion_planner import MotionPlanner
from galvo_threads import ExecutionThread, PreviewThread


class MatrixBridge(QObject):
    """
    QObject Bridge for Parameter Mapping Matrix (matching mapping_controller.py in main.py).
    Generates 2D power vs frequency test grids and handles execution/framing.
    """
    matrixCellsChanged = Signal()
    paramsChanged = Signal()
    statusMessageChanged = Signal(str)
    isExecutingChanged = Signal(bool)
    isPausedChanged = Signal(bool)
    isFramingChanged = Signal(bool)
    activeCellIndexChanged = Signal(int)
    hardwareAlert = Signal(str, str)

    def __init__(self, galvo_bridge=None, parent=None):
        super().__init__(parent)
        self.galvo_bridge = galvo_bridge
        self.galvo_controller = galvo_bridge.controller if galvo_bridge else None

        # Matrix Generation Parameters - defaults exactly matching mapping_controller.py
        self._power_start = 10.0
        self._power_end = 90.0
        self._power_steps = 5

        self._freq_start = 20.0
        self._freq_end = 80.0
        self._freq_steps = 5

        self._cell_w = 5.0
        self._cell_h = 5.0
        self._gap_x = 2.0
        self._gap_y = 2.0

        self._fill_type = "Filled Rectangle"  # or "Vector Outline"
        self._label_axes = True
        self._speed = 1000.0

        # Telemetry & States
        self._grid_cells = []
        self._total_w = 0.0
        self._total_h = 0.0
        self._exceeds_bounds = False

        self._status_message = "Ready"
        self._is_executing = False
        self._is_paused = False
        self._is_framing = False
        self._is_aborted = False
        self._active_cell_index = -1

        self.preview_thread = None
        self.exec_thread = None
        self._cmd_to_cell = {}

        # Generate initial matrix
        self._generate_matrix_data()

    # ---------------- Property Getters ---------------- #

    def get_power_start(self) -> float: return self._power_start
    def set_power_start(self, v: float): self._power_start = float(v); self.paramsChanged.emit()

    def get_power_end(self) -> float: return self._power_end
    def set_power_end(self, v: float): self._power_end = float(v); self.paramsChanged.emit()

    def get_power_steps(self) -> int: return self._power_steps
    def set_power_steps(self, v: int): self._power_steps = max(1, int(v)); self.paramsChanged.emit()

    def get_freq_start(self) -> float: return self._freq_start
    def set_freq_start(self, v: float): self._freq_start = float(v); self.paramsChanged.emit()

    def get_freq_end(self) -> float: return self._freq_end
    def set_freq_end(self, v: float): self._freq_end = float(v); self.paramsChanged.emit()

    def get_freq_steps(self) -> int: return self._freq_steps
    def set_freq_steps(self, v: int): self._freq_steps = max(1, int(v)); self.paramsChanged.emit()

    def get_cell_w(self) -> float: return self._cell_w
    def set_cell_w(self, v: float): self._cell_w = max(0.5, float(v)); self.paramsChanged.emit()

    def get_cell_h(self) -> float: return self._cell_h
    def set_cell_h(self, v: float): self._cell_h = max(0.5, float(v)); self.paramsChanged.emit()

    def get_gap_x(self) -> float: return self._gap_x
    def set_gap_x(self, v: float): self._gap_x = max(0.0, float(v)); self.paramsChanged.emit()

    def get_gap_y(self) -> float: return self._gap_y
    def set_gap_y(self, v: float): self._gap_y = max(0.0, float(v)); self.paramsChanged.emit()

    def get_fill_type(self) -> str: return self._fill_type
    def set_fill_type(self, v: str): self._fill_type = str(v); self.paramsChanged.emit()

    def get_label_axes(self) -> bool: return self._label_axes
    def set_label_axes(self, v: bool): self._label_axes = bool(v); self.paramsChanged.emit()

    def get_speed(self) -> float: return self._speed
    def set_speed(self, v: float): self._speed = max(10.0, float(v)); self.paramsChanged.emit()

    def get_status_message(self) -> str: return self._status_message
    def get_is_executing(self) -> bool: return self._is_executing
    def get_is_paused(self) -> bool: return self._is_paused
    def get_is_framing(self) -> bool: return self._is_framing
    def get_active_cell_index(self) -> int: return self._active_cell_index

    def get_total_w(self) -> float: return self._total_w
    def get_total_h(self) -> float: return self._total_h
    def get_exceeds(self) -> bool: return self._exceeds_bounds
    def get_matrix_cells(self) -> list: return self._grid_cells

    # ---------------- QML Properties with notify Signals ---------------- #

    powerStart = Property(float, get_power_start, set_power_start, notify=paramsChanged)
    powerEnd = Property(float, get_power_end, set_power_end, notify=paramsChanged)
    powerSteps = Property(int, get_power_steps, set_power_steps, notify=paramsChanged)

    freqStart = Property(float, get_freq_start, set_freq_start, notify=paramsChanged)
    freqEnd = Property(float, get_freq_end, set_freq_end, notify=paramsChanged)
    freqSteps = Property(int, get_freq_steps, set_freq_steps, notify=paramsChanged)

    cellWidth = Property(float, get_cell_w, set_cell_w, notify=paramsChanged)
    cellHeight = Property(float, get_cell_h, set_cell_h, notify=paramsChanged)
    cellGapX = Property(float, get_gap_x, set_gap_x, notify=paramsChanged)
    cellGapY = Property(float, get_gap_y, set_gap_y, notify=paramsChanged)
    gapX = Property(float, get_gap_x, set_gap_x, notify=paramsChanged)
    gapY = Property(float, get_gap_y, set_gap_y, notify=paramsChanged)

    fillType = Property(str, get_fill_type, set_fill_type, notify=paramsChanged)
    labelAxes = Property(bool, get_label_axes, set_label_axes, notify=paramsChanged)
    markSpeed = Property(float, get_speed, set_speed, notify=paramsChanged)
    speed = Property(float, get_speed, set_speed, notify=paramsChanged)

    statusMessage = Property(str, get_status_message, notify=statusMessageChanged)
    isExecuting = Property(bool, get_is_executing, notify=isExecutingChanged)
    isRunning = Property(bool, get_is_executing, notify=isExecutingChanged)
    isPaused = Property(bool, get_is_paused, notify=isPausedChanged)
    isFraming = Property(bool, get_is_framing, notify=isFramingChanged)
    activeCellIndex = Property(int, get_active_cell_index, notify=activeCellIndexChanged)

    totalWidth = Property(float, get_total_w, notify=matrixCellsChanged)
    totalHeight = Property(float, get_total_h, notify=matrixCellsChanged)
    totalW = Property(float, get_total_w, notify=matrixCellsChanged)
    totalH = Property(float, get_total_h, notify=matrixCellsChanged)
    exceedsBounds = Property(bool, get_exceeds, notify=matrixCellsChanged)
    matrixCells = Property(list, get_matrix_cells, notify=matrixCellsChanged)

    # ---------------- Matrix Generation Logic ---------------- #

    def _get_scale_and_field_size(self):
        calib_scale = None
        if self.galvo_controller and hasattr(self.galvo_controller, 'connection') and self.galvo_controller.connection:
            if hasattr(self.galvo_controller.connection, 'calibration'):
                calib = self.galvo_controller.connection.calibration
                if calib and getattr(calib, 'is_valid', False) and getattr(calib, 'scale', None):
                    calib_scale = float(calib.scale)
        if not calib_scale:
            try:
                cor_path = os.path.join(_root, "newest100mm.cor")
                if os.path.exists(cor_path):
                    from core.calibration import GalvoCalibration
                    c = GalvoCalibration(cor_path)
                    if c.is_valid and c.scale:
                        calib_scale = float(c.scale)
            except Exception:
                pass

        field_size = 70.0
        if self.galvo_bridge and hasattr(self.galvo_bridge, '_field_size'):
            field_size = float(self.galvo_bridge._field_size)

        scale = calib_scale if calib_scale else (65535.0 / field_size)
        return scale, field_size

    def _field_size(self) -> float:
        _, f_size = self._get_scale_and_field_size()
        return f_size

    def _generate_matrix_data(self):
        cells = []
        p_steps = max(1, self._power_steps)
        f_steps = max(1, self._freq_steps)

        # Total layout dimensions
        self._total_w = (p_steps * self._cell_w) + (max(0, p_steps - 1) * self._gap_x)
        self._total_h = (f_steps * self._cell_h) + (max(0, f_steps - 1) * self._gap_y)

        # Center grid at (0, 0) in galvo coordinate space
        start_x = -self._total_w / 2.0
        start_y = -self._total_h / 2.0

        for r in range(f_steps):
            for c in range(p_steps):
                x = start_x + c * (self._cell_w + self._gap_x)
                y = start_y + r * (self._cell_h + self._gap_y)

                if p_steps > 1:
                    power = self._power_start + (self._power_end - self._power_start) * (c / (p_steps - 1))
                else:
                    power = self._power_start

                if f_steps > 1:
                    freq = self._freq_start + (self._freq_end - self._freq_start) * (r / (f_steps - 1))
                else:
                    freq = self._freq_start

                cells.append({
                    "row": int(r),
                    "col": int(c),
                    "x": float(x),
                    "y": float(y),
                    "w": float(self._cell_w),
                    "h": float(self._cell_h),
                    "power": float(power),
                    "freq": float(freq)
                })

        self._grid_cells = cells

        # Bounds checking against field size
        f_size = self._field_size()
        self._exceeds_bounds = (self._total_w > f_size) or (self._total_h > f_size)

        self.matrixCellsChanged.emit()

    @Slot(float, float, int, float, float, int, float, float, float, float, str, bool, float)
    def updateParameters(self, p_start, p_end, p_steps, f_start, f_end, f_steps,
                          cw, ch, gx, gy, fill_type, label_axes, speed):
        """Updates grid parameters and recalculates 2D matrix structure."""
        self._power_start = float(p_start)
        self._power_end = float(p_end)
        self._power_steps = max(1, int(p_steps))

        self._freq_start = float(f_start)
        self._freq_end = float(f_end)
        self._freq_steps = max(1, int(f_steps))

        self._cell_w = max(0.5, float(cw))
        self._cell_h = max(0.5, float(ch))
        self._gap_x = max(0.0, float(gx))
        self._gap_y = max(0.0, float(gy))

        self._fill_type = str(fill_type)
        self._label_axes = bool(label_axes)
        self._speed = max(10.0, float(speed))

        self._generate_matrix_data()
        self.paramsChanged.emit()
        self._set_status(f"Grid: {self._power_steps}x{self._freq_steps} ({self._total_w:.1f}x{self._total_h:.1f} mm)")

    def _set_status(self, msg: str):
        self._status_message = msg
        self.statusMessageChanged.emit(msg)

    # ---------------- Digit Font Engraving (from mapping_controller.py) ---------------- #

    def _draw_digit_lines(self, d: int, cx: float, cy: float, planner: MotionPlanner, scale: float = 1.0, speed: int = None, jump_speed: int = 2000000):
        # Crisp readable dimensions: 1.8mm width (dw=0.9mm), 3.2mm height (dh=1.6mm)
        dw = int(0.9 * scale)
        dh = int(1.6 * scale)
        x0 = int(cx - dw)
        x1 = int(cx + dw)
        y0 = int(cy + dh)
        y1 = int(cy)
        y2 = int(cy - dh)

        def mark(x, y):
            planner.add_mark(int(x), int(y), speed=speed)
        def jump(x, y):
            planner.add_jump(int(x), int(y), speed=jump_speed)

        if d == 1: jump(x1, y0); mark(x1, y2)
        elif d == 2: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); mark(x0, y2); mark(x1, y2)
        elif d == 3: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); jump(x1, y1); mark(x1, y2); mark(x0, y2)
        elif d == 4: jump(x0, y0); mark(x0, y1); mark(x1, y1); jump(x1, y0); mark(x1, y2)
        elif d == 5: jump(x1, y0); mark(x0, y0); mark(x0, y1); mark(x1, y1); mark(x1, y2); mark(x0, y2)
        elif d == 6: jump(x1, y0); mark(x0, y0); mark(x0, y2); mark(x1, y2); mark(x1, y1); mark(x0, y1)
        elif d == 7: jump(x0, y0); mark(x1, y0); mark(x1, y2)
        elif d == 8: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0); jump(x0, y1); mark(x1, y1)
        elif d == 9: jump(x1, y1); mark(x0, y1); mark(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2)
        elif d == 0: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0)

    def _draw_stroke_text(self, text: str, cx_mm: float, cy_mm: float, planner: MotionPlanner, font_size_mm: float = 2.3, speed: int = None, jump_speed: int = 2000000):
        """
        Renders clean single-stroke vector text (Hershey Simplex) centered at (cx_mm, cy_mm).
        Produces sharp, high-legibility vector engraving for text labels, units, and titles.
        """
        try:
            from core.mk_lib.tools.jhfparser import SimplexFont, JhfPath
            font = SimplexFont('')
            path = JhfPath()
            font.render(path, text, True, font_size_mm, 1.0, 1.0, 'start')

            strokes = []
            current_stroke = []
            for item in path.path:
                if item is None:
                    if current_stroke:
                        strokes.append(current_stroke)
                        current_stroke = []
                elif isinstance(item, tuple):
                    if len(item) == 2:
                        if current_stroke:
                            strokes.append(current_stroke)
                        current_stroke = [item]
                    elif len(item) == 4:
                        if not current_stroke:
                            current_stroke.append((item[0], item[1]))
                        elif current_stroke[-1] != (item[0], item[1]):
                            strokes.append(current_stroke)
                            current_stroke = [(item[0], item[1])]
                        current_stroke.append((item[2], item[3]))
            if current_stroke:
                strokes.append(current_stroke)

            if not strokes:
                return

            all_pts = [pt for st in strokes for pt in st]
            min_x, max_x = min(p[0] for p in all_pts), max(p[0] for p in all_pts)
            min_y, max_y = min(p[1] for p in all_pts), max(p[1] for p in all_pts)
            local_cx = (min_x + max_x) / 2.0
            local_cy = (min_y + max_y) / 2.0

            scale, _ = self._get_scale_and_field_size()
            center_xy = 32767

            for stroke in strokes:
                gx0 = int((cx_mm + (stroke[0][0] - local_cx)) * scale + center_xy)
                gy0 = int((cy_mm + (stroke[0][1] - local_cy)) * scale + center_xy)
                planner.add_jump(gx0, gy0, speed=jump_speed)
                for pt in stroke[1:]:
                    gx = int((cx_mm + (pt[0] - local_cx)) * scale + center_xy)
                    gy = int((cy_mm + (pt[1] - local_cy)) * scale + center_xy)
                    planner.add_mark(gx, gy, speed=speed)

            # Turn off laser cleanly after every text label
            planner.add_laser_off()
            planner.add_delay(2)
        except Exception as e:
            print(f"[MatrixBridge] Error rendering stroke text '{text}': {e}")

    # ---------------- Execution & Framing (matching mapping_controller.py) ---------------- #

    @Slot()
    def startRedPreview(self):
        """Frames matrix envelope continuously with red guide laser (matches main.py lines 367-415)."""
        if self._is_framing:
            self._stop_preview()
            return

        if self._exceeds_bounds:
            self.hardwareAlert.emit("Bounds Error", "Parameter matrix exceeds current Galvo lens field boundaries!")
            return

        if self._is_executing:
            self.abort()

        self._is_framing = True
        self._is_aborted = False
        self.isFramingChanged.emit(True)
        self._set_status(f"Framing: {self._total_w:.1f} x {self._total_h:.1f} mm (Continuous)")

        scale, field_size = self._get_scale_and_field_size()
        center_xy = 32767

        # Bounding box corners in galvo units centered at 32767
        margin_left = 16.0 if self._label_axes else 0.0
        margin_bottom = 9.0 if self._label_axes else 0.0
        margin_top = 5.5 if self._label_axes else 0.0
        x0 = int((-self._total_w / 2.0 - margin_left) * scale + center_xy)
        y0 = int((-self._total_h / 2.0 - margin_bottom) * scale + center_xy)
        x1 = int((self._total_w / 2.0) * scale + center_xy)
        y1 = int((self._total_h / 2.0 + margin_top) * scale + center_xy)

        g_min_x = min(x0, x1)
        g_max_x = max(x0, x1)
        g_min_y = min(y0, y1)
        g_max_y = max(y0, y1)

        ctrl = self.galvo_controller
        if ctrl and getattr(ctrl, 'is_connected', False) and getattr(ctrl, 'connection', None):
            try:
                self.preview_thread = PreviewThread(ctrl, g_min_x, g_max_x, g_min_y, g_max_y)
                self.preview_thread.finished_signal.connect(self._on_preview_finished)
                self.preview_thread.start()
            except Exception as e:
                print(f"[MatrixBridge] PreviewThread launch error: {e}")
                self._stop_preview()
        else:
            self._set_status(f"Framing: {self._total_w:.1f} x {self._total_h:.1f} mm (Simulation)")

    def _stop_preview(self):
        if self.preview_thread:
            try:
                self.preview_thread.running = False
                self.preview_thread.wait(400)
            except Exception:
                pass
            self.preview_thread = None

        ctrl = self.galvo_controller
        if ctrl and getattr(ctrl, 'connection', None):
            conn = ctrl.connection
            if hasattr(conn, 'reddot_off'):
                try: conn.reddot_off()
                except Exception: pass
            if hasattr(conn, 'laser_off'):
                try: conn.laser_off()
                except Exception: pass

        self._is_framing = False
        self.isFramingChanged.emit(False)
        self._set_status("Red preview stopped.")

    def _on_preview_finished(self, success):
        self._is_framing = False
        self.isFramingChanged.emit(False)
        self._set_status("Red preview finished.")

    @Slot()
    def startLaserMark(self):
        """Executes parameter matrix burn with dynamic power & frequency (matches mapping_controller.py lines 180-347)."""
        if self._is_framing:
            self._stop_preview()

        if self._exceeds_bounds:
            self.hardwareAlert.emit("Bounds Error", "Matrix exceeds lens field bounds! Reduce steps or cell size.")
            return

        if self._is_executing:
            self.abort()
            return

        if not self._grid_cells:
            return

        self._is_executing = True
        self._is_aborted = False
        self._is_paused = False
        self._active_cell_index = -1
        self.isExecutingChanged.emit(True)
        self.isPausedChanged.emit(False)
        self._set_status(f"Marking matrix ({len(self._grid_cells)} cells)...")

        scale, field_size = self._get_scale_and_field_size()
        center_xy = 32767

        # Speeds math from main.py (jump_speed 2000000, mark_speed scaled)
        jump_speed = 2000000
        raw_mark = float(self._speed)
        if raw_mark > 50000:
            mark_speed = int(raw_mark)
        else:
            mark_speed = int(raw_mark * scale)

        planner = MotionPlanner()
        planner.clear()
        planner.preview_queue = []
        self._cmd_to_cell = {}

        max_r = max((c["row"] for c in self._grid_cells), default=0)

        for idx, cell in enumerate(self._grid_cells):
            r = cell["row"]
            c = cell["col"]
            p_val = float(cell["power"])
            f_val = float(cell["freq"])

            # Galvo coordinates centered at 32767
            x0 = int(cell["x"] * scale + center_xy)
            y0 = int(cell["y"] * scale + center_xy)
            w = int(cell["w"] * scale)
            h = int(cell["h"] * scale)
            x1 = x0 + w
            y1 = y0 + h

            # Dynamic laser parameter modulation command
            planner.preview_queue.append({
                'type': 'set_params',
                'power': p_val,
                'freq': f_val
            })

            # Pass change marker for instantaneous cell index updates
            planner.preview_queue.append({
                'type': 'pass_change',
                'idx': idx
            })

            start_idx = len(planner.preview_queue)

            if self._fill_type == "Vector Outline":
                planner.add_jump(x0, y0, speed=jump_speed)
                planner.add_mark(x1, y0, speed=mark_speed)
                planner.add_mark(x1, y1, speed=mark_speed)
                planner.add_mark(x0, y1, speed=mark_speed)
                planner.add_mark(x0, y0, speed=mark_speed)
            else:
                poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                hatch_configs = [{
                    'enable': True,
                    'type': "Bidirectional",
                    'angle': 0.0,
                    'line_space': 0.05,
                    'count': 1,
                    'pen_no': 0,
                    'hatch_idx': 1
                }]
                planner.generate_hatch([poly], hatch_configs, mark_speed=mark_speed, jump_speed=jump_speed, galvo_units_per_mm=scale)

            end_idx = len(planner.preview_queue)
            for i in range(start_idx, end_idx):
                self._cmd_to_cell[i] = idx

        # Axis labels and titles engraving (with proper names and units matching UI preview)
        if self._label_axes and self._grid_cells:
            digit_speed = min(mark_speed, int(250.0 * scale))

            # Set high contrast parameters for labels
            planner.preview_queue.append({
                'type': 'set_params',
                'power': 85.0,
                'freq': 25.0
            })

            # 1. Frequency labels beside each row (on the left of column 0)
            seen_rows = set()
            for cell in self._grid_cells:
                r = cell["row"]
                if r not in seen_rows:
                    seen_rows.add(r)
                    f_val = float(cell["freq"])
                    f_text = f"{int(round(f_val))} kHz"
                    cell_x_mm = float(cell["x"])
                    cell_y_mm = float(cell["y"])
                    ch_mm = float(cell["h"])
                    target_cx = cell_x_mm - 8.5
                    target_cy = cell_y_mm + ch_mm / 2.0
                    self._draw_stroke_text(f_text, target_cx, target_cy, planner, font_size_mm=2.2, speed=digit_speed, jump_speed=jump_speed)

            # 2. Power labels below each column (below row 0)
            seen_cols = set()
            for cell in self._grid_cells:
                c = cell["col"]
                if c not in seen_cols:
                    seen_cols.add(c)
                    p_val = float(cell["power"])
                    p_text = f"{int(round(p_val))}%"
                    cell_x_mm = float(cell["x"])
                    cell_y_mm = float(cell["y"])
                    cw_mm = float(cell["w"])
                    target_cx = cell_x_mm + cw_mm / 2.0
                    target_cy = cell_y_mm - 3.2
                    self._draw_stroke_text(p_text, target_cx, target_cy, planner, font_size_mm=2.2, speed=digit_speed, jump_speed=jump_speed)

            # 3. Frequency Axis Title ("Freq (kHz)") at top left
            top_y_mm = self._total_h / 2.0
            left_x_mm = -self._total_w / 2.0
            self._draw_stroke_text("Freq (kHz)", left_x_mm - 8.5, top_y_mm + 3.8, planner, font_size_mm=2.5, speed=digit_speed, jump_speed=jump_speed)

            # 4. Laser Power Axis Title ("Laser Power (%)") centered below matrix
            bottom_y_mm = -self._total_h / 2.0
            self._draw_stroke_text("Laser Power (%)", 0.0, bottom_y_mm - 7.0, planner, font_size_mm=2.5, speed=digit_speed, jump_speed=jump_speed)

        ctrl = self.galvo_controller
        if ctrl and getattr(ctrl, 'is_connected', False) and getattr(ctrl, 'connection', None):
            try:
                self.exec_thread = ExecutionThread(ctrl, planner.preview_queue, loop_count=1)
                self.exec_thread.finished_signal.connect(self._on_marking_finished)
                self.exec_thread.progress_signal.connect(self._on_marking_progress)
                self.exec_thread.start()
            except Exception as e:
                print(f"[MatrixBridge] ExecutionThread launch error: {e}")
                self._is_executing = False
                self.isExecutingChanged.emit(False)
                self._set_status(f"Error: {e}")
        else:
            self._run_simulated_marking()

    def _on_marking_progress(self, idx, total, x, y, ctype):
        c_idx = None
        if ctype and str(ctype).startswith("pass_change:"):
            try:
                c_idx = int(str(ctype).split(":")[1])
            except Exception:
                pass
        elif idx in self._cmd_to_cell:
            c_idx = self._cmd_to_cell[idx]

        if c_idx is not None and self._active_cell_index != c_idx:
            self._active_cell_index = c_idx
            self.activeCellIndexChanged.emit(c_idx)
            if 0 <= c_idx < len(self._grid_cells):
                p = self._grid_cells[c_idx]["power"]
                f = self._grid_cells[c_idx]["freq"]
                self._set_status(f"Marking Cell {c_idx+1}/{len(self._grid_cells)}: {p:.0f}% @ {f:.0f} kHz")

    def _on_marking_finished(self, success):
        self._is_executing = False
        self._active_cell_index = -1
        self.activeCellIndexChanged.emit(-1)
        self.isExecutingChanged.emit(False)
        self.isPausedChanged.emit(False)
        self._is_paused = False
        self.exec_thread = None

        if self.galvo_controller and hasattr(self.galvo_controller, 'galvo_home'):
            try:
                self.galvo_controller.galvo_home()
            except Exception:
                pass

        if success:
            self._set_status("Matrix mark complete.")
        else:
            self._set_status("Matrix mark finished." if not self._is_aborted else "Aborted.")

    def _run_simulated_marking(self):
        import threading
        def worker():
            total = len(self._grid_cells)
            for idx in range(total):
                if self._is_aborted:
                    break
                while self._is_paused and not self._is_aborted:
                    time.sleep(0.1)
                self._active_cell_index = idx
                self.activeCellIndexChanged.emit(idx)
                p = self._grid_cells[idx]["power"]
                f = self._grid_cells[idx]["freq"]
                self._set_status(f"Marking Cell {idx+1}/{total}: {p:.0f}% @ {f:.0f} kHz (Sim)")
                time.sleep(0.12)
            self._on_marking_finished(not self._is_aborted)
        threading.Thread(target=worker, daemon=True).start()

    @Slot()
    def togglePause(self):
        if not self._is_executing:
            return
        self._is_paused = not self._is_paused
        if self.galvo_controller:
            self.galvo_controller.is_paused = self._is_paused
        self.isPausedChanged.emit(self._is_paused)
        self._set_status("Paused" if self._is_paused else "Resumed")

    @Slot()
    def abort(self):
        self._is_aborted = True
        self._is_executing = False
        self._is_framing = False
        self._is_paused = False
        self._active_cell_index = -1

        if self.galvo_controller:
            self.galvo_controller.is_paused = False

        if self.preview_thread:
            try:
                self.preview_thread.running = False
                self.preview_thread.wait(400)
            except Exception:
                pass
            self.preview_thread = None

        if self.exec_thread:
            try:
                self.exec_thread.abort()
                self.exec_thread.wait(400)
            except Exception:
                pass
            self.exec_thread = None

        ctrl = self.galvo_controller
        if ctrl and getattr(ctrl, 'connection', None):
            conn = ctrl.connection
            if hasattr(conn, 'laser_off'):
                try: conn.laser_off()
                except Exception: pass
            if hasattr(conn, 'reddot_off'):
                try: conn.reddot_off()
                except Exception: pass
            if hasattr(conn, 'stop'):
                try: conn.stop()
                except Exception: pass

        self.activeCellIndexChanged.emit(-1)
        self.isExecutingChanged.emit(False)
        self.isFramingChanged.emit(False)
        self.isPausedChanged.emit(False)
        self._set_status("Aborted.")
