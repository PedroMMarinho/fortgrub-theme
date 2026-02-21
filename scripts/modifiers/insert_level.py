from PIL import ImageDraw, ImageFont, Image
from helpers.utils import FONTS_DIR
import os

def draw_fortnite_text(base_image, pos_x, pos_y, text, font_path):
    font_size = 64
    font = ImageFont.truetype(font_path, font_size)

    # 1. Base overlay
    overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Get the raw, tight bounding box as if we drew it at (0,0)
    raw_bbox = draw.textbbox((0, 0), text, font=font)
    raw_left, raw_top, raw_right, raw_bottom = raw_bbox
    
    text_width = raw_right - raw_left
    text_height = raw_bottom - raw_top
    
    if text_width <= 0 or text_height <= 0:
        return base_image

    # Calculate exactly where to start drawing so the TOP-LEFT hits pos_x, pos_y
    draw_x = pos_x - raw_left
    draw_y = pos_y - raw_top

    left = int(draw_x + raw_left) 
    top = int(draw_y + raw_top)    
    right = int(draw_x + raw_right)
    bottom = int(draw_y + raw_bottom)
    # --------------------------------------

    # 2. Draw stroke and base text shape using calculated coordinates
    stroke_color = (0, 0, 0, 204) 
    draw.text(
        (draw_x, draw_y), 
        text, 
        font=font, 
        fill=(255, 255, 255, 255), 
        stroke_width=1,
        stroke_fill=stroke_color,
    )

    # 3. Generate the Anti-Aliased Gradient
    gradient_img = Image.new("RGBA", (int(text_width), int(text_height)))
    pixels = gradient_img.load()

    mid_x = text_width / 2.0
    base_mid_y = text_height * 0.55
    
    arch_drop = 4.0 
    shadow_height = text_height * 0.20 

    color_shadow_top = (216, 219, 223) 
    color_white = (255, 255, 255)
    color_bottom = (215, 216, 218)     

    for x in range(int(text_width)):
        x_norm = (x - mid_x) / mid_x 
        curve_y = base_mid_y + (arch_drop * (x_norm ** 2))

        for y in range(int(text_height)):
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

    # 4. Mask and Apply
    mask = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((draw_x, draw_y), text, font=font, fill=(255, 255, 255, 255))

    full_gradient = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    full_gradient.paste(gradient_img, (left, top))

    overlay.paste(full_gradient, (0, 0), mask)
    
    debug = False
    # --- DEBUGGING VISUALS ---
    if debug:
        debug_draw = ImageDraw.Draw(overlay)
        # Draw red bounding box
        debug_draw.rectangle([left, top, right, bottom], outline="red", width=2)
        # Draw green crosshair at the exact pos_x, pos_y target (now top-left)
        debug_draw.line([(pos_x - 20, pos_y), (pos_x + 20, pos_y)], fill="green", width=2)
        debug_draw.line([(pos_x, pos_y - 20), (pos_x, pos_y + 20)], fill="green", width=2)

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