with open("qml/components/cad/CadInspectorPanel.qml", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add modelRevision
old_header = """    property var shapesModel: []
    property int selectedIndex: -1
    property var selectedShape: (selectedIndex >= 0 && selectedIndex < shapesModel.length) ? shapesModel[selectedIndex] : null"""

new_header = """    property var shapesModel: []
    property int modelRevision: 0
    onShapesModelChanged: modelRevision++
    property int selectedIndex: -1
    property var selectedShape: (modelRevision >= 0 && selectedIndex >= 0 && selectedIndex < shapesModel.length) ? shapesModel[selectedIndex] : null"""

assert old_header in content, "old_header not found"
content = content.replace(old_header, new_header)

# 2. Update delegateRow
old_delegate = """                                        readonly property bool isVis: !(modelData && modelData.visible === false)
                                        readonly property bool isLck: Boolean(modelData && modelData.locked === true)
                                        property bool isEditingName: false

                                        function startEditingName() {
                                            isEditingName = true
                                            inlineNameEdit.text = (modelData && modelData.name) ? modelData.name : ""
                                            inlineNameEdit.forceActiveFocus()
                                            inlineNameEdit.selectAll()
                                        }

                                        function commitInlineName() {
                                            if (isEditingName) {
                                                isEditingName = false
                                                var val = inlineNameEdit.text.trim()
                                                if (val.length > 0 && val !== modelData.name) {
                                                    root.shapeRenamed(index, val)
                                                }
                                            }
                                        }"""

new_delegate = """                                        readonly property var currentShape: (root.modelRevision >= 0 && index >= 0 && index < root.shapesModel.length) ? root.shapesModel[index] : modelData
                                        readonly property bool isVis: !(currentShape && currentShape.visible === false)
                                        readonly property bool isLck: Boolean(currentShape && currentShape.locked === true)
                                        property bool isEditingName: false

                                        function startEditingName() {
                                            isEditingName = true
                                            inlineNameEdit.text = (currentShape && currentShape.name) ? currentShape.name : ""
                                            inlineNameEdit.forceActiveFocus()
                                            inlineNameEdit.selectAll()
                                        }

                                        function commitInlineName() {
                                            if (isEditingName) {
                                                isEditingName = false
                                                var val = inlineNameEdit.text.trim()
                                                if (val.length > 0 && currentShape && val !== currentShape.name) {
                                                    root.shapeRenamed(index, val)
                                                    root.modelRevision++
                                                }
                                            }
                                        }"""

assert old_delegate in content, "old_delegate not found"
content = content.replace(old_delegate, new_delegate)

# 3. Update pen dot color in delegate
old_pen_dot = "color: Theme.penPalette[((modelData && modelData.penId) || 0) % Theme.penPalette.length].color"
new_pen_dot = "color: Theme.penPalette[((currentShape && currentShape.penId) || 0) % Theme.penPalette.length].color"
assert old_pen_dot in content, "old_pen_dot not found"
content = content.replace(old_pen_dot, new_pen_dot)

# 4. Update eyeMa & lockMa onClicked to increment modelRevision
old_eye_click = """                                                    onClicked: {
                                                        root.shapeVisibilityToggled(index)
                                                    }"""
new_eye_click = """                                                    onClicked: {
                                                        root.shapeVisibilityToggled(index)
                                                        root.modelRevision++
                                                    }"""
assert old_eye_click in content, "old_eye_click not found"
content = content.replace(old_eye_click, new_eye_click)

old_lock_click = """                                                    onClicked: {
                                                        root.shapeLockToggled(index)
                                                    }"""
new_lock_click = """                                                    onClicked: {
                                                        root.shapeLockToggled(index)
                                                        root.modelRevision++
                                                    }"""
assert old_lock_click in content, "old_lock_click not found"
content = content.replace(old_lock_click, new_lock_click)

# 5. Update text in delegate
old_text = 'text: (modelData && modelData.name) ? modelData.name : "Entity"'
new_text = 'text: (currentShape && currentShape.name) ? currentShape.name : "Entity"'
assert old_text in content, "old_text not found"
content = content.replace(old_text, new_text)

# 6. Add Entity Name input field right above Position/Size
old_pos_hdr = """                            // Header: Position | Size [MM] | Actions
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8"""

new_pos_hdr = """                            // Selected Entity Name Edit Box
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: root.selectedShape !== null

                                CadInput {
                                    id: entityNameInput
                                    Layout.fillWidth: true
                                    label: "Entity Name"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    text: root.selectedShape ? (root.selectedShape.name || "") : ""
                                    onEditingFinished: {
                                        if (root.selectedShape && root.selectedIndex >= 0) {
                                            var newN = text.trim()
                                            if (newN.length > 0 && newN !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, newN)
                                                root.modelRevision++
                                            }
                                        }
                                    }
                                }
                            }

                            // Header: Position | Size [MM] | Actions
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8"""

assert old_pos_hdr in content, "old_pos_hdr not found"
content = content.replace(old_pos_hdr, new_pos_hdr)

with open("qml/components/cad/CadInspectorPanel.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated CadInspectorPanel.qml")

