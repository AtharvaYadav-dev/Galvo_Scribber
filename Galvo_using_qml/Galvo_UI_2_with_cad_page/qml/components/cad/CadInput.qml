import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

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

    implicitWidth: 160
    implicitHeight: 32

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 5
        color: Theme.bgInput
        border.color: textInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
        border.width: 1

        Behavior on border.color { ColorAnimation { duration: 150 } }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            spacing: 6

            Text {
                visible: root.label.length > 0
                text: root.label
                font.family: "Segoe UI, Inter, sans-serif"
                font.pixelSize: 11
                font.weight: Font.DemiBold
                color: Theme.textSecondary
                Layout.alignment: Qt.AlignVCenter
                Layout.maximumWidth: 115
                elide: Text.ElideRight
            }

            TextInput {
                id: textInput
                Layout.fillWidth: true
                Layout.minimumWidth: 40
                Layout.alignment: Qt.AlignVCenter
                horizontalAlignment: TextInput.AlignRight
                font.family: "Consolas, 'IBM Plex Mono', monospace"
                font.pixelSize: 12
                font.weight: Font.Bold
                color: Theme.textPrimary
                readOnly: root.readOnly
                selectByMouse: true
                selectionColor: Theme.accentCyan
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
                font.family: "Segoe UI, Inter, sans-serif"
                font.pixelSize: 10
                font.weight: Font.Normal
                color: Theme.textMuted
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }
}
