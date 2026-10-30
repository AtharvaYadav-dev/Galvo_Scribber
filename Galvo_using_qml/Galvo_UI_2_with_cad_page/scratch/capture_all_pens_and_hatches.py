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

def capture():
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
        tab_group = None
        for c in win.findChildren(object):
            if c.objectName() == "cadCanvas":
                cad_canvas = c
            elif c.objectName() == "inspector":
                inspector = c
            elif c.objectName() == "inspectorTabGroup":
                tab_group = c

        # 4 shapes with different pens:
        # s1: Pen 0 (Black)
        s1 = {"id": 1, "name": "Pen0_Black", "type": "rect", "xMm": -18.0, "yMm": 14.0, "wMm": 16.0, "hMm": 16.0, "rotation": 0, "penId": 0, "hatched": True, "visible": True, "locked": False}
        # s2: Pen 1 (Blue)
        s2 = {"id": 2, "name": "Pen1_Blue", "type": "rect", "xMm": 18.0, "yMm": 14.0, "wMm": 16.0, "hMm": 16.0, "rotation": 0, "penId": 1, "hatched": True, "visible": True, "locked": False}
        # s3: Pen 2 (Red)
        s3 = {"id": 3, "name": "Pen2_Red", "type": "rect", "xMm": -18.0, "yMm": -14.0, "wMm": 16.0, "hMm": 16.0, "rotation": 0, "penId": 2, "hatched": True, "visible": True, "locked": False}
        # s4: Pen 3 (Green)
        s4 = {"id": 4, "name": "Pen3_Green", "type": "circle", "xMm": 18.0, "yMm": -14.0, "wMm": 16.0, "hMm": 16.0, "rotation": 0, "penId": 3, "hatched": True, "visible": True, "locked": False}

        s1["hatch_lines"] = cad_bridge.computeHatchPreviewLines(s1)
        s2["hatch_lines"] = cad_bridge.computeHatchPreviewLines(s2)
        s3["hatch_lines"] = cad_bridge.computeHatchPreviewLines(s3)
        s4["hatch_lines"] = cad_bridge.computeHatchPreviewLines(s4)

        shapes = [s1, s2, s3, s4]
        if cad_canvas:
            cad_canvas.setProperty("shapes", shapes)
            cad_canvas.setProperty("selectedIndex", 2) # Select Pen 2 (Red) shape
            for child in cad_canvas.findChildren(object):
                if hasattr(child, "requestPaint"):
                    child.requestPaint()

        if inspector:
            inspector.setProperty("selectedIndex", 2)
            if hasattr(inspector, "updateTransformInputs"):
                inspector.updateTransformInputs()

        # Switch to Laser Pens & Process tab
        if tab_group:
            tab_group.setProperty("currentIndex", 1)

        app.processEvents()

        out_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\pen_sync_and_hatch_verified.png"
        img = win.grabWindow()
        img.save(out_path)
        print("Verification screenshot saved to:", out_path)
        app.quit()

    QTimer.singleShot(1000, do_action)
    app.exec()

if __name__ == "__main__":
    capture()
