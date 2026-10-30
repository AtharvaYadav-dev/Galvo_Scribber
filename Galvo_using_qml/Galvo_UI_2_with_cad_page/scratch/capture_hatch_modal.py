import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl, QTimer
from bridges.cad_bridge import CadBridge
from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge

def capture():
    app = QApplication.instance() or QApplication(sys.argv)
    view = QQuickView()

    galvo = GalvoBridge()
    jog = JogBridge()
    cad = CadBridge(galvo, jog)

    view.rootContext().setContextProperty("galvo", galvo)
    view.rootContext().setContextProperty("jog", jog)
    view.rootContext().setContextProperty("cad", cad)

    wrapper_qml = os.path.join(_root, "scratch", "hatch_modal_preview.qml")
    with open(wrapper_qml, "w", encoding="utf-8") as f:
        f.write('''import QtQuick
import QtQuick.Controls
import "../qml/components/cad"

Rectangle {
    width: 840
    height: 700
    color: "#080C16"

    CadHatchModal {
        id: modal
        anchors.fill: parent
        visible: true
        Component.onCompleted: {
            openModal(null)
        }
    }
}
''')

    view.setSource(QUrl.fromLocalFile(wrapper_qml))
    view.resize(840, 700)
    view.show()

    output_path = os.path.join(_root, "scratch", "hatch_modal_screenshot.png")

    def do_grab():
        img = view.grabWindow()
        img.save(output_path)
        print("SAVED_SCREENSHOT:", output_path)
        app.quit()

    QTimer.singleShot(800, do_grab)
    app.exec()

if __name__ == "__main__":
    capture()
