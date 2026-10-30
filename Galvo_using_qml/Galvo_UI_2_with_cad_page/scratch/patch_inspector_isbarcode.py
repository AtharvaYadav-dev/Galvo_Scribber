inspector_path = r"qml/components/cad/CadInspectorPanel.qml"
with open(inspector_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'visible: root.selectedShape !== null && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix")',
    'visible: root.selectedShape !== null && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || Boolean(root.selectedShape.isBarcode))'
)

text = text.replace(
    'name: root.selectedShape && root.selectedShape.type === "qrcode" ? "qr_code_2" : "horizontal_rule"',
    'name: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode")) ? "qr_code_2" : "horizontal_rule"'
)

text = text.replace(
    'text: root.selectedShape ? (root.selectedShape.type === "qrcode" ? "2D QR CODE MATRIX" : (root.selectedShape.type === "barcode128" ? "1D CODE 128 BARCODE" : "2D DATAMATRIX")) : "BARCODE"',
    'text: root.selectedShape ? ((root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode") ? "2D QR CODE MATRIX" : ((root.selectedShape.type === "barcode128" || root.selectedShape.barcodeType === "barcode128") ? "1D CODE 128 BARCODE" : "2D DATAMATRIX")) : "BARCODE"'
)

text = text.replace(
    'text: root.selectedShape && root.selectedShape.type === "qrcode" ? "ISO 18004" : "GS1"',
    'text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode")) ? "ISO 18004" : "GS1"'
)

text = text.replace(
    'text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && root.selectedShape.text) ? String(root.selectedShape.text) : ""',
    'text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && root.selectedShape.text) ? String(root.selectedShape.text) : ""'
)

text = text.replace(
    'if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && text !== root.selectedShape.text) {',
    'if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && text !== root.selectedShape.text) {'
)

text = text.replace(
    'var res = cad.generateBarcodeEntity(root.selectedShape.type, text, root.selectedShape.wMm)',
    'var bType = root.selectedShape.barcodeType || root.selectedShape.type || "qrcode"\n                                                var res = cad.generateBarcodeEntity(bType, text, root.selectedShape.wMm)'
)

text = text.replace(
    'if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && typeof cad !== "undefined" && cad) {',
    'if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && typeof cad !== "undefined" && cad) {'
)

text = text.replace(
    'var res = cad.generateBarcodeEntity(root.selectedShape.type, root.selectedShape.text, root.selectedShape.wMm)',
    'var bType2 = root.selectedShape.barcodeType || root.selectedShape.type || "qrcode"\n                                                var res = cad.generateBarcodeEntity(bType2, root.selectedShape.text, root.selectedShape.wMm)'
)

with open(inspector_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Targeted replacements applied to CadInspectorPanel.qml successfully.")
