import os
from glob import glob
from PySide6.QtCore import QPointF
from core.mk_lib.tools.jhfparser import JhfFont
from core.mk_lib.tools.shxparser import ShxFont
from core.mk_lib.tools.ttfparser import TrueTypeFont

class GalvoFontPath:
    """
    Receives drawing commands from MeerK40t font parsers and constructs polygons.
    """
    def __init__(self):
        self.polygons = []
        self.current_poly = []
        self.cursor_x = 0
        self.cursor_y = 0

    def new_path(self):
        if self.current_poly:
            self.polygons.append(self.current_poly)
            self.current_poly = []

    def character_end(self):
        self.new_path()

    def move(self, x, y):
        self.new_path()
        self.cursor_x, self.cursor_y = x, y
        self.current_poly.append((x, y))

    def line(self, x0, y0, x1, y1):
        if not self.current_poly:
            self.current_poly.append((self.cursor_x, self.cursor_y))
        self.current_poly.append((x1, y1))
        self.cursor_x, self.cursor_y = x1, y1

    def quad(self, x0, y0, x1, y1, x2, y2):
        steps = 10
        if not self.current_poly:
            self.current_poly.append((self.cursor_x, self.cursor_y))
            
        start_x, start_y = self.cursor_x, self.cursor_y
        for i in range(1, steps + 1):
            t = i / steps
            x = (1 - t)**2 * start_x + 2 * (1 - t) * t * x1 + t**2 * x2
            y = (1 - t)**2 * start_y + 2 * (1 - t) * t * y1 + t**2 * y2
            self.current_poly.append((x, y))
            
        self.cursor_x, self.cursor_y = x2, y2

    def cubic(self, x0, y0, x1, y1, x2, y2, x3, y3):
        steps = 10
        if not self.current_poly:
            self.current_poly.append((self.cursor_x, self.cursor_y))
            
        start_x, start_y = self.cursor_x, self.cursor_y
        for i in range(1, steps + 1):
            t = i / steps
            x = (1-t)**3 * start_x + 3*(1-t)**2 * t * x1 + 3*(1-t) * t**2 * x2 + t**3 * x3
            y = (1-t)**3 * start_y + 3*(1-t)**2 * t * y1 + 3*(1-t) * t**2 * y2 + t**3 * y3
            self.current_poly.append((x, y))
            
        self.cursor_x, self.cursor_y = x3, y3

    def close(self):
        if self.current_poly and len(self.current_poly) > 1:
            self.current_poly.append(self.current_poly[0])
        self.new_path()

    def arc(self, x0, y0, cx, cy, x1, y1):
        # Simplify arc to a line for now
        self.line(None, None, x1, y1)

class TextParser:
    def __init__(self):
        self.fonts = {}
        self.load_system_fonts()

    def load_system_fonts(self):
        # Load standard windows fonts
        windir = os.environ.get("WINDIR", "C:\\Windows")
        font_dir = os.path.join(windir, "Fonts")
        
        # Load all TTF fonts
        ttf_files = glob(os.path.join(font_dir, "*.ttf"))
        for file in ttf_files:
            name = os.path.basename(file)
            self.fonts[name] = file
            
        # If user has some JHF or SHX in a local fonts folder, load them
        local_fonts = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.exists(local_fonts):
            for file in glob(os.path.join(local_fonts, "*.*")):
                if file.endswith('.ttf') or file.endswith('.jhf') or file.endswith('.shx'):
                    name = os.path.basename(file)
                    self.fonts[name] = file
                    
        # Sort fonts alphabetically
        self.fonts = dict(sorted(self.fonts.items()))

    def parse_text(self, text, font_name, font_size=50, align="start"):
        if font_name not in self.fonts:
            return []
            
        font_path = self.fonts[font_name]
        
        if font_path.lower().endswith('.ttf') or font_path.lower().endswith('.otf'):
            from PySide6.QtGui import QPainterPath, QFont, QFontDatabase
            
            db = QFontDatabase()
            font_id = db.addApplicationFont(font_path)
            if font_id != -1:
                family = db.applicationFontFamilies(font_id)[0]
                font = QFont(family, font_size)
                path = QPainterPath()
                path.addText(0, 0, font, text)
                polygons = path.toSubpathPolygons()
                
                res = []
                for poly in polygons:
                    pts = []
                    for i in range(poly.size()):
                        pt = poly.at(i)
                        # Negate Y because QPainterPath +Y goes down, but our system +Y goes up
                        pts.append((pt.x(), -pt.y()))
                    res.append(pts)
                return res
            return []
            
        elif font_path.lower().endswith('.jhf'):
            cfont = JhfFont(font_path)
        elif font_path.lower().endswith('.shx'):
            cfont = ShxFont(font_path)
        else:
            return []
            
        path = GalvoFontPath()
        
        cfont.render(path, text, True, font_size, 1.0, 1.1, align)
        path.new_path() # flush
        
        return path.polygons
