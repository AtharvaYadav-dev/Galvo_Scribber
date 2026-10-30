import os

inspector_path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadInspectorPanel.qml"
with open(inspector_path, "r", encoding="utf-8") as f:
    text = f.read().replace("\r\n", "\n")

target = """                TabBar {
                    id: tabGroup
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: 0"""

replacement = """                TabBar {
                    id: tabGroup
                    objectName: "inspectorTabGroup"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: 0"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(inspector_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully added objectName to tabGroup")
else:
    print("Target not found")

