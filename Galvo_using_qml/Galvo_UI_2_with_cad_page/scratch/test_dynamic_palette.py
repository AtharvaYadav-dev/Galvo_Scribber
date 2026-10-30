import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

def test_dynamic_palette():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    qml_str = """
    import QtQuick
    import "."

    Item {
        id: root
        Component.onCompleted: {
            console.log("Initial count:", Theme.penPalette.length)
        }
    }
    """
    engine.loadData(qml_str.encode('utf-8'), os.path.join(qml_dir, "test.qml"))
    if not engine.rootObjects():
        print("FAIL")
        return False
    print("SUCCESS")
    return True

if __name__ == "__main__":
    test_dynamic_palette()

