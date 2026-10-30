with open("qml/components/cad/CadInspectorPanel.qml", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the duplicate block
duplicate_block = """                            // Selected Entity Name Edit Box
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

"""

if duplicate_block in content:
    content = content.replace(duplicate_block, "")
    print("Removed duplicate block")

# Update line 618 to add modelRevision++
old_rename = """                                            if (root.selectedShape && text.trim().length > 0 && text.trim() !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, text.trim())
                                            }"""

new_rename = """                                            if (root.selectedShape && text.trim().length > 0 && text.trim() !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, text.trim())
                                                root.modelRevision++
                                            }"""

content = content.replace(old_rename, new_rename)

with open("qml/components/cad/CadInspectorPanel.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated CadInspectorPanel.qml successfully")

