import QtQuick
import QtQuick.Controls
import ".."

Item {
    id: root

    // Galvo Machine envelope in mm
    property real fieldSizeMm: 110.0 // 110 x 110 mm optical field

    // Viewport Navigation
    property real zoomScale: 2.5 // Screen pixels per mm (initial 2.5px = 1mm)
    property real panOffsetX: 0.0
    property real panOffsetY: 0.0

    // Center optical origin in canvas pixel coordinates
    readonly property real originX: (width / 2) + panOffsetX
    readonly property real originY: (height / 2) + panOffsetY

    onOriginXChanged: canvas.requestPaint()
    onOriginYChanged: canvas.requestPaint()
    onZoomScaleChanged: canvas.requestPaint()
    onWidthChanged: canvas.requestPaint()
    onHeightChanged: canvas.requestPaint()

    // Live mouse telemetry in millimeters relative to Galvo optical center (0,0)
    property real mouseCoordMmX: 0.0
    property real mouseCoordMmY: 0.0

    // Selected shape index (-1 when nothing is selected)
    property int selectedIndex: -1

    // Shapes data model (starts empty for clean project)
    property var shapes: []

    signal shapeSelected(var shape)
    signal shapeModified(var shape)

    clip: true

    function zoomIn() {
        zoomScale = Math.min(12.0, zoomScale * 1.25)
    }

    function zoomOut() {
        zoomScale = Math.max(0.4, zoomScale / 1.25)
    }

    function zoomFit() {
        panOffsetX = 0
        panOffsetY = 0
        var availableMin = Math.min(width, height) - 80
        zoomScale = Math.max(1.0, availableMin / fieldSizeMm)
    }

    function centerSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            s.xMm = 0
            s.yMm = 0
            shapesChanged()
            shapeModified(s)
            canvas.requestPaint()
        }
    }

    function rotateSelectedShape(deg) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            s.rotation = (s.rotation + deg) % 360
            shapesChanged()
            shapeModified(s)
            canvas.requestPaint()
        }
    }

    function deleteSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var copy = shapes.slice()
            copy.splice(selectedIndex, 1)
            shapes = copy
            selectedIndex = Math.min(selectedIndex, shapes.length - 1)
            shapesChanged()
            canvas.requestPaint()
        }
    }

    // High-performance Canvas
    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.FramebufferObject
        renderStrategy: Canvas.Immediate

        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var isDark = CadTheme.isDark
            var ox = root.originX
            var oy = root.originY
            var scale = root.zoomScale
            var halfFieldPx = (root.fieldSizeMm / 2) * scale

            // 1. Fill Canvas background
            ctx.fillStyle = CadTheme.canvasBg
            ctx.fillRect(0, 0, width, height)

            // 2. Draw Minor & Major Adaptive Grid
            var gridStepMm = 10.0
            if (scale > 5.0) gridStepMm = 2.0
            else if (scale < 1.0) gridStepMm = 20.0

            var gridStepPx = gridStepMm * scale

            ctx.lineWidth = 1
            ctx.strokeStyle = CadTheme.canvasGridMinor
            ctx.beginPath()

            // Vertical grid lines
            for (var x = ox % gridStepPx; x < width; x += gridStepPx) {
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
            }
            // Horizontal grid lines
            for (var y = oy % gridStepPx; y < height; y += gridStepPx) {
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
            }
            ctx.stroke()

            // 3. Galvo Optical Bed Field Boundary (Square 110x110 mm)
            ctx.fillStyle = CadTheme.canvasBedFill
            ctx.fillRect(ox - halfFieldPx, oy - halfFieldPx, halfFieldPx * 2, halfFieldPx * 2)

            ctx.lineWidth = 1.5
            ctx.strokeStyle = CadTheme.canvasBedBorder
            ctx.setLineDash([8, 5])
            ctx.strokeRect(ox - halfFieldPx, oy - halfFieldPx, halfFieldPx * 2, halfFieldPx * 2)
            ctx.setLineDash([])

            // Corner decorative brackets for optical field
            var brk = Math.min(16, halfFieldPx * 0.25)
            ctx.strokeStyle = CadTheme.accentCyan
            ctx.lineWidth = 2
            ctx.beginPath()
            // Top Left
            ctx.moveTo(ox - halfFieldPx, oy - halfFieldPx + brk); ctx.lineTo(ox - halfFieldPx, oy - halfFieldPx); ctx.lineTo(ox - halfFieldPx + brk, oy - halfFieldPx)
            // Top Right
            ctx.moveTo(ox + halfFieldPx - brk, oy - halfFieldPx); ctx.lineTo(ox + halfFieldPx, oy - halfFieldPx); ctx.lineTo(ox + halfFieldPx, oy - halfFieldPx + brk)
            // Bottom Right
            ctx.moveTo(ox + halfFieldPx, oy + halfFieldPx - brk); ctx.lineTo(ox + halfFieldPx, oy + halfFieldPx); ctx.lineTo(ox + halfFieldPx - brk, oy + halfFieldPx)
            // Bottom Left
            ctx.moveTo(ox - halfFieldPx + brk, oy + halfFieldPx); ctx.lineTo(ox - halfFieldPx, oy + halfFieldPx); ctx.lineTo(ox - halfFieldPx, oy + halfFieldPx - brk)
            ctx.stroke()

            // 4. Optical Center Axes (X = 0, Y = 0)
            ctx.strokeStyle = CadTheme.canvasAxis
            ctx.lineWidth = 1.2
            ctx.setLineDash([4, 4])
            ctx.beginPath()
            ctx.moveTo(ox, 0); ctx.lineTo(ox, height)
            ctx.moveTo(0, oy); ctx.lineTo(width, oy)
            ctx.stroke()
            ctx.setLineDash([])

            // Optical Center Ring Marker (0,0)
            ctx.fillStyle = CadTheme.accentCyan
            ctx.beginPath()
            ctx.arc(ox, oy, 3, 0, Math.PI * 2)
            ctx.fill()

            // 5. Render Vector CAD Shapes
            for (var i = 0; i < root.shapes.length; i++) {
                var shp = root.shapes[i]
                if (!shp.visible) continue

                var sx = ox + shp.xMm * scale
                var sy = oy - shp.yMm * scale // CAD +Y is upwards
                var sw = shp.wMm * scale
                var sh = shp.hMm * scale
                var isSel = (i === root.selectedIndex)

                var penColor = CadTheme.penPalette[shp.penId % CadTheme.penPalette.length].color

                ctx.save()
                ctx.translate(sx, sy)
                if (shp.rotation !== 0) {
                    ctx.rotate((-shp.rotation * Math.PI) / 180)
                }

                ctx.strokeStyle = penColor
                ctx.lineWidth = isSel ? 2.5 : 1.5

                if (shp.type === "rect") {
                    ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    // If hatched, draw fine diagonal hatch lines
                    if (shp.hatched) {
                        ctx.save()
                        ctx.strokeStyle = isDark ? Qt.rgba(1, 1, 1, 0.25) : Qt.rgba(0, 0, 0, 0.2)
                        ctx.lineWidth = 0.8
                        var hStep = Math.max(3, 0.5 * scale)
                        for (var hx = -sw / 2; hx < sw / 2 + sh; hx += hStep) {
                            ctx.beginPath()
                            ctx.moveTo(hx, -sh / 2)
                            ctx.lineTo(hx - sh, sh / 2)
                            ctx.stroke()
                        }
                        ctx.restore()
                    }
                } else if (shp.type === "circle") {
                    ctx.beginPath()
                    ctx.arc(0, 0, sw / 2, 0, Math.PI * 2)
                    ctx.stroke()
                } else if (shp.type === "text") {
                    ctx.fillStyle = penColor
                    ctx.font = "bold " + Math.round(sh * 0.85) + "px 'Inter', 'Segoe UI', sans-serif"
                    ctx.textAlign = "center"
                    ctx.textBaseline = "middle"
                    ctx.fillText(shp.text || "LASER", 0, 0)
                    ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                } else if (shp.type === "qrcode") {
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)
                    ctx.fillStyle = isDark ? "#070B14" : "#FFFFFF"
                    var blockSize = sw / 6
                    ctx.fillRect(-sw / 2 + blockSize, -sh / 2 + blockSize, blockSize * 4, blockSize * 4)
                    ctx.fillStyle = penColor
                    ctx.fillRect(-sw / 2 + blockSize * 2, -sh / 2 + blockSize * 2, blockSize * 2, blockSize * 2)
                }

                // 6. Draw Selection Bounding Box & Handles if Selected
                if (isSel) {
                    ctx.strokeStyle = CadTheme.canvasSelectionBox
                    ctx.lineWidth = 1.2
                    ctx.setLineDash([4, 3])
                    var pad = 4
                    ctx.strokeRect(-sw / 2 - pad, -sh / 2 - pad, sw + pad * 2, sh + pad * 2)
                    ctx.setLineDash([])

                    // Corner & Edge Handles
                    ctx.fillStyle = CadTheme.canvasHandleFill
                    ctx.strokeStyle = CadTheme.canvasHandleBorder
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
                }

                ctx.restore()
            }
        }
    }

    // Viewport Interactions: Panning, Zooming, and Mouse Coordinate Telemetry
    MouseArea {
        id: canvasMa
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
        cursorShape: pressedButtons & Qt.MiddleButton ? Qt.ClosedHandCursor : Qt.CrossCursor

        property real lastMouseX: 0
        property real lastMouseY: 0
        property bool isDraggingShape: false

        onWheel: function(wheel) {
            var factor = wheel.angleDelta.y > 0 ? 1.15 : 0.85
            var newScale = root.zoomScale * factor
            if (newScale >= 0.4 && newScale <= 15.0) {
                // Zoom around cursor
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
            lastMouseX = mouse.x
            lastMouseY = mouse.y

            // Left Click: Hit-test objects
            if (mouse.button === Qt.LeftButton) {
                var clickMmX = (mouse.x - root.originX) / root.zoomScale
                var clickMmY = (root.originY - mouse.y) / root.zoomScale

                var hitIndex = -1
                for (var i = root.shapes.length - 1; i >= 0; i--) {
                    var s = root.shapes[i]
                    if (!s.visible) continue
                    var halfW = s.wMm / 2
                    var halfH = s.hMm / 2
                    if (clickMmX >= s.xMm - halfW && clickMmX <= s.xMm + halfW &&
                        clickMmY >= s.yMm - halfH && clickMmY <= s.yMm + halfH) {
                        hitIndex = i
                        break
                    }
                }

                root.selectedIndex = hitIndex
                if (hitIndex >= 0) {
                    root.shapeSelected(root.shapes[hitIndex])
                    isDraggingShape = true
                }
                canvas.requestPaint()
            }
        }

        onPositionChanged: function(mouse) {
            // Update live telemetry in mm relative to Galvo optical center (0,0)
            root.mouseCoordMmX = (mouse.x - root.originX) / root.zoomScale
            root.mouseCoordMmY = (root.originY - mouse.y) / root.zoomScale

            var dx = mouse.x - lastMouseX
            var dy = mouse.y - lastMouseY

            // Middle Click Pan or Spacebar Pan
            if (mouse.buttons & Qt.MiddleButton || (mouse.buttons & Qt.LeftButton && (canvasMa.drag.active || !isDraggingShape && root.selectedIndex === -1))) {
                root.panOffsetX += dx
                root.panOffsetY += dy
                canvas.requestPaint()
            } else if (isDraggingShape && (mouse.buttons & Qt.LeftButton) && root.selectedIndex >= 0) {
                // Drag selected shape
                var sel = root.shapes[root.selectedIndex]
                if (!sel.locked) {
                    sel.xMm += dx / root.zoomScale
                    sel.yMm -= dy / root.zoomScale
                    root.shapesChanged()
                    root.shapeModified(sel)
                    canvas.requestPaint()
                }
            }

            lastMouseX = mouse.x
            lastMouseY = mouse.y
        }

        onReleased: {
            isDraggingShape = false
        }
    }

    // Floating In-Canvas HUD for Selected Object Actions
    Rectangle {
        id: floatingHud
        visible: root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length
        height: 34
        radius: 6
        color: CadTheme.isDark ? "#17233D" : "#FFFFFF"
        border.color: CadTheme.borderActive
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

            CadButton {
                iconName: "rotate_90_degrees_cw"
                tooltipText: "Rotate 90° Clockwise"
                onClicked: root.rotateSelectedShape(90)
            }
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: "Center to Galvo Origin (0,0)"
                onClicked: root.centerSelectedShape()
            }
            CadButton {
                iconName: "delete"
                variant: "danger"
                tooltipText: "Delete Object"
                onClicked: root.deleteSelectedShape()
            }
        }
    }

    // Re-paint canvas when theme changes
    Connections {
        target: CadTheme
        function onIsDarkChanged() { canvas.requestPaint() }
    }
}
