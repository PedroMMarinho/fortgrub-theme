from PIL import ImageColor, ImageDraw, ImageFont, Image
from helpers.utils import FONTS_DIR
import os


def draw_fortnite_text(base_image, pos_x, pos_y, text, font_path):
    font_size = 64
    font = ImageFont.truetype(font_path, font_size)

    # 1. Base overlay
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 2. Draw stroke and base text shape
    stroke_color = (0, 0, 0, 204) 


    # 3. Get text dimensions
    bbox = draw.textbbox((pos_x, pos_y), text, font=font)
    left, top, right, bottom = bbox
    text_width = right - left
    text_height = bottom - top
    
    print(top)
    draw.text(
        (pos_x, pos_y), 
        text, 
        font=font, 
        fill=(255, 255, 255, 255), 
        stroke_width=1,
        stroke_fill=stroke_color,
    )

    if text_width <= 0 or text_height <= 0:
        return base_image

    # 4. Generate the Anti-Aliased Gradient
    gradient_img = Image.new("RGBA", (text_width, text_height))
    pixels = gradient_img.load()

    mid_x = text_width / 2.0
    base_mid_y = text_height * 0.55
    
    arch_drop = 4.0 # How many pixels the curve drops at the edges (creates the dome)
    shadow_height = text_height * 0.20 # Top shadow only covers the top 

    color_shadow_top = (216, 219, 223) # #d8dbdf
    color_white = (255, 255, 255)
    color_bottom = (215, 216, 218)     # #d7d8da

    for x in range(text_width):
        x_norm = (x - mid_x) / mid_x 
        
        curve_y = base_mid_y + (arch_drop * (x_norm ** 2))

        for y in range(text_height):
            
            # --- TOP COLOR LOGIC (Shadow + White) ---
            if y <= shadow_height:
                ratio = y / max(1.0, shadow_height)
                top_r = int(color_shadow_top[0] + (255 - color_shadow_top[0]) * ratio)
                top_g = int(color_shadow_top[1] + (255 - color_shadow_top[1]) * ratio)
                top_b = int(color_shadow_top[2] + (255 - color_shadow_top[2]) * ratio)
                current_top_color = (top_r, top_g, top_b)
            else:
                current_top_color = color_white

            if y < int(curve_y):
                pixels[x, y] = (*current_top_color, 255)
                
            elif y > int(curve_y):
                pixels[x, y] = (*color_bottom, 255)
                
            else:
                frac = curve_y - int(curve_y) 
                
                r = int(current_top_color[0] * frac + color_bottom[0] * (1 - frac))
                g = int(current_top_color[1] * frac + color_bottom[1] * (1 - frac))
                b = int(current_top_color[2] * frac + color_bottom[2] * (1 - frac))
                
                pixels[x, y] = (r, g, b, 255)

    # 5. Mask and Apply
    mask = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((pos_x, pos_y), text, font=font, fill=(255, 255, 255, 255))

    full_gradient = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    full_gradient.paste(gradient_img, (left, top))

    overlay.paste(full_gradient, (0, 0), mask)
    base_rgba = base_image.convert("RGBA")
    combined = Image.alpha_composite(base_rgba, overlay)

    return combined.convert("RGB")

def add_level_text(base_image, config):
    level = config.get("level", 1)
    font_path = os.path.join(FONTS_DIR, "Burbank", "BurbankBigCondensed-Black.otf")
    
    text_str = str(level)
    
    # Target Center Coordinates
    pos_x = 332
    pos_y = 235
    
    return draw_fortnite_text(base_image, pos_x, pos_y, text_str, font_path)