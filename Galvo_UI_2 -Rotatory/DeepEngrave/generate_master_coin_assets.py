import xml.etree.ElementTree as ET
import re
import math
import numpy as np
import cv2
import ezdxf

def parse_svg_path(d_str, samples_per_bezier=20):
    """
    Parses SVG path string containing M, L, C, Z commands into list of polylines.
    """
    tokens = re.findall(r'([A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)', d_str)
    polylines = []
    current_poly = []
    current_pt = (0.0, 0.0)
    start_pt = (0.0, 0.0)
    
    i = 0
    cmd = 'M'
    while i < len(tokens):
        token = tokens[i]
        if token.isalpha():
            cmd = token
            i += 1
            if i >= len(tokens):
                break
        
        if cmd == 'M':
            x = float(tokens[i])
            y = float(tokens[i+1])
            i += 2
            current_pt = (x, y)
            start_pt = current_pt
            if current_poly:
                polylines.append(current_poly)
            current_poly = [current_pt]
            cmd = 'L' # Subsequent pairs are treated as implicit LineTo
        elif cmd == 'L':
            x = float(tokens[i])
            y = float(tokens[i+1])
            i += 2
            current_pt = (x, y)
            current_poly.append(current_pt)
        elif cmd == 'C':
            x1 = float(tokens[i])
            y1 = float(tokens[i+1])
            x2 = float(tokens[i+2])
            y2 = float(tokens[i+3])
            x = float(tokens[i+4])
            y = float(tokens[i+5])
            i += 6
            p0 = current_pt
            p1 = (x1, y1)
            p2 = (x2, y2)
            p3 = (x, y)
            for step in range(1, samples_per_bezier + 1):
                t = step / float(samples_per_bezier)
                t_inv = 1.0 - t
                bx = (t_inv**3)*p0[0] + 3*(t_inv**2)*t*p1[0] + 3*t_inv*(t**2)*p2[0] + (t**3)*p3[0]
                by = (t_inv**3)*p0[1] + 3*(t_inv**2)*t*p1[1] + 3*t_inv*(t**2)*p2[1] + (t**3)*p3[1]
                current_poly.append((bx, by))
            current_pt = p3
        elif cmd == 'Z':
            if current_poly and start_pt != current_pt:
                current_poly.append(start_pt)
            current_pt = start_pt
            if current_poly:
                polylines.append(current_poly)
                current_poly = []
            # cmd remains Z or next token
        else:
            i += 1
            
    if current_poly:
        polylines.append(current_poly)
        
    return polylines

