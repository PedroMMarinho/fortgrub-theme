import re
import os
import json
from helpers.utils import THEME_CONFIG_PATH
import shlex

GRUB_CFG_PATH = '/boot/grub/grub.cfg'


def parse_grub_cfg(config, save_to_config = True, cfg_path=GRUB_CFG_PATH):
    if not os.path.exists(cfg_path):
        print(f"❌ Error: grub.cfg not found at {cfg_path}")
        return []

    with open(cfg_path, 'r') as f:
        lines = f.readlines()

    entries = []
    stack = [entries]

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        try:
            tokens = shlex.split(clean_line, comments=True)
        except ValueError:
            continue
            
        if not tokens:
            continue

        if tokens[0] == '}':
            if len(stack) > 1:
                stack.pop()
            continue

        if tokens[0] in ['menuentry', 'submenu']:
            current_name = tokens[1]
            entry_type = tokens[0]
            
            classes = []
            for i, token in enumerate(tokens):
                if token == '--class' and i + 1 < len(tokens):
                    classes.append(tokens[i+1])
            
            new_entry = {
                "name": current_name,
                "type": entry_type,
                "class": classes,
                "children": []
            }
            
            if isinstance(stack[-1], list):
                stack[-1].append(new_entry)

            if tokens[-1] == '{':
                if entry_type == 'submenu':
                    stack.append(new_entry['children'])
                else:
                    stack.append("IGNORE")
    if save_to_config:
        config['menu-entries'] = entries
        with open(THEME_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)

    return entries


    
