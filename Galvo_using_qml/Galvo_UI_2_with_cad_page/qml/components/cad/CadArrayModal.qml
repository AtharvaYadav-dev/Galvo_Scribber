import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var targetShape: null
    property bool isOpened: false

    property int countX: 1
    property int countY: 1
    property real incXMm: 10.0
    property real incYMm: 10.0

    signal arrayConfirmed(int countX, int countY, real incXMm, real incYMm)

    anchors.fill: parent
    color: "transparent"
    visible: isOpened
    z: 200

    function openModal(shape) {
        targetShape = shape
        countX = 1
        countY = 1
        if (shape) {
            incXMm = (shape.wMm !== undefined && shape.wMm > 0) ? Number(shape.wMm) + 5.0 : 10.0
            incYMm = (shape.hMm !== undefined && shape.hMm > 0) ? Number(shape.hMm) + 5.0 : 10.0
        } else {
            incXMm = 10.0
            incYMm = 10.0
        }
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
        height: Math.min(390, root.height > 0 ? (root.height - 40) : 390)
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
                    id: arrayHeaderDrag
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
                            text: "▦"
                            font.bold: true
                            font.pixelSize: 14
                            color: Theme.accentCyan
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Array Grid Replication"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "Duplicate entity across X and Y dimensions"
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

            // Scrollable Body for responsive resizing
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: modalBox.width - 36
                    spacing: 12

                    // Grid Inputs Card matching EZCad screenshot
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: gridCol.implicitHeight + 20
                        radius: 8
                color: Theme.bgCardAlt
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: gridCol
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    // Column Titles
                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "AXIS"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                            Layout.preferredWidth: 30
                        }
                        Text {
                            text: "COUNT"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                            Layout.fillWidth: true
                        }
                        Text {
                            text: "INCREMENT [MM]"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                            Layout.fillWidth: true
                        }
                    }

                    // Row X
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: "X"
                            font.bold: true
                            font.pixelSize: 12
                            color: Theme.accentCyan
                            Layout.preferredWidth: 30
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Count"
                            text: root.countX.toString()
                            onValueChanged: function(v) { root.countX = Math.max(1, Math.min(100, Math.round(v))) }
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Inc"
                            unit: "mm"
                            text: root.incXMm.toFixed(2)
                            onValueChanged: function(v) { root.incXMm = v }
                        }
                    }

                    // Row Y
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: "Y"
                            font.bold: true
                            font.pixelSize: 12
                            color: Theme.accentGreen
                            Layout.preferredWidth: 30
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Count"
                            text: root.countY.toString()
                            onValueChanged: function(v) { root.countY = Math.max(1, Math.min(100, Math.round(v))) }
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Inc"
                            unit: "mm"
                            text: root.incYMm.toFixed(2)
                            onValueChanged: function(v) { root.incYMm = v }
                        }
                    }

                    // Replication Summary Badge
                    Rectangle {
                        Layout.fillWidth: true
                        height: 28
                        radius: 4
                        color: Theme.isDark ? "#12203A" : "#EFF6FF"
                        border.color: Theme.accentCyan
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 6
                            Text {
                                text: "Total entities after array: " + (root.countX * root.countY)
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.accentCyan
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: "Span: " + ((root.countX - 1) * root.incXMm).toFixed(1) + " × " + ((root.countY - 1) * root.incYMm).toFixed(1) + " mm"
                                font.pixelSize: 10
                                color: Theme.textMuted
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
                    text: "Apply Array"
                    variant: "accent"
                    onClicked: {
                        root.arrayConfirmed(root.countX, root.countY, root.incXMm, root.incYMm)
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
