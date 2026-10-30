with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('                } else if (shp.type === "qrcode") {')
s2 = text.find('                } else if (shp.type === "polygon" || shp.type === "dxf" || shp.type === "svg" || shp.type === "line") {')

assert s1 != -1 and s2 != -1, f"Indices not found: s1={s1}, s2={s2}"

replacement = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
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
                    }
"""

text = text[:s1] + replacement + text[s2:]

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadCanvas.qml barcode/QR rendering updated successfully!")

