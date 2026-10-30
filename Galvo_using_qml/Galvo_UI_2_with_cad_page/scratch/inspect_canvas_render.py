with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('                } else if (shp.type === "qrcode") {')
s2 = text.find('                } else if (shp.type === "polygon" || shp.type === "dxf"')
print(f's1={s1}, s2={s2}')
print(repr(text[s1:s2]))

