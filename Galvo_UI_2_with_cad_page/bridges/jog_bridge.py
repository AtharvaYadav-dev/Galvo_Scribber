import sys
import os
import math
from configparser import ConfigParser
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtWidgets import QApplication

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from machine.stepper_controller import StepperController


class JogBridge(QObject):
    """
    QObject Bridge for Z-Axis & Focal Height Stepper Control, Focal Calibration,
    and Galvo Optical Centering.
    (XY motion is handled entirely by Galvo mirrors).
    """
    zPosChanged = Signal(float)
    focusConfigChanged = Signal(float, float, float, float) # base_focus, obj_height, sample_height, target_focus
    stepSizeChanged = Signal(float)
    motionStatusChanged = Signal(str)
    guideLaserChanged = Signal(bool, bool) # red_dot, laser_beam

    CONFIG_FILE = os.path.join(_root, "config", "config.ini")

    def __init__(self, galvo_bridge=None, parent=None):
        super().__init__(parent)
        self.galvo_bridge = galvo_bridge
        self.galvo_controller = galvo_bridge.controller if galvo_bridge else None

        # Connect StepperController using galvo's hardware connection
        conn = self.galvo_controller.connection if self.galvo_controller else None
        self.stepper = StepperController(conn)

        # Z state (limits: 0.0 to 120.0 mm)
        self._z = 27.0
        if self.stepper:
            self.stepper.z_position = self._z

        # Focus Calibration parameters (loaded from config.ini)
        self._base_focus_z = 27.0
        self._object_height = 0.0
        self._sample_height = 0.0
        self._target_focus_z = 27.0

        # Motion parameters
        self._step_size = 5.0     # Choices: 10.0, 5.0, 1.0, 0.1 mm
        self._feed_rate = 1000.0  # pulses/sec

        # Guide Lasers
        self._red_pointer = False
        self._guide_laser = False

        self._load_config()

    # ---------------- Properties for QML ---------------- #

    def get_z(self) -> float:
        return self._z

    def get_base_focus_z(self) -> float:
        return self._base_focus_z

    def get_object_height(self) -> float:
        return self._object_height

    def get_sample_height(self) -> float:
        return self._sample_height

    def get_target_focus_z(self) -> float:
        return self._target_focus_z

    def get_step_size(self) -> float:
        return self._step_size

    def get_red_pointer(self) -> bool:
        return self._red_pointer

    def get_guide_laser(self) -> bool:
        return self._guide_laser

    zPos = Property(float, get_z, notify=zPosChanged)
    baseFocusZ = Property(float, get_base_focus_z, notify=focusConfigChanged)
    objectHeight = Property(float, get_object_height, notify=focusConfigChanged)
    sampleHeight = Property(float, get_sample_height, notify=focusConfigChanged)
    targetFocusZ = Property(float, get_target_focus_z, notify=focusConfigChanged)
    stepSize = Property(float, get_step_size, notify=stepSizeChanged)
    redPointerOn = Property(bool, get_red_pointer, notify=guideLaserChanged)
    guideLaserOn = Property(bool, get_guide_laser, notify=guideLaserChanged)

    # ---------------- Focal Math & Configuration ---------------- #

    def _load_config(self):
        """Loads saved focal distances from config/config.ini."""
        if not os.path.exists(self.CONFIG_FILE):
            self._recalculate_target()
            return

        parser = ConfigParser()
        try:
            parser.read(self.CONFIG_FILE)
            if parser.has_section("focus"):
                self._base_focus_z = float(parser.get("focus", "galvo_z_focus", fallback="27.0"))
                self._object_height = float(parser.get("focus", "galvoobjheight", fallback="0.0"))
                self._sample_height = float(parser.get("focus", "galvosampleheight", fallback="0.0"))
                self._z = float(parser.get("focus", "finalgalvofocus", fallback=str(self._base_focus_z)))
                if self.stepper:
                    self.stepper.z_position = self._z
        except Exception as e:
            print(f"Error loading focus config: {e}")

        self._recalculate_target()

    def _recalculate_target(self):
        """Formula matching main.py: finalgalvofocus = (base_focus - object_height) + sample_height."""
        final_obj_focus = self._base_focus_z - self._object_height
        self._target_focus_z = max(0.0, min(120.0, final_obj_focus + self._sample_height))
        self.focusConfigChanged.emit(self._base_focus_z, self._object_height, self._sample_height, self._target_focus_z)

    def _save_config(self):
        """Saves updated focus parameters to config.ini."""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        parser = ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            parser.read(self.CONFIG_FILE)
        if not parser.has_section("focus"):
            parser.add_section("focus")

        parser.set("focus", "galvo_z_focus", f"{self._base_focus_z:.2f}")
        parser.set("focus", "galvoobjheight", f"{self._object_height:.2f}")
        parser.set("focus", "galvosampleheight", f"{self._sample_height:.2f}")
        parser.set("focus", "finalobjectfocus", f"{(self._base_focus_z - self._object_height):.2f}")
        parser.set("focus", "finalgalvofocus", f"{self._target_focus_z:.2f}")

        try:
            with open(self.CONFIG_FILE, "w") as f:
                parser.write(f)
        except Exception as e:
            print(f"Error saving config.ini: {e}")

    # ---------------- Slots for QML ---------------- #

    @Slot(int)
    def jogZ(self, direction: int):
        """
        Jogs Z axis relative by stepSize.
        direction: +1 (UP/Raise head) or -1 (DOWN/Lower head)
        Clamped between 0.0 and 120.0 mm.
        """
        delta = self._step_size * direction
        target_z = self._z + delta

        # Safety Limit Check
        if target_z > 120.0:
            delta = 120.0 - self._z
            self.motionStatusChanged.emit("Warning: Reached Z-Axis Upper Limit (120 mm)")
        elif target_z < 0.0:
            delta = 0.0 - self._z
            self.motionStatusChanged.emit("Warning: Reached Z-Axis Lower Limit (0 mm)")

        if abs(delta) < 0.001:
            return

        try:
            if self.stepper and getattr(self.stepper.connection, 'is_initialized', False):
                self.stepper.move_z_relative(delta, speed=int(self._feed_rate))
                self._z = self.stepper.z_position
            else:
                self._z += delta
                if self.stepper:
                    self.stepper.z_position = self._z

            self.motionStatusChanged.emit(f"Moved Z by {delta:+.2f} mm -> Height: {self._z:.3f} mm")
        except Exception as e:
            self.motionStatusChanged.emit(f"Z Move Error: {e}")

        self.zPosChanged.emit(self._z)

    @Slot(float)
    def moveToZ(self, target_mm: float):
        """Moves Z axis to an absolute millimeter height."""
        target_mm = max(0.0, min(120.0, float(target_mm)))
        try:
            if self.stepper and getattr(self.stepper.connection, 'is_initialized', False):
                self.stepper.move_z_absolute(target_mm, speed=int(self._feed_rate))
                self._z = self.stepper.z_position
            else:
                self._z = target_mm
                if self.stepper:
                    self.stepper.z_position = self._z

            self.motionStatusChanged.emit(f"Moved Z to absolute position {self._z:.3f} mm")
        except Exception as e:
            self.motionStatusChanged.emit(f"Move Error: {e}")

        self.zPosChanged.emit(self._z)

    @Slot()
    def moveToTargetFocus(self):
        """Automatically moves Z axis directly to the calculated workpiece target focus."""
        self.moveToZ(self._target_focus_z)
        self.motionStatusChanged.emit(f"Z aligned to Target Workpiece Focus: {self._target_focus_z:.2f} mm")

    @Slot()
    def setAsBaseFocus(self):
        """Saves current Z position as the calibrated base focal height."""
        self._base_focus_z = self._z
        self._recalculate_target()
        self._save_config()
        self.motionStatusChanged.emit(f"Saved Base Focal Plane at Z = {self._base_focus_z:.2f} mm")

    @Slot(float)
    def setObjectHeight(self, val: float):
        """Sets object / workpiece thickness in mm."""
        self._object_height = max(0.0, float(val))
        self._recalculate_target()
        self._save_config()
        self.motionStatusChanged.emit(f"Workpiece thickness set to {self._object_height:.2f} mm (Target Focus: {self._target_focus_z:.2f} mm)")

    @Slot(float)
    def setSampleHeight(self, val: float):
        """Sets sample / fixture height in mm."""
        self._sample_height = max(0.0, float(val))
        self._recalculate_target()
        self._save_config()
        self.motionStatusChanged.emit(f"Sample offset set to {self._sample_height:.2f} mm")

    @Slot()
    def homeZ(self):
        """Performs physical limit switch homing for the Z stepper axis."""
        self.motionStatusChanged.emit("Homing Z-Axis to physical limit switch...")
        try:
            if self.stepper and getattr(self.stepper.connection, 'is_initialized', False):
                app_inst = QApplication.instance()
                success = self.stepper.home_z(app_instance=app_inst)
                self._z = self.stepper.z_position
                if success:
                    self.motionStatusChanged.emit("Z-Axis limit switch homing complete (0.000 mm)")
                else:
                    self.motionStatusChanged.emit("Z-Axis homing failed: Limit switch not triggered")
            else:
                self._z = 0.0
                if self.stepper:
                    self.stepper.z_position = 0.0
                self.motionStatusChanged.emit("Z-Axis homed to 0.000 mm (Simulator Mode)")
        except Exception as e:
            self.motionStatusChanged.emit(f"Homing Error: {e}")

        self.zPosChanged.emit(self._z)

    @Slot()
    def homeGalvo(self):
        """Centers the optical Galvo mirrors to home position (32767, 32767)."""
        if self.galvo_controller:
            try:
                self.galvo_controller.galvo_home()
                self.motionStatusChanged.emit("Galvo Mirrors Centered at (0, 0)")
            except Exception as e:
                self.motionStatusChanged.emit(f"Galvo home error: {e}")

    @Slot()
    def homeAll(self):
        """Centers Galvo mirrors and homes the Z stepper axis."""
        self.homeGalvo()
        self.homeZ()
        self.motionStatusChanged.emit("Galvo Centered & Z-Axis Homed Successfully")

    @Slot(float)
    def setStepSize(self, val: float):
        self._step_size = float(val)
        self.stepSizeChanged.emit(self._step_size)
        self.motionStatusChanged.emit(f"Z Step Increment set to {self._step_size} mm")

    @Slot()
    def toggleRedPointer(self):
        """Toggles the guide red pointer diode on/off."""
        if not self.galvo_controller or not self.galvo_controller.connection:
            return
        conn = self.galvo_controller.connection
        self._red_pointer = not self._red_pointer
        try:
            if self._red_pointer and hasattr(conn, 'reddot_on'):
                conn.reddot_on()
                self.motionStatusChanged.emit("Red Guide Pointer: ON")
            elif hasattr(conn, 'reddot_off'):
                conn.reddot_off()
                self.motionStatusChanged.emit("Red Guide Pointer: OFF")
        except Exception as e:
            self.motionStatusChanged.emit(f"Red pointer error: {e}")

        self.guideLaserChanged.emit(self._red_pointer, self._guide_laser)

    @Slot()
    def toggleGuideLaser(self):
        """Toggles the laser focus beam (DO1) on/off for spot checking."""
        if not self.galvo_controller or not self.galvo_controller.connection:
            return
        conn = self.galvo_controller.connection
        self._guide_laser = not self._guide_laser
        try:
            if self._guide_laser and hasattr(conn, 'laser_on'):
                conn.laser_on()
                self.motionStatusChanged.emit("⚠️ Focus Laser Beam: ON")
            elif hasattr(conn, 'laser_off'):
                conn.laser_off()
                self.motionStatusChanged.emit("Focus Laser Beam: OFF")
        except Exception as e:
            self.motionStatusChanged.emit(f"Laser toggle error: {e}")

        self.guideLaserChanged.emit(self._red_pointer, self._guide_laser)

    @Slot(str)
    def fireQuickShape(self, shape_name: str):
        """Fires a quick test burn (circle, triangle, square) using the galvo mirrors."""
        if not self.galvo_controller:
            self.motionStatusChanged.emit("Controller unavailable")
            return

        shape_name = shape_name.lower()
        self.motionStatusChanged.emit(f"Firing quick test pattern: {shape_name.capitalize()}...")
        try:
            from core.motion_planner import MotionPlanner
            planner = MotionPlanner()
            half = 15.0 # 30x30 mm test shape
            scale = 655.35 # units per mm

            def g(val_mm):
                return int(32767 + (val_mm * scale))

            speed = 30000

            if shape_name == "square":
                planner.add_jump(g(-half), g(-half), speed)
                planner.add_mark(g(half), g(-half), speed)
                planner.add_mark(g(half), g(half), speed)
                planner.add_mark(g(-half), g(half), speed)
                planner.add_mark(g(-half), g(-half), speed)
            elif shape_name == "circle":
                for i in range(37):
                    a = math.radians(i * 10)
                    px = half * math.cos(a)
                    py = half * math.sin(a)
                    if i == 0:
                        planner.add_jump(g(px), g(py), speed)
                    else:
                        planner.add_mark(g(px), g(py), speed)
            elif shape_name == "triangle":
                planner.add_jump(g(0), g(half), speed)
                planner.add_mark(g(half), g(-half), speed)
                planner.add_mark(g(-half), g(-half), speed)
                planner.add_mark(g(0), g(half), speed)

            self.galvo_controller.execute_queue(planner.preview_queue, loop_count=1)
            self.galvo_controller.galvo_home()
            self.motionStatusChanged.emit(f"Quick {shape_name.capitalize()} burn complete")
        except Exception as e:
            self.motionStatusChanged.emit(f"Burn pattern error: {e}")
