with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                        // Main Vector Canvas
                        CadCanvas {
                            id: cadCanvas
                            objectName: "cadCanvas"
                            Layout.fillWidth: true
                            Layout.fillHeight: true"""

replacement = """                        // Main Vector Canvas
                        CadCanvas {
                            id: cadCanvas
                            objectName: "cadCanvas"
                            currentPenId: inspector.selectedPenId
                            Layout.fillWidth: true
                            Layout.fillHeight: true"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Bound cadCanvas.currentPenId to inspector.selectedPenId")
else:
    print("WARNING: target not found in CadView.qml")

