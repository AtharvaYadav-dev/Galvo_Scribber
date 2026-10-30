import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl

app = QApplication(sys.argv)
view = QQuickView()
view.setSource(QUrl.fromLocalFile("qml/views/CadView.qml"))
root = view.rootObject()
view.resize(1200, 800)
view.show()
app.processEvents()

# Find cadCanvas and inspector
cadCanvas = None
inspector = None
for c in root.findChildren(object):
    cls = c.metaObject().className()
    if "CadCanvas" in cls:
        cadCanvas = c
    elif "CadInspectorPanel" in cls:
        inspector = c

print("Found cadCanvas:", cadCanvas)
print("Found inspector:", inspector)

# Add 2 shapes via cadCanvas
shapes = [
    {"type": "rect", "name": "Rect_1", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "penId": 0, "visible": True, "locked": False},
    {"type": "circle", "name": "Circle_2", "xMm": 10, "yMm": 10, "wMm": 15, "hMm": 15, "penId": 1, "visible": True, "locked": False}
]
cadCanvas.setProperty("shapes", shapes)
app.processEvents()

# Check delegate items
def print_delegates():
    for item in inspector.findChildren(object):
        isLck = item.property("isLck")
        isVis = item.property("isVis")
        if isLck is not None:
            print("  Delegate item:", item, "isLck=", isLck, "isVis=", isVis)

print("Before lock toggle:")
print_delegates()

print("Calling cadCanvas.toggleShapeLock(0)...")
cadCanvas.toggleShapeLock(0)
app.processEvents()

print("After lock toggle:")
print_delegates()

