from PIL import Image, ImageDraw, ImageFont
import os
from helpers.utils import FONTS_DIR, IMAGES_DIR

def add_battle_pass_details(img, entry):
    
    battlepass_info = entry.get("battlepass", {})
    if battlepass_info == {}:
        return
    
    tier = battlepass_info.get("tier", 0)
    stars = battlepass_info.get("stars", 0)

    draw = ImageDraw.Draw(img)

    # Draw Battle Pass Tier
    tier_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 21)
    tier_text = f"TIER {tier}"
    tier_pos = (120,452)
    tier_color = "#fffeb9"

    (left, top, right, bottom) = tier_font.getbbox(tier_text)

    draw.text((tier_pos[0], tier_pos[1] - top + 1), tier_text, font=tier_font, fill=tier_color)

    # Draw Shinning star and star count
    position = (379 - 14, 427 - 11)
    star_icon = Image.open(os.path.join(IMAGES_DIR, "battlepass-star.png")).convert("RGBA")
    img.alpha_composite(star_icon, dest=position)

    # Battle Pass
    battlepass_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf"), 24)
    battlepass_text_pos = (426, 440)

    if tier >= 100:
        battlepass_color = (255, 255, 255, 102)
        battlepass_text = "MAX"
        (left, top, right, bottom) = battlepass_font.getbbox(battlepass_text)

        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)

        text_x = battlepass_text_pos[0]
        text_y = battlepass_text_pos[1] - top
        overlay_draw.text((text_x, text_y), battlepass_text, font=battlepass_font, fill=battlepass_color)

        img.alpha_composite(text_overlay)
    else:
        # Threshold stars to be strictly between 0 and 9
        current_stars = max(0, min(9, int(stars)))
        
        # Strings
        str_stars = str(current_stars)
        str_slash = "/"
        str_max = "10"
        
        # Fonts
        font_numbers = battlepass_font
        font_slash = ImageFont.truetype(os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Regular.ttf"), 32)
        
        # Colors
        color_stars = "#fff19d"
        color_opacity = (255, 255, 255, 102) # White with 40% opacity
        gap = 2
        
        # 1. Get bounding boxes to calculate widths
        (left_stars, top_stars, right_stars, bottom_stars) = font_numbers.getbbox(str_stars)
        width_stars = right_stars - left_stars
        
        (left_slash, top_slash, right_slash, bottom_slash) = font_slash.getbbox(str_slash)
        width_slash = right_slash - left_slash
        
        (left_max, top_max, right_max, bottom_max) = font_numbers.getbbox(str_max)
        
        # 2. X Positioning (Starting the whole string at battlepass_text_pos[0])
        x_stars = battlepass_text_pos[0]
        x_slash = x_stars + width_stars + gap
        x_max = x_slash + width_slash + gap
        
        # 3. Y Positioning centered strictly on the slash
        draw_y_slash = 438 - top_slash
        
        # Calculate the true mathematical middle of the slash
        slash_center_y = draw_y_slash + ((top_slash + bottom_slash) / 2.0)
        
        # Unified bounding box for the numbers so they don't bounce up or down
        unified_top = min(top_stars, top_max)
        unified_bottom = max(bottom_stars, bottom_max)
        
        # Force the numbers to vertically center perfectly across the slash's middle
        draw_y_numbers = slash_center_y - ((unified_top + unified_bottom) / 2.0)
        
        # --- DRAWING ---
        
        # Draw solid yellow stars number directly on the main image
        draw.text((x_stars, draw_y_numbers), str_stars, font=font_numbers, fill=color_stars)
        
        # Setup transparent overlay for the 40% opacity elements
        text_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(text_overlay)
        
        # Draw the slash and the max stars on the overlay
        overlay_draw.text((x_slash, draw_y_slash), str_slash, font=font_slash, fill=color_opacity)
        overlay_draw.text((x_max, draw_y_numbers), str_max, font=font_numbers, fill=color_opacity)
        
        # Stamp the transparent layer onto the main image
        img.alpha_composite(text_overlay)

