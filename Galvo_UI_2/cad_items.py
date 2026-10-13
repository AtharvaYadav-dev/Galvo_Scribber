import math
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont,
    QCursor, QTransform, QImage, QPixmap
)
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsPathItem,
    QStyleOptionGraphicsItem, QWidget
)

# Standard EzCad 8-Pen Layer Color Palette
PEN_PALETTE = [
    "#000000",  # Pen 0: Black
    "#0000ff",  # Pen 1: Blue
    "#ff0000",  # Pen 2: Red
    "#00aa00",  # Pen 3: Green
    "#e67e22",  # Pen 4: Orange / Gold
    "#9b59b6",  # Pen 5: Magenta / Purple
    "#00a8ff",  # Pen 6: Cyan
    "#795548",  # Pen 7: Brown
]


class CadShapeItem(QGraphicsItem):
    """
    Base class for all CAD vector entities.
    Stores millimeter coordinates, EzCad pen assignment (0-7),
    and supports path extraction for Galvo laser planning.
    """
    _id_counter = 1

    def __init__(self, name: str = "", shape_type: str = "Shape", parent=None):
        super().__init__(parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        if not name:
            name = f"{shape_type}_{CadShapeItem._id_counter}"
            CadShapeItem._id_counter += 1
        self.name = name
        self.shape_type = shape_type
        
        self.pen_id = 0
        self.stroke_color = QColor(PEN_PALETTE[0])
        self.stroke_width = 0.25  # mm visual line thickness
        self.fill_color = QColor(0, 0, 0, 0)  # Transparent
        self.is_closed = True
        self.is_locked = False
        self.visible_in_laser = True

    def set_pen(self, pen_id: int):
        self.pen_id = max(0, min(7, pen_id))
        self.stroke_color = QColor(PEN_PALETTE[self.pen_id])
        self.update()

    def itemChange(self, change, value):
        if change in (
            QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged,
            QGraphicsItem.GraphicsItemChange.ItemSelectedChange
        ):
            sc = self.scene()
            if sc and hasattr(sc, "update_selection_box"):
                sc.update_selection_box()
            if sc and hasattr(sc, "shapeGeometryChanged"):
                sc.shapeGeometryChanged.emit(self)
        return super().itemChange(change, value)

    def to_painter_path(self) -> QPainterPath:
        """Return local vector QPainterPath. Must be overridden by subclasses."""
        return QPainterPath()

    def scene_painter_path(self) -> QPainterPath:
        """Return scene-space vector QPainterPath with all transforms applied."""
        return self.sceneTransform().map(self.to_painter_path())

    def shape(self) -> QPainterPath:
        p = self.to_painter_path()
        from PySide6.QtGui import QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(max(1.2, self.stroke_width))
        return stroker.createStroke(p)

    def boundingRect(self) -> QRectF:
        p = self.to_painter_path()
        pad = max(1.0, self.stroke_width / 2.0 + 0.5)
        return p.boundingRect().adjusted(-pad, -pad, pad, pad)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # When selected, EzCad highlights object in red/magenta or outline
        pen = QPen(self.stroke_color, self.stroke_width)
        pen.setCosmetic(False)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        if self.isSelected():
            pen.setColor(QColor("#e74c3c"))
            pen.setWidthF(max(self.stroke_width, 0.4))

        painter.setPen(pen)
        painter.setBrush(QBrush(self.fill_color))
        painter.drawPath(self.to_painter_path())


class CadLineItem(CadShapeItem):
    """2D CAD Line Segment."""
    def __init__(self, p1: QPointF, p2: QPointF, parent=None):
        super().__init__(shape_type="Line", parent=parent)
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
    """2D CAD Rectangle with optional corner radius."""
    def __init__(self, rect: QRectF, corner_radius: float = 0.0, parent=None):
        super().__init__(shape_type="Rect", parent=parent)
        self.rect = rect.normalized()
        self.corner_radius = corner_radius
        self.is_closed = True

    def set_rect(self, rect: QRectF, corner_radius: float = None):
        self.prepareGeometryChange()
        self.rect = rect.normalized()
        if corner_radius is not None:
            self.corner_radius = corner_radius
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        if self.corner_radius > 0:
            path.addRoundedRect(self.rect, self.corner_radius, self.corner_radius)
        else:
            path.addRect(self.rect)
        return path


class CadCircleItem(CadShapeItem):
    """2D CAD Circle / Ellipse."""
    def __init__(self, center: QPointF, rx: float, ry: float = None, parent=None):
        super().__init__(shape_type="Circle" if (ry is None or abs(rx - ry) < 1e-4) else "Ellipse", parent=parent)
        self.center = center
        self.rx = abs(rx)
        self.ry = abs(ry) if ry is not None else self.rx
        self.is_closed = True

    def set_circle(self, center: QPointF, rx: float, ry: float = None):
        self.prepareGeometryChange()
        self.center = center
        self.rx = abs(rx)
        self.ry = abs(ry) if ry is not None else self.rx
        self.shape_type = "Circle" if abs(self.rx - self.ry) < 1e-4 else "Ellipse"
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self.center, self.rx, self.ry)
        return path


