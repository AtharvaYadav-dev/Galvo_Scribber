import os

canvas_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    text = f.read().replace("\r\n", "\n")

target = """                var penColor = Theme.getPenColor(shp.penId || 0)

                ctx.save()"""

replacement = """                var rawPenColor = Theme.getPenColor(shp.penId || 0)
                var penColor = rawPenColor
                // On dark canvas, pure black pen (#000000) is invisible against #070B14, so render with crisp high-contrast silver (#E2E8F0)
                if (Theme.isDark && (rawPenColor === "#000000" || String(rawPenColor).toLowerCase() === "#000000" || String(rawPenColor).toLowerCase() === "#000")) {
                    penColor = "#E2E8F0"
                }

                ctx.save()"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(canvas_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully patched penColor in CadCanvas.qml")
else:
    print("Target still not found")

