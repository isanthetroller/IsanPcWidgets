import json
import os
import sys
import winreg

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
APP_NAME = "DesktopWidgets"

FONTS = [
    "Bahnschrift",
    "Segoe UI",
    "Cascadia Code",
    "Consolas",
    "Century Gothic",
    "Georgia",
    "Trebuchet MS",
    "Arial Black",
    "Impact",
    "Lucida Console",
    "Palatino Linotype",
    "Book Antiqua",
    "Copperplate Gothic Bold",
    "Candara",
    "Gabriola",
    "MV Boli",
    "Segoe Script",
    "OCR A Extended",
    "Showcard Gothic",
    "Stencil",
    "Magneto",
    "Harlow Solid Italic",
    "Juice ITC",
    "Ravie",
]

DEFAULT_CONFIG = {
    "auto_start": False,
    "theme": "emerald",
    "font": "Bahnschrift",
    "no_bg": False,
    "locked": False,
    "widgets": {
        "datetime":   {"enabled": True,  "x": 200, "y": 100, "scale": 1.0, "template": "classic"},
        "clock":      {"enabled": False, "x": 600, "y": 100, "scale": 1.0},
        "system":     {"enabled": True,  "x": 200, "y": 320, "scale": 1.0},
        "stopwatch":  {"enabled": False, "x": 600, "y": 320, "scale": 1.0},
        "quotes":     {"enabled": False, "x": 200, "y": 580, "scale": 1.0},
        "calendar":   {"enabled": False, "x": 600, "y": 100, "scale": 1.0},
        "countdown":  {"enabled": False, "x": 600, "y": 400, "scale": 1.0, "target": "2026-12-31", "label": "New Year"},
        "battery":    {"enabled": False, "x": 900, "y": 100, "scale": 1.0},
        "uptime":     {"enabled": False, "x": 900, "y": 280, "scale": 1.0},
        "network":    {"enabled": False, "x": 900, "y": 420, "scale": 1.0},
        "notes":      {"enabled": False, "x": 600, "y": 580, "scale": 1.0, "text": ""},
    },
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Merge with defaults for missing keys
            for key, val in DEFAULT_CONFIG.items():
                if key not in cfg:
                    cfg[key] = val
                elif isinstance(val, dict):
                    for k2, v2 in val.items():
                        if k2 not in cfg[key]:
                            cfg[key][k2] = v2
            return cfg
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass


def set_auto_start(enabled):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        )
        if enabled:
            exe = sys.executable
            script = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}" "{script}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except OSError:
        pass
