with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 369 to 371 (0-indexed 368 to 370)
# Line 391 to 395 (0-indexed 390 to 394)
# Let's do it by slicing
part1 = lines[:368] # up to line 368: pushUndoState()\n
# skip 368, 369, 370 (lines 369, 370, 371)
part2 = lines[371:390] # from line 372: s.xMm = 0 up to line 390: pushUndoState()\n
# skip 390, 391, 392, 393, 394 (lines 391, 392, 393, 394, 395)
part3 = lines[395:]

fixed_lines = part1 + part2 + part3
with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed successfully!")
