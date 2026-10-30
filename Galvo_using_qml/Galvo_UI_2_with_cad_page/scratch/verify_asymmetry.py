from PySide6.QtGui import QFont, QFontMetricsF, QGuiApplication
import sys

app = QGuiApplication.instance() or QGuiApplication(sys.argv)

qf = QFont("AMS Vasudeva", 34)
fm = QFontMetricsF(qf)
ascent = fm.ascent()
descent = fm.descent()
print(f"ascent: {ascent}, descent: {descent}")
offset = (ascent - descent) / 2.0
print(f"Asymmetry offset: {offset}")
print(f"When middle is used, baseline is at: {-offset}")
print(f"Total shift up: {ascent - offset}")

