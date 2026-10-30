import os
import sys

_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

os.environ["QSG_RENDER_LOOP"] = "basic"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtQuickControls2 import QQuickStyle

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    QQuickStyle.setStyle("Basic")
    app.setApplicationName("Galvo CAD Studio")

    # Load Material Icons font
    font_path = os.path.join(_app_dir, "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        fid = QFontDatabase.addApplicationFont(font_path)
        if fid != -1:
            print(f"[CAD Studio] Loaded vector icon font: {QFontDatabase.applicationFontFamilies(fid)}")

    engine = QQmlApplicationEngine()
    engine.addImportPath(_app_dir)

    main_qml = os.path.join(_app_dir, "main_window.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("[CAD Studio] Error: Failed to load main_window.qml")
        sys.exit(-1)

    print("[CAD Studio] Successfully initialized Next-Gen CAD Studio!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
