import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtCore import QUrl, QTimer, QMetaObject
from PySide6.QtGui import QFontDatabase

def main():
    _dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _dir not in sys.path:
        sys.path.insert(0, _dir)
    os.environ["QSG_RENDER_LOOP"] = "basic"
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)

    font_path = os.path.join(_dir, "qml", "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    from bridges.galvo_bridge import GalvoBridge
    from bridges.jog_bridge import JogBridge
    from bridges.serial_bridge import SerialBridge
    from bridges.cad_bridge import CadBridge
    from bridges.camera_bridge import CameraBridge, CameraVideoItem

    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    galvo = GalvoBridge()
    jog = JogBridge(galvo_bridge=galvo)
    serial = SerialBridge()
    cad = CadBridge(galvo_bridge=galvo)
    camera = CameraBridge()

    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_dir, "qml"))

    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo)
    root_context.setContextProperty("jog", jog)
    root_context.setContextProperty("serial", serial)
    root_context.setContextProperty("cad", cad)
    root_context.setContextProperty("camera", camera)

    main_qml = os.path.join(_dir, "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(main_qml))
    if not engine.rootObjects():
        sys.exit(1)

    win = engine.rootObjects()[0]
    win.show()

    def open_modal_dark():
        jog_modal = None
        for child in win.children():
            if child.property("title") == "Z-Axis Stepper & Focal Calibration":
                jog_modal = child
                break
        if jog_modal:
            jog_modal.open()
        QTimer.singleShot(600, capture_dark)

    def capture_dark():
        img = win.grabWindow()
        out_path = os.path.join(_dir, "qml", "jog_dark_preview.png")
        img.save(out_path)
        print(f"Saved: {out_path}")
        win.toggleTheme()
        QTimer.singleShot(600, capture_light)

    def capture_light():
        img = win.grabWindow()
        out_path = os.path.join(_dir, "qml", "jog_light_preview.png")
        img.save(out_path)
        print(f"Saved: {out_path}")
        app.quit()

    QTimer.singleShot(500, open_modal_dark)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
