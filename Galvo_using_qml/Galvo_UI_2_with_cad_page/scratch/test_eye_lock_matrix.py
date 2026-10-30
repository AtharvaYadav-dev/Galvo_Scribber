import os
import sys

_app_dir = r"D:\Galvo_using_qml\Galvo_UI_2_with_cad_page"
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtCore import QUrl

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem

def test_eye_lock_and_matrix():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda ws: [print("WARN:", w.toString()) for w in ws])
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    ctx = engine.rootContext()
    ctx.setContextProperty("galvo", GalvoBridge())
    ctx.setContextProperty("jog", JogBridge())
    ctx.setContextProperty("serial", SerialBridge())
    cad_bridge = CadBridge()
    ctx.setContextProperty("cad", cad_bridge)
    ctx.setContextProperty("camera", CameraBridge())

    test_qml_path = os.path.join(_app_dir, "scratch", "test_runner.qml")
    test_qml = """import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../qml/components/cad"

Item {
    id: root
    width: 1000
    height: 700

    CadCanvas {
        id: canvas
        width: 600
        height: 600
    }

    CadInspectorPanel {
        id: inspector
        shapesModel: canvas.shapes
        selectedIndex: canvas.selectedIndex
        onShapeSelected: function(idx) { canvas.selectedIndex = idx }
        onShapeDeleted: function(idx) {
            canvas.selectedIndex = idx
            canvas.deleteSelectedShape()
        }
        onShapeVisibilityToggled: function(idx) {
            canvas.toggleShapeVisibility(idx)
        }
        onShapeLockToggled: function(idx) {
            canvas.toggleShapeLock(idx)
        }
        onShapeRenamed: function(idx, newName) {
            canvas.renameShape(idx, newName)
        }
    }

    function runTests() {
        // 1. Add shapes to canvas
        var s1 = { id: 1, name: "Rect_1", type: "rect", xMm: 10.0, yMm: 10.0, wMm: 20.0, hMm: 10.0, visible: true, locked: false }
        var s2 = { id: 2, name: "Circle_2", type: "circle", xMm: -5.0, yMm: 5.0, wMm: 14.0, hMm: 14.0, visible: true, locked: false }
        canvas.shapes = [s1, s2]
        canvas.shapesChanged()
        canvas.selectedIndex = 0

        console.log("Initial count: " + canvas.shapes.length)
        if (canvas.shapes.length !== 2) throw new Error("Expected 2 shapes")

        // Test Shape Renaming via Inspector signal
        inspector.shapeRenamed(0, "LaserContour_A")
        console.log("After rename s1:", canvas.shapes[0].name)
        if (canvas.shapes[0].name !== "LaserContour_A") throw new Error("Shape 0 rename failed!")

        // 2. Test Visibility Toggle via Inspector signal
        inspector.shapeVisibilityToggled(0)
        console.log("After toggle visibility s1: " + canvas.shapes[0].visible)
        if (canvas.shapes[0].visible !== false) throw new Error("Shape 1 should be hidden (visible=false)")

        inspector.shapeVisibilityToggled(0)
        console.log("After 2nd toggle visibility s1: " + canvas.shapes[0].visible)
        if (canvas.shapes[0].visible !== true) throw new Error("Shape 1 should be visible again (visible=true)")

        // 3. Test Lock Toggle via Inspector signal
        inspector.shapeLockToggled(1)
        console.log("After toggle lock s2: " + canvas.shapes[1].locked)
        if (canvas.shapes[1].locked !== true) throw new Error("Shape 2 should be locked (locked=true)")

        // Try to delete locked shape - should be prevented!
        canvas.selectedIndex = 1
        canvas.deleteSelectedShape()
        if (canvas.shapes.length !== 2) throw new Error("Locked shape 2 was deleted! It must be protected!")
        console.log("Locked shape protected from deletion successfully!")

        inspector.shapeLockToggled(1)
        if (canvas.shapes[1].locked !== false) throw new Error("Shape 2 should be unlocked")
        console.log("Shape 2 unlocked successfully!")

        // 4. Test 9-Point Anchor Transform
        // Bounding box of Rect_1: Center=(10, 10), W=20, H=10
        // Top-Left (index 0): x = 10 - 10 = 0, y = 10 + 5 = 15
        var tl = inspector.getAnchorPos(10, 10, 20, 10, 0)
        if (Math.abs(tl.x - 0) > 1e-4 || Math.abs(tl.y - 15) > 1e-4) throw new Error("Top-Left anchor incorrect: " + JSON.stringify(tl))

        // Center (index 4): x = 10, y = 10
        var c = inspector.getAnchorPos(10, 10, 20, 10, 4)
        if (Math.abs(c.x - 10) > 1e-4 || Math.abs(c.y - 10) > 1e-4) throw new Error("Center anchor incorrect: " + JSON.stringify(c))

        // Bottom-Left (index 6): x = 10 - 10 = 0, y = 10 - 5 = 5
        var bl = inspector.getAnchorPos(10, 10, 20, 10, 6)
        if (Math.abs(bl.x - 0) > 1e-4 || Math.abs(bl.y - 5) > 1e-4) throw new Error("Bottom-Left anchor incorrect: " + JSON.stringify(bl))

        // Test getCenterFromAnchor for Bottom-Left
        var newCenter = inspector.getCenterFromAnchor(0, 5, 20, 10, 6)
        if (Math.abs(newCenter.x - 10) > 1e-4 || Math.abs(newCenter.y - 10) > 1e-4) throw new Error("getCenterFromAnchor incorrect: " + JSON.stringify(newCenter))

        console.log("ALL EYE, LOCK, AND 9-POINT ANCHOR TESTS PASSED!")
        return true
    }
}
"""
    with open(test_qml_path, "w", encoding="utf-8") as f:
        f.write(test_qml)

    engine.load(QUrl.fromLocalFile(test_qml_path))
    if not engine.rootObjects():
        print("FAIL: test component not created")
        return False

    root = engine.rootObjects()[0]
    result = root.runTests()
    return result

if __name__ == "__main__":
    if test_eye_lock_and_matrix():
        print("SUCCESS")
        sys.exit(0)
    else:
        print("FAILURE")
        sys.exit(1)
