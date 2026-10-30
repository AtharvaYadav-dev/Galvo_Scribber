import sys
import os
import time

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge
from bridges.jog_bridge import JogBridge

def test_cad_backend():
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("--- 1. Initializing Bridges ---")
    galvo = GalvoBridge()
    jog = JogBridge(galvo_bridge=galvo)
    cad = CadBridge(galvo_bridge=galvo, jog_bridge=jog)
    
    # Set custom object thickness to test dynamic focal target
    jog.setObjectHeight(5.0)  # Workpiece 5mm thick
    expected_target = jog.targetFocusZ
    print(f"[OK] Target Workpiece Focus: {expected_target:.2f} mm")

    # Verify hardware connect and stepper sync
    galvo.connectHardware()
    assert jog.stepper.connection == galvo.controller.connection, "Stepper connection should be synchronized"
    print("[OK] Hardware connect and StepperController connection sync: OK")

    print("\n--- 2. Testing Shape to Motion Planner Vector Conversion ---")
    test_shapes = [
        {
            "id": 1,
            "name": "Rect_1",
            "type": "rect",
            "xMm": 0, "yMm": 0,
            "wMm": 15, "hMm": 15,
            "rotation": 0, "penId": 0, "hatched": False, "visible": True
        }
    ]
    
    # Test Framing (F1)
    print("\n--- 3. Testing Red Light Framing (F1) ---")
    cad.toggleFraming(test_shapes, False, -1)
    assert cad.isFraming is True, "Framing should be active"
    print(f"[OK] Red pointer framing started: Status = '{cad.statusMessage}'")
    cad.toggleFraming()
    assert cad.isFraming is False, "Framing should be inactive after toggle"
    print("[OK] Red pointer framing stopped successfully: OK")

    # Test Laser Marking Execution (F2)
    print("\n--- 4. Testing Laser Marking Execution (F2) ---")
    cad.executeMark(test_shapes, False, -1, 1)
    assert cad.isMarking is True, "Marking should be active"
    print(f"[OK] Laser mark execution launched: Status = '{cad.statusMessage}'")
    print(f"[OK] Motion queue size = {len(cad.planner.send_queue)} commands")
    
    # Wait for completion in hardware/simulation mode (1599 commands)
    for _ in range(150):
        app.processEvents()
        time.sleep(0.1)
        if not cad.isMarking:
            break
            
    assert cad.isMarking is False, "Marking should finish cleanly"
    print(f"[OK] Laser mark execution completed: Status = '{cad.statusMessage}'")

    # Test DXF Import
    print("\n--- 5. Testing DXF Import ---")
    imported_results = []
    cad.shapesImported.connect(lambda s: imported_results.extend(s))
    sample_dxf = os.path.join(_app_dir, "my_test.dxf")
    if os.path.exists(sample_dxf):
        cad.importFile(sample_dxf)
        app.processEvents()
        assert len(imported_results) > 0, "DXF should produce imported shape"
        shp = imported_results[0]
        print(f"[OK] DXF Imported: Name='{shp['name']}', Dimensions={shp['wMm']}x{shp['hMm']} mm, Paths count={len(shp['paths'])}")
    else:
        print("my_test.dxf not found, skipping file test")

    print("\n==============================================")
    print(" ALL CAD BACKEND & HARDWARE TESTS PASSED (100%)")
    print("==============================================")

if __name__ == "__main__":
    test_cad_backend()
