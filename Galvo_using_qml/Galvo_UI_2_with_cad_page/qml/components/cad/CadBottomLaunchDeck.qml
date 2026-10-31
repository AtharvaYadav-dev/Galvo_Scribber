import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property bool isFraming: (typeof cad !== "undefined" && cad) ? cad.isFraming : ((typeof galvo !== "undefined" && galvo) ? galvo.redPointerOn : false)
    property bool isMarking: (typeof cad !== "undefined" && cad) ? cad.isMarking : ((typeof galvo !== "undefined" && galvo) ? galvo.isLaserFiring : false)
    property real markProgress: (typeof cad !== "undefined" && cad) ? cad.markProgress : 0.0
    property int markCurrentCmd: (typeof cad !== "undefined" && cad) ? cad.markCurrentCmd : 0
    property int markTotalCmds: (typeof cad !== "undefined" && cad) ? cad.markTotalCmds : 0
    property bool isPaused: (typeof cad !== "undefined" && cad) ? cad.isPaused : false
    property string markElapsedStr: (typeof cad !== "undefined" && cad) ? cad.markElapsedStr : "00:00"
    property string markRemainingStr: (typeof cad !== "undefined" && cad) ? cad.markRemainingStr : "--:--"
    property real liveLaserX: (typeof cad !== "undefined" && cad) ? cad.liveLaserX : 0.0
    property real liveLaserY: (typeof cad !== "undefined" && cad) ? cad.liveLaserY : 0.0
    property real mouseCoordX: 0.0
    property real mouseCoordY: 0.0
    property real zoomPercent: 100.0
    property int partCount: 0
    property int totalCount: 142

    property bool continuousMode: false
    property bool markSelectedOnly: true

    signal redPointerToggled(bool active)
    signal markTriggered()
    signal abortTriggered()
    signal pauseTriggered()
    signal resetCounter()

    height: 56
    color: Theme.bgHeader
    border.color: Theme.borderCard
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        // 1. Primary Industrial Action Buttons
        RowLayout {
            spacing: 8

            // Red Light Pointer / Framing (F1)
            Rectangle {
                id: redBtnBg
                height: 38
                implicitWidth: redBtnRow.implicitWidth + 22
                radius: 7
                color: root.isFraming
                    ? Theme.accentAmber
                    : (redMa.containsMouse ? Theme.btnRedPointerHover : Theme.btnRedPointerBg)
                border.color: Theme.btnRedPointerBorder
                border.width: 1.5

                scale: redMa.pressed ? 0.94 : (redMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale { NumberAnimation { duration: 100 } }
                Behavior on color { ColorAnimation { duration: 150 } }

                RowLayout {
                    id: redBtnRow
                    anchors.centerIn: parent
                    spacing: 7

                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: root.isFraming ? "#000000" : Theme.accentAmber

                        SequentialAnimation on opacity {
                            running: root.isFraming
                            loops: Animation.Infinite
                            PropertyAnimation { to: 0.2; duration: 400 }
                            PropertyAnimation { to: 1.0; duration: 400 }
                        }
                    }

                    Text {
                        text: root.isFraming ? "FRAMING ON (F1)" : "RED LIGHT (F1)"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: root.isFraming ? "#000000" : Theme.btnRedPointerText
                    }
                }

                MouseArea {
                    id: redMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.redPointerToggled(!root.isFraming)
                    }
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Red laser guide boundary preview (HotKey: F1)"
                }
            }

            // Start Laser Marking (F2)
            Rectangle {
                id: markBtnBg
                height: 38
                implicitWidth: markBtnRow.implicitWidth + 24
                radius: 7
                color: root.isMarking
                    ? Theme.accentRed
                    : (markMa.containsMouse ? Theme.btnMarkHover : Theme.btnMarkBg)
                border.color: root.isMarking ? Theme.accentRed : Theme.btnMarkBorder
                border.width: 1.5

                scale: markMa.pressed ? 0.94 : (markMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale { NumberAnimation { duration: 100 } }
                Behavior on color { ColorAnimation { duration: 150 } }

                RowLayout {
                    id: markBtnRow
                    anchors.centerIn: parent
                    spacing: 7

                    CadIcon {
                        name: root.isMarking ? "stop" : "flash_on"
                        size: 16
                        iconColor: root.isMarking ? "#FFFFFF" : Theme.btnMarkText
                    }

                    Text {
                        text: root.isMarking ? "STOP LASER (F2)" : "START MARK (F2)"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: root.isMarking ? "#FFFFFF" : Theme.btnMarkText
                    }
                }

                MouseArea {
                    id: markMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (root.isMarking) {
                            root.abortTriggered()
                        } else {
                            root.markTriggered()
                        }
                    }
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Execute high-speed galvo laser burn (HotKey: F2)"
                }
            }

            // Pause / Resume Button (F3) - visible when marking is active
            Rectangle {
                id: pauseBtnBg
                height: 38
                implicitWidth: pauseBtnRow.implicitWidth + 20
                radius: 7
                visible: root.isMarking
                color: root.isPaused
                    ? (pauseMa.containsMouse ? "#D97706" : "#F59E0B")
                    : (pauseMa.containsMouse ? Theme.bgCardHover : Theme.bgCardAlt)
                border.color: root.isPaused ? "#F59E0B" : Theme.borderCard
                border.width: 1.5

                scale: pauseMa.pressed ? 0.94 : (pauseMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale { NumberAnimation { duration: 100 } }
                Behavior on color { ColorAnimation { duration: 150 } }

                RowLayout {
                    id: pauseBtnRow
                    anchors.centerIn: parent
                    spacing: 6

                    CadIcon {
                        name: root.isPaused ? "play_arrow" : "pause"
                        size: 16
                        iconColor: root.isPaused ? "#000000" : Theme.textPrimary
                    }

                    Text {
                        text: root.isPaused ? "RESUME (F3)" : "PAUSE (F3)"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: root.isPaused ? "#000000" : Theme.textPrimary
                    }
                }

                MouseArea {
                    id: pauseMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.pauseTriggered()
                    ToolTip.visible: containsMouse
                    ToolTip.text: root.isPaused ? "Resume laser execution (F3)" : "Pause laser execution safely (F3)"
                }
            }
        }

        // Custom Themed Toggles
        RowLayout {
            spacing: 8

            // Toggle 1: Continuous
            RowLayout {
                spacing: 5
                Rectangle {
                    width: 15
                    height: 15
                    radius: 3
                    color: root.continuousMode ? Theme.accentCyan : (Theme.isDark ? "#16223B" : "#F1F5F9")
                    border.color: root.continuousMode ? Theme.accentCyan : Theme.borderCard
                    border.width: 1
                    Layout.alignment: Qt.AlignVCenter

                    CadIcon {
                        visible: root.continuousMode
                        anchors.centerIn: parent
                        name: "check"
                        size: 11
                        iconColor: "#0A0F1D"
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.continuousMode = !root.continuousMode
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignVCenter
                    text: "Continuous"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 10
                    color: Theme.textPrimary
                }
            }

            // Toggle 2: Mark Selected
            RowLayout {
                spacing: 5
                Rectangle {
                    width: 15
                    height: 15
                    radius: 3
                    color: root.markSelectedOnly ? Theme.accentCyan : (Theme.isDark ? "#16223B" : "#F1F5F9")
                    border.color: root.markSelectedOnly ? Theme.accentCyan : Theme.borderCard
                    border.width: 1
                    Layout.alignment: Qt.AlignVCenter

                    CadIcon {
                        visible: root.markSelectedOnly
                        anchors.centerIn: parent
                        name: "check"
                        size: 11
                        iconColor: "#0A0F1D"
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.markSelectedOnly = !root.markSelectedOnly
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignVCenter
                    text: "Selected"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 10
                    color: Theme.textPrimary
                }
            }

            // Toggle 3: Auto Z-Focus (Workpiece Target Focal Plane)
            RowLayout {
                spacing: 5
                Rectangle {
                    width: 15
                    height: 15
                    radius: 3
                    color: (typeof cad !== "undefined" && cad && cad.autoFocusZ) ? Theme.accentCyan : (Theme.isDark ? "#16223B" : "#F1F5F9")
                    border.color: (typeof cad !== "undefined" && cad && cad.autoFocusZ) ? Theme.accentCyan : Theme.borderCard
                    border.width: 1
                    Layout.alignment: Qt.AlignVCenter

                    CadIcon {
                        visible: typeof cad !== "undefined" && cad && cad.autoFocusZ
                        anchors.centerIn: parent
                        name: "check"
                        size: 11
                        iconColor: "#0A0F1D"
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (typeof cad !== "undefined" && cad) {
                                cad.autoFocusZ = !cad.autoFocusZ
                            }
                        }
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignVCenter
                    text: "Auto Z (" + (typeof jog !== "undefined" ? jog.targetFocusZ.toFixed(1) : "27.0") + "mm)"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 10
                    font.weight: (typeof cad !== "undefined" && cad && cad.autoFocusZ) ? Font.DemiBold : Font.Normal
                    color: (typeof cad !== "undefined" && cad && cad.autoFocusZ) ? Theme.accentCyan : Theme.textPrimary
                }
            }
        }

        // Divider
        Rectangle { width: 1; height: 22; color: Theme.borderMuted }

        // Batch Counter Card
        RowLayout {
            spacing: 4
            Text {
                text: "PARTS:"
                font.family: "Segoe UI, Inter, sans-serif"
                font.pixelSize: 10
                font.weight: Font.Bold
                color: Theme.textMuted
            }
            Text {
                text: root.partCount.toString()
                font.family: "Consolas, monospace"
                font.pixelSize: 12
                font.weight: Font.Bold
                color: Theme.textPrimary
            }
            Text {
                text: "/" + root.totalCount.toString()
                font.family: "Consolas, monospace"
                font.pixelSize: 10
                color: Theme.textSecondary
            }
            CadButton {
                text: "R"
                customRadius: 3
                implicitWidth: 20
                implicitHeight: 20
                tooltipText: "Reset batch part counter"
                onClicked: root.resetCounter()
            }
        }

        // Flexible Spring Spacer Before Progress
        Item {
            Layout.fillWidth: true
            Layout.minimumWidth: 4
        }

        // Center Laser Marking Progress HUD Card (Self-contained, bounded, responsive)
        Rectangle {
            id: centerProgressCard
            visible: root.isMarking || (root.markProgress > 0 && root.markProgress < 100)
            opacity: visible ? 1.0 : 0.0
            Behavior on opacity { NumberAnimation { duration: 200 } }

            Layout.preferredWidth: 260
            Layout.minimumWidth: 160
            Layout.maximumWidth: 300
            Layout.fillWidth: false
            Layout.alignment: Qt.AlignVCenter
            height: 40
            radius: 6
            color: root.isPaused 
                ? (Theme.isDark ? "#241604" : "#FEF3C7") 
                : (Theme.isDark ? "#0A1424" : "#F0F9FF")
            border.color: root.isPaused ? "#F59E0B" : (Theme.isDark ? "#1E3A5F" : "#BAE6FD")
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                anchors.topMargin: 3
                anchors.bottomMargin: 3
                spacing: 2

                // Row 1: Status indicator + Cmd Counter + Percentage
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Rectangle {
                        width: 6
                        height: 6
                        radius: 3
                        color: root.isPaused ? "#F59E0B" : Theme.accentCyan
                        SequentialAnimation on opacity {
                            running: root.isMarking && !root.isPaused
                            loops: Animation.Infinite
                            PropertyAnimation { to: 0.2; duration: 250 }
                            PropertyAnimation { to: 1.0; duration: 250 }
                        }
                    }

                    Text {
                        text: root.isPaused ? "PAUSED" : "MARKING"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: root.isPaused ? "#F59E0B" : Theme.accentCyan
                    }

                    Text {
                        text: "•"
                        font.pixelSize: 8
                        color: Theme.textMuted
                    }

                    Text {
                        text: (root.markTotalCmds > 0)
                            ? ("Cmd " + root.markCurrentCmd + "/" + root.markTotalCmds)
                            : "Laser Firing..."
                        font.family: "Consolas, monospace"
                        font.pixelSize: 9
                        color: Theme.textSecondary
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    Text {
                        text: root.markProgress.toFixed(1) + "%"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: root.isPaused ? "#F59E0B" : Theme.accentCyan
                    }
                }

                // Row 2: Sleek Progress Track with Shimmer
                Rectangle {
                    Layout.fillWidth: true
                    height: 4
                    radius: 2
                    color: Theme.isDark ? "#060B14" : "#E2E8F0"
                    border.color: Theme.borderCard
                    border.width: 0.5
                    clip: true

                    Rectangle {
                        id: progTrackFill
                        height: parent.height
                        radius: 2
                        width: Math.max(0, Math.min(parent.width, parent.width * (root.markProgress / 100.0)))
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: root.isPaused ? "#F59E0B" : Theme.accentCyan }
                            GradientStop { position: 1.0; color: root.isPaused ? "#D97706" : Theme.accentGreen }
                        }
                        Behavior on width { NumberAnimation { duration: 60 } }

                        // Shimmer light sweep
                        Rectangle {
                            width: 20
                            height: parent.height
                            opacity: 0.5
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: "transparent" }
                                GradientStop { position: 0.5; color: "#FFFFFF" }
                                GradientStop { position: 1.0; color: "transparent" }
                            }
                            NumberAnimation on x {
                                running: root.isMarking && !root.isPaused
                                loops: Animation.Infinite
                                from: -20
                                to: progTrackFill.width + 10
                                duration: 750
                            }
                        }
                    }
                }

                // Row 3: Elapsed & Remaining Time Telemetry
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        text: "⏱ " + root.markElapsedStr
                        font.family: "Consolas, monospace"
                        font.pixelSize: 9
                        color: Theme.textMuted
                    }

                    Text { text: "•"; font.pixelSize: 8; color: Theme.textMuted }

                    Text {
                        text: "Rem: " + root.markRemainingStr
                        font.family: "Consolas, monospace"
                        font.pixelSize: 9
                        font.weight: Font.DemiBold
                        color: root.isPaused ? "#F59E0B" : Theme.accentCyan
                    }

                    Item { Layout.fillWidth: true }
                }
            }
        }

        // Flexible Spring Spacer After Progress
        Item {
            Layout.fillWidth: true
            Layout.minimumWidth: 4
        }

        // Precision Telemetry: Live Cursor Coordinates
        Rectangle {
            height: 30
            implicitWidth: telemetryRow.implicitWidth + 14
            radius: 5
            color: Theme.bgCardAlt
            border.color: Theme.borderCard
            border.width: 1

            RowLayout {
                id: telemetryRow
                anchors.centerIn: parent
                spacing: 8

                RowLayout {
                    spacing: 4
                    Text {
                        text: "X"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: root.isMarking ? Theme.accentCyan : Theme.accentAmber
                    }
                    Text {
                        text: (root.isMarking ? root.liveLaserX : root.mouseCoordX).toFixed(3) + " mm"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: root.isMarking ? Theme.accentCyan : Theme.textPrimary
                    }
                }

                RowLayout {
                    spacing: 4
                    Text {
                        text: "Y"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: root.isMarking ? Theme.accentGreen : Theme.accentCyan
                    }
                    Text {
                        text: (root.isMarking ? root.liveLaserY : root.mouseCoordY).toFixed(3) + " mm"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: root.isMarking ? Theme.accentGreen : Theme.textPrimary
                    }
                }
            }
        }

        // Hardware Status Indicator Badge
        Rectangle {
            height: 28
            radius: 14
            color: (typeof galvo !== "undefined" && galvo && galvo.isConnected)
                ? (galvo.isDemo ? (Theme.isDark ? "#2E2413" : "#FEF3C7") : (Theme.isDark ? "#062E20" : "#D1FAE5"))
                : (Theme.isDark ? "#17233D" : "#E2E8F0")
            border.color: (typeof galvo !== "undefined" && galvo && galvo.isConnected)
                ? (galvo.isDemo ? Theme.accentAmber : Theme.accentGreen)
                : Theme.borderCard
            border.width: 1
            implicitWidth: hwRow.implicitWidth + 18

            RowLayout {
                id: hwRow
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    width: 7
                    height: 7
                    radius: 3.5
                    color: (typeof galvo !== "undefined" && galvo && galvo.isConnected)
                        ? (galvo.isDemo ? Theme.accentAmber : Theme.accentGreen)
                        : Theme.textMuted
                }

                Text {
                    text: (typeof galvo !== "undefined" && galvo && galvo.isConnected)
                        ? (galvo.isDemo ? "SIMULATION" : "HARDWARE ONLINE")
                        : "OFFLINE"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: (typeof galvo !== "undefined" && galvo && galvo.isConnected)
                        ? (galvo.isDemo ? Theme.accentAmber : Theme.accentGreen)
                        : Theme.textMuted
                }
            }
        }
    }
}
