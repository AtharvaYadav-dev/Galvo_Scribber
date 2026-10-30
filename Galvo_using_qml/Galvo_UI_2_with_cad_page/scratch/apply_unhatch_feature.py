import os

# 1. Update CadCanvas.qml
canvas_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadCanvas.qml"
with open(canvas_path, "r", encoding="utf-8") as f:
    canvas_text = f.read().replace("\r\n", "\n")

# Add unhatchSelectedShape function after rotateSelectedShape
target_rotate = """    function rotateSelectedShape(deg) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            s.rotation = (s.rotation + deg) % 360
            shapesChanged()
            shapeModified(s)
            canvas.requestPaint()
        }
    }"""

repl_rotate = """    function rotateSelectedShape(deg) {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            s.rotation = (s.rotation + deg) % 360
            shapesChanged()
            shapeModified(s)
            canvas.requestPaint()
        }
    }

    function unhatchSelectedShape() {
        if (selectedIndex >= 0 && selectedIndex < shapes.length) {
            var s = shapes[selectedIndex]
            if (s.locked === true) {
                if (typeof cad !== "undefined" && cad) {
                    cad.set_status_message("Cannot unhatch locked object '" + (s.name || "Object") + "'. Unlock it first.")
                }
                return
            }
            pushUndoState()
            s.hatched = false
            s.hatch_lines = []
            var copy = shapes.slice()
            copy[selectedIndex] = s
            shapes = copy
            shapesChanged()
            shapeModified(s)
            shapeSelected(s)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(shapes)
                cad.set_status_message("Removed hatch infill from '" + (s.name || "Object") + "'.")
            }
            canvas.requestPaint()
        }
    }"""

if target_rotate in canvas_text:
    canvas_text = canvas_text.replace(target_rotate, repl_rotate, 1)
    print("Added unhatchSelectedShape to CadCanvas.qml")
else:
    print("WARNING: target_rotate not found in CadCanvas.qml")

# Add Remove Hatch button to floating HUD row
target_hud = """            readonly property bool isLocked: (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length && root.shapes[root.selectedIndex]) ? Boolean(root.shapes[root.selectedIndex].locked) : false

            CadButton {
                iconName: "rotate_90_degrees_cw"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Rotate 90° Clockwise"
                enabled: !hudRow.isLocked
                onClicked: root.rotateSelectedShape(90)
            }
            CadButton {
                iconName: "content_copy"
                tooltipText: "Duplicate Object"
                onClicked: root.duplicateSelectedShape()
            }
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Center to Galvo Origin (0,0)"
                enabled: !hudRow.isLocked
                onClicked: root.centerSelectedShape()
            }
            CadButton {
                iconName: "delete"
                variant: "danger"
                tooltipText: hudRow.isLocked ? "Object is locked (Unlock to delete)" : "Delete Object"
                enabled: !hudRow.isLocked
                onClicked: root.deleteSelectedShape()
            }"""

repl_hud = """            readonly property bool isLocked: (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length && root.shapes[root.selectedIndex]) ? Boolean(root.shapes[root.selectedIndex].locked) : false
            readonly property bool isHatched: (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length && root.shapes[root.selectedIndex]) ? Boolean(root.shapes[root.selectedIndex].hatched) : false

            CadButton {
                iconName: "rotate_90_degrees_cw"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Rotate 90° Clockwise"
                enabled: !hudRow.isLocked
                onClicked: root.rotateSelectedShape(90)
            }
            CadButton {
                iconName: "content_copy"
                tooltipText: "Duplicate Object"
                onClicked: root.duplicateSelectedShape()
            }
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Center to Galvo Origin (0,0)"
                enabled: !hudRow.isLocked
                onClicked: root.centerSelectedShape()
            }
            CadButton {
                visible: hudRow.isHatched
                iconName: "layers_clear"
                tooltipText: hudRow.isLocked ? "Object is locked" : "Remove Hatch (Unhatch Object)"
                enabled: !hudRow.isLocked
                variant: "outline"
                onClicked: root.unhatchSelectedShape()
            }
            CadButton {
                iconName: "delete"
                variant: "danger"
                tooltipText: hudRow.isLocked ? "Object is locked (Unlock to delete)" : "Delete Object"
                enabled: !hudRow.isLocked
                onClicked: root.deleteSelectedShape()
            }"""

