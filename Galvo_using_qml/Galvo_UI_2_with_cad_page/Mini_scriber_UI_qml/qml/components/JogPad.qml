import QtQuick
import QtQuick.Layouts

Item {
    id: root

    signal jogClicked(string direction)
    signal centerClicked()

    property string centerLabel: "CENTER"

    implicitWidth: 168
    implicitHeight: 168

    readonly property real discSize: Math.min(width, height)
    readonly property real btnSize: Math.max(36, Math.round(discSize * (discSize >= 220 ? (66.0 / 260.0) : (48.0 / 168.0))))
    readonly property real outerMargin: Math.max(6, Math.round(discSize * (8.0 / 168.0)))
    readonly property real btnGap: Math.max(3, Math.round((discSize - 2 * outerMargin - 3 * btnSize) / 2.0))
    readonly property real centerSize: root.btnSize

    Rectangle {
        id: disc
        width: root.discSize
        height: root.discSize
        radius: root.discSize / 2
        anchors.centerIn: parent
        color: Theme.jogPlateBg
        border.color: Theme.jogPlateBorder
        border.width: 1

        // Center Action Button (e.g. CENTER or ALIGN)
        Rectangle {
            id: centerBtn
            width: root.centerSize
            height: root.centerSize
            radius: root.centerSize / 2
            anchors.centerIn: parent
            color: centerMa.down ? Qt.darker(Theme.jogCenterBg, 1.1) : (centerMa.containsMouse ? Qt.lighter(Theme.jogCenterBg, 1.05) : Theme.jogCenterBg)
            border.color: Theme.jogCenterBorder
            border.width: 1
            z: 2

            Column {
                anchors.centerIn: parent
                spacing: 1
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "⌖"
                    font.pixelSize: Math.max(14, Math.round(root.centerSize * 0.36))
                    color: Theme.jogCenterText
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: root.centerLabel
                    font.family: "Inter"
                    font.pixelSize: Math.max(7, Math.round(root.centerSize * 0.17))
                    font.weight: Font.Bold
                    color: Theme.jogCenterText
                }
            }

            MouseArea {
                id: centerMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.centerClicked()
            }
        }

        // +Y Button (North)
        Rectangle {
            id: yPlusBtn
            width: root.btnSize
            height: root.btnSize
            radius: 6
            anchors.horizontalCenter: centerBtn.horizontalCenter
            anchors.bottom: centerBtn.top
            anchors.bottomMargin: root.btnGap
            color: yPlusMa.down ? Qt.darker(Theme.jogBtnBg, 1.1) : (yPlusMa.containsMouse ? Theme.jogBtnHover : Theme.jogBtnBg)
            border.color: Theme.jogBtnBorder
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "+Y"
                font.family: "IBM Plex Mono"
                font.pixelSize: Math.max(11, Math.round(root.btnSize * 0.28))
                font.weight: Font.DemiBold
                color: Theme.jogBtnText
            }

            MouseArea {
                id: yPlusMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.jogClicked("yplus")
            }
        }

        // -Y Button (South)
        Rectangle {
            id: yMinusBtn
            width: root.btnSize
            height: root.btnSize
            radius: 6
            anchors.horizontalCenter: centerBtn.horizontalCenter
            anchors.top: centerBtn.bottom
            anchors.topMargin: root.btnGap
            color: yMinusMa.down ? Qt.darker(Theme.jogBtnBg, 1.1) : (yMinusMa.containsMouse ? Theme.jogBtnHover : Theme.jogBtnBg)
            border.color: Theme.jogBtnBorder
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "-Y"
                font.family: "IBM Plex Mono"
                font.pixelSize: Math.max(11, Math.round(root.btnSize * 0.28))
                font.weight: Font.DemiBold
                color: Theme.jogBtnText
            }

            MouseArea {
                id: yMinusMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.jogClicked("yminus")
            }
        }

        // -X Button (West)
        Rectangle {
            id: xMinusBtn
            width: root.btnSize
            height: root.btnSize
            radius: 6
            anchors.verticalCenter: centerBtn.verticalCenter
            anchors.right: centerBtn.left
            anchors.rightMargin: root.btnGap
            color: xMinusMa.down ? Qt.darker(Theme.jogBtnBg, 1.1) : (xMinusMa.containsMouse ? Theme.jogBtnHover : Theme.jogBtnBg)
            border.color: Theme.jogBtnBorder
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "-X"
                font.family: "IBM Plex Mono"
                font.pixelSize: Math.max(11, Math.round(root.btnSize * 0.28))
                font.weight: Font.DemiBold
                color: Theme.jogBtnText
            }

            MouseArea {
                id: xMinusMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.jogClicked("xminus")
            }
        }

        // +X Button (East)
        Rectangle {
            id: xPlusBtn
            width: root.btnSize
            height: root.btnSize
            radius: 6
            anchors.verticalCenter: centerBtn.verticalCenter
            anchors.left: centerBtn.right
            anchors.leftMargin: root.btnGap
            color: xPlusMa.down ? Qt.darker(Theme.jogBtnBg, 1.1) : (xPlusMa.containsMouse ? Theme.jogBtnHover : Theme.jogBtnBg)
            border.color: Theme.jogBtnBorder
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "+X"
                font.family: "IBM Plex Mono"
                font.pixelSize: Math.max(11, Math.round(root.btnSize * 0.28))
                font.weight: Font.DemiBold
                color: Theme.jogBtnText
            }

            MouseArea {
                id: xPlusMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.jogClicked("xplus")
            }
        }
    }
}
