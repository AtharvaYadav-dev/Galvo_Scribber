import os
import configparser

def _load_app_name():
    ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.ini")
    if os.path.exists(ini_path):
        try:
            cfg = configparser.ConfigParser()
            cfg.read(ini_path, encoding="utf-8")
            if cfg.has_option("hardware", "machine_name"):
                name = cfg.get("hardware", "machine_name").strip()
                if name:
                    return name
            if cfg.has_option("main", "machine_name"):
                name = cfg.get("main", "machine_name").strip()
                if name:
                    return name
        except Exception:
            pass
    return "Mini Scriber"

APP_NAME = _load_app_name()
COMPANY = "Spécialisé Products Private Limited"
VERSION = "1.1.6"
EXE_NAME = f"{APP_NAME.replace(' ', '_')}.exe"
