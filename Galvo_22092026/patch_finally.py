import re
with open('machine/galvo_controller.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_indent(s):
    return len(s) - len(s.lstrip())

start_idx = -1
for i, line in enumerate(lines):
    if "for loop_idx in range(loop_count):" in line:
        start_idx = i
        break

if start_idx != -1:
    indent = get_indent(lines[start_idx])
    lines.insert(start_idx, " " * indent + "try:\n")
    for i in range(start_idx + 1, len(lines)):
        if get_indent(lines[i]) >= indent:
            if lines[i].strip():
                lines[i] = "    " + lines[i]
        else:
            if lines[i].strip() == "": continue
            break
            
    # Add finally block
    finally_idx = i
    lines.insert(finally_idx, " " * indent + "finally:\n")
    lines.insert(finally_idx + 1, " " * (indent + 4) + "if hasattr(self.connection, 'laser_off'):\n")
    lines.insert(finally_idx + 2, " " * (indent + 8) + "self.connection.laser_off()\n")
    lines.insert(finally_idx + 3, " " * (indent + 4) + "if hasattr(self.connection, 'set_analog_do_bit'):\n")
    lines.insert(finally_idx + 4, " " * (indent + 8) + "self.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)\n")

with open('machine/galvo_controller.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
