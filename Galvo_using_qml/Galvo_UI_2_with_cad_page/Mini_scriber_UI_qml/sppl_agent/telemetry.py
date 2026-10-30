import threading
import time
import requests
import sys
import traceback
import os

class TelemetryManager:
    def __init__(self, agent):
        self.agent = agent
        self.heartbeat_thread = None
        self.running = False

    def hook_exceptions(self):
        """Captures unhandled exceptions globally and sends them to backend."""
        original_excepthook = sys.excepthook

        def custom_excepthook(exc_type, exc_value, exc_traceback):
            stack_trace = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.report_error(str(exc_type.__name__), str(exc_value), stack_trace)
            # Call original
            original_excepthook(exc_type, exc_value, exc_traceback)

        sys.excepthook = custom_excepthook
        print("[SPPL Agent] Global exception hook installed.")

    def report_error(self, error_type: str, error_message: str, stack_trace: str):
        payload = {
            "deviceId": self.agent.device_id,
            "errorType": error_type,
            "errorMessage": error_message,
            "stackTrace": stack_trace,
            "version": self.agent.app_version
        }
        try:
            requests.post(f"{self.agent.api_url}/api/errors", json=payload)
        except Exception:
            pass # Fail silently on crash reports

    def start_heartbeat(self, interval_seconds=300):
        if self.running:
            return
            
        self.running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, 
            args=(interval_seconds,), 
            daemon=True
        )
        self.heartbeat_thread.start()
        print(f"[SPPL Agent] Heartbeat started (interval: {interval_seconds}s).")

    def _heartbeat_loop(self, interval):
        while self.running:
            payload = {
                "deviceId": self.agent.device_id,
                "version": self.agent.app_version
            }
            try:
                requests.post(f"{self.agent.api_url}/api/devices/heartbeat", json=payload)
                self.upload_logs()
            except Exception:
                pass # Fail silently if network is down
            time.sleep(interval)

    def upload_logs(self):
        log_files = ["app.log", "terminal_logs.txt", os.path.join("error_logs", "app_error.log")]
        url = f"{self.agent.api_url}/api/devices/{self.agent.device_id}/logs"
        
        for log_file in log_files:
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                try:
                    with open(log_file, "rb") as f:
                        files = {"file": (os.path.basename(log_file), f, "text/plain")}
                        # Increased timeout to 60s because large logs get truncated on slow networks
                        requests.post(url, files=files, timeout=60)
                except Exception:
                    pass # Fail silently if log upload fails
