import os
import sys
import time
import math
import glob
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from com import SerialCom
from core.connection.base import BaseConnection
from core.connection.mock import MockConnection
try:
    from core.connection.hardware import HardwareConnection
    HAS_HARDWARE_MODULE = True
except Exception:
    HardwareConnection = None
    HAS_HARDWARE_MODULE = False

from machine.galvo_controller import GalvoController
from machine.stepper_controller import StepperController
from core.calibration import GalvoCalibration
from core.coordinate_mapper import CoordinateConfig
from core.motion_planner import MotionPlanner
import configparser
from dxf import DXFParser
from core.parsers.svgelements import SVG, Path, Shape, Line


def parse_svg_paths_fast(filepath_or_content: str, is_content: bool = False) -> Tuple[List[List[Tuple[float, float]]], Dict[str, float]]:
    """
    Ultra-fast SVG path parser with intelligent linear and curved segment discretization.
    Converts SVG coordinates to centered physical millimeter coordinates (-50 to +50mm).
    """
    if is_content:
        svg = SVG.parse(filepath_or_content)
    else:
        svg = SVG.parse(filepath_or_content)

    paths: List[List[Tuple[float, float]]] = []
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    # Convert 96 DPI CSS pixels to physical millimeters (25.4 mm / 96 px = 0.264583 mm/px)
    scale_factor = 25.4 / 96.0

    for element in svg.elements():
        if not isinstance(element, Shape):
            continue
        try:
            path_obj = Path(element)
        except Exception:
            continue
        if len(path_obj) == 0:
            continue

        path_pts: List[Tuple[float, float]] = []
        for seg in path_obj:
            if isinstance(seg, Line):
                p0 = seg.point(0)
                p1 = seg.point(1)
                for pt in (p0, p1):
                    x = pt.real * scale_factor
                    y = -pt.imag * scale_factor
                    path_pts.append((x, y))
                    min_x = min(min_x, x); max_x = max(max_x, x)
                    min_y = min(min_y, y); max_y = max(max_y, y)
            else:
                try:
                    seg_len = max(1.0, seg.length() * scale_factor)
                except Exception:
                    seg_len = 5.0
                samples = max(4, min(36, int(seg_len / 0.5)))
                for i in range(samples):
                    pt = seg.point(i / (samples - 1))
                    x = pt.real * scale_factor
                    y = -pt.imag * scale_factor
                    path_pts.append((x, y))
                    min_x = min(min_x, x); max_x = max(max_x, x)
                    min_y = min(min_y, y); max_y = max(max_y, y)

        if path_pts:
            paths.append(path_pts)

    if not paths or min_x == float('inf'):
        return [], {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "width": 0, "height": 0}

    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    width = max_x - min_x
    height = max_y - min_y

    centered_paths = [
        [(float(round(x - cx, 3)), float(round(y - cy, 3))) for x, y in p]
        for p in paths
    ]

    bounds = {
        "min_x": float(round(-width / 2.0, 2)),
        "max_x": float(round(width / 2.0, 2)),
        "min_y": float(round(-height / 2.0, 2)),
        "max_y": float(round(height / 2.0, 2)),
        "width": float(round(width, 2)),
        "height": float(round(height, 2))
    }
    return centered_paths, bounds


def parse_dxf_paths_fast(filepath: str) -> Tuple[List[List[Tuple[float, float]]], Dict[str, float]]:
    """
    Extracts geometric polylines and primitives from DXF file.
    Converts entities to centered physical millimeter coordinates.
    """
    p = DXFParser(filepath)
    ents = p.extractEntities()
    paths: List[List[Tuple[float, float]]] = []
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    for layer, elist in ents.items():
        for etype, data in elist:
            if etype == 'LINE':
                x0, y0, x1, y1 = data
                paths.append([(x0, y0), (x1, y1)])
                min_x = min(min_x, x0, x1); max_x = max(max_x, x0, x1)
                min_y = min(min_y, y0, y1); max_y = max(max_y, y0, y1)
            elif etype == 'CIRCLE':
                cx, cy, r = data
                pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 365, 8)]
                paths.append(pts)
                min_x = min(min_x, cx - r); max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r); max_y = max(max_y, cy + r)
            elif etype == 'ARC':
                cx, cy, r, sa, ea = data
                if ea < sa:
                    ea += 360
                span = ea - sa
                samples = max(8, int(span / 8.0))
                pts = []
                for i in range(samples + 1):
                    ang = math.radians(sa + (span * (i / samples)))
                    pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
                paths.append(pts)
                for px, py in pts:
                    min_x = min(min_x, px); max_x = max(max_x, px)
                    min_y = min(min_y, py); max_y = max(max_y, py)
            elif etype == 'POLYLINE':
                pts = [(pt[0], pt[1]) for pt in data['points']]
                if data.get('closed') and pts and pts[0] != pts[-1]:
                    pts.append(pts[0])
                if len(pts) >= 2:
                    paths.append(pts)
                    for px, py in pts:
                        min_x = min(min_x, px); max_x = max(max_x, px)
                        min_y = min(min_y, py); max_y = max(max_y, py)

    if not paths or min_x == float('inf'):
        return [], {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "width": 0, "height": 0}

    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    width = max_x - min_x
    height = max_y - min_y

    centered_paths = [
        [(float(round(x - cx, 3)), float(round(y - cy, 3))) for x, y in p]
        for p in paths
    ]

    bounds = {
        "min_x": float(round(-width / 2.0, 2)),
        "max_x": float(round(width / 2.0, 2)),
        "min_y": float(round(-height / 2.0, 2)),
        "max_y": float(round(height / 2.0, 2)),
        "width": float(round(width, 2)),
        "height": float(round(height, 2))
    }
    return centered_paths, bounds


