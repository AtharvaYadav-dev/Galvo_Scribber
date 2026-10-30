import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QTimer
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtGui import QPainter, QImage
from PySide6.QtQuick import QQuickWindow
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge

def capture():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)

    galvo = GalvoBridge()
    cad = CadBridge(galvo_bridge=galvo)

    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_app_dir, "qml"))
    engine.rootContext().setContextProperty("cad", cad)

    comp = QQmlComponent(engine, os.path.join(_app_dir, "qml", "views", "CadView.qml"))
    view = comp.create()

    canvas = view.findChild(QObject, "cadCanvas")
    inspector = view.findChild(QObject, "inspector")
    combo = inspector.findChild(QObject, "fontFamilyCombo")

    t_shape = {
        "id": 1, "name": "Text_1", "type": "text", "text": "EZCAD VECTOR",
        "xMm": 0.0, "yMm": 0.0, "wMm": 45.0, "hMm": 6.0,
        "fontFamily": "Segoe UI", "rotation": 0, "penId": 0,
        "hatched": False, "visible": True, "locked": False
    }
    canvas.setProperty("shapes", [t_shape])
    canvas.setProperty("selectedIndex", 0)

    # Filter with 'ari'
    combo.setProperty("searchFilter", "ari")

    win = QQuickWindow()
    view.setParentItem(win.contentItem())
    win.setGeometry(100, 100, 1100, 750)
    win.show()

    def do_capture():
        img = win.grabWindow()
        out_path = os.path.join(_app_dir, "scratch", "searchable_font_verified.png")
        img.save(out_path)
        print("Screenshot saved to:", out_path)
        app.quit()

    QTimer.singleShot(500, do_capture)
    app.exec()

if __name__ == "__main__":
    capture()

