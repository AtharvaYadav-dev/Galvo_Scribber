with open("qml/components/cad/CadTopCommandBar.qml", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update root properties
old_props = """    property alias themeToggleEnabled: themeBtn.visible
    property bool hasSelection: false
    property bool isSelectionLocked: false"""

new_props = """    property alias themeToggleEnabled: themeBtn.visible
    property bool hasSelection: false
    property bool isSelectionLocked: false
    property bool canUndo: false
    property bool canRedo: false
    property bool isSelectionGroup: false
    property int totalShapesCount: 0"""

assert old_props in content, "old_props not found"
content = content.replace(old_props, new_props)

# 2. Update Undo and Redo buttons
old_undo_redo = """        // History Actions
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "undo"
                tooltipText: "Undo last edit (Ctrl+Z)"
                onClicked: root.undoTriggered()
            }
            CadButton {
                iconName: "redo"
                tooltipText: "Redo last edit (Ctrl+Y)"
                onClicked: root.redoTriggered()
            }
        }"""

new_undo_redo = """        // History Actions
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "undo"
                tooltipText: "Undo last edit (Ctrl+Z)"
                enabled: root.canUndo
                onClicked: root.undoTriggered()
            }
            CadButton {
                iconName: "redo"
                tooltipText: "Redo last edit (Ctrl+Y)"
                enabled: root.canRedo
                onClicked: root.redoTriggered()
            }
        }"""

assert old_undo_redo in content, "old_undo_redo not found"
content = content.replace(old_undo_redo, new_undo_redo)

# 3. Update Group and Ungroup buttons
old_group = """            CadButton {
                iconName: "group_work"
                tooltipText: !root.hasSelection ? "Group (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Group selected objects")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.groupTriggered()
            }
            CadButton {
                iconName: "layers_clear"
                tooltipText: !root.hasSelection ? "Ungroup (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Ungroup selection")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.ungroupTriggered()
            }"""

new_group = """            CadButton {
                iconName: "group_work"
                tooltipText: (root.totalShapesCount < 2) ? "Group (Requires 2+ objects on canvas)" : "Group all objects into unified group (Ctrl+G)"
                enabled: root.totalShapesCount >= 2 && !root.isSelectionLocked
                onClicked: root.groupTriggered()
            }
            CadButton {
                iconName: "layers_clear"
                tooltipText: !root.isSelectionGroup ? "Ungroup (Select a group entity first)" : "Ungroup selected group into individual objects (Ctrl+Shift+G)"
                enabled: root.isSelectionGroup && !root.isSelectionLocked
                onClicked: root.ungroupTriggered()
            }"""

assert old_group in content, "old_group not found"
content = content.replace(old_group, new_group)

with open("qml/components/cad/CadTopCommandBar.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated CadTopCommandBar.qml successfully")

