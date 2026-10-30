import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "./cad"

Rectangle {
    id: root

    property string title: "Tool Window"
    property string iconName: "settings"
    property real modalWidth: 800
    property real modalHeight: 600
    default property alias content: contentContainer.data

    signal closed()

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.40)
    z: 200
    visible: opacity > 0
    opacity: 0

    Behavior on opacity { NumberAnimation { duration: 150 } }

    function open() {
        if (root.width > 0 && root.height > 0) {
            modalCard.x = Math.max(10, Math.round((root.width - modalCard.width) / 2))
            modalCard.y = Math.max(10, Math.round((root.height - modalCard.height) / 2))
        }
        opacity = 1.0
    }

    function close() {
        opacity = 0.0
        root.closed()
    }

    // 1. Full Backdrop Blocker: Absorbs all clicks, drags, hover, and wheel events so background is never affected
    MouseArea {
        id: backdropBlocker
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

    // Modal Window Card
    Rectangle {
        id: modalCard
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: Math.min(root.modalWidth, root.width - 40)
        height: Math.min(root.modalHeight, root.height - 40)
        radius: 10
        color: Theme.bgCard
        border.color: Theme.accentCyan
        border.width: 1.5
        clip: true

        scale: root.opacity > 0 ? 1.0 : 0.95
        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }

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
                // Consume all unhandled scroll deltas inside the modal
                event.accepted = true
            }
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // Header Bar (Draggable)
            Rectangle {
                Layout.fillWidth: true
                height: 48
                color: Theme.bgCardHeader
                border.color: Theme.borderCard
                border.width: 1

                MouseArea {
                    id: toolHeaderDrag
                    anchors.fill: parent
                    drag.target: modalCard
                    drag.minimumX: -modalCard.width + 100
                    drag.maximumX: root.width - 100
                    drag.minimumY: 0
                    drag.maximumY: root.height - 50
                    cursorShape: Qt.SizeAllCursor
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 12
                    spacing: 10

                    Text {
                        text: root.iconName
                        font.family: "Material Icons"
                        font.pixelSize: 20
                        color: Theme.accentCyan
                    }

                    Text {
                        text: root.title
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 14
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        width: 32
                        height: 32
                        radius: 6
                        z: 2
                        color: closeMa.containsMouse ? (Theme.isDark ? "#2A151C" : "#FEE2E2") : "transparent"
                        border.color: closeMa.containsMouse ? Theme.accentRed : "transparent"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "close"
                            font.family: "Material Icons"
                            font.pixelSize: 18
                            color: closeMa.containsMouse ? Theme.accentRed : Theme.textSecondary
                        }

                        MouseArea {
                            id: closeMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.close()
                        }
                    }
                }
            }

            // Body Content Area
            Item {
                id: contentContainer
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        // Responsive Resize Handle
        CadWindowResizeHandle {
            target: modalCard
            minWidth: 460
            minHeight: 360
        }
    }
}
