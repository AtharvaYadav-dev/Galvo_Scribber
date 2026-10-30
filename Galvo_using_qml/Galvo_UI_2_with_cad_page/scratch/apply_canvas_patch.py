import os

canvas_path = r"qml/components/cad/CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    // 1. High-contrast white backing card for optical scanning & smartphone camera redirection
                    ctx.fillStyle = "#FFFFFF"
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)

                    // 2. Crisp optical black barcode modules & bars (scannable directly from screen)
                    ctx.fillStyle = (penColor === "#FFFFFF" || penColor === "#ffffff") ? "#111827" : "#0A0F1D"
                    if (shp.rects && shp.rects.length > 0) {
                        for (var ri = 0; ri < shp.rects.length; ri++) {
                            var rc = shp.rects[ri]
                            var rx = rc.x * scale
                            var ry = -rc.y * scale
                            var rw = rc.w * scale
                            var rh = rc.h * scale
                            ctx.fillRect(rx, ry, rw, rh)
                        }
                    } else if (shp.paths && shp.paths.length > 0) {
                        ctx.beginPath()
                        for (var pi = 0; pi < shp.paths.length; pi++) {
                            var sp = shp.paths[pi]
                            if (sp.length >= 2) {
                                ctx.moveTo(sp[0][0] * scale, -sp[0][1] * scale)
                                for (var ki = 1; ki < sp.length; ki++) {
                                    ctx.lineTo(sp[ki][0] * scale, -sp[ki][1] * scale)
                                }
                            }
                        }
                        ctx.fill()
                    }

                    // 3. Laser pen color perimeter indicator border
                    ctx.strokeStyle = penColor
                    ctx.lineWidth = 1.5
                    ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)"""

replacement_str = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    // 1. High-contrast white backing card for optical scanning & smartphone camera redirection
                    ctx.fillStyle = "#FFFFFF"
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)

                    // 2. Crisp optical black barcode modules & bars (scannable directly from screen)
                    if (!shp.hatched) {
                        ctx.fillStyle = (penColor === "#FFFFFF" || penColor === "#ffffff") ? "#111827" : "#0A0F1D"
                        if (shp.rects && shp.rects.length > 0) {
                            var oLap = 0.5 // Eliminates Porter-Duff subpixel antialiasing gaps between adjacent module rows
                            for (var ri = 0; ri < shp.rects.length; ri++) {
                                var rc = shp.rects[ri]
                                var rx = rc.x * scale
                                var ry = -rc.y * scale
                                var rw = rc.w * scale
                                var rh = rc.h * scale
                                ctx.fillRect(rx, ry, rw + (rw > 0 ? oLap : 0), rh + (rh > 0 ? oLap : 0))
                            }
                        } else if (shp.paths && shp.paths.length > 0) {
                            ctx.beginPath()
                            for (var pi = 0; pi < shp.paths.length; pi++) {
                                var sp = shp.paths[pi]
                                if (sp.length >= 2) {
                                    ctx.moveTo(sp[0][0] * scale, -sp[0][1] * scale)
                                    for (var ki = 1; ki < sp.length; ki++) {
                                        ctx.lineTo(sp[ki][0] * scale, -sp[ki][1] * scale)
                                    }
                                }
                            }
                            ctx.fill()
                        }
                    } else {
                        // When hatched: stroke light module borders so vector hatch lines inside are crisp and visible
                        ctx.strokeStyle = penColor
                        ctx.lineWidth = 0.75
                        if (shp.rects && shp.rects.length > 0) {
                            for (var ri2 = 0; ri2 < shp.rects.length; ri2++) {
                                var rc2 = shp.rects[ri2]
                                ctx.strokeRect(rc2.x * scale, -rc2.y * scale, rc2.w * scale, rc2.h * scale)
                            }
                        }
                    }

                    // 3. Laser pen color perimeter indicator border
                    ctx.strokeStyle = penColor
                    ctx.lineWidth = 1.5
                    ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)"""

content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(canvas_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched CadCanvas.qml")
else:
    print("Error: target_norm not found in CadCanvas.qml")

