import sys
import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"set_analog_do_bit\(([^,]+),\s*([^,]+),\s*(float\(freq\)|freq_val)\s*/\s*4\.0,\s*3\)"
replacement = r"set_analog_do_bit(\1, \2, self.galvo_controller.connection.clamp_laser_freq(\3) / 4.0 if hasattr(self.galvo_controller.connection, 'clamp_laser_freq') else \3 / 4.0, 3)"

new_content = re.sub(pattern, replacement, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
