import math
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PySide6.QtQuick import QQuickImageProvider
from camera_thread import CameraThread
from pygrabber.dshow_graph import FilterGraph

class CameraImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        # Default placeholder image
        self._image = QImage(640, 480, QImage.Format_RGB888)
        self._image.fill(QColor(20, 22, 28))

    def update_image(self, img: QImage):
        self._image = img

    def requestImage(self, id_str, size, requested_size):
        return self._image


class CameraBridge(QObject):
    devicesChanged = Signal()
    streamingChanged = Signal(bool)
    frameReady = Signal(int)
    errorOccurred = Signal(str)
    selectedDeviceIndexChanged = Signal(int)
    reticleChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_provider = CameraImageProvider()
        self._thread = None
        self._devices = []
        self._selected_device_index = 0
        self._is_streaming = False
        self._frame_id = 0
        self._demo_mode = False
        self._demo_timer = QTimer(self)
        self._demo_timer.timeout.connect(self._render_demo_frame)
        self._demo_angle = 0.0

        self._show_reticle = True
        self._reticle_size = 50

        # Defer DirectShow device enumeration to avoid blocking GUI first paint
        self._devices = ["Simulator Camera (Test Pattern)"]
        QTimer.singleShot(150, self.refreshDevices)

    @property
    def image_provider(self):
        return self._image_provider

    # --- Properties ---
    @Property(list, notify=devicesChanged)
    def devices(self):
        return self._devices

    @Property(int, notify=selectedDeviceIndexChanged)
    def selectedDeviceIndex(self):
        return self._selected_device_index

    @selectedDeviceIndex.setter
    def selectedDeviceIndex(self, idx: int):
        if self._selected_device_index != idx:
            self._selected_device_index = idx
            self.selectedDeviceIndexChanged.emit(idx)

    @Property(bool, notify=streamingChanged)
    def isStreaming(self):
        return self._is_streaming

    @Property(int, notify=frameReady)
    def frameId(self):
        return self._frame_id

    @Property(bool, notify=reticleChanged)
    def showReticle(self):
        return self._show_reticle

    @showReticle.setter
    def showReticle(self, val: bool):
        if self._show_reticle != val:
            self._show_reticle = val
            self.reticleChanged.emit()

    @Property(int, notify=reticleChanged)
    def reticleSize(self):
        return self._reticle_size

    @reticleSize.setter
    def reticleSize(self, val: int):
        if self._reticle_size != val:
            self._reticle_size = val
            self.reticleChanged.emit()

    # --- Slots ---
    @Slot()
    def refreshDevices(self):
        try:
            devs = FilterGraph().get_input_devices()
            self._devices = devs if devs else ["Simulator Camera (Test Pattern)"]
        except Exception:
            self._devices = ["Simulator Camera (Test Pattern)"]
        self.devicesChanged.emit()

    @Slot(int)
    def startCamera(self, index: int = -1):
        if self._is_streaming:
            self.stopCamera()

        if index >= 0:
            self._selected_device_index = index

        # Check if real camera or demo
        dev_name = self._devices[self._selected_device_index] if self._selected_device_index < len(self._devices) else ""
        if "Simulator" in dev_name or not dev_name:
            self._demo_mode = True
            self._is_streaming = True
            self._demo_timer.start(33)  # ~30 FPS
            self.streamingChanged.emit(True)
            return

        # Real hardware camera
        try:
            self._demo_mode = False
            self._thread = CameraThread(self._selected_device_index, device_name=dev_name)
            self._thread.frame_update.connect(self._on_frame_received)
            self._thread.error_occurred.connect(self._on_camera_error)
            self._thread.start()
            self._is_streaming = True
            self.streamingChanged.emit(True)
        except Exception as e:
            self.errorOccurred.emit(f"Failed to start camera: {e}")
            self._is_streaming = False
            self.streamingChanged.emit(False)

    @Slot()
    def stopCamera(self):
        if self._demo_mode:
            self._demo_timer.stop()
            self._demo_mode = False
        elif self._thread:
            self._thread.stop()
            self._thread = None

        self._is_streaming = False
        self.streamingChanged.emit(False)

    def _on_frame_received(self, img: QImage):
        self._image_provider.update_image(img)
        self._frame_id += 1
        self.frameReady.emit(self._frame_id)

    def _on_camera_error(self, err_msg: str):
        self.errorOccurred.emit(err_msg)
        self.stopCamera()

    def _render_demo_frame(self):
        """Generates dynamic 30 FPS CAD alignment demo feed when hardware camera isn't attached."""
        w, h = 640, 480
        img = QImage(w, h, QImage.Format_RGB888)
        img.fill(QColor(18, 20, 26))

        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)

        # Draw grid
        p.setPen(QPen(QColor(35, 40, 52), 1))
        step = 40
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)

        cx, cy = w // 2, h // 2

        # Draw animated sample alignment target
        self._demo_angle += 0.03
        r = 90
        p.setPen(QPen(QColor(0, 229, 255, 120), 2))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Concentric rings
        p.setPen(QPen(QColor(0, 229, 255, 60), 1))
        p.drawEllipse(cx - 45, cy - 45, 90, 90)

        # Simulated fiducial target
        p.setPen(QPen(QColor(255, 145, 0), 2))
        p.drawRect(cx - 15, cy - 15, 30, 30)

        # Crosshairs
        p.setPen(QPen(QColor(255, 50, 70), 1))
        p.drawLine(cx - 60, cy, cx + 60, cy)
        p.drawLine(cx, cy - 60, cx, cy + 60)

        # Text banner
        p.setPen(QColor(140, 150, 170))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(20, 30, "CAMERA FEED — 640x480 @ 30 FPS (SIMULATOR RETICLE)")
        p.drawText(20, 50, f"Target Lock: Center ({cx}, {cy})")
        p.end()

        self._image_provider.update_image(img)
        self._frame_id += 1
        self.frameReady.emit(self._frame_id)
