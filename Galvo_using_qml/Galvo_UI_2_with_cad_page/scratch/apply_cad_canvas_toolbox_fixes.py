with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update deleteSelectedShape and duplicateSelectedShape
target_delete_dup = """    function deleteSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            if (shapes[selectedIndex].locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot delete locked object '" + (shapes[selectedIndex].name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            var copy = shapes.slice()
            copy.splice(selectedIndex, 1)
            shapes = copy
            selectedIndex = Math.min(selectedIndex, shapes.length - 1)
            shapesChanged()
            canvas.requestPaint()
        }
    }

    function duplicateSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var orig = shapes[selectedIndex]
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
            var copy = shapes.slice()
            copy.push(clone)
            shapes = copy
            shapesChanged()
            selectedIndex = shapes.length - 1
            shapeSelected(clone)
            canvas.requestPaint()
        }
    }"""

new_delete_dup = """    function deleteSelectedShape() {
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
    }"""

assert target_delete_dup in text, "target_delete_dup not found"
text = text.replace(target_delete_dup, new_delete_dup, 1)

# 2. Update Canvas Barcode Rendering
target_barcode_render = """                } else if (shp.type === "qrcode") {
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)
                    ctx.fillStyle = isDark ? "#070B14" : "#FFFFFF"
                    var blockSize = sw / 6
                    ctx.fillRect(-sw / 2 + blockSize, -sh / 2 + blockSize, blockSize * 4, blockSize * 4)
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2 + blockSize * 2, -sh / 2 + blockSize * 2, blockSize * 2, blockSize * 2)"""

new_barcode_render = """                } else if (shp.type === "qrcode") {
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)
                    ctx.fillStyle = isDark ? "#070B14" : "#FFFFFF"
                    var blockSize = sw / 7
                    // Position detection pattern markers at three corners
                    ctx.fillRect(-sw / 2 + blockSize, -sh / 2 + blockSize, blockSize * 5, blockSize * 5)
                    ctx.fillRect(sw / 2 - blockSize * 6, -sh / 2 + blockSize, blockSize * 5, blockSize * 5)
                    ctx.fillRect(-sw / 2 + blockSize, sh / 2 - blockSize * 6, blockSize * 5, blockSize * 5)
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2 + blockSize * 2, -sh / 2 + blockSize * 2, blockSize * 3, blockSize * 3)
                    ctx.fillRect(sw / 2 - blockSize * 5, -sh / 2 + blockSize * 2, blockSize * 3, blockSize * 3)
                    ctx.fillRect(-sw / 2 + blockSize * 2, sh / 2 - blockSize * 5, blockSize * 3, blockSize * 3)
                    // Center data dots
                    ctx.fillRect(-blockSize, -blockSize, blockSize * 2, blockSize * 2)
                } else if (shp.type === "datamatrix") {
                    ctx.fillStyle = penColor
                    var dmThick = Math.max(2, sw / 12)
                    ctx.fillRect(-sw / 2, -sh / 2, dmThick, sh) // left solid L
                    ctx.fillRect(-sw / 2, sh / 2 - dmThick, sw, dmThick) // bottom solid L
                    var dSteps = 10
                    var stepW = sw / dSteps
                    for (var dsi = 0; dsi < dSteps; dsi += 2) {
                        ctx.fillRect(-sw / 2 + dsi * stepW, -sh / 2, stepW, dmThick) // top alternating
                        ctx.fillRect(sw / 2 - dmThick, -sh / 2 + dsi * stepW, dmThick, stepW) // right alternating
                    }
                    for (var rmi = 2; rmi < dSteps - 2; rmi++) {
                        for (var cmi = 2; cmi < dSteps - 2; cmi++) {
                            if ((rmi * 7 + cmi * 13) % 3 === 0) {
                                ctx.fillRect(-sw / 2 + cmi * stepW, -sh / 2 + rmi * stepW, stepW * 0.8, stepW * 0.8)
                            }
                        }
                    }
                } else if (shp.type === "barcode128") {
                    ctx.fillStyle = penColor
                    var totalBars = 24
                    var unitW = sw / (totalBars * 1.5)
                    var curBx = -sw / 2 + unitW * 0.5
                    for (var bIdx = 0; bIdx < totalBars; bIdx++) {
                        var isThick = (bIdx % 3 === 0)
                        var bW = unitW * (isThick ? 1.8 : 1.0)
                        if ((bIdx * 11 + 5) % 7 > 2) {
                            ctx.fillRect(curBx, -sh / 2, bW, sh)
                        }
                        curBx += bW + unitW * 0.5
                    }"""

assert target_barcode_render in text, "target_barcode_render not found"
text = text.replace(target_barcode_render, new_barcode_render, 1)

# 3. Update cursorShape
target_cursor = """        cursorShape: {
            if (pressedButtons & Qt.MiddleButton) return Qt.ClosedHandCursor
            if (root.activeTool !== "select") return Qt.CrossCursor
            return Qt.ArrowCursor
        }"""

new_cursor = """        cursorShape: {
            if (pressedButtons & Qt.MiddleButton) return Qt.ClosedHandCursor
            if (root.activeTool === "node") {
                if (root.draggingNodePointIndex >= 0 || root.hoveredNodePointIndex >= 0) return Qt.PointingHandCursor
                return Qt.CrossCursor
            }
            if (root.activeTool !== "select") return Qt.CrossCursor
            return Qt.ArrowCursor
        }"""

assert target_cursor in text, "target_cursor not found"
text = text.replace(target_cursor, new_cursor, 1)

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Part A of CadCanvas.qml updated successfully!")

