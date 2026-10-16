import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, Qt
from PySide6.QtWidgets import QApplication

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from cad_canvas import CadCanvasWidget
from core.motion_planner import MotionPlanner
from core.coordinate_mapper import CoordinateConfig


class MockMainWindow:
    """Lightweight adapter providing required galvo controller & planner attributes to CadCanvasWidget."""
    def __init__(self, galvo_controller):
        self.galvo_controller = galvo_controller
        self.planner = MotionPlanner()
        self.galvo_config = CoordinateConfig()
        self.galvo_threads = {}


class CadBridge(QObject):
    """
    QObject Bridge for 2D Vector CAD Operations, DXF/SVG Loading,
    Red-Guide Framing (F1), and Laser Marking (F2).
    """
    cadStateChanged = Signal()
    framingChanged = Signal(bool)
    markingChanged = Signal(bool)
    progressChanged = Signal(int, int, float) # current, total, percent
    shapeCountChanged = Signal(int)

    def __init__(self, galvo_bridge=None, parent=None):
        super().__init__(parent)
        self.galvo_bridge = galvo_bridge
        self.galvo_controller = galvo_bridge.controller if galvo_bridge else None

        # Adapter for CadCanvasWidget
        self._adapter = MockMainWindow(self.galvo_controller)
        self.cad_widget = None
        self._cad_window = None

        self._is_framing = False
        self._is_marking = False
        self._shape_count = 0
        self._field_size = 100.0

    # ---------------- Properties for QML ---------------- #

    def get_is_framing(self) -> bool:
        return self._is_framing

    def get_is_marking(self) -> bool:
        return self._is_marking

    def get_shape_count(self) -> int:
        return self._shape_count

    def get_field_size(self) -> float:
        return self._field_size

    isFraming = Property(bool, get_is_framing, notify=framingChanged)
    isMarking = Property(bool, get_is_marking, notify=markingChanged)
    shapeCount = Property(int, get_shape_count, notify=shapeCountChanged)
    fieldSize = Property(float, get_field_size, notify=cadStateChanged)

    # ---------------- Slots for QML ---------------- #

    @Slot()
    def openCadEditor(self):
        """Opens or brings to focus the high-precision 2D CAD Canvas window."""
        if self.cad_widget is None:
            self.cad_widget = CadCanvasWidget(main_window=self._adapter)
            self.cad_widget.setWindowTitle("Galvo Studio - 2D CAD Canvas & Hatching Editor")
            self.cad_widget.resize(1150, 750)
            
            # Connect scene changes to QML bridge
            if hasattr(self.cad_widget, 'scene'):
                self.cad_widget.scene.changed.connect(self._on_scene_changed)

        self.cad_widget.show()
        self.cad_widget.raise_()
        self.cad_widget.activateWindow()
        self._on_scene_changed()

    @Slot(str)
    def importFile(self, file_path: str):
        """Imports a DXF or SVG vector file into the CAD canvas."""
        if not file_path:
            return
        # Remove file:/// prefix if from QML file picker
        if file_path.startswith("file:///"):
            file_path = file_path[8:]
        file_path = os.path.normpath(file_path)

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        if self.cad_widget is None:
            self.openCadEditor()

        try:
            if file_path.lower().endswith(".dxf"):
                if hasattr(self.cad_widget, "_import_dxf_file"):
                    self.cad_widget._import_dxf_file(file_path)
            elif file_path.lower().endswith(".svg"):
                if hasattr(self.cad_widget, "_import_svg_file"):
                    self.cad_widget._import_svg_file(file_path)
            self._on_scene_changed()
        except Exception as e:
            print(f"Error importing file: {e}")

    @Slot()
    def toggleFraming(self):
        """Toggles red pointer bounding frame (F1) around all objects."""
        if self.cad_widget is None:
            self.openCadEditor()
        try:
            self.cad_widget._toggle_red_light()
            self._is_framing = getattr(self.cad_widget, 'is_framing', False)
            self.framingChanged.emit(self._is_framing)
        except Exception as e:
            print(f"Framing error: {e}")

    @Slot()
    def executeMark(self):
        """Executes laser marking (F2) for all vector shapes and hatches."""
        if self.cad_widget is None:
            self.openCadEditor()
        try:
            self._is_marking = True
            self.markingChanged.emit(True)
            self.cad_widget._execute_mark()
        except Exception as e:
            print(f"Execution mark error: {e}")
        finally:
            self._is_marking = getattr(self.cad_widget, 'is_marking', False)
            self.markingChanged.emit(self._is_marking)

    @Slot()
    def abortMark(self):
        """Aborts active laser marking or red pointer framing."""
        if self.cad_widget:
            if hasattr(self.cad_widget, '_abort_mark'):
                self.cad_widget._abort_mark()
            if getattr(self.cad_widget, 'is_framing', False):
                self.cad_widget._toggle_red_light()

        self._is_marking = False
        self._is_framing = False
        self.markingChanged.emit(False)
        self.framingChanged.emit(False)

    def _on_scene_changed(self, *args):
        if self.cad_widget and hasattr(self.cad_widget, 'scene'):
            from cad_items import CadShapeItem
            shapes = [it for it in self.cad_widget.scene.items() if isinstance(it, CadShapeItem)]
            self._shape_count = len(shapes)
            self.shapeCountChanged.emit(self._shape_count)
