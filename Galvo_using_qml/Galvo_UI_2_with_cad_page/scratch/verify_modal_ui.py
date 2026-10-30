import os
import sys
from PySide6.QtCore import QUrl, QTimer, Qt
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

def open_modal():
    print("Opening CadBarcodeModal...")
    modal = root_window.findChild(object, "barcodeModal")
    # If not found by objectName, search in children
    if not modal:
        for ch in root_window.children():
            if "barcodeModal" in str(ch) or "CadBarcodeModal" in str(ch):
                modal = ch
                break
    
    # Try finding toolbox or setting property
    toolbox = root_window.findChild(object, "toolbox")
    if modal:
        modal.setProperty("visible", True)
        print("Set modal visible.")
    else:
        # Fallback: invoke toolbox barcode trigger
        print("Modal object direct reference not found, trying QML method...")
    
    def take_modal_screenshot():
        img = root_window.grabWindow()
        artifact_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\barcode_modal_options_verified.png"
        img.save(artifact_path)
        print(f"Saved modal screenshot to {artifact_path}")
        QTimer.singleShot(400, app.quit)

    QTimer.singleShot(800, take_modal_screenshot)

QTimer.singleShot(800, open_modal)
sys.exit(app.exec())

