import os
from helpers.utils import load_config, ENTRIES_CONFIG_PATH, DEFAULT_ENTRY_CONFIG_PATH, get_package_count, save_config
from helpers.grub_parser import parse_grub_cfg
import copy


def run():
    print("Starting Theme Setup ...")

    # Load main config
    config = {}

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
    config["season"] = "3"
    
    config["missions"] = {
        "battlepass" : {
            "description": "I Use Arch btw!",
            "current-stars": 1,
            "total-stars": 1,
            "star-reward": 10,
        },
        "daily1" : {
            "description": "Search 7 Chests in Risky Reels",
            "current-stars": 1,
            "total-stars": 7,
            "star-reward": 5,
            "xp-reward": 500

        },
        "daily2" : {
            "description": "Get a low taper fade, it's still massive",
            "current-stars": 0,
            "total-stars": 1,
            "star-reward": 5,
            "xp-reward": 1000

        },
        "daily3" : {
            "description": "Eliminate 3 opponents in Tilted Towers",
            "current-stars": 2,
            "total-stars": 3,
            "star-reward": 5,
            "xp-reward": 500
        },
    }

    config["entries"] = entries

    save_config(config)

    print("Theme setup completed successfully!")
    print("Checkout the config.json file to customize the theme how you want !!!")
    print("When statisfied with the config, run 'make generate' to create the theme")


def apply_defaults(entries, default_config):
    for entry in entries:
        entry.update(copy.deepcopy(default_config))
        
        if "children" in entry and entry["children"]:
            apply_defaults(entry["children"], default_config)