import requests
import os
import subprocess
import tempfile
import threading
import sys

class UpdateManager:
    def __init__(self, agent):
        self.agent = agent
        
    def check_for_updates(self, auto_install=True):
        """Queries the backend for the latest release, with direct fallback to GitHub API."""
        print("[SPPL Agent] Checking for updates...")
        data = None
        
        # 1. Try SPPL Backend API (with a 3-second timeout)
        try:
            url = f"{self.agent.api_url}/api/updates/latest?projectId={self.agent.project_id}"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
        except Exception as e:
            print(f"[SPPL Agent] SPPL Server check failed/unreachable ({e}). Falling back to GitHub API directly...")

        # 2. Fallback to direct GitHub API if backend check failed or returned nothing
        if not data or not data.get("version"):
            try:
                gh_url = "https://api.github.com/repos/ruthrane25/Mini_Scriber/releases/latest"
                headers = {"Accept": "application/vnd.github+json"}
                gh_resp = requests.get(gh_url, headers=headers, timeout=5)
                if gh_resp.status_code == 200:
                    rel = gh_resp.json()
                    ver = rel.get("tag_name", "").lstrip("v")
                    dl_url = ""
                    for asset in rel.get("assets", []):
                        if asset.get("name", "").endswith(".exe"):
                            dl_url = asset.get("browser_download_url", "")
                            break
                    if ver and dl_url:
                        data = {
                            "version": ver,
                            "downloadUrl": dl_url,
                            "releaseNotes": rel.get("body", "")
                        }
                    else:
                        print(f"[SPPL Agent] GitHub Release found ({ver}), but no .exe asset found.")
            except Exception as gh_e:
                print(f"[SPPL Agent] Direct GitHub API check failed: {gh_e}")

        # 3. Process update result
        if data and data.get("version"):
            latest_version = data.get("version")
            download_url = data.get("downloadUrl")
            
            def _parse_version(v_str):
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

            if _parse_version(latest_version) > _parse_version(self.agent.app_version):
                print(f"[SPPL Agent] Update available: v{latest_version} (Current: v{self.agent.app_version})")
                if auto_install and download_url:
                    threading.Thread(target=self._download_and_install, args=(latest_version, download_url), daemon=True).start()
                return data
            else:
                print(f"[SPPL Agent] You are on the latest version or a newer dev build (v{self.agent.app_version} >= v{latest_version}).")
                return {"version": latest_version, "upToDate": True}
        else:
            print("[SPPL Agent] Unable to fetch update information.")
            
        return None
        
    def _report_status(self, version: str, status: str, error_msg: str = None):
        payload = {
            "deviceId": self.agent.device_id,
            "projectId": self.agent.project_id,
            "version": version,
            "status": status,
            "errorMessage": error_msg
        }
        try:
            requests.post(f"{self.agent.api_url}/api/updates/status", json=payload, timeout=3)
        except Exception:
            pass

    def _download_and_install(self, version: str, download_url: str, progress_callback=None, cancel_event=None):
        try:
            print(f"[SPPL Agent] Downloading update v{version}...")
            # If the download URL is a relative path to our backend, construct the full URL
            if download_url.startswith("/api/"):
                download_url = f"{self.agent.api_url}{download_url}"
                
            installer_path = os.path.join(tempfile.gettempdir(), f"Mini_Scriber_update_{version}.exe")
            
            # Streaming download
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(installer_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if cancel_event and cancel_event.is_set():
                            print("[SPPL Agent] Download cancelled by user.")
                            return
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                progress_callback(progress)
                        
            print("[SPPL Agent] Download complete.")
            self._report_status(version, "Downloaded")
            
            # Execute Inno Setup installer silently
            print("[SPPL Agent] Launching installer and exiting current process...")
            subprocess.Popen([installer_path, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART"])
            
            # The installer is running; exit current app so files can be overwritten
            sys.exit(0)
            
        except Exception as e:
            print(f"[SPPL Agent] Update failed: {e}")
            self._report_status(version, "Failed", str(e))
