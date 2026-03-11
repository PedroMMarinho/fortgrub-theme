import os
from PIL import Image, ImageDraw, ImageFont
from helpers.utils import FONTS_DIR, IMAGES_DIR, load_image


def add_missions(config, img):
    missions = config.get("missions", {})
    star_icon = load_image(os.path.join(IMAGES_DIR, "level-star-exp.png")).convert("RGBA")
    arrow_icon = load_image(os.path.join(IMAGES_DIR, "level-arrow.png")).convert("RGBA")

    for mission_type, mission_info in missions.items():
        add_mission(mission_type, img, mission_info, star_icon, arrow_icon)

    return img


def add_mission(mission_type, img, config, star_icon, arrow_icon): 
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
    star_number_text = "5"
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
    # --- STEP 3: Draw Arrow Icon ---
    # Distance is 7 px to the left of the star icon
    arrow_icon_x = star_icon_x - 7 - arrow_icon.width
    arrow_icon_y = int(star_center_y - (arrow_icon.height / 2))
    
    colored_arrow = Image.new("RGBA", arrow_icon.size, "#3c435d")
    
    img.paste(colored_arrow, (int(arrow_icon_x), arrow_icon_y), arrow_icon)
    # ------------------------------
    # TODO
    # Then draw the current-stars/total-stars 7 px to the left. 
    # For the numbers use font with 21.1
    # For the slash use font with 30
    # Center the numbers around the slash
    # Distance from slash to number on the rigth is 4 px and to the left 6 px

    font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21.1)

    font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 30)


    # Draw rectangle of 3 px border 3c435d color and fill with 00001d, width will be dynamic
    # Distanced to the rigth number by 8 px.
    # Should have the remaining width, with spacing of 16 px to the left of the container. Height should be 44 px down from the top.