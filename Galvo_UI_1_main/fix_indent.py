import sys

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if "inverted_power = self.galvo_controller.connection.map_laser_power(float(pwr))" in lines[i]:
        if not lines[i].startswith("                            inverted_power"):
            lines[i] = "                            " + lines[i].lstrip()

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
