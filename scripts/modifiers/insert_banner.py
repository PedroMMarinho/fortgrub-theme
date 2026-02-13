from PIL import Image, ImageDraw, ImageOps
from helpers.utils import load_config, COLORS_CONFIG_PATH, load_image, BANNERS_DIR

def create_banner_bg(color):
    width, height = 96, 120
    
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # (x, y) points
    points = [
        (0, 0),          # Top Left
        (96, 0),         # Top Right
        (96, 93),        # Right Vertical End
        (49, 120),       # Right Tip (96 - 47 = 49)
        (47, 120),       # Left Tip (0 + 47 = 47)
        (0, 93)          # Left Vertical End
    ]
    
    draw.polygon(points, fill=color)
    # TODO GRADIENT FILL
    return img

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

def add_banner(base_image, config): 
    banner_info = config.get("banner", {})
    banner_icon_name = banner_info.get("icon")
    banner_color_name = banner_info.get("color")

    color_config = load_config(COLORS_CONFIG_PATH)
    banner_rgb = tuple(color_config.get(banner_color_name, {}).get("rgb", (100, 100, 100)))
    
    banner_img = create_banner_bg(banner_rgb)
    

    banner_mask = banner_img.split()[-1]
    
    if banner_icon_name:
        icon_img = process_banner_icon(banner_icon_name)
        
        if icon_img:
            bg_w, bg_h = banner_img.size
            icon_w, icon_h = icon_img.size
            
            pos_x = (bg_w - icon_w) // 2
            pos_y = (bg_h - icon_h) // 2 
            
            banner_img.paste(icon_img, (pos_x, pos_y), icon_img)
            
            banner_img.putalpha(banner_mask)

    banner_position = (91, 250) 
    
    base_image.paste(banner_img, banner_position, banner_img)
    
    return base_image, banner_img