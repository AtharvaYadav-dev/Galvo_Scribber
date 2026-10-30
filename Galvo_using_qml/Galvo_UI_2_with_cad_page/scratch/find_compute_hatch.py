with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'computeHatchPreviewLines' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(i, min(len(lines), i+50)):
            print(f"  {j+1}: {lines[j]}", end="")
        break

