import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle

def test_search_logic():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_app_dir, "qml"))

    comp = QQmlComponent(engine, os.path.join(_app_dir, "qml", "components", "cad", "CadComboBox.qml"))
    if comp.status() != QQmlComponent.Status.Ready:
        for err in comp.errors():
            print("Error:", err.toString())
        return False

    combo = comp.create()
    combo.setProperty("searchable", True)
    test_fonts = ["Segoe UI", "Arial", "Calibri", "Consolas", "Courier New", "Times New Roman"]
    combo.setProperty("model", test_fonts)

    # 1. Check all items initially
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print("Initial filteredModel:", fm)
    assert len(fm) == 6

    # 2. Filter by 'co'
    combo.setProperty("searchFilter", "co")
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print("After filter 'co':", fm)
    assert len(fm) == 2
    assert "Consolas" in fm and "Courier New" in fm

    # 3. Filter by 'times'
    combo.setProperty("searchFilter", "times")
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print("After filter 'times':", fm)
    assert len(fm) == 1
    assert fm[0] == "Times New Roman"

    # 4. Select item
    combo.selectItem("Times New Roman")
    print("Selected displayText:", combo.property("displayText"))
    print("Selected currentIndex:", combo.property("currentIndex"))
    assert combo.property("displayText") == "Times New Roman"
    assert combo.property("currentIndex") == 5

    # 5. Clear filter
    combo.setProperty("searchFilter", "")
    fm = combo.property("filteredModel")
    if hasattr(fm, "toVariant"):
        fm = fm.toVariant()
    print("After clearing filter:", len(fm))
    assert len(fm) == 6

    print("\n--- CAD COMBOBOX SEARCH LOGIC VERIFIED 100% ---")
    return True

if __name__ == "__main__":
    test_search_logic()

