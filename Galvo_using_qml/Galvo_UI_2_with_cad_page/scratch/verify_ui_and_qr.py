import os
import sys
import time
from PySide6.QtCore import QUrl, QTimer, Qt, QPoint, QEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QMouseEvent

os.chdir(r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
sys.path.insert(0, r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

# Import bridges
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

def test_workflow():
    print("Testing QR generation and export...")
    # Generate barcode shape
    res = cad_bridge.generateBarcodeEntity("qrcode", "https://www.specialiseproducts.com", 20.0)
    print(f"Generated QR Code: {len(res.get('rects', []))} 2D merged rects.")
    
    # Add to canvas
    shp = {
        "id": 1,
        "name": "QRCode_1",
        "type": "qrcode",
        "text": "https://www.specialiseproducts.com",
        "xMm": 0.0,
        "yMm": 0.0,
        "wMm": 20.0,
        "hMm": 20.0,
        "rotation": 0.0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False,
        "rects": res.get("rects", []),
        "paths": res.get("paths", [])
    }
    
    cad_canvas = root_window.findChild(object, "cadCanvas")
    if cad_canvas:
        cad_canvas.setProperty("shapes", [shp])
        cad_canvas.setProperty("selectedIndex", 0)
        from PySide6.QtCore import QMetaObject
        QMetaObject.invokeMethod(cad_canvas, "requestPaint")
        print("Set shape in cadCanvas and requested paint.")
    
    inspector = root_window.findChild(object, "inspector")
    if inspector:
        inspector.setProperty("shapesModel", [shp])
        inspector.setProperty("selectedIndex", 0)
        print("Selected shape in inspector.")
    
    # Test export non-interactively
    os.makedirs("test_verify_exports", exist_ok=True)
    dxf_res = cad_bridge.exportBarcodeFile(shp, "dxf", "test_verify_exports/export_qr.dxf")
    svg_res = cad_bridge.exportBarcodeFile(shp, "svg", "test_verify_exports/export_qr.svg")
    png_res = cad_bridge.exportBarcodeFile(shp, "png", "test_verify_exports/export_qr.png")
    
    print("DXF export:", dxf_res)
    print("SVG export:", svg_res)
    print("PNG export:", png_res)
    
    def take_screenshot():
        img = root_window.grabWindow()
        artifact_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\qr_export_and_canvas_verified.png"
        img.save(artifact_path)
        print(f"Saved verified screenshot to {artifact_path}")
        QTimer.singleShot(300, app.quit)

    QTimer.singleShot(1000, take_screenshot)

QTimer.singleShot(800, test_workflow)
sys.exit(app.exec())
