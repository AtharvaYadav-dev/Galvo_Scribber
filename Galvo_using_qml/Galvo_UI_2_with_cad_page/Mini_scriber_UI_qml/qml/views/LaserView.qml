import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

ScrollView {
    id: root
    clip: true
    ScrollBar.horizontal.policy: ScrollBar.AsNeeded
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    Item {
        width: Math.max(root.availableWidth, 920)
        implicitHeight: mainCol.implicitHeight + 48

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: 28
            spacing: 24

            // Page Heading
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    spacing: 4
                    Text {
                        text: "Laser Control"
                        font.family: "Inter"
                        font.pixelSize: 26
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }
                    Text {
                        text: "Focus calibration, zero reference and dual-laser optical alignment."
                        font.family: "Inter"
                        font.pixelSize: 12
                        color: Theme.textSecondary
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: settings.machineName.toUpperCase() + "  /  CONTROL"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: Theme.textMuted
                    Layout.alignment: Qt.AlignTop
                }
            }

            // 1. Top Readout Cards (Emission State & Stored Calibration)
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Laser Emission State Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 96
                    radius: 10
                    color: Theme.isDark ? "#111827" : "#10204D"
                    border.color: Theme.isDark ? "#1E293B" : "#192D78"
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16

                        Rectangle {
                            width: 44
                            height: 44
                            radius: 8
                            color: laser.laserActive ? "#C72E36" : (Theme.isDark ? "#1E293B" : "#172338")
                            border.color: laser.laserActive ? "#EF4444" : Theme.accentAmber
                            border.width: 1

                            AppIcon {
                                anchors.centerIn: parent
                                name: "flash_on"
                                size: 22
                                iconColor: Theme.accentAmber
                            }

                            SequentialAnimation on opacity {
                                running: laser.laserActive
                                loops: Animation.Infinite
                                PropertyAnimation { to: 0.3; duration: 400 }
                                PropertyAnimation { to: 1.0; duration: 400 }
                            }
                        }

                        ColumnLayout {
                            spacing: 3
                            Layout.fillWidth: true

                            Text {
                                text: "EMISSION STATE"
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                                color: "#A6B1C4"
                            }
                            Text {
                                text: laser.laserActive ? "ACTIVE (FIRING)" : "STANDBY (OFF)"
                                font.family: "Inter"
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: laser.laserActive ? "#F87171" : "#34D399"
                            }
                            Text {
                                text: "Target: " + laser.selectedLaser
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: "#A6B1C4"
                            }
                        }
                    }
                }

                // Calibrated Stored Focus & Offsets Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 96
                    radius: 10
                    color: Theme.bgCard
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 6

                        Text {
                            text: "STORED CALIBRATION"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            spacing: 18
                            Text {
                                text: "Laser 1: " + laser.laser1Focus.toFixed(2) + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            Text {
                                visible: settings.laserCount > 1
                                text: "Laser 2: " + laser.laser2Focus.toFixed(2) + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                        }

                        Text {
                            text: settings.laserCount > 1
                                ? ("Offset: X" + (laser.xOffset >= 0 ? "+" : "") + laser.xOffset.toFixed(2) + "  Y" + (laser.yOffset >= 0 ? "+" : "") + laser.yOffset.toFixed(2))
                                : "Single laser optical configuration (No offset required)"
                            font.family: settings.laserCount > 1 ? "IBM Plex Mono" : "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                    }
                }
            }

            // 2. Focus & Dual-Laser Offset Calibration Grid
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Card A: Laser Focus Calibration
                MetricCard {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "Laser focus calibration"
                    subtitle: "Focus = Z + object height"
                    accentColor: Theme.accentAmber

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        // Laser Selection & Object Height Row
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text {
                                    text: "Select laser"
                                    font.family: "Inter"
                                    font.pixelSize: 11
                                    font.weight: Font.DemiBold
                                    color: Theme.textSecondary
                                }
                                RowLayout {
                                    spacing: 8
                                    Repeater {
                                        model: laser.availableLasers
                                        delegate: Rectangle {
                                            id: laserChip
                                            width: 106
                                            height: 36
                                            radius: 8
                                            property bool isSelected: laser.selectedLaser === modelData

                                            color: isSelected 
                                                ? (Theme.isDark ? "#172E4C" : "#DBEAFE") 
                                                : (chipMa.containsMouse ? (Theme.isDark ? "#1E293B" : "#F1F5F9") : Theme.btnSecondaryBg)
                                            border.color: isSelected 
                                                ? Theme.accentCyan 
                                                : (chipMa.containsMouse ? Theme.borderInputFocus : Theme.borderInput)
                                            border.width: isSelected ? 2 : 1

                                            RowLayout {
                                                anchors.centerIn: parent
                                                spacing: 6
                                                Rectangle {
                                                    width: 7
                                                    height: 7
                                                    radius: 3.5
                                                    color: isSelected ? Theme.accentCyan : Theme.textMuted
                                                }
                                                Text {
                                                    text: modelData
                                                    font.family: "Inter"
                                                    font.pixelSize: 11
                                                    font.weight: isSelected ? Font.Bold : Font.DemiBold
                                                    color: isSelected ? (Theme.isDark ? "#FFFFFF" : "#1E40AF") : Theme.textPrimary
                                                }
                                            }
                                            MouseArea {
                                                id: chipMa
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                hoverEnabled: true
                                                onClicked: laser.selectedLaser = modelData
                                            }
                                        }
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.preferredWidth: 150
                                spacing: 4
                                Text {
                                    text: "Object height (mm)"
                                    font.family: "Inter"
                                    font.pixelSize: 11
                                    font.weight: Font.DemiBold
                                    color: Theme.textSecondary
                                }
                                Rectangle {
                                    width: 150
                                    height: 32
                                    radius: 6
                                    color: Theme.bgInput
                                    border.color: objHeightInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10

                                        TextInput {
                                            id: objHeightInput
                                            Layout.fillWidth: true
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: laser.objHeight.toString()
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var v = parseFloat(text)
                                                if (!isNaN(v)) laser.setObjHeight(v)
                                            }
                                        }

                                        Text {
                                            text: "mm"
                                            font.family: "Inter"
                                            font.pixelSize: 11
                                            color: Theme.textSecondary
                                        }
                                    }
                                }
                            }
                        }

                        // Focus Spot Toggle Button (Prominently Highlighted with Laser Safety Border)
                        Rectangle {
                            Layout.fillWidth: true
                            height: 44
                            radius: 8
                            color: laser.laserActive
                                ? (Theme.isDark ? "#7F1D1D" : "#DC2626")
                                : (spotMa.containsMouse 
                                    ? (Theme.isDark ? "#1E3A8A" : "#2563EB")
                                    : (Theme.isDark ? "#1E2A4A" : "#1D4ED8"))
                            border.color: laser.laserActive 
                                ? "#EF4444" 
                                : (Theme.isDark ? Theme.accentCyan : "#3B82F6")
                            border.width: laser.laserActive ? 2 : 1.5

                            // Pulsing glow when firing
                            SequentialAnimation on border.color {
                                running: laser.laserActive
                                loops: Animation.Infinite
                                ColorAnimation { to: "#FCA5A5"; duration: 400 }
                                ColorAnimation { to: "#EF4444"; duration: 400 }
                            }

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 8
                                AppIcon {
                                    name: laser.laserActive ? "power_settings_new" : "flash_on"
                                    size: 16
                                    iconColor: "#FFFFFF"
                                }
                                Text {
                                    text: laser.laserActive ? "TURN OFF FOCUS SPOT (ACTIVE)" : "TURN ON FOCUS SPOT (" + laser.selectedLaser + ")"
                                    font.family: "Inter"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#FFFFFF"
                                    font.letterSpacing: 0.5
                                }
                            }

                            MouseArea {
                                id: spotMa
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: laser.toggleFocusLaser()
                            }
                        }

                        // Z Focus Step Chips & Buttons
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "Z FOCUS STEP"
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                            }

                            RowLayout {
                                spacing: 8
                                Repeater {
                                    model: [1.0, 0.1, 0.01]
                                    delegate: Rectangle {
                                        id: zStepChip
                                        width: 66
                                        height: 32
                                        radius: 6
                                        property bool isSelected: laser.focusStep === modelData
                                        color: isSelected 
                                            ? (Theme.isDark ? "#172A4A" : "#DBEAFE") 
                                            : (zStepMa.containsMouse ? (Theme.isDark ? "#172033" : "#F1F5F9") : Theme.btnSecondaryBg)
                                        border.color: isSelected 
                                            ? Theme.accentCyan 
                                            : (zStepMa.containsMouse ? Theme.borderInputFocus : Theme.borderInput)
                                        border.width: isSelected ? 1.5 : 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData + " mm"
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 11
                                            font.weight: isSelected ? Font.Bold : Font.DemiBold
                                            color: isSelected ? (Theme.isDark ? Theme.accentCyan : "#1E40AF") : Theme.textPrimary
                                        }
                                        MouseArea {
                                            id: zStepMa
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            hoverEnabled: true
                                            onClicked: laser.setFocusStep(modelData)
                                        }
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                Layout.topMargin: 4

                                AppButton {
                                    Layout.fillWidth: true
                                    text: "▲  Z+ Focus (Up)"
                                    variant: "outline"
                                    onClicked: laser.jogFocusZ("plus")
                                }
                                AppButton {
                                    Layout.fillWidth: true
                                    text: "▼  Z− Focus (Down)"
                                    variant: "outline"
                                    onClicked: laser.jogFocusZ("minus")
                                }
                            }
                        }

                        // Current Z & Computed Focus Display Box
                        Rectangle {
                            Layout.fillWidth: true
                            height: 64
                            radius: 8
                            color: Theme.isDark ? "#080D18" : "#10204D"
                            border.color: Theme.isDark ? "#1E293B" : "#192D78"
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 4

                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: "Current Z"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: "#A6B1C4"
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: motion.zPos.toFixed(3) + " mm"
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 12
                                        font.weight: Font.DemiBold
                                        color: "#FFFFFF"
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: "Calculated focus"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: "#A6B1C4"
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: (motion.zPos + laser.objHeight).toFixed(3) + " mm"
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 18
                                        font.weight: Font.Bold
                                        color: "#34D399"
                                    }
                                }
                            }
                        }

                        // Save Focus Button
                        AppButton {
                            Layout.fillWidth: true
                            implicitHeight: 44
                            iconName: "save"
                            text: "Set & Save Focus (" + laser.selectedLaser + ")"
                            variant: "success"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            onClicked: laser.saveFocus()
                        }

                        Text {
                            text: "Calibration is stored for the selected laser."
                            font.family: "Inter"
                            font.pixelSize: 10
                            color: Theme.textSecondary
                        }
                    }
                }

                // Card B: Dual-Laser Offset Calibration (visible when 2 lasers configured)
                MetricCard {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: settings.laserCount > 1
                    title: "Dual-laser offset calibration"
                    subtitle: "Zero reference & optical alignment"
                    accentColor: Theme.accentAmber

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        // Step 01
                        RowLayout {
                            spacing: 8
                            Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentAmber }
                            Text {
                                text: "01  Reference zero setup"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            AppButton {
                                Layout.fillWidth: true
                                implicitHeight: 42
                                iconName: laser.laserActive ? "power_settings_new" : "my_location"
                                text: laser.laserActive ? "Turn Off Laser" : "Drive to Focus & Fire"
                                variant: laser.laserActive ? "danger" : "primary"
                                font.weight: Font.Bold
                                onClicked: laser.toggleOffsetLaser()
                            }

                            AppButton {
                                Layout.fillWidth: true
                                implicitHeight: 42
                                iconName: "place"
                                text: "Set Zero Reference"
                                variant: "warning"
                                font.weight: Font.Bold
                                onClicked: laser.setZeroReference()
                            }
                        }

                        Text {
                            text: laser.isZeroSet ? "Reference set for " + laser.zeroLaser + " — Now align Laser 2:" : "Status: Reference zero not yet recorded"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: laser.isZeroSet ? Theme.accentGreen : Theme.textSecondary
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.borderCard
                            Layout.topMargin: 4
                            Layout.bottomMargin: 4
                        }

                        // Step 02
                        RowLayout {
                            spacing: 8
                            Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentAmber }
                            Text {
                                text: "02  Offset jogging · align to mark"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                        }

                        // Step 02: Offset Jogging & Alignment
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 20
                            Layout.alignment: Qt.AlignVCenter

                            // Left: Step Distance Chips (2x2 Grid)
                            ColumnLayout {
                                spacing: 8
                                Layout.alignment: Qt.AlignVCenter

                                Text {
                                    text: "STEP DISTANCE"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: Theme.textSecondary
                                }

                                GridLayout {
                                    columns: 2
                                    columnSpacing: 8
                                    rowSpacing: 8

                                    Repeater {
                                        model: [10.0, 5.0, 1.0, 0.1]
                                        delegate: Rectangle {
                                            width: 58
                                            height: 32
                                            radius: 6
                                            color: laser.offsetStep === modelData ? 
                                                (Theme.isDark ? "#1E293B" : "#E0E7FF") : 
                                                Theme.btnSecondaryBg
                                            border.color: laser.offsetStep === modelData ? 
                                                Theme.accentCyan : 
                                                Theme.borderInput
                                            border.width: laser.offsetStep === modelData ? 2 : 1

                                            RowLayout {
                                                anchors.centerIn: parent
                                                spacing: 4

                                                Rectangle {
                                                    width: 5
                                                    height: 5
                                                    radius: 2.5
                                                    color: Theme.accentCyan
                                                    visible: laser.offsetStep === modelData
                                                }

                                                Text {
                                                    text: (modelData >= 1 ? modelData.toFixed(0) : modelData.toString()) + " mm"
                                                    font.family: "IBM Plex Mono"
                                                    font.pixelSize: 11
                                                    font.weight: Font.Bold
                                                    color: laser.offsetStep === modelData ? 
                                                        (Theme.isDark ? "#38BDF8" : "#0284C7") : 
                                                        Theme.textPrimary
                                                }
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: laser.setOffsetStep(modelData)
                                            }
                                        }
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }

                            // Right: Circular Offset Jog Pad
                            JogPad {
                                Layout.preferredWidth: 168
                                Layout.preferredHeight: 168
                                centerLabel: "ALIGN"
                                onJogClicked: function(dir) {
                                    if (dir === "yplus") laser.jogOffset("offyplus")
                                    else if (dir === "yminus") laser.jogOffset("offyminus")
                                    else if (dir === "xplus") laser.jogOffset("offxplus")
                                    else if (dir === "xminus") laser.jogOffset("offxminus")
                                }
                                onCenterClicked: laser.saveOffset()
                            }

                            Item { Layout.fillWidth: true }
                        }

                        // Save Offset Button
                        AppButton {
                            Layout.fillWidth: true
                            implicitHeight: 44
                            iconName: "save"
                            text: "Set & Save Offset (" + laser.selectedLaser + ")"
                            variant: laser.isZeroSet ? "success" : "secondary"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            enabled: laser.isZeroSet
                            onClicked: laser.saveOffset()
                        }
                    }
                }

                // Card B-Single: Single-Laser Optical Architecture Profile
                MetricCard {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: settings.laserCount === 1
                    title: "Single-laser optical profile"
                    subtitle: "Direct focus & beam alignment status"
                    accentColor: Theme.accentCyan

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 16

                        Rectangle {
                            Layout.fillWidth: true
                            height: 60
                            radius: 8
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 10
                                AppIcon { name: "bolt"; size: 22; iconColor: Theme.accentCyan }
                                ColumnLayout {
                                    spacing: 2
                                    Text {
                                        text: "Active Laser: Laser 1"
                                        font.family: "Inter"
                                        font.pixelSize: 12
                                        font.weight: Font.Bold
                                        color: Theme.textPrimary
                                    }
                                    Text {
                                        text: "Machine configured in Single Laser Mode via Admin Machine Setup."
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: Theme.textSecondary
                                    }
                                }
                            }
                        }

                        // Status parameters
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Focus calibration parameter:"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: laser.laser1Focus.toFixed(2) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentAmber }
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Dual-laser offset compensation:"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: "BYPASSED (1 LASER)"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentGreen }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.borderCard
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "To activate dual lasers (Laser 1 + Laser 2 with optical offset alignment), log in as Admin and switch to Dual Laser mode in Machine Setup."
                            font.family: "Inter"
                            font.pixelSize: 10
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                            lineHeight: 1.3
                        }
                    }
                }
            }

            // Bottom Controller Offline / Warning Banner
            Rectangle {
                Layout.fillWidth: true
                height: 44
                radius: 6
                visible: !serial.connected
                color: Theme.isDark ? "#1A0F14" : "#FEE2E2"
                border.color: Theme.isDark ? "#7F1D1D" : "#FECACA"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: 10

                    AppIcon {
                        name: "link_off"
                        size: 16
                        iconColor: Theme.isDark ? "#F87171" : "#C72E36"
                    }

                    Text {
                        text: "Controller offline. Connect the port before sending motion or laser commands."
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.isDark ? "#F87171" : "#C72E36"
                    }
                }
            }
        }
    }
}
