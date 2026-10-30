import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

def test():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_data = b"""
    import QtQuick
    import QtQuick.Controls

    ApplicationWindow {
        visible: false
        width: 400
        height: 300
        title: "Test"
    }
    """
    engine.loadData(qml_data)
    if not engine.rootObjects():
        print("ERROR: Root object not created")
        return False
    print("SUCCESS: PySide6 QML loaded QtQuick and QtQuick.Controls!")
    return True

if __name__ == "__main__":
    test()
