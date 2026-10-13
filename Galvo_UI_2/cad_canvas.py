import math
import os
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, Slot
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont,
    QCursor, QTransform, QWheelEvent, QMouseEvent, QKeyEvent, QIcon
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
    QGraphicsRectItem, QGraphicsEllipseItem, QInputDialog,
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame
)

from cad_items import (
    CadShapeItem, CadLineItem, CadRectItem, CadCircleItem, CadTextItem,
    SelectionHandleBox
)


class CadScene(QGraphicsScene):
    """
    Precision 2D CAD Graphics Scene in millimeter real-world coordinates.
    Origin (0, 0) is centered on the Galvo marking field.
    """
    coordinateChanged = Signal(float, float)
    selectionChangedCustom = Signal()

    def __init__(self, field_size_mm: float = 110.0, parent=None):
        super().__init__(parent)
        self.field_size = field_size_mm
        half = field_size_mm / 2.0
        self.setSceneRect(-half - 15.0, -half - 15.0, field_size_mm + 30.0, field_size_mm + 30.0)
        
        self.active_tool = "select"
        self.snap_enabled = True
        self.snap_grid_size = 1.0  # mm
        
        # Interactive drawing state
        self.start_scene_pt = None
        self.temp_preview_item = None
        self.selection_box = None
        
        # Dragging handle state
        self.dragging_handle = SelectionHandleBox.HANDLE_NONE
        self.handle_drag_start_pt = None
        self.handle_target_init_pos = None

        self.selectionChanged.connect(self._on_scene_selection_changed)

    def set_tool(self, tool_name: str):
        self.active_tool = tool_name
        if self.temp_preview_item:
            self.removeItem(self.temp_preview_item)
            self.temp_preview_item = None
        self.start_scene_pt = None
        if tool_name != "select":
            self.clearSelection()

    def snap_point(self, pt: QPointF) -> QPointF:
        if not self.snap_enabled or self.snap_grid_size <= 0:
            return pt
        grid = self.snap_grid_size
        sx = round(pt.x() / grid) * grid
        sy = round(pt.y() / grid) * grid
        return QPointF(sx, sy)

    def _on_scene_selection_changed(self):
        selected = [item for item in self.selectedItems() if isinstance(item, CadShapeItem)]
        if self.selection_box:
            self.removeItem(self.selection_box)
            self.selection_box = None

        if len(selected) == 1:
            self.selection_box = SelectionHandleBox(selected[0])
            self.addItem(self.selection_box)

        self.selectionChangedCustom.emit()
        self.update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # 1. Fill deep dark modern canvas background
        painter.fillRect(rect, QColor("#1e222d"))

        # 2. Draw physical Galvo bed area
        half = self.field_size / 2.0
        bed_rect = QRectF(-half, -half, self.field_size, self.field_size)
        painter.fillRect(bed_rect, QColor("#151820"))
        
        bed_border_pen = QPen(QColor("#2f3640"), 0.5)
        bed_border_pen.setCosmetic(True)
        painter.setPen(bed_border_pen)
        painter.drawRect(bed_rect)

        # 3. Millimeter Grid Lines (Major: 10mm, Minor: 1mm or 5mm)
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        minor_pen = QPen(QColor("#232733"), 0.5)
        minor_pen.setCosmetic(True)
        major_pen = QPen(QColor("#2e3444"), 0.8)
        major_pen.setCosmetic(True)

        # Draw vertical grid
        for x in range(left, right + 1):
            if x % 10 == 0:
                painter.setPen(major_pen)
                painter.drawLine(x, top, x, bottom)
            elif x % 2 == 0 and abs(painter.transform().m11()) > 1.5:
                painter.setPen(minor_pen)
                painter.drawLine(x, top, x, bottom)

        # Draw horizontal grid
        for y in range(top, bottom + 1):
            if y % 10 == 0:
                painter.setPen(major_pen)
                painter.drawLine(left, y, right, y)
            elif y % 2 == 0 and abs(painter.transform().m11()) > 1.5:
                painter.setPen(minor_pen)
                painter.drawLine(left, y, right, y)

        # 4. Center Coordinate Axes Crosshairs at (0, 0)
        axis_pen_x = QPen(QColor("#ff4757"), 1.0)
        axis_pen_x.setCosmetic(True)
        painter.setPen(axis_pen_x)
        painter.drawLine(-half, 0, half, 0)

        axis_pen_y = QPen(QColor("#2ed573"), 1.0)
        axis_pen_y.setCosmetic(True)
        painter.setPen(axis_pen_y)
        painter.drawLine(0, -half, 0, half)

    def mousePressEvent(self, event):
        scene_pt = event.scenePos()
        self.coordinateChanged.emit(scene_pt.x(), scene_pt.y())

        # Check if clicking on an interactive handle
        if self.selection_box and self.active_tool == "select":
            h_id = self.selection_box.handle_at_point(scene_pt, tolerance_mm=3.0 / event.widget().transform().m11() if event.widget() else 2.0)
            if h_id != SelectionHandleBox.HANDLE_NONE:
                self.dragging_handle = h_id
                self.handle_drag_start_pt = scene_pt
                self.handle_target_init_pos = self.selection_box.target_item.pos()
                event.accept()
                return

        if self.active_tool == "select":
            super().mousePressEvent(event)
        elif self.active_tool in ("line", "rect", "circle"):
            self.start_scene_pt = self.snap_point(scene_pt)
            preview_pen = QPen(QColor("#00d2ff"), 0.3, Qt.PenStyle.DashLine)
            preview_pen.setCosmetic(True)

            if self.active_tool == "line":
                self.temp_preview_item = QGraphicsLineItem(QLineF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)
            elif self.active_tool == "rect":
                self.temp_preview_item = QGraphicsRectItem(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)
            elif self.active_tool == "circle":
                self.temp_preview_item = QGraphicsEllipseItem(QRectF(self.start_scene_pt, self.start_scene_pt))
                self.temp_preview_item.setPen(preview_pen)

            if self.temp_preview_item:
                self.addItem(self.temp_preview_item)
            event.accept()
        elif self.active_tool == "text":
            pos = self.snap_point(scene_pt)
            text_str, ok = QInputDialog.getText(None, "Add Text", "Enter text to vectorize:")
            if ok and text_str.strip():
                item = CadTextItem(text_str.strip(), pos, font_size_mm=10.0)
                self.addItem(item)
                self.clearSelection()
                item.setSelected(True)
                self.set_tool("select")
            event.accept()

    def mouseMoveEvent(self, event):
        scene_pt = event.scenePos()
        self.coordinateChanged.emit(scene_pt.x(), scene_pt.y())

        # Handle dragging / scaling / rotating
        if self.dragging_handle != SelectionHandleBox.HANDLE_NONE and self.selection_box:
            delta = scene_pt - self.handle_drag_start_pt
            target = self.selection_box.target_item
            if self.dragging_handle == SelectionHandleBox.HANDLE_ROTATE:
                # Rotate around target center
                center = target.mapToScene(target.boundingRect().center())
                angle = math.degrees(math.atan2(scene_pt.y() - center.y(), scene_pt.x() - center.x())) + 90.0
                target.setTransformOriginPoint(target.boundingRect().center())
                target.setRotation(angle)
            else:
                # Scale item proportionally or free
                scale_factor = 1.0 + (delta.x() + delta.y()) / 100.0
                if scale_factor > 0.05:
                    target.setTransformOriginPoint(target.boundingRect().center())
                    target.setScale(scale_factor)
            self.selection_box.update()
            event.accept()
            return

        if self.temp_preview_item and self.start_scene_pt:
            cur_pt = self.snap_point(scene_pt)
            
            # Shift key constraint
            is_shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

            if self.active_tool == "line":
                if is_shift:
                    # Snap line to 0, 45, 90 deg
                    dx = cur_pt.x() - self.start_scene_pt.x()
                    dy = cur_pt.y() - self.start_scene_pt.y()
                    if abs(dx) > abs(dy) * 2:
                        cur_pt.setY(self.start_scene_pt.y())
                    elif abs(dy) > abs(dx) * 2:
                        cur_pt.setX(self.start_scene_pt.x())
                    else:
                        sign_y = 1 if dy >= 0 else -1
                        cur_pt.setY(self.start_scene_pt.y() + abs(dx) * sign_y)
                self.temp_preview_item.setLine(QLineF(self.start_scene_pt, cur_pt))

            elif self.active_tool == "rect":
                rx = min(self.start_scene_pt.x(), cur_pt.x())
                ry = min(self.start_scene_pt.y(), cur_pt.y())
                rw = abs(cur_pt.x() - self.start_scene_pt.x())
                rh = abs(cur_pt.y() - self.start_scene_pt.y())
                if is_shift:
                    side = max(rw, rh)
                    rw = rh = side
                self.temp_preview_item.setRect(QRectF(rx, ry, rw, rh))

            elif self.active_tool == "circle":
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
            if self.selection_box:
                self.selection_box.update()
            event.accept()
            return

        if self.temp_preview_item and self.start_scene_pt:
            cur_pt = self.snap_point(event.scenePos())
            self.removeItem(self.temp_preview_item)
            self.temp_preview_item = None
            
            created_item = None
            if self.active_tool == "line":
                if math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y()) > 0.2:
                    created_item = CadLineItem(self.start_scene_pt, cur_pt)

            elif self.active_tool == "rect":
                rx = min(self.start_scene_pt.x(), cur_pt.x())
                ry = min(self.start_scene_pt.y(), cur_pt.y())
                rw = abs(cur_pt.x() - self.start_scene_pt.x())
                rh = abs(cur_pt.y() - self.start_scene_pt.y())
                if rw > 0.2 and rh > 0.2:
                    created_item = CadRectItem(QRectF(rx, ry, rw, rh))

            elif self.active_tool == "circle":
                radius = math.hypot(cur_pt.x() - self.start_scene_pt.x(), cur_pt.y() - self.start_scene_pt.y())
                if radius > 0.2:
                    created_item = CadCircleItem(self.start_scene_pt, radius)

            if created_item:
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
            for item in self.selectedItems():
                if isinstance(item, CadShapeItem):
                    self.removeItem(item)
            self.clearSelection()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.set_tool("select")
            event.accept()
        else:
            super().keyPressEvent(event)


