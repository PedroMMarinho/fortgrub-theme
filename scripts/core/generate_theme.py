from helpers.utils import BASE_IMAGE, load_config, load_image, save_config, CACHED_DIR
from modifiers.insert_emoticon import change_emoticon
from scripts.modifiers.insert_icon import generate_cached_final_images
from scripts.modifiers.insert_season import insert_season
from scripts.modifiers.insert_missions import add_missions
from scripts.modifiers.insert_final_images import generate_icon_final_images

def run():
    print("Starting Theme Generation ...")

    # Load main config
    config = load_config()
    

    # Load base image
    base_image = load_image(BASE_IMAGE)

    # Add season text to base image
    base_image = insert_season(config, base_image)

    # Add missions
    add_missions(config, base_image)

    # Generate cached images 
    generate_cached_final_images(config, base_image)

    # Change progress bar emoticon
    change_emoticon(config)

    # Generate final_images onto icons dir
    # Background and vbucks applying here
    generate_icon_final_images(config)

    print("Theme generation completed successfully!")