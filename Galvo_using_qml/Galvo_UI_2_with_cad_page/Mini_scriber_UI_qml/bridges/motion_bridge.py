import os
import re
from PySide6.QtCore import QObject, Signal, Slot, Property
from util import ConfigHandler

class MotionBridge(QObject):
    positionChanged = Signal()
    travelChanged = Signal()
    feedChanged = Signal()
    safetyAlert = Signal(str)

    def __init__(self, serial_bridge, settings_bridge=None, parent=None):
        super().__init__(parent)
        self._serial = serial_bridge
        self._settings = settings_bridge
        self._serial.add_response_listener(self._handle_serial_response)

        # Coordinate state
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0

        # Motion settings
        self._travel = 10.0
        self._jog_feed = 1000
        self._laser_feed = 500
        self._z_max_limit = 16.0
        self._x_center = 50.0
        self._y_center = 50.0
        self._z_center = 8.0

        self._load_config_feed()
        self._sync_with_hardware_config()
        if self._settings:
            self._settings.hardwareConfigChanged.connect(self._sync_with_hardware_config)

    def _sync_with_hardware_config(self):
        if self._settings:
            self._z_max_limit = float(self._settings.zMaxTravel)
            self._x_center = round(float(self._settings.bedWidth) / 2.0, 3)
            self._y_center = round(float(self._settings.bedHeight) / 2.0, 3)
            self._z_center = round(self._z_max_limit / 2.0, 3)
        else:
            try:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                cfg_path = os.path.join(app_dir, "config", "config.ini")
                ch = ConfigHandler()
                ch.ini_parser.read(cfg_path)
                zm = ch.getValues("hardware", "z_max")
                if zm: self._z_max_limit = float(zm)
                bw = ch.getValues("hardware", "bed_width")
                bh = ch.getValues("hardware", "bed_height")
                if bw: self._x_center = round(float(bw) / 2.0, 3)
                if bh: self._y_center = round(float(bh) / 2.0, 3)
                self._z_center = round(self._z_max_limit / 2.0, 3)
            except Exception:
                pass
        self.travelChanged.emit()

    def _load_config_feed(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cfg_path = os.path.join(app_dir, "config", "config.ini")
            ch = ConfigHandler()
            ch.ini_parser.read(cfg_path)
            j_val = ch.getValues("feed", "jog")
            l_val = ch.getValues("feed", "laser")
            if j_val: self._jog_feed = min(2000, max(100, int(j_val)))
            if l_val: self._laser_feed = int(l_val)
        except Exception as e:
            print(f"[MotionBridge] Warning: Could not read config feeds: {e}")

    def canMoveZPlus(self, delta: float) -> bool:
        """Strict hardware safety boundary check matching main.py canMoveZPlus."""
        if self._z + delta > self._z_max_limit:
            self.safetyAlert.emit(f"Z+ move blocked! Would exceed maximum travel limit of {self._z_max_limit} mm.")
            return False
        return True

    @Slot(str)
    def _handle_serial_response(self, line: str):
        # Parse M114 response: e.g. "X:10.50 Y:20.00 Z:5.00"
        if "X:" in line and "Y:" in line:
            try:
                x_match = re.search(r'X:([-\d\.]+)', line)
                y_match = re.search(r'Y:([-\d\.]+)', line)
                z_match = re.search(r'Z:([-\d\.]+)', line)
                changed = False

                if x_match:
                    self._x = float(x_match.group(1))
                    changed = True
                if y_match:
                    self._y = float(y_match.group(1))
                    changed = True
                if z_match:
                    self._z = float(z_match.group(1))
                    changed = True

                if changed:
                    self.positionChanged.emit()
            except Exception as e:
                print(f"[MotionBridge] Failed to parse position: {e}")

    @Slot(float, float)
    def setSimulatedPosition(self, x: float, y: float):
        """Allows simulation or preview stepping to smoothly track virtual laser head."""
        self._x = round(float(x), 3)
        self._y = round(float(y), 3)
        self.positionChanged.emit()

    # --- Properties ---
    @Property(float, notify=positionChanged)
    def xPos(self):
        return round(self._x, 3)

    @Property(float, notify=positionChanged)
    def yPos(self):
        return round(self._y, 3)

    @Property(float, notify=positionChanged)
    def zPos(self):
        return round(self._z, 3)

    @Property(float, notify=travelChanged)
    def travelDistance(self):
        return self._travel

    @Property(int, notify=feedChanged)
    def jogFeed(self):
        return self._jog_feed

    @Property(float, notify=travelChanged)
    def zMaxLimit(self):
        return self._z_max_limit

    @Property(float, notify=travelChanged)
    def xCenter(self):
        return self._x_center

    @Property(float, notify=travelChanged)
    def yCenter(self):
        return self._y_center

    @Property(float, notify=travelChanged)
    def zCenter(self):
        return self._z_center

    # --- Slots ---
    @Slot(float)
    def setTravel(self, val: float):
        if val > 0 and self._travel != val:
            self._travel = val
            self.travelChanged.emit()

    @Slot(int)
    def setFeed(self, val: int):
        clamped = min(2000, max(100, int(val)))
        if self._jog_feed != clamped:
            self._jog_feed = clamped
            self.feedChanged.emit()

    @Slot(str)
    @Slot(str, float)
    def jog(self, direction: str, step_override: float = 0.0):
        """
        Jog directions: 'xplus', 'xminus', 'yplus', 'yminus', 'zplus', 'zminus'
        Supports optional step_override to allow camera/focus jog without changing global travel.
        """
        dir_lower = direction.lower()
        dist = step_override if step_override > 0.0 else self._travel

        # Z Safety check
        if dir_lower == "zplus":
            if not self.canMoveZPlus(dist):
                return

        axis_map = {
            "xplus": ("X", dist),
            "xminus": ("X", -dist),
            "yplus": ("Y", dist),
            "yminus": ("Y", -dist),
            "zplus": ("Z", dist),
            "zminus": ("Z", -dist),
        }

        if dir_lower in axis_map:
            axis, amount = axis_map[dir_lower]
            if self._serial.connected:
                # Relative move + restore G90 + M114
                self._serial.sendGcode("G91")
                self._serial.sendGcode(f"G1 F{self._jog_feed} {axis}{amount}")
                self._serial.sendGcode("G90")
                self._serial.sendGcode("M114")
            else:
                # Simulator mode when offline
                if axis == "X":
                    self._x += amount
                elif axis == "Y":
                    self._y += amount
                elif axis == "Z":
                    self._z = min(self._z_max_limit, max(0.0, self._z + amount))
                self.positionChanged.emit()

    @Slot()
    def homeAll(self):
        if self._serial.connected:
            self._serial.sendGcode("G28")
            self._serial.sendGcode("M114")
        else:
            self._x = 0.0
            self._y = 0.0
            self._z = 0.0
            self.positionChanged.emit()

    @Slot(str)
    def homeAxis(self, axis: str):
        ax = axis.upper()
        if self._serial.connected:
            self._serial.sendGcode(f"G28 {ax}")
            self._serial.sendGcode("M114")
        else:
            if ax == "X": self._x = 0.0
            elif ax == "Y": self._y = 0.0
            elif ax == "Z": self._z = 0.0
            self.positionChanged.emit()

    @Slot()
    def zeroAll(self):
        if self._serial.connected:
            self._serial.sendGcode("G92 X0 Y0 Z0")
            self._serial.sendGcode("M114")
        else:
            self._x = 0.0
            self._y = 0.0
            self._z = 0.0
            self.positionChanged.emit()

    @Slot(str)
    def zeroAxis(self, axis: str):
        ax = axis.upper()
        if self._serial.connected:
            self._serial.sendGcode(f"G92 {ax}0")
            self._serial.sendGcode("M114")
        else:
            if ax == "X": self._x = 0.0
            elif ax == "Y": self._y = 0.0
            elif ax == "Z": self._z = 0.0
            self.positionChanged.emit()

    @Slot()
    def centerXY(self):
        if self._serial.connected:
            self._serial.sendGcode("G90")
            self._serial.sendGcode(f"G1 F{self._jog_feed} X{self._x_center} Y{self._y_center}")
            self._serial.sendGcode("M114")
        else:
            self._x = self._x_center
            self._y = self._y_center
            self.positionChanged.emit()

    @Slot()
    def centerZ(self):
        if self._serial.connected:
            self._serial.sendGcode("G90")
            self._serial.sendGcode(f"G1 F{self._jog_feed} Z{self._z_center}")
            self._serial.sendGcode("M114")
        else:
            self._z = self._z_center
            self.positionChanged.emit()

    @Slot(float, float)
    def moveToCoordinates(self, x: float, y: float):
        """Commands absolute motion to target bed coordinate (e.g. Print Starting Index Point)."""
        x_target = round(float(x), 3)
        y_target = round(float(y), 3)
        if self._serial.connected:
            self._serial.sendGcode("G90")
            self._serial.sendGcode(f"G1 F{self._jog_feed} X{x_target} Y{y_target}")
            self._serial.sendGcode("M114")
        else:
            self._x = x_target
            self._y = y_target
            self.positionChanged.emit()

    @Slot()
    def park(self):
        """Moves toolhead to safe loading/parking position at (X50, Y0)."""
        self.moveToCoordinates(self._x_center, 0.0)

    @Slot(float, float, float)
    def moveToXYZ(self, x: float, y: float, z: float):
        """Commands absolute motion to target (X, Y, Z) coordinates with boundary check."""
        x_target = round(float(x), 3)
        y_target = round(float(y), 3)
        z_target = min(self._z_max_limit, max(0.0, round(float(z), 3)))
        if self._serial.connected:
            self._serial.sendGcode("G90")
            self._serial.sendGcode(f"G1 F{self._jog_feed} X{x_target} Y{y_target} Z{z_target}")
            self._serial.sendGcode("M114")
        else:
            self._x = x_target
            self._y = y_target
            self._z = z_target
            self.positionChanged.emit()

