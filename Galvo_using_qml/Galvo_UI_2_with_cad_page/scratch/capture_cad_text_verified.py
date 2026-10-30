import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl, QTimer, QMetaObject
from bridges.cad_bridge import CadBridge
from bridges.jog_bridge import JogBridge

app = QApplication.instance() or QApplication(sys.argv)

view = QQuickView()
view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
view.setWidth(1360)
view.setHeight(850)

cad = CadBridge()
jog = JogBridge()

ctx = view.rootContext()
ctx.setContextProperty("cad", cad)
ctx.setContextProperty("jog", jog)

qml_path = os.path.join(_root, "qml", "views", "CadView.qml")
view.setSource(QUrl.fromLocalFile(qml_path))
view.show()

def add_text_step():
    root = view.rootObject()
    if root:
        QMetaObject.invokeMethod(root, "createDefaultText")
        print("Invoked createDefaultText() on CadView root.")

def save_step():
    save_path = os.path.join(_root, "scratch", "cad_text_selected_verified.png")
    img = view.grabWindow()
    img.save(save_path)
    print(f"Captured screenshot to {save_path}")
    view.close()
    app.quit()

QTimer.singleShot(1500, add_text_step)
QTimer.singleShot(3500, save_step)

sys.exit(app.exec())
