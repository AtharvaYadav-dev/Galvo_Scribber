import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from main_qml import ThemeManager

def test_red_hatch():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    galvo_bridge = GalvoBridge()
    jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
    serial_bridge = SerialBridge()
    cad_bridge = CadBridge(galvo_bridge=galvo_bridge, jog_bridge=jog_bridge)
    camera_bridge = CameraBridge()
    settings_bridge = SettingsBridge(cad_bridge=cad_bridge)
    matrix_bridge = MatrixBridge(galvo_bridge=galvo_bridge)
    theme_manager = ThemeManager()

    engine = QQmlApplicationEngine()
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)
    root_context.setContextProperty("settings", settings_bridge)
    root_context.setContextProperty("matrix", matrix_bridge)
    root_context.setContextProperty("matrixBridge", matrix_bridge)
    root_context.setContextProperty("appLogoUrl", "")
    root_context.setContextProperty("themeManager", theme_manager)

    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    app.processEvents()

    # Create a red shape (penId = 2)
    red_circle = {
        "id": 1,
        "name": "Circle_1",
        "type": "circle",
        "xMm": 0.0,
        "yMm": 0.0,
        "wMm": 30.0,
        "hMm": 30.0,
        "penId": 2, # Pen 2 = Red
        "hatched": True,
        "visible": True,
        "locked": False
    }

    # Compute hatch lines
    lines = cad_bridge.computeHatchPreviewLines(red_circle)
    print(f"Generated {len(lines)} hatch lines for red circle.")
    assert len(lines) > 0, "Hatch lines should be generated"

    # Check pen_id on hatch lines
    pen_ids = set(l.get("pen_id") for l in lines)
    print(f"Hatch lines pen_ids: {pen_ids}")
    assert 2 in pen_ids, f"Expected hatch lines to inherit Pen 2 (Red), got {pen_ids}"

    # Get Pen colors from Theme / CadBridge
    pens = cad_bridge.getPens()
    pen2_color = [p["color"] for p in pens if p["id"] == 2][0]
    pen0_color = [p["color"] for p in pens if p["id"] == 0][0]
    print(f"Pen 2 color: {pen2_color}")
    print(f"Pen 0 color: {pen0_color}")

    assert pen2_color == "#EF4444", f"Pen 2 should be Red #EF4444, got {pen2_color}"
    assert pen0_color != "#000000", f"Pen 0 should NOT be pure black #000000! Got {pen0_color}"

    print("\n=======================================================")
    print(" RED PEN HATCHING COLOR VERIFIED: 100% SUCCESS!")
    print("=======================================================")
    return True

if __name__ == "__main__":
    success = test_red_hatch()
    sys.exit(0 if success else 1)

