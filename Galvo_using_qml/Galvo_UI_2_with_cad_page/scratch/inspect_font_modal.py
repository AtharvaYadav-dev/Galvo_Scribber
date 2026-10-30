import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl

app = QApplication(sys.argv)
view = QQuickView()
view.setSource(QUrl.fromLocalFile("qml/components/cad/CadTextFontModal.qml"))
root = view.rootObject()
root.setProperty("isOpened", True)
root.setWidth(1000)
root.setHeight(800)
view.resize(1000, 800)
view.show()
app.processEvents()

for child in root.childItems():
    print("Top level child:", child, child.property("width"), child.property("height"), child.property("x"), child.property("y"))
    for c in child.childItems():
        print("  Child:", c, c.property("width"), c.property("height"), c.property("x"), c.property("y"))
        for c2 in c.childItems():
            print("    Grandchild:", c2, c2.property("width"), c2.property("height"), c2.property("x"), c2.property("y"))

view.grabWindow().save("scratch/font_modal_debug.png")
print("Saved debug screenshot")

