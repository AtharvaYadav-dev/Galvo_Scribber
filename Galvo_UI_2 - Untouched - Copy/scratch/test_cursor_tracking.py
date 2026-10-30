import sys
import os

sys.path.insert(0, os.path.abspath("."))
from PySide6.QtWidgets import QApplication
from preview_galvo import GalvoPreviewWidget
from core.split_printing_manager import SplitPrintingManager
from core.coordinate_mapper import CoordinateConfig

app = QApplication.instance() or QApplication([])

cfg = CoordinateConfig()
cfg.field_size = 70.0

preview = GalvoPreviewWidget()
preview.config = cfg

mgr = SplitPrintingManager()
mgr.enabled = True
mgr.set_split_grid(2, 2)

# Design 100x100 centered around (0, 0) -> x in [-50, 50], y in [-50, 50]
# Part 2 is top-right quadrant: x in [0, 50], y in [0, 50], center is (25, 25)
poly = [(10.0, 10.0), (40.0, 10.0), (40.0, 40.0), (10.0, 40.0), (10.0, 10.0)]
mgr.set_raw_polygons([poly], lens_size=70.0)
mgr.generate_tile_queues(cfg)

# Select Part 2 (index 1)
mgr.set_active_part(1)
preview.split_mgr = mgr
preview.split_view_mode = "whole"
preview.draw_split_preview(mgr, "whole")

# In tile 1 (Part 2), tile center is cx=25.0, cy=25.0
tile2 = mgr.tiles[1]
cx, cy = tile2.center
print(f"Tile 2 center: cx={cx}, cy={cy}")

# Take the first mark command from tile 2 queue
mark_cmd = None
for cmd in tile2.galvo_queue:
    if cmd.get('type') == 'mark':
        mark_cmd = cmd
        break

assert mark_cmd is not None
gx, gy = mark_cmd['x'], mark_cmd['y']

# Call update_progress
preview.update_progress(0, gx, gy, 'mark')

cursor_pos = preview.laser_cursor.pos()
print(f"Laser cursor position in 'whole' mode: x={cursor_pos.x():.2f}, y={cursor_pos.y():.2f}")

# The original polygon had points with x in [10, 40] and y in [10, 40].
# In the scene, scene_x = pt_x, scene_y = -pt_y.
# So cursor x must be in [10, 40] and cursor y must be in [-40, -10].
assert 10.0 <= cursor_pos.x() <= 40.0, f"Cursor x {cursor_pos.x()} not in [10, 40]"
assert -40.0 <= cursor_pos.y() <= -10.0, f"Cursor y {cursor_pos.y()} not in [-40, -10]"

print("Now testing 'active_lens' mode...")
preview.split_view_mode = "active_lens"
preview.update_progress(0, gx, gy, 'mark')
cursor_pos_lens = preview.laser_cursor.pos()
print(f"Laser cursor position in 'active_lens' mode: x={cursor_pos_lens.x():.2f}, y={cursor_pos_lens.y():.2f}")
# In lens mode, centered around (0,0), so (pt_x - 25, -(pt_y - 25))
# For pt in [10, 40], centered is in [-15, +15]
assert -15.0 <= cursor_pos_lens.x() <= 15.0, f"Lens cursor x {cursor_pos_lens.x()} not centered"
assert -15.0 <= cursor_pos_lens.y() <= 15.0, f"Lens cursor y {cursor_pos_lens.y()} not centered"

print("\nALL CURSOR TRACKING ACCURACY TESTS PASSED!")
