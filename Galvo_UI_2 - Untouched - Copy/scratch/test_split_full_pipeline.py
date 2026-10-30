import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from core.svg_parser import SVGParser
from core.coordinate_mapper import CoordinateConfig
from core.split_printing_manager import SplitPrintingManager
from preview_galvo import GalvoPreviewWidget

print("=== STEP 1: Parse Large SVG File ===")
svg_file = os.path.join("svg_files", "250 122mmsizeMicron channel.svg")
assert os.path.exists(svg_file), f"SVG file {svg_file} not found!"

parser = SVGParser(field_size=100.0)
polys = parser.parse_to_polygons(svg_file)
print(f"Parsed {len(polys)} polygon loops from {svg_file}")

# Calculate bounds
min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')
for p in polys:
    for pt in p:
        min_x = min(min_x, pt[0])
        max_x = max(max_x, pt[0])
        min_y = min(min_y, pt[1])
        max_y = max(max_y, pt[1])

w = max_x - min_x
h = max_y - min_y
print(f"SVG Dimensions: {w:.2f} mm x {h:.2f} mm (Lens Size: 100.0 mm)")
assert w > 100.0 or h > 100.0, "Expected design to exceed 100mm lens size"

print("\n=== STEP 2: Test Suggest Splits ===")
mgr = SplitPrintingManager()
mgr.enabled = True
c, r, label = mgr.suggest_splits(w, h, 100.0)
print(f"Auto-suggested split for {w:.1f}x{h:.1f} mm: {c} cols x {r} rows -> {label}")
assert c * r <= 8, f"Splits {c}x{r} exceed max 8 parts!"

print("\n=== STEP 3: Test Split Presets (Max 8 Parts) ===")
presets_to_test = [
    (2, 1), # 2 splits horizontal
    (1, 2), # 2 splits vertical
    (3, 1), # 3 splits
    (2, 2), # 4 splits
    (3, 2), # 6 splits
    (4, 2), # 8 splits
    (2, 4), # 8 splits
    (8, 1), # 8 splits columns
    (1, 8), # 8 splits rows
]

# Center polygons around origin
cx = min_x + w / 2.0
cy = min_y + h / 2.0
shifted_polys = [[(pt[0] - cx, pt[1] - cy) for pt in p] for p in polys]

for cols, rows in presets_to_test:
    mgr.set_raw_polygons(shifted_polys, lens_size=100.0)
    mgr.set_split_grid(cols, rows)
    total = len(mgr.tiles)
    assert total == cols * rows, f"Expected {cols*rows} tiles, got {total}"
    assert total <= 8, f"Exceeded max 8 parts: {total}"
    print(f"Preset {cols}x{rows} -> {total} parts generated. All tiles within lens? {[t.width <= 100.0 and t.height <= 100.0 for t in mgr.tiles]}")

print("\n=== STEP 4: Test Queue Generation for 4 Splits (2x2) ===")
mgr.set_split_grid(2, 2)
cfg = CoordinateConfig()
cfg.field_size = 100.0
mgr.generate_tile_queues(cfg, start_x=0.0, start_y=0.0, mark_speed=1000, jump_speed=2000, is_hatch=False)

for t in mgr.tiles:
    print(f"  {t.label}: bounds=({t.rect[0]:.1f}, {t.rect[1]:.1f}, {t.rect[2]:.1f}, {t.rect[3]:.1f}), "
          f"size={t.width:.1f}x{t.height:.1f} mm, commands={len(t.galvo_queue)}")
    assert len(t.galvo_queue) > 0, f"Expected commands in {t.label}"

print("\n=== STEP 5: Test Part Navigation & Active Tile Selection ===")
assert mgr.active_part_idx == 0
mgr.next_part()
assert mgr.active_part_idx == 1
print(f"Advanced to: {mgr.get_active_tile().label}")
mgr.next_part()
assert mgr.active_part_idx == 2
print(f"Advanced to: {mgr.get_active_tile().label}")
mgr.prev_part()
assert mgr.active_part_idx == 1
print(f"Stepped back to: {mgr.get_active_tile().label}")
mgr.set_active_part(3)
assert mgr.active_part_idx == 3
print(f"Direct selected: {mgr.get_active_tile().label}")

print("\n=== STEP 6: Test GalvoPreviewWidget Split Rendering ===", flush=True)
preview = GalvoPreviewWidget()

# Render whole file preview with dividers and highlight on active part
preview.draw_split_preview(mgr, view_mode='whole')
print("Rendered 'whole' split preview successfully.", flush=True)

# Switch active part and update highlight
preview.update_split_active_tile(1)
print("Updated active tile highlight to Part 2 successfully.", flush=True)

# Render active part centered at lens
preview.draw_split_preview(mgr, view_mode='active_lens')
print("Rendered 'active_lens' centered view successfully.", flush=True)

# Test signal connection
received_parts = []
preview.part_selected_signal.connect(lambda idx: received_parts.append(idx))
preview.part_selected_signal.emit(2)
assert received_parts == [2], "part_selected_signal failed"
print("part_selected_signal verified.", flush=True)

print("\n==========================================", flush=True)
print("ALL SPLIT PRINTING PIPELINE TESTS PASSED!", flush=True)
print("==========================================", flush=True)
sys.exit(0)
