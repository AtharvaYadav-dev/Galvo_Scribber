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
        
        from core.fill.fill.fills import eulerian_fill, scanline_fill, spiral_fill
        try:
            from shapely.geometry import Polygon, LineString, Point
            from shapely.ops import unary_union
        except ImportError:
            print("Shapely is required for advanced hatching (Offsets, Loops).")
            return
            
        import math
        import traceback
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
                
            shapely_polys = []
            for poly in polygons:
                if len(poly) >= 3:
                    p = Polygon(poly)
                    if p.is_valid:
                        shapely_polys.append(p)
            
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
            edge_offset_mm = cfg.get('edge_offset', 0.0)
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
                continue

            # NumLoops & Loop distance
            num_loops = cfg.get('num_loops', 0)
            loop_distance_gu = cfg.get('loop_distance', 0.05) * galvo_units_per_mm
            if num_loops > 0 and loop_distance_gu > 0:
                for i in range(num_loops):
                    loop_polys = []
                    for wp in working_polys:
                        ring = wp.buffer(-loop_distance_gu * (i + 1))
                        if ring.is_empty:
                            continue
                        if ring.geom_type == 'MultiPolygon':
                            loop_polys.extend(list(ring.geoms))
                        elif ring.geom_type == 'Polygon':
                            loop_polys.append(ring)
                            
                    for ring in loop_polys:
                        coords = list(ring.exterior.coords)
                        self.add_jump(int(coords[0][0]), int(coords[0][1]), speed=jump_speed)
                        for pt in coords[1:]:
                            self.add_mark(int(pt[0]), int(pt[1]), speed=mark_speed)
                        for interior in ring.interiors:
                            int_coords = list(interior.coords)
                            self.add_jump(int(int_coords[0][0]), int(int_coords[0][1]), speed=jump_speed)
                            for pt in int_coords[1:]:
                                self.add_mark(int(pt[0]), int(pt[1]), speed=mark_speed)
                                    
            hatch_style = cfg.get('type', "Bidirectional")
            if hatch_style == "Ring-like":
                fill_alg = spiral_fill
                unidirectional = False
            elif hatch_style == "Optimized / Bow-tie":
                fill_alg = eulerian_fill
                unidirectional = False
            elif hatch_style == "Unidirectional":
                fill_alg = scanline_fill
                unidirectional = True
            else:
                fill_alg = scanline_fill
                unidirectional = False
                
            angles = [cfg.get('angle', 0.0)]
            if cfg.get('cross_hatch', False):
                angles.append(angles[0] + 90.0)
                
            count = cfg.get('count', 1)
            auto_rotate = cfg.get('auto_rotate', False)
            rotate_angle = cfg.get('rotate_angle', 10.0)
            
            start_offset_gu = cfg.get('start_offset', 0.0) * galvo_units_per_mm
            end_offset_gu = cfg.get('end_offset', 0.0) * galvo_units_per_mm
            line_reduction_gu = cfg.get('line_reduction', 0.0) * galvo_units_per_mm
            
            trim_start = line_reduction_gu - start_offset_gu
            trim_end = line_reduction_gu - end_offset_gu
            
            for c in range(count):
                for a in angles:
                    if QCoreApplication: QCoreApplication.processEvents()
                    current_angle = a + (c * rotate_angle if auto_rotate else 0)
                    
                    settings = {
                        "hatch_distance": str(cfg.get('line_space', 0.1) * galvo_units_per_mm),
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
                        if not points: continue
                        
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
                            self._draw_trimmed_line(line, trim_start, trim_end, mark_speed, jump_speed)
                            
                    except Exception as e:
                        print(f"Hatch failed: {e}")
                        traceback.print_exc()

            # Follow edge once
            if cfg.get('follow_edge', False):
                for wp in working_polys:
                    coords = list(wp.exterior.coords)
                    self.add_jump(int(coords[0][0]), int(coords[0][1]), speed=jump_speed)
                    for pt in coords[1:]:
                        self.add_mark(int(pt[0]), int(pt[1]), speed=mark_speed)
                    for interior in wp.interiors:
                        int_coords = list(interior.coords)
                        self.add_jump(int(int_coords[0][0]), int(int_coords[0][1]), speed=jump_speed)
                        for pt in int_coords[1:]:
                            self.add_mark(int(pt[0]), int(pt[1]), speed=mark_speed)

    def _draw_trimmed_line(self, line_points, trim_start, trim_end, mark_speed, jump_speed):
        """Helper to trim a hatch line segment at both ends before drawing."""
        if len(line_points) < 2:
            return
            
        import math
        if trim_start <= 0 and trim_end <= 0:
            self.add_jump(int(line_points[0][0]), int(line_points[0][1]), speed=jump_speed)
            for pt in line_points[1:]:
                self.add_mark(int(pt[0]), int(pt[1]), speed=mark_speed)
            return

        p1 = line_points[0]
        p2 = line_points[-1]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        
        if length <= (trim_start + trim_end):
            return # Trimmed away completely
            
        ux = dx / length
        uy = dy / length
        
        new_start = (p1[0] + ux * max(0, trim_start), p1[1] + uy * max(0, trim_start))
        new_end = (p2[0] - ux * max(0, trim_end), p2[1] - uy * max(0, trim_end))
        
        self.add_jump(int(new_start[0]), int(new_start[1]), speed=jump_speed)
        self.add_mark(int(new_end[0]), int(new_end[1]), speed=mark_speed)

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
            
        # Filter out non-motion paths for TSP
        motion_paths = [p for p in paths if any(cmd['type'] in ('jump', 'mark') for cmd in p)]
        static_paths = [p for p in paths if p not in motion_paths]
        
        if len(motion_paths) < 2:
            return # nothing to optimize
            
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
