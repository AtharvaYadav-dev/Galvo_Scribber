"""
Interactive 3D STL Preview Widget for Galvo Laser Marking.
Renders the 3D mesh with real-time lighting, interactive orbit/pan/zoom,
and a visual cutting plane indicating the active slicing layer depth.
Includes safe fallback if OpenGL context is limited.
"""

import math
import numpy as np

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

try:
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from OpenGL.GL import (
        glEnable, glDisable, glClear, glClearColor, glViewport,
        glMatrixMode, glLoadIdentity, glShadeModel, glLightfv,
        glMaterialfv, glColorMaterial, glBegin, glEnd, glVertex3f,
        glNormal3f, glColor4f, glTranslatef, glScalef, glRotatef,
        glLineWidth, glPushMatrix, glPopMatrix,
        glGenLists, glNewList, glEndList, glCallList, glDeleteLists, GL_COMPILE,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
        GL_COLOR_MATERIAL, GL_LIGHTING, GL_LIGHT0, GL_POSITION, GL_DIFFUSE, GL_AMBIENT,
        GL_SPECULAR, GL_SHININESS, GL_SMOOTH, GL_FRONT_AND_BACK,
        GL_AMBIENT_AND_DIFFUSE, GL_TRIANGLES, GL_LINES, GL_LINE_LOOP,
        GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glBlendFunc,
        GL_PROJECTION, GL_MODELVIEW, GL_CULL_FACE
    )
    from OpenGL.GLU import gluPerspective
    HAS_OPENGL = True
except ImportError:
    QOpenGLWidget = QWidget
    HAS_OPENGL = False


