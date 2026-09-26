import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix reset_cal_to_nominal
old_reset = r"""    def reset_cal_to_nominal\(self\):\n        w = self\.cal_default_w\n        default_vals = \[\n            \(w, w\), \(0, w\), \(w, w\),\n            \(w, 0\), \(0, 0\), \(w, 0\),\n            \(w, w\), \(0, w\), \(w, w\)\n        \]"""

new_reset = r"""    def reset_cal_to_nominal(self):
        w = self.cal_default_w
        default_vals = [
            (-w, w), (0, w), (w, w),
            (-w, 0), (0, 0), (w, 0),
            (-w, -w), (0, -w), (w, -w)
        ]"""

content = re.sub(old_reset, new_reset, content)

# Fix generate_calibration signs
old_gen = r"""            sx, sy = signs\[galvo_idx\]\n            meas_x = raw_x \* sx if sx != 0 else 0\n            meas_y = raw_y \* sy if sy != 0 else 0\n\n            galvo_measurements\[galvo_idx\] = \(meas_x, meas_y\)"""

new_gen = r"""            # Use raw coordinates directly, as they now properly follow sign conventions
            galvo_measurements[galvo_idx] = (raw_x, raw_y)"""

content = re.sub(old_gen, new_gen, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
