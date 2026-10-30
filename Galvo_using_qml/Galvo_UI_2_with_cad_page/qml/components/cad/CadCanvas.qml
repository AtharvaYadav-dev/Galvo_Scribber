import QtQuick
import QtQuick.Controls
import "../.."

Item {
    id: root

    property bool interactionBlocked: false

    // Galvo Machine envelope & Optical Alignment in mm
    property real fieldSizeMm: (typeof cad !== "undefined" && cad && cad.fieldSize > 0) ? cad.fieldSize : 110.0
    property real fieldOffsetX: (typeof cad !== "undefined" && cad) ? cad.offsetX : 0.0
    property real fieldOffsetY: (typeof cad !== "undefined" && cad) ? cad.offsetY : 0.0
    property real fieldAngleDeg: (typeof cad !== "undefined" && cad) ? cad.fieldAngle : 0.0
    property real g1ScalePct: (typeof settings !== "undefined" && settings) ? settings.g1Scale : 100.0
    property real g2ScalePct: (typeof settings !== "undefined" && settings) ? settings.g2Scale : 100.0

    // Viewport Navigation
    property real zoomScale: 2.5 // Screen pixels per mm (initial 2.5px = 1mm)
    property real panOffsetX: 0.0
    property real panOffsetY: 0.0

    // Center optical origin in canvas pixel coordinates
    readonly property real originX: (width / 2) + panOffsetX
    readonly property real originY: (height / 2) + panOffsetY

    function requestPaint() {
        if (canvas) canvas.requestPaint()
    }

    property bool initialFitDone: false

    onOriginXChanged: canvas.requestPaint()
    onOriginYChanged: canvas.requestPaint()
    onZoomScaleChanged: canvas.requestPaint()
    onFieldOffsetXChanged: canvas.requestPaint()
    onFieldOffsetYChanged: canvas.requestPaint()
    onFieldAngleDegChanged: canvas.requestPaint()
    onWidthChanged: {
        canvas.requestPaint()
        if (!initialFitDone && width > 100 && height > 100) {
            initialFitDone = true
            fitField()
        }
    }
    onHeightChanged: {
        canvas.requestPaint()
        if (!initialFitDone && width > 100 && height > 100) {
            initialFitDone = true
            fitField()
        }
    }
    onFieldSizeMmChanged: {
        fitField()
    }

    // Dynamic Bidirectional Hardware Sync with CadBridge and SettingsBridge
    Connections {
        target: (typeof cad !== "undefined") ? cad : null
        function onFieldSettingsChanged(fSize, offX, offY, angle) {
            root.fieldSizeMm = fSize
            root.fieldOffsetX = offX
            root.fieldOffsetY = offY
            root.fieldAngleDeg = angle
            root.fitField()
            canvas.requestPaint()
        }
        function onFieldSizeChanged(fSize) {
            root.fieldSizeMm = fSize
            root.fitField()
            canvas.requestPaint()
        }
        function onCadStateChanged() {
            if (typeof cad !== "undefined" && cad) {
                root.fieldSizeMm = cad.fieldSize
                root.fieldOffsetX = cad.offsetX
                root.fieldOffsetY = cad.offsetY
                root.fieldAngleDeg = cad.fieldAngle
            }
            canvas.requestPaint()
        }
    }

    Connections {
        target: (typeof settings !== "undefined") ? settings : null
        function onFieldSettingsChanged(fSize, offX, offY, angle) {
            root.fieldSizeMm = fSize
            root.fieldOffsetX = offX
            root.fieldOffsetY = offY
            root.fieldAngleDeg = angle
            root.fitField()
            canvas.requestPaint()
        }
        function onAdvancedConfigChanged() {
            if (typeof settings !== "undefined" && settings) {
                root.g1ScalePct = settings.g1Scale
                root.g2ScalePct = settings.g2Scale
            }
            canvas.requestPaint()
        }
    }

    Component.onCompleted: {
        if (typeof cad !== "undefined" && cad) {
            root.fieldSizeMm = cad.fieldSize
            root.fieldOffsetX = cad.offsetX
            root.fieldOffsetY = cad.offsetY
            root.fieldAngleDeg = cad.fieldAngle
        }
        Qt.callLater(fitField)
    }

    // Live mouse telemetry in millimeters relative to Galvo optical center (0,0)
    property real mouseCoordMmX: 0.0
    property real mouseCoordMmY: 0.0

    // Selected shape index (-1 when nothing is selected)
    property int selectedIndex: -1
    property int currentPenId: 0

    // Shapes data model (starts empty for clean project)
    property var shapes: []

    signal shapeSelected(var shape)
    signal shapeModified(var shape)
    signal hatchTriggered(var shape)

    // Undo / Redo History Management
    property var undoStack: []
    property var redoStack: []
    property int maxHistory: 40
    readonly property bool canUndo: undoStack.length > 0
    readonly property bool canRedo: redoStack.length > 0

    function pushUndoState() {
        var snap = JSON.stringify(shapes)
        var newStack = undoStack.slice()
        newStack.push(snap)
        if (newStack.length > maxHistory) newStack.shift()
        undoStack = newStack
        redoStack = []
    }

    function undo() {
        if (undoStack.length === 0) {
            if (typeof cad !== "undefined" && cad) cad.set_status_message("Nothing to undo.")
            return
        }
        var curSnap = JSON.stringify(shapes)
        var newRedo = redoStack.slice()
        newRedo.push(curSnap)
        redoStack = newRedo

        var newUndo = undoStack.slice()
        var prev = newUndo.pop()
        undoStack = newUndo

        shapes = JSON.parse(prev)
        if (selectedIndex >= shapes.length) selectedIndex = shapes.length - 1
        shapesChanged()
        canvas.requestPaint()
        if (typeof cad !== "undefined" && cad) {
            cad.updateShapes(shapes)
            cad.set_status_message("Undo successful.")
        }
    }

    function redo() {
        if (redoStack.length === 0) {
            if (typeof cad !== "undefined" && cad) cad.set_status_message("Nothing to redo.")
            return
        }
        var curSnap = JSON.stringify(shapes)
        var newUndo = undoStack.slice()
        newUndo.push(curSnap)
        undoStack = newUndo

        var newRedo = redoStack.slice()
        var next = newRedo.pop()
        redoStack = newRedo

        shapes = JSON.parse(next)
        if (selectedIndex >= shapes.length) selectedIndex = shapes.length - 1
        shapesChanged()
        canvas.requestPaint()
        if (typeof cad !== "undefined" && cad) {
            cad.updateShapes(shapes)
            cad.set_status_message("Redo successful.")
        }
    }

    // Grouping & Ungrouping Engine
    function groupSelectedShapes() {
        if (shapes.length < 2) {
            if (typeof cad !== "undefined" && cad) cad.set_status_message("Need at least 2 objects on canvas to create a group.")
            return
        }
        pushUndoState()
        var groupChildren = shapes.slice()
        var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
        for (var i = 0; i < groupChildren.length; i++) {
            var s = groupChildren[i]
            var hw = (s.wMm || 10.0) / 2.0
            var hh = (s.hMm || 10.0) / 2.0
            if ((s.xMm - hw) < minX) minX = s.xMm - hw
            if ((s.xMm + hw) > maxX) maxX = s.xMm + hw
            if ((s.yMm - hh) < minY) minY = s.yMm - hh
            if ((s.yMm + hh) > maxY) maxY = s.yMm + hh
        }
        var groupCx = round2((minX + maxX) / 2.0)
        var groupCy = round2((minY + maxY) / 2.0)
        var groupW = round2(maxX - minX)
        var groupH = round2(maxY - minY)

        var relativeChildren = []
        for (var j = 0; j < groupChildren.length; j++) {
            var ch = Object.assign({}, groupChildren[j])
            ch.relX = round3(ch.xMm - groupCx)
            ch.relY = round3(ch.yMm - groupCy)
            relativeChildren.push(ch)
        }

        var newGroup = {
            id: 1,
            name: "Group_1",
            type: "group",
            xMm: groupCx,
            yMm: groupCy,
            wMm: groupW,
            hMm: groupH,
            rotation: 0,
            penId: root.currentPenId,
            visible: true,
            locked: false,
            children: relativeChildren
        }

        shapes = [newGroup]
        selectedIndex = 0
        shapesChanged()
        shapeSelected(newGroup)
        canvas.requestPaint()
        if (typeof cad !== "undefined" && cad) {
            cad.updateShapes(shapes)
            cad.set_status_message("Grouped " + relativeChildren.length + " objects into " + newGroup.name + ".")
        }
    }

    function ungroupSelectedShape() {
        if (selectedIndex < 0 || selectedIndex >= shapes.length) {
            if (typeof cad !== "undefined" && cad) cad.set_status_message("Select a group entity to ungroup.")
            return
        }
        var target = shapes[selectedIndex]
        if (target.type !== "group" || !target.children || target.children.length === 0) {
            if (typeof cad !== "undefined" && cad) cad.set_status_message("Selected object is not a group.")
            return
        }
        pushUndoState()
        var gx = target.xMm || 0.0
        var gy = target.yMm || 0.0
        var unpacked = []
        for (var i = 0; i < target.children.length; i++) {
            var ch = Object.assign({}, target.children[i])
            ch.xMm = round2(gx + (ch.relX !== undefined ? ch.relX : 0))
            ch.yMm = round2(gy + (ch.relY !== undefined ? ch.relY : 0))
            delete ch.relX
            delete ch.relY
            ch.id = unpacked.length + 1
            unpacked.push(ch)
        }

        var copy = shapes.slice()
        copy.splice(selectedIndex, 1)
        for (var k = 0; k < unpacked.length; k++) {
            copy.splice(selectedIndex + k, 0, unpacked[k])
        }
        shapes = copy
        selectedIndex = Math.min(shapes.length - 1, selectedIndex)
        shapesChanged()
        shapeSelected(shapes[selectedIndex])
        canvas.requestPaint()
        if (typeof cad !== "undefined" && cad) {
            cad.updateShapes(shapes)
            cad.set_status_message("Ungrouped into " + unpacked.length + " individual objects.")
        }
    }

    clip: true

    // Active CAD tool: 'select', 'node', 'line', 'curve', 'rect', 'circle', 'polygon', etc.
    property string activeTool: "select"

    // Interactive Node / Vertex Edit Engine
    property int hoveredNodePathIndex: -1
    property int hoveredNodePointIndex: -1
    property int draggingNodePathIndex: -1
    property int draggingNodePointIndex: -1
    property var activeNodePathPts: []

    function finishNodePolyline() {
        if (activeNodePathPts.length >= 2) {
            pushUndoState()
            var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
            for (var i = 0; i < activeNodePathPts.length; i++) {
                var p = activeNodePathPts[i]
                if (p[0] < minX) minX = p[0]
                if (p[0] > maxX) maxX = p[0]
                if (p[1] < minY) minY = p[1]
                if (p[1] > maxY) maxY = p[1]
            }
            var pcx = round2((minX + maxX) / 2.0)
            var pcy = round2((minY + maxY) / 2.0)
            var pw = round2(Math.max(1.0, maxX - minX))
            var ph = round2(Math.max(1.0, maxY - minY))

            var relPts = []
            for (var j = 0; j < activeNodePathPts.length; j++) {
                relPts.push([round3(activeNodePathPts[j][0] - pcx), round3(activeNodePathPts[j][1] - pcy)])
            }

            var newPoly = {
                id: shapes.length + 1,
                name: "Polyline_" + (shapes.length + 1),
                type: "polygon",
                xMm: pcx,
                yMm: pcy,
                wMm: pw,
                hMm: ph,
                rotation: 0,
                penId: root.currentPenId,
                hatched: false,
                visible: true,
                locked: false,
                paths: [relPts]
            }

            var updated = shapes.slice()
            updated.push(newPoly)
            shapes = updated
            shapesChanged()
            selectedIndex = shapes.length - 1
            shapeSelected(newPoly)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
            }
        }
        activeNodePathPts = []
        activeTool = "select"
        toolFinished()
        canvas.requestPaint()
    }

    function recalculateShapeBounds(shp) {
        if (!shp || !shp.paths || shp.paths.length === 0) return
        var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
        for (var p = 0; p < shp.paths.length; p++) {
            var sub = shp.paths[p]
            for (var k = 0; k < sub.length; k++) {
                if (sub[k][0] < minX) minX = sub[k][0]
                if (sub[k][0] > maxX) maxX = sub[k][0]
                if (sub[k][1] < minY) minY = sub[k][1]
                if (sub[k][1] > maxY) maxY = sub[k][1]
            }
        }
        if (minX !== Infinity && maxX !== -Infinity) {
            shp.wMm = round2(Math.max(1.0, maxX - minX))
            shp.hMm = round2(Math.max(1.0, maxY - minY))
        }
    }
    signal toolFinished()

    // Interactive shape drawing state
    property bool isDrawingShape: false
    property real drawStartMmX: 0.0
    property real drawStartMmY: 0.0
    property real drawCurrentMmX: 0.0
    property real drawCurrentMmY: 0.0
    property var drawFreehandPts: []

    function round2(v) { return Math.round(v * 100) / 100 }
    function round3(v) { return Math.round(v * 1000) / 1000 }

    function zoomIn() {
        zoomScale = Math.min(12.0, zoomScale * 1.25)
    }

    function zoomOut() {
        zoomScale = Math.max(0.4, zoomScale / 1.25)
    }

    function fitField() {
        if (width <= 50 || height <= 50) return
        panOffsetX = 0
        panOffsetY = 0
        var margin = 48
        var availW = Math.max(50, width - margin * 2)
        var availH = Math.max(50, height - margin * 2)
        var fSize = (fieldSizeMm > 0) ? fieldSizeMm : 70.0
        var effW = fSize + Math.abs(fieldOffsetX) * 2
        var effH = fSize + Math.abs(fieldOffsetY) * 2
        var fitScale = Math.min(availW / effW, availH / effH)
        zoomScale = Math.max(0.4, Math.min(12.0, fitScale))
        canvas.requestPaint()
    }

    function zoomFit() {
        fitField()
    }

    function fitSelectionToField() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) return
            pushUndoState()
            var targetField = (fieldSizeMm > 0) ? fieldSizeMm * 0.9 : 60.0
            var curW = s.wMm > 0 ? s.wMm : 10.0
            var curH = s.hMm > 0 ? s.hMm : 10.0
            var factor = Math.min(targetField / curW, targetField / curH)
            
            s.wMm = round2(s.wMm * factor)
            s.hMm = round2(s.hMm * factor)
            s.xMm = 0.0
            s.yMm = 0.0
            
            if (s.paths && s.paths.length > 0) {
                for (var p = 0; p < s.paths.length; p++) {
                    var sub = s.paths[p]
                    for (var k = 0; k < sub.length; k++) {
                        sub[k][0] = round3(sub[k][0] * factor)
                        sub[k][1] = round3(sub[k][1] * factor)
                    }
                }
            }
            s.hatch_lines = []
            if (s.hatched && typeof cad !== "undefined" && cad) {
                s.hatch_lines = cad.computeHatchPreviewLines(s)
            }
            var copyFit = shapes.slice()
            copyFit[selectedIndex] = s
            shapes = copyFit
            shapesChanged()
            shapeModified(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
            }
            fitField()
            canvas.requestPaint()
        }
    }

    function centerSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {
                if (typeof cad !== "undefined" && cad) cad.set_status_message("Object is locked.")
                return
            }
            pushUndoState()
            s.xMm = 0
            s.yMm = 0
            s.hatch_lines = []
            if (s.hatched && typeof cad !== "undefined" && cad) {
                s.hatch_lines = cad.computeHatchPreviewLines(s)
            }
            var copyCenter = shapes.slice()
            copyCenter[selectedIndex] = s
            shapes = copyCenter
            shapesChanged()
            shapeModified(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
            }
            canvas.requestPaint()
        }
    }

    function alignSelectedShape(mode) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot align locked object '" + (s.name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            var fSize = (fieldSizeMm > 0) ? fieldSizeMm : 70.0
            var halfF = fSize / 2.0
            var halfW = (s.wMm || 10.0) / 2.0
            var halfH = (s.hMm || 10.0) / 2.0

            if (mode === "left") {
                s.xMm = round2(-halfF + halfW)
            } else if (mode === "right") {
                s.xMm = round2(halfF - halfW)
            } else if (mode === "center_h") {
                s.xMm = 0.0
            } else if (mode === "top") {
                s.yMm = round2(halfF - halfH)
            } else if (mode === "bottom") {
                s.yMm = round2(-halfF + halfH)
            } else if (mode === "center_v") {
                s.yMm = 0.0
            } else if (mode === "center") {
                s.xMm = 0.0
                s.yMm = 0.0
            }

            s.hatch_lines = []
            if (s.hatched && typeof cad !== "undefined" && cad) {
                s.hatch_lines = cad.computeHatchPreviewLines(s)
            }
            var copyAlign = shapes.slice()
            copyAlign[selectedIndex] = s
            shapes = copyAlign
            shapesChanged()
            shapeModified(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
                cad.set_status_message("Aligned " + (s.name || "Object") + " to " + mode + ".")
            }
            canvas.requestPaint()
        }
    }

    function rotateSelectedShape(deg) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot rotate locked object '" + (s.name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            s.rotation = Math.round(((s.rotation + deg) % 360 + 360) % 360)
            s.hatch_lines = []
            if (s.hatched && typeof cad !== "undefined" && cad) {
                s.hatch_lines = cad.computeHatchPreviewLines(s)
            }
            var copyRot = shapes.slice()
            copyRot[selectedIndex] = s
            shapes = copyRot
            shapesChanged()
            shapeModified(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
            }
            canvas.requestPaint()
        }
    }

    function unhatchSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot unhatch locked object '" + (s.name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            s.hatched = false
            s.mark_contour = true
            s.hatch_lines = []
            var copy = shapes.slice()
            copy[selectedIndex] = s
            shapes = copy
            shapesChanged()
            shapeModified(s)
            shapeSelected(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
                cad.set_status_message("Removed hatch infill from '" + (s.name || "Object") + "'.")
            }
            canvas.requestPaint()
        }
    }

    function deleteSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            if (shapes[selectedIndex].locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot delete locked object '" + (shapes[selectedIndex].name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            var copy = shapes.slice()
            var deletedItem = copy.splice(selectedIndex, 1)[0]
            shapes = copy
            selectedIndex = Math.min(selectedIndex, shapes.length - 1)
            shapesChanged()
            if (selectedIndex >= 0 && selectedIndex < shapes.length) {
                shapeSelected(shapes[selectedIndex])
            } else {
                shapeSelected(null)
            }
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
                cad.set_status_message("Deleted '" + (deletedItem.name || "Object") + "'.")
            }
            canvas.requestPaint()
        }
    }

    function duplicateSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var orig = shapes[selectedIndex]
            pushUndoState()
            var clone = {
                id: shapes.length + 1,
                name: orig.name + "_Copy",
                type: orig.type,
                text: orig.text || "",
                xMm: orig.xMm + 5.0,
                yMm: orig.yMm - 5.0,
                wMm: orig.wMm,
                hMm: orig.hMm,
                rotation: orig.rotation,
                penId: orig.penId,
                hatched: orig.hatched,
                visible: true,
                locked: false
            }
            if (orig.paths) clone.paths = JSON.parse(JSON.stringify(orig.paths))
            if (orig.points) clone.points = JSON.parse(JSON.stringify(orig.points))
            if (orig.fontFamily) clone.fontFamily = orig.fontFamily
            if (orig.fontType) clone.fontType = orig.fontType
            if (orig.textAlign) clone.textAlign = orig.textAlign
            if (orig.charSpace) clone.charSpace = orig.charSpace
            if (orig.lineSpace) clone.lineSpace = orig.lineSpace
            if (orig.bold) clone.bold = orig.bold
            if (orig.italic) clone.italic = orig.italic

            var copy = shapes.slice()
            copy.push(clone)
            shapes = copy
            shapesChanged()
            selectedIndex = shapes.length - 1
            shapeSelected(clone)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
                cad.set_status_message("Duplicated '" + orig.name + "'.")
            }
            canvas.requestPaint()
        }
    }

    function toggleShapeVisibility(idx) {
        if (idx >= 0 && idx < shapes.length) {
            var copy = shapes.slice()
            var s = Object.assign({}, copy[idx])
            s.visible = (s.visible === false) ? true : false
            copy[idx] = s
            shapes = copy
            if (selectedIndex === idx && !s.visible) {
                selectedIndex = -1
                shapeSelected(null)
            }
            shapesChanged()
            if (canvas) canvas.requestPaint()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
                cad.set_status_message((s.name || "Object") + (s.visible ? " is now visible." : " is hidden from canvas."))
            }
        }
    }

    function toggleShapeLock(idx) {
        if (idx >= 0 && idx < shapes.length) {
            var copy = shapes.slice()
            var s = Object.assign({}, copy[idx])
            s.locked = !s.locked
            copy[idx] = s
            shapes = copy
            shapesChanged()
            if (canvas) canvas.requestPaint()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
                cad.set_status_message((s.name || "Object") + (s.locked ? " is locked against movement." : " is unlocked."))
            }
        }
    }

    function renameShape(idx, newName) {
        if (idx >= 0 && idx < shapes.length && newName && newName.trim().length > 0) {
            var copy = shapes.slice()
            var s = Object.assign({}, copy[idx])
            s.name = newName.trim()
            copy[idx] = s
            shapes = copy
            shapesChanged()
            canvas.requestPaint()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
                cad.set_status_message("Renamed object to '" + s.name + "'.")
            }
        }
    }

    // High-performance Vector Canvas
    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.FramebufferObject
        renderStrategy: Canvas.Immediate

        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var isDark = Theme.isDark
            var ox = root.originX
            var oy = root.originY
            var scale = root.zoomScale
            var halfFieldPx = (root.fieldSizeMm / 2) * scale

            // 1. Fill Canvas background
            ctx.fillStyle = Theme.canvasBg
            ctx.fillRect(0, 0, width, height)

            // 2. Draw Minor & Major Adaptive Grid
            var gridStepMm = 10.0
            if (scale > 5.0) gridStepMm = 2.0
            else if (scale < 1.0) gridStepMm = 20.0

            var gridStepPx = gridStepMm * scale

            ctx.lineWidth = 1
            ctx.strokeStyle = Theme.canvasGridMinor
            ctx.beginPath()

            for (var x = ox % gridStepPx; x < width; x += gridStepPx) {
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
            }
            for (var y = oy % gridStepPx; y < height; y += gridStepPx) {
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
            }
            ctx.stroke()

            // 3. Galvo Optical Bed Field Boundary (Sized, Offset & Rotated from Machine Config)
            var bedCx = ox + root.fieldOffsetX * scale
            var bedCy = oy - root.fieldOffsetY * scale

            ctx.save()
            ctx.translate(bedCx, bedCy)
            if (root.fieldAngleDeg !== 0) {
                ctx.rotate((-root.fieldAngleDeg * Math.PI) / 180)
            }

            // Fill optical bed area
            ctx.fillStyle = Theme.canvasBedFill
            ctx.fillRect(-halfFieldPx, -halfFieldPx, halfFieldPx * 2, halfFieldPx * 2)

            // Dashed bed boundary
            ctx.lineWidth = 1.5
            ctx.strokeStyle = Theme.canvasBedBorder
            ctx.setLineDash([8, 5])
            ctx.strokeRect(-halfFieldPx, -halfFieldPx, halfFieldPx * 2, halfFieldPx * 2)
            ctx.setLineDash([])

            // Corner decorative brackets for optical field
            var brk = Math.min(16, halfFieldPx * 0.25)
            ctx.strokeStyle = Theme.accentCyan
            ctx.lineWidth = 2
            ctx.beginPath()
            ctx.moveTo(-halfFieldPx, -halfFieldPx + brk); ctx.lineTo(-halfFieldPx, -halfFieldPx); ctx.lineTo(-halfFieldPx + brk, -halfFieldPx)
            ctx.moveTo(halfFieldPx - brk, -halfFieldPx); ctx.lineTo(halfFieldPx, -halfFieldPx); ctx.lineTo(halfFieldPx, -halfFieldPx + brk)
            ctx.moveTo(halfFieldPx, halfFieldPx - brk); ctx.lineTo(halfFieldPx, halfFieldPx); ctx.lineTo(halfFieldPx - brk, halfFieldPx)
            ctx.moveTo(-halfFieldPx + brk, halfFieldPx); ctx.lineTo(-halfFieldPx, halfFieldPx); ctx.lineTo(-halfFieldPx, halfFieldPx - brk)
            ctx.stroke()

            // Optical Field Internal Center Axes (Dashed light cyan crosshair)
            ctx.strokeStyle = Qt.rgba(0.0, 0.85, 0.95, 0.35)
            ctx.lineWidth = 1
            ctx.setLineDash([4, 4])
            ctx.beginPath()
            ctx.moveTo(0, -halfFieldPx); ctx.lineTo(0, halfFieldPx)
            ctx.moveTo(-halfFieldPx, 0); ctx.lineTo(halfFieldPx, 0)
            ctx.stroke()
            ctx.setLineDash([])

            // Optical Center Ring Marker
            ctx.fillStyle = Theme.accentCyan
            ctx.beginPath()
            ctx.arc(0, 0, 3.5, 0, Math.PI * 2)
            ctx.fill()

            // Field Dimensions & Offset Info Watermark Text on Bed
            ctx.font = "10px Consolas, monospace"
            ctx.fillStyle = isDark ? Qt.rgba(1, 1, 1, 0.40) : Qt.rgba(0, 0, 0, 0.40)
            ctx.textAlign = "left"
            ctx.textBaseline = "top"
            var fieldInfoStr = root.fieldSizeMm.toFixed(1) + " × " + root.fieldSizeMm.toFixed(1) + " mm [Lens Area]"
            if (Math.abs(root.fieldOffsetX) > 0.01 || Math.abs(root.fieldOffsetY) > 0.01 || Math.abs(root.fieldAngleDeg) > 0.01) {
                fieldInfoStr += "  (ΔX=" + root.fieldOffsetX.toFixed(1) + ", ΔY=" + root.fieldOffsetY.toFixed(1) + "mm, θ=" + root.fieldAngleDeg.toFixed(1) + "°)"
            }
            ctx.fillText(fieldInfoStr, -halfFieldPx + 8, -halfFieldPx + 8)

            ctx.restore()

            // 4. Global Machine Physical Origin (0,0) Reference & Guide Line
            ctx.strokeStyle = Theme.canvasAxis
            ctx.lineWidth = 1.0
            ctx.setLineDash([3, 3])
            ctx.beginPath()
            ctx.moveTo(ox, 0); ctx.lineTo(ox, height)
            ctx.moveTo(0, oy); ctx.lineTo(width, oy)
            ctx.stroke()
            ctx.setLineDash([])

            // Machine (0,0) Center Mark
            ctx.strokeStyle = Theme.textMuted
            ctx.lineWidth = 1.5
            ctx.beginPath()
            ctx.arc(ox, oy, 4, 0, Math.PI * 2)
            ctx.stroke()

            // If offset, draw vector connection between machine origin and optical bed center
            if (Math.abs(root.fieldOffsetX) > 0.1 || Math.abs(root.fieldOffsetY) > 0.1) {
                ctx.save()
                ctx.strokeStyle = Qt.rgba(0.95, 0.65, 0.1, 0.7) // Amber offset vector
                ctx.lineWidth = 1.2
                ctx.setLineDash([4, 4])
                ctx.beginPath()
                ctx.moveTo(ox, oy)
                ctx.lineTo(bedCx, bedCy)
                ctx.stroke()
                ctx.restore()
            }

            // 5. Render Vector CAD Shapes
            for (var i = 0; i < root.shapes.length; i++) {
                var shp = root.shapes[i]
                if (shp.visible === false) continue

                var sx = ox + shp.xMm * scale
                var sy = oy - shp.yMm * scale // CAD +Y is upwards
                var sw = shp.wMm * scale
                var sh = shp.hMm * scale
                var isSel = (i === root.selectedIndex)

                var rawPenColor = Theme.getPenColor(shp.penId || 0)
                var penColor = rawPenColor
                // On dark canvas, pure black pen (#000000) is invisible against #070B14, so render with crisp high-contrast silver (#E2E8F0)
                if (Theme.isDark && (rawPenColor === "#000000" || String(rawPenColor).toLowerCase() === "#000000" || String(rawPenColor).toLowerCase() === "#000")) {
                    penColor = "#E2E8F0"
                }

                ctx.save()
                ctx.translate(sx, sy)
                if (shp.rotation !== 0) {
                    ctx.rotate((-shp.rotation * Math.PI) / 180)
                }

                ctx.strokeStyle = isSel ? (shp.locked ? "#F59E0B" : penColor) : penColor
                ctx.lineWidth = isSel ? 2.5 : 1.5

                if (shp.type === "group") {
                    if (isSel) {
                        ctx.save()
                        ctx.setLineDash([4, 4])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.5)
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                        ctx.restore()
                    }
                    if (shp.children && shp.children.length > 0) {
                        for (var ci = 0; ci < shp.children.length; ci++) {
                            var ch = shp.children[ci]
                            var cRelX = (ch.relX !== undefined ? ch.relX : 0) * scale
                            var cRelY = -(ch.relY !== undefined ? ch.relY : 0) * scale
                            var cW = (ch.wMm || 10.0) * scale
                            var cH = (ch.hMm || 10.0) * scale
                            var cPen = Theme.getPenColor((ch.penId !== undefined ? ch.penId : shp.penId) || 0)

                            ctx.save()
                            ctx.translate(cRelX, cRelY)
                            if (ch.rotation) ctx.rotate((-ch.rotation * Math.PI) / 180)
                            ctx.strokeStyle = isSel ? penColor : cPen
                            ctx.lineWidth = isSel ? 2.0 : 1.5

                            if (ch.type === "rect") {
                                ctx.strokeRect(-cW / 2, -cH / 2, cW, cH)
                            } else if (ch.type === "circle") {
                                ctx.beginPath()
                                ctx.arc(0, 0, cW / 2, 0, Math.PI * 2)
                                ctx.stroke()
                            } else if (ch.type === "text") {
                                ctx.fillStyle = isSel ? penColor : cPen
                                ctx.font = (ch.bold ? "bold " : "") + (ch.italic ? "italic " : "") + Math.round(cH * 0.75) + "px '" + (ch.fontFamily || "Segoe UI") + "', sans-serif"
                                ctx.textAlign = "center"
                                ctx.textBaseline = "alphabetic"
                                ctx.fillText(ch.text || "TEXT", 0, cH * 0.25)
                            } else if (ch.paths && ch.paths.length > 0) {
                                ctx.beginPath()
                                for (var cpi = 0; cpi < ch.paths.length; cpi++) {
                                    var subP = ch.paths[cpi]
                                    for (var cki = 0; cki < subP.length; cki++) {
                                        var pX = subP[cki][0] * scale
                                        var pY = -subP[cki][1] * scale
                                        if (cki === 0) ctx.moveTo(pX, pY)
                                        else ctx.lineTo(pX, pY)
                                    }
                                }
                                ctx.stroke()
                            }
                            ctx.restore()
                        }
                    }
                } else if (shp.type === "rect") {
                    if (!shp.hatched || shp.mark_contour !== false) {
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.45)
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                        ctx.restore()
                    }
                } else if (shp.type === "circle") {
                    ctx.beginPath()
                    ctx.arc(0, 0, sw / 2, 0, Math.PI * 2)
                    if (!shp.hatched || shp.mark_contour !== false) {
                        ctx.stroke()
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.45)
                        ctx.stroke()
                        ctx.restore()
                    }
                } else if (shp.type === "text") {
                    // If shape is not hatched, draw crisp Canvas 2D font text.
                    // If hatched, MotionPlanner vector hatch lines (drawn below) render the entity.
                    if (!shp.hatched) {
                        var txt = String(shp.text || "TEXT")
                        var fFamily = shp.fontFamily || "Segoe UI"
                        var isBold = Boolean(shp.bold)
                        var isItalic = Boolean(shp.italic)
                        var tAlign = shp.textAlign || "center"
                        var fontStyle = (isItalic ? "italic " : "") + (isBold ? "bold " : "")

                        ctx.fillStyle = penColor
                        ctx.textAlign = tAlign
                        ctx.textBaseline = "middle"

                        if (shp.circleText) {
                            // CircleText Mode: Render along circular arc
                            var cDiamMm = (shp.circleDiameter !== undefined && shp.circleDiameter > 0) ? Number(shp.circleDiameter) : 20.0
                            var cRadiusPx = (cDiamMm / 2.0) * scale
                            var baseAngleDeg = (shp.circleBaseAngle !== undefined) ? Number(shp.circleBaseAngle) : 90.0
                            var totalChars = txt.length

                            // Draw subtle circular reference path
                            ctx.save()
                            ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.25)
                            ctx.lineWidth = 1.0
                            ctx.setLineDash([3, 3])
                            ctx.beginPath()
                            ctx.arc(0, 0, cRadiusPx, 0, Math.PI * 2)
                            ctx.stroke()
                            ctx.restore()

                            if (totalChars > 0) {
                                var charWPx = Math.max(8, Math.round(sh * 0.7))
                                var angularStep = Math.min(Math.PI / 4, charWPx / Math.max(10, cRadiusPx))
                                var startAngle = (baseAngleDeg * Math.PI / 180.0) + (totalChars - 1) * angularStep / 2.0
                                ctx.font = fontStyle + Math.max(8, Math.round(sh * 0.85)) + "px '" + fFamily + "', sans-serif"

                                for (var cIdx = 0; cIdx < totalChars; cIdx++) {
                                    var theta = startAngle - cIdx * angularStep
                                    var chX = cRadiusPx * Math.cos(theta)
                                    var chY = -cRadiusPx * Math.sin(theta) // Invert Y for canvas
                                    var rotTangent = -theta + Math.PI / 2.0

                                    ctx.save()
                                    ctx.translate(chX, chY)
                                    ctx.rotate(rotTangent)
                                    ctx.fillText(txt[cIdx], 0, 0)
                                    ctx.restore()
                                }
                            }
                        } else {
                            // Linear Text Mode: Multi-line and alignment support (alphabetic baseline prevents Marathi/Devanagari font descent shift)
                            var lines = txt.split("\n")
                            var lineH = sh / Math.max(1, lines.length)
                            ctx.font = fontStyle + Math.max(8, Math.round(lineH * 0.85)) + "px '" + fFamily + "', sans-serif"
                            ctx.textBaseline = "alphabetic"

                            for (var lIdx = 0; lIdx < lines.length; lIdx++) {
                                var lY = (-sh / 2) + (lIdx + 0.75) * lineH
                                var lX = 0
                                if (tAlign === "left") lX = -sw / 2
                                else if (tAlign === "right") lX = sw / 2
                                ctx.fillText(lines[lIdx], lX, lY)
                            }
                        }
                    }
                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    // 1. White backing card: only if explicitly enabled on shape, otherwise clean dark CAD background
                    if (Boolean(shp.showBackground)) {
                        ctx.fillStyle = "#FFFFFF"
                        ctx.fillRect(-sw / 2, -sh / 2, sw, sh)
                    }

                    // 2. Crisp barcode modules & bars in laser pen color
                    if (!shp.hatched) {
                        ctx.fillStyle = Boolean(shp.showBackground) ? ((penColor === "#FFFFFF" || penColor === "#ffffff") ? "#111827" : "#0A0F1D") : penColor
                        if (shp.rects && shp.rects.length > 0) {
                            var oLap = 0.5 // Eliminates Porter-Duff subpixel antialiasing gaps between adjacent module rows
                            for (var ri = 0; ri < shp.rects.length; ri++) {
                                var rc = shp.rects[ri]
                                var rx = rc.x * scale
                                var ry = -rc.y * scale
                                var rw = rc.w * scale
                                var rh = rc.h * scale
                                ctx.fillRect(rx, ry, rw + (rw > 0 ? oLap : 0), rh + (rh > 0 ? oLap : 0))
                            }
                        } else if (shp.paths && shp.paths.length > 0) {
                            ctx.beginPath()
                            for (var pi = 0; pi < shp.paths.length; pi++) {
                                var sp = shp.paths[pi]
                                if (sp.length >= 2) {
                                    ctx.moveTo(sp[0][0] * scale, -sp[0][1] * scale)
                                    for (var ki = 1; ki < sp.length; ki++) {
                                        ctx.lineTo(sp[ki][0] * scale, -sp[ki][1] * scale)
                                    }
                                }
                            }
                            ctx.fill()
                        }
                    } else {
                        // When hatched: stroke light module borders so vector hatch lines inside are crisp and visible
                        ctx.strokeStyle = penColor
                        ctx.lineWidth = 0.75
                        if (shp.rects && shp.rects.length > 0) {
                            for (var ri2 = 0; ri2 < shp.rects.length; ri2++) {
                                var rc2 = shp.rects[ri2]
                                ctx.strokeRect(rc2.x * scale, -rc2.y * scale, rc2.w * scale, rc2.h * scale)
                            }
                        }
                    }

                    // 3. Laser pen color perimeter indicator border
                    ctx.strokeStyle = penColor
                    ctx.lineWidth = 1.5
                    ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                } else if (shp.type === "polygon" || shp.type === "dxf" || shp.type === "svg" || shp.type === "line") {
                    if (shp.paths && shp.paths.length > 0) {
                        ctx.beginPath()
                        for (var p = 0; p < shp.paths.length; p++) {
                            var sub = shp.paths[p]
                            if (!sub || sub.length < 2) continue
                            ctx.moveTo(sub[0][0] * scale, -sub[0][1] * scale)
                            for (var k = 1; k < sub.length; k++) {
                                ctx.lineTo(sub[k][0] * scale, -sub[k][1] * scale)
                            }
                        }
                        ctx.stroke()
                    } else if (shp.points && shp.points.length >= 2) {
                        ctx.beginPath()
                        ctx.moveTo(shp.points[0][0] * scale, -shp.points[0][1] * scale)
                        for (var k = 1; k < shp.points.length; k++) {
                            ctx.lineTo(shp.points[k][0] * scale, -shp.points[k][1] * scale)
                        }
                        ctx.stroke()
                    }
                }

                // Selection Bounding Box & 8 Resize Handles
                if (isSel) {
                    ctx.strokeStyle = Theme.canvasSelectionBox
                    ctx.lineWidth = 1.2
                    ctx.setLineDash([4, 3])
                    var pad = 4
                    ctx.strokeRect(-sw / 2 - pad, -sh / 2 - pad, sw + pad * 2, sh + pad * 2)
                    ctx.setLineDash([])

                    ctx.fillStyle = Theme.canvasHandleFill
                    ctx.strokeStyle = Theme.canvasHandleBorder
                    ctx.lineWidth = 1
                    var hs = 6
                    var handlePts = [
                        { x: -sw / 2 - pad, y: -sh / 2 - pad },
                        { x: 0,             y: -sh / 2 - pad },
                        { x: sw / 2 + pad,  y: -sh / 2 - pad },
                        { x: sw / 2 + pad,  y: 0 },
                        { x: sw / 2 + pad,  y: sh / 2 + pad },
                        { x: 0,             y: sh / 2 + pad },
                        { x: -sw / 2 - pad, y: sh / 2 + pad },
                        { x: -sw / 2 - pad, y: 0 }
                    ]
                    for (var h = 0; h < handlePts.length; h++) {
                        ctx.fillRect(handlePts[h].x - hs / 2, handlePts[h].y - hs / 2, hs, hs)
                        ctx.strokeRect(handlePts[h].x - hs / 2, handlePts[h].y - hs / 2, hs, hs)
                    }

                    // Vertex Node Handles for Node / Vertex Edit Tool
                    if (root.activeTool === "node") {
                        var nodeRad = 5.0
                        if (shp.paths && shp.paths.length > 0) {
                            for (var npi = 0; npi < shp.paths.length; npi++) {
                                var nsub = shp.paths[npi]
                                for (var nki = 0; nki < nsub.length; nki++) {
                                    var vX = nsub[nki][0] * scale
                                    var vY = -nsub[nki][1] * scale
                                    var isHovN = (root.hoveredNodePathIndex === npi && root.hoveredNodePointIndex === nki)
                                    var isDragN = (root.draggingNodePathIndex === npi && root.draggingNodePointIndex === nki)
                                    ctx.beginPath()
                                    ctx.arc(vX, vY, (isHovN || isDragN) ? nodeRad + 2 : nodeRad, 0, Math.PI * 2)
                                    ctx.fillStyle = (isHovN || isDragN) ? Theme.accentCyan : "#FFFFFF"
                                    ctx.fill()
                                    ctx.strokeStyle = Theme.isDark ? "#0F172A" : "#1E293B"
                                    ctx.lineWidth = 1.5
                                    ctx.stroke()
                                }
                            }
                        }
                    }
                }

                ctx.restore()

                // Render High-Precision Vector Hatch Infill Lines (computed by MotionPlanner)
                if (shp.hatched) {
                    if ((!shp.hatch_lines || shp.hatch_lines.length === 0) && typeof cad !== "undefined" && cad) {
                        shp.hatch_lines = cad.computeHatchPreviewLines(shp)
                    }
                    if (shp.hatch_lines && shp.hatch_lines.length > 0) {
                        ctx.save()
                        ctx.lineWidth = 0.9
                        for (var hl = 0; hl < shp.hatch_lines.length; hl++) {
                            var hline = shp.hatch_lines[hl]
                            var rawHCol = (hline.pen_id !== undefined)
                                ? Theme.getPenColor(hline.pen_id)
                                : rawPenColor
                            var hPenCol = rawHCol
                            if (Theme.isDark && (rawHCol === "#000000" || String(rawHCol).toLowerCase() === "#000000" || String(rawHCol).toLowerCase() === "#000")) {
                                hPenCol = "#94A3B8"
                            }
                            ctx.strokeStyle = hPenCol
                            ctx.beginPath()
                            var hpts = hline.points
                            if (hpts && hpts.length >= 2) {
                                ctx.moveTo(ox + hpts[0][0] * scale, oy - hpts[0][1] * scale)
                                for (var pi = 1; pi < hpts.length; pi++) {
                                    ctx.lineTo(ox + hpts[pi][0] * scale, oy - hpts[pi][1] * scale)
                                }
                                ctx.stroke()
                            }
                        }
                        ctx.restore()
                    }
                }
            }

            // 6. Interactive Shape Drawing Rubber-Band Live Preview
            if (root.isDrawingShape && root.activeTool !== "select") {
                var dsx0 = ox + root.drawStartMmX * scale
                var dsy0 = oy - root.drawStartMmY * scale
                var dsx1 = ox + root.drawCurrentMmX * scale
                var dsy1 = oy - root.drawCurrentMmY * scale

                ctx.save()
                ctx.strokeStyle = Theme.accentCyan
                ctx.lineWidth = 1.8
                ctx.setLineDash([6, 4])

                if (root.activeTool === "rect") {
                    var rleft = Math.min(dsx0, dsx1)
                    var rtop = Math.min(dsy0, dsy1)
                    var rwidth = Math.abs(dsx1 - dsx0)
                    var rheight = Math.abs(dsy1 - dsy0)
                    ctx.strokeRect(rleft, rtop, rwidth, rheight)
                } else if (root.activeTool === "circle") {
                    var radPx = Math.hypot(dsx1 - dsx0, dsy1 - dsy0)
                    ctx.beginPath()
                    ctx.arc(dsx0, dsy0, radPx, 0, Math.PI * 2)
                    ctx.stroke()
                } else if (root.activeTool === "polygon") {
                    var radPolyPx = Math.hypot(dsx1 - dsx0, dsy1 - dsy0)
                    var pSides = 5
                    ctx.beginPath()
                    for (var psi = 0; psi <= pSides; psi++) {
                        var pAng = -Math.PI / 2 + (psi * 2 * Math.PI) / pSides
                        var pxx = dsx0 + radPolyPx * Math.cos(pAng)
                        var pyy = dsy0 + radPolyPx * Math.sin(pAng)
                        if (psi === 0) ctx.moveTo(pxx, pyy)
                        else ctx.lineTo(pxx, pyy)
                    }
                    ctx.stroke()
                } else if (root.activeTool === "line") {
                    ctx.beginPath()
                    ctx.moveTo(dsx0, dsy0)
                    ctx.lineTo(dsx1, dsy1)
                    ctx.stroke()
                } else if (root.activeTool === "curve" && root.drawFreehandPts.length >= 2) {
                    ctx.beginPath()
                    ctx.moveTo(ox + root.drawFreehandPts[0][0] * scale, oy - root.drawFreehandPts[0][1] * scale)
                    for (var fi = 1; fi < root.drawFreehandPts.length; fi++) {
                        ctx.lineTo(ox + root.drawFreehandPts[fi][0] * scale, oy - root.drawFreehandPts[fi][1] * scale)
                    }
                    ctx.stroke()
                }
                ctx.restore()
            }

            // 7. Node / Polyline Interactive Construction Preview
            if (root.activeTool === "node" && root.activeNodePathPts.length > 0) {
                ctx.save()
                ctx.strokeStyle = Theme.accentCyan
                ctx.lineWidth = 1.8
                ctx.beginPath()
                var p0x = ox + root.activeNodePathPts[0][0] * scale
                var p0y = oy - root.activeNodePathPts[0][1] * scale
                ctx.moveTo(p0x, p0y)
                for (var ni = 1; ni < root.activeNodePathPts.length; ni++) {
                    var pnx = ox + root.activeNodePathPts[ni][0] * scale
                    var pny = oy - root.activeNodePathPts[ni][1] * scale
                    ctx.lineTo(pnx, pny)
                }
                var curMx = ox + root.mouseCoordMmX * scale
                var curMy = oy - root.mouseCoordMmY * scale
                ctx.lineTo(curMx, curMy)
                ctx.stroke()

                ctx.fillStyle = "#FFFFFF"
                ctx.strokeStyle = Theme.accentCyan
                ctx.lineWidth = 1.5
                for (var nj = 0; nj < root.activeNodePathPts.length; nj++) {
                    var ndx = ox + root.activeNodePathPts[nj][0] * scale
                    var ndy = oy - root.activeNodePathPts[nj][1] * scale
                    ctx.beginPath()
                    ctx.arc(ndx, ndy, 4, 0, Math.PI * 2)
                    ctx.fill()
                    ctx.stroke()
                }
                ctx.restore()
            }
        }
    }

    // Interactive Keyboard Shortcuts (Undo, Redo, Group, Hatch, Delete, Zoom)
    focus: true
    Keys.onPressed: function(event) {
        if ((event.modifiers & Qt.ControlModifier) && event.key === Qt.Key_Z) {
            root.undo()
            event.accepted = true
        } else if ((event.modifiers & Qt.ControlModifier) && (event.key === Qt.Key_Y || ((event.modifiers & Qt.ShiftModifier) && event.key === Qt.Key_Z))) {
            root.redo()
            event.accepted = true
        } else if ((event.modifiers & Qt.ControlModifier) && event.key === Qt.Key_G) {
            if (event.modifiers & Qt.ShiftModifier) {
                root.ungroupSelectedShape()
            } else {
                root.groupSelectedShapes()
            }
            event.accepted = true
        } else if (event.key === Qt.Key_H && !(event.modifiers & Qt.ControlModifier)) {
            if (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                root.hatchTriggered(root.shapes[root.selectedIndex])
                event.accepted = true
            }
        } else if (event.key === Qt.Key_Delete || event.key === Qt.Key_Backspace) {
            root.deleteSelectedShape()
            event.accepted = true
        } else if (event.key === Qt.Key_Plus || event.key === Qt.Key_Equal) {
            root.zoomIn()
            event.accepted = true
        } else if (event.key === Qt.Key_Minus) {
            root.zoomOut()
            event.accepted = true
        } else if (event.key === Qt.Key_0) {
            root.zoomFit()
            event.accepted = true
        } else if (event.key === Qt.Key_Escape) {
            if (root.activeNodePathPts.length > 0) {
                root.activeNodePathPts = []
            }
            root.activeTool = "select"
            root.isDrawingShape = false
            root.toolFinished()
            canvas.requestPaint()
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (root.activeTool === "node" && root.activeNodePathPts.length >= 2) {
                root.finishNodePolyline()
                event.accepted = true
            }
        } else if (event.key === Qt.Key_V && !(event.modifiers & Qt.ControlModifier)) {
            root.activeTool = "select"
            root.toolFinished()
            event.accepted = true
        }
    }

    // Viewport Interactions: Pan, Zoom, Object Click & Drag, Interactive Shape Drawing
    MouseArea {
        id: canvasMa
        anchors.fill: parent
        enabled: !root.interactionBlocked
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
        cursorShape: {
            if (pressedButtons & Qt.MiddleButton) return Qt.ClosedHandCursor
            if (root.activeTool === "node") {
                if (root.draggingNodePointIndex >= 0 || root.hoveredNodePointIndex >= 0) return Qt.PointingHandCursor
                return Qt.CrossCursor
            }
            if (root.activeTool !== "select") return Qt.CrossCursor
            return Qt.ArrowCursor
        }

        property real lastMouseX: 0
        property real lastMouseY: 0
        property bool isDraggingShape: false

        onWheel: function(wheel) {
            if (root.interactionBlocked) {
                wheel.accepted = true
                return
            }
            var factor = wheel.angleDelta.y > 0 ? 1.15 : 0.85
            var newScale = root.zoomScale * factor
            if (newScale >= 0.4 && newScale <= 15.0) {
                var cursorX = wheel.x
                var cursorY = wheel.y
                var mmX = (cursorX - root.originX) / root.zoomScale
                var mmY = (root.originY - cursorY) / root.zoomScale

                root.zoomScale = newScale
                root.panOffsetX = cursorX - (root.width / 2) - mmX * newScale
                root.panOffsetY = cursorY - (root.height / 2) + mmY * newScale
                canvas.requestPaint()
            }
        }

        onPressed: function(mouse) {
            if (root.interactionBlocked) {
                mouse.accepted = true
                return
            }
            lastMouseX = mouse.x
            lastMouseY = mouse.y

            if (mouse.button === Qt.LeftButton) {
                var clickMmX = (mouse.x - root.originX) / root.zoomScale
                var clickMmY = (root.originY - mouse.y) / root.zoomScale

                // 1. Interactive Node Tool
                if (root.activeTool === "node") {
                    if (root.hoveredNodePathIndex >= 0 && root.hoveredNodePointIndex >= 0) {
                        root.pushUndoState()
                        root.draggingNodePathIndex = root.hoveredNodePathIndex
                        root.draggingNodePointIndex = root.hoveredNodePointIndex
                        return
                    }

                    // Check if clicked an existing shape to select it for node editing
                    var nodeHitIndex = -1
                    for (var ni = root.shapes.length - 1; ni >= 0; ni--) {
                        var ns = root.shapes[ni]
                        if (ns.visible === false) continue
                        var nhw = (ns.wMm || 10) / 2
                        var nhh = (ns.hMm || 10) / 2
                        if (clickMmX >= ns.xMm - nhw && clickMmX <= ns.xMm + nhw &&
                            clickMmY >= ns.yMm - nhh && clickMmY <= ns.yMm + nhh) {
                            nodeHitIndex = ni
                            break
                        }
                    }
                    if (nodeHitIndex >= 0) {
                        root.selectedIndex = nodeHitIndex
                        root.shapeSelected(root.shapes[nodeHitIndex])
                        canvas.requestPaint()
                        return
                    }

                    // Click on empty space: Add node to active polyline construction
                    var newPts = root.activeNodePathPts.slice()
                    newPts.push([root.round2(clickMmX), root.round2(clickMmY)])
                    root.activeNodePathPts = newPts
                    canvas.requestPaint()
                    return
                }

                // 2. Interactive Shape Drawing Tools
                if (root.activeTool !== "select") {
                    root.isDrawingShape = true
                    root.drawStartMmX = clickMmX
                    root.drawStartMmY = clickMmY
                    root.drawCurrentMmX = clickMmX
                    root.drawCurrentMmY = clickMmY
                    root.drawFreehandPts = [[clickMmX, clickMmY]]
                    canvas.requestPaint()
                    return
                }

                // 3. Selection / Pick Tool
                var hitIndex = -1
                for (var i = root.shapes.length - 1; i >= 0; i--) {
                    var s = root.shapes[i]
                    if (s.visible === false) continue
                    var halfW = (s.wMm || 10) / 2
                    var halfH = (s.hMm || 10) / 2
                    if (clickMmX >= s.xMm - halfW && clickMmX <= s.xMm + halfW &&
                        clickMmY >= s.yMm - halfH && clickMmY <= s.yMm + halfH) {
                        hitIndex = i
                        break
                    }
                }

                root.selectedIndex = hitIndex
                if (hitIndex >= 0) {
                    root.shapeSelected(root.shapes[hitIndex])
                    isDraggingShape = (root.shapes[hitIndex].locked !== true)
                } else {
                    root.shapeSelected(null)
                }
                canvas.requestPaint()
            }
        }

        onPositionChanged: function(mouse) {
            if (root.interactionBlocked) {
                mouse.accepted = true
                return
            }
            root.mouseCoordMmX = (mouse.x - root.originX) / root.zoomScale
            root.mouseCoordMmY = (root.originY - mouse.y) / root.zoomScale

            var dx = mouse.x - lastMouseX
            var dy = mouse.y - lastMouseY

            // 1. Vertex Dragging in Node Tool
            if (root.activeTool === "node" && root.draggingNodePointIndex >= 0 && root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                var selShp = root.shapes[root.selectedIndex]
                if (selShp && selShp.paths && !selShp.locked) {
                    var sRad = -(selShp.rotation || 0) * Math.PI / 180.0
                    var cosR = Math.cos(sRad)
                    var sinR = Math.sin(sRad)
                    var dxMm = dx / root.zoomScale
                    var dyMm = -dy / root.zoomScale
                    var localDx = dxMm * cosR + dyMm * sinR
                    var localDy = -dxMm * sinR + dyMm * cosR

                    var pi = root.draggingNodePathIndex
                    var ki = root.draggingNodePointIndex
                    if (pi >= 0 && pi < selShp.paths.length && ki >= 0 && ki < selShp.paths[pi].length) {
                        selShp.paths[pi][ki][0] = root.round3(selShp.paths[pi][ki][0] + localDx)
                        selShp.paths[pi][ki][1] = root.round3(selShp.paths[pi][ki][1] + localDy)
                        root.recalculateShapeBounds(selShp)
                        selShp.hatch_lines = []
                        root.shapesChanged()
                        root.shapeModified(selShp)
                        canvas.requestPaint()
                    }
                }
                lastMouseX = mouse.x
                lastMouseY = mouse.y
                return
            }

            // 2. Vertex Proximity Hover Detection in Node Tool (within 8px)
            if (root.activeTool === "node") {
                var foundHovP = -1
                var foundHovK = -1
                if (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                    var chkShp = root.shapes[root.selectedIndex]
                    if (chkShp && chkShp.paths && chkShp.paths.length > 0) {
                        var sRad = -(chkShp.rotation || 0) * Math.PI / 180.0
                        var cosR = Math.cos(sRad)
                        var sinR = Math.sin(sRad)
                        var relMx = root.mouseCoordMmX - chkShp.xMm
                        var relMy = root.mouseCoordMmY - chkShp.yMm
                        var locMx = relMx * cosR + relMy * sinR
                        var locMy = -relMx * sinR + relMy * cosR

                        for (var p = 0; p < chkShp.paths.length; p++) {
                            var subp = chkShp.paths[p]
                            for (var k = 0; k < subp.length; k++) {
                                var distPx = Math.hypot(locMx - subp[k][0], locMy - subp[k][1]) * root.zoomScale
                                if (distPx <= 8.0) {
                                    foundHovP = p
                                    foundHovK = k
                                    break
                                }
                            }
                            if (foundHovP >= 0) break
                        }
                    }
                }
                if (root.hoveredNodePathIndex !== foundHovP || root.hoveredNodePointIndex !== foundHovK) {
                    root.hoveredNodePathIndex = foundHovP
                    root.hoveredNodePointIndex = foundHovK
                    canvas.requestPaint()
                }
                if (root.activeNodePathPts.length > 0) {
                    canvas.requestPaint()
                }
            }

            // 3. Shape Drawing Preview
            if (root.isDrawingShape) {
                root.drawCurrentMmX = root.mouseCoordMmX
                root.drawCurrentMmY = root.mouseCoordMmY
                if (root.activeTool === "curve") {
                    root.drawFreehandPts.push([root.mouseCoordMmX, root.mouseCoordMmY])
                }
                canvas.requestPaint()
                lastMouseX = mouse.x
                lastMouseY = mouse.y
                return
            }

            // 4. Pan Viewport or Move Selected Shape
            if (mouse.buttons & Qt.MiddleButton || (mouse.buttons & Qt.LeftButton && (canvasMa.drag.active || !isDraggingShape && root.selectedIndex === -1))) {
                root.panOffsetX += dx
                root.panOffsetY += dy
                canvas.requestPaint()
            } else if (isDraggingShape && (mouse.buttons & Qt.LeftButton) && root.selectedIndex >= 0) {
                var sel = root.shapes[root.selectedIndex]
                if (!sel.locked) {
                    sel.xMm += dx / root.zoomScale
                    sel.yMm -= dy / root.zoomScale
                    sel.hatch_lines = []
                    root.shapesChanged()
                    root.shapeModified(sel)
                    canvas.requestPaint()
                }
            }

            lastMouseX = mouse.x
            lastMouseY = mouse.y
        }

        onReleased: function(mouse) {
            if (root.interactionBlocked) {
                mouse.accepted = true
                return
            }
            // 1. Finish Vertex Drag in Node Tool
            if (root.activeTool === "node" && root.draggingNodePointIndex >= 0) {
                root.draggingNodePathIndex = -1
                root.draggingNodePointIndex = -1
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(root.shapes)
                }
                canvas.requestPaint()
                return
            }

            // 2. Shape Creation Release
            if (root.isDrawingShape) {
                root.isDrawingShape = false
                var penId = root.currentPenId
                var shapeCreated = false

                if (root.activeTool === "rect") {
                    var minX = Math.min(root.drawStartMmX, root.drawCurrentMmX)
                    var maxX = Math.max(root.drawStartMmX, root.drawCurrentMmX)
                    var minY = Math.min(root.drawStartMmY, root.drawCurrentMmY)
                    var maxY = Math.max(root.drawStartMmY, root.drawCurrentMmY)
                    var rw = maxX - minX
                    var rh = maxY - minY
                    if (rw >= 0.5 && rh >= 0.5) {
                        root.pushUndoState()
                        var newRect = {
                            id: root.shapes.length + 1,
                            name: "Rect_" + (root.shapes.length + 1),
                            type: "rect",
                            xMm: root.round2((minX + maxX) / 2.0),
                            yMm: root.round2((minY + maxY) / 2.0),
                            wMm: root.round2(rw),
                            hMm: root.round2(rh),
                            rotation: 0,
                            penId: penId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        var updatedR = root.shapes.slice()
                        updatedR.push(newRect)
                        root.shapes = updatedR
                        root.shapesChanged()
                        root.selectedIndex = root.shapes.length - 1
                        root.shapeSelected(newRect)
                        shapeCreated = true
                    }
                } else if (root.activeTool === "circle") {
                    var r = Math.hypot(root.drawCurrentMmX - root.drawStartMmX, root.drawCurrentMmY - root.drawStartMmY)
                    if (r >= 0.5) {
                        root.pushUndoState()
                        var newCirc = {
                            id: root.shapes.length + 1,
                            name: "Circle_" + (root.shapes.length + 1),
                            type: "circle",
                            xMm: root.round2(root.drawStartMmX),
                            yMm: root.round2(root.drawStartMmY),
                            wMm: root.round2(r * 2),
                            hMm: root.round2(r * 2),
                            rotation: 0,
                            penId: penId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        var updatedC = root.shapes.slice()
                        updatedC.push(newCirc)
                        root.shapes = updatedC
                        root.shapesChanged()
                        root.selectedIndex = root.shapes.length - 1
                        root.shapeSelected(newCirc)
                        shapeCreated = true
                    }
                } else if (root.activeTool === "polygon") {
                    var rPoly = Math.hypot(root.drawCurrentMmX - root.drawStartMmX, root.drawCurrentMmY - root.drawStartMmY)
                    if (rPoly >= 0.5) {
                        root.pushUndoState()
                        var pSides = 5
                        var polyPts = []
                        for (var psi = 0; psi < pSides; psi++) {
                            var pAng = -Math.PI / 2 + (psi * 2 * Math.PI) / pSides
                            polyPts.push([root.round3(rPoly * Math.cos(pAng)), root.round3(rPoly * Math.sin(pAng))])
                        }
                        polyPts.push([polyPts[0][0], polyPts[0][1]])
                        var newPoly = {
                            id: root.shapes.length + 1,
                            name: "Polygon_" + (root.shapes.length + 1),
                            type: "polygon",
                            xMm: root.round2(root.drawStartMmX),
                            yMm: root.round2(root.drawStartMmY),
                            wMm: root.round2(rPoly * 2),
                            hMm: root.round2(rPoly * 2),
                            rotation: 0,
                            penId: penId,
                            hatched: false,
                            visible: true,
                            locked: false,
                            paths: [polyPts]
                        }
                        var updatedPoly = root.shapes.slice()
                        updatedPoly.push(newPoly)
                        root.shapes = updatedPoly
                        root.shapesChanged()
                        root.selectedIndex = root.shapes.length - 1
                        root.shapeSelected(newPoly)
                        shapeCreated = true
                    }
                } else if (root.activeTool === "line") {
                    var dist = Math.hypot(root.drawCurrentMmX - root.drawStartMmX, root.drawCurrentMmY - root.drawStartMmY)
                    if (dist >= 0.5) {
                        root.pushUndoState()
                        var lx0 = root.drawStartMmX
                        var ly0 = root.drawStartMmY
                        var lx1 = root.drawCurrentMmX
                        var ly1 = root.drawCurrentMmY
                        var lcx = (lx0 + lx1) / 2.0
                        var lcy = (ly0 + ly1) / 2.0
                        var lw = Math.abs(lx1 - lx0)
                        var lh = Math.abs(ly1 - ly0)
                        var relLine = [[root.round3(lx0 - lcx), root.round3(ly0 - lcy)], [root.round3(lx1 - lcx), root.round3(ly1 - lcy)]]
                        var newLine = {
                            id: root.shapes.length + 1,
                            name: "Line_" + (root.shapes.length + 1),
                            type: "polygon",
                            xMm: root.round2(lcx),
                            yMm: root.round2(lcy),
                            wMm: root.round2(Math.max(1.0, lw)),
                            hMm: root.round2(Math.max(1.0, lh)),
                            rotation: 0,
                            penId: penId,
                            hatched: false,
                            visible: true,
                            locked: false,
                            paths: [relLine]
                        }
                        var updatedL = root.shapes.slice()
                        updatedL.push(newLine)
                        root.shapes = updatedL
                        root.shapesChanged()
                        root.selectedIndex = root.shapes.length - 1
                        root.shapeSelected(newLine)
                        shapeCreated = true
                    }
                } else if (root.activeTool === "curve") {
                    if (root.drawFreehandPts.length >= 2) {
                        root.pushUndoState()
                        var pts = root.drawFreehandPts
                        var cminX = 1e9, cmaxX = -1e9, cminY = 1e9, cmaxY = -1e9
                        for (var pi = 0; pi < pts.length; pi++) {
                            cminX = Math.min(cminX, pts[pi][0])
                            cmaxX = Math.max(cmaxX, pts[pi][0])
                            cminY = Math.min(cminY, pts[pi][1])
                            cmaxY = Math.max(cmaxY, pts[pi][1])
                        }
                        var ccx = (cminX + cmaxX) / 2.0
                        var ccy = (cminY + cmaxY) / 2.0
                        var cw = cmaxX - cminX
                        var ch = cmaxY - cminY
                        var relPts = []
                        for (var pi = 0; pi < pts.length; pi++) {
                            relPts.push([root.round3(pts[pi][0] - ccx), root.round3(pts[pi][1] - ccy)])
                        }
                        var newCurve = {
                            id: root.shapes.length + 1,
                            name: "Curve_" + (root.shapes.length + 1),
                            type: "polygon",
                            xMm: root.round2(ccx),
                            yMm: root.round2(ccy),
                            wMm: root.round2(Math.max(1.0, cw)),
                            hMm: root.round2(Math.max(1.0, ch)),
                            rotation: 0,
                            penId: penId,
                            hatched: false,
                            visible: true,
                            locked: false,
                            paths: [relPts]
                        }
                        var updatedCv = root.shapes.slice()
                        updatedCv.push(newCurve)
                        root.shapes = updatedCv
                        root.shapesChanged()
                        root.selectedIndex = root.shapes.length - 1
                        root.shapeSelected(newCurve)
                        shapeCreated = true
                    }
                }

                // Reset back to selection tool
                root.activeTool = "select"
                root.toolFinished()
                canvas.requestPaint()
                if (shapeCreated && typeof cad !== "undefined" && cad) {
                    cad.updateShapes(root.shapes)
                }
                return
            }

            // 3. Finish Moving Shape
            if (isDraggingShape) {
                isDraggingShape = false
                if (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                    var curShp = root.shapes[root.selectedIndex]
                    if (curShp) curShp.hatch_lines = []
                    if (typeof cad !== "undefined" && cad) cad.updateShapes(root.shapes)
                    canvas.requestPaint()
                }
            }
        }

        onDoubleClicked: function(mouse) {
            if (root.activeTool === "node" && root.activeNodePathPts.length >= 2) {
                root.finishNodePolyline()
            }
        }
    }

    // Floating In-Canvas HUD for Selected Object Actions
    Rectangle {
        id: floatingHud
        visible: root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length
        height: 34
        radius: 6
        color: Theme.isDark ? "#17233D" : "#FFFFFF"
        border.color: Theme.borderActive
        border.width: 1
        implicitWidth: hudRow.implicitWidth + 16

        x: {
            if (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                var s = root.shapes[root.selectedIndex]
                var px = root.originX + s.xMm * root.zoomScale
                return Math.max(10, Math.min(root.width - width - 10, px - width / 2))
            }
            return 10
        }
        y: {
            if (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length) {
                var s = root.shapes[root.selectedIndex]
                var py = root.originY - s.yMm * root.zoomScale - (s.hMm / 2) * root.zoomScale
                return Math.max(10, py - 44)
            }
            return 10
        }

        Row {
            id: hudRow
            anchors.centerIn: parent
            spacing: 6

            readonly property bool isLocked: (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length && root.shapes[root.selectedIndex]) ? Boolean(root.shapes[root.selectedIndex].locked) : false
            readonly property bool isHatched: (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length && root.shapes[root.selectedIndex]) ? Boolean(root.shapes[root.selectedIndex].hatched) : false

            CadButton {
                iconName: "rotate_90_degrees_cw"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Rotate 90° Clockwise"
                enabled: !hudRow.isLocked
                onClicked: root.rotateSelectedShape(90)
            }
            CadButton {
                iconName: "content_copy"
                tooltipText: "Duplicate Object"
                onClicked: root.duplicateSelectedShape()
            }
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Center to Galvo Origin (0,0)"
                enabled: !hudRow.isLocked
                onClicked: root.centerSelectedShape()
            }
            CadButton {
                visible: hudRow.isHatched
                iconName: "layers_clear"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Remove Hatch (Unhatch Object)"
                enabled: !hudRow.isLocked
                variant: "outline"
                onClicked: root.unhatchSelectedShape()
            }
            CadButton {
                iconName: "delete"
                variant: "danger"
                tooltipText: hudRow.isLocked ? "Object is locked (Unlock to delete)" : "Delete Object"
                enabled: !hudRow.isLocked
                onClicked: root.deleteSelectedShape()
            }
        }
    }

    Connections {
        target: Theme
        function onIsDarkChanged() { canvas.requestPaint() }
        function onPenPaletteUpdated() { canvas.requestPaint() }
        function onPenPaletteChanged() { canvas.requestPaint() }
    }
}
