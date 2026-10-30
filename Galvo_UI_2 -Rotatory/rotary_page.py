"""
Rotary Marking Page (EZCad2 RotaryMark / SplitMark2 / MarkDemo Compatible)
==========================================================================
Production-grade PySide6 user interface for cylindrical galvo laser marking.

Features:
- Live Dimension-Adaptive Pipeline: When workpiece diameter or height changes,
  EVERYTHING (circumference, pulse resolution, direct text, scale rulers, 360° wraps,
  optimal optical split sizes, 3D cylinder simulation, and slice bands) updates automatically!
- Quick Workpiece Dimension Bar: Immediate access to Part Ø (mm), Height / Length (mm),
  Circumference C (mm), Auto-Optimal Split, and Refresh directly on top of the canvas.
- Dual Canvas Preview: 2D Unwrapped View & Interactive 3D Cylindrical Orbit View.
- 3D Interactive Controls: Full 3D mouse orbit (roll 0°-360° + pitch tilt -50° to +50°),
  auto-spin 360° turntable animation, material themes (Brushed Steel, Anodized Black, Brass/Gold),
  X-Ray ghosted backside mode for 360° visibility, soft red laser apex fan beam, and 3D lathe chuck.
- Direct Vector Text Printing: Real-time text typing with font, size mm, bold/italic,
  orientation (circumferential wrap vs axial), 360° wrap fitting, and angular repetition.
- Editable Scale Ruler Generator: Graduated dials and rulers (angular degree 0°-360° and metric mm)
  with minor/medium/major ticks, side placement, baselines, and vector number labels.
- EZCad RingMark / MarkDemo Integration: 4-Way directional jog keypad (Up/Down rotate, Left/Right axial),
  Ring Inside marking mode (inverting pulses and internal bore focus), part/job counters and timers.
- Slice timeline & partition preview, manual split line placement, and active slice highlight.
- Non-blocking execution thread with red-light framing (F1), laser marking (F2), pause/resume, and E-Stop (F3).
- Hardware coordinate transformation pipeline (CoordinateConfig.apply_transform).
- Runs standalone (`python rotary_page.py`) or embedded in `main.py`.
"""

import sys
import os
import math
import re
import time
from typing import List, Tuple, Dict, Optional, Any

from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, Signal, Slot, QThread
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPainterPath, 
    QLinearGradient, QRadialGradient, QKeySequence, QShortcut,
    QPolygonF
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, 
    QComboBox, QDoubleSpinBox, QSpinBox, QGroupBox, QSplitter, 
    QProgressBar, QFileDialog, QMessageBox, QFrame, QRadioButton, 
    QButtonGroup, QScrollArea, QSizePolicy, QListWidget, QListWidgetItem,
    QTabWidget, QTextEdit, QDialog, QInputDialog
)

# Ensure root directory is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from rotary_slicer import RotarySlicingEngine, RotaryConfig, RotarySlice
from core.coordinate_mapper import CoordinateConfig


class CleanAxialSpinBox(QSpinBox):
    """QSpinBox for axial repeats that displays 'Auto (Square)' on 0 but cleanly accepts numeric typing without snapping to 0."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setKeyboardTracking(False)

    def textFromValue(self, val):
        if val == 0:
            return "0 (Auto Square)"
        return str(val)

    def valueFromText(self, text):
        clean = re.sub(r'[^0-9]', '', str(text))
        return int(clean) if clean else 0


def setup_smart_spinbox(sb, select_on_focus: bool = True):
    """
    Guarantees reliable, glitch-free number entry across all spinboxes:
    1. Disables keyboard tracking so intermediate keystrokes don't trigger premature recalculations.
    2. Auto-selects entire text on focus or click so typing immediately replaces the old number cleanly.
    3. Prevents cursor hopping or suffix mangling.
    """
    if hasattr(sb, 'setKeyboardTracking'):
        sb.setKeyboardTracking(False)
    if hasattr(sb, 'lineEdit'):
        le = sb.lineEdit()
        if le and select_on_focus:
            orig_focus_in = le.focusInEvent
            def _focus_in(event):
                orig_focus_in(event)
                QTimer.singleShot(0, le.selectAll)
            le.focusInEvent = _focus_in

            orig_mouse_press = le.mousePressEvent
            def _mouse_press(event):
                had_focus = le.hasFocus()
                orig_mouse_press(event)
                if not had_focus:
                    QTimer.singleShot(0, le.selectAll)
            le.mousePressEvent = _mouse_press


# =============================================================================
# 1. ENHANCED INTERACTIVE 3D & 2D CYLINDRICAL CANVAS WIDGET
# =============================================================================

class RotaryCanvasWidget(QWidget):
    """
    High-performance QPainter canvas displaying:
    1. Unwrapped 2D view: Workpiece axial length and circumference C = pi * D,
       slice partition bands, manual split lines, and active slice highlight.
    2. Interactive 3D Cylindrical Orbit View:
       - 3D mouse orbit: Horizontal roll (0°-360°) + vertical pitch/tilt (-50° to +50°).
       - Auto-Spin 360° turntable animation (smooth 60 FPS).
       - Material themes: Brushed Steel, Anodized Black, Brass / Gold.
       - X-Ray Mode: Ghosted translucent rendering of vectors on the backside of the cylinder.
       - Glowing top-dead-center (TDC) laser focus apex and fan beam.
       - Ring Inside visualization: Hollow bore with inside beam projection.
       - 3D lathe chuck with clamping jaws and degree markings.
    """
    sliceSelected = Signal(int)
    splitLineAdded = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(520, 460)
        self.setFocusPolicy(Qt.StrongFocus)

        # View mode: 'unwrapped_2d' or 'cylinder_3d'
        self.view_mode = 'cylinder_3d'

        # Artwork & Slicing State
        self.raw_paths: List[List[Tuple[float, float]]] = []
        self.slices: List[RotarySlice] = []
        self.active_slice_idx: int = -1
        self.hover_slice_idx: int = -1
        self.config: RotaryConfig = RotaryConfig()
        self.custom_split_lines: List[float] = []

        # Canvas Pan & Zoom
        self.zoom: float = 4.2  # screen pixels per mm
        self.pan_x: float = 260.0
        self.pan_y: float = 230.0
        self.is_panning: bool = False
        self.is_rotating_3d: bool = False
        self.last_mouse_pos = QPointF(0, 0)
        self.press_mouse_pos = QPointF(0, 0)

        # 3D Cylinder Orbit Angles (degrees)
        self.sim_cylinder_angle_deg: float = 0.0  # Horizontal roll (0°-360°)
        self.pitch_deg: float = 16.0             # Vertical tilt (-50° to +50°)

        # 3D Visual Options
        self.material_theme: str = 'Brushed Steel'  # 'Brushed Steel', 'Anodized Black', 'Brass / Gold'
        self.xray_mode: bool = True               # Ghosted backside lines
        self.ring_inside_mode: bool = False       # Inner bore marking

        # Auto-Spin Timer (60 FPS)
        self.auto_spin_timer = QTimer(self)
        self.auto_spin_timer.setInterval(16)
        self.auto_spin_timer.timeout.connect(self._on_auto_spin_tick)
        self.is_auto_spinning: bool = False

        self.setMouseTracking(True)

        # Interactive Artwork Selection, Resize & Rotation
        self.artwork_selected: bool = True
        self.is_dragging_artwork: bool = False
        self.is_resizing_artwork: bool = False
        self.is_rotating_artwork: bool = False
        self.active_resize_handle: int = -1
        self.show_slice_partitions: bool = False
        self.drag_start_mouse_pos = QPointF(0, 0)
        self.drag_start_offset_x: float = 0.0
        self.drag_start_offset_y: float = 0.0
        self.drag_start_rot: float = 0.0
        self.drag_start_angle: float = 0.0
        self.drag_center_screen = QPointF(0, 0)
        self.drag_start_width: float = 0.0
        self.drag_start_height: float = 0.0
        self.drag_start_scale_x: float = 100.0
        self.drag_start_scale_y: float = 100.0

        # Floating Canvas Overlay Bar (Rotate & Center directly on preview)
        self.overlay_bar = QFrame(self)
        self.overlay_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 24, 38, 225);
                border: 1px solid #2d3748;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #242b38;
                color: #e2e8f0;
                border: 1px solid #3e4c5e;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #0d3b66;
                color: #00d2ff;
                border-color: #00d2ff;
            }
        """)
        lay_ovl = QHBoxLayout(self.overlay_bar)
        lay_ovl.setContentsMargins(4, 4, 4, 4)
        lay_ovl.setSpacing(4)

        self.btn_ovl_rotate = QPushButton("🔄 Rotate (H ⇄ V)")
        self.btn_ovl_rotate.setToolTip("Click to toggle orientation between Horizontal and Vertical (90°)")
        self.btn_ovl_rotate.clicked.connect(self._on_ovl_rotate_clicked)
        lay_ovl.addWidget(self.btn_ovl_rotate)

        self.btn_ovl_ccw = QPushButton("⟲ -90°")
        self.btn_ovl_ccw.setToolTip("Rotate 90° Counter-Clockwise")
        self.btn_ovl_ccw.clicked.connect(lambda: self._on_ovl_rotate_step(-90.0))
        lay_ovl.addWidget(self.btn_ovl_ccw)

        self.btn_ovl_cw = QPushButton("⟳ +90°")
        self.btn_ovl_cw.setToolTip("Rotate 90° Clockwise")
        self.btn_ovl_cw.clicked.connect(lambda: self._on_ovl_rotate_step(90.0))
        lay_ovl.addWidget(self.btn_ovl_cw)

        self.btn_ovl_center = QPushButton("⊕ Center")
        self.btn_ovl_center.setToolTip("Center artwork on workpiece cylinder")
        self.btn_ovl_center.clicked.connect(self._on_ovl_center_clicked)
        lay_ovl.addWidget(self.btn_ovl_center)

        self.btn_ovl_wrap360 = QPushButton("⤢ 360° Wrap")
        self.btn_ovl_wrap360.setToolTip("Scale artwork/pattern to 100% cover pipe circumference")
        self.btn_ovl_wrap360.clicked.connect(self._on_ovl_wrap360_clicked)
        lay_ovl.addWidget(self.btn_ovl_wrap360)

        self.btn_ovl_flip_x = QPushButton("⇆ Flip X")
        self.btn_ovl_flip_x.setToolTip("Mirror horizontally (Flip artwork along X axis)")
        self.btn_ovl_flip_x.clicked.connect(self._on_ovl_flip_x_clicked)
        lay_ovl.addWidget(self.btn_ovl_flip_x)

        self.btn_ovl_flip_y = QPushButton("⇅ Flip Y")
        self.btn_ovl_flip_y.setToolTip("Mirror vertically (Flip artwork along Y axis)")
        self.btn_ovl_flip_y.clicked.connect(self._on_ovl_flip_y_clicked)
        lay_ovl.addWidget(self.btn_ovl_flip_y)

        self.btn_ovl_slices = QPushButton("👁 Slice Lines: OFF")
        self.btn_ovl_slices.setToolTip("Show / Hide slice partition lines in 2D preview")
        self.btn_ovl_slices.clicked.connect(self._on_ovl_toggle_slices)
        lay_ovl.addWidget(self.btn_ovl_slices)

    def set_data(self, paths: List[List[Tuple[float, float]]], slices: List[RotarySlice], config: RotaryConfig):
        """Updates artwork, slice partition data, and config. Re-frames view if diameter changed."""
        prev_d = getattr(self.config, 'diameter', None)
        self.raw_paths = paths
        self.slices = slices
        self.config = config
        self.custom_split_lines = getattr(config, 'custom_split_lines', [])
        self.ring_inside_mode = getattr(config, 'ring_inside', False)

        if prev_d is None or abs(prev_d - config.diameter) > 0.1:
            self.reset_view()
        else:
            self.update()

    def set_active_slice(self, idx: int):
        """Highlights the currently executing or selected slice."""
        self.active_slice_idx = idx
        if 0 <= idx < len(self.slices):
            self.sim_cylinder_angle_deg = self.slices[idx].rotation_angle_deg
        self.update()

    def set_view_mode(self, mode: str):
        """Toggles between 'unwrapped_2d' and 'cylinder_3d'."""
        self.view_mode = mode
        self.reset_view()
        self.update()

    def set_material_theme(self, theme: str):
        """Sets cylinder material shader."""
        self.material_theme = theme
        self.update()

    def set_xray_mode(self, enabled: bool):
        """Enables/disables ghosted backside vector rendering."""
        self.xray_mode = enabled
        self.update()

    def set_ring_inside_mode(self, enabled: bool):
        """Toggles Ring Inside visualization."""
        self.ring_inside_mode = enabled
        self.update()

    def toggle_auto_spin(self) -> bool:
        """Toggles 360-degree continuous turntable animation."""
        if self.is_auto_spinning:
            self.auto_spin_timer.stop()
            self.is_auto_spinning = False
        else:
            self.auto_spin_timer.start()
            self.is_auto_spinning = True
        return self.is_auto_spinning

    def _on_auto_spin_tick(self):
        """Advances 3D roll angle smoothly."""
        self.sim_cylinder_angle_deg = (self.sim_cylinder_angle_deg + 0.6) % 360.0
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay_bar') and self.overlay_bar:
            self.overlay_bar.adjustSize()
            x = self.width() - self.overlay_bar.width() - 10
            self.overlay_bar.move(max(10, x), 10)
            self.overlay_bar.raise_()

    def parent_page(self):
        p = self.parent()
        while p is not None:
            if hasattr(p, 'spn_offset_x') and hasattr(p, 'apply_artwork_transforms'):
                return p
            p = p.parent()
        return None

    def _on_ovl_rotate_clicked(self):
        p = self.parent_page()
        if p and hasattr(p, 'toggle_artwork_orientation'):
            p.toggle_artwork_orientation()

    def _on_ovl_rotate_step(self, delta: float):
        p = self.parent_page()
        if p and hasattr(p, 'rotate_artwork_by'):
            p.rotate_artwork_by(delta)

    def _on_ovl_center_clicked(self):
        p = self.parent_page()
        if p and hasattr(p, 'center_artwork_on_cylinder'):
            p.center_artwork_on_cylinder()

    def _on_ovl_wrap360_clicked(self):
        p = self.parent_page()
        if p and hasattr(p, 'fit_artwork_to_360'):
            p.fit_artwork_to_360()

    def get_artwork_screen_bbox(self):
        """Returns QRectF in screen pixels and (min_x, min_y, max_x, max_y) in mm."""
        if not self.raw_paths:
            return None
        xs = [pt[0] for poly in self.raw_paths for pt in poly]
        ys = [pt[1] for poly in self.raw_paths for pt in poly]
        if not xs or not ys:
            return None
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        sx0 = self.pan_x + (min_x * self.zoom)
        sy0 = self.pan_y + (min_y * self.zoom)
        sw = max(2.0, (max_x - min_x) * self.zoom)
        sh = max(2.0, (max_y - min_y) * self.zoom)
        return QRectF(sx0, sy0, sw, sh), (min_x, min_y, max_x, max_y)

    HANDLE_NONE = -1
    HANDLE_TL = 0
    HANDLE_TR = 1
    HANDLE_BL = 2
    HANDLE_BR = 3
    HANDLE_T = 4
    HANDLE_B = 5
    HANDLE_L = 6
    HANDLE_R = 7

    def _on_ovl_flip_x_clicked(self):
        p = self.parent_page()
        if p and hasattr(p, 'toggle_mirror_x'):
            p.toggle_mirror_x()

    def _on_ovl_flip_y_clicked(self):
        p = self.parent_page()
        if p and hasattr(p, 'toggle_mirror_y'):
            p.toggle_mirror_y()

    def _on_ovl_toggle_slices(self):
        self.show_slice_partitions = not self.show_slice_partitions
        if hasattr(self, 'btn_ovl_slices'):
            if self.show_slice_partitions:
                self.btn_ovl_slices.setText("👁 Slice Lines: ON")
                self.btn_ovl_slices.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;")
            else:
                self.btn_ovl_slices.setText("👁 Slice Lines: OFF")
                self.btn_ovl_slices.setStyleSheet("")
        p = self.parent_page()
        if p and hasattr(p, 'chk_show_slice_partitions'):
            p.chk_show_slice_partitions.blockSignals(True)
            p.chk_show_slice_partitions.setChecked(self.show_slice_partitions)
            p.chk_show_slice_partitions.blockSignals(False)
        self.update()

    def _get_handle_under_mouse(self, pos: QPointF, rect: QRectF) -> int:
        h_sz = 7.0
        handles = {
            self.HANDLE_TL: QPointF(rect.left(), rect.top()),
            self.HANDLE_TR: QPointF(rect.right(), rect.top()),
            self.HANDLE_BL: QPointF(rect.left(), rect.bottom()),
            self.HANDLE_BR: QPointF(rect.right(), rect.bottom()),
            self.HANDLE_T:  QPointF(rect.center().x(), rect.top()),
            self.HANDLE_B:  QPointF(rect.center().x(), rect.bottom()),
            self.HANDLE_L:  QPointF(rect.left(), rect.center().y()),
            self.HANDLE_R:  QPointF(rect.right(), rect.center().y()),
        }
        for h_id, pt in handles.items():
            if math.hypot(pos.x() - pt.x(), pos.y() - pt.y()) <= h_sz + 4.0:
                return h_id
        return self.HANDLE_NONE

    def _is_on_rotation_pin(self, pos: QPointF) -> bool:
        res = self.get_artwork_screen_bbox()
        if not res:
            return False
        rect, _ = res
        pin_cx = rect.center().x()
        pin_cy = rect.top() - 22.0
        return math.hypot(pos.x() - pin_cx, pos.y() - pin_cy) <= 14.0

    def _is_inside_artwork_bbox(self, pos: QPointF) -> bool:
        res = self.get_artwork_screen_bbox()
        if not res:
            return False
        rect, _ = res
        return rect.adjusted(-8, -8, 8, 8).contains(pos)

    def reset_view(self):
        """Fits artwork and cylinder into viewport with healthy margins based on current diameter & length."""
        w = max(100, self.width())
        h = max(100, self.height())

        c = max(10.0, self.config.circumference)
        axial_len = max(20.0, getattr(self.config, 'axial_length', 50.0))
        if self.raw_paths:
            xs = [pt[0] for poly in self.raw_paths for pt in poly]
            if xs:
                axial_len = max(axial_len, max(xs) - min(0.0, min(xs)) + 25.0)

        if self.view_mode == 'unwrapped_2d':
            fit_scale_x = (w * 0.74) / max(10.0, axial_len)
            fit_scale_y = (h * 0.74) / max(10.0, c)
            self.zoom = max(0.8, min(fit_scale_x, fit_scale_y))
            self.pan_x = (w - (axial_len * self.zoom)) / 2.0
            self.pan_y = (h - (c * self.zoom)) / 2.0
        else:
            self.pan_x = w * 0.48
            self.pan_y = h * 0.52
            r_est = max(1.0, self.config.diameter) / 2.0
            # Frame workpiece nicely (taking ~65% of screen height/width)
            self.zoom = min(w / (axial_len * 1.5), h / (r_est * 5.2))
            self.zoom = max(1.0, min(25.0, self.zoom))
            self.pitch_deg = 16.0

        self.update()

    # --- Mouse Interaction (Pan, Zoom, 3D Orbit Drag, Slice Selection) ---
    def wheelEvent(self, event):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        new_zoom = max(0.4, min(40.0, self.zoom * zoom_factor))

        mouse_pos = event.position()
        self.pan_x = mouse_pos.x() - (mouse_pos.x() - self.pan_x) * (new_zoom / self.zoom)
        self.pan_y = mouse_pos.y() - (mouse_pos.y() - self.pan_y) * (new_zoom / self.zoom)
        self.zoom = new_zoom
        self.update()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.position()
        self.press_mouse_pos = event.position()

        if event.button() == Qt.LeftButton:
            if self.view_mode == 'cylinder_3d':
                self.is_rotating_3d = True
            else:
                # 2D Unwrapped View
                res = self.get_artwork_screen_bbox()
                if res:
                    rect, (min_x, min_y, max_x, max_y) = res
                    # Check 1: Click on top rotation pin handle
                    if self._is_on_rotation_pin(event.position()):
                        self.is_rotating_artwork = True
                        self.drag_start_mouse_pos = event.position()
                        p = self.parent_page()
                        self.drag_start_rot = p.spn_art_rotation.value() if (p and hasattr(p, 'spn_art_rotation')) else 0.0
                        self.drag_center_screen = rect.center()
                        v = event.position() - self.drag_center_screen
                        self.drag_start_angle = math.degrees(math.atan2(v.y(), v.x()))
                        self.setCursor(Qt.PointingHandCursor)
                        return

                    # Check 2: Click on one of 8 resize handles
                    handle = self._get_handle_under_mouse(event.position(), rect)
                    if handle != self.HANDLE_NONE:
                        self.is_resizing_artwork = True
                        self.active_resize_handle = handle
                        self.drag_start_mouse_pos = event.position()
                        p = self.parent_page()
                        self.drag_start_width = max(0.1, max_x - min_x)
                        self.drag_start_height = max(0.1, max_y - min_y)
                        self.drag_start_scale_x = p.spn_scale_x.value() if (p and hasattr(p, 'spn_scale_x')) else 100.0
                        self.drag_start_scale_y = p.spn_scale_y.value() if (p and hasattr(p, 'spn_scale_y')) else 100.0
                        self.drag_start_offset_x = p.spn_offset_x.value() if (p and hasattr(p, 'spn_offset_x')) else 0.0
                        self.drag_start_offset_y = p.spn_offset_y.value() if (p and hasattr(p, 'spn_offset_y')) else 0.0
                        return

                    # Check 3: Click on/inside artwork bounding box to select & drag relocate
                    if self._is_inside_artwork_bbox(event.position()):
                        self.artwork_selected = True
                        self.is_dragging_artwork = True
                        self.drag_start_mouse_pos = event.position()
                        p = self.parent_page()
                        if p and hasattr(p, 'spn_offset_x') and hasattr(p, 'spn_offset_y'):
                            self.drag_start_offset_x = p.spn_offset_x.value()
                            self.drag_start_offset_y = p.spn_offset_y.value()
                        self.setCursor(Qt.ClosedHandCursor)
                        self.update()
                        return
                    else:
                        self.is_panning = True
                else:
                    self.is_panning = True
        elif event.button() in (Qt.MiddleButton, Qt.RightButton):
            self.is_panning = True

    def mouseMoveEvent(self, event):
        pos = event.position()
        delta = pos - self.last_mouse_pos

        if self.is_rotating_artwork:
            v = pos - self.drag_center_screen
            current_angle = math.degrees(math.atan2(v.y(), v.x()))
            delta_angle = current_angle - self.drag_start_angle
            raw_angle = self.drag_start_rot + delta_angle
            if event.modifiers() & Qt.ShiftModifier:
                new_rot = round(raw_angle / 15.0) * 15.0
            else:
                new_rot = round(raw_angle, 1)
            new_rot = ((new_rot + 180.0) % 360.0) - 180.0
            p = self.parent_page()
            if p and hasattr(p, 'interactive_rotate_artwork'):
                p.interactive_rotate_artwork(new_rot)
            self.last_mouse_pos = pos
            return
        elif self.is_resizing_artwork:
            delta_px = pos - self.drag_start_mouse_pos
            delta_x_mm = delta_px.x() / self.zoom
            delta_y_mm = delta_px.y() / self.zoom
            p = self.parent_page()
            if p and hasattr(p, 'interactive_resize_artwork'):
                p.interactive_resize_artwork(
                    self.active_resize_handle,
                    delta_x_mm, delta_y_mm,
                    self.drag_start_scale_x, self.drag_start_scale_y,
                    self.drag_start_offset_x, self.drag_start_offset_y,
                    self.drag_start_width, self.drag_start_height,
                    shift_held=bool(event.modifiers() & Qt.ShiftModifier)
                )
            self.last_mouse_pos = pos
            return
        elif self.is_dragging_artwork:
            delta_px = pos - self.drag_start_mouse_pos
            delta_x_mm = delta_px.x() / self.zoom
            delta_y_mm = delta_px.y() / self.zoom
            p = self.parent_page()
            if p and hasattr(p, 'interactive_move_artwork'):
                new_x = round(self.drag_start_offset_x + delta_x_mm, 2)
                new_y = round(self.drag_start_offset_y + delta_y_mm, 2)
                p.interactive_move_artwork(new_x, new_y)
            self.last_mouse_pos = pos
            return
        elif self.is_rotating_3d and self.view_mode == 'cylinder_3d':
            roll_delta = delta.x() * 0.55
            self.sim_cylinder_angle_deg = (self.sim_cylinder_angle_deg + roll_delta) % 360.0
            pitch_delta = -delta.y() * 0.4
            self.pitch_deg = max(-50.0, min(50.0, self.pitch_deg + pitch_delta))
            self.update()
        elif self.is_panning:
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.update()
        else:
            # 2D Hover detection for artwork selection handles and slice partitions
            if self.view_mode == 'unwrapped_2d' and self.raw_paths:
                res = self.get_artwork_screen_bbox()
                if res:
                    rect, _ = res
                    if self._is_on_rotation_pin(pos):
                        self.setCursor(Qt.PointingHandCursor)
                        self.setToolTip("Drag to Rotate Artwork Smoothly | Click to Rotate 90°")
                    else:
                        h_id = self._get_handle_under_mouse(pos, rect)
                        if h_id in (self.HANDLE_TL, self.HANDLE_BR):
                            self.setCursor(Qt.SizeFDiagCursor)
                            self.setToolTip("Drag to Resize (Diagonal)")
                        elif h_id in (self.HANDLE_TR, self.HANDLE_BL):
                            self.setCursor(Qt.SizeBDiagCursor)
                            self.setToolTip("Drag to Resize (Diagonal)")
                        elif h_id in (self.HANDLE_T, self.HANDLE_B):
                            self.setCursor(Qt.SizeVerCursor)
                            self.setToolTip("Drag to Resize Height")
                        elif h_id in (self.HANDLE_L, self.HANDLE_R):
                            self.setCursor(Qt.SizeHorCursor)
                            self.setToolTip("Drag to Resize Width")
                        elif self._is_inside_artwork_bbox(pos):
                            self.setCursor(Qt.SizeAllCursor)
                            self.setToolTip("Click and Drag to Relocate Artwork on Workpiece")
                        else:
                            self.setCursor(Qt.ArrowCursor)
                            self.setToolTip("")

            if self.view_mode == 'unwrapped_2d' and self.slices and getattr(self, 'show_slice_partitions', False):
                c_y = (pos.y() - self.pan_y) / self.zoom if self.config.axis.upper() == 'Y' else (pos.x() - self.pan_x) / self.zoom
                hovered = -1
                for idx, sl in enumerate(self.slices):
                    b0, b1 = sl.bounds_orig
                    if b0 <= c_y <= b1:
                        hovered = idx
                        break
                if hovered != self.hover_slice_idx:
                    self.hover_slice_idx = hovered
                    self.update()

        self.last_mouse_pos = pos

    def mouseReleaseEvent(self, event):
        if self.is_rotating_artwork:
            self.is_rotating_artwork = False
            drag_dist = (event.position() - self.drag_start_mouse_pos).manhattanLength()
            p = self.parent_page()
            if drag_dist < 4.0:
                if p and hasattr(p, 'toggle_artwork_orientation'):
                    p.toggle_artwork_orientation()
            else:
                if p and hasattr(p, 'apply_artwork_transforms'):
                    p.apply_artwork_transforms()
            self.update()
            return

        if self.is_resizing_artwork:
            self.is_resizing_artwork = False
            p = self.parent_page()
            if p and hasattr(p, 'apply_artwork_transforms'):
                p.apply_artwork_transforms()
            self.update()
            return

        if self.is_dragging_artwork:
            self.is_dragging_artwork = False
            self.setCursor(Qt.SizeAllCursor if self._is_inside_artwork_bbox(event.position()) else Qt.ArrowCursor)
            p = self.parent_page()
            if p and hasattr(p, 'apply_artwork_transforms'):
                p.apply_artwork_transforms()
            self.update()
            return

        drag_dist = (event.position() - self.press_mouse_pos).manhattanLength()
        if drag_dist < 6.0 and event.button() == Qt.LeftButton and self.view_mode == 'unwrapped_2d':
            pos = event.position()
            is_y = (self.config.axis.upper() == 'Y')
            val = (pos.y() - self.pan_y) / self.zoom if is_y else (pos.x() - self.pan_x) / self.zoom

            # If mode is split by line, clicking adds a split line
            if getattr(self.config, 'mode', '') == 'split_by_line':
                if 0.0 <= val <= self.config.circumference:
                    self.splitLineAdded.emit(round(val, 2))

            # Select slice under click
            clicked_slice = -1
            for sl in self.slices:
                b0, b1 = sl.bounds_orig
                if b0 <= val <= b1:
                    clicked_slice = sl.slice_index
                    break

            if clicked_slice != -1:
                self.set_active_slice(clicked_slice)
                self.sliceSelected.emit(clicked_slice)

        self.is_panning = False
        self.is_rotating_3d = False

    # --- QPainter Rendering Engine ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # 1. Background Grid
        painter.fillRect(self.rect(), QColor("#101319"))
        self._draw_grid(painter)

        if self.view_mode == 'unwrapped_2d':
            self._render_unwrapped_2d(painter)
        else:
            self._render_cylinder_3d(painter)

        # 2. Viewport HUD Overlay
        self._render_hud(painter)

    def _draw_grid(self, painter: QPainter):
        """Draws millimeter grid."""
        painter.save()
        grid_step_px = 10.0 * self.zoom
        if grid_step_px > 6.0:
            pen = QPen(QColor(30, 36, 48, 110), 1, Qt.DotLine)
            painter.setPen(pen)

            start_x = self.pan_x % grid_step_px
            while start_x < self.width():
                painter.drawLine(int(start_x), 0, int(start_x), self.height())
                start_x += grid_step_px

            start_y = self.pan_y % grid_step_px
            while start_y < self.height():
                painter.drawLine(0, int(start_y), self.width(), int(start_y))
                start_y += grid_step_px

        # Origin Crosshair (0, 0)
        painter.setPen(QPen(QColor("#00d2ff"), 1.2, Qt.DashLine))
        painter.drawLine(int(self.pan_x - 15), int(self.pan_y), int(self.pan_x + 15), int(self.pan_y))
        painter.drawLine(int(self.pan_x), int(self.pan_y - 15), int(self.pan_x), int(self.pan_y + 15))
        painter.restore()

    def _render_unwrapped_2d(self, painter: QPainter):
        """Renders 2D unwrapped workpiece area, slice partitions, and artwork."""
        painter.save()
        c = max(1.0, self.config.circumference)
        axial_len = max(20.0, getattr(self.config, 'axial_length', 50.0))
        if self.raw_paths:
            xs = [pt[0] for poly in self.raw_paths for pt in poly]
            if xs:
                axial_len = max(axial_len, max(xs) + 15.0)

        is_y = (self.config.axis.upper() == 'Y')
        rect_w = (axial_len if is_y else c) * self.zoom
        rect_h = (c if is_y else axial_len) * self.zoom
        rect_x = self.pan_x
        rect_y = self.pan_y

        # Workpiece Boundary
        painter.setPen(QPen(QColor("#0099cc"), 1.8))
        painter.setBrush(QBrush(QColor(18, 28, 42, 190)))
        painter.drawRect(QRectF(rect_x, rect_y, rect_w, rect_h))

        # Circumference & Length Annotations
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(QColor("#00d2ff"))
        if is_y:
            painter.drawText(int(rect_x + 4), int(rect_y - 8), f"◄ Workpiece Axial Length: {axial_len:.1f} mm ►")
            painter.drawText(int(rect_x + rect_w + 8), int(rect_y + rect_h / 2), f"Circumference: {c:.2f} mm (360°)")
        else:
            painter.drawText(int(rect_x + 4), int(rect_y - 8), f"Circumference: {c:.2f} mm (360°)")
            painter.drawText(int(rect_x + rect_w + 8), int(rect_y + rect_h / 2), f"Axial: {axial_len:.1f} mm")

        # Render Slice Partitions (only when enabled by user)
        if getattr(self, 'show_slice_partitions', False):
            for sl in self.slices:
                is_active = (sl.slice_index == self.active_slice_idx)
                is_hover = (sl.slice_index == self.hover_slice_idx)

                s_start = sl.bounds_orig[0]
                s_end = sl.bounds_orig[1]
                s_size = s_end - s_start

                if is_y:
                    sx = rect_x
                    sy = self.pan_y + (s_start * self.zoom)
                    sw = rect_w
                    sh = s_size * self.zoom
                else:
                    sx = self.pan_x + (s_start * self.zoom)
                    sy = rect_y
                    sw = s_size * self.zoom
                    sh = rect_h

                band_rect = QRectF(sx, sy, sw, sh)

                if is_active:
                    painter.setPen(QPen(QColor("#00ff66"), 2.2))
                    painter.setBrush(QBrush(QColor(0, 255, 102, 50)))
                    painter.drawRect(band_rect)
                elif is_hover:
                    painter.setPen(QPen(QColor("#00d2ff"), 1.8))
                    painter.setBrush(QBrush(QColor(0, 210, 255, 35)))
                    painter.drawRect(band_rect)
                else:
                    painter.setPen(QPen(QColor(255, 255, 255, 45), 1, Qt.DashLine))
                    painter.setBrush(QBrush(QColor(255, 255, 255, 6)))
                    painter.drawRect(band_rect)

                # Slice number badge
                step_skip = max(1, len(self.slices) // 25)
                if sl.slice_index % step_skip == 0 or is_active:
                    painter.setPen(QColor(220, 255, 220) if is_active else QColor(160, 175, 190, 150))
                    painter.setFont(QFont("Segoe UI", 8, QFont.Bold if is_active else QFont.Normal))
                    if is_y:
                        painter.drawText(int(rect_x + rect_w - 46), int(sy + 12), f"#{sl.slice_index + 1}")
                    else:
                        painter.drawText(int(sx + 3), int(rect_y + 12), f"#{sl.slice_index + 1}")

        # Render Custom Split Lines
        if getattr(self.config, 'mode', '') == 'split_by_line' and self.custom_split_lines:
            painter.setPen(QPen(QColor("#ffaa00"), 1.8, Qt.DashDotLine))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            for val in self.custom_split_lines:
                if is_y:
                    line_y = self.pan_y + (val * self.zoom)
                    painter.drawLine(int(rect_x - 10), int(line_y), int(rect_x + rect_w + 10), int(line_y))
                    painter.setPen(QColor("#ffaa00"))
                    painter.drawText(int(rect_x + rect_w + 12), int(line_y + 4), f"Split: {val:.2f}mm")
                else:
                    line_x = self.pan_x + (val * self.zoom)
                    painter.drawLine(int(line_x), int(rect_y - 10), int(line_x), int(rect_y + rect_h + 10))
                    painter.setPen(QColor("#ffaa00"))
                    painter.drawText(int(line_x + 2), int(rect_y - 12), f"Split: {val:.2f}mm")

        # Render Base Artwork Vectors
        pen_art = QPen(QColor("#e2e8f0"), 1.3)
        painter.setPen(pen_art)
        painter.setBrush(Qt.NoBrush)

        for poly in self.raw_paths:
            if len(poly) < 2:
                continue
            path = QPainterPath()
            p0 = poly[0]
            path.moveTo(self.pan_x + (p0[0] * self.zoom), self.pan_y + (p0[1] * self.zoom))
            for pt in poly[1:]:
                path.lineTo(self.pan_x + (pt[0] * self.zoom), self.pan_y + (pt[1] * self.zoom))
            painter.drawPath(path)

        # Reference Contour Borders (when contour marking is disabled, preview borders so user can still see them)
        p_page = self.parent_page()
        if p_page and hasattr(p_page, 'chk_hatch_enable') and hasattr(p_page, 'chk_hatch_mark_contour'):
            show_ref = getattr(p_page, 'chk_hatch_preview_reference_contour', None)
            should_show_ref = (show_ref.isChecked() if show_ref else True)
            if p_page.chk_hatch_enable.isChecked() and not p_page.chk_hatch_mark_contour.isChecked() and should_show_ref:
                ref_paths = getattr(p_page, 'preview_contour_paths', [])
                if ref_paths:
                    ref_pen = QPen(QColor(0, 220, 255, 170), 1.2, Qt.DashLine)
                    painter.setPen(ref_pen)
                    painter.setBrush(Qt.NoBrush)
                    for poly in ref_paths:
                        if len(poly) < 2:
                            continue
                        path = QPainterPath()
                        path.moveTo(self.pan_x + (poly[0][0] * self.zoom), self.pan_y + (poly[0][1] * self.zoom))
                        for pt in poly[1:]:
                            path.lineTo(self.pan_x + (pt[0] * self.zoom), self.pan_y + (pt[1] * self.zoom))
                        painter.drawPath(path)

        # Highlight Active Slice Vectors in Glowing Neon
        if 0 <= self.active_slice_idx < len(self.slices):
            active_sl = self.slices[self.active_slice_idx]
            glow_pen = QPen(QColor("#00ff66"), 2.4)
            painter.setPen(glow_pen)
            for poly in active_sl.unwrapped_paths:
                if len(poly) < 2:
                    continue
                path = QPainterPath()
                path.moveTo(self.pan_x + (poly[0][0] * self.zoom), self.pan_y + (poly[0][1] * self.zoom))
                for pt in poly[1:]:
                    path.lineTo(self.pan_x + (pt[0] * self.zoom), self.pan_y + (pt[1] * self.zoom))
                painter.drawPath(path)

        # Render Interactive Artwork Selection Box, Handles, and Rotation Pin
        if self.artwork_selected and self.raw_paths:
            res = self.get_artwork_screen_bbox()
            if res:
                rect, (min_x, min_y, max_x, max_y) = res
                w_mm = max_x - min_x
                h_mm = max_y - min_y
                is_vert = (h_mm > w_mm)
                orient_lbl = "VERTICAL" if is_vert else "HORIZONTAL"

                # 1. Bounding Box Outline
                box_color = QColor("#00d2ff") if self.is_dragging_artwork else QColor("#00ff66")
                painter.setPen(QPen(box_color, 1.6, Qt.DashLine))
                painter.setBrush(QBrush(QColor(0, 255, 102, 12) if not self.is_dragging_artwork else QColor(0, 210, 255, 25)))
                painter.drawRect(rect)

                # 2. Handles (8 resize/anchor squares)
                h_pts = [
                    rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight(),
                    QPointF(rect.center().x(), rect.top()),
                    QPointF(rect.center().x(), rect.bottom()),
                    QPointF(rect.left(), rect.center().y()),
                    QPointF(rect.right(), rect.center().y())
                ]
                painter.setPen(QPen(box_color, 1.2))
                painter.setBrush(QBrush(QColor("#ffffff")))
                for hp in h_pts:
                    painter.drawRect(QRectF(hp.x() - 3.5, hp.y() - 3.5, 7.0, 7.0))

                # 3. Center Crosshair
                c_pt = rect.center()
                painter.setPen(QPen(box_color, 1.0))
                painter.drawLine(int(c_pt.x() - 6), int(c_pt.y()), int(c_pt.x() + 6), int(c_pt.y()))
                painter.drawLine(int(c_pt.x()), int(c_pt.y() - 6), int(c_pt.x()), int(c_pt.y() + 6))

                # 4. Rotation Pin Handle (protruding above top edge)
                pin_cx = c_pt.x()
                pin_cy = rect.top() - 22.0
                painter.setPen(QPen(box_color, 1.5))
                painter.drawLine(int(pin_cx), int(rect.top()), int(pin_cx), int(pin_cy + 8.0))

                painter.setBrush(QBrush(QColor(16, 32, 54, 230)))
                painter.drawEllipse(QPointF(pin_cx, pin_cy), 8.5, 8.5)
                painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
                painter.setPen(QColor("#00ff66" if not is_vert else "#00d2ff"))
                painter.drawText(int(pin_cx - 4.5), int(pin_cy + 4.5), "⟳")

                # 5. Dimension & Orientation Pill Badge
                badge_text = f"⬚ {w_mm:.1f} x {h_mm:.1f} mm  •  [{orient_lbl}]  •  Drag to Move"
                painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
                fm = painter.fontMetrics()
                badge_w = fm.horizontalAdvance(badge_text) + 16
                badge_h = 18
                badge_x = int(c_pt.x() - badge_w / 2)
                badge_y = int(rect.bottom() + 6)
                badge_rect = QRectF(badge_x, badge_y, badge_w, badge_h)

                painter.setPen(QPen(QColor("#2d3748"), 1))
                painter.setBrush(QBrush(QColor(16, 24, 38, 220)))
                painter.drawRoundedRect(badge_rect, 4, 4)

                painter.setPen(QColor("#00d2ff" if is_vert else "#00ff66"))
                painter.drawText(badge_rect, Qt.AlignCenter, badge_text)

        painter.restore()

    def _render_cylinder_3d(self, painter: QPainter):
        """
        Renders fully interactive 3D cylindrical workpiece with:
        - Roll rotation (0°-360°) and pitch/tilt perspective (-50° to +50°).
        - Material themes: Brushed Steel, Anodized Black, Brass/Gold.
        - Lathe 3-jaw chuck with rotating degree markings.
        - Laser focus apex fan beam and top dead center line.
        - X-Ray ghosted backside vectors.
        - Ring Inside hollow bore view when ring_inside_mode is enabled.
        """
        painter.save()
        cx = self.pan_x
        cy = self.pan_y

        r_mm = max(1.0, self.config.diameter) / 2.0
        r_px = r_mm * self.zoom
        axial_len_mm = max(20.0, getattr(self.config, 'axial_length', 50.0))
        length_px = axial_len_mm * self.zoom

        pitch_rad = math.radians(self.pitch_deg)
        roll_rad = math.radians(self.sim_cylinder_angle_deg)
        circ = max(1.0, self.config.circumference)
        is_y = (self.config.axis.upper() == 'Y')

        # 3D Center offsets for cylinder ends
        half_len = length_px / 2.0
        x_left = cx - half_len * math.cos(pitch_rad)
        y_left = cy - half_len * math.sin(pitch_rad) * 0.25

        x_right = cx + half_len * math.cos(pitch_rad)
        y_right = cy + half_len * math.sin(pitch_rad) * 0.25

        # End Cap Ellipse radii
        cap_rx = max(4.0, r_px * max(0.2, abs(math.sin(pitch_rad)) + 0.35))
        cap_ry = r_px

        # -------------------------------------------------------------
        # A. Lathe Chuck Clamping Head (Left End)
        # -------------------------------------------------------------
        chuck_w = max(25.0, 32.0 * (self.zoom / 4.0))
        chuck_rect = QRectF(x_left - chuck_w, y_left - (r_px * 1.35), chuck_w, r_px * 2.7)
        grad_chuck = QLinearGradient(chuck_rect.left(), chuck_rect.top(), chuck_rect.left(), chuck_rect.bottom())
        grad_chuck.setColorAt(0.0, QColor("#1f242d"))
        grad_chuck.setColorAt(0.5, QColor("#3f495a"))
        grad_chuck.setColorAt(1.0, QColor("#181c24"))
        painter.setPen(QPen(QColor("#4f5b70"), 1.5))
        painter.setBrush(grad_chuck)
        painter.drawRoundedRect(chuck_rect, 4, 4)

        # Chuck Jaws & Degree Dial
        painter.setPen(QPen(QColor("#00d2ff"), 1.5))
        painter.drawLine(int(x_left - chuck_w), int(y_left), int(x_left), int(y_left))
        # Degree readout on chuck
        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        painter.setPen(QColor("#00e5ff"))
        painter.drawText(int(x_left - chuck_w + 3), int(y_left - (r_px * 0.7)), f"{int(self.sim_cylinder_angle_deg):03d}°")

        # -------------------------------------------------------------
        # B. Cylinder Body Gradient Material
        # -------------------------------------------------------------
        grad_body = QLinearGradient(cx, cy - r_px, cx, cy + r_px)
        if self.material_theme == 'Anodized Black':
            grad_body.setColorAt(0.0, QColor("#121418"))
            grad_body.setColorAt(0.25, QColor("#222831"))
            grad_body.setColorAt(0.5, QColor("#393e46"))  # Subtle highlight
            grad_body.setColorAt(0.75, QColor("#1e232a"))
            grad_body.setColorAt(1.0, QColor("#0d0f12"))
            stroke_color = QColor("#4b5563")
        elif self.material_theme == 'Brass / Gold':
            grad_body.setColorAt(0.0, QColor("#5a4212"))
            grad_body.setColorAt(0.2, QColor("#997223"))
            grad_body.setColorAt(0.5, QColor("#f4d06f"))  # Warm golden apex
            grad_body.setColorAt(0.8, QColor("#85621c"))
            grad_body.setColorAt(1.0, QColor("#3e2c0b"))
            stroke_color = QColor("#d4af37")
        else: # 'Brushed Steel' (Default)
            grad_body.setColorAt(0.0, QColor("#252d3a"))
            grad_body.setColorAt(0.2, QColor("#4f5e74"))
            grad_body.setColorAt(0.5, QColor("#a6b9d0"))  # Sharp metallic reflection
            grad_body.setColorAt(0.8, QColor("#3b4759"))
            grad_body.setColorAt(1.0, QColor("#1b212b"))
            stroke_color = QColor("#72849c")

        # Cylinder Body Path (connecting left cap to right cap)
        body_path = QPainterPath()
        body_path.moveTo(x_left, y_left - r_px)
        body_path.lineTo(x_right, y_right - r_px)
        body_path.arcTo(x_right - cap_rx, y_right - cap_ry, cap_rx * 2, cap_ry * 2, 90, -180)
        body_path.lineTo(x_left, y_left + r_px)
        body_path.arcTo(x_left - cap_rx, y_left - cap_ry, cap_rx * 2, cap_ry * 2, 270, -180)
        body_path.closeSubpath()

        painter.setPen(QPen(stroke_color, 1.4))
        painter.setBrush(grad_body)
        painter.drawPath(body_path)

        # Right Free End Cap
        cap_rect = QRectF(x_right - cap_rx, y_right - cap_ry, cap_rx * 2, cap_ry * 2)
        grad_cap = QRadialGradient(x_right, y_right, cap_ry)
        grad_cap.setColorAt(0.0, QColor("#445265") if self.material_theme != 'Brass / Gold' else QColor("#aa842d"))
        grad_cap.setColorAt(1.0, QColor("#1e242e") if self.material_theme != 'Brass / Gold' else QColor("#48340d"))
        painter.setBrush(grad_cap)
        painter.drawEllipse(cap_rect)

        # Hollow Ring Inside visualization
        if self.ring_inside_mode:
            inner_r_px = r_px * 0.72
            inner_cap_rx = cap_rx * 0.72
            inner_rect = QRectF(x_right - inner_cap_rx, y_right - inner_r_px, inner_cap_rx * 2, inner_r_px * 2)
            painter.setBrush(QColor("#080a0e"))
            painter.setPen(QPen(QColor("#00d2ff"), 1.2, Qt.DashLine))
            painter.drawEllipse(inner_rect)

        # -------------------------------------------------------------
        # C. 3D Active Slice Band Highlight
        # -------------------------------------------------------------
        if 0 <= self.active_slice_idx < len(self.slices):
            active_sl = self.slices[self.active_slice_idx]
            s_start = active_sl.bounds_orig[0]

            if is_y:
                arc_angle_deg = (s_start / circ) * 360.0 - self.sim_cylinder_angle_deg
                glow_pen = QPen(QColor("#00ff66"), 3.0)
                painter.setPen(glow_pen)
                ring_x = x_left + (length_px * 0.5)
                painter.drawArc(QRectF(ring_x - cap_rx, cy - cap_ry, cap_rx * 2, cap_ry * 2), int(arc_angle_deg * 16), int(30 * 16))
            else:
                strip_x0 = x_left + (s_start * self.zoom)
                strip_w = (active_sl.bounds_orig[1] - s_start) * self.zoom
                painter.setPen(QPen(QColor("#00ff66"), 1.8))
                painter.setBrush(QBrush(QColor(0, 255, 102, 35)))
                painter.drawRect(QRectF(strip_x0, cy - r_px, strip_w, 2 * r_px))

        # -------------------------------------------------------------
        # D. Project Vector Artwork onto Curved 3D Cylinder Surface
        # -------------------------------------------------------------
        def _project_pt(axial_mm: float, rotary_mm: float) -> Tuple[float, float, bool]:
            """Projects 2D workpiece coordinates (axial, rotary) onto screen (x, y, is_front)."""
            alpha = (rotary_mm / circ) * 2.0 * math.pi
            beta = (alpha - roll_rad) % (2.0 * math.pi)

            u_centered = (axial_mm - (axial_len_mm / 2.0)) * self.zoom
            y_loc = -r_px * math.cos(beta)
            z_loc = r_px * math.sin(beta)

            px = cx + u_centered * math.cos(pitch_rad) - z_loc * math.sin(pitch_rad) * 0.35
            py = cy + y_loc * math.cos(pitch_rad) + u_centered * math.sin(pitch_rad) * 0.25

            is_front = (math.sin(beta) >= -0.05)
            return px, py, is_front

        # 1. Backside Vectors (X-Ray Mode)
        if self.xray_mode:
            pen_xray = QPen(QColor(0, 210, 255, 80), 1.0, Qt.DotLine)
            painter.setPen(pen_xray)
            painter.setBrush(Qt.NoBrush)

            for poly in self.raw_paths:
                if len(poly) < 2:
                    continue
                prev_proj = None
                for pt in poly:
                    u_coord = pt[0] if is_y else pt[1]
                    v_coord = pt[1] if is_y else pt[0]
                    proj_x, proj_y, is_front = _project_pt(u_coord, v_coord)
                    if not is_front and prev_proj and not prev_proj[2]:
                        painter.drawLine(int(prev_proj[0]), int(prev_proj[1]), int(proj_x), int(proj_y))
                    prev_proj = (proj_x, proj_y, is_front)

        # 2. Frontside Vectors (Crisp & Vibrant)
        front_color = QColor("#ffffff") if self.material_theme != 'Anodized Black' else QColor("#00e5ff")
        pen_front = QPen(front_color, 1.6)
        painter.setPen(pen_front)
        painter.setBrush(Qt.NoBrush)

        for poly in self.raw_paths:
            if len(poly) < 2:
                continue
            prev_proj = None
            for pt in poly:
                u_coord = pt[0] if is_y else pt[1]
                v_coord = pt[1] if is_y else pt[0]
                proj_x, proj_y, is_front = _project_pt(u_coord, v_coord)
                if is_front and prev_proj and prev_proj[2]:
                    painter.drawLine(int(prev_proj[0]), int(prev_proj[1]), int(proj_x), int(proj_y))
                prev_proj = (proj_x, proj_y, is_front)

        # Reference Contour Borders on 3D Cylinder (visible when contour marking is disabled)
        p_page = self.parent_page()
        if p_page and hasattr(p_page, 'chk_hatch_enable') and hasattr(p_page, 'chk_hatch_mark_contour'):
            show_ref = getattr(p_page, 'chk_hatch_preview_reference_contour', None)
            should_show_ref = (show_ref.isChecked() if show_ref else True)
            if p_page.chk_hatch_enable.isChecked() and not p_page.chk_hatch_mark_contour.isChecked() and should_show_ref:
                ref_paths = getattr(p_page, 'preview_contour_paths', [])
                if ref_paths:
                    pen_ref = QPen(QColor(0, 220, 255, 175), 1.2, Qt.DashLine)
                    painter.setPen(pen_ref)
                    for poly in ref_paths:
                        if len(poly) < 2:
                            continue
                        prev_proj = None
                        for pt in poly:
                            u_coord = pt[0] if is_y else pt[1]
                            v_coord = pt[1] if is_y else pt[0]
                            proj_x, proj_y, is_front = _project_pt(u_coord, v_coord)
                            if is_front and prev_proj and prev_proj[2]:
                                painter.drawLine(int(prev_proj[0]), int(prev_proj[1]), int(proj_x), int(proj_y))
                            prev_proj = (proj_x, proj_y, is_front)

        # -------------------------------------------------------------
        # E. Laser Focus Apex Line & Soft Red Diode Fan Beam
        # -------------------------------------------------------------
        apex_y = cy - (r_px * math.cos(pitch_rad))
        fan_top_y = max(15.0, apex_y - 65.0)
        fan_poly = QPolygonF([
            QPointF(cx, fan_top_y),
            QPointF(x_left + 10, apex_y),
            QPointF(x_right - 10, apex_y)
        ])
        grad_beam = QLinearGradient(cx, fan_top_y, cx, apex_y)
        grad_beam.setColorAt(0.0, QColor(255, 0, 60, 140))
        grad_beam.setColorAt(0.6, QColor(255, 30, 80, 50))
        grad_beam.setColorAt(1.0, QColor(255, 0, 0, 10))
        painter.setPen(Qt.NoPen)
        painter.setBrush(grad_beam)
        painter.drawPolygon(fan_poly)

        painter.setPen(QPen(QColor("#ff1a4b"), 2.2, Qt.SolidLine))
        painter.drawLine(int(x_left - 15), int(apex_y), int(x_right + 15), int(apex_y))

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor("#ff3366"))
        painter.drawText(int(cx - 65), int(apex_y - 8), "LASER APEX (TDC 0°)")

        painter.restore()

    def _render_hud(self, painter: QPainter):
        """Renders heads-up telemetry overlay."""
        painter.save()
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(200, 220, 240, 210))

        mode_str = "2D Unwrapped" if self.view_mode == 'unwrapped_2d' else "3D Interactive Orbit"
        rot_str = f"Chuck: {self.sim_cylinder_angle_deg:.1f}° | Pitch: {self.pitch_deg:.1f}°" if self.view_mode == 'cylinder_3d' else ""
        slices_str = f"Slices: {len(self.slices)}"
        dim_str = f"Ø {self.config.diameter:.2f} mm | C {self.config.circumference:.2f} mm"

        hud_text = f"[{mode_str}]  {rot_str}  |  {dim_str}  |  {slices_str}"
        painter.drawText(15, self.height() - 15, hud_text)

        if self.view_mode == 'cylinder_3d':
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor(130, 150, 180, 180))
            painter.drawText(15, self.height() - 32, "Drag Left Mouse: Orbit (Roll + Pitch) | Wheel: Zoom | Middle Mouse: Pan")

        painter.restore()


