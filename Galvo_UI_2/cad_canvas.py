import math
import os
import time
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, Signal, Slot, QTimer, QSize
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont,
    QCursor, QTransform, QWheelEvent, QMouseEvent, QKeyEvent, QIcon,
    QLinearGradient, QAction, QKeySequence
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
    QGraphicsRectItem, QGraphicsEllipseItem, QInputDialog,
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QDoubleSpinBox,
    QSpinBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMenuBar, QMenu, QToolBar, QButtonGroup, QRadioButton,
    QScrollArea, QDialog, QLineEdit, QAbstractItemView
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
            text_str, ok = QInputDialog.getText(None, "EzCad Text", "Enter text to vectorize:")
            if ok and text_str.strip():
                item = CadTextItem(text_str.strip(), pos, font_size_mm=8.0)
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

    def drawBackground(self, painter: QPainter, rect: QRectF):
        self.cad_scene.drawBackground(painter, rect)

        self._is_panning = False
        self._pan_start_pos = None

        self.horizontalScrollBar().valueChanged.connect(lambda: self.viewScrolled.emit())
        self.verticalScrollBar().valueChanged.connect(lambda: self.viewScrolled.emit())

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(factor, factor)
        self.viewScrolled.emit()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

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
        half = self.cad_scene.field_size / 2.0
        margin = 10.0
        self.fitInView(-half - margin, -half - margin, self.cad_scene.field_size + margin * 2.0, self.cad_scene.field_size + margin * 2.0, Qt.AspectRatioMode.KeepAspectRatio)
        self.viewScrolled.emit()


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

        self._init_ui()
        self._connect_signals()

        # Initial zoom fit
        QTimer.singleShot(100, self.view.zoom_to_fit)

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
        """Auto-refresh field size from config whenever page becomes visible."""
        super().showEvent(event)
        new_size = self._get_configured_field_size()
        if abs(self.scene.field_size - new_size) > 0.01:
            self.scene.set_field_size(new_size)
            self.view.zoom_to_fit()
        self._update_status_bar(0.0, 0.0)

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
        l_layout.addWidget(self.table_objects)

        vbox.addWidget(list_frame, stretch=4)

        # --- 2. Object Property Dock ---
        prop_frame = QFrame()
        prop_frame.setObjectName("dockFrame")
        p_layout = QVBoxLayout(prop_frame)
        p_layout.setContentsMargins(1, 1, 1, 1)
        p_layout.setSpacing(2)

        title_prop = QLabel("Object property")
        title_prop.setObjectName("dockTitle")
        p_layout.addWidget(title_prop)

        grid = QGridLayout()
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(3)

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

        # Apply Button
        self.btn_apply_prop = QPushButton("Apply")
        self.btn_apply_prop.setStyleSheet("background: #3498db; color: white; font-weight: bold; min-height: 22px;")
        self.btn_apply_prop.clicked.connect(self._apply_properties_to_selected)
        grid.addWidget(self.btn_apply_prop, 4, 0, 1, 3)

        p_layout.addLayout(grid)

        # Dynamic subpanel for Text, Barcode, or Shape-specific details
        self.prop_detail_frame = QFrame()
        self.prop_detail_layout = QVBoxLayout(self.prop_detail_frame)
        self.prop_detail_layout.setContentsMargins(4, 2, 4, 2)
        p_layout.addWidget(self.prop_detail_frame)

        vbox.addWidget(prop_frame, stretch=5)
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
        self.btn_red_light.setStyleSheet("font-weight: bold; font-size: 12px; min-width: 68px; min-height: 28px; background: #e8e8e8;")
        self.btn_red_light.clicked.connect(self._toggle_red_light)
        ctrl_layout.addWidget(self.btn_red_light)

        # Mark(F2) Button
        self.btn_mark = QPushButton("Mark(F2)")
        self.btn_mark.setStyleSheet("font-weight: bold; font-size: 12px; min-width: 68px; min-height: 28px; background: #27ae60; color: white;")
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
        self.lbl_part_no = QLabel("0")
        self.lbl_part_no.setStyleSheet("background: #ffffff; border: 1px solid #b0b0b0; padding: 2px 6px; font-weight: bold;")
        ctrl_layout.addWidget(self.lbl_part_no)

        self.btn_reset_counter = QPushButton("R")
        self.btn_reset_counter.setToolTip("Reset Part Counter")
        self.btn_reset_counter.setFixedSize(22, 22)
        self.btn_reset_counter.clicked.connect(self._reset_counter)
        ctrl_layout.addWidget(self.btn_reset_counter)

        ctrl_layout.addWidget(QLabel("Total no"))
        self.lbl_total_no = QLabel("0")
        self.lbl_total_no.setStyleSheet("background: #ffffff; border: 1px solid #b0b0b0; padding: 2px 6px;")
        ctrl_layout.addWidget(self.lbl_total_no)

        # Timers
        ctrl_layout.addWidget(QLabel("Power On"))
        self.lbl_power_timer = QLabel("00:00:00")
        self.lbl_power_timer.setStyleSheet("background: #ffffff; border: 1px solid #b0b0b0; padding: 2px 6px;")
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
        finally:
            self._syncing_props = False

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
            self.pen_params[pen_id] = {
                "loop": self.sp_loop.value(),
                "speed": self.sp_speed.value(),
                "power": self.sp_power.value(),
                "freq": self.sp_freq.value(),
                "start_tc": self.sp_start_tc.value(),
                "laser_off_tc": self.sp_off_tc.value(),
                "end_tc": self.sp_end_tc.value(),
                "poly_tc": self.sp_poly_tc.value(),
                "on": True
            }

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

    # --- Hatch Dialog ---
    def _open_hatch_dialog(self):
        selected = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]
        if not selected:
            QMessageBox.information(self, "Hatch", "Select a closed contour shape to apply hatch fill.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Hatch Parameters (EzCad)")
        layout = QVBoxLayout(dlg)

        grid = QGridLayout()
        grid.addWidget(QLabel("Line Pitch / Spacing [MM]:"), 0, 0)
        sp_pitch = QDoubleSpinBox()
        sp_pitch.setRange(0.01, 10.0)
        sp_pitch.setValue(0.1)
        sp_pitch.setDecimals(3)
        grid.addWidget(sp_pitch, 0, 1)

        grid.addWidget(QLabel("Hatch Angle [Deg]:"), 1, 0)
        sp_angle = QDoubleSpinBox()
        sp_angle.setRange(-360.0, 360.0)
        sp_angle.setValue(45.0)
        grid.addWidget(sp_angle, 1, 1)

        cb_cross = QCheckBox("Cross Hatch (2nd Pass +90°)")
        cb_cross.setChecked(True)
        grid.addWidget(cb_cross, 2, 0, 1, 2)

        layout.addLayout(grid)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            pitch = sp_pitch.value()
            angle = sp_angle.value()
            cross = cb_cross.isChecked()

            for item in selected:
                hatch_item = CadHatchItem(item, line_pitch=pitch, angle_deg=angle, cross_hatch=cross)
                hatch_item.set_pen(item.pen_id)
                self.scene.addItem(hatch_item)

            self.scene.update()
            self._refresh_object_list_table()

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

    def _reset_counter(self):
        self.part_counter = 0
        self.lbl_part_no.setText("0")

    # --- Hardware Execution: Red Pointer (F1) & Marking (F2) ---
    def _toggle_red_light(self):
        if not self.is_framing:
            # Start Red Light Framing
            shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
            if self.cb_mark_select.isChecked():
                shapes = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]

            if not shapes:
                QMessageBox.information(self, "Red Light Guide", "Add or select shapes to guide frame.")
                return

            # Compute bounding box
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            for item in shapes:
                b = item.sceneTransform().mapRect(item.boundingRect())
                min_x = min(min_x, b.left())
                max_x = max(max_x, b.right())
                min_y = min(min_y, b.top())
                max_y = max(max_y, b.bottom())

            # Draw visual framing rectangle on canvas
            if self.framing_rect_item and self.framing_rect_item.scene() == self.scene:
                self.scene.removeItem(self.framing_rect_item)

            frame_pen = QPen(QColor("#e74c3c"), 0.8, Qt.PenStyle.DashDotLine)
            frame_pen.setCosmetic(True)
            self.framing_rect_item = QGraphicsRectItem(QRectF(min_x, min_y, max_x - min_x, max_y - min_y))
            self.framing_rect_item.setPen(frame_pen)
            self.framing_rect_item.setZValue(3000)
            self.scene.addItem(self.framing_rect_item)

            # Hardware red pointer
            if self.main_window and hasattr(self.main_window, 'galvo_controller'):
                ctrl = self.main_window.galvo_controller
                if getattr(ctrl, 'is_connected', False) and ctrl.connection:
                    try:
                        from galvo_threads import PreviewThread
                        self.preview_thread = PreviewThread(ctrl, min_x, max_x, min_y, max_y)
                        self.preview_thread.start()
                    except Exception as e:
                        print(f"Hardware red pointer frame started via connection: {e}")
                        if hasattr(ctrl.connection, 'reddot_on'):
                            ctrl.connection.reddot_on()

            self.is_framing = True
            self.btn_red_light.setText("STOP (F1)")
            self.btn_red_light.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; min-width: 68px; min-height: 28px;")

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
            self.btn_red_light.setStyleSheet("background: #e8e8e8; font-weight: bold; min-width: 68px; min-height: 28px;")

    def _execute_mark(self):
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if self.cb_mark_select.isChecked():
            shapes = [item for item in self.scene.selectedItems() if isinstance(item, CadShapeItem)]

        if not shapes:
            QMessageBox.information(self, "Mark", "No shapes to mark.")
            return

        if not self.main_window or not hasattr(self.main_window, 'planner'):
            QMessageBox.warning(self, "Engine", "Galvo MotionPlanner engine not found.")
            return

        planner = self.main_window.planner
        planner.clear()

        # Group shapes by pen_id so each pen uses its specific speed, power, freq
        shapes_by_pen = {}
        for item in shapes:
            shapes_by_pen.setdefault(item.pen_id, []).append(item)

        for pen_id, pen_shapes in sorted(shapes_by_pen.items()):
            p_params = self.pen_params[pen_id] if pen_id < len(self.pen_params) else self.pen_params[0]
            mark_speed = int(p_params["speed"])
            jump_speed = 3000

            for loop_i in range(p_params["loop"]):
                for item in pen_shapes:
                    path = item.scene_painter_path()
                    for polygon in path.toSubpathPolygons():
                        if len(polygon) < 2:
                            continue

                        # 1. Jump to start
                        start_pt = polygon[0]
                        planner.add_jump(start_pt.x(), start_pt.y(), speed=jump_speed)

                        # 2. Mark through vertices
                        for pt in polygon[1:]:
                            planner.add_mark(pt.x(), pt.y(), speed=mark_speed)

                        # 3. Close contour if closed
                        if item.is_closed and polygon.isClosed():
                            planner.add_mark(start_pt.x(), start_pt.y(), speed=mark_speed)

        # Update counter
        self.part_counter += 1
        self.total_counter += 1
        self.lbl_part_no.setText(str(self.part_counter))
        self.lbl_total_no.setText(str(self.total_counter))

        # Check if hardware is connected and run
        if hasattr(self.main_window, 'galvo_controller') and getattr(self.main_window.galvo_controller, 'is_connected', False):
            try:
                # Set laser power/freq from current pen
                curr_p = self.pen_params[self.current_pen_idx]
                self.main_window.galvo_controller.live_power = curr_p["power"]
                self.main_window.galvo_controller.live_freq = curr_p["freq"]
                # Invoke execution
                if hasattr(self.main_window, 'printGalvoAction') and hasattr(self.main_window, 'ui') and hasattr(self.main_window.ui, 'printrungalvoPushButton'):
                    self.main_window.printGalvoAction(self.main_window.ui.printrungalvoPushButton)
            except Exception as e:
                print(f"Error triggering galvo controller: {e}")
        else:
            QMessageBox.information(
                self, "Mark Queued",
                f"Generated {len(planner.send_queue)} laser commands for {len(shapes)} shapes across active pens.\n(Galvo hardware in simulation/offline mode)"
            )
