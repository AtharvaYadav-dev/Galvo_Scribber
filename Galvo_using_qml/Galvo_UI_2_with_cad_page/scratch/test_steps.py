import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRectF, QPointF
from cad_canvas import CadCanvasWidget
from cad_items import CadRectItem, CadTextItem, CadHatchItem

app = QApplication.instance() or QApplication(sys.argv)
class MockMainWindow:
    def __init__(self):
        self.galvo_config = None
        from core.motion_planner import MotionPlanner
        self.planner = MotionPlanner()
        self.galvo_controller = None

mw = MockMainWindow()
widget = CadCanvasWidget(main_window=mw)

rect = CadRectItem(QRectF(-20, -20, 40, 40))
widget.scene.addItem(rect)

print("Step 1: getting shapes", flush=True)
shapes = [item for item in widget.scene.items() if isinstance(item, CadRectItem)]

print("Step 2: path", flush=True)
path = rect.scene_painter_path()
print("Polygons count:", len(path.toSubpathPolygons()), flush=True)

print("Step 3: map to galvo", flush=True)
gx, gy = widget._map_to_galvo(0, 0)
print(f"Galvo coords: {gx}, {gy}", flush=True)

print("Step 4: add to planner", flush=True)
mw.planner.add_jump(gx, gy)
mw.planner.add_mark(gx + 100, gy + 100)
print("Planner queue size:", len(mw.planner.send_queue), flush=True)

print("Step 5: test if QMessageBox blocks", flush=True)
# If len(planner.send_queue) was 0, it calls QMessageBox.information!
# In an offscreen / headless script with no user, QMessageBox.information waits forever!
os._exit(0)
