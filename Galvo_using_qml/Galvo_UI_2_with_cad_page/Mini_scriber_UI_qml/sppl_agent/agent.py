import requests
import uuid
import platform
import os
import json
import threading
from pathlib import Path
from .telemetry import TelemetryManager
from .updater import UpdateManager

class SPPLAgent:
    def __init__(self, api_url: str, project_id: str, client_id: str, app_version: str):
        self.api_url = api_url.rstrip('/')
        self.project_id = project_id
        self.client_id = client_id
        self.app_version = app_version
        self.device_id = self._get_or_create_device_id()
        
        # Initialize sub-modules
        self.telemetry = TelemetryManager(self)
        self.updater = UpdateManager(self)

    def _get_or_create_device_id(self) -> str:
        """Retrieves an existing device ID from local storage or generates a new one. Also persists client_id."""
        config_dir = Path(os.getenv('APPDATA', '~/')) / 'SPPL' / self.project_id
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / 'device.json'
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    
                # If a client ID was previously saved, use it to survive generic updates
                saved_client_id = data.get('client_id')
                if saved_client_id and self.client_id == "demo_client_456":
                    self.client_id = saved_client_id
                    
                device_id = data.get('device_id')
                if device_id:
                    # Update saved config with latest client_id if we have a custom one
                    if self.client_id != "demo_client_456" and saved_client_id != self.client_id:
                        data['client_id'] = self.client_id
                        with open(config_path, 'w') as f:
                            json.dump(data, f)
                    return device_id
            except Exception:
                pass
                
        # Generate new ID based on hardware/UUID
        new_id = f"{self.project_id[:3].upper()}-{str(uuid.uuid4())[:8].upper()}"
        with open(config_path, 'w') as f:
            json.dump({'device_id': new_id, 'client_id': self.client_id}, f)
        return new_id

    def register_device(self):
        """Registers the device with the SPPL backend."""
        payload = {
            "deviceId": self.device_id,
            "clientId": self.client_id,
            "projectId": self.project_id,
            "computerName": platform.node(),
            "os": platform.system(),
            "osRelease": platform.release(),
            "version": self.app_version
        }
        
        try:
            resp = requests.post(f"{self.api_url}/api/devices/register", json=payload, timeout=45)
            resp.raise_for_status()
            print(f"[SPPL Agent] Device {self.device_id} registered successfully.")
        except Exception as e:
            print(f"[SPPL Agent] Registration failed: {e}")

    def start(self):
        """Starts all background tasks (Heartbeat, Global Exception hooking)."""
        # Run registration in background thread so it doesn't block UI while Render wakes up
        threading.Thread(target=self.register_device, daemon=True).start()
        self.telemetry.hook_exceptions()
        self.telemetry.start_heartbeat()

    def upload_log(self, file_path: str):
        """Uploads a log file to the SPPL backend."""
        path = Path(file_path)
        if not path.exists():
            print(f"[SPPL Agent] Log file not found: {file_path}")
            return False
            
        try:
            with open(path, 'rb') as f:
                files = {'file': (path.name, f, 'text/plain')}
                resp = requests.post(
                    f"{self.api_url}/api/devices/{self.device_id}/logs",
                    files=files
                )
                resp.raise_for_status()
                print(f"[SPPL Agent] Log file {path.name} uploaded successfully.")
                return True
        except Exception as e:
            print(f"[SPPL Agent] Log upload failed: {e}")
            return False
