# 1. Patch CadHatchModal.qml
with open('qml/components/cad/CadHatchModal.qml', 'r', encoding='utf-8') as f:
    hatch_content = f.read()

old_open = """        if (shp && shp.hatch_profiles) {
            for (var k in shp.hatch_profiles) {
                if (profiles[k]) {
                    profiles[k] = Object.assign({}, shp.hatch_profiles[k])
                }
            }
            if (shp.mark_contour !== undefined) markContour = shp.mark_contour
            if (shp.mark_contour_first !== undefined) markContourFirst = shp.mark_contour_first
        }"""

new_open = """        if (shp && shp.hatch_profiles) {
            for (var k in shp.hatch_profiles) {
                if (profiles[k]) {
                    profiles[k] = Object.assign({}, shp.hatch_profiles[k])
                }
            }
            if (shp.mark_contour !== undefined) markContour = shp.mark_contour
            if (shp.mark_contour_first !== undefined) markContourFirst = shp.mark_contour_first
        } else if (shp && shp.penId !== undefined && shp.penId > 0) {
            for (var pk in profiles) {
                profiles[pk].pen_no = shp.penId
            }
        }"""

if old_open in hatch_content:
    hatch_content = hatch_content.replace(old_open, new_open, 1)
    print("Updated CadHatchModal openModal fallback")
else:
    print("WARNING: old_open not found in CadHatchModal")

old_pen_selector = "penSelector.selectedPenId = (p.pen_no !== undefined && p.pen_no >= 0 && p.pen_no < 8) ? p.pen_no : 0"
new_pen_selector = """penSelector.selectedPenId = (p.pen_no !== undefined && p.pen_no > 0)
            ? p.pen_no
            : ((targetShape && targetShape.penId !== undefined && targetShape.penId > 0) ? targetShape.penId : 0)"""

if old_pen_selector in hatch_content:
    hatch_content = hatch_content.replace(old_pen_selector, new_pen_selector, 1)
    print("Updated CadHatchModal penSelector logic")
else:
    print("WARNING: old_pen_selector not found in CadHatchModal")

with open('qml/components/cad/CadHatchModal.qml', 'w', encoding='utf-8') as f:
    f.write(hatch_content)
print("Saved CadHatchModal.qml")

# 2. Patch CadInspectorPanel.qml
with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    insp_content = f.read()

old_assign = """                    // Apply Pen to selection
                    CadButton {
                        Layout.fillWidth: true
                        text: "Assign Pen " + root.selectedPenId + " to Selected Shape"
                        variant: "outline"
                        onClicked: {
                            if (root.selectedShape) {
                                root.selectedShape.penId = root.selectedPenId
                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                            }
                        }
                    }"""

new_assign = """                    // Apply Pen to selection
                    CadButton {
                        Layout.fillWidth: true
                        text: "Assign Pen " + root.selectedPenId + " to Selected Shape"
                        variant: "outline"
                        onClicked: {
                            if (root.selectedShape) {
                                root.selectedShape.penId = root.selectedPenId
                                if (root.selectedShape.hatch_profiles) {
                                    for (var hk in root.selectedShape.hatch_profiles) {
                                        root.selectedShape.hatch_profiles[hk].pen_no = root.selectedPenId
                                    }
                                }
                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                            }
                        }
                    }"""

if old_assign in insp_content:
    insp_content = insp_content.replace(old_assign, new_assign, 1)
    print("Updated CadInspectorPanel Assign Pen button to update hatch_profiles")
else:
    print("WARNING: old_assign not found in CadInspectorPanel")

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(insp_content)
print("Saved CadInspectorPanel.qml")

