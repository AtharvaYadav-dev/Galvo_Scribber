import os

# 1. Patch CadInspectorPanel.qml
inspector_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadInspectorPanel.qml"
with open(inspector_path, "r", encoding="utf-8") as f:
    insp_text = f.read().replace("\r\n", "\n")

# syncSelectedShape
target_sync = """    function syncSelectedShape() {
        if (selectedIndex >= 0 && shapesModel && selectedIndex < shapesModel.length) {
            selectedShape = shapesModel[selectedIndex]
        } else {
            selectedShape = null
        }
    }"""

repl_sync = """    function syncSelectedShape() {
        if (selectedIndex >= 0 && shapesModel && selectedIndex < shapesModel.length) {
            selectedShape = shapesModel[selectedIndex]
            if (selectedShape && selectedShape.penId !== undefined) {
                selectedPenId = selectedShape.penId
            }
        } else {
            selectedShape = null
        }
    }"""

if target_sync in insp_text:
    insp_text = insp_text.replace(target_sync, repl_sync, 1)
    print("Successfully patched syncSelectedShape in CadInspectorPanel.qml")
else:
    print("WARNING: target_sync not found in CadInspectorPanel.qml")

# updateTransformInputs
target_trans = """    function updateTransformInputs() {
        if (!root.selectedShape) {
            inputX.text = "0.000"
            inputY.text = "0.000"
            inputW.text = "0.000"
            inputH.text = "0.000"
            inputRot.text = "0"
            inputZ.text = "0.000"
            return
        }"""

repl_trans = """    function updateTransformInputs() {
        if (!root.selectedShape) {
            inputX.text = "0.000"
            inputY.text = "0.000"
            inputW.text = "0.000"
            inputH.text = "0.000"
            inputRot.text = "0"
            inputZ.text = "0.000"
            return
        }
        if (root.selectedShape.penId !== undefined) {
            root.selectedPenId = root.selectedShape.penId
        }"""

if target_trans in insp_text:
    insp_text = insp_text.replace(target_trans, repl_trans, 1)
    print("Successfully patched updateTransformInputs in CadInspectorPanel.qml")
else:
    print("WARNING: target_trans not found in CadInspectorPanel.qml")

# penMa onClicked
target_pen_ma = """                                    onClicked: {
                                        root.selectedPenId = modelData.id
                                        root.penChanged(modelData.id)
                                        speedSlider.value = modelData.speed
                                        powerSlider.value = modelData.power
                                        freqSlider.value = modelData.freq
                                    }"""

repl_pen_ma = """                                    onClicked: {
                                        root.selectedPenId = modelData.id
                                        if (root.selectedShape) {
                                            root.selectedShape.penId = modelData.id
                                            if (root.selectedShape.hatch_profiles) {
                                                for (var hk in root.selectedShape.hatch_profiles) {
                                                    root.selectedShape.hatch_profiles[hk].pen_no = modelData.id
                                                }
                                            }
                                            root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                        root.penChanged(modelData.id)
                                        speedSlider.value = modelData.speed
                                        powerSlider.value = modelData.power
                                        freqSlider.value = modelData.freq
                                    }"""

if target_pen_ma in insp_text:
    insp_text = insp_text.replace(target_pen_ma, repl_pen_ma, 1)
    print("Successfully patched penMa onClicked in CadInspectorPanel.qml")
else:
    print("WARNING: target_pen_ma not found in CadInspectorPanel.qml")

# Assign Pen button
target_btn = """                    CadButton {
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

repl_btn = """                    CadButton {
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
                                root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                                root.penChanged(root.selectedPenId)
                            }
                        }
                    }"""

if target_btn in insp_text:
    insp_text = insp_text.replace(target_btn, repl_btn, 1)
    print("Successfully patched Assign Pen button in CadInspectorPanel.qml")
else:
    print("WARNING: target_btn not found in CadInspectorPanel.qml")

with open(inspector_path, "w", encoding="utf-8") as f:
    f.write(insp_text)

# 2. Patch CadView.qml
cad_view_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\views\CadView.qml"
with open(cad_view_path, "r", encoding="utf-8") as f:
    view_text = f.read().replace("\r\n", "\n")

target_view_pen = """                    onPenChanged: function(pId) {
                        if (inspector.selectedShape) {
                            inspector.selectedShape.penId = pId
                            inspector.selectedShape.hatch_lines = []
                            cadCanvas.shapesChanged()
                            if (typeof cad !== "undefined" && cad) {
                                cad.updateShapes(cadCanvas.shapes)
                            }
                            cadCanvas.requestPaint()
                        }
                    }"""

repl_view_pen = """                    onPenChanged: function(pId) {
                        if (inspector.selectedShape && cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                            var target = inspector.selectedShape
                            target.penId = pId
                            if (target.hatch_profiles) {
                                for (var hk in target.hatch_profiles) {
                                    target.hatch_profiles[hk].pen_no = pId
                                }
                            }
                            target.hatch_lines = []
                            var copy = cadCanvas.shapes.slice()
                            copy[cadCanvas.selectedIndex] = target
                            cadCanvas.shapes = copy
                            cadCanvas.shapesChanged()
                            if (typeof cad !== "undefined" && cad) {
                                cad.updateShapes(cadCanvas.shapes)
                            }
                            cadCanvas.requestPaint()
                        }
                    }"""

if target_view_pen in view_text:
    view_text = view_text.replace(target_view_pen, repl_view_pen, 1)
    print("Successfully patched onPenChanged in CadView.qml")
else:
    print("WARNING: target_view_pen not found in CadView.qml")

target_view_hatch = """        onApplyHatch: function(profs, markContour, markContourFirst) {
            var target = inspector.selectedShape
            if (target) {
                target.hatched = true
                target.mark_contour = markContour
                target.mark_contour_first = markContourFirst
                target.hatch_profiles = JSON.parse(JSON.stringify(profs))
                if (typeof cad !== "undefined" && cad) {
                    target.hatch_lines = cad.computeHatchPreviewLines(target)
                }
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
            }
        }"""

repl_view_hatch = """        onApplyHatch: function(profs, markContour, markContourFirst) {
            var target = inspector.selectedShape
            if (target) {
                target.hatched = true
                target.mark_contour = markContour
                target.mark_contour_first = markContourFirst
                target.hatch_profiles = JSON.parse(JSON.stringify(profs))
                if (typeof cad !== "undefined" && cad) {
                    target.hatch_lines = cad.computeHatchPreviewLines(target)
                }
                if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                    var copyH = cadCanvas.shapes.slice()
                    copyH[cadCanvas.selectedIndex] = target
                    cadCanvas.shapes = copyH
                }
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
            }
        }"""

if target_view_hatch in view_text:
    view_text = view_text.replace(target_view_hatch, repl_view_hatch, 1)
    print("Successfully patched onApplyHatch in CadView.qml")
else:
    print("WARNING: target_view_hatch not found in CadView.qml")

with open(cad_view_path, "w", encoding="utf-8") as f:
    f.write(view_text)

print("Inspector and CadView patched successfully.")

