with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

target_props = "    // Active CAD tool: 'select', 'rect', 'circle', 'line', 'curve', etc.\n    property string activeTool: \"select\"\n"

new_props = """    // Active CAD tool: 'select', 'node', 'line', 'curve', 'rect', 'circle', 'polygon', etc.
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
                penId: (selectedIndex >= 0 && selectedIndex < shapes.length) ? (shapes[selectedIndex].penId || 0) : 0,
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
"""

assert target_props in text, "target_props not found"
text = text.replace(target_props, new_props, 1)

# 2. Render Node Handles in canvas when root.activeTool === "node"
target_handles = """                    for (var h = 0; h < handlePts.length; h++) {
                        ctx.fillRect(handlePts[h].x - hs / 2, handlePts[h].y - hs / 2, hs, hs)
                        ctx.strokeRect(handlePts[h].x - hs / 2, handlePts[h].y - hs / 2, hs, hs)
                    }
                }"""

new_handles = """                    for (var h = 0; h < handlePts.length; h++) {
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
                }"""

assert target_handles in text, "target_handles not found"
text = text.replace(target_handles, new_handles, 1)

# 3. Add live rubberband for polygon and activeNodePathPts
target_rubberband = """                } else if (root.activeTool === "circle" || root.activeTool === "polygon") {
                    var radPx = Math.hypot(dsx1 - dsx0, dsy1 - dsy0)
                    ctx.beginPath()
                    ctx.arc(dsx0, dsy0, radPx, 0, Math.PI * 2)
                    ctx.stroke()"""

new_rubberband = """                } else if (root.activeTool === "circle") {
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
                    ctx.stroke()"""

assert target_rubberband in text, "target_rubberband not found"
text = text.replace(target_rubberband, new_rubberband, 1)

# 4. Add Node Polyline live preview
target_live_end = """                }
                ctx.restore()
            }
        }
    }"""

new_live_end = """                }
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
    }"""

assert target_live_end in text, "target_live_end not found"
text = text.replace(target_live_end, new_live_end, 1)

# 5. Keyboard shortcuts: Esc cancels activeTool / polyline, Enter finishes polyline, V selects
target_keys = """        } else if (event.key === Qt.Key_0) {
            root.zoomFit()
            event.accepted = true
        }"""

new_keys = """        } else if (event.key === Qt.Key_0) {
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
        }"""

assert target_keys in text, "target_keys not found"
text = text.replace(target_keys, new_keys, 1)

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Part 1 of CadCanvas.qml updated successfully!")
