# 1. Patch CadCanvas.qml
with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    canvas_content = f.read()

target_canvas = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    ctx.fillStyle = penColor
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
                    } else {
                        ctx.strokeStyle = penColor
                        ctx.strokeRect(-sw / 2, -sh / 2, sw, sh)
                    }"""

replacement_canvas = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
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

assert target_canvas in canvas_content, "target_canvas not found"
canvas_content = canvas_content.replace(target_canvas, replacement_canvas, 1)

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(canvas_content)
print("Successfully patched CadCanvas.qml with scan-ready white backing and pen border!")

# 2. Patch CadView.qml
with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    view_content = f.read()

target_view = """            if (entityData && entityData.wMm) w = entityData.wMm

            var newCode = {"""

replacement_view = """            if (entityData && entityData.wMm) w = entityData.wMm
            if (entityData && entityData.hMm) h = entityData.hMm

            var newCode = {"""

assert target_view in view_content, "target_view not found"
view_content = view_content.replace(target_view, replacement_view, 1)

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(view_content)
print("Successfully patched CadView.qml with exact entity wMm and hMm!")

