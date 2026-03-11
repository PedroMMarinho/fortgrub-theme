from PIL import Image, ImageDraw, ImageOps, ImageEnhance
from helpers.utils import load_config, COLORS_CONFIG_PATH, load_image, BANNERS_DIR
import bisect
import os


def shift_color_brightness(rgb, factor):
    """
    Adjusts the brightness of an RGB tuple.
    factor > 1.0 = Lighter
    factor < 1.0 = Darker
    """
    r, g, b = rgb
    new_r = min(255, int(r * factor))
    new_g = min(255, int(g * factor))
    new_b = min(255, int(b * factor))
    return (new_r, new_g, new_b)

def create_linear_gradient_fill(size, top_color, bottom_color):
    """
    Generates a vertical linear gradient from top_color to bottom_color.
    """
    width, height = size
    
    gradient = Image.new('RGB', (1, height))
    pixels = gradient.load()

    for y in range(height):
        ratio = y / float(height - 1) 
        
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        
        pixels[0, y] = (r, g, b)
    
    return gradient.resize((width, height))

def create_banner_bg(color):
    width, height = 96, 120
    supersample = 4  # Draw at 4x scale for perfectly smooth edges
    
    if len(color) == 4: color = color[:3]
    
    top_color = shift_color_brightness(color, 1.3)
    bottom_color = shift_color_brightness(color, 0.7)
    
    # Create the base gradient at normal size
    banner_img = create_linear_gradient_fill((width, height), top_color, bottom_color)
    banner_img = banner_img.convert("RGBA") 
    
    # Create a LARGER mask for supersampling
    mask_w = width * supersample
    mask_h = height * supersample
    mask = Image.new("L", (mask_w, mask_h), 0) 
    draw_mask = ImageDraw.Draw(mask)
    
    bridge_width = 1 * supersample
    center_x = mask_w // 2 
    
    # Scale all coordinates by the supersample factor
    points = [
        (0, 0),                         
        (mask_w - 1, 0),                 
        (mask_w - 1, 93 * supersample),                
        (center_x + bridge_width, mask_h - 1),  
        (center_x - bridge_width, mask_h - 1),  
        (0, 93 * supersample)                         
    ]
    
    draw_mask.polygon(points, fill=255)
    
    # Resize the mask back down using LANCZOS for smooth anti-aliasing
    mask = mask.resize((width, height), resample=Image.Resampling.LANCZOS)
    
    banner_img.putalpha(mask)
    
    return banner_img

def process_banner_icon(icon_name):
    target_size = (128, 128) 
    icon_path = BANNERS_DIR + "/icons/" + icon_name
    try:
        raw_icon = load_image(icon_path)
        if raw_icon is None: return None
        
        mask = raw_icon.convert("L")
        
        white_icon = Image.new("RGBA", mask.size, (255, 255, 255, 0))
        white_icon.putalpha(mask)
        
        return ImageOps.contain(white_icon, target_size, method=Image.Resampling.LANCZOS)
        
    except Exception as e:
        print(f"❌ Error processing banner icon: {e}")
        return None

