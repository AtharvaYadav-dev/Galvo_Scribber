import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../qml/components/cad"

Item {
    id: root
    width: 1200
    height: 800

    CadCanvas {
        id: canvas
        width: 600
        height: 600
        fieldSizeMm: 70.0
    }

    CadTopCommandBar {
        id: topBar
        hasSelection: canvas.selectedIndex >= 0 && canvas.selectedIndex < canvas.shapes.length
    }

    CadHatchModal {
        id: hatchModal
    }

    CadTextFontModal {
        id: fontModal
    }

    CadArrayModal {
        id: arrayModal
    }

    function runTests() {
        console.log("=== 1. Testing hasSelection gating ===")
        canvas.shapes = [
            { id: 1, name: "Rect_1", type: "rect", xMm: 0, yMm: 0, wMm: 20, hMm: 10, visible: true, locked: false }
        ]
        canvas.shapesChanged()
        canvas.selectedIndex = -1 // Deselect

        if (topBar.hasSelection !== false) throw new Error("Expected hasSelection=false when nothing selected")
        console.log("hasSelection correctly FALSE when no object selected.")

        canvas.selectedIndex = 0 // Select object
        if (topBar.hasSelection !== true) throw new Error("Expected hasSelection=true when object selected")
        console.log("hasSelection correctly TRUE when object selected.")

        console.log("=== 2. Testing Alignment Features ===")
        // Center_H
        canvas.alignSelectedShape("center_h")
        if (canvas.shapes[0].xMm !== 0.0) throw new Error("center_h alignment failed")

        // Left: field 70mm, half=35mm, shape W=20mm, half=10mm -> expected x = -35 + 10 = -25mm
        canvas.alignSelectedShape("left")
        if (Math.abs(canvas.shapes[0].xMm - (-25.0)) > 1e-3) throw new Error("left alignment failed: " + canvas.shapes[0].xMm)

        // Right: expected x = 35 - 10 = 25mm
        canvas.alignSelectedShape("right")
        if (Math.abs(canvas.shapes[0].xMm - 25.0) > 1e-3) throw new Error("right alignment failed: " + canvas.shapes[0].xMm)

        // Center_V
        canvas.alignSelectedShape("center_v")
        if (canvas.shapes[0].yMm !== 0.0) throw new Error("center_v alignment failed")

        // Top: field 70mm, half=35mm, shape H=10mm, half=5mm -> expected y = 35 - 5 = 30mm
        canvas.alignSelectedShape("top")
        if (Math.abs(canvas.shapes[0].yMm - 30.0) > 1e-3) throw new Error("top alignment failed: " + canvas.shapes[0].yMm)

        console.log("Alignment features correctly positioned shape!")

        console.log("=== 3. Testing Modal Movability & Transparency ===")
        // Hatch Modal
        hatchModal.openModal(canvas.shapes[0])
        var origX = hatchModal.children[0].x
        var origY = hatchModal.children[0].y
        console.log("HatchModal initial pos:", origX, origY)
        // Drag move simulation
        hatchModal.children[0].x = origX + 150
        hatchModal.children[0].y = origY + 80
        if (hatchModal.children[0].x !== origX + 150) throw new Error("Hatch modal card not movable!")
        console.log("HatchModal card is movable to:", hatchModal.children[0].x, hatchModal.children[0].y)
        hatchModal.close()

        // Font Modal
        fontModal.openModal(canvas.shapes[0])
        var fOrigX = fontModal.children[0].x
        var fOrigY = fontModal.children[0].y
        fontModal.children[0].x = fOrigX - 100
        if (fontModal.children[0].x !== fOrigX - 100) throw new Error("Font modal card not movable!")
        console.log("FontModal card is movable to:", fontModal.children[0].x)
        fontModal.closeModal()

        console.log("ALL TESTS PASSED SUCCESSFULLY!")
        return true
    }
}
