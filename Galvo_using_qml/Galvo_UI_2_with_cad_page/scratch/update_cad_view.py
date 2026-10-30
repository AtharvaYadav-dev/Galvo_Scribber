with open('qml/views/CadView.qml', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '            // 1. Top Unified Command Ribbon\n            CadTopCommandBar {\n                Layout.fillWidth: true',
    '            // 1. Top Unified Command Ribbon\n            CadTopCommandBar {\n                id: topCommandBar\n                objectName: "topCommandBar"\n                Layout.fillWidth: true'
)

text = text.replace(
    '                        // Main Vector Canvas\n                        CadCanvas {\n                            id: cadCanvas\n                            Layout.fillWidth: true',
    '                        // Main Vector Canvas\n                        CadCanvas {\n                            id: cadCanvas\n                            objectName: "cadCanvas"\n                            Layout.fillWidth: true'
)

with open('qml/views/CadView.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("CadView updated successfully")

