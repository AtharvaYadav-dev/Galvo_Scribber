import sys
sys.path.append(r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
from PySide6.QtGui import QGuiApplication
app = QGuiApplication(sys.argv)
from bridges.cad_bridge import CadBridge
from core.motion_planner import compute_hatch_geometry
cad = CadBridge()
text_shp = {'type': 'text', 'text': '1', 'xMm': 0.0, 'yMm': 0.0, 'wMm': 10.0, 'hMm': 10.0, 'rotation': 0.0}
polys = cad._shape_to_polygons(text_shp)
calib_scale, galvo_units_per_mm, lens_size = cad._sync_calibration_and_field_size()
all_polys_galvo = [[cad.galvo_config.apply_transform(x, y) for (x, y) in p] for p in polys]
hatch_cfg = {'enable': True, 'follow_edge': False, 'all_calc': False, 'cross_hatch': False, 'type': 'Bidirectional', 'angle': 45.0, 'line_space': 0.05}
lines = compute_hatch_geometry(all_polys_galvo, hatch_cfg, galvo_units_per_mm=galvo_units_per_mm)
print(f'Digit 1 hatch lines: {len(lines)}')
for l in lines[:5]:
    print('  ', l)
