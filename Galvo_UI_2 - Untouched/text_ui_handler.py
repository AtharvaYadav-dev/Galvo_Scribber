import os
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, 
                               QDoubleSpinBox, QGroupBox, QWidget, QCompleter)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

class FontPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.polygons = []
        
    def set_polygons(self, polygons):
        self.polygons = polygons
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        
        if not self.polygons:
            return
            
        pen = QPen(QColor("#00ff00"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Calculate bounding box with inverted Y for display
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for poly in self.polygons:
            for x, y in poly:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, -y)
                max_y = max(max_y, -y)
                
        width = max_x - min_x if max_x > min_x else 1
        height = max_y - min_y if max_y > min_y else 1
        
        # Scale to fit
        margin = 10
        scale_x = (self.width() - margin * 2) / width
        scale_y = (self.height() - margin * 2) / height
        scale = min(scale_x, scale_y)
        
        # Offset to center
        cx = (self.width() - (width * scale)) / 2 - (min_x * scale)
        cy = (self.height() - (height * scale)) / 2 - (min_y * scale)
        
        path = QPainterPath()
        for poly in self.polygons:
            if not poly: continue
            
            p0 = poly[0]
            path.moveTo(p0[0] * scale + cx, -p0[1] * scale + cy)
            for p in poly[1:]:
                path.lineTo(p[0] * scale + cx, -p[1] * scale + cy)
                
        painter.drawPath(path)


class TextUIHandler:
    def __init__(self, main_window):
        self.mw = main_window
        self.setup_ui()
        
    def setup_ui(self):
        page = getattr(self.mw.ui, 'textPage', None)
        if page is None:
            self.mw.logger.error("textPage not found in UI")
            return
            
        # Prevent double initialization
        if page.layout() is not None:
            return
            
        layout = QVBoxLayout(page)
        
        # Create a container frame so the background picks up the dark theme
        from PySide6.QtWidgets import QFrame
        frame = QFrame()
        frame.setObjectName("textContainerFrame")
        frame.setStyleSheet("QFrame#textContainerFrame { background-color: transparent; }")
        layout.addWidget(frame)
        
        group_layout = QVBoxLayout(frame)
        group_layout.setContentsMargins(20, 20, 20, 20)
        group_layout.setSpacing(15)
        
        # Live Preview
        self.preview_widget = FontPreviewWidget()
        group_layout.addWidget(self.preview_widget)
        
        # Settings Container
        settings_layout = QHBoxLayout()
        
        # Font Selection
        lbl_font = QLabel("Font:")
        lbl_font.setStyleSheet("color: white;")
        settings_layout.addWidget(lbl_font)
        
        self.line_search_font = QLineEdit()
        self.line_search_font.setPlaceholderText("Search...")
        self.line_search_font.setMinimumWidth(100)
        self.line_search_font.textChanged.connect(self.filter_fonts)
        settings_layout.addWidget(self.line_search_font)
        
        self.btn_refresh_fonts = QPushButton("↻")
        self.btn_refresh_fonts.setToolTip("Refresh Fonts")
        self.btn_refresh_fonts.setFixedSize(30, 30)
        self.btn_refresh_fonts.clicked.connect(self.refresh_fonts)
        settings_layout.addWidget(self.btn_refresh_fonts)
        
        self.combo_font = QComboBox()
        self.combo_font.addItems(list(self.mw.text_parser.fonts.keys()))
        self.combo_font.setMinimumWidth(150)
        settings_layout.addWidget(self.combo_font)
        
        # Font Size (in mm)
        lbl_size = QLabel("Size (mm):")
        lbl_size.setStyleSheet("color: white;")
        settings_layout.addWidget(lbl_size)
        self.spin_size = QDoubleSpinBox()
        self.spin_size.setRange(1, 500)
        self.spin_size.setValue(10.0)
        settings_layout.addWidget(self.spin_size)
        
        # Power
        lbl_power = QLabel("Power (%):")
        lbl_power.setStyleSheet("color: white;")
        settings_layout.addWidget(lbl_power)
        self.spin_power = QDoubleSpinBox()
        self.spin_power.setRange(0, 100)
        self.spin_power.setValue(100.0)
        settings_layout.addWidget(self.spin_power)
        
        # Frequency
        lbl_freq = QLabel("Freq (kHz):")
        lbl_freq.setStyleSheet("color: white;")
        settings_layout.addWidget(lbl_freq)
        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setRange(20, 100)
        self.spin_freq.setValue(30.0)
        settings_layout.addWidget(self.spin_freq)
        
        group_layout.addLayout(settings_layout)
        
        # Speeds Container
        speeds_layout = QHBoxLayout()
        
        # Mark Speed
        lbl_mark = QLabel("Mark Speed (mm/s):")
        lbl_mark.setStyleSheet("color: white;")
        speeds_layout.addWidget(lbl_mark)
        self.spin_mark = QDoubleSpinBox()
        self.spin_mark.setRange(1, 10000)
        self.spin_mark.setValue(1000.0)
        speeds_layout.addWidget(self.spin_mark)
        
        # Jump Speed
        lbl_jump = QLabel("Jump Speed (mm/s):")
        lbl_jump.setStyleSheet("color: white;")
        speeds_layout.addWidget(lbl_jump)
        self.spin_jump = QDoubleSpinBox()
        self.spin_jump.setRange(1, 15000)
        self.spin_jump.setValue(2000.0)
        speeds_layout.addWidget(self.spin_jump)
        
        group_layout.addLayout(speeds_layout)
        
        # Text Input
        text_layout = QHBoxLayout()
        lbl_text = QLabel("Text:")
        lbl_text.setStyleSheet("color: white;")
        text_layout.addWidget(lbl_text)
        self.line_text = QLineEdit("Laser Marking")
        text_layout.addWidget(self.line_text)
        
        group_layout.addLayout(text_layout)
        
        # Save / Generate Button
        self.btn_save = QPushButton("Save && Send to Galvo Preview")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("background-color: #2c3e50; color: white; border-radius: 5px; font-weight: bold;")
        self.btn_save.clicked.connect(self.on_save_clicked)
        group_layout.addWidget(self.btn_save)
        
        layout.addStretch()
        
        # Connect signals for live preview
        self.combo_font.currentTextChanged.connect(self.update_preview)
        self.spin_size.valueChanged.connect(self.update_preview)
        self.line_text.textChanged.connect(self.update_preview)
        
        # Initial preview
        self.update_preview()
        
    def refresh_fonts(self):
        self.mw.text_parser.fonts.clear()
        self.mw.text_parser.load_system_fonts()
        self.filter_fonts(self.line_search_font.text())
        
    def filter_fonts(self, text):
        self.combo_font.blockSignals(True)
        self.combo_font.clear()
        
        all_fonts = list(self.mw.text_parser.fonts.keys())
        if not text:
            self.combo_font.addItems(all_fonts)
        else:
            search_text = text.lower()
            filtered = [f for f in all_fonts if search_text in f.lower()]
            self.combo_font.addItems(filtered)
            
        self.combo_font.blockSignals(False)
        self.update_preview()
        
    def update_preview(self, *args):
        text = self.line_text.text()
        font_name = self.combo_font.currentText()
        font_size = self.spin_size.value()
        
        if not text or not font_name:
            self.preview_widget.set_polygons([])
            return
            
        polygons = self.mw.text_parser.parse_text(text, font_name, font_size=font_size)
        self.preview_widget.set_polygons(polygons)

    def on_save_clicked(self):
        text = self.line_text.text()
        font_name = self.combo_font.currentText()
        font_size = self.spin_size.value()
        
        if not text or not font_name:
            self.mw.showCustomPopup("Error", "Please enter text and select a font.")
            return
            
        try:
            # Parse text into polygons using the existing TextParser
            # font_size here is treated as roughly millimeters in height
            polygons = self.mw.text_parser.parse_text(text, font_name, font_size=font_size)
            
            if not polygons:
                self.mw.showCustomPopup("Error", "Could not generate vector path from text.")
                return
                
            # Convert to Galvo Units and center it
            if hasattr(self.mw, 'galvo_config'):
                scale = 65535.0 / self.mw.galvo_config.field_size
            else:
                scale = 655.35 # Default assuming 100mm field
            
            # Find bounding box to center the text exactly at (0,0) in mm space
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            for poly in polygons:
                for x, y in poly:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    
            text_cx = (min_x + max_x) / 2.0 if min_x != float('inf') else 0
            text_cy = (min_y + max_y) / 2.0 if min_y != float('inf') else 0
            
            scaled_polygons = []
            for poly in polygons:
                scaled_poly = []
                for x, y in poly:
                    # Shift text to 0,0 in mm space
                    mm_x = x - text_cx
                    mm_y = y - text_cy
                    
                    if hasattr(self.mw, 'galvo_config'):
                        # apply_transform handles scaling, offsets, inversions, and Galvo integer mapping (32767 center)
                        gx, gy = self.mw.galvo_config.apply_transform(mm_x, mm_y)
                    else:
                        # Fallback if no galvo config
                        gx = int(32767 + (mm_x * scale))
                        gy = int(32767 + (mm_y * scale))
                        
                    scaled_poly.append((gx, gy))
                scaled_polygons.append(scaled_poly)
                
            # Switch to print preview page so the user can see it
            if hasattr(self.mw.ui, 'printgalvoPage'):
                self.mw.ui.mainPages.setCurrentWidget(self.mw.ui.printgalvoPage)
                
            # Grab basic hatch config
            hatch_configs = [{
                'enable': True,
                'type': 'Bidirectional',
                'angle': 0.0,
                'line_space': 0.05,
                'cross_hatch': False,
                'count': 1,
                'hatch_idx': 1
            }]
            
            # Optionally inherit from UI settings if needed
            if hasattr(self.mw, 'hatch_profiles') and 1 in self.mw.hatch_profiles:
                p = self.mw.hatch_profiles[1]
                hatch_configs[0]['angle'] = float(p.get("angle", 0.0) or 0.0)
                hatch_configs[0]['line_space'] = float(p.get("line_space", 0.05) or 0.05)
                hatch_configs[0]['cross_hatch'] = (p.get("cross_hatch", False) == 'true')

            # Clear current queue
            self.mw.planner.clear()
            
            # Update global power and frequency for the marking engine
            power_val = self.spin_power.value()
            freq_val = self.spin_freq.value()
            mark_speed_mm = self.spin_mark.value()
            jump_speed_mm = self.spin_jump.value()
            
            self.mw.pgm_laserpower = float(power_val)
            self.mw.pgm_laserfreq = float(freq_val)
            
            # Sync to the main UI sliders so the print page knows the values
            if hasattr(self.mw.ui, 'galvolaserpowerHorizontalSlider_2'):
                self.mw.ui.galvolaserpowerHorizontalSlider_2.setValue(int(power_val))
            if hasattr(self.mw.ui, 'galvolaserfreqHorizontalSlider'):
                self.mw.ui.galvolaserfreqHorizontalSlider.setValue(int(freq_val))
                
            # Sync speed variables in the Program page using WidgetHandler
            if hasattr(self.mw, 'programgalvo_widgets'):
                self.mw.wh.invokeMethod(self.mw.programgalvo_widgets.pgmmarkspeedgalvo, "set", str(mark_speed_mm))
                self.mw.wh.invokeMethod(self.mw.programgalvo_widgets.pgmjumpspeed, "set", str(jump_speed_mm))
                
            # If the galvo controller has live tracking properties, update them too
            if hasattr(self.mw, 'galvo_controller'):
                self.mw.galvo_controller.live_power = power_val
                self.mw.galvo_controller.live_freq = freq_val
            
            # Generate hatch
            scaled_mark_speed = int(mark_speed_mm * scale)
            scaled_jump_speed = int(jump_speed_mm * scale)
            
            self.mw.planner.generate_hatch(
                scaled_polygons,
                hatch_configs,
                mark_speed=scaled_mark_speed,
                jump_speed=scaled_jump_speed,
                galvo_units_per_mm=scale
            )
            
            # Save into the send queue
            self.mw.planner.commit_to_send_queue()
            
            # Update bounds
            if hasattr(self.mw, 'update_galvo_preview_bounds'):
                self.mw.update_galvo_preview_bounds()
                
            # Force preview to redraw
            if hasattr(self.mw, 'galvo_preview'):
                self.mw.galvo_preview.draw_queue(self.mw.planner.preview_queue)
                    
            self.mw.logger.info(f"Text generated and sent to planner. {len(polygons)} polygons.")
            
        except Exception as e:
            self.mw.logger.error(f"Error generating text: {e}")
            self.mw.showCustomPopup("Error", f"Failed to generate text:\n{str(e)}")
