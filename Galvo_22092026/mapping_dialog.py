from PyQt6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
    QPushButton, QGroupBox, QGridLayout, QComboBox, QWidget, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QRectF, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

from core.motion_planner import MotionPlanner

class GridPreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.grid_data = [] # List of dicts with r, c, rect, power, freq
        self.active_cell = None
        self.field_size = 110.0 # default
        
    def set_field_size(self, size):
        self.field_size = size
        self.update()

    def update_grid(self, grid_data):
        self.grid_data = grid_data
        self.update()

    def set_active_cell(self, r, c):
        self.active_cell = (r, c)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.black)
        
        if not self.grid_data:
            return

        max_x = max((d['rect'].right() for d in self.grid_data), default=0)
        max_y = max((d['rect'].bottom() for d in self.grid_data), default=0)
        min_x = min((d['rect'].left() for d in self.grid_data), default=0)
        min_y = min((d['rect'].top() for d in self.grid_data), default=0)
        
        # Consider the field size as the max bounds to scale
        cx = (max_x + min_x) / 2
        cy = (max_y + min_y) / 2
        
        # scale based on field size
        scale_x = self.width() / (self.field_size * 1.1)
        scale_y = self.height() / (self.field_size * 1.1)
        scale = min(scale_x, scale_y)

        # Field bounding box (centered on grid center)
        offset_x = self.width() / 2 - (cx * scale)
        offset_y = self.height() / 2 - (cy * scale)
        
        # Draw field boundary
        field_rect = QRectF(self.width()/2 - (self.field_size/2)*scale, 
                            self.height()/2 - (self.field_size/2)*scale,
                            self.field_size*scale, self.field_size*scale)
        painter.setPen(QPen(Qt.green, 2, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(field_rect)
        
        # Draw "Field Limit" text
        painter.setPen(Qt.green)
        painter.drawText(field_rect.bottomLeft() + QPointF(5, -5), f"Field Limit ({self.field_size}x{self.field_size} mm)")

        if max_x == 0 or max_y == 0:
            return

        for cell in self.grid_data:
            r = cell['r']
            c = cell['c']
            rect = cell['rect']
            power = cell['power']
            
            sr = QRectF(offset_x + rect.x() * scale, offset_y + rect.y() * scale,
                        rect.width() * scale, rect.height() * scale)

            if self.active_cell == (r, c):
                painter.setPen(QPen(Qt.red, 2))
                painter.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
            else:
                intensity = int(255 * (power / 100.0))
                color = QColor(255, 0, 0, intensity)
                painter.setPen(QPen(Qt.white, 1))
                painter.setBrush(QBrush(color, Qt.SolidPattern))
            
            painter.drawRect(sr)

class ParameterMappingDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parameter Mapping Matrix")
        self.resize(800, 600)
        self.main_window = main_window
        self.galvo = main_window.galvo_controller
        self.is_running = False
        self.is_aborted = False
        
        try:
            self.field_size = self.main_window.galvo_config.field_size
        except AttributeError:
            self.field_size = 110.0
            
        self.setup_ui()
        self.canvas.set_field_size(self.field_size)
        self.generate_matrix()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Config Panel
        config_layout = QVBoxLayout()
        
        # Power (X-Axis)
        power_group = QGroupBox("Power (%) - X Axis")
        power_layout = QGridLayout()
        power_layout.addWidget(QLabel("Start:"), 0, 0)
        self.power_start = QLineEdit("10.0")
        power_layout.addWidget(self.power_start, 0, 1)
        power_layout.addWidget(QLabel("End:"), 1, 0)
        self.power_end = QLineEdit("90.0")
        power_layout.addWidget(self.power_end, 1, 1)
        power_layout.addWidget(QLabel("Steps:"), 2, 0)
        self.power_steps = QLineEdit("5")
        power_layout.addWidget(self.power_steps, 2, 1)
        power_group.setLayout(power_layout)
        config_layout.addWidget(power_group)

        # Frequency (Y-Axis)
        freq_group = QGroupBox("Frequency (kHz) - Y Axis")
        freq_layout = QGridLayout()
        freq_layout.addWidget(QLabel("Start:"), 0, 0)
        self.freq_start = QLineEdit("20.0")
        freq_layout.addWidget(self.freq_start, 0, 1)
        freq_layout.addWidget(QLabel("End:"), 1, 0)
        self.freq_end = QLineEdit("80.0")
        freq_layout.addWidget(self.freq_end, 1, 1)
        freq_layout.addWidget(QLabel("Steps:"), 2, 0)
        self.freq_steps = QLineEdit("5")
        freq_layout.addWidget(self.freq_steps, 2, 1)
        freq_group.setLayout(freq_layout)
        config_layout.addWidget(freq_group)

        # Geometry
        geom_group = QGroupBox("Cell Geometry")
        geom_layout = QGridLayout()
        geom_layout.addWidget(QLabel("Width (mm):"), 0, 0)
        self.cell_w = QLineEdit("5.0")
        geom_layout.addWidget(self.cell_w, 0, 1)
        geom_layout.addWidget(QLabel("Height (mm):"), 1, 0)
        self.cell_h = QLineEdit("5.0")
        geom_layout.addWidget(self.cell_h, 1, 1)
        geom_layout.addWidget(QLabel("Gap X (mm):"), 2, 0)
        self.gap_x = QLineEdit("2.0")
        geom_layout.addWidget(self.gap_x, 2, 1)
        geom_layout.addWidget(QLabel("Gap Y (mm):"), 3, 0)
        self.gap_y = QLineEdit("2.0")
        geom_layout.addWidget(self.gap_y, 3, 1)
        geom_layout.addWidget(QLabel("Fill Type:"), 4, 0)
        self.fill_type = QComboBox()
        self.fill_type.addItems(["Filled Rectangle", "Vector Outline"])
        geom_layout.addWidget(self.fill_type, 4, 1)
        self.label_axes = QCheckBox("Label axes with parameter values")
        geom_layout.addWidget(self.label_axes, 5, 0, 1, 2)
        geom_group.setLayout(geom_layout)
        config_layout.addWidget(geom_group)

        # Controls
        self.btn_preview = QPushButton("Red Mark (F1 / Preview)")
        self.btn_preview.clicked.connect(self.run_preview)
        self.btn_mark = QPushButton("Laser Mark (F2 / Execute)")
        self.btn_mark.clicked.connect(self.run_mark)
        self.btn_stop = QPushButton("Stop / Abort (Esc)")
        self.btn_stop.clicked.connect(self.abort)
        
        config_layout.addWidget(self.btn_preview)
        config_layout.addWidget(self.btn_mark)
        config_layout.addWidget(self.btn_stop)
        config_layout.addStretch()

        # Canvas
        self.canvas = GridPreviewCanvas()
        
        main_layout.addLayout(config_layout)
        main_layout.addWidget(self.canvas, 1)

        # Update preview when config changes
        for le in [self.power_start, self.power_end, self.power_steps,
                   self.freq_start, self.freq_end, self.freq_steps,
                   self.cell_w, self.cell_h, self.gap_x, self.gap_y]:
            le.textChanged.connect(self.generate_matrix)

    def generate_matrix(self):
        try:
            p_start = float(self.power_start.text())
            p_end = float(self.power_end.text())
            p_steps = max(1, int(self.power_steps.text()))
            
            f_start = float(self.freq_start.text())
            f_end = float(self.freq_end.text())
            f_steps = max(1, int(self.freq_steps.text()))
            
            cw = float(self.cell_w.text())
            ch = float(self.cell_h.text())
            gx = float(self.gap_x.text())
            gy = float(self.gap_y.text())
        except ValueError:
            return

        self.grid_data = []
        for r in range(f_steps):
            for c in range(p_steps):
                x = c * (cw + gx)
                y = r * (ch + gy)
                rect = QRectF(x, y, cw, ch)
                
                # interpolate power and freq
                if p_steps > 1:
                    power = p_start + (p_end - p_start) * (c / (p_steps - 1))
                else:
                    power = p_start
                    
                if f_steps > 1:
                    freq = f_start + (f_end - f_start) * (r / (f_steps - 1))
                else:
                    freq = f_start
                    
                self.grid_data.append({
                    'r': r, 'c': c,
                    'rect': rect,
                    'power': power,
                    'freq': freq
                })

        # Calculate bounding box and check limits
        if self.grid_data:
            max_x = max((d['rect'].right() for d in self.grid_data), default=0)
            max_y = max((d['rect'].bottom() for d in self.grid_data), default=0)
            
            if max_x > self.field_size or max_y > self.field_size:
                self.btn_preview.setEnabled(False)
                self.btn_mark.setEnabled(False)
                self.btn_mark.setText("Matrix Exceeds Field bounds!")
            else:
                self.btn_preview.setEnabled(True)
                self.btn_mark.setEnabled(True)
                self.btn_mark.setText("Laser Mark (F2 / Execute)")

        self.canvas.update_grid(self.grid_data)

    def draw_digit_lines(self, d, cx, cy, planner, scale=1.0):
        # A simple digit drawer mimicking main.py for labels
        dw = int(1.0 * scale)
        dh = int(2.0 * scale)
        x0 = cx - dw
        x1 = cx + dw
        y0 = cy + dh
        y1 = cy
        y2 = cy - dh
        
        def mark(x, y):
            planner.add_mark(x, y)
        def jump(x, y):
            planner.add_jump(x, y)

        if d == 1: jump(x1, y0); mark(x1, y2)
        elif d == 2: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); mark(x0, y2); mark(x1, y2)
        elif d == 3: jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); jump(x1, y1); mark(x1, y2); mark(x0, y2)
        elif d == 4: jump(x0, y0); mark(x0, y1); mark(x1, y1); jump(x1, y0); mark(x1, y2)
        elif d == 5: jump(x1, y0); mark(x0, y0); mark(x0, y1); mark(x1, y1); mark(x1, y2); mark(x0, y2)
        elif d == 6: jump(x1, y0); mark(x0, y0); mark(x0, y2); mark(x1, y2); mark(x1, y1); mark(x0, y1)
        elif d == 7: jump(x0, y0); mark(x1, y0); mark(x1, y2)
        elif d == 8: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0); jump(x0, y1); mark(x1, y1)
        elif d == 9: jump(x1, y1); mark(x0, y1); mark(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2)
        elif d == 0: jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0)

    def draw_number(self, num_val, cx, cy, planner, scale=1.0):
        # Break number to digits
        s = str(int(num_val))
        cw = 3.0 * scale
        start_x = cx - (len(s) - 1) * cw / 2.0
        for i, char in enumerate(s):
            if char.isdigit():
                self.draw_digit_lines(int(char), start_x + i * cw, cy, planner, scale)

    def _execute(self, is_preview=False):
        if self.is_running:
            return
        
        try:
            field_size = self.main_window.galvo_config.field_size
            scale = 65535.0 / field_size
        except AttributeError:
            scale = 533.89
            
        center_xy = 32767
        
        planner = MotionPlanner()
        planner.preview_queue = [] # clear
        self.cmd_to_cell = {} # maps queue index to (r, c)

        # Precalculate bounds
        if not self.grid_data:
            return
            
        max_x = max(d['rect'].right() for d in self.grid_data)
        max_y = max(d['rect'].bottom() for d in self.grid_data)
        
        # Shift to center
        cx = max_x / 2.0
        cy = max_y / 2.0

        try:
            jump_speed = int(self.main_window.wh.invokeMethod(self.main_window.programgalvo_widgets.pgmjumpspeed, "get") or 2000000)
            mark_speed = int(self.main_window.wh.invokeMethod(self.main_window.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000000)
        except Exception:
            jump_speed = 2000000
            mark_speed = 1000000

        for cell in self.grid_data:
            r = cell['rect']
            power = cell['power']
            freq = cell['freq']
            
            x0 = (r.left() - cx) * scale + center_xy
            y0 = (r.top() - cy) * scale + center_xy
            w = r.width() * scale
            h = r.height() * scale
            
            x1 = x0 + w
            y1 = y0 + h

            # Record start index of this cell
            start_idx = len(planner.preview_queue)

            if not is_preview:
                planner.preview_queue.append({
                    'type': 'set_params',
                    'power': power,
                    'freq': freq
                })

            if is_preview or self.fill_type.currentText() == "Vector Outline":
                planner.add_jump(x0, y0, speed=jump_speed)
                planner.add_mark(x1, y0, speed=mark_speed)
                planner.add_mark(x1, y1, speed=mark_speed)
                planner.add_mark(x0, y1, speed=mark_speed)
                planner.add_mark(x0, y0, speed=mark_speed)
            else:
                poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                p = self.main_window.hatch_profiles[1]
                cfg = {
                    'enable': True,
                    'follow_edge': p.get("follow_edge", False) == 'true' if isinstance(p.get("follow_edge", False), str) else p.get("follow_edge", False),
                    'all_calc': p.get("all_calc", False) == 'true' if isinstance(p.get("all_calc", False), str) else p.get("all_calc", False),
                    'cross_hatch': p.get("cross_hatch", False) == 'true' if isinstance(p.get("cross_hatch", False), str) else p.get("cross_hatch", False),
                    'type': "Bidirectional",
                    'angle': float(p.get("angle", "0.0") or 0.0),
                    'pen_no': 0,
                    'count': int(p.get("count", "1") or 1),
                    'line_space': float(p.get("line_space", "0.05") or 0.05),
                    'avg_distribute': p.get("avg_dist", False) == 'true' if isinstance(p.get("avg_dist", False), str) else p.get("avg_dist", False),
                    'edge_offset': float(p.get("edge_off", "0.0") or 0.0),
                    'start_offset': float(p.get("start_off", "0.0") or 0.0),
                    'end_offset': float(p.get("end_off", "0.0") or 0.0),
                    'line_reduction': float(p.get("line_red", "0.0") or 0.0),
                    'num_loops': int(p.get("num_loops", "0") or 0),
                    'loop_distance': float(p.get("loop_dist", "0.05") or 0.05),
                    'auto_rotate': p.get("auto_rot", False) == 'true' if isinstance(p.get("auto_rot", False), str) else p.get("auto_rot", False),
                    'rotate_angle': float(p.get("rot_angle", "10.0") or 10.0),
                    'hatch_idx': 1
                }
                planner.generate_hatch([poly], [cfg], mark_speed=mark_speed, jump_speed=jump_speed, galvo_units_per_mm=scale)
                
            # Map all generated commands to this cell
            end_idx = len(planner.preview_queue)
            for i in range(start_idx, end_idx):
                self.cmd_to_cell[i] = (cell['r'], cell['c'])
                
            # Labels (only drawn once, ideally, but for simplicity we can draw next to cells)
            if self.label_axes.isChecked():
                # Draw Y axis label on first column
                if cell['c'] == 0:
                    lbl_x = x0 - (5.0 * scale)
                    lbl_y = y0 + h/2.0
                    self.draw_number(freq, lbl_x, lbl_y, planner, scale=scale*0.5)
                # Draw X axis label on last row
                max_r = max(d['r'] for d in self.grid_data)
                if cell['r'] == max_r:
                    lbl_x = x0 + w/2.0
                    lbl_y = y1 + (5.0 * scale)
                    self.draw_number(power, lbl_x, lbl_y, planner, scale=scale*0.5)

        self.is_aborted = False
        self.is_running = True

        if is_preview:
            # Convert marks to jumps for red light preview so we don't fire the laser
            for cmd in planner.preview_queue:
                if cmd.get('type') == 'mark':
                    cmd['type'] = 'jump'
                    
            # Enable reddot, hard-lock Q-Switch (usually galvo_controller reddot_on does this)
            if hasattr(self.galvo, 'connection') and self.galvo.connection:
                if hasattr(self.galvo.connection, 'reddot_on'):
                    self.galvo.connection.reddot_on()
        else:
            self.main_window.set_cal_status("Status: Marking Matrix...")
            
        success = self.galvo.execute_queue(
            planner.preview_queue,
            loop_count=999999 if is_preview else 1,
            abort_check=lambda: self.is_aborted,
            progress_callback=self._progress_cb
        )

        if is_preview:
            if hasattr(self.galvo, 'connection') and self.galvo.connection:
                if hasattr(self.galvo.connection, 'reddot_off'):
                    self.galvo.connection.reddot_off()
            
        if hasattr(self.galvo, 'connection') and self.galvo.connection:
            if hasattr(self.galvo.connection, 'laser_off'):
                self.galvo.connection.laser_off()
        self.is_running = False

    def _progress_cb(self, idx, total, x, y, ctype):
        if idx in self.cmd_to_cell:
            r, c = self.cmd_to_cell[idx]
            if self.canvas.active_cell != (r, c):
                self.canvas.set_active_cell(r, c)
        QApplication.processEvents()

    def run_preview(self):
        self._execute(is_preview=True)

    def run_mark(self):
        self._execute(is_preview=False)

    def abort(self):
        self.is_aborted = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.abort()
        elif event.key() == Qt.Key_F1:
            self.run_preview()
        elif event.key() == Qt.Key_F2:
            self.run_mark()
        else:
            super().keyPressEvent(event)
