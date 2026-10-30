import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path: sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QTimer
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQuick import QQuickWindow
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge

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

# Try to find what font and text causes this
# Let's test AMS Vasudeva with various texts or Marathi fonts
t_shape = {
    "id": 1, "name": "Text_1", "type": "text", "text": "मराठी",
    "xMm": 0.0, "yMm": 0.0, "wMm": 15.0, "hMm": 15.0,
    "fontFamily": "AMS Vasudeva", "rotation": 0, "penId": 0,
    "hatched": False, "visible": True, "locked": False
}
canvas.setProperty("shapes", [t_shape])
canvas.setProperty("selectedIndex", 0)

win = QQuickWindow()
view.setParentItem(win.contentItem())
win.setGeometry(100, 100, 1000, 700)
win.show()

def do_capture():
    img = win.grabWindow()
    out = os.path.join(_app_dir, "scratch", "debug_marathi_box.png")
    img.save(out)
    print("Saved debug_marathi_box.png")
    app.quit()

QTimer.singleShot(400, do_capture)
app.exec()

