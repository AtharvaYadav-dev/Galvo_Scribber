import sys
sys.path.append(r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
from PySide6.QtGui import QGuiApplication
app = QGuiApplication(sys.argv)
from bridges.cad_bridge import CadBridge
cad = CadBridge()

text_shp = {
    "id": 1,
    "name": "Text_1",
    "type": "text",
    "text": "ABC",
    "xMm": 0.0,
    "yMm": 0.0,
    "wMm": 30.0,
    "hMm": 10.0,
    "rotation": 0.0,
    "hatched": True,
    "visible": True,
    "locked": False
}

cad.updateShapes([text_shp])
cad.executeMark([text_shp])

print("Planner preview queue length:", len(cad.planner.preview_queue))
jumps = [c for c in cad.planner.preview_queue if c.get('type') == 'jump']
marks = [c for c in cad.planner.preview_queue if c.get('type') == 'mark']
print(f"Jumps: {len(jumps)}, Marks: {len(marks)}")

if marks:
    print("Sample marks:")
    for m in marks[:5]:
        print(" ", m)
