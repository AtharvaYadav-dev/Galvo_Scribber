import QtQuick

Rectangle {
    width: 800
    height: 700
    color: "#0B1120"

    Canvas {
        id: cv
        anchors.fill: parent
        onPaint: {
            var ctx = cv.getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var sw = 100
            var sh = 40
            var baselines = ["middle", "alphabetic", "top", "bottom"]

            for (var i = 0; i < baselines.length; i++) {
                var cx = 150 + (i % 2) * 350
                var cy = 150 + Math.floor(i / 2) * 300

                ctx.save()
                ctx.translate(cx, cy)
                ctx.strokeStyle = "#06B6D4"
                ctx.lineWidth = 2
                ctx.strokeRect(-sw/2, -sh/2, sw, sh)

                ctx.fillStyle = "#FFFFFF"
                ctx.textAlign = "center"
                ctx.textBaseline = baselines[i]
                ctx.font = "34px 'AMS Vasudeva', sans-serif"

                var ly = 0
                if (baselines[i] === "alphabetic") {
                    ly = sh * 0.25 // standard baseline offset from center
                }
                ctx.fillText("मराठी", 0, ly)

                // Label
                ctx.fillStyle = "#F59E0B"
                ctx.font = "14px sans-serif"
                ctx.textBaseline = "top"
                ctx.fillText("baseline: " + baselines[i] + " (ly=" + ly + ")", 0, sh/2 + 10)

                ctx.restore()
            }
        }
    }
}
