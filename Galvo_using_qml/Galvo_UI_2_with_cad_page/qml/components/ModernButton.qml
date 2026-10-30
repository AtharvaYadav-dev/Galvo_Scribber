import QtQuick
import QtQuick.Controls
import ".."

Item {
    id: root

    property alias text: label.text
    property bool primary: false
    property bool danger: false

    property color btnColor: (primary || danger) ? "transparent" : (Theme.isDark ? "#17233D" : "#FFFFFF")
    property color hoverColor: Theme.isDark ? "#22355C" : "#F1F5F9"
    property color textColor: (primary || danger) ? "#ffffff" : Theme.textPrimary
    property color borderColor: (primary || danger) ? "transparent" : (Theme.isDark ? "#28344E" : "#CBD5E1")
    property int radius: 6

    signal clicked()

    implicitWidth: Math.max(90, label.implicitWidth + 24)
    implicitHeight: 34

    // Dynamic color calculation based on role
    readonly property color resolvedBg: {
        if (danger) return mouseArea.pressed ? "#c0392b" : (mouseArea.containsMouse ? "#e74c3c" : "#7d1919")
        if (primary) return mouseArea.pressed ? "#0099cc" : (mouseArea.containsMouse ? "#33d6ff" : "#00b4d8")
        return mouseArea.pressed ? (Theme.isDark ? "#121C30" : "#E2E8F0") : (mouseArea.containsMouse ? hoverColor : btnColor)
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
            font.pixelSize: 12
            font.weight: (root.primary || root.danger) ? Font.Bold : Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
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
