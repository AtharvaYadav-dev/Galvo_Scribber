import zxingcpp
import numpy as np
from PIL import Image

def generateBarcodeEntity(code_type, content, size_mm):
    content = str(content).strip() if content else "12345"
    size_mm = max(5.0, float(size_mm or 20.0))
    code_type_lower = code_type.lower()
    rects = []
    paths = []
    out_w = size_mm
    out_h = size_mm

    if "matrix" in code_type_lower:
        bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.DataMatrix)
        bm = zxingcpp.write_barcode_to_image(bc)
        grid = (np.array(bm) == 0).astype(int)
    elif "128" in code_type_lower or "bar" in code_type_lower:
        bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.Code128)
        bm = zxingcpp.write_barcode_to_image(bc)
        arr = np.array(bm)
        grid = (arr[len(arr) // 2] == 0).astype(int)
        out_h = round(size_mm * 0.35, 3)
    else:
        bc = zxingcpp.create_barcode(content, zxingcpp.BarcodeFormat.QRCode)
        bm = zxingcpp.write_barcode_to_image(bc)
        grid = (np.array(bm) == 0).astype(int)

    is_1d = (grid.ndim == 1)
    if is_1d:
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
                rects.append({"x": bx0, "y": by1, "w": round(bx1 - bx0, 3), "h": out_h})
                paths.append([[bx0, by0], [bx1, by0], [bx1, by1], [bx0, by1], [bx0, by0]])
            else:
                bi += 1
    else:
        rows = len(grid)
        cols = len(grid[0])
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
                    rects.append({"x": lx0, "y": ly1, "w": round(lx1 - lx0, 3), "h": round(ly1 - ly0, 3)})
                    paths.append([[lx0, ly0], [lx1, ly0], [lx1, ly1], [lx0, ly1], [lx0, ly0]])
                else:
                    c += 1

    return {"success": True, "type": code_type, "text": content, "wMm": out_w, "hMm": out_h, "rects": rects, "paths": paths}

def verify(code_type, content, fmt):
    res = generateBarcodeEntity(code_type, content, 30.0)
    scale = 10
    w_px = int(res['wMm'] * scale)
    h_px = int(res['hMm'] * scale)
    pad = 20
    img = np.ones((h_px + pad * 2, w_px + pad * 2), dtype=np.uint8) * 255
    cx = (w_px + pad * 2) // 2
    cy = (h_px + pad * 2) // 2

    for rc in res['rects']:
        x0 = int(round(rc['x'] * scale + cx))
        y0 = int(round(-rc['y'] * scale + cy))
        w = int(round(rc['w'] * scale))
        h = int(round(rc['h'] * scale))
        img[y0:y0+h, x0:x0+w] = 0

    read_res = zxingcpp.read_barcode(img, [fmt])
    print(f"[{code_type}] Valid: {read_res.valid}, Decoded: {read_res.text}")
    assert read_res.valid and read_res.text == content, f"Failed for {code_type}"

verify("DataMatrix", "https://google.com/matrix", zxingcpp.BarcodeFormat.DataMatrix)
verify("Code 128", "TEST123456", zxingcpp.BarcodeFormat.Code128)
verify("QR Code", "https://google.com/qr", zxingcpp.BarcodeFormat.QRCode)
print("ALL VERIFICATIONS PASSED 100%!")

