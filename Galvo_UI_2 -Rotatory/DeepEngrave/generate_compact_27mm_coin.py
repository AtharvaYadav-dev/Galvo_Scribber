import os
import math
import numpy as np
import cv2
import ezdxf

def generate_compact_27mm_coin(output_dir, diameter_mm=27.0, thickness_mm=1.8, max_depth_mm=0.75, resolution_px=1080):
    """
    Generates a lightweight, compact, high-precision 3D bas-relief coin file:
    - Diameter: strictly 27.0 mm (Circular / Round)
    - Substrate Thickness: ~1.7mm to 1.9mm (1.8mm nominal)
    - Max Relief Depth: 0.75 mm (leaves 1.05mm solid base, no burn-through/warping)
    - Resolution: 1080 x 1080 pixels (40 pixels/mm = 25 um/px spot match)
    - File size: Ultra-compact (< 300 KB), fast loading, zero UI lag
    """
    os.makedirs(output_dir, exist_ok=True)
    img_size = int(resolution_px)
    radius_mm = diameter_mm / 2.0 # 13.5 mm
    scale = img_size / diameter_mm # 40.0 px/mm
    cx = img_size / 2.0
    cy = img_size / 2.0
    
    print(f"[Coin27mm] Generating optimized {img_size}x{img_size} circular coin...")
    
    # Grid coordinates
    y_idx, x_idx = np.ogrid[:img_size, :img_size]
    x_mm = (x_idx - cx) / scale
    y_mm = (cy - y_idx) / scale # Invert Y so up is positive
    r_mm = np.sqrt(x_mm**2 + y_mm**2)
    theta = np.arctan2(y_mm, x_mm)
    
    # Z array: 0.0 mm = top unengraved surface (rim, crests)
    # -max_depth_mm = deepest background floor (-0.75 mm)
    z_mm = np.full((img_size, img_size), -max_depth_mm, dtype=np.float32)
    
    # 1. OUTSIDE CIRCLE: Clean Cutout Plane (-max_depth_mm)
    outside_circle = r_mm > radius_mm
    z_mm[outside_circle] = -max_depth_mm
    
    # 2. RAISED OUTER PROTECTIVE RIM (0.00 mm Depth)
    # Rim outer: 13.5 mm, inner flat: 12.6 mm
    rim_flat = (r_mm >= 12.60) & (r_mm <= radius_mm)
    z_mm[rim_flat] = 0.0
    
    # Rim slope (chamfer down to base field)
    rim_slope = (r_mm >= 12.15) & (r_mm < 12.60)
    t_slope = (r_mm[rim_slope] - 12.15) / (12.60 - 12.15)
    z_mm[rim_slope] = -0.65 + 0.65 * (t_slope**1.4)
    
    # Base field background floor: -0.65 mm
    field = r_mm < 12.15
    z_mm[field] = -0.65
    
    # 3. BEADED DENTICLE RING: 60 Spherical Domed Mint Beads at R = 11.70 mm
    num_beads = 60
    bead_r = 11.70
    b_rad = 0.28 # mm radius
    for b in range(num_beads):
        b_ang = b * 2.0 * math.pi / float(num_beads)
        bx = bead_r * math.cos(b_ang)
        by = bead_r * math.sin(b_ang)
        d_bead = np.sqrt((x_mm - bx)**2 + (y_mm - by)**2)
        b_mask = d_bead <= b_rad
        if np.any(b_mask):
            dome = np.sqrt(np.maximum(0.0, 1.0 - (d_bead[b_mask] / b_rad)**2))
            bead_z = -0.60 + 0.42 * dome # Peak at -0.18 mm
            z_mm[b_mask] = np.maximum(z_mm[b_mask], bead_z)
            
    # 4. BI-METALLIC TRENCH at R = 8.85 mm to 9.15 mm
    trench = (r_mm >= 8.85) & (r_mm <= 9.15)
    trench_depth = np.cos((r_mm[trench] - 9.0) / 0.15 * (math.pi / 2.0))
    z_mm[trench] = np.minimum(z_mm[trench], -0.65 - 0.08 * trench_depth)
    
    # 5. SUNBURST GUILLOCHÉ BACKGROUND IN INNER CORE
    core_mask = (r_mm < 8.80) & (r_mm > 0.8)
    sunburst = np.sin(theta[core_mask] * 48.0) * 0.030 # +/- 30 um
    z_mm[core_mask] += sunburst
    
    # 6. SYMMETRICAL WHEAT / LAUREL LEAVES
    def add_leaf(lx, ly, l_len, l_wid, l_rot, peak_z):
        cos_a = math.cos(l_rot)
        sin_a = math.sin(l_rot)
        dx = x_mm - lx
        dy = y_mm - ly
        u = dx * cos_a + dy * sin_a
        v = -dx * sin_a + dy * cos_a
        mask = (u >= -l_len/2.0) & (u <= l_len/2.0) & (np.abs(v) <= l_wid/2.0)
        norm_dist = (u[mask] / (l_len/2.0))**2 + (v[mask] / (l_wid/2.0))**2
        inside = norm_dist <= 1.0
        if np.any(inside):
            sub = np.zeros_like(mask)
            sub[mask] = inside
            dome = np.sqrt(np.maximum(0.0, 1.0 - norm_dist[inside]))
            leaf_z = -0.58 + (peak_z + 0.58) * dome
            z_mm[sub] = np.maximum(z_mm[sub], leaf_z)

    # 8 leaves each side
    for i in range(8):
        ang_deg = 120.0 + i * 16.0
        ang_rad = math.radians(ang_deg)
        lr = 6.9
        add_leaf(lr * math.cos(ang_rad), lr * math.sin(ang_rad), 1.5, 0.75, ang_rad + math.pi/4.0, -0.15)
        
        # Right mirror
        ang_deg_r = 60.0 - i * 16.0
        ang_rad_r = math.radians(ang_deg_r)
        add_leaf(lr * math.cos(ang_rad_r), lr * math.sin(ang_rad_r), 1.5, 0.75, ang_rad_r - math.pi/4.0, -0.15)

    # 7. BEVELED TYPOGRAPHY & SYMBOLS
    def add_beveled_shape(pts_mm, top_z=-0.04, base_z=-0.50, max_dist=0.30):
        pts_px = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in pts_mm], dtype=np.int32)
        poly_m = np.zeros((img_size, img_size), dtype=np.uint8)
        cv2.fillPoly(poly_m, [pts_px], 255)
        dist = cv2.distanceTransform(poly_m, cv2.DIST_L2, 5) / scale
        bevel = np.clip(dist / max_dist, 0.0, 1.0)
        z_val = base_z + (top_z - base_z) * (bevel**0.75)
        active = poly_m > 0
        z_mm[active] = np.maximum(z_mm[active], z_val[active])

    # Rupee Symbol '₹'
    add_beveled_shape([(-2.3, 4.6), (2.3, 4.6), (2.3, 4.0), (-2.3, 4.0)], top_z=-0.05)
    add_beveled_shape([(-2.3, 3.6), (1.7, 3.6), (1.7, 3.0), (-2.3, 3.0)], top_z=-0.05)
    add_beveled_shape([(-1.4, 4.6), (-0.8, 4.6), (-0.8, 1.8), (-1.4, 1.8)], top_z=-0.05)
    # Loop
    loop_pts = []
    for a in range(-90, 91, 15):
        rad = math.radians(a)
        loop_pts.append((-0.8 + 1.3 * math.cos(rad), 3.3 + 0.75 * math.sin(rad)))
    for a in range(90, -91, -15):
        rad = math.radians(a)
        loop_pts.append((-0.8 + 0.8 * math.cos(rad), 3.3 + 0.40 * math.sin(rad)))
    add_beveled_shape(loop_pts, top_z=-0.05)
    add_beveled_shape([(-0.8, 2.5), (1.8, 0.9), (1.2, 0.9), (-1.4, 2.3)], top_z=-0.05)

    # Denomination '10'
    d1_pts = [
        (-2.6, -1.0), (-1.7, -0.4), (-1.1, -0.4), (-1.1, -4.5),
        (-0.5, -4.5), (-0.5, -5.1), (-2.9, -5.1), (-2.9, -4.5),
        (-2.0, -4.5), (-2.0, -1.0)
    ]
    add_beveled_shape(d1_pts, top_z=-0.03)

    # Digit '0'
    d0_outer = [(1.7 + 1.5 * math.cos(math.radians(a)), -2.8 + 2.3 * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    d0_inner = [(1.7 + 0.75 * math.cos(math.radians(a)), -2.8 + 1.45 * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    pts_px0 = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in d0_outer], dtype=np.int32)
    poly_m0 = np.zeros((img_size, img_size), dtype=np.uint8)
    cv2.fillPoly(poly_m0, [pts_px0], 255)
    inner_px0 = np.array([[int(round(cx + p[0]*scale)), int(round(cy - p[1]*scale))] for p in d0_inner], dtype=np.int32)
    cv2.fillPoly(poly_m0, [inner_px0], 0)
    dist0 = cv2.distanceTransform(poly_m0, cv2.DIST_L2, 5) / scale
    z_d0 = -0.50 + 0.47 * np.clip(dist0 / 0.35, 0.0, 1.0)**0.75
    active0 = poly_m0 > 0
    z_mm[active0] = np.maximum(z_mm[active0], z_d0[active0])

    # Arc text: "INDIA BHARAT" & "2026 TEN RUPEES"
    text_img = np.zeros((img_size, img_size), dtype=np.uint8)
    for idx_c, char in enumerate("INDIA  BHARAT"):
        if char == ' ': continue
        t = idx_c / 12.0
        ang = math.radians(145.0 + t * (35.0 - 145.0))
        tx = 10.35 * math.cos(ang)
        ty = 10.35 * math.sin(ang)
        px = int(round(cx + tx * scale))
        py = int(round(cy - ty * scale))
        cv2.putText(text_img, char, (px - 10, py + 10), cv2.FONT_HERSHEY_DUPLEX, 0.65, 255, 2, cv2.LINE_AA)

    for idx_c, char in enumerate("2026  TEN RUPEES"):
        if char == ' ': continue
        t = idx_c / 15.0
        ang = math.radians(215.0 + t * (325.0 - 215.0))
        tx = 10.35 * math.cos(ang)
        ty = 10.35 * math.sin(ang)
        px = int(round(cx + tx * scale))
        py = int(round(cy - ty * scale))
        cv2.putText(text_img, char, (px - 9, py + 9), cv2.FONT_HERSHEY_DUPLEX, 0.58, 255, 2, cv2.LINE_AA)

    dist_txt = cv2.distanceTransform(text_img, cv2.DIST_L2, 5) / scale
    z_txt = -0.52 + 0.46 * np.clip(dist_txt / 0.16, 0.0, 1.0)
    active_txt = text_img > 0
    z_mm[active_txt] = np.maximum(z_mm[active_txt], z_txt[active_txt])

    # Noida Mintmark Diamond
    add_beveled_shape([(0.0, -5.7), (0.40, -6.1), (0.0, -6.5), (-0.40, -6.1)], top_z=-0.05)

    # STRICT CIRCLE BOUNDARY CUTOFF
    z_mm[outside_circle] = -max_depth_mm

    # -------------------------------------------------------------------------
    # NORMALIZE & EXPORT COMPACT PNGs
    # -------------------------------------------------------------------------
    norm_z = (z_mm - (-max_depth_mm)) / max_depth_mm
    norm_z = np.clip(norm_z, 0.0, 1.0)

    # 1. 16-Bit Grayscale PNG (Compact & Light, compression level 9)
    hmap_16 = (norm_z * 65535.0).astype(np.uint16)
    hmap_16 = cv2.GaussianBlur(hmap_16, (3, 3), 0.5)
    
    path_16bit = os.path.join(output_dir, "rupee_10_coin_27mm_relief_16bit.png")
    cv2.imwrite(path_16bit, hmap_16, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    sz_16 = os.path.getsize(path_16bit) / 1024.0
    print(f"[Coin27mm] Saved Compact 16-Bit Heightmap: {path_16bit} ({sz_16:.1f} KB)")

    # 2. 8-Bit Grayscale PNG (Super light ~100 KB, universally compatible)
    hmap_8 = (norm_z * 255.0).astype(np.uint8)
    path_8bit = os.path.join(output_dir, "rupee_10_coin_27mm_relief_8bit.png")
    cv2.imwrite(path_8bit, hmap_8, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    sz_8 = os.path.getsize(path_8bit) / 1024.0
    print(f"[Coin27mm] Saved Compact 8-Bit Heightmap: {path_8bit} ({sz_8:.1f} KB)")

    # 3. Photorealistic Brass Studio Lighting Render
    dx = cv2.Sobel(norm_z, cv2.CV_32F, 1, 0, ksize=3)
    dy = cv2.Sobel(norm_z, cv2.CV_32F, 0, 1, ksize=3)
    norm = np.sqrt(dx**2 + dy**2 + 1.0)
    shade = np.clip((-dx * -0.5 - dy * 0.5 + 0.707) / norm, 0.0, 1.0)
    
    brass_bgr = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    brass_bgr[:, :, 0] = (shade * 35 + norm_z * 25).astype(np.uint8)  # Blue
    brass_bgr[:, :, 1] = (shade * 175 + norm_z * 45).astype(np.uint8) # Green
    brass_bgr[:, :, 2] = (shade * 225 + norm_z * 30).astype(np.uint8) # Red
    brass_bgr[outside_circle] = [18, 18, 18]
    
    path_render = os.path.join(output_dir, "rupee_10_coin_27mm_brass_render.png")
    cv2.imwrite(path_render, brass_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    sz_render = os.path.getsize(path_render) / 1024.0
    print(f"[Coin27mm] Saved Studio Render: {path_render} ({sz_render:.1f} KB)")

    # 4. Generate matching true 1:1 DXF (27.0 mm diameter)
    generate_matching_dxf(output_dir, diameter_mm, radius_mm, num_beads, bead_r, b_rad)
    
    return path_16bit, path_8bit, path_render

def generate_matching_dxf(output_dir, diameter_mm, radius_mm, num_beads, bead_r, b_rad):
    dxf_path = os.path.join(output_dir, "rupee_10_coin_27mm_relief.dxf")
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    # Setup layers
    for lyr, col in [("00_RIM", 7), ("01_BEADS", 5), ("02_GROOVE", 4), ("03_LEAVES", 3), ("04_DENOM", 2), ("05_RUPEE", 1)]:
        doc.layers.add(name=lyr, color=col)
        
    # Rim & Boundary
    msp.add_circle((0, 0), radius_mm, dxfattribs={"layer": "00_RIM"})
    msp.add_circle((0, 0), 12.60, dxfattribs={"layer": "00_RIM"})
    msp.add_circle((0, 0), 12.15, dxfattribs={"layer": "00_RIM"})
    
    # Beads
    for b in range(num_beads):
        ang = b * 2.0 * math.pi / float(num_beads)
        msp.add_circle((bead_r * math.cos(ang), bead_r * math.sin(ang)), b_rad, dxfattribs={"layer": "01_BEADS"})
        
    # Groove
    msp.add_circle((0, 0), 9.15, dxfattribs={"layer": "02_GROOVE"})
    msp.add_circle((0, 0), 8.85, dxfattribs={"layer": "02_GROOVE"})
    
    doc.saveas(dxf_path)
    print(f"[Coin27mm] Saved Matching 27mm DXF: {dxf_path} ({os.path.getsize(dxf_path)/1024.0:.1f} KB)")

if __name__ == "__main__":
    out_dir = r"d:\Atharva\Galvo_Scribber\Galvo_UI_2\DeepEngrave"
    generate_compact_27mm_coin(out_dir, diameter_mm=27.0, thickness_mm=1.8, max_depth_mm=0.75, resolution_px=1080)
