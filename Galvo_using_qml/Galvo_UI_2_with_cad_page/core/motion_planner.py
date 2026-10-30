def trim_line_segment(line_points, trim_start=0.0, trim_end=0.0):
    """Helper to trim a hatch line segment at both ends before drawing."""
    if not line_points or len(line_points) < 2:
        return None
    if trim_start <= 0 and trim_end <= 0:
        return line_points

    import math
    p1 = line_points[0]
    p2 = line_points[-1]

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)

    if length <= (trim_start + trim_end):
        return None  # Trimmed away completely

    ux = dx / length
    uy = dy / length

    new_start = (p1[0] + ux * max(0.0, trim_start), p1[1] + uy * max(0.0, trim_start))
    new_end = (p2[0] - ux * max(0.0, trim_end), p2[1] - uy * max(0.0, trim_end))
    return [new_start, new_end]


def compute_hatch_geometry(polygons, cfg, galvo_units_per_mm=1.0) -> list:
    """
    Computes vector hatch lines, inward loops, and contours for a single hatch configuration.
    polygons: List of polygons, each is a list of (x, y) tuples.
    cfg: Dictionary with EzCAD hatch configuration keys.
    galvo_units_per_mm: Scale factor (1.0 for direct mm coordinates in CAD).
    Returns: List of polylines, where each polyline is a list of (x, y) coordinates.
    """
    if not polygons or not cfg:
        return []

    from core.fill.fill.fills import eulerian_fill, scanline_fill, spiral_fill
    try:
        from shapely.geometry import Polygon, LineString, Point
        from shapely.ops import unary_union
    except ImportError:
        print("Shapely is required for advanced hatching (Offsets, Loops).")
        return []

    import math
    import traceback

    # Convert raw loop coordinates to valid Shapely Polygons
    raw_polys = []
    for poly in polygons:
        if len(poly) >= 3:
            try:
                poly_obj = Polygon(poly)
                if not poly_obj.is_valid:
                    poly_obj = poly_obj.buffer(0)
                if not poly_obj.is_empty:
                    if poly_obj.geom_type == 'MultiPolygon':
                        raw_polys.extend(list(poly_obj.geoms))
                    elif poly_obj.geom_type == 'Polygon':
                        raw_polys.append(poly_obj)
            except Exception:
                pass

    if not raw_polys:
        return []

    # Determine nesting depth for each polygon (even = solid shell / island, odd = hole)
    n = len(raw_polys)
    depths = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j:
                try:
                    if raw_polys[j].covers(raw_polys[i]):
                        depths[i] += 1
                except Exception:
                    pass

    shells = [(i, raw_polys[i]) for i in range(n) if depths[i] % 2 == 0]
    holes = [(i, raw_polys[i]) for i in range(n) if depths[i] % 2 == 1]

    shapely_polys = []
    for s_idx, s_poly in shells:
        s_depth = depths[s_idx]
        direct_holes = []
        for h_idx, h_poly in holes:
            if depths[h_idx] == s_depth + 1:
                try:
                    if s_poly.covers(h_poly):
                        direct_holes.append(h_poly.exterior.coords)
                except Exception:
                    pass
        try:
            poly_with_holes = Polygon(shell=s_poly.exterior.coords, holes=direct_holes)
            if not poly_with_holes.is_valid:
                poly_with_holes = poly_with_holes.buffer(0)
            if not poly_with_holes.is_empty:
                if poly_with_holes.geom_type == 'MultiPolygon':
                    shapely_polys.extend(list(poly_with_holes.geoms))
                else:
                    shapely_polys.append(poly_with_holes)
        except Exception:
            shapely_polys.append(s_poly)

    if cfg.get('all_calc', False):
        try:
            union_poly = unary_union(shapely_polys)
            if union_poly.geom_type == 'MultiPolygon':
                shapely_polys = list(union_poly.geoms)
            elif union_poly.geom_type == 'Polygon':
                shapely_polys = [union_poly]
        except Exception as e:
            print(f"All calc union failed: {e}")

    # Edge Offset (Shrinking is negative buffer)
    edge_offset_mm = float(cfg.get('edge_offset', 0.0) or 0.0)
    edge_offset_gu = edge_offset_mm * galvo_units_per_mm

    working_polys = []
    for p in shapely_polys:
        if edge_offset_gu != 0:
            buffered = p.buffer(-edge_offset_gu)
            if buffered.is_empty:
                continue
            if buffered.geom_type == 'MultiPolygon':
                working_polys.extend(list(buffered.geoms))
            else:
                working_polys.append(buffered)
        else:
            working_polys.append(p)

    if not working_polys:
        return []

    result_segments = []

    # NumLoops & Loop distance
    num_loops = int(cfg.get('num_loops', 0) or 0)
    loop_distance_gu = float(cfg.get('loop_distance', 0.05) or 0.05) * galvo_units_per_mm
    if num_loops > 0 and loop_distance_gu > 0:
        for i in range(num_loops):
            for wp in working_polys:
                ring = wp.buffer(-loop_distance_gu * (i + 1))
                if ring.is_empty:
                    continue
                rings_to_add = list(ring.geoms) if ring.geom_type == 'MultiPolygon' else [ring]
                for r in rings_to_add:
                    result_segments.append(list(r.exterior.coords))
                    for interior in r.interiors:
                        result_segments.append(list(interior.coords))

    hatch_style = cfg.get('type', "Bidirectional")
    if "Ring" in hatch_style:
        fill_alg = spiral_fill
        unidirectional = False
    elif "Bow" in hatch_style or "Optimized" in hatch_style:
        fill_alg = eulerian_fill
        unidirectional = False
    elif "Uni" in hatch_style:
        fill_alg = scanline_fill
        unidirectional = True
    else:
        fill_alg = scanline_fill
        unidirectional = False

    angles = [float(cfg.get('angle', 0.0) or 0.0)]
    if cfg.get('cross_hatch', False):
        angles.append(angles[0] + 90.0)

    count = int(cfg.get('count', 1) or 1)
    auto_rotate = bool(cfg.get('auto_rotate', False))
    rotate_angle = float(cfg.get('rotate_angle', 10.0) or 10.0)

    start_offset_gu = float(cfg.get('start_offset', 0.0) or 0.0) * galvo_units_per_mm
    end_offset_gu = float(cfg.get('end_offset', 0.0) or 0.0) * galvo_units_per_mm
    line_reduction_gu = float(cfg.get('line_reduction', 0.0) or 0.0) * galvo_units_per_mm

    trim_start = line_reduction_gu - start_offset_gu
    trim_end = line_reduction_gu - end_offset_gu
    base_line_space = float(cfg.get('line_space', 0.05) or 0.05)

    for c in range(count):
        for a in angles:
            current_angle = a + (c * rotate_angle if auto_rotate else 0)

            # Average distribute line calculation if requested
            eff_line_space = base_line_space
            if cfg.get('avg_dist', False) or cfg.get('avg_distribute', False):
                try:
                    rad = math.radians(current_angle)
                    nx, ny = -math.sin(rad), math.cos(rad)
                    all_projs = []
                    for wp in working_polys:
                        for pt in wp.exterior.coords:
                            all_projs.append(pt[0] * nx + pt[1] * ny)
                    if all_projs:
                        span = (max(all_projs) - min(all_projs)) / galvo_units_per_mm
                        n_divs = max(1, round(span / max(0.001, base_line_space)))
                        eff_line_space = span / n_divs
                except Exception:
                    eff_line_space = base_line_space

            settings = {
                "hatch_distance": str(eff_line_space * galvo_units_per_mm),
                "hatch_angle": f"{current_angle}deg"
            }

            complex_polys = []
            for wp in working_polys:
                for coord in wp.exterior.coords:
                    complex_polys.append(complex(coord[0], coord[1]))
                complex_polys.append(None)
                for interior in wp.interiors:
                    for coord in interior.coords:
                        complex_polys.append(complex(coord[0], coord[1]))
                    complex_polys.append(None)

            try:
                points = fill_alg(settings, complex_polys, None)
                if not points:
                    continue

                current_line = []
                all_lines = []
                for pt in points:
                    if pt is None:
                        if current_line:
                            all_lines.append(current_line)
                            current_line = []
                    else:
                        if isinstance(pt, complex):
                            current_line.append((pt.real, pt.imag))
                        else:
                            current_line.append((pt[0], pt[1]))
                if current_line:
                    all_lines.append(current_line)

                # If unidirectional is True, enforce lines point in consistent general direction
                if unidirectional:
                    rad = math.radians(current_angle)
                    ux = math.cos(rad)
                    uy = math.sin(rad)
                    for idx, line in enumerate(all_lines):
                        if len(line) >= 2:
                            dx = line[-1][0] - line[0][0]
                            dy = line[-1][1] - line[0][1]
                            dot = dx * ux + dy * uy
                            if dot < 0:
                                all_lines[idx] = list(reversed(line))

                for line in all_lines:
                    trimmed = trim_line_segment(line, trim_start, trim_end)
                    if trimmed:
                        result_segments.append(trimmed)

            except Exception as e:
                print(f"Hatch fill failed: {e}")
                traceback.print_exc()

    # Follow edge once
    if cfg.get('follow_edge', False):
        for wp in working_polys:
            result_segments.append(list(wp.exterior.coords))
            for interior in wp.interiors:
                result_segments.append(list(interior.coords))

    return result_segments


