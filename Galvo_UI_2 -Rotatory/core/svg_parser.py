import math
import os
import io
from core.coordinate_mapper import mm_to_galvo
from core.parsers.svgelements import (
    SVG, Path, Shape, Move, Line, Close, CubicBezier, QuadraticBezier, Arc
)

class SVGParser:
    def __init__(self, field_size=100):
        self.field_size = field_size

    def parse_to_points(self, filepath, resolution=0.1):
        """
        Parses the SVG and returns a list of paths using svgelements.
        Each path is a list of (x, y) coordinates in physical millimeters, centered at (0, 0).
        - Segments are discretized cleanly and adaptively without over-sampling straight lines.
        - Move commands cleanly separate contours into independent subpaths.
        - Redundant collinear and micro-jitter points (<0.01mm) are decimated.
        """
        if not filepath or not os.path.isfile(filepath):
            print(f"SVGParser: File not found: {filepath}")
            return []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            svg = SVG.parse(io.StringIO(content))
        except Exception as e:
            print(f"Error parsing SVG {filepath}: {e}")
            return []

        scale_factor = 25.4 / 96.0  # 1 SVG User Unit (96 DPI pixel) = 25.4 / 96 mm
        all_paths_raw = []

        try:
            elements = list(svg.elements())
        except Exception as e:
            print(f"Error reading SVG elements from {filepath}: {e}")
            return []

        for element in elements:
            if not isinstance(element, Shape):
                continue

            try:
                path_obj = Path(element)
            except Exception:
                continue

            if len(path_obj) == 0:
                continue

            current_subpath = []

            for seg in path_obj:
                if isinstance(seg, Move):
                    if len(current_subpath) >= 2:
                        all_paths_raw.append(current_subpath)
                    current_subpath = [(seg.end.real, seg.end.imag)]
                elif isinstance(seg, Line):
                    if not current_subpath:
                        current_subpath.append((seg.start.real, seg.start.imag))
                    current_subpath.append((seg.end.real, seg.end.imag))
                elif isinstance(seg, Close):
                    if current_subpath:
                        if (seg.end.real, seg.end.imag) != current_subpath[-1]:
                            current_subpath.append((seg.end.real, seg.end.imag))
                        if len(current_subpath) >= 2:
                            all_paths_raw.append(current_subpath)
                        current_subpath = []
                else:
                    # Curved segment: CubicBezier, QuadraticBezier, Arc, etc.
                    try:
                        seg_len = seg.length()
                    except Exception:
                        seg_len = 0.0

                    if seg_len <= 1e-6:
                        continue

                    seg_len_mm = seg_len * scale_factor
                    # Adaptive sampling based on mm length: clamp between 4 and 64 samples
                    step = max(0.05, float(resolution))
                    num_samples = max(4, min(64, int(math.ceil(seg_len_mm / step))))

                    if not current_subpath:
                        current_subpath.append((seg.start.real, seg.start.imag))
                    for i in range(1, num_samples):
                        t = i / (num_samples - 1)
                        pt = seg.point(t)
                        current_subpath.append((pt.real, pt.imag))

            if len(current_subpath) >= 2:
                all_paths_raw.append(current_subpath)

        if not all_paths_raw:
            return []

        # Find bounding box across all raw paths
        min_x = min(min(pt[0] for pt in p) for p in all_paths_raw)
        max_x = max(max(pt[0] for pt in p) for p in all_paths_raw)
        min_y = min(min(pt[1] for pt in p) for p in all_paths_raw)
        max_y = max(max(pt[1] for pt in p) for p in all_paths_raw)

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        final_paths = []
        min_dist_sq = (0.01) ** 2  # 0.01 mm minimum segment threshold

        for path in all_paths_raw:
            new_path = []
            for x, y in path:
                # Center, convert to physical millimeters, flip Y (+Y up for Galvo / CAD)
                nx = (x - center_x) * scale_factor
                ny = -(y - center_y) * scale_factor

                if not new_path:
                    new_path.append((nx, ny))
                else:
                    px, py = new_path[-1]
                    d_sq = (nx - px) ** 2 + (ny - py) ** 2
                    if d_sq >= min_dist_sq:
                        new_path.append((nx, ny))

            if len(new_path) >= 2:
                final_paths.append(new_path)

        return final_paths

    def parse_to_polygons(self, filepath, resolution=0.1):
        """
        Parses the SVG and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates in mm, centered at (0,0).
        """
        return self.parse_to_points(filepath, resolution)
