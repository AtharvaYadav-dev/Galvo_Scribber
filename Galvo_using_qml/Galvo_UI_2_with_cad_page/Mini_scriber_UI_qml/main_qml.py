import os
import sys
import time

# Ensure current working directory is the script/bundle directory so relative paths resolve
if getattr(sys, "frozen", False):
    _app_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))

if os.getcwd() != _app_dir:
    try:
        os.chdir(_app_dir)
    except Exception:
        pass
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

# Fix Windows D3D11 swapchain resize deadlock during maximize/restore/resize:
# 1. Force the synchronous "basic" render loop (single-threaded rendering on GUI thread).
#    This eliminates multi-threaded swapchain deadlocks, DXGI presentation hangs,
#    and the Windows DWM hardware cursor freeze when maximizing or resizing the window.
# 2. Enable High-DPI scaling.
os.environ["QSG_RENDER_LOOP"] = "basic"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtCore import QUrl, Qt, QTimer, QObject, QEvent
from PySide6.QtGui import QIcon, QFontDatabase, QPixmap, QPainter, QColor, QFont

from PySide6.QtQuickControls2 import QQuickStyle

# Import high-performance Python Bridges
from bridges.serial_bridge import SerialBridge
from bridges.motion_bridge import MotionBridge
from bridges.laser_bridge import LaserBridge
from bridges.camera_bridge import CameraBridge
from bridges.terminal_bridge import TerminalBridge
from bridges.job_bridge import JobBridge
from bridges.settings_bridge import SettingsBridge
from bridges.notification_bridge import NotificationBridge
from bridges.updater_bridge import UpdaterBridge

class UIActivityFilter(QObject):
    """Global filter detecting any user interaction across the entire UI with 1.0s debounce
    to prevent event queue starvation during rapid mouse movement or window resizing."""
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        self._last_trigger = 0.0
        self.activity_events = {
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.Wheel,
            QEvent.Type.TouchBegin,
            QEvent.Type.TouchUpdate,
        }

    def eventFilter(self, watched, event):
        if event.type() in self.activity_events:
            now = time.monotonic()
            if now - self._last_trigger >= 1.0:
                self._last_trigger = now
                self.callback()
        return super().eventFilter(watched, event)

