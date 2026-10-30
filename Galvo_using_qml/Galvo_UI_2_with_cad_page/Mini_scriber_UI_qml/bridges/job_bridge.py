import os
import re
import math
import time
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer, QUrl
from dxf import DXFParser
from gerber_parser import GerberParser
from util import ConfigHandler, FileHandler

class JobBridge(QObject):
    fileLoaded = Signal()
    jobStateChanged = Signal(str)
    progressChanged = Signal(float, int, int)
    timeUpdated = Signal(int, int)
    laserFiringChanged = Signal(bool)
    toolpathReady = Signal()
    parametersChanged = Signal()
    statusAlert = Signal(str)
    alignmentModeChanged = Signal(str)
    boundaryWarning = Signal(str, str, bool, float, float)
    isOutOfBoundsChanged = Signal()
    laserHeadMoved = Signal(float, float)

    def __init__(self, serial_bridge, motion_bridge, settings_bridge=None, parent=None):
        super().__init__(parent)
        self._serial = serial_bridge
        self._motion = motion_bridge
        self._settings = settings_bridge
        self._serial.add_response_listener(self._handle_serial_response)

        self._file_path = ""
        self._file_name = "No file loaded"
        self._commands = []
        self._current_index = 0
        self._state = "Idle"  # Idle, Ready, Running, Paused, Complete, Aborted
        self._progress = 0.0

        # Timing & Real-Time ETA State
        self._job_start_time = 0.0
        self._job_pause_time = 0.0
        self._job_paused_duration = 0.0
        self._elapsed_seconds = 0
        self._remaining_seconds = 0
        self._total_estimated_seconds = 0
        self._is_laser_firing = False

        self._time_timer = QTimer(self)
        self._time_timer.setInterval(1000)
        self._time_timer.timeout.connect(self._on_time_tick)

        # Boundary & Sizing state (matching main.py)
        self._is_out_of_bounds = False
        self._is_too_large = False
        self._boundary_title = ""
        self._boundary_message = ""
        self._can_shift = False
        self._raw_design_w = 0.0
        self._raw_design_h = 0.0

        # Alignment mode: "index" (starts from physical index point) or "center" (centered on bed)
        self._alignment_mode = "index"

        # Design & Machine Parameters
        self._sample_height = 1.0  # mm
        self._feed_rate = 1000.0   # mm/min
        self._selected_laser = "Laser 1"
        self._focus = 10.0
        self._zpos = 9.0

        # Vector toolpath segments for QML canvas: list of dicts {x1, y1, x2, y2, laser}
        self._toolpath_segments = []
        self._min_x = 0.0
        self._max_x = 100.0
        self._min_y = 0.0
        self._max_y = 100.0

        # Helper instances
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_file_path = os.path.join(app_dir, "config", "config.ini")
        self._ch = ConfigHandler()
        self._fh = FileHandler()

        self._jog_feed = 1000.0
        self._active_feed = 500.0
        self._seg_start_x = 0.0
        self._seg_start_y = 0.0
        self._seg_target_x = 0.0
        self._seg_target_y = 0.0
        self._seg_duration = 0.0
        self._seg_elapsed = 0.0
        self._seg_progress = 1.0
        self._head_x = 0.0
        self._head_y = 0.0
        self._last_sim_tick = time.time()

        # Offline simulation timer (40 FPS high-resolution interpolation)
        self._exec_timer = QTimer(self)
        self._exec_timer.setInterval(25)
        self._exec_timer.timeout.connect(self._step_job_simulation)

        if self._settings:
            self._settings.hardwareConfigChanged.connect(self._on_hardware_changed)

    def _on_hardware_changed(self):
        if self._settings and self._settings.laserCount == 1:
            if self._selected_laser != "Laser 1":
                self._selected_laser = "Laser 1"
                self.parametersChanged.emit()
        if self._file_path and os.path.exists(self._file_path):
            self.processAndGenerate()

    def _read_config_laser_focus(self, laser_name: str) -> float:
        """Reads calibrated focus for the specified laser from config.ini."""
        if not os.path.exists(self._config_file_path):
            return 10.0
        try:
            self._ch.ini_parser.read(self._config_file_path)
            focus_dict = self._ch.getSection("focus")
            if focus_dict:
                for k, v in focus_dict.items():
                    clean_v = v.replace('{', '').replace('}', '').replace("'", "")
                    if ':' in clean_v:
                        parts = clean_v.split(':')
                        name = parts[0].strip()
                        val = float(parts[1].strip())
                        if name.lower() == laser_name.lower():
                            return val
        except Exception as e:
            print(f"[JobBridge] Error reading laser focus: {e}")
        return 10.0

    def _read_config_offsets(self):
        """Reads index and dual-laser offsets from config.ini."""
        xindex, yindex = 0.0, 0.0
        offset_laser = "Laser 2"
        xoffset, yoffset = 0.0, 0.0

        if not os.path.exists(self._config_file_path):
            return xindex, yindex, offset_laser, xoffset, yoffset

        try:
            self._ch.ini_parser.read(self._config_file_path)
            xi = self._ch.getValues("index", "xindex")
            yi = self._ch.getValues("index", "yindex")
            if xi: xindex = float(xi)
            if yi: yindex = float(yi)

            ol = self._ch.getValues("offset", "laser")
            if ol: offset_laser = ol.strip()
            xo = self._ch.getValues("offset", "xoffset")
            yo = self._ch.getValues("offset", "yoffset")
            if xo: xoffset = float(xo)
            if yo: yoffset = float(yo)
        except Exception as e:
            print(f"[JobBridge] Error reading offsets: {e}")

        return xindex, yindex, offset_laser, xoffset, yoffset

    @Slot(str)
    def _handle_serial_response(self, text: str):
        """M400 + M114 closed-loop feedback step from firmware."""
        if self._state == "Running" and self._serial.connected:
            if "X:" in text and "Y:" in text:
                xm = re.search(r'X:([-\d\.]+)', text)
                ym = re.search(r'Y:([-\d\.]+)', text)
                if xm and ym:
                    try:
                        rx = float(xm.group(1))
                        ry = float(ym.group(1))
                        self._seg_start_x = rx
                        self._seg_start_y = ry
                        self._seg_target_x = rx
                        self._seg_target_y = ry
                    except ValueError:
                        pass
                self._step_job_hardware()

    # --- Properties ---
    @Property(str, notify=fileLoaded)
    def fileName(self):
        return self._file_name

    @Property(str, notify=fileLoaded)
    def filePath(self):
        return self._file_path

    @Property(int, notify=fileLoaded)
    def totalCommands(self):
        return len(self._commands)

    @Property(int, notify=progressChanged)
    def currentCommand(self):
        return self._current_index

    @Property(float, notify=progressChanged)
    def progress(self):
        return self._progress

    @Property(str, notify=jobStateChanged)
    def state(self):
        return self._state

    def _format_time(self, seconds: int) -> str:
        s = max(0, int(seconds))
        m = s // 60
        sec = s % 60
        if m >= 60:
            h = m // 60
            m = m % 60
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"

    def _on_time_tick(self):
        if self._state == "Running":
            now = time.time()
            self._elapsed_seconds = max(0, int(now - self._job_start_time - self._job_paused_duration))
            if self._progress > 2.0:
                projected_total = self._elapsed_seconds / (self._progress / 100.0)
                self._remaining_seconds = max(0, int(projected_total - self._elapsed_seconds))
            else:
                self._remaining_seconds = max(0, int(self._total_estimated_seconds - self._elapsed_seconds))
            self.timeUpdated.emit(self._elapsed_seconds, self._remaining_seconds)

    @Property(str, notify=timeUpdated)
    def elapsedTime(self):
        return self._format_time(self._elapsed_seconds)

    @Property(str, notify=timeUpdated)
    def remainingTime(self):
        return self._format_time(self._remaining_seconds)

    @Property(str, notify=parametersChanged)
    def totalEstimatedTime(self):
        return self._format_time(self._total_estimated_seconds)

    @Property(int, notify=timeUpdated)
    def elapsedSeconds(self):
        return self._elapsed_seconds

    @Property(int, notify=timeUpdated)
    def remainingSeconds(self):
        return self._remaining_seconds

    @Property(int, notify=parametersChanged)
    def totalEstimatedSeconds(self):
        return self._total_estimated_seconds

    @Property(bool, notify=laserFiringChanged)
    def isLaserFiring(self):
        return self._is_laser_firing

    @Property(float, notify=laserHeadMoved)
    def headX(self):
        return round(self._head_x, 3)

    @Property(float, notify=laserHeadMoved)
    def headY(self):
        return round(self._head_y, 3)

    @Property(float, notify=laserHeadMoved)
    def segmentProgress(self):
        return round(self._seg_progress, 3)

    @Property(list, notify=toolpathReady)
    def toolpathSegments(self):
        return self._toolpath_segments

    @Property(float, notify=fileLoaded)
    def minX(self): return self._min_x

    @Property(float, notify=fileLoaded)
    def maxX(self): return self._max_x

    @Property(float, notify=fileLoaded)
    def minY(self): return self._min_y

    @Property(float, notify=fileLoaded)
    def maxY(self): return self._max_y

    @Property(float, notify=fileLoaded)
    def designWidth(self): return max(0.0, self._max_x - self._min_x)

    @Property(float, notify=fileLoaded)
    def designHeight(self): return max(0.0, self._max_y - self._min_y)

    @Property(int, notify=toolpathReady)
    def cutCount(self): return sum(1 for s in self._toolpath_segments if s.get('laser'))

    @Property(int, notify=toolpathReady)
    def travelCount(self): return sum(1 for s in self._toolpath_segments if not s.get('laser'))

    # Design Parameters Properties
    @Property(float, notify=parametersChanged)
    def sampleHeight(self):
        return self._sample_height

    @Property(float, notify=parametersChanged)
    def feedRate(self):
        return self._feed_rate

    @Property(str, notify=parametersChanged)
    def selectedLaser(self):
        return self._selected_laser

    @Property(float, notify=parametersChanged)
    def calculatedZpos(self):
        return self._zpos

    @Property(str, notify=alignmentModeChanged)
    def alignmentMode(self):
        return self._alignment_mode

    # Boundary & Sizing Properties (matching main.py)
    @Property(bool, notify=isOutOfBoundsChanged)
    def isOutOfBounds(self):
        return self._is_out_of_bounds

    @Property(bool, notify=isOutOfBoundsChanged)
    def isTooLarge(self):
        return self._is_too_large

    @Property(str, notify=isOutOfBoundsChanged)
    def boundaryTitle(self):
        return self._boundary_title

    @Property(str, notify=isOutOfBoundsChanged)
    def boundaryMessage(self):
        return self._boundary_message

    @Property(bool, notify=isOutOfBoundsChanged)
    def canShiftToFit(self):
        return self._can_shift

    @Property(float, notify=fileLoaded)
    def rawDesignWidth(self):
        return self._raw_design_w

    @Property(float, notify=fileLoaded)
    def rawDesignHeight(self):
        return self._raw_design_h

    @Slot(str)
    def setAlignmentMode(self, mode: str):
        clean_mode = str(mode).strip().lower()
        if clean_mode in ["index", "center"] and self._alignment_mode != clean_mode:
            self._alignment_mode = clean_mode
            self.alignmentModeChanged.emit(self._alignment_mode)
            self.processAndGenerate()

    @Slot()
    def adjustToIndex(self):
        self.setAlignmentMode("index")

    @Slot()
    def adjustToCenter(self):
        self.setAlignmentMode("center")

    @Slot()
    def shiftToFit(self):
        """Automatically centers or shifts the design to fit within bed boundaries, matching main.py QMessageBox.Yes."""
        self.adjustToCenter()

    @Slot()
    def dismissBoundaryWarning(self):
        pass

    @Slot()
    def showBoundaryWarning(self):
        """Re-emits the boundary warning signal to show the modal dialog."""
        if self._is_out_of_bounds:
            self.boundaryWarning.emit(self._boundary_title, self._boundary_message, self._can_shift, self._raw_design_w, self._raw_design_h)

    # --- Slots: Parameters ---
    @Slot(float)
    def setSampleHeight(self, val: float):
        if val >= 0 and self._sample_height != val:
            self._sample_height = val
            self.processAndGenerate()

    @Slot(float)
    def setFeedRate(self, val: float):
        if val > 0 and self._feed_rate != val:
            self._feed_rate = val
            self.processAndGenerate()

    def pgmGcode(self, gstr: str) -> str:
        """
        Converts standard M3 / M5 laser commands into hardware PWM port assignments
        matching main.py pgmGcode() and initLaser():
        Laser 1:
            M3 -> M106 P0 S255
            M5 -> M106 P0 S0
        Laser 2:
            M3 -> M106 P1 S255
            M5 -> M106 P1 S0
        """
        p_chan = 0 if "1" in str(self._selected_laser) else 1
        cmd_strip = gstr.strip()

        # Handle M3 (ON)
        if re.match(r'^M0?3\b', cmd_strip, re.IGNORECASE):
            return f"M106 P{p_chan} S255"
        # Handle M5 (OFF)
        elif re.match(r'^M0?5\b', cmd_strip, re.IGNORECASE):
            return f"M106 P{p_chan} S0"

        return cmd_strip

    @Slot(str)
    @Slot(int)
    def setSelectedLaser(self, val):
        if self._settings and self._settings.laserCount == 1:
            target = "Laser 1"
        else:
            s_val = str(val).strip()
            if s_val in ["1", "Laser 1"]:
                target = "Laser 1"
            elif s_val in ["2", "Laser 2"]:
                target = "Laser 2"
            else:
                return

        if self._selected_laser != target:
            self._selected_laser = target
            self.parametersChanged.emit()
            self.processAndGenerate()

    # --- Slots: File Loading & Generation ---
    @Slot(str)
    def loadFile(self, path_or_url: str):
        if not path_or_url:
            return

        clean_path = path_or_url
        if clean_path.startswith("file:"):
            clean_path = QUrl(clean_path).toLocalFile()
        clean_path = os.path.normpath(clean_path)

        if not os.path.exists(clean_path):
            self.statusAlert.emit(f"File not found: {clean_path}")
            return

        self._file_path = clean_path
        self._file_name = os.path.basename(clean_path)

        # 1. Auto-fetch sidecar parameters if previously saved (<filename>.dxf.json)
        saved_params = self._fh.loadDxfParams(clean_path)
        if saved_params:
            data = saved_params.get("Program page parameters", saved_params)
            h = data.get("Sample Height") or data.get("height")
            f = data.get("Feed") or data.get("feed")
            l = data.get("Selected Laser") or data.get("laser")
            if h is not None:
                try: self._sample_height = float(h)
                except ValueError: pass
            if f is not None:
                try: self._feed_rate = float(f)
                except ValueError: pass
            if l in ["Laser 1", "Laser 2"]:
                self._selected_laser = l
            self.statusAlert.emit(f"Loaded saved parameters for {self._file_name}")

        self.processAndGenerate()

    @Slot()
    def processAndGenerate(self):
        """
        Calculates cutting Z = focus - sample_height,
        applies index & offsets, generates G-code, and extracts vector preview segments.
        Matching main.py programAction.
        """
        if not self._file_path or not os.path.exists(self._file_path):
            return

        ext = os.path.splitext(self._file_path)[1].lower()

        try:
            # 1. Calculate Z cutting height
            self._focus = self._read_config_laser_focus(self._selected_laser)
            self._zpos = max(0.0, round(self._focus - self._sample_height, 3))

            # 2. Read index and offsets
            xindex, yindex, offset_laser, xoffset, yoffset = self._read_config_offsets()

            laser_xoff = xoffset if self._selected_laser == offset_laser else 0.0
            laser_yoff = yoffset if self._selected_laser == offset_laser else 0.0

            bw = float(self._settings.bedWidth) if self._settings else 100.0
            bh = float(self._settings.bedHeight) if self._settings else 100.0
            if self._settings and self._settings.laserCount == 1:
                self._selected_laser = "Laser 1"

            raw_lines = []
            fits_bed = True
            design_w = 0.0
            design_h = 0.0

            if ext == ".dxf":
                parser = DXFParser(self._file_path)
                parser.setBedCorners((0, 0), (bw, 0), (bw, bh), (0, bh))
                parser.setZvalue(self._zpos)
                parser.setFeedRate(self._feed_rate)

                if self._alignment_mode == "center":
                    gcode_lines = parser.generateGcode(align_center=True, laser_xoff=laser_xoff, laser_yoff=laser_yoff)
                else:
                    # Align design origin directly to index point (yellow crosshair)
                    parser.align_to_origin = True
                    parser.setIndex(xindex + laser_xoff, yindex + laser_yoff)
                    gcode_lines = parser.generateGcode(align_center=False)

                design_w = getattr(parser, 'gcode_width', 0.0)
                design_h = getattr(parser, 'gcode_height', 0.0)

                if not gcode_lines:
                    fits_bed = False
                    if self._alignment_mode == "center":
                        gcode_lines = parser.generateGcode(ignore_fit=True, align_center=True, laser_xoff=laser_xoff, laser_yoff=laser_yoff)
                    else:
                        gcode_lines = parser.generateGcode(ignore_fit=True, align_center=False)

                raw_lines = gcode_lines if gcode_lines else []

            elif ext in [".gbr", ".gtl", ".gbl", ".gto", ".gbo", ".gts", ".gbs", ".gml"]:
                parser = GerberParser(self._file_path)
                parser.setBedCorners((0, 0), (bw, 0), (bw, bh), (0, bh))
                parser.setZvalue(self._zpos)
                parser.setFeedRate(self._feed_rate)

                if self._alignment_mode == "center":
                    gcode_lines = parser.generateGcode(align_center=True, laser_xoff=laser_xoff, laser_yoff=laser_yoff)
                else:
                    parser.setIndex(xindex + laser_xoff, yindex + laser_yoff)
                    gcode_lines = parser.generateGcode(align_center=False)

                design_w = getattr(parser, 'gcode_width', 0.0)
                design_h = getattr(parser, 'gcode_height', 0.0)

                if not gcode_lines:
                    fits_bed = False
                    if self._alignment_mode == "center":
                        gcode_lines = parser.generateGcode(ignore_fit=True, align_center=True, laser_xoff=laser_xoff, laser_yoff=laser_yoff)
                    else:
                        gcode_lines = parser.generateGcode(ignore_fit=True, align_center=False)

                raw_lines = gcode_lines if gcode_lines else []
            else:
                # Standard raw G-code text file
                with open(self._file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_lines = f.readlines()

            # Filter and convert M3/M5 to hardware M106 P0/P1 commands matching main.py
            converted = []
            for l in raw_lines:
                line = l.strip()
                if not line or line.startswith(";"):
                    continue
                converted.append(self.pgmGcode(line))

            self._commands = converted
            self._current_index = 0
            self._progress = 0.0

            # Parse vector segments for 2D canvas
            self._parse_vector_segments()

            # Calculate actual boundary box from parsed segments & parser
            self._raw_design_w = design_w if design_w > 0 else max(0.0, self._max_x - self._min_x)
            self._raw_design_h = design_h if design_h > 0 else max(0.0, self._max_y - self._min_y)

            # Check boundary conditions matching main.py lines 1765-1785
            tol = 0.05
            is_physically_too_large = (self._raw_design_w > bw + tol) or (self._raw_design_h > bh + tol)
            exceeds_bed_now = not fits_bed or (self._min_x < -tol or self._max_x > bw + tol or self._min_y < -tol or self._max_y > bh + tol)

            if is_physically_too_large:
                self._is_too_large = True
                self._is_out_of_bounds = True
                self._can_shift = False
                self._boundary_title = "Design Too Large"
                self._boundary_message = (
                    f"The design ({self._raw_design_w:.1f} × {self._raw_design_h:.1f} mm) is larger than the machine boundaries "
                    f"({bw:.0f} × {bh:.0f} mm) even after shifting to the index point. Please modify or scale down the design."
                )
                self._set_state("Error")
                self.isOutOfBoundsChanged.emit()
                self.boundaryWarning.emit(self._boundary_title, self._boundary_message, False, self._raw_design_w, self._raw_design_h)
                self.statusAlert.emit(f"Warning: Design too large ({self._raw_design_w:.1f}×{self._raw_design_h:.1f} mm > {bw:.0f}×{bh:.0f} mm)")
            elif exceeds_bed_now:
                self._is_too_large = False
                self._is_out_of_bounds = True
                self._can_shift = True
                self._boundary_title = "Program Error"
                self._boundary_message = (
                    f"Generated G-code is empty or design ({self._raw_design_w:.1f} × {self._raw_design_h:.1f} mm) exceeds machine boundaries "
                    f"with the current index point.\n\nDo you want to shift the design to the center of the bed?"
                )
                self._set_state("Error")
                self.isOutOfBoundsChanged.emit()
                self.boundaryWarning.emit(self._boundary_title, self._boundary_message, True, self._raw_design_w, self._raw_design_h)
                self.statusAlert.emit("Warning: Design exceeds machine boundaries at current position.")
            else:
                self._is_too_large = False
                self._is_out_of_bounds = False
                self._can_shift = False
                self._boundary_title = ""
                self._boundary_message = ""
                self._set_state("Ready")
                self.isOutOfBoundsChanged.emit()

            # Calculate theoretical total estimated execution time
            total_time_sec = 0.0
            cx_est, cy_est = 0.0, 0.0
            l_feed = float(self._feed_rate) if self._feed_rate > 0 else 500.0
            j_feed = 1000.0

            for c_line in self._commands:
                c_up = c_line.strip().upper()
                is_g0 = c_up.startswith("G0 ") or c_up.startswith("G00")
                spd = (j_feed if is_g0 else l_feed) / 60.0
                spd = max(1.0, spd)

                xm = re.search(r'X([-\d\.]+)', c_up)
                ym = re.search(r'Y([-\d\.]+)', c_up)
                if xm or ym:
                    nx_est = float(xm.group(1)) if xm else cx_est
                    ny_est = float(ym.group(1)) if ym else cy_est
                    d = math.hypot(nx_est - cx_est, ny_est - cy_est)
                    total_time_sec += (d / spd) + 0.025
                    cx_est, cy_est = nx_est, ny_est
                else:
                    total_time_sec += 0.015

            self._total_estimated_seconds = max(1, int(round(total_time_sec)))
            self._remaining_seconds = self._total_estimated_seconds
            self._elapsed_seconds = 0

            # Save to config/final_output.gcode
            try:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                out_path = os.path.join(app_dir, "config", "final_output.gcode")
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write("\n".join(self._commands) + "\n")
                p_chan = 0 if "1" in self._selected_laser else 1
                print(f"[JobBridge] Saved {len(self._commands)} commands to {out_path} ({self._selected_laser}: P{p_chan})")
            except Exception as e:
                print(f"[JobBridge] Failed to save final_output.gcode: {e}")

            # Save sidecar parameters
            try:
                sidecar_params = {
                    "Program page parameters": {
                        "Sample Height": self._sample_height,
                        "Feed": self._feed_rate,
                        "Selected Laser": self._selected_laser
                    }
                }
                self._fh.saveDxfParams(self._file_path, sidecar_params)
            except Exception as e:
                print(f"[JobBridge] Failed to save sidecar params: {e}")

            self.fileLoaded.emit()
            self.parametersChanged.emit()
            self.toolpathReady.emit()
            if not self._is_out_of_bounds:
                self.statusAlert.emit(f"Generated G-code for {self._file_name} (Z={self._zpos}mm, Feed={self._feed_rate})")

        except Exception as e:
            self._set_state("Error")
            self.statusAlert.emit(f"Error processing design: {e}")

    def _parse_vector_segments(self):
        """Converts G0/G1/G2/G3 moves into 2D line segments for QML interactive canvas."""
        segments = []
        cur_x, cur_y = 0.0, 0.0
        laser_on = False

        has_laser_m_codes = any(
            re.search(r'\bM0?[34]\b', l.upper()) or "M106" in l.upper()
            for l in self._commands
        )

        design_xs = []
        design_ys = []

        for cmd_idx, line in enumerate(self._commands):
            cmd_text = re.sub(r'\(.*?\)', '', line)
            cmd_text = cmd_text.split(';')[0].strip().upper()
            if not cmd_text:
                continue

            if re.search(r'\bM0?[34]\b', cmd_text):
                laser_on = True
            elif re.search(r'\bM0?5\b', cmd_text) or "M107" in cmd_text:
                laser_on = False
            elif "M106" in cmd_text:
                s_match = re.search(r'S([-\d\.]+)', cmd_text)
                if s_match and float(s_match.group(1)) == 0:
                    laser_on = False
                else:
                    laser_on = True

            m = re.match(r'^(G0?[0-3])\b', cmd_text)
            if not m:
                if re.search(r'\b[XY][-\d\.]+', cmd_text) and not cmd_text.startswith("G"):
                    cmd_type = "G1"
                else:
                    continue
            else:
                raw_code = m.group(1)
                if raw_code in ("G0", "G00"): cmd_type = "G0"
                elif raw_code in ("G1", "G01"): cmd_type = "G1"
                elif raw_code in ("G2", "G02"): cmd_type = "G2"
                elif raw_code in ("G3", "G03"): cmd_type = "G3"
                else: continue

            x_match = re.search(r'X([-\d\.]+)', cmd_text)
            y_match = re.search(r'Y([-\d\.]+)', cmd_text)

            if not x_match and not y_match:
                continue

            nx = float(x_match.group(1)) if x_match else cur_x
            ny = float(y_match.group(1)) if y_match else cur_y

            is_cut = bool(laser_on and cmd_type != "G0") if has_laser_m_codes else bool(cmd_type != "G0")
            fm = re.search(r'F([-\d\.]+)', cmd_text)
            line_feed = float(fm.group(1)) if fm else (float(self._feed_rate) if is_cut else 1000.0)

            if cmd_type in ("G2", "G3"):
                i_match = re.search(r'I([-\d\.]+)', cmd_text)
                j_match = re.search(r'J([-\d\.]+)', cmd_text)
                i_val = float(i_match.group(1)) if i_match else 0.0
                j_val = float(j_match.group(1)) if j_match else 0.0

                cx = cur_x + i_val
                cy = cur_y + j_val
                r = math.hypot(i_val, j_val)

                if r > 1e-4:
                    start_angle = math.atan2(-j_val, -i_val)
                    end_angle = math.atan2(ny - cy, nx - cx)

                    if cmd_type == "G2":
                        if end_angle >= start_angle:
                            end_angle -= 2 * math.pi
                    else:
                        if end_angle <= start_angle:
                            end_angle += 2 * math.pi

                    total_angle = end_angle - start_angle
                    steps = max(4, min(32, int(abs(total_angle) / (math.pi / 8))))
                    prev_x, prev_y = cur_x, cur_y

                    for s in range(1, steps + 1):
                        theta = start_angle + total_angle * (s / steps)
                        sx = cx + r * math.cos(theta)
                        sy = cy + r * math.sin(theta)
                        segments.append({
                            "x1": round(prev_x, 3),
                            "y1": round(prev_y, 3),
                            "x2": round(sx, 3),
                            "y2": round(sy, 3),
                            "laser": is_cut,
                            "cmd_idx": cmd_idx,
                            "feed": line_feed
                        })
                        prev_x, prev_y = sx, sy
                        design_xs.extend([prev_x, sx])
                        design_ys.extend([prev_y, sy])
                else:
                    segments.append({
                        "x1": round(cur_x, 3),
                        "y1": round(cur_y, 3),
                        "x2": round(nx, 3),
                        "y2": round(ny, 3),
                        "laser": is_cut,
                        "cmd_idx": cmd_idx,
                        "feed": line_feed
                    })
                    design_xs.extend([cur_x, nx])
                    design_ys.extend([cur_y, ny])
            else:
                segments.append({
                    "x1": round(cur_x, 3),
                    "y1": round(cur_y, 3),
                    "x2": round(nx, 3),
                    "y2": round(ny, 3),
                    "laser": is_cut,
                    "cmd_idx": cmd_idx,
                    "feed": line_feed
                })
                design_xs.extend([cur_x, nx])
                design_ys.extend([cur_y, ny])

            cur_x, cur_y = nx, ny

        cut_xs = [s['x1'] for s in segments if s['laser']] + [s['x2'] for s in segments if s['laser']]
        cut_ys = [s['y1'] for s in segments if s['laser']] + [s['y2'] for s in segments if s['laser']]
        if cut_xs and cut_ys:
            self._min_x = round(min(cut_xs), 2)
            self._max_x = round(max(cut_xs), 2)
            self._min_y = round(min(cut_ys), 2)
            self._max_y = round(max(cut_ys), 2)
        elif design_xs and design_ys:
            self._min_x = round(min(design_xs), 2)
            self._max_x = round(max(design_xs), 2)
            self._min_y = round(min(design_ys), 2)
            self._max_y = round(max(design_ys), 2)
        else:
            self._min_x = 0.0
            self._max_x = 100.0
            self._min_y = 0.0
            self._max_y = 100.0

        self._toolpath_segments = segments

    def _set_state(self, new_state: str):
        self._state = new_state
        self.jobStateChanged.emit(new_state)

    # --- Job Execution Controls (Closed-Loop Firmware Handshake & Smooth Trajectory) ---
    def _send_command_at_index(self, idx: int):
        if idx >= len(self._commands):
            self.finishJob()
            return

        cmd = self.pgmGcode(self._commands[idx])
        self._update_laser_firing_from_cmd(cmd)

        c_up = str(cmd).upper()
        xm = re.search(r'X([-\d\.]+)', c_up)
        ym = re.search(r'Y([-\d\.]+)', c_up)

        if xm or ym:
            nx = float(xm.group(1)) if xm else self._seg_start_x
            ny = float(ym.group(1)) if ym else self._seg_start_y
            dist = math.hypot(nx - self._seg_start_x, ny - self._seg_start_y)

            is_g0 = c_up.startswith("G0 ") or c_up.startswith("G00")
            fm = re.search(r'F([-\d\.]+)', c_up)
            if fm:
                feed = float(fm.group(1))
                if not is_g0:
                    self._active_feed = feed
            else:
                feed = self._jog_feed if is_g0 else self._active_feed

            spd = max(1.0, feed / 60.0)

            self._seg_target_x = nx
            self._seg_target_y = ny
            self._seg_duration = max(0.04, dist / spd) if dist > 0.005 else 0.02
            self._seg_elapsed = 0.0
            self._seg_progress = 0.0
            self._last_sim_tick = time.time()
            self._exec_timer.start()

        self._serial.sendGcode(cmd)
        self._serial.sendGcode("M400")  # Wait for firmware move completion
        self._serial.sendGcode("M114")  # Query position -> triggers next step on response

    def _update_laser_firing_from_cmd(self, cmd_text: str):
        c_up = str(cmd_text).upper()
        if "M106" in c_up:
            sm = re.search(r'S([-\d\.]+)', c_up)
            firing = bool(sm and float(sm.group(1)) > 0)
        elif "M3" in c_up or "M03" in c_up:
            firing = True
        elif "M5" in c_up or "M05" in c_up or "M107" in c_up:
            firing = False
        else:
            firing = self._is_laser_firing

        if firing != self._is_laser_firing:
            self._is_laser_firing = firing
            self.laserFiringChanged.emit(self._is_laser_firing)

    def _step_job_hardware(self):
        """Advances job index after M114 confirmation from controller."""
        if self._state != "Running":
            return

        # Synchronize target coordinates and complete segment
        self._seg_start_x = self._seg_target_x
        self._seg_start_y = self._seg_target_y
        self._seg_progress = 1.0

        if self._motion:
            self._motion.setSimulatedPosition(self._seg_target_x, self._seg_target_y)

        self._current_index += 1
        self._progress = (self._current_index / len(self._commands)) * 100.0
        self.progressChanged.emit(self._progress, self._current_index, len(self._commands))

        if self._current_index < len(self._commands):
            self._send_command_at_index(self._current_index)
        else:
            self.finishJob()

    def _step_job_simulation(self):
        """Continuous high-frequency (40 FPS) interpolation step providing live gliding axis tracking."""
        if self._state != "Running":
            self._exec_timer.stop()
            return

        now = time.time()
        dt = max(0.001, min(0.08, now - self._last_sim_tick))
        self._last_sim_tick = now

        is_hardware = bool(self._serial and self._serial.connected)

        if not is_hardware:
            # Check if current vector move has completed in simulation mode
            if self._seg_progress >= 1.0:
                if self._current_index >= len(self._commands):
                    self.finishJob()
                    return

                cmd = self._commands[self._current_index]
                self._update_laser_firing_from_cmd(cmd)

                c_up = str(cmd).upper()
                xm = re.search(r'X([-\d\.]+)', c_up)
                ym = re.search(r'Y([-\d\.]+)', c_up)

                if xm or ym:
                    nx = float(xm.group(1)) if xm else self._seg_start_x
                    ny = float(ym.group(1)) if ym else self._seg_start_y
                    dist = math.hypot(nx - self._seg_start_x, ny - self._seg_start_y)

                    is_g0 = c_up.startswith("G0 ") or c_up.startswith("G00")
                    fm = re.search(r'F([-\d\.]+)', c_up)
                    if fm:
                        self._active_feed = float(fm.group(1))
                    spd = max(1.0, (self._jog_feed if is_g0 else self._active_feed) / 60.0)

                    self._seg_target_x = nx
                    self._seg_target_y = ny

                    if dist > 0.005:
                        self._seg_duration = max(0.03, dist / spd)
                    else:
                        self._seg_start_x = nx
                        self._seg_start_y = ny
                        self._seg_duration = 0.02

                    self._seg_elapsed = 0.0
                    self._seg_progress = 0.0
                else:
                    self._seg_duration = 0.02
                    self._seg_elapsed = 0.0
                    self._seg_progress = 0.0

        # Advance along the active segment
        self._seg_elapsed += dt
        if self._seg_duration > 0:
            self._seg_progress = min(1.0, self._seg_elapsed / self._seg_duration)
        else:
            self._seg_progress = 1.0

        # Continuous smooth linear interpolation
        self._head_x = self._seg_start_x + self._seg_progress * (self._seg_target_x - self._seg_start_x)
        self._head_y = self._seg_start_y + self._seg_progress * (self._seg_target_y - self._seg_start_y)
        self.laserHeadMoved.emit(self._head_x, self._head_y)

        if self._motion:
            if abs(self._head_x - self._motion.xPos) >= 0.15 or abs(self._head_y - self._motion.yPos) >= 0.15 or self._seg_progress >= 1.0:
                self._motion.setSimulatedPosition(round(self._head_x, 3), round(self._head_y, 3))

        total_cmds = len(self._commands)
        if total_cmds > 0:
            cmd_base = (self._current_index / total_cmds) * 100.0
            cmd_frac = (self._seg_progress / total_cmds) * 100.0
            new_prog = min(100.0, cmd_base + cmd_frac)
            if abs(new_prog - self._progress) >= 0.25 or self._seg_progress >= 1.0:
                self._progress = new_prog
                self.progressChanged.emit(self._progress, self._current_index, total_cmds)

        if not is_hardware:
            if self._seg_progress >= 1.0:
                self._seg_start_x = self._seg_target_x
                self._seg_start_y = self._seg_target_y
                self._current_index += 1

    @Slot()
    def startJob(self):
        if self._is_out_of_bounds:
            self.statusAlert.emit("Cannot start job: Design exceeds machine boundaries (100×100 mm).")
            return

        if not self._commands:
            self.statusAlert.emit("No job loaded to run.")
            return

        start_x = self._motion.xPos if self._motion else 0.0
        start_y = self._motion.yPos if self._motion else 0.0
        self._seg_start_x = start_x
        self._seg_start_y = start_y
        self._seg_target_x = start_x
        self._seg_target_y = start_y
        self._seg_duration = 0.0
        self._seg_elapsed = 0.0
        self._seg_progress = 1.0
        self._last_sim_tick = time.time()

        self._current_index = 0
        self._job_start_time = time.time()
        self._job_pause_time = 0.0
        self._job_paused_duration = 0.0
        self._elapsed_seconds = 0
        self._remaining_seconds = self._total_estimated_seconds
        self._is_laser_firing = False
        self._time_timer.start()
        self.timeUpdated.emit(0, self._remaining_seconds)

        self._set_state("Running")

        if self._serial.connected:
            self._send_command_at_index(0)
        else:
            self._exec_timer.start()

        self.statusAlert.emit("Job Started")

    @Slot()
    def pauseJob(self):
        if self._state == "Running":
            self._exec_timer.stop()
            self._time_timer.stop()
            self._job_pause_time = time.time()
            self._is_laser_firing = False
            self.laserFiringChanged.emit(False)

            if self._serial.connected:
                self._serial.sendGcode("M106 P0 S0")
                self._serial.sendGcode("M106 P1 S0")
                self._serial.sendGcode("M5")
            self._set_state("Paused")
            self.statusAlert.emit("Job Paused")

    @Slot()
    def resumeJob(self):
        if self._state == "Paused":
            self._set_state("Running")
            if self._job_pause_time > 0:
                self._job_paused_duration += (time.time() - self._job_pause_time)
            self._time_timer.start()

            if self._serial.connected:
                self._send_command_at_index(self._current_index)
            else:
                self._exec_timer.start()
            self.statusAlert.emit("Job Resumed")

    @Slot()
    def abortJob(self):
        """Matching main.py abort: stops laser, sends M410 quickstop, homes with G28."""
        self._exec_timer.stop()
        self._time_timer.stop()
        self._is_laser_firing = False
        self.laserFiringChanged.emit(False)

        if self._serial.connected:
            # 1. Turn off laser
            self._serial.sendGcode("M106 P0 S0")
            self._serial.sendGcode("M106 P1 S0")
            self._serial.sendGcode("M5")
            # 2. Hard quick-stop
            self._serial.sendGcode("M410")
            # 3. Home machine after abort
            self._serial.sendGcode("G28")
            self._serial.sendGcode("M114")

        self._set_state("Aborted")
        self.statusAlert.emit("Job ABORTED — Machine homed safely")

    @Slot()
    def startInspection(self):
        """
        Executes camera inspection matching main.py runInspection:
        - Strips laser firing (M3, M5, M106) and G28
        - Offsets X/Y with active laser's camera offset from config.ini
        - Applies camera_inspection_feed (300 mm/min)
        - Saves to config/inspection_output.gcode
        - Starts closed-loop firmware handshake execution
        """
        if not self._commands:
            self.errorOccurred.emit("Please load a design or G-code file first.")
            return

        try:
            # Read camera offsets and speed from config.ini
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cfg_path = os.path.join(app_dir, "config", "config.ini")
            ch = ConfigHandler()
            ch.ini_parser.read(cfg_path)

            cam_ox, cam_oy = 0.0, 0.0
            if self._selected_laser == 1:
                cam_ox = float(ch.getValues("camera_offset", "laser1_x") or 0.0)
                cam_oy = float(ch.getValues("camera_offset", "laser1_y") or 0.0)
            else:
                cam_ox = float(ch.getValues("camera_offset", "laser2_x") or 0.0)
                cam_oy = float(ch.getValues("camera_offset", "laser2_y") or 0.0)

            insp_feed = int(ch.getValues("camera", "inspection_feed") or 300)

            # Filter commands: strip G28, laser controls (M3, M5, M106), comments
            filtered = [
                c for c in self._commands
                if "G28" not in c and not c.startswith(("M3", "M5", "M106", ";"))
            ]

            inspection_commands = []
            for line in filtered:
                if "X" in line or "Y" in line:
                    def rx(m): return f"X{float(m.group(1)) + cam_ox:.3f}"
                    def ry(m): return f"Y{float(m.group(1)) + cam_oy:.3f}"
                    line = re.sub(r'X([-0-9.]+)', rx, line)
                    line = re.sub(r'Y([-0-9.]+)', ry, line)
                    if "F" in line:
                        line = re.sub(r'F([-0-9.]+)', f'F{insp_feed}', line)
                    else:
                        line = line.strip() + f" F{insp_feed}"
                inspection_commands.append(line)

            # Save inspection_output.gcode
            out_path = os.path.join(app_dir, "config", "inspection_output.gcode")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(inspection_commands))

            print(f"[JobBridge] Inspection G-code generated ({len(inspection_commands)} commands) with offset X={cam_ox}, Y={cam_oy}")

            # Load into job execution commands
            self._commands = inspection_commands
            self._current_index = 0
            self._progress = 0.0
            self.totalCommandsChanged.emit()
            self.currentCommandChanged.emit()
            self.progressChanged.emit(0.0, 0, len(self._commands))

            # Start execution
            self.startJob()
            self.statusAlert.emit("Optical Inspection Routine Started")

        except Exception as e:
            self.errorOccurred.emit(f"Failed to start camera inspection: {e}")

    def finishJob(self):
        self._exec_timer.stop()
        self._time_timer.stop()
        self._is_laser_firing = False
        self.laserFiringChanged.emit(False)
        self._set_state("Complete")
        self._progress = 100.0
        self._remaining_seconds = 0
        self.timeUpdated.emit(self._elapsed_seconds, 0)
        self.progressChanged.emit(100.0, len(self._commands), len(self._commands))
        self.statusAlert.emit("Job Execution Complete!")
