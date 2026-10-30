import math
import os
import time
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, Signal, Slot, QTimer, QSize, QEvent
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont, QFontDatabase,
    QCursor, QTransform, QWheelEvent, QMouseEvent, QKeyEvent, QIcon,
    QLinearGradient, QAction, QKeySequence, QPixmap, QShortcut
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem, QInputDialog,
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QDoubleSpinBox,
    QSpinBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMenuBar, QMenu, QToolBar, QButtonGroup, QRadioButton,
    QScrollArea, QDialog, QLineEdit, QTextEdit, QAbstractItemView, QAbstractSpinBox
)

from cad_items import (
    PEN_PALETTE, CadShapeItem, CadLineItem, CadRectItem,
    CadCircleItem, CadPolygonItem, CadTextItem, CadBarcodeItem,
    CadHatchItem, SelectionHandleBox
)


class CornerBox(QWidget):
    """Top-left intersection box between horizontal and vertical rulers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#e8e8e8"))
        painter.setPen(QPen(QColor("#808080"), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        # Draw small origin cross
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawLine(8, 12, 16, 12)
        painter.drawLine(12, 8, 12, 16)


class HorizontalRuler(QWidget):
    """Top interactive millimeter ruler matching EzCad viewport pan & zoom."""
    def __init__(self, view, scene, parent=None):
        super().__init__(parent)
        self.view = view
        self.cad_scene = scene
        self.setFixedHeight(24)
        self.cursor_x_scene = 0.0

    def set_cursor_x(self, x_scene: float):
        self.cursor_x_scene = x_scene
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f0f0f0"))
        
        # Bottom border line
        painter.setPen(QPen(QColor("#808080"), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        transform = self.view.transform()
        scale = abs(transform.m11())
        if scale < 1e-4:
            return

        # Visible scene range
        left_scene = self.view.mapToScene(0, 0).x()
        right_scene = self.view.mapToScene(self.width(), 0).x()

        # Step size based on zoom level
        if scale > 8.0:
            step = 1.0
        elif scale > 3.0:
            step = 2.0
        elif scale > 1.2:
            step = 5.0
        elif scale > 0.4:
            step = 10.0
        else:
            step = 20.0

        first_mark = math.floor(left_scene / step) * step
        last_mark = math.ceil(right_scene / step) * step

        painter.setFont(QFont("Arial", 7))
        h = self.height()

        cur = first_mark
        while cur <= last_mark:
            vx = self.view.mapFromScene(QPointF(cur, 0.0)).x()
            is_major = (abs(round(cur) % 10) < 1e-4)
            is_medium = (abs(round(cur) % 5) < 1e-4)

            if is_major:
                painter.setPen(QPen(QColor("#333333"), 1))
                painter.drawLine(vx, h - 9, vx, h - 1)
                text = f"{int(round(cur))}"
                painter.drawText(vx + 2, 11, text)
            elif is_medium:
                painter.setPen(QPen(QColor("#666666"), 1))
                painter.drawLine(vx, h - 6, vx, h - 1)
            else:
                painter.setPen(QPen(QColor("#999999"), 1))
                painter.drawLine(vx, h - 3, vx, h - 1)

            cur += step

        # Draw red cursor position indicator
        cx = self.view.mapFromScene(QPointF(self.cursor_x_scene, 0.0)).x()
        painter.setPen(QPen(QColor("#e74c3c"), 1))
        painter.drawLine(cx, 0, cx, h - 1)


class VerticalRuler(QWidget):
    """Left interactive millimeter ruler (EzCad coordinate convention: Y+ is UP)."""
    def __init__(self, view, scene, parent=None):
        super().__init__(parent)
        self.view = view
        self.cad_scene = scene
        self.setFixedWidth(24)
        self.cursor_y_scene = 0.0

    def set_cursor_y(self, y_scene: float):
        self.cursor_y_scene = y_scene
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f0f0f0"))

        # Right border line
        painter.setPen(QPen(QColor("#808080"), 1))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        transform = self.view.transform()
        scale = abs(transform.m22())
        if scale < 1e-4:
            return

        top_scene = self.view.mapToScene(0, 0).y()
        bottom_scene = self.view.mapToScene(0, self.height()).y()

        if scale > 8.0:
            step = 1.0
        elif scale > 3.0:
            step = 2.0
        elif scale > 1.2:
            step = 5.0
        elif scale > 0.4:
            step = 10.0
        else:
            step = 20.0

        first_mark = math.floor(top_scene / step) * step
        last_mark = math.ceil(bottom_scene / step) * step

        painter.setFont(QFont("Arial", 6))
        w = self.width()

        cur = first_mark
        while cur <= last_mark:
            vy = self.view.mapFromScene(QPointF(0.0, cur)).y()
            # EzCad convention: display Y as -scene_y
            ezcad_y = -cur
            is_major = (abs(round(ezcad_y) % 10) < 1e-4)
            is_medium = (abs(round(ezcad_y) % 5) < 1e-4)

            if is_major:
                painter.setPen(QPen(QColor("#333333"), 1))
                painter.drawLine(w - 9, vy, w - 1, vy)
                text = f"{int(round(ezcad_y))}"
                # Render vertical text or small offset text
                painter.drawText(2, vy - 2, text)
            elif is_medium:
                painter.setPen(QPen(QColor("#666666"), 1))
                painter.drawLine(w - 6, vy, w - 1, vy)
            else:
                painter.setPen(QPen(QColor("#999999"), 1))
                painter.drawLine(w - 3, vy, w - 1, vy)

            cur += step

        # Draw red cursor position indicator
        cy = self.view.mapFromScene(QPointF(0.0, self.cursor_y_scene)).y()
        painter.setPen(QPen(QColor("#e74c3c"), 1))
        painter.drawLine(0, cy, w - 1, cy)


class AnchorSelector(QWidget):
    """3x3 Grid 9-Point Anchor Selector (Top-Left, Center, Bottom-Right, etc.)."""
    anchorChanged = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(54, 54)
        self.anchor_x = 1  # 0: left, 1: center, 2: right
        self.anchor_y = 1  # 0: top, 1: center, 2: bottom

    def mousePressEvent(self, event: QMouseEvent):
        gx = max(0, min(2, int(event.position().x() // 18)))
        gy = max(0, min(2, int(event.position().y() // 18)))
        if gx != self.anchor_x or gy != self.anchor_y:
            self.anchor_x = gx
            self.anchor_y = gy
            self.update()
            self.anchorChanged.emit(self.anchor_x, self.anchor_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Frame
        painter.setPen(QPen(QColor("#7f8c8d"), 1))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRect(0, 0, 53, 53)

        # 3x3 Grid lines
        painter.setPen(QPen(QColor("#bdc3c7"), 1, Qt.PenStyle.DotLine))
        painter.drawLine(18, 0, 18, 53)
        painter.drawLine(36, 0, 36, 53)
        painter.drawLine(0, 18, 53, 18)
        painter.drawLine(0, 36, 53, 36)

        # Draw points
        for gy in range(3):
            for gx in range(3):
                cx = 9 + gx * 18
                cy = 9 + gy * 18
                if gx == self.anchor_x and gy == self.anchor_y:
                    painter.setPen(QPen(QColor("#c0392b"), 1))
                    painter.setBrush(QBrush(QColor("#e74c3c")))
                    painter.drawEllipse(QPointF(cx, cy), 4.5, 4.5)
                else:
                    painter.setPen(QPen(QColor("#7f8c8d"), 1))
                    painter.setBrush(QBrush(QColor("#bdc3c7")))
                    painter.drawEllipse(QPointF(cx, cy), 2.5, 2.5)


class CadScene(QGraphicsScene):
    """
    EzCad Precision Millimeter CAD Scene.
    Center (0, 0) is the Galvo mirror optical center.
    Pure white bed sheet with realistic drop shadow and millimeter grid.
    """
    coordinateChanged = Signal(float, float)
    selectionChangedCustom = Signal()
    toolChanged = Signal(str)
    shapeGeometryChanged = Signal(object)

    def __init__(self, field_size_mm: float = 70.0, parent=None):
        super().__init__(parent)
        self.field_size = float(field_size_mm)
        self._update_scene_rect()

        self.active_tool = "select"
        self.snap_enabled = True
        self.snap_grid_size = 1.0  # mm
        self.active_pen_id = 0

        # Interactive states
        self.start_scene_pt = None
        self.temp_preview_item = None
        self.selection_box = None
        self._in_selection_change = False

        # Transform handle state
        self.dragging_handle = SelectionHandleBox.HANDLE_NONE
        self.handle_drag_start_pt = None
        self.handle_target_init_pos = None
        self.handle_target_init_scale = 1.0
        self.handle_target_init_rot = 0.0
        self.handle_center_scene_pt = None
        self.handle_drag_init_dist = 1.0
        self.handle_drag_init_angle = 0.0

        # Red light framing simulation item
        self.framing_rect_item = None

        self.selectionChanged.connect(self._on_scene_selection_changed)

    def set_field_size(self, size_mm: float):
        if size_mm > 5.0 and abs(self.field_size - size_mm) > 0.01:
            self.field_size = float(size_mm)
            self._update_scene_rect()
            self.update()

    def _update_scene_rect(self):
        half = self.field_size / 2.0
        # Extra 40mm margin around the bed for comfortable panning
        margin = max(30.0, self.field_size * 0.3)
        self.setSceneRect(-half - margin, -half - margin, self.field_size + margin * 2.0, self.field_size + margin * 2.0)

    def _view_scale(self, event=None) -> float:
        scale = 1.0
        if event and hasattr(event, 'widget') and event.widget():
            parent = event.widget().parentWidget()
            if isinstance(parent, QGraphicsView):
                scale = abs(parent.transform().m11())
        if (scale < 1e-4 or scale == 1.0) and self.views():
            scale = abs(self.views()[0].transform().m11())
        return scale if scale > 1e-4 else 1.0

    def set_tool(self, tool_name: str):
        self.active_tool = tool_name
        if self.temp_preview_item:
            if self.temp_preview_item.scene() == self:
                self.removeItem(self.temp_preview_item)
            self.temp_preview_item = None
        self.start_scene_pt = None
        if tool_name != "select":
            self.clearSelection()
        self.toolChanged.emit(tool_name)

    def snap_point(self, pt: QPointF) -> QPointF:
        if not self.snap_enabled or self.snap_grid_size <= 0:
            return pt
        grid = self.snap_grid_size
        sx = round(pt.x() / grid) * grid
        sy = round(pt.y() / grid) * grid
        return QPointF(sx, sy)

    def update_selection_box(self):
        if self.selection_box and self.selection_box.scene() == self:
            self.selection_box.prepareGeometryChange()
            self.selection_box.update()

    def _on_scene_selection_changed(self):
        if self._in_selection_change:
            return
        self._in_selection_change = True
        try:
            if self.selection_box:
                if self.selection_box.scene() == self:
                    self.removeItem(self.selection_box)
                self.selection_box = None

            selected = [item for item in list(self.selectedItems()) if isinstance(item, CadShapeItem)]
            if len(selected) == 1:
                self.selection_box = SelectionHandleBox(selected[0])
                self.addItem(self.selection_box)

            self.selectionChangedCustom.emit()
            self.update()
        finally:
            self._in_selection_change = False

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # 1. Outer canvas workspace (classic EzCad soft light gray)
        painter.fillRect(rect, QColor("#e0e0e0"))

        half = self.field_size / 2.0
        bed_rect = QRectF(-half, -half, self.field_size, self.field_size)

        # 2. Realistic EzCad Drop Shadow behind the pure white bed sheet (bottom & right)
        scale = abs(painter.transform().m11())
        if scale < 1e-4:
            scale = 1.0
        shadow_offset = 3.5 / scale  # Screen-pixel invariant drop shadow
        shadow_rect = QRectF(-half + shadow_offset, -half + shadow_offset, self.field_size, self.field_size)
        painter.fillRect(shadow_rect, QColor("#666666"))

        # 3. Pure White Galvo Bed Sheet
        painter.fillRect(bed_rect, QColor("#ffffff"))

        # 4. Millimeter Grid Pattern across the ENTIRE visible viewport (rect),
        # both inside the field box and outside across the workspace!
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        # Grid line pens inside the white field box:
        in_minor_pen = QPen(QColor("#eeeeee"), 0.5)
        in_minor_pen.setCosmetic(True)
        in_major_pen = QPen(QColor("#cccccc"), 0.8)
        in_major_pen.setCosmetic(True)

        # Grid line pens outside the field box (on light gray background):
        out_minor_pen = QPen(QColor("#d4d4d4"), 0.5)
        out_minor_pen.setCosmetic(True)
        out_major_pen = QPen(QColor("#b0b0b0"), 0.8)
        out_major_pen.setCosmetic(True)

        show_minor = (scale > 1.2)

        # Draw Vertical Grid Lines across entire workspace
        for x in range(left, right + 1):
            is_major = (x % 10 == 0)
            is_minor = (x % 2 == 0 or x % 5 == 0) if show_minor else False
            if not is_major and not is_minor:
                continue

            pen_out = out_major_pen if is_major else out_minor_pen
            pen_in = in_major_pen if is_major else in_minor_pen

            if -half <= x <= half:
                # Segment above bed_rect
                if top < -half:
                    painter.setPen(pen_out)
                    painter.drawLine(x, top, x, int(-half))
                # Segment inside bed_rect
                painter.setPen(pen_in)
                painter.drawLine(x, max(top, int(-half)), x, min(bottom, int(half)))
                # Segment below bed_rect
                if bottom > half:
                    painter.setPen(pen_out)
                    painter.drawLine(x, int(half), x, bottom)
            else:
                # Entire line outside bed_rect
                painter.setPen(pen_out)
                painter.drawLine(x, top, x, bottom)

        # Draw Horizontal Grid Lines across entire workspace
        for y in range(top, bottom + 1):
            is_major = (y % 10 == 0)
            is_minor = (y % 2 == 0 or y % 5 == 0) if show_minor else False
            if not is_major and not is_minor:
                continue

            pen_out = out_major_pen if is_major else out_minor_pen
            pen_in = in_major_pen if is_major else in_minor_pen

            if -half <= y <= half:
                # Segment left of bed_rect
                if left < -half:
                    painter.setPen(pen_out)
                    painter.drawLine(left, y, int(-half), y)
                # Segment inside bed_rect
                painter.setPen(pen_in)
                painter.drawLine(max(left, int(-half)), y, min(right, int(half)), y)
                # Segment right of bed_rect
                if right > half:
                    painter.setPen(pen_out)
                    painter.drawLine(int(half), y, right, y)
            else:
                # Entire line outside bed_rect
                painter.setPen(pen_out)
                painter.drawLine(left, y, right, y)

        # 5. Solid 1px Black Border around the Field Box
        border_pen = QPen(QColor("#000000"), 1.0)
        border_pen.setCosmetic(True)
        painter.setPen(border_pen)
        painter.drawRect(bed_rect)

        # 6. Center Coordinate Crosshairs (Dashed lines through (0, 0))
        # Spans across the entire canvas just like in EzCad Capture.PNG
        cross_pen = QPen(QColor("#2c3e50"), 1.0, Qt.PenStyle.DashLine)
        cross_pen.setCosmetic(True)
        painter.setPen(cross_pen)
        painter.drawLine(left, 0, right, 0)
        painter.drawLine(0, top, 0, bottom)

    def mousePressEvent(self, event):
        scene_pt = event.scenePos()
        self.coordinateChanged.emit(scene_pt.x(), scene_pt.y())

        # Transform handle hit test
        if self.selection_box and self.active_tool == "select":
            scale = self._view_scale(event)
            h_id = self.selection_box.handle_at_point(scene_pt, tolerance_mm=5.0 / scale, scale=scale)
            if h_id != SelectionHandleBox.HANDLE_NONE:
                self.dragging_handle = h_id
                self.handle_drag_start_pt = scene_pt
                target = self.selection_box.target_item
                target.setTransformOriginPoint(target.boundingRect().center())
                self.handle_target_init_pos = target.pos()
                self.handle_target_init_scale = target.scale()
                self.handle_target_init_rot = target.rotation()
                center = target.mapToScene(target.boundingRect().center())
                self.handle_center_scene_pt = center
                self.handle_drag_init_dist = max(0.1, math.hypot(scene_pt.x() - center.x(), scene_pt.y() - center.y()))
                self.handle_drag_init_angle = math.degrees(math.atan2(scene_pt.y() - center.y(), scene_pt.x() - center.x()))
                event.accept()
                return

        if self.active_tool == "select":
            super().mousePressEvent(event)
        elif self.active_tool in ("line", "rect", "circle", "ellipse", "polygon"):
            self.start_scene_pt = self.snap_point(scene_pt)
            preview_pen = QPen(QColor("#0055ff"), 0.5, Qt.PenStyle.DashLine)
            preview_pen.setCosmetic(True)

            if self.active_tool == "line":
                self.temp_preview_item = QGraphicsLineItem(QLineF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)
            elif self.active_tool == "rect":
                self.temp_preview_item = QGraphicsRectItem(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)
            elif self.active_tool in ("circle", "ellipse"):
                self.temp_preview_item = QGraphicsEllipseItem(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)
            elif self.active_tool == "polygon":
                self.temp_preview_item = QGraphicsEllipseItem(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)

            if self.temp_preview_item:
                self.addItem(self.temp_preview_item)
            event.accept()

        elif self.active_tool == "text":
            pos = self.snap_point(scene_pt)
            font_fam = getattr(self, "default_font_family", "Arial")
            font_size = getattr(self, "default_font_height", 10.0)
            char_space = getattr(self, "default_text_space", 0.0)
            # Instantly place editable default TEXT entity
            item = CadTextItem(
                text="TEXT",
                font_size_mm=font_size,
                font_family=font_fam,
                char_spacing=char_space,
                bold=False,
                italic=False
            )
            # Center text on clicked point
            bounds = item.boundingRect()
            item.setPos(pos.x() - bounds.width() / 2.0, pos.y() - bounds.height() / 2.0)
            item.set_pen(self.active_pen_id)
            self.addItem(item)
            self.clearSelection()
            item.setSelected(True)
            self.set_tool("select")
            event.accept()

        elif self.active_tool == "barcode":
            pos = self.snap_point(scene_pt)
            code_str, ok = QInputDialog.getText(None, "EzCad 2D Barcode / QR", "Enter Barcode / QR content:")
            if ok and code_str.strip():
                item = CadBarcodeItem(code_str.strip(), pos, size_mm=20.0, code_type="QR Code")
                item.set_pen(self.active_pen_id)
                self.addItem(item)
                self.clearSelection()
                item.setSelected(True)
                self.set_tool("select")
            event.accept()

    def mouseMoveEvent(self, event):
        scene_pt = event.scenePos()
        self.coordinateChanged.emit(scene_pt.x(), scene_pt.y())

        # 1. Transform Handle Dragging
        if self.dragging_handle != SelectionHandleBox.HANDLE_NONE and self.selection_box:
            target = self.selection_box.target_item
            center = self.handle_center_scene_pt
            if self.dragging_handle == SelectionHandleBox.HANDLE_ROTATE:
                cur_angle = math.degrees(math.atan2(scene_pt.y() - center.y(), scene_pt.x() - center.x()))
                delta_angle = cur_angle - self.handle_drag_init_angle
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    target_rot = round((self.handle_target_init_rot + delta_angle) / 15.0) * 15.0
                    target.setRotation(target_rot)
                else:
                    target.setRotation(self.handle_target_init_rot + delta_angle)
            else:
                cur_dist = math.hypot(scene_pt.x() - center.x(), scene_pt.y() - center.y())
                ratio = cur_dist / self.handle_drag_init_dist
                new_scale = max(0.05, self.handle_target_init_scale * ratio)
                target.setScale(new_scale)

            self.selection_box.prepareGeometryChange()
            self.selection_box.update()
            event.accept()
            return

        # 2. Hover cursor over handles
        if self.selection_box and self.active_tool == "select" and self.views():
            scale = self._view_scale(event)
            h_id = self.selection_box.handle_at_point(scene_pt, tolerance_mm=5.0 / scale, scale=scale)
            view = self.views()[0]
            if h_id != SelectionHandleBox.HANDLE_NONE:
                view.setCursor(self.selection_box.cursor_for_handle(h_id))
            else:
                view.setCursor(Qt.CursorShape.ArrowCursor)

        # 3. Interactive Preview
        if self.temp_preview_item and self.start_scene_pt:
            cur_pt = self.snap_point(scene_pt)
            is_shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

            if self.active_tool == "line":
                if is_shift:
                    dx = cur_pt.x() - self.start_scene_pt.x()
                    dy = cur_pt.y() - self.start_scene_pt.y()
                    if abs(dx) > abs(dy) * 2:
                        cur_pt.setY(self.start_scene_pt.y())
                    elif abs(dy) > abs(dx) * 2:
                        cur_pt.setX(self.start_scene_pt.x())
                self.temp_preview_item.setLine(QLineF(self.start_scene_pt, cur_pt))

            elif self.active_tool == "rect":
                rx = min(self.start_scene_pt.x(), cur_pt.x())
                ry = min(self.start_scene_pt.y(), cur_pt.y())
                rw = abs(cur_pt.x() - self.start_scene_pt.x())
                rh = abs(cur_pt.y() - self.start_scene_pt.y())
                if is_shift:
                    side = max(rw, rh)
                    rw = rh = side
                    if cur_pt.x() < self.start_scene_pt.x():
                        rx = self.start_scene_pt.x() - side
                    if cur_pt.y() < self.start_scene_pt.y():
                        ry = self.start_scene_pt.y() - side
                self.temp_preview_item.setRect(QRectF(rx, ry, rw, rh))

            elif self.active_tool in ("circle", "ellipse", "polygon"):
                radius = math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y())
                self.temp_preview_item.setRect(QRectF(
                    self.start_scene_pt.x() - radius,
                    self.start_scene_pt.y() - radius,
                    radius * 2.0,
                    radius * 2.0
                ))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragging_handle != SelectionHandleBox.HANDLE_NONE:
            self.dragging_handle = SelectionHandleBox.HANDLE_NONE
            self.handle_drag_start_pt = None
            if self.selection_box and self.selection_box.scene() == self:
                self.selection_box.prepareGeometryChange()
                self.selection_box.update()
            event.accept()
            return

        if self.temp_preview_item and self.start_scene_pt:
            cur_pt = self.snap_point(event.scenePos())
            if self.temp_preview_item.scene() == self:
                self.removeItem(self.temp_preview_item)
            self.temp_preview_item = None

            created_item = None
            is_shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

            if self.active_tool == "line":
                if math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y()) > 0.2:
                    created_item = CadLineItem(self.start_scene_pt, cur_pt)

            elif self.active_tool == "rect":
                rx = min(self.start_scene_pt.x(), cur_pt.x())
                ry = min(self.start_scene_pt.y(), cur_pt.y())
                rw = abs(cur_pt.x() - self.start_scene_pt.x())
                rh = abs(cur_pt.y() - self.start_scene_pt.y())
                if is_shift:
                    rw = rh = max(rw, rh)
                if rw > 0.2 and rh > 0.2:
                    created_item = CadRectItem(QRectF(rx, ry, rw, rh))

            elif self.active_tool in ("circle", "ellipse"):
                radius = math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y())
                if radius > 0.2:
                    created_item = CadCircleItem(self.start_scene_pt, radius)

            elif self.active_tool == "polygon":
                radius = math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y())
                if radius > 0.2:
                    created_item = CadPolygonItem.create_regular(self.start_scene_pt, radius, num_sides=5)

            if created_item:
                created_item.set_pen(self.active_pen_id)
                self.addItem(created_item)
                self.clearSelection()
                created_item.setSelected(True)

            self.start_scene_pt = None
            self.set_tool("select")
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, 'handle_cad_key_event'):
            if parent_widget.handle_cad_key_event(event):
                event.accept()
                return
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in list(self.selectedItems()):
                if isinstance(item, CadShapeItem) and item.scene() == self:
                    self.removeItem(item)
            self.clearSelection()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.set_tool("select")
            event.accept()
        else:
            super().keyPressEvent(event)


class CadView(QGraphicsView):
    """EzCad Viewport with mouse-centered zoom, smooth pan, and ruler updates."""
    viewScrolled = Signal()

    def __init__(self, scene: CadScene, parent=None):
        super().__init__(scene, parent)
        self.cad_scene = scene
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setBackgroundBrush(Qt.BrushStyle.NoBrush)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._is_panning = False
        self._pan_start_pos = None

        self.horizontalScrollBar().valueChanged.connect(lambda: self.viewScrolled.emit())
        self.verticalScrollBar().valueChanged.connect(lambda: self.viewScrolled.emit())

    def drawBackground(self, painter: QPainter, rect: QRectF):
        self.cad_scene.drawBackground(painter, rect)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(factor, factor)
        self.viewScrolled.emit()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        self.setFocus()
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        parent_widget = self.parentWidget()
        while parent_widget and not isinstance(parent_widget, CadCanvasWidget):
            parent_widget = parent_widget.parentWidget()
        if parent_widget and hasattr(parent_widget, 'handle_cad_key_event'):
            if parent_widget.handle_cad_key_event(event):
                event.accept()
                return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning and self._pan_start_pos:
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.viewScrolled.emit()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self._pan_start_pos = None
            if self.cad_scene.active_tool == "select":
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.viewScrolled.emit()

    def zoom_to_fit(self):
        """Fit the configured Galvo field box squarely in view with comfortable framing margins."""
        if self.viewport().width() <= 20 or self.viewport().height() <= 20:
            return
        half = self.cad_scene.field_size / 2.0
        margin = max(8.0, self.cad_scene.field_size * 0.15)
        target_w = self.cad_scene.field_size + margin * 2.0
        target_h = self.cad_scene.field_size + margin * 2.0
        self.fitInView(-half - margin, -half - margin, target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio)
        self.centerOn(0.0, 0.0)
        self.viewScrolled.emit()


class EzcadHatchDialog(QDialog):
    """
    EzCad Replica Hatch Dialog (Exact visual & functional parity with EzCad2).
    Supports Mark Contour, 3 Hatch Profiles, All Calc, Follow Edge, Cross Hatch,
    5 Hatch Types, Angle, 8-Pen palette, Line Space, Offsets, NumLoops, and Undo Hatch.
    """
    undoHatchRequested = Signal()

    HATCH_TYPES = [
        "Bidirectional",
        "Unidirectional",
        "Ring-like",
        "Optimized / Bow-tie",
        "Auto-Sorting / Block Hatch"
    ]

    def __init__(self, parent=None, hatch_profiles=None, target_items=None):
        super().__init__(parent)
        self.setWindowTitle("Hatch")
        self.setFixedSize(390, 480)
        self.target_items = target_items or []

        import copy
        self.hatch_profiles = copy.deepcopy(hatch_profiles) if hatch_profiles else {}
        for idx in [1, 2, 3]:
            if idx not in self.hatch_profiles:
                self.hatch_profiles[idx] = {
                    "enable": (idx == 1),
                    "mark_contour": True,
                    "all_calc": True,
                    "follow_edge": True,
                    "cross_hatch": False,
                    "type": "Bidirectional",
                    "angle": "45.0" if idx == 1 else ("-45.0" if idx == 2 else "90.0"),
                    "pen_no": 0,
                    "count": "1",
                    "line_space": "0.03",
                    "avg_dist": False,
                    "edge_off": "0.0",
                    "start_off": "0.0",
                    "end_off": "0.0",
                    "line_red": "0.0",
                    "num_loops": "0",
                    "loop_dist": "0.5",
                    "auto_rot": False,
                    "rot_angle": "10.0"
                }
        self.current_idx = 1
        self.current_hatch_type = "Bidirectional"
        self._syncing = False

        self._init_ui()
        self._load_profile(self.current_idx)

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background: #f0f0f0;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 11px;
            }
            QPushButton {
                background: #e1e1e1;
                border: 1px solid #707070;
                border-radius: 2px;
                padding: 2px 10px;
                min-height: 22px;
                font-size: 11px;
                color: #000000;
            }
            QPushButton:hover {
                background: #e5f1fb;
                border-color: #0078d7;
            }
            QPushButton:pressed {
                background: #cce4f7;
                border-color: #005499;
            }
            QDoubleSpinBox, QSpinBox, QLineEdit {
                background: #ffffff;
                border: 1px solid #7f9db9;
                border-radius: 0px;
                padding: 1px 3px;
                font-size: 11px;
                min-height: 19px;
                max-height: 19px;
                color: #000000;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                height: 0px;
                border: none;
            }
            QComboBox {
                background: #ffffff;
                border: 1px solid #7f9db9;
                border-radius: 0px;
                padding: 1px 3px;
                font-size: 11px;
                min-height: 19px;
                max-height: 19px;
            }
            QCheckBox, QRadioButton {
                font-size: 11px;
                spacing: 5px;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # === LEFT COLUMN: Controls ===
        left_col = QVBoxLayout()
        left_col.setSpacing(4)

        # 1. Mark Contour Checkbox & Preview Button
        row_mark = QHBoxLayout()
        self.cb_mark_contour = QCheckBox("Mark Contour")
        self.cb_mark_contour.setChecked(True)
        row_mark.addWidget(self.cb_mark_contour)

        self.btn_contour_type = QPushButton()
        self.btn_contour_type.setFixedSize(36, 22)
        self.btn_contour_type.setIcon(QIcon(self._create_contour_pixmap()))
        self.btn_contour_type.setIconSize(QSize(34, 20))
        self.btn_contour_type.setToolTip("Mark outline contour")
        row_mark.addWidget(self.btn_contour_type)
        row_mark.addStretch()
        left_col.addLayout(row_mark)

        # 2. Hatch 1 / 2 / 3 Radio Button Group in Frame
        frame_tabs = QFrame()
        frame_tabs.setStyleSheet("QFrame { background: #f8f8f8; border: 1px solid #c0c0c0; border-radius: 2px; }")
        layout_tabs = QHBoxLayout(frame_tabs)
        layout_tabs.setContentsMargins(6, 3, 6, 3)
        layout_tabs.setSpacing(14)

        self.btn_group_hatch = QButtonGroup(self)
        self.rb_hatch1 = QRadioButton("Hatch1")
        self.rb_hatch2 = QRadioButton("2")
        self.rb_hatch3 = QRadioButton("3")
        self.rb_hatch1.setChecked(True)

        self.btn_group_hatch.addButton(self.rb_hatch1, 1)
        self.btn_group_hatch.addButton(self.rb_hatch2, 2)
        self.btn_group_hatch.addButton(self.rb_hatch3, 3)

        layout_tabs.addWidget(self.rb_hatch1)
        layout_tabs.addWidget(self.rb_hatch2)
        layout_tabs.addWidget(self.rb_hatch3)
        layout_tabs.addStretch()

        self.btn_group_hatch.idToggled.connect(self._on_hatch_tab_changed)
        left_col.addWidget(frame_tabs)

        # 3. Checkboxes & Type Icon Row
        row_checks_type = QHBoxLayout()
        row_checks_type.setSpacing(8)

        v_checks = QVBoxLayout()
        v_checks.setSpacing(2)
        self.cb_enable = QCheckBox("Enable")
        self.cb_enable.setChecked(True)
        v_checks.addWidget(self.cb_enable)

        self.cb_all_calc = QCheckBox("All calc")
        self.cb_all_calc.setChecked(True)
        v_checks.addWidget(self.cb_all_calc)

        self.cb_follow_edge = QCheckBox("Follow edge once")
        self.cb_follow_edge.setChecked(True)
        v_checks.addWidget(self.cb_follow_edge)

        self.cb_cross_hatch = QCheckBox("Cross hatch")
        v_checks.addWidget(self.cb_cross_hatch)
        row_checks_type.addLayout(v_checks)

        # Type Button with graphical hatch pattern diagram
        v_type = QVBoxLayout()
        v_type.setSpacing(2)
        lbl_type = QLabel("Type")
        lbl_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_type.addWidget(lbl_type)

        self.btn_hatch_type = QPushButton()
        self.btn_hatch_type.setFixedSize(38, 38)
        self.btn_hatch_type.setToolTip("Click to cycle Hatch Pattern Type (Bidirectional, Unidirectional, Ring-like, Bow-tie, Block)")
        self.btn_hatch_type.clicked.connect(self._cycle_hatch_type)
        v_type.addWidget(self.btn_hatch_type)
        row_checks_type.addLayout(v_type)
        row_checks_type.addStretch()
        left_col.addLayout(row_checks_type)

        # 4. Angle & Pen No. Row
        row_ang_pen = QHBoxLayout()
        row_ang_pen.setSpacing(4)
        row_ang_pen.addWidget(QLabel("Angle"))
        self.sp_angle = QDoubleSpinBox()
        self.sp_angle.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_angle.setRange(-360.0, 360.0)
        self.sp_angle.setValue(45.0)
        self.sp_angle.setFixedWidth(52)
        row_ang_pen.addWidget(self.sp_angle)
        row_ang_pen.addWidget(QLabel("Deg"))
        row_ang_pen.addSpacing(6)
        row_ang_pen.addWidget(QLabel("Pen No."))

        self.cb_pen_no = QComboBox()
        self.cb_pen_no.setFixedWidth(66)
        for i in range(8):
            pm = QPixmap(14, 14)
            pm.fill(QColor(PEN_PALETTE[i]))
            p = QPainter(pm)
            p.setPen(QColor("#000000"))
            p.drawRect(0, 0, 13, 13)
            p.end()
            self.cb_pen_no.addItem(QIcon(pm), f"  {i}")
        row_ang_pen.addWidget(self.cb_pen_no)
        row_ang_pen.addStretch()
        left_col.addLayout(row_ang_pen)

        # 5. Count Row
        row_count = QHBoxLayout()
        lbl_c = QLabel("Count")
        lbl_c.setFixedWidth(82)
        row_count.addWidget(lbl_c)
        self.sp_count = QSpinBox()
        self.sp_count.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_count.setRange(1, 100)
        self.sp_count.setValue(1)
        self.sp_count.setFixedWidth(52)
        row_count.addWidget(self.sp_count)
        row_count.addStretch()
        left_col.addLayout(row_count)

        # 6. Line Space Row
        row_space = QHBoxLayout()
        lbl_ls = QLabel("Line Space")
        lbl_ls.setFixedWidth(82)
        row_space.addWidget(lbl_ls)
        self.sp_line_space = QDoubleSpinBox()
        self.sp_line_space.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_line_space.setRange(0.001, 10.0)
        self.sp_line_space.setDecimals(3)
        self.sp_line_space.setSingleStep(0.01)
        self.sp_line_space.setValue(0.03)
        self.sp_line_space.setFixedWidth(52)
        row_space.addWidget(self.sp_line_space)
        row_space.addWidget(QLabel("MM"))
        row_space.addStretch()
        left_col.addLayout(row_space)

        # 7. Average distribute line
        self.cb_avg_dist = QCheckBox("Average distribute line")
        left_col.addWidget(self.cb_avg_dist)

        # 8. Offsets
        def make_offset_row(label_text: str, default_val: float = 0.0):
            r = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(82)
            r.addWidget(lbl)
            sp = QDoubleSpinBox()
            sp.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            sp.setRange(-50.0, 50.0)
            sp.setDecimals(3)
            sp.setSingleStep(0.05)
            sp.setValue(default_val)
            sp.setFixedWidth(52)
            r.addWidget(sp)
            r.addWidget(QLabel("MM"))
            r.addStretch()
            left_col.addLayout(r)
            return sp

        self.sp_edge_off = make_offset_row("Edge Offset", 0.0)
        self.sp_start_off = make_offset_row("Start Offset", 0.0)
        self.sp_end_off = make_offset_row("End Offset", 0.0)
        self.sp_line_red = make_offset_row("Linereduction", 0.0)

        # 9. NumLoops & Loop distance
        row_loops = QHBoxLayout()
        lbl_nl = QLabel("NumLoops")
        lbl_nl.setFixedWidth(82)
        row_loops.addWidget(lbl_nl)
        self.sp_num_loops = QSpinBox()
        self.sp_num_loops.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_num_loops.setRange(0, 50)
        self.sp_num_loops.setValue(0)
        self.sp_num_loops.setFixedWidth(52)
        row_loops.addWidget(self.sp_num_loops)
        row_loops.addStretch()
        left_col.addLayout(row_loops)

        row_ld = QHBoxLayout()
        lbl_ld = QLabel("Loop distance")
        lbl_ld.setFixedWidth(82)
        row_ld.addWidget(lbl_ld)
        self.sp_loop_dist = QDoubleSpinBox()
        self.sp_loop_dist.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_loop_dist.setRange(0.001, 10.0)
        self.sp_loop_dist.setDecimals(3)
        self.sp_loop_dist.setValue(0.5)
        self.sp_loop_dist.setFixedWidth(52)
        row_ld.addWidget(self.sp_loop_dist)
        row_ld.addWidget(QLabel("MM"))
        row_ld.addStretch()
        left_col.addLayout(row_ld)

        # 10. Auto rotate hatch angle
        self.cb_auto_rot = QCheckBox("Auto rorate hatch angle")
        left_col.addWidget(self.cb_auto_rot)

        row_rot_ang = QHBoxLayout()
        row_rot_ang.setContentsMargins(18, 0, 0, 0)
        self.sp_rot_angle = QDoubleSpinBox()
        self.sp_rot_angle.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_rot_angle.setRange(-180.0, 180.0)
        self.sp_rot_angle.setValue(10.0)
        self.sp_rot_angle.setFixedWidth(52)
        row_rot_ang.addWidget(self.sp_rot_angle)
        row_rot_ang.addWidget(QLabel("Degree"))
        row_rot_ang.addStretch()
        left_col.addLayout(row_rot_ang)

        main_layout.addLayout(left_col, stretch=1)

        # === RIGHT COLUMN: Action Buttons ===
        right_col = QVBoxLayout()
        right_col.setContentsMargins(2, 4, 2, 4)
        right_col.setSpacing(8)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setFixedSize(85, 24)
        self.btn_ok.setStyleSheet("font-weight: bold; background: #e8e8e8; border: 1px solid #707070;")
        self.btn_ok.clicked.connect(self._on_ok)
        right_col.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedSize(85, 24)
        self.btn_cancel.clicked.connect(self.reject)
        right_col.addWidget(self.btn_cancel)

        right_col.addSpacing(14)

        self.btn_undo = QPushButton("Undo Hatch")
        self.btn_undo.setFixedSize(95, 26)
        self.btn_undo.setToolTip("Remove hatch fill lines from selected shape(s)")
        self.btn_undo.clicked.connect(self._on_undo_hatch)
        right_col.addWidget(self.btn_undo)

        right_col.addStretch()
        main_layout.addLayout(right_col)

    def _create_contour_pixmap(self) -> QPixmap:
        pm = QPixmap(34, 20)
        pm.fill(QColor("#f4f4f4"))
        p = QPainter(pm)
        p.setPen(QPen(QColor("#808080"), 1))
        p.drawRect(0, 0, 33, 19)
        p.setPen(QPen(QColor("#0033bb"), 1))
        p.drawLine(3, 4, 30, 4)
        p.drawLine(3, 8, 30, 8)
        p.drawLine(3, 12, 30, 12)
        p.drawLine(3, 16, 30, 16)
        p.setPen(QPen(QColor("#cc0000"), 1))
        p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        p.drawText(QRectF(0, 0, 34, 20), Qt.AlignmentFlag.AlignCenter, "1")
        p.end()
        return pm

    def _create_hatch_type_pixmap(self, type_str: str) -> QPixmap:
        pm = QPixmap(36, 36)
        pm.fill(QColor("#ffffff"))
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QPen(QColor("#7f9db9"), 1))
        p.drawRect(0, 0, 35, 35)

        blue_pen = QPen(QColor("#0022cc"), 1.4)
        red_pen = QPen(QColor("#dd0000"), 1.2)

        if "Uni" in type_str:
            p.setPen(blue_pen)
            for y in [9, 18, 27]:
                p.drawLine(6, y, 28, y)
                p.drawLine(24, y - 2, 28, y)
                p.drawLine(24, y + 2, 28, y)
            p.setPen(QPen(QColor("#dd0000"), 1.0, Qt.PenStyle.DashLine))
            p.drawLine(28, 9, 6, 18)
            p.drawLine(28, 18, 6, 27)
        elif "Ring" in type_str:
            p.setPen(blue_pen)
            p.drawRect(6, 6, 24, 24)
            p.setPen(red_pen)
            p.drawRect(11, 11, 14, 14)
        elif "Bow" in type_str or "Optimized" in type_str:
            p.setPen(blue_pen)
            p.drawLine(6, 8, 30, 8)
            p.drawLine(30, 8, 30, 18)
            p.drawLine(30, 18, 6, 18)
            p.drawLine(6, 18, 6, 28)
            p.drawLine(6, 28, 30, 28)
        elif "Block" in type_str or "Sort" in type_str:
            p.setPen(blue_pen)
            p.drawRect(6, 6, 10, 10)
            p.drawRect(20, 6, 10, 10)
            p.drawRect(6, 20, 10, 10)
            p.drawRect(20, 20, 10, 10)
        else:  # Bidirectional
            p.setPen(blue_pen)
            p.drawLine(6, 9, 28, 9)
            p.drawLine(24, 7, 28, 9)
            p.drawLine(24, 11, 28, 9)

            p.drawLine(28, 18, 6, 18)
            p.drawLine(10, 16, 6, 18)
            p.drawLine(10, 20, 6, 18)

            p.drawLine(6, 27, 28, 27)
            p.drawLine(24, 25, 28, 27)
            p.drawLine(24, 29, 28, 27)

            p.setPen(red_pen)
            p.drawLine(28, 9, 28, 18)
            p.drawLine(6, 18, 6, 27)

        p.end()
        return pm

    def _update_type_button(self):
        pix = self._create_hatch_type_pixmap(self.current_hatch_type)
        self.btn_hatch_type.setIcon(QIcon(pix))
        self.btn_hatch_type.setIconSize(QSize(36, 36))
        self.btn_hatch_type.setToolTip(f"Hatch Type: {self.current_hatch_type} (Click to cycle)")

    def _cycle_hatch_type(self):
        try:
            curr_idx = self.HATCH_TYPES.index(self.current_hatch_type)
        except ValueError:
            curr_idx = 0
        next_idx = (curr_idx + 1) % len(self.HATCH_TYPES)
        self.current_hatch_type = self.HATCH_TYPES[next_idx]
        self._update_type_button()

    def _load_profile(self, idx: int):
        self._syncing = True
        try:
            self.current_idx = idx
            if idx not in self.hatch_profiles:
                self.hatch_profiles[idx] = {
                    "enable": False,
                    "mark_contour": True,
                    "all_calc": True,
                    "follow_edge": True,
                    "cross_hatch": False,
                    "type": "Bidirectional",
                    "angle": "45",
                    "pen_no": 0,
                    "count": "1",
                    "line_space": "0.03",
                    "avg_dist": False,
                    "edge_off": "0",
                    "start_off": "0",
                    "end_off": "0",
                    "line_red": "0",
                    "num_loops": "0",
                    "loop_dist": "0.5",
                    "auto_rot": False,
                    "rot_angle": "10.0"
                }
            p = self.hatch_profiles[idx]
            self.cb_mark_contour.setChecked(bool(p.get("mark_contour", True)))
            self.cb_enable.setChecked(bool(p.get("enable", True)))
            self.cb_all_calc.setChecked(bool(p.get("all_calc", True)))
            self.cb_follow_edge.setChecked(bool(p.get("follow_edge", True)))
            self.cb_cross_hatch.setChecked(bool(p.get("cross_hatch", False)))

            h_type = str(p.get("type", "Bidirectional"))
            self.current_hatch_type = h_type
            self._update_type_button()

            self.sp_angle.setValue(float(p.get("angle", 45.0) or 45.0))
            pen_idx = max(0, min(7, int(p.get("pen_no", 0) or 0)))
            self.cb_pen_no.setCurrentIndex(pen_idx)

            self.sp_count.setValue(int(p.get("count", 1) or 1))
            self.sp_line_space.setValue(float(p.get("line_space", 0.03) or 0.03))
            self.cb_avg_dist.setChecked(bool(p.get("avg_dist", False)))

            self.sp_edge_off.setValue(float(p.get("edge_off", 0.0) or 0.0))
            self.sp_start_off.setValue(float(p.get("start_off", 0.0) or 0.0))
            self.sp_end_off.setValue(float(p.get("end_off", 0.0) or 0.0))
            self.sp_line_red.setValue(float(p.get("line_red", 0.0) or 0.0))

            self.sp_num_loops.setValue(int(p.get("num_loops", 0) or 0))
            self.sp_loop_dist.setValue(float(p.get("loop_dist", 0.5) or 0.5))

            self.cb_auto_rot.setChecked(bool(p.get("auto_rot", False)))
            self.sp_rot_angle.setValue(float(p.get("rot_angle", 10.0) or 10.0))
        finally:
            self._syncing = False

    def _save_profile(self, idx: int):
        if self._syncing:
            return
        if idx not in self.hatch_profiles:
            self.hatch_profiles[idx] = {}
        p = self.hatch_profiles[idx]
        p["mark_contour"] = self.cb_mark_contour.isChecked()
        p["enable"] = self.cb_enable.isChecked()
        p["all_calc"] = self.cb_all_calc.isChecked()
        p["follow_edge"] = self.cb_follow_edge.isChecked()
        p["cross_hatch"] = self.cb_cross_hatch.isChecked()
        p["type"] = self.current_hatch_type
        p["angle"] = f"{self.sp_angle.value():.1f}"
        p["pen_no"] = self.cb_pen_no.currentIndex()
        p["count"] = str(self.sp_count.value())
        p["line_space"] = f"{self.sp_line_space.value():.4f}".rstrip('0').rstrip('.')
        p["avg_dist"] = self.cb_avg_dist.isChecked()
        p["edge_off"] = f"{self.sp_edge_off.value():.3f}".rstrip('0').rstrip('.')
        p["start_off"] = f"{self.sp_start_off.value():.3f}".rstrip('0').rstrip('.')
        p["end_off"] = f"{self.sp_end_off.value():.3f}".rstrip('0').rstrip('.')
        p["line_red"] = f"{self.sp_line_red.value():.3f}".rstrip('0').rstrip('.')
        p["num_loops"] = str(self.sp_num_loops.value())
        p["loop_dist"] = f"{self.sp_loop_dist.value():.3f}".rstrip('0').rstrip('.')
        p["auto_rot"] = self.cb_auto_rot.isChecked()
        p["rot_angle"] = f"{self.sp_rot_angle.value():.1f}"

    def _on_hatch_tab_changed(self, button_id: int, checked: bool):
        if not checked or self._syncing:
            return
        self._save_profile(self.current_idx)
        self.current_idx = button_id
        self._load_profile(button_id)

    def _on_ok(self):
        self._save_profile(self.current_idx)
        self.accept()

    def _on_undo_hatch(self):
        self.undoHatchRequested.emit()
        self.accept()


class CadCanvasWidget(QWidget):
    """
    EzCad-Lite Complete Laser CAD Studio.
    Faithful replica of EzCad2 with:
    - Pure white bed sheet sized strictly from machine config
    - Drop shadow, millimeter grid, center crosshairs
    - Top interactive millimeter ruler and Left vertical ruler (Y+ up)
    - 2-Row Top Toolbars (File, Edit, Alignment, Transform, Hatch 'H', Zoom)
    - Left docks: Object list & Object property with 3x3 9-point anchor selector
    - Left vertical tool palette (Select, Line, Rect, Circle, Polygon, Text, QR, Barcode, Image, Hatch)
    - Right dock: Marking parameter (8-Pen layer table, quick color swatches, laser params)
    - Bottom execution bar: Red(F1) guide framing, Mark(F2) laser marking, continuous, part counter, status bar
    """
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

        # Initial field size from config
        init_size = self._get_configured_field_size()
        self.scene = CadScene(field_size_mm=init_size, parent=self)
        self.view = CadView(self.scene, parent=self)

        # Pen parameters model (8 Pens: 0 to 7)
        self.pen_params = []
        default_speeds = [2000, 1500, 1000, 2500, 3000, 1200, 1800, 800]
        default_powers = [60.0, 70.0, 80.0, 50.0, 40.0, 75.0, 65.0, 90.0]
        default_freqs = [70.0, 50.0, 40.0, 80.0, 90.0, 45.0, 60.0, 35.0]

        for i in range(8):
            self.pen_params.append({
                "loop": 1,
                "speed": default_speeds[i],
                "power": default_powers[i],
                "freq": default_freqs[i],
                "start_tc": 300,
                "laser_off_tc": 100,
                "end_tc": 300,
                "poly_tc": 100,
                "on": True
            })

        self.current_pen_idx = 0
        self.part_counter = 0
        self.total_counter = 0
        self.is_framing = False
        self.aspect_ratio_locked = True
        self._syncing_props = False
        self._syncing_text_props = False

        # EzCad Text Defaults: Arial, 10.0mm, 0.0mm space
        self.default_font_family = "Arial"
        self.default_font_height = 10.0
        self.default_text_space = 0.0
        self.scene.default_font_family = self.default_font_family
        self.scene.default_font_height = self.default_font_height
        self.scene.default_text_space = self.default_text_space

        # EzCad 3 Hatch Profiles (matching main.py program page and EzCad Hatch dialog image)
        self.hatch_profiles = {
            1: {
                "enable": True,
                "mark_contour": True,
                "all_calc": True,
                "follow_edge": True,
                "cross_hatch": False,
                "type": "Bidirectional",
                "angle": "45",
                "pen_no": 0,
                "count": "1",
                "line_space": "0.03",
                "avg_dist": False,
                "edge_off": "0",
                "start_off": "0",
                "end_off": "0",
                "line_red": "0",
                "num_loops": "0",
                "loop_dist": "0.5",
                "auto_rot": False,
                "rot_angle": "10.0"
            },
            2: {
                "enable": False,
                "mark_contour": True,
                "all_calc": True,
                "follow_edge": True,
                "cross_hatch": False,
                "type": "Bidirectional",
                "angle": "90",
                "pen_no": 1,
                "count": "1",
                "line_space": "0.03",
                "avg_dist": False,
                "edge_off": "0",
                "start_off": "0",
                "end_off": "0",
                "line_red": "0",
                "num_loops": "0",
                "loop_dist": "0.5",
                "auto_rot": False,
                "rot_angle": "10.0"
            },
            3: {
                "enable": False,
                "mark_contour": True,
                "all_calc": True,
                "follow_edge": True,
                "cross_hatch": False,
                "type": "Bidirectional",
                "angle": "0",
                "pen_no": 2,
                "count": "1",
                "line_space": "0.03",
                "avg_dist": False,
                "edge_off": "0",
                "start_off": "0",
                "end_off": "0",
                "line_red": "0",
                "num_loops": "0",
                "loop_dist": "0.5",
                "auto_rot": False,
                "rot_angle": "10.0"
            }
        }

        self.is_marking = False
        self._abort_requested = False
        self.framing_rect_item = None
        self.preview_thread = None
        self.exec_thread = None

        self._start_time = time.time()
        self._power_timer = QTimer(self)
        self._power_timer.setInterval(1000)
        self._power_timer.timeout.connect(self._update_power_on_timer)
        self._power_timer.start()

        self._init_ui()
        self._connect_signals()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._clipboard_items = []

        # Global Keyboard Shortcuts: F1 (Red Guide), F2 (Mark), Escape (Stop/Abort)
        self._shortcut_f1 = QShortcut(QKeySequence(Qt.Key.Key_F1), self, self._toggle_red_light)
        self._shortcut_f1.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._shortcut_f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self, self._execute_mark)
        self._shortcut_f2.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._shortcut_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self._on_escape_pressed)
        self._shortcut_esc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

    def _get_configured_field_size(self) -> float:
        """Dynamically read field_size from config.ini [GalvoField] or UI."""
        val = 70.0
        if self.main_window:
            # 1. Check live UI LineEdit if available
            if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'fieldsizeconfLineEdit'):
                txt = self.main_window.ui.fieldsizeconfLineEdit.text().strip()
                if txt:
                    try:
                        return float(txt)
                    except:
                        pass
            # 2. Check configgalvo_widgets map
            if hasattr(self.main_window, 'configgalvo_widgets') and hasattr(self.main_window.configgalvo_widgets, 'fieldsizeconf'):
                try:
                    ui_val = self.main_window.wh.invokeMethod(self.main_window.configgalvo_widgets.fieldsizeconf, "get")
                    if ui_val:
                        return float(ui_val)
                except:
                    pass
            # 3. Check config handler (self.ch)
            if hasattr(self.main_window, 'ch'):
                try:
                    cval = self.main_window.ch.getValues("GalvoField", "field_size")
                    if cval:
                        return float(cval)
                except:
                    pass
            # 4. Check galvo_config
            if hasattr(self.main_window, 'galvo_config') and hasattr(self.main_window.galvo_config, 'field_size'):
                try:
                    return float(self.main_window.galvo_config.field_size)
                except:
                    pass
        return val

    def refresh_field_size(self):
        """Public method to re-read field size and redraw scene."""
        new_size = self._get_configured_field_size()
        self.scene.set_field_size(new_size)
        self.view.zoom_to_fit()
        self._update_status_bar(0.0, 0.0)

    def _dialog_set_field_size(self):
        cur_size = self.scene.field_size
        new_size, ok = QInputDialog.getDouble(
            self, "Galvo Field Size",
            "Enter Galvo Field Size (mm):",
            value=cur_size, min=5.0, max=1000.0, decimals=2
        )
        if ok and new_size > 0:
            self.scene.set_field_size(new_size)
            if self.main_window:
                if hasattr(self.main_window, 'ch'):
                    self.main_window.ch.addParameter("GalvoField", "field_size", f"{new_size:.1f}")
                    if hasattr(self.main_window, 'config_file_path'):
                        self.main_window.ch.updateFile(self.main_window.config_file_path)
                if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'fieldsizeconfLineEdit'):
                    self.main_window.ui.fieldsizeconfLineEdit.setText(f"{new_size:.1f}")
                elif hasattr(self.main_window, 'configgalvo_widgets') and hasattr(self.main_window.configgalvo_widgets, 'fieldsizeconf'):
                    self.main_window.wh.invokeMethod(self.main_window.configgalvo_widgets.fieldsizeconf, "set", f"{new_size:.1f}")
            self.view.zoom_to_fit()
            self._update_status_bar(0.0, 0.0)

    def showEvent(self, event):
        """Auto-refresh field size and laser parameters whenever CAD page is shown."""
        super().showEvent(event)
        new_size = self._get_configured_field_size()
        self.scene.set_field_size(new_size)
        # By default, ALWAYS frame and center the field size view when CAD page is opened
        self.view.zoom_to_fit()
        QTimer.singleShot(0, self.view.zoom_to_fit)
        QTimer.singleShot(60, self.view.zoom_to_fit)
        self.view.setFocus()
        QTimer.singleShot(100, self.view.setFocus)
        self._update_status_bar(0.0, 0.0)

        # Synchronize live laser power and frequency from the Laser page / main window
        if self.main_window:
            pwr = None
            if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'galvolaserpowerHorizontalSlider_2'):
                try:
                    pwr = float(self.main_window.ui.galvolaserpowerHorizontalSlider_2.value())
                except Exception:
                    pass
            elif hasattr(self.main_window, 'pgm_laserpower') and self.main_window.pgm_laserpower is not None:
                pwr = float(self.main_window.pgm_laserpower)

            freq = None
            if hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'galvolaserfreqHorizontalSlider'):
                try:
                    freq = float(self.main_window.ui.galvolaserfreqHorizontalSlider.value())
                except Exception:
                    pass
            elif hasattr(self.main_window, 'pgm_laserfreq') and self.main_window.pgm_laserfreq is not None:
                freq = float(self.main_window.pgm_laserfreq)

            if pwr is not None and hasattr(self, 'sp_power') and 0 <= self.current_pen_idx < len(self.pen_params):
                self.pen_params[self.current_pen_idx]["power"] = pwr
                self.sp_power.blockSignals(True)
                self.sp_power.setValue(pwr)
                self.sp_power.blockSignals(False)

            if freq is not None and hasattr(self, 'sp_freq') and 0 <= self.current_pen_idx < len(self.pen_params):
                self.pen_params[self.current_pen_idx]["freq"] = freq
                self.sp_freq.blockSignals(True)
                self.sp_freq.setValue(freq)
                self.sp_freq.blockSignals(False)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Apply EzCad Classic Windows Desktop Styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 11px;
                color: #222222;
            }
            QToolBar {
                background: #f4f4f4;
                border-bottom: 1px solid #d0d0d0;
                padding: 2px;
                spacing: 2px;
            }
            QToolButton, QPushButton {
                background: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 2px;
                padding: 3px 6px;
                min-height: 18px;
            }
            QToolButton:hover, QPushButton:hover {
                background: #d8e8f8;
                border-color: #70a0d0;
            }
            QToolButton:pressed, QPushButton:pressed {
                background: #b8d0e8;
            }
            QToolButton:checked, QPushButton:checked {
                background: #cde0f5;
                border: 1px solid #3388dd;
            }
            QFrame#dockFrame {
                background: #f8f8f8;
                border: 1px solid #c8c8c8;
            }
            QLabel#dockTitle {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dbe6f3, stop:1 #b0cbe8);
                color: #103060;
                font-weight: bold;
                padding: 3px 6px;
                border-bottom: 1px solid #9bbcdb;
            }
            QTableWidget {
                background: #ffffff;
                gridline-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                selection-background-color: #3388dd;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background: #eeeeee;
                border: 1px solid #d0d0d0;
                padding: 2px 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QDoubleSpinBox, QSpinBox, QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #b0b0b0;
                border-radius: 1px;
                padding: 2px;
                min-height: 18px;
            }
        """)

        # 1. Top Menu Bar
        menu_bar = self._create_menu_bar()
        main_layout.addWidget(menu_bar)

        # 2. Top Toolbars (2 Rows)
        tb_row1 = self._create_toolbar_row1()
        tb_row2 = self._create_toolbar_row2()
        main_layout.addWidget(tb_row1)
        main_layout.addWidget(tb_row2)

        # 3. Main Workspace Splitter (Left Docks | Left Tools | Center Viewport | Right Dock)
        workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        workspace_splitter.setHandleWidth(3)

        # --- Left Docks Container (Object list & Object property) ---
        left_dock_widget = self._create_left_docks()
        workspace_splitter.addWidget(left_dock_widget)

        # --- Left Tool Palette (Vertical Toolbar) ---
        left_tool_bar = self._create_left_tool_palette()
        workspace_splitter.addWidget(left_tool_bar)

        # --- Center Viewport with Rulers ---
        center_container = self._create_center_viewport()
        workspace_splitter.addWidget(center_container)

        # --- Right Dock Container (Marking parameter) ---
        right_dock_widget = self._create_right_dock()
        workspace_splitter.addWidget(right_dock_widget)

        # Set splitter sizes: Left 180px, ToolBar 34px, Center 680px, Right 220px
        workspace_splitter.setSizes([185, 36, 680, 220])
        main_layout.addWidget(workspace_splitter, stretch=1)

        # 4. Bottom Execution & Control Bar
        bottom_bar = self._create_bottom_execution_bar()
        main_layout.addWidget(bottom_bar)

    def _create_menu_bar(self) -> QMenuBar:
        mb = QMenuBar()
        mb.setStyleSheet("background: #f0f0f0; border-bottom: 1px solid #d0d0d0;")

        # File Menu
        file_menu = mb.addMenu("&File")
        file_menu.addAction("New", self._on_new_file, QKeySequence("Ctrl+N"))
        file_menu.addAction("Open...", self._on_open_file, QKeySequence("Ctrl+O"))
        file_menu.addAction("Save", self._on_save_file, QKeySequence("Ctrl+S"))
        file_menu.addSeparator()
        file_menu.addAction("Import Vector (DXF)...", self._import_dxf)
        file_menu.addAction("Import Image (BMP, PNG)...", self._import_image)
        file_menu.addAction("Export DXF...", self._export_dxf)
        file_menu.addSeparator()
        file_menu.addAction("Clear All", self._clear_all)

        # Edit Menu
        edit_menu = mb.addMenu("&Edit")
        edit_menu.addAction("Delete Selected", self._delete_selected, QKeySequence("Del"))
        edit_menu.addAction("Select All", self._select_all, QKeySequence("Ctrl+A"))
        edit_menu.addSeparator()
        edit_menu.addAction("Center to (0,0)", self._center_to_origin)
        edit_menu.addAction("Lock Object", lambda: self._toggle_lock(True))
        edit_menu.addAction("Unlock Object", lambda: self._toggle_lock(False))

        # Draw Menu
        draw_menu = mb.addMenu("&Draw")
        draw_menu.addAction("Line", lambda: self._select_tool("line"))
        draw_menu.addAction("Rectangle", lambda: self._select_tool("rect"))
        draw_menu.addAction("Circle / Ellipse", lambda: self._select_tool("circle"))
        draw_menu.addAction("Polygon", lambda: self._select_tool("polygon"))
        draw_menu.addAction("Text (F)", lambda: self._select_tool("text"))
        draw_menu.addAction("2D Barcode / QR", lambda: self._select_tool("barcode"))
        draw_menu.addAction("Hatch (H)", self._open_hatch_dialog)

        # Modify Menu
        mod_menu = mb.addMenu("&Modify")
        mod_menu.addAction("Align Left", lambda: self._align_shapes("left"))
        mod_menu.addAction("Align Right", lambda: self._align_shapes("right"))
        mod_menu.addAction("Align Top", lambda: self._align_shapes("top"))
        mod_menu.addAction("Align Bottom", lambda: self._align_shapes("bottom"))
        mod_menu.addAction("Align Center X", lambda: self._align_shapes("center_x"))
        mod_menu.addAction("Align Center Y", lambda: self._align_shapes("center_y"))
        mod_menu.addSeparator()
        mod_menu.addAction("Mirror Horizontal", lambda: self._mirror_shapes(horizontal=True))
        mod_menu.addAction("Mirror Vertical", lambda: self._mirror_shapes(horizontal=False))

        # View Menu
        view_menu = mb.addMenu("&View")
        view_menu.addAction("Zoom In", lambda: self.view.scale(1.2, 1.2))
        view_menu.addAction("Zoom Out", lambda: self.view.scale(1.0 / 1.2, 1.0 / 1.2))
        view_menu.addAction("Fit Bed", self.view.zoom_to_fit)
        view_menu.addSeparator()
        view_menu.addAction("Set Field Size...", self._dialog_set_field_size)

        # Laser Menu
        laser_menu = mb.addMenu("&Laser")
        laser_menu.addAction("Red Light Guide (F1)", self._toggle_red_light, QKeySequence("F1"))
        laser_menu.addAction("Mark (F2)", self._execute_mark, QKeySequence("F2"))

        # Help Menu
        help_menu = mb.addMenu("&Help")
        help_menu.addAction("About EzCad CAD Studio", lambda: QMessageBox.about(self, "EzCad CAD Studio", "EzCad2 Replica CAD Studio\nField: Millimeter Galvo Laser Coordinates\nJCZ / Galvo Motion Engine"))

        return mb

    def _create_toolbar_row1(self) -> QToolBar:
        tb = QToolBar("File and Transform")
        tb.setIconSize(QSize(18, 18))

        btn_new = tb.addAction("New")
        btn_new.setToolTip("New File (Ctrl+N)")
        btn_new.triggered.connect(self._on_new_file)

        btn_open = tb.addAction("Open")
        btn_open.setToolTip("Open File (Ctrl+O)")
        btn_open.triggered.connect(self._on_open_file)

        btn_save = tb.addAction("Save")
        btn_save.setToolTip("Save File (Ctrl+S)")
        btn_save.triggered.connect(self._on_save_file)

        tb.addSeparator()

        btn_cut = tb.addAction("Cut")
        btn_cut.triggered.connect(self._delete_selected)

        btn_del = tb.addAction("Del")
        btn_del.setToolTip("Delete Selected Shape (Del)")
        btn_del.triggered.connect(self._delete_selected)

        tb.addSeparator()

        # The classic EzCad Hatch 'H' icon
        self.btn_hatch = QPushButton("H")
        self.btn_hatch.setToolTip("Hatch Fill (H) - Scanline vector infill")
        self.btn_hatch.setStyleSheet("font-weight: bold; font-size: 13px; color: #2c3e50; min-width: 24px;")
        self.btn_hatch.clicked.connect(self._open_hatch_dialog)
        tb.addWidget(self.btn_hatch)

        tb.addSeparator()

        btn_zin = tb.addAction("Zoom +")
        btn_zin.triggered.connect(lambda: self.view.scale(1.25, 1.25))

        btn_zout = tb.addAction("Zoom -")
        btn_zout.triggered.connect(lambda: self.view.scale(0.8, 0.8))

        btn_zfit = tb.addAction("Fit Bed")
        btn_zfit.triggered.connect(self.view.zoom_to_fit)

        tb.addSeparator()

        self.cb_snap = QCheckBox("Snap")
        self.cb_snap.setChecked(True)
        self.cb_snap.setToolTip("Snap cursor to 1mm millimeter grid")
        self.cb_snap.toggled.connect(lambda c: setattr(self.scene, 'snap_enabled', c))
        tb.addWidget(self.cb_snap)

        return tb

    def _create_toolbar_row2(self) -> QToolBar:
        tb = QToolBar("Alignment and Transform")
        tb.setIconSize(QSize(18, 18))

        btn_origin = tb.addAction("Center (0,0)")
        btn_origin.setToolTip("Move selected object to Origin (0,0)")
        btn_origin.triggered.connect(self._center_to_origin)

        tb.addSeparator()

        btn_al = tb.addAction("Align L")
        btn_al.setToolTip("Align Left")
        btn_al.triggered.connect(lambda: self._align_shapes("left"))

        btn_ar = tb.addAction("Align R")
        btn_ar.setToolTip("Align Right")
        btn_ar.triggered.connect(lambda: self._align_shapes("right"))

        btn_at = tb.addAction("Align T")
        btn_at.setToolTip("Align Top")
        btn_at.triggered.connect(lambda: self._align_shapes("top"))

        btn_ab = tb.addAction("Align B")
        btn_ab.setToolTip("Align Bottom")
        btn_ab.triggered.connect(lambda: self._align_shapes("bottom"))

        btn_acx = tb.addAction("Align CX")
        btn_acx.setToolTip("Align Center X")
        btn_acx.triggered.connect(lambda: self._align_shapes("center_x"))

        btn_acy = tb.addAction("Align CY")
        btn_acy.setToolTip("Align Center Y")
        btn_acy.triggered.connect(lambda: self._align_shapes("center_y"))

        tb.addSeparator()

        btn_lock = tb.addAction("Lock")
        btn_lock.setToolTip("Lock selected entity")
        btn_lock.triggered.connect(lambda: self._toggle_lock(True))

        btn_unlock = tb.addAction("Unlock")
        btn_unlock.setToolTip("Unlock selected entity")
        btn_unlock.triggered.connect(lambda: self._toggle_lock(False))

        tb.addSeparator()

        btn_mh = tb.addAction("Mirror X")
        btn_mh.setToolTip("Mirror Horizontal")
        btn_mh.triggered.connect(lambda: self._mirror_shapes(horizontal=True))

        btn_mv = tb.addAction("Mirror Y")
        btn_mv.setToolTip("Mirror Vertical")
        btn_mv.triggered.connect(lambda: self._mirror_shapes(horizontal=False))

        return tb

    def _create_left_docks(self) -> QWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(4)

        # --- 1. Object List Dock ---
        list_frame = QFrame()
        list_frame.setObjectName("dockFrame")
        l_layout = QVBoxLayout(list_frame)
        l_layout.setContentsMargins(1, 1, 1, 1)
        l_layout.setSpacing(2)

        title_list = QLabel("Object list")
        title_list.setObjectName("dockTitle")
        l_layout.addWidget(title_list)

        self.table_objects = QTableWidget(0, 2)
        self.table_objects.setHorizontalHeaderLabels(["Name", "Type"])
        self.table_objects.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_objects.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_objects.verticalHeader().setVisible(False)
        self.table_objects.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_objects.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.table_objects.installEventFilter(self)
        l_layout.addWidget(self.table_objects)

        list_frame.setMaximumHeight(110)
        vbox.addWidget(list_frame, stretch=0)

        # --- 2. Object Property Dock ---
        prop_frame = QFrame()
        prop_frame.setObjectName("dockFrame")
        p_layout = QVBoxLayout(prop_frame)
        p_layout.setContentsMargins(1, 1, 1, 1)
        p_layout.setSpacing(2)

        self.title_prop = QLabel("Object property")
        self.title_prop.setObjectName("dockTitle")
        p_layout.addWidget(self.title_prop)

        # Scroll area for properties ensuring all text controls fit cleanly without clipping
        prop_scroll = QScrollArea()
        prop_scroll.setWidgetResizable(True)
        prop_scroll.setFrameShape(QFrame.Shape.NoFrame)
        prop_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        prop_inner_widget = QWidget()
        prop_inner_layout = QVBoxLayout(prop_inner_widget)
        prop_inner_layout.setContentsMargins(2, 2, 2, 2)
        prop_inner_layout.setSpacing(3)

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setHorizontalSpacing(3)
        grid.setVerticalSpacing(2)

        grid.addWidget(QLabel("Position"), 0, 0, 1, 2)
        grid.addWidget(QLabel("Size[MM]"), 0, 2, 1, 2)

        # X & Width
        grid.addWidget(QLabel("X"), 1, 0)
        self.sp_pos_x = QDoubleSpinBox()
        self.sp_pos_x.setRange(-500.0, 500.0)
        self.sp_pos_x.setDecimals(3)
        grid.addWidget(self.sp_pos_x, 1, 1)

        self.sp_size_w = QDoubleSpinBox()
        self.sp_size_w.setRange(0.01, 1000.0)
        self.sp_size_w.setDecimals(3)
        self.sp_size_w.valueChanged.connect(self._on_width_spin_changed)
        grid.addWidget(self.sp_size_w, 1, 2, 1, 2)

        # Y & Height
        grid.addWidget(QLabel("Y"), 2, 0)
        self.sp_pos_y = QDoubleSpinBox()
        self.sp_pos_y.setRange(-500.0, 500.0)
        self.sp_pos_y.setDecimals(3)
        grid.addWidget(self.sp_pos_y, 2, 1)

        self.sp_size_h = QDoubleSpinBox()
        self.sp_size_h.setRange(0.01, 1000.0)
        self.sp_size_h.setDecimals(3)
        self.sp_size_h.valueChanged.connect(self._on_height_spin_changed)
        grid.addWidget(self.sp_size_h, 2, 2, 1, 2)

        # Z / Angle & Lock Aspect + 9-point Anchor
        grid.addWidget(QLabel("Z"), 3, 0)
        self.sp_rot = QDoubleSpinBox()
        self.sp_rot.setRange(-360.0, 360.0)
        self.sp_rot.setDecimals(1)
        grid.addWidget(self.sp_rot, 3, 1)

        self.btn_lock_aspect = QPushButton("🔒")
        self.btn_lock_aspect.setCheckable(True)
        self.btn_lock_aspect.setChecked(True)
        self.btn_lock_aspect.setToolTip("Lock aspect ratio")
        self.btn_lock_aspect.setFixedSize(22, 22)
        self.btn_lock_aspect.toggled.connect(lambda c: setattr(self, 'aspect_ratio_locked', c))
        grid.addWidget(self.btn_lock_aspect, 3, 2)

        self.anchor_selector = AnchorSelector()
        grid.addWidget(self.anchor_selector, 3, 3, 2, 1)

        # Action Buttons Row: Array, Input Port, Apply (matching EzCad Image 3)
        row_btn_layout = QHBoxLayout()
        row_btn_layout.setContentsMargins(0, 2, 0, 0)
        row_btn_layout.setSpacing(3)

        self.btn_array = QPushButton("Array")
        self.btn_array.setStyleSheet("font-size: 11px; padding: 2px 4px; min-height: 20px;")
        self.btn_array.clicked.connect(self._open_array_dialog)
        row_btn_layout.addWidget(self.btn_array)

        self.btn_input_port = QPushButton("Input Port")
        self.btn_input_port.setStyleSheet("font-size: 11px; padding: 2px 4px; min-height: 20px;")
        self.btn_input_port.clicked.connect(lambda: QMessageBox.information(self, "Input Port", "EzCad I/O trigger configuration."))
        row_btn_layout.addWidget(self.btn_input_port)

        self.btn_apply_prop = QPushButton("Apply")
        self.btn_apply_prop.setStyleSheet("background: #3498db; color: white; font-weight: bold; font-size: 11px; padding: 2px 4px; min-height: 20px;")
        self.btn_apply_prop.clicked.connect(self._apply_properties_to_selected)
        row_btn_layout.addWidget(self.btn_apply_prop)

        grid.addLayout(row_btn_layout, 4, 0, 1, 3)

        prop_inner_layout.addLayout(grid)

        # Dynamic subpanel for Text, Barcode, or Shape-specific details
        self.prop_detail_frame = QFrame()
        self.prop_detail_layout = QVBoxLayout(self.prop_detail_frame)
        self.prop_detail_layout.setContentsMargins(2, 2, 2, 2)
        self.prop_detail_layout.setSpacing(2)

        # Create and add the EzCad Text properties panel
        self.text_prop_widget = self._create_text_property_panel()
        self.prop_detail_layout.addWidget(self.text_prop_widget)

        prop_inner_layout.addWidget(self.prop_detail_frame)
        prop_inner_layout.addStretch()

        prop_scroll.setWidget(prop_inner_widget)
        p_layout.addWidget(prop_scroll)

        vbox.addWidget(prop_frame, stretch=1)
        return container

    def _create_left_tool_palette(self) -> QWidget:
        palette = QFrame()
        palette.setStyleSheet("""
            QFrame {
                background: #f0f0f0;
                border-right: 1px solid #c0c0c0;
            }
            QPushButton {
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                font-size: 11px;
                padding: 1px;
                border: 1px solid #c0c0c0;
                background: #e8e8e8;
            }
            QPushButton:hover {
                background: #d0e4f8;
            }
            QPushButton:checked {
                background: #bad8f8;
                border: 1px solid #2070c0;
            }
        """)
        vbox = QVBoxLayout(palette)
        vbox.setContentsMargins(2, 4, 2, 4)
        vbox.setSpacing(3)

        self.tool_buttons = {}

        def add_btn(tool_name: str, symbol: str, tooltip: str):
            b = QPushButton(symbol)
            b.setCheckable(True)
            b.setToolTip(tooltip)
            b.clicked.connect(lambda: self._select_tool(tool_name))
            vbox.addWidget(b)
            self.tool_buttons[tool_name] = b
            return b

        add_btn("select", "↖", "Pick / Select Tool")
        add_btn("line", "╱", "Line Tool")
        add_btn("rect", "▭", "Rectangle Tool")
        add_btn("circle", "◯", "Circle / Ellipse Tool")
        add_btn("polygon", "⬡", "Polygon Tool")
        add_btn("text", "fI", "Text Tool")
        add_btn("barcode", "|||", "2D Barcode / QR Tool")

        btn_img = QPushButton("🖼")
        btn_img.setToolTip("Import Bitmap Image (BMP, PNG, JPG)")
        btn_img.clicked.connect(self._import_image)
        vbox.addWidget(btn_img)

        btn_hatch = QPushButton("H")
        btn_hatch.setToolTip("Vector Hatch (H)")
        btn_hatch.clicked.connect(self._open_hatch_dialog)
        vbox.addWidget(btn_hatch)

        vbox.addStretch()

        self.tool_buttons["select"].setChecked(True)
        return palette

    def _create_center_viewport(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        # Top-left corner box
        self.corner_box = CornerBox(container)
        grid.addWidget(self.corner_box, 0, 0)

        # Top Horizontal Ruler
        self.h_ruler = HorizontalRuler(self.view, self.scene, container)
        grid.addWidget(self.h_ruler, 0, 1)

        # Left Vertical Ruler
        self.v_ruler = VerticalRuler(self.view, self.scene, container)
        grid.addWidget(self.v_ruler, 1, 0)

        # CAD Viewport
        grid.addWidget(self.view, 1, 1)

        # Sync rulers when view pans or scales
        self.view.viewScrolled.connect(self.h_ruler.update)
        self.view.viewScrolled.connect(self.v_ruler.update)

        return container

    def _create_right_dock(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("dockFrame")
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(3)

        title = QLabel("Marking parameter")
        title.setObjectName("dockTitle")
        vbox.addWidget(title)

        # --- 8-Pen Layer Table ---
        self.table_pens = QTableWidget(8, 3)
        self.table_pens.setHorizontalHeaderLabels(["Pen No.", "Color", "On/"])
        self.table_pens.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_pens.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table_pens.setColumnWidth(1, 36)
        self.table_pens.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table_pens.setColumnWidth(2, 32)
        self.table_pens.verticalHeader().setVisible(False)
        self.table_pens.setFixedHeight(160)
        self.table_pens.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        for i in range(8):
            # Pen name
            it_name = QTableWidgetItem(f"* {i} Default")
            it_name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_pens.setItem(i, 0, it_name)

            # Color swatch
            it_color = QTableWidgetItem()
            it_color.setBackground(QBrush(QColor(PEN_PALETTE[i])))
            it_color.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table_pens.setItem(i, 1, it_color)

            # On/Off status
            it_on = QTableWidgetItem("On")
            it_on.setFlags(Qt.ItemFlag.ItemIsEnabled)
            it_on.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_pens.setItem(i, 2, it_on)

        self.table_pens.itemSelectionChanged.connect(self._on_pen_row_selected)
        vbox.addWidget(self.table_pens)

        # --- Quick Color Swatches Bar ---
        swatch_layout = QHBoxLayout()
        swatch_layout.setContentsMargins(2, 1, 2, 1)
        swatch_layout.setSpacing(2)

        for i, hex_c in enumerate(PEN_PALETTE):
            btn_c = QPushButton()
            btn_c.setFixedSize(18, 18)
            btn_c.setStyleSheet(f"background-color: {hex_c}; border: 1px solid #555555; border-radius: 2px;")
            btn_c.setToolTip(f"Set Pen {i}")
            btn_c.clicked.connect(lambda checked=False, p_id=i: self._assign_pen_to_selected(p_id))
            swatch_layout.addWidget(btn_c)

        vbox.addLayout(swatch_layout)

        # Checkbox: Use default param
        self.cb_use_default = QCheckBox("Use default param")
        self.cb_use_default.setChecked(True)
        vbox.addWidget(self.cb_use_default)

        # --- Parameter Form ---
        form_grid = QGridLayout()
        form_grid.setContentsMargins(4, 2, 4, 2)
        form_grid.setHorizontalSpacing(4)
        form_grid.setVerticalSpacing(2)

        # Current pen
        form_grid.addWidget(QLabel("Current pen"), 0, 0)
        self.sp_current_pen = QSpinBox()
        self.sp_current_pen.setRange(0, 7)
        self.sp_current_pen.valueChanged.connect(self._on_current_pen_spin_changed)
        form_grid.addWidget(self.sp_current_pen, 0, 1)

        # Loop count
        form_grid.addWidget(QLabel("Loop Count"), 1, 0)
        self.sp_loop = QSpinBox()
        self.sp_loop.setRange(1, 9999)
        self.sp_loop.setValue(1)
        self.sp_loop.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_loop, 1, 1)

        # Speed (MM/Second)
        form_grid.addWidget(QLabel("Speed[MM/S]"), 2, 0)
        self.sp_speed = QDoubleSpinBox()
        self.sp_speed.setRange(1.0, 10000.0)
        self.sp_speed.setValue(2000.0)
        self.sp_speed.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_speed, 2, 1)

        # Power %
        form_grid.addWidget(QLabel("Power%"), 3, 0)
        self.sp_power = QDoubleSpinBox()
        self.sp_power.setRange(0.0, 100.0)
        self.sp_power.setValue(60.0)
        self.sp_power.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_power, 3, 1)

        # Frequency (KHz)
        form_grid.addWidget(QLabel("Freq(KHz)"), 4, 0)
        self.sp_freq = QDoubleSpinBox()
        self.sp_freq.setRange(1.0, 500.0)
        self.sp_freq.setValue(70.0)
        self.sp_freq.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_freq, 4, 1)

        # Delays
        form_grid.addWidget(QLabel("Start TC(US)"), 5, 0)
        self.sp_start_tc = QSpinBox()
        self.sp_start_tc.setRange(0, 10000)
        self.sp_start_tc.setValue(300)
        self.sp_start_tc.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_start_tc, 5, 1)

        form_grid.addWidget(QLabel("Laser Off TC"), 6, 0)
        self.sp_off_tc = QSpinBox()
        self.sp_off_tc.setRange(0, 10000)
        self.sp_off_tc.setValue(100)
        self.sp_off_tc.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_off_tc, 6, 1)

        form_grid.addWidget(QLabel("End TC(US)"), 7, 0)
        self.sp_end_tc = QSpinBox()
        self.sp_end_tc.setRange(0, 10000)
        self.sp_end_tc.setValue(300)
        self.sp_end_tc.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_end_tc, 7, 1)

        form_grid.addWidget(QLabel("Poly TC(US)"), 8, 0)
        self.sp_poly_tc = QSpinBox()
        self.sp_poly_tc.setRange(0, 10000)
        self.sp_poly_tc.setValue(100)
        self.sp_poly_tc.valueChanged.connect(self._save_active_pen_params)
        form_grid.addWidget(self.sp_poly_tc, 8, 1)

        vbox.addLayout(form_grid)

        # Advance & Library buttons
        btn_adv = QPushButton("Advance...")
        btn_adv.clicked.connect(lambda: QMessageBox.information(self, "Advance Parameters", "Laser timing delays & jump calibration applied."))
        vbox.addWidget(btn_adv)

        vbox.addStretch()
        return frame

    def _create_bottom_execution_bar(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #f0f0f0;
                border-top: 1px solid #c0c0c0;
            }
        """)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(4, 3, 4, 2)
        vbox.setSpacing(3)

        # 1. Action Buttons Row (Red(F1), Mark(F2), Checkboxes, Counter, Timers)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setContentsMargins(2, 0, 2, 0)
        ctrl_layout.setSpacing(8)

        # Red(F1) Button
        self.btn_red_light = QPushButton("Red(F1)")
        self.btn_red_light.setStyleSheet("font-weight: bold; font-size: 11px; min-width: 68px; height: 26px; background: #e8e8e8; border: 1px solid #707070;")
        self.btn_red_light.clicked.connect(self._toggle_red_light)
        ctrl_layout.addWidget(self.btn_red_light)

        # Mark(F2) Button
        self.btn_mark = QPushButton("Mark(F2)")
        self.btn_mark.setStyleSheet("font-weight: bold; font-size: 11px; min-width: 68px; height: 26px; background: #27ae60; color: white; border: 1px solid #1e8449;")
        self.btn_mark.clicked.connect(self._execute_mark)
        ctrl_layout.addWidget(self.btn_mark)

        # Execution Options
        self.cb_continuous = QCheckBox("[C]Continuous")
        ctrl_layout.addWidget(self.cb_continuous)

        self.cb_mark_select = QCheckBox("[S]Mark Select")
        ctrl_layout.addWidget(self.cb_mark_select)

        self.cb_show_contour = QCheckBox("Show contour")
        self.cb_show_contour.setChecked(True)
        ctrl_layout.addWidget(self.cb_show_contour)

        self.cb_continue_mode = QCheckBox("Continue mode")
        ctrl_layout.addWidget(self.cb_continue_mode)

        # Part Counter
        ctrl_layout.addWidget(QLabel("Part"))
        self.edit_part_no = QLineEdit("0")
        self.edit_part_no.setFixedWidth(36)
        self.edit_part_no.setFixedHeight(22)
        self.edit_part_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit_part_no.setStyleSheet("background: #ffffff; border: 1px solid #7f9db9; font-size: 11px;")
        self.edit_part_no.textChanged.connect(self._on_part_no_edited)
        ctrl_layout.addWidget(self.edit_part_no)
        self.lbl_part_no = self.edit_part_no

        self.btn_reset_counter = QPushButton("R")
        self.btn_reset_counter.setToolTip("Reset Part Counter")
        self.btn_reset_counter.setFixedSize(20, 20)
        self.btn_reset_counter.setStyleSheet("background: #e8e8e8; border: 1px solid #808080; font-size: 10px; font-weight: bold; padding: 0;")
        self.btn_reset_counter.clicked.connect(self._reset_counter)
        ctrl_layout.addWidget(self.btn_reset_counter)

        ctrl_layout.addWidget(QLabel("Total no"))
        self.edit_total_no = QLineEdit("0")
        self.edit_total_no.setFixedWidth(36)
        self.edit_total_no.setFixedHeight(22)
        self.edit_total_no.setReadOnly(True)
        self.edit_total_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit_total_no.setStyleSheet("background: #ffffff; border: 1px solid #7f9db9; font-size: 11px;")
        ctrl_layout.addWidget(self.edit_total_no)
        self.lbl_total_no = self.edit_total_no

        # Timers
        ctrl_layout.addWidget(QLabel("Power On"))
        self.lbl_power_timer = QLabel("00:00:00")
        self.lbl_power_timer.setFixedWidth(68)
        self.lbl_power_timer.setFixedHeight(22)
        self.lbl_power_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_power_timer.setStyleSheet("background: #ffffff; border: 1px solid #7f9db9; font-family: Consolas, monospace; font-size: 11px;")
        ctrl_layout.addWidget(self.lbl_power_timer)

        ctrl_layout.addStretch()
        vbox.addLayout(ctrl_layout)

        # 2. Status Bar (Coordinates & Machine Info)
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(4, 1, 4, 1)

        self.lbl_status_selection = QLabel("No object selected")
        status_layout.addWidget(self.lbl_status_selection)

        status_layout.addStretch()

        self.lbl_status_coords = QLabel("X: 0.000, Y: 0.000")
        self.lbl_status_coords.setStyleSheet("font-family: Consolas, monospace; font-weight: bold; color: #2980b9;")
        status_layout.addWidget(self.lbl_status_coords)

        sep = QLabel("|")
        sep.setStyleSheet("color: #999999;")
        status_layout.addWidget(sep)

        self.lbl_status_info = QLabel(f"Grid: 1.0mm | Field: {self.scene.field_size:.1f}×{self.scene.field_size:.1f} mm")
        self.lbl_status_info.setStyleSheet("color: #555555;")
        status_layout.addWidget(self.lbl_status_info)

        vbox.addLayout(status_layout)
        return container

    def _connect_signals(self):
        self.scene.coordinateChanged.connect(self._on_mouse_coords_changed)
        self.scene.selectionChangedCustom.connect(self._on_scene_selection_changed)
        self.scene.shapeGeometryChanged.connect(self._on_shape_geometry_changed)
        self.scene.toolChanged.connect(self._on_tool_changed_internal)

    # --- Tool and Selection Management ---
    def _select_tool(self, tool_name: str):
        self.scene.set_tool(tool_name)

    def _on_tool_changed_internal(self, tool_name: str):
        for name, btn in self.tool_buttons.items():
            btn.setChecked(name == tool_name)
        if tool_name == "select":
            self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.setCursor(Qt.CursorShape.CrossCursor)

    def _on_mouse_coords_changed(self, scene_x: float, scene_y: float):
        self.h_ruler.set_cursor_x(scene_x)
        self.v_ruler.set_cursor_y(scene_y)
        self._update_status_bar(scene_x, scene_y)

    def _update_status_bar(self, scene_x: float, scene_y: float):
        # EzCad convention: display Y as -scene_y
        self.lbl_status_coords.setText(f"X: {scene_x:+.3f}, Y: {-scene_y:+.3f}")
        self.lbl_status_info.setText(f"Grid: 1.0mm | Field: {self.scene.field_size:.1f}×{self.scene.field_size:.1f} mm")

    def _on_scene_selection_changed(self):
        self._refresh_object_list_table()
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if len(selected) == 1:
            item = selected[0]
            self.lbl_status_selection.setText(f"Selected: {item.name} ({item.shape_type})")
            self._load_item_properties(item)
        elif len(selected) > 1:
            self.lbl_status_selection.setText(f"Selected: {len(selected)} objects")
        else:
            self.lbl_status_selection.setText("No object selected")
            self._clear_property_inputs()

    def _refresh_object_list_table(self):
        self.table_objects.blockSignals(True)
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        self.table_objects.setRowCount(len(shapes))

        for row, item in enumerate(shapes):
            it_name = QTableWidgetItem(item.name)
            it_type = QTableWidgetItem(item.shape_type)
            if item.isSelected():
                it_name.setSelected(True)
                it_type.setSelected(True)
            self.table_objects.setItem(row, 0, it_name)
            self.table_objects.setItem(row, 1, it_type)

        self.table_objects.blockSignals(False)

    def _on_table_selection_changed(self):
        selected_rows = [index.row() for index in self.table_objects.selectionModel().selectedRows()]
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]

        self.scene.blockSignals(True)
        self.scene.clearSelection()
        for r in selected_rows:
            if 0 <= r < len(shapes):
                shapes[r].setSelected(True)
        self.scene.blockSignals(False)
        self.scene._on_scene_selection_changed()

    def _on_shape_geometry_changed(self, item):
        if item.isSelected():
            self._load_item_properties(item)

    def _load_item_properties(self, item: CadShapeItem):
        self._syncing_props = True
        try:
            bounds = item.sceneTransform().mapRect(item.boundingRect())
            # EzCad convention: display Y as -center_y
            cx = bounds.center().x()
            cy = -bounds.center().y()
            w = bounds.width()
            h = bounds.height()

            self.sp_pos_x.setValue(cx)
            self.sp_pos_y.setValue(cy)
            self.sp_size_w.setValue(w)
            self.sp_size_h.setValue(h)
            self.sp_rot.setValue(item.rotation())

            # Update Pen selection
            self.sp_current_pen.setValue(item.pen_id)
            self._load_pen_params_to_form(item.pen_id)

            # EzCad Text Mode: update dock title to "Text" and load text controls
            if isinstance(item, CadTextItem):
                self.title_prop.setText("Text")
                if hasattr(self, 'text_prop_widget'):
                    self.text_prop_widget.setVisible(True)
                    self._load_text_properties(item)
            else:
                self.title_prop.setText(f"{item.shape_type} property")
                if hasattr(self, 'text_prop_widget'):
                    self.text_prop_widget.setVisible(False)
        finally:
            self._syncing_props = False

    def _clear_property_inputs(self):
        self._syncing_props = True
        try:
            self.sp_pos_x.setValue(0.0)
            self.sp_pos_y.setValue(0.0)
            self.sp_size_w.setValue(0.0)
            self.sp_size_h.setValue(0.0)
            self.sp_rot.setValue(0.0)
            if hasattr(self, 'title_prop'):
                self.title_prop.setText("Object property")
            if hasattr(self, 'text_prop_widget'):
                self.text_prop_widget.setVisible(False)
        finally:
            self._syncing_props = False

    def _load_property_inputs(self):
        """Update property panel fields from current scene selection."""
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if len(selected) == 1:
            self._load_item_properties(selected[0])
        else:
            self._clear_property_inputs()

    # --- EzCad Dedicated Text Property Panel (Image 2 & 3 Parity) ---
    def _create_text_property_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(4)

        # 1. Font Type Row: Label "Font" + Combobox "TrueType Font-XXX"
        row_font_type = QHBoxLayout()
        row_font_type.setSpacing(4)
        lbl_font = QLabel("Font")
        lbl_font.setFixedWidth(36)
        lbl_font.setStyleSheet("font-size: 11px;")
        row_font_type.addWidget(lbl_font)

        self.cb_font_type = QComboBox()
        self.cb_font_type.setStyleSheet("font-size: 11px; padding: 1px 3px;")
        font_count = len(QFontDatabase.families())
        self.cb_font_type.addItems([
            f"TrueType Font-{font_count}",
            "SHX Font",
            "DotMatrix Font",
            "Barcode Font"
        ])
        row_font_type.addWidget(self.cb_font_type, stretch=1)
        layout.addLayout(row_font_type)

        # 2. Font Family Combobox (Full width): e.g. "Arial"
        self.cb_font_family = QComboBox()
        self.cb_font_family.setStyleSheet("font-size: 11px; padding: 1px 3px;")
        families = sorted(list(set(QFontDatabase.families())))
        if self.main_window and hasattr(self.main_window, 'text_parser') and self.main_window.text_parser:
            tp_fonts = list(self.main_window.text_parser.fonts.keys())
            for f in sorted(tp_fonts):
                if f not in families:
                    families.append(f)
        self.cb_font_family.addItems(families)
        default_fam = "Arial"
        if default_fam in families:
            self.cb_font_family.setCurrentText(default_fam)
        elif families:
            self.cb_font_family.setCurrentIndex(0)
        self.cb_font_family.currentTextChanged.connect(self._on_font_family_changed)
        layout.addWidget(self.cb_font_family)

        # 3. Action Buttons: [ H ] (Red hatch), [ F ] (Blue italic F), [ 💾 ] (Save floppy)
        row_btns = QHBoxLayout()
        row_btns.setSpacing(6)

        self.btn_text_hatch = QPushButton("H")
        self.btn_text_hatch.setToolTip("Hatch (H) - Toggle laser scanline infill")
        self.btn_text_hatch.setCheckable(True)
        self.btn_text_hatch.setChecked(True)
        self.btn_text_hatch.setFixedSize(30, 24)
        self.btn_text_hatch.setStyleSheet("""
            QPushButton {
                font-family: Arial, sans-serif;
                font-weight: 900;
                font-size: 13px;
                color: #cc0000;
                background: #f7f7f7;
                border: 1px solid #999999;
                border-radius: 1px;
            }
            QPushButton:hover {
                background: #ffe6e6;
                border-color: #cc0000;
            }
            QPushButton:checked {
                background: #ffcccc;
                border: 1px solid #cc0000;
                color: #990000;
            }
        """)
        self.btn_text_hatch.clicked.connect(self._toggle_text_hatch)
        row_btns.addWidget(self.btn_text_hatch)

        self.btn_text_style = QPushButton("F")
        self.btn_text_style.setToolTip("Font Style - Toggle Italic / Bold")
        self.btn_text_style.setCheckable(True)
        self.btn_text_style.setChecked(False)
        self.btn_text_style.setFixedSize(30, 24)
        self.btn_text_style.setStyleSheet("""
            QPushButton {
                font-family: 'Times New Roman', serif;
                font-style: italic;
                font-weight: bold;
                font-size: 14px;
                color: #0044cc;
                background: #f7f7f7;
                border: 1px solid #999999;
                border-radius: 1px;
            }
            QPushButton:hover {
                background: #e6f0ff;
                border-color: #0044cc;
            }
            QPushButton:checked {
                background: #cce0ff;
                border: 1px solid #0044cc;
                color: #002288;
            }
        """)
        self.btn_text_style.clicked.connect(self._toggle_text_font_style)
        row_btns.addWidget(self.btn_text_style)

        self.btn_text_save = QPushButton("💾")
        self.btn_text_save.setToolTip("Save Current Text Font Parameters as Session Default")
        self.btn_text_save.setFixedSize(30, 24)
        self.btn_text_save.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background: #f7f7f7;
                border: 1px solid #999999;
                border-radius: 1px;
            }
            QPushButton:hover {
                background: #e8e8e8;
                border-color: #555555;
            }
        """)
        self.btn_text_save.clicked.connect(self._save_text_font_defaults)
        row_btns.addWidget(self.btn_text_save)

        row_btns.addStretch()
        layout.addLayout(row_btns)

        # 4. Spacing Radios: (•) Auto TT   ( ) Equal TT   ( ) Fixed TT
        row_radios = QHBoxLayout()
        row_radios.setSpacing(2)

        self.btn_group_spacing = QButtonGroup(widget)
        self.rb_spacing_auto = QRadioButton("Auto TT")
        self.rb_spacing_auto.setToolTip("Auto character spacing based on font metrics")
        self.rb_spacing_auto.setStyleSheet("font-size: 10px; color: #cc0000; font-weight: bold;")
        self.btn_group_spacing.addButton(self.rb_spacing_auto, 0)
        row_radios.addWidget(self.rb_spacing_auto)

        self.rb_spacing_equal = QRadioButton("Equal TT")
        self.rb_spacing_equal.setToolTip("Equal inter-character spacing (Text Space)")
        self.rb_spacing_equal.setStyleSheet("font-size: 10px;")
        self.btn_group_spacing.addButton(self.rb_spacing_equal, 1)
        row_radios.addWidget(self.rb_spacing_equal)

        self.rb_spacing_fixed = QRadioButton("Fixed TT")
        self.rb_spacing_fixed.setToolTip("Fixed pitch character spacing")
        self.rb_spacing_fixed.setStyleSheet("font-size: 10px;")
        self.btn_group_spacing.addButton(self.rb_spacing_fixed, 2)
        row_radios.addWidget(self.rb_spacing_fixed)

        self.rb_spacing_auto.setChecked(True)
        self.btn_group_spacing.idToggled.connect(self._on_spacing_mode_changed)
        layout.addLayout(row_radios)

        # 5. Text Space Row: Label "Text Space" + QDoubleSpinBox (0.000)
        row_space = QHBoxLayout()
        row_space.setSpacing(4)
        lbl_space = QLabel("Text Space")
        lbl_space.setStyleSheet("font-size: 11px;")
        row_space.addWidget(lbl_space)

        self.sp_text_space = QDoubleSpinBox()
        self.sp_text_space.setRange(-50.0, 100.0)
        self.sp_text_space.setDecimals(3)
        self.sp_text_space.setSingleStep(0.1)
        self.sp_text_space.setValue(0.0)
        self.sp_text_space.setStyleSheet("font-size: 11px;")
        self.sp_text_space.valueChanged.connect(self._on_text_space_changed)
        row_space.addWidget(self.sp_text_space)
        layout.addLayout(row_space)

        # 6. Height Row: Label "Height" + QDoubleSpinBox (10.000MM)
        row_height = QHBoxLayout()
        row_height.setSpacing(4)
        lbl_height = QLabel("Height")
        lbl_height.setStyleSheet("font-size: 11px;")
        row_height.addWidget(lbl_height)

        self.sp_text_height = QDoubleSpinBox()
        self.sp_text_height.setRange(0.1, 500.0)
        self.sp_text_height.setDecimals(3)
        self.sp_text_height.setSingleStep(0.5)
        self.sp_text_height.setSuffix("MM")
        self.sp_text_height.setValue(10.0)
        self.sp_text_height.setStyleSheet("font-size: 11px;")
        self.sp_text_height.valueChanged.connect(self._on_text_height_changed)
        row_height.addWidget(self.sp_text_height)
        layout.addLayout(row_height)

        # 7. Text Label + Multi-line Text Edit Area
        lbl_text = QLabel("Text")
        lbl_text.setStyleSheet("font-size: 11px;")
        layout.addWidget(lbl_text)

        self.txt_text_content = QTextEdit()
        self.txt_text_content.setPlainText("TEXT")
        self.txt_text_content.setFixedHeight(58)
        self.txt_text_content.setStyleSheet("""
            QTextEdit {
                font-family: 'Leelawadee UI Semilight', Arial, sans-serif;
                font-size: 11px;
                background: #ffffff;
                border: 1px solid #b0b0b0;
            }
        """)
        self.txt_text_content.textChanged.connect(self._on_text_content_changed)
        layout.addWidget(self.txt_text_content)

        # 8. Checkbox: [ ] Enable variable Text
        self.cb_enable_variable = QCheckBox("Enable variable Text")
        self.cb_enable_variable.setStyleSheet("font-size: 11px;")
        self.cb_enable_variable.toggled.connect(self._on_enable_variable_toggled)
        layout.addWidget(self.cb_enable_variable)

        # 9. Variable Text Options Container
        self.var_text_container = QWidget()
        var_layout = QVBoxLayout(self.var_text_container)
        var_layout.setContentsMargins(4, 2, 2, 2)
        var_layout.setSpacing(2)

        row_vtype = QHBoxLayout()
        row_vtype.addWidget(QLabel("Type:"))
        self.cb_var_type = QComboBox()
        self.cb_var_type.addItems(["Serial No.", "Date (YYYY-MM-DD)", "Time (HH:MM:SS)"])
        self.cb_var_type.currentTextChanged.connect(self._on_var_type_changed)
        row_vtype.addWidget(self.cb_var_type)
        var_layout.addLayout(row_vtype)

        self.var_serial_widget = QWidget()
        self.var_serial_row = QHBoxLayout(self.var_serial_widget)
        self.var_serial_row.setContentsMargins(0, 0, 0, 0)
        self.var_serial_row.addWidget(QLabel("Cur:"))
        self.sp_var_cur = QSpinBox()
        self.sp_var_cur.setRange(0, 999999)
        self.sp_var_cur.setValue(1)
        self.sp_var_cur.valueChanged.connect(self._on_var_cur_changed)
        self.var_serial_row.addWidget(self.sp_var_cur)

        self.var_serial_row.addWidget(QLabel("Step:"))
        self.sp_var_step = QSpinBox()
        self.sp_var_step.setRange(1, 100)
        self.sp_var_step.setValue(1)
        self.sp_var_step.valueChanged.connect(self._on_var_step_changed)
        self.var_serial_row.addWidget(self.sp_var_step)

        self.var_serial_row.addWidget(QLabel("Digits:"))
        self.sp_var_digits = QSpinBox()
        self.sp_var_digits.setRange(1, 10)
        self.sp_var_digits.setValue(4)
        self.sp_var_digits.valueChanged.connect(self._on_var_digits_changed)
        self.var_serial_row.addWidget(self.sp_var_digits)
        var_layout.addWidget(self.var_serial_widget)

        self.var_text_container.setVisible(False)
        layout.addWidget(self.var_text_container)

        widget.setVisible(False)
        return widget

    def _load_text_properties(self, item: CadTextItem):
        self._syncing_text_props = True
        try:
            self.cb_font_family.setCurrentText(item.font_family)
            self.btn_text_hatch.setChecked(item.hatch_enabled)
            self.btn_text_style.setChecked(item.italic)

            if item.spacing_mode == 0:
                self.rb_spacing_auto.setChecked(True)
            elif item.spacing_mode == 1:
                self.rb_spacing_equal.setChecked(True)
            elif item.spacing_mode == 2:
                self.rb_spacing_fixed.setChecked(True)

            self.sp_text_space.setValue(item.char_spacing)
            self.sp_text_height.setValue(item.font_size_mm)

            if self.txt_text_content.toPlainText() != item.text:
                self.txt_text_content.setPlainText(item.text)

            self.cb_enable_variable.setChecked(item.enable_variable_text)
            self.var_text_container.setVisible(item.enable_variable_text)
            self.sp_var_cur.setValue(item.var_current)
            self.sp_var_step.setValue(item.var_step)
            self.sp_var_digits.setValue(item.var_digits)
            if item.var_type == "Serial":
                self.cb_var_type.setCurrentText("Serial No.")
                self.var_serial_widget.setVisible(True)
            elif item.var_type == "Date":
                self.cb_var_type.setCurrentText("Date (YYYY-MM-DD)")
                self.var_serial_widget.setVisible(False)
            elif item.var_type == "Time":
                self.cb_var_type.setCurrentText("Time (HH:MM:SS)")
                self.var_serial_widget.setVisible(False)
        finally:
            self._syncing_text_props = False

    def _on_text_content_changed(self):
        if self._syncing_text_props:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        new_text = self.txt_text_content.toPlainText()
        item.set_properties(text=new_text)
        self.scene.update_selection_box()
        bounds = item.sceneTransform().mapRect(item.boundingRect())
        self._syncing_props = True
        self.sp_size_w.setValue(bounds.width())
        self.sp_size_h.setValue(bounds.height())
        self._syncing_props = False
        self.scene.update()

    def _on_text_height_changed(self, new_h: float):
        if self._syncing_text_props:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        item.set_properties(font_size_mm=new_h)
        self.scene.update_selection_box()
        bounds = item.sceneTransform().mapRect(item.boundingRect())
        self._syncing_props = True
        self.sp_size_w.setValue(bounds.width())
        self.sp_size_h.setValue(bounds.height())
        self._syncing_props = False
        self.scene.update()

    def _on_text_space_changed(self, new_space: float):
        if self._syncing_text_props:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        item.set_properties(char_spacing=new_space)
        self.scene.update_selection_box()
        bounds = item.sceneTransform().mapRect(item.boundingRect())
        self._syncing_props = True
        self.sp_size_w.setValue(bounds.width())
        self.sp_size_h.setValue(bounds.height())
        self._syncing_props = False
        self.scene.update()

    def _on_font_family_changed(self, family: str):
        if self._syncing_text_props:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]

        # Resolve TTF/OTF font file to family if selected from text_parser
        resolved_family = family
        if self.main_window and hasattr(self.main_window, 'text_parser') and self.main_window.text_parser:
            tp = self.main_window.text_parser
            if family in tp.fonts:
                fpath = tp.fonts[family]
                db = QFontDatabase()
                fid = db.addApplicationFont(fpath)
                if fid != -1:
                    fams = db.applicationFontFamilies(fid)
                    if fams:
                        resolved_family = fams[0]

        item.set_properties(font_family=resolved_family)
        self.scene.update_selection_box()
        bounds = item.sceneTransform().mapRect(item.boundingRect())
        self._syncing_props = True
        self.sp_size_w.setValue(bounds.width())
        self.sp_size_h.setValue(bounds.height())
        self._syncing_props = False
        self.scene.update()

    def _toggle_text_hatch(self, checked: bool):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        item.set_properties(hatch_enabled=checked)
        self.scene.update()

    def _toggle_text_font_style(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        menu = QMenu(self)
        act_italic = menu.addAction("Italic")
        act_italic.setCheckable(True)
        act_italic.setChecked(item.italic)
        act_bold = menu.addAction("Bold")
        act_bold.setCheckable(True)
        act_bold.setChecked(item.bold)

        pos = self.btn_text_style.mapToGlobal(QPointF(0, self.btn_text_style.height()).toPoint())
        action = menu.exec(pos)
        if action == act_italic:
            item.set_properties(italic=act_italic.isChecked())
            self.btn_text_style.setChecked(act_italic.isChecked())
            self.scene.update_selection_box()
            self.scene.update()
        elif action == act_bold:
            item.set_properties(bold=act_bold.isChecked())
            self.scene.update_selection_box()
            self.scene.update()

    def _on_spacing_mode_changed(self, mode_id: int, checked: bool):
        if not checked or self._syncing_text_props:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        item.set_properties(spacing_mode=mode_id)
        self.scene.update_selection_box()
        bounds = item.sceneTransform().mapRect(item.boundingRect())
        self._syncing_props = True
        self.sp_size_w.setValue(bounds.width())
        self.sp_size_h.setValue(bounds.height())
        self._syncing_props = False
        self.scene.update()

    def _save_text_font_defaults(self):
        self.default_font_family = self.cb_font_family.currentText()
        self.default_font_height = self.sp_text_height.value()
        self.default_text_space = self.sp_text_space.value()
        self.scene.default_font_family = self.default_font_family
        self.scene.default_font_height = self.default_font_height
        self.scene.default_text_space = self.default_text_space
        self.lbl_status_selection.setText("Saved default text parameters.")

    def _on_enable_variable_toggled(self, checked: bool):
        self.var_text_container.setVisible(checked)
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if selected:
            item = selected[0]
            item.set_properties(enable_variable=checked)
            self.scene.update_selection_box()
            self.scene.update()

    def _on_var_type_changed(self, vtype_str: str):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if not selected:
            return
        item = selected[0]
        if "Serial" in vtype_str:
            vtype = "Serial"
            self.var_serial_widget.setVisible(True)
        elif "Date" in vtype_str:
            vtype = "Date"
            self.var_serial_widget.setVisible(False)
        else:
            vtype = "Time"
            self.var_serial_widget.setVisible(False)
        item.set_properties(var_type=vtype)
        self.scene.update_selection_box()
        self.scene.update()

    def _on_var_cur_changed(self, val: int):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if selected:
            selected[0].var_current = val
            selected[0].set_properties()
            self.scene.update()

    def _on_var_step_changed(self, val: int):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if selected:
            selected[0].var_step = val

    def _on_var_digits_changed(self, val: int):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadTextItem)]
        if selected:
            selected[0].var_digits = val
            selected[0].set_properties()
            self.scene.update()

    def _open_array_dialog(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            QMessageBox.information(self, "Array", "Please select an object first to create an array.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Array Distribution")
        dlg.setFixedSize(220, 180)
        v = QVBoxLayout(dlg)

        g = QGridLayout()
        g.addWidget(QLabel("Row Count:"), 0, 0)
        sp_rows = QSpinBox()
        sp_rows.setRange(1, 100)
        sp_rows.setValue(2)
        g.addWidget(sp_rows, 0, 1)

        g.addWidget(QLabel("Col Count:"), 1, 0)
        sp_cols = QSpinBox()
        sp_cols.setRange(1, 100)
        sp_cols.setValue(2)
        g.addWidget(sp_cols, 1, 1)

        g.addWidget(QLabel("X Step (MM):"), 2, 0)
        sp_dx = QDoubleSpinBox()
        sp_dx.setRange(-200.0, 200.0)
        sp_dx.setValue(20.0)
        g.addWidget(sp_dx, 2, 1)

        g.addWidget(QLabel("Y Step (MM):"), 3, 0)
        sp_dy = QDoubleSpinBox()
        sp_dy.setRange(-200.0, 200.0)
        sp_dy.setValue(-10.0)
        g.addWidget(sp_dy, 3, 1)

        v.addLayout(g)

        btn_ok = QPushButton("OK")
        btn_ok.setStyleSheet("background: #3498db; color: white; font-weight: bold;")
        btn_ok.clicked.connect(dlg.accept)
        v.addWidget(btn_ok)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            rows = sp_rows.value()
            cols = sp_cols.value()
            dx = sp_dx.value()
            dy = sp_dy.value()
            target = selected[0]

            for r in range(rows):
                for c in range(cols):
                    if r == 0 and c == 0:
                        continue
                    if isinstance(target, CadTextItem):
                        new_item = CadTextItem(
                            text=target.text,
                            font_size_mm=target.font_size_mm,
                            font_family=target.font_family,
                            char_spacing=target.char_spacing,
                            bold=target.bold,
                            italic=target.italic
                        )
                        new_item.spacing_mode = target.spacing_mode
                        new_item.hatch_enabled = target.hatch_enabled
                        new_item.setPos(target.pos().x() + c * dx, target.pos().y() - r * dy)
                        new_item.set_pen(target.pen_id)
                        self.scene.addItem(new_item)
            self.scene.update()
            self._refresh_object_list_table()

    def _on_width_spin_changed(self, new_w: float):
        if self._syncing_props or not self.aspect_ratio_locked:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if len(selected) == 1:
            bounds = selected[0].boundingRect()
            if bounds.width() > 1e-4:
                ratio = bounds.height() / bounds.width()
                self._syncing_props = True
                self.sp_size_h.setValue(new_w * ratio)
                self._syncing_props = False

    def _on_height_spin_changed(self, new_h: float):
        if self._syncing_props or not self.aspect_ratio_locked:
            return
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if len(selected) == 1:
            bounds = selected[0].boundingRect()
            if bounds.height() > 1e-4:
                ratio = bounds.width() / bounds.height()
                self._syncing_props = True
                self.sp_size_w.setValue(new_h * ratio)
                self._syncing_props = False

    def _apply_properties_to_selected(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            return

        target_cx = self.sp_pos_x.value()
        # Invert back to scene coordinate
        target_cy = -self.sp_pos_y.value()
        target_w = self.sp_size_w.value()
        target_h = self.sp_size_h.value()
        target_rot = self.sp_rot.value()

        # Anchor offset
        ax = self.anchor_selector.anchor_x  # 0: left, 1: center, 2: right
        ay = self.anchor_selector.anchor_y  # 0: top, 1: center, 2: bottom

        for item in selected:
            cur_bounds = item.boundingRect()
            cur_w = cur_bounds.width()
            cur_h = cur_bounds.height()
            if cur_w < 1e-4 or cur_h < 1e-4:
                continue

            scale_x = target_w / cur_w
            scale_y = target_h / cur_h

            item.setScale(scale_x)
            item.setRotation(target_rot)

            # Anchor shift
            anchor_scene_x = target_cx - (ax - 1) * (target_w / 2.0)
            anchor_scene_y = target_cy - (ay - 1) * (target_h / 2.0)

            item.setPos(anchor_scene_x, anchor_scene_y)

        self.scene.update_selection_box()
        self.scene.update()

    # --- Pen / Layer Management ---
    def _on_pen_row_selected(self):
        rows = [index.row() for index in self.table_pens.selectionModel().selectedRows()]
        if rows:
            pen_id = rows[0]
            self.current_pen_idx = pen_id
            self.sp_current_pen.setValue(pen_id)
            self._load_pen_params_to_form(pen_id)

    def _on_current_pen_spin_changed(self, pen_id: int):
        self.current_pen_idx = pen_id
        self.scene.active_pen_id = pen_id
        self._load_pen_params_to_form(pen_id)
        # Highlight in table
        self.table_pens.selectRow(pen_id)

    def _load_pen_params_to_form(self, pen_id: int):
        if 0 <= pen_id < len(self.pen_params):
            p = self.pen_params[pen_id]
            self.sp_loop.setValue(p["loop"])
            self.sp_speed.setValue(p["speed"])
            self.sp_power.setValue(p["power"])
            self.sp_freq.setValue(p["freq"])
            self.sp_start_tc.setValue(p["start_tc"])
            self.sp_off_tc.setValue(p["laser_off_tc"])
            self.sp_end_tc.setValue(p["end_tc"])
            self.sp_poly_tc.setValue(p["poly_tc"])

    def _save_active_pen_params(self):
        pen_id = self.current_pen_idx
        if 0 <= pen_id < len(self.pen_params):
            pwr = self.sp_power.value()
            frq = self.sp_freq.value()
            self.pen_params[pen_id] = {
                "loop": self.sp_loop.value(),
                "speed": self.sp_speed.value(),
                "power": pwr,
                "freq": frq,
                "start_tc": self.sp_start_tc.value(),
                "laser_off_tc": self.sp_off_tc.value(),
                "end_tc": self.sp_end_tc.value(),
                "poly_tc": self.sp_poly_tc.value(),
                "on": True
            }

            # Sync power and freq directly with Laser page & main window
            if self.main_window:
                self.main_window.pgm_laserpower = float(pwr)
                self.main_window.pgm_laserfreq = float(frq)
                if hasattr(self.main_window, 'ui'):
                    if hasattr(self.main_window.ui, 'galvolaserpowerHorizontalSlider_2'):
                        self.main_window.ui.galvolaserpowerHorizontalSlider_2.blockSignals(True)
                        self.main_window.ui.galvolaserpowerHorizontalSlider_2.setValue(int(pwr))
                        self.main_window.ui.galvolaserpowerHorizontalSlider_2.blockSignals(False)
                    if hasattr(self.main_window.ui, 'laserpowerLineEdit'):
                        self.main_window.ui.laserpowerLineEdit.setText(str(int(pwr)))
                    if hasattr(self.main_window.ui, 'galvolaserfreqHorizontalSlider'):
                        self.main_window.ui.galvolaserfreqHorizontalSlider.blockSignals(True)
                        self.main_window.ui.galvolaserfreqHorizontalSlider.setValue(int(frq))
                        self.main_window.ui.galvolaserfreqHorizontalSlider.blockSignals(False)
                    if hasattr(self.main_window.ui, 'laserfreqLineEdit'):
                        self.main_window.ui.laserfreqLineEdit.setText(str(int(frq)))

                if hasattr(self.main_window, 'galvo_controller') and getattr(self.main_window.galvo_controller, 'is_connected', False):
                    self.main_window.galvo_controller.live_power = float(pwr)
                    self.main_window.galvo_controller.live_freq = float(frq)

                if hasattr(self.main_window, '_apply_galvo_laser_settings'):
                    self.main_window._apply_galvo_laser_settings()

    def _assign_pen_to_selected(self, pen_id: int):
        self.current_pen_idx = pen_id
        self.sp_current_pen.setValue(pen_id)
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        for item in selected:
            item.set_pen(pen_id)
        self.scene.update()

    # --- Actions: Alignment & Transforms ---
    def _center_to_origin(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            # Center all shapes
            selected = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if not selected:
            return

        for item in selected:
            bounds = item.sceneTransform().mapRect(item.boundingRect())
            dx = -bounds.center().x()
            dy = -bounds.center().y()
            item.setPos(item.pos().x() + dx, item.pos().y() + dy)

        self.scene.update_selection_box()
        self.scene.update()

    def _align_shapes(self, align_type: str):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if len(selected) < 2:
            return

        ref_bounds = selected[0].sceneTransform().mapRect(selected[0].boundingRect())

        for item in selected[1:]:
            b = item.sceneTransform().mapRect(item.boundingRect())
            dx = 0.0
            dy = 0.0

            if align_type == "left":
                dx = ref_bounds.left() - b.left()
            elif align_type == "right":
                dx = ref_bounds.right() - b.right()
            elif align_type == "top":
                dy = ref_bounds.top() - b.top()
            elif align_type == "bottom":
                dy = ref_bounds.bottom() - b.bottom()
            elif align_type == "center_x":
                dx = ref_bounds.center().x() - b.center().x()
            elif align_type == "center_y":
                dy = ref_bounds.center().y() - b.center().y()

            item.setPos(item.pos().x() + dx, item.pos().y() + dy)

        self.scene.update_selection_box()
        self.scene.update()

    def _mirror_shapes(self, horizontal: bool = True):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            return
        for item in selected:
            t = item.transform()
            if horizontal:
                t.scale(-1, 1)
            else:
                t.scale(1, -1)
            item.setTransform(t)
        self.scene.update_selection_box()
        self.scene.update()

    def _toggle_lock(self, lock: bool):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        for item in selected:
            item.is_locked = lock
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not lock)

    def _delete_selected(self):
        for item in list(self.scene.selectedItems()):
            if isinstance(item, CadShapeItem) and item.scene() == self.scene:
                self.scene.removeItem(item)
        self.scene.clearSelection()
        self._refresh_object_list_table()

    def _select_all(self):
        for item in self.scene.items():
            if isinstance(item, CadShapeItem):
                item.setSelected(True)

    def _clear_all(self):
        reply = QMessageBox.question(self, "Clear Canvas", "Remove all objects from the CAD workspace?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item in list(self.scene.items()):
                if isinstance(item, CadShapeItem) and item.scene() == self.scene:
                    self.scene.removeItem(item)
            self.scene.clearSelection()
            self._refresh_object_list_table()

    # --- EzCad Hatch Dialog (Exact Visual & Functional Parity with Image) ---
    def _open_hatch_dialog(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            # If nothing is selected, target all closed vector shapes on canvas
            selected = [item for item in self.scene.items() if isinstance(item, CadShapeItem) and getattr(item, 'is_closed', True)]
            if not selected:
                QMessageBox.information(self, "Hatch", "Please select or create a closed contour shape or text to apply hatch fill.")
                return

        # Fetch hatch profiles from main_window if available, else local
        profiles = getattr(self.main_window, 'hatch_profiles', None) if self.main_window else None
        if not profiles:
            profiles = self.hatch_profiles

        dlg = EzcadHatchDialog(parent=self, hatch_profiles=profiles, target_items=selected)

        def handle_undo_hatch():
            for item in selected:
                if hasattr(item, 'hatch_items') and item.hatch_items:
                    for h in item.hatch_items:
                        if h.scene() == self.scene:
                            self.scene.removeItem(h)
                    item.hatch_items.clear()
                elif hasattr(item, 'hatch_item') and item.hatch_item:
                    if item.hatch_item.scene() == self.scene:
                        self.scene.removeItem(item.hatch_item)
                    item.hatch_item = None
                if isinstance(item, CadTextItem):
                    item.set_properties(hatch_enabled=False)
            self.scene.update()
            self._refresh_object_list_table()
            self.lbl_status_selection.setText("Hatch fill removed from selected object(s).")

        dlg.undoHatchRequested.connect(handle_undo_hatch)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Sync back to main_window and save to config if available
            if self.main_window and hasattr(self.main_window, 'hatch_profiles'):
                self.main_window.hatch_profiles.update(dlg.hatch_profiles)
                if hasattr(self.main_window, 'save_current_hatch_profile'):
                    self.main_window.save_current_hatch_profile()
            self.hatch_profiles.update(dlg.hatch_profiles)

            # Gather active profiles (or profile 1 if none explicitly active)
            active_cfgs = [p for p in dlg.hatch_profiles.values() if p.get("enable", False)]
            if not active_cfgs:
                active_cfgs = [dlg.hatch_profiles[1]]

            for item in selected:
                # Remove existing hatch
                if hasattr(item, 'hatch_items') and item.hatch_items:
                    for h in item.hatch_items:
                        if h.scene() == self.scene:
                            self.scene.removeItem(h)
                    item.hatch_items.clear()
                elif hasattr(item, 'hatch_item') and item.hatch_item:
                    if item.hatch_item.scene() == self.scene:
                        self.scene.removeItem(item.hatch_item)
                    item.hatch_item = None

                item.hatch_items = []

                if isinstance(item, CadTextItem):
                    cfg = active_cfgs[0]
                    pitch = float(cfg.get("line_space", "0.03") or 0.03)
                    item.hatch_pitch = pitch
                    item.set_properties(hatch_enabled=True)

                for cfg in active_cfgs:
                    pitch = float(cfg.get("line_space", "0.03") or 0.03)
                    angle = float(cfg.get("angle", "45.0") or 45.0)
                    cross = bool(cfg.get("cross_hatch", False))
                    follow = bool(cfg.get("follow_edge", True))
                    edge_off = float(cfg.get("edge_off", "0.0") or 0.0)
                    start_off = float(cfg.get("start_off", "0.0") or 0.0)
                    end_off = float(cfg.get("end_off", "0.0") or 0.0)
                    line_red = float(cfg.get("line_red", "0.0") or 0.0)
                    num_loops = int(cfg.get("num_loops", "0") or 0)
                    loop_dist = float(cfg.get("loop_dist", "0.5") or 0.5)
                    pen_id = int(cfg.get("pen_no", 0) or 0)
                    hatch_type = cfg.get("type", "Bidirectional")
                    count = int(cfg.get("count", 1) or 1)
                    auto_rot = bool(cfg.get("auto_rot", False))
                    rot_angle = float(cfg.get("rot_angle", "10.0") or 10.0)
                    all_calc = bool(cfg.get("all_calc", True))
                    avg_dist = bool(cfg.get("avg_dist", False))
                    mark_contour = bool(cfg.get("mark_contour", True))

                    if not mark_contour:
                        item.stroke_color = QColor(0, 0, 0, 0)
                    else:
                        item.set_pen(pen_id)

                    hatch_item = CadHatchItem(
                        target_item=item,
                        line_pitch=pitch,
                        angle_deg=angle,
                        cross_hatch=cross,
                        follow_edge=follow,
                        edge_offset=edge_off,
                        start_offset=start_off,
                        end_offset=end_off,
                        line_reduction=line_red,
                        num_loops=num_loops,
                        loop_distance=loop_dist,
                        hatch_type=hatch_type,
                        pen_id=pen_id,
                        count=count,
                        auto_rotate=auto_rot,
                        rotate_angle=rot_angle,
                        all_calc=all_calc,
                        avg_dist=avg_dist
                    )
                    hatch_item.setParentItem(item)
                    item.hatch_items.append(hatch_item)

            self.scene.update()
            self._refresh_object_list_table()
            self.lbl_status_selection.setText("Hatch applied to selected object(s).")

    # --- Import / Export ---
    def _import_dxf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import DXF File", "", "DXF Files (*.dxf)")
        if not file_path:
            return

        try:
            import ezdxf
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            count = 0

            for entity in msp:
                if entity.dxftype() == 'LINE':
                    p1 = QPointF(entity.dxf.start.x, entity.dxf.start.y)
                    p2 = QPointF(entity.dxf.end.x, entity.dxf.end.y)
                    item = CadLineItem(p1, p2)
                    item.set_pen(self.current_pen_idx)
                    self.scene.addItem(item)
                    count += 1
                elif entity.dxftype() == 'LWPOLYLINE':
                    pts = [QPointF(x, y) for x, y, *_ in entity.get_points()]
                    if len(pts) >= 2:
                        item = CadPolygonItem(pts)
                        item.set_pen(self.current_pen_idx)
                        self.scene.addItem(item)
                        count += 1
                elif entity.dxftype() == 'CIRCLE':
                    center = QPointF(entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    item = CadCircleItem(center, radius)
                    item.set_pen(self.current_pen_idx)
                    self.scene.addItem(item)
                    count += 1

            self._refresh_object_list_table()
            self.view.zoom_to_fit()
            QMessageBox.information(self, "Import Complete", f"Imported {count} vector entities from DXF.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import DXF:\n{e}")

    def _import_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if not file_path:
            return
        # Add as centered rect boundary placeholder
        item = CadRectItem(QRectF(-15.0, -15.0, 30.0, 30.0))
        item.name = os.path.basename(file_path)
        item.set_pen(self.current_pen_idx)
        self.scene.addItem(item)
        self._refresh_object_list_table()

    def _export_dxf(self):
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if not shapes:
            QMessageBox.information(self, "Empty Canvas", "Draw at least one shape before exporting.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export DXF", "cad_drawing.dxf", "DXF Files (*.dxf)")
        if not file_path:
            return

        try:
            import ezdxf
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()

            for item in shapes:
                path = item.scene_painter_path()
                for polygon in path.toSubpathPolygons():
                    if len(polygon) < 2:
                        continue
                    pts = [(pt.x(), pt.y()) for pt in polygon]
                    msp.add_lwpolyline(pts, close=item.is_closed)

            doc.saveas(file_path)
            QMessageBox.information(self, "Export Complete", f"Saved DXF to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export DXF: {e}")

    def _on_new_file(self):
        self._clear_all()

    def _on_open_file(self):
        self._import_dxf()

    def _on_save_file(self):
        self._export_dxf()

    def _update_power_on_timer(self):
        """Update live system uptime timer (HH:MM:SS) in bottom execution bar."""
        elapsed = int(time.time() - self._start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.lbl_power_timer.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def _on_part_no_edited(self, text: str):
        """Allow manual editing of part counter."""
        try:
            self.part_counter = int(text) if text.strip() else 0
        except ValueError:
            pass

    def _reset_counter(self):
        """Reset part counter to zero."""
        self.part_counter = 0
        self.edit_part_no.setText("0")

    def _on_escape_pressed(self):
        """Global Escape key stops active red-light framing, aborts marking, or clears selection."""
        if self.is_framing:
            self._toggle_red_light()
        elif self.is_marking:
            self._abort_mark()
        else:
            self.scene.clearSelection()
            self.scene.set_tool("select")

    def is_text_input_focused(self) -> bool:
        from PySide6.QtWidgets import QApplication, QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox
        focus_w = QApplication.focusWidget()
        if focus_w is None:
            return False
        return isinstance(focus_w, (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox))

    def handle_cad_key_event(self, event: QKeyEvent) -> bool:
        key = event.key()
        modifiers = event.modifiers()

        # Priority global shortcuts
        if key == Qt.Key.Key_F1:
            self._toggle_red_light()
            return True
        elif key == Qt.Key.Key_F2:
            self._execute_mark()
            return True
        elif key == Qt.Key.Key_Escape:
            self._on_escape_pressed()
            return True

        # If user is currently typing inside a text box or spinbox, do NOT intercept standard editing keys
        if self.is_text_input_focused():
            return False

        # 1. Delete / Backspace
        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
            if selected:
                for item in selected:
                    if hasattr(item, 'hatch_items') and item.hatch_items:
                        for h in list(item.hatch_items):
                            if h.scene() == self.scene:
                                self.scene.removeItem(h)
                        item.hatch_items.clear()
                    if item.scene() == self.scene:
                        self.scene.removeItem(item)
                self.scene.clearSelection()
                self._refresh_object_list_table()
                self._clear_property_inputs()
                self.lbl_status_selection.setText(f"Deleted {len(selected)} item(s).")
                return True

        # 2. Arrow keys (Nudge selected shapes)
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            step = 1.0  # Default mm
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                step = 0.1  # Fine
            elif modifiers & Qt.KeyboardModifier.ControlModifier:
                step = 10.0 # Fast
            elif hasattr(self.scene, 'snap_grid_size') and self.scene.snap_grid_size > 0:
                step = float(self.scene.snap_grid_size)

            dx, dy = 0.0, 0.0
            if key == Qt.Key.Key_Left:
                dx = -step
            elif key == Qt.Key.Key_Right:
                dx = step
            elif key == Qt.Key.Key_Up:
                dy = -step  # In Qt scene, negative Y is visually UP
            elif key == Qt.Key.Key_Down:
                dy = step   # In Qt scene, positive Y is visually DOWN

            selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
            if selected:
                for item in selected:
                    item.setPos(item.pos() + QPointF(dx, dy))
                self.scene.update_selection_box()
                self.scene.update()
                self._refresh_object_list_table()
                self._load_property_inputs()
                self.lbl_status_selection.setText(f"Moved {len(selected)} item(s) by ({dx:+.2f}, {-dy:+.2f}) mm.")
                return True

        # 3. Ctrl combinations
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_A:
                all_shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
                for item in all_shapes:
                    item.setSelected(True)
                self.lbl_status_selection.setText(f"Selected all ({len(all_shapes)} items).")
                return True
            elif key == Qt.Key.Key_C:
                selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
                if selected:
                    self._clipboard_items = selected
                    self.lbl_status_selection.setText(f"Copied {len(selected)} item(s).")
                    return True
            elif key == Qt.Key.Key_V:
                if hasattr(self, '_clipboard_items') and self._clipboard_items:
                    new_selected = []
                    self.scene.clearSelection()
                    for target in self._clipboard_items:
                        new_item = self._duplicate_item(target, offset_x=2.0, offset_y=2.0)
                        if new_item:
                            new_selected.append(new_item)
                    self._clipboard_items = new_selected
                    self._refresh_object_list_table()
                    self._load_property_inputs()
                    self.lbl_status_selection.setText(f"Pasted {len(new_selected)} item(s).")
                    return True
            elif key == Qt.Key.Key_D:
                selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
                if selected:
                    self.scene.clearSelection()
                    for target in selected:
                        self._duplicate_item(target, offset_x=2.0, offset_y=2.0)
                    self._refresh_object_list_table()
                    self._load_property_inputs()
                    return True
            elif key == Qt.Key.Key_H:
                self._open_hatch_dialog()
                return True

        # 4. Single key shortcuts
        if key == Qt.Key.Key_H:
            self._open_hatch_dialog()
            return True

        return False

    def keyPressEvent(self, event: QKeyEvent):
        if self.handle_cad_key_event(event):
            event.accept()
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if obj == getattr(self, 'table_objects', None) and event.type() in (QEvent.Type.KeyPress, QEvent.KeyPress):
            if self.handle_cad_key_event(event):
                return True
        return super().eventFilter(obj, event)

    def _duplicate_item(self, target: CadShapeItem, offset_x: float = 2.0, offset_y: float = 2.0):
        new_item = None
        new_pos = target.pos() + QPointF(offset_x, offset_y)
        if isinstance(target, CadTextItem):
            new_item = CadTextItem(
                text=target.text,
                font_size_mm=target.font_size_mm,
                font_family=target.font_family,
                char_spacing=target.char_spacing,
                bold=target.bold,
                italic=target.italic
            )
            new_item.spacing_mode = target.spacing_mode
            new_item.hatch_enabled = target.hatch_enabled
            new_item.hatch_pitch = target.hatch_pitch
            new_item.enable_variable_text = target.enable_variable_text
            new_item.var_type = target.var_type
            new_item.var_current = target.var_current
            new_item.var_step = target.var_step
            new_item.var_digits = target.var_digits
        elif isinstance(target, CadRectItem):
            new_item = CadRectItem(rect=target.rect, corner_radius=target.corner_radius)
        elif isinstance(target, CadCircleItem):
            new_item = CadCircleItem(center=target.center, rx=target.rx, ry=target.ry)
        elif isinstance(target, CadLineItem):
            new_item = CadLineItem(p1=target.p1, p2=target.p2)
        elif isinstance(target, CadPolygonItem):
            new_item = CadPolygonItem(points=list(target.points))
        elif isinstance(target, CadBarcodeItem):
            new_item = CadBarcodeItem(content=target.content, pos=target.pos_origin, size_mm=target.size_mm, code_type=target.code_type)

        if new_item:
            new_item.setPos(new_pos)
            new_item.setRotation(target.rotation())
            new_item.set_pen(target.pen_id)
            self.scene.addItem(new_item)
            new_item.setSelected(True)

            if hasattr(target, 'hatch_items') and target.hatch_items:
                new_item.hatch_items = []
                for h in target.hatch_items:
                    h_copy = CadHatchItem(
                        target_item=new_item,
                        line_pitch=h.line_pitch,
                        angle_deg=h.angle_deg,
                        cross_hatch=h.cross_hatch,
                        follow_edge=h.follow_edge,
                        edge_offset=h.edge_offset,
                        start_offset=h.start_offset,
                        end_offset=h.end_offset,
                        line_reduction=h.line_reduction,
                        num_loops=h.num_loops,
                        loop_distance=h.loop_distance,
                        hatch_type=h.hatch_type,
                        pen_id=h.pen_id,
                        count=h.count,
                        auto_rotate=h.auto_rotate,
                        rotate_angle=h.rotate_angle,
                        all_calc=h.all_calc,
                        avg_dist=h.avg_dist
                    )
                    self.scene.addItem(h_copy)
                    new_item.hatch_items.append(h_copy)

        return new_item

    def _map_to_galvo(self, x_mm: float, y_mm: float):
        """
        Convert centered millimeter canvas coordinates to 16-bit Galvo DAC units (0-65535).
        Uses machine calibration matrix from GalvoConfig if available.
        Note: In QGraphicsScene (CAD canvas), +Y points DOWNWARD, whereas in physical machine /
        Cartesian space, +Y points UPWARD. Therefore, y_mm is inverted (-y_mm) before mapping.
        """
        phys_y = -y_mm
        if self.main_window and hasattr(self.main_window, 'galvo_config') and self.main_window.galvo_config:
            try:
                return self.main_window.galvo_config.apply_transform(x_mm, phys_y)
            except Exception:
                pass
        field_size = getattr(self.scene, 'field_size_mm', 70.0) or 70.0
        scale = 65535.0 / field_size
        gx = int(round(32767 + x_mm * scale))
        gy = int(round(32767 + phys_y * scale))
        return max(0, min(65535, gx)), max(0, min(65535, gy))

    # --- Hardware Execution: Red Pointer (F1) & Marking (F2) ---
    def _toggle_red_light(self):
        """Toggle Red Light Framing (F1) with visual guide and hardware PreviewThread."""
        if not self.is_framing:
            # 1. Determine target shapes
            shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
            if self.cb_mark_select.isChecked():
                shapes = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]

            if not shapes:
                QMessageBox.information(self, "Red Light Guide", "Add or select shapes to guide frame.")
                return

            # 2. Compute bounding box in mm
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            for item in shapes:
                b = item.sceneTransform().mapRect(item.boundingRect())
                min_x = min(min_x, b.left())
                max_x = max(max_x, b.right())
                min_y = min(min_y, b.top())
                max_y = max(max_y, b.bottom())

            # Map to galvo coordinates
            gx1, gy1 = self._map_to_galvo(min_x, min_y)
            gx2, gy2 = self._map_to_galvo(max_x, max_y)
            g_min_x = min(gx1, gx2)
            g_max_x = max(gx1, gx2)
            g_min_y = min(gy1, gy2)
            g_max_y = max(gy1, gy2)

            # 3. Visual framing guide on canvas
            if self.framing_rect_item and self.framing_rect_item.scene() == self.scene:
                self.scene.removeItem(self.framing_rect_item)

            frame_pen = QPen(QColor("#e74c3c"), 0.8, Qt.PenStyle.DashDotLine)
            frame_pen.setCosmetic(True)

            if self.cb_show_contour.isChecked():
                combined_path = QPainterPath()
                for item in shapes:
                    combined_path.addPath(item.scene_painter_path())
                self.framing_rect_item = QGraphicsPathItem(combined_path)
            else:
                self.framing_rect_item = QGraphicsRectItem(QRectF(min_x, min_y, max_x - min_x, max_y - min_y))

            self.framing_rect_item.setPen(frame_pen)
            self.framing_rect_item.setZValue(3000)
            self.scene.addItem(self.framing_rect_item)

            # 4. Hardware red pointer thread
            if self.main_window and hasattr(self.main_window, 'galvo_controller'):
                ctrl = self.main_window.galvo_controller
                if getattr(ctrl, 'is_connected', False) and ctrl.connection:
                    try:
                        from galvo_threads import PreviewThread
                        self.preview_thread = PreviewThread(ctrl, g_min_x, g_max_x, g_min_y, g_max_y)
                        self.preview_thread.start()
                    except Exception as e:
                        print(f"Hardware red pointer frame started via connection: {e}")
                        if hasattr(ctrl.connection, 'reddot_on'):
                            ctrl.connection.reddot_on()

            self.is_framing = True
            self.btn_red_light.setText("STOP (F1)")
            self.btn_red_light.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; min-width: 68px; min-height: 28px;")
            self.lbl_status_selection.setText("Red light guide previewing...")

        else:
            # Stop Red Light Framing
            if self.framing_rect_item and self.framing_rect_item.scene() == self.scene:
                self.scene.removeItem(self.framing_rect_item)
                self.framing_rect_item = None

            if hasattr(self, 'preview_thread') and self.preview_thread:
                self.preview_thread.running = False
                self.preview_thread.wait(500)
                self.preview_thread = None

            if self.main_window and hasattr(self.main_window, 'galvo_controller'):
                ctrl = self.main_window.galvo_controller
                if getattr(ctrl, 'is_connected', False) and ctrl.connection:
                    if hasattr(ctrl.connection, 'reddot_off'):
                        ctrl.connection.reddot_off()
                    if hasattr(ctrl.connection, 'stop'):
                        ctrl.connection.stop()

            self.is_framing = False
            self.btn_red_light.setText("Red(F1)")
            self.btn_red_light.setStyleSheet("font-weight: bold; font-size: 11px; min-width: 68px; height: 26px; background: #e8e8e8; border: 1px solid #707070;")
            self.lbl_status_selection.setText("Red light guide stopped.")

    def _execute_mark(self):
        """Execute laser marking (F2) with pen speeds, loop counts, contours and hatches."""
        if self.is_marking:
            self._abort_mark()
            return

        # Stop framing if active
        if self.is_framing:
            self._toggle_red_light()

        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if self.cb_mark_select.isChecked():
            shapes = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]

        if not shapes:
            QMessageBox.information(self, "Mark", "No shapes to mark.")
            return

        # Ensure motion planner exists
        planner = getattr(self.main_window, 'planner', None)
        if planner is None:
            from core.motion_planner import MotionPlanner
            planner = MotionPlanner()
            if self.main_window:
                self.main_window.planner = planner
        planner.clear()

        field_size = self._get_configured_field_size()
        galvo_units_per_mm = 65535.0 / (field_size if field_size > 0 else 70.0)

        # Group shapes by pen_id so each pen uses its specific speed, power, freq
        shapes_by_pen = {}
        for item in shapes:
            shapes_by_pen.setdefault(item.pen_id, []).append(item)

        for pen_id, pen_shapes in sorted(shapes_by_pen.items()):
            p_params = self.pen_params[pen_id] if pen_id < len(self.pen_params) else self.pen_params[0]
            if not p_params.get("on", True):
                continue

            raw_speed = float(p_params.get("speed", 2000))
            mark_speed = int(raw_speed * galvo_units_per_mm)
            jump_speed = int(3000 * galvo_units_per_mm)
            loop_count = int(p_params.get("loop", 1))

            for _ in range(loop_count):
                for item in pen_shapes:
                    # 1. Contours
                    if item.stroke_color.alpha() > 0:
                        path = item.scene_painter_path()
                        for polygon in path.toSubpathPolygons():
                            pts = list(polygon)
                            if len(pts) < 2:
                                continue

                            start_gx, start_gy = self._map_to_galvo(pts[0].x(), pts[0].y())
                            planner.add_jump(start_gx, start_gy, speed=jump_speed)

                            for pt in pts[1:]:
                                gx, gy = self._map_to_galvo(pt.x(), pt.y())
                                planner.add_mark(gx, gy, speed=mark_speed)

                            if item.is_closed and polygon.isClosed():
                                planner.add_mark(start_gx, start_gy, speed=mark_speed)

                    # 2. Hatches
                    if hasattr(item, 'hatch_items') and item.hatch_items:
                        for hatch in item.hatch_items:
                            h_pen = hatch.pen_id
                            h_params = self.pen_params[h_pen] if h_pen < len(self.pen_params) else p_params
                            h_mark_speed = int(float(h_params.get("speed", 2000)) * galvo_units_per_mm)
                            h_path = hatch.scene_painter_path()
                            for poly in h_path.toSubpathPolygons():
                                pts = list(poly)
                                if len(pts) >= 2:
                                    p1_gx, p1_gy = self._map_to_galvo(pts[0].x(), pts[0].y())
                                    planner.add_jump(p1_gx, p1_gy, speed=jump_speed)
                                    for pt in pts[1:]:
                                        gx, gy = self._map_to_galvo(pt.x(), pt.y())
                                        planner.add_mark(gx, gy, speed=h_mark_speed)

                    # 3. Text hatch infill if CadTextItem (only if not already marked via hatch_items)
                    if isinstance(item, CadTextItem) and getattr(item, 'hatch_enabled', False) and not (hasattr(item, 'hatch_items') and item.hatch_items):
                        if hasattr(item, '_cached_hatch_path') and item._cached_hatch_path:
                            for poly in item._cached_hatch_path.toSubpathPolygons():
                                pts = list(poly)
                                if len(pts) >= 2:
                                    p1_sc = item.mapToScene(pts[0])
                                    p1_gx, p1_gy = self._map_to_galvo(p1_sc.x(), p1_sc.y())
                                    planner.add_jump(p1_gx, p1_gy, speed=jump_speed)
                                    for pt in pts[1:]:
                                        pt_sc = item.mapToScene(pt)
                                        gx, gy = self._map_to_galvo(pt_sc.x(), pt_sc.y())
                                        planner.add_mark(gx, gy, speed=mark_speed)

        if hasattr(planner, 'commit_to_send_queue'):
            planner.commit_to_send_queue()
        elif hasattr(planner, 'preview_queue'):
            planner.send_queue = list(planner.preview_queue)

        if not planner.send_queue:
            QMessageBox.information(self, "Mark", "Nothing to mark in selected shapes.")
            return

        self.is_marking = True
        self._abort_requested = False
        self.btn_mark.setText("STOP (F2)")
        self.btn_mark.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; min-width: 68px; min-height: 28px;")
        self.btn_red_light.setEnabled(False)
        self.lbl_status_selection.setText(f"Marking {len(shapes)} object(s)... ({len(planner.send_queue)} commands)")

        # Set live laser power & freq from current pen and sync to Laser Page
        curr_p = self.pen_params[self.current_pen_idx]
        power_val = float(curr_p.get("power", 60.0))
        freq_val = float(curr_p.get("freq", 70.0))

        if self.main_window:
            self.main_window.pgm_laserpower = power_val
            self.main_window.pgm_laserfreq = freq_val
            if hasattr(self.main_window, 'ui'):
                if hasattr(self.main_window.ui, 'galvolaserpowerHorizontalSlider_2'):
                    self.main_window.ui.galvolaserpowerHorizontalSlider_2.blockSignals(True)
                    self.main_window.ui.galvolaserpowerHorizontalSlider_2.setValue(int(power_val))
                    self.main_window.ui.galvolaserpowerHorizontalSlider_2.blockSignals(False)
                if hasattr(self.main_window.ui, 'laserpowerLineEdit'):
                    self.main_window.ui.laserpowerLineEdit.setText(str(int(power_val)))
                if hasattr(self.main_window.ui, 'galvolaserfreqHorizontalSlider'):
                    self.main_window.ui.galvolaserfreqHorizontalSlider.blockSignals(True)
                    self.main_window.ui.galvolaserfreqHorizontalSlider.setValue(int(freq_val))
                    self.main_window.ui.galvolaserfreqHorizontalSlider.blockSignals(False)
                if hasattr(self.main_window.ui, 'laserfreqLineEdit'):
                    self.main_window.ui.laserfreqLineEdit.setText(str(int(freq_val)))

            if hasattr(self.main_window, '_apply_galvo_laser_settings'):
                self.main_window._apply_galvo_laser_settings()

        if hasattr(self.main_window, 'galvo_controller') and getattr(self.main_window.galvo_controller, 'is_connected', False):
            ctrl = self.main_window.galvo_controller
            ctrl.live_power = power_val
            ctrl.live_freq = freq_val

            try:
                from galvo_threads import ExecutionThread
                self.exec_thread = ExecutionThread(ctrl, planner.send_queue, loop_count=1)
                self.exec_thread.finished_signal.connect(self._on_mark_finished)
                self.exec_thread.start()
            except Exception as e:
                print(f"Failed to start ExecutionThread: {e}")
                self._on_mark_finished(False)
        else:
            # Offline simulation mode
            sim_delay = min(2500, max(400, len(planner.send_queue) * 2))
            QTimer.singleShot(sim_delay, lambda: self._on_mark_finished(True))

    def _on_mark_finished(self, success: bool):
        """Called when marking completes or aborts."""
        self.is_marking = False
        self.exec_thread = None
        self.btn_mark.setText("Mark(F2)")
        self.btn_mark.setStyleSheet("font-weight: bold; font-size: 11px; min-width: 68px; height: 26px; background: #27ae60; color: white; border: 1px solid #1e8449;")
        self.btn_red_light.setEnabled(True)

        if success and not self._abort_requested:
            self.part_counter += 1
            self.total_counter += 1
            self.edit_part_no.setText(str(self.part_counter))
            self.edit_total_no.setText(str(self.total_counter))

            # Auto-advance serial numbers on text items
            for item in self.scene.items():
                if isinstance(item, CadTextItem) and getattr(item, 'enable_variable_text', False):
                    item.advance_variable()

            self.lbl_status_selection.setText(f"Mark completed. Part: {self.part_counter} | Total: {self.total_counter}")

            # Continuous mode loop
            if self.cb_continuous.isChecked() and not self._abort_requested:
                QTimer.singleShot(250, self._execute_mark)
        else:
            self.lbl_status_selection.setText("Mark stopped / aborted.")

    def _abort_mark(self):
        """Abort active laser marking."""
        self._abort_requested = True
        if hasattr(self, 'exec_thread') and self.exec_thread:
            self.exec_thread.abort()
            self.exec_thread.wait(500)
            self.exec_thread = None

        if self.main_window and hasattr(self.main_window, 'galvo_controller'):
            ctrl = self.main_window.galvo_controller
            if getattr(ctrl, 'connection', None):
                if hasattr(ctrl.connection, 'stop'):
                    ctrl.connection.stop()
                if hasattr(ctrl.connection, 'laser_off'):
                    ctrl.connection.laser_off()

        self._on_mark_finished(False)

