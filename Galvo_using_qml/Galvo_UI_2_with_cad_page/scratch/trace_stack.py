with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_stack = False
stack_depth = 0
for i, line in enumerate(lines):
    if 'StackLayout {' in line:
        in_stack = True
        stack_start = i+1
        stack_depth = 1
        print(f"StackLayout started at line {i+1}")
        continue
    if in_stack:
        clean = ''
        in_str = False
        for c in line:
            if c == '"': in_str = not in_str
            elif not in_str: clean += c
        for c in clean:
            if c == '{':
                stack_depth += 1
                if stack_depth == 2:
                    print(f"  Child of StackLayout opened at line {i+1}: {line.strip()[:60]}")
            elif c == '}':
                if stack_depth == 2:
                    print(f"  Child of StackLayout CLOSED at line {i+1}: {line.strip()[:60]}")
                stack_depth -= 1
                if stack_depth == 0:
                    print(f"StackLayout CLOSED at line {i+1}")
                    in_stack = False
                    break