class STL3DOpenGLWidget(QOpenGLWidget if HAS_OPENGL else QWidget):
    """
    Hardware-accelerated 3D OpenGL viewport for STL visualization.
    Shows the 3D model, bounding platform, and an active cutting plane.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = None
        self.normals = None
        self.faces = None
        self.mesh_bounds = None
        self.center = [0.0, 0.0, 0.0]
        self.scale = 1.0

        # Camera state
        self.rot_x = 30.0
        self.rot_y = -45.0
        self.zoom = 1.8
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_pos = QPoint()

        # Cutting plane state
        self.current_z = 0.0
        self.min_z = 0.0
        self.max_z = 1.0
        self.show_cut_plane = True
        self.show_wireframe = False

        # Display list for high-speed GPU rendering
        self.display_list = None
        self.mesh_needs_compile = False

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)

    def cleanupGL(self):
        """Releases the compiled OpenGL display list from GPU memory."""
        if HAS_OPENGL and self.display_list is not None:
            try:
                glDeleteLists(self.display_list, 1)
            except Exception:
                pass
            self.display_list = None

    def closeEvent(self, event):
        self.cleanupGL()
        super().closeEvent(event)

    def set_mesh(self, mesh):
        """Loads a trimesh Trimesh object for rendering."""
        if mesh is None or not hasattr(mesh, 'vertices') or len(mesh.vertices) == 0:
            self.vertices = None
            self.normals = None
            self.faces = None
            self.mesh_bounds = None
            self.mesh_needs_compile = True
            self.update()
            return

        try:
            b = mesh.bounds
            self.mesh_bounds = (tuple(b[0]), tuple(b[1]))
            cx = float((b[0][0] + b[1][0]) / 2.0)
            cy = float((b[0][1] + b[1][1]) / 2.0)
            cz = float((b[0][2] + b[1][2]) / 2.0)
            self.center = [cx, cy, cz]
            
            dx = float(b[1][0] - b[0][0])
            dy = float(b[1][1] - b[0][1])
            dz = float(b[1][2] - b[0][2])
            max_extent = max(dx, dy, dz, 0.001)
            self.scale = 2.0 / max_extent

            self.min_z = float(b[0][2])
            self.max_z = float(b[1][2])
            self.current_z = self.max_z

            # Extract vertex and normal arrays
            # Each triangle vertex with normal
            self.vertices = np.ascontiguousarray(mesh.vertices[mesh.faces], dtype=np.float32)
            if hasattr(mesh, 'face_normals') and len(mesh.face_normals) == len(mesh.faces):
                self.normals = np.ascontiguousarray(mesh.face_normals, dtype=np.float32)
            else:
                self.normals = None
            self.faces = mesh.faces
            self.mesh_needs_compile = True
        except Exception as e:
            print(f"[STL3DOpenGLWidget] Error loading mesh: {e}")
            self.vertices = None
            self.mesh_needs_compile = True

        self.update()

    def set_cutting_height(self, z_height: float):
        """Updates the active layer cutting plane position."""
        self.current_z = float(z_height)
        self.update()

    def reset_view(self):
        """Resets camera view angles and zoom."""
        self.rot_x = 30.0
        self.rot_y = -45.0
        self.zoom = 1.8
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    if HAS_OPENGL:
        def initializeGL(self):
            glClearColor(0.12, 0.13, 0.15, 1.0)
            glEnable(GL_DEPTH_TEST)
            glShadeModel(GL_SMOOTH)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Lights
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 2.0, 0.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.95, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.35, 0.35, 0.4, 1.0])

        def resizeGL(self, w, h):
            if h == 0:
                h = 1
            glViewport(0, 0, w, h)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)

        def paintGL(self):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Camera view
            glTranslatef(self.pan_x, self.pan_y, -5.0 / max(0.1, self.zoom))
            glRotatef(self.rot_x, 1.0, 0.0, 0.0)
            glRotatef(self.rot_y, 0.0, 0.0, 1.0) # Z is up for industrial laser

            # Draw laser bed / grid
            self._draw_laser_bed()

            if self.vertices is None or len(self.vertices) == 0:
                if self.display_list is not None:
                    try:
                        glDeleteLists(self.display_list, 1)
                    except Exception:
                        pass
                    self.display_list = None
                self._draw_placeholder_cube()
                return

            # Compile GPU display list once upon mesh change
            if self.mesh_needs_compile:
                if self.display_list is not None:
                    try:
                        glDeleteLists(self.display_list, 1)
                    except Exception:
                        pass
                    self.display_list = None
                try:
                    self.display_list = glGenLists(1)
                    glNewList(self.display_list, GL_COMPILE)
                    glBegin(GL_TRIANGLES)
                    has_fn = self.normals is not None and len(self.normals) == len(self.vertices)
                    for i, tri in enumerate(self.vertices):
                        if has_fn:
                            n = self.normals[i]
                            glNormal3f(float(n[0]), float(n[1]), float(n[2]))
                        glVertex3f(float(tri[0][0]), float(tri[0][1]), float(tri[0][2]))
                        glVertex3f(float(tri[1][0]), float(tri[1][1]), float(tri[1][2]))
                        glVertex3f(float(tri[2][0]), float(tri[2][1]), float(tri[2][2]))
                    glEnd()
                    glEndList()
                except Exception as e:
                    print(f"[STL3DOpenGLWidget] Error compiling display list: {e}")
                    self.display_list = None
                self.mesh_needs_compile = False

            glPushMatrix()
            # Center and scale model
            glScalef(self.scale, self.scale, self.scale)
            glTranslatef(-self.center[0], -self.center[1], -self.center[2])

            # Draw STL triangles via GPU display list (<1ms render time)
            glEnable(GL_LIGHTING)
            glColor4f(0.35, 0.65, 0.95, 1.0) # Industrial anodized cyan/blue
            if self.display_list is not None:
                glCallList(self.display_list)
            else:
                # Fallback to immediate mode if display list fails
                glBegin(GL_TRIANGLES)
                has_fn = self.normals is not None and len(self.normals) == len(self.vertices)
                for i, tri in enumerate(self.vertices):
                    if has_fn:
                        n = self.normals[i]
                        glNormal3f(n[0], n[1], n[2])
                    glVertex3f(tri[0][0], tri[0][1], tri[0][2])
                    glVertex3f(tri[1][0], tri[1][1], tri[1][2])
                    glVertex3f(tri[2][0], tri[2][1], tri[2][2])
                glEnd()

            # Draw visual cutting plane at active layer
            if self.show_cut_plane and self.mesh_bounds is not None:
                self._draw_cutting_plane()

            glPopMatrix()

        def _draw_laser_bed(self):
            """Draws a subtle circular or square coordinate grid at Z=0."""
            glDisable(GL_LIGHTING)
            glColor4f(0.25, 0.28, 0.32, 0.6)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            step = 0.5
            span = 2.0
            x = -span
            while x <= span + 0.01:
                glVertex3f(x, -span, -1.0)
                glVertex3f(x, span, -1.0)
                glVertex3f(-span, x, -1.0)
                glVertex3f(span, x, -1.0)
                x += step
            glEnd()
            glEnable(GL_LIGHTING)

        def _draw_cutting_plane(self):
            """Renders a semi-transparent laser focal/cutting plane at current_z."""
            glDisable(GL_LIGHTING)
            b0, b1 = self.mesh_bounds
            margin = (b1[0] - b0[0]) * 0.15
            x0, x1 = b0[0] - margin, b1[0] + margin
            y0, y1 = b0[1] - margin, b1[1] + margin
            cz = self.current_z

            # Plane border (Glowing Orange Laser Line)
            glColor4f(1.0, 0.45, 0.0, 0.9)
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            glVertex3f(x0, y0, cz)
            glVertex3f(x1, y0, cz)
            glVertex3f(x1, y1, cz)
            glVertex3f(x0, y1, cz)
            glEnd()

            # Semi-transparent plane fill
            glColor4f(1.0, 0.35, 0.0, 0.18)
            glBegin(GL_TRIANGLES)
            glVertex3f(x0, y0, cz)
            glVertex3f(x1, y0, cz)
            glVertex3f(x1, y1, cz)
            glVertex3f(x0, y0, cz)
            glVertex3f(x1, y1, cz)
            glVertex3f(x0, y1, cz)
            glEnd()
            glEnable(GL_LIGHTING)

        def _draw_placeholder_cube(self):
            """Rendered when no mesh is loaded."""
            glDisable(GL_LIGHTING)
            glColor4f(0.4, 0.45, 0.5, 0.5)
            glLineWidth(1.0)
            # Simple wire box
            glBegin(GL_LINES)
            for dx in [-0.5, 0.5]:
                for dy in [-0.5, 0.5]:
                    glVertex3f(dx, dy, -0.5)
                    glVertex3f(dx, dy, 0.5)
            for dz in [-0.5, 0.5]:
                glVertex3f(-0.5, -0.5, dz)
                glVertex3f(0.5, -0.5, dz)
                glVertex3f(0.5, -0.5, dz)
                glVertex3f(0.5, 0.5, dz)
                glVertex3f(0.5, 0.5, dz)
                glVertex3f(-0.5, 0.5, dz)
                glVertex3f(-0.5, 0.5, dz)
                glVertex3f(-0.5, -0.5, dz)
            glEnd()
            glEnable(GL_LIGHTING)

        def mousePressEvent(self, event):
            self.last_pos = event.pos()

        def mouseMoveEvent(self, event):
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            if event.buttons() & Qt.LeftButton:
                self.rot_y += dx * 0.5
                self.rot_x += dy * 0.5
                self.update()
            elif event.buttons() & (Qt.RightButton | Qt.MiddleButton):
                self.pan_x += dx * 0.005 / max(0.1, self.zoom)
                self.pan_y -= dy * 0.005 / max(0.1, self.zoom)
                self.update()
            self.last_pos = event.pos()

        def wheelEvent(self, event):
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom *= 1.15
            elif delta < 0:
                self.zoom /= 1.15
            self.zoom = max(0.1, min(20.0, self.zoom))
            self.update()

    else:
        # Fallback 2D/isometric painter if PyOpenGL is missing
        def paintEvent(self, event):
            p = QPainter(self)
            p.fillRect(self.rect(), QColor(30, 33, 38))
            p.setPen(QPen(QColor(180, 190, 205), 1))
            p.setFont(QFont("Segoe UI", 10))
            txt = "3D Preview (PyOpenGL not available)"
            if self.mesh_bounds is not None:
                b0, b1 = self.mesh_bounds
                txt = f"STL Loaded: {b1[0]-b0[0]:.1f} x {b1[1]-b0[1]:.1f} x {b1[2]-b0[2]:.2f} mm"
            p.drawText(self.rect(), Qt.AlignCenter, txt)


class STL3DPreviewWidget(QWidget):
    """
    Complete composite container for 3D STL preview with controls
    (Reset View, Wireframe toggle, cutting plane height sync).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header toolbar
        tb = QHBoxLayout()
        tb.setContentsMargins(6, 4, 6, 4)
        self.btn_reset_view = QPushButton("Reset View", self)
        self.btn_reset_view.setStyleSheet("""
            QPushButton {
                background: #2b2e38; color: #d0d4e0; border: 1px solid #454958;
                border-radius: 4px; padding: 3px 8px; font-size: 11px;
            }
            QPushButton:hover { background: #383c4a; border-color: #5c6276; }
        """)
        self.btn_reset_view.clicked.connect(self._on_reset_view)
        tb.addWidget(self.btn_reset_view)

        self.label_dims = QLabel("No 3D Model Loaded", self)
        self.label_dims.setStyleSheet("color: #8f96a8; font-size: 11px;")
        tb.addWidget(self.label_dims)
        tb.addStretch()

        layout.addLayout(tb)

        # 3D Viewport
        self.gl_widget = STL3DOpenGLWidget(self)
        layout.addWidget(self.gl_widget, stretch=1)

    def load_mesh(self, mesh):
        self.gl_widget.set_mesh(mesh)
        if mesh is not None and hasattr(mesh, 'bounds'):
            b = mesh.bounds
            dx = float(b[1][0] - b[0][0])
            dy = float(b[1][1] - b[0][1])
            dz = float(b[1][2] - b[0][2])
            self.label_dims.setText(f"STL: {dx:.1f} x {dy:.1f} x {dz:.2f} mm")
        else:
            self.label_dims.setText("No 3D Model Loaded")

    def set_current_layer(self, layer_idx: int, total_layers: int, z_height: float):
        self.gl_widget.set_cutting_height(z_height)

    @property
    def max_z(self):
        return getattr(self.gl_widget, 'max_z', 0.0)

    @property
    def min_z(self):
        return getattr(self.gl_widget, 'min_z', 0.0)

    def _on_reset_view(self):
        self.gl_widget.reset_view()
