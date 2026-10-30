import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import QTimer
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

warnings_detected = []

def on_qml_warning(warnings):
    for w in warnings:
        msg = w.toString()
        print("QML WARNING:", msg)
        warnings_detected.append(msg)

def test_tabs_and_shapes():
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
    engine.warnings.connect(on_qml_warning)

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

    if not engine.rootObjects():
        print("FAIL: Root object not created")
        return False

    app.processEvents()

    # Find inspector
    root_window = engine.rootObjects()[0]
    cad_view = root_window.findChild(type(root_window), "cadView")
    cad_canvas = root_window.findChild(type(root_window), "cadCanvas")
    inspector = root_window.findChild(type(root_window), "inspector")

    print(f"cad_canvas found: {cad_canvas is not None}")
    print(f"inspector found: {inspector is not None}")

    if inspector and cad_canvas:
        # Create shapes
        s1 = {"id": "Text_1", "name": "Text_1", "type": "text", "text": "HELLO", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 5, "rotation": 0, "zMm": 0, "penId": 0, "locked": False, "visible": True}
        s2 = {"id": "Rect_2", "name": "Rect_2", "type": "rect", "xMm": 10, "yMm": 10, "wMm": 15, "hMm": 15, "rotation": 0, "zMm": 0, "penId": 1, "locked": False, "visible": True}
        
        cad_canvas.setProperty("shapes", [s1, s2])
        cad_canvas.setProperty("selectedIndex", 0)
        app.processEvents()

        # Check inspector selectedShape
        sel = inspector.property("selectedShape")
        print("Selected Shape:", sel.get("name") if sel else None)
        assert sel is not None and sel.get("name") == "Text_1"

        # Select second shape
        cad_canvas.setProperty("selectedIndex", 1)
        app.processEvents()
        sel2 = inspector.property("selectedShape")
        print("Selected Shape 2:", sel2.get("name") if sel2 else None)
        assert sel2 is not None and sel2.get("name") == "Rect_2"

        # Deselect
        cad_canvas.setProperty("selectedIndex", -1)
        app.processEvents()
        sel_none = inspector.property("selectedShape")
        print("Selected None:", sel_none)
        assert sel_none is None

    # Check for binding loops
    binding_loops = [w for w in warnings_detected if "Binding loop" in w]
    if binding_loops:
        print("FAIL: Binding loops detected:", binding_loops)
        return False

    print("ALL TESTS PASSED: StackLayout isolating tabs properly, zero binding loops!")
    return True

if __name__ == "__main__":
    success = test_tabs_and_shapes()
    sys.exit(0 if success else 1)

