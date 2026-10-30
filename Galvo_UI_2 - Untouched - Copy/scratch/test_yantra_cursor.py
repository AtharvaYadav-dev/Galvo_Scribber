import os, sys
sys.path.insert(0, os.path.abspath('.'))

from core.svg_parser import SVGParser
from core.split_printing_manager import SplitPrintingManager
from core.coordinate_mapper import CoordinateConfig
from preview_galvo import GalvoPreviewWidget
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

cfg = CoordinateConfig()
cfg.field_size = 70.0
cfg.galvo_1_is_x = False

parser = SVGParser(field_size=70.0)
polys = parser.parse_to_polygons('svg_files/yantra.svg')

min_x, max_x = min(pt[0] for p in polys for pt in p), max(pt[0] for p in polys for pt in p)
min_y, max_y = min(pt[1] for p in polys for pt in p), max(pt[1] for p in polys for pt in p)
w = max_x - min_x
h = max_y - min_y
shift_x = -(min_x + w/2.0)
shift_y = -(min_y + h/2.0)
shifted = [[(pt[0]+shift_x, pt[1]+shift_y) for pt in p] for p in polys]

mgr = SplitPrintingManager()
mgr.enabled = True
mgr.set_split_grid(2, 2)
mgr.set_raw_polygons(shifted, lens_size=70.0)

# Simulate start_x=25.0 as saved in yantra.svg.json
start_x = 25.0
start_y = 0.0
mgr.generate_tile_queues(cfg, start_x=start_x, start_y=start_y)

preview = GalvoPreviewWidget(config=cfg)
preview.split_mgr = mgr
preview.split_view_mode = 'whole'
preview.draw_split_preview(mgr, 'whole')

active_t = mgr.tiles[0] # Part 1
cx, cy = active_t.center
print(f'Active Tile: {active_t.label}, center=({cx:.2f}, {cy:.2f})')

# Let's inspect commands in active_t.galvo_queue
mark_cmds = [cmd for cmd in active_t.galvo_queue if cmd['type'] == 'mark']
print(f'Total mark commands in Part 1: {len(mark_cmds)}')

# Test first 5 mark commands
for i in range(min(5, len(mark_cmds))):
    cmd = mark_cmds[i]
    gx, gy = cmd['x'], cmd['y']
    preview.update_progress(i, gx, gy, 'mark')
    cursor_pos = preview.laser_cursor.pos()
    print(f'Cmd {i}: gx={gx}, gy={gy} -> Cursor: ({cursor_pos.x():.2f}, {cursor_pos.y():.2f})')
    
# Let's see bounding box of Part 1 in design space
p1_polys = active_t.polygons
p1_min_x = min(pt[0] for p in p1_polys for pt in p)
p1_max_x = max(pt[0] for p in p1_polys for pt in p)
p1_min_y = min(pt[1] for p in p1_polys for pt in p)
p1_max_y = max(pt[1] for p in p1_polys for pt in p)
print(f'Part 1 Polygons bounds: X=[{p1_min_x:.2f}, {p1_max_x:.2f}], Y=[{p1_min_y:.2f}, {p1_max_y:.2f}]')
print(f'Expected Scene X in [{p1_min_x:.2f}, {p1_max_x:.2f}], Scene Y in [{-p1_max_y:.2f}, {-p1_min_y:.2f}]')

first_pos = preview.laser_cursor.pos()
print(f'Actual First Cursor pos: X={first_pos.x():.2f}, Y={first_pos.y():.2f}')
if p1_min_x <= first_pos.x() <= p1_max_x and -p1_max_y <= first_pos.y() <= -p1_min_y:
    print('SUCCESS: Cursor is within Part 1 bounds!')
else:
    print(f'DISCREPANCY: Cursor X={first_pos.x():.2f} (expected [{p1_min_x:.2f}, {p1_max_x:.2f}])!')
    print(f'Difference in X: {first_pos.x() - p1_min_x:.2f} mm')
