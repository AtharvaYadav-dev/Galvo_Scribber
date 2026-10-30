with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('        onPressed: function(mouse) {')
s2 = text.find('    // Floating In-Canvas HUD for Selected Object Actions')
print(f's1={s1}, s2={s2}')
print(repr(text[s1:s1+300]))
print("...")
print(repr(text[s2-300:s2]))

