import sys
import time

sys.path.append("d:/Atharva/Galvo_Scribber/Galvo_22092026")
from core.image_parser import ImageParser

# Let's create a dummy image to test with, or just use any image if it exists
import numpy as np
from PIL import Image

print("Generating 1000x1000 dummy image...")
img_data = np.random.randint(0, 256, (1000, 1000), dtype=np.uint8)
img = Image.fromarray(img_data, 'L')
img.save("dummy_test.png")

print("Parsing image...")
parser = ImageParser(field_size=100)
t0 = time.time()
polygons = parser.parse_to_polygons("dummy_test.png", pixel_size_mm=0.1)
t1 = time.time()

print(f"parse_to_polygons took: {t1-t0:.4f}s")
print(f"Generated {len(polygons)} segments.")

# Now simulate main.py processing
t2 = time.time()
all_polys_galvo = []
seen_polys = set()
for poly in polygons:
    if not poly: continue
    poly_galvo = []
    for pt in poly:
        poly_galvo.append((pt[0]*1000, pt[1]*1000)) # dummy transform
        
    poly_key = tuple((int(round(pt[0])), int(round(pt[1]))) for pt in poly_galvo)
    poly_key_rev = tuple(reversed(poly_key))
    if poly_key not in seen_polys and poly_key_rev not in seen_polys:
        seen_polys.add(poly_key)
        all_polys_galvo.append(poly_galvo)
        
t3 = time.time()
print(f"Main.py polygon transform and deduplication took: {t3-t2:.4f}s")

# Simulate planner
t4 = time.time()
from core.motion_planner import MotionPlanner
planner = MotionPlanner()
for poly_galvo in all_polys_galvo:
    planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=1000)
    for pt in poly_galvo[1:]:
        planner.add_mark(pt[0], pt[1], speed=1000)
        
t5 = time.time()
print(f"Planner add_jump/add_mark took: {t5-t4:.4f}s")

planner.optimize_path()
t6 = time.time()
print(f"Planner optimize_path took: {t6-t5:.4f}s")

try:
    import os
    dump_path = "galvo_output_dummy.txt"
    with open(dump_path, "w") as f:
        f.write("; Galvo Command Execution Queue\n")
        f.write(f"; Total Commands: {len(planner.send_queue)}\n")
        f.write(f"; Field Size: 100mm\n\n")
        for cmd in planner.send_queue:
            ctype = cmd.get('type')
            if ctype == 'jump':
                f.write(f"JUMP X:{cmd.get('x')} Y:{cmd.get('y')} SPEED:{cmd.get('speed')}\n")
            elif ctype == 'mark':
                f.write(f"MARK X:{cmd.get('x')} Y:{cmd.get('y')} SPEED:{cmd.get('speed')}\n")
except Exception as e:
    print("Dump error", e)

t7 = time.time()
print(f"Planner dump to txt took: {t7-t6:.4f}s")
