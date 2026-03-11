import os
from PIL import Image, ImageDraw, ImageFont
from helpers.utils import FONTS_DIR, IMAGES_DIR, load_image


def add_missions(config, img):
    missions = config.get("missions", {})
    star_icon = load_image(os.path.join(IMAGES_DIR, "level-star-exp.png")).convert("RGBA")
    arrow_icon = load_image(os.path.join(IMAGES_DIR, "level-arrow.png")).convert("RGBA")
    xp_icon = load_image(os.path.join(IMAGES_DIR, "xp-banner.png")).convert("RGBA")

    for mission_type, mission_info in missions.items():
        add_mission(mission_type, img, mission_info, star_icon, arrow_icon, xp_icon)

    return img


def add_mission(mission_type, img, config, star_icon, arrow_icon, xp_icon): 
    # Initialize the drawing context
    draw = ImageDraw.Draw(img)
    
    container_width = 464
    is_daily = mission_type.startswith("daily")
    # 72 height of the container + 4 pixels of margin
    ref_point = (32,520) if not is_daily else (32, 636 + (int(mission_type[-1]) - 1) * (72 + 4))
    
    font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 21.1)

    text_position = (ref_point[0] + 16, ref_point[1] + 12)        
    max_text_width = 432
    
    # --- STEP 1: Draw the Title ---
    mission_title = config.get("description", "Mission Title")
    draw_title = mission_title
    
    while draw.textlength(draw_title, font=font) > max_text_width and len(draw_title) > 0:
        draw_title = draw_title[:-1]
        
    if draw_title:
        title_color = (255, 255, 255, 191) 
        (left, top, right, bottom) = font.getbbox(draw_title)

        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)
        
        text_x = text_position[0] - 1
        text_y = text_position[1] - top + 1
        
        overlay_draw.text((text_x, text_y), draw_title, font=font, fill=title_color)
        img.paste(text_overlay, (0, 0), text_overlay)
    
    # --- STEP 2: Draw Star Number and Icon ---
    font_star = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21)
    star_number_text = str(config.get("star-reward", 2))
    star_number_color = "#fff19d"
    
    (left, top, right, bottom) = font_star.getbbox(star_number_text)
    text_width = right - left
    text_height = bottom - top
    
    star_number_x = ref_point[0] + container_width - 16 - text_width
    
    star_number_y = ref_point[1] + 43 - top  
    star_number_position = (star_number_x, star_number_y)
    
    text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(text_overlay)
    
    overlay_draw.text(star_number_position, star_number_text, font=font_star, fill=star_number_color)
    img.paste(text_overlay, (0, 0), text_overlay)

    star_icon_x = star_number_x - 4 - star_icon.width
    
    star_center_y = ref_point[1] + 43 + (text_height / 2)
    star_icon_y = int(star_center_y - (star_icon.height / 2))
    
    img.paste(star_icon, (int(star_icon_x), star_icon_y), star_icon)
    # --- STEP 3: Draw XP Parts ---
    anchor_x = star_icon_x

    if is_daily:
        exp_text = str(config.get("xp-reward", 500))
        font_exp = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21.1)
        exp_color = "#f1ffb7"
        
        (e_left, e_top, e_right, e_bottom) = font_exp.getbbox(exp_text)
        exp_width = e_right - e_left
        
        # Position: 6 px left of the star icon (our current anchor)
        exp_x = anchor_x - 6 - exp_width
        exp_y = ref_point[1] + 43 - e_top
        
        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)
        overlay_draw.text((exp_x, exp_y), exp_text, font=font_exp, fill=exp_color)
        img.paste(text_overlay, (0, 0), text_overlay)
        
        # 2. XP Icon: 7 px left of the text
        xp_icon_x = exp_x - 7 - xp_icon.width
        xp_icon_y = int(star_center_y - (xp_icon.height / 2))
        
        img.paste(xp_icon, (int(xp_icon_x), xp_icon_y), xp_icon)
        
        anchor_x = xp_icon_x
        

    # --- STEP 4: Draw Arrow Icon ---
    # Distance is 7 px to the left of the star icon
    offset_arrow = 7 if not is_daily else 11
    arrow_icon_x = anchor_x - offset_arrow - arrow_icon.width
    arrow_icon_y = int(star_center_y - (arrow_icon.height / 2))
    
    colored_arrow = Image.new("RGBA", arrow_icon.size, "#3c435d")
    
    img.paste(colored_arrow, (int(arrow_icon_x), arrow_icon_y), arrow_icon)
   # --- STEP 5: Current/Total Stars ---
    font_numbers = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21.1)
    font_slash = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 30)

    current_stars_text = str(config.get("current-stars", 3)) 
    total_stars_text = str(config.get("total-stars", 5))

    text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(text_overlay)
    text_color = "#ffffff"

    # 1. Total Stars (7 px left of the arrow)
    (n_left, n_top, n_right, n_bottom) = font_numbers.getbbox(total_stars_text)
    total_w = n_right - n_left
    total_h = n_bottom - n_top
    
    total_x = arrow_icon_x - 7 - total_w
    
    total_y = ref_point[1] + 43 - n_top
    
    center_y = (ref_point[1] + 43) + (total_h / 2)

    overlay_draw.text((total_x, total_y), total_stars_text, font=font_numbers, fill=text_color)

    (s_left, s_top, s_right, s_bottom) = font_slash.getbbox("/")
    slash_w = s_right - s_left
    slash_h = s_bottom - s_top
    
    slash_x = total_x - 4 - slash_w
    
    slash_top_ink = center_y - (slash_h / 2)
    slash_y = slash_top_ink - s_top 
    
    overlay_draw.text((slash_x, slash_y), "/", font=font_slash, fill=text_color)

    (c_left, c_top, c_right, c_bottom) = font_numbers.getbbox(current_stars_text)
    current_w = c_right - c_left
    
    current_x = slash_x - 6 - current_w
    current_y = ref_point[1] + 43 - c_top
    
    overlay_draw.text((current_x, current_y), current_stars_text, font=font_numbers, fill=text_color)

    img.paste(text_overlay, (0, 0), text_overlay)
    # --- STEP 6: Draw Progress Bar Rectangle ---
    rect_right_x = current_x - 8
    rect_left_x = ref_point[0] + 16
    rect_y_top = ref_point[1] + 44
    bar_height = 12 
    rect_y_bottom = rect_y_top + bar_height

    # 1. Draw the background/border rectangle
    draw.rectangle(
        [rect_left_x, rect_y_top, rect_right_x, rect_y_bottom],
        fill="#00001d",
        outline="#3c435d",
        width=3
    )
    
    current_val = float(current_stars_text)
    total_val = float(total_stars_text)
    
    if total_val > 0 and current_val > 0:
        current_val = min(current_val, total_val)
        progress_ratio = current_val / total_val
        
        inner_left = rect_left_x + 3
        inner_top = rect_y_top + 3
        inner_bottom = rect_y_bottom - 3
        max_inner_right = rect_right_x - 3
        
        max_inner_width = max_inner_right - inner_left
        fill_width = max_inner_width * progress_ratio
        inner_right = inner_left + fill_width
        
        draw.rectangle(
            [inner_left, inner_top, inner_right, inner_bottom],
            fill="#c6ff28"
        )
