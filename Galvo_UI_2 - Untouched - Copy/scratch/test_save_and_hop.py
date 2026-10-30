import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engraving_3d_manager import STL3DEngravingManager
from core.coordinate_mapper import CoordinateConfig
from util import FileHandler

def test_3d_save_and_hop():
    mgr = STL3DEngravingManager()
    fh = FileHandler()
    
    # Test 1: Cool Sango.stl
    sango_path = "D:/Users/EXPSOL/Downloads/Cool Sango.stl"
    if os.path.exists(sango_path):
        print(f"\n--- Testing {sango_path} ---")
        ok = mgr.load_stl(sango_path)
        assert ok, "Failed to load Cool Sango.stl"
        dim_x, dim_y, dim_z = mgr.get_mesh_dimensions()
        print(f"Loaded bounds: X={dim_x:.2f}, Y={dim_y:.2f}, Z={dim_z:.2f}")
        
        # Slicing test (ensure no rtree or multiplane errors)
        layers = mgr.slice_model(z_step_mm=0.03, target_depth_mm=dim_z, bg_margin_mm=2.0, carve_mode=STL3DEngravingManager.MODE_RELIEF)
        print(f"Sliced layers count: {len(layers)}")
        assert len(layers) > 0, "No layers generated!"
        
        # Test toolpath generation
        cfg = CoordinateConfig()
        cfg.field_size = 100.0
        q = mgr.generate_layer_queue(
            layer_idx=0,
            galvo_config=cfg,
            hatch_pitch_mm=0.05,
            cross_layer_rotate=True,
            mark_speed=1500,
            jump_speed=2000,
            start_x_mm=0.0,
            start_y_mm=0.0,
            mark_contour=True
        )
        print(f"Layer 0 queue items: {len(q)}")
        assert len(q) > 0, "Layer queue is empty!"

    # Test 2: round+plaster+ornament.STL (The large / rotated model)
    ornament_path = "D:/Users/EXPSOL/Downloads/round+plaster+ornament.STL"
    if os.path.exists(ornament_path):
        print(f"\n--- Testing {ornament_path} ---")
        ok = mgr.load_stl(ornament_path)
        assert ok, "Failed to load round+plaster+ornament.STL"
        dim_x, dim_y, dim_z = mgr.get_mesh_dimensions()
        print(f"Original extents: X={dim_x:.2f}, Y={dim_y:.2f}, Z={dim_z:.2f}")
        
        # Test 90-deg rotation to lay face flat
        dim_x, dim_y, dim_z = mgr.rotate_mesh_90('X')
        print(f"After Rotate 90 deg: X={dim_x:.2f}, Y={dim_y:.2f}, Z={dim_z:.2f}")
        
        # Test Auto-Fit to 100mm lens
        factor = mgr.auto_fit_to_lens(lens_size_mm=100.0, bg_margin_mm=2.0)
        dim_x, dim_y, dim_z = mgr.get_mesh_dimensions()
        print(f"After Auto-Fit (scale factor {factor:.3f}): X={dim_x:.2f}, Y={dim_y:.2f}, Z={dim_z:.2f}")
        assert dim_x + 4.0 <= 100.0, f"X exceeds lens: {dim_x + 4.0}"
        assert dim_y + 4.0 <= 100.0, f"Y exceeds lens: {dim_y + 4.0}"
        
        # Test Slicing after auto-fit
        layers = mgr.slice_model(z_step_mm=0.03, target_depth_mm=dim_z, bg_margin_mm=2.0, carve_mode=STL3DEngravingManager.MODE_RELIEF)
        print(f"Ornament sliced layers: {len(layers)}")
        assert len(layers) > 0

    print("\nALL 3D SAVE AND HOP TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_3d_save_and_hop()
