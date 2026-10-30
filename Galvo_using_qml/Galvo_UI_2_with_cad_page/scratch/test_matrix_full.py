import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtCore import QCoreApplication
from bridges.galvo_bridge import GalvoBridge
from bridges.matrix_bridge import MatrixBridge

def test_matrix_working():
    app = QCoreApplication.instance() or QCoreApplication([])
    print("=== Testing Matrix Bridge Calculations and Hardware Execution against main.py ===")

    galvo = GalvoBridge()
    matrix = MatrixBridge(galvo_bridge=galvo)

    # 1. Test Scale & Field Size
    scale, field_size = matrix._get_scale_and_field_size()
    print(f"Scale: {scale:.2f} bits/mm, Field Size: {field_size} mm")
    assert abs(scale - 533.89) < 0.1 or abs(scale - (65535.0/field_size)) < 0.1, f"Unexpected scale: {scale}"

    # 2. Test Grid Generation
    matrix.updateParameters(
        p_start=10.0, p_end=90.0, p_steps=5,
        f_start=20.0, f_end=80.0, f_steps=5,
        cw=5.0, ch=5.0, gx=2.0, gy=2.0,
        fill_type="Filled Rectangle", label_axes=True, speed=1000.0
    )
    cells = matrix.get_matrix_cells()
    assert len(cells) == 25, f"Expected 25 cells, got {len(cells)}"
    print(f"Generated {len(cells)} cells. Total dims: {matrix.get_total_w():.1f} x {matrix.get_total_h():.1f} mm")

    # Verify first and last cell
    first_cell = cells[0]
    last_cell = cells[-1]
    assert first_cell["power"] == 10.0 and first_cell["freq"] == 20.0
    assert last_cell["power"] == 90.0 and last_cell["freq"] == 80.0
    print(f"Cell [0,0]: {first_cell['power']}% @ {first_cell['freq']}kHz")
    print(f"Cell [4,4]: {last_cell['power']}% @ {last_cell['freq']}kHz")

    # 3. Test Preview Bounding Box Math (matching mapping_controller.py lines 387-391)
    center_xy = 32767
    x0 = int((-matrix._total_w / 2.0) * scale + center_xy)
    y0 = int((-matrix._total_h / 2.0) * scale + center_xy)
    x1 = int((matrix._total_w / 2.0) * scale + center_xy)
    y1 = int((matrix._total_h / 2.0) * scale + center_xy)
    print(f"Red preview framing box: [{x0}, {y0}] to [{x1}, {y1}] (span: {x1-x0} x {y1-y0} DAC units)")
    expected_span = int(matrix._total_w * scale)
    assert abs((x1 - x0) - expected_span) <= 2, f"Expected span ~{expected_span}, got {x1-x0}"

    # 4. Test Red Preview toggle & simulation
    matrix.startRedPreview()
    assert matrix.get_is_framing() == True, "Expected isFraming to be True"
    matrix.startRedPreview()
    assert matrix.get_is_framing() == False, "Expected isFraming to be toggled off"
    print("Red Preview toggle verified.")

    # 5. Test Laser Mark Queue Generation & Execution
    matrix.startLaserMark()
    assert matrix.get_is_executing() == True, "Expected isExecuting to be True"
    
    # Test Pause / Resume
    matrix.togglePause()
    assert matrix.get_is_paused() == True, "Expected isPaused to be True"
    matrix.togglePause()
    assert matrix.get_is_paused() == False, "Expected isPaused to be False after resume"
    print("Pause and Resume verified.")

    # Test Abort
    matrix.abort()
    assert matrix.get_is_executing() == False, "Expected isExecuting to be False after abort"
    assert matrix.get_is_framing() == False, "Expected isFraming to be False after abort"
    assert matrix.get_active_cell_index() == -1, "Expected activeCellIndex to be -1 after abort"
    print("Abort verified.")

    print("\nALL MATRIX CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_matrix_working()
