import QtQuick
import "../.."

Canvas {
    id: ruler

    property bool isVertical: false
    property real originPos: isVertical ? (height / 2) : (width / 2) // Canvas center in px
    property real zoomScale: 2.5 // Screen pixels per millimeter
    property real mouseCoordMm: 0.0 // Current mouse coordinate in mm to draw marker

    renderTarget: Canvas.FramebufferObject
    renderStrategy: Canvas.Immediate

    onOriginPosChanged: requestPaint()
    onZoomScaleChanged: requestPaint()
    onMouseCoordMmChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    Connections {
        target: Theme
        function onIsDarkChanged() { ruler.requestPaint() }
    }

    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)

        var isDark = Theme.isDark
        ctx.fillStyle = isDark ? "#0A0F1D" : "#F8FAFC"
        ctx.fillRect(0, 0, width, height)

        ctx.strokeStyle = isDark ? "#1E2A42" : "#DCE3EE"
        ctx.lineWidth = 1

        // Baseline border
        ctx.beginPath()
        if (isVertical) {
            ctx.moveTo(width - 0.5, 0)
            ctx.lineTo(width - 0.5, height)
        } else {
            ctx.moveTo(0, height - 0.5)
            ctx.lineTo(width, height - 0.5)
        }
        ctx.stroke()

        // Adaptive tick frequency based on zoom scale
        var mmStep = 1.0
        var labelStep = 10.0
        if (zoomScale < 0.8) {
            mmStep = 10.0
            labelStep = 50.0
        } else if (zoomScale < 1.5) {
            mmStep = 5.0
            labelStep = 20.0
        } else if (zoomScale > 6.0) {
            mmStep = 0.5
            labelStep = 5.0
        }

        var pxStep = mmStep * zoomScale
        if (pxStep <= 0) return

        var center = isVertical ? originPos : originPos
        var maxLen = isVertical ? height : width

        var minMm = Math.floor((-center) / zoomScale) - 5
        var maxMm = Math.ceil((maxLen - center) / zoomScale) + 5
        var startMm = Math.floor(minMm / mmStep) * mmStep

        ctx.strokeStyle = isDark ? "#28385A" : "#CBD5E1"
        ctx.lineWidth = 1
        ctx.beginPath()

        for (var mm = startMm; mm <= maxMm; mm += mmStep) {
            // In CAD Cartesian coordinates, +Y is upwards
            var pos = isVertical ? (center - mm * zoomScale) : (center + mm * zoomScale)
            if (pos < -5 || pos > maxLen + 5) continue

            var isMajor = (Math.abs(mm % labelStep) < 0.001)
            var isMedium = (Math.abs(mm % (labelStep / 2)) < 0.001)

            var tickLen = isMajor ? 10 : (isMedium ? 6 : 3)

            if (isVertical) {
                ctx.moveTo(width - tickLen, pos)
                ctx.lineTo(width, pos)
            } else {
                ctx.moveTo(pos, height - tickLen)
                ctx.lineTo(pos, height)
            }
        }
        ctx.stroke()

        // Draw Labels for Major ticks
        ctx.fillStyle = isDark ? "#8493A8" : "#64728A"
        ctx.font = "9px Consolas, monospace"
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"

        for (var lmm = startMm; lmm <= maxMm; lmm += mmStep) {
            if (Math.abs(lmm % labelStep) < 0.001) {
                var lpos = isVertical ? (center - lmm * zoomScale) : (center + lmm * zoomScale)
                if (lpos < 8 || lpos > maxLen - 8) continue

                var txt = Math.round(lmm).toString()
                if (isVertical) {
                    ctx.save()
                    ctx.translate(14, lpos)
                    ctx.rotate(-Math.PI / 2)
                    ctx.fillText(txt, 0, 0)
                    ctx.restore()
                } else {
                    ctx.fillText(txt, lpos, 9)
                }
            }
        }

        // Draw live mouse position tracking reticle
        var markerPos = isVertical ? (center - mouseCoordMm * zoomScale) : (center + mouseCoordMm * zoomScale)
        if (markerPos >= 0 && markerPos <= maxLen) {
            ctx.fillStyle = isDark ? "#00E5FF" : "#192D78"
            ctx.beginPath()
            if (isVertical) {
                ctx.moveTo(width, markerPos)
                ctx.lineTo(width - 6, markerPos - 3.5)
                ctx.lineTo(width - 6, markerPos + 3.5)
            } else {
                ctx.moveTo(markerPos, height)
                ctx.lineTo(markerPos - 3.5, height - 6)
                ctx.lineTo(markerPos + 3.5, height - 6)
            }
            ctx.closePath()
            ctx.fill()
        }
    }
}
