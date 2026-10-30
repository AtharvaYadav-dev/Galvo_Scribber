import os
import math
import numpy as np
import cv2
import ezdxf

def create_perfect_coin_assets(base_dir, diameter_mm=27.0, max_depth_mm=0.50):
    """
    Generates a mathematically perfect 3D Bas-Relief Coin model for 1.0mm brass.
    Diameter: 27.0 mm (RBI official spec)
    Max relief depth: 0.50 mm (safe budget for 1.0mm sheet)
    Resolution: 2700 x 2700 pixels (10 microns per pixel)
    """
    os.makedirs(base_dir, exist_ok=True)
    img_size = int(diameter_mm * 100) # 2700 px
    radius_mm = diameter_mm / 2.0     # 13.5 mm
    scale = img_size / diameter_mm     # 100.0 px/mm
    cx = img_size / 2.0
    cy = img_size / 2.0
    
    print(f"[PerfectCoin] Generating {img_size}x{img_size} 16-bit Master Heightmap...")
    
    # Coordinate grid in millimeters relative to center
    y_idx, x_idx = np.ogrid[:img_size, :img_size]
    x_mm = (x_idx - cx) / scale
    y_mm = (cy - y_idx) / scale # Invert Y so up is positive
    r_mm = np.sqrt(x_mm**2 + y_mm**2)
    theta = np.arctan2(y_mm, x_mm) # Angle in radians [-pi, pi]
    
    # Height array in millimeters: 0.0 mm = top unengraved surface, -0.50 mm = deepest floor
    # We will later map this to 16-bit unsigned int: 0.0mm -> 65535 (white), -0.50mm -> 0 (black)
    z_mm = np.full((img_size, img_size), -max_depth_mm, dtype=np.float32)
    
    # -------------------------------------------------------------------------
    # 1. OUTSIDE COIN BACKGROUND (Pure Black / Cutout Plane)
    # -------------------------------------------------------------------------
    outside_mask = r_mm > radius_mm
    z_mm[outside_mask] = -max_depth_mm
    
    # -------------------------------------------------------------------------
    # 2. RAISED OUTER PROTECTIVE RIM (0.00 mm Depth - Top Plateau)
    # Rim width: 0.8 mm (12.7 mm to 13.5 mm radius)
    # Inner chamfer: 12.3 mm to 12.7 mm
    # -------------------------------------------------------------------------
    rim_flat_mask = (r_mm >= 12.65) & (r_mm <= radius_mm)
    z_mm[rim_flat_mask] = 0.0 # Top surface
    
    # Rim inner slope (smooth chamfer transition from 0.0 down to base floor -0.42mm)
    rim_slope_mask = (r_mm >= 12.20) & (r_mm < 12.65)
    slope_t = (r_mm[rim_slope_mask] - 12.20) / (12.65 - 12.20) # 0 to 1
    z_mm[rim_slope_mask] = -0.42 + 0.42 * (slope_t**1.5)
    
    # Base coin field background: -0.42 mm
    field_mask = r_mm < 12.20
    z_mm[field_mask] = -0.42
    
    # -------------------------------------------------------------------------
    # 3. BEADED DENTICLE RING (72 Spherical Mint Beads at R = 11.85 mm)
    # Real mint coins have a beaded inner ring that frames the coin.
    # -------------------------------------------------------------------------
    num_beads = 72
    bead_r_center = 11.80
    bead_radius = 0.22
    for b in range(num_beads):
        b_ang = b * 2.0 * math.pi / float(num_beads)
        bx = bead_r_center * math.cos(b_ang)
        by = bead_r_center * math.sin(b_ang)
        
        # Distance from bead center
        d_bead = np.sqrt((x_mm - bx)**2 + (y_mm - by)**2)
        b_mask = d_bead <= bead_radius
        if np.any(b_mask):
            # Spherical dome profile
            dome = np.sqrt(np.maximum(0.0, 1.0 - (d_bead[b_mask] / bead_radius)**2))
            bead_z = -0.38 + 0.26 * dome # Peak height at -0.12 mm
            z_mm[b_mask] = np.maximum(z_mm[b_mask], bead_z)
            
    # -------------------------------------------------------------------------
    # 4. BI-METALLIC GROOVE (Ring separating outer and inner core at R = 9.0 mm)
    # -------------------------------------------------------------------------
    trench_mask = (r_mm >= 8.85) & (r_mm <= 9.15)
    trench_prof = np.cos((r_mm[trench_mask] - 9.0) / 0.15 * (math.pi / 2.0))
    z_mm[trench_mask] = np.minimum(z_mm[trench_mask], -0.42 - 0.06 * trench_prof)
    
    # -------------------------------------------------------------------------
    # 5. GUILLOCHÉ SUNBURST BACKGROUND TEXTURE (Inner Core R < 8.8 mm)
    # 72 micro-fluting facets creating dynamic holographic reflection on brass
    # -------------------------------------------------------------------------
    core_field_mask = (r_mm < 8.80) & (r_mm > 1.0)
    sunburst = np.sin(theta[core_field_mask] * 72.0) * 0.020 # +/- 20 microns
    z_mm[core_field_mask] += sunburst
    
    # -------------------------------------------------------------------------
    # 6. SYMMETRICAL LAUREL WHEAT EARS / LEAVES (Left & Right Flanks)
    # 12 leaves on left, 12 leaves on right
    # -------------------------------------------------------------------------
    def draw_leaf(lx, ly, leaf_len, leaf_wid, leaf_rot, peak_height_mm):
        cos_l = math.cos(leaf_rot)
        sin_l = math.sin(leaf_rot)
        dx = x_mm - lx
        dy = y_mm - ly
        u = dx * cos_l + dy * sin_l # Along leaf major axis
        v = -dx * sin_l + dy * cos_l # Along leaf minor axis
        
        leaf_mask = (u >= -leaf_len/2.0) & (u <= leaf_len/2.0) & (np.abs(v) <= leaf_wid/2.0)
        u_norm = (u[leaf_mask] / (leaf_len/2.0))**2
        v_norm = (v[leaf_mask] / (leaf_wid/2.0))**2
        dist_sq = u_norm + v_norm
        inside = dist_sq <= 1.0
        
        if np.any(inside):
            sub_mask = np.zeros_like(leaf_mask)
            sub_mask[leaf_mask] = inside
            dome = np.sqrt(np.maximum(0.0, 1.0 - dist_sq[inside]))
            cur_z = -0.38 + (peak_height_mm + 0.38) * dome
            z_mm[sub_mask] = np.maximum(z_mm[sub_mask], cur_z)

    # Place left wheat leaves (curving from bottom-left to top-left)
    for i in range(10):
        ang_deg = 115.0 + i * 14.0 # 115 to 241 deg
        ang_rad = math.radians(ang_deg)
        lr = 6.8 + 0.15 * math.sin(i * 0.3)
        lx = lr * math.cos(ang_rad)
        ly = lr * math.sin(ang_rad)
        draw_leaf(lx, ly, leaf_len=1.4, leaf_wid=0.7, leaf_rot=ang_rad + math.pi/4.0, peak_height_mm=-0.10)
        
    # Place right wheat leaves (curving symmetrically on right side)
    for i in range(10):
        ang_deg = 65.0 - i * 14.0 # 65 to -61 deg
        ang_rad = math.radians(ang_deg)
        lr = 6.8 + 0.15 * math.sin(i * 0.3)
        lx = lr * math.cos(ang_rad)
        ly = lr * math.sin(ang_rad)
        draw_leaf(lx, ly, leaf_len=1.4, leaf_wid=0.7, leaf_rot=ang_rad - math.pi/4.0, peak_height_mm=-0.10)

    # -------------------------------------------------------------------------
    # 7. HIGH-PRECISION VECTOR TYPOGRAPHY & INSIGNIA
    # We rasterize perfect mathematical vector paths with beveled chamfers
    # -------------------------------------------------------------------------
    # Helper: draw beveled polygon with stepped height
    def draw_beveled_polygon(pts_mm, base_z=-0.30, top_z=-0.04, bevel_steps=8):
        pts_px = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in pts_mm], dtype=np.int32)
        poly_mask = np.zeros((img_size, img_size), dtype=np.uint8)
        cv2.fillPoly(poly_mask, [pts_px], 255)
        
        # Distance transform for perfect smooth chamfer bevel
        dist = cv2.distanceTransform(poly_mask, cv2.DIST_L2, 5) / scale # In mm
        max_dist = 0.25 # Bevel width in mm
        bevel_factor = np.clip(dist / max_dist, 0.0, 1.0)
        
        # Apply bevel curve
        z_poly = base_z + (top_z - base_z) * (bevel_factor**0.8)
        active = poly_mask > 0
        z_mm[active] = np.maximum(z_mm[active], z_poly[active])

    # A. RUPEE SYMBOL '₹' (Centered at X=0, Y=+3.4 mm)
    # Top bar
    draw_beveled_polygon([(-2.4, 4.8), (2.4, 4.8), (2.4, 4.3), (-2.4, 4.3)], top_z=-0.04)
    # Second bar
    draw_beveled_polygon([(-2.4, 3.8), (1.8, 3.8), (1.8, 3.3), (-2.4, 3.3)], top_z=-0.04)
    # Vertical stem & upper loop
    draw_beveled_polygon([(-1.4, 4.8), (-0.8, 4.8), (-0.8, 2.0), (-1.4, 2.0)], top_z=-0.04)
    # Curved loop of 'R'
    loop_pts = []
    for a in range(-90, 91, 15):
        rad = math.radians(a)
        loop_pts.append((-0.8 + 1.4 * math.cos(rad), 3.55 + 0.8 * math.sin(rad)))
    for a in range(90, -91, -15):
        rad = math.radians(a)
        loop_pts.append((-0.8 + 0.9 * math.cos(rad), 3.55 + 0.45 * math.sin(rad)))
    draw_beveled_polygon(loop_pts, top_z=-0.04)
    # Diagonal leg of '₹'
    draw_beveled_polygon([(-0.8, 2.8), (1.9, 1.1), (1.3, 1.1), (-1.4, 2.5)], top_z=-0.04)

    # B. DENOMINATION '10' (Centered at X=0, Y=-2.8 mm)
    # Digit '1'
    d1_pts = [
        (-2.8, -1.2), (-1.9, -0.6), (-1.2, -0.6), (-1.2, -4.8),
        (-0.5, -4.8), (-0.5, -5.4), (-3.2, -5.4), (-3.2, -4.8),
        (-2.2, -4.8), (-2.2, -1.2)
    ]
    draw_beveled_polygon(d1_pts, top_z=-0.02)
    
    # Digit '0' (Symmetric beveled oval)
    d0_outer = []
    for a in range(0, 360, 10):
        rad = math.radians(a)
        d0_outer.append((1.8 + 1.6 * math.cos(rad), -3.0 + 2.4 * math.sin(rad)))
    d0_inner = []
    for a in range(0, 360, 10):
        rad = math.radians(a)
        d0_inner.append((1.8 + 0.8 * math.cos(rad), -3.0 + 1.5 * math.sin(rad)))
        
    # Draw outer oval
    pts_px = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in d0_outer], dtype=np.int32)
    poly_mask0 = np.zeros((img_size, img_size), dtype=np.uint8)
    cv2.fillPoly(poly_mask0, [pts_px], 255)
    # Mask out inner oval hole
    inner_px = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in d0_inner], dtype=np.int32)
    cv2.fillPoly(poly_mask0, [inner_px], 0)
    
    dist0 = cv2.distanceTransform(poly_mask0, cv2.DIST_L2, 5) / scale
    z_d0 = -0.30 + 0.28 * np.clip(dist0 / 0.35, 0.0, 1.0)**0.8
    active0 = poly_mask0 > 0
    z_mm[active0] = np.maximum(z_mm[active0], z_d0[active0])

    # C. RADIAL ARC TEXT: "BHARAT INDIA" ON UPPER RING (R = 10.3 mm)
    # We render circular text using OpenCV along polar arc
    arc_text_img = np.zeros((img_size, img_size), dtype=np.uint8)
    # Render upper legend
    text_upper = "INDIA  BHARAT"
    # Text angles: 140 deg down to 40 deg across top
    ang_start = 145.0
    ang_end = 35.0
    n_chars = len(text_upper)
    for idx_c, char in enumerate(text_upper):
        if char == ' ': continue
        t_c = idx_c / float(n_chars - 1)
        ang_c = math.radians(ang_start + t_c * (ang_end - ang_start))
        tx = 10.35 * math.cos(ang_c)
        ty = 10.35 * math.sin(ang_c)
        px = int(round(cx + tx * scale))
        py = int(round(cy - ty * scale))
        cv2.putText(arc_text_img, char, (px - 18, py + 18), cv2.FONT_HERSHEY_DUPLEX, 1.3, 255, 3, cv2.LINE_AA)

    # Render lower legend: "2026 TEN RUPEES"
    text_lower = "2026  TEN RUPEES"
    ang_start_l = 215.0
    ang_end_l = 325.0
    n_chars_l = len(text_lower)
    for idx_c, char in enumerate(text_lower):
        if char == ' ': continue
        t_c = idx_c / float(n_chars_l - 1)
        ang_c = math.radians(ang_start_l + t_c * (ang_end_l - ang_start_l))
        tx = 10.35 * math.cos(ang_c)
        ty = 10.35 * math.sin(ang_c)
        px = int(round(cx + tx * scale))
        py = int(round(cy - ty * scale))
        cv2.putText(arc_text_img, char, (px - 18, py + 18), cv2.FONT_HERSHEY_DUPLEX, 1.1, 255, 3, cv2.LINE_AA)

    # Bevel the text
    dist_txt = cv2.distanceTransform(arc_text_img, cv2.DIST_L2, 5) / scale
    z_txt = -0.32 + 0.28 * np.clip(dist_txt / 0.18, 0.0, 1.0)
    active_txt = arc_text_img > 0
    z_mm[active_txt] = np.maximum(z_mm[active_txt], z_txt[active_txt])

    # D. NOIDA MINTMARK DIAMOND at (X=0, Y=-6.4 mm)
    diamond_pts = [(0.0, -5.9), (0.45, -6.4), (0.0, -6.9), (-0.45, -6.4)]
    draw_beveled_polygon(diamond_pts, top_z=-0.04)

    # -------------------------------------------------------------------------
    # 8. POST-PROCESSING: SMOOTH ORGANIC CURVATURE & EXPORT
    # -------------------------------------------------------------------------
    # Outside coin remains flat cutout plane
    z_mm[outside_mask] = -max_depth_mm
    
    # Normalize to 16-bit: -max_depth_mm -> 0, 0.00 mm -> 65535
    norm_z = (z_mm - (-max_depth_mm)) / max_depth_mm # 0.0 to 1.0
    norm_z = np.clip(norm_z, 0.0, 1.0)
    
    heightmap_16 = (norm_z * 65535.0).astype(np.uint16)
    
    # Anti-alias micro smoothing
    heightmap_16 = cv2.GaussianBlur(heightmap_16, (3, 3), 0.7)
    
    hmap_path = os.path.join(base_dir, "rupee_10_coin_perfect_heightmap_16bit.png")
    cv2.imwrite(hmap_path, heightmap_16)
    print(f"[PerfectCoin] Saved 16-Bit Master Heightmap: {hmap_path}")
    
    # 8-bit preview image
    hmap_preview8 = (heightmap_16 >> 8).astype(np.uint8)
    preview_path = os.path.join(base_dir, "rupee_10_coin_perfect_heightmap_preview.png")
    cv2.imwrite(preview_path, hmap_preview8)
    print(f"[PerfectCoin] Saved 8-Bit Preview Heightmap: {preview_path}")

    # Generate realistic 3D hillshade relief image (simulating brass under studio light)
    dx = cv2.Sobel(norm_z, cv2.CV_32F, 1, 0, ksize=3)
    dy = cv2.Sobel(norm_z, cv2.CV_32F, 0, 1, ksize=3)
    # Light source from top-left (angle 315 deg, altitude 45 deg)
    lx = -0.5
    ly = 0.5
    lz = 0.707
    norm = np.sqrt(dx**2 + dy**2 + 1.0)
    shade = ((-dx * lx - dy * ly + lz) / norm)
    shade = np.clip(shade, 0.0, 1.0)
    
    # Brass golden color grading: B=60, G=190, R=235
    brass_render = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    brass_render[:, :, 0] = (shade * 40 + norm_z * 30).astype(np.uint8)   # Blue
    brass_render[:, :, 1] = (shade * 175 + norm_z * 50).astype(np.uint8)  # Green
    brass_render[:, :, 2] = (shade * 220 + norm_z * 35).astype(np.uint8)  # Red
    brass_render[outside_mask] = [20, 20, 20] # Dark background outside coin
    
    render_path = os.path.join(base_dir, "rupee_10_coin_perfect_brass_render.png")
    cv2.imwrite(render_path, brass_render)
    print(f"[PerfectCoin] Saved Realistic 3D Brass Studio Render: {render_path}")

    # -------------------------------------------------------------------------
    # 9. GENERATE PERFECT MULTI-LAYER DXF & SVG
    # -------------------------------------------------------------------------
    generate_perfect_dxf(base_dir, diameter_mm, radius_mm, num_beads, bead_r_center, bead_radius)
    generate_perfect_svg(base_dir, diameter_mm, radius_mm, num_beads, bead_r_center, bead_radius)

