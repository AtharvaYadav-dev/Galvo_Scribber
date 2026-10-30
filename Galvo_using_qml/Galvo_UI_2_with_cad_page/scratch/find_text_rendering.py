with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'type === "text"' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(max(0, i - 5), min(len(lines), i + 40)):
            print(f"  {j+1}: {lines[j]}", end="")

