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

from PySide6.QtCore import Qt, QObject, Slot, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.serial_bridge import SerialBridge
from bridges.cad_bridge import CadBridge
from bridges.camera_bridge import CameraBridge, CameraVideoItem
from bridges.settings_bridge import SettingsBridge
from bridges.matrix_bridge import MatrixBridge
from bridges.calibration_bridge import CalibrationBridge


class ThemeManager(QObject):
    """Bridge for syncing OS window titlebar and DWM attributes with the QML theme."""
    def __init__(self, win=None, parent=None):
        super().__init__(parent)
        self.win = win

    def setWindow(self, win):
        self.win = win

    @Slot(bool)
    def updateTheme(self, is_dark: bool):
        if sys.platform == "win32" and self.win:
            try:
                import ctypes
                hwnd = int(self.win.winId())
                dwm = ctypes.windll.dwmapi
                
                # 1. Enable Immersive Dark Mode (20 = Windows 11 / modern 10, 19 = early Windows 10)
                dark_mode = ctypes.c_int(1 if is_dark else 0)
                dwm.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
                dwm.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
                
                # 2. Set Caption Background Color (DWMWA_CAPTION_COLOR = 35)
                # Dark: #0F172A (0x002A170F), Light: #FFFFFF (0x00FFFFFF)
                cap_color = ctypes.c_uint32(0x002A170F if is_dark else 0x00FFFFFF)
                dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(cap_color), ctypes.sizeof(cap_color))
                
                # 3. Set Border Color (DWMWA_BORDER_COLOR = 34)
                # Dark: #1E2C4A (0x004A2C1E), Light: #DCE3EE (0x00EEE3DC)
                border_color = ctypes.c_uint32(0x004A2C1E if is_dark else 0x00EEE3DC)
                dwm.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_color), ctypes.sizeof(border_color))
                
                # 4. Set Title Text Color (DWMWA_TEXT_COLOR = 36)
                # Dark: #FFFFFF (0x00FFFFFF), Light: #0F172A (0x002A170F)
                txt_color = ctypes.c_uint32(0x00FFFFFF if is_dark else 0x002A170F)
                dwm.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(txt_color), ctypes.sizeof(txt_color))
            except Exception as e:
                print(f"[main_qml] DWM titlebar styling notice: {e}")


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

    # Register vector icon font
    from PySide6.QtGui import QFontDatabase
    font_path = os.path.join(_app_dir, "qml", "fonts", "MaterialIcons-Regular.ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    # Register custom C++/Python QML Types
    qmlRegisterType(CameraVideoItem, "GalvoVision", 1, 0, "CameraVideoItem")

    # Set application icon if available
    icon_path = os.path.join(_app_dir, "logo", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialize Hardware, CAD, Vision, Settings & Matrix Bridges
    galvo_bridge = GalvoBridge()
    jog_bridge = JogBridge(galvo_bridge=galvo_bridge)
    serial_bridge = SerialBridge()
    cad_bridge = CadBridge(galvo_bridge=galvo_bridge, jog_bridge=jog_bridge)
    camera_bridge = CameraBridge()
    settings_bridge = SettingsBridge(cad_bridge=cad_bridge)
    matrix_bridge = MatrixBridge(galvo_bridge=galvo_bridge)
    calibration_bridge = CalibrationBridge(galvo_bridge=galvo_bridge, settings_bridge=settings_bridge)

    if settings_bridge.machineName:
        app.setApplicationName(settings_bridge.machineName)

    # Resolve company logo URL for QML
    logo_file = os.path.join(_app_dir, "logo", "SPPL-logo-sq.png")
    app_logo_url = "file:///" + logo_file.replace("\\", "/")

    # Create QML Application Engine
    engine = QQmlApplicationEngine()

    # Add QML directory to import search paths
    qml_dir = os.path.join(_app_dir, "qml")
    engine.addImportPath(qml_dir)

    theme_manager = ThemeManager()

    # Expose Python objects to QML globally
    root_context = engine.rootContext()
    root_context.setContextProperty("galvo", galvo_bridge)
    root_context.setContextProperty("jog", jog_bridge)
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("cad", cad_bridge)
    root_context.setContextProperty("camera", camera_bridge)
    root_context.setContextProperty("settings", settings_bridge)
    root_context.setContextProperty("matrix", matrix_bridge)
    root_context.setContextProperty("matrixBridge", matrix_bridge)
    root_context.setContextProperty("calibration", calibration_bridge)
    root_context.setContextProperty("calibrationBridge", calibration_bridge)
    root_context.setContextProperty("appLogoUrl", app_logo_url)
    root_context.setContextProperty("themeManager", theme_manager)

    # Load Main QML file
    main_qml_path = os.path.join(qml_dir, "main.qml")
    engine.load(main_qml_path)

    root_objs = engine.rootObjects()
    if not root_objs:
        print("ERROR: Failed to load main.qml!")
        sys.exit(-1)

    win = root_objs[0]
    theme_manager.setWindow(win)
    theme_manager.updateTheme(True)
    QTimer.singleShot(100, lambda: theme_manager.updateTheme(True))

    # Dynamically sync window title when machine name is changed in Settings
    settings_bridge.machineNameChanged.connect(
        lambda name: win.setTitle(f"{name} — Industrial CAD & Laser Workstation") if win else None
    )

    print("==================================================")
    print(" GALVO STUDIO (PySide6 QML Edition) STARTED")
    print(" 100% Python Architecture - Zero Qt Designer XML")
    print("==================================================")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
