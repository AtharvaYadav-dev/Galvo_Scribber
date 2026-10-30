import json, sys
sys.path.insert(0, '.')
from core.svg_parser import SVGParser
from core.coordinate_mapper import CoordinateConfig
from core.motion_planner import MotionPlanner

with open('svg_files/38mmsize 250Micron channel.svg.json') as f:
    params = json.load(f)['Galvo program page parameters']

cfg = CoordinateConfig()
cfg.field_size = 122.75000468261253

parser = SVGParser(field_size=cfg.field_size)
polygons = parser.parse_to_polygons('svg_files/38mmsize 250Micron channel.svg')

min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')
for poly in polygons:
    for pt in poly:
        min_x = min(min_x, pt[0])
        max_x = max(max_x, pt[0])
        min_y = min(min_y, pt[1])
        max_y = max(max_y, pt[1])

w = max_x - min_x
h = max_y - min_y
print(f'Dimensions: {w:.3f} mm x {h:.3f} mm (Expected: 37.933 mm x 37.933 mm)')

design_center_x = min_x + w / 2.0
design_center_y = min_y + h / 2.0
shift_x = 0.0 - design_center_x
shift_y = 0.0 - design_center_y

galvo_units_per_mm = 65535.0 / cfg.field_size
raw_jump = float(params['Jump Speed'])
raw_mark = float(params['Mark Speed'])
jump_speed = int(raw_jump * galvo_units_per_mm)
mark_speed = int(raw_mark * galvo_units_per_mm)

print(f'Speeds: Raw Mark={raw_mark} mm/s -> Hardware={mark_speed} counts/s | Raw Jump={raw_jump} mm/s -> Hardware={jump_speed} counts/s')

planner = MotionPlanner()
all_polys_galvo = []
seen_polys = set()

for poly in polygons:
    if not poly: continue
    poly_galvo = []
    for pt in poly:
        gx, gy = cfg.apply_transform(pt[0] + shift_x, pt[1] + shift_y)
        poly_galvo.append((gx, gy))
    poly_key = tuple((int(round(pt[0])), int(round(pt[1]))) for pt in poly_galvo)
    poly_key_rev = tuple(reversed(poly_key))
    if poly_key not in seen_polys and poly_key_rev not in seen_polys:
        seen_polys.add(poly_key)
        all_polys_galvo.append(poly_galvo)

for poly_galvo in all_polys_galvo:
    planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
    for pt in poly_galvo[1:]:
        planner.add_mark(pt[0], pt[1], speed=mark_speed)

planner.optimize_path()
planner.commit_to_send_queue()

print(f"Total Commands Generated: {len(planner.send_queue)} (Marks: {sum(1 for c in planner.send_queue if c['type'] == 'mark')}, Jumps: {sum(1 for c in planner.send_queue if c['type'] == 'jump')})")

with open('CopytoAnalysePreviousParameters/Galvo_UI_2/config/galvo_output.txt') as f:
    ref_lines = [l.strip() for l in f if l.strip() and not l.startswith(';')]

curr_lines = []
for cmd in planner.send_queue:
    ctype = cmd['type'].upper()
    curr_lines.append(f"{ctype} X:{cmd['x']} Y:{cmd['y']} SPEED:{cmd['speed']}")

print(f'Matches reference galvo_output.txt exactly: {ref_lines == curr_lines}')
if ref_lines != curr_lines:
    print('First 5 REF :', ref_lines[:5])
    print('First 5 CURR:', curr_lines[:5])
