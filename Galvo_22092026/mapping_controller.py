from PySide6.QtWidgets import QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtWidgets import QApplication

from core.motion_planner import MotionPlanner
from mapping_dialog import GridPreviewCanvas

class ParameterMappingController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui = main_window.ui
        self.galvo = main_window.galvo_controller
        self.is_running = False
        self.is_aborted = False
        
        try:
            self.field_size = self.main_window.galvo_config.field_size
        except AttributeError:
            self.field_size = 110.0
            
        self.setup_ui()
        self.canvas.set_field_size(self.field_size)
        # Call generate_matrix shortly after init to allow UI setup
        QTimer.singleShot(100, self.generate_matrix)

    def setup_ui(self):
        self.power_start = self.ui.powstartLineEdit
        self.power_end = self.ui.powendLineEdit
        self.power_steps = self.ui.powstepsLineEdit
        
        self.freq_start = self.ui.freqstartLineEdit
        self.freq_end = self.ui.freqendLineEdit
        self.freq_steps = self.ui.freqstepsLineEdit
        
        self.cell_w = self.ui.cellwidthLineEdit
        self.cell_h = self.ui.cellheightLineEdit
        self.gap_x = self.ui.cellgapxLineEdit
        self.gap_y = self.ui.cellgapyLineEdit
        
        self.fill_type = self.ui.cellfilltypeComboBox
        self.label_axes = self.ui.celllabelaxisCheckBox
        
        self.btn_preview = self.ui.redmarkmatPushButton
        self.btn_mark = self.ui.lasermarkmatPushButton
        self.btn_stop = self.ui.stopmatPushButton
        
        if self.fill_type.count() == 0:
            self.fill_type.addItems(["Filled Rectangle", "Vector Outline"])
            
        self.canvas = GridPreviewCanvas()
        layout = QVBoxLayout(self.ui.mappmatrixgalvoFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        for le in [self.power_start, self.power_end, self.power_steps,
                   self.freq_start, self.freq_end, self.freq_steps,
                   self.cell_w, self.cell_h, self.gap_x, self.gap_y]:
            le.textChanged.connect(self.generate_matrix)
        self.fill_type.currentIndexChanged.connect(self.generate_matrix)
        self.label_axes.stateChanged.connect(self.generate_matrix)

    def generate_matrix(self, *args):
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

        self.canvas.update_grid(self.grid_data, show_labels=self.label_axes.isChecked())

    def draw_digit_lines(self, d, cx, cy, planner, scale=1.0):
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
        planner.preview_queue = []
        self.cmd_to_cell = {}

        if not self.grid_data:
            return
            
        max_x = max(d['rect'].right() for d in self.grid_data)
        max_y = max(d['rect'].bottom() for d in self.grid_data)
        
        cx = max_x / 2.0
        cy = max_y / 2.0

        try:
            jump_speed = int(self.main_window.wh.invokeMethod(self.main_window.programgalvo_widgets.pgmjumpspeed, "get") or 2000000)
            mark_speed = int(self.main_window.wh.invokeMethod(self.main_window.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000000)
        except Exception:
            jump_speed = 2000000
            mark_speed = 1000000

        for cell in self.grid_data:
            r_rect = cell['rect']
            power = cell['power']
            freq = cell['freq']
            
            x0 = (r_rect.left() - cx) * scale + center_xy
            y0 = (r_rect.top() - cy) * scale + center_xy
            w = r_rect.width() * scale
            h = r_rect.height() * scale
            
            x1 = x0 + w
            y1 = y0 + h

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
                self.main_window.save_current_hatch_profile()
                hatch_configs = []
                for k, p in self.main_window.hatch_profiles.items():
                    if not p.get("enable", False):
                        continue
                    cfg = {
                        'enable': True,
                        'follow_edge': p.get("follow_edge", False) == 'true' if isinstance(p.get("follow_edge", False), str) else p.get("follow_edge", False),
                        'all_calc': p.get("all_calc", False) == 'true' if isinstance(p.get("all_calc", False), str) else p.get("all_calc", False),
                        'cross_hatch': p.get("cross_hatch", False) == 'true' if isinstance(p.get("cross_hatch", False), str) else p.get("cross_hatch", False),
                        'type': p.get("type", "Bidirectional") or "Bidirectional",
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
                        'hatch_idx': k
                    }
                    hatch_configs.append(cfg)
                    
                if not hatch_configs:
                    # Fallback if no hatch enabled
                    p = self.main_window.hatch_profiles[1]
                    hatch_configs.append({'enable': True, 'type': "Bidirectional", 'angle': float(p.get("angle", "0.0") or 0.0), 'line_space': float(p.get("line_space", "0.05") or 0.05), 'count': int(p.get("count", "1") or 1), 'pen_no': 0, 'hatch_idx': 1})
                    
                planner.generate_hatch([poly], hatch_configs, mark_speed=mark_speed, jump_speed=jump_speed, galvo_units_per_mm=scale)
                
            end_idx = len(planner.preview_queue)
            for i in range(start_idx, end_idx):
                self.cmd_to_cell[i] = (cell['r'], cell['c'])
                
            if self.label_axes.isChecked():
                max_r = max(d['r'] for d in self.grid_data)
                if cell['c'] == 0 or cell['r'] == max_r:
                    if not is_preview:
                        planner.preview_queue.append({
                            'type': 'set_params',
                            'power': 100.0,
                            'freq': 20.0
                        })
                        
                if cell['c'] == 0:
                    lbl_x = x0 - (5.0 * scale)
                    lbl_y = y0 + h/2.0
                    self.draw_number(freq, lbl_x, lbl_y, planner, scale=scale*0.5)
                
                if cell['r'] == max_r:
                    lbl_x = x0 + w/2.0
                    lbl_y = y1 + (5.0 * scale)
                    self.draw_number(power, lbl_x, lbl_y, planner, scale=scale*0.5)

        self.is_aborted = False
        self.is_running = True

        if is_preview:
            for cmd in planner.preview_queue:
                if cmd.get('type') == 'mark':
                    cmd['type'] = 'jump'
                    
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
        if not hasattr(self, '_last_ui_update'):
            self._last_ui_update = 0.0
            
        if idx in self.cmd_to_cell:
            r, c = self.cmd_to_cell[idx]
            if self.canvas.active_cell != (r, c):
                self.canvas.set_active_cell(r, c)
                
        import time
        if time.time() - self._last_ui_update > 0.05:
            QApplication.processEvents()
            self._last_ui_update = time.time()

    def run_preview(self):
        self._execute(is_preview=True)

    def run_mark(self):
        self._execute(is_preview=False)

    def abort(self):
        self.is_aborted = True
