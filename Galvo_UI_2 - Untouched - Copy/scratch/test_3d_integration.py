import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engraving_3d_manager import STL3DEngravingManager
from core.coordinate_mapper import CoordinateConfig

def test_3d_pipeline():
    mgr = STL3DEngravingManager()
    stl_path = "test_3d_relief.stl"
    assert os.path.exists(stl_path), "Test STL not found"
    
    ok = mgr.load_stl(stl_path)
    assert ok, "Failed to load test STL"
    dim_x, dim_y, dim_z = mgr.get_mesh_dimensions()
    print(f"[TEST] Loaded STL bounds: X={dim_x:.2f}mm, Y={dim_y:.2f}mm, Z={dim_z:.2f}mm")
    assert dim_x > 0 and dim_y > 0 and dim_z > 0

    # Test Material Preset Loading
    presets = list(mgr.presets.keys())
    print(f"[TEST] Available Presets: {len(presets)} -> {presets}")
    assert "Aluminium (6061 / 7075)" in presets
    assert "Stainless Steel / Steel" in presets
    assert "Brass / Copper" in presets

    # Test Resolution calculation for Aluminium
    fine_params = mgr.get_preset_params("Aluminium (6061 / 7075)", STL3DEngravingManager.RES_FINE)
    std_params = mgr.get_preset_params("Aluminium (6061 / 7075)", STL3DEngravingManager.RES_STANDARD)
    fast_params = mgr.get_preset_params("Aluminium (6061 / 7075)", STL3DEngravingManager.RES_FAST)

    passes_fine = mgr.calculate_passes(dim_z, fine_params['z_step'])
    passes_std = mgr.calculate_passes(dim_z, std_params['z_step'])
    passes_fast = mgr.calculate_passes(dim_z, fast_params['z_step'])

    print(f"[TEST] Passes - Fine: {passes_fine} (step {fine_params['z_step']}mm), Std: {passes_std} (step {std_params['z_step']}mm), Fast: {passes_fast} (step {fast_params['z_step']}mm)")
    assert passes_fine > passes_std > passes_fast

    # Test Slicing Relief (Negative background ablation)
    layers = mgr.slice_model(z_step_mm=std_params['z_step'], bg_margin_mm=std_params['bg_margin'], carve_mode=STL3DEngravingManager.MODE_RELIEF)
    print(f"[TEST] Sliced {len(layers)} relief layers successfully.")
    assert len(layers) == passes_std

    # Test Layer Queue generation with rotating angle
    coord_cfg = CoordinateConfig()
    q0 = mgr.generate_layer_queue(0, coord_cfg, hatch_pitch_mm=std_params['hatch_pitch'], cross_layer_rotate=True)
    q1 = mgr.generate_layer_queue(1, coord_cfg, hatch_pitch_mm=std_params['hatch_pitch'], cross_layer_rotate=True)
    print(f"[TEST] Layer 0 commands: {len(q0)}, Layer 1 commands: {len(q1)}")
    assert len(q0) > 0 and len(q1) > 0

    print("[TEST] ALL 3D ENGRAVING INTEGRATION TESTS PASSED!")

if __name__ == "__main__":
    test_3d_pipeline()
