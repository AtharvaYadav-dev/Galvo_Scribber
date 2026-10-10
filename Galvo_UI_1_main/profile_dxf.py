import sys
import time

sys.path.append("d:/Atharva/Galvo_Scribber/Galvo_22092026")
from dxf import DXFParser

file = "d:/Atharva/Galvo_Scribber/Galvo_22092026/wafer_grid_30mm_250um.dxf"
print("Loading DXF...")
t0 = time.time()
parser = DXFParser(file)
t1 = time.time()
print(f"Init (readfile): {t1-t0:.2f}s")

polygons = parser.parse_to_polygons(field_size=110)
t2 = time.time()
print(f"parse_to_polygons: {t2-t1:.2f}s")
print(f"Total polygons: {len(polygons)}")
