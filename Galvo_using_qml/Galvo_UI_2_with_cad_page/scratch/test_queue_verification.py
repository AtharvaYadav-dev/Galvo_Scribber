import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtCore import QCoreApplication
from bridges.galvo_bridge import GalvoBridge
from bridges.matrix_bridge import MatrixBridge
from core.motion_planner import MotionPlanner

def test_queue_generation():
    app = QCoreApplication.instance() or QCoreApplication([])
    galvo = GalvoBridge()
    matrix = MatrixBridge(galvo_bridge=galvo)

    scale, field_size = matrix._get_scale_and_field_size()
    center_xy = 32767
    jump_speed = 2000000
    mark_speed = int(1000.0 * scale)

    planner = MotionPlanner()
    planner.clear()

    # Verify hatching on a sample cell
    x0 = int((-10.0) * scale + center_xy)
    y0 = int((-10.0) * scale + center_xy)
    w = int(5.0 * scale)
    h = int(5.0 * scale)
    x1 = x0 + w
    y1 = y0 + h

    poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    hatch_configs = [{
        'enable': True,
        'type': "Bidirectional",
        'angle': 0.0,
        'line_space': 0.05,
        'count': 1,
        'pen_no': 0,
        'hatch_idx': 1
    }]

    planner.generate_hatch([poly], hatch_configs, mark_speed=mark_speed, jump_speed=jump_speed, galvo_units_per_mm=scale)
    print(f"Generated {len(planner.preview_queue)} commands for sample cell hatch.")
    assert len(planner.preview_queue) > 10, "Expected hatch lines to be populated in preview queue"

    # Verify pass_change
    has_pass = any(c.get('type') == 'pass_change' for c in planner.preview_queue)
    assert has_pass, "Expected pass_change in preview queue"

    # Verify jumps have speed 2000000
    jumps = [c for c in planner.preview_queue if c.get('type') == 'jump']
    assert all(c.get('speed') == jump_speed for c in jumps), "All jumps should have jump_speed 2000000"

    print("QUEUE GENERATION VERIFIED PERFECTLY!")

if __name__ == "__main__":
    test_queue_generation()
