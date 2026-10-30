with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    text = f.read()

target = """    CadBarcodeModal {
        id: barcodeModal
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc) {
            cadCanvas.pushUndoState()
            var shapeType = "qrcode"
            var prefix = "QRCode_"
            var w = sizeMm
            var h = sizeMm
            if (type === "Code 128") {
                shapeType = "barcode128"
                prefix = "Barcode128_"
                h = sizeMm * 0.4
            } else if (type === "DataMatrix") {
                shapeType = "datamatrix"
                prefix = "DataMatrix_"
            }
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
                hatched: true,
                visible: true,
                locked: false
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

replacement = """    CadBarcodeModal {
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

assert target in text, "target not found"
text = text.replace(target, replacement, 1)

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadView.qml updated!")

