import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dxf import DXFParser
from core.svg_parser import SVGParser
from gerber_parser import GerberParser
from core.image_parser import ImageParser

print("Testing DXFParser...")
try:
    dxf_file = os.path.abspath("dxf_files/2x2.dxf")
    p_dxf = DXFParser(dxf_file)
    polys_dxf = p_dxf.parse_to_polygons(field_size=110)
    print(f"DXF parsed: {len(polys_dxf)} polylines. First poly pt count: {len(polys_dxf[0]) if polys_dxf else 0}")
except Exception as e:
    print(f"DXF error: {e}")

print("\nTesting GerberParser...")
try:
    gbr_file = os.path.abspath("Gerber_files/concentric_circles-F_Cu.gbr")
    p_gbr = GerberParser(gbr_file)
    polys_gbr = p_gbr.parse_to_polygons(field_size=110)
    print(f"Gerber parsed: {len(polys_gbr)} polylines. First poly pt count: {len(polys_gbr[0]) if polys_gbr else 0}")
except Exception as e:
    print(f"Gerber error: {e}")

print("\nTesting GerberParser with folder...")
try:
    gbr_dir = os.path.abspath("Gerber_files/Arduino Nano IO Shield Gerber")
    for f in os.listdir(gbr_dir):
        if f.lower().endswith(('.gbr', '.gtl', '.gbl', '.gto', '.gbo', '.gts', '.gbs', '.drl')):
            target = os.path.join(gbr_dir, f)
            p = GerberParser(target)
            res = p.parse_to_polygons(field_size=110)
            print(f"  {f}: {len(res)} polylines")
            break
except Exception as e:
    print(f"Gerber dir error: {e}")

print("\nTesting CadBridge.importFile...")
from bridges.cad_bridge import CadBridge
bridge = CadBridge()

def on_imported(shapes):
    print(f"[Callback] Shapes imported: {len(shapes)}")
    for s in shapes:
        paths = s.get('paths', [])
        print(f"  Shape: name='{s['name']}', type={s['type']}, size={s['wMm']}x{s['hMm']}mm, paths={len(paths)}")

bridge.shapesImported.connect(on_imported)

print("Importing DXF with URL formatting:")
bridge.importFile("file:///d:/Galvo_using_qml/Galvo_UI_2_with_cad_page/dxf_files/2x2.dxf")

print("\nImporting Gerber with space in URL formatting:")
bridge.importFile("file:///d:/Galvo_using_qml/Galvo_UI_2_with_cad_page/Gerber_files/Arduino%20Nano%20IO%20Shield%20Gerber/Arduino%20Nano%20IO%20Shield-B_Cu.gbr")