if target_hud in canvas_text:
    canvas_text = canvas_text.replace(target_hud, repl_hud, 1)
    print("Added Remove Hatch button to floating HUD in CadCanvas.qml")
else:
    print("WARNING: target_hud not found in CadCanvas.qml")

with open(canvas_path, "w", encoding="utf-8") as f:
    f.write(canvas_text)


# 2. Update CadInspectorPanel.qml
inspector_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadInspectorPanel.qml"
with open(inspector_path, "r", encoding="utf-8") as f:
    insp_text = f.read().replace("\r\n", "\n")

# Add unhatchTriggered signal
target_sig = "    signal hatchTriggered(var shape)"
repl_sig = """    signal hatchTriggered(var shape)
    signal unhatchTriggered(var shape)"""

if target_sig in insp_text:
    insp_text = insp_text.replace(target_sig, repl_sig, 1)
    print("Added unhatchTriggered signal to CadInspectorPanel.qml")
else:
    print("WARNING: target_sig not found in CadInspectorPanel.qml")

# Add Hatch Action Controls right above EZCad Action Toolbar
target_ezcad_bar = """                    // 3. EZCad Action Toolbar (Array, Input Port, Apply)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: root.selectedShape !== null"""

repl_ezcad_bar = """                    // Hatch Infill Action Controls
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: root.selectedShape !== null

                        CadButton {
                            Layout.fillWidth: true
                            implicitHeight: 30
                            text: (root.selectedShape && root.selectedShape.hatched) ? "Hatch Settings (H)" : "Apply Hatch (H)"
                            iconName: "texture"
                            variant: (root.selectedShape && root.selectedShape.hatched) ? "outline" : "secondary"
                            tooltipText: "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.hatchTriggered(root.selectedShape)
                                }
                            }
                        }

                        CadButton {
                            visible: Boolean(root.selectedShape && root.selectedShape.hatched)
                            Layout.fillWidth: true
                            implicitHeight: 30
                            text: "Remove Hatch"
                            iconName: "layers_clear"
                            variant: "danger"
                            tooltipText: "Remove hatch infill lines from selected object"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.unhatchTriggered(root.selectedShape)
                                }
                            }
                        }
                    }

                    // 3. EZCad Action Toolbar (Array, Input Port, Apply)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: root.selectedShape !== null"""

if target_ezcad_bar in insp_text:
    insp_text = insp_text.replace(target_ezcad_bar, repl_ezcad_bar, 1)
    print("Added Hatch Action Controls to CadInspectorPanel.qml")
else:
    print("WARNING: target_ezcad_bar not found in CadInspectorPanel.qml")

with open(inspector_path, "w", encoding="utf-8") as f:
    f.write(insp_text)


# 3. Update CadTopCommandBar.qml
topbar_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadTopCommandBar.qml"
with open(topbar_path, "r", encoding="utf-8") as f:
    topbar_text = f.read().replace("\r\n", "\n")

target_top_sig = "    signal hatchTriggered()"
repl_top_sig = """    signal hatchTriggered()
    signal unhatchTriggered()
    property bool isSelectionHatched: false"""

if target_top_sig in topbar_text:
    topbar_text = topbar_text.replace(target_top_sig, repl_top_sig, 1)
    print("Added unhatchTriggered signal and isSelectionHatched to CadTopCommandBar.qml")
else:
    print("WARNING: target_top_sig not found in CadTopCommandBar.qml")

target_top_hatch = """        // Hatch Tool Trigger (Accessible only when an object is selected)
        CadButton {
            iconName: "texture"
            text: "Hatch (H)"
            variant: "accent"
            tooltipText: !root.hasSelection ? "Laser Hatching (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)")
            enabled: root.hasSelection && !root.isSelectionLocked
            onClicked: root.hatchTriggered()
        }"""

