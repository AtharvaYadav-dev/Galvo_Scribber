import sys
import os
_app_dir = os.path.abspath(".")
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtGui import QGuiApplication
app = QGuiApplication(sys.argv)

from bridges.cad_bridge import CadBridge
bridge = CadBridge()

# Test Pen 0
shp0 = {'id': 1, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20, 'penId': 0, 'hatched': True}
l0 = bridge.computeHatchPreviewLines(shp0)
print(f"Pen 0 Hatch: count={len(l0)}, line pen_id={l0[0]['pen_id'] if l0 else None}")

# Test Pen 2 (Red)
shp2 = {'id': 2, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20, 'penId': 2, 'hatched': True}
l2 = bridge.computeHatchPreviewLines(shp2)
print(f"Pen 2 Hatch: count={len(l2)}, line pen_id={l2[0]['pen_id'] if l2 else None}")

# Test Pen 1 (Blue)
shp1 = {'id': 3, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20, 'penId': 1, 'hatched': True}
l1 = bridge.computeHatchPreviewLines(shp1)
print(f"Pen 1 Hatch: count={len(l1)}, line pen_id={l1[0]['pen_id'] if l1 else None}")

