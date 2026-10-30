with open("qml/components/cad/CadInspectorPanel.qml", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace('iconName: "refresh"\n', '')
text = text.replace('iconName: "refresh"\r\n', '')
text = text.replace('iconName: "file_download"\n', '')
text = text.replace('iconName: "file_download"\r\n', '')

with open("qml/components/cad/CadInspectorPanel.qml", "w", encoding="utf-8") as f:
    f.write(text)

with open("qml/components/cad/CadBarcodeModal.qml", "r", encoding="utf-8") as f:
    mtext = f.read()

mtext = mtext.replace('iconName: "file_download"\n', '')
mtext = mtext.replace('iconName: "file_download"\r\n', '')

with open("qml/components/cad/CadBarcodeModal.qml", "w", encoding="utf-8") as f:
    f.write(mtext)

print("Icons cleaned successfully.")

