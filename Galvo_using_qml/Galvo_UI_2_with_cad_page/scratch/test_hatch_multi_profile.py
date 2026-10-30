import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bridges.cad_bridge import CadBridge
from core.motion_planner import compute_hatch_geometry

def test_hatch():
    bridge = CadBridge()
    profiles = bridge.getAllHatchProfiles()
    print("Initial profiles:", profiles)

    # Test shape (rect 20x20 at 0,0)
    test_rect = {
        "id": 1,
        "type": "rect",
        "xMm": 0,
        "yMm": 0,
        "wMm": 20,
        "hMm": 20,
        "rotation": 0,
        "visible": True,
        "hatched": True,
        "mark_contour": True
    }

    polys = bridge._shape_to_polygons(test_rect)
    print(f"Shape to polygons: {len(polys)} polygons, {len(polys[0])} points")

    # Compute hatch preview lines
    lines = bridge.computeHatchPreviewLines(test_rect)
    print(f"Computed preview hatch lines: {len(lines)} lines")

    # Test queue building with hatch
    bridge._shapes = [test_rect]
    bridge.executeMark([test_rect], False, -1, 1)
    print(f"Planner send_queue length: {len(bridge.planner.send_queue)}")
    assert len(bridge.planner.send_queue) > 0, "Queue should not be empty"
    print("Test hatch multi profile PASSED successfully!")

if __name__ == "__main__":
    test_hatch()
