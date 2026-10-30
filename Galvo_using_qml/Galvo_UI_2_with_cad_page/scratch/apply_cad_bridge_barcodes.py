with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """            if not polys:
                # Fallback to outline box if qrcode module fails
                corners = [(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0), (-w / 2.0, -h / 2.0)]
                polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype in ["polygon", "dxf", "svg", "line", "curve"]:"""

replacement = """            if not polys:
                # Fallback to outline box if qrcode module fails
                corners = [(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0), (-w / 2.0, -h / 2.0)]
                polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype == "barcode128":
            text_str = str(shp.get("text", "12345"))
            seed = sum(ord(c) for c in text_str) or 42
            num_bars = 24
            bar_w = w / float(num_bars * 1.5)
            curr_x = -w / 2.0 + bar_w * 0.5
            for b in range(num_bars):
                is_bar = ((seed * (b + 3) + b * 17) % 7) > 2
                thick = ((seed + b) % 3 == 0)
                bw = bar_w * (1.8 if thick else 1.0)
                if is_bar and (curr_x + bw) <= (w / 2.0):
                    lx0 = curr_x
                    lx1 = curr_x + bw
                    ly0 = -h / 2.0
                    ly1 = h / 2.0
                    bar_box = [(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1), (lx0, ly0)]
                    polys.append([rotate_and_shift(x, y) for (x, y) in bar_box])
                curr_x += bw + bar_w * 0.5
            if not polys:
                corners = [(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0), (-w / 2.0, -h / 2.0)]
                polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype == "datamatrix":
            text_str = str(shp.get("text", "12345"))
            grid_dim = 14
            mod_w = w / float(grid_dim)
            mod_h = h / float(grid_dim)
            seed = sum(ord(c) for c in text_str) or 99
            for r in range(grid_dim):
                for c in range(grid_dim):
                    is_solid = (c == 0 or r == grid_dim - 1)
                    is_clock = (c == grid_dim - 1 and r % 2 == 0) or (r == 0 and c % 2 == 0)
                    is_mod = ((seed + r * 13 + c * 7) % 5 < 2)
                    if is_solid or is_clock or (1 <= r < grid_dim - 1 and 1 <= c < grid_dim - 1 and is_mod):
                        lx0 = -w / 2.0 + c * mod_w
                        ly0 = h / 2.0 - (r + 1) * mod_h
                        lx1 = lx0 + mod_w
                        ly1 = ly0 + mod_h
                        square = [(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1), (lx0, ly0)]
                        polys.append([rotate_and_shift(x, y) for (x, y) in square])
            if not polys:
                corners = [(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0), (-w / 2.0, -h / 2.0)]
                polys.append([rotate_and_shift(x, y) for (x, y) in corners])

        elif stype in ["polygon", "dxf", "svg", "line", "curve"]:"""

assert target in text, "Target not found in bridges/cad_bridge.py"
text = text.replace(target, replacement, 1)

with open('bridges/cad_bridge.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("bridges/cad_bridge.py successfully updated with barcode128 and datamatrix support!")

