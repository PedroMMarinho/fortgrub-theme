import os
import io
import cairosvg
from PIL import Image, ImageOps

from helpers.utils import save_image, ICONS_DIR, IMAGES_DIR, THEME_DIR

LAYOUT_CONFIG = [
    {"pos": (922, 632),  "size": (300, 300)}, 
    {"pos": (1275, 639), "size": (220, 220)}, 
    {"pos": (1529, 603), "size": (180, 180)}, 
    {"pos": (596, 641),  "size": (220, 220)}, 
]

ARROW_ICON_PATH = os.path.join(IMAGES_DIR, "arrow-entry.png")

def load_arrow_icon():
    if os.path.exists(ARROW_ICON_PATH):
        try:
            img = Image.open(ARROW_ICON_PATH).convert("RGBA")
            return img
        except Exception as e:
            print(f"❌ Error loading arrow: {e}")
            return None
    return None

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
    return None

def render_menu_level(entries, base_image, arrow_icon, menu_id="root"):
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
                
                icon = get_icon_for_classes(entry.get('class', []), slot_size)
                
                if icon:
                    center_x = slot_pos[0] + arrow_w // 2
                    center_y = slot_pos[1] + arrow_h // 2
                    
                    paste_x = int(center_x - icon.size[0] / 2)
                    paste_y = int(center_y - icon.size[1] / 2)
                    
                    # Little Y offset to better align with GRUB's layout
                    paste_y -= 10

                    img.paste(icon, (paste_x, paste_y), icon if icon.mode == 'RGBA' else None)
        # TODO - CHANGE TO SIMPLER NAMING E.G - fortgrub1, fortgrub2, etc. (will then be a class added to grub.cfg entries to link them to the correct image)
        filename = f"menu_{menu_id}_selected_{i + 1}.png"
        save_image(img, filename, output_path=THEME_DIR + f"/icons/")

    # Recurse
    for idx, entry in enumerate(entries):
        if entry.get("children"):
            sub_id = f"{menu_id}_{idx + 1}"
            render_menu_level(entry["children"], base_image, arrow_icon, sub_id)

def generate_final_images(entries, base_image):
    print("⏳ Loading Arrow Resources...")
    arrow_icon = load_arrow_icon()

    print(f"Processing {len(entries)} root entries...")
    render_menu_level(entries, base_image, arrow_icon, "root")
    print("✅ Theme generation complete.")