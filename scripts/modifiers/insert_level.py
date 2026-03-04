from PIL import ImageDraw, ImageFont, Image
from helpers.utils import FONTS_DIR, IMAGES_DIR, load_image
import os
import math


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

# Aproximation of the original XP curve based on known milestones and the total XP for level 99.
def get_og_max_xp(level):
    if level >= 100:
        return 0
        
    known_points = {
        1: 100,
        5: 700,
        14: 1200,
        15: 1250,
        90: 28500
    }

    if level in known_points:
        return known_points[level]

    if level < 15:
        lower_lvl = max([k for k in known_points.keys() if k < level])
        upper_lvl = min([k for k in known_points.keys() if k > level])
        
        progress = (level - lower_lvl) / (upper_lvl - lower_lvl)
        xp_diff = known_points[upper_lvl] - known_points[lower_lvl]
        
        calculated_xp = known_points[lower_lvl] + (xp_diff * progress)
        return int(round(calculated_xp / 10.0) * 10)

    # Handle the late-game exponential ramp-up (Levels 16-99)
    # This specific curve locks Level 90 to exactly 28,500 
    # and pushes the cumulative sum of 1-99 to exactly ~1,170,250 XP
    
    base_xp = 1250 
    growth_rate = 0.0417 
    
    levels_past_15 = level - 15
    
    calculated_xp = base_xp * math.exp(growth_rate * levels_past_15)
    
    return int(round(calculated_xp / 10.0) * 10)

def add_level_details(img, entry):
    level = entry.get("level", 1)
    # Percentage from 0 to 100 for the progress bar
    progress = entry.get("xp-progress", 0)
    # Clamp value
    progress = max(0.0, min(99.99, float(progress)))

    reference_point = (242, 328)

    if level >= 100:
        progress_width = 238
        
        progress_bar = create_progress_bar(100.0, progress_width)

        bar_pos = (reference_point[0], reference_point[1] - 8)
        img.paste(progress_bar, bar_pos, progress_bar)
        
        font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 21)
        text = "MAX"
        
        (left, top, right, bottom) = font.getbbox(text)
        
        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)
        color_max = (255, 255, 255, 204)
        
        text_x = bar_pos[0] + 1
        
        target_bottom_y = bar_pos[1] - 2
        draw_y_max = target_bottom_y - bottom
        
        overlay_draw.text((text_x, draw_y_max), text, font=font, fill=color_max)
        
        img.paste(text_overlay, (0, 0), text_overlay)
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

       # Milestone text + LVL text
        font = ImageFont.truetype(os.path.join(FONTS_DIR, "Burbank", "BurbankBigCondensed-Black.otf"), 32)
        level_text = "LVL"
        milestone_str = str(next_level_milestone)

        (left_lvl, top_lvl, right_lvl, _) = font.getbbox(level_text)
        lvl_width = right_lvl - left_lvl

        (left_mile, top_mile, right_mile, _) = font.getbbox(milestone_str)
        mile_width = right_mile - left_mile

        #  Calculate exact starting X coordinate to guarantee a 7px gap
        # Total block size = [LVL width] + [4px gap] + [Milestone width]
        total_text_width = lvl_width + 4 + mile_width
        
        start_x = arrow_pos_second[0] - 7 - total_text_width
        
        base_y = reference_point[1] + 33

        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)

        # Draw "LVL" (40% Opacity) starting exactly at start_x
        color_lvl = (255, 255, 255, 102)
        lvl_target_pos = (start_x, base_y - top_lvl)
        overlay_draw.text(lvl_target_pos, level_text, font=font, fill=color_lvl)

        # Draw the Milestone Number (80% Opacity) 4 pixels after "LVL"
        color_milestone = (255, 255, 255, 204)
        mile_target_pos = (start_x + lvl_width + 4, base_y - top_mile)
        overlay_draw.text(mile_target_pos, milestone_str, font=font, fill=color_milestone)

        img.paste(text_overlay, (0, 0), text_overlay)

        # Add XP text below the progress bar
        needed_xp = get_og_max_xp(level)
        current_xp = int((progress / 100.0) * needed_xp)
        
        font_bold = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21.5)
        font_regular = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 29)
        font_regular_small = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 21.5)

        current_xp_str = f"{current_xp:,}"
        text_bar = "/"
        needed_xp_str = f"{needed_xp:,}"

        # Get full bounding boxes
        (left_xp, top_xp, right_xp, bottom_xp) = font_bold.getbbox(current_xp_str)
        xp_width = right_xp - left_xp

        (left_bar, top_bar, right_bar, bottom_bar) = font_regular.getbbox(text_bar)
        bar_width = right_bar - left_bar

        (left_needed, top_needed, right_needed, bottom_needed) = font_regular_small.getbbox(needed_xp_str)

        # Get the highest top point and lowest bottom point between both strings
        unified_top = min(top_xp, top_needed)
        unified_bottom = max(bottom_xp, bottom_needed)

        # 1. The absolute bottom line now ONLY applies to the slash
        target_bottom_y = reference_point[1] - 7
        
        draw_y_bar = target_bottom_y - bottom_bar
        slash_center_y = draw_y_bar + (top_bar + bottom_bar) / 2.0

        # Calculate ONE shared Draw Y for both XP numbers to lock them together
        draw_y_numbers = slash_center_y - (unified_top + unified_bottom) / 2.0

        base_x = reference_point[0]

        # Draw Current XP (100% White) using the shared Y
        draw = ImageDraw.Draw(img)
        draw.text((base_x, draw_y_numbers), current_xp_str, font=font_bold, fill="#ffffff")

        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)
        color_xp_needed = (255, 255, 255, 102)

        # Draw "/" (40% Opacity)
        slash_x = base_x + xp_width + 4
        overlay_draw.text((slash_x, draw_y_bar), text_bar, font=font_regular, fill=color_xp_needed)

        # Draw Needed XP (40% Opacity) using the exact same shared Y
        needed_x = slash_x + bar_width + 2
        overlay_draw.text((needed_x, draw_y_numbers), needed_xp_str, font=font_regular_small, fill=color_xp_needed)

        img.paste(text_overlay, (0, 0), text_overlay)
