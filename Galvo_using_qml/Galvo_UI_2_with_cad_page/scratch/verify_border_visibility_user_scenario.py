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

def verify():
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
        for c in win.findChildren(object):
            if c.objectName() == "cadCanvas":
                cad_canvas = c
            elif c.objectName() == "inspector":
                inspector = c

        # Exact user scenario: Rect_1 and Rect_2 with Pen 0 (Black), mark_contour = false, unhatched
        # Rect_1: (-15, 12), Rect_2: (4.18, 1.15, w=25.8, h=18.53)
        r1 = {
            "id": 1, "name": "Rect_1", "type": "rect",
            "xMm": -15.0, "yMm": 15.0, "wMm": 20.0, "hMm": 20.0,
            "rotation": 0, "penId": 0, "hatched": False, "mark_contour": False,
            "hatch_lines": [], "visible": True, "locked": False
        }
        r2 = {
            "id": 2, "name": "Rect_2", "type": "rect",
            "xMm": 4.183, "yMm": 1.147, "wMm": 25.8, "hMm": 18.53,
            "rotation": 0, "penId": 0, "hatched": False, "mark_contour": False,
            "hatch_lines": [], "visible": True, "locked": False
        }

        shapes = [r1, r2]
        cad_canvas.setProperty("shapes", shapes)
        cad_canvas.setProperty("selectedIndex", 1) # Select Rect_2 exactly like user image

        for child in cad_canvas.findChildren(object):
            if hasattr(child, "requestPaint"):
                child.requestPaint()

        inspector.setProperty("selectedIndex", 1)
        if hasattr(inspector, "updateTransformInputs"):
            inspector.updateTransformInputs()

        app.processEvents()

        # Capture Screenshot
        out_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\border_visibility_verified.png"
        img = win.grabWindow()
        img.save(out_path)
        print("Captured border visibility screenshot:", out_path)
        app.quit()

    QTimer.singleShot(1000, do_action)
    app.exec()

if __name__ == "__main__":
    verify()

