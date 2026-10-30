import os

canvas_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    text = f.read().replace("\r\n", "\n")

# 1. Update unhatchSelectedShape to ensure mark_contour = true
target_unhatch = """            pushUndoState()
            s.hatched = false
            s.hatch_lines = []"""

repl_unhatch = """            pushUndoState()
            s.hatched = false
            s.mark_contour = true
            s.hatch_lines = []"""

if target_unhatch in text:
    text = text.replace(target_unhatch, repl_unhatch, 1)
    print("Updated unhatchSelectedShape with s.mark_contour = true")
else:
    print("WARNING: target_unhatch not found")

# 2. Update penColor calculation in CadCanvas.qml to handle dark theme contrast for Pen 0
target_pen_col = """                var penColor = Theme.getPenColor(shp.penId !== undefined ? shp.penId : 0)

                ctx.save()"""

repl_pen_col = """                var rawPenColor = Theme.getPenColor(shp.penId !== undefined ? shp.penId : 0)
                var penColor = rawPenColor
                // On dark canvas, pure black pen (#000000) is invisible against #070B14, so render with crisp high-contrast silver (#E2E8F0)
                if (Theme.isDark && (rawPenColor === "#000000" || String(rawPenColor).toLowerCase() === "#000000" || String(rawPenColor).toLowerCase() === "#000")) {
                    penColor = "#E2E8F0"
                }

                ctx.save()"""

if target_pen_col in text:
    text = text.replace(target_pen_col, repl_pen_col, 1)
    print("Updated penColor with dark theme contrast in CadCanvas.qml")
else:
    print("WARNING: target_pen_col not found")

# 3. Update rect rendering condition
target_rect = """                } else if (shp.type === "rect") {
                    if (shp.mark_contour !== false) {
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.35)
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                        ctx.restore()
                    }"""

repl_rect = """                } else if (shp.type === "rect") {
                    if (!shp.hatched || shp.mark_contour !== false) {
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.45)
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                        ctx.restore()
                    }"""

if target_rect in text:
    text = text.replace(target_rect, repl_rect, 1)
    print("Updated rect rendering condition in CadCanvas.qml")
else:
    print("WARNING: target_rect not found")

# 4. Update circle rendering condition
target_circle = """                } else if (shp.type === "circle") {
                    ctx.beginPath()
                    ctx.arc(0, 0, sw / 2, 0, Math.PI * 2)
                    if (shp.mark_contour !== false) {
                        ctx.stroke()
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.35)
                        ctx.stroke()
                        ctx.restore()
                    }"""

repl_circle = """                } else if (shp.type === "circle") {
                    ctx.beginPath()
                    ctx.arc(0, 0, sw / 2, 0, Math.PI * 2)
                    if (!shp.hatched || shp.mark_contour !== false) {
                        ctx.stroke()
                    } else {
                        ctx.save()
                        ctx.setLineDash([3, 3])
                        ctx.strokeStyle = Qt.rgba(penColor.r, penColor.g, penColor.b, 0.45)
                        ctx.stroke()
                        ctx.restore()
                    }"""

if target_circle in text:
    text = text.replace(target_circle, repl_circle, 1)
    print("Updated circle rendering condition in CadCanvas.qml")
else:
    print("WARNING: target_circle not found")

# 5. Update hatch lines color rendering for Pen 0 on dark canvas
target_hline = """                        for (var hl = 0; hl < shp.hatch_lines.length; hl++) {
                            var hline = shp.hatch_lines[hl]
                            var hPenCol = (hline.pen_id !== undefined)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor
                            ctx.strokeStyle = hPenCol"""

repl_hline = """                        for (var hl = 0; hl < shp.hatch_lines.length; hl++) {
                            var hline = shp.hatch_lines[hl]
                            var rawHCol = (hline.pen_id !== undefined)
                                ? Theme.getPenColor(hline.pen_id)
                                : rawPenColor
                            var hPenCol = rawHCol
                            if (Theme.isDark && (rawHCol === "#000000" || String(rawHCol).toLowerCase() === "#000000" || String(rawHCol).toLowerCase() === "#000")) {
                                hPenCol = "#94A3B8"
                            }
                            ctx.strokeStyle = hPenCol"""

if target_hline in text:
    text = text.replace(target_hline, repl_hline, 1)
    print("Updated hatch line color rendering in CadCanvas.qml")
else:
    print("WARNING: target_hline not found")

with open(canvas_path, "w", encoding="utf-8") as f:
    f.write(text)

print("\nDone patching CadCanvas.qml")

