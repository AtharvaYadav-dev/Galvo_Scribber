import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any line containing self.left_menu_widgets.<deleted_key> with a commented out version or just pass
deleted_keys = ["home", "laser", "programs", "print", "camera", "camerajog", "terminal"]

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'self.left_menu_widgets.' in line:
        for key in deleted_keys:
            if f'self.left_menu_widgets.{key}' in line:
                lines[i] = '# ' + line
                break

with open('main.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
