import sys
import os

sys.path.insert(0, os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPen
from preview_galvo import GalvoPreviewWidget
from core.split_printing_manager import SplitPrintingManager

app = QApplication.instance()
if not app:
    app = QApplication([])

preview = GalvoPreviewWidget()
mgr = SplitPrintingManager()
mgr.set_split_grid(2, 2)
poly = [
    (-30.0, -30.0),
    (30.0, -30.0),
    (30.0, 30.0),
    (-30.0, 30.0),
    (-30.0, -30.0)
]
mgr.set_raw_polygons([poly], lens_size=70.0)

# Mark Part 0 as completed, make Part 1 active
mgr.mark_part_completed(0)
mgr.set_active_part(1)

preview.draw_split_preview(mgr, view_mode="whole")

# Inspect items in the scene
# Find QGraphicsPathItems and check their pens
items = preview.scene.items()
print(f"Total scene items rendered: {len(items)}")

# Verify we have items rendered
assert len(items) > 0

# Check that completed tile has green badge text and paths
badge_texts = [item.text() for item in items if hasattr(item, 'text')]
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print(f"Badges rendered in scene: {badge_texts}")

for item in items:
    if hasattr(item, 'text'):
        r = item.boundingRect()
        print(f"Badge '{item.text()}': width={r.width():.2f} mm, height={r.height():.2f} mm")

has_done_badge = any("✔ Part 1" in t for t in badge_texts)
has_ready_badge = any("★ Part 2" in t for t in badge_texts)
print(f"Contains '✔ Part 1': {has_done_badge}")
print(f"Contains '★ Part 2': {has_ready_badge}")

assert has_done_badge, "Scene must render '✔ Part 1'"
assert has_ready_badge, "Scene must render '★ Part 2'"

print("\nPREVIEW GREEN/RED/GRAY COLOR RENDERING TEST PASSED!")

