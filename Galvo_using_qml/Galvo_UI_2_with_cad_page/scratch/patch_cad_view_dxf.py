import os

cad_view_path = r"qml/views/CadView.qml"
with open(cad_view_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """    CadBarcodeModal {
        id: barcodeModal
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc) {
            cadCanvas.pushUndoState()
            var entityData = null
            if (typeof cad !== "undefined" && cad) {
                entityData = cad.generateBarcodeEntity(type, content, sizeMm)
            }
            var shapeType = "qrcode"
            var prefix = "QRCode_"
            var w = sizeMm
            var h = sizeMm
            if (type === "Code 128") {
                shapeType = "barcode128"
                prefix = "Barcode128_"
                h = (entityData && entityData.hMm) ? entityData.hMm : sizeMm * 0.4
            } else if (type === "DataMatrix") {
                shapeType = "datamatrix"
                prefix = "DataMatrix_"
            }
            if (entityData && entityData.wMm) w = entityData.wMm
            if (entityData && entityData.hMm) h = entityData.hMm

            var newCode = {
                id: cadCanvas.shapes.length + 1,
                name: prefix + (cadCanvas.shapes.length + 1),
                type: shapeType,
                text: content,
                xMm: 0,
                yMm: 0,
                wMm: Math.round(w * 10) / 10,
                hMm: Math.round(h * 10) / 10,
                rotation: 0,
                penId: inspector.selectedPenId,
                hatched: false,
                visible: true,
                locked: false,
                rects: (entityData && entityData.rects) ? entityData.rects : [],
                paths: (entityData && entityData.paths) ? entityData.paths : []
            }
            var copy = cadCanvas.shapes.slice()
            copy.push(newCode)
            cadCanvas.shapes = copy
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = copy.length - 1
            cadCanvas.shapeSelected(newCode)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
            }
            cadCanvas.requestPaint()
            barcodeModal.close()
        }
    }"""

replacement_str = """    CadBarcodeModal {
        id: barcodeModal
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc, outputFormat) {
            cadCanvas.pushUndoState()
            var mode = outputFormat || "dxf"
            var entityData = null
            if (typeof cad !== "undefined" && cad) {
                entityData = cad.generateBarcodeEntity(type, content, sizeMm)
            }
            var bType = (type === "Code 128" ? "barcode128" : (type === "DataMatrix" ? "datamatrix" : "qrcode"))
            var shapeType = (mode === "dxf" ? "dxf" : (mode === "svg" ? "svg" : bType))
            var prefix = (mode === "dxf" ? "DXF_" : (mode === "svg" ? "SVG_" : "")) + (type === "Code 128" ? "Barcode128_" : (type === "DataMatrix" ? "DataMatrix_" : "QRCode_"))
            var w = sizeMm
            var h = sizeMm
            if (type === "Code 128") {
                h = (entityData && entityData.hMm) ? entityData.hMm : sizeMm * 0.4
            }
            if (entityData && entityData.wMm) w = entityData.wMm
            if (entityData && entityData.hMm) h = entityData.hMm

            var newCode = {
                id: cadCanvas.shapes.length + 1,
                name: prefix + (cadCanvas.shapes.length + 1),
                type: shapeType, // "dxf" / "svg" (vector CAD) or optical barcode type
                isBarcode: true,
                barcodeType: bType,
                outputFormat: mode,
                text: content,
                xMm: 0,
                yMm: 0,
                wMm: Math.round(w * 10) / 10,
                hMm: Math.round(h * 10) / 10,
                rotation: 0,
                penId: inspector.selectedPenId,
                hatched: false,
                mark_contour: true,
                visible: true,
                locked: false,
                rects: (entityData && entityData.rects) ? entityData.rects : [],
                paths: (entityData && entityData.paths) ? entityData.paths : []
            }
            var copy = cadCanvas.shapes.slice()
            copy.push(newCode)
            cadCanvas.shapes = copy
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = copy.length - 1
            cadCanvas.shapeSelected(newCode)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
            }
            cadCanvas.requestPaint()
            barcodeModal.close()
        }
    }"""

content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(cad_view_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched CadView.qml")
else:
    print("Error: target_norm not found in CadView.qml")

