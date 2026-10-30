with open("qml/views/CadView.qml", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'CadBarcodeModal {\n        id: barcodeModal\n        visible: false',
    'CadBarcodeModal {\n        id: barcodeModal\n        objectName: "barcodeModal"\n        visible: false'
)
text = text.replace(
    'CadBarcodeModal {\r\n        id: barcodeModal\r\n        visible: false',
    'CadBarcodeModal {\r\n        id: barcodeModal\r\n        objectName: "barcodeModal"\r\n        visible: false'
)

with open("qml/views/CadView.qml", "w", encoding="utf-8") as f:
    f.write(text)

print("Added objectName: barcodeModal")

