import math
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont,
    QCursor, QTransform
)
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsPathItem,
    QStyleOptionGraphicsItem, QWidget
)


class CadShapeItem(QGraphicsItem):
    """
    Base class for all CAD vector shapes.
    Maintains geometry in millimeter scene coordinates, stroke/fill styling,
    and supports vector path conversion for laser toolpaths.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.stroke_color = QColor("#00d2ff")
        self.stroke_width = 0.2  # mm
        self.fill_color = QColor(0, 0, 0, 0)  # Transparent by default
        self.is_closed = True

    def to_painter_path(self) -> QPainterPath:
        """Return local vector QPainterPath. Must be overridden by subclasses."""
        return QPainterPath()

    def scene_painter_path(self) -> QPainterPath:
        """Return absolute scene-space vector QPainterPath with all transforms applied."""
        return self.sceneTransform().map(self.to_painter_path())

    def shape(self) -> QPainterPath:
        """Hit-test region including stroke width."""
        p = self.to_painter_path()
        from PySide6.QtGui import QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(max(1.0, self.stroke_width))
        return stroker.createStroke(p)

    def boundingRect(self) -> QRectF:
        p = self.to_painter_path()
        pad = self.stroke_width / 2.0 + 1.0
        return p.boundingRect().adjusted(-pad, -pad, pad, pad)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        pen = QPen(self.stroke_color, self.stroke_width)
        pen.setCosmetic(False)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        if self.isSelected():
            # Highlight selected item outline
            pen.setColor(QColor("#ff9f43"))
            pen.setWidthF(max(self.stroke_width, 0.4))

        painter.setPen(pen)
        painter.setBrush(QBrush(self.fill_color))
        painter.drawPath(self.to_painter_path())


class CadLineItem(CadShapeItem):
    """Interactive CAD Line Segment."""
    def __init__(self, p1: QPointF, p2: QPointF, parent=None):
        super().__init__(parent)
        self.p1 = p1
        self.p2 = p2
        self.is_closed = False

    def set_endpoints(self, p1: QPointF, p2: QPointF):
        self.prepareGeometryChange()
        self.p1 = p1
        self.p2 = p2
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(self.p1)
        path.lineTo(self.p2)
        return path


class CadRectItem(CadShapeItem):
    """Interactive CAD Rectangle."""
    def __init__(self, rect: QRectF, corner_radius: float = 0.0, parent=None):
        super().__init__(parent)
        self.rect = rect.normalized()
        self.corner_radius = corner_radius
        self.is_closed = True

    def set_rect(self, rect: QRectF):
        self.prepareGeometryChange()
        self.rect = rect.normalized()
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        if self.corner_radius > 0:
            path.addRoundedRect(self.rect, self.corner_radius, self.corner_radius)
        else:
            path.addRect(self.rect)
        return path


class CadCircleItem(CadShapeItem):
    """Interactive CAD Circle / Ellipse."""
    def __init__(self, center: QPointF, rx: float, ry: float = None, parent=None):
        super().__init__(parent)
        self.center = center
        self.rx = abs(rx)
        self.ry = abs(ry) if ry is not None else self.rx
        self.is_closed = True

    def set_circle(self, center: QPointF, rx: float, ry: float = None):
        self.prepareGeometryChange()
        self.center = center
        self.rx = abs(rx)
        self.ry = abs(ry) if ry is not None else self.rx
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self.center, self.rx, self.ry)
        return path


class CadTextItem(CadShapeItem):
    """Interactive CAD Text converted to vector contours."""
    def __init__(self, text: str, pos: QPointF, font_size_mm: float = 10.0, font_family: str = "Arial", parent=None):
        super().__init__(parent)
        self.text = text
        self.pos_origin = pos
        self.font_size_mm = font_size_mm
        self.font_family = font_family
        self.is_closed = True
        self._cached_path = None
        self._update_text_path()

    def set_text(self, text: str, font_size_mm: float = None, font_family: str = None):
        self.prepareGeometryChange()
        self.text = text
        if font_size_mm is not None:
            self.font_size_mm = font_size_mm
        if font_family is not None:
            self.font_family = font_family
        self._update_text_path()
        self.update()

    def _update_text_path(self):
        self._cached_path = QPainterPath()
        font = QFont(self.font_family)
        # 1 pt approx 0.352778 mm, or set pixel size
        # In scene mm: 1 scene unit = 1 mm. Set point size or pixel size to font_size_mm
        font.setPixelSize(max(1, int(round(self.font_size_mm))))
        self._cached_path.addText(self.pos_origin, font, self.text)

    def to_painter_path(self) -> QPainterPath:
        if self._cached_path is None:
            self._update_text_path()
        return self._cached_path


class SelectionHandleBox(QGraphicsItem):
    """
    Selection Bounding Box with 8 Resize Handles and 1 Rotation Handle.
    Handles use screen-space invariant rendering so they stay readable across any zoom.
    """
    HANDLE_NONE = -1
    HANDLE_TOP_LEFT = 0
    HANDLE_TOP = 1
    HANDLE_TOP_RIGHT = 2
    HANDLE_RIGHT = 3
    HANDLE_BOTTOM_RIGHT = 4
    HANDLE_BOTTOM = 5
    HANDLE_BOTTOM_LEFT = 6
    HANDLE_LEFT = 7
    HANDLE_ROTATE = 8

    def __init__(self, target_item: CadShapeItem, parent=None):
        super().__init__(parent)
        self.target_item = target_item
        self.setZValue(1000)  # Always render above shapes
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.handle_pixel_size = 8.0  # Screen pixels
        self.rotate_dist_pixels = 22.0
        self.active_handle = self.HANDLE_NONE
        self.drag_start_scene_pos = QPointF()
        self.initial_transform = QTransform()
        self.initial_bounds = QRectF()

    def target_scene_bounds(self) -> QRectF:
        if not self.target_item or not self.target_item.scene():
            return QRectF()
        return self.target_item.mapRectToScene(self.target_item.boundingRect())

    def boundingRect(self) -> QRectF:
        rect = self.target_scene_bounds()
        if rect.isEmpty():
            return QRectF()
        pad = 30.0  # Generous padding to cover rotation handle and drag bounds
        return rect.adjusted(-pad, -pad, pad, pad)

    def get_handle_positions(self) -> dict:
        rect = self.target_scene_bounds()
        if rect.isEmpty():
            return {}
        cx = rect.center().x()
        cy = rect.center().y()
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()

        return {
            self.HANDLE_TOP_LEFT: QPointF(left, top),
            self.HANDLE_TOP: QPointF(cx, top),
            self.HANDLE_TOP_RIGHT: QPointF(right, top),
            self.HANDLE_RIGHT: QPointF(right, cy),
            self.HANDLE_BOTTOM_RIGHT: QPointF(right, bottom),
            self.HANDLE_BOTTOM: QPointF(cx, bottom),
            self.HANDLE_BOTTOM_LEFT: QPointF(left, bottom),
            self.HANDLE_LEFT: QPointF(left, cy),
            self.HANDLE_ROTATE: QPointF(cx, top - 15.0),
        }

    def handle_at_point(self, scene_pt: QPointF, tolerance_mm: float = 2.0) -> int:
        handles = self.get_handle_positions()
        for h_id, pt in handles.items():
            dist = math.hypot(scene_pt.x() - pt.x(), scene_pt.y() - pt.y())
            if dist <= tolerance_mm:
                return h_id
        return self.HANDLE_NONE

    def cursor_for_handle(self, h_id: int) -> Qt.CursorShape:
        mapping = {
            self.HANDLE_TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
            self.HANDLE_TOP: Qt.CursorShape.SizeVerCursor,
            self.HANDLE_TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
            self.HANDLE_RIGHT: Qt.CursorShape.SizeHorCursor,
            self.HANDLE_BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
            self.HANDLE_BOTTOM: Qt.CursorShape.SizeVerCursor,
            self.HANDLE_BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
            self.HANDLE_LEFT: Qt.CursorShape.SizeHorCursor,
            self.HANDLE_ROTATE: Qt.CursorShape.PointingHandCursor,
        }
        return mapping.get(h_id, Qt.CursorShape.ArrowCursor)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        if not self.target_item or not self.target_item.isSelected():
            return

        rect = self.target_scene_bounds()
        if rect.isEmpty():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Calculate screen zoom scaling to keep handles screen-invariant
        scale = painter.transform().m11()
        if abs(scale) < 1e-4:
            scale = 1.0
        h_size = self.handle_pixel_size / scale
        half_h = h_size / 2.0
        r_offset = self.rotate_dist_pixels / scale

        # Draw bounding rectangle
        bound_pen = QPen(QColor("#00a8ff"), 1.0 / scale, Qt.PenStyle.DashLine)
        bound_pen.setCosmetic(True)
        painter.setPen(bound_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

        # Draw line to rotation handle
        cx = rect.center().x()
        rot_pt = QPointF(cx, rect.top() - r_offset)
        painter.drawLine(QPointF(cx, rect.top()), rot_pt)

        # Draw resize handles
        handle_pen = QPen(QColor("#0070ba"), 1.0 / scale)
        handle_pen.setCosmetic(True)
        painter.setPen(handle_pen)
        painter.setBrush(QBrush(QColor("#ffffff")))

        handles = self.get_handle_positions()
        handles[self.HANDLE_ROTATE] = rot_pt

        for h_id, pt in handles.items():
            if h_id == self.HANDLE_ROTATE:
                # Circle handle for rotation
                painter.setBrush(QBrush(QColor("#2ed573")))
                painter.drawEllipse(pt, half_h, half_h)
            else:
                painter.setBrush(QBrush(QColor("#ffffff")))
                painter.drawRect(QRectF(pt.x() - half_h, pt.y() - half_h, h_size, h_size))
