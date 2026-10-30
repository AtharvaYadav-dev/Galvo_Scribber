import sys
import os

sys.path.insert(0, os.path.abspath("."))
from core.split_printing_manager import SplitPrintingManager

# Mock QComboBox to verify items and data
class MockComboBox:
    def __init__(self):
        self.items = []
        self._current_index = 0

    def clear(self):
        self.items = []
        self._current_index = -1

    def addItem(self, label, data):
        self.items.append((label, data))
        if self._current_index == -1:
            self._current_index = 0

    def count(self):
        return len(self.items)

    def itemData(self, index):
        if 0 <= index < len(self.items):
            return self.items[index][1]
        return None

    def itemText(self, index):
        if 0 <= index < len(self.items):
            return self.items[index][0]
        return ""

    def currentData(self):
        return self.itemData(self._current_index)

    def currentText(self):
        return self.itemText(self._current_index)

    def setCurrentIndex(self, idx):
        if 0 <= idx < len(self.items):
            self._current_index = idx

    def blockSignals(self, b):
        pass


class MockMainWindow:
    def __init__(self):
        self.split_mgr = SplitPrintingManager()
        self.combo_split_preset = MockComboBox()
        self.galvo_config = type("Config", (), {"field_size": 70.0})()

    def update_split_preset_options(self, width: float = 0.0, height: float = 0.0, lens_size: float = None):
        if lens_size is None or lens_size <= 0:
            lens_size = getattr(self.galvo_config, 'field_size', 100.0)

        if width <= 0 or height <= 0:
            width = getattr(self.split_mgr, 'design_width', 0.0)
            height = getattr(self.split_mgr, 'design_height', 0.0)

        current_data = self.combo_split_preset.currentData()
        valid_presets = self.split_mgr.get_valid_presets(width, height, lens_size)

        self.combo_split_preset.blockSignals(True)
        self.combo_split_preset.clear()

        selected_idx = -1
        for idx, (label, pc, pr) in enumerate(valid_presets):
            self.combo_split_preset.addItem(label, (pc, pr))
            if current_data and current_data == (pc, pr):
                selected_idx = idx

        if selected_idx >= 0:
            self.combo_split_preset.setCurrentIndex(selected_idx)
        elif self.combo_split_preset.count() > 0:
            self.combo_split_preset.setCurrentIndex(0)
            data = self.combo_split_preset.itemData(0)
            if data and hasattr(self.split_mgr, 'set_split_grid'):
                self.split_mgr.num_cols, self.split_mgr.num_rows = data[0], data[1]

        self.combo_split_preset.blockSignals(False)


win = MockMainWindow()

# Test 1: User scenario: 150x150 mm design on 70mm lens
print("=== Scenario 1: 150x150 mm on 70 mm lens ===")
w, h, lens_size = 150.0, 150.0, 70.0
win.split_mgr.design_width = w
win.split_mgr.design_height = h
win.update_split_preset_options(w, h, lens_size)

items = [win.combo_split_preset.itemText(i) for i in range(win.combo_split_preset.count())]
datas = [win.combo_split_preset.itemData(i) for i in range(win.combo_split_preset.count())]
print(f"Dropdown options count: {len(items)}")
for t, d in zip(items, datas):
    print(f"  {t} -> {d} (tile: {w/d[0]:.1f} x {h/d[1]:.1f} mm)")

# Check that 2x2 is NOT in the dropdown
assert (2, 2) not in datas, "FAIL: 2x2 grid should be HIDDEN!"
assert (2, 1) not in datas, "FAIL: 2x1 grid should be HIDDEN!"
assert (1, 2) not in datas, "FAIL: 1x2 grid should be HIDDEN!"
assert (3, 2) not in datas, "FAIL: 3x2 grid should be HIDDEN!"
assert (2, 3) not in datas, "FAIL: 2x3 grid should be HIDDEN!"
assert (4, 2) not in datas, "FAIL: 4x2 grid should be HIDDEN!"

# Check that 3x3 IS in the dropdown and is the first/suggested preset
assert (3, 3) in datas, "FAIL: 3x3 grid MUST be available!"
s_c, s_r, s_label = win.split_mgr.suggest_splits(w, h, lens_size)
print(f"Suggested preset: {s_label} (cols={s_c}, rows={s_r})")
assert (s_c, s_r) == (3, 3), f"FAIL: Expected (3, 3) suggestion, got ({s_c}, {s_r})"
print("Scenario 1 PASSED: 2x2 is completely hidden and 3x3 is suggested!\n")

# Test 2: 80x80 mm design on 70 mm lens
print("=== Scenario 2: 80x80 mm on 70 mm lens ===")
w2, h2 = 80.0, 80.0
win.split_mgr.design_width = w2
win.split_mgr.design_height = h2
win.update_split_preset_options(w2, h2, lens_size)
datas2 = [win.combo_split_preset.itemData(i) for i in range(win.combo_split_preset.count())]
print(f"Dropdown options count for 80x80: {len(datas2)}")
assert (2, 2) in datas2, "FAIL: 2x2 grid SHOULD be available for 80x80 (tile=40x40 <= 70)!"
assert (2, 1) not in datas2, "FAIL: 2x1 grid should be HIDDEN for 80x80 (tile=40x80 > 70)!"
assert (1, 2) not in datas2, "FAIL: 1x2 grid should be HIDDEN for 80x80 (tile=80x40 > 70)!"
print("Scenario 2 PASSED: 2x2 is shown for 80x80, while 2x1 and 1x2 are hidden!\n")

# Test 3: Slicing 150x150 square with 3x3 grid
print("=== Scenario 3: Verify Slicing 150x150 mm with 3x3 Grid ===")
# Create a 150x150 mm square centered at (0, 0)
poly_150 = [
    (-75.0, -75.0),
    (75.0, -75.0),
    (75.0, 75.0),
    (-75.0, 75.0),
    (-75.0, -75.0)
]
win.split_mgr.set_split_grid(3, 3)
win.split_mgr.set_raw_polygons([poly_150], lens_size=70.0)
print(f"Generated tiles count: {len(win.split_mgr.tiles)}")
assert len(win.split_mgr.tiles) == 9, f"Expected 9 tiles, got {len(win.split_mgr.tiles)}"

for t in win.split_mgr.tiles:
    print(f"  Tile {t.part_number} (col={t.col}, row={t.row}): size={t.width:.1f}x{t.height:.1f}mm, polys={len(t.polygons)}")
    assert t.width <= 70.05 and t.height <= 70.05, f"Tile {t.width}x{t.height} exceeds 70mm lens!"

print("\nALL SCENARIO TESTS PASSED SUCCESSFULLY!")
