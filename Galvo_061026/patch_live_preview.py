import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add signal connection in setupAdvancedCalibration
old_connect = r"""            if le_y:\n                le_y\.setValidator\(QDoubleValidator\(-1000\.0, 1000\.0, 3, self\)\)\n                self\.cal_inputs_y\.append\(le_y\)"""

new_connect = r"""            if le_y:
                le_y.setValidator(QDoubleValidator(-1000.0, 1000.0, 3, self))
                self.cal_inputs_y.append(le_y)
            if le_x: le_x.textChanged.connect(self.update_cal_preview)
            if le_y: le_y.textChanged.connect(self.update_cal_preview)"""

content = re.sub(old_connect, new_connect, content)

# Add update_cal_preview function
new_func = r"""    def update_cal_preview(self):
        if not hasattr(self, 'cal_preview'): return
        
        from core.calibration_generator_ui import TRANSFORMS
        transform = TRANSFORMS[self.cal_state_idx]
        
        pts = [(0, 0)] * 9
        for i in range(9):
            x_text = self.cal_inputs_x[i].text().strip() if i < len(self.cal_inputs_x) else "0.0"
            y_text = self.cal_inputs_y[i].text().strip() if i < len(self.cal_inputs_y) else "0.0"
            
            try: x = float(x_text or 0.0)
            except ValueError: x = 0.0
            try: y = float(y_text or 0.0)
            except ValueError: y = 0.0
            
            # Undo the orientation transform for rendering since the renderer maps it back!
            pts[i] = (x, y)
            
        self.cal_preview.set_measured_points(self.cal_default_w, pts)
        
    def reset_cal_to_nominal"""

content = content.replace("    def reset_cal_to_nominal", new_func)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
