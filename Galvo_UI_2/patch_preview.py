import re

with open('core/calibration_generator_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add measured_points to GridPreviewWidget
old_init = r"""    def __init__\(self, parent=None\):\n        super\(\)\.__init__\(parent\)\n        self\.setMinimumSize\(320, 320\)\n        self\.state_idx = 0"""

new_init = r"""    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.state_idx = 0
        self.measured_points = None
        self.nominal_w = 30.0"""

content = re.sub(old_init, new_init, content)

old_set_state = r"""    def set_state\(self, idx\):\n        self\.state_idx = idx % 8\n        self\.update\(\)"""

new_set_state = r"""    def set_state(self, idx):
        self.state_idx = idx % 8
        self.update()
        
    def set_measured_points(self, w, points):
        self.nominal_w = w
        self.measured_points = points
        self.update()"""

content = re.sub(old_set_state, new_set_state, content)

# Add drawing logic to paintEvent
old_draw = r"""        # 3\. Center tick mark\n        t1 = cur\["tick_p1"\]\n        t2 = cur\["tick_p2"\]\n        p1x, p1y = map_norm\(t1\[0\], t1\[1\]\)\n        p2x, p2y = map_norm\(t2\[0\], t2\[1\]\)\n        painter\.setPen\(QPen\(QColor\(20, 20, 20\), 3\)\)\n        painter\.drawLine\(int\(p1x\), int\(p1y\), int\(p2x\), int\(p2y\)\)"""

new_draw = r"""        # 3. Center tick mark
        t1 = cur["tick_p1"]
        t2 = cur["tick_p2"]
        p1x, p1y = map_norm(t1[0], t1[1])
        p2x, p2y = map_norm(t2[0], t2[1])
        painter.setPen(QPen(QColor(20, 20, 20), 3))
        painter.drawLine(int(p1x), int(p1y), int(p2x), int(p2y))
        
        # Draw distorted mesh if available
        if self.measured_points and len(self.measured_points) == 9:
            painter.setPen(QPen(QColor(255, 0, 0, 180), 2, Qt.DashLine))
            
            def map_meas(mx, my):
                if self.nominal_w == 0: return cx, cy
                nx = mx / self.nominal_w
                ny = my / self.nominal_w
                return map_norm(nx, ny)
                
            pts = []
            for mx, my in self.measured_points:
                pts.append(map_meas(mx, my))
                
            # Draw horizontal lines
            painter.drawLine(int(pts[0][0]), int(pts[0][1]), int(pts[1][0]), int(pts[1][1]))
            painter.drawLine(int(pts[1][0]), int(pts[1][1]), int(pts[2][0]), int(pts[2][1]))
            painter.drawLine(int(pts[3][0]), int(pts[3][1]), int(pts[4][0]), int(pts[4][1]))
            painter.drawLine(int(pts[4][0]), int(pts[4][1]), int(pts[5][0]), int(pts[5][1]))
            painter.drawLine(int(pts[6][0]), int(pts[6][1]), int(pts[7][0]), int(pts[7][1]))
            painter.drawLine(int(pts[7][0]), int(pts[7][1]), int(pts[8][0]), int(pts[8][1]))
            
            # Draw vertical lines
            painter.drawLine(int(pts[0][0]), int(pts[0][1]), int(pts[3][0]), int(pts[3][1]))
            painter.drawLine(int(pts[3][0]), int(pts[3][1]), int(pts[6][0]), int(pts[6][1]))
            painter.drawLine(int(pts[1][0]), int(pts[1][1]), int(pts[4][0]), int(pts[4][1]))
            painter.drawLine(int(pts[4][0]), int(pts[4][1]), int(pts[7][0]), int(pts[7][1]))
            painter.drawLine(int(pts[2][0]), int(pts[2][1]), int(pts[5][0]), int(pts[5][1]))
            painter.drawLine(int(pts[5][0]), int(pts[5][1]), int(pts[8][0]), int(pts[8][1]))
            
            # Draw points
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            for px, py in pts:
                painter.drawEllipse(int(px) - 3, int(py) - 3, 6, 6)"""

content = re.sub(old_draw, new_draw, content)

with open('core/calibration_generator_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
