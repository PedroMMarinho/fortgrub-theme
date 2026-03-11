import os
from helpers.utils import load_image, CACHED_DIR
from scripts.modifiers.insert_background import add_background
from scripts.modifiers.insert_vbucks import add_vbucks

def generate_icon_final_images(config):
    print("⏳ Generating Final Images with Icons...")
    # Get images from cached folder
    cached_images = os.listdir(CACHED_DIR)
    if not cached_images:
        print(f"❌ Error: No cached images found in {CACHED_DIR}. Please run the caching step first.")
        return

    for img_name in cached_images:
        cached_img_path = os.path.join(CACHED_DIR, img_name)
        cached_img = load_image(cached_img_path)

        if cached_img is None:
            print(f"❌ Error: Failed to load cached image {cached_img_path}. Skipping.")
            continue
        
        # Changed background
        modified_img = add_background(cached_img, config)
        # Change vbucks
        modified_img = add_vbucks(modified_img, config)

        output_path = os.path.join("theme", "icons", img_name)
        modified_img.save(output_path)
        
        