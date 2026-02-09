import re
import os

GRUB_CFG_PATH = '/boot/grub/grub.cfg'

def parse_grub_cfg(cfg_path=GRUB_CFG_PATH):
    """
    Parses a grub.cfg file and returns a structured list of entries.
    """
    if not os.path.exists(cfg_path):
        print(f"❌ Error: grub.cfg not found at {cfg_path}")
        return []

    with open(cfg_path, 'r') as f:
        lines = f.readlines()

    entries = []
    
    stack = [entries]

    pattern = re.compile(r"^\s*(menuentry|submenu)\s+['\"]([^'\"]+)['\"](.*)\{")
    
    class_pattern = re.compile(r"--class\s+([\w-]+)")

    for line in lines:
        line = line.strip()

        match = pattern.search(line)
        if match:
            entry_type = match.group(1)  
            entry_name = match.group(2)  
            rest_of_line = match.group(3)

            classes = class_pattern.findall(rest_of_line)
            
            new_entry = {
                "name": entry_name,
                "type": entry_type,
                "class": classes,
                "children": [] 
            }

            current_context = stack[-1]
            current_context.append(new_entry)

            if entry_type == 'submenu':
                stack.append(new_entry['children'])
        
        elif line.startswith("}") and len(stack) > 1:
            stack.pop()

    return entries