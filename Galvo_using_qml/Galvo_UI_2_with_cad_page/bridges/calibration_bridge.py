import os
import shutil
import math
import struct
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox, QApplication

from core.calibration import GalvoCalibration
from core.calibration_generator import generate_cor_file
from core.calibration_generator_ui import EZCAD_ORIENTATIONS, TRANSFORMS
from galvo_threads import PreviewThread, ExecutionThread


class CalibrationBridge(QObject):
    """
    Bridge connecting QML UI with EZCAD .cor file loading, inspection,
    and 9-point calibration generation.
    """

    # Signals
    statusChanged = Signal(str)
    calibrationLoaded = Signal()
    stagedCalibrationChanged = Signal()
    parametersChanged = Signal()
    isFramingChanged = Signal(bool)
    isMarkingChanged = Signal(bool)
    orientationChanged = Signal(int)

    def __init__(self, galvo_bridge=None, settings_bridge=None, parent=None):
        super().__init__(parent)
        self.galvo_bridge = galvo_bridge
        self.settings_bridge = settings_bridge

        # Status
        self._status_message = "Ready"

        # Tab 1: Loaded .cor file info
        self._active_cor_path = ""
        self._is_valid = False
        self._signature = ""
        self._scale = 533.89
        self._field_size = 70.0
        self._min_dx = 0
        self._max_dx = 0
        self._min_dy = 0
        self._max_dy = 0
        self._avg_error = 0.0
        self._grid_sample = [] # 11x11 sample grid of (orig_x, orig_y, dx, dy)
        self._active_calibration = None

        # Tab 2: 9-Point Calibration Studio
        self._target_half_width = 25.0 # mm -> 50x50mm field
        self._cal_power = 100.0        # %
        self._cal_freq = 30.0          # kHz
        self._cal_mark_speed = 20.0    # mm/s (slow deep burn)
        self._cal_jump_speed = 200.0   # mm/s
        self._orientation_idx = 0      # 0 to 7 (EZCAD 1 to 8)
        self._is_framing = False
        self._is_marking = False
        self._reddot_thread = None
        self._exec_thread = None
        self._is_aborted = False

        # Nominal and Measured Points (9 points: -W..W)
        self._nominal_points = []
        self._measured_points = []
        self._staged_calibration = None
        self._staged_is_valid = False
        self._staged_avg_error = 0.0

        # Initialize default points
        self._recalc_nominal_points()
        self.resetToNominal()

        # Try to load existing default calibration on startup
        default_cor = os.path.join(os.getcwd(), "newest100mm.cor")
        if os.path.exists(default_cor):
            self.loadCorFile(default_cor)

    # ---------------- Properties: Status & Execution ---------------- #

    @Property(str, notify=statusChanged)
    def statusMessage(self):
        return self._status_message

    def setStatus(self, msg: str):
        self._status_message = msg
        self.statusChanged.emit(msg)

    @Property(bool, notify=isFramingChanged)
    def isFraming(self):
        return self._is_framing

    @Property(bool, notify=isMarkingChanged)
    def isMarking(self):
        return self._is_marking

    # ---------------- Properties: Loaded .COR File ---------------- #

    @Property(str, notify=calibrationLoaded)
    def activeCorPath(self):
        return self._active_cor_path

    @Property(str, notify=calibrationLoaded)
    def activeCorFileName(self):
        return os.path.basename(self._active_cor_path) if self._active_cor_path else "None"

    @Property(bool, notify=calibrationLoaded)
    def isValid(self):
        return self._is_valid

    @Property(str, notify=calibrationLoaded)
    def signature(self):
        return self._signature

    @Property(float, notify=calibrationLoaded)
    def scale(self):
        return self._scale

    @Property(float, notify=calibrationLoaded)
    def fieldSize(self):
        return self._field_size

    @Property(int, notify=calibrationLoaded)
    def minDx(self):
        return self._min_dx

    @Property(int, notify=calibrationLoaded)
    def maxDx(self):
        return self._max_dx

    @Property(int, notify=calibrationLoaded)
    def minDy(self):
        return self._min_dy

    @Property(int, notify=calibrationLoaded)
    def maxDy(self):
        return self._max_dy

    @Property(float, notify=calibrationLoaded)
    def avgErrorMm(self):
        return self._avg_error

    @Property("QVariantList", notify=calibrationLoaded)
    def gridSample(self):
        """Returns 11x11 sample points for QML distortion grid preview."""
        return self._grid_sample

    # ---------------- Properties: 9-Point Studio ---------------- #

    @Property(float, notify=parametersChanged)
    def targetHalfWidth(self):
        return self._target_half_width

    @targetHalfWidth.setter
    def targetHalfWidth(self, val: float):
        if val > 0 and val != self._target_half_width:
            self._target_half_width = val
            self._recalc_nominal_points()
            self.resetToNominal()
            self.parametersChanged.emit()

    @Property(float, notify=parametersChanged)
    def nominalFieldSize(self):
        return self._target_half_width * 2.0

    @Property(float, notify=parametersChanged)
    def calPower(self):
        return self._cal_power

    @calPower.setter
    def calPower(self, val: float):
        self._cal_power = max(0.0, min(100.0, val))
        self.parametersChanged.emit()

    @Property(float, notify=parametersChanged)
    def calFreq(self):
        return self._cal_freq

    @calFreq.setter
    def calFreq(self, val: float):
        self._cal_freq = max(20.0, min(80.0, val))
        self.parametersChanged.emit()

    @Property(float, notify=parametersChanged)
    def calMarkSpeed(self):
        return self._cal_mark_speed

    @calMarkSpeed.setter
    def calMarkSpeed(self, val: float):
        self._cal_mark_speed = max(1.0, val)
        self.parametersChanged.emit()

    @Property(float, notify=parametersChanged)
    def calJumpSpeed(self):
        return self._cal_jump_speed

    @calJumpSpeed.setter
    def calJumpSpeed(self, val: float):
        self._cal_jump_speed = max(1.0, val)
        self.parametersChanged.emit()

    @Property(int, notify=orientationChanged)
    def orientationIndex(self):
        return self._orientation_idx

    @orientationIndex.setter
    def orientationIndex(self, val: int):
        self._orientation_idx = val % 8
        self.orientationChanged.emit(self._orientation_idx)

    @Property(str, notify=orientationChanged)
    def orientationName(self):
        return f"Orientation {self._orientation_idx + 1}"

    @Property("QVariantList", notify=parametersChanged)
    def nominalPoints(self):
        return [{"x": pt[0], "y": pt[1]} for pt in self._nominal_points]

    @Property("QVariantList", notify=parametersChanged)
    def measuredPoints(self):
        return [{"x": pt[0], "y": pt[1]} for pt in self._measured_points]

    @Property(bool, notify=stagedCalibrationChanged)
    def stagedIsValid(self):
        return self._staged_is_valid

    @Property(float, notify=stagedCalibrationChanged)
    def stagedAvgError(self):
        return self._staged_avg_error

    # ---------------- Tab 1: Load, Inspect & Activate ---------------- #

    @Slot(result=bool)
    def openCorFileDialog(self):
        """Native file dialog to select a .cor file."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open EZCAD Calibration File",
            os.getcwd(),
            "EZCAD Cor Files (*.cor);;All Files (*)"
        )
        if file_path:
            return self.loadCorFile(file_path)
        return False

    @Slot(str, result=bool)
    def loadCorFile(self, file_path: str):
        """Loads and parses a binary EZCAD .cor file."""
        if not file_path or not os.path.exists(file_path):
            self.setStatus(f"File not found: {file_path}")
            return False

        try:
            cal = GalvoCalibration(file_path)
            if not cal.is_valid:
                self.setStatus("Error: Invalid or corrupted EZCAD .cor file.")
                return False

            self._active_calibration = cal
            self._active_cor_path = os.path.abspath(file_path)
            self._is_valid = True
            self._scale = float(cal.scale or 533.89)
            self._field_size = round(65535.0 / self._scale, 2) if self._scale > 0 else 70.0

            # Header signature
            with open(file_path, "rb") as f:
                header = f.read(40)
                sig_raw = header[0:20].split(b"\x00")[0]
                self._signature = sig_raw.decode("ascii", errors="ignore") or "JCZ_COR"

            # Compute delta statistics
            all_dx = [pt[0] for row in cal.grid for pt in row]
            all_dy = [pt[1] for row in cal.grid for pt in row]
            self._min_dx = int(min(all_dx))
            self._max_dx = int(max(all_dx))
            self._min_dy = int(min(all_dy))
            self._max_dy = int(max(all_dy))

            # RMS average error in mm
            squared_errs = [((dx**2 + dy**2)**0.5) / self._scale for dx, dy in zip(all_dx, all_dy)]
            self._avg_error = round(sum(squared_errs) / len(squared_errs), 4)

            # Sample 11x11 grid points (stride = 6 across 65x65)
            samples = []
            for r_idx in range(0, 65, 6):
                for c_idx in range(0, 65, 6):
                    dx, dy = cal.grid[r_idx][c_idx]
                    norm_x = (r_idx - 32) / 32.0 # -1.0 to 1.0
                    norm_y = (c_idx - 32) / 32.0 # -1.0 to 1.0
                    samples.append({
                        "nx": norm_x,
                        "ny": norm_y,
                        "dx": dx,
                        "dy": dy,
                        "dx_mm": round(dx / self._scale, 3),
                        "dy_mm": round(dy / self._scale, 3)
                    })
            self._grid_sample = samples

            self.setStatus(f"Loaded {os.path.basename(file_path)} (Scale: {self._scale:.2f} bits/mm)")
            self.calibrationLoaded.emit()
            return True

        except Exception as e:
            self.setStatus(f"Failed to load calibration: {e}")
            return False

    @Slot(result=bool)
    def applyToHardware(self):
        """Loads the active calibration into the hardware controller."""
        if not self._is_valid or not self._active_cor_path:
            self.setStatus("No valid calibration loaded to apply.")
            return False

        try:
            applied = False
            if self.galvo_bridge and hasattr(self.galvo_bridge, "controller") and self.galvo_bridge.controller:
                conn = getattr(self.galvo_bridge.controller, "connection", None)
                if conn and hasattr(conn, "calibration"):
                    conn.calibration.load_calibration(self._active_cor_path)
                    conn.enable_calibration = True
                    applied = True

            if applied:
                self.setStatus(f"Active hardware calibration updated: {self.activeCorFileName}")
                return True
            else:
                self.setStatus("Calibration staged (Hardware simulation active).")
                return True
        except Exception as e:
            self.setStatus(f"Error applying to hardware: {e}")
            return False

    @Slot(result=bool)
    def saveAsDefaultStartupCor(self):
        """Copies the active calibration to newest100mm.cor so it persists on boot."""
        if not self._is_valid or not self._active_cor_path:
            self.setStatus("No valid calibration loaded to save.")
            return False

        try:
            target_file = os.path.join(os.getcwd(), "newest100mm.cor")
            shutil.copyfile(self._active_cor_path, target_file)
            self.setStatus(f"Persisted {self.activeCorFileName} as default startup newest100mm.cor")
            return True
        except Exception as e:
            self.setStatus(f"Error persisting default calibration: {e}")
            return False

    # ---------------- Tab 2: 9-Point Studio Logic ---------------- #

    def _recalc_nominal_points(self):
        w = self._target_half_width
        self._nominal_points = [
            (-w, w),  (0.0, w),  (w, w),
            (-w, 0.0), (0.0, 0.0), (w, 0.0),
            (-w, -w), (0.0, -w), (w, -w)
        ]

    @Slot()
    def resetToNominal(self):
        """Resets all 9 measured points to nominal values."""
        self._recalc_nominal_points()
        self._measured_points = list(self._nominal_points)
        self.parametersChanged.emit()
        self.setStatus("Measured points reset to nominal.")

    @Slot(int, float, float)
    def updateMeasuredPoint(self, index: int, x: float, y: float):
        """Updates measured caliper coordinate for a single point (0..8)."""
        if 0 <= index < 9:
            self._measured_points[index] = (x, y)
            self.parametersChanged.emit()

    @Slot()
    def nextOrientation(self):
        """Cycles through the 8 standard EZCAD physical orientations."""
        self._orientation_idx = (self._orientation_idx + 1) % 8
        self.orientationChanged.emit(self._orientation_idx)
        self.setStatus(f"Switched to Orientation {self._orientation_idx + 1} of 8")

    @Slot(result=dict)
    def getOrientationInfo(self):
        """Returns details for current orientation (square/diamond coords, tick p1/p2)."""
        cur = EZCAD_ORIENTATIONS[self._orientation_idx]
        return {
            "name": str(self._orientation_idx + 1),
            "sq_x": cur["sq"][0],
            "sq_y": cur["sq"][1],
            "di_x": cur["di"][0],
            "di_y": cur["di"][1],
            "tick_p1_x": cur["tick_p1"][0],
            "tick_p1_y": cur["tick_p1"][1],
            "tick_p2_x": cur["tick_p2"][0],
            "tick_p2_y": cur["tick_p2"][1]
        }

    # ---------------- Laser & Marking Actions ---------------- #

    @Slot()
    def toggleRedDotFraming(self):
        """Toggles continuous red-dot laser framing of the calibration boundary."""
        if self._is_framing:
            self.stopRedDotFraming()
            return

        controller = getattr(self.galvo_bridge, "controller", None) if self.galvo_bridge else None
        if not controller or not getattr(controller, "is_connected", False):
            self.setStatus("Warning: Hardware controller not connected (simulating red dot).")

        scale = self._scale or 533.89
        hw = int(self._target_half_width * scale)
        c = 32767
        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw

        self._reddot_thread = PreviewThread(controller, min_x, max_x, min_y, max_y)
        self._reddot_thread.finished_signal.connect(self._on_reddot_finished)
        self._reddot_thread.start()

        self._is_framing = True
        self.isFramingChanged.emit(True)
        self.setStatus(f"Red Dot Framing Active: {self._target_half_width * 2:.1f} x {self._target_half_width * 2:.1f} mm")

    @Slot()
    def stopRedDotFraming(self):
        """Stops red-dot framing thread."""
        if self._reddot_thread:
            self._reddot_thread.running = False
            self._reddot_thread.wait()
            self._reddot_thread = None

        controller = getattr(self.galvo_bridge, "controller", None) if self.galvo_bridge else None
        if controller and hasattr(controller, "connection"):
            conn = controller.connection
            if hasattr(conn, "reddot_off"):
                conn.reddot_off()

        self._is_framing = False
        self.isFramingChanged.emit(False)
        self.setStatus("Red Dot Framing Stopped.")

    def _on_reddot_finished(self, success):
        self.stopRedDotFraming()

    @Slot()
    def markCalibrationGrid(self):
        """
        Marks the official 9-point EZCAD calibration pattern on physical plate:
        outer boundary, extended crosshair, numbered digits 1-9, square, diamond, tick.
        """
        self.stopRedDotFraming()
        self._is_aborted = False

        controller = getattr(self.galvo_bridge, "controller", None) if self.galvo_bridge else None
        if not controller:
            self.setStatus("Error: Galvo controller unavailable.")
            return

        scale = self._scale or 533.89
        field_size = 65535.0 / scale if scale > 0 else 70.0
        galvo_units_per_mm = scale
        c = 32767
        hw = int(self._target_half_width * galvo_units_per_mm)

        min_x, max_x = c - hw, c + hw
        min_y, max_y = c - hw, c + hw

        # Speed calculation
        mark_speed = int(self._cal_mark_speed * galvo_units_per_mm)
        jump_speed = int(self._cal_jump_speed * galvo_units_per_mm)

        queue = []

        def jump(x, y):
            queue.append({"type": "jump", "x": int(x), "y": int(y), "speed": jump_speed})
            queue.append({"type": "delay", "ms": 5})

        def mark(x, y):
            queue.append({"type": "mark", "x": int(x), "y": int(y), "speed": mark_speed})
            queue.append({"type": "flush"})
            queue.append({"type": "delay", "ms": 2})

        def draw_digit(d, x0, y0):
            dw = int(2.5 * galvo_units_per_mm)
            dh = int(5.0 * galvo_units_per_mm)
            x1 = x0 + dw
            y1 = int(y0 - dh / 2.0)
            y2 = y0 - dh
            if d == 1: jump(x1, y0); mark(x1, y2)
            elif d == 2: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); mark(x0, y2); mark(x1, y2)
            elif d == 3: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); jump(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 4: jump(x0, y0); mark(x0, y1); mark(x1, y1); jump(x1, y0); mark(x1, y2)
            elif d == 5: jump(x1, y0); mark(x0, y0); mark(x0, y1); mark(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 6: jump(x1, y0); mark(x0, y0); mark(x0, y2); mark(x1, y2); mark(x1, y1); mark(x0, y1)
            elif d == 7: jump(x0, y0); mark(x1, y0); mark(x1, y2)
            elif d == 8: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0); jump(x0, y1); mark(x1, y1)
            elif d == 9: jump(x1, y1); mark(x0, y1); mark(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2)

        # 1. Outer square
        jump(min_x, max_y)
        mark(max_x, max_y)
        mark(max_x, min_y)
        mark(min_x, min_y)
        mark(min_x, max_y)

        # 2. Extended crosshairs (10% extension)
        ext = int(hw * 0.1)
        jump(c, max_y + ext)
        mark(c, min_y - ext)
        jump(min_x - ext, c)
        mark(max_x + ext, c)

        # 3. Small square marker inside Point 1 (Top-Left)
        ms = int(2.0 * galvo_units_per_mm)
        o = int(ms / 1.5)
        sq_x, sq_y = min_x + o, max_y - o
        jump(sq_x, sq_y)
        mark(sq_x + ms, sq_y)
        mark(sq_x + ms, sq_y - ms)
        mark(sq_x, sq_y - ms)
        mark(sq_x, sq_y)

        # 4. Small diamond marker inside Point 9 (Bottom-Right)
        d_cx = max_x - o - int(ms / 2)
        d_cy = min_y + o + int(ms / 2)
        d_r = int(ms / 2)
        jump(d_cx, d_cy + d_r)
        mark(d_cx + d_r, d_cy)
        mark(d_cx, d_cy - d_r)
        mark(d_cx - d_r, d_cy)
        mark(d_cx, d_cy + d_r)

        # 5. Center tick mark
        tick_x = c + int(hw * 0.15)
        jump(tick_x, c + int(hw * 0.15))
        mark(tick_x, c - int(hw * 0.15))

        # 6. Digital numbers 1 through 9
        pd = int(2.0 * galvo_units_per_mm)
        dh_half = int(2.5 * galvo_units_per_mm)
        dw = int(2.5 * galvo_units_per_mm)
        dh = int(5.0 * galvo_units_per_mm)

        draw_digit(1, min_x - dw - pd, max_y + dh + pd)
        draw_digit(2, c - int(dw / 2), max_y + dh + pd)
        draw_digit(3, max_x + pd, max_y + dh + pd)
        draw_digit(4, min_x - dw - pd, c + dh_half)
        draw_digit(5, c + pd, c + dh + pd)
        draw_digit(6, max_x + pd, c + dh_half)
        draw_digit(7, min_x - dw - pd, min_y - pd)
        draw_digit(8, c - int(dw / 2), min_y - pd)
        draw_digit(9, max_x + pd, min_y - pd)

        # Apply live laser power & frequency
        controller.live_power = self._cal_power
        controller.live_freq = self._cal_freq

        # Dispatch via ExecutionThread
        self._is_marking = True
        self.isMarkingChanged.emit(True)
        self.setStatus("Marking 9-Point Calibration Grid on plate...")

        self._exec_thread = ExecutionThread(controller, queue)
        self._exec_thread.finished_signal.connect(self._on_marking_finished)
        self._exec_thread.start()

    def _on_marking_finished(self, success):
        self._is_marking = False
        self.isMarkingChanged.emit(False)
        self._exec_thread = None
        if success:
            self.setStatus("Grid Marked Successfully! Measure 9 points with calipers.")
        else:
            self.setStatus("Marking stopped or aborted.")

    @Slot()
    def stopLaser(self):
        """Immediately halts any laser marking or red dot framing operation."""
        self._is_aborted = True
        self.stopRedDotFraming()

        if self._exec_thread:
            self._exec_thread.abort()
            self._exec_thread.wait()
            self._exec_thread = None

        controller = getattr(self.galvo_bridge, "controller", None) if self.galvo_bridge else None
        if controller and hasattr(controller, "connection") and controller.connection:
            conn = controller.connection
            if hasattr(conn, "laser_off"): conn.laser_off()
            if hasattr(conn, "reddot_off"): conn.reddot_off()
            if hasattr(conn, "stop"): conn.stop()

        self._is_marking = False
        self.isMarkingChanged.emit(False)
        self.setStatus("Laser Stopped / Aborted.")

    # ---------------- Calculate & Generate .COR ---------------- #

    @Slot(result="QVariantMap")
    def calculateAndStageCalibration(self):
        """
        Computes 65x65 biquadratic calibration grid from 9 measured points
        and the active EZCAD orientation, saving to staged_calibration.cor.
        """
        self.setStatus("Calculating 65x65 biquadratic correction grid...")

        try:
            # Map user measurements according to hardware coordinate swap (TRANSFORMS[7])
            # Hardware natively swaps physical X and Y
            transform_swap = [8, 5, 2, 7, 4, 1, 6, 3, 0]
            galvo_measurements = [None] * 9

            for galvo_idx in range(9):
                ui_idx = transform_swap[galvo_idx]
                raw_x, raw_y = self._measured_points[ui_idx]
                galvo_measurements[galvo_idx] = (raw_y, raw_x)

            scale = self._scale or 533.89
            W = self._target_half_width
            nominals = [
                (-W, W), (0, W), (W, W),
                (-W, 0), (0, 0), (W, 0),
                (-W, -W), (0, -W), (W, -W)
            ]

            err_sum = sum(math.hypot(galvo_measurements[i][0] - nominals[i][0], galvo_measurements[i][1] - nominals[i][1]) for i in range(9))
            avg_err = round(err_sum / 9.0, 4)
            self._staged_avg_error = avg_err

            staged_path = os.path.join(os.getcwd(), "staged_calibration.cor")
            generate_cor_file(staged_path, scale, W, galvo_measurements)

            # Load into staged calibration object
            staged_cal = GalvoCalibration(staged_path)
            if staged_cal.is_valid:
                self._staged_calibration = staged_cal
                self._staged_is_valid = True
                self.stagedCalibrationChanged.emit()
                self.setStatus(f"Calibration Computed: Avg error {avg_err:.3f} mm. Staged for verification.")
                return {
                    "success": True,
                    "avg_error_mm": avg_err,
                    "staged_path": staged_path,
                    "message": f"Successfully generated staged_calibration.cor!\nMean distortion: {avg_err:.3f} mm."
                }
            else:
                self._staged_is_valid = False
                self.stagedCalibrationChanged.emit()
                self.setStatus("Failed to validate staged calibration.")
                return {"success": False, "message": "Failed to validate generated .cor file."}

        except Exception as e:
            self._staged_is_valid = False
            self.stagedCalibrationChanged.emit()
            self.setStatus(f"Calibration calculation error: {e}")
            return {"success": False, "message": str(e)}

    @Slot()
    def markVerificationShape(self):
        """
        Marks a verification test square and crosshair with the staged calibration applied.
        """
        if not self._staged_calibration or not self._staged_is_valid:
            self.setStatus("Error: Calculate & stage calibration before marking verification shape.")
            return

        controller = getattr(self.galvo_bridge, "controller", None) if self.galvo_bridge else None
        if not controller:
            self.setStatus("Error: Controller unavailable.")
            return

        scale = self._scale or 533.89
        galvo_units_per_mm = scale
        c = 32767
        hw = int(self._target_half_width * galvo_units_per_mm)
        cross_hw = int(hw * 0.15)

        min_x, max_x = c - hw, c + hw
        min_y, max_y = c - hw, c + hw

        mark_speed = int(self._cal_mark_speed * galvo_units_per_mm)
        jump_speed = int(self._cal_jump_speed * galvo_units_per_mm)

        queue = []

        def jump(x, y):
            cx, cy = self._staged_calibration.apply(float(x), float(y))
            queue.append({"type": "jump", "x": int(cx), "y": int(cy), "speed": jump_speed})

        def mark(x, y):
            cx, cy = self._staged_calibration.apply(float(x), float(y))
            queue.append({"type": "mark", "x": int(cx), "y": int(cy), "speed": mark_speed})
            queue.append({"type": "flush"})
            queue.append({"type": "delay", "ms": 2})

        # 1. Outer Square
        jump(min_x, max_y)
        mark(max_x, max_y)
        mark(max_x, min_y)
        mark(min_x, min_y)
        mark(min_x, max_y)

        # 2. Central crosshair
        jump(c, c + cross_hw)
        mark(c, c - cross_hw)
        jump(c - cross_hw, c)
        mark(c + cross_hw, c)

        controller.live_power = self._cal_power
        controller.live_freq = self._cal_freq

        self._is_marking = True
        self.isMarkingChanged.emit(True)
        self.setStatus("Marking Calibrated Verification Shape...")

        self._exec_thread = ExecutionThread(controller, queue)
        self._exec_thread.finished_signal.connect(self._on_marking_finished)
        self._exec_thread.start()

    @Slot(result=bool)
    def saveAndApplyStagedCalibration(self):
        """
        Prompts user to save staged_calibration.cor to target path,
        overwrites default newest100mm.cor, and activates it in the hardware.
        """
        if not self._staged_calibration or not self._staged_is_valid:
            self.setStatus("No valid staged calibration to apply.")
            return False

        save_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Calibration File",
            os.path.join(os.getcwd(), "my_galvo_calibration.cor"),
            "EZCAD Cor Files (*.cor);;All Files (*)"
        )
        if not save_path:
            return False

        try:
            staged_path = os.path.join(os.getcwd(), "staged_calibration.cor")
            shutil.copyfile(staged_path, save_path)

            # Overwrite default newest100mm.cor
            default_path = os.path.join(os.getcwd(), "newest100mm.cor")
            shutil.copyfile(staged_path, default_path)

            # Apply directly into active hardware
            applied = False
            if self.galvo_bridge and hasattr(self.galvo_bridge, "controller") and self.galvo_bridge.controller:
                conn = getattr(self.galvo_bridge.controller, "connection", None)
                if conn and hasattr(conn, "calibration"):
                    conn.calibration.load_calibration(save_path)
                    conn.enable_calibration = True
                    applied = True

            # Load into Tab 1 as active calibration
            self.loadCorFile(save_path)

            self.setStatus(f"Successfully saved and applied {os.path.basename(save_path)} to hardware!")
            return True

        except Exception as e:
            self.setStatus(f"Error saving and applying calibration: {e}")
            return False

