import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtQuick import QQuickPaintedItem

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from camera_thread import CameraThread


class CameraVideoItem(QQuickPaintedItem):
    """
    High-performance QQuickPaintedItem rendering live 25-30 FPS camera video in QML.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderTarget(QQuickPaintedItem.RenderTarget.FramebufferObject)
        self._current_frame = None

    def update_frame(self, qimg: QImage):
        # Keep a copy of the frame to draw
        self._current_frame = qimg.copy()
        self.update()

    def paint(self, painter: QPainter):
        if self._current_frame and not self._current_frame.isNull():
            painter.drawImage(self.boundingRect(), self._current_frame)
        else:
            # Draw placeholder when camera is stopped
            painter.fillRect(self.boundingRect(), Qt.black)
            painter.setPen(Qt.gray)
            painter.drawText(self.boundingRect(), Qt.AlignCenter, "CAMERA OFFLINE / STANDBY")


class CameraBridge(QObject):
    """
    QObject Bridge for Vision / Optical Camera inspection and alignment.
    """
    cameraStateChanged = Signal(bool, str) # is_running, message
    devicesChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cam_thread = None
        self._is_running = False
        self._devices = []
        self._video_item = None
        self.refreshDevices()

    def set_video_item(self, item: CameraVideoItem):
        self._video_item = item

    def get_is_running(self) -> bool:
        return self._is_running

    def get_devices(self) -> list:
        return self._devices

    isRunning = Property(bool, get_is_running, notify=cameraStateChanged)
    devices = Property(list, get_devices, notify=devicesChanged)

    @Slot(QObject)
    def registerVideoItem(self, item):
        """Allows QML CameraVideoItem to register itself directly."""
        self._video_item = item

    @Slot()
    def refreshDevices(self):
        try:
            from pygrabber.dshow_graph import FilterGraph
            self._devices = FilterGraph().get_input_devices()
        except Exception:
            self._devices = ["Default USB Camera (0)"]
        self.devicesChanged.emit(self._devices)

    @Slot(int)
    def startCamera(self, cam_index: int = 0):
        if self._is_running:
            self.stopCamera()

        try:
            dev_name = self._devices[cam_index] if cam_index < len(self._devices) else "Default Camera"
            self.cam_thread = CameraThread(cam_index=cam_index, device_name=dev_name)
            self.cam_thread.frame_update.connect(self._on_frame)
            self.cam_thread.error_occurred.connect(self._on_error)
            self.cam_thread.start()
            self._is_running = True
            self.cameraStateChanged.emit(True, f"Camera [{dev_name}] Started")
        except Exception as e:
            self._is_running = False
            self.cameraStateChanged.emit(False, f"Failed to start camera: {e}")

    @Slot()
    def stopCamera(self):
        if self.cam_thread:
            try:
                self.cam_thread.stop()
            except Exception:
                pass
            self.cam_thread = None

        self._is_running = False
        self.cameraStateChanged.emit(False, "Camera Stopped")

    def _on_frame(self, qimg: QImage):
        if self._video_item:
            self._video_item.update_frame(qimg)

    def _on_error(self, err_msg: str):
        self._is_running = False
        self.cameraStateChanged.emit(False, err_msg)
