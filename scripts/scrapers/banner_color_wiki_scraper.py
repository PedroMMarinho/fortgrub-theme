import os
import json
import re
import math
import cloudscraper
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageColor
from tqdm import tqdm

# --- Configuration ---
WIKI_URL = "https://fortnite.fandom.com/wiki/Banner_Icons"
OUTPUT_DIR = os.path.join("assets", "banners", "pallet")
FILE_JSON = os.path.join(OUTPUT_DIR, "colors.json")
FILE_IMAGE = os.path.join(OUTPUT_DIR, "palette.png")

try:
    FONT = ImageFont.truetype("arial.ttf", 10)
except IOError:
    FONT = ImageFont.load_default()

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def scrape_wiki_colors():
    print(f"🌍 Fetching HTML from {WIKI_URL}...")
    try:
        scraper = cloudscraper.create_scraper() 
        response = scraper.get(WIKI_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_table = None
        tables = soup.find_all('table')
        for t in tables:
            if "Default Colors" in t.get_text():
                target_table = t
                break
        
        if not target_table:
            print("❌ Could not find the 'Default Colors' table.")
            return {}

        parsed_colors = {}
        pending_names = [] 

        rows = target_table.find_all('tr')
        print(f"🔍 Analyzing {len(rows)} table rows...")

        for row in rows:
            # 1. Capture Names
            headers = row.find_all('th')
            if headers:
                if len(headers) == 1: continue 
                pending_names = [th.get_text(" ", strip=True) for th in headers]
                continue

            # 2. Capture Colors
            cells = row.find_all('td')
            if cells and pending_names:
                if len(cells) != len(pending_names):
                    pending_names = [] 
                    continue

                for i, cell in enumerate(cells):
                    name = pending_names[i]
                    div = cell.find('div')
                    
                    if div and div.has_attr('style'):
                        style = div['style']
                        hex_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', style)
                        
                        if hex_match:
                            hex_code = hex_match.group(0)
                            # Key = Name without spaces
                            clean_id = name.replace(" ", "")
                            rgb = ImageColor.getrgb(hex_code)
                            
                            # Simple storage, no extra fields
                            parsed_colors[clean_id] = {
                                "rgb": rgb,
                                "raw": hex_code
                            }
                pending_names = []

        return parsed_colors

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        return {}

def create_palette_image(colors_data):
    if not colors_data: return

    # --- NO SORTING ---
    # Python dicts preserve insertion order, so we just use keys() directly
    ordered_keys = list(colors_data.keys())
    
    swatch_size, padding, cols = 100, 20, 6
    rows = math.ceil(len(ordered_keys) / cols)
    
    img_w = (cols * swatch_size) + ((cols + 1) * padding)
    img_h = (rows * swatch_size) + ((rows + 1) * padding)
    img = Image.new("RGB", (img_w, img_h), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    for i, color_id in enumerate(tqdm(ordered_keys, desc="Drawing Palette")):
        data = colors_data[color_id]
        rgb = tuple(data["rgb"])
        
        col, row = i % cols, i // cols
        x = padding + (col * (swatch_size + padding))
        y = padding + (row * (swatch_size + padding))

        draw.rectangle([x, y, x + swatch_size, y + swatch_size], fill=rgb)
        
        text_color = (0, 0, 0) if (sum(rgb)/3) > 127 else (255, 255, 255)
        
        # Display the clean ID and the hex code
        draw.text((x + 5, y + 5), color_id, fill=text_color, font=FONT)
        draw.text((x + 5, y + swatch_size - 15), data.get("raw", ""), fill=text_color, font=FONT)

    img.save(FILE_IMAGE)
    print(f"🖼️  Palette image saved to: {FILE_IMAGE}")

if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    parsed_colors = scrape_wiki_colors()
    if parsed_colors:
        with open(FILE_JSON, "w") as f:
            json.dump(parsed_colors, f, indent=4)
        create_palette_image(parsed_colors)
        print("\n🎉 Done!")