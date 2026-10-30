import sys
import os

sys.path.insert(0, os.path.abspath("."))
from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QFont

app = QApplication.instance()
if not app:
    app = QApplication([])

scene = QGraphicsScene()

# Test 1: default font (pointSize 8)
t1 = scene.addSimpleText("Part 1")
t1.setFont(QFont("Arial", 8))
r1 = t1.boundingRect()
print(f"Default 8pt boundingRect: width={r1.width():.2f} mm, height={r1.height():.2f} mm")

# Test 2: setPointSizeF(2.5)
t2 = scene.addSimpleText("Part 1")
f2 = QFont("Arial")
f2.setPointSizeF(2.5)
t2.setFont(f2)
r2 = t2.boundingRect()
print(f"setPointSizeF(2.5) boundingRect: width={r2.width():.2f} mm, height={r2.height():.2f} mm")

# Test 3: setPixelSize(3)
t3 = scene.addSimpleText("Part 1")
f3 = QFont("Arial")
f3.setPixelSize(3)
t3.setFont(f3)
r3 = t3.boundingRect()
print(f"setPixelSize(3) boundingRect: width={r3.width():.2f} mm, height={r3.height():.2f} mm")

# Test 4: setPixelSize(2)
t4 = scene.addSimpleText("★ Part 2 (READY)")
f4 = QFont("Arial", -1, QFont.Bold)
f4.setPixelSize(2)
t4.setFont(f4)
r4 = t4.boundingRect()
print(f"setPixelSize(2) boundingRect: width={r4.width():.2f} mm, height={r4.height():.2f} mm")

# Test 5: scale down
t5 = scene.addSimpleText("★ Part 2 (READY)")
f5 = QFont("Arial", 8, QFont.Bold)
t5.setFont(f5)
t5.setScale(0.25)
r5 = t5.sceneBoundingRect()
print(f"scale(0.25) sceneBoundingRect: width={r5.width():.2f} mm, height={r5.height():.2f} mm")
