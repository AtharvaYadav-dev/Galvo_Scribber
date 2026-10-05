import math
import sys
import os

try:
    import shapely.geometry
    import shapely.geometry.base
    import shapely.ops
    HAS_SHAPELY = True
    
    # Monkey-patch buffer to drastically increase curve smoothness
    _original_buffer = shapely.geometry.base.BaseGeometry.buffer
    def _high_res_buffer(self, distance, quad_segs=16, **kwargs):
        # Prevent faceted circles by forcing a high quad_segs count (64 = 256 points per circle)
        if 'resolution' in kwargs:
            res = kwargs.pop('resolution')
            qs = max(64, res)
        else:
            qs = max(64, quad_segs)
        return _original_buffer(self, distance, quad_segs=qs, **kwargs)
    shapely.geometry.base.BaseGeometry.buffer = _high_res_buffer
except ImportError:
    HAS_SHAPELY = False

# Add gerbyx to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gerbyx-main', 'src'))
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser as GerbyxParser
from gerbyx.processor import GerberProcessor


class GerberParser:
    """
    Gerber -> G-code parser focused on precision laser/CNC scribing.
    Extracts primitives, performs isolation routing using Shapely, and converts to G-Code.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
            
        processor = GerberProcessor()
        parser = GerbyxParser(processor)
        tokens = tokenize_gerber(data)
        parser.parse(tokens)
        
        self.doc = processor

        self.gcode_xmin = 0.0
        self.gcode_xmax = 0.0
        self.gcode_ymin = 0.0
        self.gcode_ymax = 0.0
        self.gcode_width = 0.0
        self.gcode_height = 0.0
        self.gcode_xcenter = 0.0
        self.gcode_ycenter = 0.0

        self.shift_x = 0.0
        self.shift_y = 0.0
        self.bed_x0 = 0.0
        self.bed_y0 = 0.0
        self.bed_width = 0.0
        self.bed_height = 0.0

        self.scale = 1.0
        self.scale_flag = True

        self.zpos = 0.0
        self.zpos_safe = 20.0
        self.feed = 1000
        self.curve_feed = 250
        self.g0_feed = 1500

        self.xindex = 0.0
        self.yindex = 0.0
        self.align_to_origin = False
        
        self.path_join_tolerance = 0.005

        self.debug = False

    @staticmethod
    def _distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def shiftX(self, x):
        value = x + self.shift_x + self.xindex
        return value * self.scale if self.scale_flag else value

    def shiftY(self, y):
        value = y + self.shift_y + self.yindex
        return value * self.scale if self.scale_flag else value

    def setBedCorners(self, p1, p2, p3, p4):
        self.bed_x0 = min(p1[0], p4[0])
        self.bed_y0 = min(p1[1], p2[1])
        self.bed_width = abs(p2[0] - p1[0])
        self.bed_height = abs(p4[1] - p1[1])

    def setZvalue(self, z):
        self.zpos = float(z)

    def setFeedRate(self, feed):
        self.feed = float(feed)
        self.g0_feed = int(self.feed * 1.5)
        self.curve_feed = int(self.feed * 0.25)

    def setIndex(self, x, y):
        self.xindex = float(x)
        self.yindex = float(y)
        self.align_to_origin = True

    def computeBoundary(self, geometries):
        if not geometries:
            return 0, 0, 0, 0
        from shapely.ops import unary_union
        try:
            union = unary_union(geometries)
            minx, miny, maxx, maxy = union.bounds
            return minx, maxx, miny, maxy
        except Exception:
            return 0, 0, 0, 0

    def getGcodeSize(self, xmin, xmax, ymin, ymax):
        self.gcode_xmin = xmin * self.scale if self.scale_flag else xmin
        self.gcode_xmax = xmax * self.scale if self.scale_flag else xmax
        self.gcode_ymin = ymin * self.scale if self.scale_flag else ymin
        self.gcode_ymax = ymax * self.scale if self.scale_flag else ymax

        self.gcode_width = self.gcode_xmax - self.gcode_xmin
        self.gcode_height = self.gcode_ymax - self.gcode_ymin
        self.gcode_xcenter = self.gcode_xmin + (self.gcode_width / 2.0)
        self.gcode_ycenter = self.gcode_ymin + (self.gcode_height / 2.0)

    def validateFit(self):
        final_x_start = self.shiftX(self.gcode_xmin)
        final_y_start = self.shiftY(self.gcode_ymin)
        
        if final_x_start < self.bed_x0 or final_y_start < self.bed_y0:
            return False
        
        if (final_x_start + self.gcode_width > self.bed_x0 + self.bed_width) or \
           (final_y_start + self.gcode_height > self.bed_y0 + self.bed_height):
            return False
            
        return True

    def setCenter(self, laser_xoff, laser_yoff):
        bed_xcenter = self.bed_x0 + self.bed_width / 2.0
        bed_ycenter = self.bed_y0 + self.bed_height / 2.0
        
        self.shift_x = bed_xcenter - self.gcode_xcenter + laser_xoff
        self.shift_y = bed_ycenter - self.gcode_ycenter + laser_yoff
        
        self.getGcodeSize(
            self.gcode_xmin + self.shift_x, 
            self.gcode_xmax + self.shift_x, 
            self.gcode_ymin + self.shift_y, 
            self.gcode_ymax + self.shift_y
        )

    def _laser_move_to(self, glist, x, y):
        glist.append("M400")
        glist.append("M5")
        glist.append("G4 P250")
        glist.append(f"G0 X{x:.6f} Y{y:.6f} Z{self.zpos:.6f} F{self.g0_feed:.0f}")
        glist.append("M400")
        glist.append("M3")
        glist.append("G4 P250")
        glist.append(f"G1 F{self.feed:.0f}")

    def _append_line(self, glist, x, y):
        glist.append(f"G1 X{x:.6f} Y{y:.6f}")

    def _append_arc(self, glist, x, y, i, j, cw):
        cmd = "G2" if cw else "G3"
        glist.append(f"{cmd} X{x:.6f} Y{y:.6f} I{i:.6f} J{j:.6f}")

    def _process_polyline(self, pts, tolerance=0.02):
        segments = []
        if not pts:
            return segments
            
        is_closed = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6
        
        import numpy as np
        
        def fit_circle_kasa(pts_arr):
            x = pts_arr[:, 0]
            y = pts_arr[:, 1]
            A = np.c_[x, y, np.ones(len(x))]
            B = -(x**2 + y**2)
            try:
                res, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
                a, b, c = res
                cx = -a / 2
                cy = -b / 2
                r = np.sqrt(max(0, a**2 + b**2 - 4*c)) / 2
                return cx, cy, r
            except Exception:
                return None

        def adjust_center(cx, cy, p1, p2):
            """Project center onto perpendicular bisector of p1-p2 to guarantee exact equal radii for GRBL"""
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            sq_dist = dx*dx + dy*dy
            if sq_dist < 1e-8:
                return cx, cy
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            nx = -dy
            ny = dx
            t = ((cx - mx) * nx + (cy - my) * ny) / sq_dist
            return mx + t * nx, my + t * ny

        # 1. Check if the ENTIRE polyline is a perfect full circle
        if is_closed and len(pts) >= 12:
            pts_arr = np.array(pts[:-1]) 
            circle = fit_circle_kasa(pts_arr)
            if circle:
                cx, cy, r = circle
                dists = np.hypot(pts_arr[:, 0] - cx, pts_arr[:, 1] - cy)
                max_error = np.max(np.abs(dists - r))
                
                if r <= 500 and max_error <= tolerance:
                    # It is a perfect full circle!
                    area = 0.0
                    for k in range(len(pts_arr)):
                        p1 = pts_arr[k]
                        p2 = pts_arr[(k+1) % len(pts_arr)]
                        area += (p2[0] - p1[0]) * (p2[1] + p1[1])
                    cw = area > 0
                    
                    # Split into two EXACTLY 180-degree arcs for maximum firmware/visualizer compatibility.
                    # Some simple G-code visualizers have severe bugs when Start == End (360 degree arcs).
                    start_pt = tuple(pts[0])
                    
                    # Exact diametrically opposite point:
                    mid_pt = (2 * cx - start_pt[0], 2 * cy - start_pt[1])
                    
                    cx1, cy1 = adjust_center(cx, cy, start_pt, mid_pt)
                    segments.append(('arc', start_pt, mid_pt, cx1 - start_pt[0], cy1 - start_pt[1], cw))
                    
                    cx2, cy2 = adjust_center(cx, cy, mid_pt, start_pt)
                    segments.append(('arc', mid_pt, start_pt, cx2 - mid_pt[0], cy2 - mid_pt[1], cw))
                    return segments
                
        # 2. Process everything else (traces, keyholes) 
        # Output ONLY straight lines (G1) as requested. No partial arcs!
        for i in range(len(pts)-1):
            segments.append(('line', tuple(pts[i]), tuple(pts[i+1])))
                
        return segments

    def _rotate_closed_polyline(self, pts, start_idx):
        if not pts:
            return pts
        return pts[start_idx:] + pts[:start_idx]

    def _optimize_polylines(self, polylines):
        """
        Optimizes a list of polylines (lists of (x,y) tuples).
        """
        if not polylines:
            return []

        try:
            from scipy.spatial import cKDTree
        except ImportError:
            # Fallback O(N^2) optimization
            unvisited = list(polylines)
            optimized = []
            current = (0.0, 0.0)

            while unvisited:
                best_idx = None
                best_distance = float("inf")
                best_pts = None

                for i, pts in enumerate(unvisited):
                    if not pts: continue
                    is_closed = (math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6)
                    
                    if is_closed:
                        for v_idx, pt in enumerate(pts[:-1]):
                            d = self._distance(current, pt)
                            if d < best_distance:
                                best_distance = d
                                best_idx = i
                                best_pts = self._rotate_closed_polyline(pts[:-1], v_idx)
                                best_pts.append(best_pts[0]) # re-close
                    else:
                        d_start = self._distance(current, pts[0])
                        if d_start < best_distance:
                            best_distance = d_start
                            best_idx = i
                            best_pts = pts

                        d_end = self._distance(current, pts[-1])
                        if d_end < best_distance:
                            best_distance = d_end
                            best_idx = i
                            best_pts = pts[::-1]

                if best_idx is None:
                    best_idx = 0
                    best_pts = unvisited[0]

                unvisited.pop(best_idx)
                optimized.append(best_pts)
                if best_pts:
                    current = best_pts[-1]
                
            return optimized

        # KDTree Optimization
        pts_list = []
        pt_info = []

        for i, pts in enumerate(polylines):
            if not pts: continue
            is_closed = (math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6)
            if is_closed:
                for v_idx, pt in enumerate(pts[:-1]):
                    pts_list.append(pt)
                    pt_info.append((i, False, v_idx))
            else:
                pts_list.append(pts[0])
                pt_info.append((i, False, 0))
                pts_list.append(pts[-1])
                pt_info.append((i, True, 0))

        if not pts_list:
            return []

        tree = cKDTree(pts_list)
        
        optimized = []
        unvisited = set(range(len(polylines)))
        current = (0.0, 0.0)
        max_k = len(pts_list)

        while unvisited:
            best_idx = None
            best_pts = None
            
            k = 16
            found = False
            while not found:
                dists, idxs = tree.query(current, k=k)
                if k == 1:
                    dists = [dists]
                    idxs = [idxs]
                
                for d, pt_idx in zip(dists, idxs):
                    if pt_idx == len(pts_list):
                        continue
                        
                    ent_id, is_rev, v_idx = pt_info[pt_idx]
                    if ent_id in unvisited:
                        found = True
                        best_idx = ent_id
                        
                        pts = polylines[ent_id]
                        is_closed = (math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6)
                        
                        if is_closed:
                            best_pts = self._rotate_closed_polyline(pts[:-1], v_idx)
                            best_pts.append(best_pts[0])
                        else:
                            best_pts = pts[::-1] if is_rev else pts
                        break
                
                if found:
                    break
                
                if k >= max_k:
                    break
                
                k = min(max_k, k * 4)
                    
            if not found:
                best_idx = next(iter(unvisited))
                best_pts = polylines[best_idx]

            optimized.append(best_pts)
            unvisited.remove(best_idx)

            if best_pts:
                current = best_pts[-1]

        return optimized

    def _extract_polylines_from_geometries(self, geometries):
        """Converts shapely polygons/lines to polylines for g-code generation"""
        if not HAS_SHAPELY:
            return []
            
        polylines = []
        
        def extract_bounds(geom):
            if isinstance(geom, shapely.geometry.Polygon):
                polylines.append(list(geom.exterior.coords))
                for interior in geom.interiors:
                    polylines.append(list(interior.coords))
            elif hasattr(geom, 'geoms'): # MultiPolygon, GeometryCollection, MultiLineString
                for subgeom in geom.geoms:
                    extract_bounds(subgeom)
            elif isinstance(geom, shapely.geometry.LineString):
                polylines.append(list(geom.coords))
                    
        try:
            # Fix topology issues (near-collinear points, self-intersections) before unioning
            from shapely.validation import make_valid
            clean_geoms = []
            for geom in geometries:
                try:
                    clean = make_valid(geom)
                    if not clean.is_empty:
                        clean_geoms.append(clean)
                except:
                    clean_geoms.append(geom.buffer(0))
            
            union_geom = shapely.ops.unary_union(clean_geoms)
            extract_bounds(union_geom)
        except Exception as e:
            if getattr(self, 'debug', False): print(f"[Gerber] Shapely union failed: {e}")
            for geom in geometries:
                extract_bounds(geom)
                
        return polylines

    def generateGcode(
        self,
        ignore_fit=False,
        align_center=False,
        laser_xoff=0,
        laser_yoff=0,
    ):
        geometries = getattr(self.doc, 'geometries', [])

        if not geometries:
            return []

        xmin, xmax, ymin, ymax = self.computeBoundary(geometries)
        self.getGcodeSize(xmin, xmax, ymin, ymax)

        if align_center:
            self.setCenter(laser_xoff, laser_yoff)
        else:
            self.shift_x = -self.gcode_xmin
            self.shift_y = -self.gcode_ymin

        if not self.validateFit() and not ignore_fit:
            if self.debug:
                print("[Gerber] Design does not fit bed.")
            return []

        glist = [
            "G28",
            "G90",
            "M5",
        ]

        last_position = None
        join_tolerance = self.path_join_tolerance

        polylines = self._extract_polylines_from_geometries(geometries)
            
        optimized_polylines = self._optimize_polylines(polylines)

        for pts in optimized_polylines:
            if not pts: continue
            
            x0 = self.shiftX(pts[0][0])
            y0 = self.shiftY(pts[0][1])

            if last_position is None or math.hypot(x0 - last_position[0], y0 - last_position[1]) > join_tolerance:
                self._laser_move_to(glist, x0, y0)
            
            segments = self._process_polyline(pts, tolerance=self.path_join_tolerance)
            for seg in segments:
                if seg[0] == 'line':
                    x_next = self.shiftX(seg[2][0])
                    y_next = self.shiftY(seg[2][1])
                    self._append_line(glist, x_next, y_next)
                elif seg[0] == 'arc':
                    _, start_pt, end_pt, I_raw, J_raw, cw = seg
                    x_next = self.shiftX(end_pt[0])
                    y_next = self.shiftY(end_pt[1])
                    I = I_raw * self.scale if self.scale_flag else I_raw
                    J = J_raw * self.scale if self.scale_flag else J_raw
                    self._append_arc(glist, x_next, y_next, I, J, cw)
                
            last_position = (self.shiftX(pts[-1][0]), self.shiftY(pts[-1][1]))

        glist.append("M400")
        glist.append("M5")
        glist.append("G4 P250")
        glist.append("G28 X Y")
        
        return glist

    def parse_to_polygons(self, field_size=100, resolution=0.1, ignore_fit=True, align_center=True, laser_xoff=0, laser_yoff=0):
        """
        Parses the Gerber and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates.
        """
        geometries = getattr(self.doc, 'geometries', [])
        if not geometries:
            return []
            
        xmin, xmax, ymin, ymax = self.computeBoundary(geometries)
        self.getGcodeSize(xmin, xmax, ymin, ymax)

        if align_center:
            # For Galvo, center the design at exactly (0,0) plus any laser offset
            self.shift_x = - (self.gcode_xmin + self.gcode_width / 2.0) + laser_xoff
            self.shift_y = - (self.gcode_ymin + self.gcode_height / 2.0) + laser_yoff
        else:
            self.shift_x = -self.gcode_xmin
            self.shift_y = -self.gcode_ymin

        if not self.validateFit() and not ignore_fit:
            if self.debug:
                print("[Gerber] Design does not fit bed.")
            return []

        polylines = self._extract_polylines_from_geometries(geometries)
        optimized_polylines = self._optimize_polylines(polylines)

        all_paths_mm = []
        for pts in optimized_polylines:
            if not pts: continue
            
            path_mm = []
            for pt in pts:
                path_mm.append((round(self.shiftX(pt[0]), 6), round(self.shiftY(pt[1]), 6)))
                
            if path_mm:
                all_paths_mm.append(path_mm)
                
        if not all_paths_mm:
            return []
            
        try:
            # Fast contiguous path merge
            merged_paths = []
            current_path = []
            
            for path in all_paths_mm:
                if not path:
                    continue
                    
                if not current_path:
                    current_path = list(path)
                else:
                    if abs(current_path[-1][0] - path[0][0]) < 1e-4 and abs(current_path[-1][1] - path[0][1]) < 1e-4:
                        current_path.extend(path[1:])
                    else:
                        merged_paths.append(current_path)
                        current_path = list(path)
                        
            if current_path:
                merged_paths.append(current_path)
            
            all_paths_mm = merged_paths
        except Exception as e:
            if self.debug:
                print(f"Error merging Gerber paths: {e}")
                
        return all_paths_mm

