import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"(def on_cal_w_changed\(self, text\):\s*try:\s*val = float\(text\)\s*if val > 0:\s*self\.cal_default_w = val)"
replacement = r"\1\n                self.reset_cal_to_nominal()\n                if hasattr(self.ui, 'nominalfieldLabel'):\n                    self.ui.nominalfieldLabel.setText(f'Nominal Field: {2*val:.2f} x {2*val:.2f} mm')"

content = re.sub(pattern, replacement, content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
