import QtQuick
import QtQuick.Controls

Item {
    id: root

    signal jogRequested(string axis, int direction)
    signal centerRequested()

    implicitWidth: 220
    implicitHeight: 220

    // Component for directional buttons
    component DirButton: Rectangle {
        id: dirBtn
        property string label: ""
        property string subLabel: ""
        property color activeColor: "#00d2ff"
        signal triggered()

        width: 64
        height: 52
        radius: 8
        color: btnMouse.pressed ? "#161b26" : (btnMouse.containsMouse ? "#272f42" : "#1e2433")
        border.color: btnMouse.containsMouse ? dirBtn.activeColor : "#313a4f"
        border.width: 1.5

        Behavior on color { ColorAnimation { duration: 100 } }

        Column {
            anchors.centerIn: parent
            spacing: 2
            Text {
                text: dirBtn.label
                color: "#ffffff"
                font.pixelSize: 14
                font.weight: Font.Bold
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: dirBtn.subLabel
                color: dirBtn.activeColor
                font.pixelSize: 9
                font.weight: Font.DemiBold
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        MouseArea {
            id: btnMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: dirBtn.triggered()
        }
    }

    // Y+ (Top)
    DirButton {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        label: "▲"
        subLabel: "Y+"
        onTriggered: root.jogRequested("Y", 1)
    }

    // Y- (Bottom)
    DirButton {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        label: "▼"
        subLabel: "Y-"
        onTriggered: root.jogRequested("Y", -1)
    }

    // X- (Left)
    DirButton {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        label: "◀"
        subLabel: "X-"
        onTriggered: root.jogRequested("X", -1)
    }

    // X+ (Right)
    DirButton {
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        label: "▶"
        subLabel: "X+"
        onTriggered: root.jogRequested("X", 1)
    }

    // Center (XY Home / Center)
    Rectangle {
        anchors.centerIn: parent
        width: 68
        height: 68
        radius: 34
        color: centerMouse.pressed ? "#10131c" : (centerMouse.containsMouse ? "#2a3449" : "#202838")
        border.color: centerMouse.containsMouse ? "#00d2ff" : "#3b4761"
        border.width: 2

        Column {
            anchors.centerIn: parent
            spacing: 2
            Text {
                text: "XY"
                color: "#00d2ff"
                font.pixelSize: 12
                font.weight: Font.Bold
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: "CENTER"
                color: "#a4b1c2"
                font.pixelSize: 8
                font.weight: Font.DemiBold
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        MouseArea {
            id: centerMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.centerRequested()
        }
    }
}
