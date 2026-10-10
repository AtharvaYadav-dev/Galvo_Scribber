import sys
import os
import winreg

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLineEdit, QComboBox, QLabel)
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen
from PySide6.QtCore import Qt

from ttfparser import TrueTypeFont

# Try to import MotionPlanner for hatching 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.motion_planner import MotionPlanner
except ImportError:
    MotionPlanner = None

def get_windows_fonts():
    fonts = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
        font_dir = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'
        
        for i in range(winreg.QueryInfoKey(key)[1]):
            name, value, _ = winreg.EnumValue(key, i)
            if not os.path.isabs(value):
                filepath = os.path.join(font_dir, value)
            else:
                filepath = value
                
            if filepath.lower().endswith(('.ttf', '.otf')):
                clean_name = name.replace(' (TrueType)', '').replace(' (OpenType)', '')
                fonts[clean_name] = filepath
    except Exception as e:
        print("Error reading font registry:", e)
    return fonts

class PathWrapper:
    def __init__(self):
        self.qpath = QPainterPath()
        
    def new_path(self):
        pass
        
    def move(self, x, y):
        self.qpath.moveTo(x, -y)
        
    def line(self, x0, y0, x1, y1):
        self.qpath.lineTo(x1, -y1)
        
    def quad(self, x0, y0, cx, cy, x1, y1):
        self.qpath.quadTo(cx, -cy, x1, -y1)
        
    def close(self):
        self.qpath.closeSubpath()
        
    def character_end(self):
        pass

class FontPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.qpath = QPainterPath()

    def set_path(self, qpath):
        self.qpath = qpath
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        
        if self.qpath.isEmpty():
            return
            
        rect = self.qpath.boundingRect()
        if rect.width() > 0 and rect.height() > 0:
            scale = min(self.width() / rect.width(), self.height() / rect.height()) * 0.8
            painter.translate(self.width() / 2, self.height() / 2)
            painter.scale(scale, scale)
            painter.translate(-rect.center())
            
        pen = QPen(Qt.black)
        pen.setWidthF(2.0 / scale if scale > 0 else 1.0)
        painter.setPen(pen)
        painter.drawPath(self.qpath)

class TestUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTF Parser & Font Loader Test")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        controls = QHBoxLayout()
        self.lbl_font = QLabel("Select Font:")
        self.combo_font = QComboBox()
        self.txt_input = QLineEdit("Galvo Scribber")
        
        self.btn_print = QPushButton("Print to Planner")
        
        controls.addWidget(self.lbl_font)
        controls.addWidget(self.combo_font)
        controls.addWidget(self.txt_input)
        controls.addWidget(self.btn_print)
        
        layout.addLayout(controls)
        
        self.preview = FontPreviewWidget()
        layout.addWidget(self.preview)
        
        self.font_obj = None
        self.fonts_dict = get_windows_fonts()
        
        self.combo_font.addItems(sorted(self.fonts_dict.keys()))
        self.combo_font.currentTextChanged.connect(self.load_ttf)
        self.txt_input.textChanged.connect(self.render_text)
        self.btn_print.clicked.connect(self.print_to_planner)
        
        if self.combo_font.count() > 0:
            self.load_ttf(self.combo_font.currentText())

    def load_ttf(self, font_name):
        path = self.fonts_dict.get(font_name)
        if path and os.path.exists(path):
            try:
                self.font_obj = TrueTypeFont(path)
                self.render_text()
            except Exception as e:
                print(f"Error loading {path}: {e}")

    def render_text(self):
        if not self.font_obj:
            return
        text = self.txt_input.text()
        if not text:
            self.preview.set_path(QPainterPath())
            return
            
        wrapper = PathWrapper()
        self.font_obj.render(wrapper, text, font_size=100.0)
        self.preview.set_path(wrapper.qpath)
        
    def print_to_planner(self):
        if not self.font_obj or MotionPlanner is None:
            print("MotionPlanner not available or no font loaded.")
            return
            
        qpath = self.preview.qpath
        poly_list = []
        for qpoly in qpath.toSubpathPolygons():
            pts = [(pt.x(), pt.y()) for pt in qpoly]
            if len(pts) > 2:
                poly_list.append(pts)
                
        planner = MotionPlanner()
        # Create a basic cross-hatching config using existing logic!
        hatch_configs = [{
            'enable': True, 
            'type': 'Bidirectional', 
            'angle': 45.0, 
            'line_space': 1.0, 
            'cross_hatch': True,
            'count': 1, 
            'hatch_idx': 1
        }]
        
        print(f"Sending {len(poly_list)} text polygons to MotionPlanner...")
        planner.generate_hatch(poly_list, hatch_configs, mark_speed=1000, jump_speed=2000, galvo_units_per_mm=1.0)
        print(f"Success! Generated {len(planner.preview_queue)} low-level laser instructions from the text.")

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = TestUI()
    window.show()
    sys.exit(app.exec())
