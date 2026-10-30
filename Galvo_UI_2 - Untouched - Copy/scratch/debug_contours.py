import sys
import os
from shapely.geometry import Polygon, MultiPolygon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.engraving_3d_manager import STL3DEngravingManager
from core.coordinate_mapper import CoordinateConfig

def inspect_stl(path):
    print(f"=== Inspecting {path} ===")
    mgr = STL3DEngravingManager()
    ok = mgr.load_stl(path)
    if not ok:
        print("Failed to load")
        return
    dx, dy, dz = mgr.get_mesh_dimensions()
    print(f"Dimensions: X={dx:.2f}, Y={dy:.2f}, Z={dz:.2f}")

    layers = mgr.slice_model(z_step_mm=0.03, target_depth_mm=dz, bg_margin_mm=2.0, carve_mode=STL3DEngravingManager.MODE_RELIEF)
    print(f"Total layers: {len(layers)}")
    
    # Check layer 0, layer len//2, layer -1
    check_indices = [0, len(layers)//4, len(layers)//2, 3*len(layers)//4, len(layers)-1]
    for idx in check_indices:
        polys = mgr.get_layer_polygons(idx)
        print(f"\n--- Layer {idx} has {len(polys)} polygon rings ---")
        for p_i, poly in enumerate(polys):
            is_closed = (poly[0] == poly[-1])
            print(f"  Ring {p_i}: {len(poly)} points, closed={is_closed}, start={poly[0]}, end={poly[-1]}")
            # Check for any self-intersections, zero-length jumps, or abnormal features
            if len(poly) >= 3:
                p_obj = Polygon(poly)
                print(f"    valid={p_obj.is_valid}, area={p_obj.area:.2f}, bounds={p_obj.bounds}")

    # Now let's check generate_layer_queue
    cfg = CoordinateConfig()
    cfg.field_size = 100.0
    q = mgr.generate_layer_queue(
        layer_idx=len(layers)//2,
        galvo_config=cfg,
        hatch_pitch_mm=0.035,
        cross_layer_rotate=True,
        mark_speed=1000,
        jump_speed=2000,
        start_x_mm=0.0,
        start_y_mm=0.0,
        mark_contour=True
    )
    print(f"\nQueue for layer {len(layers)//2}: total commands={len(q)}")
    # Count jumps and marks in the queue before and after hatch
    contour_jumps = 0
    contour_marks = 0
    in_hatch = False
    for cmd in q:
        if cmd.get('type') == 'pass_change':
            in_hatch = True
        if not in_hatch:
            if cmd.get('type') == 'jump':
                contour_jumps += 1
            elif cmd.get('type') == 'mark':
                contour_marks += 1
    print(f"Contour jumps: {contour_jumps}, marks: {contour_marks}")

if __name__ == "__main__":
    inspect_stl("D:/Users/EXPSOL/Downloads/Mighty Trug (3).stl")
