import os
from helpers.utils import load_config, load_image, save_image, BASE_IMAGE
from helpers.grub_parser import parse_grub_cfg
from helpers.background import add_background

def run():
    print("Starting Theme Update ...")

    config = load_config()
    print(config)
    
    entries = parse_grub_cfg(config, True)
    print(entries)

    # LOAD BASE IMAGE
    base_image = load_image(BASE_IMAGE)

    # Add background to base image
    current_image = add_background(base_image, config)

    save_image(current_image, "test.png")
