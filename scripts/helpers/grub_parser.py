import re
import os
import json
from helpers.utils import ENTRIES_CONFIG_PATH
import shlex

GRUB_CFG_PATH = '/boot/grub/grub.cfg'


def parse_grub_cfg(config, save_to_config = True):
    if not os.path.exists(GRUB_CFG_PATH):
        print(f"❌ Error: grub.cfg not found at {GRUB_CFG_PATH}")
        return []

    with open(GRUB_CFG_PATH, 'r') as f:
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
                    class_value = tokens[i+1]
                    if not class_value.startswith('fortgrub'):
                        classes.append(class_value)
            
            new_entry = {
                "name": current_name,
                "type": entry_type,
                "class": classes,
                "children": [],
            }
            
            if isinstance(stack[-1], list):
                stack[-1].append(new_entry)

            if tokens[-1] == '{':
                if entry_type == 'submenu':
                    stack.append(new_entry['children'])
                else:
                    stack.append("IGNORE")
    
    if save_to_config:
        config["entries"] = entries
        with open(ENTRIES_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)

    return entries

def map_entries_to_grub_cfg(entries):
    if not os.path.exists(GRUB_CFG_PATH):
        print(f"❌ Error: grub.cfg not found at {GRUB_CFG_PATH}")
        return False

    def get_all_ids(entries):
        ids = []
        for entry in entries:
            ids.append(entry.get('id'))
            if entry.get('children'):
                ids.extend(get_all_ids(entry['children']))
        return ids
        
    ids = get_all_ids(entries)
    id_index = 0

    with open(GRUB_CFG_PATH, 'r') as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        clean_line = line.strip()
        
        if not clean_line.startswith(('menuentry', 'submenu')):
            new_lines.append(line)
            continue
            
        try:
            tokens = shlex.split(clean_line, comments=True)
        except ValueError:
            new_lines.append(line)
            continue
            
        if not tokens or tokens[0] not in ['menuentry', 'submenu']:
            new_lines.append(line)
            continue
            
        if id_index >= len(ids):
            new_lines.append(line)
            continue

        current_id = ids[id_index]
        id_index += 1
        
        new_tokens = []
        skip_next = False
        first_class_idx = -1
        
        for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue
                
            if token == '--class':
                if i + 1 < len(tokens) and tokens[i+1].startswith('fortgrub'):
                    skip_next = True
                    continue
                elif first_class_idx == -1:
                    first_class_idx = len(new_tokens)
                    
            new_tokens.append(token)
            
        if current_id:
            if first_class_idx != -1:
                new_tokens.insert(first_class_idx, '--class')
                new_tokens.insert(first_class_idx + 1, current_id)
            else:
                new_tokens.insert(2, '--class')
                new_tokens.insert(3, current_id)
                
        rebuilt_tokens = []
        for i, t in enumerate(new_tokens):
            if i == 1:
                rebuilt_tokens.append(f"'{t}'")
            elif ' ' in t or t == '':
                rebuilt_tokens.append(f"'{t}'")
            elif i > 0 and new_tokens[i-1] == '$menuentry_id_option':
                rebuilt_tokens.append(f"'{t}'")
            else:
                rebuilt_tokens.append(t)
                
        leading_spaces = len(line) - len(line.lstrip())
        rebuilt_line = (" " * leading_spaces) + " ".join(rebuilt_tokens) + "\n"
        new_lines.append(rebuilt_line)

    with open(GRUB_CFG_PATH, 'w') as f:
        f.writelines(new_lines)
        
    print(f"✅ Successfully mapped {id_index} entries into {GRUB_CFG_PATH}")
    return True