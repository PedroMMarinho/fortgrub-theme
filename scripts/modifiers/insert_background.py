import os
from PIL import Image
from helpers.utils import BACKGROUNDS_DIR

def add_background(base_image, config):

    background_name = config.get("background", "default.png")
    background_path = os.path.join(BACKGROUNDS_DIR, background_name)
    
    if not os.path.exists(background_path):
        print(f"⚠️ Warning: Background {background_name} not found. Returning base only.")
        return base_image

    background_image = Image.open(background_path).convert("RGBA")
    
    bg_w, bg_h = background_image.size
    base_w, base_h = base_image.size
    
    scale_factor = base_w / bg_w
    
    new_w = base_w
    new_h = int(bg_h * scale_factor)
    
    print(f"📏 Resizing background from {bg_w}x{bg_h} to {new_w}x{new_h}")

    resized_bg = background_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", base_image.size, (0, 0, 0, 255)) 

    # Slight offset to align with GRUB's background positioning (56px from top) 
    x_pos = 0
    y_pos = 56
    
    canvas.paste(resized_bg, (x_pos, y_pos), resized_bg)
    
    final_image = Image.alpha_composite(canvas, base_image)
    
    print("✅ Composited background and base image.")
    
    return final_image