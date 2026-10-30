with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update onShapesImported
target_import = """    Connections {
        target: (typeof cad !== "undefined") ? cad : null
        function onShapesImported(newShapes) {
            if (!newShapes || newShapes.length === 0) return
            var updated = cadCanvas.shapes.slice()
            for (var i = 0; i < newShapes.length; i++) {
                updated.push(newShapes[i])
            }
            cadCanvas.shapes = updated
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = updated.length - 1
            cadCanvas.zoomFit()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(cadCanvas.shapes)
            }
        }
    }"""

new_import = """    Connections {
        target: (typeof cad !== "undefined") ? cad : null
        function onShapesImported(newShapes) {
            if (!newShapes || newShapes.length === 0) return
            cadCanvas.pushUndoState()
            var updated = cadCanvas.shapes.slice()
            for (var i = 0; i < newShapes.length; i++) {
                updated.push(newShapes[i])
            }
            cadCanvas.shapes = updated
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = updated.length - 1
            if (updated.length > 0) {
                cadCanvas.shapeSelected(updated[updated.length - 1])
            }
            cadCanvas.zoomFit()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(cadCanvas.shapes)
            }
        }
    }"""

assert target_import in text, "target_import not found"
text = text.replace(target_import, new_import, 1)

# 2. Update onTextTriggered
target_text = """                    onTextTriggered: {
                        var defaultText = "TEXT"
                        var defaultFamily = "Segoe UI"
                        var defaultHeight = 4.0
                        var calculatedW = 12.15
                        if (typeof cad !== "undefined" && cad) {
                            var m = cad.measureText(defaultText, defaultFamily, defaultHeight, false, false)
                            if (m && m.wMm > 0) {
                                calculatedW = m.wMm
                            }
                        }
                        var newText = {
                            id: cadCanvas.shapes.length + 1,
                            name: "Text_" + (cadCanvas.shapes.length + 1),
                            type: "text",
                            text: defaultText,
                            xMm: 0,
                            yMm: 0,
                            wMm: calculatedW,
                            hMm: defaultHeight,
                            rotation: 0,
                            fontFamily: defaultFamily,
                            fontType: "TrueType Font",
                            textAlign: "center",
                            charSpace: 0.0,
                            lineSpace: 0.0,
                            bold: false,
                            italic: false,
                            penId: inspector.selectedPenId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        var updatedT = cadCanvas.shapes.slice()
                        updatedT.push(newText)
                        cadCanvas.shapes = updatedT
                        cadCanvas.shapesChanged()
                        cadCanvas.selectedIndex = updatedT.length - 1
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(updatedT)
                        }
                        cadCanvas.requestPaint()
                    }"""

new_text = """                    onTextTriggered: {
                        cadCanvas.pushUndoState()
                        var defaultText = "TEXT"
                        var defaultFamily = "Segoe UI"
                        var defaultHeight = 4.0
                        var calculatedW = 12.15
                        if (typeof cad !== "undefined" && cad) {
                            var m = cad.measureText(defaultText, defaultFamily, defaultHeight, false, false)
                            if (m && m.wMm > 0) {
                                calculatedW = m.wMm
                            }
                        }
                        var newText = {
                            id: cadCanvas.shapes.length + 1,
                            name: "Text_" + (cadCanvas.shapes.length + 1),
                            type: "text",
                            text: defaultText,
                            xMm: 0,
                            yMm: 0,
                            wMm: calculatedW,
                            hMm: defaultHeight,
                            rotation: 0,
                            fontFamily: defaultFamily,
                            fontType: "TrueType Font",
                            textAlign: "center",
                            charSpace: 0.0,
                            lineSpace: 0.0,
                            bold: false,
                            italic: false,
                            penId: inspector.selectedPenId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        var updatedT = cadCanvas.shapes.slice()
                        updatedT.push(newText)
                        cadCanvas.shapes = updatedT
                        cadCanvas.shapesChanged()
                        cadCanvas.selectedIndex = updatedT.length - 1
                        cadCanvas.shapeSelected(newText)
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(updatedT)
                        }
                        cadCanvas.requestPaint()
                    }"""

assert target_text in text, "target_text not found"
text = text.replace(target_text, new_text, 1)

# 3. Update CadBarcodeModal
target_barcode = """    CadBarcodeModal {
        id: barcodeModal
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc) {
            var newCode = {
                id: cadCanvas.shapes.length + 1,
                name: "Barcode_" + (cadCanvas.shapes.length + 1),
                type: "qrcode",
                text: content,
                xMm: 0,
                yMm: 0,
                wMm: sizeMm,
                hMm: sizeMm,
                rotation: 0,
                penId: inspector.selectedPenId,
                hatched: true,
                visible: true,
                locked: false
            }
            cadCanvas.shapes.push(newCode)
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = cadCanvas.shapes.length - 1
        }
    }"""

new_barcode = """    CadBarcodeModal {
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

assert target_barcode in text, "target_barcode not found"
text = text.replace(target_barcode, new_barcode, 1)

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadView.qml updated successfully!")

