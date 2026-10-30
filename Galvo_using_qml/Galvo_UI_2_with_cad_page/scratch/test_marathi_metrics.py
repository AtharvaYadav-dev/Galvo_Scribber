import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PySide6.QtGui import QFont, QPainterPath, QGuiApplication

app = QGuiApplication.instance() or QGuiApplication(sys.argv)

fonts_to_test = ["Nirmala UI", "Mangal", "Segoe UI", "Arial"]
sample_texts = ["मराठी", "श्री", "महाराष्ट्र", "गणेश", "क", "ॐ"]

for f_name in fonts_to_test:
    for txt in sample_texts:
        h_mm = 4.0
        qf = QFont(f_name, int(round(h_mm * 10)))
        path = QPainterPath()
        path.addText(0, 0, qf, txt)
        br = path.boundingRect()
        print(f"Font: {f_name:12} | Text: {txt:8} | rect: x={br.x():.2f}, y={br.y():.2f}, w={br.width():.2f}, h={br.height():.2f}")
