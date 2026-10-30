import os
import sys

_app_dir = os.path.abspath(".")
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import Qt, QTimer, QUrl, QObject
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge

QQuickStyle.setStyle("Basic")
app = QApplication(sys.argv)

qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")
galvo_bridge = GalvoBridge()
jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
serial_bridge = SerialBridge()
cad_bridge = CadBridge(galvo_bridge=galvo_bridge, jog_bridge=jog_bridge)
camera_bridge = CameraBridge()
settings_bridge = SettingsBridge(cad_bridge=cad_bridge)
matrix_bridge = MatrixBridge(galvo_bridge=galvo_bridge)

engine = QQmlApplicationEngine()
qml_dir = os.path.join(_app_dir, "qml")
engine.addImportPath(qml_dir)

engine.rootContext().setContextProperty("galvo", galvo_bridge)
engine.rootContext().setContextProperty("jog", jog_bridge)
engine.rootContext().setContextProperty("serial", serial_bridge)
engine.rootContext().setContextProperty("cad", cad_bridge)
engine.rootContext().setContextProperty("camera", camera_bridge)
engine.rootContext().setContextProperty("settings", settings_bridge)
engine.rootContext().setContextProperty("matrix", matrix_bridge)
engine.rootContext().setContextProperty("appLogoUrl", "")

main_qml_path = os.path.join(qml_dir, "main.qml")
engine.load(QUrl.fromLocalFile(main_qml_path))

def step1():
    print("\n--- STEP 1: Find Canvas & Inspector ---")
    root_objects = engine.rootObjects()
    window = root_objects[0]
    cad_canvas = window.findChild(QObject, "cadCanvas")
    inspector = window.findChild(QObject, "inspector")
    toolbox = window.findChild(QObject, "toolbox")
    print("Found cadCanvas:", cad_canvas is not None)
    print("Found inspector:", inspector is not None)

    # Add a rectangle of size 10mm x 10mm
    rect = {
        "id": 1,
        "name": "Rect_1",
        "type": "rect",
        "xMm": 0.0,
        "yMm": 0.0,
        "wMm": 10.0,
        "hMm": 10.0,
        "rotation": 0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False
    }
    cad_canvas.setProperty("shapes", [rect])
    cad_canvas.setProperty("selectedIndex", 0)
    cad_canvas.shapeSelected.emit(rect)
    print("Rectangle set: wMm =", rect["wMm"], "hMm =", rect["hMm"])

    # Wait 200ms, then trigger barcode / DataMatrix
    QTimer.singleShot(200, step2)

def step2():
    print("\n--- STEP 2: Generate DataMatrix ---")
    root_objects = engine.rootObjects()
    window = root_objects[0]
    cad_canvas = window.findChild(QObject, "cadCanvas")
    inspector = window.findChild(QObject, "inspector")

    # Generate DataMatrix like barcodeModal does
    dm_res = cad_bridge.generateBarcodeEntity("DataMatrix", "https://google.com", 20.0)
    print("dm_res wMm:", dm_res.get("wMm"), "hMm:", dm_res.get("hMm"))

    # Add DataMatrix shape
    new_code = {
        "id": 2,
        "name": "DataMatrix_2",
        "type": "datamatrix",
        "text": "https://google.com",
        "xMm": 15.0,
        "yMm": 15.0,
        "wMm": 20.0,
        "hMm": 20.0,
        "rotation": 0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False,
        "rects": dm_res.get("rects", []),
        "paths": dm_res.get("paths", [])
    }
    cur_shapes = cad_canvas.property("shapes")
    cur_shapes.append(new_code)
    cad_canvas.setProperty("shapes", cur_shapes)
    cad_canvas.setProperty("selectedIndex", 1)
    cad_canvas.shapeSelected.emit(new_code)
    print("Selected DataMatrix.")

    QTimer.singleShot(200, step3)

def step3():
    print("\n--- STEP 3: Click back on Rect_1 ---")
    root_objects = engine.rootObjects()
    window = root_objects[0]
    cad_canvas = window.findChild(QObject, "cadCanvas")
    inspector = window.findChild(QObject, "inspector")

    shapes = cad_canvas.property("shapes")
    shapes_v = shapes.toVariant() if hasattr(shapes, "toVariant") else shapes
    print("Rect_1 dimensions before selecting:", shapes_v[0]["wMm"], "x", shapes_v[0]["hMm"])

    cad_canvas.setProperty("selectedIndex", 0)
    cad_canvas.shapeSelected.emit(shapes_v[0])

    shapes_after = cad_canvas.property("shapes")
    shapes_after_v = shapes_after.toVariant() if hasattr(shapes_after, "toVariant") else shapes_after
    print("Rect_1 dimensions after selecting:", shapes_after_v[0]["wMm"], "x", shapes_after_v[0]["hMm"])
    sel_shape = inspector.property("selectedShape")
    sel_v = sel_shape.toVariant() if hasattr(sel_shape, "toVariant") else sel_shape
    print("Inspector selectedShape:", sel_v["name"] if sel_v else "None")

    app.quit()

QTimer.singleShot(500, step1)
sys.exit(app.exec())
