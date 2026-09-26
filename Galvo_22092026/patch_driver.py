import re

with open('machine/galvo_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_jump = r"""                            # Apply 90 deg CCW rotation \+ horizontal mirror = Swap X and Y\n                            cmd_x = cmd\['y'\]\n                            cmd_y = cmd\['x'\]"""

new_jump = r"""                            # Apply True 90 deg CCW transformation to match screen coordinates to physical galvo
                            cmd_x = cmd['y']
                            cmd_y = 65534 - cmd['x']"""

content = re.sub(old_jump, new_jump, content)

with open('machine/galvo_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
