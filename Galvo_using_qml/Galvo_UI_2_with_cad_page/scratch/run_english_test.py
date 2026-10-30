import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtQuick import QQuickView

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

            ctx.save()
            ctx.translate(cx, cy)
            ctx.strokeStyle = "#06B6D4"
            ctx.lineWidth = 2
            ctx.strokeRect(-sw/2, -sh/2, sw, sh)

            ctx.fillStyle = "#FFFFFF"
            ctx.textAlign = "center"
            ctx.textBaseline = "alphabetic"
            ctx.font = "34px 'Segoe UI', sans-serif"
            
            // Baseline at +sh * 0.25
            ctx.fillText("ENGLISH", 0, sh * 0.25)
            ctx.restore()
        }
    }
}
"""

with open("scratch/test_english_alphabetic.qml", "w", encoding="utf-8") as f:
    f.write(qml_test)

view = QQuickView()
view.setSource(QUrl.fromLocalFile(os.path.abspath("scratch/test_english_alphabetic.qml")))
view.show()

def snap():
    img = view.grabWindow()
    img.save("scratch/test_english_alphabetic.png")
    app.quit()

QTimer.singleShot(400, snap)
app.exec()

