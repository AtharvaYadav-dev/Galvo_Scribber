with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('onTextTriggered:')
s2 = text.find('onImportTriggered:')
print("onTextTriggered block:")
print(text[s1:s2])

s3 = text.find('CadBarcodeModal {')
s4 = text.find('CadTextFontModal {')
print("CadBarcodeModal block:")
print(text[s3:s4])

