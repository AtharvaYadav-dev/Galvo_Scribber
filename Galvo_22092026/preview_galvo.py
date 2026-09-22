try:
    from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPen, QColor, QPainter, QPainterPath
except ImportError:
    print("Warning: PySide6 not installed. Please run: pip install PySide6")
    # Mock classes for when PySide6 is not available
    class QGraphicsView:
        def __init__(self, parent=None): pass
    class QGraphicsScene:
        def __init__(self, parent=None): pass

from core.coordinate_mapper import galvo_to_mm

class GalvoPreviewWidget(QGraphicsView):
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
            self.mark_pen.setWidthF(0.2)
            
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
        
        field_size = self.config.field_size if self.config else 100.0
        target_x_mm, target_y_mm = self._get_preview_coords(x, y, field_size)
        
        if not hasattr(self, 'laser_cursor'):
            from PySide6.QtGui import QBrush
            self.laser_cursor = self.scene.addEllipse(-1, -1, 2, 2, QPen(QColor(0, 255, 0)), QBrush(QColor(0, 255, 0)))
            self.laser_cursor.setZValue(100) # keep on top
        else:
            import shiboken6
            if not shiboken6.isValid(self.laser_cursor):
                from PySide6.QtGui import QBrush
                self.laser_cursor = self.scene.addEllipse(-1, -1, 2, 2, QPen(QColor(0, 255, 0)), QBrush(QColor(0, 255, 0)))
                self.laser_cursor.setZValue(100)
            
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
        
        for cmd in queue:
            if 'x' in cmd and 'y' in cmd:
                target_x_mm, target_y_mm = self._get_preview_coords(cmd['x'], cmd['y'], field_size)
                
                if cmd['type'] == 'jump':
                    jump_path.moveTo(current_x_mm, current_y_mm)
                    jump_path.lineTo(target_x_mm, target_y_mm)
                elif cmd['type'] == 'mark':
                    mark_path.moveTo(current_x_mm, current_y_mm)
                    mark_path.lineTo(target_x_mm, target_y_mm)
                    
                current_x_mm = target_x_mm
                current_y_mm = target_y_mm

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
