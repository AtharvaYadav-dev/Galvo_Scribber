import os
import sys

os.chdir(r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
sys.path.insert(0, r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from bridges.calibration_bridge import CalibrationBridge

app = QApplication.instance() or QApplication(sys.argv)
engine = QQmlApplicationEngine()

galvo_bridge = GalvoBridge()
jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
serial_bridge = SerialBridge()
cad_bridge = CadBridge(galvo_bridge=galvo_bridge, jog_bridge=jog_bridge)
camera_bridge = CameraBridge()
settings_bridge = SettingsBridge(cad_bridge=cad_bridge)
matrix_bridge = MatrixBridge(galvo_bridge=galvo_bridge)
calibration_bridge = CalibrationBridge(galvo_bridge=galvo_bridge, settings_bridge=settings_bridge)

root_context = engine.rootContext()
root_context.setContextProperty("galvo", galvo_bridge)
root_context.setContextProperty("jog", jog_bridge)
root_context.setContextProperty("serial", serial_bridge)
root_context.setContextProperty("cad", cad_bridge)
root_context.setContextProperty("camera", camera_bridge)
root_context.setContextProperty("settings", settings_bridge)
root_context.setContextProperty("matrix", matrix_bridge)
root_context.setContextProperty("calibration", calibration_bridge)
root_context.setContextProperty("calibrationBridge", calibration_bridge)
root_context.setContextProperty("appLogoUrl", "")

qml_dir = os.path.join(os.getcwd(), "qml")
engine.addImportPath(qml_dir)
engine.load(os.path.join(qml_dir, "main.qml"))

win = engine.rootObjects()[0]
modal = win.findChild(object, "corCalibrationModal")
view = win.findChild(object, "corCalibrationView")

def dump(item, indent=0):
    w = item.property("width") if hasattr(item, "property") else "?"
    h = item.property("height") if hasattr(item, "property") else "?"
    x = item.property("x") if hasattr(item, "property") else "?"
    y = item.property("y") if hasattr(item, "property") else "?"
    vis = item.property("visible") if hasattr(item, "property") else "?"
    obj_name = item.objectName() if hasattr(item, "objectName") else ""
    cls = item.metaObject().className() if hasattr(item, "metaObject") else type(item).__name__
    print("  "*indent + f"{cls} [obj={obj_name}] pos=({x},{y}) size={w}x{h} vis={vis}")
    for c in item.children():
        dump(c, indent+1)

print("=== VIEW GEOMETRY ===")
modal.open()
view.forceActiveFocus()
dump(view, 0)

