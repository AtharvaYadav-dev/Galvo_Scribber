import json
import re

with open('ui_interface.py', 'r', encoding='utf-8') as f:
    ui_content = f.read()

# Extract all button names from ui_interface.py
button_names = set(re.findall(r'self\.(\w+PushButton)\s*=\s*QPushButton\(', ui_content))

with open('style.json', 'r', encoding='utf-8') as f:
    style = json.load(f)

# Filter navigation buttons
for stacked in style.get('QStackedWidget', []):
    for nav in stacked.get('navigation', []):
        for btn_group in nav.get('navigationButtons', []):
            keys_to_delete = [k for k in btn_group.keys() if k.endswith('PushButton') and k not in button_names]
            for k in keys_to_delete:
                del btn_group[k]

# Filter push button groups
for btn_group in style.get('QPushButtonGroup', []):
    valid_buttons = [b for b in btn_group.get('Buttons', []) if b in button_names or not b.endswith('PushButton')]
    btn_group['Buttons'] = valid_buttons
    if btn_group.get('ActiveButton') not in valid_buttons:
        btn_group['ActiveButton'] = valid_buttons[0] if valid_buttons else ""

with open('style.json', 'w', encoding='utf-8') as f:
    json.dump(style, f, indent=4)