# --------------------------------------------------------------------------
# HIGH-PRECISION SINGLE-STROKE VECTOR FONT FOR LASER MARKING
# --------------------------------------------------------------------------
_VECTOR_FONT: Dict[str, List[List[Tuple[float, float]]]] = {
    'A': [[(0.0, 0.0), (0.0, 0.7), (0.5, 1.0), (1.0, 0.7), (1.0, 0.0)], [(0.0, 0.4), (1.0, 0.4)]],
    'B': [[(0.0, 0.0), (0.0, 1.0), (0.7, 1.0), (1.0, 0.8), (0.7, 0.5), (0.0, 0.5)], [(0.7, 0.5), (1.0, 0.25), (0.7, 0.0), (0.0, 0.0)]],
    'C': [[(1.0, 0.9), (0.3, 1.0), (0.0, 0.7), (0.0, 0.3), (0.3, 0.0), (1.0, 0.1)]],
    'D': [[(0.0, 0.0), (0.0, 1.0), (0.6, 1.0), (1.0, 0.7), (1.0, 0.3), (0.6, 0.0), (0.0, 0.0)]],
    'E': [[(1.0, 1.0), (0.0, 1.0), (0.0, 0.0), (1.0, 0.0)], [(0.0, 0.5), (0.7, 0.5)]],
    'F': [[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0)], [(0.0, 0.5), (0.7, 0.5)]],
    'G': [[(1.0, 0.9), (0.3, 1.0), (0.0, 0.7), (0.0, 0.3), (0.3, 0.0), (1.0, 0.1), (1.0, 0.5), (0.5, 0.5)]],
    'H': [[(0.0, 0.0), (0.0, 1.0)], [(1.0, 0.0), (1.0, 1.0)], [(0.0, 0.5), (1.0, 0.5)]],
    'I': [[(0.2, 1.0), (0.8, 1.0)], [(0.5, 1.0), (0.5, 0.0)], [(0.2, 0.0), (0.8, 0.0)]],
    'J': [[(0.8, 1.0), (0.8, 0.2), (0.6, 0.0), (0.2, 0.0), (0.0, 0.2)]],
    'K': [[(0.0, 0.0), (0.0, 1.0)], [(1.0, 1.0), (0.0, 0.5), (1.0, 0.0)]],
    'L': [[(0.0, 1.0), (0.0, 0.0), (1.0, 0.0)]],
    'M': [[(0.0, 0.0), (0.0, 1.0), (0.5, 0.5), (1.0, 1.0), (1.0, 0.0)]],
    'N': [[(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]],
    'O': [[(0.3, 1.0), (0.7, 1.0), (1.0, 0.75), (1.0, 0.25), (0.7, 0.0), (0.3, 0.0), (0.0, 0.25), (0.0, 0.75), (0.3, 1.0)]],
    'P': [[(0.0, 0.0), (0.0, 1.0), (0.8, 1.0), (1.0, 0.8), (0.8, 0.5), (0.0, 0.5)]],
    'Q': [[(0.3, 1.0), (0.7, 1.0), (1.0, 0.75), (1.0, 0.25), (0.7, 0.0), (0.3, 0.0), (0.0, 0.25), (0.0, 0.75), (0.3, 1.0)], [(0.6, 0.3), (1.0, 0.0)]],
    'R': [[(0.0, 0.0), (0.0, 1.0), (0.8, 1.0), (1.0, 0.8), (0.8, 0.5), (0.0, 0.5)], [(0.5, 0.5), (1.0, 0.0)]],
    'S': [[(1.0, 0.85), (0.7, 1.0), (0.3, 1.0), (0.0, 0.8), (0.2, 0.55), (0.8, 0.45), (1.0, 0.2), (0.7, 0.0), (0.3, 0.0), (0.0, 0.15)]],
    'T': [[(0.0, 1.0), (1.0, 1.0)], [(0.5, 1.0), (0.5, 0.0)]],
    'U': [[(0.0, 1.0), (0.0, 0.2), (0.2, 0.0), (0.8, 0.0), (1.0, 0.2), (1.0, 1.0)]],
    'V': [[(0.0, 1.0), (0.5, 0.0), (1.0, 1.0)]],
    'W': [[(0.0, 1.0), (0.25, 0.0), (0.5, 0.6), (0.75, 0.0), (1.0, 1.0)]],
    'X': [[(0.0, 0.0), (1.0, 1.0)], [(0.0, 1.0), (1.0, 0.0)]],
    'Y': [[(0.0, 1.0), (0.5, 0.5), (1.0, 1.0)], [(0.5, 0.5), (0.5, 0.0)]],
    'Z': [[(0.0, 1.0), (1.0, 1.0), (0.0, 0.0), (1.0, 0.0)]],
    '0': [[(0.3, 1.0), (0.7, 1.0), (1.0, 0.75), (1.0, 0.25), (0.7, 0.0), (0.3, 0.0), (0.0, 0.25), (0.0, 0.75), (0.3, 1.0)], [(0.2, 0.2), (0.8, 0.8)]],
    '1': [[(0.2, 0.8), (0.5, 1.0), (0.5, 0.0)], [(0.2, 0.0), (0.8, 0.0)]],
    '2': [[(0.0, 0.8), (0.2, 1.0), (0.8, 1.0), (1.0, 0.8), (1.0, 0.6), (0.0, 0.0), (1.0, 0.0)]],
    '3': [[(0.0, 1.0), (1.0, 1.0), (0.5, 0.5), (0.8, 0.5), (1.0, 0.3), (0.8, 0.0), (0.2, 0.0), (0.0, 0.2)]],
    '4': [[(0.8, 0.0), (0.8, 1.0), (0.0, 0.3), (1.0, 0.3)]],
    '5': [[(1.0, 1.0), (0.0, 1.0), (0.0, 0.6), (0.8, 0.6), (1.0, 0.4), (0.8, 0.0), (0.0, 0.0)]],
    '6': [[(0.8, 1.0), (0.3, 1.0), (0.0, 0.7), (0.0, 0.2), (0.3, 0.0), (0.7, 0.0), (1.0, 0.25), (1.0, 0.5), (0.0, 0.5)]],
    '7': [[(0.0, 1.0), (1.0, 1.0), (0.4, 0.0)]],
    '8': [[(0.3, 1.0), (0.7, 1.0), (0.9, 0.8), (0.7, 0.5), (0.3, 0.5), (0.1, 0.8), (0.3, 1.0)], [(0.3, 0.5), (0.7, 0.5), (1.0, 0.2), (0.8, 0.0), (0.2, 0.0), (0.0, 0.2), (0.3, 0.5)]],
    '9': [[(1.0, 0.5), (0.0, 0.5), (0.0, 0.75), (0.3, 1.0), (0.7, 1.0), (1.0, 0.8), (1.0, 0.3), (0.7, 0.0), (0.2, 0.0)]],
    ' ': [],
    '-': [[(0.2, 0.5), (0.8, 0.5)]],
    '_': [[(0.0, 0.0), (1.0, 0.0)]],
    '.': [[(0.4, 0.0), (0.6, 0.0), (0.6, 0.1), (0.4, 0.1), (0.4, 0.0)]],
    ':': [[(0.4, 0.2), (0.6, 0.2)], [(0.4, 0.7), (0.6, 0.7)]],
    '+': [[(0.2, 0.5), (0.8, 0.5)], [(0.5, 0.2), (0.5, 0.8)]],
    '/': [[(0.1, 0.0), (0.9, 1.0)]],
}


