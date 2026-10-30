with open("qml/components/cad/CadCanvas.qml", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add undo / redo properties
old_shapes_decl = """    // Shapes data model (starts empty for clean project)
    property var shapes: []

    signal shapeSelected(var shape)
    signal shapeModified(var shape)"""

new_shapes_decl = """    // Shapes data model (starts empty for clean project)
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
            penId: (selectedIndex >= 0 && selectedIndex < shapes.length) ? (shapes[selectedIndex].penId || 0) : 0,
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
    }"""

assert old_shapes_decl in content, "old_shapes_decl not found"
content = content.replace(old_shapes_decl, new_shapes_decl)

# 2. Add pushUndoState to centerSelectedShape
old_center = """    function centerSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {"""

new_center = """    function centerSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {
                if (typeof cad !== "undefined" && cad) cad.set_status_message("Object is locked.")
                return
            }
            pushUndoState()"""

assert old_center in content, "old_center not found"
content = content.replace(old_center, new_center)

# 3. Add pushUndoState to fitSelectionToField
old_fit = """    function fitSelectionToField() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]"""

new_fit = """    function fitSelectionToField() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) return
            pushUndoState()"""

assert old_fit in content, "old_fit not found"
content = content.replace(old_fit, new_fit)

# 4. Add pushUndoState to alignSelectedShape
old_align = """    function alignSelectedShape(mode) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {"""

new_align = """    function alignSelectedShape(mode) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot align locked object '" + (s.name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()"""

assert old_align in content, "old_align not found"
content = content.replace(old_align, new_align)

# 5. Add pushUndoState to deleteSelectedShape
old_del = """    function deleteSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            if (shapes[selectedIndex].locked === true) {"""

new_del = """    function deleteSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            if (shapes[selectedIndex].locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot delete locked object '" + (shapes[selectedIndex].name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()"""

assert old_del in content, "old_del not found"
content = content.replace(old_del, new_del)

# 6. Add group rendering in onPaint
old_on_paint_rect = """                if (shp.type === "rect") {
                    if (shp.mark_contour !== false) {
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    } else {"""

new_on_paint_rect = """                if (shp.type === "group") {
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
                            var cPen = Theme.penPalette[((ch.penId !== undefined ? ch.penId : shp.penId) || 0) % Theme.penPalette.length].color

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
                                ctx.font = (ch.bold ? "bold " : "") + (ch.italic ? "italic " : "") + Math.round(cH * 0.75) + "px sans-serif"
                                ctx.textAlign = "center"
                                ctx.textBaseline = "middle"
                                ctx.fillText(ch.text || "TEXT", 0, 0)
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
                    if (shp.mark_contour !== false) {
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    } else {"""

assert old_on_paint_rect in content, "old_on_paint_rect not found"
content = content.replace(old_on_paint_rect, new_on_paint_rect)

# 7. Add keyboard shortcuts to CadCanvas
old_mouse_area_header = """    // Viewport Interactions: Pan, Zoom, Object Click & Drag, Interactive Shape Drawing
    MouseArea {
        id: canvasMa
        anchors.fill: parent"""

new_mouse_area_header = """    // Interactive Keyboard Shortcuts (Undo, Redo, Group, Hatch, Delete, Zoom)
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
        }
    }

    // Viewport Interactions: Pan, Zoom, Object Click & Drag, Interactive Shape Drawing
    MouseArea {
        id: canvasMa
        anchors.fill: parent"""

assert old_mouse_area_header in content, "old_mouse_area_header not found"
content = content.replace(old_mouse_area_header, new_mouse_area_header)

with open("qml/components/cad/CadCanvas.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated CadCanvas.qml successfully")