class CadPolygonItem(CadShapeItem):
    """2D CAD Multi-point Closed Polygon / Regular Polygon."""
    def __init__(self, points: list, parent=None):
        super().__init__(shape_type="Polygon", parent=parent)
        self.points = [QPointF(p) for p in points]
        self.is_closed = True

    @classmethod
    def create_regular(cls, center: QPointF, radius: float, num_sides: int = 5):
        pts = []
        angle_step = 2.0 * math.pi / max(3, num_sides)
        start_angle = -math.pi / 2.0  # Top point
        for i in range(num_sides):
            a = start_angle + i * angle_step
            pts.append(QPointF(center.x() + radius * math.cos(a), center.y() + radius * math.sin(a)))
        return cls(pts)

    def set_points(self, points: list):
        self.prepareGeometryChange()
        self.points = [QPointF(p) for p in points]
        self.update()

    def to_painter_path(self) -> QPainterPath:
        path = QPainterPath()
        if not self.points:
            return path
        path.moveTo(self.points[0])
        for pt in self.points[1:]:
            path.lineTo(pt)
        path.closeSubpath()
        return path


class CadTextItem(CadShapeItem):
    """Vector CAD Text converted to outline paths for laser marking."""
    def __init__(self, text: str, pos: QPointF, font_size_mm: float = 8.0, font_family: str = "Arial", parent=None):
        super().__init__(shape_type="Text", parent=parent)
        self.text = text
        self.pos_origin = pos
        self.font_size_mm = font_size_mm
        self.font_family = font_family
        self.char_spacing = 0.0  # mm
        self.is_closed = True
        self._cached_path = None
        self._update_text_path()

    def set_text(self, text: str, font_size_mm: float = None, font_family: str = None, char_spacing: float = None):
        self.prepareGeometryChange()
        self.text = text
        if font_size_mm is not None:
            self.font_size_mm = font_size_mm
        if font_family is not None:
            self.font_family = font_family
        if char_spacing is not None:
            self.char_spacing = char_spacing
        self._update_text_path()
        self.update()

    def _update_text_path(self):
        self._cached_path = QPainterPath()
        font = QFont(self.font_family)
        # Font size in mm
        font.setPixelSize(max(2, int(round(self.font_size_mm))))
        self._cached_path.addText(self.pos_origin, font, self.text)

    def to_painter_path(self) -> QPainterPath:
        if self._cached_path is None:
            self._update_text_path()
        return self._cached_path


class CadBarcodeItem(CadShapeItem):
    """
    Vector QR Code / 2D Barcode entity.
    Generates actual vector square modules for laser marking.
    """
    def __init__(self, content: str, pos: QPointF, size_mm: float = 20.0, code_type: str = "QR Code", parent=None):
        super().__init__(shape_type="Barcode", parent=parent)
        self.content = content
        self.pos_origin = pos
        self.size_mm = max(5.0, size_mm)
        self.code_type = code_type
        self.is_closed = True
        self._cached_path = None
        self._generate_matrix_path()

    def set_content(self, content: str, size_mm: float = None, code_type: str = None):
        self.prepareGeometryChange()
        self.content = content
        if size_mm is not None:
            self.size_mm = max(5.0, size_mm)
        if code_type is not None:
            self.code_type = code_type
        self._generate_matrix_path()
        self.update()

    def _generate_matrix_path(self):
        self._cached_path = QPainterPath()
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=1,
                border=1,
            )
            qr.add_data(self.content)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            
            n = len(matrix)
            module_size = self.size_mm / float(n)
            ox = self.pos_origin.x()
            oy = self.pos_origin.y()
            
            for row in range(n):
                for col in range(n):
                    if matrix[row][col]:
                        rx = ox + col * module_size
                        ry = oy + row * module_size
                        self._cached_path.addRect(rx, ry, module_size, module_size)
        except Exception as e:
            # Fallback simple test matrix if qrcode fails
            ox = self.pos_origin.x()
            oy = self.pos_origin.y()
            self._cached_path.addRect(ox, oy, self.size_mm, self.size_mm)

    def to_painter_path(self) -> QPainterPath:
        if self._cached_path is None:
            self._generate_matrix_path()
        return self._cached_path


