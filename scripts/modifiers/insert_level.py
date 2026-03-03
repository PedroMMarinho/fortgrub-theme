from PIL import ImageDraw, ImageFont, Image
from helpers.utils import FONTS_DIR, IMAGES_DIR, load_image
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

    return combined.convert("RGBA")

def add_level_text(base_image, config):
    level = config.get("level", 1)
    font_path = os.path.join(FONTS_DIR, "Burbank", "BurbankBigCondensed-Black.otf")
    
    text_str = str(level)
    
    # Target Center Coordinates
    pos_x = 332
    pos_y = 235
    
    return draw_fortnite_text(base_image, pos_x, pos_y, text_str, font_path)


def create_progress_bar(progress, width):
    bar_height = 18
    border_color = "#636d84"
    fill_color = "#c6ff28"
    border_size = 3  

    # 1. Clamp progress to ensure it strictly stays between 0 and 100
    progress = max(0.0, min(100.0, float(progress)))

    # 2. Create base image filled with total transparency
    img = Image.new("RGBA", (width, bar_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 3. Draw the border explicitly as an outline
    draw.rectangle(
        [0, 0, width - 1, bar_height - 1], 
        outline=border_color, 
        width=border_size
    )

    # Calculate inner coordinates for the fill
    inner_x0 = border_size
    inner_y0 = border_size
    inner_x1 = width - border_size
    inner_y1 = bar_height - border_size

    # 4. Calculate and draw the filled progress
    if progress > 0:
        max_fill_width = (inner_x1 - inner_x0)
        fill_width = int(max_fill_width * (progress / 100.0))
        
        # Only draw the fill if the width is at least 1 pixel
        if fill_width > 0:
            draw.rectangle(
                [inner_x0, inner_y0, inner_x0 + fill_width - 1, inner_y1 - 1], 
                fill=fill_color
            )

    return img



def add_level_details(img, entry):
    level = entry.get("level", 1)
    # Percentage from 0 to 100 for the progress bar
    progress = entry.get("progress", 0)
    reference_point = (242, 328)

    if level >= 100:
        progress_width = 238
        pass
        # Put Max text with green progress bar
    else:
        progress_width = 148
        
        progress_bar = create_progress_bar(progress,progress_width)

        img.paste(progress_bar, reference_point, progress_bar)

        # Put arrow icon on the right of the progress bar
        arrow_icon = load_image(os.path.join(IMAGES_DIR, "level-arrow.png"))

        arrow_pos_x = reference_point[0] + progress_width + 8
        arrow_pos_y = reference_point[1] + 1

        arrow_pos_first = (arrow_pos_x, arrow_pos_y)
        img.paste(arrow_icon, arrow_pos_first, arrow_icon)

        arrow_pos_second = (arrow_pos_x, arrow_pos_y + 20 + arrow_icon.height)
        img.paste(arrow_icon, arrow_pos_second, arrow_icon)


        # Load star battle pass icon
        level_star_icon = load_image(os.path.join(IMAGES_DIR, "level-star-exp.png"))

        level_star_pos_first = (arrow_pos_x + 8 + arrow_icon.width, reference_point[1] - 5)

        img.paste(level_star_icon, level_star_pos_first, level_star_icon)

        level_star_pos_second = (level_star_pos_first[0], level_star_pos_first[1] + level_star_icon.height + 7)
        img.paste(level_star_icon, level_star_pos_second, level_star_icon)
    
        next_level_milestone = (level // 5 + 1) * 5

        # Add yellow text next to arrows
        n_star_first = "2"
        n_star_second = "10" if next_level_milestone % 10 == 0 else "5"

        n_star_x = level_star_pos_first[0] + level_star_icon.width + 4        
        n_star_first_pos = (n_star_x, reference_point[1] + 1)
        
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 23.5)

        (_, top, _, bottom) = font.getbbox(n_star_first)

        color = "#fff19d"
        draw.text((n_star_first_pos[0], n_star_first_pos[1] - top), str(n_star_first), font=font, fill=color)

        offset_y_text = bottom - top

        (_, top, _, _) = font.getbbox(n_star_second)

        draw.text((n_star_first_pos[0], n_star_first_pos[1] + offset_y_text + 20 - top), str(n_star_second), font=font, fill=color)


        return
        milestone_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Burbank", "BurbankBigCondensed-Black.otf"), 32)

        # Get next level milestone
        print(f"Current Level: {level}, Next Milestone: {next_level_milestone}")

        milestone_pos = (360, 361)

        # All white with opacity 80 %
        draw = ImageDraw.Draw(img)
        draw.text(milestone_pos, next_level_milestone, font=milestone_font, fill=(255, 255, 255, 204))
