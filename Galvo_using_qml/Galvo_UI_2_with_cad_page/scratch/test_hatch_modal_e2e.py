import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtCore import QUrl
from bridges.cad_bridge import CadBridge
from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge

def test_hatch_modal():
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    galvo = GalvoBridge()
    jog = JogBridge()
    cad = CadBridge(galvo, jog)

    engine.rootContext().setContextProperty("galvo", galvo)
    engine.rootContext().setContextProperty("jog", jog)
    engine.rootContext().setContextProperty("cad", cad)

    # Instantiate CadHatchModal directly
    modal_path = os.path.join(_root, "qml", "components", "cad", "CadHatchModal.qml")
    comp = QQmlComponent(engine, QUrl.fromLocalFile(modal_path))
    if comp.isError():
        for err in comp.errors():
            print("QML Error:", err.toString())
        assert False, "CadHatchModal component failed to compile"

    modal = comp.create()
    assert modal is not None, "Failed to create CadHatchModal object"
    print("CadHatchModal created successfully.")

    # Test openModal
    test_shape = {
        "id": 1,
        "type": "circle",
        "xMm": 0,
        "yMm": 0,
        "wMm": 15,
        "hMm": 15,
        "rotation": 0,
        "visible": True,
        "hatched": False
    }

    modal.openModal(test_shape)
    assert modal.property("visible") == True, "Modal should be visible after openModal"
    assert modal.property("currentProfileIdx") == 1, "Initial profile should be 1"

    # Test switching profiles
    modal.switchProfile(2)
    assert modal.property("currentProfileIdx") == 2, "Profile should be 2 after switch"

    modal.switchProfile(3)
    assert modal.property("currentProfileIdx") == 3, "Profile should be 3 after switch"

    # Test apply
    modal.applyAndClose()
    assert modal.property("visible") == False, "Modal should be hidden after applyAndClose"

    # Verify preview line generation for shape
    preview_lines = cad.computeHatchPreviewLines(test_shape)
    print(f"Generated {len(preview_lines)} preview hatch lines for circle shape")

    print("ALL CadHatchModal E2E tests PASSED!")

if __name__ == "__main__":
    test_hatch_modal()
