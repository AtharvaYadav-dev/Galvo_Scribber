import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtCore import QCoreApplication
app = QCoreApplication.instance() or QCoreApplication(sys.argv)

from bridges.cad_bridge import CadBridge

try:
    b = CadBridge()
    pens = b.getPens()
    print('Initial pens count:', len(pens))
    new_id = b.addPen('Test Custom Pen', '#FF0055')
    print('New pen id:', new_id)
    print('Updated count:', len(b.getPens()))
    b.updatePenColor(new_id, '#00FFAA')
    print('Updated color:', [p['color'] for p in b.getPens() if p['id'] == new_id])
    b.deletePen(new_id)
    print('Count after delete:', len(b.getPens()))
    print('ALL CAD PENS TESTS PASSED!')
except Exception as e:
    import traceback
    traceback.print_exc()
