import sys
import os
import math
import json
import copy
import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtGui import QPainterPath, QFont, QPolygonF, QFontDatabase
from PySide6.QtWidgets import QApplication

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from core.motion_planner import MotionPlanner, compute_hatch_geometry
from core.coordinate_mapper import CoordinateConfig
from core.mk_lib.tools.jhfparser import SimplexFont, JhfPath
from galvo_threads import ExecutionThread, PreviewThread
from dxf import DXFParser
from core.svg_parser import SVGParser
from gerber_parser import GerberParser
from core.image_parser import ImageParser
from configparser import ConfigParser
from PySide6.QtCore import QUrl
from urllib.parse import unquote

try:
    import qrcode
except ImportError:
    qrcode = None


class MockMainWindow:
    """Lightweight adapter providing required galvo controller & planner attributes if QWidget is used."""
    def __init__(self, galvo_controller):
        self.galvo_controller = galvo_controller
        self.planner = MotionPlanner()
        self.galvo_config = CoordinateConfig()
        self.galvo_threads = {}


class CadBridge(QObject):
    """
    High-Performance QObject Bridge connecting the QML CAD Canvas directly
    to the Galvo Hardware Controller, MotionPlanner, Red-Light Guide (F1),
    Laser Execution Engine (F2), and Vector DXF/SVG Parsers.
    """
    cadStateChanged = Signal()
    framingChanged = Signal(bool)
    markingChanged = Signal(bool)
    progressChanged = Signal(int, int, float)  # current, total, percent (0.0 to 100.0)
    shapeCountChanged = Signal(int)
    shapesImported = Signal(list)              # Emits list of parsed shapes for QML
    statusMessageChanged = Signal(str)
    autoFocusZChanged = Signal(bool)
    fieldSizeChanged = Signal(float)
    fieldSettingsChanged = Signal(float, float, float, float) # size, off_x, off_y, angle
    hardwareAlert = Signal(str, str) # title, message
    hatchProfilesChanged = Signal()
    pensChanged = Signal(list)

    CONFIG_FILE = os.path.join(_root, "config", "config.ini")
    PENS_CONFIG_FILE = os.path.join(_root, "config", "pens.json")

    def __init__(self, galvo_bridge=None, jog_bridge=None, parent=None):
        super().__init__(parent)
        self.galvo_bridge = galvo_bridge
        self.jog_bridge = jog_bridge
        self.galvo_controller = galvo_bridge.controller if galvo_bridge else None

        self.planner = MotionPlanner()
        self.galvo_config = CoordinateConfig()

        self._shapes = []
        self._is_framing = False
        self._is_marking = False
        self._is_paused = False
        self._auto_focus_z = True             # Enabled by default
        self._shape_count = 0
        self._field_size = 70.0
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._angle = 0.0
        self._status_message = "Ready"

        self.preview_thread = None
        self.exec_thread = None

        # Load persisted [GalvoField] and Hatch Profiles from config/config.ini
        self._mark_contour = True
        self._mark_contour_first = True
        self._hatch_profiles = {1: self._default_hatch_profile(), 2: self._default_hatch_profile(), 3: self._default_hatch_profile()}
        self._load_config()
        self._load_hatch_profiles()
        self._sync_calibration_and_field_size()
        self._pens = self._load_pens()

        if self.galvo_bridge:
            try:
                self.galvo_bridge.connectionChanged.connect(self._on_galvo_connection_changed)
            except Exception as e:
                print(f"[CadBridge] Connection listener error: {e}")

        # Available Fonts for CAD text entity creation
        common_fonts = [
            "Simplex (Single-Stroke Vector)",
            "Arial",
            "Segoe UI",
            "Leelawadee UI",
            "Times New Roman",
            "Calibri",
            "Consolas",
            "Courier New",
            "Verdana",
            "Tahoma",
            "Trebuchet MS",
            "Georgia",
            "Impact"
        ]
        try:
            db_fams = list(QFontDatabase.families())
            for f in db_fams:
                if f not in common_fonts:
                    common_fonts.append(f)
        except Exception:
            pass
        self._available_fonts = common_fonts

        # Adapter for legacy CadCanvasWidget if requested
        self._adapter = MockMainWindow(self.galvo_controller)
        self.cad_widget = None

    def _on_galvo_connection_changed(self, connected, is_demo, msg):
        """Called whenever galvo hardware connection state changes."""
        self._sync_calibration_and_field_size()

    def _sync_calibration_and_field_size(self):
        """
        Exact math from main.py (lines 2325-2335 and 2470-2485):
        Checks if a .cor calibration file is loaded and provides a native scale.
        If calib.scale is present (e.g. 533.89 from newest100mm.cor):
            galvo_units_per_mm = calib.scale
            lens_size = 65535.0 / calib.scale (122.75 mm)
            self.galvo_config.field_size = lens_size
        Else:
            f_size = self._field_size if self._field_size > 0 else 100.0
            galvo_units_per_mm = 65535.0 / f_size
            lens_size = f_size
            self.galvo_config.field_size = lens_size

        Returns: (calib_scale, galvo_units_per_mm, lens_size)
        """
        calib_scale = None
        ctrl = self.galvo_controller
        if ctrl and getattr(ctrl, 'connection', None):
            if hasattr(ctrl.connection, 'calibration'):
                calib = ctrl.connection.calibration
                if calib and getattr(calib, 'is_valid', False) and getattr(calib, 'scale', None) is not None:
                    calib_scale = calib.scale

        # Fallback to local newest100mm.cor if controller connection not initialized yet (matching main.py line 86-89)
        if calib_scale is None:
            cor_path = os.path.join(_root, "newest100mm.cor")
            if os.path.exists(cor_path):
                try:
                    from core.calibration import GalvoCalibration
                    calib_obj = GalvoCalibration(cor_path)
                    if calib_obj.is_valid and calib_obj.scale is not None:
                        calib_scale = calib_obj.scale
                except Exception:
                    pass

        lens_size = self._field_size if self._field_size > 0 else 70.0
        self.galvo_config.field_size = lens_size

        if calib_scale:
            galvo_units_per_mm = float(calib_scale)
            self.galvo_config.calib_scale = galvo_units_per_mm
            print(f"[CadBridge] Lens Field: {lens_size:.1f}mm | Optical Scale: {galvo_units_per_mm:.2f} bits/mm (.cor calibration)")
        else:
            galvo_units_per_mm = 65535.0 / lens_size
            self.galvo_config.calib_scale = None
            print(f"[CadBridge] Lens Field: {lens_size:.1f}mm | Linear Scale: {galvo_units_per_mm:.2f} bits/mm")

        return calib_scale, galvo_units_per_mm, lens_size

    # ---------------- Field Configuration (config.ini [GalvoField]) ---------------- #

    def _load_config(self):
        """Loads lens field size and geometric mapping from config/config.ini."""
        if not os.path.exists(self.CONFIG_FILE):
            return
        parser = ConfigParser()
        try:
            parser.read(self.CONFIG_FILE)
            if parser.has_section("GalvoField"):
                self._field_size = float(parser.get("GalvoField", "field_size", fallback="70.0"))
                self._offset_x = float(parser.get("GalvoField", "offset_x", fallback="0.0"))
                self._offset_y = float(parser.get("GalvoField", "offset_y", fallback="0.0"))
                self._angle = float(parser.get("GalvoField", "angle", fallback="0.0"))
                self.galvo_config.field_size = self._field_size
                self.galvo_config.offset_x = self._offset_x
                self.galvo_config.offset_y = self._offset_y
                self.galvo_config.angle = self._angle

                self.galvo_config.galvo_1_is_x = parser.getboolean("GalvoField", "galvo1_x", fallback=False)
                self.galvo_config.g1_negate = parser.getboolean("GalvoField", "g1_negate", fallback=False)
                self.galvo_config.g1_scale = float(parser.get("GalvoField", "g1_scale", fallback="100.0"))
                self.galvo_config.g1_bulge = float(parser.get("GalvoField", "g1_barrel", fallback="1.0"))
                self.galvo_config.g1_skew = float(parser.get("GalvoField", "g1_par", fallback="1.0"))
                self.galvo_config.g1_trapezoid = float(parser.get("GalvoField", "g1_trapezoid", fallback="1.0"))

                self.galvo_config.g2_negate = parser.getboolean("GalvoField", "g2_negate", fallback=False)
                self.galvo_config.g2_scale = float(parser.get("GalvoField", "g2_scale", fallback="100.0"))
                self.galvo_config.g2_bulge = float(parser.get("GalvoField", "g2_barrel", fallback="1.0"))
                self.galvo_config.g2_skew = float(parser.get("GalvoField", "g2_par", fallback="1.0"))
                self.galvo_config.g2_trapezoid = float(parser.get("GalvoField", "g2_trapezoid", fallback="1.0"))

                self._pos_after_mark = parser.get("GalvoField", "pos_after_mark", fallback="confgalvocent")
                self._sp_x = float(parser.get("GalvoField", "sp_x", fallback="0.0"))
                self._sp_y = float(parser.get("GalvoField", "sp_y", fallback="0.0"))

                print(f"[CadBridge] Loaded [GalvoField]: field_size={self._field_size}mm, offset=({self._offset_x}, {self._offset_y}), angle={self._angle}°")
        except Exception as e:
            print(f"[CadBridge] Error loading config.ini [GalvoField]: {e}")

    def _save_config(self):
        """Saves lens field size and geometric mapping to config/config.ini."""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        parser = ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            parser.read(self.CONFIG_FILE)
        if not parser.has_section("GalvoField"):
            parser.add_section("GalvoField")
        parser.set("GalvoField", "field_size", f"{self._field_size:.1f}")
        parser.set("GalvoField", "offset_x", f"{self._offset_x:.2f}")
        parser.set("GalvoField", "offset_y", f"{self._offset_y:.2f}")
        parser.set("GalvoField", "angle", f"{self._angle:.2f}")
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
            print(f"[CadBridge] Saved [GalvoField] field_size={self._field_size:.1f}mm to {self.CONFIG_FILE}")
        except Exception as e:
            print(f"[CadBridge] Error saving config.ini [GalvoField]: {e}")


    def _default_pens(self):
        return [
            {"id": 0, "name": "Pen 0 (Default)", "color": "#00E5FF", "speed": 1200, "power": 50, "freq": 35, "passes": 1},
            {"id": 1, "name": "Pen 1 (Blue)",    "color": "#2563EB", "speed": 1800, "power": 40, "freq": 45, "passes": 1},
            {"id": 2, "name": "Pen 2 (Red)",     "color": "#EF4444", "speed": 800,  "power": 75, "freq": 30, "passes": 2},
            {"id": 3, "name": "Pen 3 (Green)",   "color": "#10B981", "speed": 2000, "power": 30, "freq": 60, "passes": 1},
            {"id": 4, "name": "Pen 4 (Amber)",   "color": "#F59E0B", "speed": 1500, "power": 60, "freq": 40, "passes": 1},
            {"id": 5, "name": "Pen 5 (Purple)",  "color": "#A855F7", "speed": 1000, "power": 70, "freq": 35, "passes": 1},
            {"id": 6, "name": "Pen 6 (Cyan)",    "color": "#06B6D4", "speed": 2200, "power": 25, "freq": 70, "passes": 1},
            {"id": 7, "name": "Pen 7 (Brown)",   "color": "#854D0E", "speed": 600,  "power": 85, "freq": 25, "passes": 3}
        ]

    def _load_pens(self):
        if os.path.exists(self.PENS_CONFIG_FILE):
            try:
                with open(self.PENS_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        print(f"[CadBridge] Loaded {len(data)} Pens from {self.PENS_CONFIG_FILE}")
                        return data
            except Exception as e:
                print(f"[CadBridge] Error loading pens.json: {e}")
        return self._default_pens()

    @Slot(result=list)
    def getPens(self):
        return self._pens

    @Slot(list)
    def savePens(self, pens_list):
        try:
            self._pens = list(pens_list)
            os.makedirs(os.path.dirname(self.PENS_CONFIG_FILE), exist_ok=True)
            with open(self.PENS_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._pens, f, indent=2)
            print(f"[CadBridge] Saved {len(self._pens)} Pens to {self.PENS_CONFIG_FILE}")
            self.pensChanged.emit(self._pens)
        except Exception as e:
            print(f"[CadBridge] Error saving pens: {e}")

    @Slot(str, str, result=int)
    def addPen(self, name="", color=""):
        next_id = 0
        for p in self._pens:
            if p.get("id", 0) >= next_id:
                next_id = p.get("id", 0) + 1
        distinct_colors = ["#EC4899", "#14B8A6", "#EAB308", "#6366F1", "#F97316", "#84CC16", "#06B6D4", "#A855F7", "#F43F5E", "#3B82F6"]
        col = color if color else distinct_colors[(next_id - 8) % len(distinct_colors)]
        p_name = name if name else f"Pen {next_id}"
        new_pen = {
            "id": next_id,
            "name": p_name,
            "color": col,
            "speed": 1500,
            "power": 50,
            "freq": 35,
            "passes": 1
        }
        self._pens.append(new_pen)
        self.savePens(self._pens)
        print(f"[CadBridge] Added Pen {next_id} ({p_name}, {col})")
        return next_id

    @Slot(int, str)
    def updatePenColor(self, pen_id, color):
        for p in self._pens:
            if p.get("id") == pen_id:
                p["color"] = color
                break
        self.savePens(self._pens)
        print(f"[CadBridge] Updated Pen {pen_id} color to {color}")

    @Slot(int, str, result=bool)
    def updatePenName(self, pen_id, name):
        for p in self._pens:
            if p.get("id") == pen_id:
                p["name"] = name
                self.savePens(self._pens)
                return True
        return False

    @Slot(int)
    def deletePen(self, pen_id):
        if pen_id == 0:
            return
        self._pens = [p for p in self._pens if p.get("id") != pen_id]
        self.savePens(self._pens)
        print(f"[CadBridge] Deleted Pen {pen_id}")

    @Slot(float)
    def setFieldSize(self, size: float):
        """Updates and persists Galvo lens optical field size (mm)."""
        if size <= 0:
            return
        self._field_size = float(size)
        self.galvo_config.field_size = self._field_size
        self._save_config()
        self.fieldSizeChanged.emit(self._field_size)
        self.cadStateChanged.emit()
        self._set_status(f"Optical Field Size updated to {self._field_size:.1f} mm")

    @Slot(float, float, float, float)
    def setFieldSettings(self, size: float, off_x: float, off_y: float, angle: float):
        """Updates and persists full Galvo lens & coordinate transformation settings."""
        if size > 0:
            self._field_size = float(size)
            self.galvo_config.field_size = self._field_size
        self._offset_x = float(off_x)
        self._offset_y = float(off_y)
        self._angle = float(angle)
        self.galvo_config.offset_x = self._offset_x
        self.galvo_config.offset_y = self._offset_y
        self.galvo_config.angle = self._angle
        self._save_config()
        self.fieldSizeChanged.emit(self._field_size)
        self.fieldSettingsChanged.emit(self._field_size, self._offset_x, self._offset_y, self._angle)
        self.cadStateChanged.emit()
        self._set_status(f"Field settings applied ({self._field_size:.1f}mm, off=[{self._offset_x:.1f}, {self._offset_y:.1f}], rot={self._angle:.1f}°)")

    @Slot(float, float, float, float, bool, bool, float, float, float, float, bool, float, float, float, float, str, float, float)
    def setFullGalvoConfig(self, field_size: float, off_x: float, off_y: float, angle: float, galvo1_x: bool,
                           g1_neg: bool, g1_scale: float, g1_bar: float, g1_par: float, g1_trap: float,
                           g2_neg: bool, g2_scale: float, g2_bar: float, g2_par: float, g2_trap: float,
                           pos_after: str, sp_x: float, sp_y: float, save_to_disk: bool = False):
        """Applies complete optical distortion correction, mirror mappings, and park positions."""
        changed = (
            abs(self._field_size - float(field_size)) > 0.001 or
            abs(self._offset_x - float(off_x)) > 0.001 or
            abs(self._offset_y - float(off_y)) > 0.001 or
            abs(self._angle - float(angle)) > 0.001 or
            abs(self.galvo_config.g1_scale - float(g1_scale)) > 0.0001 or
            abs(self.galvo_config.g2_scale - float(g2_scale)) > 0.0001
        )
        if field_size > 0:
            self._field_size = float(field_size)
            self.galvo_config.field_size = self._field_size
        self._offset_x = float(off_x)
        self._offset_y = float(off_y)
        self._angle = float(angle)
        self.galvo_config.offset_x = self._offset_x
        self.galvo_config.offset_y = self._offset_y
        self.galvo_config.angle = self._angle

        self.galvo_config.galvo_1_is_x = bool(galvo1_x)
        self.galvo_config.g1_negate = bool(g1_neg)
        self.galvo_config.g1_scale = float(g1_scale)
        self.galvo_config.g1_bulge = float(g1_bar)
        self.galvo_config.g1_skew = float(g1_par)
        self.galvo_config.g1_trapezoid = float(g1_trap)

        self.galvo_config.g2_negate = bool(g2_neg)
        self.galvo_config.g2_scale = float(g2_scale)
        self.galvo_config.g2_bulge = float(g2_bar)
        self.galvo_config.g2_skew = float(g2_par)
        self.galvo_config.g2_trapezoid = float(g2_trap)

        self._pos_after_mark = str(pos_after)
        self._sp_x = float(sp_x)
        self._sp_y = float(sp_y)

        if save_to_disk:
            self._save_config()

        if changed:
            self.fieldSizeChanged.emit(self._field_size)
            self.fieldSettingsChanged.emit(self._field_size, self._offset_x, self._offset_y, self._angle)
            self.cadStateChanged.emit()

    # ---------------- Properties for QML ---------------- #

    def get_auto_focus_z(self) -> bool:
        return self._auto_focus_z

    def set_auto_focus_z(self, val: bool):
        if self._auto_focus_z != val:
            self._auto_focus_z = val
            self.autoFocusZChanged.emit(self._auto_focus_z)

    def get_is_framing(self) -> bool:
        return self._is_framing

    def get_is_marking(self) -> bool:
        return self._is_marking

    def get_is_paused(self) -> bool:
        return self._is_paused

    def get_shape_count(self) -> int:
        return self._shape_count

    def get_field_size(self) -> float:
        return self._field_size

    def get_status_message(self) -> str:
        return self._status_message

    @Slot(str)
    def set_status_message(self, msg: str):
        self._set_status(str(msg))

    isFraming = Property(bool, get_is_framing, notify=framingChanged)
    isMarking = Property(bool, get_is_marking, notify=markingChanged)
    isPaused = Property(bool, get_is_paused, notify=cadStateChanged)
    autoFocusZ = Property(bool, get_auto_focus_z, set_auto_focus_z, notify=autoFocusZChanged)
    shapeCount = Property(int, get_shape_count, notify=shapeCountChanged)
    fieldSize = Property(float, get_field_size, setFieldSize, notify=fieldSizeChanged)
    offsetX = Property(float, lambda self: self._offset_x, notify=fieldSettingsChanged)
    offsetY = Property(float, lambda self: self._offset_y, notify=fieldSettingsChanged)
    fieldAngle = Property(float, lambda self: self._angle, notify=fieldSettingsChanged)
    galvo1X = Property(bool, lambda self: getattr(self.galvo_config, 'galvo_1_is_x', False), notify=cadStateChanged)
    g1Scale = Property(float, lambda self: getattr(self.galvo_config, 'g1_scale', 100.0), notify=cadStateChanged)
    g2Scale = Property(float, lambda self: getattr(self.galvo_config, 'g2_scale', 100.0), notify=cadStateChanged)
    statusMessage = Property(str, get_status_message, set_status_message, notify=statusMessageChanged)
    availableFonts = Property(list, lambda self: self._available_fonts, constant=True)

    @Slot(result=list)
    def getAvailableFonts(self) -> list:
        """Returns full list of TrueType and Vector fonts available on system."""
        return self._available_fonts

    @Slot(str, str, float, bool, bool, result='QVariant')
    def measureText(self, text: str, font_family: str, font_height_mm: float, bold: bool, italic: bool):
        """
        Calculates exact CAD millimeter bounding dimensions for a given text string,
        font family, font height, and style.
        """
        try:
            h_mm = max(0.5, float(font_height_mm))
            if not text:
                return {"wMm": round(h_mm * 2.0, 2), "hMm": round(h_mm, 2)}

            if font_family and font_family.startswith("Simplex"):
                # Approximate 0.7 aspect ratio for Simplex stroke characters
                w_mm = len(text) * h_mm * 0.7
                return {"wMm": round(w_mm, 2), "hMm": round(h_mm, 2)}

            qf = QFont(font_family if font_family else "Arial", int(round(h_mm * 10)))
            qf.setBold(bool(bold))
            qf.setItalic(bool(italic))
            path = QPainterPath()
            path.addText(0, 0, qf, text)
            br = path.boundingRect()
            if br.height() > 0:
                scale = h_mm / br.height()
                w_mm = float(br.width() * scale)
                return {"wMm": round(w_mm, 2), "hMm": round(h_mm, 2)}
        except Exception as e:
            print(f"[CadBridge] measureText error: {e}")
        return {"wMm": round(float(len(text) * font_height_mm * 0.7), 2), "hMm": round(float(font_height_mm), 2)}

    @Slot('QVariant', int, int, float, float, result='QVariant')
    def applyArray(self, shape_dict: dict, count_x: int, count_y: int, inc_x_mm: float, inc_y_mm: float):
        """
        Replicates the given shape entity into a 2D array grid of count_x by count_y items.
        Returns list of newly generated shape entities.
        """
        if not shape_dict or (count_x <= 1 and count_y <= 1):
            return []

        base = dict(shape_dict)
        base_x = float(base.get("xMm", 0.0))
        base_y = float(base.get("yMm", 0.0))
        orig_id = int(base.get("id", 1))
        orig_name = str(base.get("name", "Shape"))

        new_shapes = []
        idx = 1
        for ix in range(count_x):
            for iy in range(count_y):
                if ix == 0 and iy == 0:
                    continue
                clone = copy.deepcopy(base)
                clone["id"] = orig_id + 1000 + idx
                clone["name"] = f"{orig_name}_r{iy+1}_c{ix+1}"
                clone["xMm"] = round(base_x + ix * inc_x_mm, 3)
                clone["yMm"] = round(base_y + iy * inc_y_mm, 3)
                new_shapes.append(clone)
                idx += 1

        print(f"[CadBridge] Generated array replication: {len(new_shapes)} clones from {orig_name}")
        return new_shapes

    # ---------------- Focal Alignment (Matching main.py) ---------------- #

    def _align_z_to_focus(self) -> bool:
        """
        Homes Z axis to limit switch and moves stepper head directly to
        the calculated workpiece focus height (matching main.py lines 2795-2838).
        """
        if not self.jog_bridge:
            return True

        target_z = float(getattr(self.jog_bridge, 'targetFocusZ', 27.0))
        current_z = float(getattr(self.jog_bridge, 'zPos', -999.0))

        # If already at focus plane, no need to re-home and re-move
        if abs(current_z - target_z) < 0.05:
            print(f"[CadBridge] Z-Axis already positioned at focal plane: {current_z:.2f} mm")
            return True

        self._set_status(f"Aligning Z-Axis to workpiece focus: {target_z:.2f} mm...")
        print(f"[CadBridge] Initiating Z-axis focal alignment: current={current_z:.2f} mm -> target={target_z:.2f} mm")

        stepper = getattr(self.jog_bridge, 'stepper', None)
        if stepper and getattr(stepper.connection, 'is_initialized', False):
            app_inst = QApplication.instance()
            print(f"[CadBridge] Homing Z axis to physical limit switch...")
            if not stepper.home_z(app_instance=app_inst):
                print("[CadBridge] Warning: Z-axis limit homing failed. Moving directly to target focus.")
            
            print(f"[CadBridge] Moving Z axis to focus position: {target_z:.2f} mm")
            stepper.move_z_absolute(target_z, speed=3000)
            self.jog_bridge._z = target_z
            self.jog_bridge.zPosChanged.emit(target_z)

            # Wait until stepper motor finishes moving before starting laser
            import time
            start_wait = time.time()
            while time.time() < getattr(stepper, 'next_ready_time', time.time()) and (time.time() - start_wait) < 15.0:
                if app_inst:
                    app_inst.processEvents()
                time.sleep(0.05)
        else:
            # Simulation / Demo mode
            self.jog_bridge.moveToTargetFocus()

        self._set_status(f"Z-Axis aligned at focal plane ({target_z:.2f} mm)")
        print(f"[CadBridge] Z-Axis aligned at focal plane: {target_z:.2f} mm")
        return True

    @Slot()
    def moveToFocus(self):
        """Manually commands Z stepper axis to go to calculated focus plane."""
        self._align_z_to_focus()

    # ---------------- Shape Synchronization ---------------- #

    @Slot(str, str, float, result='QVariant')
    def generateBarcodeEntity(self, code_type: str, content: str, size_mm: float) -> dict:
        """
        Generates industrial ISO/IEC compliant 2D QR Code, 1D Code 128, and DataMatrix ECC 200 vector geometry.
        - Primary engine: zxing-cpp (Standard C++ ISO engine for phones, cameras, & industrial scanners)
        - Fallbacks: qrcode (border=4) and reportlab (Code128 / DataMatrix)
        - Run-length horizontal merging for laser optimization and fast QML Canvas rendering
        - Outputs standard wMm, hMm, rects, and closed polygon vector paths
        """
        content = str(content).strip() if content else "12345"
        size_mm = max(5.0, float(size_mm or 20.0))
        code_type_lower = code_type.lower()

        rects = []
        paths = []
        out_w = size_mm
        out_h = size_mm

        grid = None
        is_linear_1d = False

        # 1. Primary engine: zxing-cpp
        try:
            import zxingcpp
            import numpy as np

            if "matrix" in code_type_lower:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.DataMatrix)
                bm = zxingcpp.write_barcode_to_image(bc)
                grid = (np.array(bm) == 0).astype(int)
                out_w = size_mm
                out_h = size_mm

            elif "128" in code_type_lower or "bar" in code_type_lower:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.Code128)
                bm = zxingcpp.write_barcode_to_image(bc)
                arr = np.array(bm)
                mid_row = arr[len(arr) // 2]
                grid = (mid_row == 0).astype(int)
                is_linear_1d = True
                out_w = size_mm
                out_h = round(size_mm * 0.35, 3)

            else:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.QRCode)
                bm = zxingcpp.write_barcode_to_image(bc)
                grid = (np.array(bm) == 0).astype(int)
                out_w = size_mm
                out_h = size_mm

        except Exception as zx_err:
            print(f"[CadBridge] zxingcpp generation notice: {zx_err}")
            grid = None

        # 2. Resilient fallbacks
        if grid is None:
            if "matrix" in code_type_lower:
                try:
                    from reportlab.graphics.barcode import createBarcodeDrawing
                    d = createBarcodeDrawing('ECC200DataMatrix', value=content)
                    bc = d.contents[0]
                    raw = bc.encoded
                    cw = len(raw[0])
                    # Add 1 module quiet zone border
                    grid = [[0] * (cw + 2)] + [[0] + list(r) + [0] for r in raw] + [[0] * (cw + 2)]
                    out_w = size_mm
                    out_h = size_mm
                except Exception as dm_err:
                    print(f"[CadBridge] DataMatrix reportlab fallback error: {dm_err}")

            elif "128" in code_type_lower or "bar" in code_type_lower:
                try:
                    out_h = round(size_mm * 0.35, 3)
                    CODE128_PATTERNS = [
                        '11011001100', '11001101100', '11001100110', '10010011000', '10010001100',
                        '10001001100', '10011001000', '10011000100', '10001100100', '11001001000',
                        '11001000100', '11000100100', '10110011100', '10011011100', '10011001110',
                        '10111001100', '10011101100', '10011100110', '11001110010', '11001011100',
                        '11001001110', '11011100100', '11001110100', '11101101110', '11101001100',
                        '11100101100', '11100100110', '11101100100', '11100110100', '11100110010',
                        '11011011000', '11011000110', '11000110110', '10100011000', '10001011000',
                        '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',
                        '11000101000', '11000100010', '10110111000', '10110001110', '10001101110',
                        '10111011000', '10111000110', '10001110110', '11101110110', '11010001110',
                        '11000101110', '11011101000', '11011100010', '11011101110', '11101011000',
                        '11101000110', '11100010110', '11101101000', '11101100010', '11100011010',
                        '11101111010', '11001000010', '11110001010', '10100110000', '10100001100',
                        '10010110000', '10010000110', '10000101100', '10000100110', '10110010000',
                        '10110000100', '10011010000', '10011000010', '10000110100', '10000110010',
                        '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',
                        '10100111100', '10010111100', '10010011110', '10111100100', '10011110100',
                        '10011110010', '11110100100', '11110010100', '11110010010', '11011011110',
                        '11011110110', '11110110110', '10101111000', '10100011110', '10001011110',
                        '10111101000', '10111100010', '11110101000', '11110100010', '10111011110',
                        '10111101110', '11101011110', '11110101110', '11010000100', '11010010000',
                        '11010011100', '1100011101011'
                    ]
                    values = [104]
                    for ch in content:
                        v = ord(ch) - 32
                        values.append(v if 0 <= v <= 95 else 0)
                    checksum = values[0]
                    for i in range(1, len(values)):
                        checksum = (checksum + i * values[i]) % 103
                    values.append(checksum)
                    values.append(106)
                    raw_bits = ''.join(CODE128_PATTERNS[v] for v in values)
                    # Add mandatory 10-module quiet zones on both sides
                    bit_str = ('0' * 10) + raw_bits + ('0' * 10)
                    grid = [int(b) for b in bit_str]
                    is_linear_1d = True
                except Exception as bar_err:
                    print(f"[CadBridge] Code 128 fallback error: {bar_err}")

            else:
                try:
                    import qrcode
                    qr = qrcode.QRCode(
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=1,
                        border=4
                    )
                    qr.add_data(content)
                    qr.make(fit=True)
                    grid = qr.get_matrix()
                    out_w = size_mm
                    out_h = size_mm
                except Exception as qr_err:
                    print(f"[CadBridge] QR Code fallback error: {qr_err}")

        # 3. Convert binary grid into run-length merged rectangles and closed paths
        if grid is not None:
            if is_linear_1d:
                n_bits = len(grid)
                mod_w = out_w / float(n_bits)
                bi = 0
                while bi < n_bits:
                    if grid[bi]:
                        sb = bi
                        while bi < n_bits and grid[bi]:
                            bi += 1
                        bw = (bi - sb) * mod_w
                        bx0 = round(-out_w / 2.0 + sb * mod_w, 3)
                        bx1 = round(bx0 + bw, 3)
                        by0 = round(-out_h / 2.0, 3)
                        by1 = round(out_h / 2.0, 3)
                        rects.append({
                            "x": bx0,
                            "y": by1,
                            "w": round(bx1 - bx0, 3),
                            "h": out_h
                        })
                        paths.append([
                            [bx0, by0], [bx1, by0],
                            [bx1, by1], [bx0, by1], [bx0, by0]
                        ])
                    else:
                        bi += 1
            else:
                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 1
                mod_w = out_w / float(cols)
                mod_h = out_h / float(rows)

                # 2D maximal greedy rectangle merging (merges contiguous horizontal and vertical module blocks)
                visited = [[False] * cols for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] and not visited[r][c]:
                            # Find contiguous span along row r
                            w_span = 0
                            while c + w_span < cols and grid[r][c + w_span] and not visited[r][c + w_span]:
                                w_span += 1
                            # Expand vertically while all columns in span are unvisited and solid
                            h_span = 1
                            while r + h_span < rows:
                                if all(grid[r + h_span][c + i] and not visited[r + h_span][c + i] for i in range(w_span)):
                                    h_span += 1
                                else:
                                    break
                            # Mark cells as visited
                            for dr in range(h_span):
                                for dc in range(w_span):
                                    visited[r + dr][c + dc] = True

                            lx0 = round(-out_w / 2.0 + c * mod_w, 3)
                            lx1 = round(-out_w / 2.0 + (c + w_span) * mod_w, 3)
                            ly0 = round(out_h / 2.0 - (r + h_span) * mod_h, 3)
                            ly1 = round(out_h / 2.0 - r * mod_h, 3)

                            rects.append({
                                "x": lx0,
                                "y": ly1,
                                "w": round(lx1 - lx0, 3),
                                "h": round(ly1 - ly0, 3)
                            })
                            paths.append([
                                [lx0, ly0], [lx1, ly0],
                                [lx1, ly1], [lx0, ly1], [lx0, ly0]
                            ])

        return {
            "success": True,
            "type": code_type,
            "text": content,
            "wMm": out_w,
            "hMm": out_h,
            "rects": rects,
            "paths": paths
        }

    @Slot("QVariantMap", str, result="QVariantMap")
    @Slot("QVariantMap", str, str, result="QVariantMap")
    def exportBarcodeFile(self, shape_dict: dict, format_ext: str, target_path: str = "") -> dict:
        """
        Exports a 2D QR Code, 1D Code 128, or DataMatrix entity to DXF, SVG, or PNG format.
        If target_path is omitted or empty, prompts user with a native QFileDialog.
        """
        try:
            from PySide6.QtWidgets import QFileDialog
            import re

            format_ext = str(format_ext).strip().lower()
            if format_ext not in ["dxf", "svg", "png"]:
                format_ext = "dxf"

            code_type = str(shape_dict.get("barcodeType") or shape_dict.get("type", "qrcode"))
            text_content = str(shape_dict.get("text", "12345"))
            size_mm = float(shape_dict.get("wMm", 20.0))

            # Ensure we have up-to-date geometry
            rects = shape_dict.get("rects")
            paths = shape_dict.get("paths")
            w_mm = float(shape_dict.get("wMm", size_mm))
            h_mm = float(shape_dict.get("hMm", size_mm))

            if not rects or not paths:
                gen_data = self.generateBarcodeEntity(code_type, text_content, size_mm)
                rects = gen_data.get("rects", [])
                paths = gen_data.get("paths", [])
                w_mm = gen_data.get("wMm", w_mm)
                h_mm = gen_data.get("hMm", h_mm)

            # Determine default save folder
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "QR", "Barcode DXF")
            os.makedirs(save_dir, exist_ok=True)

            shp_name = str(shape_dict.get("name") or code_type or "Barcode")
            clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', shp_name)
            default_target = os.path.join(save_dir, f"{clean_name}.{format_ext}")

            if not target_path:
                filters = {
                    "dxf": "DXF Vector CAD File (*.dxf)",
                    "svg": "SVG Scalable Vector Graphics (*.svg)",
                    "png": "PNG High-Resolution Image (*.png)"
                }
                filter_str = f"{filters.get(format_ext, 'All Files (*)')};;All Files (*)"
                chosen, _ = QFileDialog.getSaveFileName(
                    None,
                    f"Export {format_ext.upper()} Code - {shp_name}",
                    default_target,
                    filter_str
                )
                if not chosen:
                    return {"success": False, "cancelled": True}
                target_path = chosen

            if not target_path.lower().endswith(f".{format_ext}"):
                target_path += f".{format_ext}"

            # 1. DXF Vector CAD Export
            if format_ext == "dxf":
                import ezdxf
                doc = ezdxf.new("R2010")
                msp = doc.modelspace()
                for rc in rects:
                    x0 = float(rc["x"])
                    y0 = float(rc["y"]) - float(rc["h"])
                    x1 = float(rc["x"]) + float(rc["w"])
                    y1 = float(rc["y"])
                    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True)

                if bool(shape_dict.get("hatched")) and shape_dict.get("hatch_lines"):
                    h_layer = doc.layers.add("HATCH")
                    h_layer.color = 1
                    for hl in shape_dict["hatch_lines"]:
                        pts = hl.get("points", [])
                        for i in range(len(pts) - 1):
                            msp.add_line(pts[i], pts[i+1], dxfattribs={"layer": "HATCH"})

                doc.saveas(target_path)

            # 2. SVG Scalable Vector Graphics Export
            elif format_ext == "svg":
                min_x = round(-w_mm / 2.0, 3)
                min_y = round(-h_mm / 2.0, 3)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {w_mm} {h_mm}" width="{w_mm}mm" height="{h_mm}mm">\n')
                    f.write('  <g fill="black">\n')
                    for rc in rects:
                        rx = float(rc["x"])
                        ry = -float(rc["y"])
                        rw = float(rc["w"])
                        rh = float(rc["h"])
                        f.write(f'    <rect x="{rx:.3f}" y="{ry:.3f}" width="{rw:.3f}" height="{rh:.3f}"/>\n')
                    f.write('  </g>\n</svg>\n')

            # 3. PNG High-Resolution Scannable Raster Image
            elif format_ext == "png":
                from PySide6.QtGui import QImage, QPainter, QColor
                from PySide6.QtCore import QRectF

                px_w = 1200
                px_h = max(300, int(round(1200 * (h_mm / max(1.0, w_mm)))))
                scale_px = px_w / max(1.0, w_mm)

                img = QImage(px_w, px_h, QImage.Format_ARGB32)
                img.fill(QColor("white"))
                p = QPainter(img)
                p.translate(px_w / 2.0, px_h / 2.0)
                for rc in rects:
                    rx = float(rc["x"]) * scale_px
                    ry = -float(rc["y"]) * scale_px
                    rw = float(rc["w"]) * scale_px
                    rh = float(rc["h"]) * scale_px
                    p.fillRect(QRectF(rx, ry, rw + 0.5, rh + 0.5), QColor("#0A0F1D"))
                p.end()
                img.save(target_path)

            self._set_status(f"Exported {format_ext.upper()} to: {os.path.basename(target_path)}")
            return {"success": True, "filePath": target_path, "format": format_ext}

        except Exception as exp_err:
            print(f"[CadBridge] exportBarcodeFile error: {exp_err}")
            self._set_status(f"Export failed: {str(exp_err)}")
            return {"success": False, "error": str(exp_err)}

    @Slot(list)
    def updateShapes(self, shapes: list):
        """Synchronizes current QML vector shapes model to Python backend."""
        self._shapes = shapes or []
        self._shape_count = len(self._shapes)
        self.shapeCountChanged.emit(self._shape_count)

    # ---------------- Hatch Profiles Management (EZCad & main.py) ---------------- #

    def _default_hatch_profile(self):
        """Default hatch profile parameters matching main.py lines 2364-2384 and EZCad defaults."""
        return {
            "enable": False,
            "all_calc": False,
            "follow_edge": False,
            "cross_hatch": False,
            "type": "Bidirectional",
            "angle": 0.0,
            "count": 1,
            "line_space": 0.05,
            "avg_dist": False,
            "edge_off": 0.0,
            "start_off": 0.0,
            "end_off": 0.0,
            "line_red": 0.0,
            "num_loops": 0,
            "loop_dist": 0.05,
            "auto_rot": False,
            "rot_angle": 10.0,
            "pen_no": 0
        }

    def _load_hatch_profiles(self):
        """Loads Hatch 1, 2, 3 profiles from config/config.ini matching main.py lines 2386-2397."""
        if not os.path.exists(self.CONFIG_FILE):
            return
        parser = ConfigParser()
        try:
            parser.read(self.CONFIG_FILE)
            if parser.has_section("hatch_general"):
                self._mark_contour = parser.getboolean("hatch_general", "mark_contour", fallback=True)
                self._mark_contour_first = parser.getboolean("hatch_general", "mark_contour_first", fallback=True)
            elif parser.has_option("hatch_profile_1", "mark_contour"):
                self._mark_contour = parser.getboolean("hatch_profile_1", "mark_contour", fallback=True)

            for idx in [1, 2, 3]:
                sec = f"hatch_profile_{idx}"
                if parser.has_section(sec):
                    p = self._hatch_profiles[idx]
                    p["enable"] = parser.getboolean(sec, "enable", fallback=p["enable"])
                    p["all_calc"] = parser.getboolean(sec, "all_calc", fallback=p["all_calc"])
                    p["follow_edge"] = parser.getboolean(sec, "follow_edge", fallback=p["follow_edge"])
                    p["cross_hatch"] = parser.getboolean(sec, "cross_hatch", fallback=p["cross_hatch"])
                    p["type"] = parser.get(sec, "type", fallback=p["type"])
                    try: p["angle"] = float(parser.get(sec, "angle", fallback=str(p["angle"])))
                    except: pass
                    try: p["count"] = int(float(parser.get(sec, "count", fallback=str(p["count"]))))
                    except: pass
                    try: p["line_space"] = float(parser.get(sec, "line_space", fallback=str(p["line_space"])))
                    except: pass
                    p["avg_dist"] = parser.getboolean(sec, "avg_dist", fallback=p["avg_dist"])
                    try: p["edge_off"] = float(parser.get(sec, "edge_off", fallback=str(p["edge_off"])))
                    except: pass
                    try: p["start_off"] = float(parser.get(sec, "start_off", fallback=str(p["start_off"])))
                    except: pass
                    try: p["end_off"] = float(parser.get(sec, "end_off", fallback=str(p["end_off"])))
                    except: pass
                    try: p["line_red"] = float(parser.get(sec, "line_red", fallback=str(p["line_red"])))
                    except: pass
                    try: p["num_loops"] = int(float(parser.get(sec, "num_loops", fallback=str(p["num_loops"]))))
                    except: pass
                    try: p["loop_dist"] = float(parser.get(sec, "loop_dist", fallback=str(p["loop_dist"])))
                    except: pass
                    p["auto_rot"] = parser.getboolean(sec, "auto_rot", fallback=p["auto_rot"])
                    try: p["rot_angle"] = float(parser.get(sec, "rot_angle", fallback=str(p["rot_angle"])))
                    except: pass
                    try: p["pen_no"] = int(float(parser.get(sec, "pen_no", fallback=str(p.get("pen_no", 0)))))
                    except: pass
            print(f"[CadBridge] Loaded 3 Hatch Profiles from {self.CONFIG_FILE} (mark_contour={self._mark_contour})")
        except Exception as e:
            print(f"[CadBridge] Error loading hatch profiles from config: {e}")

    def _save_hatch_profiles_to_file(self):
        """Saves Hatch 1, 2, 3 profiles to config/config.ini matching main.py lines 2420-2424."""
        try:
            parser = ConfigParser()
            if os.path.exists(self.CONFIG_FILE):
                parser.read(self.CONFIG_FILE)
            if not parser.has_section("hatch_general"):
                parser.add_section("hatch_general")
            parser.set("hatch_general", "mark_contour", str(self._mark_contour))
            parser.set("hatch_general", "mark_contour_first", str(self._mark_contour_first))

            for idx in [1, 2, 3]:
                sec = f"hatch_profile_{idx}"
                if not parser.has_section(sec):
                    parser.add_section(sec)
                p = self._hatch_profiles[idx]
                for k, v in p.items():
                    parser.set(sec, k, str(v))
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
            print(f"[CadBridge] Saved 3 Hatch Profiles to {self.CONFIG_FILE}")
            self.hatchProfilesChanged.emit()
        except Exception as e:
            print(f"[CadBridge] Error writing hatch profiles to config: {e}")

    @Slot(result="QVariantMap")
    def getAllHatchProfiles(self):
        """Returns all 3 profiles + mark contour flags for QML dialog."""
        return {
            "1": dict(self._hatch_profiles[1]),
            "2": dict(self._hatch_profiles[2]),
            "3": dict(self._hatch_profiles[3]),
            "mark_contour": self._mark_contour,
            "mark_contour_first": self._mark_contour_first
        }

    @Slot(int, result="QVariantMap")
    def getHatchProfile(self, idx: int):
        """Returns a single hatch profile by index (1, 2, 3)."""
        return dict(self._hatch_profiles.get(idx, self._default_hatch_profile()))

    @Slot(int, "QVariantMap")
    def saveHatchProfile(self, idx: int, profile: dict):
        """Updates and persists a single hatch profile."""
        if idx not in self._hatch_profiles:
            return
        self._hatch_profiles[idx].update(profile)
        self._save_hatch_profiles_to_file()

    @Slot("QVariantMap", bool, bool)
    def saveAllHatchProfiles(self, profiles: dict, mark_contour: bool, mark_contour_first: bool = True):
        """Updates all 3 profiles and contour ordering in memory and writes to config.ini."""
        self._mark_contour = mark_contour
        self._mark_contour_first = mark_contour_first
        for idx in [1, 2, 3]:
            str_k = str(idx)
            if str_k in profiles:
                self._hatch_profiles[idx].update(profiles[str_k])
            elif idx in profiles:
                self._hatch_profiles[idx].update(profiles[idx])
        self._save_hatch_profiles_to_file()

    @Slot("QVariantMap", result=list)
    def computeHatchPreviewLines(self, shp: dict):
        """
        Computes hatch vector lines in shape / bed millimeters
        for direct high-fidelity visual preview on CadCanvas.
        """
        try:
            polys = self._shape_to_polygons(shp)
            if not polys:
                return []

            active_cfgs = []
            shape_pen = int(shp.get("penId", 0) or 0)
            shape_hatch = shp.get("hatch_profiles")
            has_custom_hatch = isinstance(shape_hatch, dict) and len(shape_hatch) > 0
            source_profiles = shape_hatch if has_custom_hatch else self._hatch_profiles

            for k in [1, 2, 3]:
                p = source_profiles.get(k) or source_profiles.get(str(k))
                if p and p.get("enable", False):
                    if has_custom_hatch and p.get("pen_no") is not None:
                        chosen_pen = int(p.get("pen_no", 0) or 0)
                    else:
                        chosen_pen = shape_pen
                    cfg = {
                        'enable': True,
                        'follow_edge': p.get("follow_edge", False),
                        'all_calc': p.get("all_calc", False),
                        'cross_hatch': p.get("cross_hatch", False),
                        'type': p.get("type", "Bidirectional"),
                        'angle': float(p.get("angle", 0.0) or 0.0),
                        'pen_no': chosen_pen,
                        'count': int(p.get("count", 1) or 1),
                        'line_space': float(p.get("line_space", 0.05) or 0.05),
                        'avg_distribute': p.get("avg_dist", False),
                        'edge_offset': float(p.get("edge_off", 0.0) or 0.0),
                        'start_offset': float(p.get("start_off", 0.0) or 0.0),
                        'end_offset': float(p.get("end_off", 0.0) or 0.0),
                        'line_reduction': float(p.get("line_red", 0.0) or 0.0),
                        'num_loops': int(p.get("num_loops", 0) or 0),
                        'loop_distance': float(p.get("loop_dist", 0.05) or 0.05),
                        'auto_rotate': p.get("auto_rot", False),
                        'rotate_angle': float(p.get("rot_angle", 10.0) or 10.0),
                        'hatch_idx': k
                    }
                    active_cfgs.append(cfg)

            if not active_cfgs and bool(shp.get("hatched", False)):
                active_cfgs.append({
                    'enable': True,
                    'follow_edge': False,
                    'all_calc': False,
                    'cross_hatch': False,
                    'type': "Bidirectional",
                    'angle': 45.0,
                    'pen_no': shape_pen,
                    'count': 1,
                    'line_space': 0.05,
                    'avg_distribute': False,
                    'edge_offset': 0.0,
                    'start_offset': 0.0,
                    'end_offset': 0.0,
                    'line_reduction': 0.0,
                    'num_loops': 0,
                    'loop_distance': 0.05,
                    'auto_rotate': False,
                    'rotate_angle': 10.0,
                    'hatch_idx': 1
                })

            if not active_cfgs:
                return []

            all_lines = []
            for cfg in active_cfgs:
                segs = compute_hatch_geometry(polys, cfg, galvo_units_per_mm=1.0)
                pen_id = int(cfg.get("pen_no", shape_pen))
                for s in segs:
                    if len(s) >= 2:
                        all_lines.append({
                            "pen_id": pen_id,
                            "points": [[float(pt[0]), float(pt[1])] for pt in s]
                        })
            return all_lines
        except Exception as e:
            print(f"[CadBridge] Preview hatch error: {e}")
            return []

    # ---------------- Vector Geometry Conversion ---------------- #

    def _shape_to_polygons(self, shp: dict) -> list:
        """
        Converts a single QML shape dictionary into a list of 2D millimeter polygons
        relative to the center origin (0, 0).
        Returns: list of [(x, y), ...] polygons.
        """
        stype = shp.get("type", "rect")
        cx = float(shp.get("xMm", 0.0))
        cy = float(shp.get("yMm", 0.0))
        w = float(shp.get("wMm", 10.0))
        h = float(shp.get("hMm", 10.0))
        rot_deg = float(shp.get("rotation", 0.0))
        rot_rad = math.radians(rot_deg)
        cos_a = math.cos(rot_rad)
        sin_a = math.sin(rot_rad)

        def rotate_and_shift(lx, ly):
            rx = cx + lx * cos_a - ly * sin_a
            ry = cy + lx * sin_a + ly * cos_a
            return (rx, ry)

        polys = []

        if stype == "group" and shp.get("children"):
            for ch in shp.get("children", []):
                ch_flat = dict(ch)
                ch_rel_x = float(ch.get("relX", 0.0))
                ch_rel_y = float(ch.get("relY", 0.0))
                child_center_x, child_center_y = rotate_and_shift(ch_rel_x, ch_rel_y)
                ch_flat["xMm"] = child_center_x
                ch_flat["yMm"] = child_center_y
                ch_flat["rotation"] = (float(ch.get("rotation", 0.0)) + rot_deg) % 360
                child_polys = self._shape_to_polygons(ch_flat)
                polys.extend(child_polys)
            return polys

        if stype == "rect":
            corners = [
                (-w / 2.0, -h / 2.0),
                (w / 2.0, -h / 2.0),
                (w / 2.0, h / 2.0),
                (-w / 2.0, h / 2.0),
                (-w / 2.0, -h / 2.0)
            ]
            polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype == "circle":
            r = w / 2.0
            n_segments = 64
            pts = []
            for i in range(n_segments + 1):
                theta = (2.0 * math.pi * i) / n_segments
                lx = r * math.cos(theta)
                ly = r * math.sin(theta)
                pts.append(rotate_and_shift(lx, ly))
            polys.append(pts)

        elif stype == "text":
            raw_text = str(shp.get("text", "TEXT"))
            if not raw_text:
                raw_text = "TEXT"

            # 1. Resolve Variable Text if enabled
            if bool(shp.get("enableVariableText", False)):
                var_entities = shp.get("variableEntities", [])
                if var_entities:
                    composed = []
                    for ent in var_entities:
                        etype = ent.get("type", "fixed")
                        if etype == "fixed":
                            composed.append(str(ent.get("text", "")))
                        elif etype == "serial":
                            cur_val = int(ent.get("current", 1))
                            step_val = int(ent.get("step", 1))
                            digits = int(ent.get("digits", 5))
                            composed.append(str(cur_val).zfill(digits))
                            # Auto increment serial number for next cycle
                            ent["current"] = cur_val + step_val
                        elif etype == "datetime":
                            fmt = str(ent.get("format", "%Y-%m-%d %H:%M:%S"))
                            composed.append(datetime.datetime.now().strftime(fmt))
                    raw_text = "".join(composed) if composed else raw_text

            font_family = str(shp.get("fontFamily", "Segoe UI"))
            font_type = str(shp.get("fontType", "TrueType Font"))
            font_h_mm = max(0.5, float(shp.get("hMm", 5.0)))
            bold = bool(shp.get("bold", False))
            italic = bool(shp.get("italic", False))
            char_space = float(shp.get("charSpace", 0.0))
            line_space = float(shp.get("lineSpace", 0.0))
            char_width_pct = max(10.0, float(shp.get("charWidthPct", 100.0))) / 100.0
            slant_deg = float(shp.get("angle", 0.0))
            slant_rad = math.radians(slant_deg)
            circle_text = bool(shp.get("circleText", False))
            circle_diam = max(1.0, float(shp.get("circleDiameter", 20.0)))
            circle_base_angle = float(shp.get("circleBaseAngle", 90.0))
            text_align = str(shp.get("textAlign", "center")).lower()

            # 2. CircleText Mode: Distribute characters along circle circumference
            if circle_text:
                radius_mm = circle_diam / 2.0
                total_len = len(raw_text)
                if total_len > 0:
                    char_w = font_h_mm * 0.7 * char_width_pct
                    angular_step_rad = char_w / radius_mm
                    start_angle_rad = math.radians(circle_base_angle) + (total_len - 1) * angular_step_rad / 2.0
                    qf_c = QFont(font_family if not font_family.startswith("Simplex") else "Arial", int(round(font_h_mm * 10)))
                    qf_c.setBold(bold)
                    qf_c.setItalic(italic)

                    for i, ch in enumerate(raw_text):
                        theta = start_angle_rad - i * angular_step_rad
                        char_cx = radius_mm * math.cos(theta)
                        char_cy = radius_mm * math.sin(theta)
                        rot_tangent = theta - math.pi / 2.0

                        path = QPainterPath()
                        path.addText(0, 0, qf_c, ch)
                        br = path.boundingRect()
                        if br.width() <= 0 or br.height() <= 0:
                            continue

                        scale_c = font_h_mm / br.height()
                        cos_t = math.cos(rot_tangent)
                        sin_t = math.sin(rot_tangent)

                        for sp in path.toSubpathPolygons():
                            pts = []
                            for k in range(sp.size()):
                                pt = sp.at(k)
                                lx0 = (pt.x() - br.center().x()) * scale_c * char_width_pct
                                ly0 = -(pt.y() - br.center().y()) * scale_c
                                if slant_deg != 0:
                                    lx0 += ly0 * math.tan(slant_rad)
                                rx0 = char_cx + lx0 * cos_t - ly0 * sin_t
                                ry0 = char_cy + lx0 * sin_t + ly0 * cos_t
                                pts.append(rotate_and_shift(rx0, ry0))
                            if len(pts) >= 2:
                                polys.append(pts)

            # 3. Single-Stroke Hershey Simplex Font Mode
            elif font_family.startswith("Simplex") or font_type == "Single-Stroke (Hershey)":
                try:
                    sfont = SimplexFont('')
                    spath = JhfPath()
                    sfont.render(spath, raw_text, True, font_h_mm, 1.0, 1.0, 'start')

                    strokes = []
                    curr_stroke = []
                    for item in spath.path:
                        if item is None:
                            if curr_stroke:
                                strokes.append(curr_stroke)
                                curr_stroke = []
                        elif isinstance(item, tuple):
                            if len(item) == 2:
                                if curr_stroke: strokes.append(curr_stroke)
                                curr_stroke = [item]
                            elif len(item) == 4:
                                if not curr_stroke: curr_stroke.append((item[0], item[1]))
                                elif curr_stroke[-1] != (item[0], item[1]):
                                    strokes.append(curr_stroke)
                                    curr_stroke = [(item[0], item[1])]
                                curr_stroke.append((item[2], item[3]))
                    if curr_stroke:
                        strokes.append(curr_stroke)

                    if strokes:
                        all_pts = [pt for st in strokes for pt in st]
                        min_lx = min(p[0] for p in all_pts)
                        max_lx = max(p[0] for p in all_pts)
                        min_ly = min(p[1] for p in all_pts)
                        max_ly = max(p[1] for p in all_pts)
                        local_cx = (min_lx + max_lx) / 2.0
                        local_cy = (min_ly + max_ly) / 2.0

                        for st in strokes:
                            pts = []
                            for pt in st:
                                lx = (pt[0] - local_cx) * char_width_pct
                                ly = -(pt[1] - local_cy)
                                if slant_deg != 0:
                                    lx += ly * math.tan(slant_rad)
                                pts.append(rotate_and_shift(lx, ly))
                            if len(pts) >= 2:
                                polys.append(pts)
                except Exception as e:
                    print(f"[CadBridge] Simplex stroke text error: {e}")

            # 4. Standard TrueType / OpenType Vector Outline Subpaths
            else:
                lines = raw_text.split("\n")
                line_count = len(lines)
                qf = QFont(font_family, int(round(font_h_mm * 10)))
                qf.setBold(bold)
                qf.setItalic(italic)
                if char_space != 0:
                    qf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, char_space * 10)

                total_block_h = line_count * font_h_mm + max(0, line_count - 1) * line_space

                for line_idx, line_str in enumerate(lines):
                    if not line_str:
                        continue
                    path = QPainterPath()
                    path.addText(0, 0, qf, line_str)
                    brect = path.boundingRect()
                    if brect.width() <= 0 or brect.height() <= 0:
                        continue

                    scale_y = font_h_mm / brect.height()
                    scale_x = scale_y * char_width_pct

                    line_y_offset = (total_block_h / 2.0) - (line_idx * (font_h_mm + line_space)) - (font_h_mm / 2.0)

                    line_x_offset = 0.0
                    line_w_mm = brect.width() * scale_x
                    if "left" in text_align:
                        line_x_offset = -w / 2.0 + line_w_mm / 2.0
                    elif "right" in text_align:
                        line_x_offset = w / 2.0 - line_w_mm / 2.0

                    for subpoly in path.toSubpathPolygons():
                        pts = []
                        for pt in list(subpoly):
                            lx = (pt.x() - brect.center().x()) * scale_x + line_x_offset
                            ly = -(pt.y() - brect.center().y()) * scale_y + line_y_offset
                            if slant_deg != 0:
                                lx += ly * math.tan(slant_rad)
                            pts.append(rotate_and_shift(lx, ly))
                        if len(pts) >= 2:
                            polys.append(pts)

        elif stype in ["qrcode", "barcode128", "datamatrix"]:
            raw_paths = shp.get("paths", [])
            if not raw_paths:
                # Dynamically generate merged horizontal run-length polygons
                b_res = self.generateBarcodeEntity(stype, shp.get("text", "12345"), w)
                raw_paths = b_res.get("paths", [])
            if raw_paths:
                for subpath in raw_paths:
                    pts = [rotate_and_shift(p[0], p[1]) for p in subpath]
                    if len(pts) >= 2:
                        polys.append(pts)
            if not polys:
                corners = [(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0), (-w / 2.0, -h / 2.0)]
                polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype in ["polygon", "dxf", "svg", "line", "curve"]:
            raw_paths = shp.get("paths", [])
            if raw_paths:
                for subpath in raw_paths:
                    pts = [rotate_and_shift(p[0], p[1]) for p in subpath]
                    if len(pts) >= 2:
                        polys.append(pts)
            else:
                raw_pts = shp.get("points", [])
                if len(raw_pts) >= 2:
                    polys.append([rotate_and_shift(p[0], p[1]) for p in raw_pts])

        return polys

    def _extract_active_shapes(self, shapes=None, mark_selected_only=False, selected_index=-1) -> list:
        source = shapes if shapes is not None else self._shapes
        if not source:
            return []
        candidates = [source[selected_index]] if (mark_selected_only and 0 <= selected_index < len(source)) else [s for s in source if s.get("visible", True)]
        active = []
        for s in candidates:
            if s.get("type") == "group" and "children" in s and s["children"]:
                gx = float(s.get("xMm", 0.0))
                gy = float(s.get("yMm", 0.0))
                for ch in s["children"]:
                    flat_ch = dict(ch)
                    flat_ch["xMm"] = gx + float(ch.get("relX", 0.0))
                    flat_ch["yMm"] = gy + float(ch.get("relY", 0.0))
                    flat_ch["penId"] = ch.get("penId", s.get("penId", 0))
                    active.append(flat_ch)
            else:
                active.append(s)
        return active

    # ---------------- Red Light Framing (F1) ---------------- #

    @Slot()
    @Slot(list)
    @Slot(list, bool, int)
    def toggleFraming(self, shapes=None, mark_selected_only=False, selected_index=-1):
        """
        Toggles the Guide Red Pointer Framing (F1).
        Computes bounding box over active QML shapes and continuously cycles
        the red laser pointer at high speed.
        """
        if self._is_framing:
            self._stop_framing()
            return

        active_shapes = self._extract_active_shapes(shapes, mark_selected_only, selected_index)
        if not active_shapes:
            self._set_status("No shapes to frame. Add shapes first.")
            return

        # Compute bounding envelope in millimeters
        all_polys = []
        for s in active_shapes:
            all_polys.extend(self._shape_to_polygons(s))

        if not all_polys:
            self._set_status("No vector geometry found to frame.")
            return

        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        for poly in all_polys:
            for pt in poly:
                min_x = min(min_x, pt[0])
                max_x = max(max_x, pt[0])
                min_y = min(min_y, pt[1])
                max_y = max(max_y, pt[1])

        if min_x == float('inf'):
            return

        if self.galvo_bridge and (self.galvo_bridge.isDemo or not self.galvo_bridge.isConnected):
            print(f"[CadBridge] Red Framing operating in simulation/preview mode.")

        # 1. Sync calibration scale & optical field from main.py math
        calib_scale, galvo_units_per_mm, lens_size = self._sync_calibration_and_field_size()

        # Add 0.5mm margin for clear alignment
        min_x -= 0.5; max_x += 0.5
        min_y -= 0.5; max_y += 0.5

        # Transform all 4 corners through optical affine mapping to handle rotation/scale/distortion correctly
        corners = [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y)
        ]
        g_pts = [self.galvo_config.apply_transform(x, y) for (x, y) in corners]
        g_min_x = min(p[0] for p in g_pts)
        g_max_x = max(p[0] for p in g_pts)
        g_min_y = min(p[1] for p in g_pts)
        g_max_y = max(p[1] for p in g_pts)

        # Align Z axis to workpiece focal height when framing starts
        if self._auto_focus_z:
            self._align_z_to_focus()

        ctrl = self.galvo_controller
        if ctrl and ctrl.connection and getattr(ctrl.connection, 'is_initialized', False):
            try:
                self.preview_thread = PreviewThread(ctrl, g_min_x, g_max_x, g_min_y, g_max_y)
                self.preview_thread.start()
            except Exception as e:
                print(f"[CadBridge] PreviewThread error: {e}")
                if hasattr(ctrl.connection, 'reddot_on'):
                    ctrl.connection.reddot_on()
        else:
            print(f"[CadBridge] Red Framing simulated: Box ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f}) mm -> Galvo [{g_min_x}, {g_min_y}] to [{g_max_x}, {g_max_y}]")

        self._is_framing = True
        self.framingChanged.emit(True)
        self._set_status(f"Red Light Framing ON [{min_x:.1f}, {min_y:.1f} to {max_x:.1f}, {max_y:.1f} mm]")

    def _stop_framing(self):
        """Safely terminates the preview thread and shuts off red beam."""
        if self.preview_thread:
            self.preview_thread.running = False
            self.preview_thread.wait(400)
            self.preview_thread = None

        ctrl = self.galvo_controller
        if ctrl and ctrl.connection:
            try:
                if hasattr(ctrl.connection, 'reddot_off'):
                    ctrl.connection.reddot_off()
                if hasattr(ctrl.connection, 'stop'):
                    ctrl.connection.stop()
            except Exception as e:
                print(f"[CadBridge] Stop reddot error: {e}")

        self._is_framing = False
        self.framingChanged.emit(False)
        self._set_status("Red Light Framing stopped.")

    # ---------------- Laser Marking Execution (F2) ---------------- #

    @Slot()
    @Slot(list)
    @Slot(list, bool, int)
    @Slot(list, bool, int, int)
    def executeMark(self, shapes=None, mark_selected_only=False, selected_index=-1, loop_count=1):
        """
        Executes high-precision vector laser marking (F2).
        Implements exact math and hardware control from main.py:
        - Scale & field_size derived from .cor calibration (lines 2470-2485)
        - Speeds converted from mm/s to galvo units/s (lines 2487-2496)
        - Hardware power & frequency applied with live thread injection (lines 1980-2015, 2846-2865)
        - Path deduplication (lines 2629-2637)
        - Exact hatch geometry in galvo space (lines 2644-2651)
        """
        if self.galvo_bridge and (self.galvo_bridge.isDemo or not self.galvo_bridge.isConnected):
            print(f"[CadBridge] Laser Marking operating in simulation/preview mode.")

        if self._is_marking:
            self.abortMark()
            return

        if self._is_framing:
            self._stop_framing()

        active_shapes = self._extract_active_shapes(shapes, mark_selected_only, selected_index)
        if not active_shapes:
            self._set_status("No shapes to mark. Create or import vector geometry first.")
            return

        # 1. Sync calibration scale & optical field from main.py math
        calib_scale, galvo_units_per_mm, lens_size = self._sync_calibration_and_field_size()

        # 2. Speeds math from main.py lines 2487-2496
        raw_jump = float(getattr(self.galvo_bridge, 'jumpSpeed', 2000.0)) if self.galvo_bridge else 2000.0
        if raw_jump > 50000: raw_jump = 2000.0
        jump_speed = int(raw_jump * galvo_units_per_mm)
        default_mark_speed_mm = float(getattr(self.galvo_bridge, 'speed', 1000.0)) if self.galvo_bridge else 1000.0

        # 3. Apply Laser Power and Frequency from main.py math (lines 1980-2015, 2846-2865)
        mark_power = float(self.galvo_bridge.power) if self.galvo_bridge else 50.0
        mark_freq = float(self.galvo_bridge.frequency) if self.galvo_bridge else 35.0
        if active_shapes:
            s0 = active_shapes[0]
            if "power" in s0:
                mark_power = float(s0["power"])
            if "frequency" in s0:
                mark_freq = float(s0["frequency"])

        if self.galvo_bridge and hasattr(self.galvo_bridge, "apply_laser_power_and_freq"):
            self.galvo_bridge.apply_laser_power_and_freq(mark_power, mark_freq)
        elif self.galvo_controller:
            self.galvo_controller.live_power = mark_power
            self.galvo_controller.live_freq = mark_freq

        self.planner.clear()

        # 4. Generate Galvo Paths with exact main.py deduplication and hatching
        for shp in active_shapes:
            polys = self._shape_to_polygons(shp)
            if not polys:
                continue

            raw_mark = float(shp.get("speed", default_mark_speed_mm))
            if raw_mark > 50000: raw_mark = 1000.0
            mark_speed = int(raw_mark * galvo_units_per_mm)

            is_hatched = bool(shp.get("hatched", False))

            # Deduplicate identical overlapping paths (main.py lines 2629-2637)
            all_polys_galvo = []
            seen_polys = set()

            for poly in polys:
                if len(poly) < 2:
                    continue
                poly_galvo = []
                for pt in poly:
                    gx, gy = self.galvo_config.apply_transform(pt[0], pt[1])
                    poly_galvo.append((gx, gy))

                poly_key = tuple((int(round(pt[0])), int(round(pt[1]))) for pt in poly_galvo)
                poly_key_rev = tuple(reversed(poly_key))
                if poly_key not in seen_polys and poly_key_rev not in seen_polys:
                    seen_polys.add(poly_key)
                    all_polys_galvo.append(poly_galvo)

            shp_mark_contour = shp.get("mark_contour", self._mark_contour)
            shp_mark_contour_first = shp.get("mark_contour_first", self._mark_contour_first)

            def emit_contours():
                if shp_mark_contour:
                    for poly_galvo in all_polys_galvo:
                        self.planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
                        for pt in poly_galvo[1:]:
                            self.planner.add_mark(pt[0], pt[1], speed=mark_speed)
                        # Close contour loop only if not already closed
                        if poly_galvo[0] != poly_galvo[-1]:
                            self.planner.add_mark(poly_galvo[0][0], poly_galvo[0][1], speed=mark_speed)

            # 4a. Outer Contours First (if mark_contour_first)
            if shp_mark_contour_first:
                emit_contours()

            # 4b. Multi-Profile Infill Hatches (main.py lines 2568-2651, computed in galvo space)
            if is_hatched and all_polys_galvo:
                hatch_configs = []
                shape_pen = int(shp.get("penId", 0) or 0)
                shape_profiles = shp.get("hatch_profiles")
                has_custom_hatch = isinstance(shape_profiles, dict) and len(shape_profiles) > 0
                profiles_source = shape_profiles if has_custom_hatch else self._hatch_profiles

                for k in [1, 2, 3]:
                    p = profiles_source.get(k) or profiles_source.get(str(k))
                    if p and p.get("enable", False):
                        chosen_pen = int(p.get("pen_no", 0) or 0) if (has_custom_hatch and p.get("pen_no") is not None) else shape_pen
                        hatch_configs.append({
                            'enable': True,
                            'follow_edge': p.get("follow_edge", False),
                            'all_calc': p.get("all_calc", False),
                            'cross_hatch': p.get("cross_hatch", False),
                            'type': p.get("type", "Bidirectional"),
                            'angle': float(p.get("angle", 0.0) or 0.0),
                            'pen_no': chosen_pen,
                            'count': int(p.get("count", 1) or 1),
                            'line_space': float(p.get("line_space", 0.05) or 0.05),
                            'avg_distribute': p.get("avg_dist", False),
                            'edge_offset': float(p.get("edge_off", 0.0) or 0.0),
                            'start_offset': float(p.get("start_off", 0.0) or 0.0),
                            'end_offset': float(p.get("end_off", 0.0) or 0.0),
                            'line_reduction': float(p.get("line_red", 0.0) or 0.0),
                            'num_loops': int(p.get("num_loops", 0) or 0),
                            'loop_distance': float(p.get("loop_dist", 0.05) or 0.05),
                            'auto_rotate': p.get("auto_rot", False),
                            'rotate_angle': float(p.get("rot_angle", 10.0) or 10.0),
                            'hatch_idx': k
                        })

                if not hatch_configs:
                    # Fallback default profile if marked hatched but none enabled
                    hatch_configs.append({
                        'enable': True,
                        'follow_edge': False,
                        'all_calc': False,
                        'cross_hatch': False,
                        'type': "Bidirectional",
                        'angle': 45.0,
                        'pen_no': int(shp.get("penId", 0)),
                        'count': 1,
                        'line_space': 0.05,
                        'avg_distribute': False,
                        'edge_offset': 0.0,
                        'start_offset': 0.0,
                        'end_offset': 0.0,
                        'line_reduction': 0.0,
                        'num_loops': 0,
                        'loop_distance': 0.05,
                        'auto_rotate': False,
                        'rotate_angle': 10.0,
                        'hatch_idx': 1
                    })

                try:
                    self.planner.generate_hatch(
                        all_polys_galvo,
                        hatch_configs,
                        mark_speed=mark_speed,
                        jump_speed=jump_speed,
                        galvo_units_per_mm=galvo_units_per_mm
                    )
                except Exception as e:
                    print(f"[CadBridge] Multi-profile hatch generation error: {e}")

            # 4c. Outer Contours Last (if not mark_contour_first)
            if not shp_mark_contour_first:
                emit_contours()

        # Commit to queue
        if hasattr(self.planner, 'commit_to_send_queue'):
            self.planner.commit_to_send_queue()
        elif hasattr(self.planner, 'preview_queue'):
            self.planner.send_queue = list(self.planner.preview_queue)

        if not self.planner.send_queue:
            self._set_status("Motion queue is empty. Cannot mark.")
            return

        cmd_count = len(self.planner.send_queue)
        print(f"[CadBridge] Preparing laser mark: {cmd_count} vector commands (loops={loop_count})")

        # 5. Automatic Z-Axis Focal Alignment (Matching main.py lines 2795-2838)
        if self._auto_focus_z:
            self._align_z_to_focus()

        ctrl = self.galvo_controller
        if ctrl and ctrl.connection:
            try:
                self.exec_thread = ExecutionThread(ctrl, self.planner.send_queue, loop_count=loop_count)
                self.exec_thread.finished_signal.connect(self._on_execution_finished)
                self.exec_thread.progress_signal.connect(self._on_execution_progress)
                self.exec_thread.start()
            except Exception as e:
                print(f"[CadBridge] ExecutionThread launch error: {e}")
                self._is_marking = False
                self.markingChanged.emit(False)
                return
        else:
            # Simulation execution in background
            self._simulate_execution(cmd_count)

        self._is_marking = True
        self.markingChanged.emit(True)
        self._set_status(f"Laser Marking Active ({cmd_count} commands)...")

    def _simulate_execution(self, total_cmds: int):
        """Simulates laser mark progress smoothly if hardware is in demo mode."""
        from PySide6.QtCore import QTimer
        self._sim_idx = 0
        self._sim_timer = QTimer(self)

        def step():
            self._sim_idx += max(1, total_cmds // 40)
            if self._sim_idx >= total_cmds:
                self._sim_timer.stop()
                self._on_execution_finished(True)
            else:
                pct = (self._sim_idx / float(total_cmds)) * 100.0
                self.progressChanged.emit(self._sim_idx, total_cmds, pct)

        self._sim_timer.timeout.connect(step)
        self._sim_timer.start(50)

    def _on_execution_progress(self, idx, total, x, y, ctype):
        pct = (idx / float(total)) * 100.0 if total > 0 else 0.0
        self.progressChanged.emit(idx, total, pct)

    def _execute_post_mark_park(self):
        """Moves galvo mirrors to configured position after marking completes."""
        try:
            ctrl = self.galvo_controller
            if not ctrl or not hasattr(ctrl, 'connection') or not ctrl.connection:
                return

            pos = getattr(self, '_pos_after_mark', 'confgalvocent')
            f_half = self._field_size / 2.0
            target_x = 0.0
            target_y = 0.0

            if "nomov" in pos:
                return
            elif "galvocent" in pos:
                target_x, target_y = 0.0, 0.0
            elif "topleft" in pos:
                target_x, target_y = -f_half, f_half
            elif "topright" in pos:
                target_x, target_y = f_half, f_half
            elif "botright" in pos:
                target_x, target_y = f_half, -f_half
            elif "botleft" in pos:
                target_x, target_y = -f_half, -f_half
            elif "specpos" in pos:
                target_x = getattr(self, '_sp_x', 0.0)
                target_y = getattr(self, '_sp_y', 0.0)

            gx, gy = self.galvo_config.apply_transform(target_x, target_y)
            if hasattr(ctrl, 'execute_queue'):
                ctrl.execute_queue([{'type': 'jump', 'x': int(gx), 'y': int(gy), 'speed': 20000}], loop_count=1)
                print(f"[CadBridge] Post-mark parked at '{pos}' -> ({target_x}, {target_y}) mm")
        except Exception as e:
            print(f"[CadBridge] Post-mark park error: {e}")

    def _on_execution_finished(self, success: bool):
        self._is_marking = False
        self.markingChanged.emit(False)
        self.progressChanged.emit(100, 100, 100.0)
        status = "Laser marking completed successfully!" if success else "Laser marking ended with warnings/aborted."
        self._set_status(status)
        if success:
            self._execute_post_mark_park()

    @Slot()
    def abortMark(self):
        """Immediate abort for marking or framing (Escape hotkey)."""
        if self._is_framing:
            self._stop_framing()

        if self.exec_thread and self.exec_thread.isRunning():
            self.exec_thread.abort()
            self.exec_thread.wait(500)
            self.exec_thread = None

        if hasattr(self, '_sim_timer') and self._sim_timer.isActive():
            self._sim_timer.stop()

        ctrl = self.galvo_controller
        if ctrl and ctrl.connection:
            try:
                if hasattr(ctrl.connection, 'laser_off'):
                    ctrl.connection.laser_off()
                if hasattr(ctrl.connection, 'stop'):
                    ctrl.connection.stop()
            except Exception as e:
                print(f"[CadBridge] Abort error: {e}")

        self._is_marking = False
        self.markingChanged.emit(False)
        self.progressChanged.emit(0, 0, 0.0)
        self._set_status("Operation ABORTED.")

    @Slot()
    def togglePause(self):
        """Toggles Pause/Resume for laser marking (F3 hotkey)."""
        ctrl = self.galvo_controller
        if ctrl:
            ctrl.is_paused = not getattr(ctrl, 'is_paused', False)
            self._is_paused = ctrl.is_paused
            self.cadStateChanged.emit()
            self._set_status("Laser Marking PAUSED" if self._is_paused else "Laser Marking RESUMED")

    # ---------------- File Import (DXF / SVG / Gerber / Raster) ---------------- #

    @Slot(str)
    def importFile(self, file_path: str):
        """
        Parses a CAD vector or raster file (.dxf, .svg, .gbr/.gtl/... Gerber, .png/.jpg/.bmp)
        and converts entities into native QML shapes that display immediately on the QML Canvas.
        """
        if not file_path:
            return

        # Correctly decode Qt URL or raw Windows filesystem path (spaces, %20, etc.)
        u = QUrl(file_path)
        if u.isLocalFile():
            local_path = u.toLocalFile()
        else:
            local_path = file_path
            if local_path.startswith("file:///"):
                local_path = local_path[8:]
            local_path = unquote(local_path)

        local_path = os.path.normpath(local_path)
        self._last_imported_path = local_path

        if not os.path.exists(local_path):
            self._set_status(f"File not found: {local_path}")
            return

        file_name = os.path.basename(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        self._set_status(f"Importing CAD file: {file_name}...")
        imported_shapes = []

        try:
            polygons = []
            if ext == ".dxf":
                parser = DXFParser(local_path)
                polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
            elif ext == ".svg":
                parser = SVGParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)
            elif ext in ('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.gml', '.gtp', '.gbp', '.drl', '.txt'):
                parser = GerberParser(local_path)
                polygons = parser.parse_to_polygons(field_size=self.galvo_config.field_size)
            elif ext in ('.bmp', '.jpg', '.jpeg', '.png'):
                parser = ImageParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)
            else:
                # Default fallback attempt as SVG
                parser = SVGParser(field_size=self.galvo_config.field_size)
                polygons = parser.parse_to_polygons(local_path)

            if not polygons:
                self._set_status(f"No vector curves or polylines found in {file_name}.")
                return

            # Compute overall bounding box
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            for poly in polygons:
                for pt in poly:
                    min_x = min(min_x, pt[0])
                    max_x = max(max_x, pt[0])
                    min_y = min(min_y, pt[1])
                    max_y = max(max_y, pt[1])

            if min_x == float('inf'):
                self._set_status(f"Invalid geometry in {file_name}.")
                return

            bw = float(max_x - min_x) if max_x > min_x else 10.0
            bh = float(max_y - min_y) if max_y > min_y else 10.0
            cx = float((min_x + max_x) / 2.0)
            cy = float((min_y + max_y) / 2.0)

            # Normalize polylines relative to (cx, cy)
            rel_paths = []
            for poly in polygons:
                rel_poly = [[float(round(pt[0] - cx, 3)), float(round(pt[1] - cy, 3))] for pt in poly]
                rel_paths.append(rel_poly)

            # Package as a unified QML Vector CAD Shape
            shape_name = os.path.splitext(file_name)[0]
            qml_shape = {
                "id": int(len(self._shapes) + 1),
                "name": str(shape_name),
                "type": "polygon",
                "xMm": float(round(cx, 2)),
                "yMm": float(round(cy, 2)),
                "wMm": float(round(bw, 2)),
                "hMm": float(round(bh, 2)),
                "rotation": 0.0,
                "penId": 0,
                "hatched": False,
                "visible": True,
                "locked": False,
                "paths": rel_paths
            }
            imported_shapes.append(qml_shape)

            # Emit to QML Canvas
            self.shapesImported.emit(imported_shapes)
            self._set_status(f"Imported '{shape_name}' ({len(polygons)} curves, {bw:.1f}x{bh:.1f}mm)")

        except Exception as e:
            err_msg = f"Import error: {e}"
            print(f"[CadBridge] {err_msg}")
            self._set_status(err_msg)

    @Slot()
    def reimportLastFile(self):
        """Re-parses the most recently imported CAD file with updated galvo_config."""
        if hasattr(self, '_last_imported_path') and self._last_imported_path and os.path.exists(self._last_imported_path):
            self.importFile(self._last_imported_path)

    # ---------------- Legacy Adapter Fallback ---------------- #

    @Slot()
    def openCadEditor(self):
        """Optional fallback to launch the separate QWidget window if desired."""
        from cad_canvas import CadCanvasWidget
        if self.cad_widget is None:
            self.cad_widget = CadCanvasWidget(main_window=self._adapter)
            self.cad_widget.setWindowTitle("Galvo Studio - 2D CAD Canvas & Hatching Editor")
            self.cad_widget.resize(1150, 750)
        self.cad_widget.show()
        self.cad_widget.raise_()
        self.cad_widget.activateWindow()

    def _set_status(self, msg: str):
        self._status_message = str(msg)
        self.statusMessageChanged.emit(self._status_message)
        print(f"[CadBridge] {msg}")
