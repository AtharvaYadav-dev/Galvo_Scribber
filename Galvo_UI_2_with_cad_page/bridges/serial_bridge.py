import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from com import SerialCom


class SerialBridge(QObject):
    """
    QObject Bridge for Serial COM communication (Microcontroller / Blackpill).
    """
    portsChanged = Signal(list)
    connectionStatusChanged = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.com = SerialCom()
        self._is_connected = False
        self._current_port = ""
        self._current_baud = "115200"
        self._ports = []
        self.refreshPorts()

    def get_ports(self) -> list:
        return self._ports

    def get_is_connected(self) -> bool:
        return self._is_connected

    ports = Property(list, get_ports, notify=portsChanged)
    isConnected = Property(bool, get_is_connected, notify=connectionStatusChanged)

    @Slot()
    def refreshPorts(self):
        try:
            self._ports = self.com.getPorts()
        except Exception:
            self._ports = []
        self.portsChanged.emit(self._ports)

    @Slot(str, str)
    def connectPort(self, port: str, baud: str = "115200"):
        if not port:
            self.connectionStatusChanged.emit(False, "Select a valid COM port")
            return
        try:
            # Here you can connect via self.com.connect(...) if configured
            self._current_port = port
            self._current_baud = baud
            self._is_connected = True
            self.connectionStatusChanged.emit(True, f"Connected to {port} @ {baud}")
        except Exception as e:
            self._is_connected = False
            self.connectionStatusChanged.emit(False, str(e))

    @Slot()
    def disconnectPort(self):
        self._is_connected = False
        self.connectionStatusChanged.emit(False, "Disconnected from COM")
