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
rect.name = "Box_1"
widget.scene.addItem(rect)

hatch = CadHatchItem(target_item=rect, line_pitch=1.0, angle_deg=45.0)
rect.hatch_items.append(hatch)

print("Items in scene:", len(widget.scene.items()), flush=True)
shapes = [item for item in widget.scene.items() if isinstance(item, CadRectItem)]
print("Rect shapes in scene:", len(shapes), flush=True)

try:
    widget._execute_mark()
    print("Execute mark finished without error. Queue size:", len(mw.planner.send_queue), flush=True)
except Exception as e:
    import traceback
    traceback.print_exc()
os._exit(0)
