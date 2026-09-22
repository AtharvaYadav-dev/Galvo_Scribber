import serial
import serial.tools.list_ports
import threading
from enum import Enum, auto

class SerialConfigError(Enum):
    NONE = auto()
    PORT_AND_BAUD_INVALID = auto()
    PORT_INVALID = auto()
    BAUD_INVALID = auto()


class SerialCom:
    def __init__(self):
        self.port = None
        self.baudrate = None
        self.serial_connection = None
        self.read_thread = None
        self.is_connected = False

        # Thread stop flag
        self._stop_event = threading.Event()

        # Callbacks (UI connects these)
        self.response_callback = None
        self.exception_callback = None
        
        self._error_table = {
            (False, False) : SerialConfigError.PORT_AND_BAUD_INVALID,
            (False, True) : SerialConfigError.PORT_INVALID,
            (True, False) : SerialConfigError.BAUD_INVALID,
            (True, True) : SerialConfigError.NONE
        }

    def configCallbacks(self, responseCallback=None, exceptionCallback=None):
        self.response_callback = responseCallback
        self.exception_callback = exceptionCallback

    def getPorts(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def getBaudrates(self):
        return ["9600", "57600", "115200", "250000"]

    def validatePort(self, port):
        return port in self.getPorts()

    def validateBaudrate(self, baudrate):
        try:
            int(baudrate)
            return True
        except ValueError:
            return False
        
    def validateConfig(self, port, baud):
        vport = self.validatePort(port)
        vbaud = self.validateBaudrate(baud)
        
        key = (vport is True, vbaud is True)
        return self._error_table[key]

    def connect(self):
        if not self.port or not self.baudrate:
            if self.exception_callback:
                self.exception_callback("Port or baudrate not set")
            return

        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=int(self.baudrate),
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected = True
            self._stop_event.clear()

            #  Start background read thread
            self.read_thread = threading.Thread(target=self.readloop, daemon=True)
            self.read_thread.start()

        except Exception as e:
            if self.exception_callback:
                self._emit_exception(e)

    def disconnect(self):
        try:
            self._stop_event.set()
            if self.read_thread and self.read_thread.is_alive() and threading.current_thread() != self.read_thread:
                self.read_thread.join(timeout=1)

            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()

        except Exception as e:
            if self.exception_callback:
                self._emit_exception(e)

        finally:
            self.serial_connection = None
            self.is_connected = False

    def send(self, gcode_str):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                if not gcode_str.endswith('\n'):
                    gcode_str += '\n'
                self.serial_connection.write(gcode_str.encode('utf-8'))
            except Exception as e:
                if self.exception_callback:
                    self._emit_exception(e)

    def readloop(self):
        try:
            while not self._stop_event.is_set() and self.serial_connection and self.serial_connection.is_open:
                try:
                    line = self.serial_connection.readline().decode(errors="ignore").strip()
                    if line and self.response_callback:
                        self.response_callback(line)
                        print(f"response : {line}")
                except Exception as e:
                    if self._stop_event.is_set():
                        break  # normal exit on disconnect
                    if self.exception_callback:
                        self._emit_exception(e)
                    break
        finally:
            self.serial_connection = None
            self.is_connected = False

    #  helper: always stringify exception before sending to UI
    def _emit_exception(self, e):
        try:
            msg = str(e) if not isinstance(e, str) else e
            self.exception_callback(msg)
        except Exception:
            pass
