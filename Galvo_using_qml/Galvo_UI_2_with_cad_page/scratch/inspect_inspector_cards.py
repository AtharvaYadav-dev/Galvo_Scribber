with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'visible: root.selectedShape !== null && root.selectedShape.type === "text"' in line:
        print(f'Text Card starts at: {i+1}')
    if 'Laser Pen Assignment' in line or 'HATCH INFILL CONFIGURATION' in line or 'SELECT LASER PEN' in line:
        print(f'{i+1}: {line.strip()[:80]}')

