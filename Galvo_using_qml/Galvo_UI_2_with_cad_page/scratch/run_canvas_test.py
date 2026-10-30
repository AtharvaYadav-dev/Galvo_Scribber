import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl

app = QApplication.instance() or QApplication(sys.argv)

qml_test = """
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

            // Draw center coordinate crosshair
            ctx.strokeStyle = "#475569"
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(0, cy); ctx.lineTo(width, cy)
            ctx.moveTo(cx, 0); ctx.lineTo(cx, height)
            ctx.stroke()

            // Draw object box (cyan dashed) centered at (cx, cy)
            ctx.save()
            ctx.translate(cx, cy)
            ctx.strokeStyle = "#06B6D4"
            ctx.lineWidth = 2
            ctx.strokeRect(-sw/2, -sh/2, sw, sh)

            // Draw text with ctx.fillText
            ctx.fillStyle = "#FFFFFF"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            ctx.font = "34px 'AMS Vasudeva', sans-serif"
            
            // Text drawn at center (0, 0)
            ctx.fillText("मराठी", 0, 0)
            ctx.restore()

            // Also draw another test below for English
            ctx.save()
            ctx.translate(cx, 450)
            ctx.strokeStyle = "#06B6D4"
            ctx.strokeRect(-sw/2, -sh/2, sw, sh)
            ctx.fillStyle = "#FFFFFF"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            ctx.font = "34px 'Segoe UI', sans-serif"
            ctx.fillText("ENGLISH", 0, 0)
            ctx.restore()
        }
    }
}
"""

with open("scratch/test_canvas_font.qml", "w", encoding="utf-8") as f:
    f.write(qml_test)

view = QQuickView()
view.setSource(QUrl.fromLocalFile(os.path.abspath("scratch/test_canvas_font.qml")))
view.show()

def snap():
    img = view.grabWindow()
    img.save("scratch/test_canvas_font.png")
    print("Saved test_canvas_font.png")
    app.quit()

QTimer.singleShot(400, snap)
app.exec()

