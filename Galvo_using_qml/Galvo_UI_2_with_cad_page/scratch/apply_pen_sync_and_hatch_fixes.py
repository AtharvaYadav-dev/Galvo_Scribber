import os
import sys

base_dir = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page"

# 1. Patch bridges/cad_bridge.py
cad_bridge_path = os.path.join(base_dir, "bridges", "cad_bridge.py")
with open(cad_bridge_path, "r", encoding="utf-8") as f:
    cad_code = f.read()

# Replace computeHatchPreviewLines block
target_hatch_preview = """            active_cfgs = []
            shape_hatch = shp.get("hatch_profiles")
            source_profiles = shape_hatch if (isinstance(shape_hatch, dict) and len(shape_hatch) > 0) else self._hatch_profiles

            for k in [1, 2, 3]:
                p = source_profiles.get(k) or source_profiles.get(str(k))
                if p and p.get("enable", False):
                    cfg = {
                        'enable': True,
                        'follow_edge': p.get("follow_edge", False),
                        'all_calc': p.get("all_calc", False),
                        'cross_hatch': p.get("cross_hatch", False),
                        'type': p.get("type", "Bidirectional"),
                        'angle': float(p.get("angle", 0.0) or 0.0),
                        'pen_no': int(p.get("pen_no", 0) or 0),
                        'count': int(p.get("count", 1) or 1),
                        'line_space': float(p.get("line_space", 0.05) or 0.05),
                        'avg_distribute': p.get("avg_dist", False),
                        'edge_offset': float(p.get("edge_off", 0.0) or 0.0),
                        'start_offset': float(p.get("start_off", 0.0) or 0.0),
                        'end_offset': float(p.get("end_off", 0.0) or 0.0),
                        'line_reduction': float(p.get("line_red", 0.0) or 0.0),
                        'num_loops': int(p.get("num_loops", 0) or 0),
                        'loop_distance': float(p.get("loop_dist", 0.05) or 0.05),
                        'auto_rotate': p.get("auto_rot", False),
                        'rotate_angle': float(p.get("rot_angle", 10.0) or 10.0),
                        'hatch_idx': k
                    }
                    active_cfgs.append(cfg)

            if not active_cfgs and bool(shp.get("hatched", False)):
                active_cfgs.append({
                    'enable': True,
                    'follow_edge': False,
                    'all_calc': False,
                    'cross_hatch': False,
                    'type': "Bidirectional",
                    'angle': 45.0,
                    'pen_no': int(shp.get("penId", 0)),
                    'count': 1,
                    'line_space': 0.05,
                    'avg_distribute': False,
                    'edge_offset': 0.0,
                    'start_offset': 0.0,
                    'end_offset': 0.0,
                    'line_reduction': 0.0,
                    'num_loops': 0,
                    'loop_distance': 0.05,
                    'auto_rotate': False,
                    'rotate_angle': 10.0,
                    'hatch_idx': 1
                })

            if not active_cfgs:
                return []

            all_lines = []
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

replacement_hatch_preview = """            active_cfgs = []
            shape_pen = int(shp.get("penId", 0) or 0)
            shape_hatch = shp.get("hatch_profiles")
            has_custom_hatch = isinstance(shape_hatch, dict) and len(shape_hatch) > 0
            source_profiles = shape_hatch if has_custom_hatch else self._hatch_profiles

            for k in [1, 2, 3]:
                p = source_profiles.get(k) or source_profiles.get(str(k))
                if p and p.get("enable", False):
                    if has_custom_hatch and p.get("pen_no") is not None:
                        chosen_pen = int(p.get("pen_no", 0) or 0)
                    else:
                        chosen_pen = shape_pen
                    cfg = {
                        'enable': True,
                        'follow_edge': p.get("follow_edge", False),
                        'all_calc': p.get("all_calc", False),
                        'cross_hatch': p.get("cross_hatch", False),
                        'type': p.get("type", "Bidirectional"),
                        'angle': float(p.get("angle", 0.0) or 0.0),
                        'pen_no': chosen_pen,
                        'count': int(p.get("count", 1) or 1),
                        'line_space': float(p.get("line_space", 0.05) or 0.05),
                        'avg_distribute': p.get("avg_dist", False),
                        'edge_offset': float(p.get("edge_off", 0.0) or 0.0),
                        'start_offset': float(p.get("start_off", 0.0) or 0.0),
                        'end_offset': float(p.get("end_off", 0.0) or 0.0),
                        'line_reduction': float(p.get("line_red", 0.0) or 0.0),
                        'num_loops': int(p.get("num_loops", 0) or 0),
                        'loop_distance': float(p.get("loop_dist", 0.05) or 0.05),
                        'auto_rotate': p.get("auto_rot", False),
                        'rotate_angle': float(p.get("rot_angle", 10.0) or 10.0),
                        'hatch_idx': k
                    }
                    active_cfgs.append(cfg)

            if not active_cfgs and bool(shp.get("hatched", False)):
                active_cfgs.append({
                    'enable': True,
                    'follow_edge': False,
                    'all_calc': False,
                    'cross_hatch': False,
                    'type': "Bidirectional",
                    'angle': 45.0,
                    'pen_no': shape_pen,
                    'count': 1,
                    'line_space': 0.05,
                    'avg_distribute': False,
                    'edge_offset': 0.0,
                    'start_offset': 0.0,
                    'end_offset': 0.0,
                    'line_reduction': 0.0,
                    'num_loops': 0,
                    'loop_distance': 0.05,
                    'auto_rotate': False,
                    'rotate_angle': 10.0,
                    'hatch_idx': 1
                })

            if not active_cfgs:
                return []

            all_lines = []
            for cfg in active_cfgs:
                segs = compute_hatch_geometry(polys, cfg, galvo_units_per_mm=1.0)
                pen_id = int(cfg.get("pen_no", shape_pen))
                for s in segs:
                    if len(s) >= 2:
                        all_lines.append({
                            "pen_id": pen_id,
                            "points": [[float(pt[0]), float(pt[1])] for pt in s]
                        })"""

# Normalize line endings for replacement
norm_cad = cad_code.replace("\r\n", "\n")
norm_target = target_hatch_preview.replace("\r\n", "\n")
norm_repl = replacement_hatch_preview.replace("\r\n", "\n")

if norm_target in norm_cad:
    norm_cad = norm_cad.replace(norm_target, norm_repl, 1)
    print("Successfully patched computeHatchPreviewLines in cad_bridge.py")
else:
    print("WARNING: target_hatch_preview not found in cad_bridge.py")

# Also check generateGalvoQueue hatch pen assignment around line 1500
target_queue_hatch = """                    for k in [1, 2, 3]:
                        p = source_profiles.get(k) or source_profiles.get(str(k))
                        if p and p.get("enable", False):
                            hatch_configs.append({
                                'enable': True,
                                'follow_edge': p.get("follow_edge", False),
                                'all_calc': p.get("all_calc", False),
                                'cross_hatch': p.get("cross_hatch", False),
                                'type': p.get("type", "Bidirectional"),
                                'angle': float(p.get("angle", 0.0) or 0.0),
                                'pen_no': int(p.get("pen_no", 0) or 0),"""

repl_queue_hatch = """                    shape_pen = int(shp.get("penId", 0) or 0)
                    has_custom_hatch = isinstance(shape_hatch, dict) and len(shape_hatch) > 0
                    for k in [1, 2, 3]:
                        p = source_profiles.get(k) or source_profiles.get(str(k))
                        if p and p.get("enable", False):
                            chosen_pen = int(p.get("pen_no", 0) or 0) if (has_custom_hatch and p.get("pen_no") is not None) else shape_pen
                            hatch_configs.append({
                                'enable': True,
                                'follow_edge': p.get("follow_edge", False),
                                'all_calc': p.get("all_calc", False),
                                'cross_hatch': p.get("cross_hatch", False),
                                'type': p.get("type", "Bidirectional"),
                                'angle': float(p.get("angle", 0.0) or 0.0),
                                'pen_no': chosen_pen,"""

if target_queue_hatch in norm_cad:
    norm_cad = norm_cad.replace(target_queue_hatch, repl_queue_hatch, 1)
    print("Successfully patched generateGalvoQueue in cad_bridge.py")
else:
    print("WARNING: target_queue_hatch not found in cad_bridge.py")

with open(cad_bridge_path, "w", encoding="utf-8") as f:
    f.write(norm_cad)

print("Done patching cad_bridge.py")

