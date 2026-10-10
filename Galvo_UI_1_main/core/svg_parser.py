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
        Resolution defines the distance between sampled points.
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

        for element in svg.elements():
            if not isinstance(element, Shape):
                continue
                
            # Convert to Path to standardize
            path_obj = Path(element)
            if len(path_obj) == 0:
                continue
                
            # Discretize path into points
            path_mm = []
            
            # svgelements points are complex numbers (real=x, imag=y)
            for seg in path_obj:
                try:
                    seg_len = seg.length()
                except:
                    continue
                    
                if seg_len <= 0:
                    continue
                    
                num_samples = max(2, int(seg_len / resolution))
                for i in range(num_samples):
                    t = i / (num_samples - 1)
                    pt = seg.point(t)
                    x, y = pt.real, pt.imag
                    
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    
                    path_mm.append((x, y))
                    
            if path_mm:
                all_paths_mm.append(path_mm)
            
        if not all_paths_mm:
            return []
            
        # Calculate bounding box and center
        width = max_x - min_x
        height = max_y - min_y
        center_x = min_x + width / 2.0
        center_y = min_y + height / 2.0
        
        # Convert from SVG User Units (usually 96 DPI pixels) to mm
        # 1 inch = 25.4 mm. 96 pixels = 1 inch. -> 1 pixel = 25.4 / 96.0 mm
        scale_factor = 25.4 / 96.0
        
        # Apply transformation: Shift to center -> Scale -> Flip Y
        for path in all_paths_mm:
            for i in range(len(path)):
                x, y = path[i]
                # Center it
                x = x - center_x
                y = y - center_y
                # Scale it
                x = x * scale_factor
                y = y * scale_factor
                # Flip Y (SVG has +Y down, physical usually has +Y up)
                y = -y
                path[i] = (x, y)
                
        return all_paths_mm

    def parse_to_polygons(self, filepath, resolution=0.1):
        """
        Parses the SVG and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates in mm, centered at (0,0).
        """
        return self.parse_to_points(filepath, resolution)
