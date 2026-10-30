import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge
from bridges.settings_bridge import SettingsBridge

def test_main_math_replication():
    print("=== Testing main.py math integration in new UI bridges ===")
    
    galvo = GalvoBridge()
    cad = CadBridge(galvo_bridge=galvo)
    settings = SettingsBridge(cad_bridge=cad)
    
    # 1. Verify calibration scale detection and lens size override (from main.py lines 2325-2335 & 2470-2485)
    calib_scale, units_per_mm, lens_size = cad._sync_calibration_and_field_size()
    print(f"Calibration scale: {calib_scale}")
    print(f"Galvo units per mm: {units_per_mm}")
    print(f"Lens field size (main.py math): {lens_size:.2f} mm")
    print(f"galvo_config.field_size: {cad.galvo_config.field_size:.2f} mm")
    
    # Verify configured 70mm lens field size is preserved while optical scale is 533.89
    assert abs(units_per_mm - 533.89) < 0.1, f"Expected units_per_mm ~533.89, got {units_per_mm}"
    assert abs(lens_size - 70.0) < 0.1, f"Expected lens_size 70.0mm, got {lens_size}"
    assert abs(cad.galvo_config.field_size - 70.0) < 0.1, f"Expected galvo_config field_size 70.0, got {cad.galvo_config.field_size}"
    
    # 2. Verify 36.00 mm and 37.00 mm DAC deflection match main.py
    # 36mm * 533.89 = 19220 bits
    g1_top, g2_top = cad.galvo_config.apply_transform(0.0, 18.0)
    g1_bot, g2_bot = cad.galvo_config.apply_transform(0.0, -18.0)
    delta_bits_y = g2_top - g2_bot
    print(f"36.00mm delta DAC bits: {delta_bits_y} (expected ~19219 bits)")
    assert abs(delta_bits_y - 19219) <= 2, f"Expected ~19219 DAC bits for 36mm, got {delta_bits_y}"
    
    # 3. Test laser power & frequency function
    galvo.setPower(45.0)
    galvo.setFrequency(30.0)
    assert galvo.controller.live_power == 45.0, f"Expected live_power 45.0, got {galvo.controller.live_power}"
    assert galvo.controller.live_freq == 30.0, f"Expected live_freq 30.0, got {galvo.controller.live_freq}"
    print(f"Laser power ({galvo.controller.live_power}%) & freq ({galvo.controller.live_freq}kHz) successfully set on controller.")
    
    print("ALL TESTS PASSED! main.py math and functions fully replicated.")

if __name__ == "__main__":
    test_main_math_replication()
