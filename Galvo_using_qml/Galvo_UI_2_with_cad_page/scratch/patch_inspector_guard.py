with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Patch fontFamilyCombo.onActivated
old_font_act = """                                onActivated: function(index) {
                                    if (root.selectedShape) {
                                        var chosenFont = (index >= 0 && model && index < model.length) ? model[index] : currentText"""

new_font_act = """                                onActivated: function(index) {
                                    if (root.selectedShape && root.selectedShape.type === "text") {
                                        var chosenFont = (index >= 0 && model && index < model.length) ? model[index] : currentText"""

assert old_font_act in content, "old_font_act not found"
content = content.replace(old_font_act, new_font_act, 1)

# 2. Patch textHeightInput.onValueChanged
old_height_val = """                                onValueChanged: function(v) {
                                    if (root.selectedShape) {
                                        root.selectedShape.hMm = Math.max(0.5, v)"""

new_height_val = """                                onValueChanged: function(v) {
                                    if (root.selectedShape && root.selectedShape.type === "text") {
                                        root.selectedShape.hMm = Math.max(0.5, v)"""

assert old_height_val in content, "old_height_val not found"
content = content.replace(old_height_val, new_height_val, 1)

# 3. Patch textEditArea
old_text_area = """                                TextArea {
                                    id: textEditArea
                                    text: root.selectedShape ? (root.selectedShape.text || "TEXT") : "TEXT"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 12
                                    color: Theme.textPrimary
                                    wrapMode: TextEdit.Wrap
                                    selectByMouse: true
                                    background: null

                                    onTextChanged: {
                                        if (root.selectedShape && root.selectedShape.text !== text) {"""

new_text_area = """                                TextArea {
                                    id: textEditArea
                                    text: (root.selectedShape && root.selectedShape.type === "text") ? (root.selectedShape.text || "TEXT") : ""
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 12
                                    color: Theme.textPrimary
                                    wrapMode: TextEdit.Wrap
                                    selectByMouse: true
                                    background: null

                                    onTextChanged: {
                                        if (root.selectedShape && root.selectedShape.type === "text" && root.selectedShape.text !== text) {"""

assert old_text_area in content, "old_text_area not found"
content = content.replace(old_text_area, new_text_area, 1)

# 4. Patch barcodeContentInput
old_barcode_input = """                                TextField {
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
                                        if (root.selectedShape && text !== root.selectedShape.text) {"""

new_barcode_input = """                                TextField {
                                    id: barcodeContentInput
                                    Layout.fillWidth: true
                                    text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && root.selectedShape.text) ? String(root.selectedShape.text) : ""
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
                                        if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && text !== root.selectedShape.text) {"""

assert old_barcode_input in content, "old_barcode_input not found"
content = content.replace(old_barcode_input, new_barcode_input, 1)

# 5. Patch Regenerate Matrix button
old_regen = """                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {"""

new_regen = """                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                        onClicked: {
                                            if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix") && typeof cad !== "undefined" && cad) {"""

assert old_regen in content, "old_regen not found"
content = content.replace(old_regen, new_regen, 1)

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully patched CadInspectorPanel.qml with strict shape-type guards!")

