try:
    from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QPen, QColor, QPainter, QPainterPath, QBrush, QFont
except ImportError:
    print("Warning: PySide6 not installed. Please run: pip install PySide6")
    # Mock classes for when PySide6 is not available
    class QGraphicsView:
        def __init__(self, parent=None): pass
    class QGraphicsScene:
        def __init__(self, parent=None): pass
    class Signal:
        def __init__(self, *args): pass
        def connect(self, f): pass
        def emit(self, *args): pass

from core.coordinate_mapper import galvo_to_mm

class GalvoPreviewWidget(QGraphicsView):
    part_selected_signal = Signal(int)
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config
        
        if 'QGraphicsScene' in globals():
            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            
            self.setRenderHint(QPainter.Antialiasing)
            self.scene.setBackgroundBrush(QColor("white"))
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self._initial_fit_done = False
            
            # Setup physical coordinates where (0,0) is center
            field_size = self.config.field_size if self.config else 100.0
            half_field = field_size / 2.0
            self.scene.setSceneRect(-half_field, -half_field, field_size, field_size)
            
            self.mark_pen = QPen(QColor(255, 0, 0)) # Red for marking (Laser ON)
            self.mark_pen.setWidthF(0) # 0 means cosmetic pen (1 pixel wide regardless of zoom)
            
            self.jump_pen = QPen(QColor(150, 150, 150, 150)) # Gray dashed for jumps (Laser OFF)
            self.jump_pen.setStyle(Qt.DashLine)
            self.jump_pen.setWidthF(0.1)

    def _get_preview_coords(self, galvo_x, galvo_y, field_size):
        if self.config and hasattr(self.config, 'reverse_transform'):
            pure_x, pure_y = self.config.reverse_transform(galvo_x, galvo_y)
            import math
            rad = math.radians(self.config.angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            x_rot = pure_x * cos_a - pure_y * sin_a
            y_rot = pure_x * sin_a + pure_y * cos_a
            preview_x = x_rot + self.config.offset_x
            preview_y = y_rot + self.config.offset_y
            return preview_x, -preview_y
        else:
            return galvo_to_mm(galvo_x, field_size), -galvo_to_mm(galvo_y, field_size)

    def reset_progress(self):
        if hasattr(self, 'laser_cursor'):
            try:
                # Only try to remove if it's still a valid C++ object
                import shiboken6
                if shiboken6.isValid(self.laser_cursor):
                    self.scene.removeItem(self.laser_cursor)
            except Exception:
                pass
            del self.laser_cursor

    def update_progress(self, idx, x, y, ctype):
        if not hasattr(self, 'scene'): return
        
        field_size = self.config.field_size if self.config else 70.0
        target_x_mm, target_y_mm = self._get_preview_coords(x, y, field_size)

        # In split printing "whole" mode, offset by the active tile's center in design space
        # so the green dot tracks the actual printed part's quadrant/position accurately
        if (hasattr(self, 'split_mgr') and self.split_mgr and 
            getattr(self.split_mgr, 'enabled', False) and 
            getattr(self.split_mgr, 'auto_center_on_lens', True) and
            getattr(self, 'split_view_mode', 'whole') == "whole"):
            active_t = self.split_mgr.get_active_tile()
            if active_t:
                cx, cy = active_t.center
                params = getattr(self.split_mgr, '_queue_params', {}) or {}
                sx = float(params.get('start_x', 0.0) or 0.0)
                sy = float(params.get('start_y', 0.0) or 0.0)
                target_x_mm += (cx - sx)
                target_y_mm -= (cy - sy)
        
        need_create = False
        if not hasattr(self, 'laser_cursor') or self.laser_cursor is None:
            need_create = True
        else:
            try:
                import shiboken6
                if not shiboken6.isValid(self.laser_cursor) or self.laser_cursor.scene() != self.scene:
                    need_create = True
            except Exception:
                need_create = True

        if need_create:
            from PySide6.QtGui import QBrush
            self.laser_cursor = self.scene.addEllipse(-0.8, -0.8, 1.6, 1.6, QPen(QColor(0, 0, 0, 220), 0.2), QBrush(QColor(34, 197, 94)))
            self.laser_cursor.setZValue(200) # keep on top
            
        self.laser_cursor.setPos(target_x_mm, target_y_mm)

    def draw_queue(self, queue):
        if not hasattr(self, 'scene'): return
        
        self.scene.clear()
        if hasattr(self, 'laser_cursor'):
            del self.laser_cursor
        
        # Draw field boundary
        field_size = self.config.field_size if self.config else 100.0
        bounds_pen = QPen(QColor(0, 0, 255))
        bounds_pen.setWidthF(0.5)
        half_field = field_size / 2.0
        self.scene.addRect(-half_field, -half_field, field_size, field_size, bounds_pen)
        
        current_x_mm = 0.0
        current_y_mm = 0.0
        
        jump_path = QPainterPath()
        mark_path = QPainterPath()
        is_marking = False
        
        for cmd in queue:
            ctype = cmd.get('type')
            if ctype in ('mark', 'jump') and 'x' in cmd and 'y' in cmd:
                target_x_mm, target_y_mm = self._get_preview_coords(cmd['x'], cmd['y'], field_size)
                
                if ctype == 'jump':
                    jump_path.moveTo(current_x_mm, current_y_mm)
                    jump_path.lineTo(target_x_mm, target_y_mm)
                    is_marking = False
                elif ctype == 'mark':
                    if not is_marking:
                        mark_path.moveTo(current_x_mm, current_y_mm)
                        is_marking = True
                    mark_path.lineTo(target_x_mm, target_y_mm)
                    
                current_x_mm = target_x_mm
                current_y_mm = target_y_mm
            elif ctype in ('laser_off', 'delay'):
                is_marking = False

        if not jump_path.isEmpty():
            self.scene.addPath(jump_path, self.jump_pen)
        if not mark_path.isEmpty():
            self.scene.addPath(mark_path, self.mark_pen)

        # Ensure everything is visible initially
        if not getattr(self, '_initial_fit_done', False):
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self._initial_fit_done = True
        
    def reset_view(self):
        if hasattr(self, 'scene'):
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            
    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.reset_view()
        super().mouseDoubleClickEvent(event)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'scene') and not getattr(self, '_initial_fit_done', False):
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and hasattr(self, 'split_mgr') and self.split_mgr and getattr(self.split_mgr, 'enabled', False) and getattr(self, 'split_view_mode', 'whole') == "whole":
            scene_pos = self.mapToScene(event.pos())
            mm_x = scene_pos.x()
            mm_y = -scene_pos.y()
            for tile in self.split_mgr.tiles:
                xmin, ymin, xmax, ymax = tile.rect
                if xmin <= mm_x <= xmax and ymin <= mm_y <= ymax:
                    self.part_selected_signal.emit(tile.index)
                    break
        super().mousePressEvent(event)

    def draw_split_preview(self, split_mgr, view_mode="whole"):
        """
        Renders the full split design on the canvas:
        - Whole design vectors visible across all parts.
        - Inactive parts rendered in clean slate gray.
        - Active part highlighted in vibrant laser red with an emerald glow box and badge.
        - Split grid cut lines rendered in dashed amber.
        - Physical lens field boundary rendered in blue.
        """
        if not hasattr(self, 'scene'):
            return

        self.split_mgr = split_mgr
        self.split_view_mode = view_mode
        self.scene.clear()
        if hasattr(self, 'laser_cursor'):
            del self.laser_cursor

        field_size = self.config.field_size if self.config else 100.0
        half_field = field_size / 2.0

        # Physical galvo field boundary (blue)
        bounds_pen = QPen(QColor(30, 144, 255))
        bounds_pen.setWidthF(0.6)
        self.scene.addRect(-half_field, -half_field, field_size, field_size, bounds_pen)

        # Subtle center crosshair
        cross_pen = QPen(QColor(210, 215, 225, 160))
        cross_pen.setWidthF(0.2)
        cross_pen.setStyle(Qt.DashLine)
        self.scene.addLine(-half_field, 0, half_field, 0, cross_pen)
        self.scene.addLine(0, -half_field, 0, half_field, cross_pen)

        if not split_mgr or not split_mgr.tiles:
            return

        if view_mode == "active_lens":
            active_tile = split_mgr.get_active_tile()
            if active_tile:
                self.draw_queue(active_tile.galvo_queue)
            return

        # 1. Tile bounding boxes, active highlight & badges
        active_idx = split_mgr.active_part_idx
        for tile in split_mgr.tiles:
            xmin, ymin, xmax, ymax = tile.rect
            scene_x = xmin
            scene_y = -ymax
            scene_w = max(0.1, xmax - xmin)
            scene_h = max(0.1, ymax - ymin)

            is_active = (tile.index == active_idx)
            is_done = getattr(tile, 'is_completed', False) or (hasattr(split_mgr, 'is_part_completed') and split_mgr.is_part_completed(tile.index))

            if is_active:
                if is_done:
                    # Active and already printed: vibrant emerald border + green tint
                    box_pen = QPen(QColor(16, 185, 129)) # Emerald-500
                    box_pen.setWidthF(1.2)
                    box_brush = QBrush(QColor(16, 185, 129, 40))
                    badge_text = f"★ {tile.label} (DONE)"
                    badge_color = QColor(16, 185, 129)
                else:
                    # Active and ready to print: sky blue border + glow
                    box_pen = QPen(QColor(14, 165, 233)) # Sky Blue
                    box_pen.setWidthF(1.2)
                    box_brush = QBrush(QColor(14, 165, 233, 30))
                    badge_text = f"★ {tile.label}"
                    badge_color = QColor(14, 165, 233)

                r_item = self.scene.addRect(scene_x, scene_y, scene_w, scene_h, box_pen, box_brush)
                r_item.setZValue(2)

                badge = self.scene.addSimpleText(badge_text)
                font_act = QFont("Arial", -1, QFont.Bold)
                font_act.setPixelSize(2) # Small, clean and unobtrusive
                badge.setFont(font_act)
                badge.setBrush(QBrush(badge_color))
                badge.setPos(scene_x + 1.0, scene_y + 0.8)
                badge.setZValue(10)

            elif is_done:
                # Inactive but completed/printed: solid green box + green badge
                box_pen = QPen(QColor(34, 197, 94)) # Green-500
                box_pen.setWidthF(1.2)
                box_brush = QBrush(QColor(34, 197, 94, 30)) # Translucent green
                r_item = self.scene.addRect(scene_x, scene_y, scene_w, scene_h, box_pen, box_brush)
                r_item.setZValue(1)

                badge = self.scene.addSimpleText(f"✔ {tile.label}")
                font_done = QFont("Arial", -1, QFont.Bold)
                font_done.setPixelSize(2) # Small and clean
                badge.setFont(font_done)
                badge.setBrush(QBrush(QColor(34, 197, 94)))
                badge.setPos(scene_x + 1.2, scene_y + 1.0)
                badge.setZValue(3)

            else:
                # Inactive and not yet printed: slate gray dashed box
                inactive_box_pen = QPen(QColor(148, 163, 184, 160))
                inactive_box_pen.setWidthF(0.8)
                inactive_box_pen.setStyle(Qt.DashLine)
                r_item = self.scene.addRect(scene_x, scene_y, scene_w, scene_h, inactive_box_pen)
                r_item.setZValue(1)

                badge = self.scene.addSimpleText(tile.label)
                font_inact = QFont("Arial")
                font_inact.setPixelSize(2) # Small and clean
                badge.setFont(font_inact)
                badge.setBrush(QBrush(QColor(148, 163, 184)))
                badge.setPos(scene_x + 1.2, scene_y + 1.0)
                badge.setZValue(3)

        # 2. Draw design vector paths:
        # - Completed parts: GREEN
        # - Active unprinted part: BRIGHT LASER RED
        # - Inactive unprinted parts: SLATE GRAY
        done_path_pen = QPen(QColor(34, 197, 94)) # Vibrant Green
        done_path_pen.setWidthF(1.1)

        active_path_pen = QPen(QColor(239, 68, 68)) # Laser Red
        active_path_pen.setWidthF(1.3)

        inactive_path_pen = QPen(QColor(148, 163, 184, 200)) # Slate Gray
        inactive_path_pen.setWidthF(0.8)

        for tile in split_mgr.tiles:
            is_active = (tile.index == active_idx)
            is_done = getattr(tile, 'is_completed', False) or (hasattr(split_mgr, 'is_part_completed') and split_mgr.is_part_completed(tile.index))

            if is_done:
                pen_to_use = done_path_pen
                z_val = 6 if is_active else 5
            elif is_active:
                pen_to_use = active_path_pen
                z_val = 6
            else:
                pen_to_use = inactive_path_pen
                z_val = 4

            combined_path = QPainterPath()
            for poly in tile.polygons:
                if len(poly) < 2:
                    continue
                combined_path.moveTo(poly[0][0], -poly[0][1])
                for pt in poly[1:]:
                    combined_path.lineTo(pt[0], -pt[1])

            if not combined_path.isEmpty():
                path_item = self.scene.addPath(combined_path, pen_to_use)
                path_item.setZValue(z_val)

        # 3. Draw dashed amber split divider lines
        divider_pen = QPen(QColor(245, 158, 11, 220)) # Amber
        divider_pen.setWidthF(1.2)
        divider_pen.setStyle(Qt.DashLine)

        min_x, min_y, max_x, max_y = split_mgr.bounds
        cols = split_mgr.num_cols
        rows = split_mgr.num_rows
        tile_w = split_mgr.design_width / cols
        tile_h = split_mgr.design_height / rows

        for c in range(1, cols):
            div_x = min_x + c * tile_w
            div_line = self.scene.addLine(div_x, -max_y, div_x, -min_y, divider_pen)
            div_line.setZValue(7)

        for r in range(1, rows):
            div_y = max_y - r * tile_h
            div_line = self.scene.addLine(min_x, -div_y, max_x, -div_y, divider_pen)
            div_line.setZValue(7)

        # Auto-fit view to encompass both the field and the design
        design_rect = self.scene.itemsBoundingRect()
        union_rect = design_rect.united(self.scene.sceneRect())
        self.fitInView(union_rect, Qt.KeepAspectRatio)

    def update_split_active_tile(self, active_idx):
        """Quick refresh when active tile changes."""
        if hasattr(self, 'split_mgr') and self.split_mgr:
            self.split_mgr.set_active_part(active_idx)
            self.draw_split_preview(self.split_mgr, getattr(self, 'split_view_mode', 'whole'))

