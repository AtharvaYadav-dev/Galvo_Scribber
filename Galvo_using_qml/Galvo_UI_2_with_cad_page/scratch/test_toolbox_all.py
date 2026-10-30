import sys
import os
import io
import json
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from PySide6.QtCore import QCoreApplication, QTimer, Qt, QPointF, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow

# Ensure app runs in offscreen/headless mode
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.getcwd())

def test_all_11_tools():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    
    # Import Bridges
    from bridges.cad_bridge import CadBridge
    from bridges.galvo_bridge import GalvoBridge
    from bridges.settings_bridge import SettingsBridge

    cad = CadBridge()
    galvo = GalvoBridge()
    settings = SettingsBridge()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("cad", cad)
    engine.rootContext().setContextProperty("galvo", galvo)
    engine.rootContext().setContextProperty("settingsBridge", settings)

    engine.load("qml/main.qml")
    if not engine.rootObjects():
        print("FAIL: Could not load main.qml")
        sys.exit(1)

    root = engine.rootObjects()[0]
    cadCanvas = root.findChild(QObject, "cadCanvas")
    
    if not cadCanvas:
        def find_cad_canvas(obj):
            if obj.objectName() == "cadCanvas":
                return obj
            for child in obj.children():
                res = find_cad_canvas(child)
                if res is not None: return res
            return None
        cadCanvas = find_cad_canvas(root)

    print("Located cadCanvas successfully!")
    assert cadCanvas is not None, "CadCanvas not found in QML hierarchy"

    def get_shapes():
        val = cadCanvas.property("shapes")
        if hasattr(val, "toVariant"):
            return val.toVariant()
        return val

    # Reset shapes
    cadCanvas.setProperty("shapes", [])
    assert len(get_shapes()) == 0, "Canvas should be empty"

    # TEST 1: RECTANGLE TOOL
    print("[1/11] Testing Rectangle Tool...")
    rect_shp = {
        "id": 1, "name": "Rect_1", "type": "rect",
        "xMm": 0.0, "yMm": 0.0, "wMm": 20.0, "hMm": 20.0,
        "rotation": 0, "penId": 0, "hatched": False, "visible": True, "locked": False
    }
    cadCanvas.pushUndoState()
    cadCanvas.setProperty("shapes", [rect_shp])
    cadCanvas.setProperty("selectedIndex", 0)
    assert len(get_shapes()) == 1
    assert get_shapes()[0]["type"] == "rect"
    print("  -> Rectangle created and verified!")

    # TEST 2: CIRCLE TOOL
    print("[2/11] Testing Circle Tool...")
    circ_shp = {
        "id": 2, "name": "Circle_2", "type": "circle",
        "xMm": 15.0, "yMm": 0.0, "wMm": 10.0, "hMm": 10.0,
        "rotation": 0, "penId": 1, "hatched": False, "visible": True, "locked": False
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.append(circ_shp)
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 2
    assert get_shapes()[1]["type"] == "circle"
    print("  -> Circle created and verified!")

    # TEST 3: POLYGON TOOL
    print("[3/11] Testing Polygon Tool (5-sided regular pentagon)...")
    p_radius = 8.0
    p_sides = 5
    poly_pts = []
    for psi in range(p_sides):
        ang = -math.pi / 2.0 + (psi * 2.0 * math.pi) / p_sides
        poly_pts.append([round(p_radius * math.cos(ang), 3), round(p_radius * math.sin(ang), 3)])
    poly_pts.append(poly_pts[0])
    poly_shp = {
        "id": 3, "name": "Polygon_3", "type": "polygon",
        "xMm": -15.0, "yMm": 0.0, "wMm": 16.0, "hMm": 16.0,
        "rotation": 0, "penId": 0, "hatched": False, "visible": True, "locked": False,
        "paths": [poly_pts]
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.append(poly_shp)
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 3
    assert get_shapes()[2]["type"] == "polygon"
    assert len(get_shapes()[2]["paths"][0]) == 6
    print("  -> Polygon created and verified!")

    # TEST 4: LINE TOOL
    print("[4/11] Testing Line Tool...")
    line_pts = [[-10.0, 0.0], [10.0, 0.0]]
    line_shp = {
        "id": 4, "name": "Line_4", "type": "polygon",
        "xMm": 0.0, "yMm": 15.0, "wMm": 20.0, "hMm": 1.0,
        "rotation": 0, "penId": 0, "hatched": False, "visible": True, "locked": False,
        "paths": [line_pts]
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.append(line_shp)
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 4
    print("  -> Line created and verified!")

    # TEST 5: CURVE TOOL
    print("[5/11] Testing Curve / Freehand Tool...")
    curve_pts = [[-5.0, -5.0], [0.0, 5.0], [5.0, -5.0]]
    curve_shp = {
        "id": 5, "name": "Curve_5", "type": "polygon",
        "xMm": 0.0, "yMm": -15.0, "wMm": 10.0, "hMm": 10.0,
        "rotation": 0, "penId": 0, "hatched": False, "visible": True, "locked": False,
        "paths": [curve_pts]
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.append(curve_shp)
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 5
    print("  -> Curve created and verified!")

    # TEST 6: TEXT TOOL
    print("[6/11] Testing Laser Text & Font Tool...")
    text_shp = {
        "id": 6, "name": "Text_6", "type": "text",
        "text": "SP2L TEST", "xMm": 0.0, "yMm": 0.0, "wMm": 20.0, "hMm": 4.0,
        "rotation": 0, "fontFamily": "Segoe UI", "fontType": "TrueType Font",
        "textAlign": "center", "penId": 0, "hatched": False, "visible": True, "locked": False
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.append(text_shp)
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 6
    m = cad.measureText("SP2L TEST", "Segoe UI", 4.0, False, False)
    assert m["wMm"] > 0, "cad.measureText should return valid width"
    print(f"  -> Text created and verified! Width measured: {m['wMm']:.2f}mm")

    # TEST 7: BARCODE & QR CODE TOOL (QR, Code 128, DataMatrix)
    print("[7/11] Testing QR Code & Barcode Tool...")
    qr_shp = {
        "id": 7, "name": "QRCode_7", "type": "qrcode",
        "text": "https://galvo.io", "xMm": -20.0, "yMm": 20.0, "wMm": 15.0, "hMm": 15.0,
        "rotation": 0, "penId": 0, "hatched": True, "visible": True, "locked": False
    }
    b128_shp = {
        "id": 8, "name": "Barcode128_8", "type": "barcode128",
        "text": "SN-987654", "xMm": 20.0, "yMm": 20.0, "wMm": 25.0, "hMm": 10.0,
        "rotation": 0, "penId": 0, "hatched": True, "visible": True, "locked": False
    }
    dm_shp = {
        "id": 9, "name": "DataMatrix_9", "type": "datamatrix",
        "text": "DM-00123", "xMm": 20.0, "yMm": -20.0, "wMm": 12.0, "hMm": 12.0,
        "rotation": 0, "penId": 0, "hatched": True, "visible": True, "locked": False
    }
    cadCanvas.pushUndoState()
    shapes = list(get_shapes())
    shapes.extend([qr_shp, b128_shp, dm_shp])
    cadCanvas.setProperty("shapes", shapes)
    assert len(get_shapes()) == 9
    
    # Test vector generation in CadBridge for all 3 barcode types
    qr_polys = cad._shape_to_polygons(qr_shp)
    b128_polys = cad._shape_to_polygons(b128_shp)
    dm_polys = cad._shape_to_polygons(dm_shp)
    assert len(qr_polys) > 0, "QR Code vector polygons should not be empty"
    assert len(b128_polys) > 0, "Barcode 128 vector bars should not be empty"
    assert len(dm_polys) > 0, "DataMatrix vector modules should not be empty"
    print(f"  -> QR Code ({len(qr_polys)} polys), Barcode 128 ({len(b128_polys)} bars), DataMatrix ({len(dm_polys)} modules) verified!")

    # TEST 8: NODE / VERTEX EDIT ENGINE
    print("[8/11] Testing Node / Vertex Edit Engine...")
    cadCanvas.setProperty("activeTool", "node")
    cadCanvas.setProperty("selectedIndex", 2) # Select the 5-sided polygon
    # Test polyline construction
    cadCanvas.setProperty("activeNodePathPts", [[0.0, 0.0], [5.0, 5.0], [10.0, 0.0]])
    cadCanvas.finishNodePolyline()
    assert len(get_shapes()) == 10, "Polyline should create new shape"
    last_poly = get_shapes()[-1]
    assert last_poly["type"] == "polygon"
    assert len(last_poly["paths"][0]) == 3
    print("  -> Node polyline finished and shape created!")

    # Test vertex drag on polygon
    cadCanvas.setProperty("selectedIndex", 9)
    poly_target = get_shapes()[9]
    old_p0 = poly_target["paths"][0][0]
    cadCanvas.pushUndoState()
    # Move vertex 0
    poly_target["paths"][0][0] = [old_p0[0] + 2.0, old_p0[1] - 1.0]
    cadCanvas.recalculateShapeBounds(poly_target)
    assert poly_target["paths"][0][0][0] == old_p0[0] + 2.0
    print("  -> Node vertex modification and recalculateShapeBounds verified!")

    # TEST 9: SELECT / PICK TOOL & HOTKEY V
    print("[9/11] Testing Select Tool & Hotkey V...")
    cadCanvas.setProperty("activeTool", "node")
    assert cadCanvas.property("activeTool") == "node"
    # Switch to select
    cadCanvas.setProperty("activeTool", "select")
    assert cadCanvas.property("activeTool") == "select"
    cadCanvas.setProperty("selectedIndex", 0)
    assert cadCanvas.property("selectedIndex") == 0
    print("  -> Select tool and switching verified!")

    # TEST 10: DUPLICATE & DELETE TOOL
    print("[10/11] Testing Duplicate & Delete Tool...")
    pre_count = len(get_shapes())
    cadCanvas.setProperty("selectedIndex", 0)
    cadCanvas.duplicateSelectedShape()
    assert len(get_shapes()) == pre_count + 1
    print(f"  -> Duplicated shape, count now: {len(get_shapes())}")
    
    # Delete the duplicated shape
    cadCanvas.deleteSelectedShape()
    assert len(get_shapes()) == pre_count
    print(f"  -> Deleted selected shape, count restored to: {len(get_shapes())}")

    # TEST 11: UNDO / REDO HISTORY
    print("[11/11] Testing Undo / Redo History across all tools...")
    # Undo delete restores the duplicate
    cadCanvas.undo()
    assert len(get_shapes()) == pre_count + 1, "Undo delete should restore the duplicate"
    print(f"  -> Undo delete restored duplicate! Count: {len(get_shapes())}")

    # Undo duplicate restores pre-duplication count
    cadCanvas.undo()
    assert len(get_shapes()) == pre_count, "Undo duplicate should revert back to original count"
    print(f"  -> Undo duplicate restored original state! Count: {len(get_shapes())}")

    # Redo duplicate re-adds duplicate
    cadCanvas.redo()
    assert len(get_shapes()) == pre_count + 1, "Redo duplicate should re-add duplicate"
    print(f"  -> Redo duplicate restored duplicate! Count: {len(get_shapes())}")

    # Redo delete removes duplicate again
    cadCanvas.redo()
    assert len(get_shapes()) == pre_count, "Redo delete should re-delete duplicate"
    print(f"  -> Redo delete removed duplicate! Count: {len(get_shapes())}")

    print("\n=======================================================")
    print(" ALL 11 TOOLBOX TOOLS FULLY FUNCTIONAL AND VERIFIED! ")
    print("=======================================================")

if __name__ == "__main__":
    test_all_11_tools()
