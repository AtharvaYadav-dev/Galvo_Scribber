with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    text = f.read()

old_mod = """                    onShapeModified: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                        }
                        cadCanvas.shapesChanged()
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.requestPaint()
                    }"""

new_mod = """                    onShapeModified: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                        }
                        if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length && shp) {
                            var copy = cadCanvas.shapes.slice()
                            copy[cadCanvas.selectedIndex] = shp
                            cadCanvas.shapes = copy
                        }
                        cadCanvas.shapesChanged()
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.requestPaint()
                    }"""

old_app = """                    onApplyTriggered: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                        }
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.shapesChanged()
                        cadCanvas.requestPaint()
                    }"""

new_app = """                    onApplyTriggered: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                        }
                        if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length && shp) {
                            var copy2 = cadCanvas.shapes.slice()
                            copy2[cadCanvas.selectedIndex] = shp
                            cadCanvas.shapes = copy2
                        }
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.shapesChanged()
                        cadCanvas.requestPaint()
                    }"""

assert old_mod in text, "old_mod not found"
assert old_app in text, "old_app not found"

text = text.replace(old_mod, new_mod, 1)
text = text.replace(old_app, new_app, 1)

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated CadView.qml onShapeModified and onApplyTriggered")

