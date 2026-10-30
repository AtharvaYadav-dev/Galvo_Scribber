import QtQuick
import "../.."

Item {
    id: root

    required property Item target
    property real minWidth: 380
    property real minHeight: 280
    property real maxWidth: (target && target.parent) ? Math.max(minWidth, target.parent.width - 20) : 1600
    property real maxHeight: (target && target.parent) ? Math.max(minHeight, target.parent.height - 20) : 1200

    anchors.fill: target
    z: 99

    // Right Edge Resize Handle
    MouseArea {
        id: rightEdge
        width: 8
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.bottomMargin: 18
        cursorShape: Qt.SizeHorCursor

        property real startMouseX: 0
        property real startW: 0

        onPressed: function(mouse) {
            startMouseX = mouse.x
            startW = target.width
        }

        onPositionChanged: function(mouse) {
            if (pressed) {
                var delta = mouse.x - startMouseX
                var newW = startW + delta
                target.width = Math.max(root.minWidth, Math.min(root.maxWidth, newW))
            }
        }
    }

    // Bottom Edge Resize Handle
    MouseArea {
        id: bottomEdge
        height: 8
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 18
        cursorShape: Qt.SizeVerCursor

        property real startMouseY: 0
        property real startH: 0

        onPressed: function(mouse) {
            startMouseY = mouse.y
            startH = target.height
        }

        onPositionChanged: function(mouse) {
            if (pressed) {
                var delta = mouse.y - startMouseY
                var newH = startH + delta
                target.height = Math.max(root.minHeight, Math.min(root.maxHeight, newH))
            }
        }
    }

    // Bottom-Right Corner Grip Handle
    Item {
        id: cornerGrip
        width: 18
        height: 18
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        Canvas {
            id: gripCanvas
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.strokeStyle = cornerMa.containsMouse ? Theme.accentCyan : (Theme.isDark ? "#64748B" : "#94A3B8")
                ctx.lineWidth = 1.5
                ctx.lineCap = "round"

                // Stripe 1 (inner)
                ctx.beginPath()
                ctx.moveTo(width - 3, height - 11)
                ctx.lineTo(width - 11, height - 3)
                ctx.stroke()

                // Stripe 2 (middle)
                ctx.beginPath()
                ctx.moveTo(width - 3, height - 7)
                ctx.lineTo(width - 7, height - 3)
                ctx.stroke()

                // Stripe 3 (outer)
                ctx.beginPath()
                ctx.moveTo(width - 3, height - 3)
                ctx.lineTo(width - 3, height - 3)
                ctx.stroke()
            }
        }

        MouseArea {
            id: cornerMa
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SizeFDiagCursor

            property real startMouseX: 0
            property real startMouseY: 0
            property real startW: 0
            property real startH: 0

            onPressed: function(mouse) {
                startMouseX = mouse.x
                startMouseY = mouse.y
                startW = target.width
                startH = target.height
            }

            onPositionChanged: function(mouse) {
                if (pressed) {
                    var deltaX = mouse.x - startMouseX
                    var deltaY = mouse.y - startMouseY
                    var newW = startW + deltaX
                    var newH = startH + deltaY
                    target.width = Math.max(root.minWidth, Math.min(root.maxWidth, newW))
                    target.height = Math.max(root.minHeight, Math.min(root.maxHeight, newH))
                }
            }

            onHoveredChanged: gripCanvas.requestPaint()
        }
    }
}

