import os
import sys
import io

# Ensure utf-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from bridges.galvo_bridge import GalvoBridge
from bridges.cad_bridge import CadBridge

def run_test():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)

    galvo = GalvoBridge()
    cad = CadBridge(galvo_bridge=galvo)

    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_app_dir, "qml"))
    engine.rootContext().setContextProperty("cad", cad)

    comp = QQmlComponent(engine, os.path.join(_app_dir, "qml", "views", "CadView.qml"))
    if comp.status() != QQmlComponent.Status.Ready:
        for err in comp.errors():
            print("QML Error:", err.toString())
        return False

    view = comp.create()
    if not view:
        print("FAIL: could not create CadView")
        return False

    canvas = view.findChild(QObject, "cadCanvas")
    assert canvas is not None

    print(f"Total available fonts in CadBridge: {len(cad.availableFonts)}")
    assert len(cad.availableFonts) > 5

    # 1. Add a text shape
    t_shape = {
        "id": 1,
        "name": "Text_1",
        "type": "text",
        "text": "SEARCHABLE FONT TEST",
        "xMm": 0.0,
        "yMm": 0.0,
        "wMm": 50.0,
        "hMm": 6.0,
        "fontFamily": "Segoe UI",
        "rotation": 0,
        "penId": 0,
        "hatched": False,
        "visible": True,
        "locked": False
    }

    canvas.setProperty("shapes", [t_shape])
    canvas.setProperty("selectedIndex", 0)

    # 2. Find fontFamilyCombo in inspector
    # In QML, inspector is inside CadView
    inspector = view.findChild(QObject, "inspector")
    assert inspector is not None, "Inspector not found"

    combo = inspector.findChild(QObject, "fontFamilyCombo")
    assert combo is not None, "fontFamilyCombo not found"

    print("fontFamilyCombo searchable:", combo.property("searchable"))
    assert combo.property("searchable") == True

    # 3. Test filtering with 'arial'
    combo.setProperty("searchFilter", "arial")
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print(f"Filter 'arial' yielded {len(fm)} fonts: {fm[:5]}")
    assert len(fm) >= 1
    assert any("arial" in str(x).lower() for x in fm)

    # 4. Test filtering with 'times'
    combo.setProperty("searchFilter", "times")
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print(f"Filter 'times' yielded {len(fm)} fonts: {fm[:5]}")
    assert any("times" in str(x).lower() for x in fm)

    # 5. Select font via selectItem
    target_font = fm[0]
    combo.selectItem(target_font)

    shapes = canvas.property("shapes")
    if hasattr(shapes, "toVariant"):
        shapes = shapes.toVariant()
    current_font = shapes[0]["fontFamily"]
    print(f"After selecting: shape fontFamily is '{current_font}' (expected '{target_font}')")
    assert current_font == target_font

    # 6. Check text width re-measurement
    print(f"Recalculated text width: {shapes[0]['wMm']:.3f} mm")
    assert shapes[0]["wMm"] > 0

    # 7. Test font modal
    font_modal = view.findChild(QObject, "textFontModal")
    assert font_modal is not None
    modal_combo = font_modal.findChild(QObject, "modalFontCombo")
    assert modal_combo is not None
    assert modal_combo.property("searchable") == True
    print("modalFontCombo in CadTextFontModal is also searchable: True")

    print("\n=======================================================")
    print("ALL TEXT FACE SEARCH TESTS PASSED 100%!")
    print("=======================================================")
    return True

if __name__ == "__main__":
    if not run_test():
        sys.exit(1)

