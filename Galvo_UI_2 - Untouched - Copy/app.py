import os
import sys
import time
import socket
import argparse
import threading
import subprocess
import mimetypes
import http.server
import urllib.request
import urllib.error
import webview
from bridge import GalvoHardwareBridge

# Explicitly guarantee MIME types for Windows environments
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("application/json", ".json")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
FRONTEND_INDEX = os.path.join(FRONTEND_DIST, "index.html")


def find_free_port(start_port: int = 5174) -> int:
    """Finds an available local port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port


def is_server_alive(url: str, timeout: float = 1.0) -> bool:
    """Checks if a URL is responding with HTTP 200/304."""
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        return req.status in (200, 304)
    except Exception:
        return False


class QuietStaticServer(http.server.SimpleHTTPRequestHandler):
    """Zero-log static file server with explicit MIME and CORS headers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIST, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # Suppress console clutter


def start_local_static_server(port: int) -> http.server.ThreadingHTTPServer:
    """Spins up a lightweight local server to deliver frontend assets cleanly to WebView2."""
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), QuietStaticServer)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def build_frontend_if_needed():
    """Builds frontend production bundle if missing."""
    if not os.path.exists(FRONTEND_INDEX):
        print("[App] Production bundle not found. Building frontend with Vite...")
        try:
            subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, shell=True, check=True)
            print("[App] Frontend build completed successfully.")
        except Exception as e:
            print(f"[App] Frontend build failed: {e}")


def launch_vite_dev_server() -> subprocess.Popen:
    """Spawns Vite development server in background writing to log file to avoid pipe buffer deadlocks."""
    print("[App] Launching Vite development server...")
    log_path = os.path.join(BASE_DIR, "vite_dev.log")
    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    # Wait up to 6 seconds for Vite to bind
    for _ in range(30):
        time.sleep(0.2)
        if is_server_alive("http://127.0.0.1:5173"):
            print("[App] Vite dev server is online at http://127.0.0.1:5173")
            break
    return proc


def main():
    parser = argparse.ArgumentParser(description="Galvo Laser Studio Pro")
    parser.add_argument("--dev", action="store_true", help="Run with Vite Dev Server & HMR")
    parser.add_argument("--prod", action="store_true", help="Run with local production bundle")
    parser.add_argument("--port", type=int, default=0, help="Custom server port")
    args = parser.parse_args()

    bridge = GalvoHardwareBridge()
    dev_process = None
    http_server = None

    if args.dev:
        # Development Mode
        dev_url = "http://127.0.0.1:5173"
        if not is_server_alive(dev_url):
            dev_process = launch_vite_dev_server()
        if is_server_alive(dev_url):
            target_url = dev_url
            print(f"[App] Mode: DEVELOPMENT (HMR) -> {target_url}")
        else:
            print("[App] Vite dev server not responding. Falling back seamlessly to local production engine.")
            build_frontend_if_needed()
            prod_port = args.port if args.port > 0 else find_free_port(5174)
            http_server = start_local_static_server(prod_port)
            target_url = f"http://127.0.0.1:{prod_port}"
            print(f"[App] Mode: PRODUCTION (Local Engine) -> {target_url}")
    else:
        # Production Mode (Default & Recommended)
        build_frontend_if_needed()
        prod_port = args.port if args.port > 0 else find_free_port(5174)
        http_server = start_local_static_server(prod_port)
        target_url = f"http://127.0.0.1:{prod_port}"
        print(f"[App] Mode: PRODUCTION (Local Engine) -> {target_url}")

    # Create Native Desktop Window
    # NOTE: easy_drag must be False so Canvas dragging/panning works properly!
    window = webview.create_window(
        title="Galvo Laser Studio Pro // Industrial Laser Controller",
        url=target_url,
        js_api=bridge,
        width=1440,
        height=900,
        min_size=(1280, 800),
        background_color="#09090b",
        text_select=True,
        easy_drag=False
    )

    def on_closing():
        print("[App] Window closing. Executing safety beam shutdown...")
        try:
            bridge.emergency_stop()
            bridge.disconnect_device()
        except Exception as e:
            print(f"[App] Error during shutdown: {e}")

        if http_server:
            try:
                http_server.shutdown()
                http_server.server_close()
            except Exception:
                pass

        if dev_process:
            try:
                dev_process.terminate()
            except Exception:
                pass

    window.events.closing += on_closing
    window.events.closed += on_closing

    print("[App] Launching native window...")
    try:
        webview.start(debug=args.dev)
    except Exception as e:
        print(f"[App] Webview exited: {e}")


if __name__ == "__main__":
    main()
