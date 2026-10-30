with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add onOpenColorPickerRequested to inspector
old_inspector_pen = """                    onPenChanged: function(pId) {
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

new_inspector_pen = """                    onPenChanged: function(pId) {
                        if (inspector.selectedShape) {
                            inspector.selectedShape.penId = pId
                            inspector.selectedShape.hatch_lines = []
                            cadCanvas.shapesChanged()
                            if (typeof cad !== "undefined" && cad) {
                                cad.updateShapes(cadCanvas.shapes)
                            }
                            cadCanvas.requestPaint()
                        }
                    }
                    onOpenColorPickerRequested: function(penId, color, name) {
                        colorPickerModal.openModal(penId, color, name)
                    }"""

if old_inspector_pen.replace('\n', '\r\n') in content:
    content = content.replace(old_inspector_pen.replace('\n', '\r\n'), new_inspector_pen.replace('\n', '\r\n'), 1)
    print("Added onOpenColorPickerRequested (CRLF)")
elif old_inspector_pen in content:
    content = content.replace(old_inspector_pen, new_inspector_pen, 1)
    print("Added onOpenColorPickerRequested (LF)")
else:
    print("WARNING: old_inspector_pen not found!")

# 2. Add CadColorPickerModal declaration
old_end = """    // EZCad Advance Variable Text Modal
    CadVariableTextModal {
        id: variableTextModal
        onVariableSettingsConfirmed: function(enabled, entitiesList, fixedWidth, fixedWidthVal) {
            var target = inspector.selectedShape
            if (target) {
                target.enableVariableText = enabled
                target.variableEntities = JSON.parse(JSON.stringify(entitiesList))
                target.enableFixedWidth = fixedWidth
                target.fixedWidthMm = fixedWidthVal
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
            }
        }
    }"""

new_end = """    // EZCad Advance Variable Text Modal
    CadVariableTextModal {
        id: variableTextModal
        onVariableSettingsConfirmed: function(enabled, entitiesList, fixedWidth, fixedWidthVal) {
            var target = inspector.selectedShape
            if (target) {
                target.enableVariableText = enabled
                target.variableEntities = JSON.parse(JSON.stringify(entitiesList))
                target.enableFixedWidth = fixedWidth
                target.fixedWidthMm = fixedWidthVal
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
            }
        }
    }

    // Laser Pen Color Palette & Configuration Modal
    CadColorPickerModal {
        id: colorPickerModal
        onColorConfirmed: function(penId, newColor, newName) {
            Theme.updatePenColor(penId, newColor)
            if (newName && newName.length > 0) {
                Theme.updatePenParam(penId, "name", newName)
            }
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(cadCanvas.shapes)
            }
            cadCanvas.shapesChanged()
            cadCanvas.requestPaint()
        }
    }"""

if old_end.replace('\n', '\r\n') in content:
    content = content.replace(old_end.replace('\n', '\r\n'), new_end.replace('\n', '\r\n'), 1)
    print("Added CadColorPickerModal (CRLF)")
elif old_end in content:
    content = content.replace(old_end, new_end, 1)
    print("Added CadColorPickerModal (LF)")
else:
    print("WARNING: old_end not found!")

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved qml/views/CadView.qml")

