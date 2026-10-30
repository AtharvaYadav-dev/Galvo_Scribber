with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                                    }
            }

            // TAB 2: LASER PENS & PROCESS PARAMETERS"""

replacement = """                                    }

                    // 5. DEDICATED 2D BARCODE & QR CODE INSPECTOR
                    // (Visible specifically when a Barcode or QR entity is selected)
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: root.selectedShape !== null && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix")

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.borderCard
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: barcodeInnerCol.implicitHeight + 20
                            radius: 8
                            color: Theme.bgCardAlt
                            border.color: Theme.borderActive
                            border.width: 1

                            ColumnLayout {
                                id: barcodeInnerCol
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8

                                RowLayout {
                                    Layout.fillWidth: true
                                    CadIcon {
                                        name: root.selectedShape && root.selectedShape.type === "qrcode" ? "qr_code_2" : "horizontal_rule"
                                        size: 16
                                        iconColor: Theme.accentCyan
                                    }
                                    Text {
                                        text: root.selectedShape ? (root.selectedShape.type === "qrcode" ? "2D QR CODE MATRIX" : (root.selectedShape.type === "barcode128" ? "1D CODE 128 BARCODE" : "2D DATAMATRIX")) : "BARCODE"
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.textPrimary
                                    }
                                    Item { Layout.fillWidth: true }
                                    Rectangle {
                                        width: 60
                                        height: 18
                                        radius: 4
                                        color: Qt.rgba(0.0, 0.8, 0.9, 0.15)
                                        border.color: Theme.accentCyan
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: root.selectedShape && root.selectedShape.type === "qrcode" ? "ISO 18004" : "GS1"
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: Theme.accentCyan
                                        }
                                    }
                                }

                                Text {
                                    text: "ENCODED DATA CONTENT / SERIAL / URL"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.textMuted
                                }

                                TextField {
                                    id: barcodeContentInput
                                    Layout.fillWidth: true
                                    text: (root.selectedShape && root.selectedShape.text) ? String(root.selectedShape.text) : ""
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 11
                                    color: Theme.textPrimary
                                    placeholderText: "Enter URL, text, or serial..."
                                    background: Rectangle {
                                        radius: 5
                                        color: Theme.bgInput
                                        border.color: barcodeContentInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                        border.width: 1
                                    }
                                    onEditingFinished: {
                                        if (root.selectedShape && text !== root.selectedShape.text) {
                                            root.selectedShape.text = text
                                            if (typeof cad !== "undefined" && cad) {
                                                var res = cad.generateBarcodeEntity(root.selectedShape.type, text, root.selectedShape.wMm)
                                                if (res && res.rects) {
                                                    root.selectedShape.rects = res.rects
                                                    root.selectedShape.paths = res.paths
                                                    if (res.hMm) root.selectedShape.hMm = res.hMm
                                                }
                                            }
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
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
                            }
                        }
                    }
                }
            }

            // TAB 2: LASER PENS & PROCESS PARAMETERS"""

assert target in text, "target not found in CadInspectorPanel.qml"
text = text.replace(target, replacement, 1)

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadInspectorPanel.qml successfully updated with Barcode & QR Code card!")

