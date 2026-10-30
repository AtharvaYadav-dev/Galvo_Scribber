with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """                            CadComboBox {
                                id: fontFamilyCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                model: (typeof cad !== "undefined" && cad) ? cad.availableFonts : ["Segoe UI", "Arial", "Leelawadee UI", "Times New Roman", "Consolas"]
                                currentIndex: {
                                    if (!root.selectedShape) return 0
                                    var f = root.selectedShape.fontFamily || "Segoe UI"
                                    var idx = find(f)
                                    return (idx >= 0) ? idx : 0
                                }
                                onActivated: function(index) {
                                    if (root.selectedShape) {
                                        root.selectedShape.fontFamily = currentText
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        if (typeof cad !== "undefined" && cad) {
                                            var m = cad.measureText(
                                                root.selectedShape.text || "TEXT",
                                                currentText,
                                                root.selectedShape.hMm || 4.0,
                                                Boolean(root.selectedShape.bold),
                                                Boolean(root.selectedShape.italic)
                                            )
                                            if (m && m.wMm > 0) {
                                                root.selectedShape.wMm = m.wMm
                                                inputW.text = m.wMm.toFixed(3)
                                            }
                                        }
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }"""

new_block = """                            CadComboBox {
                                id: fontFamilyCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                searchable: true
                                searchPlaceholder: "Search font face (e.g. Arial)..."
                                model: (typeof cad !== "undefined" && cad) ? cad.availableFonts : ["Segoe UI", "Arial", "Leelawadee UI", "Times New Roman", "Consolas"]
                                currentIndex: {
                                    if (!root.selectedShape) return 0
                                    var f = root.selectedShape.fontFamily || "Segoe UI"
                                    var idx = find(f)
                                    return (idx >= 0) ? idx : 0
                                }
                                onActivated: function(index) {
                                    if (root.selectedShape) {
                                        var chosenFont = (index >= 0 && model && index < model.length) ? model[index] : currentText
                                        root.selectedShape.fontFamily = chosenFont
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        if (typeof cad !== "undefined" && cad) {
                                            var m = cad.measureText(
                                                root.selectedShape.text || "TEXT",
                                                chosenFont,
                                                root.selectedShape.hMm || 4.0,
                                                Boolean(root.selectedShape.bold),
                                                Boolean(root.selectedShape.italic)
                                            )
                                            if (m && m.wMm > 0) {
                                                root.selectedShape.wMm = m.wMm
                                                inputW.text = m.wMm.toFixed(3)
                                            }
                                        }
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }"""

old_update = """            if (typeof textHeightInput !== "undefined" && textHeightInput) textHeightInput.text = Number(root.selectedShape.hMm || 4.0).toFixed(3)
        }"""

new_update = """            if (typeof textHeightInput !== "undefined" && textHeightInput) textHeightInput.text = Number(root.selectedShape.hMm || 4.0).toFixed(3)
            if (typeof fontFamilyCombo !== "undefined" && fontFamilyCombo) {
                var f = root.selectedShape.fontFamily || "Segoe UI"
                var fIdx = fontFamilyCombo.find(f)
                if (fIdx >= 0) {
                    fontFamilyCombo.currentIndex = fIdx
                    fontFamilyCombo.displayText = f
                }
            }
        }"""

assert old_block in text, "old_block not found in CadInspectorPanel.qml"
assert old_update in text, "old_update not found in CadInspectorPanel.qml"

text = text.replace(old_block, new_block, 1)
text = text.replace(old_update, new_update, 1)

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated CadInspectorPanel.qml with searchable Face combo")

