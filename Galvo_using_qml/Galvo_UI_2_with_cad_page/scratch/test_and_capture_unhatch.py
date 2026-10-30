import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
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

def test_unhatch():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)

    font_path = os.path.join(_app_dir, "qml", "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

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

    win = engine.rootObjects()[0]
    win.show()

    def do_action():
        cad_canvas = None
        inspector = None
        topbar = None
        for c in win.findChildren(object):
            if c.objectName() == "cadCanvas":
                cad_canvas = c
            elif c.objectName() == "inspector":
                inspector = c
            elif c.objectName() == "topCommandBar":
                topbar = c

        assert cad_canvas is not None, "cadCanvas must be found"
        assert inspector is not None, "inspector must be found"
        assert topbar is not None, "topCommandBar must be found"

        # Create a hatched red rectangle
        s1 = {"id": 1, "name": "Red_Workpiece", "type": "rect", "xMm": 0.0, "yMm": 0.0, "wMm": 30.0, "hMm": 20.0, "rotation": 0, "penId": 2, "hatched": True, "visible": True, "locked": False}
        s1["hatch_lines"] = cad_bridge.computeHatchPreviewLines(s1)

        cad_canvas.setProperty("shapes", [s1])
        cad_canvas.setProperty("selectedIndex", 0)

        for child in cad_canvas.findChildren(object):
            if hasattr(child, "requestPaint"):
                child.requestPaint()

        inspector.setProperty("selectedIndex", 0)
        if hasattr(inspector, "updateTransformInputs"):
            inspector.updateTransformInputs()

        app.processEvents()

        # Capture Screenshot 1: Hatched State
        out_hatched = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\unhatch_option_visible.png"
        img1 = win.grabWindow()
        img1.save(out_hatched)
        print("Captured hatched state screenshot:", out_hatched)

        # Verify Unhatch Action
        print("Testing unhatchSelectedShape()...")
        cad_canvas.unhatchSelectedShape()
        app.processEvents()

        shapes_prop = cad_canvas.property("shapes")
        shapes_after = shapes_prop.toVariant() if hasattr(shapes_prop, "toVariant") else shapes_prop
        assert len(shapes_after) == 1, "Shape must still exist"
        assert shapes_after[0]["hatched"] is False, "Shape must be unhatched"
        assert len(shapes_after[0]["hatch_lines"]) == 0, "Hatch lines must be cleared"
        print("Unhatch verified: hatched=False, hatch_lines cleared!")

        # Capture Screenshot 2: Unhatched State
        out_unhatched = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\unhatch_action_verified.png"
        img2 = win.grabWindow()
        img2.save(out_unhatched)
        print("Captured unhatched state screenshot:", out_unhatched)

        # Test Undo
        print("Testing undo()...")
        cad_canvas.undo()
        app.processEvents()
        shapes_prop2 = cad_canvas.property("shapes")
        shapes_undo = shapes_prop2.toVariant() if hasattr(shapes_prop2, "toVariant") else shapes_prop2
        assert shapes_undo[0]["hatched"] is True, "Undo must restore hatched=True"
        print("Undo verified: hatched restored to True!")

        print("\n=======================================================")
        print(" ALL UNHATCH OPTIONS & FUNCTIONALITY VERIFIED: 100% SUCCESS!")
        print("=======================================================")
        app.quit()

    QTimer.singleShot(1000, do_action)
    app.exec()

if __name__ == "__main__":
    test_unhatch()
