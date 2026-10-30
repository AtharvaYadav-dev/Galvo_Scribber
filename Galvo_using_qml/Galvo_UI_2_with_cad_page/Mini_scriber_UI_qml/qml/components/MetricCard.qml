import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    property string title: ""
    property string subtitle: ""
    property color accentColor: Theme.accentAmber
    default property alias content: contentLayout.data

    color: Theme.bgCard
    radius: 10
    border.color: Theme.borderCard
    border.width: 1
    clip: true

    Behavior on color { ColorAnimation { duration: 200 } }
    Behavior on border.color { ColorAnimation { duration: 200 } }

    implicitWidth: 320
    implicitHeight: mainCol.implicitHeight + 32

    ColumnLayout {
        id: mainCol
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Header Row
        RowLayout {
            Layout.fillWidth: true
            visible: root.title.length > 0
            spacing: 8

            Rectangle {
                width: 4
                height: 14
                radius: 2
                color: root.accentColor
            }

            Text {
                text: root.title
                font.family: "Segoe UI"
                font.pixelSize: 12
                font.weight: Font.Bold
                color: Theme.textPrimary
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            Text {
                text: root.subtitle
                font.family: "Segoe UI"
                font.pixelSize: 10
                color: Theme.textSecondary
                visible: root.subtitle.length > 0
                elide: Text.ElideRight
                Layout.alignment: Qt.AlignRight
                Layout.maximumWidth: Math.max(120, root.width - 140)
            }
        }

        // Direct content layout for children
        ColumnLayout {
            id: contentLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
        }
    }
}
