with open("qml/views/CadView.qml", "r", encoding="utf-8") as f:
    content = f.read()

old_bar = """            // 1. Top Unified Command Ribbon
            CadTopCommandBar {
                Layout.fillWidth: true
                hasSelection: cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length
                isSelectionLocked: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].locked)
                onOpenFileDialogTriggered: importFileDialog.open()
                onHatchTriggered: {
                    if (cadCanvas.selectedIndex >= 0) {
                        hatchModal.openModal(inspector.selectedShape)
                    }
                }
                onAlignTriggered: function(mode) {
                    cadCanvas.alignSelectedShape(mode)
                }
                onZoomInTriggered: cadCanvas.zoomIn()
                onZoomOutTriggered: cadCanvas.zoomOut()
                onZoomFitTriggered: cadCanvas.zoomFit()
                onCenterToBedTriggered: cadCanvas.centerSelectedShape()
                onFitToFieldTriggered: cadCanvas.fitSelectionToField()
                onUndoTriggered: console.log("[CAD] Undo triggered")
                onRedoTriggered: console.log("[CAD] Redo triggered")
                onGroupTriggered: console.log("[CAD] Group triggered")
                onUngroupTriggered: console.log("[CAD] Ungroup triggered")
            }"""

new_bar = """            // 1. Top Unified Command Ribbon
            CadTopCommandBar {
                Layout.fillWidth: true
                hasSelection: cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length
                isSelectionLocked: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].locked)
                canUndo: cadCanvas.canUndo
                canRedo: cadCanvas.canRedo
                isSelectionGroup: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].type === "group")
                totalShapesCount: cadCanvas.shapes.length

                onOpenFileDialogTriggered: importFileDialog.open()
                onHatchTriggered: {
                    if (cadCanvas.selectedIndex >= 0) {
                        hatchModal.openModal(inspector.selectedShape)
                    }
                }
                onAlignTriggered: function(mode) {
                    cadCanvas.alignSelectedShape(mode)
                }
                onZoomInTriggered: cadCanvas.zoomIn()
                onZoomOutTriggered: cadCanvas.zoomOut()
                onZoomFitTriggered: cadCanvas.zoomFit()
                onCenterToBedTriggered: cadCanvas.centerSelectedShape()
                onFitToFieldTriggered: cadCanvas.fitSelectionToField()
                onUndoTriggered: cadCanvas.undo()
                onRedoTriggered: cadCanvas.redo()
                onGroupTriggered: cadCanvas.groupSelectedShapes()
                onUngroupTriggered: cadCanvas.ungroupSelectedShape()
            }"""

assert old_bar in content, "old_bar not found in CadView.qml"
content = content.replace(old_bar, new_bar)

# Also connect cadCanvas onHatchTriggered
old_canvas = """                        CadCanvas {
                            id: cadCanvas
                            Layout.fillWidth: true
                            Layout.fillHeight: true"""

new_canvas = """                        CadCanvas {
                            id: cadCanvas
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            onHatchTriggered: function(shp) {
                                hatchModal.openModal(shp)
                            }"""

if old_canvas in content:
    content = content.replace(old_canvas, new_canvas)

with open("qml/views/CadView.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated CadView.qml successfully")

