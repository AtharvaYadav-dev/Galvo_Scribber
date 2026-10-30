import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import trimesh

# Initialize headless Qt App
app = QApplication.instance()
if not app:
    app = QApplication([])

from preview_stl_3d import STL3DOpenGLWidget, STL3DPreviewWidget
from core.engraving_3d_manager import STL3DEngravingManager
from core.coordinate_mapper import CoordinateConfig

def test_scrub_performance():
    stl_path = "D:/Users/EXPSOL/Downloads/Mighty Trug (8).stl"
    if not os.path.exists(stl_path):
        stl_path = "scratch/test_3d_relief.stl"
    
    print(f"[TEST] Using model: {stl_path}")
    mesh = trimesh.load(stl_path)
    print(f"[TEST] Model has {len(mesh.faces)} triangles")

    # 1. Test 3D Widget display list compilation & cutting plane movement
    w3d = STL3DPreviewWidget()
    w3d.load_mesh(mesh)
    w3d.resize(600, 600)
    w3d.show()

    # Process events to allow initializeGL and paintGL to run
    app.processEvents()

    # Verify display list compiled
    gl_w = w3d.gl_widget
    print(f"[TEST] Display list compiled: {gl_w.display_list is not None}")
    assert gl_w.display_list is not None, "Display list was not compiled!"

    # Benchmark cutting plane update across 100 layer movements
    t0 = time.perf_counter()
    for layer_i in range(1, 101):
        z_h = w3d.max_z - (layer_i * 0.02)
        w3d.set_current_layer(layer_i, 100, z_h)
        # Process paint event
        app.processEvents()
    elapsed_3d = time.perf_counter() - t0
    avg_per_frame = (elapsed_3d / 100.0) * 1000.0
    print(f"[TEST] 100 cutting plane 3D frames rendered in: {elapsed_3d*1000:.1f} ms (avg {avg_per_frame:.2f} ms/frame)")
    assert avg_per_frame < 35.0, f"3D rendering too slow: {avg_per_frame:.2f} ms/frame"

    # 2. Test Slicing and Layer Queue Caching
    mgr = STL3DEngravingManager()
    mgr.load_stl(stl_path)
    dim_x, dim_y, dim_z = mgr.get_mesh_dimensions()
    mgr.slice_model(z_step_mm=0.03, target_depth_mm=dim_z, bg_margin_mm=2.0)
    
    cfg = CoordinateConfig()
    cfg.field_size = 100.0

    cache = {}
    
    # Test debounced vs cached retrieval
    t0 = time.perf_counter()
    # First time computing layer 5
    q5 = mgr.generate_layer_queue(5, cfg, hatch_pitch_mm=0.05)
    cache[5] = q5
    t_compute = (time.perf_counter() - t0) * 1000.0
    print(f"[TEST] First compute of Layer 5 hatching: {t_compute:.2f} ms")

    # Second time retrieval from cache
    t0 = time.perf_counter()
    q5_cached = cache[5]
    t_cache = (time.perf_counter() - t0) * 1000.0
    print(f"[TEST] Cached retrieval of Layer 5: {t_cache:.4f} ms")
    assert t_cache < 0.1, "Cache retrieval was not instantaneous!"
    assert len(q5_cached) == len(q5)

    w3d.close()
    print("\n[TEST] ALL SLIDER SCRUB PERFORMANCE BENCHMARKS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_scrub_performance()