def generate_perfect_dxf(base_dir, diameter_mm, radius_mm, num_beads, bead_r_center, bead_radius):
    dxf_path = os.path.join(base_dir, "rupee_10_coin_perfect_master.dxf")
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    layers = [
        {"id": "00_RIM_AND_BASE", "color": 7},      # White/Black
        {"id": "01_MINT_BEAD_RING", "color": 5},    # Blue
        {"id": "02_BIMETAL_GROOVE", "color": 4},    # Cyan
        {"id": "03_WHEAT_LEAVES", "color": 3},      # Green
        {"id": "04_DENOMINATION_10", "color": 2},   # Yellow
        {"id": "05_RUPEE_SYMBOL", "color": 1},      # Red
    ]
    for lyr in layers:
        doc.layers.add(name=lyr["id"], color=lyr["color"])
        
    # Layer 00: Outer Rim & Boundaries (Centered at 0,0)
    msp.add_circle((0, 0), radius_mm, dxfattribs={"layer": "00_RIM_AND_BASE"})
    msp.add_circle((0, 0), 12.65, dxfattribs={"layer": "00_RIM_AND_BASE"})
    msp.add_circle((0, 0), 12.20, dxfattribs={"layer": "00_RIM_AND_BASE"})
    
    # Layer 01: 72 Mint Beads
    for b in range(num_beads):
        b_ang = b * 2.0 * math.pi / float(num_beads)
        bx = bead_r_center * math.cos(b_ang)
        by = bead_r_center * math.sin(b_ang)
        msp.add_circle((bx, by), bead_radius, dxfattribs={"layer": "01_MINT_BEAD_RING"})
        
    # Layer 02: Bi-metallic groove
    msp.add_circle((0, 0), 9.15, dxfattribs={"layer": "02_BIMETAL_GROOVE"})
    msp.add_circle((0, 0), 8.85, dxfattribs={"layer": "02_BIMETAL_GROOVE"})
    
    # Layer 03: Wheat leaves
    for i in range(10):
        for side in [-1, 1]:
            ang_deg = 115.0 + i * 14.0 if side == -1 else 65.0 - i * 14.0
            ang_rad = math.radians(ang_deg)
            lr = 6.8
            lx = lr * math.cos(ang_rad)
            ly = lr * math.sin(ang_rad)
            # Add leaf ellipse
            msp.add_ellipse(
                center=(lx, ly),
                major_axis=(0.7 * math.cos(ang_rad), 0.7 * math.sin(ang_rad)),
                ratio=0.5,
                dxfattribs={"layer": "03_WHEAT_LEAVES"}
            )
            
    # Layer 04: Denomination Numeral 10
    d1_pts = [
        (-2.8, -1.2), (-1.9, -0.6), (-1.2, -0.6), (-1.2, -4.8),
        (-0.5, -4.8), (-0.5, -5.4), (-3.2, -5.4), (-3.2, -4.8),
        (-2.2, -4.8), (-2.2, -1.2)
    ]
    msp.add_lwpolyline(d1_pts, close=True, dxfattribs={"layer": "04_DENOMINATION_10"})
    
    # Digit 0 inner and outer ellipse
    msp.add_ellipse(center=(1.8, -3.0), major_axis=(0, 2.4), ratio=1.6/2.4, dxfattribs={"layer": "04_DENOMINATION_10"})
    msp.add_ellipse(center=(1.8, -3.0), major_axis=(0, 1.5), ratio=0.8/1.5, dxfattribs={"layer": "04_DENOMINATION_10"})
    
    # Layer 05: Rupee Symbol
    msp.add_lwpolyline([(-2.4, 4.8), (2.4, 4.8), (2.4, 4.3), (-2.4, 4.3)], close=True, dxfattribs={"layer": "05_RUPEE_SYMBOL"})
    msp.add_lwpolyline([(-2.4, 3.8), (1.8, 3.8), (1.8, 3.3), (-2.4, 3.3)], close=True, dxfattribs={"layer": "05_RUPEE_SYMBOL"})
    msp.add_lwpolyline([(-1.4, 4.8), (-0.8, 4.8), (-0.8, 2.0), (-1.4, 2.0)], close=True, dxfattribs={"layer": "05_RUPEE_SYMBOL"})
    msp.add_lwpolyline([(-0.8, 2.8), (1.9, 1.1), (1.3, 1.1), (-1.4, 2.5)], close=True, dxfattribs={"layer": "05_RUPEE_SYMBOL"})
    
    doc.saveas(dxf_path)
    print(f"[PerfectCoin] Saved Perfect Multi-Layer DXF: {dxf_path}")

