import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl, QTimer
from bridges.cad_bridge import CadBridge
from bridges.jog_bridge import JogBridge

app = QApplication.instance() or QApplication(sys.argv)

view = QQuickView()
view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
view.setWidth(1280)
view.setHeight(800)

cad = CadBridge()
jog = JogBridge()

ctx = view.rootContext()
ctx.setContextProperty("cad", cad)
ctx.setContextProperty("jog", jog)

qml_path = os.path.join(_root, "qml", "views", "CadView.qml")
view.setSource(QUrl.fromLocalFile(qml_path))
view.show()

def setup_text():
    root = view.rootObject()
    # Trigger text creation on toolbox
    toolbox = root.findChild(object, "toolbox") or root
    # Add a text shape directly to cadCanvas
    canvas = root.findChild(object, "cadCanvas")
    if canvas:
        m = cad.measureText("TEXT", "Segoe UI", 4.0, False, False)
        text_shp = {
            "id": 1,
            "name": "Text_1",
            "type": "text",
            "text": "TEXT",
            "xMm": 0.0,
            "yMm": 0.0,
            "wMm": m.get("wMm", 12.15),
            "hMm": 4.0,
            "rotation": 0,
            "fontFamily": "Segoe UI",
            "fontType": "TrueType Font",
            "textAlign": "center",
            "charSpace": 0.0,
            "lineSpace": 0.0,
            "bold": False,
            "italic": False,
            "penId": 0,
            "hatched": False,
            "visible": True,
            "locked": False
        }
        canvas.setProperty("shapes", [text_shp])
        canvas.setProperty("selectedIndex", 0)
        print("Text shape injected and selected.")

def save_frame():
    save_path = os.path.join(_root, "scratch", "cad_view_text_verified.png")
    img = view.grabWindow()
    img.save(save_path)
    print(f"Saved snapshot to: {save_path}")
    view.close()
    app.quit()

QTimer.singleShot(1500, setup_text)
QTimer.singleShot(3000, save_frame)

sys.exit(app.exec())