# TODO Add border images
def draw_border(base_image, center_x, center_y, level):
    # The upper limit for each "tier"
    level_thresholds = [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, 94, 99]
    
    # 1. Find the Index
    # Level 1 -> Index 0 (Value 4)
    # Level 4 -> Index 0 (Value 4)
    # Level 5 -> Index 1 (Value 9)
    # Level 100 -> Index 20 (End of list)
    image_index = bisect.bisect_left(level_thresholds, level)
    
    filename = f"banner_border_{image_index}.png"
    file_path = os.path.join(BANNERS_DIR, "borders", filename)
    
    
    border_img = load_image(file_path) if os.path.exists(file_path) else None

    
    if border_img:
        border_w, border_h = border_img.size
        
        paste_x = center_x - (border_w // 2)
        paste_y = center_y - (border_h // 2)
        
        base_image.paste(border_img, (paste_x, paste_y), border_img)
    else:
        #print(f"⚠️ Warning: Border image for level {level} not found at {file_path}. Using level 0 fallback.")
        fallback_path = os.path.join(BANNERS_DIR, "borders", "banner_border_0.png")
        fallback_img = load_image(fallback_path)

        if fallback_img:
            fallback_w, fallback_h = fallback_img.size

            paste_x = center_x - (fallback_w // 2)
            paste_y = center_y - (fallback_h // 2)
            base_image.paste(fallback_img, (paste_x, paste_y), fallback_img)

    # Debug - Draw a red rectangle around the banner area to visualize the center and size (for development purposes)
    #draw = ImageDraw.Draw(base_image)
    #draw.rectangle(
    #    [center_x - 100, center_y - 100, center_x + 99, center_y + 99], 
    #    outline="red", width=1
    #)
    #print(f"❌ Error loading border image for level {level}. Expected at {file_path}. Drew fallback rectangle instead.")            

    return base_image



def apply_inner_border(banner_img, border_width=3, darkness_factor=0.6):
    """
    darkness_factor: 1.0 = Original, 0.5 = 50% Darker.
    """
    supersample = 4 
    
    enhancer = ImageEnhance.Brightness(banner_img)
    dark_clone = enhancer.enhance(darkness_factor)
    
    w, h = banner_img.size
    mask_w = w * supersample
    mask_h = h * supersample
    
    # Create the LARGER mask
    border_mask = Image.new("L", (mask_w, mask_h), 0)
    draw_mask = ImageDraw.Draw(border_mask)
    
    bridge_width = 1 * supersample
    center_x = mask_w // 2 
    
    points = [
        (0, 0),                         
        (mask_w - 1, 0),                 
        (mask_w - 1, 93 * supersample),                
        (center_x + bridge_width, mask_h - 1),  
        (center_x - bridge_width, mask_h - 1),  
        (0, 93 * supersample)                         
    ]
    
    # Draw the line, making sure to scale the line width too
    draw_mask.line(points + [points[0]], fill=255, width=(border_width * 2) * supersample)

    border_mask = border_mask.resize((w, h), resample=Image.Resampling.LANCZOS)

    original_alpha = banner_img.split()[-1]
    
    final_mask = Image.new("L", (w, h), 0)
    final_mask.paste(border_mask, (0, 0), original_alpha)

    result_img = banner_img.copy()
    result_img.paste(dark_clone, (0, 0), final_mask)
    
    return result_img


def gen_base_banner(banner_info):

    banner_icon_name = banner_info.get("icon")
    banner_color_name = banner_info.get("color")

    color_config = load_config(COLORS_CONFIG_PATH)
    banner_rgb = tuple(color_config.get(banner_color_name, {}).get("rgb", (100, 100, 100)))

    banner_img = create_banner_bg(banner_rgb)

    banner_mask = banner_img.split()[-1]


    icon_img = process_banner_icon(banner_icon_name)
        
    bg_w, bg_h = banner_img.size
    icon_w, icon_h = icon_img.size
    
    pos_x = (bg_w - icon_w) // 2
    pos_y = (bg_h - icon_h) // 2 
    
    banner_img.paste(icon_img, (pos_x, pos_y), icon_img)
    
    banner_img.putalpha(banner_mask)

    return banner_img


def add_banner(base_image, config):

    banner_info = config.get("banner", {})

    banner_img = gen_base_banner(banner_info)

    banner_position = (91, 250) 
    
    # Banner with border darkened for better contrast against the background
    banner_to_paste = apply_inner_border(banner_img, border_width=2, darkness_factor=0.86)

    base_image.paste(banner_to_paste, banner_position, banner_img)
    
    banner_width, banner_height = banner_to_paste.size
    
    center_x = (banner_width // 2) + banner_position[0]
    center_y = (banner_height // 2) + banner_position[1]
    
    
    draw_border(base_image, center_x, center_y, config.get("level", 1))

    return base_image, banner_img