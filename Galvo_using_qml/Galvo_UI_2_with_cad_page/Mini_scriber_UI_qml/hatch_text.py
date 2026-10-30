import ezdxf
from ezdxf.addons import text2path
from ezdxf.path import nesting, tools
import os
from shapely.geometry import Polygon, LineString

dxf_dir = r"d:\TeamDev\Scribing_V3\Scribing_V3_UI1_with_dxf_changes_for_new_files\dxf_files"
os.makedirs(dxf_dir, exist_ok=True)
out_path = os.path.join(dxf_dir, "SPPL_Date_Hatched.dxf")

doc = ezdxf.new('R2010')
msp = doc.modelspace()

text = "SPPL 12082026"
# Create a dummy TEXT entity to generate paths
dummy = doc.modelspace().add_text(text, dxfattribs={'height': 4})
dummy.set_placement((0,0))
paths = text2path.make_paths_from_entity(dummy)
doc.modelspace().delete_entity(dummy)

# Flatten paths into vertices
polygons = []
for p in paths:
    # flatten to line segments, distance=0.05 controls resolution
    vertices = list(p.flattening(0.05))
    if len(vertices) > 2:
        polygons.append(Polygon(vertices))

# We can union all paths using shapely's unary_union or symmetrical difference to handle holes properly.
# Actually, the Even-Odd rule is often used. 
# An easier way: create a large filled area by intersecting horizontal lines with all polygons.
# Since text polygons might intersect or contain holes, shapely handles Polygon holes via XOR (symmetric_difference).
from shapely.ops import unary_union

# To handle holes properly, we XOR all polygons. 
# Usually, letters are separate outer contours, and holes are inside them.
final_shape = None
for poly in polygons:
    if final_shape is None:
        final_shape = poly
    else:
        final_shape = final_shape.symmetric_difference(poly)

# Now final_shape contains the filled letters with holes correctly cut out.
# Let's create hatching lines.
minx, miny, maxx, maxy = final_shape.bounds
hatch_spacing = 0.2

y = miny
while y <= maxy:
    line = LineString([(minx - 1, y), (maxx + 1, y)])
    intersection = final_shape.intersection(line)
    
    # intersection could be a LineString or MultiLineString
    if intersection.geom_type == 'LineString':
        if not intersection.is_empty:
            coords = list(intersection.coords)
            msp.add_line(coords[0], coords[1])
    elif intersection.geom_type == 'MultiLineString':
        for geom in intersection.geoms:
            if not geom.is_empty:
                coords = list(geom.coords)
                msp.add_line(coords[0], coords[-1])
    
    y += hatch_spacing

# Let's also draw the outline
if final_shape.geom_type == 'Polygon':
    shapes = [final_shape]
elif final_shape.geom_type == 'MultiPolygon':
    shapes = final_shape.geoms
else:
    shapes = []

for poly in shapes:
    # exterior
    ext_coords = list(poly.exterior.coords)
    for i in range(len(ext_coords) - 1):
        msp.add_line(ext_coords[i], ext_coords[i+1])
    # interiors (holes)
    for interior in poly.interiors:
        int_coords = list(interior.coords)
        for i in range(len(int_coords) - 1):
            msp.add_line(int_coords[i], int_coords[i+1])

doc.saveas(out_path)
print(f"Successfully saved hatched DXF to {out_path}")
