with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'floatingHud' in l:
        for j in range(max(0, i-5), min(len(lines), i+60)):
            print(f"{j+1}: {lines[j]}", end="")
        break

