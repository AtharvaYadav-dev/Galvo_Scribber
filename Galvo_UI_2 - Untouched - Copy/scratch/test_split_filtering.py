import sys
import os

sys.path.insert(0, os.path.abspath("."))
from core.split_printing_manager import SplitPrintingManager

mgr = SplitPrintingManager()

print("--- Test 1: 150x150 mm file on 70mm lens ---")
valid_150 = mgr.get_valid_presets(150.0, 150.0, 70.0)
print(f"Total valid presets: {len(valid_150)}")
for label, c, r in valid_150:
    tw = 150.0 / c
    th = 150.0 / r
    print(f"  {label}: cols={c}, rows={r}, tile={tw:.1f}x{th:.1f}mm")
    assert tw <= 70.05 and th <= 70.05, f"Tile {tw}x{th} exceeds 70mm lens!"

# Verify that 2x2, 2x1, 1x2 are NOT in valid_150
has_2x2 = any(c == 2 and r == 2 for _, c, r in valid_150)
has_2x1 = any(c == 2 and r == 1 for _, c, r in valid_150)
has_1x2 = any(c == 1 and r == 2 for _, c, r in valid_150)
print(f"Contains 2x2: {has_2x2} (Expected: False)")
print(f"Contains 2x1: {has_2x1} (Expected: False)")
print(f"Contains 1x2: {has_1x2} (Expected: False)")
assert not has_2x2, "2x2 MUST be hidden for 150x150 on 70mm lens!"
assert not has_2x1, "2x1 MUST be hidden for 150x150 on 70mm lens!"
assert not has_1x2, "1x2 MUST be hidden for 150x150 on 70mm lens!"

# Verify suggest_splits returns 3x3
s_c, s_r, s_label = mgr.suggest_splits(150.0, 150.0, 70.0)
print(f"Suggested split: {s_label} (cols={s_c}, rows={s_r})")
assert s_c == 3 and s_r == 3, f"Expected 3x3 suggestion, got {s_c}x{s_r}"

print("\n--- Test 2: 80x80 mm file on 70mm lens ---")
valid_80 = mgr.get_valid_presets(80.0, 80.0, 70.0)
has_2x2_80 = any(c == 2 and r == 2 for _, c, r in valid_80)
has_2x1_80 = any(c == 2 and r == 1 for _, c, r in valid_80)
print(f"80x80: Contains 2x2: {has_2x2_80} (Expected: True, tile=40x40)")
print(f"80x80: Contains 2x1: {has_2x1_80} (Expected: False, tile=40x80 > 70)")
assert has_2x2_80, "2x2 should be allowed for 80x80 on 70mm lens!"
assert not has_2x1_80, "2x1 should NOT be allowed for 80x80 on 70mm lens!"

print("\n--- Test 3: No file loaded (0x0) ---")
valid_0 = mgr.get_valid_presets(0.0, 0.0, 70.0)
print(f"Default presets count: {len(valid_0)}")
assert len(valid_0) == len(SplitPrintingManager.BASE_PRESETS)

print("\nALL SPLIT FILTERING TESTS PASSED!")
