with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('        onPressed: function(mouse) {')
s2 = text.find('    // Floating In-Canvas HUD for Selected Object Actions')

assert s1 != -1 and s2 != -1, f"Indices not found: s1={s1}, s2={s2}"

new_mouse_area = """        onPressed: function(mouse) {
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
                var penId = (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length)
                    ? (root.shapes[root.selectedIndex].penId || 0) : 0
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

"""

text = text[:s1] + new_mouse_area + text[s2:]

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadCanvas.qml mouse interactions and shape creation updated successfully!")

