import datetime
from PySide6.QtCore import QObject, Signal, Slot

class TerminalBridge(QObject):
    logAdded = Signal(str, str, str)  # timestamp, text, type ("rx", "tx", "err", "info")
    cleared = Signal()

    def __init__(self, serial_bridge, parent=None):
        super().__init__(parent)
        self._serial = serial_bridge
        self._serial.add_response_listener(self._on_rx)
        self._serial.errorOccurred.connect(self._on_err)
        self._serial.statusMessage.connect(self._on_info)

    def _now(self):
        return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def _on_rx(self, line: str):
        self.logAdded.emit(self._now(), line, "rx")

    def _on_err(self, err: str):
        self.logAdded.emit(self._now(), f"ERROR: {err}", "err")

    def _on_info(self, info: str):
        self.logAdded.emit(self._now(), f"INFO: {info}", "info")

    # --- Slots ---
    @Slot(str)
    def sendCommand(self, cmd: str):
        if not cmd:
            return
        cmd = cmd.strip()
        self.logAdded.emit(self._now(), f">> {cmd}", "tx")
        self._serial.sendGcode(cmd)

    @Slot()
    def clearLog(self):
        self.cleared.emit()
