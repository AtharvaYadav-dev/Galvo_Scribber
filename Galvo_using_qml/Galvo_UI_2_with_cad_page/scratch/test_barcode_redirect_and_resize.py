import os
import sys
import zxingcpp
import numpy as np
from PIL import Image

_app_dir = os.path.abspath(".")
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import Qt, QTimer, QUrl, QObject
from PySide6.QtGui import QIcon, QFontDatabase, QImage
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

def run_tests():
    print("==================================================")
    print(" RUNNING BARCODE REDIRECT & RESIZE FIX VERIFICATION")
    print("==================================================")

    # 1. Verify CadBridge generateBarcodeEntity decode with zxingcpp
    test_cases = [
        ("DataMatrix", "https://example.com/matrix", zxingcpp.BarcodeFormat.DataMatrix),
        ("Code 128", "12345678", zxingcpp.BarcodeFormat.Code128),
        ("QR Code", "https://example.com/qr", zxingcpp.BarcodeFormat.QRCode),
    ]

    for ctype, ctext, cfmt in test_cases:
        res = cad_bridge.generateBarcodeEntity(ctype, ctext, 25.0)
        assert res["success"] is True
        print(f"[{ctype}] Generated: w={res['wMm']}mm, h={res['hMm']}mm, rects={len(res['rects'])}, paths={len(res['paths'])}")

        # Render simulated canvas rects to test optical scan readability (at standard 20 px/mm resolution)
        scale = 20
        w_px = int(res["wMm"] * scale)
        h_px = int(res["hMm"] * scale)
        pad = 40
        img = np.ones((h_px + pad * 2, w_px + pad * 2), dtype=np.uint8) * 255
        cx = (w_px + pad * 2) // 2
        cy = (h_px + pad * 2) // 2
        for rc in res["rects"]:
            x0 = int(round(rc["x"] * scale + cx))
            y0 = int(round(-rc["y"] * scale + cy))
            w = int(round(rc["w"] * scale))
            h = int(round(rc["h"] * scale))
            img[y0:y0+h, x0:x0+w] = 0

        read_res = zxingcpp.read_barcode(img, [cfmt])
        print(f"[{ctype}] Scan Result -> Valid: {read_res.valid if read_res else False}, Decoded: '{read_res.text if read_res else None}'")
        assert read_res and read_res.valid and read_res.text == ctext, f"Optical decode mismatch for {ctype}"

    # 2. Verify Canvas Object stability (no growing bug)
    root_objects = engine.rootObjects()
    window = root_objects[0]
    cad_canvas = window.findChild(QObject, "cadCanvas")
    inspector = window.findChild(QObject, "inspector")

    # Add 1 rectangle and 1 circle and 1 DataMatrix
    rect = {
        "id": 1,
        "name": "Rect_1",
        "type": "rect",
        "xMm": -20.0,
        "yMm": 0.0,
        "wMm": 15.0,
        "hMm": 15.0,
        "rotation": 0,
        "penId": 2, # Red Pen
        "hatched": False,
        "visible": True,
        "locked": False
    }

    dm_res = cad_bridge.generateBarcodeEntity("DataMatrix", "https://google.com", 20.0)
    dm = {
        "id": 2,
        "name": "DataMatrix_1",
        "type": "datamatrix",
        "text": "https://google.com",
        "xMm": 15.0,
        "yMm": 0.0,
        "wMm": 20.0,
        "hMm": 20.0,
        "rotation": 0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False,
        "rects": dm_res["rects"],
        "paths": dm_res["paths"]
    }

    shapes = [rect, dm]
    cad_canvas.setProperty("shapes", shapes)
    cad_canvas.setProperty("selectedIndex", 1) # Select DataMatrix
    cad_canvas.shapeSelected.emit(dm)

    # Now click back onto Rect_1
    cad_canvas.setProperty("selectedIndex", 0) # Select Rect_1
    cad_canvas.shapeSelected.emit(rect)

    cur_shapes = cad_canvas.property("shapes")
    shapes_v = cur_shapes.toVariant() if hasattr(cur_shapes, "toVariant") else cur_shapes
    r_w = shapes_v[0]["wMm"]
    r_h = shapes_v[0]["hMm"]
    print(f"Rect_1 dimension check: {r_w} x {r_h} (Expected: 15.0 x 15.0)")
    assert r_w == 15.0 and r_h == 15.0, f"Shape resized unexpectedly to {r_w} x {r_h}!"

    # 3. Take screenshot of the UI showing canvas with both shapes
    cad_canvas.requestPaint()
    QTimer.singleShot(400, capture_screen)

def capture_screen():
    root_objects = engine.rootObjects()
    window = root_objects[0]
    window.resize(1280, 800)
    image = window.grabWindow()
    artifact_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\barcode_and_shapes_verified.png"
    image.save(artifact_path)
    print(f"Visual artifact saved to: {artifact_path}")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    app.quit()

QTimer.singleShot(600, run_tests)
sys.exit(app.exec())
