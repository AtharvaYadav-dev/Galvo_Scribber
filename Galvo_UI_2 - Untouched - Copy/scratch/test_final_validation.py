import os, sys
sys.path.insert(0, os.path.abspath('.'))

from preview_galvo import GalvoPreviewWidget
from core.split_printing_manager import SplitPrintingManager
from core.coordinate_mapper import CoordinateConfig
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

cfg = CoordinateConfig()
cfg.field_size = 70.0

mgr = SplitPrintingManager()
mgr.enabled = True
mgr.set_split_grid(3, 3)

poly = [(-60.0, 60.0), (-30.0, 60.0), (-30.0, 30.0), (-60.0, 30.0), (-60.0, 60.0)]
mgr.set_raw_polygons([poly], lens_size=70.0)
mgr.generate_tile_queues(cfg, start_x=0.0, start_y=0.0)

preview = GalvoPreviewWidget(config=cfg)
preview.split_mgr = mgr
preview.split_view_mode = 'whole'
preview.draw_split_preview(mgr, 'whole')

tile = mgr.tiles[0]
for cmd in tile.galvo_queue[:5]:
    if cmd['type'] in ('jump', 'mark'):
        preview.update_progress(0, cmd['x'], cmd['y'], cmd['type'])
        c = preview.laser_cursor.pos()
        print(f"Progress cmd {cmd['type']}: Cursor at ({c.x():.3f}, {c.y():.3f})")

print("Validation script completed cleanly!")
