with open('qml/components/cad/CadTextFontModal.qml', 'r', encoding='utf-8') as f:
    text = f.read()

# Add property string selectedFontFamily
old_props = """    // State properties cloned from targetShape
    property string textAlign: "center" // left, center, right"""

new_props = """    // State properties cloned from targetShape
    property string selectedFontFamily: "Segoe UI"
    property string textAlign: "center" // left, center, right"""

old_open = """        if (shape) {
            textAlign = shape.textAlign || "center" """

new_open = """        if (shape) {
            selectedFontFamily = shape.fontFamily || "Segoe UI"
            textAlign = shape.textAlign || "center" """

old_gather = """    function gatherProps() {
        return {
            textAlign: textAlign,"""

new_gather = """    function gatherProps() {
        return {
            fontFamily: selectedFontFamily,
            textAlign: textAlign,"""

old_col = """                ColumnLayout {
                    width: Math.max(540, modalBox.width - 48)
                    spacing: 14

                    // 2. Alignment, Style & Orientation Card"""

new_col = """                ColumnLayout {
                    width: Math.max(540, modalBox.width - 48)
                    spacing: 14

                    // 1. Font Family & Typeface Card (Searchable)
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: fontFaceRow.implicitHeight + 16
                        radius: 8
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        RowLayout {
                            id: fontFaceRow
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 12

                            Text {
                                text: "FONT FACE"
                                font.pixelSize: 9
                                font.weight: Font.Bold
                                color: Theme.textMuted
                                Layout.preferredWidth: 80
                            }

                            CadComboBox {
                                id: modalFontCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                searchable: true
                                searchPlaceholder: "Search font face (e.g. Arial, Times)..."
                                model: (typeof cad !== "undefined" && cad) ? cad.availableFonts : ["Segoe UI", "Arial", "Times New Roman", "Consolas"]
                                currentIndex: {
                                    var f = root.selectedFontFamily || "Segoe UI"
                                    var idx = find(f)
                                    return (idx >= 0) ? idx : 0
                                }
                                onActivated: function(index) {
                                    var chosen = (index >= 0 && model && index < model.length) ? model[index] : currentText
                                    root.selectedFontFamily = chosen
                                }
                            }
                        }
                    }

                    // 2. Alignment, Style & Orientation Card"""

text = text.replace(old_props, new_props, 1)
text = text.replace(old_open, new_open, 1)
text = text.replace(old_gather, new_gather, 1)
text = text.replace(old_col, new_col, 1)

with open('qml/components/cad/CadTextFontModal.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated CadTextFontModal.qml successfully")

