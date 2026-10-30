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

    qml_code = """
    import QtQuick
    import QtQuick.Controls
    import QtQuick.Layouts
    import "qml"
    import "qml/components/cad"

    Rectangle {
        width: 400
        height: 500
        color: "#0F172A"

        CadComboBox {
            id: combo
            searchable: true
            model: [
                "Segoe UI", "Arial", "Arial Black", "Calibri", "Cambria",
                "Consolas", "Courier New", "Georgia", "Impact", "Times New Roman",
                "Trebuchet MS", "Verdana"
            ]
        }
    }
    """

    comp = QQmlComponent(engine)
    comp.setData(qml_code.encode("utf-8"), "")
    if comp.status() != QQmlComponent.Status.Ready:
        for err in comp.errors():
            print("Error:", err.toString())
        return False
    
    obj = comp.create()
    print("Test object created:", obj is not None)
    return True

if __name__ == "__main__":
    test()

