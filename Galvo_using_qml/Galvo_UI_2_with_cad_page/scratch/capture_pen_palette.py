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

def capture_ui():
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

    if not engine.rootObjects():
        print("FAIL: Root object not created")
        return False

    win = engine.rootObjects()[0]
    win.show()

    def do_actions():
        # Switch to Tab 1 (Laser Pens & Process)
        inspector = win.findChild(type(win), "inspector")
        cad_view = win.findChild(type(win), "cadView")
        
        # Trigger openColorPicker on inspector
        app.processEvents()

        # Save screenshot
        out_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\pen_palette_verified.png"
        img = win.grabWindow()
        img.save(out_path)
        print("Screenshot saved to:", out_path)
        app.quit()

    QTimer.singleShot(1000, do_actions)
    app.exec()
    return True

if __name__ == "__main__":
    capture_ui()