def main():
    # PassThrough rounding prevents 1-pixel rounding mismatches between Windows work area
    # and Qt geometry that can abort or hang window maximize on scaled displays.
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    QQuickStyle.setStyle("Basic")
    import version
    app.setApplicationName(version.APP_NAME)
    app.setOrganizationName("Spécialisé Products Private Limited")
    app.setOrganizationDomain("specialiseproducts.com")
    app.setStyle("Fusion")

    # Immediate Native Splash Screen (shows within 150ms so user knows the app is opening)
    splash = None
    splash_path = os.path.join(_app_dir, "logo", "SPPL-logo-sq.png")
    if os.path.exists(splash_path):
        try:
            splash_pix = QPixmap(340, 220)
            splash_pix.fill(QColor("#0F172A"))
            p = QPainter(splash_pix)
            p.setRenderHint(QPainter.Antialiasing)
            logo_pix = QPixmap(splash_path).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.drawPixmap(134, 25, logo_pix)
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Inter", 13, QFont.Bold))
            p.drawText(0, 130, 340, 25, Qt.AlignCenter, f"{version.APP_NAME} 2.0")
            p.setPen(QColor("#00E5FF"))
            p.setFont(QFont("Inter", 9, QFont.Normal))
            p.drawText(0, 160, 340, 20, Qt.AlignCenter, "Starting declarative GPU engine...")
            p.end()
            splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            splash.show()
            app.processEvents()
        except Exception as e:
            print(f"[main_qml] Splash screen notice: {e}")
 
    # Register Google Font Icons (Material Icons) for professional UI vector iconography
    font_paths = [
        os.path.join(_app_dir, "fonts", "MaterialIcons-Regular.ttf"),
        os.path.join(_app_dir, "qml", "fonts", "MaterialIcons-Regular.ttf")
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            font_id = QFontDatabase.addApplicationFont(fp)
            if font_id != -1:
                print(f"[main_qml] Successfully registered font: {QFontDatabase.applicationFontFamilies(font_id)}")
                break
            else:
                print(f"[main_qml] Warning: Failed to register font at {fp}")

    # Instantiate Bridges
    serial_bridge = SerialBridge()
    settings_bridge = SettingsBridge()
    motion_bridge = MotionBridge(serial_bridge, settings_bridge)
    laser_bridge = LaserBridge(serial_bridge, motion_bridge, settings_bridge)
    camera_bridge = CameraBridge()
    terminal_bridge = TerminalBridge(serial_bridge)
    job_bridge = JobBridge(serial_bridge, motion_bridge, settings_bridge)
    notification_bridge = NotificationBridge(
        serial_bridge=serial_bridge,
        motion_bridge=motion_bridge,
        laser_bridge=laser_bridge,
        job_bridge=job_bridge,
        settings_bridge=settings_bridge
    )
    updater_bridge = UpdaterBridge(
        laser_bridge=laser_bridge,
        camera_bridge=camera_bridge,
        notification_bridge=notification_bridge,
        parent=app
    )

    # Install UI Activity Inactivity Watcher (Resets 10-minute idle timer on any UI movement)
    activity_filter = UIActivityFilter(settings_bridge.userActivityDetected, app)
    app.installEventFilter(activity_filter)

    logo_path = os.path.abspath(os.path.join(_app_dir, "logo", "SPPL-logo-sq.png"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    # Initialize QML Engine
    engine = QQmlApplicationEngine()

    # Register Camera Image Provider for zero-latency direct frame rendering
    engine.addImageProvider("camera", camera_bridge.image_provider)

    # Expose bridges and branding to QML context
    root_context = engine.rootContext()
    root_context.setContextProperty("appLogoUrl", QUrl.fromLocalFile(logo_path).toString() if os.path.exists(logo_path) else "")
    root_context.setContextProperty("serial", serial_bridge)
    root_context.setContextProperty("motion", motion_bridge)
    root_context.setContextProperty("laser", laser_bridge)
    root_context.setContextProperty("camera", camera_bridge)
    root_context.setContextProperty("terminal", terminal_bridge)
    root_context.setContextProperty("job", job_bridge)
    root_context.setContextProperty("settings", settings_bridge)
    root_context.setContextProperty("notifications", notification_bridge)
    root_context.setContextProperty("updater", updater_bridge)

    # Automatic background check for updates 5 seconds after startup
    QTimer.singleShot(5000, lambda: updater_bridge.checkForUpdates(silent=True))

    # Instantiate centralized Theme object based on Figma specifications
    theme_qml_path = os.path.join(_app_dir, "qml", "ThemeTokens.qml")
    theme_component = QQmlComponent(engine, QUrl.fromLocalFile(theme_qml_path))
    theme_obj = theme_component.create(root_context)
    if theme_obj:
        root_context.setContextProperty("Theme", theme_obj)
    else:
        print("[main_qml] Notice: Theme component fallback")

    # Load main QML file
    qml_file = os.path.join(_app_dir, "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        print(f"Error: Failed to load QML interface from {qml_file}")
        sys.exit(-1)

    win = engine.rootObjects()[0]
    if splash:
        splash.close()

    # Guarantee immediate frame presentation on window state changes (Maximize, Restore, Minimize)
    # to keep DWM compositor and DirectX swapchain in lockstep.
    try:
        win.windowStateChanged.connect(lambda state: win.requestUpdate())
        win.visibleChanged.connect(lambda: win.requestUpdate())
    except Exception as e:
        print(f"[main_qml] Notice: window update hook {e}")

    # Apply Windows 10/11 Dark/Light Mode and Custom Titlebar Color
    _cached_hwnd = None
    def apply_dwm_titlebar():
        nonlocal _cached_hwnd
        if sys.platform == "win32" and win:
            try:
                import ctypes
                if _cached_hwnd is None:
                    _cached_hwnd = int(win.winId())
                hwnd = _cached_hwnd
                dwm = ctypes.windll.dwmapi
                is_dark = settings_bridge.isDark
                
                # 1. Enable Immersive Dark Mode (1 for dark, 0 for light)
                dark_mode = ctypes.c_int(1 if is_dark else 0)
                dwm.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
                dwm.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
                
                # 2. Set Titlebar Background Color (DWMWA_CAPTION_COLOR = 35)
                # Dark: #0F172A (0x002A170F), Light: #FFFFFF (0x00FFFFFF)
                cap_color = ctypes.c_uint32(0x002A170F if is_dark else 0x00FFFFFF)
                dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(cap_color), ctypes.sizeof(cap_color))
                
                # 3. Set Titlebar Border Color (DWMWA_BORDER_COLOR = 34)
                # Dark: #1E293B (0x003B291E), Light: #DCE2EC (0x00ECE2DC)
                border_color = ctypes.c_uint32(0x003B291E if is_dark else 0x00ECE2DC)
                dwm.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_color), ctypes.sizeof(border_color))

                # 4. Set Titlebar Text Color (DWMWA_TEXT_COLOR = 36)
                # Dark: #FFFFFF (0x00FFFFFF), Light: #172440 (0x00402417)
                txt_color = ctypes.c_uint32(0x00FFFFFF if is_dark else 0x00402417)
                dwm.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(txt_color), ctypes.sizeof(txt_color))
            except Exception as e:
                print(f"[main_qml] DWM titlebar styling notice: {e}")

    apply_dwm_titlebar()
    QTimer.singleShot(150, apply_dwm_titlebar)
    settings_bridge.themeChanged.connect(apply_dwm_titlebar)

    # Clean Application Shutdown Hook:
    # Guarantees that all lasers are automatically extinguished and COM port disconnected
    # matching main.py closeEvent() and shutdownLaser()
    _exited = False
    def on_app_exit():
        nonlocal _exited
        if _exited:
            return
        _exited = True
        print("[main_qml] Application exit requested — executing automatic laser shutdown...")
        try:
            # Safely stop active job timer without sending any motion/homing commands (no G28)
            if hasattr(job_bridge, "_exec_timer"):
                job_bridge._exec_timer.stop()
        except Exception as e:
            print(f"[main_qml] Job stop on exit notice: {e}")
        try:
            laser_bridge.shutdownLaser()
        except Exception as e:
            print(f"[main_qml] Laser shutdown on exit notice: {e}")
        try:
            camera_bridge.stopCamera()
        except Exception as e:
            print(f"[main_qml] Camera stop on exit notice: {e}")
        try:
            serial_bridge.disconnectSerial()
        except Exception as e:
            print(f"[main_qml] Serial disconnect on exit notice: {e}")

    app.aboutToQuit.connect(on_app_exit)

    print("==================================================")
    print(" Mini Scriber 2.0 (PySide6 + QML) Engine Started")
    print(" Zero Qt Designer XML — 100% Declarative UI")
    print("==================================================")

    ret = app.exec()
    on_app_exit()
    sys.exit(ret)

if __name__ == "__main__":
    main()
