import os

# 1. Patch CadBarcodeModal.qml
modal_path = r"qml/components/cad/CadBarcodeModal.qml"
with open(modal_path, "r", encoding="utf-8") as f:
    modal_content = f.read()

# Add property outputFormat and update signal
modal_content = modal_content.replace(
    'property real codeSizeMm: 20.0',
    'property real codeSizeMm: 20.0\n    property string outputFormat: "dxf" // "dxf" (Vector CAD), "svg" (Vector Paths), "barcode" (Optical)'
)

modal_content = modal_content.replace(
    'signal generateBarcode(string type, string content, real sizeMm, bool autoInc)',
    'signal generateBarcode(string type, string content, real sizeMm, bool autoInc, string outputFormat)'
)

# Insert Format Selector right under Barcode Type selection
format_selector_snippet = """                    // Format Selector: DXF Vector vs SVG Vector vs Optical Barcode
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Text {
                            text: "CANVAS ADD FORMAT / GEOMETRY TYPE"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Repeater {
                                model: [
                                    { id: "dxf", label: "DXF Vector (CAD)", tip: "Adds as pure CAD polylines in laser pen color (No white PNG card)" },
                                    { id: "svg", label: "SVG Vector", tip: "Adds as SVG vector paths (No white PNG card)" },
                                    { id: "barcode", label: "Optical Card", tip: "Adds as screen scannable barcode card" }
                                ]
                                delegate: CadButton {
                                    Layout.fillWidth: true
                                    text: modelData.label
                                    isActive: root.outputFormat === modelData.id
                                    tooltipText: modelData.tip
                                    onClicked: root.outputFormat = modelData.id
                                }
                            }
                        }
                    }
"""

target_after_type = """                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Repeater {
                            model: ["QR Code", "Code 128", "DataMatrix"]
                            delegate: CadButton {
                                Layout.fillWidth: true
                                text: modelData
                                isActive: root.barcodeType === modelData
                                onClicked: root.barcodeType = modelData
                            }
                        }
                    }"""

if target_after_type in modal_content:
    modal_content = modal_content.replace(
        target_after_type,
        target_after_type + "\n\n" + format_selector_snippet
    )
    print("Added format selector to CadBarcodeModal.qml")
else:
    print("Warning: target_after_type not matched in CadBarcodeModal.qml")

# Update Add to Canvas button to pass outputFormat
modal_content = modal_content.replace(
    'root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement)\n                        root.close()',
    'root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement, root.outputFormat)\n                        root.close()'
)
modal_content = modal_content.replace(
    'root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement)\r\n                        root.close()',
    'root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement, root.outputFormat)\r\n                        root.close()'
)

with open(modal_path, "w", encoding="utf-8") as f:
    f.write(modal_content)
print("Updated CadBarcodeModal.qml")

