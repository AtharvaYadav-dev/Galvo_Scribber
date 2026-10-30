import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle

def test():
    QQuickStyle.setStyle("Basic")
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(_app_dir, "qml"))

    # We will test loading CadComboBox with searchable=true
    comp = QQmlComponent(engine, os.path.join(_app_dir, "qml", "components", "cad", "CadComboBox.qml"))
    if comp.status() != QQmlComponent.Status.Ready:
        for err in comp.errors():
            print("Error in CadComboBox:", err.toString())
        return False
    print("CadComboBox is Ready!")
    return True

if __name__ == "__main__":
    test()
