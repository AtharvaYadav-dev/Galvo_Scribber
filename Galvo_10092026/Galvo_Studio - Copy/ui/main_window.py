import sys
import os
import json

try:
    from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QSpinBox, QLabel, QLineEdit, QCheckBox, QDoubleSpinBox, QTabWidget, QFormLayout, QComboBox, QGroupBox, QRadioButton
    from PySide6.QtCore import QThread, Signal, QTimer
    from PySide6.QtGui import QPainterPath, QFont
except ImportError:
    pass # Handled in preview_widget or main

from ui.preview_widget import GalvoPreviewWidget
from core.motion_planner import MotionPlanner
from core.svg_parser import SVGParser
from core.text_parser import TextParser
from core.coordinate_mapper import CoordinateConfig
from machine.galvo_controller import GalvoController
from machine.stepper_controller import StepperController

class ExecutionThread(QThread):
    finished_signal = Signal(bool)
    progress_signal = Signal(float, float)
    
    def __init__(self, controller, queue, loop_count=1):
        super().__init__()
        self.controller = controller
        self.queue = queue
        self.loop_count = loop_count
        self._abort = False
        
    def abort(self):
        self._abort = True
        
    def run(self):
        def on_pos(x, y):
            self.progress_signal.emit(x, y)
        success = self.controller.execute_queue(
            self.queue, 
            self.loop_count, 
            progress_callback=on_pos, 
            abort_check=lambda: self._abort
        )
        self.finished_signal.emit(success)

