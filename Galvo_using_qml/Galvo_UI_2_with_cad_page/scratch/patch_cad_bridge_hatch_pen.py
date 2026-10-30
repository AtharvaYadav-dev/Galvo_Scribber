with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_hatch_loop = """            all_lines = []
            for cfg in active_cfgs:
                segs = compute_hatch_geometry(polys, cfg, galvo_units_per_mm=1.0)
                pen_id = cfg.get("pen_no", 0)
                for s in segs:
                    if len(s) >= 2:
                        all_lines.append({
                            "pen_id": pen_id,
                            "points": [[float(pt[0]), float(pt[1])] for pt in s]
                        })"""

new_hatch_loop = """            all_lines = []
            for cfg in active_cfgs:
                segs = compute_hatch_geometry(polys, cfg, galvo_units_per_mm=1.0)
                pen_id = int(cfg.get("pen_no", 0) or 0)
                if pen_id == 0 and int(shp.get("penId", 0) or 0) > 0:
                    pen_id = int(shp.get("penId", 0))
                for s in segs:
                    if len(s) >= 2:
                        all_lines.append({
                            "pen_id": pen_id,
                            "points": [[float(pt[0]), float(pt[1])] for pt in s]
                        })"""

if old_hatch_loop in content:
    content = content.replace(old_hatch_loop, new_hatch_loop, 1)
    with open('bridges/cad_bridge.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated computeHatchPreviewLines in bridges/cad_bridge.py")
else:
    print("WARNING: old_hatch_loop not found")

