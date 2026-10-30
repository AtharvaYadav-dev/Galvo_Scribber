import os
import sys
import time

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView, QQuickWindow
from PySide6.QtCore import QUrl, QTimer
from bridges.cad_bridge import CadBridge
from bridges.jog_bridge import JogBridge
from bridges.matrix_bridge import MatrixBridge
from bridges.settings_bridge import SettingsBridge
from bridges.galvo_bridge import GalvoBridge
from bridges.camera_bridge import CameraBridge

app = QApplication.instance() or QApplication(sys.argv)

view = QQuickView()
view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
view.setWidth(1280)
view.setHeight(800)

cad = CadBridge()
jog = JogBridge()
matrix = MatrixBridge()
settings = SettingsBridge()
galvo = GalvoBridge()
camera = CameraBridge()

ctx = view.rootContext()
ctx.setContextProperty("cad", cad)
ctx.setContextProperty("jog", jog)
ctx.setContextProperty("matrix", matrix)
ctx.setContextProperty("settings", settings)
ctx.setContextProperty("galvo", galvo)
ctx.setContextProperty("camera", camera)

qml_path = os.path.join(_root, "qml", "main.qml")
view.setSource(QUrl.fromLocalFile(qml_path))
view.show()

def on_step1():
    # Simulate clicking CAD view tab and adding text
    root = view.rootObject()
    print("Capturing initial view...")
    
def capture_and_quit():
    img = view.grabWindow()
    save_path = os.path.join(_root, "scratch", "cad_text_ui_verified.png")
    img.save(save_path)
    print(f"Captured screenshot to: {save_path}")
    view.close()
    app.quit()

QTimer.singleShot(1000, on_step1)
QTimer.singleShot(2500, capture_and_quit)
sys.exit(app.exec())
