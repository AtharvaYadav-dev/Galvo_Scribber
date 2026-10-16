import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property

# Ensure project root is in sys.path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from machine.galvo_controller import GalvoController


class GalvoBridge(QObject):
    """
    QObject Bridge connecting GalvoController (DLL / Mock) to the QML Interface.
    Exposes reactive properties and callable slots for laser & galvo operations.
    """
    connectionChanged = Signal(bool, bool, str)  # is_connected, is_demo, status_text
    statusMessageChanged = Signal(str)
    parametersChanged = Signal()
    laserStateChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = GalvoController()
        self._is_connected = False
        self._is_demo = True
        self._status_message = "Ready (Not Connected)"
        self._power = 20.0        # % (0 - 100)
        self._speed = 1000.0      # mm/s
        self._frequency = 30.0    # kHz (20 - 80)
        self._is_firing = False
        self._red_pointer_on = False

    # ---------------- Properties for QML ---------------- #

    def get_is_connected(self) -> bool:
        return self._is_connected

    def get_is_demo(self) -> bool:
        return self._is_demo

    def get_status_message(self) -> str:
        return self._status_message

    def get_power(self) -> float:
        return self._power

    def get_speed(self) -> float:
        return self._speed

    def get_frequency(self) -> float:
        return self._frequency

    def get_is_firing(self) -> bool:
        return self._is_firing

    def get_red_pointer(self) -> bool:
        return self._red_pointer_on

    isConnected = Property(bool, get_is_connected, notify=connectionChanged)
    isDemo = Property(bool, get_is_demo, notify=connectionChanged)
    statusMessage = Property(str, get_status_message, notify=statusMessageChanged)
    power = Property(float, get_power, notify=parametersChanged)
    speed = Property(float, get_speed, notify=parametersChanged)
    frequency = Property(float, get_frequency, notify=parametersChanged)
    isLaserFiring = Property(bool, get_is_firing, notify=laserStateChanged)
    redPointerOn = Property(bool, get_red_pointer, notify=parametersChanged)

    # ---------------- Slots Invoked from QML ---------------- #

    @Slot()
    def connectHardware(self):
        """Attempts connection to physical Galvo hardware (fallback to Simulator)."""
        self.setStatus("Connecting to Galvo controller...")
        try:
            connected = self.controller.connect(force_mock=False)
            self._is_connected = True
            if connected:
                self._is_demo = False
                self.setStatus("Connected to Hardware Galvo")
            else:
                self._is_demo = True
                self.setStatus("Running in Simulation / Demo Mode")
            
            # Auto home on connect
            self.controller.galvo_home()
        except Exception as e:
            self._is_connected = False
            self._is_demo = True
            self.setStatus(f"Connection Error: {e}")

        self.connectionChanged.emit(self._is_connected, self._is_demo, self._status_message)

    @Slot()
    def disconnectHardware(self):
        """Safely shuts off laser and disconnects from controller."""
        try:
            self.controller.disconnect()
            self._is_connected = False
            self._is_demo = True
            self.setStatus("Disconnected")
        except Exception as e:
            self.setStatus(f"Disconnect Error: {e}")

        self.connectionChanged.emit(self._is_connected, self._is_demo, self._status_message)

    @Slot()
    def homeGalvo(self):
        """Homes the galvanometer mirror positions to center (32767, 32767)."""
        if not self.controller:
            self.setStatus("Cannot home: Controller not initialized")
            return
        try:
            self.setStatus("Homing Galvo mirrors...")
            self.controller.galvo_home()
            self.setStatus("Galvo Centered (Home)")
        except Exception as e:
            self.setStatus(f"Homing failed: {e}")

    @Slot()
    def toggleRedPointer(self):
        """Toggles the guide red pointer on/off."""
        if not self.controller.connection:
            self.setStatus("Controller connection unavailable")
            return
        try:
            self._red_pointer_on = not self._red_pointer_on
            if self._red_pointer_on:
                if hasattr(self.controller.connection, 'reddot_on'):
                    self.controller.connection.reddot_on()
                self.setStatus("Red Pointer ON")
            else:
                if hasattr(self.controller.connection, 'reddot_off'):
                    self.controller.connection.reddot_off()
                self.setStatus("Red Pointer OFF")
            self.parametersChanged.emit()
        except Exception as e:
            self.setStatus(f"Red pointer error: {e}")

    @Slot()
    def testPattern(self):
        """Runs a safe test square pattern."""
        try:
            self._is_firing = True
            self.laserStateChanged.emit(True)
            self.setStatus("Marking Test Pattern...")
            self.controller.test_pattern()
            self.setStatus("Test Pattern Finished")
        except Exception as e:
            self.setStatus(f"Test pattern error: {e}")
        finally:
            self._is_firing = False
            self.laserStateChanged.emit(False)

    @Slot()
    def emergencyStop(self):
        """Immediate laser shutdown and abort."""
        try:
            if self.controller.connection and hasattr(self.controller.connection, 'laser_off'):
                self.controller.connection.laser_off()
            self._is_firing = False
            self.laserStateChanged.emit(False)
            self.setStatus("EMERGENCY STOP TRIGGERED - Laser is OFF")
        except Exception as e:
            self.setStatus(f"Emergency stop error: {e}")

    @Slot(float)
    def setPower(self, val: float):
        self._power = max(1.0, min(100.0, float(val)))
        self.parametersChanged.emit()

    @Slot(float)
    def setSpeed(self, val: float):
        self._speed = max(10.0, min(10000.0, float(val)))
        self.parametersChanged.emit()

    @Slot(float)
    def setFrequency(self, val: float):
        self._frequency = max(20.0, min(80.0, float(val)))
        self.parametersChanged.emit()

    def setStatus(self, msg: str):
        self._status_message = str(msg)
        self.statusMessageChanged.emit(self._status_message)
        print(f"[GalvoBridge] {msg}")
