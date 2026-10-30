import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QTimer, QMetaObject
from PySide6.QtGui import QFontDatabase

def main():
    _dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["QSG_RENDER_LOOP"] = "basic"
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)

    font_path = os.path.join(_dir, "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    engine = QQmlApplicationEngine()
    engine.addImportPath(_dir)

    main_qml = os.path.join(_dir, "main_window.qml")
    engine.load(QUrl.fromLocalFile(main_qml))
    if not engine.rootObjects():
        print("Failed to load")
        sys.exit(1)

    win = engine.rootObjects()[0]
    win.show()

    def capture_dark():
        img = win.grabWindow()
        out_dark = os.path.join(_dir, "cad_dark_mode_preview.png")
        img.save(out_dark)
        print(f"Saved: {out_dark}")

        # Invoke toggleTheme on root object
        QMetaObject.invokeMethod(win, "toggleTheme")
        QTimer.singleShot(600, capture_light)

    def capture_light():
        img = win.grabWindow()
        out_light = os.path.join(_dir, "cad_light_mode_preview.png")
        img.save(out_light)
        print(f"Saved: {out_light}")
        app.quit()

    QTimer.singleShot(800, capture_dark)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
