from helpers.utils import get_package_count, load_image, IMAGES_DIR, load_font, FONTS_DIR
from PIL import Image, ImageDraw
import os
import json
from helpers.utils import THEME_CONFIG_PATH

def create_vbuck_container(package_number, base_image):
    # 1. Setup Constants
    anchor_right_x = 1636
    anchor_top_y = 18
    height = 48
    min_width = 128
    border_color = "#7ba5d4"
    border_thickness = 3
    # Padding settings
    padding_right = 45  

    padding_left = 48  
    
    # 2. Calculate Width based on Text
    font_path = os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf")
    font = load_font(font_path, 24) 
    text_str = "{:,}".format(package_number)
    
    bbox = font.getbbox(text_str)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1] 
    
    required_width = padding_left + text_width + padding_right
    final_width = max(min_width, required_width)

    start_x = int(anchor_right_x - final_width)
    start_y = anchor_top_y

    container = Image.new("RGBA", (int(final_width), height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(container)

    draw.rectangle(
        [0, 0, final_width - 1, height - 1], 
        outline=border_color, 
        width=border_thickness
    )

    if final_width > min_width:
        text_x = final_width - text_width - 45
    else:
        text_x = final_width - 80
        

    text_y = (height - text_height) // 2 - bbox[1]

    draw.text((text_x, text_y), text_str, font=font, fill="white")

    # Place the V-Buck icon
    vbuck_icon = load_image(os.path.join(IMAGES_DIR, "vbuck.png"))
    vbuck_icon = vbuck_icon.resize((34, 34), Image.Resampling.LANCZOS)

    vbuck_x = text_x - 7 - vbuck_icon.width
    vbuck_y = 7

    container.paste(vbuck_icon, (vbuck_x, vbuck_y), vbuck_icon)

    base_draw = ImageDraw.Draw(base_image)
    # Add trapezoid triangle on the left 
    triangle_start_x = 1496
    triangle_start_y = 8
    triangle_color = "#000022"
    triangle_offset_x = final_width - min_width if final_width > min_width else 0

    triangle_offset_y = 71
    
    # Triangle points: 
    triangle_points = [
        (triangle_start_x, triangle_start_y),
        (triangle_start_x - triangle_offset_x, triangle_start_y),
        (triangle_start_x - 18 - triangle_offset_x, triangle_start_y + triangle_offset_y),
        (triangle_start_x, triangle_start_y + triangle_offset_y)
    ]

    base_draw.polygon(triangle_points, fill=triangle_color)

   
    base_image.paste(container, (start_x, start_y), container)

    
    return base_image


def add_vbucks(base_image, config):
    package_number = get_package_count()

    current_image = create_vbuck_container(package_number, base_image)

    config["vbucks"] = package_number

    with open(THEME_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)

    return current_image

    