with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(920, 975):
    print(f'{i+1}: {repr(lines[i])}')

