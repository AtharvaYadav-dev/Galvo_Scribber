import QtQuick

Text {
    id: root

    property string name: ""
    property real size: 16
    property color iconColor: "#FFFFFF"

    text: name
    font.family: "Material Icons"
    font.pixelSize: size
    color: iconColor
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
}
