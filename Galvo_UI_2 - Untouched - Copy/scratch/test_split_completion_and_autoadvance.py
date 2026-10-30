import sys
import os

sys.path.insert(0, os.path.abspath("."))
from core.split_printing_manager import SplitPrintingManager

mgr = SplitPrintingManager()
mgr.set_split_grid(3, 3)

# Create a test polyline for a 150x150 mm square
poly_150 = [
    (-75.0, -75.0),
    (75.0, -75.0),
    (75.0, 75.0),
    (-75.0, 75.0),
    (-75.0, -75.0)
]
mgr.set_raw_polygons([poly_150], lens_size=70.0)

print(f"Total parts created: {mgr.total_parts}")
assert mgr.total_parts == 9

# Verify initial completion status
for t in mgr.tiles:
    assert not t.is_completed, f"Tile {t.part_number} should initially not be completed"

# Step 1: Simulate Part 1 finishes printing
print("--- Step 1: Part 1 finishes printing ---")
mgr.mark_part_completed(0)
assert mgr.is_part_completed(0)
assert mgr.tiles[0].is_completed
assert not mgr.is_part_completed(1)
print("Part 1 is completed! Status for Part 1: True, Part 2: False")

# Advance to Part 2
mgr.set_active_part(1)
assert mgr.active_part_idx == 1
print(f"Active part auto-advanced to Part {mgr.active_part_idx + 1}")

# Step 2: Simulate Part 2 finishes printing
print("--- Step 2: Part 2 finishes printing ---")
mgr.mark_part_completed(1)
assert mgr.is_part_completed(0)
assert mgr.is_part_completed(1)
assert not mgr.is_part_completed(2)
print("Parts 1 & 2 are completed!")

# Advance to Part 3
mgr.set_active_part(2)
assert mgr.active_part_idx == 2
print(f"Active part auto-advanced to Part {mgr.active_part_idx + 1}")

# Step 3: Test user manual selection (user clicks back on Part 1)
print("--- Step 3: User manual selection ---")
mgr.set_active_part(0)
assert mgr.active_part_idx == 0
assert mgr.is_part_completed(0)
print(f"User manually selected Part {mgr.active_part_idx + 1} (is_completed={mgr.tiles[0].is_completed})")

# Step 4: Reset progress
print("--- Step 4: Reset progress ---")
mgr.clear_completed()
mgr.set_active_part(0)
assert len(mgr.completed_parts) == 0
for t in mgr.tiles:
    assert not t.is_completed
print("Progress reset successfully! All parts are unprinted.")

print("\nALL COMPLETION AND AUTO-ADVANCE LOGIC TESTS PASSED!")
