with open('bridges/cad_bridge.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def measureText' in l or 'def text_to_vector' in l or 'font_to_path' in l or 'compute_text' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(i, min(len(lines), i+40)):
            print(f"  {j+1}: {lines[j]}", end="")