def generate_perfect_svg(base_dir, diameter_mm, radius_mm, num_beads, bead_r_center, bead_radius):
    svg_path = os.path.join(base_dir, "rupee_10_coin_perfect_master.svg")
    cx = radius_mm
    cy = radius_mm
    
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{diameter_mm:.3f}mm" height="{diameter_mm:.3f}mm" viewBox="0 0 {diameter_mm:.3f} {diameter_mm:.3f}" version="1.1">\n')
        f.write('  <style>\n')
        f.write('    .rim { fill: none; stroke: #000000; stroke-width: 0.05; }\n')
        f.write('    .bead { fill: none; stroke: #0000ff; stroke-width: 0.05; }\n')
        f.write('    .groove { fill: none; stroke: #00cccc; stroke-width: 0.05; }\n')
        f.write('    .leaves { fill: none; stroke: #00aa00; stroke-width: 0.05; }\n')
        f.write('    .num { fill: none; stroke: #ff8800; stroke-width: 0.05; }\n')
        f.write('    .rupee { fill: none; stroke: #ff0000; stroke-width: 0.05; }\n')
        f.write('  </style>\n')
        
        # Layer 00: Rim
        f.write('  <g id="LAYER_00_RIM" class="rim">\n')
        f.write(f'    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="{radius_mm:.3f}" />\n')
        f.write(f'    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="12.650" />\n')
        f.write(f'    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="12.200" />\n')
        f.write('  </g>\n')
        
        # Layer 01: Beads
        f.write('  <g id="LAYER_01_BEADS" class="bead">\n')
        for b in range(num_beads):
            b_ang = b * 2.0 * math.pi / float(num_beads)
            bx = cx + bead_r_center * math.cos(b_ang)
            by = cy - bead_r_center * math.sin(b_ang)
            f.write(f'    <circle cx="{bx:.3f}" cy="{by:.3f}" r="{bead_radius:.3f}" />\n')
        f.write('  </g>\n')
        
        # Layer 02: Groove
        f.write('  <g id="LAYER_02_GROOVE" class="groove">\n')
        f.write(f'    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="9.150" />\n')
        f.write(f'    <circle cx="{cx:.3f}" cy="{cy:.3f}" r="8.850" />\n')
        f.write('  </g>\n')
        
        # Layer 03: Wheat leaves
        f.write('  <g id="LAYER_03_LEAVES" class="leaves">\n')
        for i in range(10):
            for side in [-1, 1]:
                ang_deg = 115.0 + i * 14.0 if side == -1 else 65.0 - i * 14.0
                ang_rad = math.radians(ang_deg)
                lr = 6.8
                lx = cx + lr * math.cos(ang_rad)
                ly = cy - lr * math.sin(ang_rad)
                f.write(f'    <ellipse cx="{lx:.3f}" cy="{ly:.3f}" rx="0.700" ry="0.350" transform="rotate({-math.degrees(ang_rad):.1f} {lx:.3f} {ly:.3f})" />\n')
        f.write('  </g>\n')
        
        # Layer 04: Denomination 10
        f.write('  <g id="LAYER_04_NUMERAL_10" class="num">\n')
        f.write(f'    <path d="M {cx-2.8:.3f},{cy+1.2:.3f} L {cx-1.9:.3f},{cy+0.6:.3f} L {cx-1.2:.3f},{cy+0.6:.3f} L {cx-1.2:.3f},{cy+4.8:.3f} L {cx-0.5:.3f},{cy+4.8:.3f} L {cx-0.5:.3f},{cy+5.4:.3f} L {cx-3.2:.3f},{cy+5.4:.3f} L {cx-3.2:.3f},{cy+4.8:.3f} L {cx-2.2:.3f},{cy+4.8:.3f} L {cx-2.2:.3f},{cy+1.2:.3f} Z" />\n')
        f.write(f'    <ellipse cx="{cx+1.8:.3f}" cy="{cy+3.0:.3f}" rx="1.600" ry="2.400" />\n')
        f.write(f'    <ellipse cx="{cx+1.8:.3f}" cy="{cy+3.0:.3f}" rx="0.800" ry="1.500" />\n')
        f.write('  </g>\n')
        
        # Layer 05: Rupee Symbol
        f.write('  <g id="LAYER_05_RUPEE" class="rupee">\n')
        f.write(f'    <rect x="{cx-2.4:.3f}" y="{cy-4.8:.3f}" width="4.800" height="0.500" />\n')
        f.write(f'    <rect x="{cx-2.4:.3f}" y="{cy-3.8:.3f}" width="4.200" height="0.500" />\n')
        f.write(f'    <rect x="{cx-1.4:.3f}" y="{cy-4.8:.3f}" width="0.600" height="2.800" />\n')
        f.write(f'    <path d="M {cx-0.8:.3f},{cy-2.8:.3f} L {cx+1.9:.3f},{cy-1.1:.3f} L {cx+1.3:.3f},{cy-1.1:.3f} L {cx-1.4:.3f},{cy-2.5:.3f} Z" />\n')
        f.write('  </g>\n')
        f.write('</svg>\n')
        
    print(f"[PerfectCoin] Saved Perfect Multi-Layer SVG: {svg_path}")

if __name__ == "__main__":
    out_dir = r"d:\Atharva\Galvo_Scribber\Galvo_UI_2\DeepEngrave"
    create_perfect_coin_assets(out_dir, diameter_mm=27.0, max_depth_mm=0.50)
