with open('qml/components/cad/CadHatchModal.qml', 'r', encoding='utf-8') as f:
    content = f.read()

old_hatch_pen = 'color: (typeof Theme !== "undefined" && Theme.penPalette) ? Theme.penPalette[penSelector.selectedPenId].color : "#000000"'
new_hatch_pen = 'color: (typeof Theme !== "undefined" && Theme.getPenColor) ? Theme.getPenColor(penSelector.selectedPenId) : "#000000"'

if old_hatch_pen in content:
    content = content.replace(old_hatch_pen, new_hatch_pen, 1)
    with open('qml/components/cad/CadHatchModal.qml', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated CadHatchModal.qml pen color lookup")
else:
    print("WARNING: old_hatch_pen not found")

