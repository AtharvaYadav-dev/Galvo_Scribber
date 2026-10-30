import os

bridge_path = r"bridges/cad_bridge.py"
with open(bridge_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """            else:
                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 1
                mod_w = out_w / float(cols)
                mod_h = out_h / float(rows)
                for r in range(rows):
                    c = 0
                    while c < cols:
                        if grid[r][c]:
                            start_c = c
                            while c < cols and grid[r][c]:
                                c += 1
                            run_len = c - start_c
                            lx0 = round(-out_w / 2.0 + start_c * mod_w, 3)
                            lx1 = round(-out_w / 2.0 + (start_c + run_len) * mod_w, 3)
                            ly0 = round(out_h / 2.0 - (r + 1) * mod_h, 3)
                            ly1 = round(out_h / 2.0 - r * mod_h, 3)

                            rects.append({
                                "x": lx0,
                                "y": ly1,
                                "w": round(lx1 - lx0, 3),
                                "h": round(ly1 - ly0, 3)
                            })
                            paths.append([
                                [lx0, ly0], [lx1, ly0],
                                [lx1, ly1], [lx0, ly1], [lx0, ly0]
                            ])
                        else:
                            c += 1

        return {
            "success": True,
            "type": code_type,
            "text": content,
            "wMm": out_w,
            "hMm": out_h,
            "rects": rects,
            "paths": paths
        }"""

replacement_str = """            else:
                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 1
                mod_w = out_w / float(cols)
                mod_h = out_h / float(rows)

                # 2D maximal greedy rectangle merging (merges contiguous horizontal and vertical module blocks)
                visited = [[False] * cols for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] and not visited[r][c]:
                            # Find contiguous span along row r
                            w_span = 0
                            while c + w_span < cols and grid[r][c + w_span] and not visited[r][c + w_span]:
                                w_span += 1
                            # Expand vertically while all columns in span are unvisited and solid
                            h_span = 1
                            while r + h_span < rows:
                                if all(grid[r + h_span][c + i] and not visited[r + h_span][c + i] for i in range(w_span)):
                                    h_span += 1
                                else:
                                    break
                            # Mark cells as visited
                            for dr in range(h_span):
                                for dc in range(w_span):
                                    visited[r + dr][c + dc] = True

                            lx0 = round(-out_w / 2.0 + c * mod_w, 3)
                            lx1 = round(-out_w / 2.0 + (c + w_span) * mod_w, 3)
                            ly0 = round(out_h / 2.0 - (r + h_span) * mod_h, 3)
                            ly1 = round(out_h / 2.0 - r * mod_h, 3)

                            rects.append({
                                "x": lx0,
                                "y": ly1,
                                "w": round(lx1 - lx0, 3),
                                "h": round(ly1 - ly0, 3)
                            })
                            paths.append([
                                [lx0, ly0], [lx1, ly0],
                                [lx1, ly1], [lx0, ly1], [lx0, ly0]
                            ])

        return {
            "success": True,
            "type": code_type,
            "text": content,
            "wMm": out_w,
            "hMm": out_h,
            "rects": rects,
            "paths": paths
        }

    @Slot("QVariantMap", str, result="QVariantMap")
    @Slot("QVariantMap", str, str, result="QVariantMap")
    def exportBarcodeFile(self, shape_dict: dict, format_ext: str, target_path: str = "") -> dict:
        \"\"\"
        Exports a 2D QR Code, 1D Code 128, or DataMatrix entity to DXF, SVG, or PNG format.
        If target_path is omitted or empty, prompts user with a native QFileDialog.
        \"\"\"
        try:
            from PySide6.QtWidgets import QFileDialog
            import re

            format_ext = str(format_ext).strip().lower()
            if format_ext not in ["dxf", "svg", "png"]:
                format_ext = "dxf"

            code_type = str(shape_dict.get("type", "qrcode"))
            text_content = str(shape_dict.get("text", "12345"))
            size_mm = float(shape_dict.get("wMm", 20.0))

            # Ensure we have up-to-date geometry
            rects = shape_dict.get("rects")
            paths = shape_dict.get("paths")
            w_mm = float(shape_dict.get("wMm", size_mm))
            h_mm = float(shape_dict.get("hMm", size_mm))

            if not rects or not paths:
                gen_data = self.generateBarcodeEntity(code_type, text_content, size_mm)
                rects = gen_data.get("rects", [])
                paths = gen_data.get("paths", [])
                w_mm = gen_data.get("wMm", w_mm)
                h_mm = gen_data.get("hMm", h_mm)

            # Determine default save folder
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "QR", "Barcode DXF")
            os.makedirs(save_dir, exist_ok=True)

            shp_name = str(shape_dict.get("name") or code_type or "Barcode")
            clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', shp_name)
            default_target = os.path.join(save_dir, f"{clean_name}.{format_ext}")

            if not target_path:
                filters = {
                    "dxf": "DXF Vector CAD File (*.dxf)",
                    "svg": "SVG Scalable Vector Graphics (*.svg)",
                    "png": "PNG High-Resolution Image (*.png)"
                }
                filter_str = f"{filters.get(format_ext, 'All Files (*)')};;All Files (*)"
                chosen, _ = QFileDialog.getSaveFileName(
                    None,
                    f"Export {format_ext.upper()} Code - {shp_name}",
                    default_target,
                    filter_str
                )
                if not chosen:
                    return {"success": False, "cancelled": True}
                target_path = chosen

            if not target_path.lower().endswith(f".{format_ext}"):
                target_path += f".{format_ext}"

            # 1. DXF Vector CAD Export
            if format_ext == "dxf":
                import ezdxf
                doc = ezdxf.new("R2010")
                msp = doc.modelspace()
                for rc in rects:
                    x0 = float(rc["x"])
                    y0 = float(rc["y"]) - float(rc["h"])
                    x1 = float(rc["x"]) + float(rc["w"])
                    y1 = float(rc["y"])
                    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True)

                if bool(shape_dict.get("hatched")) and shape_dict.get("hatch_lines"):
                    h_layer = doc.layers.add("HATCH")
                    h_layer.color = 1
                    for hl in shape_dict["hatch_lines"]:
                        pts = hl.get("points", [])
                        for i in range(len(pts) - 1):
                            msp.add_line(pts[i], pts[i+1], dxfattribs={"layer": "HATCH"})

                doc.saveas(target_path)

            # 2. SVG Scalable Vector Graphics Export
            elif format_ext == "svg":
                min_x = round(-w_mm / 2.0, 3)
                min_y = round(-h_mm / 2.0, 3)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\\n')
                    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {w_mm} {h_mm}" width="{w_mm}mm" height="{h_mm}mm">\\n')
                    f.write(f'  <rect x="{min_x}" y="{min_y}" width="{w_mm}" height="{h_mm}" fill="white"/>\\n')
                    f.write('  <g fill="black">\\n')
                    for rc in rects:
                        rx = float(rc["x"])
                        ry = -float(rc["y"])
                        rw = float(rc["w"])
                        rh = float(rc["h"])
                        f.write(f'    <rect x="{rx:.3f}" y="{ry:.3f}" width="{rw:.3f}" height="{rh:.3f}"/>\\n')
                    f.write('  </g>\\n</svg>\\n')

            # 3. PNG High-Resolution Scannable Raster Image
            elif format_ext == "png":
                from PySide6.QtGui import QImage, QPainter, QColor
                from PySide6.QtCore import QRectF

                px_w = 1200
                px_h = max(300, int(round(1200 * (h_mm / max(1.0, w_mm)))))
                scale_px = px_w / max(1.0, w_mm)

                img = QImage(px_w, px_h, QImage.Format_ARGB32)
                img.fill(QColor("white"))
                p = QPainter(img)
                p.translate(px_w / 2.0, px_h / 2.0)
                for rc in rects:
                    rx = float(rc["x"]) * scale_px
                    ry = -float(rc["y"]) * scale_px
                    rw = float(rc["w"]) * scale_px
                    rh = float(rc["h"]) * scale_px
                    p.fillRect(QRectF(rx, ry, rw + 0.5, rh + 0.5), QColor("#0A0F1D"))
                p.end()
                img.save(target_path)

            self._set_status(f"Exported {format_ext.upper()} to: {os.path.basename(target_path)}")
            return {"success": True, "filePath": target_path, "format": format_ext}

        except Exception as exp_err:
            print(f"[CadBridge] exportBarcodeFile error: {exp_err}")
            self._set_status(f"Export failed: {str(exp_err)}")
            return {"success": False, "error": str(exp_err)}"""

# Normalize newlines for replacement
content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(bridge_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched cad_bridge.py")
else:
    print("Error: target_norm not found in cad_bridge.py")

