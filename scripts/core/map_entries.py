

from scripts.helpers.grub_parser import map_entries_to_grub_cfg
from scripts.helpers.utils import ENTRIES_CONFIG_PATH, load_config



def run():
    print("Mapping entries onto grub.cfg ...")
    # Load entries config and parse grub.cfg
    config = load_config()

    entries = config.get("entries", [])
    map_entries_to_grub_cfg(entries)