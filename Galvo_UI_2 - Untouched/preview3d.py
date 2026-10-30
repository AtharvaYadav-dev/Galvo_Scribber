from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QCheckBox
from PySide6.QtGui import QMouseEvent, QWheelEvent, QColor, QFont, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QTimer
import resources_rc
from OpenGL.GL import *
from OpenGL.GLU import *

from gcode import GcodeHandler
import math

class GCode3DPreview(QOpenGLWidget):

    # Signals (to keep GL calls in GUI thread)
    sigLoadGcode = Signal(list)
    sigMarkSegment = Signal(str)
    sigRequestUpdate = Signal()
    sigGlError = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # -------------------------
        # G-code data
        # -------------------------
        self.segment_dict = {}
        self.layers = {}          # layer_z -> list of segment keys
        self.layer_z_list = []    # sorted z values
        self.selected_layer_index = None
        self.line_to_segment = {}
        self._segment_orig_colors = {}  # seg_key -> original QColor
        
        self.layer_round_digits = 4
        self.show_travel = True
        self.dark_mode = True
        self.live_printing = False
        self.current_print_layer = None
        self.completed_segments = set()
        self.processed_gcode = None
        self.last_print_z = None

        self.gh = GcodeHandler()

        # Cura-like feature styles
        self.feature_style = {
            "travel":    (QColor(70, 70, 160), 1.0),    # Blue (Thin)
            "wall":      (QColor(230, 25, 25),  5.0),   # Red
            "inner_wall":(QColor(25, 200, 25),  5.0),   # Green
            "infill":    (QColor(255, 150, 0),  3.0),   # Orange
            "skin":      (QColor(240, 240, 50), 3.5),   # Yellow
            "skirt":     (QColor(100, 150, 250), 3.0),  # Light Blue
            "active":    (QColor(255, 255, 255), 6.0),  # White (Active) - Default Dark Mode
            "completed": (QColor(40, 180, 40),  4.5),   # Green (Completed)
        }
        
        self.ghost_alpha = 0.25

        # -------------------------
        # Camera & Bed
        # -------------------------
        self.rot_x = -60.0
        self.rot_y = -45.0
        self.zoom = -100.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_mouse = None
        
        self.model_center_x = 25.0
        self.model_center_y = 25.0
        self.model_center_z = 0.0
        self.locked_center = None

        self.bed_width = 50.0
        self.bed_height = 50.0
        self.bed_z_height = 50.0

        self.setFocusPolicy(Qt.StrongFocus)

        # Timer for auto-closing overlay
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setInterval(10000) # 10 seconds
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(lambda: self.overlay.hide())

        # UI Initialization
        self._create_overlay()

        # Connect signals to slots
        self.sigLoadGcode.connect(self._onLoadGcode, Qt.QueuedConnection)
        self.sigMarkSegment.connect(self._onMarkSegment, Qt.QueuedConnection)
        self.sigRequestUpdate.connect(self.update, Qt.QueuedConnection)

    def _create_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setObjectName("Overlay")
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Define shared style components
        self.dark_overlay_qss = """
            QWidget#Overlay { background: rgba(20, 20, 20, 220); border: 1px solid rgba(255, 255, 255, 30); border-radius: 10px; }
            QLabel { color: #E0E0E0; font-weight: bold; background: transparent; }
            QPushButton { 
                background-color: rgba(60, 60, 60, 200); 
                color: #FFFFFF; 
                border: 1px solid rgba(255, 255, 255, 40); 
                border-radius: 5px; 
                padding: 5px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(80, 80, 80, 255); border: 1px solid rgba(255, 255, 255, 80); }
            QPushButton:pressed { background-color: rgba(40, 40, 40, 255); }
            QCheckBox { color: #E0E0E0; spacing: 5px; background: transparent; font-size: 11px; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #666; border-radius: 3px; background: #222; }
            QCheckBox::indicator:checked { background: #0078D7; border: 1px solid #005a9e; }
        """
        
        self.light_overlay_qss = """
            QWidget#Overlay { background: rgba(240, 240, 240, 230); border: 1px solid rgba(0, 0, 0, 40); border-radius: 10px; }
            QLabel { color: #202020; font-weight: bold; background: transparent; }
            QPushButton { 
                background-color: rgba(220, 220, 220, 220); 
                color: #000000; 
                border: 1px solid rgba(0, 0, 0, 60); 
                border-radius: 5px; 
                padding: 5px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(200, 200, 200, 255); border: 1px solid rgba(0, 0, 0, 100); }
            QPushButton:pressed { background-color: rgba(180, 180, 180, 255); }
            QCheckBox { color: #202020; spacing: 5px; background: transparent; font-size: 11px; }
            QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #999; border-radius: 3px; background: #FFFFFF; }
            QCheckBox::indicator:checked { background: #0078D7; border: 1px solid #005a9e; }
        """
        
        v = QVBoxLayout(self.overlay)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        self.lbl_info = QLabel("Layers: 0")
        self.lbl_info.setFont(QFont("Arial", 9))
        v.addWidget(self.lbl_info)

        h_ctrl = QHBoxLayout()
        self.btn_theme = QPushButton("Light Mode")
        self.btn_theme.setFixedWidth(85)
        self.btn_theme.setToolTip("Dark/Light Theme Toggle")
        self.btn_theme.clicked.connect(self.toggle_theme)
        h_ctrl.addWidget(self.btn_theme)

        self.chk_travel = QCheckBox("Travel")
        self.chk_travel.setChecked(True)
        self.chk_travel.setToolTip("Show or Hide travel (non-printing) moves")
        self.chk_travel.toggled.connect(self._on_travel_toggle)
        h_ctrl.addWidget(self.chk_travel)
        v.addLayout(h_ctrl)

        h_views = QHBoxLayout()
        h_views.setSpacing(2)
        view_tips = {
            "top": "Top View (XY Plane)", 
            "front": "Front View (XZ Plane)", 
            "side": "Side View (YZ Plane)", 
            "iso": "Perspective Isometric View"
        }
        for label, view_name in [("Top", "top"), ("Front", "front"), ("Side", "side"), ("ISO", "iso")]:
            btn = QPushButton(label)
            btn.setFixedWidth(38)
            btn.setToolTip(view_tips[view_name])
            btn.clicked.connect(lambda _, vn=view_name: self.set_view(vn))
            h_views.addWidget(btn)
        v.addLayout(h_views)

        self.overlay.resize(210, 115)
        
        # Eye button to toggle overlay
        self.btn_eye = QPushButton(self)
        self.btn_eye.setIcon(QIcon(":/icons/icons/eye.svg"))
        self.btn_eye.setFixedSize(32, 32)
        self.btn_eye.setToolTip("Show/Hide Overlay")
        self.btn_eye.setCursor(Qt.PointingHandCursor)
        self.btn_eye.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 16px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(16, 42, 131, 230);
                border: 1px solid rgba(255, 255, 255, 100);
            }
            QPushButton:pressed {
                background-color: rgba(10, 30, 100, 255);
            }
        """)
        self.btn_eye.clicked.connect(self.toggle_overlay)
        
        # Initially hide overlay
        self.overlay.hide()
        
        # Apply initial theme now that all widgets are created
        self.apply_theme_style()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        # Position eye button at top right
        self.btn_eye.move(self.width() - self.btn_eye.width() - 8, 8)
        # Position overlay below eye button
        self.overlay.move(self.width() - self.overlay.width() - 8, self.btn_eye.height() + 16)

    def toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
            self.auto_close_timer.stop()
        else:
            self.overlay.show()
            self.auto_close_timer.start()

    # -------------------------
    # Public API
    # -------------------------
    def loadGcode(self, gcode_lines: list[str]) -> None:
        """Thread-safe G-code loader."""
        self.sigLoadGcode.emit(list(gcode_lines))

    def markSegment(self, gcode: str) -> None:
        """Thread-safe executed segment marker."""
        self.sigMarkSegment.emit(str(gcode))

    def setBedSize(self, width, height, z_height=30.0):
        self.bed_width = float(width)
        self.bed_height = float(height)
        self.bed_z_height = float(z_height)
        self.sigRequestUpdate.emit()

    def set_live_printing(self, state: bool):
        self.live_printing = bool(state)
        if not state:
            if self.processed_gcode:
                self.completed_segments.add(self.processed_gcode)
            self.processed_gcode = None
            self.current_print_layer = None
        self._update_info_label()
        self.sigRequestUpdate.emit()

    def clear_marking(self):
        self.completed_segments.clear()
        self.processed_gcode = None
        self.current_print_layer = None
        self._update_info_label()
        self.sigRequestUpdate.emit()

    def clear(self):
        """Completely removes all G-code and resets the preview."""
        self.segment_dict = {}
        self.layers = {}
        self.layer_z_list = []
        self.completed_segments.clear()
        self.processed_gcode = None
        self.current_print_layer = None
        self.last_print_z = None
        self._update_info_label()
        self.sigRequestUpdate.emit()

    def set_view(self, view_name):
        if view_name == "top":
            self.rot_x, self.rot_y = 0.0, 0.0
        elif view_name == "front":
            self.rot_x, self.rot_y = -90.0, 0.0
        elif view_name == "side":
            self.rot_x, self.rot_y = -90.0, -90.0
        elif view_name == "iso":
            self.rot_x, self.rot_y = -60.0, -45.0
        self.fit_model()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme_style()
        self.sigRequestUpdate.emit()

    def apply_theme_style(self):
        """Applies styles to overlay based on current dark_mode state."""
        if self.dark_mode:
            # When background is Dark, make the box Light for contrast
            self.btn_theme.setText("Light Mode")
            self.feature_style["active"] = (QColor(255, 255, 255), 6.0)
            self.overlay.setStyleSheet(self.light_overlay_qss)
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 220);
                    border: 1px solid rgba(0, 0, 0, 40);
                    border-radius: 16px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: rgba(230, 230, 230, 255);
                    border: 1px solid rgba(0, 0, 0, 80);
                }
            """)
        else:
            # When background is Light, make the box Dark for contrast
            self.btn_theme.setText("Dark Mode")
            self.feature_style["active"] = (QColor(30, 30, 30), 6.0)
            self.overlay.setStyleSheet(self.dark_overlay_qss)
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background-color: rgba(16, 42, 131, 220);
                    border: 1px solid rgba(255, 255, 255, 40);
                    border-radius: 16px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: rgba(40, 70, 160, 255);
                    border: 1px solid rgba(255, 255, 255, 80);
                }
            """)

    def _on_travel_toggle(self, state):
        self.show_travel = bool(state)
        self.sigRequestUpdate.emit()

    # -------------------------
    # Slots
    # -------------------------
    @Slot(list)
    def _onLoadGcode(self, gcode_lines: list[str]) -> None:
        self.segment_dict = {}
        self.layers = {}
        self.layer_z_list = []
        self.completed_segments.clear()
        self.processed_gcode = None
        self.current_print_layer = None

        pos = {"X": 0.0, "Y": 0.0, "Z": 0.0, "E": 0.0}
        x0 = y0 = z0 = 0.0
        relative_mode = False
        current_layer_z = None

        for line in gcode_lines:
            raw_line = line.strip()
            if not raw_line or raw_line.startswith(';'):
                continue

            tokens = raw_line.split()
            if not tokens: continue
            cmd = tokens[0].upper()

            if cmd == "G90": relative_mode = False; continue
            if cmd == "G91": relative_mode = True; continue

            if cmd.startswith("G28"):
                for tok in tokens[1:]:
                    if len(tok) >= 2 and tok[0].upper() == "Z":
                        pos["Z"] = float(tok[1:])
                x0, y0, z0 = pos["X"], pos["Y"], pos["Z"]
                continue

            for tok in tokens[1:]:
                if len(tok) < 2: continue
                axis = tok[0].upper()
                try: val = float(tok[1:])
                except: continue
                if axis in ("X", "Y", "Z"):
                    if relative_mode: pos[axis] += val
                    else: pos[axis] = val
                elif axis == "E": pos["E"] = val

            x1, y1, z1 = pos["X"], pos["Y"], pos["Z"]

            if (x1, y1, z1) != (x0, y0, z0):
                seg_key = raw_line
                feature = self._classify_feature(x0, y0, x1, y1, raw_line)
                self.segment_dict[seg_key] = (x0, y0, z0, x1, y1, z1, feature)
                
                # Layer tracking by Z value — works for both FDM (E moves) and
                # laser scribing (no E axis). Every motion with a new Z = new layer.
                lz = round(z1, self.layer_round_digits)
                if current_layer_z is None or lz != current_layer_z:
                    current_layer_z = lz
                    self.layers.setdefault(current_layer_z, [])
                self.layers[current_layer_z].append(seg_key)

            x0, y0, z0 = x1, y1, z1

        self.layer_z_list = sorted(self.layers.keys())
        
        self.selected_layer_index = len(self.layer_z_list)-1 if self.layer_z_list else None
        self._update_info_label()
        self.fit_model()

    @Slot(str)
    def _onMarkSegment(self, gcode: str) -> None:
        if gcode in self.segment_dict:
            if self.processed_gcode:
                self.completed_segments.add(self.processed_gcode)
            self.processed_gcode = gcode
            
            x0, y0, z0, x1, y1, z1, feature = self.segment_dict[gcode]
            if feature != "travel":
                self.last_print_z = round(z1, self.layer_round_digits)
                self.current_print_layer = self.last_print_z
                
            self._update_info_label()
            self.sigRequestUpdate.emit()

    # -------------------------
    # OpenGL
    # -------------------------
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glDisable(GL_LIGHTING)
        glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, max(1, w), max(1, h))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w/h if h>0 else 1.0, 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        bg = (0.1, 0.1, 0.1) if self.dark_mode else (0.9, 0.9, 0.9)
        glClearColor(*bg, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.pan_x, self.pan_y, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 0, 1)
        glTranslatef(-self.model_center_x, -self.model_center_y, -self.model_center_z)

        self.drawGrid()
        self.drawVolume()
        self.drawAxes()
        self.drawSegments()

    def drawGrid(self):
        step = 10
        w, h = int(self.bed_width), int(self.bed_height)
        grid_color = (0.25, 0.25, 0.25, 1.0) if self.dark_mode else (0.6, 0.6, 0.6, 1.0)
        
        # Draw thin lines
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glColor4f(*grid_color)
        for i in range(0, w + 1, step):
            if i % 50 != 0:
                glVertex3f(i, 0, 0); glVertex3f(i, h, 0)
        for i in range(0, h + 1, step):
            if i % 50 != 0:
                glVertex3f(0, i, 0); glVertex3f(w, i, 0)
        glEnd()

        # Draw thick lines every 50mm
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor4f(*grid_color)
        for i in range(0, w + 1, step):
            if i % 50 == 0:
                glVertex3f(i, 0, 0); glVertex3f(i, h, 0)
        for i in range(0, h + 1, step):
            if i % 50 == 0:
                glVertex3f(0, i, 0); glVertex3f(w, i, 0)
        glEnd()
        glLineWidth(1.0)

    def drawVolume(self):
        w, h, z = self.bed_width, self.bed_height, self.bed_z_height
        glLineWidth(1.5)
        glColor4f(0.0, 0.8, 1.0, 0.7)
        # Bed base loop
        glBegin(GL_LINE_LOOP)
        glVertex3f(0,0,0); glVertex3f(w,0,0); glVertex3f(w,h,0); glVertex3f(0,h,0)
        glEnd()
        # Vertical posts + top loop
        glBegin(GL_LINES)
        glVertex3f(0,0,0); glVertex3f(0,0,z)
        glVertex3f(w,0,0); glVertex3f(w,0,z)
        glVertex3f(w,h,0); glVertex3f(w,h,z)
        glVertex3f(0,h,0); glVertex3f(0,h,z)
        glVertex3f(0,0,z); glVertex3f(w,0,z)
        glVertex3f(w,0,z); glVertex3f(w,h,z)
        glVertex3f(w,h,z); glVertex3f(0,h,z)
        glVertex3f(0,h,z); glVertex3f(0,0,z)
        glEnd()

    def drawAxes(self, axis_len=30):
        glLineWidth(4.0)
        glBegin(GL_LINES)
        glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(axis_len,0,0)
        glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,axis_len,0)
        glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,axis_len)
        glEnd()

    def drawSegments(self):
        if not self.segment_dict: return

        # If no layers were built (e.g. laser scribing with no E axis),
        # fall back to drawing every segment directly from segment_dict.
        if not self.layer_z_list:
            for seg, value in self.segment_dict.items():
                x0, y0, z0, x1, y1, z1, feature = value
                if feature == "travel" and not self.show_travel:
                    continue
                if seg == self.processed_gcode:
                    color, width = self.feature_style["active"]
                elif seg in self.completed_segments:
                    color, width = self.feature_style["completed"]
                else:
                    color, width = self.feature_style.get(feature, self.feature_style["wall"])
                glLineWidth(width)
                glBegin(GL_LINES)
                glColor4f(color.redF(), color.greenF(), color.blueF(), 1.0)
                glVertex3f(x0, y0, z0); glVertex3f(x1, y1, z1)
                glEnd()
            glLineWidth(1.0)
            return

        # Layer-based drawing (used when layers are present)
        if self.live_printing and self.current_print_layer is not None:
            idx = self.layer_z_list.index(self.current_print_layer)
            layer_keys = self.layer_z_list[:idx + 1]
        else:
            layer_keys = self.layer_z_list

        for z in layer_keys:
            for seg in self.layers.get(z, []):
                x0, y0, z0, x1, y1, z1, feature = self.segment_dict[seg]
                
                if feature == "travel" and not self.show_travel:
                    continue

                alpha = 1.0
                
                if seg == self.processed_gcode:
                    color, width = self.feature_style["active"]
                elif seg in self.completed_segments:
                    color, width = self.feature_style["completed"]
                else:
                    color, width = self.feature_style.get(feature, self.feature_style["wall"])

                glLineWidth(width)
                glBegin(GL_LINES)
                glColor4f(color.redF(), color.greenF(), color.blueF(), alpha)
                glVertex3f(x0, y0, z0); glVertex3f(x1, y1, z1)
                glEnd()
        glLineWidth(1.0)

    # -------------------------
    # Helpers
    # -------------------------
    def _update_info_label(self):
        total = len(self.layer_z_list)
        self.lbl_info.setText(f"Layers: {total}")

    def _classify_feature(self, x0, y0, x1, y1, line):
        """Classify a move segment for color coding.
        For laser scribing (no E axis):  G0 = travel, G1/G2/G3 = scribing.
        For FDM (has E axis): use extrusion distance heuristics.
        """
        tokens = line.split()
        cmd = tokens[0].upper() if tokens else ""

        # FDM path: check for extrusion
        if "E" in line.upper():
            dist = math.hypot(x1-x0, y1-y0)
            if dist < 2.0: return "wall"
            if abs(x1-x0) > 1.0 and abs(y1-y0) > 1.0: return "infill"
            return "skin"

        # Laser scribing path: G0 = rapid/travel, G1/G2/G3 = scribing move
        if cmd in ("G0", "G00"):
            return "travel"
        if cmd in ("G1", "G01", "G2", "G02", "G3", "G03"):
            return "wall"   # scribing move — shown in red

        return "travel"

    def fit_model(self):
        if not self.segment_dict: return
        xmin = ymin = zmin = float('inf')
        xmax = ymax = zmax = float('-inf')
        has_print = False
        for (x0,y0,z0,x1,y1,z1,feat) in self.segment_dict.values():
            if feat == "travel": continue
            xmin=min(xmin,x0,x1); xmax=max(xmax,x0,x1)
            ymin=min(ymin,y0,y1); ymax=max(ymax,y0,y1)
            zmin=min(zmin,z0,z1); zmax=max(zmax,z0,z1)
            has_print = True
        
        if not has_print:
            for (x0,y0,z0,x1,y1,z1,feat) in self.segment_dict.values():
                xmin=min(xmin,x0,x1); xmax=max(xmax,x0,x1)
                ymin=min(ymin,y0,y1); ymax=max(ymax,y0,y1)
                zmin=min(zmin,z0,z1); zmax=max(zmax,z0,z1)

        self.model_center_x = (xmin+xmax)/2.0
        self.model_center_y = (ymin+ymax)/2.0
        self.model_center_z = (zmin+zmax)/2.0
        dim = max(xmax-xmin, ymax-ymin, zmax-zmin, 1.0)
        self.zoom = -max(50.0, dim * 1.5)
        self.pan_x = self.pan_y = 0.0
        self.sigRequestUpdate.emit()

    # -------------------------
    # Interaction
    # -------------------------
    def mousePressEvent(self, event):
        self.last_mouse = event.position()
        self.press_pos = event.position()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'press_pos') and (event.position()-self.press_pos).manhattanLength() < 3:
            self.fit_model()

    def mouseMoveEvent(self, event):
        if self.last_mouse is None: return
        dx = event.position().x() - self.last_mouse.x()
        dy = event.position().y() - self.last_mouse.y()
        if event.buttons() & Qt.LeftButton:
            self.rot_y += dx * 0.5; self.rot_x += dy * 0.5
        elif event.buttons() & Qt.MiddleButton or (event.buttons() & Qt.LeftButton and (event.modifiers() & Qt.ControlModifier)):
            self.pan_x += dx * 0.2; self.pan_y -= dy * 0.2
        self.last_mouse = event.position()
        self.sigRequestUpdate.emit()

    def wheelEvent(self, event):
        factor = math.pow(1.2, event.angleDelta().y() / 120.0)
        self.zoom *= 1.0 / factor
        self.zoom = min(-1.0, max(-20000.0, self.zoom))
        self.sigRequestUpdate.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F: self.fit_model()
        elif event.key() == Qt.Key_A:
            self.selected_layer_index = None if self.selected_layer_index is not None else 0
            self.sigRequestUpdate.emit()
            self._update_info_label()
        super().keyPressEvent(event)

    def resetPreview(self):
        self.clear_marking()
        self.rot_x, self.rot_y, self.zoom, self.pan_x, self.pan_y = -60.0, -45.0, -100.0, 0.0, 0.0
        self.selected_layer_index = None
        self.update()
