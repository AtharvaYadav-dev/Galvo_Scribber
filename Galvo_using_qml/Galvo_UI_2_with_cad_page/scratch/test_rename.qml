import QtQuick
import '../qml/components/cad'

Item {
    id: root
    width: 800
    height: 600

    CadCanvas {
        id: canvas
        shapes: [
            { id: 1, name: 'Rect_1', type: 'rect', xMm: 0, yMm: 0, wMm: 10, hMm: 10, visible: true, locked: false }
        ]
    }

    CadInspectorPanel {
        id: inspector
        shapesModel: canvas.shapes
        selectedIndex: 0
        onShapeRenamed: function(idx, newName) {
            canvas.renameShape(idx, newName)
        }
    }

    Component.onCompleted: {
        console.log('Original name:', canvas.shapes[0].name)
        inspector.shapeRenamed(0, 'CustomLaserBadge')
        console.log('After rename:', canvas.shapes[0].name)
        if (canvas.shapes[0].name !== 'CustomLaserBadge') {
            console.error('FAIL: rename did not update!')
            Qt.quit()
        }
        console.log('SUCCESS: rename verified!')
    }
}