# =============================================================================
# 2. ROTARY HARDWARE EXECUTION THREAD
# =============================================================================

class RotaryExecutionThread(QThread):
    """Non-blocking hardware execution thread for galvo & stepper."""
    sliceStarted = Signal(int, int)
    sliceCompleted = Signal(int, int)
    progressUpdated = Signal(float)
    logMessage = Signal(str)
    jobFinished = Signal(bool, str)

    def __init__(
        self,
        slices: List[RotarySlice],
        config: RotaryConfig,
        galvo_controller=None,
        stepper_controller=None,
        galvo_config=None,
        is_redlight: bool = False,
        loop_framing: bool = False,
        continuous: bool = False,
        laser_power: float = 80.0,
        laser_freq: float = 30.0,
        mark_speed: float = 500.0,
        jump_speed: float = 2000.0,
        parent=None
    ):
        super().__init__(parent)
        self.slices = slices
        self.config = config
        self.galvo_controller = galvo_controller
        self.stepper_controller = stepper_controller
        self.galvo_config = galvo_config
        self.is_redlight = is_redlight
        self.loop_framing = loop_framing
        self.continuous = continuous
        self.laser_power = laser_power
        self.laser_freq = laser_freq
        self.mark_speed = mark_speed
        self.jump_speed = jump_speed

        self._is_running = True
        self._is_paused = False

    def stop(self):
        self._is_running = False
        self._is_paused = False

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def is_paused(self) -> bool:
        return self._is_paused

    def run(self):
        if not self.slices:
            self.jobFinished.emit(False, "No slices to execute.")
            return

        total_slices = len(self.slices)
        action_name = "Red-Light Framing" if self.is_redlight else "Laser Marking"
        self.logMessage.emit(f"=== Starting Rotary {action_name} ({total_slices} slices) ===")

        if not self.is_redlight and self.galvo_controller:
            self.galvo_controller.live_power = self.laser_power
            self.galvo_controller.live_freq = self.laser_freq

        if self.is_redlight:
            self._set_red_pointer(True)

        total_pulses_stepped = 0
        start_time = time.time()

        try:
            while self._is_running:
                for idx, sl in enumerate(self.slices):
                    if not self._is_running:
                        self.logMessage.emit("Job Aborted by Operator.")
                        break

                    while self._is_paused and self._is_running:
                        time.sleep(0.05)

                    self.sliceStarted.emit(idx, total_slices)
                    self.progressUpdated.emit((idx / total_slices) * 100.0)

                    self._ensure_laser_off()

                    pulses_to_step = sl.step_pulses
                    if getattr(self.config, 'ring_inside', False):
                        pulses_to_step = -pulses_to_step

                    if pulses_to_step != 0:
                        self.logMessage.emit(f"Slice #{idx+1}: Advancing Rotary by {pulses_to_step} pulses ({sl.delta_distance_mm:.3f} mm)...")
                        self._execute_stepper_move(pulses_to_step)
                        total_pulses_stepped += pulses_to_step

                        settle_s = self.config.settling_delay_ms / 1000.0
                        if settle_s > 0:
                            time.sleep(settle_s)

                    if not self._is_running:
                        break

                    if sl.paths:
                        self.logMessage.emit(f"Slice #{idx+1}: Executing Galvo Scan ({len(sl.paths)} vectors, {sl.total_path_length_mm:.1f} mm at TDC)...")
                        self._execute_galvo_slice(sl)

                    self.sliceCompleted.emit(idx, total_slices)

                # Completing 360 wrap final step if applicable
                is_wrap = getattr(self.slices[0], 'is_wrap_360', False) if self.slices else False
                completion_pulses = getattr(self.slices[-1], 'completion_pulses', 0) if self.slices else 0

                if is_wrap and completion_pulses != 0 and self._is_running:
                    if getattr(self.config, 'ring_inside', False):
                        completion_pulses = -completion_pulses
                    self.logMessage.emit(f"Finalizing 360° Wrap: Advancing {completion_pulses} pulses (Exact 360.0° chuck revolution)...")
                    self._execute_stepper_move(completion_pulses)
                    total_pulses_stepped += completion_pulses

                if self.is_redlight and self.loop_framing and self._is_running:
                    if total_pulses_stepped != 0:
                        if not is_wrap:
                            self.logMessage.emit("Framing Loop: Returning to initial index...")
                            self._execute_stepper_move(-total_pulses_stepped)
                        total_pulses_stepped = 0
                        time.sleep(0.1)
                    continue
                elif self.continuous and not self.is_redlight and self._is_running:
                    if total_pulses_stepped != 0:
                        if not is_wrap:
                            self._execute_stepper_move(-total_pulses_stepped)
                        total_pulses_stepped = 0
                        time.sleep(0.2)
                    continue
                else:
                    break

            if is_wrap:
                self.logMessage.emit(f"Full 360° Revolution Completed ({total_pulses_stepped} pulses). Chuck aligned at 0° origin.")
            elif self.config.return_to_zero and total_pulses_stepped != 0 and self._is_running:
                self.logMessage.emit(f"Returning Rotary Chuck to Origin ({-total_pulses_stepped} pulses)...")
                self._execute_stepper_move(-total_pulses_stepped)
                settle_s = self.config.settling_delay_ms / 1000.0
                if settle_s > 0:
                    time.sleep(settle_s)

            elapsed = time.time() - start_time
            self.progressUpdated.emit(100.0)
            self.logMessage.emit(f"=== Rotary Job Completed in {elapsed:.1f}s ===")
            self.jobFinished.emit(True, f"Completed {total_slices} slices in {elapsed:.1f}s")

        except Exception as e:
            self.logMessage.emit(f"Execution Error: {e}")
            self.jobFinished.emit(False, str(e))
        finally:
            self._ensure_laser_off()
            if self.is_redlight:
                self._set_red_pointer(False)

    def _ensure_laser_off(self):
        if self.galvo_controller and hasattr(self.galvo_controller, 'connection') and self.galvo_controller.connection:
            conn = self.galvo_controller.connection
            if hasattr(conn, 'laser_off'):
                try:
                    conn.laser_off()
                except Exception:
                    pass

    def _set_red_pointer(self, state: bool):
        if self.galvo_controller and hasattr(self.galvo_controller, 'connection') and self.galvo_controller.connection:
            conn = self.galvo_controller.connection
            try:
                if state:
                    if hasattr(conn, 'reddot_on'):
                        conn.reddot_on()
                else:
                    if hasattr(conn, 'reddot_off'):
                        conn.reddot_off()
            except Exception:
                pass

    def _execute_stepper_move(self, pulses: int):
        if pulses == 0:
            return
        speed = max(100, int(self.config.max_speed))
        axis = str(self.config.stepper_axis or 'Z').upper()
        t_travel = (abs(pulses) / speed) + (self.config.accel_time_ms / 1000.0)

        if self.stepper_controller:
            if hasattr(self.stepper_controller, 'move_axis_pulses'):
                self.stepper_controller.move_axis_pulses(axis, pulses, speed)
                return
            elif hasattr(self.stepper_controller, 'connection') and self.stepper_controller.connection:
                conn = self.stepper_controller.connection
                if hasattr(conn, 'axis_move'):
                    conn.axis_move(axis, pulses, speed, is_relative=True)
                    if hasattr(conn, 'wait_for_axis_motion'):
                        conn.wait_for_axis_motion(axis, timeout=t_travel + 1.0)
                    else:
                        time.sleep(t_travel)
                    return

        time.sleep(min(0.25, t_travel))

    def _execute_galvo_slice(self, sl: RotarySlice):
        if not sl.paths:
            return

        field_size = getattr(self.galvo_config, 'field_size', 110.0) or 110.0
        galvo_units_per_mm = 65535.0 / max(1.0, field_size)

        mark_spd_units = int(self.mark_speed * galvo_units_per_mm)
        jump_spd_units = int(self.jump_speed * galvo_units_per_mm)

        send_queue = []
        for poly in sl.paths:
            if not poly or len(poly) < 1:
                continue

            p0 = poly[0]
            gx0, gy0 = self._to_galvo_coords(p0[0], p0[1])
            send_queue.append({'type': 'jump', 'x': gx0, 'y': gy0, 'speed': jump_spd_units})

            if not self.is_redlight:
                send_queue.append({'type': 'laser_on'})

            for pt in poly[1:]:
                gx, gy = self._to_galvo_coords(pt[0], pt[1])
                send_queue.append({'type': 'mark', 'x': gx, 'y': gy, 'speed': mark_spd_units})

            if not self.is_redlight:
                send_queue.append({'type': 'laser_off'})

        if self.galvo_controller and hasattr(self.galvo_controller, 'execute_queue') and send_queue:
            self.galvo_controller.execute_queue(
                send_queue, 
                loop_count=1,
                abort_check=lambda: not self._is_running
            )
        else:
            time.sleep(min(0.3, max(0.02, sl.total_path_length_mm / max(10.0, self.mark_speed))))

    def _to_galvo_coords(self, x_mm: float, y_mm: float) -> Tuple[int, int]:
        if self.galvo_config and hasattr(self.galvo_config, 'apply_transform'):
            return self.galvo_config.apply_transform(x_mm, y_mm)
        
        field_size = 110.0
        gx = int(32767 + (x_mm / (field_size / 2.0)) * 32767)
        gy = int(32767 + (y_mm / (field_size / 2.0)) * 32767)
        return max(0, min(65535, gx)), max(0, min(65535, gy))


