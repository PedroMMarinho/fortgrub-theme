from PIL import Image, ImageDraw, ImageFont
import os
from scripts.helpers.utils import FONTS_DIR, load_font


def insert_season(config, base_image):
    season = config.get("season", 0)
    season_string = f"SEASON {season}"
    
    font_path = os.path.join(FONTS_DIR, "Burbank", "BurbankBigCondensed-Black.otf")
    season_font = ImageFont.truetype(font_path, 32)

    season_position = (48, 168)

    (left, top, right, bottom) = season_font.getbbox(season_string)
    
    season_color = (255, 255, 255, 191)

    text_overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(text_overlay)

    text_x = season_position[0]
    text_y = season_position[1] - top
    overlay_draw.text((text_x, text_y), season_string, font=season_font, fill=season_color)

    base_image.alpha_composite(text_overlay)
    
    return base_image



