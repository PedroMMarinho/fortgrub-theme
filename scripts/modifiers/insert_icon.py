import json
import os
import io
import cairosvg
from PIL import Image, ImageOps, ImageDraw

from helpers.utils import save_image, ICONS_DIR, IMAGES_DIR, THEME_DIR, FONTS_DIR, load_image, load_font, THEME_CONFIG_PATH

LAYOUT_CONFIG = [
    {"pos": (922, 632),  "size": (300, 300)}, 
    {"pos": (1275, 639), "size": (220, 220)}, 
    {"pos": (1529, 603), "size": (180, 180)}, 
    {"pos": (596, 641),  "size": (220, 220)}, 
]

ARROW_ICON_PATH = os.path.join(IMAGES_DIR, "arrow-entry.png")
CROWN_IMAGE_PATH = os.path.join(IMAGES_DIR, "crown.png")

def get_icon_for_classes(classes, size):
    if not classes: return None
    class_list = classes if isinstance(classes, list) else [classes]
    target_w, target_h = size

    for cls in class_list:
        svg_path = os.path.join(ICONS_DIR, f"{cls}.svg")
        if os.path.exists(svg_path):
            try:
                # To improve quality, we render at a higher resolution and then downscale.
                oversample_factor = 4
                render_w = target_w * oversample_factor
                render_h = target_h * oversample_factor
                
                png_data = cairosvg.svg2png(url=svg_path, output_width=render_w, output_height=render_h)
                
                raw_icon = Image.open(io.BytesIO(png_data)).convert("RGBA")
                
                bbox = raw_icon.getbbox()
                
                if bbox:
                    trimmed_icon = raw_icon.crop(bbox)
                    
                    final_icon = ImageOps.contain(
                        trimmed_icon, 
                        (target_w, target_h), 
                        method=Image.Resampling.LANCZOS
                    )
                    
                    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                    offset_x = (target_w - final_icon.width) // 2
                    offset_y = (target_h - final_icon.height) // 2
                    canvas.paste(final_icon, (offset_x, offset_y))
                    
                    return canvas
                
                return raw_icon.resize((target_w, target_h), Image.Resampling.LANCZOS)

            except Exception as e:
                print(f"❌ Error converting {cls}.svg: {e}")

    # Throw error if no icon found for any class
    raise ValueError(f"No icon found for classes {class_list}")

def render_menu_level(entries, base_image, arrow_icon, banner_image, menu_id="root", global_counter=None, config=None):
    if global_counter is None:
        global_counter = [0]

    count = len(entries)
    if count == 0: return

    for i in range(count):
        img = base_image.copy()
        
        items_to_draw = []
        should_wrap_prev = count >= 4
        
        items_to_draw.append({"slot_idx": 0, "entry_idx": i, "is_arrow": False})
        
        next_val = i + 1
        items_to_draw.append({"slot_idx": 1, "entry_idx": next_val, "is_arrow": next_val >= count})
        
        next_next_val = i + 2
        items_to_draw.append({"slot_idx": 2, "entry_idx": next_next_val, "is_arrow": next_next_val >= count})
        
        if should_wrap_prev:
            items_to_draw.append({"slot_idx": 3, "entry_idx": (i - 1) % count, "is_arrow": False})
        else:
            prev_val = i - 1
            items_to_draw.append({"slot_idx": 3, "entry_idx": prev_val, "is_arrow": prev_val < 0})
            
        for item in items_to_draw:
            slot_config = LAYOUT_CONFIG[item["slot_idx"]]
            slot_pos = slot_config["pos"]  
            slot_size = slot_config["size"] 
            
            arrow_w, arrow_h = (0, 0)
            if arrow_icon:
                arrow_w, arrow_h = arrow_icon.size

            if item["is_arrow"]:
                if arrow_icon:
                    icon = arrow_icon
                    paste_x, paste_y = slot_pos
                    img.paste(icon, (paste_x, paste_y), icon if icon.mode == 'RGBA' else None)
            else:
                entry = entries[item["entry_idx"]]
                gen_icon_for_entry(entry, slot_size, slot_pos, (arrow_w, arrow_h), img, item["slot_idx"], banner_image)
        
        global_counter[0] += 1
        current_id = global_counter[0]
        
        # 2. Define the class name (e.g., "fortgrub1")
        class_name = f"fortgrub{current_id}"
        
        # 3. Inject into the JSON entry and save it to the config
        entries[i]["injected_class"] = class_name
        
        with open(THEME_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)


        clean_filename = f"{class_name}.png"
        save_image(img, clean_filename, output_path=THEME_DIR + f"/icons/")

        # For debugging purposes
        #debug_filename = f"menu_{menu_id}_selected_{i + 1}.png"
        #save_image(img, debug_filename, output_path=THEME_DIR + f"/icons/") 
        

    # Recurse
    for idx, entry in enumerate(entries):
        if entry.get("children"):
            sub_id = f"{menu_id}_{idx + 1}"
            render_menu_level(entry["children"], base_image, arrow_icon, banner_image, sub_id, global_counter, config)


