# scripts/helpers/utils.py
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
THEME_CONFIG_PATH = os.path.join(SCRIPTS_DIR, "config.json")
BASE_IMAGE = os.path.join(ASSETS_DIR, "base.png")

def load_config(path=THEME_CONFIG_PATH):
    if not os.path.exists(path):
        print(f"❌ Error: Config file not found at {path}")
        return None

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON. {e}")
        return None