# =============================================================================
# =============================================================================
# 3. INTERACTIVE 360° ROTARY CALIBRATION WIZARD (EZCAD STYLE)
# =============================================================================

class Calibrate360Wizard(QDialog):
    """
    EZCad-Style Interactive 360° Rotary Axis Calibration Wizard.
    Calibrates exact stepper pulses & gear ratio by:
    1. Distance / Circumference (mm) - e.g. Commanded 255mm but rotated 323mm (+68mm)
    2. Number of full turns (e.g. 13 turns, 1.27 turns, 1 turn)
    3. Degrees (e.g. 456°, 4680°, 360°)
    """
    def __init__(self, parent_page: 'RotaryMarkingPage'):
        super().__init__(parent_page)
        self.page = parent_page
        self.calculated_pulses = 395
        self.calculated_gear = 0.7895
        self.setWindowTitle("⚙ 360° Rotary Axis Calibration Wizard")
        self.setMinimumWidth(600)
        self.setStyleSheet("""
            QDialog { background-color: #1a1e28; color: #e0e8f0; font-family: 'Segoe UI', sans-serif; }
            QGroupBox { border: 1px solid #2e3a4e; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #00d2ff; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLabel { color: #c0d0e0; }
            QPushButton { background-color: #243044; color: #ffffff; border: 1px solid #3d4f6c; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #31425e; border-color: #00d2ff; }
            QPushButton#btn_apply { background-color: #007a52; color: #ffffff; border: none; font-size: 10pt; }
            QPushButton#btn_apply:hover { background-color: #009966; }
            QPushButton#btn_test { background-color: #7a4b00; color: #ffcc00; border: none; font-size: 9pt; }
            QPushButton#btn_test:hover { background-color: #995e00; }
            QDoubleSpinBox, QSpinBox { background-color: #131720; color: #00ffff; border: 1px solid #2e3a4e; border-radius: 4px; padding: 4px; font-weight: bold; }
            QRadioButton { color: #d0e0f0; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header Info
        lbl_head = QLabel("Interactive 360° Chuck Rotation Calibration")
        lbl_head.setStyleSheet("font-size: 13pt; font-weight: bold; color: #00ffff;")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel(
            "Calibrate exact stepper pulses so that 360° rotation matches your cylinder circumference perfectly.\n"
            "Solves circumference over-rotation (e.g. commanded 255mm but rotated 323mm, 68mm more)."
        )
        lbl_desc.setStyleSheet("color: #8da2be; font-size: 9pt;")
        layout.addWidget(lbl_desc)

        # Step 1: Current Setting & Test Spin
        grp1 = QGroupBox("Step 1: Test Current 360° Pulse Setting")
        lay1 = QVBoxLayout(grp1)
        self.lbl_curr_info = QLabel()
        lay1.addWidget(self.lbl_curr_info)

        btn_test_current = QPushButton("▶ Test-Spin Chuck (Current 360° Pulses)")
        btn_test_current.setObjectName("btn_test")
        btn_test_current.clicked.connect(self._spin_current)
        lay1.addWidget(btn_test_current)
        layout.addWidget(grp1)

        # Step 2: Calibration Method & Observed Rotation
        grp2 = QGroupBox("Step 2: Enter Observed Rotation Measurement")
        lay2 = QVBoxLayout(grp2)

        lay_radios = QHBoxLayout()
        self.rb_dist = QRadioButton("Surface Distance / Circumference (mm)")
        self.rb_dist.setChecked(True)
        self.rb_turns = QRadioButton("Full Turns / Revolutions")
        self.rb_degs = QRadioButton("Angle in Degrees (°)")
        lay_radios.addWidget(self.rb_dist)
        lay_radios.addWidget(self.rb_turns)
        lay_radios.addWidget(self.rb_degs)
        lay2.addLayout(lay_radios)

        # Mode A: Circumference & Distance Inputs
        self.frame_dist = QFrame()
        lay_fd = QGridLayout(self.frame_dist)
        lay_fd.setContentsMargins(0, 4, 0, 4)

        lay_fd.addWidget(QLabel("Commanded / Expected Circumference:"), 0, 0)
        self.spn_target_c = QDoubleSpinBox()
        self.spn_target_c.setRange(1.0, 5000.0)
        self.spn_target_c.setDecimals(2)
        curr_c = self.page.config.circumference
        self.spn_target_c.setValue(255.0 if abs(curr_c - 78.54) < 1.0 else curr_c)
        self.spn_target_c.setSuffix(" mm")
        lay_fd.addWidget(self.spn_target_c, 0, 1)

        lay_fd.addWidget(QLabel("Actual Measured Surface Distance:"), 1, 0)
        self.spn_actual_dist = QDoubleSpinBox()
        self.spn_actual_dist.setRange(1.0, 50000.0)
        self.spn_actual_dist.setDecimals(2)
        self.spn_actual_dist.setValue(323.0) # User's exact physical observation
        self.spn_actual_dist.setSuffix(" mm")
        lay_fd.addWidget(self.spn_actual_dist, 1, 1)

        self.lbl_dist_error = QLabel("Over-rotation Error: +68.00 mm (+26.7%)")
        self.lbl_dist_error.setStyleSheet("color: #ffaa00; font-weight: bold;")
        lay_fd.addWidget(self.lbl_dist_error, 2, 0, 1, 2)
        lay2.addWidget(self.frame_dist)

        # Mode B: Turns & Degrees Single Input
        self.frame_single = QFrame()
        lay_fs = QHBoxLayout(self.frame_single)
        lay_fs.setContentsMargins(0, 4, 0, 4)
        self.lbl_input_prompt = QLabel("Observed Value:")
        self.spn_input_val = QDoubleSpinBox()
        self.spn_input_val.setRange(0.01, 72000.0)
        self.spn_input_val.setDecimals(2)
        self.spn_input_val.setValue(1.27)
        lay_fs.addWidget(self.lbl_input_prompt)
        lay_fs.addWidget(self.spn_input_val)
        self.frame_single.setVisible(False)
        lay2.addWidget(self.frame_single)

        # Quick Preset Buttons
        lay_presets = QHBoxLayout()
        btn_preset_255 = QPushButton("255mm → 323mm (+68mm)")
        btn_preset_255.setToolTip("Fix 68mm over-rotation on 255mm circumference (323mm actual)")
        btn_preset_255.setStyleSheet("background-color: #3b2d18; color: #ffcc00; font-weight: bold;")
        btn_preset_255.clicked.connect(self._set_preset_255_323)

        btn_13 = QPushButton("13 Turns (492 p)")
        btn_13.clicked.connect(lambda: self._set_turns(13.0))

        btn_12_8 = QPushButton("12.8 Turns (500 p)")
        btn_12_8.clicked.connect(lambda: self._set_turns(12.8))

        btn_1 = QPushButton("Exact 1 Turn (0mm error)")
        btn_1.clicked.connect(self._set_exact_1_turn)

        btn_close_3mm = QPushButton("Close 3mm Gap (→ 400 p)")
        btn_close_3mm.setToolTip("Compensate 3mm gap: sets 400 pulses/rev (200-step motor at 2x microstep)")
        btn_close_3mm.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;")
        btn_close_3mm.clicked.connect(self._set_close_3mm_gap)

        lay_presets.addWidget(btn_close_3mm)
        lay_presets.addWidget(btn_preset_255)
        lay_presets.addWidget(btn_13)
        lay_presets.addWidget(btn_12_8)
        lay_presets.addWidget(btn_1)
        lay2.addLayout(lay_presets)
        layout.addWidget(grp2)

        # Step 3: Result & Verification
        grp3 = QGroupBox("Step 3: Calibrated 360° Output")
        lay3 = QVBoxLayout(grp3)
        self.lbl_result = QLabel()
        self.lbl_result.setStyleSheet("font-size: 9pt; font-family: Consolas; color: #00ffcc;")
        lay3.addWidget(self.lbl_result)

        lay_choice = QHBoxLayout()
        self.rb_apply_pulses = QRadioButton("Apply as Pulses/Rev (395 pulses, Gear = 1.000)")
        self.rb_apply_pulses.setChecked(True)
        self.rb_apply_gear = QRadioButton("Apply as Gear Ratio (0.7895, Pulses/Rev = 500)")
        lay_choice.addWidget(self.rb_apply_pulses)
        lay_choice.addWidget(self.rb_apply_gear)
        lay3.addLayout(lay_choice)

        btn_verify = QPushButton("▶ Test 360° with New Calibration (Verify Exact Distance)")
        btn_verify.setObjectName("btn_test")
        btn_verify.clicked.connect(self._test_new_pulses)
        lay3.addWidget(btn_verify)
        layout.addWidget(grp3)

        # Action Buttons
        lay_actions = QHBoxLayout()
        btn_apply = QPushButton("✓ Apply & Save Calibration")
        btn_apply.setObjectName("btn_apply")
        btn_apply.clicked.connect(self._apply_calibration)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        lay_actions.addWidget(btn_apply)
        lay_actions.addWidget(btn_cancel)
        layout.addLayout(lay_actions)

        # Signal connections
        self.rb_dist.toggled.connect(self._on_mode_changed)
        self.rb_turns.toggled.connect(self._on_mode_changed)
        self.rb_degs.toggled.connect(self._on_mode_changed)
        self.spn_target_c.valueChanged.connect(self._recalculate)
        self.spn_actual_dist.valueChanged.connect(self._recalculate)
        self.spn_input_val.valueChanged.connect(self._recalculate)
        self.rb_apply_pulses.toggled.connect(self._recalculate)
        self.rb_apply_gear.toggled.connect(self._recalculate)

        self._refresh_current_info()
        self._recalculate()

    def _refresh_current_info(self):
        p360 = int(round(self.page.config.total_pulses_360))
        gear = self.page.spn_gear_ratio.value()
        p_rev = self.page.spn_pulses_rev.value()
        self.lbl_curr_info.setText(
            f"Current Hardware Setting: <b>{p360:,} pulses</b> per 360° revolution "
            f"(Pulses/Rev: {p_rev:,}, Gear Ratio: {gear:.4f})."
        )

    def _spin_current(self):
        self.page.test_full_revolution()

    def _set_close_3mm_gap(self):
        self.rb_dist.setChecked(True)
        c = self.spn_target_c.value()
        self.spn_actual_dist.setValue(max(1.0, c - 3.0)) # 3mm short of full turn
        self.rb_apply_pulses.setChecked(True)
        self._recalculate()

    def _set_preset_255_323(self):
        self.rb_dist.setChecked(True)
        self.spn_target_c.setValue(255.0)
        self.spn_actual_dist.setValue(323.0)
        self._recalculate()

    def _set_exact_1_turn(self):
        self.rb_dist.setChecked(True)
        c = self.spn_target_c.value()
        self.spn_actual_dist.setValue(c)
        self._recalculate()

    def _set_turns(self, turns: float):
        self.rb_turns.setChecked(True)
        self.spn_input_val.setValue(turns)
        self._recalculate()

    def _on_mode_changed(self):
        if self.rb_dist.isChecked():
            self.frame_dist.setVisible(True)
            self.frame_single.setVisible(False)
        elif self.rb_turns.isChecked():
            self.frame_dist.setVisible(False)
            self.frame_single.setVisible(True)
            self.lbl_input_prompt.setText("Observed Turns:")
            self.spn_input_val.setSuffix(" turns")
            self.spn_input_val.setRange(0.01, 200.0)
            self.spn_input_val.setValue(1.27)
        else:
            self.frame_dist.setVisible(False)
            self.frame_single.setVisible(True)
            self.lbl_input_prompt.setText("Observed Angle:")
            self.spn_input_val.setSuffix("°")
            self.spn_input_val.setRange(1.0, 72000.0)
            self.spn_input_val.setValue(456.0)
        self._recalculate()

    def _recalculate(self):
        old_p360 = self.page.config.total_pulses_360
        if self.rb_dist.isChecked():
            target_c = max(0.1, self.spn_target_c.value())
            actual_d = max(0.1, self.spn_actual_dist.value())
            err = actual_d - target_c
            err_pct = (err / target_c) * 100.0
            sign_str = "+" if err >= 0 else ""
            self.lbl_dist_error.setText(f"Rotation Error: {sign_str}{err:.2f} mm ({sign_str}{err_pct:.1f}%)")
            self.lbl_dist_error.setStyleSheet("color: #ffaa00; font-weight: bold;" if abs(err) > 0.05 else "color: #00ffcc; font-weight: bold;")
            
            # Scale factor: ratio of commanded to actual
            ratio = target_c / actual_d
            new_p360 = old_p360 * ratio
            turns = actual_d / target_c
            actual_deg = turns * 360.0
        elif self.rb_turns.isChecked():
            turns = max(0.01, self.spn_input_val.value())
            actual_deg = turns * 360.0
            ratio = 1.0 / turns
            new_p360 = old_p360 * ratio
        else:
            actual_deg = max(0.1, self.spn_input_val.value())
            turns = actual_deg / 360.0
            ratio = 360.0 / actual_deg
            new_p360 = old_p360 * ratio

        p_exact = max(1, int(round(new_p360)))
        gear_corr = round(self.page.spn_gear_ratio.value() * ratio, 4)

        self.rb_apply_pulses.setText(f"Apply as Pulses/Rev: {p_exact} pulses (Gear Ratio = 1.0000)")
        self.rb_apply_gear.setText(f"Apply as Gear Ratio: {gear_corr:.4f} (Pulses/Rev = {self.page.spn_pulses_rev.value()})")

        if self.rb_apply_gear.isChecked():
            self.calculated_pulses = int(round(self.page.spn_pulses_rev.value() * gear_corr))
            self.calculated_gear = gear_corr
        else:
            self.calculated_pulses = p_exact
            self.calculated_gear = 1.0000

        self.lbl_result.setText(
            f"Observed: {actual_deg:.1f}° ({turns:.3f} turns, Scale Factor: {ratio:.4f})\n"
            f"-> Corrected 360° Pulses: {self.calculated_pulses:,} pulses (Ratio: {self.calculated_gear:.4f})\n"
            f"Click 'Test 360° with New Calibration' to test-spin chuck."
        )

    def _test_new_pulses(self):
        pulses = self.calculated_pulses
        if self.page.config.reverse_direction:
            pulses = -pulses
        speed = max(100, int(self.page.config.max_speed))
        axis = str(self.page.config.stepper_axis or 'Z').upper()
        self.page.lbl_console_log.setText(f"Testing new calibration: {pulses} pulses (Exact 360.0°)...")
        if self.page.stepper_controller and hasattr(self.page.stepper_controller, 'move_axis_pulses'):
            self.page.stepper_controller.move_axis_pulses(axis, pulses, speed)

    def _apply_calibration(self):
        if self.rb_apply_gear.isChecked():
            self.page.spn_gear_ratio.setValue(self.calculated_gear)
        else:
            self.page.spn_pulses_rev.setValue(self.calculated_pulses)
            self.page.spn_gear_ratio.setValue(1.0000)

        # If user was in distance mode, sync workpiece diameter & circumference
        if self.rb_dist.isChecked():
            target_c = self.spn_target_c.value()
            target_d = target_c / 3.141592653589793
            self.page.spn_diameter.setValue(round(target_d, 2))

        self.page._on_dimensions_changed()
        self.page.save_rotary_settings()
        total_p = int(round(self.page.config.total_pulses_360))
        QMessageBox.information(
            self, "Calibration Saved",
            f"360° Rotary Calibration Applied & Saved!\n\n"
            f"• 360° Pulses: {total_p:,} pulses\n"
            f"• Pulses/Rev: {self.page.spn_pulses_rev.value():,}\n"
            f"• Gear Ratio: {self.page.spn_gear_ratio.value():.4f}\n"
            f"• Circumference: {self.page.config.circumference:.2f} mm\n\n"
            f"360° rotation will now move exactly {self.page.config.circumference:.2f} mm!"
        )
        self.accept()

# =============================================================================
# 4. PRODUCTION-GRADE PYSIDE6 ROTARY MARKING PAGE WIDGET
# =============================================================================

# =============================================================================

class RotaryMarkingPage(QWidget):
    """
    Dedicated EZCad2 RotaryMark, SplitMark2, and MarkDemo industrial UI page.
    Includes live diameter synchronization across all generators, slicing, and 3D preview.
    """

    def __init__(self, parent=None, galvo_controller=None, stepper_controller=None, galvo_config=None):
        super().__init__(parent)
        self.main_window = parent
        self.galvo_controller = galvo_controller
        self.stepper_controller = stepper_controller
        self.galvo_config = galvo_config or getattr(parent, 'galvo_config', None) or CoordinateConfig()

        self.slicing_engine = RotarySlicingEngine()
        self.config = RotaryConfig()

        # Artwork source (original) & transformed paths
        self.source_paths: List[List[Tuple[float, float]]] = []
        self.raw_paths: List[List[Tuple[float, float]]] = []
        self.preview_contour_paths: List[List[Tuple[float, float]]] = []
        self.slices: List[RotarySlice] = []
        self.exec_thread: Optional[RotaryExecutionThread] = None
        self.mirror_x: bool = False
        self.mirror_y: bool = False

        # Tracks which feature generated current active artwork: 'preset', 'direct_text', 'scale_ruler', 'cad_vector'
        self.active_generator: str = 'preset'

        self.current_rotary_angle_deg: float = 0.0
        self.current_axial_x_mm: float = 0.0

        # Part and Timer Counters (EZCad RingMark / MarkDemo)
        self.part_count: int = 0
        self.total_count: int = 0
        self.time_part_sec: float = 0.0
        self.time_total_sec: float = 0.0
        self.job_timer = QTimer(self)
        self.job_timer.setInterval(1000)
        self.job_timer.timeout.connect(self._on_timer_second)

        # Typing debounce timer for live text input
        self.typing_timer = QTimer(self)
        self.typing_timer.setSingleShot(True)
        self.typing_timer.setInterval(180)
        self.typing_timer.timeout.connect(lambda: self.on_generate_direct_text(append=False, auto_triggered=True))

        self._init_ui()
        self._apply_dark_industrial_style()
        self._connect_signals()

        # Load initial demo ruler
        self.load_preset_pattern("Cylindrical Ruler (360°)")
        self.load_rotary_settings()

    def get_config_path(self) -> str:
        return os.path.join(_current_dir, "config", "config.ini")

    def load_rotary_settings(self):
        """Loads persistent rotary calibration and workpiece settings from config.ini."""
        import configparser
        path = self.get_config_path()
        if not os.path.exists(path):
            return
        try:
            cfg = configparser.ConfigParser()
            cfg.read(path, encoding='utf-8')
            if cfg.has_section("rotary"):
                sec = cfg["rotary"]
                if "diameter" in sec:
                    self.spn_diameter.setValue(float(sec["diameter"]))
                if "workpiece_height" in sec:
                    self.spn_workpiece_height.setValue(float(sec["workpiece_height"]))
                if "pulses_per_rev" in sec:
                    self.spn_pulses_rev.setValue(int(sec["pulses_per_rev"]))
                if "gear_ratio" in sec:
                    self.spn_gear_ratio.setValue(float(sec["gear_ratio"]))
                if "max_speed" in sec:
                    self.spn_max_speed.setValue(int(sec["max_speed"]))
                if "accel_time_ms" in sec:
                    self.spn_accel_time.setValue(int(sec["accel_time_ms"]))
                if "reverse_dir" in sec:
                    self.chk_reverse_dir.setChecked(sec.getboolean("reverse_dir"))
                self._on_dimensions_changed()
        except Exception as e:
            print(f"Error loading rotary settings: {e}")

    def save_rotary_settings(self):
        """Saves current rotary calibration settings to config.ini permanently."""
        import configparser
        path = self.get_config_path()
        try:
            cfg = configparser.ConfigParser()
            if os.path.exists(path):
                cfg.read(path, encoding='utf-8')
            if not cfg.has_section("rotary"):
                cfg.add_section("rotary")
            cfg.set("rotary", "diameter", str(self.spn_diameter.value()))
            cfg.set("rotary", "workpiece_height", str(self.spn_workpiece_height.value()))
            cfg.set("rotary", "pulses_per_rev", str(self.spn_pulses_rev.value()))
            cfg.set("rotary", "gear_ratio", str(self.spn_gear_ratio.value()))
            cfg.set("rotary", "max_speed", str(self.spn_max_speed.value()))
            cfg.set("rotary", "accel_time_ms", str(self.spn_accel_time.value()))
            cfg.set("rotary", "reverse_dir", str(self.chk_reverse_dir.isChecked()))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding='utf-8') as f:
                cfg.write(f)
        except Exception as e:
            print(f"Error saving rotary settings: {e}")

    def _init_ui(self):
        """Builds the complete industrial UI layout with quick workpiece header & 6 tabs."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ---------------------------------------------------------------------
        # LEFT COLUMN: Canvas, Quick Dimensions Header & Telemetry Bar
        # ---------------------------------------------------------------------
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # 1. Top Canvas Navigation Toolbar
        canvas_bar = QHBoxLayout()
        self.lbl_title = QLabel("ROTARY MARK // CYLINDRICAL SPLIT ENGINE")
        self.lbl_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #00d2ff;")
        canvas_bar.addWidget(self.lbl_title)
        canvas_bar.addStretch()

        self.btn_back_cad = QPushButton("◄ Back to CAD (F5)")
        self.btn_back_cad.setStyleSheet("background-color: #242b38; color: #a0b0c5; font-size: 8pt; padding: 4px 8px;")
        canvas_bar.addWidget(self.btn_back_cad)

        self.btn_view_3d = QPushButton("3D Cylinder")
        self.btn_view_3d.setCheckable(True)
        self.btn_view_3d.setChecked(True)

        self.btn_view_2d = QPushButton("2D Unwrapped")
        self.btn_view_2d.setCheckable(True)

        self.view_btn_group = QButtonGroup(self)
        self.view_btn_group.addButton(self.btn_view_3d)
        self.view_btn_group.addButton(self.btn_view_2d)

        self.btn_auto_spin = QPushButton("▶ Auto-Spin")
        self.btn_auto_spin.setToolTip("Auto-rotates cylinder 360° turntable continuously")

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Brushed Steel", "Anodized Black", "Brass / Gold"])
        self.combo_theme.setToolTip("Workpiece material shader")

        self.chk_xray = QCheckBox("X-Ray")
        self.chk_xray.setChecked(True)
        self.chk_xray.setToolTip("Shows ghosted backside vectors through cylinder")

        self.btn_reset_view = QPushButton("Reset View")

        # Dynamic Orientation Toggle directly in top canvas bar
        self.btn_canvas_toggle_rot = QPushButton("🔄 Rotate (H ⇄ V)")
        self.btn_canvas_toggle_rot.setStyleSheet("""
            QPushButton {
                background-color: #0d3b66;
                color: #00d2ff;
                font-weight: bold;
                font-size: 8pt;
                padding: 4px 8px;
                border: 1px solid #00d2ff;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1a5276;
                color: #ffffff;
            }
        """)
        self.btn_canvas_toggle_rot.setToolTip("If vertical, rotates to horizontal; if horizontal, rotates to vertical (90° toggle)")

        canvas_bar.addWidget(self.btn_view_3d)
        canvas_bar.addWidget(self.btn_view_2d)
        canvas_bar.addWidget(self.btn_auto_spin)
        canvas_bar.addWidget(self.combo_theme)
        canvas_bar.addWidget(self.chk_xray)
        # 360° Wrap Button in Canvas Bar
        self.btn_canvas_wrap360 = QPushButton("⤢ 360° Wrap")
        self.btn_canvas_wrap360.setStyleSheet("""
            QPushButton {
                background-color: #004d40;
                color: #00ff66;
                font-weight: bold;
                font-size: 8pt;
                padding: 4px 8px;
                border: 1px solid #00ff66;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00695c;
                color: #ffffff;
            }
        """)
        self.btn_canvas_wrap360.setToolTip("Scale artwork/pattern to 100% cover pipe circumference")

        canvas_bar.addWidget(self.btn_reset_view)
        canvas_bar.addWidget(self.btn_canvas_toggle_rot)
        canvas_bar.addWidget(self.btn_canvas_wrap360)
        left_layout.addLayout(canvas_bar)

        # 2. Quick Workpiece Dimensions Bar (EZCad RingMark / MarkDemo Style)
        dim_bar = QFrame()
        dim_bar.setStyleSheet("""
            QFrame {
                background-color: #1a202c;
                border: 1px solid #2d3748;
                border-radius: 5px;
            }
        """)
        lay_dim = QHBoxLayout(dim_bar)
        lay_dim.setContentsMargins(8, 4, 8, 4)
        lay_dim.setSpacing(10)

        lbl_d = QLabel("Part Ø:")
        lbl_d.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 9pt;")
        self.spn_top_diameter = QDoubleSpinBox()
        self.spn_top_diameter.setRange(1.0, 500.0)
        self.spn_top_diameter.setValue(25.0)
        self.spn_top_diameter.setDecimals(2)
        self.spn_top_diameter.setSuffix(" mm")
        self.spn_top_diameter.setToolTip("Change workpiece diameter - all functions, text, scale rulers & slices adapt automatically!")
        self.spn_top_diameter.setStyleSheet("font-weight: bold; color: #00ffff; background: #131720;")

        lbl_h = QLabel("Height / L:")
        lbl_h.setStyleSheet("color: #a0b0c5; font-weight: bold; font-size: 9pt;")
        self.spn_top_height = QDoubleSpinBox()
        self.spn_top_height.setRange(2.0, 600.0)
        self.spn_top_height.setValue(50.0)
        self.spn_top_height.setDecimals(1)
        self.spn_top_height.setSuffix(" mm")
        self.spn_top_height.setToolTip("Workpiece axial length / height (mm)")

        self.lbl_top_c = QLabel("C: 78.54 mm")
        self.lbl_top_c.setStyleSheet("color: #00ffcc; font-weight: bold; font-size: 9pt; font-family: Consolas;")
        self.lbl_top_c.setToolTip("Workpiece Circumference = pi * Diameter")

        self.btn_top_optimal_split = QPushButton("🎯 Auto Split")
        self.btn_top_optimal_split.setToolTip("Calculates optically optimal strip width for this diameter")
        self.btn_top_optimal_split.setStyleSheet("font-size: 8pt; padding: 3px 6px; background-color: #1c334d; color: #00d2ff;")

        self.btn_top_refresh = QPushButton("🔄 Refresh")
        self.btn_top_refresh.setToolTip("Re-slices and refreshes all views and artwork")
        self.btn_top_refresh.setStyleSheet("font-size: 8pt; font-weight: bold; padding: 3px 8px; background-color: #2b394e; color: #ffffff;")

        lay_dim.addWidget(lbl_d)
        lay_dim.addWidget(self.spn_top_diameter)
        lay_dim.addWidget(lbl_h)
        lay_dim.addWidget(self.spn_top_height)
        lay_dim.addWidget(self.lbl_top_c)
        lay_dim.addStretch()
        lay_dim.addWidget(self.btn_top_optimal_split)
        lay_dim.addWidget(self.btn_top_refresh)
        left_layout.addWidget(dim_bar)

        # 3. Interactive Canvas
        self.canvas = RotaryCanvasWidget(self)
        left_layout.addWidget(self.canvas, stretch=4)

        # 4. Execution Progress & Telemetry Bar
        progress_box = QFrame()
        progress_box.setObjectName("progressBox")
        prog_layout = QVBoxLayout(progress_box)
        prog_layout.setContentsMargins(8, 8, 8, 8)
        prog_layout.setSpacing(4)

        prog_top_layout = QHBoxLayout()
        self.lbl_job_status = QLabel("Ready // No active job")
        self.lbl_job_status.setStyleSheet("font-weight: bold; color: #a0b0c5;")
        self.lbl_slice_badge = QLabel("Slices: 0 / 0")
        self.lbl_slice_badge.setStyleSheet("color: #00d2ff; font-weight: bold;")
        prog_top_layout.addWidget(self.lbl_job_status)
        prog_top_layout.addStretch()
        prog_top_layout.addWidget(self.lbl_slice_badge)
        prog_layout.addLayout(prog_top_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        prog_layout.addWidget(self.progress_bar)

        # Part Counters & Timers Row
        counters_layout = QHBoxLayout()
        counters_layout.addWidget(QLabel("Part:"))
        self.spn_part_count = QSpinBox()
        self.spn_part_count.setRange(0, 999999)
        self.spn_part_count.setValue(0)
        self.btn_reset_part = QPushButton("R")
        self.btn_reset_part.setFixedWidth(26)
        self.btn_reset_part.setToolTip("Reset Part Count")
        counters_layout.addWidget(self.spn_part_count)
        counters_layout.addWidget(self.btn_reset_part)

        counters_layout.addSpacing(10)
        counters_layout.addWidget(QLabel("Total:"))
        self.spn_total_count = QSpinBox()
        self.spn_total_count.setRange(0, 999999)
        self.spn_total_count.setValue(0)
        counters_layout.addWidget(self.spn_total_count)

        counters_layout.addSpacing(10)
        counters_layout.addWidget(QLabel("Time Part:"))
        self.lbl_time_part = QLabel("00:00:00")
        self.lbl_time_part.setStyleSheet("color: #00ffcc; font-family: Consolas; font-weight: bold;")
        counters_layout.addWidget(self.lbl_time_part)

        counters_layout.addSpacing(10)
        counters_layout.addWidget(QLabel("Time Total:"))
        self.lbl_time_total = QLabel("00:00:00")
        self.lbl_time_total.setStyleSheet("color: #00ffcc; font-family: Consolas; font-weight: bold;")
        counters_layout.addWidget(self.lbl_time_total)
        counters_layout.addStretch()

        prog_layout.addLayout(counters_layout)

        self.lbl_console_log = QLabel("Engine Initialized. Configure workpiece or type direct text to mark.")
        self.lbl_console_log.setStyleSheet("font-size: 8pt; color: #78889b; font-family: Consolas;")
        prog_layout.addWidget(self.lbl_console_log)

        left_layout.addWidget(progress_box, stretch=0)
        main_layout.addLayout(left_layout, stretch=3)

        # ---------------------------------------------------------------------
        # RIGHT COLUMN: 6-Tab Industrial Control Center
        # ---------------------------------------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setMinimumWidth(430)
        self.tabs.setMaximumWidth(520)

        # Tab 1: ✍ Direct Text
        tab_text = self._build_tab_direct_text()
        self.tabs.addTab(tab_text, "✍ Direct Text")

        # Tab 2: 📏 Scale Ruler
        tab_ruler = self._build_tab_scale_ruler()
        self.tabs.addTab(tab_ruler, "📏 Scale Ruler")

        # Tab 3: ✨ Pipe Patterns & 360° Wraps
        self.tab_patterns = self._build_tab_patterns()
        self.tabs.addTab(self.tab_patterns, "✨ Pipe Patterns")

        # Tab 4: 🎨 Artwork & Transform
        tab_art = self._build_tab_artwork_transform()
        self.tabs.addTab(tab_art, "🎨 Artwork")

        # Tab 4: 🏁 Hatch Fill (EzCad Style Infill)
        self.tab_hatch = self._build_tab_hatch()
        self.tabs.addTab(self.tab_hatch, "🏁 Hatch Fill")

        # Tab 5: ⚙ Rotary Setup & 4-Way Jog Keypad
        tab_rotary = self._build_tab_rotary_setup()
        self.tabs.addTab(tab_rotary, "⚙ Setup & Jog")

        # Tab 5: ✂ Slicing & Kinematics
        tab_slicing = self._build_tab_slicing()
        self.tabs.addTab(tab_slicing, "✂ Slicing")

        # Tab 6: ⚡ Laser & Execution
        tab_exec = self._build_tab_execution()
        self.tabs.addTab(tab_exec, "⚡ Execution")

        main_layout.addWidget(self.tabs, stretch=2)

        # Keyboard Shortcuts
        QShortcut(QKeySequence("F1"), self, self.on_redlight_clicked)
        QShortcut(QKeySequence("F2"), self, self.on_mark_clicked)
        QShortcut(QKeySequence("F3"), self, self.on_stop_clicked)
        QShortcut(QKeySequence("F5"), self, self.on_back_to_cad_clicked)
        QShortcut(QKeySequence("Space"), self, self.on_pause_clicked)

        # Configure all spinboxes across all tabs for glitch-free typing (no tracking lockups, auto select-all)
        for sb in (self.findChildren(QSpinBox) + self.findChildren(QDoubleSpinBox)):
            setup_smart_spinbox(sb)

    # -------------------------------------------------------------------------
    # TAB 1: ✍ Direct Text Generator
    # -------------------------------------------------------------------------
    def _build_tab_direct_text(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_geom = QGroupBox("Target Workpiece Geometry")
        lay_g = QHBoxLayout(grp_geom)
        lay_g.addWidget(QLabel("Diameter (D):"))
        self.spn_text_diameter = QDoubleSpinBox()
        self.spn_text_diameter.setRange(1.0, 500.0)
        self.spn_text_diameter.setValue(25.0)
        self.spn_text_diameter.setDecimals(2)
        self.spn_text_diameter.setSuffix(" mm")
        self.spn_text_diameter.setStyleSheet("font-weight: bold; color: #00ffff; background: #131720;")
        lay_g.addWidget(self.spn_text_diameter)

        self.lbl_text_circ = QLabel("Circumference (C = π×D): 78.54 mm")
        self.lbl_text_circ.setStyleSheet("font-weight: bold; color: #00d2ff; padding-left: 10px;")
        lay_g.addWidget(self.lbl_text_circ)
        layout.addWidget(grp_geom)

        grp_text = QGroupBox("Direct Vector Text Printing")
        lay_t = QGridLayout(grp_text)
        lay_t.setSpacing(6)

        lay_t.addWidget(QLabel("Text String:"), 0, 0)
        self.txt_direct_text = QLineEdit("EZCAD ROTARY PRO")
        self.txt_direct_text.setStyleSheet("font-weight: bold; font-size: 10pt; color: #00d2ff;")
        lay_t.addWidget(self.txt_direct_text, 0, 1, 1, 3)

        lay_t.addWidget(QLabel("Font Family:"), 1, 0)
        self.combo_font_family = QComboBox()
        self.combo_font_family.addItems(["Arial", "Segoe UI", "Consolas", "Times New Roman", "Impact", "Courier New"])
        lay_t.addWidget(self.combo_font_family, 1, 1, 1, 3)

        lay_t.addWidget(QLabel("Font Height:"), 2, 0)
        self.spn_font_size = QDoubleSpinBox()
        self.spn_font_size.setRange(0.5, 60.0)
        self.spn_font_size.setValue(4.0)
        self.spn_font_size.setSuffix(" mm")
        lay_t.addWidget(self.spn_font_size, 2, 1)

        lay_t.addWidget(QLabel("Letter Spacing:"), 2, 2)
        self.spn_letter_spacing = QDoubleSpinBox()
        self.spn_letter_spacing.setRange(-2.0, 15.0)
        self.spn_letter_spacing.setValue(0.5)
        self.spn_letter_spacing.setSuffix(" mm")
        lay_t.addWidget(self.spn_letter_spacing, 2, 3)

        lay_t_style = QHBoxLayout()
        self.chk_font_bold = QCheckBox("Bold")
        self.chk_font_bold.setChecked(True)
        self.chk_font_italic = QCheckBox("Italic")
        lay_t_style.addWidget(self.chk_font_bold)
        lay_t_style.addWidget(self.chk_font_italic)
        lay_t.addLayout(lay_t_style, 3, 1, 1, 2)

        lay_t.addWidget(QLabel("Orientation:"), 4, 0)
        self.combo_text_orientation = QComboBox()
        self.combo_text_orientation.addItems(["Circumferential (Wrap Around)", "Axial (Along Workpiece)"])
        lay_t.addWidget(self.combo_text_orientation, 4, 1, 1, 3)

        lay_t.addWidget(QLabel("Angular Repetition:"), 5, 0)
        self.spn_text_reps = QSpinBox()
        self.spn_text_reps.setRange(1, 36)
        self.spn_text_reps.setValue(1)
        self.spn_text_reps.setSuffix(" times")
        lay_t.addWidget(self.spn_text_reps, 5, 1)

        lay_t.addWidget(QLabel("Start Angle:"), 5, 2)
        self.spn_text_start_angle = QDoubleSpinBox()
        self.spn_text_start_angle.setRange(0.0, 360.0)
        self.spn_text_start_angle.setValue(0.0)
        self.spn_text_start_angle.setSuffix("°")
        lay_t.addWidget(self.spn_text_start_angle, 5, 3)

        self.chk_text_autofit = QCheckBox("Auto-Fit to 360° Circumference")
        self.chk_text_autofit.setChecked(False)
        self.chk_text_autofit.setToolTip("Automatically scales text so it wraps seamlessly around the diameter")
        lay_t.addWidget(self.chk_text_autofit, 6, 0, 1, 4)

        self.chk_text_hatch_quick = QCheckBox("Enable Hatch Infill for Text (EzCad Style)")
        self.chk_text_hatch_quick.setToolTip("Fills text outlines with dense laser scanlines instead of just marking the outer border")
        lay_t.addWidget(self.chk_text_hatch_quick, 7, 0, 1, 4)

        layout.addWidget(grp_text)

        # Quick Actions
        lay_btns = QHBoxLayout()
        self.btn_apply_text = QPushButton("Generate & Set as Artwork")
        self.btn_apply_text.setStyleSheet("background-color: #005a7d; color: #ffffff; font-weight: bold; padding: 7px;")
        self.btn_append_text = QPushButton("+ Append to Artwork")
        lay_btns.addWidget(self.btn_apply_text)
        lay_btns.addWidget(self.btn_append_text)
        layout.addLayout(lay_btns)

        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB 2: 📏 Editable Scale Ruler Generator
    # -------------------------------------------------------------------------
    def _build_tab_scale_ruler(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_r_geom = QGroupBox("Target Workpiece Geometry")
        lay_rg = QHBoxLayout(grp_r_geom)
        lay_rg.addWidget(QLabel("Diameter (D):"))
        self.spn_ruler_diameter = QDoubleSpinBox()
        self.spn_ruler_diameter.setRange(1.0, 500.0)
        self.spn_ruler_diameter.setValue(25.0)
        self.spn_ruler_diameter.setDecimals(2)
        self.spn_ruler_diameter.setSuffix(" mm")
        self.spn_ruler_diameter.setStyleSheet("font-weight: bold; color: #00ffff; background: #131720;")
        lay_rg.addWidget(self.spn_ruler_diameter)

        self.lbl_ruler_circ = QLabel("Circumference (C = π×D): 78.54 mm")
        self.lbl_ruler_circ.setStyleSheet("font-weight: bold; color: #00d2ff; padding-left: 10px;")
        lay_rg.addWidget(self.lbl_ruler_circ)
        layout.addWidget(grp_r_geom)

        grp_ruler = QGroupBox("Scale Ruler & Dial Parameters")
        lay_r = QGridLayout(grp_ruler)
        lay_r.setSpacing(6)

        lay_r.addWidget(QLabel("Ruler Type:"), 0, 0)
        self.combo_ruler_type = QComboBox()
        self.combo_ruler_type.addItems(["Angular Degree Scale (0° - 360°)", "Circumference Metric Scale (0 - C mm)", "Linear Metric Scale (Axial mm)"])
        lay_r.addWidget(self.combo_ruler_type, 0, 1, 1, 2)

        lay_r.addWidget(QLabel("Minor Tick:"), 1, 0)
        self.spn_ruler_minor_step = QDoubleSpinBox()
        self.spn_ruler_minor_step.setRange(0.1, 90.0)
        self.spn_ruler_minor_step.setValue(1.0)
        self.spn_ruler_minor_len = QDoubleSpinBox()
        self.spn_ruler_minor_len.setRange(0.5, 30.0)
        self.spn_ruler_minor_len.setValue(2.5)
        self.spn_ruler_minor_len.setSuffix(" mm")
        lay_r.addWidget(self.spn_ruler_minor_step, 1, 1)
        lay_r.addWidget(self.spn_ruler_minor_len, 1, 2)

        lay_r.addWidget(QLabel("Medium Tick:"), 2, 0)
        self.spn_ruler_medium_step = QDoubleSpinBox()
        self.spn_ruler_medium_step.setRange(0.5, 90.0)
        self.spn_ruler_medium_step.setValue(5.0)
        self.spn_ruler_medium_len = QDoubleSpinBox()
        self.spn_ruler_medium_len.setRange(0.5, 30.0)
        self.spn_ruler_medium_len.setValue(4.5)
        self.spn_ruler_medium_len.setSuffix(" mm")
        lay_r.addWidget(self.spn_ruler_medium_step, 2, 1)
        lay_r.addWidget(self.spn_ruler_medium_len, 2, 2)

        lay_r.addWidget(QLabel("Major Tick:"), 3, 0)
        self.spn_ruler_major_step = QDoubleSpinBox()
        self.spn_ruler_major_step.setRange(1.0, 180.0)
        self.spn_ruler_major_step.setValue(10.0)
        self.spn_ruler_major_len = QDoubleSpinBox()
        self.spn_ruler_major_len.setRange(1.0, 40.0)
        self.spn_ruler_major_len.setValue(7.0)
        self.spn_ruler_major_len.setSuffix(" mm")
        lay_r.addWidget(self.spn_ruler_major_step, 3, 1)
        lay_r.addWidget(self.spn_ruler_major_len, 3, 2)

        lay_r.addWidget(QLabel("Tick Side:"), 4, 0)
        self.combo_ruler_side = QComboBox()
        self.combo_ruler_side.addItems(["Left/Top", "Right/Bottom", "Both Sides"])
        lay_r.addWidget(self.combo_ruler_side, 4, 1, 1, 2)

        self.chk_ruler_baseline = QCheckBox("Include Continuous Baseline")
        self.chk_ruler_baseline.setChecked(True)
        lay_r.addWidget(self.chk_ruler_baseline, 5, 0, 1, 3)

        self.chk_ruler_numbers = QCheckBox("Include Vector Number Labels")
        self.chk_ruler_numbers.setChecked(True)
        lay_r.addWidget(self.chk_ruler_numbers, 6, 0, 1, 3)

        lay_r.addWidget(QLabel("Number Step:"), 7, 0)
        self.spn_ruler_num_step = QDoubleSpinBox()
        self.spn_ruler_num_step.setRange(1.0, 180.0)
        self.spn_ruler_num_step.setValue(10.0)
        lay_r.addWidget(self.spn_ruler_num_step, 7, 1)

        lay_r.addWidget(QLabel("Font Size:"), 7, 2)
        self.spn_ruler_font_sz = QDoubleSpinBox()
        self.spn_ruler_font_sz.setRange(0.8, 15.0)
        self.spn_ruler_font_sz.setValue(2.6)
        self.spn_ruler_font_sz.setSuffix(" mm")
        lay_r.addWidget(self.spn_ruler_font_sz, 7, 3)

        layout.addWidget(grp_ruler)

        # Buttons
        lay_r_btns = QHBoxLayout()
        self.btn_apply_ruler = QPushButton("Generate & Set as Artwork")
        self.btn_apply_ruler.setStyleSheet("background-color: #005a7d; color: #ffffff; font-weight: bold; padding: 7px;")
        self.btn_append_ruler = QPushButton("+ Append Ruler")
        lay_r_btns.addWidget(self.btn_apply_ruler)
        lay_r_btns.addWidget(self.btn_append_ruler)
        layout.addLayout(lay_r_btns)

        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB 3: 🎨 Artwork & Transform
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # TAB: ✨ PROCEDURAL PIPE PATTERNS & 360° WRAP GENERATOR
    # -------------------------------------------------------------------------
    def _build_tab_patterns(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 1. Pattern Design Selection Group
        grp_pattern = QGroupBox("Procedural Pipe Patterns & Design Textures")
        lay_pat = QGridLayout(grp_pattern)
        lay_pat.setSpacing(6)

        lay_pat.addWidget(QLabel("Pattern Design:"), 0, 0)
        self.combo_pipe_pattern = QComboBox()
        self.combo_pipe_pattern.addItems([
            "🏁 Checkerboard / Chess Tile Grid (Odd/Even Hatchable)",
            "💎 Diamond Knurl / Facets (Odd/Even Hatchable)",
            "⬡ Hexagonal Honeycomb Lattice (Odd/Even Hatchable)",
            "🧱 Brick / Subway Tile Mesh (Odd/Even Hatchable)",
            "🐟 Fish Scale / Moroccan Scallop (Odd/Even Hatchable)",
            "🧺 Basketweave / Carbon Fiber Twill (Braided Texture)",
            "🌀 Helical Spiral Flutes (Continuous Ribbons)",
            "⚡ Herringbone / Chevron Zigzag Band",
            "🏛️ Greek Key / Meander Fretwork",
            "〰️ Harmonic Sine Wave Rings",
            "💈 Straight Axial Flutes (Longitudinal Ribs)",
            "📏 Precision 360° Engineering Scale",
            "🎯 Split Overlap Calibration Stripes"
        ])
        self.combo_pipe_pattern.setStyleSheet("font-weight: bold; color: #00d2ff; font-size: 9pt;")
        self.combo_pipe_pattern.setToolTip("Select continuous procedural texture or decorative wrap pattern")
        lay_pat.addWidget(self.combo_pipe_pattern, 0, 1)

        layout.addWidget(grp_pattern)

        # 2. Seamless 360° Circumference Coverage Group
        grp_circ = QGroupBox("Seamless 360° Circumference Coverage")
        lay_c = QGridLayout(grp_circ)
        lay_c.setSpacing(6)

        self.chk_pattern_auto_cover = QCheckBox("✔ Auto-Cover 100% Circumference (Seamless 360°)")
        self.chk_pattern_auto_cover.setChecked(True)
        self.chk_pattern_auto_cover.setStyleSheet("font-weight: bold; color: #00ff66; font-size: 9pt;")
        self.chk_pattern_auto_cover.setToolTip("Guarantees pattern seamlessly wraps the entire circumference C = pi * D with 0 seam gap or overlap")
        lay_c.addWidget(self.chk_pattern_auto_cover, 0, 0, 1, 2)

        self.chk_pattern_auto_update = QCheckBox("✔ Auto-Regenerate on Diameter Change")
        self.chk_pattern_auto_update.setChecked(True)
        self.chk_pattern_auto_update.setToolTip("Whenever you change the pipe diameter, the pattern automatically adapts to cover 100% of the new circumference")
        lay_c.addWidget(self.chk_pattern_auto_update, 1, 0, 1, 2)

        lay_c.addWidget(QLabel("Circumference Repeats:"), 2, 0)
        self.spn_pattern_repeats = QSpinBox()
        self.spn_pattern_repeats.setRange(2, 360)
        self.spn_pattern_repeats.setValue(24)
        self.spn_pattern_repeats.setSuffix(" repeats")
        self.spn_pattern_repeats.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_pattern_repeats.setToolTip("Number of facets or repeats evenly distributed around the 360° pipe circumference")
        lay_c.addWidget(self.spn_pattern_repeats, 2, 1)

        lay_c.addWidget(QLabel("Axial Divisions / Rows:"), 3, 0)
        self.spn_pattern_axial_repeats = CleanAxialSpinBox()
        self.spn_pattern_axial_repeats.setRange(0, 500)
        self.spn_pattern_axial_repeats.setValue(0)
        self.spn_pattern_axial_repeats.setStyleSheet("color: #00d2ff;")
        self.spn_pattern_axial_repeats.setToolTip("Independent control of repeats along cylinder axis (0 = automatic square aspect ratio)")
        lay_c.addWidget(self.spn_pattern_axial_repeats, 3, 1)

        lay_c.addWidget(QLabel("Axial Length (mm):"), 4, 0)
        self.spn_pattern_length = QDoubleSpinBox()
        self.spn_pattern_length.setRange(1.0, 1500.0)
        self.spn_pattern_length.setDecimals(2)
        self.spn_pattern_length.setValue(50.0)
        self.spn_pattern_length.setSuffix(" mm")
        self.spn_pattern_length.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_pattern_length.setToolTip("Coverage length along the pipe axis")
        lay_c.addWidget(self.spn_pattern_length, 4, 1)

        lay_c.addWidget(QLabel("Cell Inset / Spacing:"), 5, 0)
        self.spn_pattern_inset = QDoubleSpinBox()
        self.spn_pattern_inset.setRange(0.0, 10.0)
        self.spn_pattern_inset.setDecimals(2)
        self.spn_pattern_inset.setValue(0.0)
        self.spn_pattern_inset.setSuffix(" mm")
        self.spn_pattern_inset.setToolTip("Gap/margin between pattern tiles (0.0mm for touching boundaries)")
        lay_c.addWidget(self.spn_pattern_inset, 5, 1)

        lay_c.addWidget(QLabel("Spiral Turns / Wave Cycles:"), 6, 0)
        self.spn_pattern_param = QDoubleSpinBox()
        self.spn_pattern_param.setRange(0.25, 64.0)
        self.spn_pattern_param.setDecimals(2)
        self.spn_pattern_param.setValue(1.0)
        self.spn_pattern_param.setSingleStep(0.5)
        self.spn_pattern_param.setToolTip("Number of spiral revolutions for Helical Spiral, or frequency cycles for Sine Waves")
        lay_c.addWidget(self.spn_pattern_param, 6, 1)

        self.lbl_pattern_circ_info = QLabel("Circumference: C = 255.00 mm | Step: 10.63 mm (100% 360° Covered)")
        self.lbl_pattern_circ_info.setStyleSheet("color: #00ff66; font-size: 8pt; font-weight: bold;")
        lay_c.addWidget(self.lbl_pattern_circ_info, 7, 0, 1, 2)

        self.chk_pattern_align_slices = QCheckBox("✔ Auto-Align Slices to Pattern Repeats (Zero-Seam Slicing)")
        self.chk_pattern_align_slices.setChecked(True)
        self.chk_pattern_align_slices.setStyleSheet("font-weight: bold; color: #00ff66; font-size: 9pt;")
        self.chk_pattern_align_slices.setToolTip("Aligns slice boundaries exactly with pattern tile divisions so 45° and diagonal hatch lines are NEVER sliced in half!")
        lay_c.addWidget(self.chk_pattern_align_slices, 8, 0, 1, 2)

        layout.addWidget(grp_circ)

        # 3. Advanced Pattern Hatching & Alternating Infill Controls
        grp_pat_hatch = QGroupBox("Pattern Hatching & Alternating Cell Infill")
        lay_ph = QGridLayout(grp_pat_hatch)
        lay_ph.setSpacing(6)

        self.chk_pattern_hatch = QCheckBox("✔ Enable Hatch Infill for Pattern")
        self.chk_pattern_hatch.setChecked(True)
        self.chk_pattern_hatch.setStyleSheet("font-weight: bold; color: #00ff66; font-size: 9pt;")
        self.chk_pattern_hatch.setToolTip("Enables dense laser hatch scanlines inside pattern cells")
        lay_ph.addWidget(self.chk_pattern_hatch, 0, 0, 1, 2)

        lay_ph.addWidget(QLabel("Hatch Infill Style:"), 1, 0)
        self.combo_pattern_hatch_style = QComboBox()
        self.combo_pattern_hatch_style.addItems([
            "⚅ Odd/Even Checkerboard (Half Hatched, Half Outlines)",
            "⚄ Inverted Odd/Even (Odd Hatched, Even Outlines)",
            "⬛ Solid Alternating (Hatched Blocks Only, No Empty Outlines)",
            "▦ 0° / 90° Dual-Angle Cross Chess (Alternating Infill)",
            "📐 45° / -45° Herringbone Alternating (Twill Weave Infill)",
            "🔺 3-Angle Prism (0° / 60° / 120° Tri-Tone Infill)",
            "◎ Concentric Rings / Nested Cell Infill",
            "✖ Cross-Hatch Inside Each Cell (Dual Pass +90°)",
            "◼ All Cells Hatched (100% Infill)",
            "◻ Outlines Only (No Hatch Infill)"
        ])
        self.combo_pattern_hatch_style.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.combo_pattern_hatch_style.setToolTip("Control which cells receive hatch infill (half hatched odd/even, all hatched, twill, or cross chess)")
        lay_ph.addWidget(self.combo_pattern_hatch_style, 1, 1)

        lay_ph.addWidget(QLabel("Hatch Line Pitch:"), 2, 0)
        self.spn_pattern_hatch_pitch = QDoubleSpinBox()
        self.spn_pattern_hatch_pitch.setRange(0.005, 2.0)
        self.spn_pattern_hatch_pitch.setDecimals(3)
        self.spn_pattern_hatch_pitch.setValue(0.050)
        self.spn_pattern_hatch_pitch.setSuffix(" mm")
        self.spn_pattern_hatch_pitch.setStyleSheet("color: #00ff66; font-weight: bold;")
        self.spn_pattern_hatch_pitch.setToolTip("Laser line spacing inside pattern cells")
        lay_ph.addWidget(self.spn_pattern_hatch_pitch, 2, 1)

        lay_ph.addWidget(QLabel("Hatch Angle:"), 3, 0)
        self.spn_pattern_hatch_angle = QDoubleSpinBox()
        self.spn_pattern_hatch_angle.setRange(-180.0, 180.0)
        self.spn_pattern_hatch_angle.setDecimals(1)
        self.spn_pattern_hatch_angle.setValue(45.0)
        self.spn_pattern_hatch_angle.setSuffix("°")
        self.spn_pattern_hatch_angle.setToolTip("Orientation angle of hatch lines inside pattern cells (45° for knurls/basketweave, 0° for axial)")
        lay_ph.addWidget(self.spn_pattern_hatch_angle, 3, 1)

        lay_ph.addWidget(QLabel("Scan Direction:"), 4, 0)
        self.combo_pattern_hatch_dir = QComboBox()
        self.combo_pattern_hatch_dir.addItems([
            "⚡ Bidirectional (Fast Meander)",
            "➡️ Unidirectional (One-Way Scan, Uniform Glare)"
        ])
        self.combo_pattern_hatch_dir.setStyleSheet("color: #00d2ff;")
        lay_ph.addWidget(self.combo_pattern_hatch_dir, 4, 1)

        self.chk_pattern_mark_contour = QCheckBox("Mark Cell Perimeter Outlines")
        self.chk_pattern_mark_contour.setChecked(False)
        self.chk_pattern_mark_contour.setToolTip("Draw crisp outer boundary border around each cell")
        lay_ph.addWidget(self.chk_pattern_mark_contour, 5, 0, 1, 2)

        layout.addWidget(grp_pat_hatch)

        # 4. Generation Action Buttons
        lay_btns = QHBoxLayout()
        self.btn_generate_pattern = QPushButton("✨ Generate & Wrap Pattern")
        self.btn_generate_pattern.setStyleSheet("""
            QPushButton {
                background-color: #004d40;
                color: #00ff66;
                font-weight: bold;
                font-size: 9pt;
                padding: 8px 14px;
                border: 1px solid #00ff66;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00695c;
                color: #ffffff;
            }
        """)
        self.btn_generate_pattern.setToolTip("Generates the selected pattern and wraps it seamlessly around 100% of the pipe circumference")

        self.btn_append_pattern = QPushButton("+ Append")
        self.btn_append_pattern.setStyleSheet("background-color: #242b38; color: #a0aec0; padding: 8px 10px; font-weight: bold;")
        self.btn_append_pattern.setToolTip("Appends pattern to existing artwork instead of replacing it")

        lay_btns.addWidget(self.btn_generate_pattern, stretch=3)
        lay_btns.addWidget(self.btn_append_pattern, stretch=1)
        layout.addLayout(lay_btns)

        layout.addStretch()
        return widget

    def _build_tab_artwork_transform(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_file = QGroupBox("Presets & External CAD")
        lay_file = QVBoxLayout(grp_file)
        lay_p = QHBoxLayout()
        self.combo_presets = QComboBox()
        self.combo_presets.addItems([
            "Cylindrical Ruler (360°)",
            "Vernier Degree Scale",
            "Diamond Grid Wrap",
            "Calibration Stripes (Split Overlap)",
            "Load External DXF / SVG..."
        ])
        self.btn_load_pattern = QPushButton("Load")
        self.btn_open_file = QPushButton("📂 Open SVG / DXF")
        self.btn_open_file.setStyleSheet("background-color: #0d3b66; color: #00d2ff; font-weight: bold; padding: 4px 8px;")
        self.btn_open_file.setToolTip("Browse and load external SVG vector graphic or DXF CAD file")
        lay_p.addWidget(self.combo_presets, stretch=3)
        lay_p.addWidget(self.btn_load_pattern, stretch=1)
        lay_p.addWidget(self.btn_open_file, stretch=2)
        lay_file.addLayout(lay_p)
        layout.addWidget(grp_file)

        grp_trans = QGroupBox("Artwork Sizing & Positioning")
        lay_t = QGridLayout(grp_trans)
        lay_t.setSpacing(6)

        # Direct Millimeter Sizing Controls
        lay_t.addWidget(QLabel("Target Width (mm):"), 0, 0)
        self.spn_art_width = QDoubleSpinBox()
        self.spn_art_width.setRange(0.01, 1000.0)
        self.spn_art_width.setDecimals(2)
        self.spn_art_width.setValue(0.0)
        self.spn_art_width.setSuffix(" mm")
        self.spn_art_width.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_art_width.setToolTip("Set exact physical width in millimeters along cylinder axis")
        lay_t.addWidget(self.spn_art_width, 0, 1)

        lay_t.addWidget(QLabel("Target Height (mm):"), 1, 0)
        self.spn_art_height = QDoubleSpinBox()
        self.spn_art_height.setRange(0.01, 2500.0)
        self.spn_art_height.setDecimals(2)
        self.spn_art_height.setValue(0.0)
        self.spn_art_height.setSuffix(" mm")
        self.spn_art_height.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_art_height.setToolTip("Set exact physical height in millimeters along circumference")
        lay_t.addWidget(self.spn_art_height, 1, 1)

        # Offsets
        lay_t.addWidget(QLabel("Offset X (Axial):"), 2, 0)
        self.spn_offset_x = QDoubleSpinBox()
        self.spn_offset_x.setRange(-300.0, 300.0)
        self.spn_offset_x.setDecimals(2)
        self.spn_offset_x.setValue(0.0)
        self.spn_offset_x.setSuffix(" mm")
        lay_t.addWidget(self.spn_offset_x, 2, 1)

        lay_t.addWidget(QLabel("Offset Y (Rotary):"), 3, 0)
        self.spn_offset_y = QDoubleSpinBox()
        self.spn_offset_y.setRange(-500.0, 500.0)
        self.spn_offset_y.setDecimals(2)
        self.spn_offset_y.setValue(0.0)
        self.spn_offset_y.setSuffix(" mm")
        lay_t.addWidget(self.spn_offset_y, 3, 1)

        # Scale %
        lay_t.addWidget(QLabel("Scale X / Y (%):"), 4, 0)
        lay_scale = QHBoxLayout()
        self.spn_scale_x = QDoubleSpinBox()
        self.spn_scale_x.setRange(0.01, 10000.0)
        self.spn_scale_x.setDecimals(2)
        self.spn_scale_x.setValue(100.0)
        self.spn_scale_x.setSuffix("%")
        self.spn_scale_y = QDoubleSpinBox()
        self.spn_scale_y.setRange(0.01, 10000.0)
        self.spn_scale_y.setDecimals(2)
        self.spn_scale_y.setValue(100.0)
        self.spn_scale_y.setSuffix("%")
        lay_scale.addWidget(self.spn_scale_x)
        lay_scale.addWidget(self.spn_scale_y)
        lay_t.addLayout(lay_scale, 4, 1)

        # Rotation & Orientation Section
        lay_t.addWidget(QLabel("Rotation Angle:"), 5, 0)
        lay_rot = QHBoxLayout()
        self.spn_art_rotation = QDoubleSpinBox()
        self.spn_art_rotation.setRange(-360.0, 360.0)
        self.spn_art_rotation.setDecimals(1)
        self.spn_art_rotation.setValue(0.0)
        self.spn_art_rotation.setSingleStep(90.0)
        self.spn_art_rotation.setSuffix("°")
        self.spn_art_rotation.setStyleSheet("font-weight: bold; color: #00ff66;")
        self.spn_art_rotation.setToolTip("Rotate artwork around its center in degrees")

        self.btn_rot_ccw = QPushButton("⟲ -90°")
        self.btn_rot_ccw.setToolTip("Rotate 90° Counter-Clockwise")
        self.btn_rot_cw = QPushButton("⟳ +90°")
        self.btn_rot_cw.setToolTip("Rotate 90° Clockwise")
        lay_rot.addWidget(self.spn_art_rotation, stretch=2)
        lay_rot.addWidget(self.btn_rot_ccw, stretch=1)
        lay_rot.addWidget(self.btn_rot_cw, stretch=1)
        lay_t.addLayout(lay_rot, 5, 1)

        # Mirror / Flip Controls
        lay_mirror = QHBoxLayout()
        self.chk_mirror_x = QCheckBox("⇆ Mirror Horizontal (Flip X)")
        self.chk_mirror_x.setToolTip("Flips the artwork horizontally along the cylinder axis")
        self.chk_mirror_y = QCheckBox("⇅ Mirror Vertical (Flip Y)")
        self.chk_mirror_y.setToolTip("Flips the artwork vertically along the circumference")
        lay_mirror.addWidget(self.chk_mirror_x)
        lay_mirror.addWidget(self.chk_mirror_y)
        lay_t.addLayout(lay_mirror, 6, 0, 1, 2)

        # Dynamic Horizontal <-> Vertical Orientation Toggle Button
        self.btn_toggle_orientation = QPushButton("🔄 Rotate to Horizontal / Vertical (90°)")
        self.btn_toggle_orientation.setStyleSheet("""
            QPushButton {
                background-color: #0d3b66;
                color: #00d2ff;
                font-weight: bold;
                font-size: 9pt;
                padding: 6px 12px;
                border: 1px solid #00d2ff;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1a5276;
                color: #ffffff;
            }
        """)
        self.btn_toggle_orientation.setToolTip("If vertical, rotates to horizontal; if horizontal, rotates to vertical (90° toggle)")
        lay_t.addWidget(self.btn_toggle_orientation, 6, 0, 1, 2)

        self.lbl_art_size = QLabel("Size: W 0.00 x H 0.00 mm")
        self.lbl_art_size.setStyleSheet("color: #718096; font-size: 8pt;")
        lay_t.addWidget(self.lbl_art_size, 7, 0, 1, 2)

        self.chk_lock_aspect = QCheckBox("Lock Aspect Ratio")
        self.chk_lock_aspect.setChecked(False)
        lay_t.addWidget(self.chk_lock_aspect, 8, 0, 1, 2)

        self.chk_auto_fit_diameter = QCheckBox("Auto-Fit Height to 360° on Diameter Change")
        self.chk_auto_fit_diameter.setChecked(False)
        self.chk_auto_fit_diameter.setToolTip("Automatically keeps artwork height matched to workpiece circumference")
        lay_t.addWidget(self.chk_auto_fit_diameter, 9, 0, 1, 2)

        self.chk_mark_selected = QCheckBox("Mark Selected Only")
        self.chk_mark_selected.setChecked(False)
        lay_t.addWidget(self.chk_mark_selected, 10, 0, 1, 2)

        # Quick Fit & Sizing Action Buttons
        lay_fit = QHBoxLayout()
        self.btn_fit_part = QPushButton("Fit to Part")
        self.btn_fit_part.setStyleSheet("background-color: #1e3a5f; color: #00d2ff; font-weight: bold;")
        self.btn_fit_part.setToolTip("Scales artwork proportionally to fit comfortably on the cylindrical workpiece.")
        self.btn_reset_scale = QPushButton("1:1 CAD Size")
        self.btn_reset_scale.setToolTip("Restores 100% native CAD/SVG millimeter dimensions.")
        self.btn_fit_360 = QPushButton("Fit 360° Wrap")
        self.btn_fit_360.setToolTip("Scales artwork height so it seamlessly wraps 360° around workpiece.")
        self.btn_center_art = QPushButton("Center")
        self.btn_align_apex = QPushButton("Align 0°")
        lay_fit.addWidget(self.btn_fit_part)
        lay_fit.addWidget(self.btn_reset_scale)
        lay_fit.addWidget(self.btn_fit_360)
        lay_fit.addWidget(self.btn_center_art)
        lay_fit.addWidget(self.btn_align_apex)
        lay_t.addLayout(lay_fit, 11, 0, 1, 2)

        # 360° Circumference Tiling Group for Imported Vector CAD / SVG
        lay_tile = QHBoxLayout()
        lay_tile.addWidget(QLabel("Tile around 360°:"))
        self.spn_art_tile_count = QSpinBox()
        self.spn_art_tile_count.setRange(1, 64)
        self.spn_art_tile_count.setValue(4)
        self.spn_art_tile_count.setSuffix(" tiles")
        self.spn_art_tile_count.setToolTip("Number of times to duplicate and evenly distribute artwork around 360° circumference")
        lay_tile.addWidget(self.spn_art_tile_count)

        self.btn_art_tile_360 = QPushButton("🔄 Tile around Pipe")
        self.btn_art_tile_360.setStyleSheet("background-color: #0d3b66; color: #00d2ff; font-weight: bold;")
        self.btn_art_tile_360.setToolTip("Duplicates artwork N times around the 360° pipe circumference with equal angular spacing")
        lay_tile.addWidget(self.btn_art_tile_360)
        lay_t.addLayout(lay_tile, 12, 0, 1, 2)

        # Quick Hatch Bar
        lay_hatch_bar = QHBoxLayout()
        self.chk_art_hatch_quick = QCheckBox("Enable Hatch Fill")
        self.chk_art_hatch_quick.setToolTip("Quick toggle for laser hatch infill on this artwork")
        self.btn_goto_hatch = QPushButton("🏁 Hatch Settings...")
        self.btn_goto_hatch.setStyleSheet("background-color: #0d3b66; color: #00d2ff; font-weight: bold; padding: 4px 8px;")
        self.btn_goto_hatch.setToolTip("Switch to Hatch Fill tab to configure density, angle, and cross-hatch")
        lay_hatch_bar.addWidget(self.chk_art_hatch_quick)
        lay_hatch_bar.addWidget(self.btn_goto_hatch)
        lay_t.addLayout(lay_hatch_bar, 13, 0, 1, 2)

        layout.addWidget(grp_trans)
        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB: 🏁 EzCad-Style Rotary Vector Hatch Infill
    # -------------------------------------------------------------------------
    def _build_tab_hatch(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Master Switch Group
        grp_master = QGroupBox("EzCad Hatch Infill Control")
        lay_m = QVBoxLayout(grp_master)
        self.chk_hatch_enable = QCheckBox("✔ Enable Hatch Infill for Rotary Marking")
        self.chk_hatch_enable.setStyleSheet("font-weight: bold; font-size: 10pt; color: #00d2ff;")
        self.chk_hatch_enable.setToolTip("Generates dense laser infill scan lines for closed artwork and text contours")
        lay_m.addWidget(self.chk_hatch_enable)

        self.lbl_hatch_stats = QLabel("Status: Hatch Disabled (Contour Outlines Only)")
        self.lbl_hatch_stats.setStyleSheet("color: #a0aec0; font-size: 8pt;")
        lay_m.addWidget(self.lbl_hatch_stats)

        lbl_axial_hint = QLabel("💡 Tip: 0.0° Axial Hatch sweeps along cylinder axis without chopping lines across slice seams!")
        lbl_axial_hint.setStyleSheet("color: #00d2ff; font-size: 8pt; font-style: italic;")
        lbl_axial_hint.setWordWrap(True)
        lay_m.addWidget(lbl_axial_hint)
        layout.addWidget(grp_master)

        # Hatch Parameters Group
        grp_param = QGroupBox("Hatch Scanline Parameters")
        lay_p = QGridLayout(grp_param)
        lay_p.setSpacing(6)

        lay_p.addWidget(QLabel("Line Pitch / Spacing:"), 0, 0)
        self.spn_hatch_pitch = QDoubleSpinBox()
        self.spn_hatch_pitch.setRange(0.005, 5.0)
        self.spn_hatch_pitch.setDecimals(3)
        self.spn_hatch_pitch.setValue(0.050)
        self.spn_hatch_pitch.setSingleStep(0.010)
        self.spn_hatch_pitch.setSuffix(" mm")
        self.spn_hatch_pitch.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_hatch_pitch.setToolTip("Distance between adjacent scan lines (0.02mm to 0.08mm is standard for metal)")
        lay_p.addWidget(self.spn_hatch_pitch, 0, 1)

        lay_p.addWidget(QLabel("Hatch Angle:"), 1, 0)
        self.spn_hatch_angle = QDoubleSpinBox()
        self.spn_hatch_angle.setRange(-180.0, 180.0)
        self.spn_hatch_angle.setDecimals(1)
        self.spn_hatch_angle.setValue(0.0)  # 0.0 deg (Axial) is seamless for rotary!
        self.spn_hatch_angle.setSingleStep(5.0)
        self.spn_hatch_angle.setSuffix("°")
        self.spn_hatch_angle.setStyleSheet("font-weight: bold; color: #00ff66;")
        self.spn_hatch_angle.setToolTip("0° Axial runs parallel to cylinder axis for 100% seamless infill without slice lines")
        lay_p.addWidget(self.spn_hatch_angle, 1, 1)

        lay_p.addWidget(QLabel("Hatch Infill Type:"), 2, 0)
        self.combo_hatch_type = QComboBox()
        self.combo_hatch_type.addItems([
            "Linear Scanlines (1-Pass)",
            "Cross Hatch (+90° Orthogonal)",
            "Custom Angle Cross Hatch",
            "Triple Pass (3-Pass Velvet Matte)",
            "Concentric Infill (Contour Offset Loops)"
        ])
        self.combo_hatch_type.setStyleSheet("font-weight: bold; color: #00d2ff;")
        lay_p.addWidget(self.combo_hatch_type, 2, 1)

        lay_p.addWidget(QLabel("Cross Angle Offset:"), 3, 0)
        self.spn_hatch_cross_offset = QDoubleSpinBox()
        self.spn_hatch_cross_offset.setRange(1.0, 179.0)
        self.spn_hatch_cross_offset.setValue(90.0)
        self.spn_hatch_cross_offset.setSuffix("°")
        self.spn_hatch_cross_offset.setStyleSheet("color: #00d2ff;")
        lay_p.addWidget(self.spn_hatch_cross_offset, 3, 1)

        lay_p.addWidget(QLabel("Scan Direction:"), 4, 0)
        self.combo_hatch_direction = QComboBox()
        self.combo_hatch_direction.addItems([
            "⚡ Bidirectional (Fast Meander)",
            "➡️ Unidirectional (One-Way Scan, Uniform Glare)"
        ])
        self.combo_hatch_direction.setStyleSheet("color: #00d2ff;")
        lay_p.addWidget(self.combo_hatch_direction, 4, 1)

        lay_p.addWidget(QLabel("Overlap Comp:"), 5, 0)
        self.spn_hatch_overlap = QDoubleSpinBox()
        self.spn_hatch_overlap.setRange(0.00, 1.0)
        self.spn_hatch_overlap.setDecimals(3)
        self.spn_hatch_overlap.setValue(0.000)
        self.spn_hatch_overlap.setSingleStep(0.010)
        self.spn_hatch_overlap.setSuffix(" mm")
        self.spn_hatch_overlap.setStyleSheet("font-weight: bold; color: #00d2ff;")
        self.spn_hatch_overlap.setToolTip("Band overlap to bridge mechanical tolerance (0.000mm recommended for clean 45° hatch without double-burn stripe)")
        lay_p.addWidget(self.spn_hatch_overlap, 5, 1)

        lay_p.addWidget(QLabel("Edge Offset / Inset:"), 6, 0)
        self.spn_hatch_edge_offset = QDoubleSpinBox()
        self.spn_hatch_edge_offset.setRange(0.00, 2.0)
        self.spn_hatch_edge_offset.setDecimals(3)
        self.spn_hatch_edge_offset.setValue(0.000)
        self.spn_hatch_edge_offset.setSingleStep(0.005)
        self.spn_hatch_edge_offset.setSuffix(" mm")
        self.spn_hatch_edge_offset.setToolTip("Margin between the boundary outline and the hatch lines to prevent burning the edge")
        lay_p.addWidget(self.spn_hatch_edge_offset, 6, 1)

        self.chk_hatch_stagger_seam = QCheckBox("✔ Staggered Seam Blend (Anti-Section Lines for 45°/Angled Hatches)")
        self.chk_hatch_stagger_seam.setChecked(True)
        self.chk_hatch_stagger_seam.setStyleSheet("color: #00ff66; font-weight: bold;")
        self.chk_hatch_stagger_seam.setToolTip("Interleaves slice boundary cut points so 45° and diagonal hatch lines never form a visible horizontal dividing line across sections")
        lay_p.addWidget(self.chk_hatch_stagger_seam, 7, 0, 1, 2)

        self.chk_hatch_cross = QCheckBox("Cross Hatch (2nd Pass)")
        self.chk_hatch_cross.setChecked(False)
        self.chk_hatch_cross.setVisible(False)

        layout.addWidget(grp_param)

        # Contour Marking Options
        grp_seq = QGroupBox("Contour Outline & Sequence")
        lay_seq = QGridLayout(grp_seq)
        lay_seq.setSpacing(6)

        self.chk_hatch_mark_contour = QCheckBox("Mark Perimeter Outline (Contour)")
        self.chk_hatch_mark_contour.setChecked(True)
        self.chk_hatch_mark_contour.setToolTip("Marks the sharp outer boundary outline of the vector artwork")
        lay_seq.addWidget(self.chk_hatch_mark_contour, 0, 0, 1, 2)

        lay_seq.addWidget(QLabel("Marking Sequence:"), 1, 0)
        self.combo_hatch_order = QComboBox()
        self.combo_hatch_order.addItems(["Outline First, then Hatch", "Hatch First, then Outline"])
        lay_seq.addWidget(self.combo_hatch_order, 1, 1)

        self.chk_hatch_preview_reference_contour = QCheckBox("Preview Reference Borders when Contour Marking is Off")
        self.chk_hatch_preview_reference_contour.setChecked(True)
        self.chk_hatch_preview_reference_contour.setToolTip("Displays artwork boundary borders cleanly in preview even when contour marking is disabled")
        lay_seq.addWidget(self.chk_hatch_preview_reference_contour, 2, 0, 1, 2)

        layout.addWidget(grp_seq)

        # Quick 1-Click Presets
        grp_presets = QGroupBox("Seamless Density & Angle Presets")
        lay_pr = QGridLayout(grp_presets)
        lay_pr.setSpacing(6)

        self.btn_preset_axial0 = QPushButton("⭐ 0° Axial (Seamless)")
        self.btn_preset_axial0.setStyleSheet("background-color: #004d40; color: #00ff66; font-weight: bold;")
        self.btn_preset_fine = QPushButton("Fine 0° (0.025 mm)")
        self.btn_preset_cross45 = QPushButton("45° Cross Hatch")
        self.btn_preset_fine_cross = QPushButton("Fine Cross (0.035 mm)")
        self.btn_preset_draft = QPushButton("Draft (0.100 mm)")
        self.btn_preset_vert90 = QPushButton("90° Vertical")

        lay_pr.addWidget(self.btn_preset_axial0, 0, 0)
        lay_pr.addWidget(self.btn_preset_fine, 0, 1)
        lay_pr.addWidget(self.btn_preset_cross45, 0, 2)
        lay_pr.addWidget(self.btn_preset_fine_cross, 1, 0)
        lay_pr.addWidget(self.btn_preset_draft, 1, 1)
        lay_pr.addWidget(self.btn_preset_vert90, 1, 2)

        layout.addWidget(grp_presets)
        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB 4: ⚙ Rotary Setup & 4-Way Directional Jog Keypad
    # -------------------------------------------------------------------------
    def _build_tab_rotary_setup(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_hw = QGroupBox("Workpiece & Motor Setup")
        lay_hw = QGridLayout(grp_hw)
        lay_hw.setSpacing(6)

        lay_hw.addWidget(QLabel("Part Diameter:"), 0, 0)
        self.spn_diameter = QDoubleSpinBox()
        self.spn_diameter.setRange(1.0, 500.0)
        self.spn_diameter.setValue(25.0)
        self.spn_diameter.setDecimals(2)
        self.spn_diameter.setSuffix(" mm")
        lay_hw.addWidget(self.spn_diameter, 0, 1)

        lay_hw.addWidget(QLabel("Part Height / Len:"), 1, 0)
        self.spn_workpiece_height = QDoubleSpinBox()
        self.spn_workpiece_height.setRange(2.0, 600.0)
        self.spn_workpiece_height.setValue(50.0)
        self.spn_workpiece_height.setSuffix(" mm")
        lay_hw.addWidget(self.spn_workpiece_height, 1, 1)

        lay_hw.addWidget(QLabel("Circumference (C):"), 2, 0)
        self.spn_circumference = QDoubleSpinBox()
        self.spn_circumference.setRange(3.14, 2500.0)
        self.spn_circumference.setValue(78.54)
        self.spn_circumference.setDecimals(2)
        self.spn_circumference.setSuffix(" mm")
        self.spn_circumference.setStyleSheet("font-weight: bold; color: #00d2ff; background: #131720;")
        self.spn_circumference.setToolTip("Workpiece circumference (C = π × D). Enter circumference directly here!")
        lay_hw.addWidget(self.spn_circumference, 2, 1)

        lay_hw.addWidget(QLabel("Pulse Resolution:"), 3, 0)
        self.lbl_pulses_per_mm = QLabel("81.49 p/mm")
        self.lbl_pulses_per_mm.setStyleSheet("color: #a0b0c5;")
        lay_hw.addWidget(self.lbl_pulses_per_mm, 3, 1)

        lay_hw.addWidget(QLabel("Motor Axis (Output):"), 4, 0)
        self.combo_motor_axis = QComboBox()
        self.combo_motor_axis.addItems(["Z-Axis (Rotary Chuck Motor)", "X-Axis", "Y-Axis"])
        self.combo_motor_axis.setCurrentIndex(0)
        lay_hw.addWidget(self.combo_motor_axis, 4, 1)

        lay_hw.addWidget(QLabel("Slicing Direction:"), 5, 0)
        self.combo_rot_axis = QComboBox()
        self.combo_rot_axis.addItems(["Y-Axis (Cylindrical Wrap)", "X-Axis (Longitudinal Slicing)"])
        lay_hw.addWidget(self.combo_rot_axis, 5, 1)

        lay_hw_chk = QHBoxLayout()
        self.chk_reverse_dir = QCheckBox("Invert Direction")
        self.chk_ring_inside = QCheckBox("Ring Inside")
        self.chk_ring_inside.setToolTip("Mark inner bore surface of rings or tubes")
        lay_hw_chk.addWidget(self.chk_reverse_dir)
        lay_hw_chk.addWidget(self.chk_ring_inside)
        lay_hw.addLayout(lay_hw_chk, 6, 0, 1, 2)

        # Retain internal pulses_rev widget for kinematics & calibration compatibility (hidden from UI)
        self.spn_pulses_rev = QSpinBox()
        self.spn_pulses_rev.setRange(20, 500000)
        self.spn_pulses_rev.setValue(400)
        self.spn_pulses_rev.setVisible(False)

        lay_hw.addWidget(QLabel("Gear / Pulley Ratio:"), 7, 0)
        self.spn_gear_ratio = QDoubleSpinBox()
        self.spn_gear_ratio.setRange(0.001, 100.0)
        self.spn_gear_ratio.setValue(1.0000)
        self.spn_gear_ratio.setDecimals(4)
        lay_hw.addWidget(self.spn_gear_ratio, 7, 1)

        lay_gear_btns = QHBoxLayout()
        for g_label, g_val in [("0.7895 (323→255mm)", 0.7895), ("1.000", 1.0), ("1.250", 1.25), ("2.000", 2.0)]:
            btn = QPushButton(g_label)
            btn.setStyleSheet("padding: 2px 4px; font-size: 8pt;")
            btn.clicked.connect(lambda _, v=g_val: self.spn_gear_ratio.setValue(v))
            lay_gear_btns.addWidget(btn)
        lay_hw.addLayout(lay_gear_btns, 8, 0, 1, 2)

        lay_hw.addWidget(QLabel("Focal Z-Comp Delta:"), 9, 0)
        self.spn_z_offset = QDoubleSpinBox()
        self.spn_z_offset.setRange(-50.0, 50.0)
        self.spn_z_offset.setValue(0.0)
        self.spn_z_offset.setSuffix(" mm")
        lay_hw.addWidget(self.spn_z_offset, 9, 1)

        layout.addWidget(grp_hw)

        # 4-Way Directional Jog Keypad
        grp_jog = QGroupBox("4-Way Jog & Calibration Keypad")
        lay_j = QVBoxLayout(grp_jog)
        lay_j.setSpacing(6)

        lay_j_cfg = QHBoxLayout()
        lay_j_cfg.addWidget(QLabel("Axis Step:"))
        self.combo_axis_step = QComboBox()
        self.combo_axis_step.addItems(["0.10", "0.50", "1.00", "5.00", "10.00", "45.00", "90.00", "180.00", "360.00"])
        self.combo_axis_step.setCurrentText("5.00")
        lay_j_cfg.addWidget(self.combo_axis_step)

        self.spn_jog_step = QDoubleSpinBox()
        self.spn_jog_step.setRange(0.01, 360.0)
        self.spn_jog_step.setValue(5.0)
        self.spn_jog_step.setSuffix(" mm/°")
        lay_j_cfg.addWidget(self.spn_jog_step)
        lay_j.addLayout(lay_j_cfg)

        grid_arrows = QGridLayout()
        grid_arrows.setSpacing(6)

        self.btn_jog_up = QPushButton("▲\nRotate +")
        self.btn_jog_up.setStyleSheet("font-size: 11pt; font-weight: bold; padding: 6px;")
        self.btn_jog_down = QPushButton("▼\nRotate -")
        self.btn_jog_down.setStyleSheet("font-size: 11pt; font-weight: bold; padding: 6px;")
        self.btn_jog_left = QPushButton("◄\nAxial -")
        self.btn_jog_left.setStyleSheet("font-size: 11pt; font-weight: bold; padding: 6px;")
        self.btn_jog_right = QPushButton("►\nAxial +")
        self.btn_jog_right.setStyleSheet("font-size: 11pt; font-weight: bold; padding: 6px;")

        grid_arrows.addWidget(self.btn_jog_up, 0, 1)
        grid_arrows.addWidget(self.btn_jog_left, 1, 0)
        grid_arrows.addWidget(self.btn_jog_right, 1, 2)
        grid_arrows.addWidget(self.btn_jog_down, 2, 1)
        lay_j.addLayout(grid_arrows)

        lay_orig = QHBoxLayout()
        self.btn_z_origin = QPushButton("Z Origin")
        self.btn_set_zero = QPushButton("Set Origin (0°)")
        self.btn_go_zero = QPushButton("Go To Origin (0°)")
        lay_orig.addWidget(self.btn_z_origin)
        lay_orig.addWidget(self.btn_set_zero)
        lay_orig.addWidget(self.btn_go_zero)
        lay_j.addLayout(lay_orig)

        lay_cal_btns = QHBoxLayout()
        self.btn_test_360 = QPushButton("Test 360° Full Revolution")
        self.btn_test_360.setStyleSheet("background-color: #3b2d18; color: #ffaa00; font-weight: bold; padding: 6px;")
        self.btn_calibrate_360 = QPushButton("⚙ Calibrate 360°")
        self.btn_calibrate_360.setStyleSheet("background-color: #1a3c5a; color: #00d2ff; font-weight: bold; padding: 6px;")
        self.btn_calibrate_360.setToolTip("Interactive 360° rotation calibration wizard")
        lay_cal_btns.addWidget(self.btn_test_360)
        lay_cal_btns.addWidget(self.btn_calibrate_360)
        lay_j.addLayout(lay_cal_btns)

        self.lbl_current_angle = QLabel("Position: X: 0.000 mm | Z: 0.000° (0 pulses)")
        self.lbl_current_angle.setStyleSheet("color: #00ffcc; font-family: Consolas; font-size: 8pt;")
        lay_j.addWidget(self.lbl_current_angle)

        layout.addWidget(grp_jog)
        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB 5: ✂ Slicing & Kinematics (SplitMark2)
    # -------------------------------------------------------------------------
    def _build_tab_slicing(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_split = QGroupBox("Split Slicing & Kinematics")
        lay_s = QGridLayout(grp_split)
        lay_s.setSpacing(6)

        lay_s.addWidget(QLabel("Marking Mode:"), 0, 0)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            "Split By Size (Cylindrical Strips)",
            "Mark By Split Line (Manual)",
            "Angular Indexing (N Parts / 360°)"
        ])
        lay_s.addWidget(self.combo_mode, 0, 1)

        lay_s.addWidget(QLabel("Split Size (S):"), 1, 0)
        lay_sp = QHBoxLayout()
        self.spn_split_size = QDoubleSpinBox()
        self.spn_split_size.setRange(0.05, 100.0)
        self.spn_split_size.setValue(2.00)
        self.spn_split_size.setDecimals(2)
        self.spn_split_size.setSuffix(" mm")
        self.btn_apply_opt_split = QPushButton("🎯 Auto")
        self.btn_apply_opt_split.setToolTip("Set optically optimal split size for current diameter")
        self.btn_apply_opt_split.setFixedWidth(55)
        lay_sp.addWidget(self.spn_split_size)
        lay_sp.addWidget(self.btn_apply_opt_split)
        lay_s.addLayout(lay_sp, 1, 1)

        self.lbl_opt_split_hint = QLabel("(Optimal for Ø25.0mm: 2.00 mm)")
        self.lbl_opt_split_hint.setStyleSheet("color: #00d2ff; font-size: 8pt;")
        lay_s.addWidget(self.lbl_opt_split_hint, 2, 1)

        self.chk_auto_split_diameter = QCheckBox("Auto-Update Split Size on Diameter Change")
        self.chk_auto_split_diameter.setChecked(True)
        lay_s.addWidget(self.chk_auto_split_diameter, 3, 0, 1, 2)

        lay_s.addWidget(QLabel("Overlap Comp:"), 4, 0)
        self.spn_overlap = QDoubleSpinBox()
        self.spn_overlap.setRange(-2.0, 2.0)
        self.spn_overlap.setValue(0.000)
        self.spn_overlap.setDecimals(3)
        self.spn_overlap.setSuffix(" mm")
        lay_s.addWidget(self.spn_overlap, 4, 1)

        lay_s.addWidget(QLabel("Angular Stations (N):"), 5, 0)
        self.spn_angular_parts = QSpinBox()
        self.spn_angular_parts.setRange(1, 72)
        self.spn_angular_parts.setValue(6)
        self.spn_angular_parts.setEnabled(False)
        lay_s.addWidget(self.spn_angular_parts, 5, 1)

        lay_s_chk = QHBoxLayout()
        self.chk_force_split = QCheckBox("Force Split")
        self.chk_force_all_split = QCheckBox("Force All Split")
        lay_s_chk.addWidget(self.chk_force_split)
        lay_s_chk.addWidget(self.chk_force_all_split)
        lay_s.addLayout(lay_s_chk, 6, 0, 1, 2)

        lay_s_preview_opts = QHBoxLayout()
        self.chk_show_slice_partitions = QCheckBox("Show Slice Partition Lines in Preview")
        self.chk_show_slice_partitions.setChecked(False)
        self.chk_show_slice_partitions.setToolTip("Toggle on to view slice boundary bands; uncheck to see clean artwork without section lines")
        lay_s_preview_opts.addWidget(self.chk_show_slice_partitions)
        lay_s.addLayout(lay_s_preview_opts, 7, 0, 1, 2)

        # Custom Split Lines Frame
        self.frame_split_lines = QFrame()
        lay_sl_box = QVBoxLayout(self.frame_split_lines)
        lay_sl_box.setContentsMargins(0, 0, 0, 0)
        lay_sl_btns = QHBoxLayout()
        self.spn_new_split_line = QDoubleSpinBox()
        self.spn_new_split_line.setRange(0.0, 500.0)
        self.spn_new_split_line.setValue(10.0)
        self.spn_new_split_line.setSuffix(" mm")
        self.btn_add_split_line = QPushButton("+ Add Line")
        self.btn_clear_split_lines = QPushButton("Clear")
        lay_sl_btns.addWidget(self.spn_new_split_line)
        lay_sl_btns.addWidget(self.btn_add_split_line)
        lay_sl_btns.addWidget(self.btn_clear_split_lines)
        lay_sl_box.addLayout(lay_sl_btns)
        self.frame_split_lines.setVisible(False)
        lay_s.addWidget(self.frame_split_lines, 7, 0, 1, 2)

        # Kinematics
        lay_s.addWidget(QLabel("Max Speed (pps):"), 8, 0)
        self.spn_max_speed = QSpinBox()
        self.spn_max_speed.setRange(100, 50000)
        self.spn_max_speed.setValue(600)
        lay_s.addWidget(self.spn_max_speed, 8, 1)

        lay_s.addWidget(QLabel("Acceleration (ms):"), 9, 0)
        self.spn_accel_time = QSpinBox()
        self.spn_accel_time.setRange(10, 1000)
        self.spn_accel_time.setValue(250)
        self.spn_accel_time.setSuffix(" ms")
        lay_s.addWidget(self.spn_accel_time, 9, 1)

        lay_s.addWidget(QLabel("Settling Delay:"), 10, 0)
        self.spn_settling_delay = QSpinBox()
        self.spn_settling_delay.setRange(0, 2000)
        self.spn_settling_delay.setValue(150)
        self.spn_settling_delay.setSuffix(" ms")
        lay_s.addWidget(self.spn_settling_delay, 10, 1)

        self.lbl_slice_stats = QLabel("Slices: 0 | Total Pulses: 0 | Est: ~0s")
        self.lbl_slice_stats.setStyleSheet("color: #ff9900; font-weight: bold; font-size: 8pt;")
        lay_s.addWidget(self.lbl_slice_stats, 11, 0, 1, 2)

        self.btn_recalculate_slices = QPushButton("Recalculate Slices")
        self.btn_recalculate_slices.setStyleSheet("background-color: #2b3545; color: #00d2ff;")
        lay_s.addWidget(self.btn_recalculate_slices, 12, 0, 1, 2)

        layout.addWidget(grp_split)
        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # TAB 6: ⚡ Laser Marking Parameters & Execution
    # -------------------------------------------------------------------------
    def _build_tab_execution(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        grp_laser = QGroupBox("Laser Parameters")
        lay_l = QGridLayout(grp_laser)
        lay_l.setSpacing(6)

        lay_l.addWidget(QLabel("Laser Power:"), 0, 0)
        self.spn_laser_power = QDoubleSpinBox()
        self.spn_laser_power.setRange(1.0, 100.0)
        self.spn_laser_power.setValue(80.0)
        self.spn_laser_power.setSuffix(" %")
        lay_l.addWidget(self.spn_laser_power, 0, 1)

        lay_l.addWidget(QLabel("Frequency:"), 1, 0)
        self.spn_laser_freq = QDoubleSpinBox()
        self.spn_laser_freq.setRange(20.0, 80.0)
        self.spn_laser_freq.setValue(30.0)
        self.spn_laser_freq.setSuffix(" kHz")
        lay_l.addWidget(self.spn_laser_freq, 1, 1)

        lay_l.addWidget(QLabel("Mark Speed:"), 2, 0)
        self.spn_mark_speed = QSpinBox()
        self.spn_mark_speed.setRange(10, 5000)
        self.spn_mark_speed.setValue(500)
        self.spn_mark_speed.setSuffix(" mm/s")
        lay_l.addWidget(self.spn_mark_speed, 2, 1)

        lay_l.addWidget(QLabel("Jump Speed:"), 3, 0)
        self.spn_jump_speed = QSpinBox()
        self.spn_jump_speed.setRange(50, 10000)
        self.spn_jump_speed.setValue(2000)
        self.spn_jump_speed.setSuffix(" mm/s")
        lay_l.addWidget(self.spn_jump_speed, 3, 1)

        layout.addWidget(grp_laser)

        grp_opts = QGroupBox("Execution Options")
        lay_opt = QVBoxLayout(grp_opts)
        self.chk_loop_framing = QCheckBox("Loop Red Light Framing")
        self.chk_loop_framing.setChecked(False)
        self.chk_continuous = QCheckBox("Continuous Marking (Run in Loop)")
        self.chk_continuous.setChecked(False)
        self.chk_return_zero = QCheckBox("Return to Zero After Marking")
        self.chk_return_zero.setChecked(True)
        lay_opt.addWidget(self.chk_loop_framing)
        lay_opt.addWidget(self.chk_continuous)
        lay_opt.addWidget(self.chk_return_zero)
        layout.addWidget(grp_opts)

        grp_exec = QGroupBox("Execution Controls")
        lay_exec = QVBoxLayout(grp_exec)
        lay_exec.setSpacing(6)

        lay_b1 = QHBoxLayout()
        self.btn_redlight = QPushButton("Light (F1)")
        self.btn_redlight.setStyleSheet("background-color: #7a1515; color: #ffcccc; font-weight: bold; padding: 10px; font-size: 10pt;")
        self.btn_mark = QPushButton("START MARK (F2)")
        self.btn_mark.setStyleSheet("background-color: #0d6b38; color: #ccffdd; font-weight: bold; font-size: 11pt; padding: 12px;")
        lay_b1.addWidget(self.btn_redlight)
        lay_b1.addWidget(self.btn_mark)
        lay_exec.addLayout(lay_b1)

        lay_b2 = QHBoxLayout()
        self.btn_pause = QPushButton("PAUSE")
        self.btn_pause.setStyleSheet("background-color: #554411; color: #ffdd88; font-weight: bold; padding: 8px;")
        self.btn_pause.setEnabled(False)
        self.btn_stop = QPushButton("STOP (F3)")
        self.btn_stop.setStyleSheet("background-color: #9e1a1a; color: #ffffff; font-weight: bold; font-size: 10pt; padding: 8px;")
        lay_b2.addWidget(self.btn_pause)
        lay_b2.addWidget(self.btn_stop)
        lay_exec.addLayout(lay_b2)

        lay_b3 = QHBoxLayout()
        self.btn_param = QPushButton("Param (F3)")
        self.btn_quit = QPushButton("Quit (F5)")
        lay_b3.addWidget(self.btn_param)
        lay_b3.addWidget(self.btn_quit)
        lay_exec.addLayout(lay_b3)

        layout.addWidget(grp_exec)
        layout.addStretch()
        return widget

    def _apply_dark_industrial_style(self):
        """Applies sleek dark industrial styling matching the rest of the application."""
        self.setStyleSheet("""
            QWidget {
                background-color: #16191f;
                color: #e2e8f0;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #2a313d;
                border-radius: 6px;
                background-color: #181c24;
                top: -1px;
            }
            QTabBar::tab {
                background: #14171e;
                border: 1px solid #28303d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 10px;
                color: #8fa0b5;
                font-weight: bold;
                font-size: 8pt;
            }
            QTabBar::tab:selected {
                background: #1c222d;
                border-color: #00d2ff;
                color: #00d2ff;
            }
            QGroupBox {
                border: 1px solid #2a313d;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 9pt;
                color: #00d2ff;
                padding: 10px 6px 6px 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QPushButton {
                background-color: #242b38;
                border: 1px solid #374254;
                border-radius: 4px;
                color: #e2e8f0;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #313a4d;
                border-color: #00d2ff;
            }
            QPushButton:pressed {
                background-color: #1a202c;
            }
            QPushButton:checked {
                background-color: #005a7d;
                border-color: #00d2ff;
                color: #ffffff;
            }
            QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: #1c212a;
                border: 1px solid #333d4d;
                border-radius: 4px;
                padding: 3px 6px;
                color: #ffffff;
                font-size: 9pt;
            }
            QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
                border: 1px solid #00d2ff;
            }
            QProgressBar {
                background-color: #1a1e27;
                border: 1px solid #2c3444;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0099cc, stop:1 #00ff66);
                border-radius: 3px;
            }
            QCheckBox {
                spacing: 6px;
                color: #cbd5e1;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                background-color: #1c212a;
                border: 1px solid #3b4557;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #00d2ff;
                border-color: #00d2ff;
            }
            QFrame#progressBox {
                background-color: #1a1e27;
                border: 1px solid #283140;
                border-radius: 6px;
            }
        """)

    def _connect_signals(self):
        """Wires up all UI signals and slots."""
        # Canvas Controls
        self.btn_view_3d.clicked.connect(lambda: self.canvas.set_view_mode('cylinder_3d'))
        self.btn_view_2d.clicked.connect(lambda: self.canvas.set_view_mode('unwrapped_2d'))
        self.btn_auto_spin.clicked.connect(self._on_toggle_auto_spin)
        self.combo_theme.currentTextChanged.connect(self.canvas.set_material_theme)
        self.chk_xray.toggled.connect(self.canvas.set_xray_mode)
        self.btn_reset_view.clicked.connect(self.canvas.reset_view)
        self.btn_back_cad.clicked.connect(self.on_back_to_cad_clicked)
        self.btn_quit.clicked.connect(self.on_back_to_cad_clicked)

        self.canvas.sliceSelected.connect(self.on_slice_selected_on_canvas)
        self.canvas.splitLineAdded.connect(self.on_split_line_added_from_canvas)

        # Quick Workpiece Dimensions Bar
        self.spn_top_diameter.valueChanged.connect(self._on_top_diameter_changed)
        self.spn_top_height.valueChanged.connect(self._on_top_height_changed)
        self.btn_top_optimal_split.clicked.connect(self._apply_optimal_split)
        self.btn_top_refresh.clicked.connect(self._on_dimensions_changed)

        # Tab 1: Direct Text
        self.btn_apply_text.clicked.connect(lambda: self.on_generate_direct_text(append=False))
        self.btn_append_text.clicked.connect(lambda: self.on_generate_direct_text(append=True))
        self.txt_direct_text.textChanged.connect(self._on_text_string_typing)
        self.txt_direct_text.returnPressed.connect(lambda: self.on_generate_direct_text(append=False))
        self.combo_font_family.currentTextChanged.connect(self._on_text_param_changed)
        self.spn_text_diameter.valueChanged.connect(self._on_top_diameter_changed)
        self.spn_font_size.valueChanged.connect(self._on_text_param_changed)
        self.spn_letter_spacing.valueChanged.connect(self._on_text_param_changed)
        self.chk_font_bold.toggled.connect(self._on_text_param_changed)
        self.chk_font_italic.toggled.connect(self._on_text_param_changed)
        self.combo_text_orientation.currentIndexChanged.connect(self._on_text_param_changed)
        self.spn_text_reps.valueChanged.connect(self._on_text_param_changed)
        self.spn_text_start_angle.valueChanged.connect(self._on_text_param_changed)
        self.chk_text_autofit.toggled.connect(self._on_text_param_changed)

        # Tab 2: Scale Ruler
        self.btn_apply_ruler.clicked.connect(lambda: self.on_generate_scale_ruler(append=False))
        self.btn_append_ruler.clicked.connect(lambda: self.on_generate_scale_ruler(append=True))
        self.spn_ruler_diameter.valueChanged.connect(self._on_top_diameter_changed)
        self.combo_ruler_type.currentIndexChanged.connect(self._on_ruler_param_changed)
        self.spn_ruler_minor_step.valueChanged.connect(self._on_ruler_param_changed)
        self.spn_ruler_medium_step.valueChanged.connect(self._on_ruler_param_changed)
        self.spn_ruler_major_step.valueChanged.connect(self._on_ruler_param_changed)
        self.combo_ruler_side.currentIndexChanged.connect(self._on_ruler_param_changed)
        self.chk_ruler_baseline.toggled.connect(self._on_ruler_param_changed)
        self.chk_ruler_numbers.toggled.connect(self._on_ruler_param_changed)
        self.spn_ruler_num_step.valueChanged.connect(self._on_ruler_param_changed)
        self.spn_ruler_font_sz.valueChanged.connect(self._on_ruler_param_changed)

        # Tab 3: Presets & Transform
        self.btn_load_pattern.clicked.connect(self.on_load_pattern_clicked)
        self.btn_open_file.clicked.connect(self.load_external_file)
        self.spn_art_width.editingFinished.connect(lambda: self._on_art_width_changed(self.spn_art_width.value()))
        self.spn_art_height.editingFinished.connect(lambda: self._on_art_height_changed(self.spn_art_height.value()))
        self.spn_art_width.valueChanged.connect(self._on_art_width_changed)
        self.spn_art_height.valueChanged.connect(self._on_art_height_changed)
        self.spn_offset_x.valueChanged.connect(self.apply_artwork_transforms)
        self.spn_offset_y.valueChanged.connect(self.apply_artwork_transforms)
        self.spn_scale_x.valueChanged.connect(self._on_scale_x_changed)
        self.spn_scale_y.valueChanged.connect(self._on_scale_y_changed)
        self.btn_fit_part.clicked.connect(self.fit_artwork_to_workpiece)
        self.btn_reset_scale.clicked.connect(self.reset_artwork_scale)
        self.btn_fit_360.clicked.connect(self.fit_artwork_to_360)
        self.btn_center_art.clicked.connect(self.center_artwork_on_cylinder)
        self.btn_align_apex.clicked.connect(self.align_artwork_to_apex)

        # Rotation, Mirror & Relocation Signals
        self.spn_art_rotation.valueChanged.connect(self.apply_artwork_transforms)
        self.btn_rot_ccw.clicked.connect(lambda: self.rotate_artwork_by(-90.0))
        self.btn_rot_cw.clicked.connect(lambda: self.rotate_artwork_by(90.0))
        self.btn_toggle_orientation.clicked.connect(self.toggle_artwork_orientation)
        self.btn_canvas_toggle_rot.clicked.connect(self.toggle_artwork_orientation)
        self.btn_canvas_wrap360.clicked.connect(self.fit_artwork_to_360)
        if hasattr(self, 'chk_mirror_x'):
            self.chk_mirror_x.toggled.connect(self._on_mirror_x_toggled)
        if hasattr(self, 'chk_mirror_y'):
            self.chk_mirror_y.toggled.connect(self._on_mirror_y_toggled)

        # Pipe Patterns Tab Signals
        self.btn_generate_pattern.clicked.connect(lambda: self.on_generate_pipe_pattern(append=False, auto_triggered=False))
        self.btn_append_pattern.clicked.connect(lambda: self.on_generate_pipe_pattern(append=True, auto_triggered=False))
        self.combo_pipe_pattern.currentIndexChanged.connect(self._on_pattern_param_changed)
        self.spn_pattern_repeats.valueChanged.connect(self._on_pattern_param_changed)
        self.spn_pattern_length.valueChanged.connect(self._on_pattern_param_changed)
        self.spn_pattern_param.valueChanged.connect(self._on_pattern_param_changed)
        self.chk_pattern_hatch.toggled.connect(self._on_pattern_hatch_toggled)
        if hasattr(self, 'combo_pattern_hatch_style'):
            self.combo_pattern_hatch_style.currentIndexChanged.connect(self._on_pattern_param_changed)
        if hasattr(self, 'spn_pattern_hatch_pitch'):
            self.spn_pattern_hatch_pitch.valueChanged.connect(self._on_pattern_param_changed)
        if hasattr(self, 'spn_pattern_hatch_angle'):
            self.spn_pattern_hatch_angle.valueChanged.connect(self._on_pattern_param_changed)
        if hasattr(self, 'chk_pattern_mark_contour'):
            self.chk_pattern_mark_contour.toggled.connect(self._on_pattern_param_changed)
        if hasattr(self, 'spn_pattern_axial_repeats'):
            self.spn_pattern_axial_repeats.valueChanged.connect(self._on_pattern_param_changed)
        if hasattr(self, 'spn_pattern_inset'):
            self.spn_pattern_inset.valueChanged.connect(self._on_pattern_param_changed)

        if hasattr(self, 'chk_pattern_align_slices'):
            self.chk_pattern_align_slices.toggled.connect(self._on_pattern_param_changed)
        if hasattr(self, 'combo_pattern_hatch_dir'):
            self.combo_pattern_hatch_dir.currentIndexChanged.connect(self._on_pattern_param_changed)
        if hasattr(self, 'combo_hatch_type'):
            self.combo_hatch_type.currentIndexChanged.connect(self._on_hatch_param_changed)
        if hasattr(self, 'spn_hatch_cross_offset'):
            self.spn_hatch_cross_offset.valueChanged.connect(self._on_hatch_param_changed)
        if hasattr(self, 'combo_hatch_direction'):
            self.combo_hatch_direction.currentIndexChanged.connect(self._on_hatch_param_changed)
        if hasattr(self, 'chk_hatch_stagger_seam'):
            self.chk_hatch_stagger_seam.toggled.connect(self._on_hatch_param_changed)
        # Artwork 360° Tiling Signal
        self.btn_art_tile_360.clicked.connect(self.tile_current_artwork_360)

        # Tab: Hatch Fill Signals
        self.chk_hatch_enable.toggled.connect(self._on_hatch_param_changed)
        self.spn_hatch_pitch.valueChanged.connect(self._on_hatch_param_changed)
        self.spn_hatch_angle.valueChanged.connect(self._on_hatch_param_changed)
        self.chk_hatch_cross.toggled.connect(self._on_hatch_param_changed)
        self.spn_hatch_edge_offset.valueChanged.connect(self._on_hatch_param_changed)
        self.chk_hatch_mark_contour.toggled.connect(self._on_hatch_param_changed)
        self.combo_hatch_order.currentIndexChanged.connect(self._on_hatch_param_changed)
        if hasattr(self, 'chk_hatch_preview_reference_contour'):
            self.chk_hatch_preview_reference_contour.toggled.connect(self.canvas.update)

        # Quick Sync Checkboxes
        self.chk_art_hatch_quick.toggled.connect(self._on_quick_art_hatch_toggled)
        self.chk_text_hatch_quick.toggled.connect(self._on_quick_text_hatch_toggled)
        self.btn_goto_hatch.clicked.connect(lambda: self.tabs.setCurrentWidget(self.tab_hatch))

        # Overlap sync between Hatch and Slicing tabs
        self.spn_hatch_overlap.valueChanged.connect(self._on_hatch_overlap_changed)
        self.spn_overlap.valueChanged.connect(self._on_slicing_overlap_changed)

        # Preset Buttons
        self.btn_preset_axial0.clicked.connect(lambda: self._set_hatch_preset(pitch=0.050, angle=0.0, cross=False))
        self.btn_preset_fine.clicked.connect(lambda: self._set_hatch_preset(pitch=0.025, angle=0.0, cross=False))
        self.btn_preset_cross45.clicked.connect(lambda: self._set_hatch_preset(pitch=0.050, angle=45.0, cross=True))
        self.btn_preset_fine_cross.clicked.connect(lambda: self._set_hatch_preset(pitch=0.035, angle=45.0, cross=True))
        self.btn_preset_draft.clicked.connect(lambda: self._set_hatch_preset(pitch=0.100, angle=0.0, cross=False))
        self.btn_preset_vert90.clicked.connect(lambda: self._set_hatch_preset(pitch=0.050, angle=90.0, cross=False))

        # Tab 4: Rotary Setup & 4-Way Jog
        self.spn_diameter.valueChanged.connect(self._on_dimensions_changed)
        if hasattr(self, 'spn_circumference'): self.spn_circumference.valueChanged.connect(self._on_circumference_input_changed)
        self.spn_workpiece_height.valueChanged.connect(self._on_dimensions_changed)
        self.spn_pulses_rev.valueChanged.connect(self._on_dimensions_changed)
        self.spn_gear_ratio.valueChanged.connect(self._on_dimensions_changed)
        self.combo_motor_axis.currentIndexChanged.connect(self.update_config_and_recalculate)
        self.combo_rot_axis.currentIndexChanged.connect(self.update_config_and_recalculate)
        self.chk_reverse_dir.toggled.connect(self.update_config_and_recalculate)
        self.chk_ring_inside.toggled.connect(self._on_ring_inside_toggled)

        # 4-Way Arrow Keypad
        self.btn_jog_up.clicked.connect(lambda: self._on_jog_arrow('UP'))
        self.btn_jog_down.clicked.connect(lambda: self._on_jog_arrow('DOWN'))
        self.btn_jog_left.clicked.connect(lambda: self._on_jog_arrow('LEFT'))
        self.btn_jog_right.clicked.connect(lambda: self._on_jog_arrow('RIGHT'))
        self.combo_axis_step.currentTextChanged.connect(self._on_axis_step_combo_changed)

        self.btn_z_origin.clicked.connect(self.set_zero_position)
        self.btn_set_zero.clicked.connect(self.set_zero_position)
        self.btn_go_zero.clicked.connect(self.go_to_zero_position)
        self.btn_test_360.clicked.connect(self.test_full_revolution)
        self.btn_calibrate_360.clicked.connect(self.on_calibrate_360)

        # Tab 5: Slicing
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        if hasattr(self, 'chk_show_slice_partitions'):
            self.chk_show_slice_partitions.toggled.connect(self._on_show_slice_partitions_toggled)
        self.spn_split_size.valueChanged.connect(self.update_config_and_recalculate)
        self.spn_overlap.valueChanged.connect(self.update_config_and_recalculate)
        self.spn_angular_parts.valueChanged.connect(self.update_config_and_recalculate)
        self.btn_apply_opt_split.clicked.connect(self._apply_optimal_split)
        self.btn_add_split_line.clicked.connect(self.on_add_split_line_clicked)
        self.btn_clear_split_lines.clicked.connect(self.on_clear_split_lines_clicked)
        self.btn_recalculate_slices.clicked.connect(self.update_config_and_recalculate)

        # Tab 6: Execution Controls & Counters
        self.btn_reset_part.clicked.connect(self._on_reset_part_count)
        self.btn_redlight.clicked.connect(self.on_redlight_clicked)
        self.btn_mark.clicked.connect(self.on_mark_clicked)
        self.btn_pause.clicked.connect(self.on_pause_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_param.clicked.connect(lambda: self.tabs.setCurrentIndex(5))

    # -------------------------------------------------------------------------
    # SYNCHRONIZED WORKPIECE DIMENSION MANAGEMENT
    # -------------------------------------------------------------------------
    def _on_top_diameter_changed(self, val: float):
        if abs(self.spn_diameter.value() - val) > 1e-4:
            self.spn_diameter.blockSignals(True)
            self.spn_diameter.setValue(val)
            self.spn_diameter.blockSignals(False)
            self._on_dimensions_changed()

    def _on_top_height_changed(self, val: float):
        if abs(self.spn_workpiece_height.value() - val) > 1e-4:
            self.spn_workpiece_height.blockSignals(True)
            self.spn_workpiece_height.setValue(val)
            self.spn_workpiece_height.blockSignals(False)
            self._on_dimensions_changed()

    @staticmethod
    def calculate_optimal_split_size(diameter: float) -> float:
        """
        Calculates optically optimal strip width S based on cylinder curvature and Rayleigh depth of focus:
        S = 2 * sqrt(D * delta_z_allowable), with delta_z_allowable = 0.04 mm.
        Clamped between 0.4 mm (small rings) and 10.0 mm (large cylinders).
        """
        opt = 2.0 * math.sqrt(max(1.0, diameter) * 0.04)
        return max(0.40, min(10.0, round(opt, 2)))

    def _apply_optimal_split(self):
        d = self.spn_diameter.value()
        opt_s = self.calculate_optimal_split_size(d)
        self.spn_split_size.setValue(opt_s)
        self.lbl_console_log.setText(f"Applied optical depth-of-focus split size: {opt_s:.2f} mm for Ø{d:.1f} mm.")

    def _on_circumference_input_changed(self, val: float):
        d = val / math.pi
        if abs(self.spn_diameter.value() - d) > 1e-4:
            self.spn_diameter.blockSignals(True)
            self.spn_diameter.setValue(d)
            self.spn_diameter.blockSignals(False)
            self._on_dimensions_changed()

    def _on_dimensions_changed(self):
        """
        Master dimension update pipeline:
        1. Recalculates circumference C = pi * D and pulse resolution K.
        2. Synchronizes top bar and tab 4 spinboxes.
        3. Updates optimal split size.
        4. Dynamically re-runs active generator (Direct Text, Scale Ruler, Preset, or CAD wrap).
        5. Recalculates slicing and re-frames 3D / 2D canvas viewports.
        """
        d = self.spn_diameter.value()
        h = self.spn_workpiece_height.value()
        c = math.pi * d
        p_rev = self.spn_pulses_rev.value()
        gear = self.spn_gear_ratio.value()
        tot_pulses = p_rev * gear
        p_per_mm = tot_pulses / max(1e-4, c)

        if hasattr(self, 'spn_circumference') and abs(self.spn_circumference.value() - c) > 1e-4:
            self.spn_circumference.blockSignals(True)
            self.spn_circumference.setValue(c)
            self.spn_circumference.blockSignals(False)
        self.lbl_pulses_per_mm.setText(f"{p_per_mm:.2f} p/mm")

        # Sync top bar
        if hasattr(self, 'spn_top_diameter') and abs(self.spn_top_diameter.value() - d) > 1e-4:
            self.spn_top_diameter.blockSignals(True)
            self.spn_top_diameter.setValue(d)
            self.spn_top_diameter.blockSignals(False)

        if hasattr(self, 'spn_top_height') and abs(self.spn_top_height.value() - h) > 1e-4:
            self.spn_top_height.blockSignals(True)
            self.spn_top_height.setValue(h)
            self.spn_top_height.blockSignals(False)

        if hasattr(self, 'lbl_top_c'):
            self.lbl_top_c.setText(f"C: {c:.2f} mm")

        # Sync Tab 1 Direct Text diameter & circumference
        if hasattr(self, 'spn_text_diameter') and abs(self.spn_text_diameter.value() - d) > 1e-4:
            self.spn_text_diameter.blockSignals(True)
            self.spn_text_diameter.setValue(d)
            self.spn_text_diameter.blockSignals(False)
        if hasattr(self, 'lbl_text_circ'):
            self.lbl_text_circ.setText(f"Circumference (C = pi*D): {c:.2f} mm")

        # Sync Tab 2 Scale Ruler diameter & circumference
        if hasattr(self, 'spn_ruler_diameter') and abs(self.spn_ruler_diameter.value() - d) > 1e-4:
            self.spn_ruler_diameter.blockSignals(True)
            self.spn_ruler_diameter.setValue(d)
            self.spn_ruler_diameter.blockSignals(False)
        if hasattr(self, 'lbl_ruler_circ'):
            self.lbl_ruler_circ.setText(f"Circumference (C = pi*D): {c:.2f} mm")

        # Optimal split size calculation
        opt_s = self.calculate_optimal_split_size(d)
        if hasattr(self, 'lbl_opt_split_hint'):
            self.lbl_opt_split_hint.setText(f"(Optimal for Ø{d:.1f}mm: {opt_s:.2f} mm)")

        if hasattr(self, 'chk_auto_split_diameter') and self.chk_auto_split_diameter.isChecked():
            self.spn_split_size.blockSignals(True)
            self.spn_split_size.setValue(opt_s)
            self.spn_split_size.blockSignals(False)

        # Update config object with new dimensions
        self.config = self.update_config_from_ui()

        # Adapt active artwork to new diameter
        gen_type = getattr(self, 'active_generator', 'preset')

        # Update Pipe Patterns Tab circumference label if present
        if hasattr(self, 'lbl_pattern_circ_info') and hasattr(self, 'spn_pattern_repeats'):
            rep = self.spn_pattern_repeats.value()
            st = c / max(1, rep)
            self.lbl_pattern_circ_info.setText(f"Circumference: C = {c:.2f} mm | Repeat Step: {st:.2f} mm (100% 360° Covered)")

        if gen_type == 'pipe_pattern':
            if hasattr(self, 'chk_pattern_auto_update') and self.chk_pattern_auto_update.isChecked():
                self.on_generate_pipe_pattern(append=False, auto_triggered=True)
            else:
                self.update_config_and_recalculate()
        elif gen_type == 'direct_text':
            self.on_generate_direct_text(append=False, auto_triggered=True)
        elif gen_type == 'scale_ruler':
            self.on_generate_scale_ruler(append=False, auto_triggered=True)
        elif gen_type == 'preset':
            curr_preset = self.combo_presets.currentText()
            if curr_preset != "Load External DXF / SVG...":
                self.load_preset_pattern(curr_preset, auto_triggered=True)
            else:
                self.update_config_and_recalculate()
        else: # CAD imported vector
            if hasattr(self, 'chk_auto_fit_diameter') and self.chk_auto_fit_diameter.isChecked() and self.source_paths:
                self.fit_artwork_to_360()
            else:
                self.update_config_and_recalculate()

        # Canvas viewport auto-framing
        self.canvas.reset_view()

    # -------------------------------------------------------------------------
    # DIRECT TEXT GENERATION & REACTIVITY
    # -------------------------------------------------------------------------
    def _on_text_string_typing(self):
        if self.tabs.currentIndex() == 0:
            self.typing_timer.start()

    def _on_text_param_changed(self):
        if self.tabs.currentIndex() == 0:
            self.on_generate_direct_text(append=False, auto_triggered=True)

    def on_generate_direct_text(self, append: bool = False, auto_triggered: bool = False):
        """Generates vector text and loads it directly into the rotary canvas."""
        text = self.txt_direct_text.text().strip()
        if not text:
            return

        orientation = 'circumferential' if self.combo_text_orientation.currentIndex() == 0 else 'axial'
        paths = RotarySlicingEngine.generate_vector_text(
            text=text,
            font_family=self.combo_font_family.currentText(),
            font_size_mm=self.spn_font_size.value(),
            bold=self.chk_font_bold.isChecked(),
            italic=self.chk_font_italic.isChecked(),
            letter_spacing_mm=self.spn_letter_spacing.value(),
            orientation=orientation,
            angle_deg=self.spn_text_start_angle.value(),
            diameter=self.spn_diameter.value(),
            repeat_count=self.spn_text_reps.value(),
            auto_fit_360=self.chk_text_autofit.isChecked(),
            axial_length=self.spn_workpiece_height.value()
        )

        if not paths:
            return

        self.active_generator = 'direct_text'

        if append and self.source_paths and not auto_triggered:
            self.source_paths.extend(paths)
        else:
            self.source_paths = paths

        self.apply_artwork_transforms()
        if not auto_triggered:
            self.tabs.setCurrentIndex(0)
            self.lbl_console_log.setText(f"Direct text generated: '{text}' ({len(paths)} vector contours).")

    # -------------------------------------------------------------------------
    # SCALE RULER GENERATION & REACTIVITY
    # -------------------------------------------------------------------------
    def _on_ruler_param_changed(self):
        if self.tabs.currentIndex() == 1:
            self.on_generate_scale_ruler(append=False, auto_triggered=True)

    def on_generate_scale_ruler(self, append: bool = False, auto_triggered: bool = False):
        """Generates editable engineering graduation ruler and applies to rotary canvas."""
        idx = self.combo_ruler_type.currentIndex()
        if idx == 0:
            ruler_type = 'degree'
            direction = 'circumferential'
            num_suffix = '°'
        elif idx == 1:
            ruler_type = 'metric'
            direction = 'circumferential'
            num_suffix = 'mm'
        else:
            ruler_type = 'metric'
            direction = 'axial'
            num_suffix = 'mm'

        side_map = {0: 'left', 1: 'right', 2: 'both'}
        side = side_map.get(self.combo_ruler_side.currentIndex(), 'left')

        paths = RotarySlicingEngine.generate_editable_ruler(
            ruler_type=ruler_type,
            diameter=self.spn_diameter.value(),
            minor_step=self.spn_ruler_minor_step.value(),
            medium_step=self.spn_ruler_medium_step.value(),
            major_step=self.spn_ruler_major_step.value(),
            minor_len=self.spn_ruler_minor_len.value(),
            medium_len=self.spn_ruler_medium_len.value(),
            major_len=self.spn_ruler_major_len.value(),
            axial_length=self.spn_workpiece_height.value(),
            tick_side=side,
            include_baseline=self.chk_ruler_baseline.isChecked(),
            include_numbers=self.chk_ruler_numbers.isChecked(),
            number_step=self.spn_ruler_num_step.value(),
            number_font_size=self.spn_ruler_font_sz.value(),
            number_suffix=num_suffix,
            direction=direction
        )

        if not paths:
            return

        self.active_generator = 'scale_ruler'

        if append and self.source_paths and not auto_triggered:
            self.source_paths.extend(paths)
        else:
            self.source_paths = paths

        self.apply_artwork_transforms()
        if not auto_triggered:
            self.tabs.setCurrentIndex(1)
            self.lbl_console_log.setText(f"Generated scale ruler ({len(paths)} vector paths).")

    # -------------------------------------------------------------------------
    # 4-WAY JOG KEYPAD & HARDWARE MOTION SLOTS
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # PROCEDURAL PIPE PATTERN SLOTS & 360° REACTIVITY
    # -------------------------------------------------------------------------
    def _on_pattern_param_changed(self):
        if hasattr(self, 'tabs') and self.tabs.currentWidget() == self.tab_patterns:
            self.on_generate_pipe_pattern(append=False, auto_triggered=True)

    def _on_pattern_hatch_toggled(self, checked: bool):
        if hasattr(self, 'chk_hatch_enable'):
            self.chk_hatch_enable.setChecked(checked)

    def on_generate_pipe_pattern(self, append: bool = False, auto_triggered: bool = False):
        """Generates procedural pipe pattern configured to 100% cover the cylinder circumference with odd/even hatch support."""
        d = self.spn_diameter.value()
        length = self.spn_pattern_length.value() if hasattr(self, 'spn_pattern_length') else self.spn_workpiece_height.value()
        repeats = self.spn_pattern_repeats.value() if hasattr(self, 'spn_pattern_repeats') else 24
        axial_reps = self.spn_pattern_axial_repeats.value() if hasattr(self, 'spn_pattern_axial_repeats') else 0
        inset = self.spn_pattern_inset.value() if hasattr(self, 'spn_pattern_inset') else 0.0
        param_val = self.spn_pattern_param.value() if hasattr(self, 'spn_pattern_param') else 1.0

        c = math.pi * max(0.1, d)
        step = c / max(1, repeats)
        if hasattr(self, 'lbl_pattern_circ_info'):
            self.lbl_pattern_circ_info.setText(f"Circumference: C = {c:.2f} mm | Repeat Step: {step:.2f} mm (100% 360° Covered)")

        # Pattern Hatch Style Resolution
        style_map = {
            0: 'odd_even',
            1: 'even_odd',
            2: 'solid_alternate',
            3: 'cross_angle',
            4: 'herringbone',
            5: 'tri_angle',
            6: 'concentric',
            7: 'cell_cross',
            8: 'all',
            9: 'none'
        }
        hatch_mode_idx = self.combo_pattern_hatch_style.currentIndex() if hasattr(self, 'combo_pattern_hatch_style') else 0
        is_pattern_hatch_on = self.chk_pattern_hatch.isChecked() if hasattr(self, 'chk_pattern_hatch') else True
        hatch_style = style_map.get(hatch_mode_idx, 'odd_even') if is_pattern_hatch_on else 'none'

        pitch = self.spn_pattern_hatch_pitch.value() if hasattr(self, 'spn_pattern_hatch_pitch') else 0.050
        angle = self.spn_pattern_hatch_angle.value() if hasattr(self, 'spn_pattern_hatch_angle') else 0.0
        mark_c = self.chk_pattern_mark_contour.isChecked() if hasattr(self, 'chk_pattern_mark_contour') else True

        unidir = (hasattr(self, 'combo_pattern_hatch_dir') and self.combo_pattern_hatch_dir.currentIndex() == 1)

        # Smart Station-Aligned Slicing: automatically aligns split size to pattern repeat step
        # so 45° diagonal hatch lines fall completely inside cells and are NEVER sliced in half!
        if hasattr(self, 'chk_pattern_align_slices') and self.chk_pattern_align_slices.isChecked():
            if hasattr(self, 'spn_split_size'):
                self.spn_split_size.blockSignals(True)
                self.spn_split_size.setValue(round(step, 3))
                self.spn_split_size.blockSignals(False)
            if hasattr(self, 'config'):
                self.config.pattern_repeats = repeats
                self.config.align_to_repeats = True

        pat_idx = self.combo_pipe_pattern.currentIndex() if hasattr(self, 'combo_pipe_pattern') else 0
        paths = []

        if pat_idx == 0:
            # Checkerboard / Chess Tile Grid (Odd/Even Hatchable)
            paths = RotarySlicingEngine.generate_checkerboard(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 1:
            # Diamond Knurl / Facets (Odd/Even Hatchable)
            paths = RotarySlicingEngine.generate_diamond_knurl(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 2:
            # Hexagonal Honeycomb Lattice (Odd/Even Hatchable)
            paths = RotarySlicingEngine.generate_honeycomb(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 3:
            # Brick / Subway Tile Mesh (Odd/Even Hatchable)
            paths = RotarySlicingEngine.generate_brick_subway(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 4:
            # Fish Scale / Moroccan Scallop (Odd/Even Hatchable)
            paths = RotarySlicingEngine.generate_fish_scale(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 5:
            # Basketweave / Carbon Fiber Twill
            paths = RotarySlicingEngine.generate_basketweave(
                diameter=d, length=length, num_repeats=repeats, axial_repeats=axial_reps,
                hatch_style=hatch_style, pitch_mm=pitch, angle_deg=angle, mark_contour=mark_c, inset_mm=inset
            )
        elif pat_idx == 6:
            # Helical Spiral Flutes
            paths = RotarySlicingEngine.generate_helical_spiral(diameter=d, length=length, num_starts=repeats, num_turns=param_val)
        elif pat_idx == 7:
            # Herringbone / Chevron
            paths = RotarySlicingEngine.generate_chevron_herringbone(diameter=d, length=length, num_repeats=repeats)
        elif pat_idx == 8:
            # Greek Key
            paths = RotarySlicingEngine.generate_greek_key(diameter=d, length=length, num_repeats=repeats)
        elif pat_idx == 9:
            # Harmonic Sine Wave Rings
            paths = RotarySlicingEngine.generate_sine_waves(diameter=d, length=length, num_waves=repeats, cycles=int(param_val))
        elif pat_idx == 10:
            # Axial Flutes
            paths = RotarySlicingEngine.generate_axial_flutes(diameter=d, length=length, num_flutes=repeats)
        elif pat_idx == 11:
            # Precision 360° Engineering Scale
            paths = RotarySlicingEngine.generate_cylindrical_ruler(diameter=d, length=length, tick_spacing_deg=360.0 / max(1, repeats))
        elif pat_idx == 12:
            # Split Overlap Calibration Stripes
            paths = RotarySlicingEngine.generate_calibration_stripes(width=length, height=c, stripe_width=c / max(1, repeats))

        if not paths:
            return

        self.active_generator = 'pipe_pattern'

        if append and self.source_paths and not auto_triggered:
            self.source_paths.extend(paths)
        else:
            self.source_paths = paths

        self.apply_artwork_transforms()
        if not auto_triggered:
            self.tabs.setCurrentWidget(self.tab_patterns)
            pat_name = self.combo_pipe_pattern.currentText()
            self.lbl_console_log.setText(f"Generated 360° pattern: {pat_name} ({len(paths)} vectors covering {c:.1f}mm circumference).")

    def tile_current_artwork_360(self):
        """Tiles/repeats the currently loaded artwork evenly around 360° pipe circumference."""
        if not self.source_paths:
            self.lbl_console_log.setText("No artwork loaded to tile.")
            return
        d = self.spn_diameter.value()
        repeats = self.spn_art_tile_count.value() if hasattr(self, 'spn_art_tile_count') else 4
        c = math.pi * max(0.1, d)

        tiled = RotarySlicingEngine.tile_paths_around_circumference(
            paths=self.source_paths,
            diameter=d,
            num_repeats=repeats,
            scale_to_fit=True
        )
        self.source_paths = tiled
        self.apply_artwork_transforms()
        self.lbl_console_log.setText(f"Tiled artwork {repeats} times around circumference ({c:.2f} mm).")

    def _on_jog_arrow(self, direction: str):
        """Executes 4-way jog step: UP/DOWN for rotary axis, LEFT/RIGHT for axial X."""
        step_val = self.spn_jog_step.value()
        cfg = self.update_config_from_ui()

        if direction in ('UP', 'DOWN'):
            deg = step_val if direction == 'UP' else -step_val
            self.jog_relative_degrees(deg)
        elif direction in ('LEFT', 'RIGHT'):
            dist_mm = step_val if direction == 'RIGHT' else -step_val
            self.current_axial_x_mm += dist_mm
            speed = max(100, int(cfg.max_speed))
            pulses_x = int(dist_mm * (cfg.pulses_per_mm or 80.0))
            if self.stepper_controller and hasattr(self.stepper_controller, 'move_axis_pulses'):
                self.stepper_controller.move_axis_pulses('X', pulses_x, speed)
            self._update_position_label()

    def _on_axis_step_combo_changed(self, text: str):
        try:
            val = float(text)
            self.spn_jog_step.setValue(val)
        except ValueError:
            pass

    def _update_position_label(self):
        tot_pulses = int(self.current_rotary_angle_deg * (self.config.total_pulses_360 / 360.0))
        self.lbl_current_angle.setText(
            f"Position: X: {self.current_axial_x_mm:.3f} mm | Z: {self.current_rotary_angle_deg:.3f}° ({tot_pulses:,} pulses)"
        )

    def jog_relative_degrees(self, deg: float):
        """Jogs rotary axis by relative degrees."""
        cfg = self.update_config_from_ui()
        pulses = int(round(deg * (cfg.total_pulses_360 / 360.0)))
        if cfg.reverse_direction:
            pulses = -pulses

        self.current_rotary_angle_deg = (self.current_rotary_angle_deg + deg) % 360.0
        self.canvas.sim_cylinder_angle_deg = self.current_rotary_angle_deg
        self.canvas.update()
        self._update_position_label()

        speed = max(100, int(cfg.max_speed))
        axis = str(cfg.stepper_axis or 'Z').upper()

        if self.stepper_controller and hasattr(self.stepper_controller, 'move_axis_pulses'):
            self.stepper_controller.move_axis_pulses(axis, pulses, speed)
        self.lbl_console_log.setText(f"Jogged {deg:+.1f}° ({pulses:+} pulses on {axis}-Axis)")

    def set_zero_position(self):
        """Zeroes position registers."""
        self.current_rotary_angle_deg = 0.0
        self.current_axial_x_mm = 0.0
        self.canvas.sim_cylinder_angle_deg = 0.0
        self.canvas.update()
        self._update_position_label()

        if self.stepper_controller and hasattr(self.stepper_controller, 'set_origin'):
            self.stepper_controller.set_origin(self.config.stepper_axis or 'Z')
        self.lbl_console_log.setText("Hardware Origin and Software Angle synchronized to 0.0°")

    def go_to_zero_position(self):
        """Moves back to 0.0° origin."""
        if abs(self.current_rotary_angle_deg) > 1e-4:
            delta = -self.current_rotary_angle_deg
            self.jog_relative_degrees(delta)
            self.current_rotary_angle_deg = 0.0
            self._update_position_label()

    def test_full_revolution(self):
        """Performs a smooth 360-degree calibration spin."""
        cfg = self.update_config_from_ui()
        p360 = int(round(cfg.total_pulses_360))
        self.lbl_console_log.setText(f"Testing 360° Full Revolution ({p360:,} pulses)...")
        self.jog_relative_degrees(360.0)

    def on_calibrate_360(self):
        """
        Interactive 360° Rotary Calibration Wizard (EZCad Style):
        Launches dedicated modal wizard allowing visual test spins, observed turn entry (e.g. 13 turns),
        exact/standard microstep calculation, and permanent saving to config.ini.
        """
        wiz = Calibrate360Wizard(self)
        wiz.exec()

    # -------------------------------------------------------------------------
    # CANVAS & 3D CONTROLS
    # -------------------------------------------------------------------------
    def _on_toggle_auto_spin(self):
        spinning = self.canvas.toggle_auto_spin()
        self.btn_auto_spin.setText("⏹ Stop Spin" if spinning else "▶ Auto-Spin")
        self.btn_auto_spin.setChecked(spinning)

    def _on_ring_inside_toggled(self, checked: bool):
        self.canvas.set_ring_inside_mode(checked)
        self.update_config_and_recalculate()
        self.lbl_console_log.setText("Ring Inside mode " + ("ACTIVATED (Bore Marking)" if checked else "Deactivated"))

    # -------------------------------------------------------------------------
    # PRESETS & ARTWORK MANAGEMENT
    # -------------------------------------------------------------------------
    def load_preset_pattern(self, name: str, auto_triggered: bool = False):
        """Generates procedural test pattern and loads into canvas."""
        d = self.spn_diameter.value()
        paths: List[List[Tuple[float, float]]] = []

        if name == "Cylindrical Ruler (360°)":
            paths = RotarySlicingEngine.generate_editable_ruler(
                diameter=d,
                minor_step=1.0,
                medium_step=5.0,
                major_step=10.0,
                minor_len=2.5,
                medium_len=4.5,
                major_len=7.0,
                include_baseline=True,
                include_numbers=True
            )
        elif name == "Vernier Degree Scale":
            paths = RotarySlicingEngine.generate_editable_ruler(
                diameter=d,
                minor_step=0.5,
                medium_step=2.5,
                major_step=5.0,
                minor_len=3.0,
                medium_len=6.0,
                major_len=9.0,
                include_baseline=True,
                include_numbers=True
            )
        elif name == "Diamond Grid Wrap":
            c = math.pi * d
            w = 50.0
            step = 10.0
            for x in range(0, int(w) + 1, int(step)):
                paths.append([(float(x), 0.0), (float(x + 10), c / 2.0), (float(x), c)])
                paths.append([(float(x + 10), 0.0), (float(x), c / 2.0), (float(x + 10), c)])
        elif name == "Calibration Stripes (Split Overlap)":
            c = math.pi * d
            split_s = self.spn_split_size.value()
            for y_mm in [i * split_s for i in range(min(50, int(c / split_s) + 1))]:
                paths.append([(5.0, y_mm), (35.0, y_mm)])
        elif name == "Load External DXF / SVG...":
            if not auto_triggered:
                self.load_external_file()
            return

        self.set_artwork(paths, generator='preset')

    def on_load_pattern_clicked(self):
        pattern_name = self.combo_presets.currentText()
        self.load_preset_pattern(pattern_name)

    def load_external_file(self):
        """Loads external DXF or SVG vector file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Vector CAD File", "", "Vector CAD Files (*.svg *.dxf);;SVG Files (*.svg);;DXF Files (*.dxf);;All Files (*.*)"
        )
        if not file_path:
            return

        paths = []
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.dxf':
            try:
                import ezdxf
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()
                for entity in msp:
                    dxftype = entity.dxftype()
                    if dxftype == 'LINE':
                        p1 = entity.dxf.start
                        p2 = entity.dxf.end
                        paths.append([(float(p1.x), float(p1.y)), (float(p2.x), float(p2.y))])
                    elif dxftype == 'LWPOLYLINE':
                        pts = [(float(p[0]), float(p[1])) for p in entity.get_points('xy')]
                        if pts:
                            paths.append(pts)
                    elif dxftype == 'POLYLINE':
                        pts = [(float(p.dxf.location.x), float(p.dxf.location.y)) for p in entity.vertices]
                        if pts:
                            paths.append(pts)
                    elif dxftype == 'CIRCLE':
                        cx, cy, r = float(entity.dxf.center.x), float(entity.dxf.center.y), float(entity.dxf.radius)
                        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 361, 10)]
                        paths.append(pts)
                    elif dxftype == 'ARC':
                        cx, cy, r = float(entity.dxf.center.x), float(entity.dxf.center.y), float(entity.dxf.radius)
                        sa, ea = float(entity.dxf.start_angle), float(entity.dxf.end_angle)
                        if ea < sa:
                            ea += 360.0
                        steps = max(8, int((ea - sa) / 10.0))
                        pts = [(cx + r * math.cos(math.radians(sa + (ea - sa) * i / steps)),
                                cy + r * math.sin(math.radians(sa + (ea - sa) * i / steps))) for i in range(steps + 1)]
                        paths.append(pts)
            except Exception as e:
                QMessageBox.warning(self, "DXF Import Error", f"Failed to parse DXF: {e}")
                return
        elif ext == '.svg':
            try:
                from core.svg_parser import SVGParser
                parser = SVGParser()
                paths = parser.parse_to_polygons(file_path)
            except Exception as e:
                QMessageBox.warning(self, "SVG Import Error", f"Failed to parse SVG:\n{e}")
                return
        else:
            QMessageBox.warning(self, "Unsupported Format", f"Format '{ext}' is not supported. Please select .svg or .dxf.")
            return

        if paths:
            # Measure original imported CAD size in mm
            min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(paths)
            w_orig = max(0.01, max_x - min_x)
            h_orig = max(0.01, max_y - min_y)

            wp_len = self.spn_workpiece_height.value()
            c = getattr(self.config, 'circumference', math.pi * self.spn_diameter.value())
            max_field = getattr(self.config, 'galvo_field_size', 100.0)

            # Check if CAD file is oversized (e.g. web SVG with 1000px viewBox, or > 120mm on small part)
            is_oversized = (w_orig > max(110.0, wp_len)) or (h_orig > max(110.0, c))

            if is_oversized:
                max_allowed_w = min(wp_len * 0.8, max_field * 0.8)
                max_allowed_h = min(c * 0.8, max_field * 0.8)
                initial_scale = min(max_allowed_w / w_orig, max_allowed_h / h_orig) * 100.0
                initial_scale = max(0.1, min(100.0, initial_scale))
            else:
                initial_scale = 100.0  # Native 1:1 true CAD millimeter size

            self.set_artwork(paths, generator='cad_vector', default_scale=initial_scale)
            self.center_artwork_on_cylinder()

            if hasattr(self, 'chk_auto_fit_diameter') and self.chk_auto_fit_diameter.isChecked():
                self.fit_artwork_to_360()

            w_cur = w_orig * (initial_scale / 100.0)
            h_cur = h_orig * (initial_scale / 100.0)

            msg = (
                f"Successfully loaded {len(paths)} vector paths from:\n{os.path.basename(file_path)}\n\n"
                f"• Dimensions: {w_cur:.2f} mm (Width) x {h_cur:.2f} mm (Height)\n"
                f"• Scale: {initial_scale:.1f}%\n\n"
                f"The artwork has been centered on the cylinder.\n"
                f"You can adjust the exact Width and Height (mm) in Tab 3."
            )
            self.lbl_console_log.setText(f"Loaded external {ext.upper()}: {os.path.basename(file_path)} ({w_cur:.1f}x{h_cur:.1f} mm)")
            QMessageBox.information(
                self, "Vector Import Successful", msg
            )
        else:
            QMessageBox.warning(
                self, "No Vector Paths Found",
                f"No vector path outlines were found in '{os.path.basename(file_path)}'.\n\n"
                f"If this file contains embedded raster images (like PNG or JPEG) instead of vector outlines, "
                f"please trace/vectorize them to vector paths first."
            )

    def set_artwork(self, paths: List[List[Tuple[float, float]]], generator: str = 'cad_vector', default_scale: float = 100.0):
        """Sets new source artwork and normalizes coordinate bounds."""
        self.source_paths = paths
        self.active_generator = generator
        if paths:
            min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(paths)
            self.orig_art_w = max(1e-4, max_x - min_x)
            self.orig_art_h = max(1e-4, max_y - min_y)
        else:
            self.orig_art_w = 0.0
            self.orig_art_h = 0.0

        self.spn_offset_x.blockSignals(True)
        self.spn_offset_y.blockSignals(True)
        self.spn_scale_x.blockSignals(True)
        self.spn_scale_y.blockSignals(True)

        self.spn_offset_x.setValue(0.0)
        self.spn_offset_y.setValue(0.0)
        self.spn_scale_x.setValue(default_scale)
        self.spn_scale_y.setValue(default_scale)
        if hasattr(self, 'spn_art_rotation'):
            self.spn_art_rotation.blockSignals(True)
            self.spn_art_rotation.setValue(0.0)
            self.spn_art_rotation.blockSignals(False)

        self.spn_offset_x.blockSignals(False)
        self.spn_offset_y.blockSignals(False)
        self.spn_scale_x.blockSignals(False)
        self.spn_scale_y.blockSignals(False)

        self.apply_artwork_transforms()

    # -------------------------------------------------------------------------
    # ARTWORK TRANSFORMATION ENGINE
    # -------------------------------------------------------------------------
    def apply_artwork_transforms(self):
        """Applies offset and scale transformations to source artwork."""
        if not self.source_paths:
            self.raw_paths = []
            self.lbl_art_size.setText("Size: W 0.00 x H 0.00 mm")
            if hasattr(self, 'spn_art_width') and hasattr(self, 'spn_art_height'):
                self.spn_art_width.blockSignals(True)
                self.spn_art_height.blockSignals(True)
                self.spn_art_width.setValue(0.0)
                self.spn_art_height.setValue(0.0)
                self.spn_art_width.blockSignals(False)
                self.spn_art_height.blockSignals(False)
            self.update_config_and_recalculate()
            return

        off_x = self.spn_offset_x.value()
        off_y = self.spn_offset_y.value()
        scale_x = self.spn_scale_x.value() / 100.0
        scale_y = self.spn_scale_y.value() / 100.0
        rot_deg = self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0
        mx = -1.0 if getattr(self, 'mirror_x', False) else 1.0
        my = -1.0 if getattr(self, 'mirror_y', False) else 1.0
        rad = math.radians(rot_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        self.orig_art_w = max(1e-4, max_x - min_x)
        self.orig_art_h = max(1e-4, max_y - min_y)

        transformed = []
        for poly in self.source_paths:
            t_poly = []
            for pt in poly:
                sx = (pt[0] - center_x) * scale_x * mx
                sy = (pt[1] - center_y) * scale_y * my
                rx = sx * cos_a - sy * sin_a
                ry = sx * sin_a + sy * cos_a
                nx = center_x + rx + off_x
                ny = center_y + ry + off_y
                t_poly.append((nx, ny))
            transformed.append(t_poly)

        self.preview_contour_paths = transformed

        # Measure base contour dimensions & check orientation
        bx0, by0, bx1, by1 = self.slicing_engine.get_artwork_bounds(transformed)
        w = max(0.0, bx1 - bx0)
        h = max(0.0, by1 - by0)
        is_vert = (h > w)
        self.lbl_art_size.setText(f"Size: W {w:.2f} x H {h:.2f} mm ({'Vertical' if is_vert else 'Horizontal'})")

        # Dynamically update Orientation Toggle Buttons based on current orientation
        btn_text = "🔄 Rotate to Horizontal (90°)" if is_vert else "🔄 Rotate to Vertical (90°)"
        btn_tip = "Artwork is currently VERTICAL (H > W). Click to rotate 90° to HORIZONTAL." if is_vert else "Artwork is currently HORIZONTAL (W >= H). Click to rotate 90° to VERTICAL."
        btn_style = (
            "background-color: #0d3b66; color: #00d2ff; font-weight: bold; font-size: 9pt; padding: 6px 12px; border: 1px solid #00d2ff; border-radius: 4px;"
            if is_vert else
            "background-color: #004d40; color: #00ff66; font-weight: bold; font-size: 9pt; padding: 6px 12px; border: 1px solid #00ff66; border-radius: 4px;"
        )
        if hasattr(self, 'btn_toggle_orientation'):
            self.btn_toggle_orientation.setText(btn_text)
            self.btn_toggle_orientation.setToolTip(btn_tip)
            self.btn_toggle_orientation.setStyleSheet(btn_style)

        if hasattr(self, 'btn_canvas_toggle_rot'):
            self.btn_canvas_toggle_rot.setText(btn_text)
            self.btn_canvas_toggle_rot.setToolTip(btn_tip)
            self.btn_canvas_toggle_rot.setStyleSheet(btn_style)

        if hasattr(self, 'canvas') and hasattr(self.canvas, 'btn_ovl_rotate'):
            self.canvas.btn_ovl_rotate.setText("🔄 Rotate to Horiz" if is_vert else "🔄 Rotate to Vert")
            self.canvas.btn_ovl_rotate.setToolTip(btn_tip)

        if hasattr(self, 'spn_art_width') and hasattr(self, 'spn_art_height'):
            # Only update spinboxes if the user is not actively typing in them
            is_w_focus = self.spn_art_width.hasFocus() or (self.spn_art_width.lineEdit() and self.spn_art_width.lineEdit().hasFocus())
            is_h_focus = self.spn_art_height.hasFocus() or (self.spn_art_height.lineEdit() and self.spn_art_height.lineEdit().hasFocus())
            if not is_w_focus:
                self.spn_art_width.blockSignals(True)
                self.spn_art_width.setValue(w)
                self.spn_art_width.blockSignals(False)
            if not is_h_focus:
                self.spn_art_height.blockSignals(True)
                self.spn_art_height.setValue(h)
                self.spn_art_height.blockSignals(False)

        # Check if Hatch Infill is enabled
        skip_global_hatch = (
            getattr(self, 'active_generator', '') == 'pipe_pattern' and
            hasattr(self, 'combo_pattern_hatch_style') and
            "Outlines Only" not in self.combo_pattern_hatch_style.currentText()
        )
        if not skip_global_hatch and hasattr(self, 'chk_hatch_enable') and self.chk_hatch_enable.isChecked():
            pitch = self.spn_hatch_pitch.value()
            angle = self.spn_hatch_angle.value()
            contour = self.chk_hatch_mark_contour.isChecked()
            contour_first = (self.combo_hatch_order.currentIndex() == 0)
            edge_off = self.spn_hatch_edge_offset.value()

            h_type_idx = self.combo_hatch_type.currentIndex() if hasattr(self, 'combo_hatch_type') else 0
            h_type_map = {0: 'line', 1: 'cross', 2: 'cross', 3: 'triple', 4: 'concentric'}
            h_type = h_type_map.get(h_type_idx, 'line')
            cross = (h_type_idx in (1, 2)) or self.chk_hatch_cross.isChecked()
            cross_offset = self.spn_hatch_cross_offset.value() if hasattr(self, 'spn_hatch_cross_offset') else 90.0
            unidir = (hasattr(self, 'combo_hatch_direction') and self.combo_hatch_direction.currentIndex() == 1)

            hatched_paths, count = self.slicing_engine.generate_hatch_fill(
                paths=transformed,
                pitch_mm=pitch,
                angle_deg=angle,
                cross_hatch=cross,
                mark_contour=contour,
                contour_first=contour_first,
                edge_offset_mm=edge_off,
                unidirectional=unidir,
                cross_angle_offset=cross_offset,
                triple_pass=(h_type == 'triple'),
                hatch_type=h_type
            )
            self.raw_paths = hatched_paths
            tot_len = sum(
                math.hypot(p[i+1][0] - p[i][0], p[i+1][1] - p[i][1])
                for p in hatched_paths for i in range(len(p)-1)
            )
            if hasattr(self, 'lbl_hatch_stats'):
                self.lbl_hatch_stats.setText(f"Hatch Active: {count} infill lines ({tot_len/1000.0:.2f} m total path)")
                self.lbl_hatch_stats.setStyleSheet("color: #00ff66; font-weight: bold; font-size: 8pt;")
        else:
            self.raw_paths = transformed
            if hasattr(self, 'lbl_hatch_stats'):
                self.lbl_hatch_stats.setText("Status: Hatch Disabled (Contour Outlines Only)")
                self.lbl_hatch_stats.setStyleSheet("color: #a0aec0; font-size: 8pt;")

        self.update_config_and_recalculate()

    def _on_mirror_x_toggled(self, checked: bool):
        self.mirror_x = checked
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'btn_ovl_flip_x'):
            self.canvas.btn_ovl_flip_x.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;" if checked else "")
        self.apply_artwork_transforms()

    def _on_mirror_y_toggled(self, checked: bool):
        self.mirror_y = checked
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'btn_ovl_flip_y'):
            self.canvas.btn_ovl_flip_y.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;" if checked else "")
        self.apply_artwork_transforms()

    def toggle_mirror_x(self):
        self.mirror_x = not getattr(self, 'mirror_x', False)
        if hasattr(self, 'chk_mirror_x'):
            self.chk_mirror_x.blockSignals(True)
            self.chk_mirror_x.setChecked(self.mirror_x)
            self.chk_mirror_x.blockSignals(False)
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'btn_ovl_flip_x'):
            self.canvas.btn_ovl_flip_x.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;" if self.mirror_x else "")
        self.apply_artwork_transforms()
        self.lbl_console_log.setText(f"Mirror Horizontal (Flip X): {'ON' if self.mirror_x else 'OFF'}")

    def toggle_mirror_y(self):
        self.mirror_y = not getattr(self, 'mirror_y', False)
        if hasattr(self, 'chk_mirror_y'):
            self.chk_mirror_y.blockSignals(True)
            self.chk_mirror_y.setChecked(self.mirror_y)
            self.chk_mirror_y.blockSignals(False)
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'btn_ovl_flip_y'):
            self.canvas.btn_ovl_flip_y.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;" if self.mirror_y else "")
        self.apply_artwork_transforms()
        self.lbl_console_log.setText(f"Mirror Vertical (Flip Y): {'ON' if self.mirror_y else 'OFF'}")

    def _on_show_slice_partitions_toggled(self, checked: bool):
        if hasattr(self, 'canvas'):
            self.canvas.show_slice_partitions = checked
            if hasattr(self.canvas, 'btn_ovl_slices'):
                if checked:
                    self.canvas.btn_ovl_slices.setText("👁 Slice Lines: ON")
                    self.canvas.btn_ovl_slices.setStyleSheet("background-color: #007a52; color: #ffffff; font-weight: bold;")
                else:
                    self.canvas.btn_ovl_slices.setText("👁 Slice Lines: OFF")
                    self.canvas.btn_ovl_slices.setStyleSheet("")
            self.canvas.update()

    def interactive_rotate_artwork(self, rot_deg: float):
        """Interactively rotates artwork during rotation handle drag without heavy reslicing."""
        if not self.source_paths:
            return
        if hasattr(self, 'spn_art_rotation'):
            self.spn_art_rotation.blockSignals(True)
            self.spn_art_rotation.setValue(rot_deg)
            self.spn_art_rotation.blockSignals(False)

        scale_x = self.spn_scale_x.value() / 100.0
        scale_y = self.spn_scale_y.value() / 100.0
        off_x = self.spn_offset_x.value()
        off_y = self.spn_offset_y.value()
        mx = -1.0 if getattr(self, 'mirror_x', False) else 1.0
        my = -1.0 if getattr(self, 'mirror_y', False) else 1.0

        rad = math.radians(rot_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        transformed = []
        for poly in self.source_paths:
            t_poly = []
            for pt in poly:
                sx = (pt[0] - center_x) * scale_x * mx
                sy = (pt[1] - center_y) * scale_y * my
                rx = sx * cos_a - sy * sin_a
                ry = sx * sin_a + sy * cos_a
                nx = center_x + rx + off_x
                ny = center_y + ry + off_y
                t_poly.append((nx, ny))
            transformed.append(t_poly)

        self.raw_paths = transformed
        self.preview_contour_paths = transformed
        self.canvas.raw_paths = transformed
        self.canvas.update()

    def interactive_resize_artwork(
        self,
        handle_idx: int,
        delta_x_mm: float,
        delta_y_mm: float,
        start_scale_x: float,
        start_scale_y: float,
        start_off_x: float,
        start_off_y: float,
        start_w_mm: float,
        start_h_mm: float,
        shift_held: bool = False
    ):
        """
        Interactive on-canvas bounding box resize handler.
        - Handle 7 (Right) & Handle 6 (Left): Adjust ONLY visual width.
          Preserves visual height unchanged regardless of rotation.
        - Handle 4 (Top) & Handle 5 (Bottom): Adjust ONLY visual height.
          Preserves visual width unchanged regardless of rotation.
        - Handles 0, 1, 2, 3 (Corners): Adjust both width and height.
          Maintains aspect ratio if chk_lock_aspect is checked or Shift is held.
        """
        if not self.source_paths or start_w_mm <= 0.01 or start_h_mm <= 0.01:
            return

        lock_aspect = (hasattr(self, 'chk_lock_aspect') and self.chk_lock_aspect.isChecked()) or shift_held

        rot = abs(round(self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0)) % 180
        is_swapped = (45 < rot < 135)

        new_scale_x = start_scale_x
        new_scale_y = start_scale_y
        new_off_x = start_off_x
        new_off_y = start_off_y

        # Handle indices: TL=0, TR=1, BL=2, BR=3, T=4, B=5, L=6, R=7
        if handle_idx == 7:  # Right edge handle - visual width ONLY
            new_w = max(0.5, start_w_mm + delta_x_mm)
            factor_w = new_w / start_w_mm
            new_off_x = start_off_x + (delta_x_mm / 2.0)
            if is_swapped:
                new_scale_y = max(1.0, start_scale_y * factor_w)
            else:
                new_scale_x = max(1.0, start_scale_x * factor_w)
        elif handle_idx == 6:  # Left edge handle - visual width ONLY
            new_w = max(0.5, start_w_mm - delta_x_mm)
            factor_w = new_w / start_w_mm
            new_off_x = start_off_x + (delta_x_mm / 2.0)
            if is_swapped:
                new_scale_y = max(1.0, start_scale_y * factor_w)
            else:
                new_scale_x = max(1.0, start_scale_x * factor_w)
        elif handle_idx == 5:  # Bottom edge handle - visual height ONLY
            new_h = max(0.5, start_h_mm + delta_y_mm)
            factor_h = new_h / start_h_mm
            new_off_y = start_off_y + (delta_y_mm / 2.0)
            if is_swapped:
                new_scale_x = max(1.0, start_scale_x * factor_h)
            else:
                new_scale_y = max(1.0, start_scale_y * factor_h)
        elif handle_idx == 4:  # Top edge handle - visual height ONLY
            new_h = max(0.5, start_h_mm - delta_y_mm)
            factor_h = new_h / start_h_mm
            new_off_y = start_off_y + (delta_y_mm / 2.0)
            if is_swapped:
                new_scale_x = max(1.0, start_scale_x * factor_h)
            else:
                new_scale_y = max(1.0, start_scale_y * factor_h)
        elif handle_idx in (0, 1, 2, 3):  # Corner handles - 2D / proportional resize
            dx = delta_x_mm if handle_idx in (1, 3) else -delta_x_mm
            dy = delta_y_mm if handle_idx in (2, 3) else -delta_y_mm
            new_w = max(0.5, start_w_mm + dx)
            new_h = max(0.5, start_h_mm + dy)
            factor_w = new_w / start_w_mm
            factor_h = new_h / start_h_mm

            if lock_aspect:
                uniform_factor = max(0.05, (factor_w + factor_h) / 2.0)
                factor_w = uniform_factor
                factor_h = uniform_factor

            if is_swapped:
                new_scale_y = max(1.0, start_scale_y * factor_w)
                new_scale_x = max(1.0, start_scale_x * factor_h)
            else:
                new_scale_x = max(1.0, start_scale_x * factor_w)
                new_scale_y = max(1.0, start_scale_y * factor_h)

            new_off_x = start_off_x + (delta_x_mm / 2.0)
            new_off_y = start_off_y + (delta_y_mm / 2.0)

        self.spn_scale_x.blockSignals(True)
        self.spn_scale_y.blockSignals(True)
        self.spn_offset_x.blockSignals(True)
        self.spn_offset_y.blockSignals(True)
        self.spn_scale_x.setValue(round(new_scale_x, 2))
        self.spn_scale_y.setValue(round(new_scale_y, 2))
        self.spn_offset_x.setValue(round(new_off_x, 2))
        self.spn_offset_y.setValue(round(new_off_y, 2))
        self.spn_scale_x.blockSignals(False)
        self.spn_scale_y.blockSignals(False)
        self.spn_offset_x.blockSignals(False)
        self.spn_offset_y.blockSignals(False)

        rot_deg = self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0
        rad = math.radians(rot_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        sc_x = new_scale_x / 100.0
        sc_y = new_scale_y / 100.0
        mx = -1.0 if getattr(self, 'mirror_x', False) else 1.0
        my = -1.0 if getattr(self, 'mirror_y', False) else 1.0

        min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        transformed = []
        for poly in self.source_paths:
            t_poly = []
            for pt in poly:
                sx = (pt[0] - center_x) * sc_x * mx
                sy = (pt[1] - center_y) * sc_y * my
                rx = sx * cos_a - sy * sin_a
                ry = sx * sin_a + sy * cos_a
                nx = center_x + rx + new_off_x
                ny = center_y + ry + new_off_y
                t_poly.append((nx, ny))
            transformed.append(t_poly)

        self.raw_paths = transformed
        self.preview_contour_paths = transformed
        self.canvas.raw_paths = transformed
        self.canvas.update()

    def interactive_move_artwork(self, off_x: float, off_y: float):
        """Interactively moves artwork during mouse drag without heavy reslicing."""
        if not self.source_paths:
            return
        self.spn_offset_x.blockSignals(True)
        self.spn_offset_y.blockSignals(True)
        self.spn_offset_x.setValue(off_x)
        self.spn_offset_y.setValue(off_y)
        self.spn_offset_x.blockSignals(False)
        self.spn_offset_y.blockSignals(False)

        scale_x = self.spn_scale_x.value() / 100.0
        scale_y = self.spn_scale_y.value() / 100.0
        rot_deg = self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0
        mx = -1.0 if getattr(self, 'mirror_x', False) else 1.0
        my = -1.0 if getattr(self, 'mirror_y', False) else 1.0
        rad = math.radians(rot_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        transformed = []
        for poly in self.source_paths:
            t_poly = []
            for pt in poly:
                sx = (pt[0] - center_x) * scale_x * mx
                sy = (pt[1] - center_y) * scale_y * my
                rx = sx * cos_a - sy * sin_a
                ry = sx * sin_a + sy * cos_a
                nx = center_x + rx + off_x
                ny = center_y + ry + off_y
                t_poly.append((nx, ny))
            transformed.append(t_poly)

        self.raw_paths = transformed
        self.preview_contour_paths = transformed
        self.canvas.raw_paths = transformed
        self.canvas.update()

    def toggle_artwork_orientation(self):
        """
        Rotates artwork 90° to toggle orientation between Horizontal and Vertical.
        If artwork is currently Vertical (H > W), rotates to Horizontal.
        If artwork is currently Horizontal (W >= H), rotates to Vertical.
        """
        if not self.source_paths:
            self.lbl_console_log.setText("No artwork loaded to rotate.")
            return

        cur_rot = self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0
        new_rot = (cur_rot + 90.0) % 360.0

        if hasattr(self, 'spn_art_rotation'):
            self.spn_art_rotation.setValue(new_rot)
        else:
            self.apply_artwork_transforms()

        if self.raw_paths:
            bx0, by0, bx1, by1 = self.slicing_engine.get_artwork_bounds(self.raw_paths)
            w = bx1 - bx0
            h = by1 - by0
            orient = "Horizontal (Axial)" if w >= h else "Vertical (Circumferential)"
            self.lbl_console_log.setText(f"Rotated artwork 90° -> {orient} (W: {w:.1f} x H: {h:.1f} mm, Angle: {new_rot:.0f}°)")

    def rotate_artwork_by(self, delta_deg: float):
        """Rotates artwork by an angular increment in degrees (e.g. +90°, -90°)."""
        if not self.source_paths:
            return
        cur_rot = self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0
        new_rot = (cur_rot + delta_deg) % 360.0
        if hasattr(self, 'spn_art_rotation'):
            self.spn_art_rotation.setValue(new_rot)

    def _on_hatch_param_changed(self):
        """Re-applies artwork transforms and updates rotary hatch infill."""
        if hasattr(self, 'chk_art_hatch_quick') and hasattr(self, 'chk_hatch_enable'):
            self.chk_art_hatch_quick.blockSignals(True)
            self.chk_art_hatch_quick.setChecked(self.chk_hatch_enable.isChecked())
            self.chk_art_hatch_quick.blockSignals(False)
        if hasattr(self, 'chk_text_hatch_quick') and hasattr(self, 'chk_hatch_enable'):
            self.chk_text_hatch_quick.blockSignals(True)
            self.chk_text_hatch_quick.setChecked(self.chk_hatch_enable.isChecked())
            self.chk_text_hatch_quick.blockSignals(False)
        self.apply_artwork_transforms()

    def _on_quick_art_hatch_toggled(self, checked: bool):
        if hasattr(self, 'chk_hatch_enable'):
            self.chk_hatch_enable.setChecked(checked)

    def _on_quick_text_hatch_toggled(self, checked: bool):
        if hasattr(self, 'chk_hatch_enable'):
            self.chk_hatch_enable.setChecked(checked)

    def _on_hatch_overlap_changed(self, val: float):
        if hasattr(self, 'spn_overlap') and abs(self.spn_overlap.value() - val) > 1e-4:
            self.spn_overlap.blockSignals(True)
            self.spn_overlap.setValue(val)
            self.spn_overlap.blockSignals(False)
        self.update_config_and_recalculate()

    def _on_slicing_overlap_changed(self, val: float):
        if hasattr(self, 'spn_hatch_overlap') and abs(self.spn_hatch_overlap.value() - val) > 1e-4:
            self.spn_hatch_overlap.blockSignals(True)
            self.spn_hatch_overlap.setValue(val)
            self.spn_hatch_overlap.blockSignals(False)
        self.update_config_and_recalculate()

    def _set_hatch_preset(self, pitch=None, angle=None, cross=None):
        if hasattr(self, 'chk_hatch_enable') and not self.chk_hatch_enable.isChecked():
            self.chk_hatch_enable.setChecked(True)
        if pitch is not None and hasattr(self, 'spn_hatch_pitch'):
            self.spn_hatch_pitch.setValue(pitch)
        if angle is not None and hasattr(self, 'spn_hatch_angle'):
            self.spn_hatch_angle.setValue(angle)
        if cross is not None and hasattr(self, 'chk_hatch_cross'):
            self.chk_hatch_cross.setChecked(cross)
        self.apply_artwork_transforms()

    def _on_art_width_changed(self, target_w: float = None):
        """Interactively adjusts artwork scale when user enters a target width in millimeters."""
        if not self.source_paths:
            return
        if target_w is None:
            target_w = self.spn_art_width.value()
        if target_w <= 0.001:
            return

        if not hasattr(self, 'orig_art_w') or self.orig_art_w < 1e-4:
            min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
            self.orig_art_w = max(1e-4, max_x - min_x)
            self.orig_art_h = max(1e-4, max_y - min_y)

        rot = abs(round(self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0)) % 180
        is_swapped = (45 < rot < 135)
        base_dim = self.orig_art_h if is_swapped else self.orig_art_w
        if base_dim < 1e-4:
            return

        new_scale = (target_w / base_dim) * 100.0

        if is_swapped:
            cur_scale_y = self.spn_scale_y.value()
            cur_visual_w = self.orig_art_h * (cur_scale_y / 100.0)
            w_ratio = target_w / max(1e-4, cur_visual_w)

            self.spn_scale_y.blockSignals(True)
            self.spn_scale_y.setValue(round(new_scale, 2))
            self.spn_scale_y.blockSignals(False)

            if self.chk_lock_aspect.isChecked():
                new_scale_x = self.spn_scale_x.value() * w_ratio
                self.spn_scale_x.blockSignals(True)
                self.spn_scale_x.setValue(round(new_scale_x, 2))
                self.spn_scale_x.blockSignals(False)
        else:
            cur_scale_x = self.spn_scale_x.value()
            cur_visual_w = self.orig_art_w * (cur_scale_x / 100.0)
            w_ratio = target_w / max(1e-4, cur_visual_w)

            self.spn_scale_x.blockSignals(True)
            self.spn_scale_x.setValue(round(new_scale, 2))
            self.spn_scale_x.blockSignals(False)

            if self.chk_lock_aspect.isChecked():
                new_scale_y = self.spn_scale_y.value() * w_ratio
                self.spn_scale_y.blockSignals(True)
                self.spn_scale_y.setValue(round(new_scale_y, 2))
                self.spn_scale_y.blockSignals(False)

        self.apply_artwork_transforms()

    def _on_art_height_changed(self, target_h: float = None):
        """Interactively adjusts artwork scale when user enters a target height in millimeters."""
        if not self.source_paths:
            return
        if target_h is None:
            target_h = self.spn_art_height.value()
        if target_h <= 0.001:
            return

        if not hasattr(self, 'orig_art_h') or self.orig_art_h < 1e-4:
            min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
            self.orig_art_w = max(1e-4, max_x - min_x)
            self.orig_art_h = max(1e-4, max_y - min_y)

        rot = abs(round(self.spn_art_rotation.value() if hasattr(self, 'spn_art_rotation') else 0.0)) % 180
        is_swapped = (45 < rot < 135)
        base_dim = self.orig_art_w if is_swapped else self.orig_art_h
        if base_dim < 1e-4:
            return

        new_scale = (target_h / base_dim) * 100.0

        if is_swapped:
            cur_scale_x = self.spn_scale_x.value()
            cur_visual_h = self.orig_art_w * (cur_scale_x / 100.0)
            h_ratio = target_h / max(1e-4, cur_visual_h)

            self.spn_scale_x.blockSignals(True)
            self.spn_scale_x.setValue(round(new_scale, 2))
            self.spn_scale_x.blockSignals(False)

            if self.chk_lock_aspect.isChecked():
                new_scale_y = self.spn_scale_y.value() * h_ratio
                self.spn_scale_y.blockSignals(True)
                self.spn_scale_y.setValue(round(new_scale_y, 2))
                self.spn_scale_y.blockSignals(False)
        else:
            cur_scale_y = self.spn_scale_y.value()
            cur_visual_h = self.orig_art_h * (cur_scale_y / 100.0)
            h_ratio = target_h / max(1e-4, cur_visual_h)

            self.spn_scale_y.blockSignals(True)
            self.spn_scale_y.setValue(round(new_scale, 2))
            self.spn_scale_y.blockSignals(False)

            if self.chk_lock_aspect.isChecked():
                new_scale_x = self.spn_scale_x.value() * h_ratio
                self.spn_scale_x.blockSignals(True)
                self.spn_scale_x.setValue(round(new_scale_x, 2))
                self.spn_scale_x.blockSignals(False)

        self.apply_artwork_transforms()

    def _on_scale_x_changed(self, val: float):
        if self.chk_lock_aspect.isChecked() and abs(self.spn_scale_y.value() - val) > 1e-4:
            self.spn_scale_y.blockSignals(True)
            self.spn_scale_y.setValue(val)
            self.spn_scale_y.blockSignals(False)
        self.apply_artwork_transforms()

    def _on_scale_y_changed(self, val: float):
        if self.chk_lock_aspect.isChecked() and abs(self.spn_scale_x.value() - val) > 1e-4:
            self.spn_scale_x.blockSignals(True)
            self.spn_scale_x.setValue(val)
            self.spn_scale_x.blockSignals(False)
        self.apply_artwork_transforms()

    def fit_artwork_to_workpiece(self):
        """Scales artwork proportionally so it fits comfortably within workpiece bounds and galvo field."""
        if not self.source_paths or not hasattr(self, 'orig_art_w') or self.orig_art_w < 1e-4:
            return
        wp_len = self.spn_workpiece_height.value()
        c = getattr(self.config, 'circumference', math.pi * self.spn_diameter.value())
        max_field = getattr(self.config, 'galvo_field_size', 100.0)

        max_allowed_w = min(wp_len * 0.8, max_field * 0.8)
        max_allowed_h = min(c * 0.8, max_field * 0.8)
        scale = min(max_allowed_w / self.orig_art_w, max_allowed_h / self.orig_art_h) * 100.0
        scale = max(0.01, min(1000.0, scale))

        self.spn_scale_x.setValue(scale)
        self.spn_scale_y.setValue(scale)
        self.center_artwork_on_cylinder()
        self.lbl_console_log.setText(f"Fitted artwork to workpiece ({self.orig_art_w * scale / 100.0:.2f} x {self.orig_art_h * scale / 100.0:.2f} mm).")

    def reset_artwork_scale(self):
        """Resets artwork scale to 100.0% (1:1 native CAD/SVG millimeter dimensions)."""
        if not self.source_paths:
            return
        self.spn_scale_x.setValue(100.0)
        self.spn_scale_y.setValue(100.0)
        self.lbl_console_log.setText("Reset artwork to 1:1 original CAD size (100.0%).")

    def fit_artwork_to_360(self):
        """Scales artwork height so it seamlessly wraps 360° around workpiece circumference."""
        if not self.source_paths:
            return
        self.active_generator = 'cad_vector'
        c = math.pi * max(0.1, self.spn_diameter.value())
        _, min_y, _, max_y = self.slicing_engine.get_artwork_bounds(self.source_paths)
        h_orig = max_y - min_y
        if h_orig > 1e-4:
            target_scale = (c / h_orig) * 100.0
            self.spn_scale_y.setValue(target_scale)
            if self.chk_lock_aspect.isChecked():
                self.spn_scale_x.setValue(target_scale)
            self.lbl_console_log.setText(f"Scaled artwork height to match circumference ({c:.2f} mm).")

    def center_artwork_on_cylinder(self):
        """Centers artwork on the cylindrical workpiece in both axial (X) and rotary (Y) directions."""
        if not self.raw_paths:
            return
        c = getattr(self.config, 'circumference', math.pi * self.spn_diameter.value())
        L = getattr(self.config, 'axial_length', self.spn_workpiece_height.value())
        min_x, min_y, max_x, max_y = self.slicing_engine.get_artwork_bounds(self.raw_paths)
        w = max_x - min_x
        h = max_y - min_y
        target_min_x = (L - w) / 2.0
        target_min_y = (c - h) / 2.0
        delta_x = target_min_x - min_x
        delta_y = target_min_y - min_y
        self.spn_offset_x.setValue(self.spn_offset_x.value() + delta_x)
        self.spn_offset_y.setValue(self.spn_offset_y.value() + delta_y)

    def align_artwork_to_apex(self):
        """Aligns the bottom/start of artwork to the 0° apex line."""
        if not self.raw_paths:
            return
        _, min_y, _, _ = self.slicing_engine.get_artwork_bounds(self.raw_paths)
        self.spn_offset_y.setValue(self.spn_offset_y.value() - min_y)

    # -------------------------------------------------------------------------
    # KINEMATICS, CONFIGURATION & SLICING RECALCULATION
    # -------------------------------------------------------------------------
    def _on_mode_changed(self, idx: int):
        is_angular = (idx == 2)
        is_split_line = (idx == 1)
        self.spn_angular_parts.setEnabled(is_angular)
        self.frame_split_lines.setVisible(is_split_line)
        self.update_config_and_recalculate()

    def on_add_split_line_clicked(self):
        val = self.spn_new_split_line.value()
        if val not in self.config.custom_split_lines:
            self.config.custom_split_lines.append(val)
            self.config.custom_split_lines.sort()
            self.update_config_and_recalculate()

    def on_clear_split_lines_clicked(self):
        self.config.custom_split_lines = []
        self.update_config_and_recalculate()

    def on_split_line_added_from_canvas(self, val: float):
        if val not in self.config.custom_split_lines:
            self.config.custom_split_lines.append(val)
            self.config.custom_split_lines.sort()
            self.update_config_and_recalculate()

    def on_slice_selected_on_canvas(self, idx: int):
        if 0 <= idx < len(self.slices):
            sl = self.slices[idx]
            self.lbl_slice_badge.setText(f"Slice: {idx+1} / {len(self.slices)}")
            self.lbl_console_log.setText(f"Selected Slice #{idx+1}: Angle {sl.rotation_angle_deg:.1f}°, {len(sl.paths)} vectors")

    def update_config_from_ui(self) -> RotaryConfig:
        """Constructs RotaryConfig object from UI inputs."""
        cfg = RotaryConfig()
        cfg.diameter = self.spn_diameter.value()
        cfg.pulses_per_rev = self.spn_pulses_rev.value()
        cfg.gear_ratio = self.spn_gear_ratio.value()
        cfg.reverse_direction = self.chk_reverse_dir.isChecked()
        cfg.ring_inside = self.chk_ring_inside.isChecked()

        axis_str = self.combo_motor_axis.currentText()
        if "Z-Axis" in axis_str:
            cfg.stepper_axis = 'Z'
        elif "X-Axis" in axis_str:
            cfg.stepper_axis = 'X'
        else:
            cfg.stepper_axis = 'Y'

        cfg.axis = 'Y' if self.combo_rot_axis.currentIndex() == 0 else 'X'

        mode_idx = self.combo_mode.currentIndex()
        if mode_idx == 0:
            cfg.mode = 'split_by_size'
        elif mode_idx == 1:
            cfg.mode = 'split_by_line'
        else:
            cfg.mode = 'angular_indexing'

        cfg.overlap = self.spn_overlap.value()
        cfg.angular_stations = self.spn_angular_parts.value()
        cfg.custom_split_lines = list(getattr(self.config, 'custom_split_lines', []))

        if (
            hasattr(self, 'chk_pattern_align_slices') and 
            self.chk_pattern_align_slices.isChecked() and 
            getattr(self, 'active_generator', '') == 'pipe_pattern'
        ):
            cfg.pattern_repeats = self.spn_pattern_repeats.value() if hasattr(self, 'spn_pattern_repeats') else 0
            cfg.align_to_repeats = True
            c = math.pi * max(0.1, cfg.diameter)
            reps = max(1, cfg.pattern_repeats)
            cfg.split_size = c / reps
        else:
            cfg.pattern_repeats = 0
            cfg.align_to_repeats = False
            cfg.split_size = self.spn_split_size.value()

        cfg.stagger_seam = self.chk_hatch_stagger_seam.isChecked() if hasattr(self, 'chk_hatch_stagger_seam') else True

        cfg.max_speed = self.spn_max_speed.value()
        cfg.accel_time_ms = self.spn_accel_time.value()
        cfg.settling_delay_ms = self.spn_settling_delay.value()
        cfg.return_to_zero = self.chk_return_zero.isChecked()
        cfg.axial_length = self.spn_workpiece_height.value()

        self.config = cfg
        return cfg

    def update_config_and_recalculate(self):
        """Re-runs Rotary Slicing Engine and updates canvas."""
        cfg = self.update_config_from_ui()

        # Perform Slicing
        self.slices = self.slicing_engine.slice_paths(self.raw_paths, cfg)
        self.canvas.set_data(self.raw_paths, self.slices, cfg)

        tot_pulses = sum(sl.step_pulses for sl in self.slices)
        est_sec = self.slicing_engine.estimate_execution_time(self.slices, cfg, self.spn_mark_speed.value())

        self.lbl_slice_stats.setText(
            f"Slices: {len(self.slices)} | Total Pulses: {tot_pulses:,} | Est Time: ~{est_sec:.1f}s"
        )
        self.lbl_slice_badge.setText(f"Slices: 0 / {len(self.slices)}")

    # -------------------------------------------------------------------------
    # PART COUNTERS & TIMERS
    # -------------------------------------------------------------------------
    def _on_reset_part_count(self):
        self.part_count = 0
        self.spn_part_count.setValue(0)
        self.time_part_sec = 0.0
        self.lbl_time_part.setText("00:00:00")

    def _on_timer_second(self):
        if self.exec_thread and self.exec_thread.isRunning() and not self.exec_thread.is_paused():
            self.time_part_sec += 1.0
            self.time_total_sec += 1.0
            self.lbl_time_part.setText(self._format_hms(self.time_part_sec))
            self.lbl_time_total.setText(self._format_hms(self.time_total_sec))

    @staticmethod
    def _format_hms(seconds: float) -> str:
        s = int(seconds)
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:02d}"

    # -------------------------------------------------------------------------
    # MASTER EXECUTION CONTROLS (F1, F2, F3, F5)
    # -------------------------------------------------------------------------
    def on_back_to_cad_clicked(self):
        """F5: Returns to CAD Canvas view."""
        self.on_stop_clicked()
        if self.main_window:
            if hasattr(self.main_window, 'main_stack'):
                if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'cadPage'):
                    self.main_window.main_stack.setCurrentWidget(self.main_window.ui.cadPage)
                else:
                    self.main_window.main_stack.setCurrentIndex(0)
            elif hasattr(self.main_window, 'pages_widget'):
                self.main_window.pages_widget.setCurrentIndex(0)
            elif hasattr(self.main_window, 'tabWidget'):
                self.main_window.tabWidget.setCurrentIndex(0)

    def on_redlight_clicked(self):
        """F1: Toggles Red-Light Framing execution."""
        if self.exec_thread and self.exec_thread.isRunning():
            if self.exec_thread.is_redlight:
                self.on_stop_clicked()
            else:
                self.lbl_console_log.setText("Cannot start red-light framing while marking is active.")
            return

        if not self.slices:
            self.update_config_and_recalculate()
        if not self.slices:
            QMessageBox.warning(self, "No Slices", "Cannot start framing: No slices generated.")
            return

        self._start_execution_thread(is_redlight=True)

    def on_mark_clicked(self):
        """F2: Initiates full laser rotary marking sequence."""
        if self.exec_thread and self.exec_thread.isRunning():
            return

        if not self.slices:
            self.update_config_and_recalculate()
        if not self.slices:
            QMessageBox.warning(self, "No Slices", "Cannot start marking: Workpiece has no slices.")
            return

        self.time_part_sec = 0.0
        self.lbl_time_part.setText("00:00:00")
        self.job_timer.start()

        self._start_execution_thread(is_redlight=False)

    def on_pause_clicked(self):
        """Spacebar / Pause button: Pauses or resumes active execution."""
        if self.exec_thread and self.exec_thread.isRunning():
            if self.exec_thread.is_paused():
                self.exec_thread.resume()
                self.btn_pause.setText("PAUSE")
                self.btn_pause.setStyleSheet("background-color: #554411; color: #ffdd88; font-weight: bold; padding: 8px;")
                self.lbl_job_status.setText("Job Resumed // Marking Active")
            else:
                self.exec_thread.pause()
                self.btn_pause.setText("RESUME")
                self.btn_pause.setStyleSheet("background-color: #005a7d; color: #ffffff; font-weight: bold; padding: 8px;")
                self.lbl_job_status.setText("Job PAUSED by Operator")

    def _start_execution_thread(self, is_redlight: bool):
        """Instantiates and launches RotaryExecutionThread."""
        self.lbl_job_status.setText("Framing Active..." if is_redlight else "Marking Active...")
        self.lbl_job_status.setStyleSheet("font-weight: bold; color: #ff3344;" if is_redlight else "font-weight: bold; color: #00ff66;")

        self.btn_mark.setEnabled(is_redlight)
        self.btn_pause.setEnabled(not is_redlight)
        self.btn_redlight.setText("Stop Framing" if is_redlight else "Light (F1)")

        self.exec_thread = RotaryExecutionThread(
            slices=self.slices,
            config=self.config,
            galvo_controller=self.galvo_controller,
            stepper_controller=self.stepper_controller,
            galvo_config=self.galvo_config,
            is_redlight=is_redlight,
            loop_framing=self.chk_loop_framing.isChecked(),
            continuous=self.chk_continuous.isChecked(),
            laser_power=self.spn_laser_power.value(),
            laser_freq=self.spn_laser_freq.value(),
            mark_speed=self.spn_mark_speed.value(),
            jump_speed=self.spn_jump_speed.value()
        )
        self.exec_thread.sliceStarted.connect(self._on_slice_started)
        self.exec_thread.sliceCompleted.connect(self._on_slice_completed)
        self.exec_thread.progressUpdated.connect(self.progress_bar.setValue)
        self.exec_thread.logMessage.connect(self.lbl_console_log.setText)
        self.exec_thread.jobFinished.connect(self._on_job_finished)
        self.exec_thread.start()

    def _on_slice_started(self, idx: int, total: int):
        self.lbl_slice_badge.setText(f"Slice: {idx+1} / {total}")
        self.canvas.set_active_slice(idx)

    def _on_slice_completed(self, idx: int, total: int):
        pass

    def _on_job_finished(self, success: bool, msg: str):
        self.job_timer.stop()
        self.canvas.set_active_slice(-1)
        self.btn_mark.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("PAUSE")
        self.btn_redlight.setText("Light (F1)")

        if success and self.exec_thread and not self.exec_thread.is_redlight:
            self.part_count += 1
            self.total_count += 1
            self.spn_part_count.setValue(self.part_count)
            self.spn_total_count.setValue(self.total_count)

        self.lbl_job_status.setText("Job Completed" if success else "Job Halted")
        self.lbl_job_status.setStyleSheet("font-weight: bold; color: #00d2ff;" if success else "font-weight: bold; color: #ff3344;")
        self.lbl_console_log.setText(msg)

    def on_stop_clicked(self):
        """F3: Emergency stop execution."""
        self.job_timer.stop()
        if self.exec_thread and self.exec_thread.isRunning():
            self.lbl_console_log.setText("EMERGENCY STOP TRIGGERED!")
            self.exec_thread.stop()
            self.exec_thread.wait(500)

        if self.galvo_controller and hasattr(self.galvo_controller, 'connection') and self.galvo_controller.connection:
            conn = self.galvo_controller.connection
            if hasattr(conn, 'stop'):
                conn.stop()
            if hasattr(conn, 'laser_off'):
                conn.laser_off()
            if hasattr(conn, 'reddot_off'):
                conn.reddot_off()

        self.btn_mark.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("PAUSE")
        self.btn_redlight.setText("Light (F1)")

        self.lbl_job_status.setText("EMERGENCY STOP HALTED")
        self.lbl_job_status.setStyleSheet("font-weight: bold; color: #ff3344;")
        self.canvas.set_active_slice(-1)


# =============================================================================
# STANDALONE APPLICATION ENTRY POINT
# =============================================================================

def main():
    """Launches the Rotary Marking Page as a standalone application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from machine.galvo_controller import GalvoController
    from machine.stepper_controller import StepperController
    
    galvo_ctrl = GalvoController()
    galvo_ctrl.connect(force_mock=True)
    stepper_ctrl = StepperController(galvo_ctrl.connection)

    window = QMainWindow()
    window.setWindowTitle("Galvo Studio Pro // EZCad RotaryMark & MarkDemo Slicing Engine")
    window.resize(1360, 860)

    rotary_page = RotaryMarkingPage(window, galvo_controller=galvo_ctrl, stepper_controller=stepper_ctrl)
    window.setCentralWidget(rotary_page)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
