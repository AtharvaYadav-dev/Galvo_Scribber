import math
from core.coordinate_mapper import mm_to_galvo
from core.parsers.svgelements import SVG, Path, Shape

class SVGParser:
    def __init__(self, field_size=100):
        self.field_size = field_size

    def parse_to_points(self, filepath, resolution=0.1):
        """
        Parses the SVG and returns a list of paths using svgelements.
        Each path is a list of (x, y) coordinates in mm.
        Optimized to avoid generating millions of redundant points for straight lines.
        """
        try:
            svg = SVG.parse(filepath)
        except Exception as e:
            print(f"Error parsing SVG {filepath}: {e}")
            return []
            
        all_paths_mm = []
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        # 96 DPI pixels to mm
        scale_factor = 25.4 / 96.0

        for element in svg.elements():
            if not isinstance(element, Shape):
                continue
                
            # Filter out white background canvas rectangles (quiet zones / canvas cards)
            try:
                fill_str = str(getattr(element, 'fill', '') or '').lower().strip()
                stroke_str = str(getattr(element, 'stroke', '') or '').lower().strip()
                if fill_str in ("#ffffff", "white", "#fff", "rgb(255, 255, 255)") and (not stroke_str or stroke_str in ("none", "transparent")):
                    continue
            except Exception:
                pass
                
            path_obj = Path(element)
            if len(path_obj) == 0:
                continue
                
            current_subpath = []
            
            for seg in path_obj:
                seg_type = type(seg).__name__
                
                if seg_type == 'Move':
                    if len(current_subpath) >= 2:
                        all_paths_mm.append(current_subpath)
                    current_subpath = []
                    start = getattr(seg, 'end', None) or getattr(seg, 'start', None)
                    if start:
                        current_subpath.append((start.real, start.imag))
                        min_x, max_x = min(min_x, start.real), max(max_x, start.real)
                        min_y, max_y = min(min_y, start.imag), max(max_y, start.imag)
                    continue
                    
                if seg_type in ('Line', 'Close'):
                    start = getattr(seg, 'start', None)
                    end = getattr(seg, 'end', None)
                    if start and not current_subpath:
                        current_subpath.append((start.real, start.imag))
                        min_x, max_x = min(min_x, start.real), max(max_x, start.real)
                        min_y, max_y = min(min_y, start.imag), max(max_y, start.imag)
                    if end:
                        current_subpath.append((end.real, end.imag))
                        min_x, max_x = min(min_x, end.real), max(max_x, end.real)
                        min_y, max_y = min(min_y, end.imag), max(max_y, end.imag)
                else:
                    # Curved segment: CubicBezier, QuadraticBezier, Arc
                    try:
                        seg_len = seg.length()
                    except Exception:
                        seg_len = 0
                        
                    if seg_len <= 0:
                        continue
                        
                    len_mm = seg_len * scale_factor
                    # Sample based on millimeter curvature, capped at 48 points per curve
                    num_samples = min(48, max(4, int(len_mm / 0.25)))
                    for i in range(1, num_samples):
                        t = i / float(num_samples - 1)
                        pt = seg.point(t)
                        x, y = pt.real, pt.imag
                        min_x, max_x = min(min_x, x), max(max_x, x)
                        min_y, max_y = min(min_y, y), max(max_y, y)
                        current_subpath.append((x, y))
                        
            if len(current_subpath) >= 2:
                all_paths_mm.append(current_subpath)
            
        if not all_paths_mm:
            return []
            
        # Calculate bounding box and center
        width = max_x - min_x
        height = max_y - min_y
        center_x = min_x + width / 2.0
        center_y = min_y + height / 2.0
        
        # Apply transformation: Shift to center -> Scale -> Flip Y
        for path in all_paths_mm:
            for i in range(len(path)):
                x, y = path[i]
                x = (x - center_x) * scale_factor
                y = -(y - center_y) * scale_factor
                path[i] = (round(x, 4), round(y, 4))
                
        return all_paths_mm

    def parse_to_polygons(self, filepath, resolution=0.1):
        """
        Parses the SVG and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates in mm, centered at (0,0).
        """
        return self.parse_to_points(filepath, resolution)
