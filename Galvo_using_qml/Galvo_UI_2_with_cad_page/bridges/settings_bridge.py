import os
import sys
from configparser import ConfigParser
from PySide6.QtCore import QObject, Signal, Slot, Property

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)


class SettingsBridge(QObject):
    """
    QObject Bridge for Application & Hardware Configuration:
    - Machine Name & Company branding (matching Mini Scriber UI)
    - Galvo Optical Field & Lens Calibration ([GalvoField])
    - Optical distortion corrections & post-mark park positions
    """
    machineNameChanged = Signal(str)
    fieldSettingsChanged = Signal(float, float, float, float)
    advancedConfigChanged = Signal()
    settingsSaved = Signal(str)

    CONFIG_FILE = os.path.join(_root, "config", "config.ini")

    def __init__(self, cad_bridge=None, parent=None):
        super().__init__(parent)
        self.cad_bridge = cad_bridge

        # Machine Identity
        self._machine_name = "Galvo Studio"

        # [GalvoField] Optical Lens Specs
        self._field_size = 70.0
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._angle = 0.0
        self._galvo1_x = False

        # Galvo 1 & 2 Calibration Factors (from configgalvo in main.py)
        self._g1_negate = False
        self._g1_scale = 100.0
        self._g1_barrel = 1.0
        self._g1_par = 1.0
        self._g1_trapezoid = 1.0

        self._g2_negate = False
        self._g2_scale = 100.0
        self._g2_barrel = 1.0
        self._g2_par = 1.0
        self._g2_trapezoid = 1.0

        self._pos_after_mark = "confgalvocent"
        self._sp_x = 0.0
        self._sp_y = 0.0

        self._load_config()

    def _load_config(self):
        """Loads machine name and [GalvoField] settings from config.ini."""
        if not os.path.exists(self.CONFIG_FILE):
            return
        try:
            parser = ConfigParser()
            parser.read(self.CONFIG_FILE)

            # 1. Machine Identity
            if parser.has_section("machine"):
                self._machine_name = parser.get("machine", "name", fallback="Galvo Studio")

            # 2. [GalvoField]
            if parser.has_section("GalvoField"):
                self._field_size = float(parser.get("GalvoField", "field_size", fallback="70.0"))
                self._offset_x = float(parser.get("GalvoField", "offset_x", fallback="0.0"))
                self._offset_y = float(parser.get("GalvoField", "offset_y", fallback="0.0"))
                self._angle = float(parser.get("GalvoField", "angle", fallback="0.0"))
                self._galvo1_x = parser.getboolean("GalvoField", "galvo1_x", fallback=False)

                self._g1_negate = parser.getboolean("GalvoField", "g1_negate", fallback=False)
                self._g1_scale = float(parser.get("GalvoField", "g1_scale", fallback="100.0"))
                self._g1_barrel = float(parser.get("GalvoField", "g1_barrel", fallback="1.0"))
                self._g1_par = float(parser.get("GalvoField", "g1_par", fallback="1.0"))
                self._g1_trapezoid = float(parser.get("GalvoField", "g1_trapezoid", fallback="1.0"))

                self._g2_negate = parser.getboolean("GalvoField", "g2_negate", fallback=False)
                self._g2_scale = float(parser.get("GalvoField", "g2_scale", fallback="100.0"))
                self._g2_barrel = float(parser.get("GalvoField", "g2_barrel", fallback="1.0"))
                self._g2_par = float(parser.get("GalvoField", "g2_par", fallback="1.0"))
                self._g2_trapezoid = float(parser.get("GalvoField", "g2_trapezoid", fallback="1.0"))

                self._pos_after_mark = parser.get("GalvoField", "pos_after_mark", fallback="confgalvocent")
                self._sp_x = float(parser.get("GalvoField", "sp_x", fallback="0.0"))
                self._sp_y = float(parser.get("GalvoField", "sp_y", fallback="0.0"))

            print(f"[SettingsBridge] Loaded machine='{self._machine_name}', field_size={self._field_size}mm")
        except Exception as e:
            print(f"[SettingsBridge] Config load error: {e}")

    # ---------------- Properties for QML ---------------- #

    def get_machine_name(self) -> str:
        return self._machine_name

    def get_field_size(self) -> float:
        if self.cad_bridge and hasattr(self.cad_bridge, 'galvo_config') and self.cad_bridge.galvo_config.field_size > 0:
            return self.cad_bridge.galvo_config.field_size
        return self._field_size

    def get_offset_x(self) -> float:
        return self._offset_x

    def get_offset_y(self) -> float:
        return self._offset_y

    def get_angle(self) -> float:
        return self._angle

    def get_g1_negate(self) -> bool:
        return self._g1_negate

    def get_g1_scale(self) -> float:
        return self._g1_scale

    def get_g1_barrel(self) -> float:
        return self._g1_barrel

    def get_g1_par(self) -> float:
        return self._g1_par

    def get_g1_trapezoid(self) -> float:
        return self._g1_trapezoid

    def get_g2_negate(self) -> bool:
        return self._g2_negate

    def get_g2_scale(self) -> float:
        return self._g2_scale

    def get_g2_barrel(self) -> float:
        return self._g2_barrel

    def get_g2_par(self) -> float:
        return self._g2_par

    def get_g2_trapezoid(self) -> float:
        return self._g2_trapezoid

    def get_pos_after_mark(self) -> str:
        return self._pos_after_mark

    def get_sp_x(self) -> float:
        return self._sp_x

    def get_sp_y(self) -> float:
        return self._sp_y

    def get_galvo1_x(self) -> bool:
        return self._galvo1_x

    machineName = Property(str, get_machine_name, notify=machineNameChanged)
    fieldSize = Property(float, get_field_size, notify=fieldSettingsChanged)
    offsetX = Property(float, get_offset_x, notify=fieldSettingsChanged)
    offsetY = Property(float, get_offset_y, notify=fieldSettingsChanged)
    fieldAngle = Property(float, get_angle, notify=fieldSettingsChanged)
    galvo1X = Property(bool, get_galvo1_x, notify=advancedConfigChanged)

    g1Negate = Property(bool, get_g1_negate, notify=advancedConfigChanged)
    g1Scale = Property(float, get_g1_scale, notify=advancedConfigChanged)
    g1Barrel = Property(float, get_g1_barrel, notify=advancedConfigChanged)
    g1Par = Property(float, get_g1_par, notify=advancedConfigChanged)
    g1Trapezoid = Property(float, get_g1_trapezoid, notify=advancedConfigChanged)

    g2Negate = Property(bool, get_g2_negate, notify=advancedConfigChanged)
    g2Scale = Property(float, get_g2_scale, notify=advancedConfigChanged)
    g2Barrel = Property(float, get_g2_barrel, notify=advancedConfigChanged)
    g2Par = Property(float, get_g2_par, notify=advancedConfigChanged)
    g2Trapezoid = Property(float, get_g2_trapezoid, notify=advancedConfigChanged)

    posAfterMark = Property(str, get_pos_after_mark, notify=advancedConfigChanged)
    spX = Property(float, get_sp_x, notify=advancedConfigChanged)
    spY = Property(float, get_sp_y, notify=advancedConfigChanged)

    # ---------------- Slots Invoked from QML ---------------- #

    @Slot(str)
    def saveMachineName(self, name: str):
        """Saves custom machine identity to config.ini and updates application UI."""
        clean_name = str(name).strip()
        if not clean_name:
            clean_name = "Galvo Studio"
        self._machine_name = clean_name

        try:
            parser = ConfigParser()
            if os.path.exists(self.CONFIG_FILE):
                parser.read(self.CONFIG_FILE)
            if not parser.has_section("machine"):
                parser.add_section("machine")
            parser.set("machine", "name", self._machine_name)
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
            print(f"[SettingsBridge] Machine name saved: '{self._machine_name}'")
        except Exception as e:
            print(f"[SettingsBridge] Error saving machine name: {e}")

        self.machineNameChanged.emit(self._machine_name)
        self.settingsSaved.emit(f"Machine name updated: {self._machine_name}")

    @Slot(float, float, float, float)
    def saveLensFieldSettings(self, field_size: float, ox: float, oy: float, angle: float):
        """Saves optical field & lens calibration settings to config.ini."""
        self._field_size = max(10.0, float(field_size))
        self._offset_x = float(ox)
        self._offset_y = float(oy)
        self._angle = float(angle)

        try:
            parser = ConfigParser()
            if os.path.exists(self.CONFIG_FILE):
                parser.read(self.CONFIG_FILE)
            if not parser.has_section("GalvoField"):
                parser.add_section("GalvoField")
            parser.set("GalvoField", "field_size", f"{self._field_size:.1f}")
            parser.set("GalvoField", "offset_x", f"{self._offset_x:.2f}")
            parser.set("GalvoField", "offset_y", f"{self._offset_y:.2f}")
            parser.set("GalvoField", "angle", f"{self._angle:.2f}")
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
        except Exception as e:
            print(f"[SettingsBridge] Error saving GalvoField: {e}")

        # Sync with CadBridge so Canvas redraws bed boundaries instantly
        if self.cad_bridge:
            self.cad_bridge.setFieldSettings(self._field_size, self._offset_x, self._offset_y, self._angle)

        self.fieldSettingsChanged.emit(self._field_size, self._offset_x, self._offset_y, self._angle)
        self.settingsSaved.emit(f"Galvo Lens Field set to {self._field_size:.1f} mm")

    @Slot(bool, float, float, float, float, bool, float, float, float, float, str, float, float)
    def saveAdvancedGalvoCalibration(self, g1_neg, g1_scale, g1_bar, g1_par, g1_trap,
                                     g2_neg, g2_scale, g2_bar, g2_par, g2_trap,
                                     pos_after, sp_x, sp_y):
        """Saves advanced distortion factors and park position to config.ini."""
        self._g1_negate = bool(g1_neg)
        self._g1_scale = float(g1_scale)
        self._g1_barrel = float(g1_bar)
        self._g1_par = float(g1_par)
        self._g1_trapezoid = float(g1_trap)

        self._g2_negate = bool(g2_neg)
        self._g2_scale = float(g2_scale)
        self._g2_barrel = float(g2_bar)
        self._g2_par = float(g2_par)
        self._g2_trapezoid = float(g2_trap)

        self._pos_after_mark = str(pos_after)
        self._sp_x = float(sp_x)
        self._sp_y = float(sp_y)

        try:
            parser = ConfigParser()
            if os.path.exists(self.CONFIG_FILE):
                parser.read(self.CONFIG_FILE)
            if not parser.has_section("GalvoField"):
                parser.add_section("GalvoField")
            parser.set("GalvoField", "g1_negate", str(self._g1_negate))
            parser.set("GalvoField", "g1_scale", f"{self._g1_scale:.2f}")
            parser.set("GalvoField", "g1_barrel", f"{self._g1_barrel:.3f}")
            parser.set("GalvoField", "g1_par", f"{self._g1_par:.3f}")
            parser.set("GalvoField", "g1_trapezoid", f"{self._g1_trapezoid:.3f}")

            parser.set("GalvoField", "g2_negate", str(self._g2_negate))
            parser.set("GalvoField", "g2_scale", f"{self._g2_scale:.2f}")
            parser.set("GalvoField", "g2_barrel", f"{self._g2_barrel:.3f}")
            parser.set("GalvoField", "g2_par", f"{self._g2_par:.3f}")
            parser.set("GalvoField", "g2_trapezoid", f"{self._g2_trapezoid:.3f}")

            parser.set("GalvoField", "pos_after_mark", self._pos_after_mark)
            parser.set("GalvoField", "sp_x", f"{self._sp_x:.2f}")
            parser.set("GalvoField", "sp_y", f"{self._sp_y:.2f}")

            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
            print("[SettingsBridge] Advanced Galvo distortion calibration saved.")
        except Exception as e:
            print(f"[SettingsBridge] Error saving advanced calib: {e}")

        self.advancedConfigChanged.emit()
        self.settingsSaved.emit("Advanced Galvo calibration saved.")

    @Slot(float, float, float, result=float)
    def computeScale(self, current_scale: float, desired: float, actual: float) -> float:
        """Calculates corrected scale from measured vs desired dimensions."""
        try:
            if float(actual) != 0:
                res = float(current_scale) * (float(desired) / float(actual))
                return round(res, 4)
        except Exception as e:
            print(f"[SettingsBridge] Scale compute error: {e}")
        return current_scale

    @Slot(float, float, float, float, bool, bool, float, float, float, float, bool, float, float, float, float, str, float, float)
    def saveFullConfigGalvo(self, field_size, off_x, off_y, angle, galvo1_x,
                            g1_neg, g1_scale, g1_bar, g1_par, g1_trap,
                            g2_neg, g2_scale, g2_bar, g2_par, g2_trap,
                            pos_after, sp_x, sp_y):
        """Saves full aspect, mirror mappings, distortion, and park position settings matching main.py."""
        self._field_size = float(field_size)
        self._offset_x = float(off_x)
        self._offset_y = float(off_y)
        self._angle = float(angle)
        self._galvo1_x = bool(galvo1_x)

        self._g1_negate = bool(g1_neg)
        self._g1_scale = float(g1_scale)
        self._g1_barrel = float(g1_bar)
        self._g1_par = float(g1_par)
        self._g1_trapezoid = float(g1_trap)

        self._g2_negate = bool(g2_neg)
        self._g2_scale = float(g2_scale)
        self._g2_barrel = float(g2_bar)
        self._g2_par = float(g2_par)
        self._g2_trapezoid = float(g2_trap)

        self._pos_after_mark = str(pos_after)
        self._sp_x = float(sp_x)
        self._sp_y = float(sp_y)

        try:
            parser = ConfigParser()
            if os.path.exists(self.CONFIG_FILE):
                parser.read(self.CONFIG_FILE)
            if not parser.has_section("GalvoField"):
                parser.add_section("GalvoField")

            parser.set("GalvoField", "field_size", f"{self._field_size:.2f}")
            parser.set("GalvoField", "offset_x", f"{self._offset_x:.2f}")
            parser.set("GalvoField", "offset_y", f"{self._offset_y:.2f}")
            parser.set("GalvoField", "angle", f"{self._angle:.2f}")
            parser.set("GalvoField", "galvo1_x", str(self._galvo1_x))

            parser.set("GalvoField", "g1_negate", str(self._g1_negate))
            parser.set("GalvoField", "g1_scale", f"{self._g1_scale:.4f}")
            parser.set("GalvoField", "g1_barrel", f"{self._g1_barrel:.3f}")
            parser.set("GalvoField", "g1_par", f"{self._g1_par:.3f}")
            parser.set("GalvoField", "g1_trapezoid", f"{self._g1_trapezoid:.3f}")

            parser.set("GalvoField", "g2_negate", str(self._g2_negate))
            parser.set("GalvoField", "g2_scale", f"{self._g2_scale:.4f}")
            parser.set("GalvoField", "g2_barrel", f"{self._g2_barrel:.3f}")
            parser.set("GalvoField", "g2_par", f"{self._g2_par:.3f}")
            parser.set("GalvoField", "g2_trapezoid", f"{self._g2_trapezoid:.3f}")

            parser.set("GalvoField", "pos_after_mark", self._pos_after_mark)
            parser.set("GalvoField", "sp_x", f"{self._sp_x:.2f}")
            parser.set("GalvoField", "sp_y", f"{self._sp_y:.2f}")

            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                parser.write(f)
            print("[SettingsBridge] Full Galvo configuration saved to config.ini.")
        except Exception as e:
            print(f"[SettingsBridge] Error saving full Galvo config: {e}")

        # Sync CAD Canvas & Hardware Transformation Engine
        if self.cad_bridge:
            if hasattr(self.cad_bridge, 'setFullGalvoConfig'):
                self.cad_bridge.setFullGalvoConfig(
                    self._field_size, self._offset_x, self._offset_y, self._angle, self._galvo1_x,
                    self._g1_negate, self._g1_scale, self._g1_barrel, self._g1_par, self._g1_trapezoid,
                    self._g2_negate, self._g2_scale, self._g2_barrel, self._g2_par, self._g2_trapezoid,
                    self._pos_after_mark, self._sp_x, self._sp_y
                )
            else:
                self.cad_bridge.setFieldSettings(self._field_size, self._offset_x, self._offset_y, self._angle)

        self.fieldSettingsChanged.emit(self._field_size, self._offset_x, self._offset_y, self._angle)
        self.advancedConfigChanged.emit()
        self.settingsSaved.emit("Galvo configuration applied successfully.")

