import QtQuick
import QtQuick.Controls

Item {
    id: root

    property alias text: label.text
    property color btnColor: "#222736"
    property color hoverColor: "#2c3347"
    property color textColor: "#ffffff"
    property color borderColor: "#353d54"
    property int radius: 6
    property bool primary: false
    property bool danger: false

    signal clicked()

    implicitWidth: 120
    implicitHeight: 40

    // Dynamic color calculation based on role
    readonly property color resolvedBg: {
        if (danger) return mouseArea.pressed ? "#c0392b" : (mouseArea.containsMouse ? "#e74c3c" : "#7d1919")
        if (primary) return mouseArea.pressed ? "#0099cc" : (mouseArea.containsMouse ? "#33d6ff" : "#00b4d8")
        return mouseArea.pressed ? "#1a1e2b" : (mouseArea.containsMouse ? hoverColor : btnColor)
    }

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: root.radius
        color: root.resolvedBg
        border.color: root.danger ? "#e74c3c" : (root.primary ? "#00d2ff" : root.borderColor)
        border.width: (root.primary || root.danger) ? 1.5 : 1

        Behavior on color {
            ColorAnimation { duration: 120 }
        }

        Text {
            id: label
            anchors.centerIn: parent
            color: root.textColor
            font.pixelSize: 13
            font.weight: (root.primary || root.danger) ? Font.DemiBold : Font.Medium
            font.family: "Segoe UI, Roboto, Arial"
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
