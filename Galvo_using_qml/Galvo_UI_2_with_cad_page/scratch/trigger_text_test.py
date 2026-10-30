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

def trigger_text():
    root = view.rootObject()
    # Find toolbox and trigger textTriggered signal
    tb = root.findChild(object, "cadToolbox")
    # Alternatively find CadInspectorPanel or invoke method
    root.metaObject().invokeMethod(root, "addTextFromScript") if hasattr(root, "addTextFromScript") else None

def save_frame():
    save_path = os.path.join(_root, "scratch", "cad_view_text_verified.png")
    img = view.grabWindow()
    img.save(save_path)
    print(f"Saved snapshot to: {save_path}")
    view.close()
    app.quit()

# Add a function on CadView for testing or direct QML execution
