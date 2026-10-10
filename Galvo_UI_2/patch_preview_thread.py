import re

with open('galvo_threads.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Modify PreviewThread.run to include DAC=0 and crosshair
old_run = r"""    def run\(self\):\n        speed = 2000000\n        if hasattr\(self\.controller\.connection, 'laser_off'\):\n            self\.controller\.connection\.laser_off\(\)\n        if hasattr\(self\.controller\.connection, 'reddot_on'\):\n            self\.controller\.connection\.reddot_on\(\)"""

new_run = r"""    def run(self):
        speed = 2000000
        if hasattr(self.controller.connection, 'laser_off'):
            self.controller.connection.laser_off()
        if hasattr(self.controller.connection, 'set_analog_do_bit'):
            self.controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
        if hasattr(self.controller.connection, 'reddot_on'):
            self.controller.connection.reddot_on()"""

content = re.sub(old_run, new_run, content)

old_draw = r"""                # Swap X and Y to match the 90deg CCW \+ mirror transform applied during marking\n                dll_obj\.GT_PROSYS_U3_galvo_move_XY\(int\(self\.min_y\), int\(self\.min_x\), speed, 0\.0, 0\.0, 0\.0\)\n                dll_obj\.GT_PROSYS_U3_galvo_move_XY\(int\(self\.min_y\), int\(self\.max_x\), speed, 0\.0, 0\.0, 0\.0\)\n                dll_obj\.GT_PROSYS_U3_galvo_move_XY\(int\(self\.max_y\), int\(self\.max_x\), speed, 0\.0, 0\.0, 0\.0\)\n                dll_obj\.GT_PROSYS_U3_galvo_move_XY\(int\(self\.max_y\), int\(self\.min_x\), speed, 0\.0, 0\.0, 0\.0\)\n                dll_obj\.GT_PROSYS_U3_galvo_move_XY\(int\(self\.min_y\), int\(self\.min_x\), speed, 0\.0, 0\.0, 0\.0\)"""

new_draw = r"""                # Swap X and Y to match the 90deg CCW + mirror transform applied during marking
                c_y = int((self.min_y + self.max_y) / 2)
                c_x = int((self.min_x + self.max_x) / 2)
                
                # Outer box
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_y), int(self.min_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_y), int(self.max_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.max_y), int(self.max_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.max_y), int(self.min_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_y), int(self.min_x), speed, 0.0, 0.0, 0.0)
                
                # Crosshair
                dll_obj.GT_PROSYS_U3_galvo_move_XY(c_y, int(self.min_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(c_y, int(self.max_x), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(c_y, c_x, speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_y), c_x, speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.max_y), c_x, speed, 0.0, 0.0, 0.0)"""

content = re.sub(old_draw, new_draw, content)

with open('galvo_threads.py', 'w', encoding='utf-8') as f:
    f.write(content)
