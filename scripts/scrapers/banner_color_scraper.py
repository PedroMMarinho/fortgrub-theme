import os
import json
import requests
import re
import colorsys
import math
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# --- Configuration ---
API_URL = "https://fortnite-api.com/v1/banners/colors"
OUTPUT_DIR = os.path.join("assets", "banners", "pallet")
FILE_JSON = os.path.join(OUTPUT_DIR, "colors.json")
FILE_IMAGE = os.path.join(OUTPUT_DIR, "palette.png")

# Try to load a font, or fallback to default
try:
    FONT = ImageFont.truetype("arial.ttf", 10)
except IOError:
    FONT = ImageFont.load_default()

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def natural_keys(text):
    """
    Helper to sort strings with numbers naturally.
    'DefaultColor2' -> ['DefaultColor', 2] (Before 10)
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

def parse_fortnite_color(color_string):
    """
    Parses Fortnite color strings into (R, G, B).
    Handles Hex (Gray666666FFDark) and HSV (GreenH120Light).
    """
    # 1. Hex Check
    hex_match = re.search(r'([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?([a-zA-Z]+)?$', color_string)
    
    if hex_match:
        hex_str = hex_match.group(1)
        suffix = hex_match.group(3) 
        
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        
        if suffix:
            if "Dark" in suffix:
                r, g, b = int(r * 0.6), int(g * 0.6), int(b * 0.6)
            elif "Light" in suffix:
                r = int(r + (255 - r) * 0.5)
                g = int(g + (255 - g) * 0.5)
                b = int(b + (255 - b) * 0.5)
        return (r, g, b)

    # 2. HSV Check
    hue_match = re.search(r'H(\d+)([a-zA-Z]+)?$', color_string)
    
    if hue_match:
        hue_angle = int(hue_match.group(1))
        suffix = hue_match.group(2) 

        saturation = 1.0
        value = 1.0

        if suffix:
            if "Dark" in suffix:
                value = 0.5      # Darker
            elif "Light" in suffix:
                saturation = 0.5 # Lighter

        r, g, b = colorsys.hsv_to_rgb(hue_angle / 360.0, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    return None

def create_palette_image(colors_data):
    """Generates a grid image of all parsed colors."""
    if not colors_data:
        return

    # Use the pre-sorted dictionary keys
    sorted_keys = list(colors_data.keys())

    swatch_size = 100
    padding = 20
    cols = 8
    rows = math.ceil(len(sorted_keys) / cols)

    img_w = (cols * swatch_size) + ((cols + 1) * padding)
    img_h = (rows * swatch_size) + ((rows + 1) * padding)

    img = Image.new("RGB", (img_w, img_h), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    print(f"🎨 Generating palette image ({img_w}x{img_h})...")

    for i, color_id in enumerate(tqdm(sorted_keys, desc="Drawing Palette")):
        data = colors_data[color_id]
        rgb = tuple(data["rgb"])
        
        col = i % cols
        row = i // cols
        
        x = padding + (col * (swatch_size + padding))
        y = padding + (row * (swatch_size + padding))

        # Draw Swatch
        draw.rectangle([x, y, x + swatch_size, y + swatch_size], fill=rgb)
        
        # Text Logic
        brightness = sum(rgb) / 3
        text_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)
        
        display_text = color_id.replace("DefaultColor", "")
        draw.text((x + 5, y + 5), display_text, fill=text_color, font=FONT)
        
        raw_code = data.get("raw", "UNK")
        draw.text((x + 5, y + swatch_size - 15), str(raw_code)[:10], fill=text_color, font=FONT)

    img.save(FILE_IMAGE)
    print(f"🖼️  Palette image saved to: {FILE_IMAGE}")

def main():
    ensure_dir(OUTPUT_DIR)
    
    print(f"🌍 Fetching colors from {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != 200:
            print("❌ API returned error status.")
            return

        raw_items = data.get("data", [])
        print(f"✅ Found {len(raw_items)} color definitions.")

        parsed_colors = {}
        
        # Parse Colors
        for item in raw_items:
            color_id = item.get("id")
            raw_string = item.get("color")
            
            if color_id and raw_string:
                rgb = parse_fortnite_color(raw_string)
                
                entry = {
                    "rgb": rgb if rgb else (255, 0, 0),
                    "category": item.get("category"),
                    "subCategoryGroup": item.get("subCategoryGroup"),
                    "raw": raw_string
                }
                
                if rgb is None:
                     entry["raw"] = f"FAIL: {raw_string}"

                parsed_colors[color_id] = entry

        # --- SORTING LOGIC FOR JSON ---
        # 1. Get keys sorted naturally (Color2 before Color10)
        sorted_keys = sorted(parsed_colors.keys(), key=natural_keys)
        
        # 2. Create a new dictionary in that order
        sorted_parsed_colors = {k: parsed_colors[k] for k in sorted_keys}

        # 3. Save Sorted JSON
        with open(FILE_JSON, "w") as f:
            json.dump(sorted_parsed_colors, f, indent=4)
        print(f"💾 Color data saved to: {FILE_JSON}")

        # 4. Generate Image (Pass the sorted dict)
        create_palette_image(sorted_parsed_colors)

        print("\n🎉 Done! Colors and Palette generated.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()