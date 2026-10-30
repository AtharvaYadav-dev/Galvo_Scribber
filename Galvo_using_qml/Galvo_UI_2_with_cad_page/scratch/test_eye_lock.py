import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
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

cadCanvas = None
inspector = None
for c in root.findChildren(object):
    cls = c.metaObject().className()
    if "CadCanvas" in cls:
        cadCanvas = c
    elif "CadInspectorPanel" in cls:
        inspector = c

print("Found cadCanvas and inspector")

shapes = [
    {"type": "rect", "name": "Rect_1", "xMm": 0, "yMm": 0, "wMm": 20, "hMm": 20, "penId": 0, "visible": True, "locked": False},
    {"type": "circle", "name": "Circle_2", "xMm": 10, "yMm": 10, "wMm": 15, "hMm": 15, "penId": 1, "visible": True, "locked": False}
]
cadCanvas.setProperty("shapes", shapes)
app.processEvents()

print("Initial shapesModel length in inspector:", len(inspector.property("shapesModel")))

# Let's inspect the delegates in entitiesRepeater
repeater = None
for r in inspector.findChildren(object):
    if "Repeater" in r.metaObject().className():
        repeater = r
        break

print("Repeater count:", repeater.property("count") if repeater else "No repeater")

# Let's call cadCanvas.toggleShapeLock(0)
print("Calling toggleShapeLock(0)...")
cadCanvas.toggleShapeLock(0)
app.processEvents()

print("After toggleShapeLock, shapes[0].locked =", cadCanvas.property("shapes")[0].get("locked"))
print("After toggleShapeLock, inspector shapesModel[0].locked =", inspector.property("shapesModel")[0].get("locked"))

# Now let's check delegate visual state
found_delegates = 0
for child in inspector.findChildren(object):
    isLck = child.property("isLck")
    if isLck is not None:
        found_delegates += 1
        print("Delegate item isLck property:", isLck)
print("Total delegates with isLck found:", found_delegates)
