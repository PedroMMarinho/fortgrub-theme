import os
from helpers.utils import load_config, ENTRIES_CONFIG_PATH, DEFAULT_ENTRY_CONFIG_PATH, get_package_count, save_config
from helpers.grub_parser import parse_grub_cfg
import copy


def run():
    print("Starting Theme Setup ...")

    # Load main config
    config = load_config()

    # Load entries config and parse grub.cfg
    entries_config = load_config(ENTRIES_CONFIG_PATH)
    #print(entries_config)
    
    entries = parse_grub_cfg(entries_config, True)
    #print(entries)

    # Add defaults to all entries
    default_entry_config = load_config(DEFAULT_ENTRY_CONFIG_PATH)
    apply_defaults(entries, default_entry_config)

    # Add theme-specific values
    vbucks = get_package_count()
    background = "Batman.png"
    progress_bar_emoticon = "Emoji_Ace.png"

    config["vbucks"] = vbucks
    config["background"] = background
    config["progress-bar-emoticon"] = progress_bar_emoticon
    config["season"] = 3
    
    config["missions"] = {
        "battlepass" : {
            "description": "I Use Arch btw",
            "current-stars": 1,
            "total-stars": 1
        },
        "daily1" : {
            "description": "Search 7 Chests in Risky Reels",
            "current-stars": 1,
            "total-stars": 7
        },
        "daily2" : {
            "description": "I Use Arch btw",
            "current-stars": 2,
            "total-stars": 3
        },
        "daily3" : {
            "description": "Get a low taper fade (It's still massive)",
            "current-stars": 0,
            "total-stars": 1
        },
    }

    config["entries"] = entries

    save_config(config)

    print("Theme setup completed successfully!")
    print("Checkout the config.json file to customize the theme how you want !!!")
    print("When statisfied with the config, run 'make generate' to create the theme")

    # LOAD BASE IMAGE
    #base_image = load_image(BASE_IMAGE)

    # Add background to base image
    #current_image = add_background(base_image, config)

    # Add banner image
    #current_image, banner_img = add_banner(current_image, config)

    # Add vbucks info
    #current_image = add_vbucks(current_image, config)

    # Add level text
    #current_image = add_level_text(current_image, config)

    # Change progress bar emoticon
    #change_emoticon(config)

    #save_image(current_image, "test.png")

    # Generate final images
    #generate_final_images(config, current_image, banner_img)

    # TODO - Change grub.cfg or other file to have the class of that entry as the injected one. (e.g., fortgrub1, fortgrub2, etc)


def apply_defaults(entries, default_config):
    for entry in entries:
        entry.update(copy.deepcopy(default_config))
        
        if "children" in entry and entry["children"]:
            apply_defaults(entry["children"], default_config)