def gen_icon_for_entry(entry, slot_size, slot_pos, arrow_size, img, slot_idx, banner_image):

    icon = get_icon_for_classes(entry.get('class', []), slot_size)
    arrow_w, arrow_h = arrow_size

    center_x = slot_pos[0] + arrow_w // 2
    center_y = slot_pos[1] + arrow_h // 2
    
    paste_x = int(center_x - icon.size[0] / 2)
    paste_y = int(center_y - icon.size[1] / 2)
    
    icon_offset_y = -10
    # Little Y offset to better align with GRUB's layout
    paste_y += icon_offset_y

    img.paste(icon, (paste_x, paste_y), icon if icon.mode == 'RGBA' else None)
        
    # Reference point of crown and text 
    reference_point = (center_x - 42, paste_y - 56)

    font_path = os.path.join(FONTS_DIR, "NotoSans", "NotoSans-Bold.ttf")
    font = load_font(font_path, 21)
    
    text_start_x = reference_point[0] 
    
    # Crown for first entry
    crown_x, crown_y = reference_point
    crown_img = load_image(CROWN_IMAGE_PATH)

    if slot_idx == 0:
        img.paste(crown_img, (crown_x, crown_y), crown_img)
        text_start_x = crown_x + crown_img.width + 4

    text_start = (text_start_x, reference_point[1] + crown_img.height // 2)

    # Name Text
    entry_name = entry.get('name')
    
    draw = ImageDraw.Draw(img)
    draw.text(text_start, entry_name, font=font, fill="white", anchor="lm")

    # Dashed Line
    line_start_pos = (reference_point[0] - 3, reference_point[1] + 24)
    line_base_width = 146

    draw_dashed_line(
        img, 
        line_start_pos, 
        line_base_width, 
        font, 
        entry_name, 
        text_start[0]
    )

    # Status Text
    status_text = "Ready" if slot_idx == 0 else "Not Ready" 
    status_color = "#64bc47" if slot_idx == 0 else "#ff737e"

    status_pos_x = text_start_x
    status_pos_y = reference_point[1] + 40

    draw.text((status_pos_x, status_pos_y), status_text, font=font, fill=status_color, anchor="lm")


    banner_pos = (reference_point[0] - 48, reference_point[1] + 3)

    # Draw main banner
    if slot_idx == 0:
        # Resize banner image to 40x50
        banner_image = banner_image.resize((40, 50))
        img.paste(banner_image, banner_pos, banner_image)
    else:
        # random banner TODO
        pass 

def draw_dashed_line(img, start_pos, min_width, font, text, text_start_x):
    text_width = font.getlength(text)
    
    line_start_x = start_pos[0]
    
    text_end_absolute = text_start_x + text_width
    
    required_width_for_text = (text_end_absolute - line_start_x)
    
    target_width = max(min_width, required_width_for_text)

    full_segment = create_detailed_segment()
    
    end_cap = full_segment.crop((0, 0, 2, 4))

    current_x, start_y = start_pos
    
    step = 8
    
    drawn_width = 0
    
    while drawn_width < (target_width - 2):
        img.paste(full_segment, (int(current_x), int(start_y)), full_segment)
        current_x += step
        drawn_width += step


    img.paste(end_cap, (int(current_x), int(start_y)), end_cap)


def create_detailed_segment(color=(255, 255, 255)):
    # 1. Dimensions
    core_w, core_h = 3, 2
    border = 1
    total_w = core_w + (border * 2)  # 5 px
    total_h = core_h + (border * 2)  # 4 px
    
    # 2. Colors
    c_solid = (color[0], color[1], color[2], 255)  # Core
    c_side  = (color[0], color[1], color[2], 51)   # 20% Opacity
    c_diag  = (color[0], color[1], color[2], 25)   # 10% Opacity (Corners)

    # 3. Create Image
    img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    
    # 4. Fill Pixels Manually for Precision
    pixels = img.load()

    # --- ROW 0 (Top Border) ---
    pixels[0, 0] = c_diag  # Top-Left Corner
    pixels[1, 0] = c_side
    pixels[2, 0] = c_side
    pixels[3, 0] = c_side
    pixels[4, 0] = c_diag  # Top-Right Corner

    # --- ROW 1 (Middle Top) ---
    pixels[0, 1] = c_side  # Left Side
    # Core Pixels
    pixels[1, 1] = c_solid
    pixels[2, 1] = c_solid
    pixels[3, 1] = c_solid
    pixels[4, 1] = c_side  # Right Side

    # --- ROW 2 (Middle Bottom) ---
    pixels[0, 2] = c_side  # Left Side
    # Core Pixels
    pixels[1, 2] = c_solid
    pixels[2, 2] = c_solid
    pixels[3, 2] = c_solid
    pixels[4, 2] = c_side  # Right Side

    # --- ROW 3 (Bottom Border) ---
    pixels[0, 3] = c_diag  # Bottom-Left Corner
    pixels[1, 3] = c_side
    pixels[2, 3] = c_side
    pixels[3, 3] = c_side
    pixels[4, 3] = c_diag  # Bottom-Right Corner

    return img


# TODO - Pass banner image to this function.
def generate_final_images(config, base_image, banner_image):
    print("⏳ Loading Arrow Resources...")
    arrow_icon = load_image(ARROW_ICON_PATH)

    entries = config.get("menu-entries", [])
    print(f"Processing {len(entries)} root entries...")
    render_menu_level(entries, base_image, arrow_icon, banner_image, "root", [0], config)
    print("✅ Theme generation complete.")

