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
    cardDetected = Signal(int, str)  # card_count, card_description
    autoConnectDismissed = Signal()
    hardwareAlert = Signal(str, str)  # title, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = GalvoController()
        self._is_connected = False
        self._is_demo = True
        self._status_message = "Ready (Not Connected)"
        self._power = 20.0        # % (0 - 100)
        self._speed = 1000.0      # mm/s (Marking Speed)
        self._jump_speed = 2000.0 # mm/s (Jump Speed)
        self._frequency = 30.0    # kHz (20 - 80)
        self._is_firing = False
        self._red_pointer_on = False
        self._detected_hw = None
        self._is_detecting = False

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

    def get_jump_speed(self) -> float:
        return self._jump_speed

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
    jumpSpeed = Property(float, get_jump_speed, notify=parametersChanged)
    frequency = Property(float, get_frequency, notify=parametersChanged)
    isLaserFiring = Property(bool, get_is_firing, notify=laserStateChanged)
    redPointerOn = Property(bool, get_red_pointer, notify=parametersChanged)

    # ---------------- Asynchronous Card Detection ---------------- #

    @Slot()
    def startCardDetection(self):
        """Asynchronously probes for physical Galvo hardware card without blocking the UI."""
        if self._is_connected or self._is_detecting:
            return
        self._is_detecting = True
        import threading
        t = threading.Thread(target=self._detect_worker, daemon=True)
        t.start()

    def _detect_worker(self):
        try:
            from core.connection.hardware import HardwareConnection
            hw = HardwareConnection()
            res, cards = hw.initialize()
            if hw.is_initialized and cards > 0:
                self._detected_hw = hw
                print(f"[GalvoBridge] Hardware card detected: {cards} card(s) found.")
                self.cardDetected.emit(cards, "GoogolTech Galvo Controller (GT-U3 / GT-500)")
            else:
                if hw.is_initialized:
                    try:
                        hw.close()
                    except Exception:
                        pass
                print("[GalvoBridge] No physical hardware card found.")
        except Exception as e:
            print(f"[GalvoBridge] Card detection probe error: {e}")
        finally:
            self._is_detecting = False

    @Slot()
    def acceptAutoConnect(self):
        """User accepted auto-connect prompt; immediately connects hardware."""
        self.connectHardware()

    @Slot()
    def rejectAutoConnect(self):
        """User declined auto-connect; releases probed card and stays in Demo Mode."""
        if self._detected_hw:
            try:
                self._detected_hw.close()
            except Exception:
                pass
            self._detected_hw = None
        self._is_connected = False
        self._is_demo = True
        self.setStatus("Simulation Mode (Auto-Connect Declined)")
        self.connectionChanged.emit(self._is_connected, self._is_demo, self._status_message)
        self.autoConnectDismissed.emit()

    # ---------------- Slots Invoked from QML ---------------- #

    @Slot()
    def connectHardware(self):
        """Attempts connection to physical Galvo hardware (fallback to Simulator)."""
        self.setStatus("Connecting to Galvo controller...")
        try:
            if self._detected_hw and self._detected_hw.is_initialized:
                self.controller.connection = self._detected_hw
                self.controller.is_connected = True
                self._detected_hw = None
                self._is_connected = True
                self._is_demo = False
                self.setStatus("Connected to Hardware Galvo")
                try:
                    self.controller.galvo_home()
                except Exception:
                    pass
            else:
                connected = self.controller.connect(force_mock=False)
                self._is_connected = True
                if connected:
                    self._is_demo = False
                    self.setStatus("Connected to Hardware Galvo")
                    self.controller.galvo_home()
                    self.apply_laser_power_and_freq(self._power, self._frequency)
                else:
                    self._is_demo = True
                    self.setStatus("Simulation Mode — Demo Version Only for Evaluation")
                    self.hardwareAlert.emit("Simulator Mode", "Could not find Galvo hardware card.\nRunning in Simulation Mode — Demo Version Only for Evaluation.")
        except Exception as e:
            self._is_connected = False
            self._is_demo = True
            self.setStatus(f"Connection Error: {e}")
            self.hardwareAlert.emit("Connection Error", f"Failed to connect to Galvo card: {e}")

        self.connectionChanged.emit(self._is_connected, self._is_demo, self._status_message)

    @Slot()
    def disconnectHardware(self):
        """Safely shuts off laser and disconnects from controller."""
        try:
            if self._detected_hw:
                try:
                    self._detected_hw.close()
                except Exception:
                    pass
                self._detected_hw = None
            self.controller.disconnect()
            self._is_connected = False
            self._is_demo = True
            self.setStatus("Disconnected (Simulation Mode)")
            self.hardwareAlert.emit("Disconnected", "Galvo controller disconnected.")
        except Exception as e:
            self.setStatus(f"Disconnect Error: {e}")

        self.connectionChanged.emit(self._is_connected, self._is_demo, self._status_message)

    @Slot()
    def homeGalvo(self):
        """Homes the galvanometer mirror positions to center (32767, 32767)."""
        if self._is_demo or not self._is_connected:
            self.hardwareAlert.emit("Hardware Disconnected", "Ensure hardware is connected before moving axis.")
            return
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
    def turnRedPointerOn(self):
        """Turns on the red guide pointer."""
        if not self._is_connected and not self._is_demo:
            self.hardwareAlert.emit("Hardware Disconnected", "Ensure hardware is connected before operating reddot laser.")
            return
        try:
            if self.controller.connection and hasattr(self.controller.connection, 'reddot_on'):
                self.controller.connection.reddot_on()
            self._red_pointer_on = True
            self.parametersChanged.emit()
            self.setStatus("Red Pointer ON")
        except Exception as e:
            self.setStatus(f"Red pointer ON error: {e}")

    @Slot()
    def turnRedPointerOff(self):
        """Turns off the red guide pointer."""
        try:
            if self.controller.connection and hasattr(self.controller.connection, 'reddot_off'):
                self.controller.connection.reddot_off()
            self._red_pointer_on = False
            self.parametersChanged.emit()
            self.setStatus("Red Pointer OFF")
        except Exception as e:
            self.setStatus(f"Red pointer OFF error: {e}")

    @Slot()
    def toggleRedPointer(self):
        """Toggles the guide red pointer on/off."""
        if self._red_pointer_on:
            self.turnRedPointerOff()
        else:
            self.turnRedPointerOn()

    @Slot()
    def turnLaserOn(self):
        """Turns on main laser emission (DO1 = HIGH)."""
        if self._power <= 0:
            self.hardwareAlert.emit("Zero Power", "Cannot turn laser ON when power is set to 0%.")
            return
        try:
            self.apply_laser_power_and_freq(self._power, self._frequency)
            if self.controller.connection and hasattr(self.controller.connection, 'laser_on'):
                self.controller.connection.laser_on()
            self._is_firing = True
            self.laserStateChanged.emit(True)
            self.setStatus("Main Laser EMISSION ACTIVE (ON)")
        except Exception as e:
            self.setStatus(f"Laser ON error: {e}")

    @Slot()
    def turnLaserOff(self):
        """Turns off main laser emission (DO1 = LOW)."""
        try:
            if self.controller.connection and hasattr(self.controller.connection, 'laser_off'):
                self.controller.connection.laser_off()
            self._is_firing = False
            self.laserStateChanged.emit(False)
            self.setStatus("Main Laser Emission OFF")
        except Exception as e:
            self.setStatus(f"Laser OFF error: {e}")

    @Slot()
    def toggleMainLaser(self):
        """Toggles main laser emission on/off."""
        if self._is_firing:
            self.turnLaserOff()
        else:
            self.turnLaserOn()

    @Slot()
    def emergencyStop(self):
        """Immediate laser shutdown and abort."""
        try:
            if self.controller.connection:
                if hasattr(self.controller.connection, 'laser_off'):
                    self.controller.connection.laser_off()
                if hasattr(self.controller.connection, 'reddot_off'):
                    self.controller.connection.reddot_off()
                if hasattr(self.controller.connection, 'stop'):
                    self.controller.connection.stop()
            self._is_firing = False
            self._red_pointer_on = False
            self.laserStateChanged.emit(False)
            self.parametersChanged.emit()
            self.setStatus("EMERGENCY STOP TRIGGERED - All Lasers are OFF")
        except Exception as e:
            self.setStatus(f"Emergency stop error: {e}")

    def apply_laser_power_and_freq(self, power_val: float, freq_val: float):
        """
        Applies laser power and PRR frequency using the exact hardware math from main.py
        (lines 1980-2015 and 2846-2865).
        - Inverts power signal for Blackpill mapping (0V = 100%, 3.3V = 0%)
        - Converts 20kHz - 80kHz to 10% - 90% duty cycle on bit 0
        - Sets bits 2 & 3 for Blackpill power and frequency channels
        - Updates controller live_power and live_freq for dynamic thread injection
        """
        ctrl = self.controller
        if not ctrl:
            return

        power_val = max(0.0, min(100.0, float(power_val)))
        freq_val = max(20.0, min(80.0, float(freq_val)))

        ctrl.live_power = power_val
        ctrl.live_freq = freq_val

        conn = getattr(ctrl, 'connection', None)
        if conn and hasattr(conn, "set_analog_do_bit"):
            try:
                # 1. Analog Power (Bit 2)
                if power_val <= 0:
                    if hasattr(conn, 'laser_off'):
                        conn.laser_off()
                    conn.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                else:
                    mapped_power = (power_val / 100.0) * 255.0
                    conn.set_analog_do_bit(255.0, mapped_power, 50.0, 2)

                # 2. PRR Frequency (Bit 0 and Bit 3)
                safe_freq = conn.clamp_laser_freq(freq_val) if hasattr(conn, 'clamp_laser_freq') else freq_val

                # Convert 20kHz - 80kHz to 10% - 90% Duty Cycle for the Blackpill (bit 0)
                freq_duty_cycle = 10.0 + ((safe_freq - 20.0) / (80.0 - 20.0)) * 80.0
                freq_duty_cycle = max(10.0, min(90.0, freq_duty_cycle))
                conn.set_analog_do_bit(100.0, freq_duty_cycle, 50.0, 0)

                # Secondary pin compensation from main.py lines 2859-2861
                if hasattr(conn, 'map_laser_power'):
                    inv_pwr = conn.map_laser_power(power_val)
                else:
                    inv_pwr = 100.0 - power_val
                conn.set_analog_do_bit(100.0, inv_pwr, 50.0, 2)
                conn.set_analog_do_bit(100.0, 50.0, safe_freq / 4.0, 3)

                print(f"[GalvoBridge] Applied Laser Settings: Power={power_val}% | Freq={safe_freq}kHz (Duty Cycle={freq_duty_cycle:.1f}%)")
            except Exception as e:
                print(f"[GalvoBridge] Error applying laser power/freq: {e}")

    @Slot(float)
    def setPower(self, val: float):
        self._power = max(1.0, min(100.0, float(val)))
        self.parametersChanged.emit()
        self.apply_laser_power_and_freq(self._power, self._frequency)

    @Slot(float)
    def setSpeed(self, val: float):
        self._speed = max(10.0, min(10000.0, float(val)))
        self.parametersChanged.emit()

    @Slot(float)
    def setJumpSpeed(self, val: float):
        self._jump_speed = max(50.0, min(10000.0, float(val)))
        self.parametersChanged.emit()

    @Slot(float)
    def setFrequency(self, val: float):
        self._frequency = max(20.0, min(80.0, float(val)))
        self.parametersChanged.emit()
        self.apply_laser_power_and_freq(self._power, self._frequency)

    @Slot(float, float, float)
    def setParameters(self, pwr: float, spd: float, freq: float):
        self._power = max(1.0, min(100.0, float(pwr)))
        self._speed = max(10.0, min(10000.0, float(spd)))
        self._frequency = max(20.0, min(80.0, float(freq)))
        self.parametersChanged.emit()
        self.apply_laser_power_and_freq(self._power, self._frequency)

    def setStatus(self, msg: str):
        self._status_message = str(msg)
        self.statusMessageChanged.emit(self._status_message)
        print(f"[GalvoBridge] {msg}")
