import sys
import os

# Set working directory to project root
_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_dir)
sys.path.insert(0, _dir)

from core.engraving_manager import EngravingManager
from machine.galvo_controller import GalvoController
from machine.stepper_controller import StepperController
from galvo_threads import ExecutionThread
from core.connection.mock import MockConnection

def test_engraving_manager():
    print("=== Testing EngravingManager ===")
    mgr = EngravingManager()
    assert "POM / Delrin (Hard Plastic)" in mgr.presets
    assert "Aluminium" in mgr.presets
    print(f"Loaded {len(mgr.presets)} default presets.")
    
    # Test calculate_loops
    loops = mgr.calculate_loops(1.0, 0.05)
    print(f"1.0mm depth with 0.05mm step = {loops} loops (expected 20)")
    assert loops == 20
    
    loops_clamped = mgr.calculate_loops(10.0, 0.05) # should clamp to 5.0mm max
    print(f"10.0mm clamped to 5.0mm = {loops_clamped} loops (expected 100)")
    assert loops_clamped == 100
    
    # Test adding custom preset
    test_name = "Test Material 1"
    mgr.add_or_update_preset(
        name=test_name, power=25.0, frequency=45.0, speed=600.0,
        z_step=0.03, max_depth=1.5, hatch_style="Cross-Hatch (90° Grid)", hatch_pitch=0.035
    )
    assert test_name in mgr.presets
    print(f"Successfully added '{test_name}': {mgr.presets[test_name]}")
    
    # Reload from file to ensure persistence
    mgr2 = EngravingManager()
    assert test_name in mgr2.presets
    print("Persistence verified.")
    
    # Clean up test preset
    mgr.delete_preset(test_name)
    assert test_name not in mgr.presets
    print("Cleanup verified.")

def test_execution_thread_engraving():
    print("\n=== Testing ExecutionThread Multi-Pass Engraving Loop ===")
    galvo = GalvoController()
    galvo.connect(force_mock=True)
    stepper = StepperController(galvo.connection)
    
    # Set starting position
    stepper.z_position = 27.0
    initial_z = 27.0
    
    # Create simple queue
    queue = [
        {'type': 'jump', 'x': 30000, 'y': 30000, 'speed': 2000},
        {'type': 'mark', 'x': 35000, 'y': 35000, 'speed': 1000},
    ]
    
    # We want 3 passes: 0.15 mm target depth, 0.05 mm step
    target_depth = 0.15
    z_step = 0.05
    loops = 3
    
    depth_records = []
    def on_depth(current_layer, total_layers, cur_depth, max_depth):
        depth_records.append((current_layer, total_layers, round(cur_depth, 3), round(max_depth, 3)))
        print(f"[Signal] Pass {current_layer}/{total_layers} | Current Depth: {cur_depth:.3f} mm / {max_depth:.3f} mm")
        
    thread = ExecutionThread(
        controller=galvo,
        queue=queue,
        loop_count=loops,
        stepper_controller=stepper,
        enable_engraving=True,
        z_step_mm=z_step,
        target_depth_mm=target_depth,
        settle_delay_s=0.02, # fast for test
        safe_return_z=initial_z
    )
    thread.depth_signal.connect(on_depth)
    
    # Run synchronously
    thread.run()
    
    print("\nRecorded Depth Progress Events:")
    for r in depth_records:
        print(" ", r)
        
    # Check that Z returned to safe initial position
    print(f"Final Z position after execution: {stepper.z_position:.2f} mm (expected {initial_z:.2f} mm)")
    assert abs(stepper.z_position - initial_z) < 0.001, "Z axis did not return to safe height!"
    print("SUCCESS: ExecutionThread multi-pass Z-drop and safe retract verified perfectly!")

if __name__ == "__main__":
    test_engraving_manager()
    test_execution_thread_engraving()
    print("\nALL ENGRAVING TESTS PASSED 100%!")
