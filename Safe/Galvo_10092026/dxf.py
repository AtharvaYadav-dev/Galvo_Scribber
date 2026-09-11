import ezdxf
import math
from collections import defaultdict


class DXFParser():
    def __init__(self, filepath):
        self.filepath = filepath
        self.doc = ezdxf.readfile(filepath)
        self.msp = self.doc.modelspace()
    
        self.gcode_xmin = 0
        self.gcode_xmax = 0
        self.gcode_ymin = 0
        self.gcode_ymax = 0
        self.gcode_width = 0
        self.gcode_height = 0
        self.gcode_xcenter = 0
        self.gcode_ycenter = 0
        self.shift_x = 0
        self.shift_y = 0        
        self.bed_x0 = 0
        self.bed_y0 = 0
        self.bed_width = 0
        self.bed_height = 0
        
        self.scale = 1        
        self.scale_flag = True

        self.zpos = 0
        self.zpos_safe = 20
        self.feed = 1000

        self.xindex = 0
        self.yindex = 0
        
    def shiftX(self, x):
        return (x + self.shift_x + self.xindex) * self.scale if self.scale_flag else x
    
    def shiftY(self, y):
        return (y + self.shift_y + self.yindex) * self.scale if self.scale_flag else y

    def extractEntities(self):
        entities = defaultdict(list)
        for e in self.msp:
            layer = e.dxf.layer if e.dxf.hasattr('layer') else 'default'
            dxftype = e.dxftype()

            if dxftype == 'LINE':
                entities[layer].append(('LINE', (e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y)))

            if dxftype == 'CIRCLE':
                entities[layer].append(('CIRCLE', (e.dxf.center.x, e.dxf.center.y, e.dxf.radius)))

            if dxftype == 'ARC':
                entities[layer].append(('ARC', (e.dxf.center.x, e.dxf.center.y, e.dxf.radius, e.dxf.start_angle, e.dxf.end_angle)))

            if dxftype in ['LWPOLYLINE', 'POLYLINE']:
                points = [(v[0], v[1]) for v in e.get_points()] if dxftype == 'LWPOLYLINE' else [(v.dxf.x, v.dxf.y) for v in e.vertices()]
                entities[layer].append(('POLYLINE', points))

            if dxftype == 'SPLINE':
                spline_points = list(e.flattening(0.1))
                entities[layer].append(('SPLINE', [(p[0], p[1]) for p in spline_points]))

            if dxftype == 'ELLIPSE':
                ellipse_points = list(e.flattening(0.1))
                entities[layer].append(('ELLIPSE', [(p[0], p[1]) for p in ellipse_points]))

        return entities
    
    def computeBoundary(self, entities):
        all_points = []
        
        if entities:
            for items in entities.values():
                for etype, data in items:
                    if etype == 'LINE':
                        all_points.extend([(data[0], data[1]), (data[2], data[3])])
                    elif etype in ['POLYLINE', 'SPLINE', 'ELLIPSE']:
                        all_points.extend(data)
                    elif etype == 'CIRCLE':
                        cx, cy, r = data
                        all_points.extend([(cx - r, cy - r), (cx + r, cy + r)])
                    elif etype == 'ARC':
                        cx, cy, r, _, _ = data
                        all_points.extend([(cx - r, cy - r), (cx + r, cy + r)])
                        
            xcords = [pt[0] for pt in all_points]
            ycords = [pt[1] for pt in all_points]
            
            xmin, xmax = min(xcords), max(xcords)
            ymin, ymax = min(ycords), max(ycords)

            # shift negative coordinates to positive
            self.shift_x = -xmin if xmin < 0 else 0
            self.shift_y = -ymin if ymin < 0 else 0
            
            return xmin, xmax, ymin, ymax
        
        return 0, 0, 0, 0
    def getGcodeSize(self, xmin, xmax, ymin, ymax):
        self.gcode_xmin = xmin
        self.gcode_xmax = xmax
        self.gcode_ymin = ymin
        self.gcode_ymax = ymax
        self.gcode_width = self.gcode_xmax - self.gcode_xmin
        self.gcode_height = self.gcode_ymax - self.gcode_ymin
        self.gcode_xcenter = self.gcode_width / 2
        self.gcode_ycenter = self.gcode_height / 2
        
    def setBedCorners(self, p1, p2, p3, p4):
        """
        Define the bed using four corner points:
        p1: bottom-left (x,y)
        p2: bottom-right (x,y)
        p3: top-right (x,y)
        p4: top-left (x,y)
        """
        self.bed_x0 = min(p1[0], p4[0])
        self.bed_y0 = min(p1[1], p2[1])
        self.bed_width = abs(p2[0] - p1[0])
        self.bed_height = abs(p4[1] - p1[1])
    
    def validateFit(self):
        if self.bed_width and self.bed_height:
            xmin = self.gcode_xmin + self.xindex
            xmax = self.gcode_xmax + self.xindex
            ymin = self.gcode_ymin + self.yindex
            ymax = self.gcode_ymax + self.yindex
            
            bed_xmin = self.bed_x0
            bed_xmax = self.bed_x0 + self.bed_width
            bed_ymin = self.bed_y0
            bed_ymax = self.bed_y0 + self.bed_height
            
            xfit = xmin >= bed_xmin and xmax <= bed_xmax
            yfit = ymin >= bed_ymin and ymax <= bed_ymax
            fit = xfit and yfit
            
            return fit
        else:
            return False            

    def parse_to_polygons(self, field_size=100, resolution=0.1):
        """
        Parses the DXF and returns a list of polygons (paths).
        Each polygon is a list of (x, y) coordinates in mm, centered at (0,0).
        """
        entities = self.extractEntities()
        all_paths_mm = []
        
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for layer, items in entities.items():
            for etype, data in items:
                path_mm = []
                if etype == 'LINE':
                    path_mm = [(data[0], data[1]), (data[2], data[3])]
                elif etype in ['POLYLINE', 'SPLINE', 'ELLIPSE']:
                    path_mm = data
                elif etype == 'CIRCLE':
                    cx, cy, r = data
                    num_samples = max(12, int(2 * math.pi * r / resolution))
                    for i in range(num_samples + 1):
                        angle = 2 * math.pi * i / num_samples
                        path_mm.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                elif etype == 'ARC':
                    cx, cy, r, start_angle_deg, end_angle_deg = data
                    start_angle = math.radians(start_angle_deg)
                    end_angle = math.radians(end_angle_deg)
                    if end_angle <= start_angle:
                        end_angle += 2 * math.pi
                    arc_length = r * (end_angle - start_angle)
                    num_samples = max(2, int(arc_length / resolution))
                    for i in range(num_samples + 1):
                        angle = start_angle + (end_angle - start_angle) * i / num_samples
                        path_mm.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
                        
                if path_mm:
                    rounded_path = [(round(pt[0], 6), round(pt[1], 6)) for pt in path_mm]
                    for pt in rounded_path:
                        min_x = min(min_x, pt[0])
                        max_x = max(max_x, pt[0])
                        min_y = min(min_y, pt[1])
                        max_y = max(max_y, pt[1])
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
            print(f"Error merging DXF paths: {e}")
            
        width = max_x - min_x
        height = max_y - min_y
        center_x = min_x + width / 2.0
        center_y = min_y + height / 2.0
        
        # DXF files are natively modeled in real-world units (usually mm).
        # Do not force-scale to 80% of the field size, preserve 1:1 scale.
        scale_factor = 1.0
        
        for path in all_paths_mm:
            for i in range(len(path)):
                x, y = path[i]
                x = (x - center_x) * scale_factor
                y = (y - center_y) * scale_factor
                # DXF is typically Y+ Up natively, no need to flip Y like we do for SVG.
                path[i] = (x, y)
                
        return all_paths_mm

    def setZvalue(self, value):
        self.zpos = value

    def getZvalue(self):
        if self.zpos is None:
            self.zpos = float(self.zpos_safe)

    def setIndex(self, x=0, y=0):
        self.xindex = float(x)
        self.yindex = float(y)
        
    def setCenter(self):
        if self.bed_width and self.bed_height:
            bed_xcenter = (self.bed_x0 + self.bed_width) / 2
            bed_ycenter = (self.bed_y0 + self.bed_height) / 2
            xindex = bed_xcenter - self.gcode_xcenter
            yindex = bed_ycenter - self.gcode_ycenter
            
            self.setIndex(xindex, yindex)

    def setFeedRate(self, feedrate):
        self.feed = int(feedrate)
            
    def generateGcode(self, operation=None, position=None):
        entities = self.extractEntities()
        glist = []
        
        bounds = self.computeBoundary(entities)
        if bounds is None:
             return []
        
        xmin, xmax, ymin, ymax = bounds
        self.getGcodeSize(xmin, xmax, ymin, ymax)
        
        if self.validateFit():
            self.getZvalue()

            gcode = "G28"
            glist.append(gcode)
            gcode = "G90"
            glist.append(gcode)                

            if self.xindex > 0:
                gcode = f"G0 X{self.xindex} F{self.feed}"
                glist.append(gcode)

            if self.yindex > 0:
                gcode = f"G0 Y{self.yindex} F{self.feed}"
                glist.append(gcode)

            gcode = "M5"
            glist.append(gcode)

            for layer, item in entities.items():
                
                for etype, data in item:
                    
                    if etype == "LINE":
                        x0, y0 = self.shiftX(data[0]), self.shiftY(data[1])
                        x1, y1 = self.shiftX(data[2]), self.shiftY(data[3])

                        gcode = "M5"
                        glist.append(gcode)                        
                        gcode = f"G0 X{x0:.3f} Y{y0:.3f} Z{self.zpos:.3f} F{self.feed}"
                        glist.append(gcode)

                        gcode = "M3"
                        glist.append(gcode)                        
                        gcode = f"G1 X{x1:.3f} Y{y1:.3f} Z{self.zpos:.3f} F{self.feed}"
                        glist.append(gcode)
                    
                    elif etype == "CIRCLE":
                        cx, cy, r = data
                        x0, y0 = self.shiftX(cx + r), self.shiftY(cy)
                        i = -r
                        j = 0

                        gcode = "M5"
                        glist.append(gcode)                        
                        gcode = f"G0 X{x0:.3f} Y{y0:.3f} Z{self.zpos:.3f} F{self.feed}"
                        glist.append(gcode)

                        gcode = "M3"
                        glist.append(gcode)                        
                        gcode = f"G2 X{x0:.3f} Y{y0:.3f} I{i:.3f} J0.00 F{self.feed}"
                        glist.append(gcode)
                    
                    elif etype == "ARC":
                        cx, cy, r, a1, a2 = data
                        # a1, a2 = -a1, -a2
                        cx_s, cy_s = self.shiftX(cx), self.shiftY(cy)
                        x0 = self.shiftX(cx + r * math.cos(math.radians(a1)))
                        y0 = self.shiftY(cy + r * math.sin(math.radians(a1)))
                        x1 = self.shiftX(cx + r * math.cos(math.radians(a2)))
                        y1 = self.shiftY(cy + r * math.sin(math.radians(a2)))
                        i = cx_s - x0
                        j = cy_s - y0
                        
                        gcode = "M5"
                        glist.append(gcode)
                        gcode = f"G0 X{x0:.3f} Y{y0:.3f} Z{self.zpos:.3f} F{self.feed}"
                        glist.append(gcode)

                        gcode = "M3"
                        glist.append(gcode)                        
                        gcode = f"G3 X{x1:.3f} Y{y1:.3f} I{i:.3f} J{j:.3f} F{self.feed}"
                        glist.append(gcode)
                    
                    elif etype in ['POLYLINE', 'SPLINE', 'ELLIPSE']:
                        points = [(self.shiftX(x), self.shiftY(y)) for x, y in data]
                        
                        if points:
                            x0, y0 = points[0]
                            gcode = "M5"
                            glist.append(gcode)
                            gcode = f"G0 X{x0:.3f} Y{y0:.3f} Z{self.zpos:.3f} F{self.feed}"
                            glist.append(gcode)

                            gcode = "M3"
                            glist.append(gcode)
                            for x, y in points[1:]:
                                gcode = f"G1 X{x:.3f} Y{y:.3f} Z{self.zpos:.3f} F{self.feed}"
                                glist.append(gcode)

            glist.append("M5")
            glist.append("G28 X Y")                                
            return glist


if __name__ == "__main__":
    
    dxf_list = ["C:/Users/exp/Desktop/FTO_P1_scribing_5x5cm.dxf",
                "D:/Mario/Works/DXF/vectorsart_16345.dxf",
                "D:/Mario/Works/DXF/FTO_P1_scribing_5x5cm.dxf",
                "D:/Mario/Works/DXF/InterDigitElectrode-F_Cu.dxf",
                "D:/Mario/Works/DXF/Diamond.dxf"
                ]
    
    index = 0
    dxf = DXFParser(dxf_list[index])

    # ✅ Define corners of bed area
    P1 = (0, 30)
    P2 = (100, 30)
    P3 = (100, 100)
    P4 = (0, 100)
    dxf.setBedCorners(P1, P2, P3, P4)

    dxf.setIndex(10, 20)
    g = dxf.generateGcode()
    
    print("Generated G-code:")
    for line in g:
        print(line)
