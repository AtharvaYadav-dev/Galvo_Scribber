import os
from core.svg_parser import SVGParser
from scratch.test_split_logic import clip_polygon_to_rect

svg_path = os.path.join("svg_files", "250 122mmsizeMicron channel.svg")
parser = SVGParser(field_size=100)
polygons = parser.parse_to_polygons(svg_path)
print(f"Loaded {len(polygons)} polygons from {svg_path}")

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
print(f"SVG Dimensions: {w:.2f} x {h:.2f} mm (Bounds: X[{min_x:.2f}, {max_x:.2f}], Y[{min_y:.2f}, {max_y:.2f}])")

# Split into 2x1 (2 columns, 1 row)
cols, rows = 2, 1
tile_w = w / cols
tile_h = h / rows
print(f"Split into {cols}x{rows}: Each tile is {tile_w:.2f} x {tile_h:.2f} mm")

for c in range(cols):
    t_xmin = min_x + c * tile_w
    t_xmax = min_x + (c + 1) * tile_w
    t_ymin = min_y
    t_ymax = max_y
    
    tile_polys = []
    for poly in polygons:
        clipped = clip_polygon_to_rect(poly, t_xmin, t_xmax, t_ymin, t_ymax)
        tile_polys.extend(clipped)
    print(f"  Tile Part {c+1}: {len(tile_polys)} paths (X: {t_xmin:.1f} to {t_xmax:.1f})")
