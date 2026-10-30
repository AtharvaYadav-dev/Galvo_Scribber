import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root

    property string barcodeType: "QR Code" // "QR Code", "Code 128", "DataMatrix"
    property string textContent: "https://www.specialiseproducts.com"
    property real codeSizeMm: 20.0
    property bool autoIncrement: false
    property int startNumber: 1
    property int stepIncrement: 1

    signal generateBarcode(string type, string content, real sizeMm, bool autoInc)
    signal closed()

    function close() {
        root.visible = false
        root.closed()
    }

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    z: 100

    focus: visible
    Keys.onEscapePressed: root.close()

    MouseArea {
        anchors.fill: parent
        onClicked: root.close()
    }

    Rectangle {
        id: modalCard
        anchors.centerIn: parent
        width: 460
        height: 520
        radius: 10
        color: CadTheme.bgCard
        border.color: CadTheme.borderActive
        border.width: 1.5

        MouseArea { anchors.fill: parent }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header
            RowLayout {
                Layout.fillWidth: true
                CadIcon {
                    name: "qr_code_2"
                    size: 22
                    iconColor: CadTheme.accentCyan
                }
                Text {
                    text: "QR Code & Barcode Generator"
                    font.family: "Inter"
                    font.pixelSize: 16
                    font.weight: Font.Bold
                    color: CadTheme.textPrimary
                }
                Item { Layout.fillWidth: true }
                CadButton {
                    iconName: "close"
                    variant: "ghost"
                    implicitWidth: 30
                    implicitHeight: 30
                    onClicked: root.close()
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: CadTheme.borderMuted }

            // Type Selector
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Repeater {
                    model: ["QR Code", "Code 128", "DataMatrix"]
                    delegate: CadButton {
                        Layout.fillWidth: true
                        text: modelData
                        isActive: root.barcodeType === modelData
                        onClicked: root.barcodeType = modelData
                    }
                }
            }

            // Text / Serial Content Input
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Text {
                    text: "ENCODED TEXT / URL / SERIAL NUMBER"
                    font.family: "Inter"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: CadTheme.textMuted
                }
                TextField {
                    id: contentField
                    Layout.fillWidth: true
                    text: root.textContent
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 12
                    color: CadTheme.textPrimary
                    placeholderText: "Enter data to encode..."
                    onTextChanged: root.textContent = text
                    background: Rectangle {
                        radius: 5
                        color: CadTheme.bgInput
                        border.color: contentField.activeFocus ? CadTheme.borderInputFocus : CadTheme.borderInput
                        border.width: 1
                    }
                }
            }

            // Size Setting
            RowLayout {
                Layout.fillWidth: true
                Text { text: "Physical Matrix Dimension"; font.family: "Inter"; font.pixelSize: 12; color: CadTheme.textPrimary }
                Item { Layout.fillWidth: true }
                CadInput {
                    unit: "mm"
                    text: root.codeSizeMm.toFixed(1)
                    onValueChanged: function(v) { root.codeSizeMm = v }
                }
            }

            // Auto-Increment Serialization Option
            Rectangle {
                Layout.fillWidth: true
                height: 110
                radius: 6
                color: CadTheme.bgCardAlt
                border.color: CadTheme.borderCard
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    CheckBox {
                        id: incCheck
                        text: "Enable Industrial Auto-Increment Counter"
                        font.family: "Inter"
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                        checked: root.autoIncrement
                        onCheckedChanged: root.autoIncrement = checked
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        enabled: root.autoIncrement
                        opacity: root.autoIncrement ? 1.0 : 0.4

                        CadInput {
                            Layout.fillWidth: true
                            label: "Start #"
                            text: root.startNumber.toString()
                            onValueChanged: function(v) { root.startNumber = Math.round(v) }
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Step (+)"
                            text: root.stepIncrement.toString()
                            onValueChanged: function(v) { root.stepIncrement = Math.round(v) }
                        }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // Action Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                CadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Add to Canvas"
                    variant: "accent"
                    onClicked: {
                        root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement)
                        root.close()
                    }
                }
            }
        }
    }
}