class MotionPlanner:
    def __init__(self):
        self.preview_queue = []
        self.send_queue = []
        
    def clear(self):
        self.preview_queue.clear()
        self.send_queue.clear()

    def add_jump(self, x, y, speed=None):
        cmd = {'type': 'jump', 'x': x, 'y': y, 'speed': speed}
        self.preview_queue.append(cmd)
        
    def add_mark(self, x, y, speed=None):
        cmd = {'type': 'mark', 'x': x, 'y': y, 'speed': speed}
        self.preview_queue.append(cmd)
        
    def add_laser_on(self):
        self.preview_queue.append({'type': 'laser_on'})
        
    def add_laser_off(self):
        self.preview_queue.append({'type': 'laser_off'})

    def add_delay(self, ms):
        self.preview_queue.append({'type': 'delay', 'ms': ms})

    def generate_hatch(self, polygons, hatch_configs, mark_speed=None, jump_speed=None, galvo_units_per_mm=1.0):
        """
        Generates scanline hatching for multiple configurations.
        polygons: List of polygons, each is a list of (x, y) tuples.
        hatch_configs: List of dicts representing Hatch 1, 2, 3 settings.
        """
        if not polygons or not hatch_configs: return

        try:
            from PySide6.QtCore import QCoreApplication
        except ImportError:
            QCoreApplication = None

        for cfg in hatch_configs:
            if QCoreApplication: QCoreApplication.processEvents()

            if not cfg.get('enable', False):
                continue

            hatch_idx = cfg.get('hatch_idx', 1)
            self.preview_queue.append({'type': 'pass_change', 'idx': hatch_idx})

            segments = compute_hatch_geometry(polygons, cfg, galvo_units_per_mm=galvo_units_per_mm)
            for seg in segments:
                if len(seg) >= 2:
                    self.add_jump(int(round(seg[0][0])), int(round(seg[0][1])), speed=jump_speed)
                    for pt in seg[1:]:
                        self.add_mark(int(round(pt[0])), int(round(pt[1])), speed=mark_speed)

    def _draw_trimmed_line(self, line_points, trim_start, trim_end, mark_speed, jump_speed):
        """Helper to trim a hatch line segment at both ends before drawing (backward compatibility)."""
        trimmed = trim_line_segment(line_points, trim_start, trim_end)
        if trimmed and len(trimmed) >= 2:
            self.add_jump(int(round(trimmed[0][0])), int(round(trimmed[0][1])), speed=jump_speed)
            for pt in trimmed[1:]:
                self.add_mark(int(round(pt[0])), int(round(pt[1])), speed=mark_speed)

    def commit_to_send_queue(self):
        """Moves optimized/verified preview commands to the send queue."""
        self.send_queue = list(self.preview_queue)
        
    def optimize_path(self):
        """
        Optimizes the path using Nearest Neighbor followed by 2-opt (TSP)
        to minimize jump distances between mark segments.
        """
        if not self.preview_queue:
            return
            
        # Group segments by continuous marks (paths)
        paths = []
        current_path = []
        
        for cmd in self.preview_queue:
            if cmd['type'] == 'jump':
                if current_path:
                    paths.append(current_path)
                    current_path = []
                current_path.append(cmd)
            elif cmd['type'] in ('mark', 'laser_on', 'laser_off'):
                current_path.append(cmd)
            else:
                if current_path:
                    paths.append(current_path)
                    current_path = []
                paths.append([cmd]) # keep delays isolated
                
        if current_path:
            paths.append(current_path)
            
        motion_paths = []
        static_paths = []
        for p in paths:
            if any(cmd['type'] in ('jump', 'mark') for cmd in p):
                motion_paths.append(p)
            else:
                static_paths.append(p)
        
        if len(motion_paths) < 2:
            return # nothing to optimize
            
        # Bypass O(N^2) path optimization for extremely large files
        if len(motion_paths) > 5000:
            return
            
        import math
        def dist(p1, p2):
            return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])
            
        def get_start_end(path):
            start = next((cmd for cmd in path if cmd['type'] in ('jump', 'mark')), None)
            end = next((cmd for cmd in reversed(path) if cmd['type'] in ('jump', 'mark')), None)
            return start, end

        # Cache start/end points to prevent O(N^2) function call overhead
        path_endpoints = {}
        for i, p in enumerate(motion_paths):
            path_endpoints[id(p)] = get_start_end(p)

        # 1. Greedy Nearest Neighbor
        optimized = [motion_paths.pop(0)]
        
        try:
            from PySide6.QtCore import QCoreApplication
        except ImportError:
            QCoreApplication = None
            
        loop_counter = 0
        while motion_paths:
            loop_counter += 1
            if loop_counter % 50 == 0 and QCoreApplication:
                QCoreApplication.processEvents()
                
            _, last_end = path_endpoints[id(optimized[-1])]
            if not last_end:
                optimized.append(motion_paths.pop(0))
                continue
                
            best_idx = 0
            best_dist = float('inf')
            
            for i, p in enumerate(motion_paths):
                start, _ = path_endpoints[id(p)]
                if not start: continue
                d = dist(last_end, start)
                if d < best_dist:
                    best_dist = d
                    best_idx = i
            optimized.append(motion_paths.pop(best_idx))
            
        # 2. Basic 2-opt refinement (only if small enough to prevent UI freeze)
        if len(optimized) < 500:
            improved = True
            while improved:
                improved = False
                for i in range(1, len(optimized) - 2):
                    for j in range(i + 1, len(optimized) - 1):
                        _, end_i1 = path_endpoints[id(optimized[i-1])]
                        start_i, end_i = path_endpoints[id(optimized[i])]
                        start_j, end_j = path_endpoints[id(optimized[j])]
                        start_j1, _ = path_endpoints[id(optimized[j+1])]
                        
                        if not all([end_i1, start_i, end_i, start_j, end_j, start_j1]):
                            continue
                            
                        current_dist = dist(end_i1, start_i) + dist(end_j, start_j1)
                        new_dist = dist(end_i1, start_j) + dist(end_i, start_j1)
                        
                        if new_dist < current_dist:
                            optimized[i:j+1] = reversed(optimized[i:j+1])
                            improved = True
                            break
                    if improved:
                        break
                    
        # Reconstruct queue
        self.preview_queue = []
        for p in optimized + static_paths:
            self.preview_queue.extend(p)

    def estimate_time(self):
        """Estimates total marking time based on queue."""
        total_time = 0.0
        # Very rough estimation based on distance / speed
        return total_time
