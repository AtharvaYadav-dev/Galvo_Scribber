import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl
from PIL import Image

app = QApplication(sys.argv)
view = QQuickView()
view.setSource(QUrl.fromLocalFile("qml/components/cad/CadHatchModal.qml"))
root = view.rootObject()
view.show()
app.processEvents()

root.openModal(None)
app.processEvents()

modalCard = root.childItems()[0]

def grab_modal(w, h, out_path):
    modalCard.setProperty("width", w)
    modalCard.setProperty("height", h)
    modalCard.setProperty("x", 10)
    modalCard.setProperty("y", 10)
    view.resize(w + 30, h + 30)
    app.processEvents()
    im = view.grabWindow()
    im.save(out_path)
    # Also crop tightly around modalCard
    pil_im = Image.open(out_path)
    cropped = pil_im.crop((10, 10, 10 + w, 10 + h))
    cropped.save(out_path.replace(".png", "_crop.png"))
    print(f"Saved {w}x{h} to {out_path}")

grab_modal(760, 580, "scratch/hatch_test_760.png")
grab_modal(640, 520, "scratch/hatch_test_640.png")
grab_modal(560, 480, "scratch/hatch_test_560.png")
