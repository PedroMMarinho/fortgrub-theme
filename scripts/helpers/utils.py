# scripts/helpers/utils.py
import os
import json
import PIL.Image as Image
from PIL import ImageFont

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directories
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
THEME_DIR = os.path.join(PROJECT_ROOT, "theme")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Files
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

def load_image(path):
    if not os.path.exists(path):
        print(f"❌ Error: Image not found at {path}")
        return None

    return Image.open(path).convert("RGBA")

def save_image(image, name ,output_path=SCRIPTS_DIR):
    image_path = os.path.join(output_path, name)
    try:
        image.save(image_path)
        print(f"✅ Saved image to {image_path}")
    except Exception as e:
        print(f"❌ Error: Failed to save image. {e}")

def load_font(path, size):
    if not os.path.exists(path):
        print(f"❌ Error: Font not found at {path}")
        return None
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"❌ Error: Failed to load font. {e}")
        return None