class CadHatchItem(CadShapeItem):
    """
    Vector Hatch Fill Entity.
    Generates parallel laser scanlines across closed shapes with angle and pitch.
    """
    def __init__(self, target_item: CadShapeItem, line_pitch: float = 0.1, angle_deg: float = 0.0, cross_hatch: bool = False, parent=None):
        super().__init__(shape_type="Hatch", parent=parent)
        self.target_name = target_item.name if target_item else ""
        self.line_pitch = max(0.01, line_pitch)
        self.angle_deg = angle_deg
        self.cross_hatch = cross_hatch
        self.is_closed = False
        self._cached_path = None
        if target_item:
            self.generate_hatch_from_shape(target_item)

    def generate_hatch_from_shape(self, target_item: CadShapeItem):
        self.prepareGeometryChange()
        self._cached_path = QPainterPath()
        poly_path = target_item.to_painter_path()
        bounds = poly_path.boundingRect()
        if bounds.isEmpty():
            return

        cx = bounds.center().x()
        cy = bounds.center().y()
        radius = math.hypot(bounds.width(), bounds.height()) / 2.0 + 1.0

        def add_lines_at_angle(angle):
            rad = math.radians(angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            # Normal vector perpendicular to scanline
            nx = -sin_a
            ny = cos_a
            
            # Line direction
            dx = cos_a
            dy = sin_a
            
            num_lines = int(2.0 * radius / self.line_pitch)
            for i in range(-num_lines // 2, num_lines // 2 + 1):
                offset = i * self.line_pitch
                # Point on line at center offset
                px = cx + nx * offset
                py = cy + ny * offset
                
                p_start = QPointF(px - dx * radius, py - dy * radius)
                p_end = QPointF(px + dx * radius, py + dy * radius)
                
                line_path = QPainterPath()
                line_path.moveTo(p_start)
                line_path.lineTo(p_end)
                
                # Intersect with the closed polygon
                clipped = poly_path.intersected(line_path)
                self._cached_path.addPath(clipped)

        add_lines_at_angle(self.angle_deg)
        if self.cross_hatch:
            add_lines_at_angle(self.angle_deg + 90.0)

        self.update()

    def to_painter_path(self) -> QPainterPath:
        return self._cached_path if self._cached_path is not None else QPainterPath()


class SelectionHandleBox(QGraphicsItem):
    """
    EzCad-style 9-point Interactive Bounding Box with 8 Resizing Handles
    and 1 Top Rotation Handle.
    Handles maintain constant screen-pixel size regardless of viewport zoom.
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
        self.setZValue(2000)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setFlags(QGraphicsItem.GraphicsItemFlag(0))
        
        self.handle_pixel_size = 7.0
        self.rotate_dist_pixels = 20.0
        self._last_scale = 1.0

    def target_scene_bounds(self) -> QRectF:
        if not self.target_item or not self.target_item.scene():
            return QRectF()
        return self.target_item.mapRectToScene(self.target_item.boundingRect())

    def boundingRect(self) -> QRectF:
        rect = self.target_scene_bounds()
        if rect.isEmpty():
            return QRectF()
        pad = 25.0
        return rect.adjusted(-pad, -pad, pad, pad)

    def get_handle_positions(self, scale: float = None) -> dict:
        rect = self.target_scene_bounds()
        if rect.isEmpty():
            return {}
        cx = rect.center().x()
        cy = rect.center().y()
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()

        s = scale if scale is not None and scale > 1e-4 else self._last_scale
        if s <= 1e-4:
            s = 1.0
        r_offset = self.rotate_dist_pixels / s

        return {
            self.HANDLE_TOP_LEFT: QPointF(left, top),
            self.HANDLE_TOP: QPointF(cx, top),
            self.HANDLE_TOP_RIGHT: QPointF(right, top),
            self.HANDLE_RIGHT: QPointF(right, cy),
            self.HANDLE_BOTTOM_RIGHT: QPointF(right, bottom),
            self.HANDLE_BOTTOM: QPointF(cx, bottom),
            self.HANDLE_BOTTOM_LEFT: QPointF(left, bottom),
            self.HANDLE_LEFT: QPointF(left, cy),
            self.HANDLE_ROTATE: QPointF(cx, top - r_offset),
        }

    def handle_at_point(self, scene_pt: QPointF, tolerance_mm: float = 2.0, scale: float = None) -> int:
        handles = self.get_handle_positions(scale=scale)
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
        scale = abs(painter.transform().m11())
        if scale < 1e-4:
            scale = 1.0
        self._last_scale = scale
        
        h_size = self.handle_pixel_size / scale
        half_h = h_size / 2.0
        r_offset = self.rotate_dist_pixels / scale

        # EzCad selection box: dark blue dashed outline
        bound_pen = QPen(QColor("#0055ff"), 1.0 / scale, Qt.PenStyle.DashLine)
        bound_pen.setCosmetic(True)
        painter.setPen(bound_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)

        # Rotation handle guide line
        cx = rect.center().x()
        rot_pt = QPointF(cx, rect.top() - r_offset)
        painter.drawLine(QPointF(cx, rect.top()), rot_pt)

        # Handles: black outlined white squares, green circle for rotation
        handle_pen = QPen(QColor("#000000"), 1.0 / scale)
        handle_pen.setCosmetic(True)
        painter.setPen(handle_pen)

        handles = self.get_handle_positions(scale=scale)
        for h_id, pt in handles.items():
            if h_id == self.HANDLE_ROTATE:
                painter.setBrush(QBrush(QColor("#2ecc71")))
                painter.drawEllipse(pt, half_h, half_h)
            else:
                painter.setBrush(QBrush(QColor("#ffffff")))
                painter.drawRect(QRectF(pt.x() - half_h, pt.y() - half_h, h_size, h_size))
