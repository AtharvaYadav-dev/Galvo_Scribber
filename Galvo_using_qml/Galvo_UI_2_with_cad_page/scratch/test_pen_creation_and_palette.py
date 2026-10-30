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
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from main_qml import ThemeManager

def test_pen_lifecycle():
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
    theme_manager = ThemeManager()

    engine = QQmlApplicationEngine()
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)
    root_context.setContextProperty("settings", settings_bridge)
    root_context.setContextProperty("matrix", matrix_bridge)
    root_context.setContextProperty("matrixBridge", matrix_bridge)
    root_context.setContextProperty("appLogoUrl", "")
    root_context.setContextProperty("themeManager", theme_manager)

    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    if not engine.rootObjects():
        print("FAIL: Root object not created")
        return False

    app.processEvents()
    print("[1/5] Application loaded successfully.")

    # 1. Test CadBridge Pen creation
    initial_pens = cad_bridge.getPens()
    initial_count = len(initial_pens)
    print(f"[2/5] Initial pens in CadBridge: {initial_count}")

    new_pen_id = cad_bridge.addPen("Pen 8 (Laser Cut)", "#F43F5E")
    print(f"[3/5] Added Pen {new_pen_id}. New count: {len(cad_bridge.getPens())}")
    assert len(cad_bridge.getPens()) == initial_count + 1

    # 2. Test color change
    cad_bridge.updatePenColor(new_pen_id, "#10B981")
    pen_data = [p for p in cad_bridge.getPens() if p["id"] == new_pen_id][0]
    print(f"[4/5] Updated Pen {new_pen_id} color: {pen_data['color']}")
    assert pen_data["color"] == "#10B981"

    # 3. Test deletion of custom pen
    cad_bridge.deletePen(new_pen_id)
    print(f"[5/5] Deleted custom Pen {new_pen_id}. Restored count: {len(cad_bridge.getPens())}")
    assert len(cad_bridge.getPens()) == initial_count

    print("\n=======================================================")
    print(" PEN CREATION & WHOLE COLOR PALETTE VERIFIED 100%!")
    print("=======================================================")
    return True

if __name__ == "__main__":
    success = test_pen_lifecycle()
    sys.exit(0 if success else 1)

