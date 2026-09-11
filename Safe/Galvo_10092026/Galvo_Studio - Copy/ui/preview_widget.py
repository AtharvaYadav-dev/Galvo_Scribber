try:
    from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPen, QColor, QPainter
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
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            
            # Setup physical coordinates where (0,0) is center
            field_size = self.config.field_size if self.config else 100.0
            half_field = field_size / 2.0
            self.scene.setSceneRect(-half_field, -half_field, field_size, field_size)
            
            self.mark_pen = QPen(QColor(255, 0, 0)) # Red for marking (Laser ON)
            self.mark_pen.setWidthF(0.2)
            
            self.jump_pen = QPen(QColor(150, 150, 150, 150)) # Gray dashed for jumps (Laser OFF)
            self.jump_pen.setStyle(Qt.DashLine)
            self.jump_pen.setWidthF(0.1)
            
            self._initial_fit_done = False

    def draw_queue(self, queue):
        if not hasattr(self, 'scene'): return
        
        self.scene.clear()
        
        # Draw field boundary
        field_size = self.config.field_size if self.config else 100.0
        bounds_pen = QPen(QColor(0, 0, 255))
        bounds_pen.setWidthF(0.5)
        half_field = field_size / 2.0
        self.scene.addRect(-half_field, -half_field, field_size, field_size, bounds_pen)
        
        current_x_mm = 0.0
        current_y_mm = 0.0
        
        for cmd in queue:
            if 'x' in cmd and 'y' in cmd:
                target_x_mm = galvo_to_mm(cmd['x'], field_size)
                # Invert Y to match typical screen coordinates vs galvo coordinates
                target_y_mm = -galvo_to_mm(cmd['y'], field_size) 
                
                if cmd['type'] == 'jump':
                    self.scene.addLine(current_x_mm, current_y_mm, target_x_mm, target_y_mm, self.jump_pen)
                elif cmd['type'] == 'mark':
                    self.scene.addLine(current_x_mm, current_y_mm, target_x_mm, target_y_mm, self.mark_pen)
                    
                current_x_mm = target_x_mm
                current_y_mm = target_y_mm

        # Ensure everything is visible initially
        if not self._initial_fit_done:
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
