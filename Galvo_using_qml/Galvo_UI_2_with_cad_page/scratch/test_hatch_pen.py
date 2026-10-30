import os
import sys

sys.path.insert(0, os.path.abspath("."))
from bridges.cad_bridge import CadBridge

b = CadBridge()

print("--- Test 1: Red shape (penId=2) with no hatch_profiles, hatched=True ---")
shp_red = {
    'id': 1, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20,
    'rotation': 0, 'penId': 2, 'hatched': True
}
lines1 = b.computeHatchPreviewLines(shp_red)
print("Lines count:", len(lines1))
if lines1:
    print("Unique pen_ids:", set(l.get('pen_id') for l in lines1))

print("\n--- Test 2: Red shape (penId=2) with hatch_profiles pen_no=0 ---")
shp_with_profiles = {
    'id': 2, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20,
    'rotation': 0, 'penId': 2, 'hatched': True,
    'hatch_profiles': {
        '1': {'enable': True, 'pen_no': 0, 'line_space': 0.05, 'angle': 45.0, 'type': 'Bidirectional'},
        '2': {'enable': False, 'pen_no': 0},
        '3': {'enable': False, 'pen_no': 0}
    }
}
lines2 = b.computeHatchPreviewLines(shp_with_profiles)
print("Lines count:", len(lines2))
if lines2:
    print("Unique pen_ids:", set(l.get('pen_id') for l in lines2))

print("\n--- Test 3: Black shape (penId=0) with hatch_profiles pen_no=0 ---")
shp_black = {
    'id': 3, 'type': 'rect', 'xMm': 0, 'yMm': 0, 'wMm': 20, 'hMm': 20,
    'rotation': 0, 'penId': 0, 'hatched': True,
    'hatch_profiles': {
        '1': {'enable': True, 'pen_no': 0, 'line_space': 0.05, 'angle': 45.0, 'type': 'Bidirectional'},
        '2': {'enable': False, 'pen_no': 0},
        '3': {'enable': False, 'pen_no': 0}
    }
}
lines3 = b.computeHatchPreviewLines(shp_black)
print("Lines count:", len(lines3))
if lines3:
    print("Unique pen_ids:", set(l.get('pen_id') for l in lines3))
