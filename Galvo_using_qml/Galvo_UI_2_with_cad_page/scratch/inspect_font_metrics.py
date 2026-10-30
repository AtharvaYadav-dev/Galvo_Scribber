from PySide6.QtGui import QFont, QFontMetricsF, QGuiApplication, QPainterPath
import sys

app = QGuiApplication.instance() or QGuiApplication(sys.argv)

for fname in ["AMS Vasudeva", "Nirmala UI", "Segoe UI", "Arial"]:
    qf = QFont(fname, 34)
    fm = QFontMetricsF(qf)
    print(f"=== Font: {fname} (size 34) ===")
    print(f"  ascent: {fm.ascent():.2f}")
    print(f"  descent: {fm.descent():.2f}")
    print(f"  height: {fm.height():.2f}")
    print(f"  leading: {fm.leading():.2f}")
    print(f"  capHeight: {fm.capHeight():.2f}")
    print(f"  xHeight: {fm.xHeight():.2f}")
    
    path = QPainterPath()
    path.addText(0, 0, qf, "A")
    br_a = path.boundingRect()
    print(f"  'A' path rect: y={br_a.y():.2f}, h={br_a.height():.2f}")

    path_m = QPainterPath()
    path_m.addText(0, 0, qf, "म")
    br_m = path_m.boundingRect()
    print(f"  'म' path rect: y={br_m.y():.2f}, h={br_m.height():.2f}")

