import sys
sys.path.append(r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page")

from core.mk_lib.tools.jhfparser import SimplexFont, JhfPath

def render_stroke_text(text, font_size=2.5):
    font = SimplexFont('')
    path = JhfPath()
    font.render(path, text, True, font_size, 1.0, 1.0, 'start')
    strokes = []
    current_stroke = []
    for item in path.path:
        if item is None:
            if current_stroke:
                strokes.append(current_stroke)
                current_stroke = []
        elif isinstance(item, tuple):
            if len(item) == 2:
                if current_stroke:
                    strokes.append(current_stroke)
                current_stroke = [item]
            elif len(item) == 4:
                if not current_stroke:
                    current_stroke.append((item[0], item[1]))
                elif current_stroke[-1] != (item[0], item[1]):
                    strokes.append(current_stroke)
                    current_stroke = [(item[0], item[1])]
                current_stroke.append((item[2], item[3]))
    if current_stroke:
        strokes.append(current_stroke)
    return strokes

# Test rendering a sample label centered at (target_cx, target_cy) in mm space
def get_label_strokes_in_mm(text, target_cx, target_cy, font_size=2.5):
    strokes = render_stroke_text(text, font_size=font_size)
    if not strokes:
        return []
    all_pts = [pt for st in strokes for pt in st]
    min_x, max_x = min(p[0] for p in all_pts), max(p[0] for p in all_pts)
    min_y, max_y = min(p[1] for p in all_pts), max(p[1] for p in all_pts)
    local_cx = (min_x + max_x) / 2.0
    local_cy = (min_y + max_y) / 2.0
    
    transformed_strokes = []
    for st in strokes:
        t_st = [(target_cx + (px - local_cx), target_cy + (py - local_cy)) for (px, py) in st]
        transformed_strokes.append(t_st)
    return transformed_strokes

st1 = get_label_strokes_in_mm("20 kHz", -20.0, 5.0, font_size=2.5)
print("Strokes for '20 kHz':", len(st1))
pts1 = [pt for s in st1 for pt in s]
print(f"BBox: X=[{min(p[0] for p in pts1):.2f}, {max(p[0] for p in pts1):.2f}], Y=[{min(p[1] for p in pts1):.2f}, {max(p[1] for p in pts1):.2f}]")

st2 = get_label_strokes_in_mm("Laser Power (%)", 0.0, -22.0, font_size=2.8)
print("Strokes for 'Laser Power (%)':", len(st2))
pts2 = [pt for s in st2 for pt in s]
print(f"BBox: X=[{min(p[0] for p in pts2):.2f}, {max(p[0] for p in pts2):.2f}], Y=[{min(p[1] for p in pts2):.2f}, {max(p[1] for p in pts2):.2f}]")
