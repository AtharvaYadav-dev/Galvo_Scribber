import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var targetShape: null
    property bool isOpened: false
    property var portBits: [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]

    signal portConditionsConfirmed(var bits)

    anchors.fill: parent
    color: "transparent"
    visible: isOpened
    z: 200

    function openModal(shape) {
        targetShape = shape
        var existing = (shape && shape.inputPortBits) ? shape.inputPortBits : []
        var b = []
        for (var i = 0; i < 16; i++) {
            b.push(existing[i] === true)
        }
        portBits = b
        if (root.width > 0 && root.height > 0) {
            modalBox.x = Math.max(10, Math.round((root.width - modalBox.width) / 2))
            modalBox.y = Math.max(10, Math.round((root.height - modalBox.height) / 2))
        }
        isOpened = true
    }

    function closeModal() {
        isOpened = false
    }

    // Full Backdrop Blocker: Absorbs all clicks, drags, hover, and wheel events so background is never affected
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        preventStealing: true
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onWheel: function(wheel) { wheel.accepted = true }
        onPressed: function(mouse) { mouse.accepted = true }
        onReleased: function(mouse) { mouse.accepted = true }
        onClicked: function(mouse) { mouse.accepted = true }
        onDoubleClicked: function(mouse) { mouse.accepted = true }
        onPositionChanged: function(mouse) { mouse.accepted = true }
    }

    // Modal Card (Movable floating card)
    Rectangle {
        id: modalBox
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: 400
        height: Math.min(360, root.height > 0 ? (root.height - 40) : 360)
        radius: 12
        color: Theme.bgCard
        border.color: Theme.accentCyan
        border.width: 1.5

        // Prevent click-through and consume unhandled wheel events within the modal card
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            onWheel: function(wheel) { wheel.accepted = true }
            onPressed: function(mouse) { mouse.accepted = true }
            onReleased: function(mouse) { mouse.accepted = true }
            onClicked: function(mouse) { mouse.accepted = true }
            onDoubleClicked: function(mouse) { mouse.accepted = true }
        }

        WheelHandler {
            target: null
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            onWheel: function(event) {
                event.accepted = true
            }
        }

        ColumnLayout {
            id: contentCol
            anchors.fill: parent
            anchors.margins: 18
            spacing: 14

            // Header (Draggable)
            Item {
                Layout.fillWidth: true
                implicitHeight: headerRow.implicitHeight

                MouseArea {
                    id: portHeaderDrag
                    anchors.fill: parent
                    drag.target: modalBox
                    drag.minimumX: -modalBox.width + 100
                    drag.maximumX: root.width - 100
                    drag.minimumY: 0
                    drag.maximumY: root.height - 50
                    cursorShape: Qt.SizeAllCursor
                }

                RowLayout {
                    id: headerRow
                    anchors.fill: parent
                    spacing: 8

                    Rectangle {
                        width: 28
                        height: 28
                        radius: 6
                        color: Theme.isDark ? "#172647" : "#EFF6FF"
                        border.color: Theme.accentCyan
                        border.width: 1
                        Text {
                            anchors.centerIn: parent
                            text: "⎋"
                            font.bold: true
                            font.pixelSize: 13
                            color: Theme.accentCyan
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Input Port Conditions"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "Conditional trigger execution bits (0 - 15)"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            color: Theme.textMuted
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Rectangle {
                        width: 26
                        height: 26
                        radius: 13
                        z: 2
                        color: closeMa.containsMouse ? (Theme.isDark ? "#2A3756" : "#E2E8F0") : "transparent"
                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 12
                            color: Theme.textMuted
                        }
                        MouseArea {
                            id: closeMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.closeModal()
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.borderCard
            }

            // Scrollable Bit Matrix Body
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: modalBox.width - 36
                    spacing: 12

                    // Bit Matrix Card matching EZCad screenshot
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: bitsCol.implicitHeight + 20
                        radius: 8
                color: Theme.bgCardAlt
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: bitsCol
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    Text {
                        text: "I/O CONTROL CONDITIONAL BITS"
                        font.pixelSize: 9
                        font.weight: Font.Bold
                        color: Theme.textMuted
                    }

                    // Row 1: Bits 7 down to 0 (matching EZCad order)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Repeater {
                            model: [7, 6, 5, 4, 3, 2, 1, 0]
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 2

                                CadCheckBox {
                                    id: bChk
                                    Layout.alignment: Qt.AlignHCenter
                                    checked: root.portBits[modelData]
                                    onCheckedChanged: {
                                        var arr = root.portBits.slice()
                                        arr[modelData] = checked
                                        root.portBits = arr
                                    }
                                }
                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.toString()
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: bChk.checked ? Theme.accentCyan : Theme.textMuted
                                }
                            }
                        }
                    }

                    // Row 2: Bits 15 down to 8 (matching EZCad order)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Repeater {
                            model: [15, 14, 13, 12, 11, 10, 9, 8]
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 2

                                CadCheckBox {
                                    id: bChk2
                                    Layout.alignment: Qt.AlignHCenter
                                    checked: root.portBits[modelData]
                                    onCheckedChanged: {
                                        var arr = root.portBits.slice()
                                        arr[modelData] = checked
                                        root.portBits = arr
                                    }
                                }
                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.toString()
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: bChk2.checked ? Theme.accentCyan : Theme.textMuted
                                }
                            }
                        }
                    }
                }
            }
        }
    }

            // Action Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Item { Layout.fillWidth: true }

                CadButton {
                    text: "Cancel"
                    variant: "ghost"
                    onClicked: root.closeModal()
                }

                CadButton {
                    text: "OK"
                    iconName: "check"
                    variant: "accent"
                    onClicked: {
                        root.portConditionsConfirmed(root.portBits)
                        root.closeModal()
                    }
                }
            }
        }

        // Responsive Resize Handle
        CadWindowResizeHandle {
            target: modalBox
            minWidth: 340
            minHeight: 280
        }
    }
}
