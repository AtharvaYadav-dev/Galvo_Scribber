# Update CadComboBox.qml contentItem with search icon
with open('qml/components/cad/CadComboBox.qml', 'r', encoding='utf-8') as f:
    cb_text = f.read()

old_content = """    contentItem: Text {
        text: control.displayText
        font: control.font
        color: control.enabled ? Theme.textPrimary : Theme.textMuted
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }"""

new_content = """    contentItem: RowLayout {
        spacing: 6
        Text {
            visible: control.searchable
            text: "🔍"
            font.pixelSize: 10
            color: control.down || control.hovered ? Theme.accentCyan : (Theme.isDark ? "#94A3B8" : "#64748B")
            Layout.alignment: Qt.AlignVCenter
        }
        Text {
            Layout.fillWidth: true
            text: control.displayText
            font: control.font
            color: control.enabled ? Theme.textPrimary : Theme.textMuted
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }"""

if old_content in cb_text:
    cb_text = cb_text.replace(old_content, new_content, 1)
    with open('qml/components/cad/CadComboBox.qml', 'w', encoding='utf-8') as f:
        f.write(cb_text)
    print("CadComboBox contentItem updated with search icon")
else:
    print("CadComboBox contentItem already updated or not found")

