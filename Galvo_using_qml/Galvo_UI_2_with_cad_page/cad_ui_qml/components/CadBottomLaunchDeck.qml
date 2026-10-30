import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root

    property bool isFraming: false
    property bool isMarking: false
    property real mouseCoordX: 0.0
    property real mouseCoordY: 0.0
    property real zoomPercent: 100.0
    property int partCount: 0
    property int totalCount: 142

    signal redPointerToggled(bool active)
    signal markTriggered()
    signal resetCounter()

    height: 56
    color: CadTheme.bgHeader
    border.color: CadTheme.borderCard
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 14

        // Primary Industrial Laser Action Buttons
        RowLayout {
            spacing: 10

            // 1. Red Light Pointer / Framing (F1)
            Rectangle {
                id: redBtnBg
                height: 40
                implicitWidth: redBtnRow.implicitWidth + 24
                radius: 7
                color: root.isFraming
                    ? CadTheme.accentAmber
                    : (redMa.containsMouse ? CadTheme.btnRedPointerHover : CadTheme.btnRedPointerBg)
                border.color: CadTheme.btnRedPointerBorder
                border.width: 1.5

                scale: redMa.pressed ? 0.94 : (redMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale { NumberAnimation { duration: 100 } }
                Behavior on color { ColorAnimation { duration: 150 } }

                RowLayout {
                    id: redBtnRow
                    anchors.centerIn: parent
                    spacing: 8

                    Rectangle {
                        width: 9
                        height: 9
                        radius: 4.5
                        color: root.isFraming ? "#000000" : CadTheme.accentAmber

                        SequentialAnimation on opacity {
                            running: root.isFraming
                            loops: Animation.Infinite
                            PropertyAnimation { to: 0.2; duration: 400 }
                            PropertyAnimation { to: 1.0; duration: 400 }
                        }
                    }

                    Text {
                        text: root.isFraming ? "FRAMING ACTIVE (F1)" : "RED LIGHT (F1)"
                        font.family: "Inter"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: root.isFraming ? "#000000" : CadTheme.btnRedPointerText
                    }
                }

                MouseArea {
                    id: redMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.isFraming = !root.isFraming
                        root.redPointerToggled(root.isFraming)
                    }
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Red laser guide boundary preview (HotKey: F1)"
                }
            }

            // 2. Start Laser Marking (F2)
            Rectangle {
                id: markBtnBg
                height: 40
                implicitWidth: markBtnRow.implicitWidth + 28
                radius: 7
                color: root.isMarking
                    ? CadTheme.accentRed
                    : (markMa.containsMouse ? CadTheme.btnMarkHover : CadTheme.btnMarkBg)
                border.color: root.isMarking ? CadTheme.accentRed : CadTheme.btnMarkBorder
                border.width: 1.5

                scale: markMa.pressed ? 0.94 : (markMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale { NumberAnimation { duration: 100 } }
                Behavior on color { ColorAnimation { duration: 150 } }

                RowLayout {
                    id: markBtnRow
                    anchors.centerIn: parent
                    spacing: 8

                    CadIcon {
                        name: root.isMarking ? "stop" : "flash_on"
                        size: 18
                        iconColor: root.isMarking ? "#FFFFFF" : CadTheme.btnMarkText
                    }

                    Text {
                        text: root.isMarking ? "STOP LASER (F2)" : "START MARK (F2)"
                        font.family: "Inter"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: root.isMarking ? "#FFFFFF" : CadTheme.btnMarkText
                    }
                }

                MouseArea {
                    id: markMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.isMarking = !root.isMarking
                        root.markTriggered()
                    }
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Execute high-speed galvo laser burn (HotKey: F2)"
                }
            }
        }

        // Marking Mode Checkboxes
        RowLayout {
            spacing: 12
            CheckBox {
                text: "Continuous"
                font.family: "Inter"
                font.pixelSize: 11
            }
            CheckBox {
                text: "Mark Selected"
                font.family: "Inter"
                font.pixelSize: 11
                checked: true
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // Batch Counter Card
        RowLayout {
            spacing: 6
            Text {
                text: "PARTS:"
                font.family: "Inter"
                font.pixelSize: 10
                font.weight: Font.Bold
                color: CadTheme.textMuted
            }
            Text {
                text: root.partCount.toString()
                font.family: "IBM Plex Mono"
                font.pixelSize: 13
                font.weight: Font.Bold
                color: CadTheme.textPrimary
            }
            Text {
                text: "/ Total: " + root.totalCount.toString()
                font.family: "IBM Plex Mono"
                font.pixelSize: 11
                color: CadTheme.textSecondary
            }
            CadButton {
                text: "R"
                customRadius: 4
                implicitWidth: 26
                implicitHeight: 26
                tooltipText: "Reset batch part counter"
                onClicked: root.resetCounter()
            }
        }

        Item { Layout.fillWidth: true }

        // Precision Telemetry: Live Cursor Position
        Rectangle {
            height: 32
            implicitWidth: telemetryRow.implicitWidth + 20
            radius: 5
            color: CadTheme.bgCardAlt
            border.color: CadTheme.borderCard
            border.width: 1

            RowLayout {
                id: telemetryRow
                anchors.centerIn: parent
                spacing: 12

                RowLayout {
                    spacing: 4
                    Text { text: "X"; font.family: "IBM Plex Mono"; font.pixelSize: 10; font.weight: Font.Bold; color: CadTheme.accentAmber }
                    Text { text: root.mouseCoordX.toFixed(3) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: CadTheme.textPrimary }
                }

                RowLayout {
                    spacing: 4
                    Text { text: "Y"; font.family: "IBM Plex Mono"; font.pixelSize: 10; font.weight: Font.Bold; color: CadTheme.accentCyan }
                    Text { text: root.mouseCoordY.toFixed(3) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: CadTheme.textPrimary }
                }
            }
        }

        // Viewport status pills
        RowLayout {
            spacing: 8
            Rectangle {
                height: 26
                radius: 4
                color: CadTheme.isDark ? "#17233D" : "#E2E8F0"
                implicitWidth: fTxt.implicitWidth + 14
                Text {
                    id: fTxt
                    anchors.centerIn: parent
                    text: "Field: 110×110 mm"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: CadTheme.textSecondary
                }
            }
            Rectangle {
                height: 26
                radius: 4
                color: CadTheme.isDark ? "#17233D" : "#E2E8F0"
                implicitWidth: zTxt.implicitWidth + 14
                Text {
                    id: zTxt
                    anchors.centerIn: parent
                    text: "Zoom: " + root.zoomPercent.toFixed(0) + "%"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: CadTheme.textSecondary
                }
            }
        }
    }
}
