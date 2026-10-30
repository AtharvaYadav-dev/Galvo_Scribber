import os

modal_path = r"qml/components/cad/CadBarcodeModal.qml"
with open(modal_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                CadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Add to Canvas"
                    variant: "accent"
                    onClicked: {
                        root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement)
                        root.close()
                    }
                }
            }"""

replacement_str = """            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                CadButton {
                    Layout.fillWidth: true
                    text: "Export DXF"
                    iconName: "file_download"
                    variant: "outline"
                    tooltipText: "Export Vector DXF for EzCad / AutoCAD / LightBurn"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp, "dxf")
                        }
                    }
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Export SVG"
                    iconName: "file_download"
                    variant: "outline"
                    tooltipText: "Export Scalable Vector Graphics (SVG)"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp2 = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp2, "svg")
                        }
                    }
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Export PNG"
                    iconName: "file_download"
                    variant: "outline"
                    tooltipText: "Export High-Resolution Scannable PNG Image"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp3 = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp3, "png")
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                CadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Add to Canvas"
                    variant: "accent"
                    onClicked: {
                        root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement)
                        root.close()
                    }
                }
            }"""

content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(modal_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched CadBarcodeModal.qml")
else:
    print("Error: target_norm not found in CadBarcodeModal.qml")

