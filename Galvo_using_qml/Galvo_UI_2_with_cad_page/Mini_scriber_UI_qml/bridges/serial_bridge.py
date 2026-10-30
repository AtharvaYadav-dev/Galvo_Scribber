import os
import sys
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer, Qt
from com import SerialCom, SerialConfigError
from util import ConfigHandler

class SerialBridge(QObject):
    connectedChanged = Signal(bool)
    portsChanged = Signal()
    portSelected = Signal(str)
    baudSelected = Signal(str)
    responseReceived = Signal(str)
    errorOccurred = Signal(str)
    statusMessage = Signal(str)
    autoConnectRequested = Signal(str, str)
    autoConnectFailed = Signal(str)
    autoConnectCancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._com = SerialCom()
        self._com.configCallbacks(
            responseCallback=self._on_response,
            exceptionCallback=self._on_exception
        )
        self._ports = []
        self._baudrates = ["9600", "57600", "115200", "250000"]
        self._selected_port = ""
        self._selected_baud = "115200"
        self._saved_port = ""
        self._saved_baud = "115200"
        self._listeners = []

        # Config file path
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_file_path = os.path.join(app_dir, "config", "config.ini")
        self._ch = ConfigHandler()

        self._init_saved_config()
        # Defer COM port bus scan by 100ms so window appears immediately
        QTimer.singleShot(100, self.refreshPorts)

    def _read_saved_config(self):
        """Reads saved COM port & baudrate from config.ini ([main] then [com])."""
        port, baud = "", "115200"
        if not os.path.exists(self._config_file_path):
            return port, baud
        try:
            self._ch.ini_parser.read(self._config_file_path)
            # Try [main] section first (as main.py did for maincom)
            p = self._ch.getValues("main", "port")
            b = self._ch.getValues("main", "baudrate")
            if not p or not b:
                # Fallback to [com] section
                p = self._ch.getValues("com", "port")
                b = self._ch.getValues("com", "baudrate")
            if p: port = p.strip()
            if b: baud = b.strip()
        except Exception as e:
            print(f"[SerialBridge] Error reading COM config: {e}")
        return port, baud

    def _save_com_config(self, port: str, baud: str):
        """Saves current COM port & baudrate to config.ini for next startup auto-connect."""
        if not os.path.exists(self._config_file_path):
            return
        try:
            self._ch.ini_parser.read(self._config_file_path)
            self._ch.addParameter("main", "port", str(port))
            self._ch.addParameter("main", "baudrate", str(baud))
            self._ch.addParameter("com", "port", str(port))
            self._ch.addParameter("com", "baudrate", str(baud))
            self._ch.updateFile(self._config_file_path)
        except Exception as e:
            print(f"[SerialBridge] Error saving COM config: {e}")

    def _init_saved_config(self):
        port, baud = self._read_saved_config()
        self._saved_port = port
        self._saved_baud = baud
        if port:
            self._selected_port = port
            self.portSelected.emit(port)
        if baud:
            self._selected_baud = baud
            self.baudSelected.emit(baud)

    def add_response_listener(self, callback):
        try:
            self.responseReceived.connect(callback, Qt.QueuedConnection)
        except Exception:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def remove_response_listener(self, callback):
        try:
            self.responseReceived.disconnect(callback)
        except Exception:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def _on_response(self, text: str):
        self.responseReceived.emit(text)
        for cb in self._listeners:
            try:
                cb(text)
            except Exception as e:
                print(f"[SerialBridge listener error]: {e}")

    def _on_exception(self, err: str):
        self.errorOccurred.emit(str(err))
        self.statusMessage.emit(f"Serial Error: {err}")
        self.connectedChanged.emit(False)

    # --- Properties ---
    @Property(bool, notify=connectedChanged)
    def connected(self):
        return bool(self._com.is_connected)

    @Property(list, notify=portsChanged)
    def ports(self):
        return self._ports

    @Property(list, constant=True)
    def baudrates(self):
        return self._baudrates

    @Property(str, notify=portSelected)
    def selectedPort(self):
        return self._selected_port

    @selectedPort.setter
    def selectedPort(self, port_name: str):
        if self._selected_port != port_name:
            self._selected_port = port_name
            self.portSelected.emit(port_name)

    @Property(str, notify=baudSelected)
    def selectedBaud(self):
        return self._selected_baud

    @selectedBaud.setter
    def selectedBaud(self, baud: str):
        if self._selected_baud != baud:
            self._selected_baud = baud
            self.baudSelected.emit(baud)

    @Property(str, notify=portSelected)
    def savedPort(self):
        return self._saved_port

    @Property(str, notify=baudSelected)
    def savedBaud(self):
        return self._saved_baud

    # --- Slots ---
    @Slot()
    def refreshPorts(self):
        self._ports = self._com.getPorts()
        if self._ports and not self._selected_port:
            self._selected_port = self._ports[0]
            self.portSelected.emit(self._selected_port)
        self.portsChanged.emit()

    @Slot()
    def checkAutoConnect(self):
        """Checks config.ini and available ports for startup auto-connection prompt matching main.py."""
        self.refreshPorts()
        port, baud = self._read_saved_config()
        self._saved_port = port
        self._saved_baud = baud

        if not port or not baud or getattr(self, "_auto_connect_rejected", False):
            return

        err = self._com.validateConfig(port, baud)
        if err == SerialConfigError.NONE:
            print(f"[SerialBridge] Auto-connect candidate available: {port} @ {baud}")
            self.autoConnectRequested.emit(port, baud)
        else:
            msg = f"COM Port Auto-Connection failed: Saved port {port} is not available. Kindly perform manual COM port configuration!"
            print(f"[SerialBridge] {msg}")
            self.autoConnectFailed.emit(msg)

    @Slot()
    def acceptAutoConnect(self):
        """Accepts auto-connect dialog: connects to saved port and auto-homes machine (G28)."""
        if not self._saved_port or not self._saved_baud:
            return
        self._selected_port = self._saved_port
        self._selected_baud = self._saved_baud
        self.portSelected.emit(self._selected_port)
        self.baudSelected.emit(self._selected_baud)

        self._com.port = self._selected_port
        self._com.baudrate = self._selected_baud
        self._com.connect()

        is_conn = bool(self._com.is_connected)
        self.connectedChanged.emit(is_conn)
        if is_conn:
            msg = f"Auto-connected to {self._selected_port} @ {self._selected_baud}. Auto-homing (G28)..."
            print(f"[SerialBridge] {msg}")
            self.statusMessage.emit(msg)
            # Matching main.py: auto-home on connect
            self.sendGcode("G28")
            self.sendGcode("M114")
            self._save_com_config(self._selected_port, self._selected_baud)
        else:
            err_msg = f"Failed to connect to {self._selected_port}"
            print(f"[SerialBridge] {err_msg}")
            self.statusMessage.emit(err_msg)
            self.errorOccurred.emit(err_msg)

    @Slot()
    def rejectAutoConnect(self):
        """Rejects auto-connect dialog to allow manual configuration."""
        self._auto_connect_rejected = True
        msg = "Auto-connection cancelled. Controller is in manual configuration mode."
        print(f"[SerialBridge] {msg}")
        self.statusMessage.emit(msg)
        self.autoConnectCancelled.emit()

    @Slot(result=bool)
    def connectSerial(self):
        if not self._selected_port or not self._selected_baud:
            self.errorOccurred.emit("Please select both a COM port and baudrate.")
            return False

        self._com.port = self._selected_port
        self._com.baudrate = self._selected_baud
        self._com.connect()
        
        is_conn = bool(self._com.is_connected)
        self.connectedChanged.emit(is_conn)
        if is_conn:
            self.statusMessage.emit(f"Connected to {self._selected_port} @ {self._selected_baud}")
            self.sendGcode("M114")
            self._save_com_config(self._selected_port, self._selected_baud)
        else:
            msg = f"Failed to connect to {self._selected_port}."
            self.statusMessage.emit(msg)
            self.errorOccurred.emit(f"{msg} Please verify the USB connection or select an available COM port in Settings.")
        return is_conn

    @Slot()
    def disconnectSerial(self):
        if self._com.is_connected:
            try:
                # Ensure lasers and spindle are off before closing COM connection
                self._com.send("M106 P0 S0\n")
                self._com.send("M106 P1 S0\n")
                self._com.send("M5\n")
                if self._com.serial_connection:
                    self._com.serial_connection.flush()
            except Exception as e:
                print(f"[SerialBridge] Laser shutdown on disconnect notice: {e}")
        self._com.disconnect()
        self.connectedChanged.emit(False)
        self.statusMessage.emit("Disconnected")

    @Slot(str)
    def sendGcode(self, cmd: str):
        if not cmd:
            return
        cmd = cmd.strip()
        if self._com.is_connected:
            self._com.send(cmd)
        else:
            self.errorOccurred.emit("Cannot send: Serial not connected")
