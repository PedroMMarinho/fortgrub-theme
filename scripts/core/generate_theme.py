from helpers.utils import BASE_IMAGE, load_config, load_image, save_config, CACHED_DIR
from modifiers.insert_emoticon import change_emoticon
from scripts.modifiers.insert_icon import generate_final_images

def run():
    print("Starting Theme Generation ...")

    # Load main config
    config = load_config()
    

    # Load base image
    base_image = load_image(BASE_IMAGE)

    # Generate cached images 
    generate_final_images(config, base_image)


    # Change progress bar emoticon
    change_emoticon(config)

    print("Theme generation completed successfully!")