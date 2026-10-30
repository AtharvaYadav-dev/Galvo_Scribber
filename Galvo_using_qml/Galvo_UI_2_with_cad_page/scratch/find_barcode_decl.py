with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'barcodeModal' in l and i > 150:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"  {j+1}: {lines[j]}", end="")
        break

