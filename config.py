import os
import json
from typing import Dict

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".language_helper.json")


def load_settings() -> Dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(settings: Dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f)
    except Exception:
        pass


def load_ui_strings() -> Dict:
    path = os.path.join(os.path.dirname(__file__), "ui_strings.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"en": {}}


UI_STRINGS = load_ui_strings()
current_ui_language = "en"


def t(key: str) -> str:
    return UI_STRINGS.get(current_ui_language, {}).get(key, key)
