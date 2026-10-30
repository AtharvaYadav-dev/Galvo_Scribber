import math

def clip_line_liang_barsky(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    u1 = 0.0
    u2 = 1.0

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if t > u2:
                    return None
                if t > u1:
                    u1 = t
            elif p[i] > 0:
                if t < u1:
                    return None
                if t < u2:
                    u2 = t

    if u1 > u2:
        return None

    return (x1 + u1 * dx, y1 + u1 * dy, x1 + u2 * dx, y1 + u2 * dy)

def clip_polygon_to_rect(poly, xmin, xmax, ymin, ymax, tol=1e-5):
    """
    Clips a polyline against a bounding box.
    Returns a list of clipped continuous polylines.
    """
    if len(poly) < 2:
        return []
        
    result_polys = []
    current_segment = []

    for i in range(len(poly) - 1):
        x1, y1 = poly[i]
        x2, y2 = poly[i+1]
        clipped = clip_line_liang_barsky(x1, y1, x2, y2, xmin, xmax, ymin, ymax)
        if clipped is not None:
            cx1, cy1, cx2, cy2 = clipped
            if not current_segment:
                current_segment.append((cx1, cy1))
                current_segment.append((cx2, cy2))
            else:
                last_x, last_y = current_segment[-1]
                if abs(last_x - cx1) < tol and abs(last_y - cy1) < tol:
                    current_segment.append((cx2, cy2))
                else:
                    result_polys.append(current_segment)
                    current_segment = [(cx1, cy1), (cx2, cy2)]
        else:
            if current_segment:
                result_polys.append(current_segment)
                current_segment = []

    if current_segment:
        result_polys.append(current_segment)

    return result_polys

# Test with a rectangle from (-50, -50) to (50, 50) clipped into 2 horizontal halves
poly = [(-50, -50), (50, -50), (50, 50), (-50, 50), (-50, -50)]

# Tile 1: Left half (-50 to 0)
tile1_polys = clip_polygon_to_rect(poly, -50, 0, -50, 50)
print("Tile 1 clipped polys count:", len(tile1_polys))
for p in tile1_polys:
    print("  T1 poly:", p)

# Tile 2: Right half (0 to 50)
tile2_polys = clip_polygon_to_rect(poly, 0, 50, -50, 50)
print("Tile 2 clipped polys count:", len(tile2_polys))
for p in tile2_polys:
    print("  T2 poly:", p)
