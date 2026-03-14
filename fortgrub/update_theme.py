import os
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

THEME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BACKGROUNDS_DIR = os.path.join(THEME_DIR, "backgrounds")
CACHED_DIR = os.path.join(THEME_DIR, "cached")

ASSETS_DIR = os.path.join(THEME_DIR, "assets")

FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

def load_font(path, size):
    if not os.path.exists(path):
        print(f"❌ Error: Font not found at {path}")
        return None
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"❌ Error: Failed to load font. {e}")
        return None

def load_image(path):
    if not os.path.exists(path):
        print(f"❌ Error: Image not found at {path}")
        return None

    return Image.open(path).convert("RGBA")


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

def update_theme():
    cached_images = [f for f in os.listdir(CACHED_DIR) if f.endswith(".png")]
    if not cached_images:
        print(f"❌ Error: No cached images found in {CACHED_DIR}. Please run caching step first.")
        return

    background_img = get_background()
    if background_img is None:
        return
        
    vbucks_layer = get_vbucks_layer()
    for img_name in cached_images:
        cached_img_path = os.path.join(CACHED_DIR, img_name)
        cached_img = Image.open(cached_img_path).convert("RGBA")

        final_image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
        
        final_image.paste(background_img, (0, 56))
        
        final_image.alpha_composite(cached_img)
        
        final_image.alpha_composite(vbucks_layer)

        output_path = os.path.join("theme", "icons", img_name)
        temp_output = output_path + ".tmp"
        
        final_image.save(temp_output, format="PNG", compress_level=1)
        os.replace(temp_output, output_path)

def get_background():
    # Choose random background
    background_files = [f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith(('.png', '.jpg'))]
    if not background_files:
        print(f"❌ Error: No background images found in {BACKGROUNDS_DIR}.")
        return None

    random_bg = random.choice(background_files)
    background_path = os.path.join(BACKGROUNDS_DIR, random_bg)
    background_image = Image.open(background_path).convert("RGBA")
    
    bg_w, bg_h = background_image.size
    base_w = 1920
    scale_factor = base_w / bg_w
    
    new_w = base_w
    new_h = int(bg_h * scale_factor)

    resized_bg = background_image.resize((new_w, new_h), Image.Resampling.BILINEAR)
    return resized_bg
          
def get_vbucks_layer():
    package_number = get_package_count()

    # 1. Setup Constants
    anchor_right_x = 1636
    anchor_top_y = 18
    height = 48
    min_width = 128
    border_color = "#7ba5d4"
    border_thickness = 3
    padding_right = 45  
    padding_left = 48  
    
    # 2. Calculate Width based on Text
    font_path = os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf")
    font = load_font(font_path, 24) 
    text_str = "{:,}".format(package_number)
    
    bbox = font.getbbox(text_str)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1] 
    
    required_width = padding_left + text_width + padding_right
    final_width = max(min_width, required_width)

    start_x = int(anchor_right_x - final_width)
    start_y = anchor_top_y

    # 3. Create the small box container
    container = Image.new("RGBA", (int(final_width), height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(container)

    draw.rectangle([0, 0, final_width - 1, height - 1], outline=border_color, width=border_thickness)

    text_x = (final_width - text_width - 45) if final_width > min_width else (final_width - 80)
    text_y = (height - text_height) // 2 - bbox[1]

    draw.text((text_x, text_y), text_str, font=font, fill="white")

    vbuck_icon = load_image(os.path.join(IMAGES_DIR, "vbuck.png"))
    vbuck_icon = vbuck_icon.resize((34, 34), Image.Resampling.BILINEAR)

    vbuck_x = text_x - 7 - vbuck_icon.width
    vbuck_y = 7
    container.paste(vbuck_icon, (vbuck_x, vbuck_y), vbuck_icon)

    # 4. Create the Master Transparent Layer
    master_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    master_draw = ImageDraw.Draw(master_layer)
    
    # Add trapezoid triangle
    triangle_start_x = 1496
    triangle_start_y = 8
    triangle_color = "#000022"
    triangle_offset_x = final_width - min_width if final_width > min_width else 0
    triangle_offset_y = 71
    
    triangle_points = [
        (triangle_start_x, triangle_start_y),
        (triangle_start_x - triangle_offset_x, triangle_start_y),
        (triangle_start_x - 18 - triangle_offset_x, triangle_start_y + triangle_offset_y),
        (triangle_start_x, triangle_start_y + triangle_offset_y)
    ]

    # Draw polygon and paste the box onto the master layer
    master_draw.polygon(triangle_points, fill=triangle_color)
    master_layer.paste(container, (start_x, start_y), container)

    return master_layer

if __name__ == "__main__":
    update_theme()