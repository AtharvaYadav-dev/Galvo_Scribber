import os
import math
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QPushButton, QLineEdit, QMessageBox, QWidget, 
                               QGroupBox, QApplication, QFrame, QScrollArea, QSlider)
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PySide6.QtCore import Qt, QRect, QTimer
from core.calibration_generator import generate_cor_file

# 8 Standard EZCAD Orientations
# Mapping of screen positions to physical orientation:
EZCAD_ORIENTATIONS = [
    {"name": "1", "sq": (-1, 1),  "di": (1, -1),  "tick_p1": (0.15, -0.15), "tick_p2": (0.15, 0.15),  "tf": lambda x, y: (x, y)},
    {"name": "2", "sq": (1, 1),   "di": (-1, -1), "tick_p1": (-0.15, -0.15),"tick_p2": (-0.15, 0.15), "tf": lambda x, y: (-x, y)},
    {"name": "3", "sq": (1, -1),  "di": (-1, 1),  "tick_p1": (-0.15, 0.15), "tick_p2": (-0.15, -0.15),"tf": lambda x, y: (-x, -y)},
    {"name": "4", "sq": (-1, -1), "di": (1, 1),   "tick_p1": (0.15, 0.15),  "tick_p2": (0.15, -0.15), "tf": lambda x, y: (x, -y)},
    {"name": "5", "sq": (-1, -1), "di": (1, 1),   "tick_p1": (0.15, 0.15),  "tick_p2": (-0.15, 0.15), "tf": lambda x, y: (-y, x)},
    {"name": "6", "sq": (-1, 1),  "di": (1, -1),  "tick_p1": (0.15, -0.15), "tick_p2": (-0.15, -0.15),"tf": lambda x, y: (-y, -x)},
    {"name": "7", "sq": (1, 1),   "di": (-1, -1), "tick_p1": (-0.15, -0.15),"tick_p2": (0.15, -0.15), "tf": lambda x, y: (y, -x)},
    {"name": "8", "sq": (1, -1),  "di": (-1, 1),  "tick_p1": (-0.15, 0.15), "tick_p2": (0.15, 0.15),  "tf": lambda x, y: (y, x)},
]

TRANSFORMS = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8], # 1
    [2, 5, 8, 1, 4, 7, 0, 3, 6], # 2
    [8, 7, 6, 5, 4, 3, 2, 1, 0], # 3
    [6, 3, 0, 7, 4, 1, 8, 5, 2], # 4
    [2, 1, 0, 5, 4, 3, 8, 7, 6], # 5
    [6, 7, 8, 3, 4, 5, 0, 1, 2], # 6
    [0, 3, 6, 1, 4, 7, 2, 5, 8], # 7
    [8, 5, 2, 7, 4, 1, 6, 3, 0], # 8
]

TRANSFORMS_MATH = [
    lambda x, y: (x, y),
    lambda x, y: (y, -x),
    lambda x, y: (-x, -y),
    lambda x, y: (-y, x),
    lambda x, y: (-x, y),
    lambda x, y: (x, -y),
    lambda x, y: (-y, -x),
    lambda x, y: (y, x),
]


class GridPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.state_idx = 0
        
    def set_state(self, idx):
        self.state_idx = idx % 8
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        w, h = self.width(), self.height()
        margin = 35
        grid_w, grid_h = w - 2 * margin, h - 2 * margin
        cx, cy = w / 2.0, h / 2.0
        
        # Grid frame and crosshair
        pen = QPen(QColor(20, 20, 20), 2)
        painter.setPen(pen)
        painter.drawRect(margin, margin, grid_w, grid_h)
        painter.drawLine(int(cx), margin, int(cx), h - margin)
        painter.drawLine(margin, int(cy), w - margin, int(cy))
        
        # Red numbers 1-9 matching EZCAD positions
        font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(220, 20, 20)) # Red text
        
        num_coords = [
            (margin - 18, margin - 6),     (int(cx) - 5, margin - 6),      (w - margin + 8, margin - 6),
            (margin - 18, int(cy) + 5),     (int(cx) + 6, int(cy) - 6),     (w - margin + 8, int(cy) + 5),
            (margin - 18, h - margin + 18), (int(cx) - 5, h - margin + 18), (w - margin + 8, h - margin + 18)
        ]
        
        for i, (nx, ny) in enumerate(num_coords):
            painter.drawText(nx, ny, str(i + 1))
            
        painter.setPen(QPen(QColor(20, 20, 20), 2))
        
        # Current orientation details
        cur = EZCAD_ORIENTATIONS[self.state_idx]
        
        def map_norm(nx, ny):
            px = cx + nx * (grid_w / 2.0)
            py = cy - ny * (grid_h / 2.0)
            return px, py
            
        # 1. Square marker
        sq_nx, sq_ny = cur["sq"]
        sq_px, sq_py = map_norm(sq_nx * 0.85, sq_ny * 0.85)
        painter.drawRect(int(sq_px) - 6, int(sq_py) - 6, 12, 12)
        
        # 2. Diamond marker
        di_nx, di_ny = cur["di"]
        di_px, di_py = map_norm(di_nx * 0.85, di_ny * 0.85)
        painter.save()
        painter.translate(di_px, di_py)
        painter.rotate(45)
        painter.drawRect(-6, -6, 12, 12)
        painter.restore()
        
        # 3. Center tick mark
        t1 = cur["tick_p1"]
        t2 = cur["tick_p2"]
        p1x, p1y = map_norm(t1[0], t1[1])
        p2x, p2y = map_norm(t2[0], t2[1])
        painter.setPen(QPen(QColor(20, 20, 20), 3))
        painter.drawLine(int(p1x), int(p1y), int(p2x), int(p2y))