class CadView(QGraphicsView):
    """Interactive CAD Viewport with smooth zoom, pan, and millimeter precision."""
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
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor("#1e222d")))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._is_panning = False
        self._pan_start_pos = None

    def wheelEvent(self, event: QWheelEvent):
        # Smooth mouse-centered zoom
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        # Middle click or Space+Left click to pan
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier and self.cad_scene.active_tool == "select"):
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
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self._pan_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def zoom_to_fit(self):
        half = self.cad_scene.field_size / 2.0
        self.fitInView(-half - 10.0, -half - 10.0, self.cad_scene.field_size + 20.0, self.cad_scene.field_size + 20.0, Qt.AspectRatioMode.KeepAspectRatio)


class CadCanvasWidget(QWidget):
    """
    Complete CAD Canvas Page with top toolbar, viewport, status coordinates,
    and Galvo engine integration.
    """
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

        self.scene = CadScene(field_size_mm=110.0, parent=self)
        self.view = CadView(self.scene, parent=self)

        self._init_ui()
        self.scene.coordinateChanged.connect(self._update_coord_label)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # --- Top Toolbar ---
        tb_frame = QFrame()
        tb_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                border: 1px solid #4a6278;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
                color: black;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
            }
        """)
        tb_layout = QHBoxLayout(tb_frame)
        tb_layout.setContentsMargins(5, 2, 5, 2)
        tb_layout.setSpacing(6)

        self.btn_select = QPushButton("Select")
        self.btn_select.setCheckable(True)
        self.btn_select.setChecked(True)
        self.btn_select.clicked.connect(lambda: self._select_tool("select"))
        tb_layout.addWidget(self.btn_select)

        self.btn_line = QPushButton("Line")
        self.btn_line.setCheckable(True)
        self.btn_line.clicked.connect(lambda: self._select_tool("line"))
        tb_layout.addWidget(self.btn_line)

        self.btn_rect = QPushButton("Rectangle")
        self.btn_rect.setCheckable(True)
        self.btn_rect.clicked.connect(lambda: self._select_tool("rect"))
        tb_layout.addWidget(self.btn_rect)

        self.btn_circle = QPushButton("Circle")
        self.btn_circle.setCheckable(True)
        self.btn_circle.clicked.connect(lambda: self._select_tool("circle"))
        tb_layout.addWidget(self.btn_circle)

        self.btn_text = QPushButton("Text")
        self.btn_text.setCheckable(True)
        self.btn_text.clicked.connect(lambda: self._select_tool("text"))
        tb_layout.addWidget(self.btn_text)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #7f8c8d;")
        tb_layout.addWidget(sep1)

        self.btn_del = QPushButton("Delete")
        self.btn_del.setStyleSheet("background-color: #c0392b; color: white;")
        self.btn_del.clicked.connect(self._delete_selected)
        tb_layout.addWidget(self.btn_del)

        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.clicked.connect(self._clear_all)
        tb_layout.addWidget(self.btn_clear)

        self.btn_fit = QPushButton("Fit Bed")
        self.btn_fit.clicked.connect(self.view.zoom_to_fit)
        tb_layout.addWidget(self.btn_fit)

        self.cb_snap = QCheckBox("Snap Grid")
        self.cb_snap.setChecked(True)
        self.cb_snap.setStyleSheet("color: white; font-weight: bold;")
        self.cb_snap.toggled.connect(self._toggle_snap)
        tb_layout.addWidget(self.cb_snap)

        tb_layout.addStretch()

        # Export & Engrave Buttons
        self.btn_dxf = QPushButton("Export DXF")
        self.btn_dxf.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        self.btn_dxf.clicked.connect(self._export_dxf)
        tb_layout.addWidget(self.btn_dxf)

        self.btn_engrave = QPushButton("Engrave on Galvo")
        self.btn_engrave.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px 16px;")
        self.btn_engrave.clicked.connect(self._send_to_galvo)
        tb_layout.addWidget(self.btn_engrave)

        layout.addWidget(tb_frame)

        # --- Center Viewport ---
        layout.addWidget(self.view, stretch=1)

        # --- Bottom Status Bar ---
        sb_frame = QFrame()
        sb_frame.setStyleSheet("background-color: #1e222d; border-top: 1px solid #2f3640; padding: 2px;")
        sb_layout = QHBoxLayout(sb_frame)
        sb_layout.setContentsMargins(10, 2, 10, 2)

        self.lbl_coord = QLabel("X: 0.00 mm | Y: 0.00 mm")
        self.lbl_coord.setStyleSheet("color: #00d2ff; font-weight: bold; font-family: Consolas, monospace;")
        sb_layout.addWidget(self.lbl_coord)

        sb_layout.addStretch()

        self.lbl_info = QLabel(f"Galvo Bed: {self.scene.field_size:.0f}×{self.scene.field_size:.0f} mm | Shapes: 0")
        self.lbl_info.setStyleSheet("color: #a4b0be; font-size: 11px;")
        sb_layout.addWidget(self.lbl_info)

        layout.addWidget(sb_frame)

    def _select_tool(self, tool_name: str):
        self.scene.set_tool(tool_name)
        self.btn_select.setChecked(tool_name == "select")
        self.btn_line.setChecked(tool_name == "line")
        self.btn_rect.setChecked(tool_name == "rect")
        self.btn_circle.setChecked(tool_name == "circle")
        self.btn_text.setChecked(tool_name == "text")

    def _toggle_snap(self, checked: bool):
        self.scene.snap_enabled = checked

    def _delete_selected(self):
        for item in self.scene.selectedItems():
            if isinstance(item, CadShapeItem):
                self.scene.removeItem(item)
        self.scene.clearSelection()
        self._update_shape_count()

    def _clear_all(self):
        reply = QMessageBox.question(self, "Clear Canvas", "Remove all vector shapes from the canvas?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item in list(self.scene.items()):
                if isinstance(item, CadShapeItem):
                    self.scene.removeItem(item)
            self.scene.clearSelection()
            self._update_shape_count()

    def _update_coord_label(self, x: float, y: float):
        self.lbl_coord.setText(f"X: {x:+.2f} mm | Y: {y:+.2f} mm")
        self._update_shape_count()

    def _update_shape_count(self):
        count = sum(1 for item in self.scene.items() if isinstance(item, CadShapeItem))
        self.lbl_info.setText(f"Galvo Bed: {self.scene.field_size:.0f}×{self.scene.field_size:.0f} mm | Shapes: {count}")

    def _export_dxf(self):
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if not shapes:
            QMessageBox.information(self, "Empty Canvas", "Draw at least one shape before exporting.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CAD to DXF", "cad_drawing.dxf", "DXF Files (*.dxf)")
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
                    is_closed = item.is_closed
                    msp.add_lwpolyline(pts, close=is_closed)

            doc.saveas(file_path)
            QMessageBox.information(self, "Export Complete", f"Successfully saved DXF to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export DXF: {e}")

    def _send_to_galvo(self):
        shapes = [item for item in self.scene.items() if isinstance(item, CadShapeItem)]
        if not shapes:
            QMessageBox.information(self, "Empty Canvas", "Draw at least one shape to engrave.")
            return

        if not self.main_window:
            QMessageBox.warning(self, "Error", "Main application reference not connected.")
            return

        # Convert all canvas paths into MotionPlanner queue
        planner = getattr(self.main_window, 'planner', None)
        if not planner:
            QMessageBox.warning(self, "Error", "MotionPlanner not found on main window.")
            return

        planner.clear()
        
        # Read marking speed from UI or use 1000 mm/s default
        mark_speed = 1000
        if hasattr(self.main_window, 'programgalvo_widgets') and hasattr(self.main_window.programgalvo_widgets, 'pgmmarkspeedgalvo'):
            try:
                mark_speed = int(self.main_window.wh.invokeMethod(self.main_window.programgalvo_widgets.pgmmarkspeedgalvo, "get") or 1000)
            except:
                mark_speed = 1000

        for item in shapes:
            path = item.scene_painter_path()
            for polygon in path.toSubpathPolygons():
                if len(polygon) < 2:
                    continue

                # 1. Jump to start point (laser off)
                start_pt = polygon[0]
                planner.add_jump(start_pt.x(), start_pt.y(), speed=mark_speed)

                # 2. Mark through vertices (laser on)
                for pt in polygon[1:]:
                    planner.add_mark(pt.x(), pt.y(), speed=mark_speed)

                # 3. Close contour if closed shape
                if item.is_closed and polygon.isClosed():
                    planner.add_mark(start_pt.x(), start_pt.y(), speed=mark_speed)

        # Update preview and switch to Print Galvo page
        if hasattr(self.main_window, 'galvo_preview'):
            self.main_window.galvo_preview.draw_queue(planner.send_queue)

        if hasattr(self.main_window, 'showMainPages'):
            self.main_window.showMainPages("printgalvo")

        self.main_window.showAutoCloseMessage(
            "CAD Shapes Loaded",
            f"Loaded {len(shapes)} CAD vector shapes ({len(planner.send_queue)} commands) into Galvo queue.",
            timeout_ms=3000
        )
