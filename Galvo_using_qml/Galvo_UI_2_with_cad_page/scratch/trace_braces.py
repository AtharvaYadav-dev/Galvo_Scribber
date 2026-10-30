with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    clean = ''
    in_str = False
    for c in line:
        if c == '"': in_str = not in_str
        elif not in_str: clean += c
    for c in clean:
        if c == '{':
            stack.append((i+1, line.strip()[:40]))
        elif c == '}':
            if stack:
                stack.pop()
            else:
                print(f"EXTRA CLOSE at line {i+1}: {repr(line.strip())}")

print(f"Remaining open tags: {len(stack)}")
for item in stack:
    print(item)

