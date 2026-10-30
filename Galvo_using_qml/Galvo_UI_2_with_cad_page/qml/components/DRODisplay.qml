import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property string axisName: "X"
    property real axisValue: 0.0
    property string unit: "mm"
    property color accentColor: "#00d2ff"

    signal zeroClicked()

    implicitWidth: 240
    implicitHeight: 90
    color: "#151821"
    radius: 8
    border.color: "#272c3d"
    border.width: 1

    // Top indicator accent line
    Rectangle {
        width: parent.width - 16
        height: 2
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        color: root.accentColor
        radius: 1
    }

    RowLayout {
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 14
        anchors.right: parent.right
        anchors.rightMargin: 14
        spacing: 8

        Text {
            text: root.axisName + " AXIS"
            color: root.accentColor
            font.pixelSize: 11
            font.weight: Font.Bold
            font.family: "Segoe UI, Roboto, Arial"
        }

        Item { Layout.fillWidth: true }

        // ZERO button
        Rectangle {
            Layout.preferredWidth: 48
            Layout.preferredHeight: 20
            radius: 4
            color: zeroMouse.containsMouse ? root.accentColor : "#202534"
            border.color: root.accentColor
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "ZERO"
                color: zeroMouse.containsMouse ? "#0c0e14" : root.accentColor
                font.pixelSize: 9
                font.weight: Font.Bold
            }

            MouseArea {
                id: zeroMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.zeroClicked()
            }
        }
    }

    // Numerical Readout
    Row {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 12
        anchors.left: parent.left
        anchors.leftMargin: 14
        spacing: 6
        baselineOffset: 0

        Text {
            text: (root.axisValue >= 0 ? "+" : "") + root.axisValue.toFixed(3)
            color: "#ffffff"
            font.pixelSize: 26
            font.weight: Font.DemiBold
            font.family: "Consolas, 'Courier New', monospace"
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 4
            text: root.unit
            color: "#7e8b9e"
            font.pixelSize: 12
            font.family: "Segoe UI, Arial"
        }
    }
}