class CalibrationGeneratorDialog(QDialog):
    def __init__(self, galvo_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EZCAD 9-Point Calibration Studio")
        self.resize(880, 680)
        self.galvo_controller = galvo_controller
        self.main_window = None
        
        self.state_idx = 0
        self.default_w = 30.0
        self.is_stopped = False
        self.reddot_timer = None
        self.is_reddot_framing = False
        
        self.field_size = 70.0
        # Retrieve field size from main window or config
        if self.main_window and hasattr(self.main_window, 'galvo_config'):
            self.field_size = getattr(self.main_window.galvo_config, 'field_size', 70.0)
            # Use 90% of the field size to leave a safe margin at the edges
            self.default_w = (self.field_size * 0.9) / 2.0
            
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                color: #0f172a;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
                color: #1e3a8a;
            }
            QLineEdit {
                border: 1px solid #94a3b8;
                border-radius: 5px;
                padding: 4px;
                background-color: #ffffff;
                color: #0f172a;
                font-weight: bold;
            }
            QLineEdit:disabled {
                background-color: #f1f5f9;
                color: #94a3b8;
            }
            QPushButton {
                background-color: #1e3a8a;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        
        # ==========================================
        # LEFT SIDE: Visual Diagram & Orientation & Laser Controls
        # ==========================================
        left_layout = QVBoxLayout()
        
        # Diagram
        diag_group = QGroupBox("1. Visual Orientation (Match Physical Mark)")
        diag_layout = QVBoxLayout()
        
        self.preview = GridPreviewWidget()
        diag_layout.addWidget(self.preview, alignment=Qt.AlignCenter)
        
        # Change image controls
        btn_bar = QHBoxLayout()
        self.lbl_state = QLabel("Image: 1 / 8")
        self.lbl_state.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_state.setStyleSheet("color: #1e3a8a;")
        
        self.btn_change_img = QPushButton("Change image >>")
        self.btn_change_img.setFixedHeight(34)
        self.btn_change_img.clicked.connect(self.next_state)
        
        btn_bar.addWidget(self.lbl_state)
        btn_bar.addWidget(self.btn_change_img)
        diag_layout.addLayout(btn_bar)
        diag_group.setLayout(diag_layout)
        left_layout.addWidget(diag_group)
        
        # Laser Controls Box
        laser_group = QGroupBox("Laser Marking Controls")
        laser_layout = QGridLayout()
        
        laser_layout.addWidget(QLabel("Power (%):"), 0, 0)
        self.slider_power = QSlider(Qt.Horizontal)
        self.slider_power.setRange(0, 100)
        self.slider_power.setValue(100)
        self.lbl_power_val = QLabel("100")
        pow_lay = QHBoxLayout()
        pow_lay.addWidget(self.slider_power)
        pow_lay.addWidget(self.lbl_power_val)
        self.slider_power.valueChanged.connect(lambda v: self.lbl_power_val.setText(str(v)))
        laser_layout.addLayout(pow_lay, 0, 1)
        
        laser_layout.addWidget(QLabel("Freq (kHz):"), 0, 2)
        self.slider_freq = QSlider(Qt.Horizontal)
        self.slider_freq.setRange(20, 80)
        self.slider_freq.setValue(30)
        self.lbl_freq_val = QLabel("30")
        freq_lay = QHBoxLayout()
        freq_lay.addWidget(self.slider_freq)
        freq_lay.addWidget(self.lbl_freq_val)
        self.slider_freq.valueChanged.connect(lambda v: self.lbl_freq_val.setText(str(v)))
        laser_layout.addLayout(freq_lay, 0, 3)
        
        # Sync with main window if available
        if self.main_window and hasattr(self.main_window, 'ui'):
            if hasattr(self.main_window.ui, 'galvolaserpowerHorizontalSlider_2'):
                main_pwr = self.main_window.ui.galvolaserpowerHorizontalSlider_2
                self.slider_power.setRange(main_pwr.minimum(), main_pwr.maximum())
                self.slider_power.setValue(main_pwr.value())
                self.slider_power.valueChanged.connect(main_pwr.setValue)
                main_pwr.valueChanged.connect(self.slider_power.setValue)
                
            if hasattr(self.main_window.ui, 'galvolaserfreqHorizontalSlider'):
                main_freq = self.main_window.ui.galvolaserfreqHorizontalSlider
                self.slider_freq.setRange(main_freq.minimum(), main_freq.maximum())
                self.slider_freq.setValue(main_freq.value())
                self.slider_freq.valueChanged.connect(main_freq.setValue)
                main_freq.valueChanged.connect(self.slider_freq.setValue)
        
        laser_layout.addWidget(QLabel("Mark Speed:"), 1, 0)
        self.input_mark_speed = QLineEdit("5000")
        self.input_mark_speed.setMaximumWidth(70)
        laser_layout.addWidget(self.input_mark_speed, 1, 1)
        
        laser_layout.addWidget(QLabel("Jump Speed:"), 1, 2)
        self.input_jump_speed = QLineEdit("15000")
        self.input_jump_speed.setMaximumWidth(70)
        laser_layout.addWidget(self.input_jump_speed, 1, 3)
        
        btn_action_layout = QHBoxLayout()
        self.btn_reddot = QPushButton("🔴 Red Dot Frame")
        self.btn_reddot.setStyleSheet("background-color: #dc2626; color: white;")
        self.btn_reddot.clicked.connect(self.dummy_action)
        btn_action_layout.addWidget(self.btn_reddot)
        
        self.btn_draw = QPushButton("⚡ Mark Calibration Grid")
        self.btn_draw.setStyleSheet("background-color: #0284c7; color: white;")
        self.btn_draw.clicked.connect(self.draw_pattern)
        btn_action_layout.addWidget(self.btn_draw)
        
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setStyleSheet("background-color: #475569; color: white;")
        self.btn_stop.clicked.connect(self.stop_pattern)
        btn_action_layout.addWidget(self.btn_stop)
        
        laser_layout.addLayout(btn_action_layout, 2, 0, 1, 4)
        laser_group.setLayout(laser_layout)
        left_layout.addWidget(laser_group)
        
        main_layout.addLayout(left_layout, 1)
        
        # ==========================================
        # RIGHT SIDE: Distances Table & Calibration Actions
        # ==========================================
        right_layout = QVBoxLayout()
        
        # Distances
        input_group = QGroupBox("2. Measured Distances from Center (mm)")
        input_layout = QVBoxLayout()
        
        # Target distance W header
        w_layout = QHBoxLayout()
        w_layout.addWidget(QLabel("Target Half-Width (W):"))
        self.input_w = QLineEdit(f"{self.default_w:.2f}")
        self.input_w.setFixedWidth(80)
        self.input_w.textChanged.connect(self.on_w_changed)
        w_layout.addWidget(self.input_w)
        w_layout.addWidget(QLabel("mm (Nominal Field = 2×W)"))
        w_layout.addStretch()
        
        btn_reset_nom = QPushButton("Reset to Nominal")
        btn_reset_nom.setStyleSheet("background-color: #64748b; color: white; padding: 3px 8px;")
        btn_reset_nom.clicked.connect(self.reset_to_nominal)
        w_layout.addWidget(btn_reset_nom)
        input_layout.addLayout(w_layout)
        
        # 9-Point table
        grid = QGridLayout()
        grid.addWidget(QLabel("<b>Pt</b>"), 0, 0, alignment=Qt.AlignCenter)
        grid.addWidget(QLabel("<b>X Distance (mm)</b>"), 0, 1, alignment=Qt.AlignCenter)
        grid.addWidget(QLabel("<b>Y Distance (mm)</b>"), 0, 2, alignment=Qt.AlignCenter)
        grid.addWidget(QLabel("<b>Description</b>"), 0, 3)
        
        self.inputs_x = []
        self.inputs_y = []
        
        pt_descs = [
            "Top-Left Corner", "Top Center", "Top-Right Corner",
            "Left Center", "Center (0,0)", "Right Center",
            "Bottom-Left Corner", "Bottom Center", "Bottom-Right Corner"
        ]
        
        w_val = self.default_w
        default_vals = [
            (w_val, w_val), (0, w_val), (w_val, w_val),
            (w_val, 0),     (0, 0),     (w_val, 0),
            (w_val, w_val), (0, w_val), (w_val, w_val)
        ]
        
        for i in range(9):
            lbl = QLabel(f"<b>{i+1}</b>")
            lbl.setStyleSheet("color: #dc2626; font-size: 13px;")
            grid.addWidget(lbl, i+1, 0, alignment=Qt.AlignCenter)
            
            le_x = QLineEdit(f"{default_vals[i][0]:.3f}")
            le_x.setAlignment(Qt.AlignCenter)
            le_y = QLineEdit(f"{default_vals[i][1]:.3f}")
            le_y.setAlignment(Qt.AlignCenter)
            
            if default_vals[i][0] == 0:
                le_x.setText("0.000")
                le_x.setEnabled(False)
            if default_vals[i][1] == 0:
                le_y.setText("0.000")
                le_y.setEnabled(False)
                
            self.inputs_x.append(le_x)
            self.inputs_y.append(le_y)
            grid.addWidget(le_x, i+1, 1)
            grid.addWidget(le_y, i+1, 2)
            
            desc_lbl = QLabel(pt_descs[i])
            desc_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            grid.addWidget(desc_lbl, i+1, 3)
            
        input_layout.addLayout(grid)
        input_group.setLayout(input_layout)
        right_layout.addWidget(input_group)
        
        # Status & Action Group
        action_group = QGroupBox("3. Apply & Verify Calibration")
        action_layout = QVBoxLayout()
        
        self.lbl_status = QLabel("Status: Ready")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #0284c7;")
        action_layout.addWidget(self.lbl_status)
        
        btn_action_box = QHBoxLayout()
        self.btn_calculate = QPushButton("✔ Calculate & Apply Calibration")
        self.btn_calculate.setFixedHeight(40)
        self.btn_calculate.setStyleSheet("background-color: #16a34a; font-size: 13px; font-weight: bold;")
        self.btn_calculate.clicked.connect(self.generate)
        btn_action_box.addWidget(self.btn_calculate)
        
        self.btn_verify = QPushButton("🎯 Mark Verification Shape")
        self.btn_verify.setFixedHeight(40)
        self.btn_verify.setStyleSheet("background-color: #0284c7; font-size: 13px; font-weight: bold;")
        self.btn_verify.clicked.connect(self.verify_pattern)
        btn_action_box.addWidget(self.btn_verify)
        
        action_layout.addLayout(btn_action_box)
        action_group.setLayout(action_layout)
        right_layout.addWidget(action_group)
        
        # Bottom Close Button
        btn_close_box = QHBoxLayout()
        btn_close_box.addStretch()
        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedWidth(100)
        self.btn_close.setStyleSheet("background-color: #64748b;")
        self.btn_close.clicked.connect(self.close)
        btn_close_box.addWidget(self.btn_close)
        right_layout.addLayout(btn_close_box)
        
        main_layout.addLayout(right_layout, 1)

    def on_w_changed(self, text):
        try:
            val = float(text)
            if val > 0:
                self.default_w = val
        except ValueError:
            pass

    def reset_to_nominal(self):
        w = self.default_w
        default_vals = [
            (w, w), (0, w), (w, w),
            (w, 0), (0, 0), (w, 0),
            (w, w), (0, w), (w, w)
        ]
        for i in range(9):
            if default_vals[i][0] != 0:
                self.inputs_x[i].setText(f"{default_vals[i][0]:.3f}")
            if default_vals[i][1] != 0:
                self.inputs_y[i].setText(f"{default_vals[i][1]:.3f}")

    def next_state(self):
        self.state_idx = (self.state_idx + 1) % 8
        self.lbl_state.setText(f"Image: {self.state_idx + 1} / 8")
        self.preview.set_state(self.state_idx)


    def stop_pattern(self):
        self.is_stopped = True
        
    def verify_pattern(self):
        self._execute_pattern(apply_calibration=True, show_msg=False)

    def draw_pattern(self):
        self._execute_pattern(apply_calibration=False, show_msg=True)

    def _execute_pattern(self, apply_calibration=False, show_msg=True):
        self.is_stopped = False
        if not self.galvo_controller or not self.galvo_controller.connection:
            QMessageBox.warning(self, "Error", "Galvo controller not connected.")
            return
            
        scale = 533.89
        hw = int(self.default_w * scale)
        c = 32767
        
        # Galvo coordinates (Y goes up in standard coords, assuming standard mapping)
        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw
        
        conn = self.galvo_controller.connection
        
        # Set the calibration state based on action
        if hasattr(conn, 'enable_calibration'):
            conn.enable_calibration = apply_calibration
            
        try:
            pwr = float(self.slider_power.value())
            freq = float(self.slider_freq.value())
            mark_speed = int(self.input_mark_speed.text())
            jump_speed = int(self.input_jump_speed.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, 5000, 20000

        # Use direct power value (100% = 100.0)
        crt_val = pwr

        # Set to power and freq
        if hasattr(conn, 'set_analog_do_bit'):
            for test_bit in [0, 1, 2]:
                conn.set_analog_do_bit(100.0, crt_val, freq, test_bit)
            import time
            time.sleep(0.05) # Small delay to ensure DAC is set before drawing
        
        queue = []
        def jump(x, y):
            # Apply horizontal mirror: x_mirrored = center - (x - center) = 2*c - x
            x = (2 * c) - x
            queue.append({'type': 'jump', 'x': int(x), 'y': int(y), 'speed': jump_speed})
            
        def mark(x, y):
            # Apply horizontal mirror
            x = (2 * c) - x
            queue.append({'type': 'mark', 'x': int(x), 'y': int(y), 'speed': mark_speed})
            
        # Helper to draw simple digits 1-9 for orientation verification
        def draw_digit(d, cx, cy):
            dw = int(1.0 * scale)
            dh = int(2.0 * scale)
            x0 = cx - dw
            x1 = cx + dw
            y0 = cy + dh
            y1 = cy
            y2 = cy - dh
            
            if d == 1:
                jump(x1, y0); mark(x1, y2)
            elif d == 2:
                jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1); mark(x0, y2); mark(x1, y2)
            elif d == 3:
                jump(x0, y0); mark(x1, y0); mark(x1, y1); mark(x0, y1)
                jump(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 4:
                jump(x0, y0); mark(x0, y1); mark(x1, y1)
                jump(x1, y0); mark(x1, y2)
            elif d == 5:
                jump(x1, y0); mark(x0, y0); mark(x0, y1); mark(x1, y1); mark(x1, y2); mark(x0, y2)
            elif d == 6:
                jump(x1, y0); mark(x0, y0); mark(x0, y2); mark(x1, y2); mark(x1, y1); mark(x0, y1)
            elif d == 7:
                jump(x0, y0); mark(x1, y0); mark(x1, y2)
            elif d == 8:
                jump(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2); mark(x0, y0)
                jump(x0, y1); mark(x1, y1)
            elif d == 9:
                jump(x1, y1); mark(x0, y1); mark(x0, y0); mark(x1, y0); mark(x1, y2); mark(x0, y2)

        try:
            # Outer square
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)
            
            # Vertical line
            jump(c, max_y)
            mark(c, min_y)
            
            # Horizontal line
            jump(min_x, c)
            mark(max_x, c)
            
            # Marker size (2mm)
            ms = int(2.0 * scale)
            o = int(ms / 2) # Padding offset
            
            # Square at Top-Left (Inside the quadrant)
            sq_x = min_x + o
            sq_y = max_y - o
            jump(sq_x, sq_y)
            mark(sq_x + ms, sq_y)
            mark(sq_x + ms, sq_y - ms)
            mark(sq_x, sq_y - ms)
            mark(sq_x, sq_y)
            
            # Diamond at Bot-Right (Inside the quadrant)
            d_cx = max_x - o - int(ms/2)
            d_cy = min_y + o + int(ms/2)
            d_r = int(ms/2)
            jump(d_cx, d_cy + d_r)
            mark(d_cx + d_r, d_cy)
            mark(d_cx, d_cy - d_r)
            mark(d_cx - d_r, d_cy)
            mark(d_cx, d_cy + d_r)
            
            # Tick mark (vertical line slightly to the RIGHT of center on horizontal axis)
            tick_x = c + int(hw * 0.15)
            tick_y_top = c + int(hw * 0.15)
            tick_y_bot = c - int(hw * 0.15)
            jump(tick_x, tick_y_top)
            mark(tick_x, tick_y_bot)
            
            # Draw Numbers 1-9 to verify orientation
            dist = int(3.0 * scale)
            # 1: Top-Left
            draw_digit(1, min_x + dist, max_y - dist)
            # 2: Top-Center
            draw_digit(2, c + dist, max_y - dist)
            # 3: Top-Right
            draw_digit(3, max_x - dist, max_y - dist)
            # 4: Left-Center
            draw_digit(4, min_x + dist, c + dist)
            # 5: Center
            draw_digit(5, c - dist, c + dist)
            # 6: Right-Center
            draw_digit(6, max_x - dist, c + dist)
            # 7: Bottom-Left
            draw_digit(7, min_x + dist, min_y + dist)
            # 8: Bottom-Center
            draw_digit(8, c + dist, min_y + dist)
            # 9: Bottom-Right
            draw_digit(9, max_x - dist, min_y + dist)
            
            self.btn_draw.setEnabled(False)
            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.is_stopped,
                progress_callback=lambda idx, tot, x, y, ctype: QApplication.processEvents()
            )
            
            if self.is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")
            
            conn.laser_off()
            conn.galvo_move_xy(c, c)
            
            if show_msg:
                QMessageBox.information(self, "Info", "Pattern drawn! Please measure the 9 points and enter the values.")
        except InterruptedError:
            pass # Or display a message if wanted
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to draw pattern: {e}")
        finally:
            if conn:
                conn.laser_off()
                if hasattr(conn, 'enable_calibration'):
                    conn.enable_calibration = False # Reset it immediately after
            self.btn_draw.setEnabled(True)
        
    def generate(self):
        # Read inputs
        ui_measurements = []
        for i in range(9):
            try:
                x = float(self.inputs_x[i].text())
                y = float(self.inputs_y[i].text())
                ui_measurements.append((x, y))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Invalid input at point {i+1}")
                return
                
        # Transform UI boxes to Galvo ideal points
        transform = TRANSFORMS[self.state_idx]
        galvo_measurements = [None] * 9
        
        # Signs for the 9 Galvo points: 
        # (Top-Left is -X, +Y in typical cartesian)
        signs = [
            (-1, 1),  (0, 1),  (1, 1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        
        for galvo_idx in range(9):
            ui_idx = transform.index(galvo_idx)
            raw_x, raw_y = ui_measurements[ui_idx]
            
            # Apply the expected sign to the absolute distance
            sx, sy = signs[galvo_idx]
            meas_x = raw_x * sx if sx != 0 else 0
            meas_y = raw_y * sy if sy != 0 else 0
            
            galvo_measurements[galvo_idx] = (meas_x, meas_y)
            
        # Hardcoded scale for now (could be an input field)
        scale = 533.89 
        
        try:
            generate_cor_file("generated_calibration.cor", scale, self.default_w, galvo_measurements)
            QMessageBox.information(self, "Success", "generated_calibration.cor created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate: {e}")
