import re
with open('core/connection/hardware.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"\s*def map_laser_power.*?return 100\.0 - float\(mapped\)\n"
content = re.sub(pattern, "\n", content, flags=re.DOTALL)

with open('core/connection/hardware.py', 'w', encoding='utf-8') as f:
    f.write(content)
