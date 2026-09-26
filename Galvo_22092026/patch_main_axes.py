import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# For draw_cal_pattern
old_draw = r"""        # Invert the X/Y swap introduced in execute_queue so the calibration grid marks strictly \n        # aligned with the raw physical hardware axes without the user's \"print\" rotation preference\.\n        def jump\(x, y\): \n            x_inv = \(2 \* c\) - x\n            queue\.append\(\{'type': 'jump', 'x': int\(y\), 'y': int\(x_inv\), 'speed': jump_speed\}\)\n        def mark\(x, y\): \n            x_inv = \(2 \* c\) - x\n            queue\.append\(\{'type': 'mark', 'x': int\(y\), 'y': int\(x_inv\), 'speed': mark_speed\}\)"""

new_draw = r"""        # Send raw coordinates; the execute_queue CCW transform now correctly aligns the screen to hardware
        def jump(x, y): 
            queue.append({'type': 'jump', 'x': int(x), 'y': int(y), 'speed': jump_speed})
        def mark(x, y): 
            queue.append({'type': 'mark', 'x': int(x), 'y': int(y), 'speed': mark_speed})"""

content = re.sub(old_draw, new_draw, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
