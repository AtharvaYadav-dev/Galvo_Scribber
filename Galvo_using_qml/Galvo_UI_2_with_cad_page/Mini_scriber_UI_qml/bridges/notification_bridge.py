import time
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property

class NotificationBridge(QObject):
    """
    Centralized Notification & Machine Audit Engine for Mini Scriber 2.0.
    Maintains a reactive, bounded queue of system, job, motion, laser,
    and security events with read/unread tracking and actionable view routing.
    """
    notificationsChanged = Signal()
    unreadCountChanged = Signal()
    notificationAdded = Signal(dict)
    requestNavigate = Signal(str)

    MAX_HISTORY = 80

    def __init__(self, serial_bridge=None, motion_bridge=None, laser_bridge=None,
                 job_bridge=None, settings_bridge=None, parent=None):
        super().__init__(parent)
        self._serial = serial_bridge
        self._motion = motion_bridge
        self._laser = laser_bridge
        self._job = job_bridge
        self._settings = settings_bridge

        self._notifications = []
        self._id_counter = 1

        # Register listeners to automatic machine signals
        self._bind_signals()

        # Seed welcome & initial system notifications
        app_name = self._settings.machineName if (self._settings and hasattr(self._settings, "machineName")) else "Mini Scriber"
        self.addNotification(
            title="System Initialized",
            message=f"{app_name} 2.0 engine started. Ready for laser processing.",
            level="success",
            target_view="motion",
            category="system"
        )

    def _bind_signals(self):
        # 1. Serial Bridge Events
        if self._serial:
            self._serial.connectedChanged.connect(self._on_serial_connected_changed)
            self._serial.errorOccurred.connect(self._on_serial_error)
            self._serial.autoConnectFailed.connect(self._on_auto_connect_failed)

        # 2. Job Bridge Events
        if self._job:
            self._job.fileLoaded.connect(self._on_job_file_loaded)
            self._job.jobStateChanged.connect(self._on_job_state_changed)
            self._job.boundaryWarning.connect(self._on_job_boundary_warning)

        # 3. Settings Bridge Events
        if self._settings:
            self._settings.loginSuccess.connect(self._on_login_success)
            self._settings.loginFailed.connect(self._on_login_failed)
            self._settings.settingsSaved.connect(self._on_settings_saved)
            self._settings.hardwareConfigChanged.connect(self._on_hardware_config_changed)

        # 4. Motion Bridge Events
        if self._motion:
            self._motion.safetyAlert.connect(self._on_motion_safety_alert)

        # 5. Laser Bridge Events
        if self._laser:
            self._laser.statusAlert.connect(self._on_laser_status_alert)

    # -------------------------------------------------------------------------
    # Signal Handlers
    # -------------------------------------------------------------------------
    def _on_serial_connected_changed(self, connected: bool):
        if connected:
            port = self._serial.selectedPort if hasattr(self._serial, "selectedPort") else "COM"
            baud = self._serial.selectedBaud if hasattr(self._serial, "selectedBaud") else "115200"
            self.addNotification(
                title="Controller Online",
                message=f"Connected to CNC controller on {port} at {baud} baud.",
                level="success",
                target_view="settings",
                category="machine"
            )
        else:
            self.addNotification(
                title="Controller Offline",
                message="Communication link with CNC microcontroller closed.",
                level="warning",
                target_view="settings",
                category="machine"
            )

    def _on_serial_error(self, err_msg: str):
        self.addNotification(
            title="Communication Error",
            message=err_msg,
            level="error",
            target_view="settings",
            category="machine"
        )

    def _on_auto_connect_failed(self, msg: str):
        self.addNotification(
            title="Auto-Connect Failed",
            message=msg,
            level="warning",
            target_view="settings",
            category="machine"
        )

    def _on_job_file_loaded(self):
        fname = self._job.fileName if hasattr(self._job, "fileName") else "design"
        self.addNotification(
            title="Design File Loaded",
            message=f"Successfully loaded '{fname}'. Preview & toolpaths ready.",
            level="info",
            target_view="job",
            category="job"
        )

    def _on_job_state_changed(self, state: str):
        if state == "Running":
            self.addNotification(
                title="Laser Scribing Active",
                message="Job execution started. Laser is firing along designated paths.",
                level="info",
                target_view="job",
                category="job"
            )
        elif state == "Complete":
            self.addNotification(
                title="Job Completed Successfully",
                message="All trajectories engraved. Laser powered off.",
                level="success",
                target_view="job",
                category="job"
            )
        elif state == "Paused":
            self.addNotification(
                title="Job Paused",
                message="Laser motion paused by operator.",
                level="warning",
                target_view="job",
                category="job"
            )
        elif state == "Aborted":
            self.addNotification(
                title="Job Aborted",
                message="Laser processing halted. Retracted to safety position.",
                level="error",
                target_view="job",
                category="job"
            )

    def _on_job_boundary_warning(self, title: str, message: str, can_shift: bool, width: float, height: float):
        level = "error" if "Too Large" in title else "warning"
        self.addNotification(
            title=title,
            message=message,
            level=level,
            target_view="job",
            category="job"
        )

    def _on_login_success(self, role: str):
        self.addNotification(
            title="Security Profile Changed",
            message=f"Authenticated as '{role}'. Permissions unlocked.",
            level="info",
            target_view="settings",
            category="security"
        )

    def _on_login_failed(self, reason: str):
        self.addNotification(
            title="Access Denied",
            message=f"Authentication rejected: {reason}",
            level="warning",
            target_view="settings",
            category="security"
        )

    def _on_settings_saved(self, msg: str):
        self.addNotification(
            title="Configuration Saved",
            message=msg,
            level="success",
            target_view="settings",
            category="system"
        )

    def _on_hardware_config_changed(self):
        if self._settings:
            w = self._settings.bedWidth
            h = self._settings.bedHeight
            origin = self._settings.originPosition
            self.addNotification(
                title="Hardware Configuration Updated",
                message=f"Workbed envelope: {w:.0f}×{h:.0f} mm · Origin datum: {origin.upper()}.",
                level="info",
                target_view="hardware",
                category="machine"
            )

    def _on_motion_safety_alert(self, msg: str):
        self.addNotification(
            title="Motion Safety Alert",
            message=msg,
            level="warning",
            target_view="motion",
            category="machine"
        )

    def _on_laser_status_alert(self, msg: str):
        self.addNotification(
            title="Laser System Alert",
            message=msg,
            level="info",
            target_view="laser",
            category="machine"
        )

    # -------------------------------------------------------------------------
    # Core API & Slots
    # -------------------------------------------------------------------------
    def _format_time_ago(self, created_at: float) -> str:
        diff = time.time() - created_at
        if diff < 10:
            return "Just now"
        elif diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff // 60)}m ago"
        elif diff < 86400:
            return f"{int(diff // 3600)}h ago"
        else:
            return f"{int(diff // 86400)}d ago"

    @Slot(str, str, str, str, str)
    def addNotification(self, title: str, message: str, level: str = "info",
                        target_view: str = "", category: str = "system"):
        """Adds a new notification to the top of the queue."""
        now = datetime.now()
        timestamp_str = now.strftime("%I:%M:%S %p").lstrip("0")
        created_time = time.time()

        item = {
            "id": self._id_counter,
            "title": str(title),
            "message": str(message),
            "level": str(level).lower(),      # "info", "success", "warning", "error"
            "category": str(category).lower(),# "machine", "job", "security", "system"
            "timestamp": timestamp_str,
            "time_ago": "Just now",
            "created_at": created_time,
            "read": False,
            "target_view": str(target_view).lower() # "motion", "laser", "job", "camera", "terminal", "hardware", "settings"
        }
        self._id_counter += 1

        self._notifications.insert(0, item)
        if len(self._notifications) > self.MAX_HISTORY:
            self._notifications = self._notifications[:self.MAX_HISTORY]

        self.notificationsChanged.emit()
        self.unreadCountChanged.emit()
        self.notificationAdded.emit(item)

    @Slot(int)
    def markAsRead(self, notif_id: int):
        """Marks a specific notification as read."""
        changed = False
        for n in self._notifications:
            if n["id"] == notif_id and not n["read"]:
                n["read"] = True
                changed = True
                break
        if changed:
            self.notificationsChanged.emit()
            self.unreadCountChanged.emit()

    @Slot()
    def markAllAsRead(self):
        """Marks all notifications in the queue as read."""
        changed = False
        for n in self._notifications:
            if not n["read"]:
                n["read"] = True
                changed = True
        if changed:
            self.notificationsChanged.emit()
            self.unreadCountChanged.emit()

    @Slot(int)
    def dismiss(self, notif_id: int):
        """Removes a single notification from history."""
        self._notifications = [n for n in self._notifications if n["id"] != notif_id]
        self.notificationsChanged.emit()
        self.unreadCountChanged.emit()

    @Slot()
    def clearAll(self):
        """Clears all notifications."""
        if self._notifications:
            self._notifications = []
            self.notificationsChanged.emit()
            self.unreadCountChanged.emit()

    @Slot(str)
    def navigateTo(self, target_view: str):
        """Requests navigation to a specific view from notification actions."""
        if target_view:
            self.requestNavigate.emit(str(target_view).lower())

    # -------------------------------------------------------------------------
    # Properties for QML
    # -------------------------------------------------------------------------
    @Property("QVariantList", notify=notificationsChanged)
    def list(self):
        # Dynamically refresh time_ago string before exposing to QML
        for n in self._notifications:
            n["time_ago"] = self._format_time_ago(n["created_at"])
        return list(self._notifications)

    @Property(int, notify=unreadCountChanged)
    def unreadCount(self):
        return sum(1 for n in self._notifications if not n["read"])

    @Property(bool, notify=unreadCountChanged)
    def hasUnread(self):
        return any(not n["read"] for n in self._notifications)
