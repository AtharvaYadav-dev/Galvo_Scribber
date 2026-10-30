import os
import sys
import time

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem

def run_test():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    
    font_path = os.path.join(_app_dir, "qml", "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    galvo_bridge = GalvoBridge()
    jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
    serial_bridge = SerialBridge()
    cad_bridge = CadBridge(galvo_bridge=galvo_bridge)
    camera_bridge = CameraBridge()

    engine = QQmlApplicationEngine()
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)

    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    if not engine.rootObjects():
        print("ERROR: Could not load main.qml")
        sys.exit(1)

    win = engine.rootObjects()[0]
    win.show()

    def capture_and_exit():
        # Capture direct rendered framebuffer
        img = win.grabWindow()
        out_path = os.path.join(qml_dir, "cad_backend_integrated_preview.png")
        img.save(out_path)
        print(f"Captured screenshot to: {out_path}")
        app.quit()

    QTimer.singleShot(1500, capture_and_exit)
    app.exec()

if __name__ == "__main__":
    run_test()
