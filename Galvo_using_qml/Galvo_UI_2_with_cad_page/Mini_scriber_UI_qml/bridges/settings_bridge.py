import os
import time
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from util import ConfigHandler

class SettingsBridge(QObject):
    settingsChanged = Signal()
    roleChanged = Signal()
    themeChanged = Signal()
    hardwareConfigChanged = Signal()
    cameraEnabledChanged = Signal()
    originPositionChanged = Signal()
    loginSuccess = Signal(str)
    loginFailed = Signal(str)
    settingsSaved = Signal(str)
    inactivityTick = Signal(int)
    rolePermissionsChanged = Signal()
    settingsPermissionsChanged = Signal()

    DEFAULT_OPERATOR_PAGES = ["motion", "laser", "job", "camera", "settings"]
    DEFAULT_SUPERVISOR_PAGES = ["motion", "laser", "job", "camera", "terminal", "settings"]

    DEFAULT_OPERATOR_SETTINGS_TABS = ["profile", "serial", "feeds", "system"]
    DEFAULT_SUPERVISOR_SETTINGS_TABS = ["profile", "serial", "feeds", "origin", "camera_offset", "system"]

    PASSWORDS = {
        "Operator": "012345",
        "Supervisor": "452301",
        "Admin": "SPPL@2026"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ch = ConfigHandler()
        
        # Path to config.ini
        import sys
        if getattr(sys, "frozen", False):
            app_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_path = os.path.join(app_dir, "config", "config.ini")

        # User Authentication & Inactivity Timeout (10 minutes = 600s)
        self._current_role = "Operator"
        self._is_privileged = False
        self._inactivity_timeout_sec = 600
        self._last_activity_time = 0.0
        self._supervisor_remaining_sec = 0

        self._inactivity_ticker = QTimer(self)
        self._inactivity_ticker.setInterval(1000)
        self._inactivity_ticker.timeout.connect(self._on_inactivity_tick)

        # Settings state
        self._theme = "dark"
        self._xindex = 10.0
        self._yindex = 10.0
        self._jog_feed = 1000
        self._laser_feed = 500
        self._cam_laser1_x = 35.8
        self._cam_laser1_y = -7.6
        self._cam_laser2_x = 84.5
        self._cam_laser2_y = -8.0
        self._cam_inspection_feed = 300
        self._cam_jog_feed = 500

        # Hardware setup state (Admin configurable from config.ini)
        self._machine_name = "Mini Scriber"
        self._laser_count = 2
        self._bed_width = 100.0
        self._bed_height = 100.0
        self._z_max = 16.0
        self._camera_enabled = True
        self._origin_position = "top-right"

        # Role-based page visibility permissions (Admin configurable)
        self._operator_pages = list(self.DEFAULT_OPERATOR_PAGES)
        self._supervisor_pages = list(self.DEFAULT_SUPERVISOR_PAGES)

        # Role-based settings tab visibility permissions (Admin configurable)
        self._operator_settings_tabs = list(self.DEFAULT_OPERATOR_SETTINGS_TABS)
        self._supervisor_settings_tabs = list(self.DEFAULT_SUPERVISOR_SETTINGS_TABS)

        self.loadSettings()

    def loadSettings(self):
        """Loads all machine settings from config.ini"""
        try:
            self._ch.ini_parser.read(self._config_path)

            # UI Theme: Always default to dark theme whenever UI is opened or installed
            self._theme = "dark"
            saved_theme = self._ch.getValues("ui", "theme")
            if saved_theme != "dark":
                try:
                    self._ch.addParameter("ui", "theme", "dark")
                    self._ch.updateFile(self._config_path)
                except Exception:
                    pass

            # Index
            x_val = self._ch.getValues("index", "xindex")
            y_val = self._ch.getValues("index", "yindex")
            if x_val is not None: self._xindex = float(x_val)
            if y_val is not None: self._yindex = float(y_val)

            # Feed
            jog_val = self._ch.getValues("feed", "jog")
            laser_val = self._ch.getValues("feed", "laser")
            if jog_val is not None: self._jog_feed = int(jog_val)
            if laser_val is not None: self._laser_feed = int(laser_val)

            # Camera Offset
            c1_x = self._ch.getValues("camera_offset", "laser1_x")
            c1_y = self._ch.getValues("camera_offset", "laser1_y")
            c2_x = self._ch.getValues("camera_offset", "laser2_x")
            c2_y = self._ch.getValues("camera_offset", "laser2_y")
            if c1_x is not None: self._cam_laser1_x = float(c1_x)
            if c1_y is not None: self._cam_laser1_y = float(c1_y)
            if c2_x is not None: self._cam_laser2_x = float(c2_x)
            if c2_y is not None: self._cam_laser2_y = float(c2_y)

            # Camera Speeds
            c_insp = self._ch.getValues("camera", "inspection_feed")
            c_jog = self._ch.getValues("camera", "jog_feed")
            if c_insp is not None: self._cam_inspection_feed = int(c_insp)
            if c_jog is not None: self._cam_jog_feed = int(c_jog)

            # Hardware Setup ([hardware])
            mn = self._ch.getValues("hardware", "machine_name")
            if not mn:
                mn = self._ch.getValues("main", "machine_name")
            if mn and str(mn).strip():
                self._machine_name = str(mn).strip()
            else:
                self._machine_name = "Mini Scriber"

            lc = self._ch.getValues("hardware", "laser_count")
            if lc is not None:
                try: self._laser_count = max(1, min(2, int(lc)))
                except ValueError: pass

            bw = self._ch.getValues("hardware", "bed_width")
            bh = self._ch.getValues("hardware", "bed_height")
            if bw is not None:
                try: self._bed_width = float(bw)
                except ValueError: pass
            if bh is not None:
                try: self._bed_height = float(bh)
                except ValueError: pass

            zm = self._ch.getValues("hardware", "z_max")
            if zm is not None:
                try: self._z_max = float(zm)
                except ValueError: pass

            ce = self._ch.getValues("hardware", "camera_enabled")
            if ce is not None:
                self._camera_enabled = (str(ce).strip().lower() in ("true", "1", "yes"))

            op = self._ch.getValues("hardware", "origin_position")
            if op in ("top-right", "top-left", "bottom-left", "bottom-right"):
                self._origin_position = str(op).strip().lower()
            else:
                self._origin_position = "top-right"

            # Role-based Page Visibility Permissions ([permissions])
            op_p = self._ch.getValues("permissions", "operator_pages")
            if op_p is not None and str(op_p).strip():
                self._operator_pages = [p.strip().lower() for p in str(op_p).split(",") if p.strip()]
            else:
                self._operator_pages = list(self.DEFAULT_OPERATOR_PAGES)

            sp_p = self._ch.getValues("permissions", "supervisor_pages")
            if sp_p is not None and str(sp_p).strip():
                self._supervisor_pages = [p.strip().lower() for p in str(sp_p).split(",") if p.strip()]
            else:
                self._supervisor_pages = list(self.DEFAULT_SUPERVISOR_PAGES)

            # Role-based Settings Tabs Permissions ([settings_permissions])
            op_st = self._ch.getValues("settings_permissions", "operator_tabs")
            if op_st is not None and str(op_st).strip():
                self._operator_settings_tabs = [p.strip().lower() for p in str(op_st).split(",") if p.strip()]
            else:
                self._operator_settings_tabs = list(self.DEFAULT_OPERATOR_SETTINGS_TABS)

            sp_st = self._ch.getValues("settings_permissions", "supervisor_tabs")
            if sp_st is not None and str(sp_st).strip():
                self._supervisor_settings_tabs = [p.strip().lower() for p in str(sp_st).split(",") if p.strip()]
            else:
                self._supervisor_settings_tabs = list(self.DEFAULT_SUPERVISOR_SETTINGS_TABS)

            self.settingsChanged.emit()
            self.originPositionChanged.emit()
            self.rolePermissionsChanged.emit()
            self.settingsPermissionsChanged.emit()
        except Exception as e:
            print(f"[SettingsBridge] Failed to load settings: {e}")

    # --- Role & Permissions Properties ---
    @Property(str, notify=roleChanged)
    def currentRole(self):
        return self._current_role

    @Property(bool, notify=roleChanged)
    def isPrivileged(self):
        return self._is_privileged

    @Property(int, notify=inactivityTick)
    def supervisorRemainingSeconds(self):
        return self._supervisor_remaining_sec

    @Property(list, notify=rolePermissionsChanged)
    def operatorPages(self):
        return self._operator_pages

    @Property(list, notify=rolePermissionsChanged)
    def supervisorPages(self):
        return self._supervisor_pages

    @Property(list, notify=settingsPermissionsChanged)
    def operatorSettingsTabs(self):
        return self._operator_settings_tabs

    @Property(list, notify=settingsPermissionsChanged)
    def supervisorSettingsTabs(self):
        return self._supervisor_settings_tabs

    @Slot(str, str, result=bool)
    def isPageAllowed(self, role: str, page_key: str) -> bool:
        """Checks if the given page is permitted for the specified role."""
        role_lower = str(role).strip().lower()
        key_lower = str(page_key).strip().lower()
        if role_lower == "admin":
            return True
        elif role_lower == "supervisor":
            return key_lower in self._supervisor_pages
        else:  # operator
            return key_lower in self._operator_pages

    @Slot(str, str, result=bool)
    def isSettingsTabAllowed(self, role: str, tab_key: str) -> bool:
        """Checks if the given settings tab/section is permitted for the specified role."""
        role_lower = str(role).strip().lower()
        key_lower = str(tab_key).strip().lower()
        if role_lower == "admin":
            return True
        elif role_lower == "supervisor":
            return key_lower in self._supervisor_settings_tabs
        else:  # operator
            return key_lower in self._operator_settings_tabs

    @Slot(list, list)
    def saveRolePermissions(self, operator_pages: list, supervisor_pages: list):
        """Saves role-based page visibility permissions to config.ini [permissions]."""
        try:
            self._operator_pages = [str(p).strip().lower() for p in operator_pages if str(p).strip()]
            self._supervisor_pages = [str(p).strip().lower() for p in supervisor_pages if str(p).strip()]

            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("permissions", "operator_pages", ",".join(self._operator_pages))
            self._ch.addParameter("permissions", "supervisor_pages", ",".join(self._supervisor_pages))
            self._ch.updateFile(self._config_path)

            self.rolePermissionsChanged.emit()
            msg = f"Role permissions updated: Operator ({','.join(self._operator_pages)}), Supervisor ({','.join(self._supervisor_pages)})"
            print(f"[SettingsBridge] {msg}")
            self.settingsSaved.emit(msg)
        except Exception as e:
            err = f"Failed to save role permissions: {e}"
            print(f"[SettingsBridge] {err}")
            self.settingsSaved.emit(err)

    @Slot(list, list)
    def saveSettingsTabPermissions(self, operator_tabs: list, supervisor_tabs: list):
        """Saves role-based settings tab visibility permissions to config.ini [settings_permissions]."""
        try:
            self._operator_settings_tabs = [str(p).strip().lower() for p in operator_tabs if str(p).strip()]
            self._supervisor_settings_tabs = [str(p).strip().lower() for p in supervisor_tabs if str(p).strip()]

            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("settings_permissions", "operator_tabs", ",".join(self._operator_settings_tabs))
            self._ch.addParameter("settings_permissions", "supervisor_tabs", ",".join(self._supervisor_settings_tabs))
            self._ch.updateFile(self._config_path)

            self.settingsPermissionsChanged.emit()
            msg = f"Settings tab permissions updated: Operator ({','.join(self._operator_settings_tabs)}), Supervisor ({','.join(self._supervisor_settings_tabs)})"
            print(f"[SettingsBridge] {msg}")
            self.settingsSaved.emit(msg)
        except Exception as e:
            err = f"Failed to save settings tab permissions: {e}"
            print(f"[SettingsBridge] {err}")
            self.settingsSaved.emit(err)

    # --- UI Theme Properties & Slots ---
    @Property(str, notify=themeChanged)
    def theme(self):
        return self._theme

    @Property(bool, notify=themeChanged)
    def isDark(self):
        return self._theme == "dark"

    @Slot(str)
    def setTheme(self, theme_val: str):
        if theme_val in ("dark", "light") and theme_val != self._theme:
            self._theme = theme_val
            try:
                self._ch.ini_parser.read(self._config_path)
                self._ch.addParameter("ui", "theme", self._theme)
                self._ch.updateFile(self._config_path)
            except Exception as e:
                print(f"[SettingsBridge] Failed to save theme: {e}")
            self.themeChanged.emit()

    @Slot()
    def toggleTheme(self):
        self.setTheme("light" if self._theme == "dark" else "dark")

    # --- Settings Properties ---
    @Property(float, notify=settingsChanged)
    def xindex(self): return self._xindex

    @Property(float, notify=settingsChanged)
    def yindex(self): return self._yindex

    @Property(str, notify=settingsChanged)
    def indexString(self):
        return f"{self._xindex:.2f}, {self._yindex:.2f}"

    @Property(int, notify=settingsChanged)
    def jogFeed(self): return self._jog_feed

    @Property(int, notify=settingsChanged)
    def laserFeed(self): return self._laser_feed

    @Property(float, notify=settingsChanged)
    def camLaser1X(self): return self._cam_laser1_x

    @Property(float, notify=settingsChanged)
    def camLaser1Y(self): return self._cam_laser1_y

    @Property(float, notify=settingsChanged)
    def camLaser2X(self): return self._cam_laser2_x

    @Property(float, notify=settingsChanged)
    def camLaser2Y(self): return self._cam_laser2_y

    @Property(int, notify=settingsChanged)
    def camInspectionFeed(self): return self._cam_inspection_feed

    @Property(int, notify=settingsChanged)
    def camJogFeed(self): return self._cam_jog_feed

    # --- Hardware Configuration Properties ---
    @Property(int, notify=hardwareConfigChanged)
    def laserCount(self): return self._laser_count

    @Property(float, notify=hardwareConfigChanged)
    def bedWidth(self): return self._bed_width

    @Property(float, notify=hardwareConfigChanged)
    def bedHeight(self): return self._bed_height

    @Property(str, notify=hardwareConfigChanged)
    def machineName(self):
        return self._machine_name

    @Property(float, notify=hardwareConfigChanged)
    def zMaxTravel(self): return self._z_max

    @Property(bool, notify=cameraEnabledChanged)
    def cameraEnabled(self): return self._camera_enabled

    @Property(str, notify=originPositionChanged)
    def originPosition(self): return self._origin_position

    @Property(bool, notify=roleChanged)
    def isAdmin(self): return self._current_role == "Admin"

    @Property(bool, notify=roleChanged)
    def isSupervisor(self): return self._current_role == "Supervisor"

    # --- Authentication & Inactivity Slots ---
    @Slot()
    def userActivityDetected(self):
        """Called whenever user moves mouse, clicks, scrolls, or types in the UI"""
        if self._current_role in ("Supervisor", "Admin"):
            self._last_activity_time = time.time()
            if self._supervisor_remaining_sec != self._inactivity_timeout_sec:
                self._supervisor_remaining_sec = self._inactivity_timeout_sec
                self.inactivityTick.emit(self._supervisor_remaining_sec)

    def _on_inactivity_tick(self):
        if self._current_role not in ("Supervisor", "Admin"):
            self._inactivity_ticker.stop()
            self._supervisor_remaining_sec = 0
            self.inactivityTick.emit(0)
            return

        elapsed = time.time() - self._last_activity_time
        remaining = max(0, int(self._inactivity_timeout_sec - elapsed))
        self._supervisor_remaining_sec = remaining
        self.inactivityTick.emit(remaining)

        if elapsed >= self._inactivity_timeout_sec:
            expired_role = self._current_role
            print(f"[SettingsBridge] 10 minutes of UI inactivity elapsed. Auto-logging out {expired_role}.")
            self._inactivity_ticker.stop()
            self._current_role = "Operator"
            self._is_privileged = False
            self._supervisor_remaining_sec = 0
            self.inactivityTick.emit(0)
            self.roleChanged.emit()
            self.loginFailed.emit(f"{expired_role} session expired due to 10 minutes of inactivity. Reverted to Operator.")

    @Slot(str, str)
    def login(self, role: str, password: str = ""):
        """
        Validates credentials strictly:
        Operator:    012345
        Supervisor:  452301 (with 10-minute idle inactivity auto-logout)
        Admin:       SPPL@2026 (with 10-minute idle inactivity auto-logout)
        """
        role_clean = role.strip() if role else "Operator"
        pwd_clean = password.strip() if password else ""

        # Map legacy Technician role name to Admin
        if role_clean == "Technician":
            role_clean = "Admin"

        expected_pwd = self.PASSWORDS.get(role_clean)
        if not expected_pwd or pwd_clean != expected_pwd:
            print(f"[SettingsBridge] Login failed for {role_clean}: invalid password")
            self.loginFailed.emit(f"Invalid password for {role_clean}! Access denied.")
            return

        # Authenticated successfully
        self._current_role = role_clean
        if role_clean in ("Supervisor", "Admin"):
            self._is_privileged = True
            self._last_activity_time = time.time()
            self._supervisor_remaining_sec = self._inactivity_timeout_sec
            self._inactivity_ticker.start()
            self.inactivityTick.emit(self._supervisor_remaining_sec)
            self.loginSuccess.emit(f"{role_clean} authenticated ({self._inactivity_timeout_sec // 60} min idle timeout).")
        else:  # Operator
            self._is_privileged = False
            self._inactivity_ticker.stop()
            self._supervisor_remaining_sec = 0
            self.inactivityTick.emit(0)
            self.loginSuccess.emit("Operator authenticated. Standard production mode active.")

        self.roleChanged.emit()

    @Slot()
    def logout(self):
        """Logs out privileged role (Supervisor or Admin) and reverts to Operator."""
        if self._current_role == "Operator":
            return
        previous_role = self._current_role
        self._current_role = "Operator"
        self._is_privileged = False
        self._inactivity_ticker.stop()
        self._supervisor_remaining_sec = 0
        self.inactivityTick.emit(0)
        self.roleChanged.emit()
        print(f"[SettingsBridge] {previous_role} logged out. Reverted to Operator role.")

    @Slot(str)
    def saveMachineName(self, name: str):
        """Saves machine designation name directly to config.ini [hardware] machine_name."""
        try:
            name_clean = str(name).strip()
            if not name_clean:
                return
            self._machine_name = name_clean
            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("hardware", "machine_name", name_clean)
            self._ch.updateFile(self._config_path)

            self.settingsChanged.emit()
            self.hardwareConfigChanged.emit()
            msg = f"Machine designation updated to '{name_clean}' in config.ini"
            print(f"[SettingsBridge] {msg}")
            self.settingsSaved.emit(msg)
        except Exception as e:
            err = f"Failed to save machine name: {e}"
            print(f"[SettingsBridge] {err}")
            self.settingsSaved.emit(err)

    @Slot(int, float, float, float, bool, str, str)
    @Slot(int, float, float, float, bool, str)
    @Slot(int, float, float, float, bool)
    def saveHardwareConfig(self, laser_count: int, bed_w: float, bed_h: float, z_max: float, cam_enabled: bool, origin_pos: str = "top-right", machine_name: str = ""):
        """Saves hardware configuration to config.ini [hardware] section."""
        try:
            if machine_name and str(machine_name).strip():
                self._machine_name = str(machine_name).strip()
            self._laser_count = max(1, min(2, int(laser_count)))
            self._bed_width = round(float(bed_w), 1)
            self._bed_height = round(float(bed_h), 1)
            self._z_max = round(float(z_max), 1)
            self._camera_enabled = bool(cam_enabled)
            if origin_pos in ("top-right", "top-left", "bottom-left", "bottom-right"):
                self._origin_position = str(origin_pos).strip().lower()

            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("hardware", "machine_name", str(self._machine_name))
            self._ch.addParameter("hardware", "laser_count", str(self._laser_count))
            self._ch.addParameter("hardware", "bed_width", str(self._bed_width))
            self._ch.addParameter("hardware", "bed_height", str(self._bed_height))
            self._ch.addParameter("hardware", "z_max", str(self._z_max))
            self._ch.addParameter("hardware", "camera_enabled", str(self._camera_enabled))
            self._ch.addParameter("hardware", "origin_position", str(self._origin_position))
            self._ch.updateFile(self._config_path)

            self.settingsChanged.emit()
            self.hardwareConfigChanged.emit()
            self.cameraEnabledChanged.emit()
            self.originPositionChanged.emit()
            msg = f"Hardware configuration saved: '{self._machine_name}', {self._laser_count} Laser(s), Bed {self._bed_width}×{self._bed_height} mm, Z={self._z_max} mm, Camera={'ON' if self._camera_enabled else 'OFF'}, Origin={self._origin_position}"
            print(f"[SettingsBridge] {msg}")
            self.settingsSaved.emit(msg)
        except Exception as e:
            err = f"Failed to save hardware configuration: {e}"
            print(f"[SettingsBridge] {err}")
            self.settingsSaved.emit(err)

    @Slot()
    def logout(self):
        self._inactivity_ticker.stop()
        self._current_role = "Operator"
        self._is_privileged = False
        self._supervisor_remaining_sec = 0
        self.inactivityTick.emit(0)
        self.roleChanged.emit()
        self.loginSuccess.emit("Logged out. Active profile reset to Operator.")

    # --- Configuration Saving Slots ---
    @Slot(float, float)
    def saveIndex(self, xindex: float, yindex: float):
        """Saves physical print starting index point to config.ini [index]."""
        try:
            self._xindex = round(float(xindex), 3)
            self._yindex = round(float(yindex), 3)
            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("index", "xindex", str(self._xindex))
            self._ch.addParameter("index", "yindex", str(self._yindex))
            self._ch.updateFile(self._config_path)
            self.settingsChanged.emit()
            msg = f"Print starting index point saved: X={self._xindex:.2f}, Y={self._yindex:.2f} mm"
            print(f"[SettingsBridge] {msg}")
            self.settingsSaved.emit(msg)
        except Exception as e:
            err_msg = f"Error saving print index point: {e}"
            print(f"[SettingsBridge] {err_msg}")
            self.settingsSaved.emit(err_msg)

    @Slot(str, result=bool)
    def saveIndexFromString(self, text: str):
        """
        Parses X,Y format matching main.py indexLineEdit (e.g. '10, 10' or '10, 7').
        Persists to config.ini [index] xindex and yindex.
        """
        try:
            raw = text.replace(";", ",").replace("/", ",")
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            if len(parts) == 2:
                xi = float(parts[0])
                yi = float(parts[1])
                self.saveIndex(xi, yi)
                return True
            else:
                msg = "Invalid format! Enter Index as 'X, Y' (e.g. 10.0, 10.0)"
                self.settingsSaved.emit(msg)
                return False
        except Exception as e:
            msg = f"Invalid Index values: {e}"
            self.settingsSaved.emit(msg)
            return False

    @Slot(int, int)
    def saveFeeds(self, jog_feed: int, laser_feed: int):
        try:
            self._jog_feed = jog_feed
            self._laser_feed = laser_feed
            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("feed", "jog", str(jog_feed))
            self._ch.addParameter("feed", "laser", str(laser_feed))
            self._ch.updateFile(self._config_path)
            self.settingsChanged.emit()
            self.settingsSaved.emit(f"Feeds saved: Jog={jog_feed}, Laser={laser_feed} mm/min")
        except Exception as e:
            self.settingsSaved.emit(f"Error saving feeds: {e}")

    @Slot(float, float, float, float, int, int)
    def saveCameraOffsets(self, l1_x: float, l1_y: float, l2_x: float, l2_y: float, insp_feed: int, jog_feed: int):
        try:
            self._cam_laser1_x = l1_x
            self._cam_laser1_y = l1_y
            self._cam_laser2_x = l2_x
            self._cam_laser2_y = l2_y
            self._cam_inspection_feed = insp_feed
            self._cam_jog_feed = jog_feed

            self._ch.ini_parser.read(self._config_path)
            self._ch.addParameter("camera_offset", "laser1_x", str(l1_x))
            self._ch.addParameter("camera_offset", "laser1_y", str(l1_y))
            self._ch.addParameter("camera_offset", "laser2_x", str(l2_x))
            self._ch.addParameter("camera_offset", "laser2_y", str(l2_y))
            self._ch.addParameter("camera", "inspection_feed", str(insp_feed))
            self._ch.addParameter("camera", "jog_feed", str(jog_feed))
            self._ch.updateFile(self._config_path)

            self.settingsChanged.emit()
            self.settingsSaved.emit("Camera offsets and speeds saved successfully")
        except Exception as e:
            self.settingsSaved.emit(f"Error saving camera settings: {e}")
