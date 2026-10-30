with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'stype in ["polygon"' in l or 'stype == "polygon"' in l or 'stype == "line"' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"  {j+1}: {lines[j]}", end="")
        break

