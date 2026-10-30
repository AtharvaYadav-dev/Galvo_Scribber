import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PySide6.QtGui import QFont, QPainterPath, QGuiApplication

app = QGuiApplication.instance() or QGuiApplication(sys.argv)
h_mm = 4.0
qf = QFont("AMS Vasudeva", int(round(h_mm * 10)))
for sample in ["A", "a", "k", "d", "मराठी", "1", "क", "श"]:
    path = QPainterPath()
    path.addText(0, 0, qf, sample)
    br = path.boundingRect()
    print(f"Sample: {sample:6} | rect: x={br.x():.2f}, y={br.y():.2f}, w={br.width():.2f}, h={br.height():.2f}")

