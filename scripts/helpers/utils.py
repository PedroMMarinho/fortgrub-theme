# scripts/helpers/utils.py
import os
import json
import PIL.Image as Image
from PIL import ImageFont

import subprocess
import re


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directories
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
THEME_DIR = os.path.join(PROJECT_ROOT, "theme")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
BANNERS_DIR = os.path.join(ASSETS_DIR, "banners")

# Files
THEME_CONFIG_PATH = os.path.join(SCRIPTS_DIR, "config.json")
COLORS_CONFIG_PATH = os.path.join(BANNERS_DIR + "/pallet/", "colors.json")
BASE_IMAGE = os.path.join(ASSETS_DIR, "base1.png")


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


def get_package_count() -> int:
    for command in [["fastfetch", "-c", "neofetch"], ["neofetch"]]:
        try:
            output = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True).stdout
            break
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    else:
        print("Error: Neither Fastfetch or Neofetch are available.")
        return 0

    for line in output.splitlines():
        if "Packages" in line:
            numbers = [int(n) for n in re.findall(r"\d+", line)]
            total_packages = sum(numbers)
            return total_packages
    else:
        print("Error: Could not find package count.")
        return 0