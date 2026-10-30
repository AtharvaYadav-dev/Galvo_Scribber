import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl, QTimer, QMetaObject
from PySide6.QtGui import QFontDatabase
from bridges.cad_bridge import CadBridge
from bridges.jog_bridge import JogBridge

app = QApplication.instance() or QApplication(sys.argv)

font_path = os.path.join(_root, "qml", "fonts", "MaterialIcons-Regular.ttf")
if os.path.exists(font_path):
    QFontDatabase.addApplicationFont(font_path)

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

def add_shapes():
    root = view.rootObject()
    if root:
        QMetaObject.invokeMethod(root, "createDefaultText")

def capture():
    save_path = os.path.join(_root, "scratch", "cad_inspector_verified.png")
    img = view.grabWindow()
    img.save(save_path)
    print(f"Captured screenshot to {save_path}")
    view.close()
    app.quit()

QTimer.singleShot(1000, add_shapes)
QTimer.singleShot(2500, capture)

sys.exit(app.exec())
