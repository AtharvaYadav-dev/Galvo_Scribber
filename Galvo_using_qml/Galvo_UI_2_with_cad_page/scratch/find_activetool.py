with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'activeTool' in l:
        print(f"Line {i+1}: {l.strip()}")

