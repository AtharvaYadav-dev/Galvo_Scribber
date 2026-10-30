with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(880, 950):
    print(f"{i+1}: {lines[i]}", end="")

