
import QtQuick

Rectangle {
    width: 600
    height: 600
    color: "#0B1120"

    Canvas {
        id: cv
        anchors.fill: parent
        onPaint: {
            var ctx = cv.getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var cx = 300
            var cy = 300
            var sw = 100
            var sh = 40

            ctx.save()
            ctx.translate(cx, cy)
            ctx.strokeStyle = "#06B6D4"
            ctx.lineWidth = 2
            ctx.strokeRect(-sw/2, -sh/2, sw, sh)

            ctx.fillStyle = "#FFFFFF"
            ctx.textAlign = "center"
            ctx.textBaseline = "alphabetic"
            ctx.font = "34px 'AMS Vasudeva', sans-serif"
            
            // Baseline at +sh * 0.25
            ctx.fillText("मराठी", 0, sh * 0.25)
            ctx.restore()
        }
    }
}