repl_top_hatch = """        // Hatch & Unhatch Tools (Accessible only when an object is selected)
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "texture"
                text: "Hatch (H)"
                variant: (root.hasSelection && root.isSelectionHatched) ? "outline" : "accent"
                tooltipText: !root.hasSelection ? "Laser Hatching (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.hatchTriggered()
            }

            CadButton {
                visible: root.hasSelection && root.isSelectionHatched
                iconName: "layers_clear"
                text: "Unhatch"
                variant: "secondary"
                tooltipText: "Remove hatch infill from selected object (Shift+H)"
                enabled: !root.isSelectionLocked
                onClicked: root.unhatchTriggered()
            }
        }"""

if target_top_hatch in topbar_text:
    topbar_text = topbar_text.replace(target_top_hatch, repl_top_hatch, 1)
    print("Added Unhatch button to CadTopCommandBar.qml")
else:
    print("WARNING: target_top_hatch not found in CadTopCommandBar.qml")

with open(topbar_path, "w", encoding="utf-8") as f:
    f.write(topbar_text)


# 4. Update CadView.qml
view_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\views\CadView.qml"
with open(view_path, "r", encoding="utf-8") as f:
    view_text = f.read().replace("\r\n", "\n")

target_view_top = """                onGroupTriggered: cadCanvas.groupSelectedShapes()
                onUngroupTriggered: cadCanvas.ungroupSelectedShape()
            }"""

repl_view_top = """                onGroupTriggered: cadCanvas.groupSelectedShapes()
                onUngroupTriggered: cadCanvas.ungroupSelectedShape()
                isSelectionHatched: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].hatched)
                onUnhatchTriggered: cadCanvas.unhatchSelectedShape()
            }"""

if target_view_top in view_text:
    view_text = view_text.replace(target_view_top, repl_view_top, 1)
    print("Connected onUnhatchTriggered and isSelectionHatched in CadView.qml")
else:
    print("WARNING: target_view_top not found in CadView.qml")

target_insp_conn = """                    onHatchTriggered: function(shp) {
                        hatchModal.openModal(shp)
                    }"""

repl_insp_conn = """                    onHatchTriggered: function(shp) {
                        hatchModal.openModal(shp)
                    }
                    onUnhatchTriggered: function(shp) {
                        cadCanvas.unhatchSelectedShape()
                    }"""

if target_insp_conn in view_text:
    view_text = view_text.replace(target_insp_conn, repl_insp_conn, 1)
    print("Connected inspector.onUnhatchTriggered in CadView.qml")
else:
    print("WARNING: target_insp_conn not found in CadView.qml")

# Update onUndoHatch to use cadCanvas.unhatchSelectedShape()
target_undo_hatch = """        onUndoHatch: function() {
            var target = inspector.selectedShape
            if (target) {
                target.hatched = false
                target.hatch_lines = []
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
            }
        }"""

repl_undo_hatch = """        onUndoHatch: function() {
            cadCanvas.unhatchSelectedShape()
        }"""

if target_undo_hatch in view_text:
    view_text = view_text.replace(target_undo_hatch, repl_undo_hatch, 1)
    print("Updated onUndoHatch in CadView.qml")
else:
    print("WARNING: target_undo_hatch not found in CadView.qml")

# Add Shift+H Shortcut to CadView.qml
target_shortcuts_end = """    function triggerAbort() {
        if (typeof cad !== "undefined" && cad) {
            cad.abortMark()
        }
    }"""

repl_shortcuts_end = """    function triggerAbort() {
        if (typeof cad !== "undefined" && cad) {
            cad.abortMark()
        }
    }

    Shortcut {
        sequence: "Shift+H"
        onActivated: {
            if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                cadCanvas.unhatchSelectedShape()
            }
        }
    }

    Shortcut {
        sequence: "H"
        onActivated: {
            if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                hatchModal.openModal(inspector.selectedShape)
            }
        }
    }"""

if target_shortcuts_end in view_text:
    view_text = view_text.replace(target_shortcuts_end, repl_shortcuts_end, 1)
    print("Added Shift+H and H shortcuts to CadView.qml")
else:
    print("WARNING: target_shortcuts_end not found in CadView.qml")

with open(view_path, "w", encoding="utf-8") as f:
    f.write(view_text)

print("\nAll unhatch features applied successfully!")

