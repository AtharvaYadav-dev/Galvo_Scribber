with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    c_line = line.split('//')[0]
    in_str = False
    for j, c in enumerate(c_line):
        if c == '"':
            in_str = not in_str
        elif not in_str:
            if c == '{':
                prefix = line[:j].strip().split()
                name = prefix[-1] if prefix else 'anon'
                stack.append((i+1, name, line.strip()))
            elif c == '}':
                if stack:
                    start_line, name, full = stack.pop()
                    if i+1 >= 1915:
                        print(f"Line {i+1} closes line {start_line} ({name}): {full[:50]}")
                else:
                    print(f"EXTRA closing brace at line {i+1}")

print("Total unclosed items count:", len(stack))
for item in stack:
    print("  Unclosed:", item)
