import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_status = r"            if loaded_ok:\n                self.set_cal_status\(\"Status : Calibrated \+ Loaded\"\)\n            else:\n                self.set_cal_status\(\"Status : Calibrated \(Not Loaded\)\"\)"

new_status = r"""            if loaded_ok:
                self.set_cal_status(f"Status : Calibrated (Residual Error: ±{avg_err:.3f} mm)")
            else:
                self.set_cal_status("Status : Calibrated (Not Loaded)")"""

content = re.sub(old_status, new_status, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
