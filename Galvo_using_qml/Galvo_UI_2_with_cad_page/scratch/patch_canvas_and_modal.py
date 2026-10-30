import os

# 1. Patch CadCanvas.qml
canvas_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    canvas_text = f.read().replace("\r\n", "\n")

target_canvas = """                            var hline = shp.hatch_lines[hl]
                            var hPenCol = (hline.pen_id !== undefined && hline.pen_id > 0)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor"""

replacement_canvas = """                            var hline = shp.hatch_lines[hl]
                            var hPenCol = (hline.pen_id !== undefined)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor"""

if target_canvas in canvas_text:
    canvas_text = canvas_text.replace(target_canvas, replacement_canvas, 1)
    with open(canvas_path, "w", encoding="utf-8") as f:
        f.write(canvas_text)
    print("Successfully patched CadCanvas.qml!")
else:
    print("WARNING: target_canvas not found in CadCanvas.qml")

# 2. Patch CadHatchModal.qml
modal_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadHatchModal.qml"
with open(modal_path, "r", encoding="utf-8") as f:
    modal_text = f.read().replace("\r\n", "\n")

target_open_modal = """        if (shp && shp.hatch_profiles) {
            for (var k in shp.hatch_profiles) {
                if (profiles[k]) {
                    profiles[k] = Object.assign({}, shp.hatch_profiles[k])
                }
            }
            if (shp.mark_contour !== undefined) markContour = shp.mark_contour
            if (shp.mark_contour_first !== undefined) markContourFirst = shp.mark_contour_first
        } else if (shp && shp.penId !== undefined && shp.penId > 0) {
            for (var pk in profiles) {
                profiles[pk].pen_no = shp.penId
            }
        }"""

replacement_open_modal = """        var shapePen = (shp && shp.penId !== undefined) ? shp.penId : 0
        if (shp && shp.hatch_profiles) {
            for (var k in shp.hatch_profiles) {
                if (profiles[k]) {
                    profiles[k] = Object.assign({}, shp.hatch_profiles[k])
                }
            }
            if (shp.mark_contour !== undefined) markContour = shp.mark_contour
            if (shp.mark_contour_first !== undefined) markContourFirst = shp.mark_contour_first
        } else {
            // Adopt shape's pen by default for active profiles
            for (var pk in profiles) {
                profiles[pk].pen_no = shapePen
            }
        }"""

if target_open_modal in modal_text:
    modal_text = modal_text.replace(target_open_modal, replacement_open_modal, 1)
    print("Successfully patched openModal in CadHatchModal.qml!")
else:
    print("WARNING: target_open_modal not found in CadHatchModal.qml")

target_load_fields = """        angleInput.text = (p.angle !== undefined) ? p.angle.toString() : "45.0"
        penSelector.selectedPenId = (p.pen_no !== undefined && p.pen_no > 0)
            ? p.pen_no
            : ((targetShape && targetShape.penId !== undefined && targetShape.penId > 0) ? targetShape.penId : 0)"""

replacement_load_fields = """        angleInput.text = (p.angle !== undefined) ? p.angle.toString() : "45.0"
        var sPen = (targetShape && targetShape.penId !== undefined) ? targetShape.penId : 0
        penSelector.selectedPenId = (p.pen_no !== undefined) ? p.pen_no : sPen"""

if target_load_fields in modal_text:
    modal_text = modal_text.replace(target_load_fields, replacement_load_fields, 1)
    print("Successfully patched loadProfileFields in CadHatchModal.qml!")
else:
    print("WARNING: target_load_fields not found in CadHatchModal.qml")

with open(modal_path, "w", encoding="utf-8") as f:
    f.write(modal_text)

# 3. Patch Theme.qml for default Pen 0 color
theme_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\Theme.qml"
with open(theme_path, "r", encoding="utf-8") as f:
    theme_text = f.read().replace("\r\n", "\n")

target_theme_p0 = '{ id: 0, name: "Pen 0 (Default)", color: isDark ? "#00E5FF" : "#192D78",'
repl_theme_p0 = '{ id: 0, name: "Pen 0 (Default)", color: "#000000",'

if target_theme_p0 in theme_text:
    theme_text = theme_text.replace(target_theme_p0, repl_theme_p0, 1)
    print("Successfully patched Theme.qml default Pen 0 color to #000000!")
else:
    print("Note: target_theme_p0 not found or already modified")

with open(theme_path, "w", encoding="utf-8") as f:
    f.write(theme_text)

print("Canvas, Hatch Modal, and Theme patched successfully.")