def generate_master_files(svg_path, out_dxf_path, out_heightmap_path):
    print(f"Reading master SVG: {svg_path}")
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Setup DXF
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    layer_config = {
        "LAYER_00_BASE_FIELD": {"dxf_aci": 7, "color_hex": "#000000", "depth_mm": 0.50, "passes": 20},
        "LAYER_01_BIMETALLIC_TRENCH": {"dxf_aci": 5, "color_hex": "#0000FF", "depth_mm": 0.40, "passes": 15},
        "LAYER_02_RELIEF_STEP_1": {"dxf_aci": 4, "color_hex": "#00FFFF", "depth_mm": 0.30, "passes": 10},
        "LAYER_03_RELIEF_STEP_2": {"dxf_aci": 3, "color_hex": "#00AA00", "depth_mm": 0.20, "passes": 6},
        "LAYER_04_HIGH_RELIEF": {"dxf_aci": 2, "color_hex": "#FF8800", "depth_mm": 0.10, "passes": 3},
        "LAYER_05_CREST_SURFACE": {"dxf_aci": 1, "color_hex": "#FF0000", "depth_mm": 0.00, "passes": 1},
    }
    
    for l_id, cfg in layer_config.items():
        doc.layers.add(name=l_id, color=cfg["dxf_aci"])
        
    # Heightmap raster resolution: 2700 x 2700 pixels (100 pixels per mm = 10 um per pixel)
    img_size = 2700
    scale = img_size / 27.0
    # 16-bit grayscale image, initial background is 0.50mm depth = darkest (value ~ 5000 out of 65535)
    # 0.00mm depth = pure white 65535, 0.50mm depth = black 0
    # Let's map height: H = (0.50 - depth) / 0.50 * 65535
    # So depth 0.0mm (highest crest) -> 65535
    # depth 0.50mm (lowest base) -> 0
    heightmap_16bit = np.zeros((img_size, img_size), dtype=np.uint16)
    
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Ingest groups / layers
    for group in root.findall('.//{http://www.w3.org/2000/svg}g'):
        layer_id = group.attrib.get('id', '')
        if layer_id not in layer_config:
            # Check inkscape label
            layer_id = group.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label', '')
            for k in layer_config:
                if k in layer_id:
                    layer_id = k
                    break
        if layer_id not in layer_config:
            continue
            
        cfg = layer_config[layer_id]
        depth = cfg["depth_mm"]
        height_val_16 = int(round((0.50 - depth) / 0.50 * 65535))
        
        # 1. Circles
        for c in group.findall('{http://www.w3.org/2000/svg}circle'):
            cx = float(c.attrib['cx'])
            cy = float(c.attrib['cy'])
            r = float(c.attrib['r'])
            # Note DXF Y goes upwards, SVG Y goes downwards. We keep metric coordinates.
            # Center is at (13.5, 13.5).
            # To preserve standard orientation, y_dxf = 27.0 - cy
            msp.add_circle((cx, 27.0 - cy), r, dxfattribs={"layer": layer_id})
            
            # Draw on heightmap
            px_cx = int(round(cx * scale))
            px_cy = int(round(cy * scale))
            px_r = int(round(r * scale))
            # For base field, the outermost circle defines the boundary of the coin
            if layer_id == "LAYER_00_BASE_FIELD" and r >= 13.0:
                cv2.circle(heightmap_16bit, (px_cx, px_cy), px_r, height_val_16, -1)
            else:
                cv2.circle(heightmap_16bit, (px_cx, px_cy), px_r, height_val_16, -1)
                
        # 2. Ellipses
        for el in group.findall('{http://www.w3.org/2000/svg}ellipse'):
            cx = float(el.attrib['cx'])
            cy = float(el.attrib['cy'])
            rx = float(el.attrib['rx'])
            ry = float(el.attrib['ry'])
            
            # Approximate ellipse in DXF as closed polyline
            pts = []
            for a in range(64):
                ang = a * 2 * math.pi / 64.0
                ex = cx + rx * math.cos(ang)
                ey = 27.0 - (cy + ry * math.sin(ang))
                pts.append((ex, ey))
            pts.append(pts[0])
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer_id})
            
            px_cx = int(round(cx * scale))
            px_cy = int(round(cy * scale))
            px_rx = int(round(rx * scale))
            px_ry = int(round(ry * scale))
            cv2.ellipse(heightmap_16bit, (px_cx, px_cy), (px_rx, px_ry), 0, 0, 360, height_val_16, -1)
            
        # 3. Paths
        for p in group.findall('{http://www.w3.org/2000/svg}path'):
            d = p.attrib['d']
            polys = parse_svg_path(d)
            for poly in polys:
                if len(poly) < 2:
                    continue
                # Add to DXF
                dxf_poly = [(pt[0], 27.0 - pt[1]) for pt in poly]
                is_closed = (math.hypot(poly[0][0] - poly[-1][0], poly[0][1] - poly[-1][1]) < 0.05)
                msp.add_lwpolyline(dxf_poly, close=is_closed, dxfattribs={"layer": layer_id})
                
                # Rasterize poly into heightmap
                img_pts = np.array([[int(round(pt[0] * scale)), int(round(pt[1] * scale))] for pt in poly], dtype=np.int32)
                if is_closed and len(img_pts) >= 3:
                    cv2.fillPoly(heightmap_16bit, [img_pts], height_val_16)
                else:
                    cv2.polylines(heightmap_16bit, [img_pts], False, height_val_16, thickness=max(1, int(round(0.1 * scale))))

    # Save DXF
    doc.saveas(out_dxf_path)
    print(f"Saved master DXF: {out_dxf_path}")
    
    # Apply subtle anti-aliasing / Gaussian blur to heightmap to prevent stair-stepping
    blurred_16 = cv2.GaussianBlur(heightmap_16bit, (5, 5), 1.0)
    cv2.imwrite(out_heightmap_path, blurred_16)
    print(f"Saved 16-bit Heightmap: {out_heightmap_path}")
    
    # Save 8-bit preview for UI and quick inspection
    preview_8bit = (blurred_16 >> 8).astype(np.uint8)
    preview_path = out_heightmap_path.replace(".png", "_preview8.png")
    cv2.imwrite(preview_path, preview_8bit)
    print(f"Saved 8-bit Heightmap Preview: {preview_path}")

if __name__ == "__main__":
    import os
    base_dir = r"d:\Atharva\Galvo_Scribber\Galvo_UI_2\DeepEngrave"
    svg_source = os.path.join(base_dir, "27mm_10_rupee_coin_3d_relief_vector.md")
    
    # Copy SVG source to clean .svg file
    master_svg = os.path.join(base_dir, "rupee_10_relief_27mm_master.svg")
    with open(svg_source, "r", encoding="utf-8") as f_in:
        content = f_in.read()
    with open(master_svg, "w", encoding="utf-8") as f_out:
        f_out.write(content)
    print(f"Saved master SVG: {master_svg}")
    
    out_dxf = os.path.join(base_dir, "rupee_10_relief_27mm_master.dxf")
    out_hmap = os.path.join(base_dir, "rupee_10_relief_27mm_heightmap.png")
    generate_master_files(master_svg, out_dxf, out_hmap)
