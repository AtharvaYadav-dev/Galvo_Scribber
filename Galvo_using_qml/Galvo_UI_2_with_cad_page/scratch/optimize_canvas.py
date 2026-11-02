with open("qml/components/cad/CadCanvas.qml", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update pushUndoState, undo, redo to avoid huge JSON.stringify
old_undo = """    function pushUndoState() {
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
    }"""

new_undo = """    function cloneShapesModel(source) {
        if (!source) return []
        var out = []
        for (var i = 0; i < source.length; i++) {
            var shp = source[i]
            var c = {}
            for (var key in shp) {
                if (key === "children" && shp.children) {
                    c.children = shp.children.map(function(ch) { return Object.assign({}, ch) })
                } else {
                    c[key] = shp[key]
                }
            }
            out.push(c)
        }
        return out
    }

    function pushUndoState() {
        var snap = cloneShapesModel(shapes)
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
        var curSnap = cloneShapesModel(shapes)
        var newRedo = redoStack.slice()
        newRedo.push(curSnap)
        redoStack = newRedo

        var newUndo = undoStack.slice()
        var prev = newUndo.pop()
        undoStack = newUndo

        shapes = prev
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
        var curSnap = cloneShapesModel(shapes)
        var newUndo = undoStack.slice()
        newUndo.push(curSnap)
        undoStack = newUndo

        var newRedo = redoStack.slice()
        var next = newRedo.pop()
        redoStack = newRedo

        shapes = next
        if (selectedIndex >= shapes.length) selectedIndex = shapes.length - 1
        shapesChanged()
        canvas.requestPaint()
        if (typeof cad !== "undefined" && cad) {
            cad.updateShapes(shapes)
            cad.set_status_message("Redo successful.")
        }
    }"""

assert old_undo in text, "old_undo not found"
text = text.replace(old_undo, new_undo, 1)

# 2. Subpixel LOD in onPaint
old_draw_poly = """                } else if (shp.type === "polygon" || shp.type === "dxf" || shp.type === "svg" || shp.type === "line" || shp.type === "curve") {
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
                }"""

new_draw_poly = """                } else if (shp.type === "polygon" || shp.type === "dxf" || shp.type === "svg" || shp.type === "line" || shp.type === "curve") {
                    if (shp.paths && shp.paths.length > 0) {
                        ctx.beginPath()
                        for (var p = 0; p < shp.paths.length; p++) {
                            var sub = shp.paths[p]
                            if (!sub || sub.length < 2) continue
                            var subLen = sub.length
                            var p0x = sub[0][0] * scale
                            var p0y = -sub[0][1] * scale
                            ctx.moveTo(p0x, p0y)
                            if (subLen > 150) {
                                var lastX = p0x
                                var lastY = p0y
                                for (var k = 1; k < subLen - 1; k++) {
                                    var px = sub[k][0] * scale
                                    var py = -sub[k][1] * scale
                                    if (Math.abs(px - lastX) >= 1.0 || Math.abs(py - lastY) >= 1.0) {
                                        ctx.lineTo(px, py)
                                        lastX = px
                                        lastY = py
                                    }
                                }
                                ctx.lineTo(sub[subLen - 1][0] * scale, -sub[subLen - 1][1] * scale)
                            } else {
                                for (var k2 = 1; k2 < subLen; k2++) {
                                    ctx.lineTo(sub[k2][0] * scale, -sub[k2][1] * scale)
                                }
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
                }"""

assert old_draw_poly in text, "old_draw_poly not found"
text = text.replace(old_draw_poly, new_draw_poly, 1)

# 3. Guard node handles drawing if thousands of points
old_node_draw = """                    // Vertex Node Handles for Node / Vertex Edit Tool
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
                    }"""

new_node_draw = """                    // Vertex Node Handles for Node / Vertex Edit Tool
                    if (root.activeTool === "node") {
                        var nodeRad = 5.0
                        if (shp.paths && shp.paths.length > 0) {
                            var totalNodePts = 0
                            for (var pci = 0; pci < shp.paths.length; pci++) {
                                totalNodePts += shp.paths[pci].length
                            }
                            if (totalNodePts <= 600) {
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
                    }"""

assert old_node_draw in text, "old_node_draw not found"
text = text.replace(old_node_draw, new_node_draw, 1)

# 4. Remove shapesChanged emission during continuous shape dragging
old_drag = """            } else if (isDraggingShape && (mouse.buttons & Qt.LeftButton) && root.selectedIndex >= 0) {
                var sel = root.shapes[root.selectedIndex]
                if (!sel.locked) {
                    sel.xMm += dx / root.zoomScale
                    sel.yMm -= dy / root.zoomScale
                    sel.hatch_lines = []
                    root.shapesChanged()
                    root.shapeModified(sel)
                    canvas.requestPaint()
                }
            }"""

new_drag = """            } else if (isDraggingShape && (mouse.buttons & Qt.LeftButton) && root.selectedIndex >= 0) {
                var sel = root.shapes[root.selectedIndex]
                if (!sel.locked) {
                    sel.xMm += dx / root.zoomScale
                    sel.yMm -= dy / root.zoomScale
                    canvas.requestPaint()
                }
            }"""

assert old_drag in text, "old_drag not found"
text = text.replace(old_drag, new_drag, 1)

with open("qml/components/cad/CadCanvas.qml", "w", encoding="utf-8") as f:
    f.write(text)

print("CadCanvas.qml successfully optimized!")