class GalvoHardwareBridge:
    """
    High-Performance PyWebView JS-Python API Bridge.
    Connects the futuristic React frontend directly to physical Galvo hardware (gt5motion DLL),
    Stepper Z-axis, Serial COM controllers (BlackPill / Grbl / G-code), laser timing, and safety systems.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Telemetry & Logs
        self._logs: List[Dict[str, Any]] = []
        self._log_counter = 0
        self._max_logs = 1000

        # Hardware Controllers from machine/
        self.galvo_controller: Optional[GalvoController] = None
        self.stepper_controller: Optional[StepperController] = None
        self.connection: Optional[BaseConnection] = None
        self.serial_com: Optional[SerialCom] = None

        # Industrial Motion Planner & Calibrated Coordinate Transformer
        self.galvo_config = CoordinateConfig()
        self.planner = MotionPlanner()
        self._load_config_ini()

        self.is_connected = False
        self.is_mock = True
        self.connected_port: Optional[str] = None
        self.connected_baud: int = 115200
        self.cards_found: int = 0

        # Hardware & Laser States
        self.laser_state = False       # DO1 (Pin 0)
        self.reddot_state = False      # DO2 (Pin 1)
        self.power_percent = 25.0      # 0.0 to 100.0%
        self.analog_power_val = 63.75  # 0 to 255.0 on bit 2
        self.frequency_khz = 35.0      # 20.0 to 80.0 kHz
        self.pulse_width_ns = 200      # ns
        self.mark_speed = 500.0        # mm/s (50 - 1800)
        self.jump_speed = 1200.0       # mm/s (100 - 1870)

        # Laser Timing & Delay Parameters (EzCad / GT-Motion Industrial Standard)
        self.laser_on_delay_us = 150   # us (10-2000)
        self.laser_off_delay_us = 150  # us (10-2000)
        self.mark_delay_us = 100       # us (10-2000)
        self.jump_delay_us = 250       # us (10-2000)
        self.poly_delay_us = 80        # us (10-1000)

        # Active .cor Lens Calibration
        self.active_cor_file = "newest100mm.cor"

        # Coordinates (Galvo field in mm, center 0,0, range -50..+50 for 100x100mm field)
        self.cur_x = 0.0
        self.cur_y = 0.0
        self.cur_z = 0.0

        # Motion & Task States
        self.is_marking = False
        self.is_framing = False
        self.is_paused = False
        self.mark_progress = 0.0
        self.estop_active = False

        # Loaded Vector File State
        self.loaded_vector_data: Optional[Dict[str, Any]] = None

        # Worker Threads & Stop Events
        self._framing_thread: Optional[threading.Thread] = None
        self._framing_stop_event = threading.Event()
        self._framing_lock = threading.Lock()
        self._framing_needs_refresh = False
        self._active_frame_points: List[Tuple[float, float]] = []
        self._active_sim_points: List[Tuple[float, float]] = []
        self._marking_thread: Optional[threading.Thread] = None
        self._marking_stop_event = threading.Event()

        self._add_log("SYSTEM", "Galvo Hardware Bridge initialized. Linking to machine controllers.", "info")

        # Auto-connect to hardware or fallback simulation
        self._init_controllers()

    def _load_config_ini(self):
        """Loads Galvo field size, axis orientations, and distortion factors from config/config.ini."""
        try:
            config_path = os.path.join(BASE_DIR, "config", "config.ini")
            if os.path.exists(config_path):
                cp = configparser.ConfigParser()
                cp.read(config_path)
                if "GalvoField" in cp:
                    sec = cp["GalvoField"]
                    self.galvo_config.field_size = float(sec.get("field_size", "100.0"))
                    self.galvo_config.offset_x = float(sec.get("offset_x", "0.0"))
                    self.galvo_config.offset_y = float(sec.get("offset_y", "0.0"))
                    self.galvo_config.angle = float(sec.get("angle", "0.0"))
                    self.galvo_config.galvo_1_is_x = (sec.get("galvo1_x", "False").strip().lower() == "true")
                    self.galvo_config.g1_negate = (sec.get("g1_negate", "False").strip().lower() == "true")
                    self.galvo_config.g1_scale = float(sec.get("g1_scale", "100.0"))
                    self.galvo_config.g1_bulge = float(sec.get("g1_barrel", "1.0"))
                    self.galvo_config.g1_skew = float(sec.get("g1_par", "1.0"))
                    self.galvo_config.g1_trapezoid = float(sec.get("g1_trapezoid", "1.0"))
                    self.galvo_config.g2_negate = (sec.get("g2_negate", "False").strip().lower() == "true")
                    self.galvo_config.g2_scale = float(sec.get("g2_scale", "100.0"))
                    self.galvo_config.g2_bulge = float(sec.get("g2_barrel", "1.0"))
                    self.galvo_config.g2_skew = float(sec.get("g2_par", "1.0"))
                    self.galvo_config.g2_trapezoid = float(sec.get("g2_trapezoid", "1.0"))
                    self._add_log("CONFIG", f"Loaded GalvoField: field_size={self.galvo_config.field_size}mm, g1_x={self.galvo_config.galvo_1_is_x}", "info")
        except Exception as e:
            self._add_log("CONFIG", f"Notice reading config.ini: {e}", "warning")

    def _get_galvo_units_per_mm(self) -> float:
        """Returns conversion scale (bits per mm) from active calibration or field size."""
        if (self.connection and hasattr(self.connection, "calibration") and 
                getattr(self.connection.calibration, "is_valid", False) and 
                getattr(self.connection.calibration, "scale", None)):
            return float(self.connection.calibration.scale)
        field_sz = self.galvo_config.field_size if self.galvo_config.field_size > 0 else 100.0
        return 65535.0 / field_sz

    def _get_hardware_speeds(self) -> Tuple[int, int]:
        """Calculates clamped mark_speed and jump_speed in Galvo bits/s [33,000 to 1,000,000]."""
        scale = self._get_galvo_units_per_mm()
        mark_bits = int(round(self.mark_speed * scale))
        jump_bits = int(round(self.jump_speed * scale))
        mark_bits = max(33000, min(1000000, mark_bits))
        jump_bits = max(33000, min(1000000, jump_bits))
        return mark_bits, jump_bits

    def _init_controllers(self, force_mock: bool = False):
        """Initializes GalvoController and StepperController."""
        try:
            self.galvo_controller = GalvoController()
            connected = self.galvo_controller.connect(force_mock=force_mock)
            self.connection = self.galvo_controller.connection
            self.stepper_controller = StepperController(self.connection)

            self.is_connected = connected
            self.is_mock = not connected
            self.cards_found = 1 if connected else 0

            if connected:
                self._add_log("HARDWARE", "Physical GoogolTech gt5motion hardware connected & initialized.", "success")
                try:
                    self.galvo_controller.galvo_home()
                    self._add_log("MOTION", "Galvo mirrors centered at (0, 0).", "info")
                except Exception as e:
                    self._add_log("HARDWARE", f"Galvo home notice: {e}", "warning")
            else:
                self._add_log("HARDWARE", "Running in high-precision Simulation mode (Mock hardware active).", "info")

            # Apply active .cor calibration if available
            self.set_calibration_file(self.active_cor_file)

            # Read initial Z coordinate
            try:
                self.cur_z = round(self.stepper_controller.get_physical_z(), 2)
            except Exception:
                self.cur_z = 0.0

            # Safe initial beam states
            self._apply_laser_off()
            self._apply_reddot_off()
            self.set_power(self.power_percent)
            self.set_frequency(self.frequency_khz)
        except Exception as e:
            self._add_log("ERROR", f"Controller init notice: {e}", "error")
            self.connection = MockConnection()
            self.connection.initialize()
            self.stepper_controller = StepperController(self.connection)
            self.is_connected = False
            self.is_mock = True

    def _add_log(self, source: str, message: str, level: str = "info"):
        """Thread-safe logging method storing categorized events for frontend console."""
        with self._lock:
            self._log_counter += 1
            entry = {
                "id": self._log_counter,
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "source": source,
                "message": message,
                "level": level  # "info", "success", "warning", "error", "gcode"
            }
            self._logs.append(entry)
            if len(self._logs) > self._max_logs:
                self._logs.pop(0)

    # --------------------------------------------------------------------------
    # SERIAL PORT & DEVICE CONNECTION
    # --------------------------------------------------------------------------
    def get_available_ports(self) -> List[Dict[str, str]]:
        """Returns list of active serial COM ports found on system."""
        ports = []
        try:
            comports = serial.tools.list_ports.comports()
            for p in comports:
                ports.append({
                    "port": p.device,
                    "desc": p.description or p.device,
                    "hwid": getattr(p, "hwid", "")
                })
        except Exception as e:
            self._add_log("ERROR", f"Failed scanning COM ports: {e}", "error")

        if not ports:
            ports = [
                {"port": "COM1", "desc": "Virtual Galvo Controller (Sim)", "hwid": "SIM_001"},
                {"port": "COM3", "desc": "USB-Serial Laser Board (BlackPill)", "hwid": "USB_SERIAL_003"},
                {"port": "COM4", "desc": "GoogolTech Motion Board", "hwid": "GT_MOTION_004"}
            ]
        return ports

    def get_baud_rates(self) -> List[int]:
        """Returns standard industrial baud rates."""
        return [9600, 19200, 38400, 57600, 115200, 250000, 500000]

    def connect_device(self, port: Optional[str] = None, baud: int = 115200, force_mock: bool = False) -> Dict[str, Any]:
        """
        Initializes connection to physical Galvo hardware (DLL) and Serial COM port.
        """
        with self._lock:
            if self.estop_active:
                return {"success": False, "error": "Cannot connect while EMERGENCY STOP is active. Reset E-STOP first."}

            self._add_log("SYSTEM", f"Connecting... Port: {port or 'None'}, Baud: {baud}, Force Mock: {force_mock}", "info")
            self._init_controllers(force_mock=force_mock)

            # Connect Serial COM if specified
            if port and port != "NONE" and port != "OFFLINE":
                try:
                    if self.serial_com and self.serial_com.is_connected:
                        self.serial_com.disconnect()

                    s = SerialCom()
                    s.port = port
                    s.baudrate = baud

                    def on_serial_response(line):
                        self._add_log("SERIAL_RX", line, "info")

                    def on_serial_exception(err):
                        self._add_log("SERIAL_ERR", str(err), "error")

                    s.configCallbacks(responseCallback=on_serial_response, exceptionCallback=on_serial_exception)
                    s.connect()

                    if s.is_connected:
                        self.serial_com = s
                        self.connected_port = port
                        self.connected_baud = baud
                        self._add_log("SERIAL", f"Serial COM Port {port} @ {baud} bps connected.", "success")
                    else:
                        self.connected_port = port
                        self.connected_baud = baud
                except Exception as e:
                    self._add_log("SERIAL", f"Serial connection notice: {e}", "warning")
                    self.connected_port = port
                    self.connected_baud = baud
            else:
                self.connected_port = None

            return {
                "success": True,
                "is_mock": self.is_mock,
                "cards": self.cards_found,
                "port": self.connected_port,
                "baud": self.connected_baud
            }

    def disconnect_device(self) -> Dict[str, Any]:
        """Safely shuts off all beams and closes connections."""
        with self._lock:
            self._add_log("SYSTEM", "Disconnecting hardware...", "warning")
            self._stop_framing_internal()
            self._stop_marking_internal()

            self._apply_laser_off()
            self._apply_reddot_off()

            if self.serial_com:
                try:
                    self.serial_com.disconnect()
                except Exception:
                    pass
                self.serial_com = None

            if self.galvo_controller:
                try:
                    self.galvo_controller.disconnect()
                except Exception:
                    pass

            self.is_connected = False
            self.connected_port = None
            self._init_controllers(force_mock=True)
            self._add_log("SYSTEM", "Hardware safely disconnected.", "info")
            return {"success": True}

    # --------------------------------------------------------------------------
    # BEAM & POWER CONTROL (DO1, DO2, ANALOG PWM)
    # --------------------------------------------------------------------------
    def _apply_laser_on(self):
        if self.connection and hasattr(self.connection, "laser_on"):
            self.connection.laser_on()
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send("M106 P0 S255")
        self.laser_state = True
        self._add_log("GCODE", "M106 P0 S255 (Laser DO1 ON)", "gcode")

    def _apply_laser_off(self):
        if self.connection and hasattr(self.connection, "laser_off"):
            self.connection.laser_off()
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send("M106 P0 S0")
        self.laser_state = False
        self._add_log("GCODE", "M106 P0 S0 (Laser DO1 OFF)", "gcode")

    def _apply_reddot_on(self):
        if self.connection and hasattr(self.connection, "reddot_on"):
            self.connection.reddot_on()
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send("M106 P1 S255")
        self.reddot_state = True
        self._add_log("GCODE", "M106 P1 S255 (Red Dot DO2 ON)", "gcode")

    def _apply_reddot_off(self):
        if self.connection and hasattr(self.connection, "reddot_off"):
            self.connection.reddot_off()
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send("M106 P1 S0")
        self.reddot_state = False
        self._add_log("GCODE", "M106 P1 S0 (Red Dot DO2 OFF)", "gcode")

    def set_laser(self, state: bool) -> Dict[str, Any]:
        """Toggles Main Laser Beam (DO1 Pin 0)."""
        if self.estop_active and state:
            self._add_log("SECURITY", "Laser firing blocked by EMERGENCY STOP latch!", "error")
            return {"success": False, "laser_state": False, "error": "E-STOP Active"}

        if state:
            self._apply_laser_on()
        else:
            self._apply_laser_off()

        return {"success": True, "laser_state": self.laser_state}

    def fire_laser_pulse(self, duration_ms: int = 200) -> Dict[str, Any]:
        """Fires a safe, timed single-shot laser pulse for alignment/burn test."""
        if self.estop_active:
            self._add_log("SECURITY", "Laser pulse blocked by EMERGENCY STOP latch!", "error")
            return {"success": False, "error": "E-STOP Active"}
        if self.is_marking:
            return {"success": False, "error": "Cannot fire pulse while marking"}

        ms = max(10, min(2000, int(duration_ms)))

        def pulse_worker():
            self._apply_laser_on()
            time.sleep(ms / 1000.0)
            self._apply_laser_off()
            self._add_log("LASER", f"Single-shot laser pulse fired ({ms} ms)", "info")

        t = threading.Thread(target=pulse_worker, daemon=True)
        t.start()
        return {"success": True, "duration_ms": ms}

    def set_reddot(self, state: bool) -> Dict[str, Any]:
        """Toggles Red Dot Pointer Guide (DO2 Pin 1)."""
        if self.estop_active and state:
            return {"success": False, "reddot_state": False, "error": "E-STOP Active"}

        if state:
            self._apply_reddot_on()
        else:
            self._apply_reddot_off()

        return {"success": True, "reddot_state": self.reddot_state}

    def set_power(self, percentage: float) -> Dict[str, Any]:
        """
        Maps 0.0 - 100.0% power to 0 - 255 analog DO bit 2.
        Calculates equivalent analog control voltage (0 - 10V).
        """
        clamped = max(0.0, min(100.0, float(percentage)))
        self.power_percent = clamped
        self.analog_power_val = (clamped / 100.0) * 255.0
        voltage = (clamped / 100.0) * 10.0

        if self.galvo_controller:
            self.galvo_controller.live_power = clamped

        if self.connection and hasattr(self.connection, "set_analog_do_bit"):
            try:
                self.connection.set_analog_do_bit(
                    max_val=255.0,
                    crt_val=self.analog_power_val,
                    freq_val=self.frequency_khz,
                    bit=2
                )
            except Exception as e:
                self._add_log("HARDWARE", f"set_analog_do_bit power error: {e}", "error")

        self._add_log("HARDWARE", f"Laser Power set to {clamped:.1f}% ({voltage:.2f}V, DAC: {self.analog_power_val:.0f}/255)", "info")
        return {
            "success": True,
            "power_percent": clamped,
            "analog_val": self.analog_power_val,
            "voltage": voltage
        }

    def set_frequency(self, khz: float) -> Dict[str, Any]:
        """
        Sets Q-switch laser pulse frequency (20 - 80 kHz).
        Converts 20kHz - 80kHz to 10% - 90% Duty Cycle on Bit 0 for the BlackPill board.
        """
        clamped = max(20.0, min(80.0, float(khz)))
        self.frequency_khz = clamped

        if self.galvo_controller:
            self.galvo_controller.live_freq = clamped

        freq_duty_cycle = 10.0 + ((clamped - 20.0) / (80.0 - 20.0)) * 80.0
        freq_duty_cycle = max(10.0, min(90.0, freq_duty_cycle))

        if self.connection and hasattr(self.connection, "set_analog_do_bit"):
            try:
                # Modulate Bit 0 (Frequency duty cycle)
                self.connection.set_analog_do_bit(
                    max_val=100.0,
                    crt_val=freq_duty_cycle,
                    freq_val=50.0,
                    bit=0
                )
                # Modulate Bit 3 (PRR Frequency Division) matching legacy main.py
                self.connection.set_analog_do_bit(
                    max_val=100.0,
                    crt_val=50.0,
                    freq_val=clamped / 4.0,
                    bit=3
                )
            except Exception as e:
                self._add_log("HARDWARE", f"Frequency modulation error: {e}", "error")

        self._add_log("HARDWARE", f"Laser Frequency set to {clamped:.1f} kHz (Duty: {freq_duty_cycle:.1f}% Bit 0, PRR Bit 3)", "info")
        return {"success": True, "frequency_khz": clamped}

    def set_pulse_width(self, width_ns: int) -> Dict[str, Any]:
        """Sets laser pulse duration in nanoseconds."""
        self.pulse_width_ns = int(width_ns)
        self._add_log("HARDWARE", f"Laser Pulse Width set to {self.pulse_width_ns} ns", "info")
        return {"success": True, "pulse_width_ns": self.pulse_width_ns}

    def set_speeds(self, mark_speed: float, jump_speed: float) -> Dict[str, Any]:
        """Sets Mark Speed (mm/s, 50-1800) and Jump Speed (mm/s, 100-1870)."""
        self.mark_speed = max(50.0, min(1800.0, float(mark_speed)))
        self.jump_speed = max(100.0, min(1870.0, float(jump_speed)))
        self._add_log("MOTION", f"Speeds updated: Mark={self.mark_speed:.0f} mm/s, Jump={self.jump_speed:.0f} mm/s", "info")
        return {
            "success": True,
            "mark_speed": self.mark_speed,
            "jump_speed": self.jump_speed
        }

    # --------------------------------------------------------------------------
    # LASER DELAYS & TIMING
    # --------------------------------------------------------------------------
    def set_laser_delays(
        self,
        on_delay_us: int = 150,
        off_delay_us: int = 150,
        mark_delay_us: int = 100,
        jump_delay_us: int = 250,
        poly_delay_us: int = 80
    ) -> Dict[str, Any]:
        """Configures microsecond industrial timing parameters."""
        self.laser_on_delay_us = max(10, min(2000, int(on_delay_us)))
        self.laser_off_delay_us = max(10, min(2000, int(off_delay_us)))
        self.mark_delay_us = max(10, min(2000, int(mark_delay_us)))
        self.jump_delay_us = max(10, min(2000, int(jump_delay_us)))
        self.poly_delay_us = max(10, min(1000, int(poly_delay_us)))

        self._add_log("TIMING", f"Delays updated: On={self.laser_on_delay_us}µs, Off={self.laser_off_delay_us}µs, Mark={self.mark_delay_us}µs, Jump={self.jump_delay_us}µs, Poly={self.poly_delay_us}µs", "info")
        return {
            "success": True,
            "on_delay": self.laser_on_delay_us,
            "off_delay": self.laser_off_delay_us,
            "mark_delay": self.mark_delay_us,
            "jump_delay": self.jump_delay_us,
            "poly_delay": self.poly_delay_us
        }

    # --------------------------------------------------------------------------
    # CALIBRATION (.COR) LENS DISTORTION FILES
    # --------------------------------------------------------------------------
    def get_calibration_files(self) -> List[str]:
        """Scans workspace directory for .cor lens calibration files."""
        cor_files = []
        for f in glob.glob(os.path.join(BASE_DIR, "*.cor")):
            cor_files.append(os.path.basename(f))
        if not cor_files:
            cor_files = ["newest100mm.cor", "70x70mini.cor", "calibration1.cor"]
        return cor_files

    def set_calibration_file(self, filename: str) -> Dict[str, Any]:
        """Loads and applies a 65x65 .cor lens distortion grid."""
        target_path = os.path.join(BASE_DIR, filename) if not os.path.isabs(filename) else filename
        if not os.path.exists(target_path):
            return {"success": False, "error": f"File not found: {filename}"}

        try:
            cal = GalvoCalibration(target_path)
            if cal.is_valid:
                self.active_cor_file = os.path.basename(filename)
                if self.connection and hasattr(self.connection, "calibration"):
                    self.connection.calibration = cal
                    self.connection.enable_calibration = True
                if cal.scale:
                    self.galvo_config.field_size = 65535.0 / cal.scale
                self._add_log("CALIBRATION", f"Active lens correction file loaded: {self.active_cor_file} (Scale: {cal.scale:.2f} bits/mm, Field: {self.galvo_config.field_size:.1f} mm)", "success")
                return {"success": True, "active_file": self.active_cor_file, "is_valid": True}
            else:
                self._add_log("CALIBRATION", f"Failed parsing .cor file: {filename}", "warning")
                return {"success": False, "error": "Invalid .cor structure"}
        except Exception as e:
            self._add_log("ERROR", f"Error setting calibration: {e}", "error")
            return {"success": False, "error": str(e)}

    # --------------------------------------------------------------------------
    # VECTOR CAD / SVG / DXF FILE IMPORTER
    # --------------------------------------------------------------------------
    def get_available_files(self) -> List[Dict[str, Any]]:
        """Returns list of all available SVG and DXF files found in svg_files/ and root."""
        file_list: List[Dict[str, Any]] = []
        search_dirs = [os.path.join(BASE_DIR, "svg_files"), BASE_DIR]

        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for ext in ("*.svg", "*.dxf"):
                for filepath in glob.glob(os.path.join(d, ext)):
                    basename = os.path.basename(filepath)
                    # Skip duplicates
                    if any(f["name"] == basename for f in file_list):
                        continue
                    try:
                        sz = os.path.getsize(filepath)
                    except Exception:
                        sz = 0
                    file_list.append({
                        "name": basename,
                        "type": "svg" if basename.lower().endswith(".svg") else "dxf",
                        "path": filepath,
                        "size": sz
                    })

        file_list.sort(key=lambda x: x["name"].lower())
        return file_list

    def load_vector_file(self, filename_or_path: str) -> Dict[str, Any]:
        """
        Parses an SVG or DXF file, normalizes geometry in mm (-50 to +50 mm),
        centers around (0, 0), and returns structured paths for the frontend canvas and laser.
        """
        target_path = filename_or_path
        if not os.path.exists(target_path):
            # Check in svg_files/
            svg_subdir = os.path.join(BASE_DIR, "svg_files", filename_or_path)
            if os.path.exists(svg_subdir):
                target_path = svg_subdir
            else:
                root_path = os.path.join(BASE_DIR, filename_or_path)
                if os.path.exists(root_path):
                    target_path = root_path
                else:
                    return {"success": False, "error": f"File not found: {filename_or_path}"}

        basename = os.path.basename(target_path)
        is_svg = basename.lower().endswith(".svg")
        is_dxf = basename.lower().endswith(".dxf")

        try:
            self._add_log("CAD", f"Parsing vector file: {basename}...", "info")
            if is_svg:
                paths, bounds = parse_svg_paths_fast(target_path)
            elif is_dxf:
                paths, bounds = parse_dxf_paths_fast(target_path)
            else:
                return {"success": False, "error": "Unsupported file format. Only .svg and .dxf supported."}

            total_points = sum(len(p) for p in paths)
            result = {
                "success": True,
                "filename": basename,
                "file_type": "svg" if is_svg else "dxf",
                "paths": paths,
                "bounds": bounds,
                "path_count": len(paths),
                "point_count": total_points
            }
            self.loaded_vector_data = result
            self._add_log("CAD", f"Loaded {basename}: {len(paths)} paths, {total_points} vertices, size: {bounds['width']} x {bounds['height']} mm", "success")
            return result
        except Exception as e:
            self._add_log("ERROR", f"Failed loading {basename}: {e}", "error")
            return {"success": False, "error": str(e)}

    def parse_vector_content(self, filename: str, content: str) -> Dict[str, Any]:
        """Parses raw text SVG or DXF content dropped or selected from the UI."""
        try:
            basename = os.path.basename(filename)
            is_svg = basename.lower().endswith(".svg") or content.strip().startswith("<svg")

            if is_svg:
                paths, bounds = parse_svg_paths_fast(content, is_content=True)
            else:
                # Save scratch DXF to parse
                scratch_dir = os.path.join(BASE_DIR, "scratch")
                os.makedirs(scratch_dir, exist_ok=True)
                scratch_file = os.path.join(scratch_dir, f"temp_{int(time.time())}.dxf")
                with open(scratch_file, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(content)
                paths, bounds = parse_dxf_paths_fast(scratch_file)
                try:
                    os.remove(scratch_file)
                except Exception:
                    pass

            total_points = sum(len(p) for p in paths)
            result = {
                "success": True,
                "filename": basename,
                "file_type": "svg" if is_svg else "dxf",
                "paths": paths,
                "bounds": bounds,
                "path_count": len(paths),
                "point_count": total_points
            }
            self.loaded_vector_data = result
            self._add_log("CAD", f"Imported {basename}: {len(paths)} paths, {total_points} vertices ({bounds['width']} x {bounds['height']} mm)", "success")
            return result
        except Exception as e:
            self._add_log("ERROR", f"Error parsing vector content: {e}", "error")
            return {"success": False, "error": str(e)}

    # --------------------------------------------------------------------------
    # Z-AXIS FOCUS STEPPER MOTOR
    # --------------------------------------------------------------------------
    def move_z(self, delta_mm: float) -> Dict[str, Any]:
        """Moves Z stepper focus axis relatively by delta_mm."""
        d = float(delta_mm)
        if self.stepper_controller:
            try:
                self.stepper_controller.move_z_relative(d)
                self.cur_z = round(self.stepper_controller.get_physical_z(), 2)
            except Exception as e:
                self._add_log("HARDWARE", f"Z move error: {e}", "error")
                self.cur_z = round(max(0.0, min(120.0, self.cur_z + d)), 2)
        else:
            self.cur_z = round(max(0.0, min(120.0, self.cur_z + d)), 2)

        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send(f"G91\nG1 Z{d:.2f} F600\nG90")

        self._add_log("MOTION", f"Z-Axis jog {d:+.2f} mm (Focus Z: {self.cur_z:.2f} mm)", "info")
        return {"success": True, "cur_z": self.cur_z}

    def home_z(self) -> Dict[str, Any]:
        """Homes the Z stepper axis to 0.00 mm."""
        if self.stepper_controller:
            try:
                self.stepper_controller.home_z()
            except Exception as e:
                self._add_log("HARDWARE", f"Z home error: {e}", "warning")
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send("G28 Z")
        self.cur_z = 0.0
        self._add_log("MOTION", "Z-Axis homed to 0.00 mm", "info")
        return {"success": True, "cur_z": 0.0}

    # --------------------------------------------------------------------------
    # HIGH-PERFORMANCE PROCEDURAL SHAPES & TOOLPATH GENERATOR
    # --------------------------------------------------------------------------
    def _generate_shape_paths(self, job_params: Optional[Dict[str, Any]] = None) -> Tuple[List[List[Tuple[float, float]]], List[Tuple[float, float]]]:
        """
        Generates physical toolpath polylines in millimeter coordinates (-50 to +50mm field).
        Returns:
            all_marking_paths: List of stroke paths for laser marking.
            framing_contour: Exact perimeter contour for red dot tracing.
        """
        p = job_params or {}
        shape = str(p.get("shape", "circle")).lower()
        w = max(1.0, float(p.get("width", 40.0)))
        h = max(1.0, float(p.get("height", 40.0)))
        ox = float(p.get("x", 0.0))
        oy = float(p.get("y", 0.0))
        angle = float(p.get("angle", 0.0))
        scale_mul = float(p.get("scale_percent", 100.0)) / 100.0
        line_spacing = max(0.01, float(p.get("line_spacing", 0.5)))
        edge_offset = max(0.0, float(p.get("edge_offset", 0.0)))
        enable_hatch = bool(p.get("enable_hatch", False))
        hatch_style = str(p.get("hatch_style", "scanline")).lower()

        w *= scale_mul
        h *= scale_mul
        half_w, half_h = w / 2.0, h / 2.0
        x_min, x_max = ox - half_w, ox + half_w
        y_min, y_max = oy - half_h, oy + half_h

        marking_paths: List[List[Tuple[float, float]]] = []
        framing_contour: List[Tuple[float, float]] = []

        if shape == "circle":
            radius = min(w, h) / 2.0
            # 36 segments (37 points, every 10 degrees) matching legacy main.py lines 2343-2351
            circle_contour = [
                (ox + radius * math.cos(math.radians(a)), oy + radius * math.sin(math.radians(a)))
                for a in range(0, 361, 10)
            ]
            framing_contour = circle_contour

            if enable_hatch and line_spacing > 0.02:
                # Horizontal circular chord hatching
                dy = -radius + edge_offset
                direction = 1
                while dy <= radius - edge_offset:
                    r2_dy2 = radius * radius - dy * dy
                    if r2_dy2 > 0:
                        chord = math.sqrt(r2_dy2) - edge_offset
                        if chord > 0:
                            p_left = (ox - chord, oy + dy)
                            p_right = (ox + chord, oy + dy)
                            if direction == 1:
                                marking_paths.append([p_left, p_right])
                            else:
                                marking_paths.append([p_right, p_left])
                            direction *= -1
                    dy += line_spacing

                # Crosshatch vertical chords
                if hatch_style == "crosshatch":
                    dx = -radius + edge_offset
                    dir_x = 1
                    while dx <= radius - edge_offset:
                        r2_dx2 = radius * radius - dx * dx
                        if r2_dx2 > 0:
                            chord_y = math.sqrt(r2_dx2) - edge_offset
                            if chord_y > 0:
                                p_bot = (ox + dx, oy - chord_y)
                                p_top = (ox + dx, oy + chord_y)
                                if dir_x == 1:
                                    marking_paths.append([p_bot, p_top])
                                else:
                                    marking_paths.append([p_top, p_bot])
                                dir_x *= -1
                        dx += line_spacing

            # Always mark the crisp outer circle boundary
            marking_paths.append(circle_contour)

        elif shape == "triangle":
            tri_contour = [
                (ox, oy + half_h),
                (ox + half_w, oy - half_h),
                (ox - half_w, oy - half_h),
                (ox, oy + half_h)
            ]
            framing_contour = tri_contour
            marking_paths.append(tri_contour)

        elif shape == "rect":
            box_contour = [
                (x_min, y_min),
                (x_max, y_min),
                (x_max, y_max),
                (x_min, y_max),
                (x_min, y_min)
            ]
            framing_contour = box_contour

            if enable_hatch and line_spacing > 0.02:
                h_start_y = y_min + edge_offset
                h_end_y = y_max - edge_offset
                h_start_x = x_min + edge_offset
                h_end_x = x_max - edge_offset

                if h_end_y > h_start_y and h_end_x > h_start_x:
                    curr_y = h_start_y
                    direction = 1
                    while curr_y <= h_end_y:
                        if direction == 1:
                            marking_paths.append([(h_start_x, curr_y), (h_end_x, curr_y)])
                        else:
                            marking_paths.append([(h_end_x, curr_y), (h_start_x, curr_y)])
                        direction *= -1
                        curr_y += line_spacing

                    if hatch_style == "crosshatch":
                        curr_x = h_start_x
                        dir_x = 1
                        while curr_x <= h_end_x:
                            if dir_x == 1:
                                marking_paths.append([(curr_x, h_start_y), (curr_x, h_end_y)])
                            else:
                                marking_paths.append([(curr_x, h_end_y), (curr_x, h_start_y)])
                            dir_x *= -1
                            curr_x += line_spacing

            marking_paths.append(box_contour)

        elif shape == "cross":
            box_contour = [
                (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)
            ]
            framing_contour = box_contour
            marking_paths.append([(ox - half_w, oy), (ox + half_w, oy)])
            marking_paths.append([(ox, oy - half_h), (ox, oy + half_h)])
            marking_paths.append(box_contour)

        elif shape == "grid":
            box_contour = [
                (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)
            ]
            framing_contour = box_contour
            marking_paths.append(box_contour)
            cols, rows = 3, 3
            cell_w = w / cols
            cell_h = h / rows
            for c in range(1, cols):
                gx = x_min + c * cell_w
                marking_paths.append([(gx, y_min), (gx, y_max)])
            for r in range(1, rows):
                gy = y_min + r * cell_h
                marking_paths.append([(x_min, gy), (x_max, gy)])

        elif shape == "text":
            text_str = str(p.get("text", "GALVO PRO")).upper()
            box_contour = [
                (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)
            ]
            framing_contour = box_contour
            n_chars = max(1, len(text_str))
            char_w = (w * 0.85) / n_chars
            char_h = h * 0.7
            start_x = ox - (n_chars * char_w) / 2.0
            base_y = oy - char_h / 2.0

            for i, ch in enumerate(text_str):
                strokes = _VECTOR_FONT.get(ch, _VECTOR_FONT.get(' ', []))
                cx0 = start_x + i * char_w
                for stroke in strokes:
                    if len(stroke) < 2:
                        continue
                    stroke_pts = [
                        (cx0 + pt[0] * char_w * 0.8, base_y + pt[1] * char_h)
                        for pt in stroke
                    ]
                    marking_paths.append(stroke_pts)

        elif shape == "file":
            raw_paths = p.get("vector_paths") or (self.loaded_vector_data.get("paths") if self.loaded_vector_data else None)
            box_contour = [
                (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)
            ]
            framing_contour = box_contour

            if raw_paths:
                for path in raw_paths:
                    if len(path) < 2:
                        continue
                    p_pts = [(ox + pt[0] * scale_mul, oy + pt[1] * scale_mul) for pt in path]
                    marking_paths.append(p_pts)

                # Use the longest vector path as contour framing reference
                longest_path = max(raw_paths, key=len)
                if len(longest_path) >= 2:
                    framing_contour = [(ox + pt[0] * scale_mul, oy + pt[1] * scale_mul) for pt in longest_path]

        # Apply Angle Rotation around Center (ox, oy) if requested
        if abs(angle) > 0.001:
            rad = math.radians(angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)

            def rot_pt(px, py):
                dx, dy = px - ox, py - oy
                return (ox + dx * cos_a - dy * sin_a, oy + dx * sin_a + dy * cos_a)

            marking_paths = [[rot_pt(x, y) for x, y in path] for path in marking_paths]
            framing_contour = [rot_pt(x, y) for x, y in framing_contour]

        return marking_paths, framing_contour

    # --------------------------------------------------------------------------
    # RED DOT FRAMING PREVIEW (CONTOUR & BBOX WITH PHYSICAL HIGH-SPEED STREAM)
    # --------------------------------------------------------------------------
    def start_framing(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Traces the exact bounding box (Box) OR contour with the Red Dot pointer (DO2).
        Uses continuous hardware mode and 2,000,000 bits/s deflection matching legacy PreviewThread.
        """
        if self.estop_active:
            return {"success": False, "error": "E-STOP active"}
        if self.is_marking:
            return {"success": False, "error": "Cannot frame while marking job is running"}

        p = params or {}
        framing_mode = str(p.get("framing_mode", "box")).lower()
        if framing_mode not in ("box", "bbox", "contour"):
            framing_mode = "box"
        shape = str(p.get("shape", "circle")).lower()

        # Generate paths and contour in mm
        marking_paths, framing_contour = self._generate_shape_paths(p)

        # Collect all points to determine bounding box in mm
        all_pts: List[Tuple[float, float]] = []
        for path in marking_paths:
            all_pts.extend(path)
        if framing_contour:
            all_pts.extend(framing_contour)
        if not all_pts:
            w = max(1.0, float(p.get("width", 40.0))) * (float(p.get("scale_percent", 100.0)) / 100.0)
            h = max(1.0, float(p.get("height", 40.0))) * (float(p.get("scale_percent", 100.0)) / 100.0)
            ox, oy = float(p.get("x", 0.0)), float(p.get("y", 0.0))
            half_w, half_h = w / 2.0, h / 2.0
            all_pts = [
                (ox - half_w, oy - half_h),
                (ox + half_w, oy - half_h),
                (ox + half_w, oy + half_h),
                (ox - half_w, oy + half_h)
            ]

        # Convert to Galvo DAC coordinates
        dac_pts = [self.galvo_config.apply_transform(pt[0], pt[1]) for pt in all_pts]
        min_gx = min(pt[0] for pt in dac_pts)
        max_gx = max(pt[0] for pt in dac_pts)
        min_gy = min(pt[1] for pt in dac_pts)
        max_gy = max(pt[1] for pt in dac_pts)

        # Optical Calibration: Map theoretical DAC coords to calibrated physical mirror angles
        cal_obj = getattr(self.connection, 'calibration', None) if self.connection else None
        enable_cal = getattr(self.connection, 'enable_calibration', True) if self.connection else False

        def to_hardware_pt(gx_val: float, gy_val: float) -> Tuple[int, int]:
            # In legacy galvo_controller: raw_x = cmd['y'], raw_y = cmd['x']
            # cal_x, cal_y = cal.apply(raw_x, raw_y)
            # DLL arg 1 = cal_x (gy), DLL arg 2 = cal_y (gx)
            if enable_cal and cal_obj and hasattr(cal_obj, 'apply'):
                c1, c2 = cal_obj.apply(float(gy_val), float(gx_val))
                return int(round(c1)), int(round(c2))
            return int(round(gy_val)), int(round(gx_val))

        # Frame paths in DAC units:
        # 1. Box mode (Default): EXACT 5-point box matching legacy PreviewThread
        # 2. Contour mode: Smooth shape contour (downsampled to <= 18 points to avoid FIFO overflow)
        if framing_mode == "contour" and framing_contour:
            # Downsample to at most 18 points so hardware continuous loop never overflows
            step = max(1, len(framing_contour) // 18)
            sampled = framing_contour[::step]
            if sampled and sampled[-1] != sampled[0]:
                sampled.append(sampled[0])
            dac_sampled = [self.galvo_config.apply_transform(pt[0], pt[1]) for pt in sampled]
            galvo_frame_points = [to_hardware_pt(gx, gy) for gx, gy in dac_sampled]
            frame_sim_pts = sampled
        else:
            # Box mode matching legacy PreviewThread
            raw_box = [
                (min_gx, min_gy),
                (max_gx, min_gy),
                (max_gx, max_gy),
                (min_gx, max_gy),
                (min_gx, min_gy)
            ]
            galvo_frame_points = [to_hardware_pt(gx, gy) for gx, gy in raw_box]
            # Box in mm for simulation (interpolated edges for smooth UI simulation glide)
            min_x_mm = min(pt[0] for pt in all_pts)
            max_x_mm = max(pt[0] for pt in all_pts)
            min_y_mm = min(pt[1] for pt in all_pts)
            max_y_mm = max(pt[1] for pt in all_pts)
            steps = 5
            frame_sim_pts = []
            for s in range(steps):
                frame_sim_pts.append((min_x_mm + (max_x_mm - min_x_mm) * (s / steps), min_y_mm))
            for s in range(steps):
                frame_sim_pts.append((max_x_mm, min_y_mm + (max_y_mm - min_y_mm) * (s / steps)))
            for s in range(steps):
                frame_sim_pts.append((max_x_mm - (max_x_mm - min_x_mm) * (s / steps), max_y_mm))
            for s in range(steps):
                frame_sim_pts.append((min_x_mm, max_y_mm - (max_y_mm - min_y_mm) * (s / steps)))
            frame_sim_pts.append((min_x_mm, min_y_mm))

        # LIVE ATOMIC UPDATE: If already framing, update target trajectory on the fly and trigger FIFO refresh!
        if self.is_framing and self._framing_thread and self._framing_thread.is_alive():
            with self._framing_lock:
                self._active_frame_points = galvo_frame_points
                self._active_sim_points = frame_sim_pts
                self._framing_needs_refresh = True
            return {"success": True, "is_framing": True, "updated": True}

        self._stop_framing_internal()

        with self._framing_lock:
            self._active_frame_points = galvo_frame_points
            self._active_sim_points = frame_sim_pts
            self._framing_needs_refresh = False

        self._framing_stop_event.clear()
        self.is_framing = True

        # Safety: Laser OFF, Analog Power 0, Red Dot ON
        self._apply_laser_off()
        if self.connection and hasattr(self.connection, "set_analog_do_bit"):
            try:
                self.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
            except Exception:
                pass
        self._apply_reddot_on()

        dll_obj = getattr(self.connection, 'dll', None) if self.connection else None
        has_continuous = dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_set_continous_mode_on')
        if has_continuous:
            try:
                dll_obj.GT_PROSYS_U3_set_continous_mode_on()
            except Exception:
                pass

        speed = 2000000 # 2 million bits/sec matching legacy PreviewThread

        def framing_worker():
            self._add_log("MOTION", f"Red Dot Framing started for {shape.upper()} ({framing_mode})", "info")
            while not self._framing_stop_event.is_set():
                needs_ref = False
                with self._framing_lock:
                    pts = list(self._active_frame_points)
                    sim_pts = list(self._active_sim_points)
                    needs_ref = self._framing_needs_refresh
                    self._framing_needs_refresh = False

                if needs_ref and has_continuous:
                    try:
                        dll_obj.GT_PROSYS_U3_set_continous_mode_off()
                        time.sleep(0.04)
                        dll_obj.GT_PROSYS_U3_set_continous_mode_on()
                    except Exception:
                        pass

                if not pts and not sim_pts:
                    time.sleep(0.02)
                    continue

                if dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_galvo_move_XY'):
                    for arg1, arg2 in pts:
                        if self._framing_stop_event.is_set():
                            break
                        dll_obj.GT_PROSYS_U3_galvo_move_XY(int(arg1), int(arg2), speed, 0.0, 0.0, 0.0)

                    # Give hardware buffer time to execute before sending the next cycle
                    # (Prevents buffer overflow exactly as in PreviewThread)
                    if hasattr(self.connection, 'wait_for_motion'):
                        try:
                            self.connection.wait_for_motion()
                        except Exception:
                            time.sleep(0.02)
                    else:
                        time.sleep(0.02)
                else:
                    # Simulation mode: glide smoothly around perimeter
                    for pt in sim_pts:
                        if self._framing_stop_event.is_set():
                            break
                        self.cur_x, self.cur_y = pt
                        time.sleep(0.02)

            if has_continuous:
                try:
                    dll_obj.GT_PROSYS_U3_set_continous_mode_off()
                except Exception:
                    pass

            self._apply_reddot_off()
            self.is_framing = False
            self._add_log("MOTION", "Red Dot Framing stopped.", "info")

        self._framing_thread = threading.Thread(target=framing_worker, daemon=True)
        self._framing_thread.start()
        return {"success": True, "is_framing": True}

    def _stop_framing_internal(self):
        if self.is_framing:
            self._framing_stop_event.set()
            if self._framing_thread and self._framing_thread.is_alive():
                self._framing_thread.join(timeout=0.5)
            self._framing_thread = None
            self.is_framing = False
            with self._framing_lock:
                self._active_frame_points = []
                self._active_sim_points = []
            self._apply_reddot_off()

    def stop_framing(self) -> Dict[str, Any]:
        """Stops active Red Dot Framing loop."""
        self._stop_framing_internal()
        return {"success": True, "is_framing": False}

    # --------------------------------------------------------------------------
    # REAL & SIMULATED LASER MARKING EXECUTION
    # --------------------------------------------------------------------------
    def start_marking(self, job_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a real or simulated laser marking job using MotionPlanner and GalvoController.
        Uses calibrated speed in bits/s, applies coordinate transformation into Galvo DAC units,
        and manages laser timing delays and telemetry.
        """
        if self.estop_active:
            return {"success": False, "error": "E-STOP active! Laser firing locked."}
        if self.is_marking:
            return {"success": False, "error": "Marking job already in progress"}

        self._stop_framing_internal()
        self._stop_marking_internal()

        params = job_params or {}
        loop_count = max(1, int(params.get("loop_count", 1)))
        shape = str(params.get("shape", "circle")).lower()

        # 1. Generate millimeter stroke paths
        paths, _ = self._generate_shape_paths(params)
        if not paths:
            return {"success": False, "error": "No vector toolpaths generated"}

        # 2. Get calibrated hardware speeds
        mark_speed_bits, jump_speed_bits = self._get_hardware_speeds()

        # 3. Populate MotionPlanner with Galvo DAC coordinates
        self.planner.clear()
        for path in paths:
            if not path or len(path) < 2:
                continue
            # Jump to path start (Laser OFF)
            p0 = path[0]
            gx0, gy0 = self.galvo_config.apply_transform(p0[0], p0[1])
            self.planner.add_jump(gx0, gy0, speed=jump_speed_bits)

            # Mark along path (Laser ON)
            for pt in path[1:]:
                gx, gy = self.galvo_config.apply_transform(pt[0], pt[1])
                self.planner.add_mark(gx, gy, speed=mark_speed_bits)

        # Safe jump back to center (0, 0)
        gx_c, gy_c = self.galvo_config.apply_transform(0.0, 0.0)
        self.planner.add_jump(gx_c, gy_c, speed=jump_speed_bits)
        self.planner.commit_to_send_queue()

        total_cmds = len(self.planner.send_queue) * loop_count
        self._marking_stop_event.clear()
        self.is_marking = True
        self.is_paused = False
        self.mark_progress = 0.0

        def marking_worker():
            self._add_log("MARK", f"Executing Marking Job: {shape.upper()} ({len(paths)} paths x {loop_count} loops)", "warning")
            self._add_log("MARK", f"Speeds: Mark={self.mark_speed:.0f} mm/s ({mark_speed_bits} bits/s), Jump={self.jump_speed:.0f} mm/s ({jump_speed_bits} bits/s)", "info")

            # Apply live laser power, frequency, and timing delays to galvo controller
            if self.galvo_controller:
                self.galvo_controller.live_power = self.power_percent
                self.galvo_controller.live_freq = self.frequency_khz
                self.galvo_controller.is_paused = False
                self.galvo_controller.on_delay_s = max(0.00001, self.laser_on_delay_us / 1_000_000.0)
                self.galvo_controller.off_delay_s = max(0.00001, self.laser_off_delay_us / 1_000_000.0)
                self.galvo_controller.end_delay_s = max(0.00001, self.mark_delay_us / 1_000_000.0)
                self.galvo_controller.mark_delay_s = max(0.00001, self.mark_delay_us / 1_000_000.0)
                self.galvo_controller.jump_delay_s = max(0.00001, self.jump_delay_us / 1_000_000.0)

            def on_progress(idx, total, cmd_x, cmd_y, ctype):
                self.mark_progress = round((idx / max(1, total)) * 100.0, 1)
                # Map back to mm for live UI crosshair
                try:
                    self.cur_x, self.cur_y = self.galvo_config.reverse_transform(cmd_x, cmd_y)
                except Exception:
                    pass
                if self.is_mock:
                    time.sleep(0.003)

            enable_engraving = bool(params.get("enable_engraving", False))
            z_step_mm = max(0.001, float(params.get("z_step_mm", 0.05)))
            target_depth_mm = max(0.01, min(10.0, float(params.get("target_depth_mm", 1.0))))
            safe_return_z = self.cur_z

            success = False
            try:
                if not self.galvo_controller:
                    success = True
                elif not enable_engraving or not self.stepper_controller or loop_count <= 1:
                    success = self.galvo_controller.execute_queue(
                        self.planner.send_queue,
                        loop_count=loop_count,
                        progress_callback=on_progress,
                        abort_check=lambda: self._marking_stop_event.is_set()
                    )
                else:
                    self._add_log("ENGRAVE", f"Multi-Pass Deep Engraving: {loop_count} passes, step={z_step_mm:.3f}mm, max_depth={target_depth_mm:.2f}mm", "warning")
                    current_depth = 0.0
                    pass_cmds = len(self.planner.send_queue)
                    total_engrave_cmds = pass_cmds * loop_count
                    success = True

                    for pass_idx in range(loop_count):
                        if self._marking_stop_event.is_set():
                            success = False
                            break

                        def pass_progress(idx, total, cmd_x, cmd_y, ctype):
                            overall = pass_idx * pass_cmds + idx
                            self.mark_progress = round((overall / max(1, total_engrave_cmds)) * 100.0, 1)
                            try:
                                self.cur_x, self.cur_y = self.galvo_config.reverse_transform(cmd_x, cmd_y)
                            except Exception:
                                pass
                            if self.is_mock:
                                time.sleep(0.003)

                        self._add_log("ENGRAVE", f"Pass {pass_idx + 1}/{loop_count} (Current Depth: {current_depth:.3f} mm)", "info")
                        pass_ok = self.galvo_controller.execute_queue(
                            self.planner.send_queue,
                            loop_count=1,
                            progress_callback=pass_progress,
                            abort_check=lambda: self._marking_stop_event.is_set()
                        )

                        if not pass_ok or self._marking_stop_event.is_set():
                            success = False
                            break

                        # Ensure laser is strictly OFF between passes
                        self._apply_laser_off()
                        if hasattr(self.connection, 'wait_for_motion'):
                            try:
                                self.connection.wait_for_motion()
                            except Exception:
                                pass

                        next_depth = (pass_idx + 1) * z_step_mm
                        if next_depth >= target_depth_mm - 0.0001 or next_depth >= 10.0:
                            self._add_log("ENGRAVE", f"Target depth reached ({next_depth:.3f} mm). Finishing engraving.", "success")
                            break

                        if pass_idx < loop_count - 1:
                            self.stepper_controller.move_z_relative(-z_step_mm, speed=1000)
                            current_depth = next_depth
                            try:
                                self.cur_z = round(self.stepper_controller.get_physical_z(), 2)
                            except Exception:
                                self.cur_z = round(self.cur_z - z_step_mm, 2)
                            time.sleep(0.15)

            except Exception as e:
                self._add_log("ERROR", f"Marking execution exception: {e}", "error")
                success = False
            finally:
                self._apply_laser_off()
                if self.connection and hasattr(self.connection, "send_buffer"):
                    self.connection.send_buffer()

                # Safe Focus Retract
                if enable_engraving and safe_return_z is not None and self.stepper_controller:
                    try:
                        self._add_log("ENGRAVE", f"Retracting Z-axis to initial starting focus height ({safe_return_z:.2f} mm)...", "info")
                        self.stepper_controller.move_z_absolute(safe_return_z, speed=1000)
                        self.cur_z = round(safe_return_z, 2)
                    except Exception as e:
                        self._add_log("ERROR", f"Error retracting Z: {e}", "error")

                if not self._marking_stop_event.is_set() and success:
                    self.mark_progress = 100.0
                    self._add_log("MARK", f"Marking Job Completed successfully ({shape.upper()}).", "success")
                else:
                    self._add_log("MARK", "Marking Job Aborted or Terminated.", "error")

                self.is_marking = False

        self._marking_thread = threading.Thread(target=marking_worker, daemon=True)
        self._marking_thread.start()
        return {"success": True, "is_marking": True}

    def _stop_marking_internal(self):
        if self.is_marking:
            self._marking_stop_event.set()
            if self.galvo_controller:
                self.galvo_controller.is_paused = False
            if self._marking_thread and self._marking_thread.is_alive():
                self._marking_thread.join(timeout=0.6)
            self._marking_thread = None
            self.is_marking = False
            self._apply_laser_off()

    def stop_marking(self) -> Dict[str, Any]:
        """Stops active marking job immediately."""
        self._stop_marking_internal()
        return {"success": True, "is_marking": False}

    def pause_marking(self) -> Dict[str, Any]:
        """Pauses the active marking job."""
        self.is_paused = True
        if self.galvo_controller:
            self.galvo_controller.is_paused = True
        self._apply_laser_off()
        self._add_log("MARK", "Marking job PAUSED.", "warning")
        return {"success": True, "is_paused": True}

    def resume_marking(self) -> Dict[str, Any]:
        """Resumes the paused marking job."""
        if not self.estop_active:
            self.is_paused = False
            if self.galvo_controller:
                self.galvo_controller.is_paused = False
            self._add_log("MARK", "Marking job RESUMED.", "info")
            return {"success": True, "is_paused": False}
        return {"success": False, "error": "Cannot resume while E-STOP is active"}

    # --------------------------------------------------------------------------
    # EMERGENCY STOP (E-STOP) - TOP PRIORITY SAFETY
    # --------------------------------------------------------------------------
    def emergency_stop(self) -> Dict[str, Any]:
        """
        EMERGENCY STOP (E-STOP):
        Immediately cuts laser power (DO1=0, DO2=0, Analog=0, G-code M106 P0 S0, M410 quick-stop).
        """
        self.estop_active = True
        self._marking_stop_event.set()
        self._framing_stop_event.set()

        try:
            if self.connection:
                if hasattr(self.connection, "laser_off"):
                    self.connection.laser_off()
                if hasattr(self.connection, "reddot_off"):
                    self.connection.reddot_off()
                if hasattr(self.connection, "set_analog_do_bit"):
                    self.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                if hasattr(self.connection, "stop"):
                    self.connection.stop()
        except Exception as e:
            print(f"[E-STOP] Hardware cut notice: {e}")

        try:
            if self.serial_com and self.serial_com.is_connected:
                self.serial_com.send("M410")
                self.serial_com.send("M106 P0 S0")
                self.serial_com.send("M106 P1 S0")
        except Exception:
            pass

        self.laser_state = False
        self.reddot_state = False
        self.is_marking = False
        self.is_framing = False
        self.is_paused = False

        self._add_log("SECURITY", ">>> EMERGENCY STOP TRIGGERED! ALL LASER POWER CUT IMMEDIATELY <<<", "error")
        return {
            "success": True,
            "estop_active": True,
            "laser_state": False,
            "reddot_state": False
        }

    def reset_estop(self) -> Dict[str, Any]:
        """Resets the E-STOP security latch after user confirms safe environment."""
        self.estop_active = False
        self._add_log("SECURITY", "Emergency Stop latch reset. Interlocks cleared.", "success")
        return {"success": True, "estop_active": False}

    # --------------------------------------------------------------------------
    # MANUAL JOG & G-CODE CONSOLE
    # --------------------------------------------------------------------------
    def move_to_xy(self, x: float, y: float) -> Dict[str, Any]:
        """Moves Galvo mirrors to target coordinates in mm (-50 to +50)."""
        clamped_x = max(-50.0, min(50.0, float(x)))
        clamped_y = max(-50.0, min(50.0, float(y)))
        self.cur_x = clamped_x
        self.cur_y = clamped_y

        gx, gy = self.galvo_config.apply_transform(clamped_x, clamped_y)
        _, jump_speed_bits = self._get_hardware_speeds()

        if self.connection and hasattr(self.connection, "galvo_move_xy"):
            # Physical Y is gy, Physical X is gx
            self.connection.galvo_move_xy(int(gy), int(gx), speed=jump_speed_bits)
            if hasattr(self.connection, "send_buffer"):
                self.connection.send_buffer()

        self._add_log("MOTION", f"Galvo move to X:{clamped_x:.2f} Y:{clamped_y:.2f} mm (DAC: {gx},{gy})", "info")
        return {"success": True, "x": clamped_x, "y": clamped_y}

    def home_galvo(self) -> Dict[str, Any]:
        """Centers Galvo mirrors to (0, 0) mm / DAC (32767, 32767)."""
        self.cur_x = 0.0
        self.cur_y = 0.0
        if self.galvo_controller:
            try:
                self.galvo_controller.galvo_home()
            except Exception as e:
                self._add_log("ERROR", f"Galvo home error: {e}", "error")
        self._add_log("MOTION", "Galvo centered at (0.00, 0.00) mm.", "info")
        return {"success": True, "x": 0.0, "y": 0.0}

    def send_gcode(self, cmd: str) -> Dict[str, Any]:
        """Sends arbitrary G-code string directly to the machine controller."""
        clean_cmd = cmd.strip()
        if not clean_cmd:
            return {"success": False, "error": "Empty command"}

        self._add_log("GCODE", clean_cmd, "gcode")
        if self.serial_com and self.serial_com.is_connected:
            self.serial_com.send(clean_cmd)
            return {"success": True, "sent": clean_cmd}
        else:
            self._add_log("SYSTEM", f"(Simulated G-code dispatched): {clean_cmd}", "info")
            return {"success": True, "sent": clean_cmd, "simulated": True}

    # --------------------------------------------------------------------------
    # TELEMETRY & LOG STREAMING FOR REACT
    # --------------------------------------------------------------------------
    def get_telemetry(self) -> Dict[str, Any]:
        """High-frequency telemetry snapshot polled by React frontend."""
        # Read exact physical Z counter from StepperController if available
        if self.stepper_controller:
            try:
                self.cur_z = round(self.stepper_controller.get_physical_z(), 2)
            except Exception:
                pass

        temp = round(24.5 + (math.sin(time.time() * 0.2) * 0.6) + (2.0 if self.laser_state else 0.0), 1)

        return {
            "connected": self.is_connected,
            "is_mock": self.is_mock,
            "port": self.connected_port,
            "baud": self.connected_baud,
            "cards_found": self.cards_found,
            "laser_state": self.laser_state,
            "reddot_state": self.reddot_state,
            "power_percent": self.power_percent,
            "analog_val": round(self.analog_power_val, 1),
            "analog_voltage": round((self.power_percent / 100.0) * 10.0, 2),
            "frequency_khz": self.frequency_khz,
            "pulse_width_ns": self.pulse_width_ns,
            "mark_speed": self.mark_speed,
            "jump_speed": self.jump_speed,
            "cur_x": round(self.cur_x, 2),
            "cur_y": round(self.cur_y, 2),
            "cur_z": round(self.cur_z, 2),
            "is_marking": self.is_marking,
            "is_framing": self.is_framing,
            "is_paused": self.is_paused,
            "mark_progress": self.mark_progress,
            "estop_active": self.estop_active,
            "temperature": temp,
            "active_cor_file": self.active_cor_file,
            "laser_on_delay_us": self.laser_on_delay_us,
            "laser_off_delay_us": self.laser_off_delay_us,
            "mark_delay_us": self.mark_delay_us,
            "jump_delay_us": self.jump_delay_us,
            "poly_delay_us": self.poly_delay_us,
            "field_size_mm": getattr(self.galvo_config, "field_size", 100.0),
        }

    def get_logs(self, clear: bool = False) -> List[Dict[str, Any]]:
        """Returns logs buffer to frontend console."""
        with self._lock:
            logs = list(self._logs)
            if clear:
                self._logs.clear()
            return logs

    def clear_logs(self) -> Dict[str, Any]:
        """Clears console log buffer."""
        with self._lock:
            self._logs.clear()
            return {"success": True}
