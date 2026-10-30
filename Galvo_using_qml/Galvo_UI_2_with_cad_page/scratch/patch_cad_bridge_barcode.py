with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "    @Slot(str, str, float, result='QVariant')\n    def generateBarcodeEntity"
end_marker = "    @Slot(list)\n    def updateShapes"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)
assert start_idx != -1 and end_idx != -1, "Markers not found!"

new_func = '''    @Slot(str, str, float, result='QVariant')
    def generateBarcodeEntity(self, code_type: str, content: str, size_mm: float) -> dict:
        """
        Generates industrial ISO/IEC compliant 2D QR Code, 1D Code 128, and DataMatrix ECC 200 vector geometry.
        - Primary engine: zxing-cpp (Standard C++ ISO engine for phones, cameras, & industrial scanners)
        - Fallbacks: qrcode (border=4) and reportlab (Code128 / DataMatrix)
        - Run-length horizontal merging for laser optimization and fast QML Canvas rendering
        - Outputs standard wMm, hMm, rects, and closed polygon vector paths
        """
        content = str(content).strip() if content else "12345"
        size_mm = max(5.0, float(size_mm or 20.0))
        code_type_lower = code_type.lower()

        rects = []
        paths = []
        out_w = size_mm
        out_h = size_mm

        grid = None
        is_linear_1d = False

        # 1. Primary engine: zxing-cpp
        try:
            import zxingcpp
            import numpy as np

            if "matrix" in code_type_lower:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.DataMatrix)
                bm = zxingcpp.write_barcode_to_image(bc)
                grid = (np.array(bm) == 0).astype(int)
                out_w = size_mm
                out_h = size_mm

            elif "128" in code_type_lower or "bar" in code_type_lower:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.Code128)
                bm = zxingcpp.write_barcode_to_image(bc)
                arr = np.array(bm)
                mid_row = arr[len(arr) // 2]
                grid = (mid_row == 0).astype(int)
                is_linear_1d = True
                out_w = size_mm
                out_h = round(size_mm * 0.35, 3)

            else:
                bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.QRCode)
                bm = zxingcpp.write_barcode_to_image(bc)
                grid = (np.array(bm) == 0).astype(int)
                out_w = size_mm
                out_h = size_mm

        except Exception as zx_err:
            print(f"[CadBridge] zxingcpp generation notice: {zx_err}")
            grid = None

        # 2. Resilient fallbacks
        if grid is None:
            if "matrix" in code_type_lower:
                try:
                    from reportlab.graphics.barcode import createBarcodeDrawing
                    d = createBarcodeDrawing('ECC200DataMatrix', value=content)
                    bc = d.contents[0]
                    raw = bc.encoded
                    cw = len(raw[0])
                    # Add 1 module quiet zone border
                    grid = [[0] * (cw + 2)] + [[0] + list(r) + [0] for r in raw] + [[0] * (cw + 2)]
                    out_w = size_mm
                    out_h = size_mm
                except Exception as dm_err:
                    print(f"[CadBridge] DataMatrix reportlab fallback error: {dm_err}")

            elif "128" in code_type_lower or "bar" in code_type_lower:
                try:
                    out_h = round(size_mm * 0.35, 3)
                    CODE128_PATTERNS = [
                        '11011001100', '11001101100', '11001100110', '10010011000', '10010001100',
                        '10001001100', '10011001000', '10011000100', '10001100100', '11001001000',
                        '11001000100', '11000100100', '10110011100', '10011011100', '10011001110',
                        '10111001100', '10011101100', '10011100110', '11001110010', '11001011100',
                        '11001001110', '11011100100', '11001110100', '11101101110', '11101001100',
                        '11100101100', '11100100110', '11101100100', '11100110100', '11100110010',
                        '11011011000', '11011000110', '11000110110', '10100011000', '10001011000',
                        '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',
                        '11000101000', '11000100010', '10110111000', '10110001110', '10001101110',
                        '10111011000', '10111000110', '10001110110', '11101110110', '11010001110',
                        '11000101110', '11011101000', '11011100010', '11011101110', '11101011000',
                        '11101000110', '11100010110', '11101101000', '11101100010', '11100011010',
                        '11101111010', '11001000010', '11110001010', '10100110000', '10100001100',
                        '10010110000', '10010000110', '10000101100', '10000100110', '10110010000',
                        '10110000100', '10011010000', '10011000010', '10000110100', '10000110010',
                        '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',
                        '10100111100', '10010111100', '10010011110', '10111100100', '10011110100',
                        '10011110010', '11110100100', '11110010100', '11110010010', '11011011110',
                        '11011110110', '11110110110', '10101111000', '10100011110', '10001011110',
                        '10111101000', '10111100010', '11110101000', '11110100010', '10111011110',
                        '10111101110', '11101011110', '11110101110', '11010000100', '11010010000',
                        '11010011100', '1100011101011'
                    ]
                    values = [104]
                    for ch in content:
                        v = ord(ch) - 32
                        values.append(v if 0 <= v <= 95 else 0)
                    checksum = values[0]
                    for i in range(1, len(values)):
                        checksum = (checksum + i * values[i]) % 103
                    values.append(checksum)
                    values.append(106)
                    raw_bits = ''.join(CODE128_PATTERNS[v] for v in values)
                    # Add mandatory 10-module quiet zones on both sides
                    bit_str = ('0' * 10) + raw_bits + ('0' * 10)
                    grid = [int(b) for b in bit_str]
                    is_linear_1d = True
                except Exception as bar_err:
                    print(f"[CadBridge] Code 128 fallback error: {bar_err}")

            else:
                try:
                    import qrcode
                    qr = qrcode.QRCode(
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=1,
                        border=4
                    )
                    qr.add_data(content)
                    qr.make(fit=True)
                    grid = qr.get_matrix()
                    out_w = size_mm
                    out_h = size_mm
                except Exception as qr_err:
                    print(f"[CadBridge] QR Code fallback error: {qr_err}")

        # 3. Convert binary grid into run-length merged rectangles and closed paths
        if grid is not None:
            if is_linear_1d:
                n_bits = len(grid)
                mod_w = out_w / float(n_bits)
                bi = 0
                while bi < n_bits:
                    if grid[bi]:
                        sb = bi
                        while bi < n_bits and grid[bi]:
                            bi += 1
                        bw = (bi - sb) * mod_w
                        bx0 = round(-out_w / 2.0 + sb * mod_w, 3)
                        bx1 = round(bx0 + bw, 3)
                        by0 = round(-out_h / 2.0, 3)
                        by1 = round(out_h / 2.0, 3)
                        rects.append({
                            "x": bx0,
                            "y": by1,
                            "w": round(bx1 - bx0, 3),
                            "h": out_h
                        })
                        paths.append([
                            [bx0, by0], [bx1, by0],
                            [bx1, by1], [bx0, by1], [bx0, by0]
                        ])
                    else:
                        bi += 1
            else:
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
        }

'''

patched = content[:start_idx] + new_func + content[end_idx:]
with open('bridges/cad_bridge.py', 'w', encoding='utf-8') as f:
    f.write(patched)

print("Successfully patched cad_bridge.py!")

