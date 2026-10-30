import os
import sys
import json
import time
import tempfile
import threading
import subprocess
import requests
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property, QCoreApplication

import version
from sppl_agent import SPPLAgent

def parse_version_tuple(v_str: str) -> tuple:
    """Parses a version string like 'v1.1.3' into a tuple of integers (1, 1, 3) for semver comparison."""
    if not v_str:
        return (0, 0, 0)
    cleaned = str(v_str).strip().lstrip("v").strip()
    parts = []
    for part in cleaned.split("."):
        digits = "".join(filter(str.isdigit, part))
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

class UpdaterBridge(QObject):
    """
    Reactive Software Updater Bridge for Mini Scriber 2.0.
    Manages non-blocking version checking, release notes parsing,
    chunk-streaming download progress, and silent Inno Setup installation.
    """
    statusChanged = Signal()
    progressChanged = Signal()
    updateCheckComplete = Signal(bool, str, str) # available, version, releaseNotes
    readyToInstall = Signal()
    updateError = Signal(str)

    def __init__(self, laser_bridge=None, camera_bridge=None, notification_bridge=None, parent=None):
        super().__init__(parent)
        self._laser = laser_bridge
        self._camera = camera_bridge
        self._notifications = notification_bridge

        self._current_version = version.VERSION
        self._latest_version = version.VERSION
        self._download_url = ""
        self._release_notes = ""
        self._is_checking = False
        self._update_available = False
        self._is_downloading = False
        self._download_progress = 0.0
        self._downloaded_mb = 0.0
        self._total_mb = 0.0
        self._speed_text = ""
        self._eta_text = ""
        self._status_message = f"Current version: v{self._current_version}"
        self._last_checked_time = "Not checked yet"
        self._download_cancel_event = None
        self._installer_path = ""

        # Initialize SPPL Agent
        self._init_sppl_agent()

    def _init_sppl_agent(self):
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(app_dir, "sppl_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cfg = json.load(f)
            else:
                cfg = {
                    "api_url": "https://sppl-server.onrender.com",
                    "project_id": "mini_scriber_proj_001",
                    "client_id": "demo_client_123"
                }

            self._agent = SPPLAgent(
                api_url=cfg.get("api_url", "https://sppl-server.onrender.com"),
                project_id=cfg.get("project_id", "mini_scriber_proj_001"),
                client_id=cfg.get("client_id", "demo_client_123"),
                app_version=self._current_version
            )
        except Exception as e:
            print(f"[UpdaterBridge] Notice: Could not init SPPLAgent: {e}")
            self._agent = None

    # -------------------------------------------------------------------------
    # Asynchronous Check for Updates
    # -------------------------------------------------------------------------
    @Slot()
    @Slot(bool)
    def checkForUpdates(self, silent=False):
        """Asynchronously checks for software updates without blocking the UI."""
        if self._is_checking or self._is_downloading:
            return

        self._is_checking = True
        self._status_message = "Checking for updates..."
        self.statusChanged.emit()

        def worker():
            update_info = None
            err_msg = ""
            try:
                if self._agent and hasattr(self._agent, "updater"):
                    update_info = self._agent.updater.check_for_updates(auto_install=False)
                else:
                    # Direct GitHub Releases API Fallback
                    gh_url = "https://api.github.com/repos/ruthrane25/Mini_Scriber/releases/latest"
                    headers = {"Accept": "application/vnd.github+json"}
                    r = requests.get(gh_url, headers=headers, timeout=6)
                    if r.status_code == 200:
                        rel = r.json()
                        ver = rel.get("tag_name", "").lstrip("v")
                        dl_url = ""
                        for asset in rel.get("assets", []):
                            if asset.get("name", "").endswith(".exe"):
                                dl_url = asset.get("browser_download_url", "")
                                break
                        update_info = {
                            "version": ver,
                            "downloadUrl": dl_url,
                            "releaseNotes": rel.get("body", "")
                        }
            except Exception as e:
                err_msg = str(e)

            # Process result back in main thread
            self._on_check_complete(update_info, err_msg, silent)

        threading.Thread(target=worker, daemon=True).start()

    def _on_check_complete(self, update_info, err_msg, silent):
        self._is_checking = False
        now_str = datetime.now().strftime("%I:%M %p").lstrip("0")
        self._last_checked_time = f"Today at {now_str}"

        if err_msg:
            self._status_message = f"Check failed: {err_msg}"
            self.statusChanged.emit()
            self.updateError.emit(err_msg)
            return

        if update_info and update_info.get("version"):
            latest = str(update_info.get("version")).lstrip("v")
            self._latest_version = latest
            self._download_url = update_info.get("downloadUrl", "")
            self._release_notes = update_info.get("releaseNotes", "")

            # Strict Semantic Version Comparison: Only notify if remote release is strictly newer
            current_tuple = parse_version_tuple(self._current_version)
            latest_tuple = parse_version_tuple(latest)
            is_newer = (latest_tuple > current_tuple and not update_info.get("upToDate", False))

            if is_newer:
                self._update_available = True
                self._status_message = f"Update available: v{latest}"
                self.statusChanged.emit()
                self.updateCheckComplete.emit(True, latest, self._release_notes)

                # Push to notification bell
                if self._notifications:
                    self._notifications.addNotification(
                        title=f"Software Update Available (v{latest})",
                        message=f"New Mini Scriber release v{latest} is ready. Click to review changelog & install.",
                        level="info",
                        target_view="settings",
                        category="system"
                    )
            else:
                self._update_available = False
                if current_tuple > latest_tuple:
                    self._status_message = f"You are running a newer development build (v{self._current_version} > v{latest})."
                else:
                    self._status_message = f"You are on the latest version (v{self._current_version})."
                self.statusChanged.emit()
                self.updateCheckComplete.emit(False, self._current_version, "")
        else:
            self._update_available = False
            self._status_message = f"Up to date (v{self._current_version})."
            self.statusChanged.emit()
            self.updateCheckComplete.emit(False, self._current_version, "")

    # -------------------------------------------------------------------------
    # Asynchronous Download of Installer
    # -------------------------------------------------------------------------
    @Slot()
    def startDownload(self):
        """Streams installer .exe download with chunk progress, high-speed buffer, and cancel support."""
        if self._is_downloading or not self._download_url:
            return

        self._is_downloading = True
        self._download_progress = 0.0
        self._downloaded_mb = 0.0
        self._total_mb = 0.0
        self._speed_text = ""
        self._eta_text = ""
        self._status_message = f"Downloading update v{self._latest_version}..."
        self._download_cancel_event = threading.Event()
        self.statusChanged.emit()
        self.progressChanged.emit()

        def worker():
            try:
                download_url = self._download_url
                if download_url.startswith("/api/") and self._agent:
                    download_url = f"{self._agent.api_url}{download_url}"

                target_filename = f"Mini_Scriber_update_{self._latest_version}.exe"
                installer_path = os.path.join(tempfile.gettempdir(), target_filename)

                # High performance session with identity encoding (no gzip overhead on binary)
                session = requests.Session()
                headers = {
                    "User-Agent": f"MiniScriber/{self._current_version}",
                    "Accept-Encoding": "identity"
                }

                with session.get(download_url, headers=headers, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total_bytes = int(r.headers.get("content-length", 0))
                    self._total_mb = round(total_bytes / (1024 * 1024), 2)
                    downloaded_bytes = 0

                    start_time = time.monotonic()
                    last_time = start_time
                    last_bytes = 0
                    last_emit_time = start_time

                    # 512 KB chunk buffer for maximum broadband network throughput
                    CHUNK_SIZE = 512 * 1024

                    with open(installer_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                            if self._download_cancel_event and self._download_cancel_event.is_set():
                                self._on_download_cancelled()
                                return

                            if chunk:
                                f.write(chunk)
                                downloaded_bytes += len(chunk)

                                now = time.monotonic()
                                # Throttle GUI signal emissions to every 150ms to prevent Qt event queue congestion
                                if (now - last_emit_time >= 0.15) or (total_bytes > 0 and downloaded_bytes >= total_bytes):
                                    time_diff = now - last_time
                                    if time_diff > 0.3:
                                        bytes_diff = downloaded_bytes - last_bytes
                                        speed_bps = bytes_diff / time_diff
                                        speed_mbps = speed_bps / (1024 * 1024)
                                        self._speed_text = f"{speed_mbps:.1f} MB/s"
                                        if speed_bps > 0 and total_bytes > downloaded_bytes:
                                            rem_sec = int((total_bytes - downloaded_bytes) / speed_bps)
                                            if rem_sec < 60:
                                                self._eta_text = f"{rem_sec}s left"
                                            else:
                                                self._eta_text = f"{rem_sec // 60}m {rem_sec % 60}s left"
                                        last_time = now
                                        last_bytes = downloaded_bytes

                                    self._downloaded_mb = round(downloaded_bytes / (1024 * 1024), 2)
                                    if total_bytes > 0:
                                        self._download_progress = min(99.9, round((downloaded_bytes / total_bytes) * 100.0, 1))

                                    last_emit_time = now
                                    self.progressChanged.emit()

                self._installer_path = installer_path
                self._on_download_complete()

            except Exception as e:
                self._on_download_error(str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_download_cancelled(self):
        self._is_downloading = False
        self._download_progress = 0.0
        self._speed_text = ""
        self._eta_text = ""
        self._status_message = "Download cancelled by operator."
        self.statusChanged.emit()
        self.progressChanged.emit()

    def _on_download_error(self, err_msg):
        self._is_downloading = False
        self._speed_text = ""
        self._eta_text = ""
        self._status_message = f"Download failed: {err_msg}"
        self.statusChanged.emit()
        self.progressChanged.emit()
        self.updateError.emit(err_msg)

    def _on_download_complete(self):
        self._is_downloading = False
        self._download_progress = 100.0
        self._speed_text = ""
        self._eta_text = ""
        self._status_message = f"Update v{self._latest_version} ready to install."
        self.statusChanged.emit()
        self.progressChanged.emit()
        self.readyToInstall.emit()

        # Push notification to the top header bell so the operator is notified even if they minimized the modal!
        if self._notifications:
            self._notifications.addNotification(
                title=f"Update Ready (v{self._latest_version})",
                message=f"Mini Scriber v{self._latest_version} finished downloading in background. Click to review & install.",
                level="success",
                target_view="update",
                category="system"
            )

    @Slot()
    def cancelDownload(self):
        """Aborts active download."""
        if self._download_cancel_event:
            self._download_cancel_event.set()

    # -------------------------------------------------------------------------
    # Safe Installation & Application Restart
    # -------------------------------------------------------------------------
    @Slot()
    def installAndRestart(self):
        """Safely shuts down laser and camera, executes installer silently, and restarts."""
        try:
            print("[UpdaterBridge] Executing safety shutdown before update...")
            # 1. Safety shut down laser
            if self._laser and hasattr(self._laser, "shutdownLaser"):
                self._laser.shutdownLaser()

            # 2. Stop camera stream
            if self._camera and hasattr(self._camera, "stopCamera"):
                self._camera.stopCamera()

            # 3. Launch Inno Setup installer detached so it is fully decoupled
            if os.path.exists(self._installer_path):
                print(f"[UpdaterBridge] Launching installer: {self._installer_path}")
                creation_flags = 0x00000008 if sys.platform == "win32" else 0  # DETACHED_PROCESS
                subprocess.Popen(
                    [
                        self._installer_path,
                        "/SILENT",
                        "/SUPPRESSMSGBOXES",
                        "/NORESTART"
                    ],
                    creationflags=creation_flags,
                    close_fds=True
                )

            # 4. Terminate process cleanly and immediately at OS kernel level.
            # This instantly releases all file locks on Mini_Scriber.exe and loaded DLLs,
            # preventing Inno Setup from stalling or waiting, and completely eliminating
            # the Windows "Not Responding" freeze dialog.
            print("[UpdaterBridge] Exiting Mini Scriber to allow installer to proceed...")
            os._exit(0)

        except Exception as e:
            print(f"[UpdaterBridge] Error launching installer: {e}")
            self.updateError.emit(str(e))

    # -------------------------------------------------------------------------
    # Properties for QML
    # -------------------------------------------------------------------------
    @Property(str, notify=statusChanged)
    def currentVersion(self):
        return self._current_version

    @Property(str, notify=statusChanged)
    def latestVersion(self):
        return self._latest_version

    @Property(bool, notify=statusChanged)
    def isChecking(self):
        return self._is_checking

    @Property(bool, notify=statusChanged)
    def updateAvailable(self):
        return self._update_available

    @Property(bool, notify=statusChanged)
    def isDownloading(self):
        return self._is_downloading

    @Property(float, notify=progressChanged)
    def downloadProgress(self):
        return self._download_progress

    @Property(float, notify=progressChanged)
    def downloadedMb(self):
        return self._downloaded_mb

    @Property(float, notify=progressChanged)
    def totalMb(self):
        return self._total_mb

    @Property(str, notify=statusChanged)
    def releaseNotes(self):
        return self._release_notes

    @Property(str, notify=statusChanged)
    def statusMessage(self):
        return self._status_message

    @Property(str, notify=statusChanged)
    def lastCheckedTime(self):
        return self._last_checked_time

    @Property(str, notify=progressChanged)
    def speedText(self):
        return self._speed_text

    @Property(str, notify=progressChanged)
    def etaText(self):
        return self._eta_text
