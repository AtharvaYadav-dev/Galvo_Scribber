import os
import sys
from PySide6.QtCore import QPointF, QPoint, Qt, QTimer
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

os.chdir(r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
sys.path.insert(0, r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from bridges.calibration_bridge import CalibrationBridge

app = QApplication.instance() or QApplication(sys.argv)
engine = QQmlApplicationEngine()

galvo_bridge = GalvoBridge()
jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
serial_bridge = SerialBridge()
cad_bridge = CadBridge(galvo_bridge=galvo_bridge, jog_bridge=jog_bridge)
camera_bridge = CameraBridge()
settings_bridge = SettingsBridge(cad_bridge=cad_bridge)
matrix_bridge = MatrixBridge(galvo_bridge=galvo_bridge)
calibration_bridge = CalibrationBridge(galvo_bridge=galvo_bridge, settings_bridge=settings_bridge)

root_context = engine.rootContext()
root_context.setContextProperty("galvo", galvo_bridge)
root_context.setContextProperty("jog", jog_bridge)
root_context.setContextProperty("serial", serial_bridge)
root_context.setContextProperty("cad", cad_bridge)
root_context.setContextProperty("camera", camera_bridge)
root_context.setContextProperty("settings", settings_bridge)
root_context.setContextProperty("matrix", matrix_bridge)
root_context.setContextProperty("matrixBridge", matrix_bridge)
root_context.setContextProperty("calibration", calibration_bridge)
root_context.setContextProperty("calibrationBridge", calibration_bridge)
root_context.setContextProperty("appLogoUrl", "")

qml_dir = os.path.join(os.getcwd(), "qml")
engine.addImportPath(qml_dir)
engine.load(os.path.join(qml_dir, "main.qml"))

if not engine.rootObjects():
    print("FAILED to load main.qml")
    sys.exit(1)

win = engine.rootObjects()[0]
win.show()

cad_canvas = win.findChild(object, "cadCanvas")
cor_modal = win.findChild(object, "corCalibrationModal")

def test_isolation():
    initial_zoom = cad_canvas.property("zoomScale")
    initial_pan_x = cad_canvas.property("panOffsetX")
    initial_pan_y = cad_canvas.property("panOffsetY")
    print(f"[TEST] Initial CAD Canvas State: zoom={initial_zoom:.4f}, pan=({initial_pan_x:.1f}, {initial_pan_y:.1f})")

    # 1. Open the modal
    cor_modal.open()
    print("[TEST] Modal opened. modal.opacity:", cor_modal.property("opacity"), "window.isAnyModalOpen:", win.property("isAnyModalOpen"))
    print("[TEST] cadCanvas.interactionBlocked:", cad_canvas.property("interactionBlocked"))

    assert cad_canvas.property("interactionBlocked") == True, "cadCanvas.interactionBlocked should be True!"

    # 2. Simulate mouse wheel scrolling in center of window (over modal)
    center_pos = QPointF(win.width() / 2, win.height() / 2)
    wheel_event = QWheelEvent(
        center_pos,
        center_pos,
        QPoint(0, 0),
        QPoint(0, 120),  # Scroll up
        Qt.NoButton,
        Qt.NoModifier,
        Qt.ScrollUpdate,
        False
    )
    QApplication.sendEvent(win, wheel_event)
    app.processEvents()

    # 3. Simulate wheel event near edge (over modal backdrop)
    edge_pos = QPointF(50, 50)
    wheel_event_edge = QWheelEvent(
        edge_pos,
        edge_pos,
        QPoint(0, 0),
        QPoint(0, -120), # Scroll down
        Qt.NoButton,
        Qt.NoModifier,
        Qt.ScrollUpdate,
        False
    )
    QApplication.sendEvent(win, wheel_event_edge)
    app.processEvents()

    # Verify zoom and pan have NOT changed at all!
    current_zoom = cad_canvas.property("zoomScale")
    current_pan_x = cad_canvas.property("panOffsetX")
    current_pan_y = cad_canvas.property("panOffsetY")
    print(f"[TEST] Post-scroll CAD Canvas State: zoom={current_zoom:.4f}, pan=({current_pan_x:.1f}, {current_pan_y:.1f})")

    assert current_zoom == initial_zoom, f"Zoom changed from {initial_zoom} to {current_zoom}!"
    assert current_pan_x == initial_pan_x, f"Pan X changed from {initial_pan_x} to {current_pan_x}!"
    assert current_pan_y == initial_pan_y, f"Pan Y changed from {initial_pan_y} to {current_pan_y}!"

    print("[TEST] SUCCESS! Background CAD canvas was completely unaffected by scrolling!")
    app.quit()

QTimer.singleShot(500, test_isolation)
app.exec()