class PreviewThread(QThread):
    def __init__(self, controller, min_x, max_x, min_y, max_y):
        super().__init__()
        self.controller = controller
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.running = True
        self.needs_refresh = False
        
    def update_bounds(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.needs_refresh = True
        
    def run(self):
        speed = 2000000
        if hasattr(self.controller.connection, 'laser_off'):
            self.controller.connection.laser_off()
        dll_obj = getattr(self.controller.connection, 'dll', None)
        has_continuous = dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_set_continous_mode_on')
        
        if has_continuous:
            dll_obj.GT_PROSYS_U3_set_continous_mode_on()
            
        import time
        
        while self.running:
            if self.needs_refresh:
                if has_continuous:
                    dll_obj.GT_PROSYS_U3_set_continous_mode_off()
                    time.sleep(0.05) # Give hardware time to clear the loop buffer
                    dll_obj.GT_PROSYS_U3_set_continous_mode_on()
                self.needs_refresh = False
                
            if dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_galvo_move_XY'):
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_x), int(self.min_y), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.max_x), int(self.min_y), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.max_x), int(self.max_y), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_x), int(self.max_y), speed, 0.0, 0.0, 0.0)
                dll_obj.GT_PROSYS_U3_galvo_move_XY(int(self.min_x), int(self.min_y), speed, 0.0, 0.0, 0.0)
                time.sleep(0.02) # Standard throttling for red-light loop
            else:
                time.sleep(0.05)

        if has_continuous:
            dll_obj.GT_PROSYS_U3_set_continous_mode_off()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galvo Studio")
        self.resize(1000, 600)
        
        self.planner = MotionPlanner()
        self.text_parser = TextParser()
        self.config = CoordinateConfig()
        self.controller = GalvoController()
        self.controller.connect()
        self.stepper_controller = StepperController(self.controller.connection)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # --- LEFT PANEL (TABS) ---
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(350)
        main_layout.addWidget(self.tabs)
        
        # 1. System Tab
        self.tab_system = QWidget()
        sys_layout = QVBoxLayout(self.tab_system)
        
        self.lbl_status = QLabel("Status: Unknown")
        sys_layout.addWidget(self.lbl_status)
        self.btn_connect = QPushButton("Connect Hardware")
        self.btn_connect.clicked.connect(self.connect_hardware)
        self.chk_force_mock = QCheckBox("Force Demo Mode (Mock)")
        self.chk_force_mock.setChecked(False)
        sys_layout.addWidget(self.btn_connect)
        sys_layout.addWidget(self.chk_force_mock)
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.disconnect_hardware)
        sys_layout.addWidget(self.btn_disconnect)
        self.update_connection_ui()
        
        sys_form = QFormLayout()
        self.spin_mark_speed = QSpinBox()
        self.spin_mark_speed.setRange(1, 5000000)
        self.spin_mark_speed.setValue(1000000)
        self.spin_mark_speed.valueChanged.connect(self.on_settings_changed)
        sys_form.addRow("Mark Speed:", self.spin_mark_speed)
        
        self.spin_jump_speed = QSpinBox()
        self.spin_jump_speed.setRange(1, 5000000)
        self.spin_jump_speed.setValue(2000000)
        self.spin_jump_speed.valueChanged.connect(self.on_settings_changed)
        sys_form.addRow("Jump Speed:", self.spin_jump_speed)
        
        self.spin_loop_count = QSpinBox()
        self.spin_loop_count.setRange(1, 1000000)
        self.spin_loop_count.setValue(1)
        self.spin_loop_count.valueChanged.connect(self.on_settings_changed)
        sys_form.addRow("Loop Count:", self.spin_loop_count)
        
        sys_layout.addLayout(sys_form)
        
        btn_test = QPushButton("Generate Test Pattern")
        btn_test.clicked.connect(self.load_test_pattern)
        sys_layout.addWidget(btn_test)
        
        # Z-Axis Control Group
        group_z = QGroupBox("Z-Axis Control")
        layout_z = QVBoxLayout(group_z)
        
        self.lbl_z_pos = QLabel("Z Position: 0.0 mm")
        self.lbl_z_pos.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
        layout_z.addWidget(self.lbl_z_pos)
        
        form_z = QFormLayout()
        self.spin_z_step = QDoubleSpinBox()
        self.spin_z_step.setRange(0.01, 100.0)
        self.spin_z_step.setValue(1.0)
        self.spin_z_step.setSuffix(" mm")
        form_z.addRow("Step Size:", self.spin_z_step)
        layout_z.addLayout(form_z)
        
        btn_layout_z = QHBoxLayout()
        self.btn_z_up = QPushButton("Z + (Up)")
        self.btn_z_up.clicked.connect(self.z_move_up)
        self.btn_z_up.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px;")
        btn_layout_z.addWidget(self.btn_z_up)
        
        self.btn_z_down = QPushButton("Z - (Down)")
        self.btn_z_down.clicked.connect(self.z_move_down)
        self.btn_z_down.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 5px;")
        btn_layout_z.addWidget(self.btn_z_down)
        
        layout_z.addLayout(btn_layout_z)
        
        self.btn_z_home = QPushButton("Set Z as Home (0.0)")
        self.btn_z_home.clicked.connect(self.z_set_home)
        layout_z.addWidget(self.btn_z_home)
        
        self.btn_set_focus = QPushButton("Set Focus")
        self.btn_set_focus.clicked.connect(self.z_set_focus)
        self.btn_set_focus.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 5px;")
        layout_z.addWidget(self.btn_set_focus)
        
        sys_layout.addWidget(group_z)
        
        sys_layout.addStretch()
        self.tabs.addTab(self.tab_system, "System")
        
        # 1.5 Config Tab
        self.tab_config = QWidget()
        cfg_layout = QVBoxLayout(self.tab_config)
        
        # Aspect Group
        group_aspect = QGroupBox("Aspect")
        form_aspect = QFormLayout(group_aspect)
        
        self.spin_field_size = QDoubleSpinBox()
        self.spin_field_size.setRange(1.0, 1000.0)
        self.spin_field_size.setValue(150.0)
        self.spin_field_size.setSuffix(" MM")
        self.spin_field_size.valueChanged.connect(self.on_config_changed)
        form_aspect.addRow("Field size:", self.spin_field_size)
        
        self.spin_offset_x = QDoubleSpinBox()
        self.spin_offset_x.setRange(-500.0, 500.0)
        self.spin_offset_x.setValue(0.0)
        self.spin_offset_x.setSuffix(" MM")
        self.spin_offset_x.valueChanged.connect(self.on_config_changed)
        form_aspect.addRow("Offset X:", self.spin_offset_x)
        
        self.spin_offset_y = QDoubleSpinBox()
        self.spin_offset_y.setRange(-500.0, 500.0)
        self.spin_offset_y.setValue(0.0)
        self.spin_offset_y.setSuffix(" MM")
        self.spin_offset_y.valueChanged.connect(self.on_config_changed)
        form_aspect.addRow("Offset Y:", self.spin_offset_y)
        
        self.spin_angle = QDoubleSpinBox()
        self.spin_angle.setRange(-360.0, 360.0)
        self.spin_angle.setValue(0.0)
        self.spin_angle.setSuffix(" Degree")
        self.spin_angle.valueChanged.connect(self.on_config_changed)
        form_aspect.addRow("Angle:", self.spin_angle)
        
        self.radio_galvo1_x = QRadioButton("Galvo1=X")
        self.radio_galvo2_x = QRadioButton("Galvo2=X")
        self.radio_galvo1_x.setChecked(True)
        self.radio_galvo1_x.toggled.connect(self.on_config_changed)
        self.radio_galvo2_x.toggled.connect(self.on_config_changed)
        
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(self.radio_galvo1_x)
        axis_layout.addWidget(self.radio_galvo2_x)
        form_aspect.addRow("Axis Map:", axis_layout)
        
        cfg_layout.addWidget(group_aspect)
        
        # Galvo 1 Group
        group_galvo1 = QGroupBox("Galvo 1")
        form_g1 = QFormLayout(group_galvo1)
        self.chk_negate_x = QCheckBox("Negate")
        self.chk_negate_x.stateChanged.connect(self.on_config_changed)
        form_g1.addRow("", self.chk_negate_x)
        self.spin_scale_x = QDoubleSpinBox()
        self.spin_scale_x.setRange(1.0, 1000.0)
        self.spin_scale_x.setDecimals(4)
        self.spin_scale_x.setValue(100.0000)
        self.spin_scale_x.valueChanged.connect(self.on_config_changed)
        form_g1.addRow("Scale:", self.spin_scale_x)
        cfg_layout.addWidget(group_galvo1)
        
        # Galvo 2 Group
        group_galvo2 = QGroupBox("Galvo 2")
        form_g2 = QFormLayout(group_galvo2)
        self.chk_negate_y = QCheckBox("Negate")
        self.chk_negate_y.stateChanged.connect(self.on_config_changed)
        form_g2.addRow("", self.chk_negate_y)
        self.spin_scale_y = QDoubleSpinBox()
        self.spin_scale_y.setRange(1.0, 1000.0)
        self.spin_scale_y.setDecimals(4)
        self.spin_scale_y.setValue(100.0000)
        self.spin_scale_y.valueChanged.connect(self.on_config_changed)
        form_g2.addRow("Scale:", self.spin_scale_y)
        cfg_layout.addWidget(group_galvo2)
        
        cfg_layout.addStretch()
        self.tabs.addTab(self.tab_config, "Config")
        
        # 2. Text Tab
        self.tab_text = QWidget()
        txt_layout = QVBoxLayout(self.tab_text)
        
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Enter text to print...")
        self.input_text.returnPressed.connect(self.load_text)
        txt_layout.addWidget(self.input_text)
        
        txt_form = QFormLayout()
        
        self.combo_font = QComboBox()
        self.combo_font.addItems(sorted(self.text_parser.fonts.keys()))
        self.combo_font.setMaxVisibleItems(15) # Prevents dropdown from going off-screen
        self.combo_font.setStyleSheet("QComboBox { combobox-popup: 0; }") # Force Qt to obey the limit on Windows
        self.combo_font.currentTextChanged.connect(self.on_settings_changed)
        txt_form.addRow("Font:", self.combo_font)
        
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(5, 500)
        self.spin_font_size.setValue(50)
        self.spin_font_size.valueChanged.connect(self.on_settings_changed)
        txt_form.addRow("Size:", self.spin_font_size)
        
        txt_layout.addLayout(txt_form)
        
        btn_text = QPushButton("Load Text")
        btn_text.clicked.connect(self.load_text)
        txt_layout.addWidget(btn_text)
        
        self.chk_enable_hatch_text = QCheckBox("Enable Hatching")
        self.chk_enable_hatch_text.stateChanged.connect(self.on_enable_hatching_toggled)
        txt_layout.addWidget(self.chk_enable_hatch_text)
        
        txt_layout.addStretch()
        self.tabs.addTab(self.tab_text, "Text")
        
        # 3. SVG Tab
        self.tab_svg = QWidget()
        svg_layout = QVBoxLayout(self.tab_svg)
        btn_svg = QPushButton("Load SVG")
        btn_svg.clicked.connect(self.load_svg)
        svg_layout.addWidget(btn_svg)
        
        self.chk_enable_hatch_svg = QCheckBox("Enable Hatching")
        self.chk_enable_hatch_svg.stateChanged.connect(self.on_enable_hatching_toggled)
        svg_layout.addWidget(self.chk_enable_hatch_svg)
        
        svg_layout.addStretch()
        self.tabs.addTab(self.tab_svg, "SVG")
        
        # 4. Hatching Tab
        self.tab_hatch = QWidget()
        hatch_layout = QVBoxLayout(self.tab_hatch)
        
        contour_layout = QHBoxLayout()
        self.chk_mark_contour = QCheckBox("Mark Contour")
        self.chk_mark_contour.setChecked(True)
        self.chk_mark_contour.stateChanged.connect(self.on_settings_changed)
        self.spin_mark_contour_pen = QSpinBox()
        self.spin_mark_contour_pen.setRange(0, 255)
        self.spin_mark_contour_pen.valueChanged.connect(self.on_settings_changed)
        contour_layout.addWidget(self.chk_mark_contour)
        contour_layout.addWidget(QLabel("Pen:"))
        contour_layout.addWidget(self.spin_mark_contour_pen)
        contour_layout.addStretch()
        hatch_layout.addLayout(contour_layout)

        self.hatch_tabs = QTabWidget()
        self.hatch_enables = []
        self.hatch_all_calc = []
        self.hatch_follow_edge = []
        self.hatch_cross_hatch = []
        self.hatch_type = []
        self.hatch_angle = []
        self.hatch_pen_no = []
        self.hatch_count = []
        self.hatch_line_space = []
        self.hatch_avg_distribute = []
        self.hatch_edge_offset = []
        self.hatch_start_offset = []
        self.hatch_end_offset = []
        self.hatch_line_reduction = []
        self.hatch_num_loops = []
        self.hatch_loop_distance = []
        self.hatch_auto_rotate = []
        self.hatch_rotate_angle = []

        for i in range(3):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            form = QFormLayout()
            
            enable = QCheckBox("Enable")
            enable.stateChanged.connect(self.on_settings_changed)
            self.hatch_enables.append(enable)
            layout.addWidget(enable)
            
            top_flags = QHBoxLayout()
            all_calc = QCheckBox("All calc")
            all_calc.stateChanged.connect(self.on_settings_changed)
            follow_edge = QCheckBox("Follow edge once")
            follow_edge.stateChanged.connect(self.on_settings_changed)
            cross_hatch = QCheckBox("Cross hatch")
            cross_hatch.stateChanged.connect(self.on_settings_changed)
            top_flags.addWidget(all_calc)
            top_flags.addWidget(follow_edge)
            top_flags.addWidget(cross_hatch)
            layout.addLayout(top_flags)

            htype = QComboBox()
            htype.addItems(["Bidirectional", "Unidirectional", "Ring-like", "Optimized / Bow-tie", "Auto-Sorting / Block Hatch"])
            htype.currentTextChanged.connect(self.on_settings_changed)
            self.hatch_type.append(htype)
            form.addRow("Type:", htype)
            
            pen_no = QSpinBox()
            pen_no.setRange(0, 255)
            pen_no.valueChanged.connect(self.on_settings_changed)
            self.hatch_pen_no.append(pen_no)
            form.addRow("Pen No.:", pen_no)

            angle = QDoubleSpinBox()
            angle.setRange(-360.0, 360.0)
            angle.setSingleStep(15.0)
            if i == 1: angle.setValue(90.0)
            angle.valueChanged.connect(self.on_settings_changed)
            self.hatch_angle.append(angle)
            form.addRow("Angle (deg):", angle)
            
            count = QSpinBox()
            count.setRange(1, 999)
            count.setValue(1)
            count.valueChanged.connect(self.on_settings_changed)
            self.hatch_count.append(count)
            form.addRow("Count:", count)

            line_space = QDoubleSpinBox()
            line_space.setRange(0.001, 10.0)
            line_space.setDecimals(3)
            line_space.setValue(0.05)
            line_space.setSingleStep(0.01)
            line_space.valueChanged.connect(self.on_settings_changed)
            self.hatch_line_space.append(line_space)
            form.addRow("Line Space (mm):", line_space)

            avg_distribute = QCheckBox("Average distribute line")
            avg_distribute.stateChanged.connect(self.on_settings_changed)
            self.hatch_avg_distribute.append(avg_distribute)
            form.addRow("", avg_distribute)

            edge_offset = QDoubleSpinBox()
            edge_offset.setRange(-10.0, 10.0)
            edge_offset.setDecimals(3)
            edge_offset.setValue(0.0)
            edge_offset.valueChanged.connect(self.on_settings_changed)
            self.hatch_edge_offset.append(edge_offset)
            form.addRow("Edge Offset (mm):", edge_offset)

            start_offset = QDoubleSpinBox()
            start_offset.setRange(-10.0, 10.0)
            start_offset.setDecimals(3)
            start_offset.setValue(0.0)
            start_offset.valueChanged.connect(self.on_settings_changed)
            self.hatch_start_offset.append(start_offset)
            form.addRow("Start Offset (mm):", start_offset)

            end_offset = QDoubleSpinBox()
            end_offset.setRange(-10.0, 10.0)
            end_offset.setDecimals(3)
            end_offset.setValue(0.0)
            end_offset.valueChanged.connect(self.on_settings_changed)
            self.hatch_end_offset.append(end_offset)
            form.addRow("End Offset (mm):", end_offset)

            line_reduction = QDoubleSpinBox()
            line_reduction.setRange(-10.0, 10.0)
            line_reduction.setDecimals(3)
            line_reduction.setValue(0.0)
            line_reduction.valueChanged.connect(self.on_settings_changed)
            self.hatch_line_reduction.append(line_reduction)
            form.addRow("Line Reduction (mm):", line_reduction)

            num_loops = QSpinBox()
            num_loops.setRange(0, 999)
            num_loops.setValue(0)
            num_loops.valueChanged.connect(self.on_settings_changed)
            self.hatch_num_loops.append(num_loops)
            form.addRow("NumLoops:", num_loops)

            loop_distance = QDoubleSpinBox()
            loop_distance.setRange(0.001, 10.0)
            loop_distance.setDecimals(3)
            loop_distance.setValue(0.05)
            loop_distance.valueChanged.connect(self.on_settings_changed)
            self.hatch_loop_distance.append(loop_distance)
            form.addRow("Loop distance (mm):", loop_distance)

            rot_layout = QHBoxLayout()
            auto_rot = QCheckBox("Auto rotate angle")
            auto_rot.stateChanged.connect(self.on_settings_changed)
            rot_angle = QDoubleSpinBox()
            rot_angle.setRange(-360.0, 360.0)
            rot_angle.setValue(10.0)
            rot_angle.valueChanged.connect(self.on_settings_changed)
            rot_layout.addWidget(auto_rot)
            rot_layout.addWidget(rot_angle)
            self.hatch_auto_rotate.append(auto_rot)
            self.hatch_rotate_angle.append(rot_angle)
            self.hatch_all_calc.append(all_calc)
            self.hatch_follow_edge.append(follow_edge)
            self.hatch_cross_hatch.append(cross_hatch)
            form.addRow("", rot_layout)

            layout.addLayout(form)
            self.hatch_tabs.addTab(tab, f"Hatch {i+1}")

        hatch_layout.addWidget(self.hatch_tabs)
        self.tabs.addTab(self.tab_hatch, "Hatch")
        
        # --- RIGHT PANEL (PREVIEW & EXECUTION) ---
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)
        
        self.preview = GalvoPreviewWidget(config=self.config)
        right_layout.addWidget(self.preview)
        
        btn_layout = QHBoxLayout()
        right_layout.addLayout(btn_layout)
        
        self.btn_preview = QPushButton("Red-Light Preview (Box)")
        self.btn_preview.setCheckable(True)
        self.btn_preview.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.btn_preview.clicked.connect(self.toggle_preview)
        btn_layout.addWidget(self.btn_preview)
        
        self.btn_execute = QPushButton("Execute Buffer")
        self.btn_execute.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_execute.clicked.connect(self.execute_queue)
        btn_layout.addWidget(self.btn_execute)
        
        self.btn_abort = QPushButton("Abort Execution")
        self.btn_abort.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_abort.clicked.connect(self.abort_execution)
        self.btn_abort.setEnabled(False)
        btn_layout.addWidget(self.btn_abort)
        
        self.btn_galvo_home = QPushButton("Galvo Home")
        self.btn_galvo_home.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.btn_galvo_home.clicked.connect(self.galvo_home)
        btn_layout.addWidget(self.btn_galvo_home)
        
        self.lbl_xy_pos = QLabel("Galvo Position: X=0.00 mm, Y=0.00 mm")
        self.lbl_xy_pos.setStyleSheet("font-weight: bold; color: #555; font-size: 14px; margin-top: 5px;")
        right_layout.addWidget(self.lbl_xy_pos)
        
        self.preview_thread = None
        
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._apply_settings)

    def get_hatch_configs(self):
        configs = []
        for i in range(3):
            if not self.hatch_enables[i].isChecked():
                continue
            cfg = {
                'enable': True,
                'follow_edge': self.hatch_follow_edge[i].isChecked(),
                'all_calc': self.hatch_all_calc[i].isChecked(),
                'cross_hatch': self.hatch_cross_hatch[i].isChecked(),
                'type': self.hatch_type[i].currentText(),
                'angle': self.hatch_angle[i].value(),
                'pen_no': self.hatch_pen_no[i].value(),
                'count': self.hatch_count[i].value(),
                'line_space': self.hatch_line_space[i].value(),
                'avg_distribute': self.hatch_avg_distribute[i].isChecked(),
                'edge_offset': self.hatch_edge_offset[i].value(),
                'start_offset': self.hatch_start_offset[i].value(),
                'end_offset': self.hatch_end_offset[i].value(),
                'line_reduction': self.hatch_line_reduction[i].value(),
                'num_loops': self.hatch_num_loops[i].value(),
                'loop_distance': self.hatch_loop_distance[i].value(),
                'auto_rotate': self.hatch_auto_rotate[i].isChecked(),
                'rotate_angle': self.hatch_rotate_angle[i].value()
            }
            configs.append(cfg)
        return configs

    def update_connection_ui(self):
        if self.controller.is_connected:
            self.lbl_status.setText("Status: Connected (Hardware)")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
        else:
            self.lbl_status.setText("Status: Disconnected (Simulator Mode)")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)

    def connect_hardware(self):
        force_mock = self.chk_force_mock.isChecked()
        success = self.controller.connect(force_mock=force_mock)
        
        # Update stepper with new connection
        self.stepper_controller.connection = self.controller.connection
        
        self.update_connection_ui()
        
        if not success and not force_mock:
            QMessageBox.warning(self, "Connection Failed", "Could not find Galvo hardware. Falling back to Simulator Mode.")

    def disconnect_hardware(self):
        self.controller.disconnect()
        self.update_connection_ui()

    def z_move_up(self):
        step = self.spin_z_step.value()
        self.stepper_controller.move_z_relative(step)  
        self.update_z_label()
        
    def z_move_down(self):
        step = self.spin_z_step.value()
        self.stepper_controller.move_z_relative(-step)   
        self.update_z_label()
        
    def z_set_home(self):
        self.btn_z_home.setEnabled(False)
        self.btn_z_home.setText("Homing... Please wait")
        
        # We pass QApplication.instance() so the UI doesn't freeze during the homing loop
        from PySide6.QtWidgets import QApplication
        success = self.stepper_controller.home_z(app_instance=QApplication.instance())
        
        self.update_z_label()
        self.btn_z_home.setEnabled(True)
        self.btn_z_home.setText("Set Z as Home (0.0)")
        
        if success:
            QMessageBox.information(self, "Homing Complete", "Z-Axis successfully homed to the limit switch.")
        else:
            QMessageBox.warning(self, "Homing Failed", "Failed to reach the limit switch. Is the switch connected?")
        
    def z_set_focus(self):
        focus_pos = self.stepper_controller.z_position
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            settings['z_focus'] = focus_pos
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            QMessageBox.information(self, "Focus Set", f"Z Focus position saved at {focus_pos:.3f} mm.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save focus: {e}")
            
    def update_z_label(self):
        phys_z = self.stepper_controller.get_physical_z()
        self.lbl_z_pos.setText(f"Z Position: {self.stepper_controller.z_position:.3f} mm (Hardware reads: {phys_z:.3f} mm)")

    def toggle_preview(self):
        if self.btn_preview.isChecked():
            # Start Preview
            if not self.planner.send_queue:
                QMessageBox.information(self, "Empty Queue", "Please load a pattern or SVG first.")
                self.btn_preview.setChecked(False)
                return
            
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            
            for cmd in self.planner.send_queue:
                if 'x' in cmd and 'y' in cmd:
                    min_x = min(min_x, cmd['x'])
                    max_x = max(max_x, cmd['x'])
                    min_y = min(min_y, cmd['y'])
                    max_y = max(max_y, cmd['y'])
                    
            if min_x == float('inf'):
                QMessageBox.information(self, "Invalid Pattern", "Pattern has no valid coordinates.")
                self.btn_preview.setChecked(False)
                return
                
            self.btn_execute.setEnabled(False)
            self.btn_preview.setText("Stop Preview")
            self.btn_preview.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            
            self.preview_thread = PreviewThread(self.controller, min_x, max_x, min_y, max_y)
            self.preview_thread.start()
        else:
            # Stop Preview
            if self.preview_thread:
                self.preview_thread.running = False
                self.preview_thread.wait()
                self.preview_thread = None
                
            self.btn_execute.setEnabled(True)
            self.btn_preview.setText("Red-Light Preview (Box)")
            self.btn_preview.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")

    def update_preview_bounds(self):
        if not self.btn_preview.isChecked() or not self.preview_thread:
            return
            
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        
        for cmd in self.planner.send_queue:
            if 'x' in cmd and 'y' in cmd:
                min_x = min(min_x, cmd['x'])
                max_x = max(max_x, cmd['x'])
                min_y = min(min_y, cmd['y'])
                max_y = max(max_y, cmd['y'])
                
        if min_x != float('inf'):
            if self.preview_thread:
                self.preview_thread.update_bounds(min_x, max_x, min_y, max_y)

    def on_settings_changed(self, *args):
        if hasattr(self, 'debounce_timer'):
            self.debounce_timer.start(500) # 500 ms delay
            
    def _apply_settings(self):
        if hasattr(self, 'last_loaded_type'):
            if self.last_loaded_type == "svg":
                self.process_svg()
            elif self.last_loaded_type == "text":
                self.process_text()

    def on_config_changed(self, *args):
        self.config.field_size = self.spin_field_size.value()
        self.config.offset_x = self.spin_offset_x.value()
        self.config.offset_y = self.spin_offset_y.value()
        self.config.angle = self.spin_angle.value()
        self.config.galvo_1_is_x = self.radio_galvo1_x.isChecked()
        self.config.negate_x = self.chk_negate_x.isChecked()
        self.config.negate_y = self.chk_negate_y.isChecked()
        self.config.scale_x = self.spin_scale_x.value()
        self.config.scale_y = self.spin_scale_y.value()
        
        # Trigger redraw
        if hasattr(self, "current_polygons"):
            self.process_text(self.current_polygons)
            
    def on_enable_hatching_toggled(self, state):
        is_checked = bool(state)
        
        self.chk_enable_hatch_text.blockSignals(True)
        self.chk_enable_hatch_svg.blockSignals(True)
        self.chk_enable_hatch_text.setChecked(is_checked)
        self.chk_enable_hatch_svg.setChecked(is_checked)
        self.chk_enable_hatch_text.blockSignals(False)
        self.chk_enable_hatch_svg.blockSignals(False)
        
        if is_checked:
            if not self.hatch_enables[0].isChecked():
                self.hatch_enables[0].setChecked(True)
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Hatch":
                    self.tabs.setCurrentIndex(i)
                    break
        else:
            for enable in self.hatch_enables:
                enable.setChecked(False)
                
        self.on_settings_changed()

    def load_text(self):
        self.last_loaded_type = "text"
        self.process_text()
        
    def process_text(self):
        text = self.input_text.text()
        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter some text to print.")
            return
            
        mark_speed = self.spin_mark_speed.value()
        jump_speed = self.spin_jump_speed.value()
        
        self.planner.clear()
        
        font_name = self.combo_font.currentText()
        font_size = self.spin_font_size.value()
        
        polygons = self.text_parser.parse_text(text, font_name, font_size=font_size)
        
        # Convert abstract points to galvo coords using CoordinateConfig
        galvo_units_per_mm = 65535 / self.config.field_size
        
        hatch_configs = self.get_hatch_configs()
        mark_contour = self.chk_mark_contour.isChecked()
        
        # Text starts at X=0, Y=0 in abstract space. 
        # CoordinateConfig maps 0,0 to the center of the Galvo bed.
        
        # Determine "All calc"
        # Since text usually consists of many polygons (characters), we should
        # handle all_calc at the planner level if possible, or just pass all polygons.
        # For simplicity, we just pass all polygons to generate_hatch at once.
        
        all_polys_galvo = []
        for poly in polygons:
            if not poly: continue
            poly_galvo = []
            for pt in poly:
                galvo_x, galvo_y = self.config.apply_transform(pt[0], pt[1])
                poly_galvo.append((galvo_x, galvo_y))
            all_polys_galvo.append(poly_galvo)

        for poly_galvo in all_polys_galvo:
            # Draw Outline
            if mark_contour:
                self.planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
                for pt in poly_galvo[1:]:
                    self.planner.add_mark(pt[0], pt[1], speed=mark_speed)
                    
        # Draw Hatching if enabled
        if hatch_configs:
            self.planner.generate_hatch(
                all_polys_galvo, 
                hatch_configs,
                mark_speed=mark_speed, 
                jump_speed=jump_speed,
                galvo_units_per_mm=galvo_units_per_mm
            )
                
        if not hatch_configs:
            self.planner.optimize_path()
            
        self.planner.commit_to_send_queue()
        self.preview.draw_queue(self.planner.preview_queue)
        self.update_preview_bounds()

    def load_test_pattern(self):
        self.planner.clear()
        
        mark_speed = self.spin_mark_speed.value()
        jump_speed = self.spin_jump_speed.value()
        
        # Jump to start
        self.planner.add_jump(20000, 20000, speed=jump_speed)
        # Draw square
        self.planner.add_mark(45000, 20000, speed=mark_speed)
        self.planner.add_mark(45000, 45000, speed=mark_speed)
        self.planner.add_mark(20000, 45000, speed=mark_speed)
        self.planner.add_mark(20000, 20000, speed=mark_speed)
        # Jump to center
        self.planner.add_jump(32767, 32767, speed=jump_speed)
        
        self.planner.commit_to_send_queue()
        self.preview.draw_queue(self.planner.preview_queue)
        self.update_preview_bounds()

    def load_svg(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open SVG File", "", "SVG Files (*.svg)")
        if not filepath:
            return
        self.last_loaded_type = "svg"
        self.last_svg_filepath = filepath
        self.process_svg()
        
    def process_svg(self):
        filepath = getattr(self, 'last_svg_filepath', None)
        if not filepath:
            return
            
        parser = SVGParser(field_size=self.config.field_size)
        polygons = parser.parse_to_polygons(filepath)
        
        if not polygons:
            QMessageBox.warning(self, "Error", "Failed to parse SVG or SVG is empty.")
            return
            
        mark_speed = self.spin_mark_speed.value()
        jump_speed = self.spin_jump_speed.value()
        self.planner.clear()
        
        hatch_configs = self.get_hatch_configs()
        mark_contour = self.chk_mark_contour.isChecked()
        galvo_units_per_mm = 65535 / self.config.field_size
        
        all_polys_galvo = []
        for poly in polygons:
            if not poly: continue
            poly_galvo = []
            for pt in poly:
                galvo_x, galvo_y = self.config.apply_transform(pt[0], pt[1])
                poly_galvo.append((galvo_x, galvo_y))
            all_polys_galvo.append(poly_galvo)

        for poly_galvo in all_polys_galvo:
            if mark_contour:
                self.planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
                for pt in poly_galvo[1:]:
                    self.planner.add_mark(pt[0], pt[1], speed=mark_speed)
                
        if hatch_configs:
            self.planner.generate_hatch(
                all_polys_galvo, 
                hatch_configs,
                mark_speed=mark_speed, 
                jump_speed=jump_speed,
                galvo_units_per_mm=galvo_units_per_mm
            )
                
        if not hatch_configs:
            self.planner.optimize_path()
            
        self.planner.commit_to_send_queue()
        self.preview.draw_queue(self.planner.preview_queue)
        self.update_preview_bounds()

    def execute_queue(self):
        if not self.planner.send_queue:
            QMessageBox.information(self, "Empty Queue", "Please load a pattern or SVG first.")
            return
            
        settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                if 'z_focus' in settings:
                    focus_pos = settings['z_focus']
                    current_pos = self.stepper_controller.z_position
                    distance = abs(focus_pos - current_pos)
                    
                    if distance > 0.001:
                        print(f"Moving to Z Focus position: {focus_pos} mm")
                        # 1000 is the default speed used in execute_queue
                        self.stepper_controller.move_axis('Z', focus_pos, speed=1000)
                        
                        # Calculate exactly how long it will take to travel this distance
                        # speed is in pulses per second. 
                        pulses_to_travel = distance * self.stepper_controller.steps_per_mm
                        travel_time_seconds = (pulses_to_travel / 1000.0) + 0.5 # Add 0.5s buffer for acceleration
                        
                        import time
                        from PySide6.QtWidgets import QApplication
                        
                        print(f"Waiting {travel_time_seconds:.2f} seconds for bed to finish moving...")
                        
                        # Non-blocking wait so UI doesn't freeze completely
                        start_time = time.time()
                        while time.time() - start_time < travel_time_seconds:
                            time.sleep(0.05)
                            QApplication.instance().processEvents()
                            
        except Exception as e:
            print(f"Failed to move to focus position: {e}")
            
        loop_count = self.spin_loop_count.value()
            
        print(f"Starting Execution (Loops: {loop_count})...")
        self.btn_execute.setEnabled(False)
        self.btn_abort.setEnabled(True)
        self.btn_preview.setEnabled(False)
        self.btn_execute.setText("Executing...")
        
        self.exec_thread = ExecutionThread(self.controller, self.planner.send_queue, loop_count)
        self.exec_thread.progress_signal.connect(self.update_xy_label)
        self.exec_thread.finished_signal.connect(self.on_execution_finished)
        self.exec_thread.start()

    def update_xy_label(self, galvo_x, galvo_y):
        mm_x, mm_y = self.config.reverse_transform(galvo_x, galvo_y)
        self.lbl_xy_pos.setText(f"Galvo Position: X={mm_x:.2f} mm, Y={mm_y:.2f} mm")

    def on_execution_finished(self, success):
        self.btn_execute.setEnabled(True)
        self.btn_abort.setEnabled(False)
        self.btn_preview.setEnabled(True)
        self.btn_execute.setText("Execute Buffer")
        if success:
            QMessageBox.information(self, "Success", "Execution complete. Check logs.")
        else:
            QMessageBox.warning(self, "Status", "Execution failed or was aborted.")

    def abort_execution(self):
        if self.exec_thread and self.exec_thread.isRunning():
            self.btn_abort.setText("Aborting...")
            self.btn_abort.setEnabled(False)
            self.exec_thread.abort()
            
    def galvo_home(self):
        success = self.controller.galvo_home()
        if success:
            QMessageBox.information(self, "Homed", "Galvo successfully sent to home position (center).")
            self.update_xy_label(32767, 32767)
        else:
            QMessageBox.warning(self, "Error", "Failed to home Galvo. Ensure hardware is connected.")
