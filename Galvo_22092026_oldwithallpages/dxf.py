import ezdxf
import math
from collections import defaultdict
from ezdxf.path import make_path
from ezdxf.addons import text2path
from ezdxf.math import bulge_to_arc


class DXFParser:
    """
    DXF -> G-code parser focused on precision laser/CNC scribing.

    Important geometry rules:
    - LWPOLYLINE/POLYLINE bulges are preserved exactly.
    - A closed polyline is NOT closed by adding a new point with bulge=0.
      The last vertex's bulge describes the last->first segment.
    - Path reversal correctly moves and negates bulges.
    - Closed paths can be rotated so machining starts at the nearest vertex.
    - LINE/ARC/CIRCLE remain true G-code geometry where possible.
    - SPLINE/ELLIPSE are flattened with a configurable geometric tolerance.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.doc = ezdxf.readfile(filepath)
        self.msp = self.doc.modelspace()

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

        # Geometry tolerances are intentionally separate.
        # Units are the same as the DXF (normally mm in your workflow).
        self.path_join_tolerance = 0.005
        self.point_duplicate_tolerance = 0.0001
        self.endpoint_tolerance = 0.001
        self.curve_flatten_tolerance = 0.005

        # Diagnostics
        self.debug = False
        self.debug_stats = {}

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def shiftX(self, x):
        value = x + self.shift_x + self.xindex
        return value * self.scale if self.scale_flag else value

    def shiftY(self, y):
        value = y + self.shift_y + self.yindex
        return value * self.scale if self.scale_flag else value

    def _scale_value(self, value):
        return value * self.scale if self.scale_flag else value

    # ------------------------------------------------------------------
    # Small geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _xy(point):
        return float(point[0]), float(point[1])

    @staticmethod
    def _distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def _same_point(a, b, tol):
        return math.hypot(a[0] - b[0], a[1] - b[1]) <= tol

    @staticmethod
    def _bulge(value):
        # Avoid -0.0 / tiny floating point noise becoming an arc.
        return 0.0 if abs(float(value)) < 1e-12 else float(value)

    def _remove_consecutive_duplicate_vertices(self, points):
        """
        Remove truly duplicate consecutive vertices, but never destroy a
        non-zero bulge attached to the segment.
        """
        if not points:
            return []

        out = [points[0]]
        for p in points[1:]:
            last = out[-1]
            if self._same_point(last, p, self.point_duplicate_tolerance):
                # If the duplicate carries a bulge, keep it because it
                # represents geometry for the outgoing segment.
                if len(p) >= 3 and abs(p[2]) > 1e-12:
                    out[-1] = (last[0], last[1], p[2])
            else:
                out.append(p)
        return out

    # ------------------------------------------------------------------
    # DXF extraction
    # ------------------------------------------------------------------

    def extractEntities(self):
        """
        Returns:
            defaultdict(list) keyed by layer.

        Entity tuples:
            ('LINE', (x0, y0, x1, y1))
            ('ARC', (cx, cy, r, start_angle, end_angle))
            ('CIRCLE', (cx, cy, r))
            ('POLYLINE', {
                'points': [(x, y, bulge), ...],
                'closed': bool
            })
        """
        entities = defaultdict(list)

        self.debug_stats = {
            "LINE": 0,
            "ARC": 0,
            "CIRCLE": 0,
            "LWPOLYLINE": 0,
            "POLYLINE": 0,
            "SPLINE": 0,
            "ELLIPSE": 0,
            "TEXT": 0,
            "MTEXT": 0,
            "INSERT": 0,
            "errors": 0,
        }

        def process_entity(e):
            try:
                layer = e.dxf.layer if e.dxf.hasattr("layer") else "default"
                dxftype = e.dxftype()

                if dxftype == "INSERT":
                    self.debug_stats["INSERT"] += 1
                    # virtual_entities() resolves block geometry.
                    for virtual_entity in e.virtual_entities():
                        process_entity(virtual_entity)
                    return

                if dxftype == "LINE":
                    self.debug_stats["LINE"] += 1
                    entities[layer].append(
                        ("LINE", (
                            float(e.dxf.start.x),
                            float(e.dxf.start.y),
                            float(e.dxf.end.x),
                            float(e.dxf.end.y),
                        ))
                    )
                    return

                if dxftype in ("LWPOLYLINE", "POLYLINE"):
                    self.debug_stats[dxftype] += 1

                    points = []
                    if dxftype == "LWPOLYLINE":
                        closed = bool(e.closed)
                        for p in e.get_points(format="xyb"):
                            x = float(p[0])
                            y = float(p[1])
                            b = self._bulge(p[2] if len(p) > 2 else 0.0)
                            points.append((x, y, b))
                    else:
                        closed = bool(e.is_closed)
                        for v in e.vertices:
                            x = float(v.dxf.location.x)
                            y = float(v.dxf.location.y)
                            b = (
                                float(v.dxf.bulge)
                                if v.dxf.hasattr("bulge")
                                else 0.0
                            )
                            points.append((x, y, self._bulge(b)))

                    points = self._remove_consecutive_duplicate_vertices(points)

                    # Many CAD exporters store a closed polyline with the first
                    # vertex repeated as the LAST vertex.  That repeated vertex
                    # is a representation of the endpoint, not an additional
                    # zero-length machining segment.
                    #
                    # Remove that duplicate so that the REAL last vertex keeps
                    # its bulge, which correctly describes:
                    #
                    #     last_real_vertex -> first_vertex
                    #
                    # This is especially important for small curved boxes.
                    if (
                        closed
                        and len(points) >= 3
                        and self._same_point(
                            (points[0][0], points[0][1]),
                            (points[-1][0], points[-1][1]),
                            self.point_duplicate_tolerance,
                        )
                    ):
                        points.pop()

                    # CRITICAL:
                    # Do NOT append first point here.
                    #
                    # For a closed bulged polyline, points[i].bulge describes
                    # the segment points[i] -> points[i+1].  The LAST real
                    # vertex's bulge describes LAST -> FIRST.
                    if len(points) >= 2:
                        entities[layer].append(
                            ("POLYLINE", {
                                "points": points,
                                "closed": closed,
                            })
                        )
                    return

                if dxftype in ("SPLINE", "ELLIPSE"):
                    self.debug_stats[dxftype] += 1
                    p = make_path(e)
                    for sub_path in p.sub_paths():
                        points = [
                            (float(v[0]), float(v[1]), 0.0)
                            for v in sub_path.flattening(
                                self.curve_flatten_tolerance
                            )
                        ]
                        points = self._remove_consecutive_duplicate_vertices(points)
                        if len(points) >= 2:
                            entities[layer].append(
                                ("POLYLINE", {
                                    "points": points,
                                    "closed": False,
                                })
                            )
                    return

                if dxftype in ("TEXT", "MTEXT"):
                    self.debug_stats[dxftype] += 1
                    paths = text2path.make_paths_from_entity(e)
                    for p in paths:
                        for sub_path in p.sub_paths():
                            points = [
                                (float(v[0]), float(v[1]), 0.0)
                                for v in sub_path.flattening(
                                    self.curve_flatten_tolerance
                                )
                            ]
                            points = self._remove_consecutive_duplicate_vertices(points)
                            if len(points) >= 2:
                                entities[layer].append(
                                    ("POLYLINE", {
                                        "points": points,
                                        "closed": False,
                                    })
                                )
                    return

                if dxftype == "ARC":
                    self.debug_stats["ARC"] += 1
                    entities[layer].append(
                        ("ARC", (
                            float(e.dxf.center.x),
                            float(e.dxf.center.y),
                            float(e.dxf.radius),
                            float(e.dxf.start_angle),
                            float(e.dxf.end_angle),
                        ))
                    )
                    return

                if dxftype == "CIRCLE":
                    self.debug_stats["CIRCLE"] += 1
                    entities[layer].append(
                        ("CIRCLE", (
                            float(e.dxf.center.x),
                            float(e.dxf.center.y),
                            float(e.dxf.radius),
                        ))
                    )
                    return

            except Exception as ex:
                self.debug_stats["errors"] += 1
                if self.debug:
                    print(f"[DXF] Failed to parse {e.dxftype()}: {ex}")

        for e in self.msp:
            process_entity(e)

        return entities

    # ------------------------------------------------------------------
    # Polyline/path helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _polyline_points(data):
        return data["points"]

    @staticmethod
    def _polyline_closed(data):
        return bool(data.get("closed", False))

    def _polyline_start_end(self, data):
        points = self._polyline_points(data)
        closed = self._polyline_closed(data)

        if not points:
            return None, None

        start = (points[0][0], points[0][1])
        if closed:
            end = start
        else:
            end = (points[-1][0], points[-1][1])
        return start, end

    def _rotate_closed_polyline(self, data, start_index):
        """
        Rotate a closed polyline without changing its geometry.

        Example:
            P0,P1,P2,P3
        rotated at P2:
            P2,P3,P0,P1

        Bulges remain attached to their ORIGINAL starting vertices.
        """
        points = list(data["points"])
        n = len(points)
        if n == 0:
            return data

        start_index %= n
        rotated = points[start_index:] + points[:start_index]

        return {
            "points": rotated,
            "closed": True,
        }

    def _reverse_polyline(self, data):
        """
        Correctly reverse a polyline.

        Original:
            P0 -(b0)-> P1 -(b1)-> P2 -(b2)-> ...

        Reversed:
            ... P2 -(-b1)-> P1 -(-b0)-> P0

        For a CLOSED path the final outgoing segment also wraps around,
        so its bulge is handled correctly.
        """
        points = list(data["points"])
        closed = bool(data.get("closed", False))
        n = len(points)

        if n < 2:
            return data

        old_bulges = [p[2] if len(p) >= 3 else 0.0 for p in points]
        reversed_points = []

        for i in range(n):
            old_index = n - 1 - i
            old_point = points[old_index]

            # New segment from reversed_points[i] to reversed_points[i+1]
            # is the reverse of old segment:
            # old_index-1 -> old_index
            source_bulge_index = (old_index - 1) % n

            if not closed and old_index == 0:
                new_bulge = 0.0
            else:
                new_bulge = -old_bulges[source_bulge_index]

            reversed_points.append(
                (old_point[0], old_point[1], self._bulge(new_bulge))
            )

        if not closed:
            reversed_points[-1] = (
                reversed_points[-1][0],
                reversed_points[-1][1],
                0.0,
            )

        return {
            "points": reversed_points,
            "closed": closed,
        }

    def _prepare_polyline_for_nearest_start(self, data, current):
        """
        For closed paths, choose the nearest vertex as the machining start.
        This reduces rapid travel and avoids starting tiny closed shapes from
        an arbitrary DXF vertex.
        """
        if not data.get("closed"):
            return data, False

        points = data["points"]
        if not points:
            return data, False

        best_index = min(
            range(len(points)),
            key=lambda i: self._distance(
                current,
                (points[i][0], points[i][1])
            )
        )

        rotated = self._rotate_closed_polyline(data, best_index)
        return rotated, False

    # ------------------------------------------------------------------
    # Boundary
    # ------------------------------------------------------------------

    def computeBoundary(self, entities):
        all_points = []

        for items in entities.values():
            for etype, data in items:
                if etype == "LINE":
                    all_points.extend([
                        (data[0], data[1]),
                        (data[2], data[3]),
                    ])

                elif etype == "POLYLINE":
                    for p in data["points"]:
                        all_points.append((p[0], p[1]))

                elif etype == "CIRCLE":
                    cx, cy, r = data
                    all_points.extend([
                        (cx - r, cy - r),
                        (cx + r, cy + r),
                    ])

                elif etype == "ARC":
                    cx, cy, r, a1, a2 = data

                    # Include endpoints plus cardinal points that lie on arc.
                    def add_angle(a):
                        ar = math.radians(a)
                        return (cx + r * math.cos(ar),
                                cy + r * math.sin(ar))

                    all_points.append(add_angle(a1))
                    all_points.append(add_angle(a2))

                    start = a1 % 360.0
                    end = a2 % 360.0
                    sweep = (a2 - a1) % 360.0
                    if sweep <= 0:
                        sweep += 360.0

                    for cardinal in (0.0, 90.0, 180.0, 270.0):
                        delta = (cardinal - start) % 360.0
                        if delta <= sweep + 1e-10:
                            all_points.append(add_angle(cardinal))

        if not all_points:
            return 0.0, 0.0, 0.0, 0.0

        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        if self.align_to_origin:
            self.shift_x = -xmin
            self.shift_y = -ymin
        else:
            self.shift_x = -xmin if xmin < 0 else 0
            self.shift_y = -ymin if ymin < 0 else 0

        return xmin, xmax, ymin, ymax

    def getGcodeSize(self, xmin, xmax, ymin, ymax):
        self.gcode_xmin = xmin
        self.gcode_xmax = xmax
        self.gcode_ymin = ymin
        self.gcode_ymax = ymax
        self.gcode_width = xmax - xmin
        self.gcode_height = ymax - ymin
        self.gcode_xcenter = self.gcode_width / 2.0
        self.gcode_ycenter = self.gcode_height / 2.0

    def setBedCorners(self, p1, p2, p3, p4):
        self.bed_x0 = min(p1[0], p4[0])
        self.bed_y0 = min(p1[1], p2[1])
        self.bed_width = abs(p2[0] - p1[0])
        self.bed_height = abs(p4[1] - p1[1])

    def validateFit(self):
        if not (self.bed_width and self.bed_height):
            return False

        xmin = self.shiftX(self.gcode_xmin)
        xmax = self.shiftX(self.gcode_xmax)
        ymin = self.shiftY(self.gcode_ymin)
        ymax = self.shiftY(self.gcode_ymax)

        bed_xmin = self.bed_x0
        bed_xmax = self.bed_x0 + self.bed_width
        bed_ymin = self.bed_y0
        bed_ymax = self.bed_y0 + self.bed_height

        return (
            xmin >= bed_xmin - self.endpoint_tolerance
            and xmax <= bed_xmax + self.endpoint_tolerance
            and ymin >= bed_ymin - self.endpoint_tolerance
            and ymax <= bed_ymax + self.endpoint_tolerance
        )

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------


    def parse_to_polygons(self, field_size=100, resolution=0.1, ignore_fit=True, align_center=True, laser_xoff=0, laser_yoff=0):
        """
        Parses the DXF and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates in mm.
        Applies identical coordinate transformations (shift/scale) and 
        nearest-neighbor layer optimization as generateGcode.
        """
        entities = self.extractEntities()
        if not entities:
            return []
            
        xmin, xmax, ymin, ymax = self.computeBoundary(entities)
        self.getGcodeSize(xmin, xmax, ymin, ymax)

        if align_center:
            # For Galvo, center the design at exactly (0,0) plus any laser offset
            self.shift_x = - (self.gcode_xmin + self.gcode_width / 2.0) + laser_xoff
            self.shift_y = - (self.gcode_ymin + self.gcode_height / 2.0) + laser_yoff

        if not self.validateFit() and not ignore_fit:
            if self.debug:
                print("[DXF] Design does not fit bed.")
            return []

        all_paths_mm = []
        
        for layer, item in entities.items():
            optimized_items = self._optimize_layer(item)
            
            for etype, data in optimized_items:
                path_mm = []
                
                if etype == 'LINE':
                    path_mm = [(self.shiftX(data[0]), self.shiftY(data[1])), 
                               (self.shiftX(data[2]), self.shiftY(data[3]))]
                               
                elif etype == 'CIRCLE':
                    cx = self.shiftX(data[0])
                    cy = self.shiftY(data[1])
                    r = self._scale_value(data[2])
                    num_samples = max(12, int(2 * math.pi * r / resolution))
                    for i in range(num_samples + 1):
                        angle = 2 * math.pi * i / num_samples
                        path_mm.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                        
                elif etype == 'ARC':
                    cx = self.shiftX(data[0])
                    cy = self.shiftY(data[1])
                    r = self._scale_value(data[2])
                    start_angle_deg, end_angle_deg = data[3], data[4]
                    start_angle = math.radians(start_angle_deg)
                    end_angle = math.radians(end_angle_deg)
                    if end_angle <= start_angle:
                        end_angle += 2 * math.pi
                    arc_length = r * (end_angle - start_angle)
                    num_samples = max(2, int(arc_length / resolution))
                    for i in range(num_samples + 1):
                        angle = start_angle + (end_angle - start_angle) * i / num_samples
                        path_mm.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                        
                elif etype == 'POLYLINE':
                    points = data["points"]
                    closed = data.get("closed", False)
                    if not points:
                        continue
                        
                    for i in range(len(points)):
                        x0 = self.shiftX(points[i][0])
                        y0 = self.shiftY(points[i][1])
                        bulge = points[i][2]
                        
                        if i == len(points) - 1:
                            if not closed:
                                path_mm.append((x0, y0))
                                break
                            else:
                                x1 = self.shiftX(points[0][0])
                                y1 = self.shiftY(points[0][1])
                        else:
                            x1 = self.shiftX(points[i+1][0])
                            y1 = self.shiftY(points[i+1][1])
                            
                        path_mm.append((x0, y0))
                        
                        if abs(bulge) > 1e-12:
                            try:
                                center, start_ang, end_ang, radius = bulge_to_arc((points[i][0], points[i][1]), (points[(i+1)%len(points)][0], points[(i+1)%len(points)][1]), bulge)
                                
                                # Shift and scale center and radius
                                cx = self.shiftX(center.x)
                                cy = self.shiftY(center.y)
                                radius = self._scale_value(radius)
                                
                                if bulge > 0:
                                    sweep = end_ang - start_ang
                                    if sweep < 0:
                                        sweep += 2 * math.pi
                                    true_start = start_ang
                                else:
                                    sweep = start_ang - end_ang
                                    if sweep > 0:
                                        sweep -= 2 * math.pi
                                    true_start = end_ang
                                    
                                arc_length = radius * abs(sweep)
                                num_samples = max(2, int(arc_length / resolution))
                                for j in range(1, num_samples):
                                    angle = true_start + sweep * j / num_samples
                                    path_mm.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
                            except Exception:
                                pass # straight line fallback
                                
                    if closed and len(points) > 0:
                        path_mm.append((self.shiftX(points[0][0]), self.shiftY(points[0][1])))

                if path_mm:
                    rounded_path = [(round(pt[0], 6), round(pt[1], 6)) for pt in path_mm]
                    all_paths_mm.append(rounded_path)
                    
        if not all_paths_mm:
            return []
            
        try:
            from shapely.geometry import LineString
            from shapely.ops import linemerge
            
            lines = []
            for path in all_paths_mm:
                if len(path) >= 2:
                    lines.append(LineString(path))
            
            if lines:
                merged = linemerge(lines)
                merged_paths = []
                if merged.geom_type == 'MultiLineString':
                    for line in merged.geoms:
                        merged_paths.append(list(line.coords))
                elif merged.geom_type == 'LineString':
                    merged_paths.append(list(merged.coords))
                
                # Update all_paths_mm with the merged continuous lines
                all_paths_mm = merged_paths
        except Exception as e:
            if self.debug:
                print(f"Error merging DXF paths: {e}")
                
        return all_paths_mm

    def setZvalue(self, value):
        self.zpos = float(value)

    def getZvalue(self):
        if self.zpos is None:
            self.zpos = float(self.zpos_safe)

    def setIndex(self, x=0, y=0):
        self.xindex = float(x)
        self.yindex = float(y)

    def setCenter(self, laser_xoff=0, laser_yoff=0):
        if self.bed_width and self.bed_height:
            bed_xcenter = self.bed_x0 + self.bed_width / 2.0
            bed_ycenter = self.bed_y0 + self.bed_height / 2.0

            current_xcenter = (
                self.gcode_xmin + self.gcode_width / 2.0 + self.shift_x
            )
            current_ycenter = (
                self.gcode_ymin + self.gcode_height / 2.0 + self.shift_y
            )

            self.setIndex(
                bed_xcenter - current_xcenter + laser_xoff,
                bed_ycenter - current_ycenter + laser_yoff,
            )

    def setFeedRate(self, feedrate):
        self.feed = int(feedrate)
        self.g0_feed = int(self.feed * 1.5)
        self.curve_feed = int(self.feed * 0.25)

    # ------------------------------------------------------------------
    # G-code helpers
    # ------------------------------------------------------------------

    def _laser_move_to(self, glist, x, y):
        glist.append("M400")
        glist.append("M5")
        glist.append("G4 P250")
        glist.append(
            f"G0 X{x:.6f} Y{y:.6f} Z{self.zpos:.6f} F{self.g0_feed}"
        )
        glist.append("M400")
        glist.append("M3")
        glist.append("G4 P250")

    def _append_line(self, glist, x, y):
        glist.append(
            f"G1 X{x:.6f} Y{y:.6f} Z{self.zpos:.6f} F{self.feed}"
        )

    def _append_bulge_segment(self, glist, x0, y0, x1, y1, bulge):
        """
        Convert one DXF bulge segment to a true G2/G3.

        IMPORTANT:
        bulge belongs to the segment STARTING at (x0,y0).
        """
        bulge = float(bulge)

        if abs(bulge) < 1e-12:
            self._append_line(glist, x1, y1)
            return

        if self._same_point((x0, y0), (x1, y1), self.point_duplicate_tolerance):
            # A non-zero-bulge zero-length segment is invalid geometry.
            # Do not emit a bogus arc.
            return

        try:
            center, start_ang, end_ang, radius = bulge_to_arc(
                (x0, y0),
                (x1, y1),
                bulge,
            )

            # bulge_to_arc is evaluated in MACHINE coordinates here, so I/J
            # already include scaling and coordinate translation correctly.
            i_off = center.x - x0
            j_off = center.y - y0

            direction = "G3" if bulge > 0 else "G2"

            glist.append(
                f"{direction} X{x1:.6f} Y{y1:.6f} "
                f"I{i_off:.6f} J{j_off:.6f} F{self.curve_feed}"
            )

        except Exception as ex:
            # Fallback should be extremely rare. A straight G1 is preferable
            # to emitting invalid G2/G3 that could stop a CNC controller.
            if self.debug:
                print(f"[GCODE] Bulge conversion failed: {ex}")
            self._append_line(glist, x1, y1)

    def _append_polyline(self, glist, data, last_position):
        points = data["points"]
        closed = bool(data.get("closed", False))

        if len(points) < 2:
            return last_position

        # Transform vertices ONCE into machine coordinates.
        machine_points = [
            (self.shiftX(p[0]), self.shiftY(p[1]), p[2])
            for p in points
        ]

        start = (machine_points[0][0], machine_points[0][1])

        if (
            last_position is None
            or self._distance(start, last_position) > self.path_join_tolerance
        ):
            self._laser_move_to(glist, start[0], start[1])
        else:
            # The physical machine position is already close enough to the
            # first vertex; explicitly use the actual first vertex for arc I/J
            # calculations rather than the previous path's rounded endpoint.
            pass

        n = len(machine_points)

        # Open polyline: P0->P1->...->Pn-1
        # Closed polyline: P0->P1->...->Pn-1->P0
        segment_count = n if closed else n - 1

        for i in range(segment_count):
            x0, y0, b = machine_points[i]

            if closed:
                x1, y1, _ = machine_points[(i + 1) % n]
            else:
                x1, y1, _ = machine_points[i + 1]

            # The endpoints of a DXF polyline are already the exact geometry.
            # Never "snap" them based on the previous machining path.
            if abs(b) < 1e-12:
                self._append_line(glist, x1, y1)
            else:
                self._append_bulge_segment(
                    glist, x0, y0, x1, y1, b
                )

        # A closed path ends EXACTLY at its first vertex.
        if closed:
            last_position = start
        else:
            last_position = (
                machine_points[-1][0],
                machine_points[-1][1],
            )

        return last_position

    def _append_circle(self, glist, data, last_position):
        cx, cy, r = data

        sx = self.shiftX(cx + r)
        sy = self.shiftY(cy)

        if (
            last_position is None
            or self._distance((sx, sy), last_position) > self.path_join_tolerance
        ):
            self._laser_move_to(glist, sx, sy)

        # Draw full circle at once
        rr = self._scale_value(r)
        i = -rr

        glist.append(
            f"G2 X{sx:.6f} Y{sy:.6f} "
            f"I{i:.6f} J0.000000 F{self.curve_feed}"
        )

        return (sx, sy)

    def _append_arc(self, glist, data, last_position):
        cx, cy, r, a1, a2 = data

        x0 = self.shiftX(cx + r * math.cos(math.radians(a1)))
        y0 = self.shiftY(cy + r * math.sin(math.radians(a1)))
        x1 = self.shiftX(cx + r * math.cos(math.radians(a2)))
        y1 = self.shiftY(cy + r * math.sin(math.radians(a2)))

        if (
            last_position is None
            or self._distance((x0, y0), last_position) > self.path_join_tolerance
        ):
            self._laser_move_to(glist, x0, y0)

        cx_s = self.shiftX(cx)
        cy_s = self.shiftY(cy)
        i_off = cx_s - x0
        j_off = cy_s - y0

        # DXF ARC is counter-clockwise in its native coordinate system.
        glist.append(
            f"G3 X{x1:.6f} Y{y1:.6f} "
            f"I{i_off:.6f} J{j_off:.6f} F{self.curve_feed}"
        )

        return (x1, y1)

    # ------------------------------------------------------------------
    # Path ordering
    # ------------------------------------------------------------------

    def _entity_start_end_candidates(self, entity):
        etype, data = entity

        if etype == "LINE":
            return (
                (data[0], data[1]),
                (data[2], data[3]),
                True,
            )

        if etype == "ARC":
            cx, cy, r, a1, a2 = data
            start = (
                cx + r * math.cos(math.radians(a1)),
                cy + r * math.sin(math.radians(a1)),
            )
            end = (
                cx + r * math.cos(math.radians(a2)),
                cy + r * math.sin(math.radians(a2)),
            )
            return start, end, False

        if etype == "CIRCLE":
            cx, cy, r = data
            start = (cx + r, cy)
            return start, start, False

        if etype == "POLYLINE":
            start, end = self._polyline_start_end(data)
            return start, end, True

        return None, None, False

    def _optimize_layer(self, items):
        """
        Nearest-endpoint ordering using scipy.spatial.cKDTree.
        """
        if not items:
            return []

        try:
            from scipy.spatial import cKDTree
        except ImportError:
            return self._optimize_layer_fallback(items)

        entities_dict = {i: entity for i, entity in enumerate(items)}
        
        pts = []
        pt_info = []

        for i, entity in entities_dict.items():
            etype, data = entity
            if etype == "POLYLINE" and data.get("closed"):
                points = data["points"]
                for v_idx, pt in enumerate(points):
                    pts.append((pt[0], pt[1]))
                    pt_info.append((i, False, v_idx))
            else:
                start, end, reversible = self._entity_start_end_candidates(entity)
                if start is not None:
                    pts.append(start)
                    pt_info.append((i, False, 0))
                if reversible and end is not None:
                    pts.append(end)
                    pt_info.append((i, True, 0))

        if not pts:
            return []

        tree = cKDTree(pts)
        
        optimized = []
        unvisited = set(entities_dict.keys())
        current = (0.0, 0.0)
        max_k = len(pts)

        while unvisited:
            best_idx = None
            best_entity = None
            
            k = 16
            found = False
            while not found:
                query_k = min(k, len(pts))
                dists, idxs = tree.query(current, k=query_k)
                if query_k == 1:
                    dists = [dists]
                    idxs = [idxs]
                
                for d, pt_idx in zip(dists, idxs):
                    if pt_idx == len(pts):
                        continue
                        
                    ent_id, is_rev, v_idx = pt_info[pt_idx]
                    if ent_id in unvisited:
                        found = True
                        best_idx = ent_id
                        
                        etype, data = entities_dict[ent_id]
                        if etype == "POLYLINE" and data.get("closed"):
                            candidate_data = self._rotate_closed_polyline(data, v_idx)
                            best_entity = ("POLYLINE", candidate_data)
                        else:
                            if is_rev:
                                if etype == "LINE":
                                    best_entity = ("LINE", (data[2], data[3], data[0], data[1]))
                                elif etype == "POLYLINE":
                                    best_entity = ("POLYLINE", self._reverse_polyline(data))
                                elif etype == "ARC":
                                    best_entity = ("ARC", (data[0], data[1], data[2], data[4], data[3]))
                                else:
                                    best_entity = entities_dict[ent_id]
                            else:
                                best_entity = entities_dict[ent_id]
                        break
                
                if found:
                    break
                
                k *= 4
                if k > 256:
                    active_indices = [i for i, info in enumerate(pt_info) if info[0] in unvisited]
                    if not active_indices:
                        break
                    pts = [pts[i] for i in active_indices]
                    pt_info = [pt_info[i] for i in active_indices]
                    tree = cKDTree(pts)
                    k = 1
                    
            if not found:
                best_idx = next(iter(unvisited))
                best_entity = entities_dict[best_idx]

            optimized.append(best_entity)
            unvisited.remove(best_idx)

            _, end_point, _ = self._entity_start_end_candidates(best_entity)
            if end_point is not None:
                current = end_point

        return optimized

    def _optimize_layer_fallback(self, items):
        """
        Nearest-endpoint ordering.

        Closed polylines are special: rotate them so the nearest vertex is
        first, rather than treating the arbitrary DXF first vertex as fixed.
        """
        unvisited = list(items)
        optimized = []
        current = (0.0, 0.0)

        while unvisited:
            best_idx = None
            best_distance = float("inf")
            best_entity = None

            for i, entity in enumerate(unvisited):
                etype, data = entity

                if etype == "POLYLINE" and data.get("closed"):
                    points = data["points"]
                    if not points:
                        continue

                    # Choose nearest vertex as the new start.
                    idx = min(
                        range(len(points)),
                        key=lambda k: self._distance(
                            current,
                            (points[k][0], points[k][1]),
                        ),
                    )
                    candidate_data = self._rotate_closed_polyline(data, idx)
                    candidate = ("POLYLINE", candidate_data)
                    candidate_start = (
                        candidate_data["points"][0][0],
                        candidate_data["points"][0][1],
                    )

                    d = self._distance(current, candidate_start)

                    if d < best_distance:
                        best_distance = d
                        best_idx = i
                        best_entity = candidate

                else:
                    start, end, reversible = self._entity_start_end_candidates(
                        entity
                    )
                    if start is None:
                        continue

                    d_start = self._distance(current, start)

                    if d_start < best_distance:
                        best_distance = d_start
                        best_idx = i
                        best_entity = entity

                    if reversible:
                        d_end = self._distance(current, end)
                        if d_end < best_distance:
                            etype2, data2 = entity

                            if etype2 == "LINE":
                                reversed_entity = (
                                    "LINE",
                                    (
                                        data2[2],
                                        data2[3],
                                        data2[0],
                                        data2[1],
                                    ),
                                )
                            elif etype2 == "POLYLINE":
                                reversed_entity = (
                                    "POLYLINE",
                                    self._reverse_polyline(data2),
                                )
                            else:
                                reversed_entity = entity

                            best_distance = d_end
                            best_idx = i
                            best_entity = reversed_entity

            if best_idx is None:
                # Defensive fallback.
                best_idx = 0
                best_entity = unvisited[0]

            unvisited.pop(best_idx)
            optimized.append(best_entity)

            start, end, _ = self._entity_start_end_candidates(best_entity)
            if start is not None:
                current = end

        return optimized

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def validateClosedPolylines(self, entities):
        """
        Check closed polyline topology BEFORE G-code generation.

        A valid closed polyline does not need its first point duplicated.
        The closing segment is represented by the last vertex's bulge.
        """
        report = {
            "closed_total": 0,
            "closed_with_bulge": 0,
            "closed_missing_bulge": 0,
            "zero_length_segments": 0,
        }

        for items in entities.values():
            for etype, data in items:
                if etype != "POLYLINE" or not data.get("closed"):
                    continue

                report["closed_total"] += 1
                points = data["points"]
                if not points:
                    continue

                last_bulge = points[-1][2] if len(points[-1]) >= 3 else 0.0
                if abs(last_bulge) > 1e-12:
                    report["closed_with_bulge"] += 1

                # A zero closing bulge is perfectly valid if the final segment
                # is supposed to be straight.
                if len(points) >= 2:
                    p0 = (points[0][0], points[0][1])
                    pn = (points[-1][0], points[-1][1])
                    if self._same_point(p0, pn, self.point_duplicate_tolerance):
                        report["zero_length_segments"] += 1

        return report

    def printDebugReport(self, entities=None):
        if entities is None:
            entities = self.extractEntities()

        print("\n========== DXF DEBUG REPORT ==========")
        print(f"File: {self.filepath}")
        for key, value in self.debug_stats.items():
            print(f"{key:24s}: {value}")

        report = self.validateClosedPolylines(entities)
        print("\nClosed polyline checks:")
        for key, value in report.items():
            print(f"{key:24s}: {value}")

        print("======================================\n")

    # ------------------------------------------------------------------
    # Main G-code generation
    # ------------------------------------------------------------------

    def generateGcode(
        self,
        operation=None,
        position=None,
        ignore_fit=False,
        align_center=False,
        laser_xoff=0,
        laser_yoff=0,
    ):
        entities = self.extractEntities()

        if self.debug:
            self.printDebugReport(entities)

        if not entities:
            return []

        xmin, xmax, ymin, ymax = self.computeBoundary(entities)
        self.getGcodeSize(xmin, xmax, ymin, ymax)

        if align_center:
            self.setCenter(laser_xoff, laser_yoff)

        if not self.validateFit() and not ignore_fit:
            if self.debug:
                print("[DXF] Design does not fit bed.")
            return []

        self.getZvalue()

        glist = [
            "G28",
            "G90",
            "M5",
        ]

        # IMPORTANT:
        # Do NOT separately issue G0 X{xindex}/Y{yindex}.
        #
        # shiftX()/shiftY() already include xindex/yindex. Doing both would
        # apply the index twice and can create an apparent geometry offset.
        #
        # This is especially important when align_center=True.

        for layer, item in entities.items():
            optimized_items = self._optimize_layer(item)

            last_x = None
            last_y = None
            last_position = None

            for etype, data in optimized_items:
                if etype == "LINE":
                    x0 = self.shiftX(data[0])
                    y0 = self.shiftY(data[1])
                    x1 = self.shiftX(data[2])
                    y1 = self.shiftY(data[3])

                    if (
                        last_position is None
                        or self._distance((x0, y0), last_position)
                        > self.path_join_tolerance
                    ):
                        self._laser_move_to(glist, x0, y0)

                    self._append_line(glist, x1, y1)
                    last_position = (x1, y1)

                elif etype == "ARC":
                    last_position = self._append_arc(
                        glist, data, last_position
                    )

                elif etype == "CIRCLE":
                    last_position = self._append_circle(
                        glist, data, last_position
                    )

                elif etype == "POLYLINE":
                    last_position = self._append_polyline(
                        glist, data, last_position
                    )

                last_x, last_y = (
                    last_position if last_position is not None else (None, None)
                )

            # Keep layer boundaries independent. The next layer gets its own
            # positioning decision.
            last_position = None
            last_x, last_y = None, None

        glist.append("M400")
        glist.append("M5")
        glist.append("G4 P250")
        glist.append("G28 X Y")
        return glist


if __name__ == "__main__":
    # Example:
    # python dxf.py
    #
    # Change this path to your DXF when testing.

    dxf_path = r"C:/Users/exp/Desktop/FSS ON  ITO.dxf"

    dxf = DXFParser(dxf_path)

    # Bed
    P1 = (0, 30)
    P2 = (100, 30)
    P3 = (100, 100)
    P4 = (0, 100)
    dxf.setBedCorners(P1, P2, P3, P4)

    # Use either manual index OR align_center=True.
    dxf.setIndex(10, 20)

    dxf.setFeedRate(1000)
    dxf.setZvalue(0)

    # Turn diagnostics on while validating the new parser.
    dxf.debug = True

    gcode = dxf.generateGcode(
        ignore_fit=True,
        align_center=False,
    )

    print(f"Generated G-code lines: {len(gcode)}")

    # Optional output file.
    output_path = r"C:/Users/exp/Desktop/FSS_ON_ITO_fixed.gcode"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(gcode))

    print(f"G-code written to: {output_path}")
