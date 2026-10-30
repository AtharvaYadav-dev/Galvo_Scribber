import os
import sys
from PySide6.QtCore import QUrl, QTimer, Qt, QMetaObject
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

os.chdir(r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
sys.path.insert(0, r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

from bridges.cad_bridge import CadBridge
from bridges.settings_bridge import SettingsBridge
from bridges.galvo_bridge import GalvoBridge

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

cad_bridge = CadBridge()
settings_bridge = SettingsBridge()
galvo_bridge = GalvoBridge()

engine.rootContext().setContextProperty("cad", cad_bridge)
engine.rootContext().setContextProperty("settingsBridge", settings_bridge)
engine.rootContext().setContextProperty("galvoBridge", galvo_bridge)

qml_file = os.path.join(os.getcwd(), "qml", "main.qml")
engine.load(QUrl.fromLocalFile(qml_file))

if not engine.rootObjects():
    print("Error: Could not load main.qml")
    sys.exit(1)

root_window = engine.rootObjects()[0]
root_window.show()

def test_dxf_barcode_workflow():
    print("Testing DXF Barcode workflow...")
    
    # 1. Generate QR Code in DXF Vector mode
    res = cad_bridge.generateBarcodeEntity("qrcode", "https://www.specialiseproducts.com", 20.0)
    print(f"Generated QR Code: {len(res.get('paths', []))} closed vector paths.")
    
    # 2. Package as a true DXF CAD vector entity
    dxf_shp = {
        "id": 1,
        "name": "DXF_QRCode_1",
        "type": "dxf",
        "isBarcode": True,
        "barcodeType": "qrcode",
        "outputFormat": "dxf",
        "text": "https://www.specialiseproducts.com",
        "xMm": 0.0,
        "yMm": 0.0,
        "wMm": 20.0,
        "hMm": 20.0,
        "rotation": 0.0,
        "penId": 2, # Red Pen to clearly demonstrate laser vector line rendering!
        "hatched": False,
        "mark_contour": True,
        "visible": True,
        "locked": False,
        "rects": res.get("rects", []),
        "paths": res.get("paths", [])
    }
    
    cad_canvas = root_window.findChild(object, "cadCanvas")
    if cad_canvas:
        cad_canvas.setProperty("shapes", [dxf_shp])
        cad_canvas.setProperty("selectedIndex", 0)
        QMetaObject.invokeMethod(cad_canvas, "requestPaint")
        print("Placed DXF QR shape onto cadCanvas with Pen 2 (Red).")
    
    inspector = root_window.findChild(object, "inspector")
    if inspector:
        inspector.setProperty("shapesModel", [dxf_shp])
        inspector.setProperty("selectedIndex", 0)
        print("Set selected shape in inspector.")
    
    def step_2_hatch_and_screenshot():
        print("Testing hatch on DXF vector QR shape...")
        # Now test hatching the DXF QR shape
        dxf_shp["hatched"] = True
        hlines = cad_bridge.computeHatchPreviewLines(dxf_shp)
        dxf_shp["hatch_lines"] = hlines
        print(f"Computed {len(hlines)} hatch lines for DXF QR shape.")
        
        if cad_canvas:
            cad_canvas.setProperty("shapes", [dxf_shp])
            QMetaObject.invokeMethod(cad_canvas, "requestPaint")
        
        # Grab screenshot
        img = root_window.grabWindow()
        artifact_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\dxf_vector_qr_verified.png"
        img.save(artifact_path)
        print(f"Saved DXF vector QR verified screenshot to {artifact_path}")
        QTimer.singleShot(400, app.quit)

    QTimer.singleShot(1000, step_2_hatch_and_screenshot)

QTimer.singleShot(800, test_dxf_barcode_workflow)
sys.exit(app.exec())

