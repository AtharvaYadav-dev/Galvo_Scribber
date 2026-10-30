import os
import re
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from laser import LaserConfig
from util import ConfigHandler

class LaserBridge(QObject):
    laserChanged = Signal()
    powerChanged = Signal()
    laserActiveChanged = Signal(bool)
    focusChanged = Signal()
    offsetChanged = Signal()
    statusAlert = Signal(str)

    def __init__(self, serial_bridge, motion_bridge=None, settings_bridge=None, parent=None):
        super().__init__(parent)
        self._serial = serial_bridge
        self._motion = motion_bridge
        self._settings = settings_bridge
        self._config = LaserConfig()

        self._available_lasers = ["Laser 1", "Laser 2"]
        self._selected_laser = "Laser 1"
        self._power = 10.0  # percentage
        self._current_ma = 0.0
        self._pulse_duration_ms = 200
        self._is_active = False

        # Config file path
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_file_path = os.path.join(app_dir, "config", "config.ini")
        self._ch = ConfigHandler()

        # Focus Calibration parameters
        self._laser1_focus = 10.0
        self._laser2_focus = 10.0
        self._obj_height = 0.0
        self._focus_step = 0.1  # 1.0, 0.1, 0.01 mm

        # Offset Calibration parameters
        self._zero_laser = "Laser 1"
        self._offset_laser = "Laser 2"
        self._x_offset = 0.0
        self._y_offset = 0.0
        self._offset_step = 1.0  # 10.0, 5.0, 1.0, 0.1 mm
        self._xtemp = 0.0
        self._ytemp = 0.0
        self._is_zero_set = False

        self._load_config()
        self._sync_with_hardware_config()
        if self._settings:
            self._settings.hardwareConfigChanged.connect(self._sync_with_hardware_config)
        self._update_current()

    def _sync_with_hardware_config(self):
        count = 2
        if self._settings:
            count = self._settings.laserCount
        else:
            try:
                ch = ConfigHandler()
                ch.ini_parser.read(self._config_file_path)
                lc = ch.getValues("hardware", "laser_count")
                if lc: count = int(lc)
            except Exception:
                pass

        if count == 1:
            self._available_lasers = ["Laser 1"]
            if self._selected_laser != "Laser 1":
                self._selected_laser = "Laser 1"
        else:
            self._available_lasers = ["Laser 1", "Laser 2"]
        self.laserChanged.emit()

    def set_motion_bridge(self, motion_bridge):
        self._motion = motion_bridge

    def _load_config(self):
        """Loads focus and offset parameters from config.ini."""
        if not os.path.exists(self._config_file_path):
            return

        try:
            self._ch.ini_parser.read(self._config_file_path)

            # Focus section
            focus_dict = self._ch.getSection("focus")
            if focus_dict:
                if 'objheight' in focus_dict:
                    try:
                        self._obj_height = float(focus_dict['objheight'])
                    except ValueError:
                        pass
                for k, v in focus_dict.items():
                    clean_v = v.replace('{', '').replace('}', '').replace("'", "")
                    if ':' in clean_v:
                        parts = clean_v.split(':')
                        name = parts[0].strip()
                        val = float(parts[1].strip())
                        if name.lower() == "laser 1":
                            self._laser1_focus = val
                        elif name.lower() == "laser 2":
                            self._laser2_focus = val

            # Zero reference section
            zero_laser = self._ch.getValues("zero", "laser")
            if zero_laser:
                self._zero_laser = zero_laser.strip()

            # Offset section
            off_laser = self._ch.getValues("offset", "laser")
            if off_laser:
                self._offset_laser = off_laser.strip()
            xoff = self._ch.getValues("offset", "xoffset")
            yoff = self._ch.getValues("offset", "yoffset")
            if xoff is not None:
                try: self._x_offset = float(xoff)
                except ValueError: pass
            if yoff is not None:
                try: self._y_offset = float(yoff)
                except ValueError: pass

        except Exception as e:
            print(f"[LaserBridge] Failed to load config: {e}")

    def _laser_key(self):
        return "laser1" if self._selected_laser == "Laser 1" else "laser2"

    def _laser_pwm_channel(self):
        return 0 if self._selected_laser == "Laser 1" else 1

    def _update_current(self):
        try:
            curr = self._config.getCurrent(self._power, self._laser_key())
            self._current_ma = float(curr) if curr is not None else 0.0
        except Exception:
            self._current_ma = 0.0

    # --- Properties ---
    @Property(list, notify=laserChanged)
    def availableLasers(self):
        return self._available_lasers

    @Property(str, notify=laserChanged)
    def selectedLaser(self):
        return self._selected_laser

    @selectedLaser.setter
    def selectedLaser(self, name: str):
        if name in self._available_lasers and self._selected_laser != name:
            if self._is_active:
                self.turnOff()
            self._selected_laser = name
            self._update_current()
            self.laserChanged.emit()
            self.powerChanged.emit()
            self.focusChanged.emit()

    @Property(float, notify=powerChanged)
    def powerPercent(self):
        return self._power

    @Property(float, notify=powerChanged)
    def currentMa(self):
        return round(self._current_ma, 1)

    @Property(int, notify=powerChanged)
    def pulseDurationMs(self):
        return self._pulse_duration_ms

    @Property(bool, notify=laserActiveChanged)
    def laserActive(self):
        return self._is_active

    # Focus Properties
    @Property(float, notify=focusChanged)
    def objHeight(self):
        return self._obj_height

    @Property(float, notify=focusChanged)
    def laser1Focus(self):
        return self._laser1_focus

    @Property(float, notify=focusChanged)
    def laser2Focus(self):
        return self._laser2_focus

    @Property(float, notify=focusChanged)
    def currentFocus(self):
        return self._laser1_focus if self._selected_laser == "Laser 1" else self._laser2_focus

    @Property(float, notify=focusChanged)
    def focusStep(self):
        return self._focus_step

    # Offset Properties
    @Property(str, notify=offsetChanged)
    def zeroLaser(self):
        return self._zero_laser

    @Property(str, notify=offsetChanged)
    def offsetLaser(self):
        return self._offset_laser

    @Property(float, notify=offsetChanged)
    def xOffset(self):
        return self._x_offset

    @Property(float, notify=offsetChanged)
    def yOffset(self):
        return self._y_offset

    @Property(float, notify=offsetChanged)
    def offsetStep(self):
        return self._offset_step

    @Property(bool, notify=offsetChanged)
    def isZeroSet(self):
        return self._is_zero_set

    # --- Slots: General & Power ---
    @Slot(float)
    def setPower(self, val: float):
        val = max(0.0, min(51.3, float(val)))
        if self._power != val:
            self._power = val
            self._update_current()
            self.powerChanged.emit()

    @Slot(int)
    def setPulseDuration(self, ms: int):
        self._pulse_duration_ms = max(10, min(5000, ms))
        self.powerChanged.emit()

    @Slot()
    def toggleLaser(self):
        if self._is_active:
            self.turnOff()
        else:
            self.turnOn()

    @Slot()
    def turnOn(self):
        p_channel = self._laser_pwm_channel()
        pwm_val = int((self._power / 51.3) * 255)
        if pwm_val <= 0:
            pwm_val = 255
        cmd = f"M106 P{p_channel} S{pwm_val}"
        if self._serial.connected:
            self._serial.sendGcode(cmd)
        self._is_active = True
        self.laserActiveChanged.emit(True)
        self.statusAlert.emit(f"{self._selected_laser} Active @ {self._power:.1f}%")

    @Slot()
    def turnOff(self):
        p_channel = self._laser_pwm_channel()
        cmd = f"M106 P{p_channel} S0"
        if self._serial.connected:
            self._serial.sendGcode(cmd)
        self._is_active = False
        self.laserActiveChanged.emit(False)
        self.statusAlert.emit(f"{self._selected_laser} Turned OFF")

    @Slot()
    @Slot(str)
    def shutdownLaser(self, name=None):
        """
        Shuts down laser output matching main.py shutdownLaser(name=None):
        - If name is specified ("Laser 1" or "Laser 2"), sends OFF command for that laser.
        - If name is None, sends OFF command for all lasers (Laser 1: P0, Laser 2: P1) + M5 emergency halt.
        """
        if self._serial and self._serial.connected:
            if name:
                p_channel = 0 if "1" in str(name) else 1
                cmd = f"M106 P{p_channel} S0"
                self._serial.sendGcode(cmd)
                print(f"[LaserBridge] {name} : OFF ({cmd})")
            else:
                self._serial.sendGcode("M106 P0 S0")
                self._serial.sendGcode("M106 P1 S0")
                self._serial.sendGcode("M5")
                print("[LaserBridge] Automatic Shutdown: All Lasers OFF (M106 P0 S0, M106 P1 S0, M5)")

            if hasattr(self._serial, "_com") and self._serial._com and self._serial._com.serial_connection:
                try:
                    self._serial._com.serial_connection.flush()
                except Exception:
                    pass

        self._is_active = False
        self.laserActiveChanged.emit(False)
        self.statusAlert.emit("Lasers Shutdown (OFF)")

    @Slot()
    def shutdownAllLasers(self):
        self.shutdownLaser(None)

    @Slot()
    def emergencyOff(self):
        self.shutdownLaser(None)

    @Slot()
    def fireSingleShot(self):
        """Fires laser for specified pulse_duration_ms, then automatically turns off."""
        if self._is_active:
            return

        p_channel = self._laser_pwm_channel()
        pwm_val = int((self._power / 51.3) * 255)
        if pwm_val <= 0:
            pwm_val = 255

        if self._serial.connected:
            self._serial.sendGcode(f"M106 P{p_channel} S{pwm_val}")

        self._is_active = True
        self.laserActiveChanged.emit(True)
        self.statusAlert.emit(f"Pulse Shot: {self._pulse_duration_ms}ms")
        QTimer.singleShot(self._pulse_duration_ms, self.turnOff)

    @Slot()
    def emergencyOff(self):
        """Immediately turns off all laser PWM outputs."""
        if self._serial.connected:
            self._serial.sendGcode("M106 P0 S0")
            self._serial.sendGcode("M106 P1 S0")
            self._serial.sendGcode("M5")
        self._is_active = False
        self.laserActiveChanged.emit(False)
        self.statusAlert.emit("All Lasers Emergency Disabled")

    # --- Slots: Focus Calibration (Matching main.py focusAction) ---
    @Slot(float)
    def setObjHeight(self, val: float):
        self._obj_height = max(0.0, float(val))
        try:
            self._ch.addParameter("focus", "objheight", str(self._obj_height))
            self._ch.updateFile(self._config_file_path)
            self.statusAlert.emit(f"Object Height set to {self._obj_height} mm")
        except Exception as e:
            print(f"[LaserBridge] Failed to save objheight: {e}")
        self.focusChanged.emit()

    @Slot(float)
    def setFocusStep(self, step: float):
        if step > 0:
            self._focus_step = step
            self.focusChanged.emit()

    @Slot()
    def toggleFocusLaser(self):
        """Toggles the laser ON for focus spot observation."""
        if self._is_active:
            self.turnOff()
        else:
            p_channel = self._laser_pwm_channel()
            cmd = f"M106 P{p_channel} S255"
            if self._serial.connected:
                self._serial.sendGcode(cmd)
            self._is_active = True
            self.laserActiveChanged.emit(True)
            self.statusAlert.emit(f"{self._selected_laser} ON for Focus Calibration")

    @Slot(str)
    def jogFocusZ(self, direction: str):
        """Jog Z for focus calibration (+/-). Respects Z_MAX_LIMIT (16mm)."""
        dist = self._focus_step if direction.lower() == "plus" else -self._focus_step
        max_z = self._motion.zMaxLimit if self._motion else 16.0
        if self._motion:
            curr_z = self._motion.zPos
            if direction.lower() == "plus" and (curr_z + self._focus_step > max_z):
                self.statusAlert.emit(f"Z+ limit reached! Max travel is {max_z:.1f} mm.")
                return

        if self._serial.connected:
            self._serial.sendGcode("G91")
            self._serial.sendGcode(f"G1 F1000 Z{dist}")
            self._serial.sendGcode("M114")
        elif self._motion:
            self._motion.jog("zplus" if direction.lower() == "plus" else "zminus")

    @Slot()
    def saveFocus(self):
        """
        Saves current focus = current_z + obj_height to config.ini.
        Turns laser OFF upon saving.
        """
        self.turnOff()
        curr_z = self._motion.zPos if self._motion else 10.0
        final_focus = round(float(curr_z) + self._obj_height, 3)

        if self._selected_laser == "Laser 1":
            self._laser1_focus = final_focus
            sec_val = f"{{'Laser 1': {final_focus}}}"
            key = "laser 1"
        else:
            self._laser2_focus = final_focus
            sec_val = f"{{'Laser 2': {final_focus}}}"
            key = "laser 2"

        try:
            self._ch.addParameter("focus", key, sec_val)
            self._ch.updateFile(self._config_file_path)
            self.statusAlert.emit(f"{self._selected_laser} Focus saved: {final_focus} mm (Z={curr_z:.2f} + H={self._obj_height:.2f})")
        except Exception as e:
            self.statusAlert.emit(f"Error saving focus to config: {e}")

        self.focusChanged.emit()

    # --- Slots: Dual-Laser Offset Calibration (Matching main.py offsetAction) ---
    @Slot(float)
    def setOffsetStep(self, step: float):
        if step > 0:
            self._offset_step = step
            self.offsetChanged.emit()

    @Slot()
    def toggleOffsetLaser(self):
        """
        Moves Z to calibrated focus height, then turns ON laser.
        """
        if self._is_active:
            self.turnOff()
        else:
            focus = self.currentFocus
            if self._serial.connected:
                self._serial.sendGcode("G90")
                self._serial.sendGcode(f"G1 F1000 Z{focus}")
                p_channel = self._laser_pwm_channel()
                self._serial.sendGcode(f"M106 P{p_channel} S255")
            self._is_active = True
            self.laserActiveChanged.emit(True)
            self.statusAlert.emit(f"{self._selected_laser} driven to focus ({focus}mm) & ON")

    @Slot()
    def setZeroReference(self):
        """
        Records (x, y) reference zero for reference laser.
        Saves to config.ini [zero] laser.
        Auto-switches to the second laser.
        """
        self.turnOff()
        self._zero_laser = self._selected_laser
        self._xtemp = self._motion.xPos if self._motion else 0.0
        self._ytemp = self._motion.yPos if self._motion else 0.0
        self._is_zero_set = True

        try:
            self._ch.addParameter("zero", "laser", self._zero_laser)
            self._ch.updateFile(self._config_file_path)
            self.statusAlert.emit(f"{self._zero_laser} set as Reference Zero at X={self._xtemp:.2f}, Y={self._ytemp:.2f}")
        except Exception as e:
            print(f"[LaserBridge] Failed to save zero: {e}")

        # Auto-switch to other laser
        next_laser = "Laser 2" if self._zero_laser == "Laser 1" else "Laser 1"
        self._selected_laser = next_laser
        self._update_current()

        self.laserChanged.emit()
        self.offsetChanged.emit()

    @Slot(str)
    def jogOffset(self, direction: str):
        """Jogs X or Y for offset calibration."""
        d = direction.lower()
        amt = self._offset_step
        if "minus" in d:
            amt = -amt

        axis = "X" if "x" in d else "Y"
        if self._serial.connected:
            self._serial.sendGcode("G91")
            self._serial.sendGcode(f"G1 F1000 {axis}{amt}")
            self._serial.sendGcode("M114")
        elif self._motion:
            self._motion.jog(direction)

    @Slot()
    def saveOffset(self):
        """
        Calculates xoffset = current_x - xtemp, yoffset = current_y - ytemp.
        Saves to config.ini [offset].
        """
        self.turnOff()
        curr_x = self._motion.xPos if self._motion else 0.0
        curr_y = self._motion.yPos if self._motion else 0.0

        self._x_offset = round(curr_x - self._xtemp, 3)
        self._y_offset = round(curr_y - self._ytemp, 3)
        self._offset_laser = self._selected_laser
        self._is_zero_set = False

        try:
            self._ch.addParameter("offset", "laser", self._offset_laser)
            self._ch.addParameter("offset", "xoffset", str(self._x_offset))
            self._ch.addParameter("offset", "yoffset", str(self._y_offset))
            self._ch.updateFile(self._config_file_path)
            self.statusAlert.emit(f"Offset saved for {self._offset_laser}: X={self._x_offset} mm, Y={self._y_offset} mm")
        except Exception as e:
            self.statusAlert.emit(f"Error saving offset to config: {e}")

        self.offsetChanged.emit()
