import os

cad_bridge_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\bridges\cad_bridge.py"
with open(cad_bridge_path, "r", encoding="utf-8") as f:
    text = f.read().replace("\r\n", "\n")

target = """                hatch_configs = []
                shape_profiles = shp.get("hatch_profiles")
                profiles_source = shape_profiles if (isinstance(shape_profiles, dict) and len(shape_profiles) > 0) else self._hatch_profiles

                for k in [1, 2, 3]:
                    p = profiles_source.get(k) or profiles_source.get(str(k))
                    if p and p.get("enable", False):
                        hatch_configs.append({
                            'enable': True,
                            'follow_edge': p.get("follow_edge", False),
                            'all_calc': p.get("all_calc", False),
                            'cross_hatch': p.get("cross_hatch", False),
                            'type': p.get("type", "Bidirectional"),
                            'angle': float(p.get("angle", 0.0) or 0.0),
                            'pen_no': int(p.get("pen_no", 0) or 0),"""

replacement = """                hatch_configs = []
                shape_pen = int(shp.get("penId", 0) or 0)
                shape_profiles = shp.get("hatch_profiles")
                has_custom_hatch = isinstance(shape_profiles, dict) and len(shape_profiles) > 0
                profiles_source = shape_profiles if has_custom_hatch else self._hatch_profiles

                for k in [1, 2, 3]:
                    p = profiles_source.get(k) or profiles_source.get(str(k))
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

if target in text:
    text = text.replace(target, replacement, 1)
    with open(cad_bridge_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully patched generateGalvoQueue hatch!")
else:
    print("Target not found!")

