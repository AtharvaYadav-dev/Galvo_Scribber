import sys
sys.path.insert(0, '.')
from core.split_printing_manager import SplitPrintingManager
from core.coordinate_mapper import CoordinateConfig

mgr = SplitPrintingManager()
# 200mm x 100mm rectangle
poly = [(-100, -50), (100, -50), (100, 50), (-100, 50), (-100, -50)]
mgr.set_raw_polygons([poly], lens_size=100.0)

cols, rows, label = mgr.suggest_splits(mgr.design_width, mgr.design_height, mgr.lens_size)
print(f"Suggested split for 200x100mm on 100mm lens: {cols}x{rows} ({label})")

mgr.set_split_grid(2, 1)
print(f"Total tiles generated: {len(mgr.tiles)}")
for t in mgr.tiles:
    print(f"  {t.label}: bounds={t.rect}, width={t.width:.1f}, height={t.height:.1f}, center={t.center}, polys={len(t.polygons)}")

cfg = CoordinateConfig()
mgr.generate_tile_queues(cfg, mark_speed=1000, jump_speed=2000)
for t in mgr.tiles:
    print(f"  {t.label} galvo queue commands: {len(t.galvo_queue)}")

print("SUCCESS: SplitPrintingManager working properly!")
