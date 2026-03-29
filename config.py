import json
import os
import sys

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".brightness_app")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "brightness": 100,
    "temperature": 6500,
    "enabled": True,
    "screens": [],
    "language": "tr",
    "autostart": False,
}

# Preset keys are language-independent; display names come from lang.py
PRESETS = {
    "day": {"brightness": 100, "temperature": 6500},
    "office": {"brightness": 85, "temperature": 5500},
    "night": {"brightness": 70, "temperature": 3400},
    "reading": {"brightness": 60, "temperature": 4200},
    "movie": {"brightness": 80, "temperature": 5000},
}

PRESET_ICONS = {
    "day": "\u2600",
    "office": "\u2328",
    "night": "\u263D",
    "reading": "\u2261",
    "movie": "\u25B6",
}

APP_NAME = "BrightnessApp"


def _get_exe_path():
    """Return the path used for autostart registry entry."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return f'"{sys.executable}" "{os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))}"'


def set_autostart(enabled):
    """Add or remove the app from Windows startup via registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        )
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_exe_path())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass


def get_autostart():
    """Check if the app is registered for Windows startup."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_QUERY_VALUE,
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


class Config:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for key in DEFAULTS:
                if key in saved:
                    self._data[key] = saved[key]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def brightness(self):
        return self._data["brightness"]

    @brightness.setter
    def brightness(self, value):
        self._data["brightness"] = max(10, min(100, value))
        self.save()

    @property
    def temperature(self):
        return self._data["temperature"]

    @temperature.setter
    def temperature(self, value):
        self._data["temperature"] = max(1000, min(6500, value))
        self.save()

    @property
    def enabled(self):
        return self._data["enabled"]

    @enabled.setter
    def enabled(self, value):
        self._data["enabled"] = bool(value)
        self.save()

    @property
    def screens(self):
        return self._data["screens"]

    @screens.setter
    def screens(self, value):
        self._data["screens"] = list(value)
        self.save()

    @property
    def language(self):
        return self._data["language"]

    @language.setter
    def language(self, value):
        self._data["language"] = value
        self.save()

    def set_preset(self, brightness, temperature):
        """Set brightness and temperature with a single save."""
        self._data["brightness"] = max(10, min(100, brightness))
        self._data["temperature"] = max(1000, min(6500, temperature))
        self.save()

    @property
    def autostart(self):
        return self._data["autostart"]

    @autostart.setter
    def autostart(self, value):
        self._data["autostart"] = bool(value)
        set_autostart(value)
        self.save()
