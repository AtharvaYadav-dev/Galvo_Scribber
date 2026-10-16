import os
import sys

# Ensure current working directory is the script directory so relative paths resolve
_app_dir = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _app_dir:
    try:
        os.chdir(_app_dir)
    except Exception:
        pass
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Set modern dark-compatible style
    QQuickStyle.setStyle("Basic")

    app = QApplication(sys.argv)
    app.setApplicationName("Galvo Studio")
    app.setOrganizationName("ProSys")

    # Register custom C++/Python QML Types
    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    # Set application icon if available
    icon_path = os.path.join(_app_dir, "logo", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialize Hardware, CAD & Vision Bridges
    galvo_bridge = GalvoBridge()
    jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
    serial_bridge = SerialBridge()
    cad_bridge = CadBridge(galvo_bridge=galvo_bridge)
    camera_bridge = CameraBridge()

    # Create QML Application Engine
    engine = QQmlApplicationEngine()

    # Add QML directory to import search paths
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    # Expose Python objects to QML globally
    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)

    # Load Main QML file
    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    if not engine.rootObjects():
        print("ERROR: Failed to load main.qml!")
        sys.exit(-1)

    print("==================================================")
    print(" GALVO STUDIO (PySide6 QML Edition) STARTED")
    print(" 100% Python Architecture - Zero Qt Designer XML")
    print("==================================================")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
