with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(1405, 1435):
    print(f"{j+1}: {lines[j]}", end="")
