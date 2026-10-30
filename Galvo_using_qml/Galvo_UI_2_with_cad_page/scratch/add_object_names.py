# 1. Add objectName: "inspector" to CadView.qml
with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    cv = f.read()
cv = cv.replace(
    '                CadInspectorPanel {\n                    id: inspector\n                    Layout.fillHeight: true',
    '                CadInspectorPanel {\n                    id: inspector\n                    objectName: "inspector"\n                    Layout.fillHeight: true'
)
with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(cv)

# 2. Add objectName: "fontFamilyCombo" in CadInspectorPanel.qml
with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    cip = f.read()
cip = cip.replace(
    '                            CadComboBox {\n                                id: fontFamilyCombo\n                                Layout.fillWidth: true',
    '                            CadComboBox {\n                                id: fontFamilyCombo\n                                objectName: "fontFamilyCombo"\n                                Layout.fillWidth: true'
)
with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(cip)

# 3. Add objectName: "modalFontCombo" in CadTextFontModal.qml
with open('qml/components/cad/CadTextFontModal.qml', 'r', encoding='utf-8') as f:
    ctm = f.read()
ctm = ctm.replace(
    '                            CadComboBox {\n                                id: modalFontCombo\n                                Layout.fillWidth: true',
    '                            CadComboBox {\n                                id: modalFontCombo\n                                objectName: "modalFontCombo"\n                                Layout.fillWidth: true'
)
with open('qml/components/cad/CadTextFontModal.qml', 'w', encoding='utf-8') as f:
    f.write(ctm)

print("Added objectNames successfully")

