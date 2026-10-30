with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    content = f.read()

old_dot = "color: Theme.penPalette[((currentShape && currentShape.penId) || 0) % Theme.penPalette.length].color"
new_dot = "color: Theme.getPenColor((currentShape && currentShape.penId) || 0)"

if old_dot in content:
    content = content.replace(old_dot, new_dot, 1)
    with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated entity list pen dot color to Theme.getPenColor")
else:
    print("WARNING: old_dot not found")

