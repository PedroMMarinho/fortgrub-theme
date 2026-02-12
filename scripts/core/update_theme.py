import os
from helpers.utils import load_config, load_image, save_image, BASE_IMAGE
from helpers.grub_parser import parse_grub_cfg
from modifiers.insert_background import add_background
from modifiers.insert_icon import generate_final_images
from modifiers.insert_banner import add_banner

def run():
    print("Starting Theme Update ...")

    config = load_config()
    print(config)
    
    # For testing purposes, we will use the parsed grub.cfg entries instead of the config.json ones.
    entries = config.get("menu-entries", [])
    #entries = parse_grub_cfg(config, True)
    #print(entries)

    # LOAD BASE IMAGE
    base_image = load_image(BASE_IMAGE)

    # Add background to base image
    current_image = add_background(base_image, config)

    # Add banner image
    current_image = add_banner(current_image, config)

    save_image(current_image, "test.png")
    # TODO: Add icons entries with the info of entries.
    #generate_final_images(entries, current_image)