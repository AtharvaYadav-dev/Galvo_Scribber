import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Item {
    id: root

    property string label: ""
    property alias text: textInput.text
    property string unit: ""
    property bool readOnly: false
    property real minimumValue: -9999.0
    property real maximumValue: 9999.0
    property int decimals: 2

    signal valueChanged(real val)
    signal editingFinished()

    implicitWidth: 140
    implicitHeight: 32

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 5
        color: CadTheme.bgInput
        border.color: textInput.activeFocus ? CadTheme.borderInputFocus : CadTheme.borderInput
        border.width: 1

        Behavior on border.color { ColorAnimation { duration: 150 } }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            spacing: 4

            Text {
                visible: root.label.length > 0
                text: root.label
                font.family: "Inter"
                font.pixelSize: 11
                font.weight: Font.DemiBold
                color: CadTheme.textSecondary
                Layout.alignment: Qt.AlignVCenter
            }

            TextInput {
                id: textInput
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                font.family: "IBM Plex Mono"
                font.pixelSize: 12
                font.weight: Font.Bold
                color: CadTheme.textPrimary
                readOnly: root.readOnly
                selectByMouse: true
                selectionColor: CadTheme.accentCyan
                selectedTextColor: "#000000"
                clip: true

                onEditingFinished: {
                    root.editingFinished()
                    var v = parseFloat(textInput.text)
                    if (!isNaN(v)) {
                        root.valueChanged(v)
                    }
                }
            }

            Text {
                visible: root.unit.length > 0
                text: root.unit
                font.family: "Inter"
                font.pixelSize: 10
                font.weight: Font.Normal
                color: CadTheme.textMuted
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }
}
