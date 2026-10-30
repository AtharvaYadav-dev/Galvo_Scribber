import os
import sys
import io

# Ensure utf-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge

def run():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)

    galvo = GalvoBridge()
    cad = CadBridge(galvo_bridge=galvo)

    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_app_dir, "qml"))
    engine.rootContext().setContextProperty("cad", cad)

    comp = QQmlComponent(engine, os.path.join(_app_dir, "qml", "views", "CadView.qml"))
    if comp.status() != QQmlComponent.Status.Ready:
        for err in comp.errors():
            print("QML Error:", err.toString())
        return False

    view = comp.create()
    if not view:
        print("FAIL: could not create CadView")
        return False

    canvas = view.findChild(QObject, "cadCanvas")
    topBar = view.findChild(QObject, "topCommandBar")

    assert canvas is not None, "CadCanvas not found"
    assert topBar is not None, "CadTopCommandBar not found"

    print("--- Testing Top Command Bar Ribbon Tools ---")

    # 1. Initial State: no shapes, canUndo=False, canRedo=False, hasSelection=False
    print(f"Initial: totalShapes={topBar.property('totalShapesCount')}, hasSelection={topBar.property('hasSelection')}, canUndo={topBar.property('canUndo')}")
    assert topBar.property("totalShapesCount") == 0
    assert not topBar.property("hasSelection")
    assert not topBar.property("canUndo")
    assert not topBar.property("canRedo")

    # 2. Add two test shapes
    s1 = {
        "id": 1,
        "name": "Rect_1",
        "type": "rect",
        "xMm": 15.0,
        "yMm": 10.0,
        "wMm": 20.0,
        "hMm": 10.0,
        "rotation": 0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False
    }
    s2 = {
        "id": 2,
        "name": "Circle_2",
        "type": "circle",
        "xMm": -10.0,
        "yMm": -15.0,
        "wMm": 14.0,
        "hMm": 14.0,
        "rotation": 0,
        "penId": 1,
        "hatched": False,
        "visible": True,
        "locked": False
    }

    canvas.setProperty("shapes", [s1, s2])
    canvas.setProperty("selectedIndex", 0)

    print(f"After adding 2 shapes: totalShapes={topBar.property('totalShapesCount')}, hasSelection={topBar.property('hasSelection')}")
    assert topBar.property("totalShapesCount") == 2
    assert topBar.property("hasSelection")

    # 3. Test Alignments
    # Mode: left -> xMm = -halfF + halfW = -35 + 10 = -25.0
    canvas.alignSelectedShape("left")
    shapes = canvas.property("shapes")
    print(f"Align Left: xMm={shapes[0]['xMm']} (expected -25.0)")
    assert shapes[0]["xMm"] == -25.0
    assert canvas.property("canUndo") == True
    assert topBar.property("canUndo") == True

    # Helper to convert shapes to Python list of dicts
    def get_shapes():
        val = canvas.property("shapes")
        if hasattr(val, "toVariant"):
            return val.toVariant()
        return val

    # Mode: right -> xMm = halfF - halfW = 35 - 10 = 25.0
    canvas.alignSelectedShape("right")
    shapes = get_shapes()
    print(f"Align Right: xMm={shapes[0]['xMm']} (expected 25.0)")
    assert shapes[0]["xMm"] == 25.0

    # Mode: center_h -> xMm = 0.0
    canvas.alignSelectedShape("center_h")
    shapes = get_shapes()
    print(f"Align Center H: xMm={shapes[0]['xMm']} (expected 0.0)")
    assert shapes[0]["xMm"] == 0.0

    # Mode: top -> yMm = halfF - halfH = 35 - 5 = 30.0
    canvas.alignSelectedShape("top")
    shapes = get_shapes()
    print(f"Align Top: yMm={shapes[0]['yMm']} (expected 30.0)")
    assert shapes[0]["yMm"] == 30.0

    # Mode: center_v -> yMm = 0.0
    canvas.alignSelectedShape("center_v")
    shapes = get_shapes()
    print(f"Align Center V: yMm={shapes[0]['yMm']} (expected 0.0)")
    assert shapes[0]["yMm"] == 0.0

    # 4. Test Center to Origin
    s1_mod = dict(shapes[0])
    s1_mod["xMm"] = 12.34
    s1_mod["yMm"] = 23.45
    canvas.setProperty("shapes", [s1_mod, shapes[1]])
    canvas.centerSelectedShape()
    shapes = get_shapes()
    print(f"Center to Origin: xMm={shapes[0]['xMm']}, yMm={shapes[0]['yMm']} (expected 0, 0)")
    assert shapes[0]["xMm"] == 0.0
    assert shapes[0]["yMm"] == 0.0

    # 5. Test Fit to Field
    canvas.fitSelectionToField()
    shapes = get_shapes()
    target_field = 70.0 * 0.9 # 63.0
    print(f"Fit to Field: wMm={shapes[0]['wMm']}, hMm={shapes[0]['hMm']} (expected max dimension = 63.0)")
    assert max(shapes[0]["wMm"], shapes[0]["hMm"]) == 63.0
    assert shapes[0]["xMm"] == 0.0
    assert shapes[0]["yMm"] == 0.0

    # 6. Test Undo & Redo
    pre_undo_w = shapes[0]["wMm"]
    canvas.undo()
    shapes = get_shapes()
    print(f"After Undo: wMm={shapes[0]['wMm']}, canRedo={topBar.property('canRedo')}")
    assert shapes[0]["wMm"] != pre_undo_w
    assert topBar.property("canRedo") == True

    canvas.redo()
    shapes = get_shapes()
    print(f"After Redo: wMm={shapes[0]['wMm']} (restored to {pre_undo_w})")
    assert shapes[0]["wMm"] == pre_undo_w

    # 7. Test Grouping
    print(f"Before Group: totalShapes={len(shapes)}, isSelectionGroup={topBar.property('isSelectionGroup')}")
    canvas.groupSelectedShapes()
    shapes = get_shapes()
    print(f"After Group: totalShapes={len(shapes)}, type={shapes[0]['type']}, isSelectionGroup={topBar.property('isSelectionGroup')}")
    assert len(shapes) == 1
    assert shapes[0]["type"] == "group"
    assert len(shapes[0]["children"]) == 2
    assert topBar.property("isSelectionGroup") == True

    # 8. Test Ungrouping
    canvas.ungroupSelectedShape()
    shapes = get_shapes()
    print(f"After Ungroup: totalShapes={len(shapes)}, isSelectionGroup={topBar.property('isSelectionGroup')}")
    assert len(shapes) == 2
    assert topBar.property("isSelectionGroup") == False

    # 9. Test Zoom Controls
    init_scale = canvas.property("zoomScale")
    canvas.zoomIn()
    zoomed_in_scale = canvas.property("zoomScale")
    print(f"Zoom In: {init_scale} -> {zoomed_in_scale}")
    assert zoomed_in_scale > init_scale

    canvas.zoomOut()
    zoomed_out_scale = canvas.property("zoomScale")
    print(f"Zoom Out: {zoomed_in_scale} -> {zoomed_out_scale}")
    assert zoomed_out_scale < zoomed_in_scale

    canvas.zoomFit()
    fit_scale = canvas.property("zoomScale")
    print(f"Zoom Fit Field Scale: {fit_scale}")
    assert fit_scale > 0

    # 10. Locked shape guard check
    s0_dict = shapes[0].toVariant() if hasattr(shapes[0], "toVariant") else shapes[0]
    s1_dict = shapes[1].toVariant() if hasattr(shapes[1], "toVariant") else shapes[1]
    s_locked = dict(s0_dict)
    s_locked["locked"] = True
    canvas.setProperty("shapes", [s_locked, s1_dict])
    canvas.setProperty("selectedIndex", 0)
    print(f"Locked check: isSelectionLocked={topBar.property('isSelectionLocked')}")
    assert topBar.property("isSelectionLocked") == True

    old_x = s_locked["xMm"]
    canvas.alignSelectedShape("left")
    shapes_after = canvas.property("shapes")
    shp0_after = shapes_after[0].toVariant() if hasattr(shapes_after[0], "toVariant") else shapes_after[0]
    assert shp0_after["xMm"] == old_x, "Locked shape should not move!"
    print("Locked guard passed: shape did not move.")

    print("\n=======================================================")
    print("ALL 15 TOP COMMAND BAR BUTTONS & ACTIONS VERIFIED 100%!")
    print("=======================================================")
    return True

if __name__ == "__main__":
    if not run():
        sys.exit(1)
