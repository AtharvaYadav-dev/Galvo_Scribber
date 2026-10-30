import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Initialize Qt Application FIRST
QQuickStyle.setStyle("Basic")
app = QApplication.instance() or QApplication(sys.argv)

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from main_qml import ThemeManager

def verify_backend():
    print("=== STEP 1: VERIFYING BACKEND CadBridge HATCH PREVIEW & QUEUE ===")
    cad = CadBridge()

    pens = cad.getPens()
    print(f"Loaded {len(pens)} pens:")
    for p in pens:
        print(f"  Pen {p['id']}: {p['name']} -> {p['color']}")

    # 1. Test Pen 0 (Black)
    shp_black = {"id": 1, "type": "rect", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "rotation": 0, "penId": 0, "hatched": True}
    lines0 = cad.computeHatchPreviewLines(shp_black)
    assert len(lines0) > 0, "Pen 0 hatch lines must be generated"
    pen_ids0 = set(l["pen_id"] for l in lines0)
    print(f"Shape Pen 0 (Black) hatch line pen_ids: {pen_ids0}")
    assert pen_ids0 == {0}, f"Expected pen_id 0, got {pen_ids0}"

    # 2. Test Pen 2 (Red)
    shp_red = {"id": 2, "type": "rect", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "rotation": 0, "penId": 2, "hatched": True}
    lines2 = cad.computeHatchPreviewLines(shp_red)
    assert len(lines2) > 0, "Pen 2 hatch lines must be generated"
    pen_ids2 = set(l["pen_id"] for l in lines2)
    print(f"Shape Pen 2 (Red) hatch line pen_ids: {pen_ids2}")
    assert pen_ids2 == {2}, f"Expected pen_id 2, got {pen_ids2}"

    # 3. Test Pen 1 (Blue)
    shp_blue = {"id": 3, "type": "rect", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "rotation": 0, "penId": 1, "hatched": True}
    lines1 = cad.computeHatchPreviewLines(shp_blue)
    assert len(lines1) > 0, "Pen 1 hatch lines must be generated"
    pen_ids1 = set(l["pen_id"] for l in lines1)
    print(f"Shape Pen 1 (Blue) hatch line pen_ids: {pen_ids1}")
    assert pen_ids1 == {1}, f"Expected pen_id 1, got {pen_ids1}"

    # 4. Test Pen 3 (Green)
    shp_green = {"id": 4, "type": "rect", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "rotation": 0, "penId": 3, "hatched": True}
    lines3 = cad.computeHatchPreviewLines(shp_green)
    assert len(lines3) > 0, "Pen 3 hatch lines must be generated"
    pen_ids3 = set(l["pen_id"] for l in lines3)
    print(f"Shape Pen 3 (Green) hatch line pen_ids: {pen_ids3}")
    assert pen_ids3 == {3}, f"Expected pen_id 3, got {pen_ids3}"

    # 5. Test Custom Hatch Profile with Pen 0 (Black) on a Red shape
    shp_red_custom_black_hatch = {
        "id": 5, "type": "rect", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "rotation": 0, "penId": 2, "hatched": True,
        "hatch_profiles": {
            "1": {"enable": True, "pen_no": 0, "line_space": 0.05, "angle": 45.0, "type": "Bidirectional"},
            "2": {"enable": False, "pen_no": 0},
            "3": {"enable": False, "pen_no": 0}
        }
    }
    lines_custom = cad.computeHatchPreviewLines(shp_red_custom_black_hatch)
    pen_ids_custom = set(l["pen_id"] for l in lines_custom)
    print(f"Red shape with custom Pen 0 (Black) hatch: pen_ids: {pen_ids_custom}")
    assert pen_ids_custom == {0}, f"Expected pen_id 0 for explicitly set black hatch, got {pen_ids_custom}"

    print("=== BACKEND HATCH VERIFICATION PASSED 100%! ===\n")
    return True

def verify_qml_ui():
    print("=== STEP 2: VERIFYING FULL QML UI & RENDERING ARTIFACT ===")
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

    app.processEvents()

    # Populate 4 shapes: Pen 0 (Black), Pen 1 (Blue), Pen 2 (Red), Pen 3 (Green)
    shapes = [
        {
            "id": 1, "name": "Black_Rect", "type": "rect",
            "xMm": -18.0, "yMm": 14.0, "wMm": 16.0, "hMm": 16.0,
            "rotation": 0, "penId": 0, "hatched": True, "visible": True, "locked": False
        },
        {
            "id": 2, "name": "Blue_Circle", "type": "circle",
            "xMm": 18.0, "yMm": 14.0, "wMm": 16.0, "hMm": 16.0,
            "rotation": 0, "penId": 1, "hatched": True, "visible": True, "locked": False
        },
        {
            "id": 3, "name": "Red_Rect", "type": "rect",
            "xMm": -18.0, "yMm": -14.0, "wMm": 16.0, "hMm": 16.0,
            "rotation": 0, "penId": 2, "hatched": True, "visible": True, "locked": False
        },
        {
            "id": 4, "name": "Green_Circle", "type": "circle",
            "xMm": 18.0, "yMm": -14.0, "wMm": 16.0, "hMm": 16.0,
            "rotation": 0, "penId": 3, "hatched": True, "visible": True, "locked": False
        }
    ]

    cad_bridge.updateShapes(shapes)
    app.processEvents()

    # Grab window screenshot
    win = engine.rootObjects()[0]
    win.show()
    for _ in range(10):
        app.processEvents()

    import time
    time.sleep(0.3)
    app.processEvents()

    img = win.grabWindow()
    artifact_path = r"C:\Users\EXPRESS\.gemini\antigravity\brain\8b52e63e-2ce9-41d3-a71e-5535aeb780f8\pen_sync_and_hatch_verified.png"
    img.save(artifact_path, "PNG")
    print(f"Captured verification artifact: {artifact_path}")
    print("=== QML UI VERIFICATION COMPLETED SUCCESSFULLY! ===")
    return True

if __name__ == "__main__":
    b_ok = verify_backend()
    q_ok = verify_qml_ui()
    sys.exit(0 if (b_ok and q_ok) else 1)
