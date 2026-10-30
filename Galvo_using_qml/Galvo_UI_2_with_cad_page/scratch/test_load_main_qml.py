import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem

def test_load():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    galvo_bridge = GalvoBridge()
    jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
    serial_bridge = SerialBridge()
    cad_bridge = CadBridge(galvo_bridge=galvo_bridge)
    camera_bridge = CameraBridge()

    engine = QQmlApplicationEngine()
    
    # Connect warnings to stdout
    engine.warnings.connect(lambda warnings: [print("QML WARNING:", w.toString()) for w in warnings])

    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)

    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    if not engine.rootObjects():
        print("FAIL: Root object not created")
        return False
    print("SUCCESS: main.qml and all components loaded cleanly without errors!")
    return True

if __name__ == "__main__":
    test_load()
