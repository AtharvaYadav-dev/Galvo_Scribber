import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: root

    property string axisName: "X"
    property real position: 0.0
    property string unit: "mm"
    property color themeColor: "#00e5ff"

    signal zeroClicked()
    signal homeClicked()

    color: Theme.droCardBg
    radius: 10
    border.color: Theme.droBorder
    border.width: 1
    implicitHeight: 104
    implicitWidth: 260

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        // Top Row: Axis Badge + Label and Unit
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                width: 28
                height: 28
                radius: 6
                color: Theme.droBadgeBg
                border.color: Theme.borderCard
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: root.axisName
                    font.family: "Inter"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: Theme.droBadgeText
                }
            }

            Text {
                text: "AXIS POSITION"
                font.family: "Inter"
                font.pixelSize: 10
                font.weight: Font.DemiBold
                color: Theme.textSecondary
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "DRO / " + root.unit
                font.family: "Inter"
                font.pixelSize: 10
                color: Theme.textSecondary
            }
        }

        // Bottom Row: Live coordinate value + Home button
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            RowLayout {
                spacing: 6
                Layout.alignment: Qt.AlignVCenter

                Text {
                    text: (root.position >= 0 ? "+" : "") + root.position.toFixed(3)
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 25
                    font.weight: Font.Bold
                    color: Theme.droNumber
                }
                Text {
                    text: root.unit
                    font.family: "Inter"
                    font.pixelSize: 12
                    color: Theme.textSecondary
                    Layout.alignment: Qt.AlignBottom
                    Layout.bottomMargin: 3
                }
            }

            Item { Layout.fillWidth: true }

            // Dedicated Single Home Button (Cleanly Contained)
            Rectangle {
                width: 72
                height: 32
                radius: 6
                color: homeMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.15) : (homeMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                border.color: homeMa.containsMouse ? Theme.accentAmber : Theme.btnSecondaryBorder
                border.width: 1
                Layout.alignment: Qt.AlignVCenter

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 5

                    Text {
                        text: "⌂"
                        font.pixelSize: 12
                        color: homeMa.containsMouse ? Theme.accentAmber : Theme.btnSecondaryText
                    }

                    Text {
                        text: "Home"
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: homeMa.containsMouse ? Theme.accentAmber : Theme.btnSecondaryText
                    }
                }

                MouseArea {
                    id: homeMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.homeClicked()
                }
            }
        }
    }
}
