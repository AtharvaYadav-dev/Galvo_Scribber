import os
import math
import time
import numpy as np
import ezdxf
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union

class Coin3DReliefEngraver:
    """
    Production-grade 3D Laser Relief Engraver for the 27mm 10-Rupee Bi-Metallic Coin on Brass.
    Calibrated strictly for:
      - 27.0 mm outer diameter, centered at (0.0, 0.0) mm.
      - 1.0 mm brass material (0.50 mm max depth relief budget).
      - Step-relief hierarchy with descending pass counts (Layers 00-05).
      - 0.025 mm (25 um) hatch line pitch.
      - Dynamic auto-rotating hatch angles (+15 deg/pass) to prevent grooving.
      - Interleaved high-frequency brass soot-cleaning passes.
    """
    def __init__(self, dxf_path=None, field_size=100.0, offset_x_mm=0.0, offset_y_mm=0.0, power_scale=1.0, speed_scale=1.0, bidirectional=True):
        self.field_size = float(field_size)
        self.galvo_units_per_mm = 65535.0 / self.field_size
        self.center_bits = 32767.5
        self.offset_x_mm = float(offset_x_mm)
        self.offset_y_mm = float(offset_y_mm)
        self.power_scale = float(power_scale)
        self.speed_scale = float(speed_scale)
        self.bidirectional = bool(bidirectional)
        
        if dxf_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.dxf_path = os.path.join(base_dir, "DeepEngrave", "rupee_10_relief_27mm_master.dxf")
        else:
            self.dxf_path = dxf_path

        # Layer recipe tailored for 1.0mm brass coin
        self.layer_recipes = [
            {
                "layer_id": "LAYER_00_BASE_FIELD",
                "name": "Base Floor & Rim Wall",
                "depth_target_mm": 0.50,
                "passes": 20,
                "power_pct": 80.0,
                "freq_khz": 30.0,
                "mark_speed_mms": 500.0,
                "jump_speed_mms": 1500.0,
                "hatch_pitch_mm": 0.025,
                "rot_angle_deg": 15.0,
                "mode": "ablate",
            },
            {
                "layer_id": "LAYER_01_BIMETALLIC_TRENCH",
                "name": "Bi-Metallic Separator Channel",
                "depth_target_mm": 0.40,
                "passes": 15,
                "power_pct": 78.0,
                "freq_khz": 30.0,
                "mark_speed_mms": 500.0,
                "jump_speed_mms": 1500.0,
                "hatch_pitch_mm": 0.025,
                "rot_angle_deg": 15.0,
                "mode": "ablate",
            },
            {
                "layer_id": "LAYER_02_RELIEF_STEP_1",
                "name": "Lower Bevel & Wheat Stems",
                "depth_target_mm": 0.30,
                "passes": 10,
                "power_pct": 75.0,
                "freq_khz": 32.0,
                "mark_speed_mms": 520.0,
                "jump_speed_mms": 1500.0,
                "hatch_pitch_mm": 0.025,
                "rot_angle_deg": 15.0,
                "mode": "ablate",
            },
            {
                "layer_id": "LAYER_03_RELIEF_STEP_2",
                "name": "Mid Relief & Rupee Symbol",
                "depth_target_mm": 0.20,
                "passes": 6,
                "power_pct": 72.0,
                "freq_khz": 35.0,
                "mark_speed_mms": 550.0,
                "jump_speed_mms": 1500.0,
                "hatch_pitch_mm": 0.025,
                "rot_angle_deg": 15.0,
                "mode": "ablate",
            },
            {
                "layer_id": "LAYER_04_HIGH_RELIEF",
                "name": "High Relief Face, 2019 & Text",
                "depth_target_mm": 0.10,
                "passes": 3,
                "power_pct": 65.0,
                "freq_khz": 40.0,
                "mark_speed_mms": 600.0,
                "jump_speed_mms": 1500.0,
                "hatch_pitch_mm": 0.025,
                "rot_angle_deg": 15.0,
                "mode": "ablate",
            },
            {
                "layer_id": "LAYER_05_CREST_SURFACE",
                "name": "Crest Surface & Frosted Polish",
                "depth_target_mm": 0.00,
                "passes": 1,
                "power_pct": 16.0,
                "freq_khz": 80.0,
                "mark_speed_mms": 1200.0,
                "jump_speed_mms": 2000.0,
                "hatch_pitch_mm": 0.035,
                "rot_angle_deg": 45.0,
                "mode": "polish",
            },
        ]
        
        self.raw_entities = {}
        self.polygons_by_layer = {}

    def mm_to_galvo(self, x_mm, y_mm):
        """Converts millimeter coordinate (relative to center) to 16-bit unsigned Galvo bits."""
        gx = self.center_bits + ((x_mm + self.offset_x_mm) * self.galvo_units_per_mm)
        gy = self.center_bits + ((y_mm + self.offset_y_mm) * self.galvo_units_per_mm)
        return int(round(np.clip(gx, 0, 65535))), int(round(np.clip(gy, 0, 65535)))

    def load_dxf_layers(self):
        """Loads and parses the master DXF into closed Shapely polygons centered around (0, 0)."""
        if not os.path.exists(self.dxf_path):
            raise FileNotFoundError(f"Master DXF not found: {self.dxf_path}")
            
        print(f"[Coin3D] Ingesting DXF: {self.dxf_path}")
        doc = ezdxf.readfile(self.dxf_path)
        msp = doc.modelspace()
        
        self.raw_entities = {recipe["layer_id"]: [] for recipe in self.layer_recipes}
        
        # Center in DXF is (13.500, 13.500) mm
        origin_x = 13.500
        origin_y = 13.500
        
        for entity in msp:
            layer = entity.dxf.layer
            if layer not in self.raw_entities:
                continue
                
            dxftype = entity.dxftype()
            if dxftype == 'CIRCLE':
                cx = entity.dxf.center.x - origin_x
                cy = entity.dxf.center.y - origin_y
                r = entity.dxf.radius
                # Discretize circle into 72 segments (~5 deg resolution)
                pts = []
                for a in range(72):
                    ang = a * 2.0 * math.pi / 72.0
                    pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
                pts.append(pts[0])
                self.raw_entities[layer].append(pts)
                
            elif dxftype in ('LWPOLYLINE', 'POLYLINE'):
                pts = []
                for v in entity.vertices():
                    x = v.dxf.location.x if dxftype == 'POLYLINE' else v[0]
                    y = v.dxf.location.y if dxftype == 'POLYLINE' else v[1]
                    pts.append((x - origin_x, y - origin_y))
                if len(pts) >= 2:
                    if entity.is_closed or math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.05:
                        if pts[0] != pts[-1]:
                            pts.append(pts[0])
                    self.raw_entities[layer].append(pts)
                    
            elif dxftype == 'LINE':
                p1 = (entity.dxf.start.x - origin_x, entity.dxf.start.y - origin_y)
                p2 = (entity.dxf.end.x - origin_x, entity.dxf.end.y - origin_y)
                self.raw_entities[layer].append([p1, p2])

        # Fallback if no specific coin recipe layers were found
        has_recipe_entities = any(len(v) > 0 for v in self.raw_entities.values())
        if not has_recipe_entities:
            print("[Coin3D] No recipe layers found in DXF. Collecting all entities into default base relief layer.")
            all_x, all_y = [], []
            for entity in msp:
                dxftype = entity.dxftype()
                if dxftype == 'CIRCLE':
                    all_x.append(entity.dxf.center.x)
                    all_y.append(entity.dxf.center.y)
                elif dxftype in ('LWPOLYLINE', 'POLYLINE'):
                    for v in entity.vertices():
                        all_x.append(v.dxf.location.x if dxftype == 'POLYLINE' else v[0])
                        all_y.append(v.dxf.location.y if dxftype == 'POLYLINE' else v[1])
                elif dxftype == 'LINE':
                    all_x.extend([entity.dxf.start.x, entity.dxf.end.x])
                    all_y.extend([entity.dxf.start.y, entity.dxf.end.y])
            
            if all_x and all_y:
                origin_x = (min(all_x) + max(all_x)) / 2.0
                origin_y = (min(all_y) + max(all_y)) / 2.0
                
            for entity in msp:
                dxftype = entity.dxftype()
                if dxftype == 'CIRCLE':
                    cx = entity.dxf.center.x - origin_x
                    cy = entity.dxf.center.y - origin_y
                    r = entity.dxf.radius
                    pts = [(cx + r * math.cos(a * 2.0 * math.pi / 72.0), cy + r * math.sin(a * 2.0 * math.pi / 72.0)) for a in range(72)]
                    pts.append(pts[0])
                    self.raw_entities["LAYER_00_BASE_FIELD"].append(pts)
                elif dxftype in ('LWPOLYLINE', 'POLYLINE'):
                    pts = []
                    for v in entity.vertices():
                        x = v.dxf.location.x if dxftype == 'POLYLINE' else v[0]
                        y = v.dxf.location.y if dxftype == 'POLYLINE' else v[1]
                        pts.append((x - origin_x, y - origin_y))
                    if len(pts) >= 2:
                        if entity.is_closed or math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.05:
                            if pts[0] != pts[-1]:
                                pts.append(pts[0])
                        self.raw_entities["LAYER_00_BASE_FIELD"].append(pts)
                elif dxftype == 'LINE':
                    p1 = (entity.dxf.start.x - origin_x, entity.dxf.start.y - origin_y)
                    p2 = (entity.dxf.end.x - origin_x, entity.dxf.end.y - origin_y)
                    self.raw_entities["LAYER_00_BASE_FIELD"].append([p1, p2])

        # Convert to valid Shapely Polygons
        self.polygons_by_layer = {}
        for layer_id, poly_list in self.raw_entities.items():
            valid_polys = []
            for pts in poly_list:
                if len(pts) >= 4 and pts[0] == pts[-1]:
                    try:
                        p = Polygon(pts)
                        if not p.is_valid:
                            p = p.buffer(0)
                        if not p.is_empty:
                            if p.geom_type == 'MultiPolygon':
                                valid_polys.extend(list(p.geoms))
                            elif p.geom_type == 'Polygon':
                                valid_polys.append(p)
                    except Exception:
                        pass
            if valid_polys:
                try:
                    union_p = unary_union(valid_polys)
                    self.polygons_by_layer[layer_id] = union_p
                except Exception:
                    self.polygons_by_layer[layer_id] = valid_polys
            else:
                self.polygons_by_layer[layer_id] = None
                
        print(f"[Coin3D] Successfully parsed {len(self.polygons_by_layer)} layers.")

    def generate_hatch_lines(self, geometry, angle_deg, pitch_mm, bidirectional=None):
        """Generates scanline hatch vectors intersecting the polygon at the given angle."""
        if geometry is None or geometry.is_empty:
            return []
            
        if bidirectional is None:
            bidirectional = getattr(self, 'bidirectional', True)

        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # Bounding box
        minx, miny, maxx, maxy = geometry.bounds
        diag = math.hypot(maxx - minx, maxy - miny) * 1.2
        cx = (minx + maxx) / 2.0
        cy = (miny + maxy) / 2.0
        
        # Number of scanlines needed
        num_lines = int(diag / pitch_mm)
        hatch_segments = []
        is_reverse = False
        
        for i in range(-num_lines // 2, num_lines // 2 + 1):
            offset = i * pitch_mm
            px = cx - offset * sin_a
            py = cy + offset * cos_a
            
            p1 = (px - diag * cos_a, py - diag * sin_a)
            p2 = (px + diag * cos_a, py + diag * sin_a)
            
            line = LineString([p1, p2])
            try:
                intersect = geometry.intersection(line)
                if intersect.is_empty:
                    continue
                line_segs = []
                if intersect.geom_type == 'LineString':
                    coords = list(intersect.coords)
                    if len(coords) >= 2:
                        line_segs.append((coords[0], coords[-1]))
                elif intersect.geom_type == 'MultiLineString':
                    for sub in intersect.geoms:
                        coords = list(sub.coords)
                        if len(coords) >= 2:
                            line_segs.append((coords[0], coords[-1]))
                            
                if bidirectional and is_reverse:
                    for (c0, c1) in reversed(line_segs):
                        hatch_segments.append((c1, c0))
                else:
                    for (c0, c1) in line_segs:
                        hatch_segments.append((c0, c1))
                if bidirectional and line_segs:
                    is_reverse = not is_reverse
            except Exception:
                pass
                
        return hatch_segments

    def compile_job_queue(self, **kwargs):
        """
        Compiles the entire multi-pass 3D engraving queue with descending passes,
        rotating hatch angles, perimeter contour traces, and cleaning passes.
        """
        pwr_scale = float(kwargs.get('power_scale', getattr(self, 'power_scale', 1.0)))
        spd_scale = float(kwargs.get('speed_scale', getattr(self, 'speed_scale', 1.0)))
        clean_int = int(kwargs.get('clean_interval', 6))
        if 'offset_x_mm' in kwargs:
            self.offset_x_mm = float(kwargs['offset_x_mm'])
        if 'offset_y_mm' in kwargs:
            self.offset_y_mm = float(kwargs['offset_y_mm'])

        if not self.polygons_by_layer:
            self.load_dxf_layers()
            
        send_queue = []
        total_layers = len(self.layer_recipes)
        self.layers = []
        total_passes = sum(r['passes'] for r in self.layer_recipes if self.polygons_by_layer.get(r['layer_id']) is not None)
        pass_counter = 0
        
        print("\n" + "="*60)
        print("COMPILING 3D COIN RELIEF ENGRAVING QUEUE (27mm 10-RUPEE COIN)")
        print(f"Power Scale: {pwr_scale:.2f} | Speed Scale: {spd_scale:.2f} | Offset: ({self.offset_x_mm:.2f}, {self.offset_y_mm:.2f})mm")
        print("="*60)
        
        for l_idx, recipe in enumerate(self.layer_recipes):
            l_id = recipe["layer_id"]
            name = recipe["name"]
            passes = recipe["passes"]
            power = max(10.0, min(95.0, recipe["power_pct"] * pwr_scale))
            freq = recipe["freq_khz"]
            m_speed = max(100.0, min(2000.0, recipe["mark_speed_mms"] * spd_scale))
            j_speed = recipe["jump_speed_mms"]
            pitch = recipe["hatch_pitch_mm"]
            base_rot = recipe["rot_angle_deg"]
            mode = recipe["mode"]
            depth_tgt = float(recipe.get("depth_target_mm", 0.5))
            
            geom = self.polygons_by_layer.get(l_id)
            if geom is None:
                continue
                
            print(f" -> Layer {l_idx:02d}: {name} | Passes: {passes} | Power: {power:.0f}% | Freq: {freq}kHz")
            
            for p in range(passes):
                pass_counter += 1
                rot_ang = (p * base_rot) % 180.0
                pass_cmds = []
                
                # Check if we should interleave a Brass Soot-Cleaning Pass
                if mode == "ablate" and clean_int > 0 and (pass_counter % clean_int == 0):
                    send_queue.append({
                        'type': 'pass_change',
                        'layer_idx': pass_counter,
                        'total_layers': total_passes,
                        'depth_mm': depth_tgt,
                        'angle_deg': 90.0,
                        'desc': f"Brass De-oxidation Cleaning Pass (after {pass_counter} ablation passes)"
                    })
                    # High-speed low-power cross-hatch clean
                    clean_lines = self.generate_hatch_lines(geom, 90.0, pitch_mm=0.040, bidirectional=True)
                    for (x1, y1), (x2, y2) in clean_lines:
                        gx1, gy1 = self.mm_to_galvo(x1, y1)
                        gx2, gy2 = self.mm_to_galvo(x2, y2)
                        send_queue.append({'type': 'jump', 'x': gx1, 'y': gy1, 'speed': int(2000 * self.galvo_units_per_mm), 'depth_mm': depth_tgt})
                        send_queue.append({'type': 'mark', 'x': gx2, 'y': gy2, 'speed': int(1400 * self.galvo_units_per_mm), 'power': 18.0, 'freq': 80.0, 'depth_mm': depth_tgt})
                
                # 1. Hatch lines
                lines = self.generate_hatch_lines(geom, rot_ang, pitch_mm=pitch, bidirectional=True)
                jump_speed_gu = int(j_speed * self.galvo_units_per_mm)
                mark_speed_gu = int(m_speed * self.galvo_units_per_mm)
                
                for (x1, y1), (x2, y2) in lines:
                    gx1, gy1 = self.mm_to_galvo(x1, y1)
                    gx2, gy2 = self.mm_to_galvo(x2, y2)
                    pass_cmds.append({'type': 'jump', 'x': gx1, 'y': gy1, 'speed': jump_speed_gu, 'depth_mm': depth_tgt})
                    pass_cmds.append({'type': 'mark', 'x': gx2, 'y': gy2, 'speed': mark_speed_gu, 'power': power, 'freq': freq, 'depth_mm': depth_tgt})
                    
                # 2. Outer contour cleanup pass (Perimeter outline to ensure razor-sharp edges)
                if p == passes - 1 or p == 0:
                    polys_to_trace = []
                    if geom.geom_type == 'Polygon':
                        polys_to_trace = [geom]
                    elif geom.geom_type == 'MultiPolygon':
                        polys_to_trace = list(geom.geoms)
                        
                    for poly in polys_to_trace:
                        ext_coords = list(poly.exterior.coords)
                        if ext_coords:
                            gx0, gy0 = self.mm_to_galvo(ext_coords[0][0], ext_coords[0][1])
                            pass_cmds.append({'type': 'jump', 'x': gx0, 'y': gy0, 'speed': jump_speed_gu, 'depth_mm': depth_tgt})
                            for pt in ext_coords[1:]:
                                gx, gy = self.mm_to_galvo(pt[0], pt[1])
                                pass_cmds.append({'type': 'mark', 'x': gx, 'y': gy, 'speed': mark_speed_gu, 'power': power * 0.75, 'freq': freq, 'depth_mm': depth_tgt})

                self.layers.append({
                    'layer_idx': pass_counter,
                    'total_layers': total_passes,
                    'depth_mm': depth_tgt,
                    'angle_deg': rot_ang,
                    'commands': pass_cmds
                })

                send_queue.append({
                    'type': 'pass_change',
                    'layer_idx': pass_counter,
                    'total_layers': total_passes,
                    'depth_mm': depth_tgt,
                    'angle_deg': rot_ang,
                    'desc': f"{name} - Pass {p+1}/{passes} (Hatch Angle: {rot_ang:.1f} deg)"
                })
                send_queue.extend(pass_cmds)
                                
        print(f"Compilation complete: Total Galvo commands = {len(send_queue)}")
        return send_queue

    def generate_redlight_boundary_queue(self):
        """Generates continuous red-pointer circular framing queue (Dia 27.0 mm) for alignment."""
        queue = []
        r = 13.500 # mm
        num_pts = 64
        speed_gu = int(1200 * self.galvo_units_per_mm)
        
        pts = []
        for i in range(num_pts):
            ang = i * 2.0 * math.pi / float(num_pts)
            x = r * math.cos(ang)
            y = r * math.sin(ang)
            gx, gy = self.mm_to_galvo(x, y)
            pts.append((gx, gy))
        pts.append(pts[0])
        
        queue.append({'type': 'jump', 'x': pts[0][0], 'y': pts[0][1], 'speed': speed_gu})
        for pt in pts[1:]:
            queue.append({'type': 'mark', 'x': pt[0], 'y': pt[1], 'speed': speed_gu})
            
        return queue

    def export_gcode(self, output_path, clean_interval: int = 6, **kwargs):
        """Exports true 3D G-code of the multi-layer relief job for 3D OpenGL preview (preview3d.py)."""
        queue = self.compile_job_queue(clean_interval=clean_interval, **kwargs)
        print(f"[Coin3D] Exporting preview G-code to: {output_path}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("; 27mm 10-Rupee Coin 3D Bas-Relief G-Code\n")
            f.write("; Material: 1.0mm Brass | Max Depth: 0.50mm\n")
            f.write("G21 ; Metric units\n")
            f.write("G90 ; Absolute coordinates\n")
            f.write("M05 ; Laser OFF\n")
            
            cur_z = 0.0
            for cmd in queue:
                ctype = cmd.get('type')
                if ctype == 'pass_change':
                    cur_z = float(cmd.get('depth_mm') or 0.0)
                    f.write(f"; {cmd.get('desc', '')}\n")
                    f.write(f"G0 Z-{cur_z:.3f}\n")
                elif ctype == 'jump':
                    x_mm = (cmd['x'] - self.center_bits) / self.galvo_units_per_mm
                    y_mm = (cmd['y'] - self.center_bits) / self.galvo_units_per_mm
                    f.write(f"G0 X{x_mm:.3f} Y{y_mm:.3f} Z-{cur_z:.3f}\n")
                elif ctype == 'mark':
                    x_mm = (cmd['x'] - self.center_bits) / self.galvo_units_per_mm
                    y_mm = (cmd['y'] - self.center_bits) / self.galvo_units_per_mm
                    p = int(cmd.get('power', 80.0) * 10)
                    f.write(f"G1 X{x_mm:.3f} Y{y_mm:.3f} Z-{cur_z:.3f} S{p}\n")
                    
            f.write("M05 ; Laser OFF\n")
            f.write("G0 X0 Y0 Z0 ; Return home\n")
        print(f"[Coin3D] True 3D G-code export complete ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    engraver = Coin3DReliefEngraver()
    engraver.load_dxf_layers()
    queue = engraver.compile_job_queue()
    gcode_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DeepEngrave", "rupee_10_relief_27mm.gcode")
    engraver.export_gcode(gcode_path)
