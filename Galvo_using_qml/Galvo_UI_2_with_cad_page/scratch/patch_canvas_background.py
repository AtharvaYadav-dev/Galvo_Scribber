import os

canvas_path = r"qml/components/cad/CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    // 1. High-contrast white backing card for optical scanning & smartphone camera redirection
                    ctx.fillStyle = "#FFFFFF"
                    ctx.fillRect(-sw / 2, -sh / 2, sw, sh)

                    // 2. Crisp optical black barcode modules & bars (scannable directly from screen)
                    if (!shp.hatched) {
                        ctx.fillStyle = (penColor === "#FFFFFF" || penColor === "#ffffff") ? "#111827" : "#0A0F1D\""""

replacement_str = """                } else if (shp.type === "qrcode" || shp.type === "datamatrix" || shp.type === "barcode128") {
                    // 1. White backing card: only if explicitly enabled on shape, otherwise clean dark CAD background
                    if (Boolean(shp.showBackground)) {
                        ctx.fillStyle = "#FFFFFF"
                        ctx.fillRect(-sw / 2, -sh / 2, sw, sh)
                    }

                    // 2. Crisp barcode modules & bars in laser pen color
                    if (!shp.hatched) {
                        ctx.fillStyle = Boolean(shp.showBackground) ? ((penColor === "#FFFFFF" || penColor === "#ffffff") ? "#111827" : "#0A0F1D") : penColor"""

content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(canvas_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched CadCanvas.qml showBackground")
else:
    print("Error: target_norm not found in CadCanvas.qml")
