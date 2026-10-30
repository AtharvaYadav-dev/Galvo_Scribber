with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(240, 265):
    print(f"{i+1}: {lines[i]}", end="")

