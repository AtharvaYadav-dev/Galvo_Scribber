import sys
import os
sys.path.append(r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

from PySide6.QtGui import QGuiApplication, QPainterPath, QFont
from bridges.cad_bridge import CadBridge
from core.coordinate_mapper import CoordinateConfig
from core.motion_planner import compute_hatch_geometry

app = QGuiApplication(sys.argv)

cad = CadBridge()
text_shp = {
    "type": "text",
    "text": "123",
    "xMm": 0.0,
    "yMm": 0.0,
    "wMm": 30.0,
    "hMm": 10.0,
    "rotation": 0.0,
    "hatched": True,
    "linePitch": 0.05
}

polys = cad._shape_to_polygons(text_shp)
print(f"Text polygons count: {len(polys)}")
for idx, p in enumerate(polys):
    print(f"  poly {idx}: {len(p)} points, min=({min(x for x,y in p):.2f}, {min(y for x,y in p):.2f}), max=({max(x for x,y in p):.2f}, {max(y for x,y in p):.2f})")

calib_scale, galvo_units_per_mm, lens_size = cad._sync_calibration_and_field_size()
print(f"galvo_units_per_mm: {galvo_units_per_mm}")

all_polys_galvo = []
for p in polys:
    poly_g = [cad.galvo_config.apply_transform(x, y) for (x, y) in p]
    all_polys_galvo.append(poly_g)

hatch_cfg = {
    'enable': True,
    'follow_edge': False,
    'all_calc': False,
    'cross_hatch': False,
    'type': "Bidirectional",
    'angle': 45.0,
    'line_space': 0.05,
    'edge_offset': 0.0,
    'start_offset': 0.0,
    'end_offset': 0.0,
    'line_reduction': 0.0,
    'num_loops': 0,
    'loop_distance': 0.05
}

hatch_lines = compute_hatch_geometry(all_polys_galvo, hatch_cfg, galvo_units_per_mm=galvo_units_per_mm)
print(f"Hatch lines count: {len(hatch_lines)}")
