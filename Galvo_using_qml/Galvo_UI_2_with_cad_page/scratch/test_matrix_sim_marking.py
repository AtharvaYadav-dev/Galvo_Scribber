import sys
import os
import time

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtCore import QCoreApplication
from bridges.galvo_bridge import GalvoBridge
from bridges.matrix_bridge import MatrixBridge

def test_sim_marking():
    app = QCoreApplication.instance() or QCoreApplication([])
    galvo = GalvoBridge()
    matrix = MatrixBridge(galvo_bridge=galvo)

    visited_cells = []
    def on_cell_changed(idx):
        visited_cells.append(idx)
        print(f"Active cell signal: {idx}")

    matrix.activeCellIndexChanged.connect(on_cell_changed)
    print("Starting simulated mark...")
    matrix.startLaserMark()

    # Wait for simulation to run through 25 cells
    start_t = time.time()
    while matrix.get_is_executing() and (time.time() - start_t) < 5.0:
        app.processEvents()
        time.sleep(0.05)

    app.processEvents()
    time.sleep(0.05)
    app.processEvents()
    print(f"Execution finished. Total cells visited: {len(visited_cells)}")
    assert len(visited_cells) >= 25, f"Expected at least 25 cell transitions, got {len(visited_cells)}"
    assert visited_cells[-1] == -1, "Expected final activeCellIndex to be -1"
    print("ALL SIMULATED MARKING CHECKS PASSED!")

if __name__ == "__main__":
    test_sim_marking()
