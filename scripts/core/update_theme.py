import os
from helpers.utils import load_config
from helpers.grub_parser import parse_grub_cfg

def run():
    print("Starting Theme Update ...")

    config = load_config()
    print(config)
    
    entries = parse_grub_cfg()
    print(entries)

    