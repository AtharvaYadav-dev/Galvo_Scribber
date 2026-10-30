import os

inspector_path = r"qml/components/cad/CadInspectorPanel.qml"
with open(inspector_path, "r", encoding="utf-8") as f:
    content = f.read()

target_str = """                                RowLayout {
                                    Layout.fillWidth: true
                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                        onClicked: {
                                            if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && typeof cad !== "undefined" && cad) {
                                                var res = cad.generateBarcodeEntity(root.selectedShape.type, root.selectedShape.text, root.selectedShape.wMm)
                                                if (res && res.rects) {
                                                    root.selectedShape.rects = res.rects
                                                    root.selectedShape.paths = res.paths
                                                    if (res.hMm) root.selectedShape.hMm = res.hMm
                                                }
                                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                                root.shapeModified(root.selectedShape)
                                                root.applyTriggered(root.selectedShape)
                                            }
                                        }
                                    }
                                }"""

replacement_str = """                                RowLayout {
                                    Layout.fillWidth: true
                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                        iconName: "refresh"
                                        onClicked: {
                                            if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && typeof cad !== "undefined" && cad) {
                                                var res = cad.generateBarcodeEntity(root.selectedShape.type, root.selectedShape.text, root.selectedShape.wMm)
                                                if (res && res.rects) {
                                                    root.selectedShape.rects = res.rects
                                                    root.selectedShape.paths = res.paths
                                                    if (res.hMm) root.selectedShape.hMm = res.hMm
                                                }
                                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                                root.shapeModified(root.selectedShape)
                                                root.applyTriggered(root.selectedShape)
                                            }
                                        }
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 1
                                    color: Theme.borderMuted
                                    opacity: 0.6
                                }

                                Text {
                                    text: "EXPORT / DOWNLOAD CODE ENTITY"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.textMuted
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "DXF"
                                        iconName: "file_download"
                                        variant: "outline"
                                        tooltipText: "Export Vector DXF for EzCad / AutoCAD / LightBurn"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "dxf")
                                            }
                                        }
                                    }

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "SVG"
                                        iconName: "file_download"
                                        variant: "outline"
                                        tooltipText: "Export Scalable Vector Graphics (SVG)"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "svg")
                                            }
                                        }
                                    }

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "PNG"
                                        iconName: "file_download"
                                        variant: "outline"
                                        tooltipText: "Export High-Resolution Scannable PNG Image"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "png")
                                            }
                                        }
                                    }
                                }"""

content_norm = content.replace("\r\n", "\n")
target_norm = target_str.replace("\r\n", "\n")
replacement_norm = replacement_str.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm, 1)
    with open(inspector_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_content)
    print("Successfully patched CadInspectorPanel.qml")
else:
    print("Error: target_norm not found in CadInspectorPanel.qml")

