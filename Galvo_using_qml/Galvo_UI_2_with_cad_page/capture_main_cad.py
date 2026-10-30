import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtCore import QUrl, QTimer, QMetaObject
from PySide6.QtGui import QFontDatabase

def main():
    _dir = os.path.dirname(os.path.abspath(__file__))
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
        print("Failed to load")
        sys.exit(1)

    win = engine.rootObjects()[0]
    win.show()

    def capture_dark():
        img = win.grabWindow()
        out_dark = os.path.join(_dir, "qml", "cad_integrated_dark.png")
        img.save(out_dark)
        print(f"Saved: {out_dark}")

        # Toggle to Light mode
        QMetaObject.invokeMethod(win, "toggleTheme") if hasattr(win, "toggleTheme") else None
        # Toggle Theme singleton directly
        engine.evaluate = getattr(engine, "evaluate", None)
        from PySide6.QtQml import QQmlComponent
        QTimer.singleShot(600, capture_light)

    def capture_light():
        # Call toggleTheme on Theme
        img = win.grabWindow()
        out_light = os.path.join(_dir, "qml", "cad_integrated_light.png")
        img.save(out_light)
        print(f"Saved: {out_light}")
        app.quit()

    QTimer.singleShot(800, capture_dark)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
