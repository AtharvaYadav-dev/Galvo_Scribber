import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path: sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge

app = QApplication.instance() or QApplication(sys.argv)
galvo = GalvoBridge()
cad = CadBridge(galvo_bridge=galvo)

shp = {
    "id": 1, "name": "Text_1", "type": "text", "text": "मराठी",
    "xMm": 0.0, "yMm": 0.0, "wMm": 15.0, "hMm": 6.0,
    "fontFamily": "AMS Vasudeva", "rotation": 0, "penId": 0,
    "hatched": True, "visible": True, "locked": False
}

polys = cad._shape_to_polygons(shp)
print(f"Total polygons extracted: {len(polys)}")
if polys:
    all_x = [pt[0] for poly in polys for pt in poly]
    all_y = [pt[1] for poly in polys for pt in poly]
    print(f"Polygon X range: {min(all_x):.2f} .. {max(all_x):.2f} (wMm = {shp['wMm']})")
    print(f"Polygon Y range: {min(all_y):.2f} .. {max(all_y):.2f} (hMm = {shp['hMm']})")
    print(f"Center: X = {(min(all_x)+max(all_x))/2:.2f}, Y = {(min(all_y)+max(all_y))/2:.2f}")

