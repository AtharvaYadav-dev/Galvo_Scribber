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
        width: Math.max(root.availableWidth, 1160)
        height: Math.max(root.availableHeight, mainCol.implicitHeight + 48)

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: 28
            spacing: 20

            // Page Heading
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    spacing: 4
                    Text {
                        text: "Motion & DRO"
                        font.family: "Inter"
                        font.pixelSize: 26
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }
                    Text {
                        text: "Live axis positions, manual jogging and machine reference controls."
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

            // 1. Digital Readout Section (3 DRO Cards, perfectly aligned with 3 columns below)
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                DroDisplay {
                    Layout.fillWidth: true
                    axisName: "X"
                    position: motion.xPos
                    onHomeClicked: motion.homeAxis("X")
                }

                DroDisplay {
                    Layout.fillWidth: true
                    axisName: "Y"
                    position: motion.yPos
                    onHomeClicked: motion.homeAxis("Y")
                }

                DroDisplay {
                    Layout.fillWidth: true
                    axisName: "Z"
                    position: motion.zPos
                    onHomeClicked: motion.homeAxis("Z")
                }
            }

            // 2. Main Motion Control Grid: 3 Balanced, Responsive Columns
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 20

                // ==========================================
                // Column 1: Manual Axis Jogging & Step Size
                // ==========================================
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 440
                    Layout.minimumWidth: 360
                    Layout.fillHeight: true
                    title: "Manual axis jogging"
                    subtitle: "Axes & stages"
                    accentColor: Theme.accentAmber

                    // Step Size Chips Row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Layout.topMargin: 2
                        Layout.bottomMargin: 6

                        Text {
                            text: "STEP"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                            color: Theme.textSecondary
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Item { Layout.fillWidth: true }

                        Repeater {
                            model: [0.1, 1.0, 5.0, 10.0, 50.0]
                            delegate: Rectangle {
                                width: 44
                                height: 26
                                radius: 5
                                color: motion.travelDistance === modelData ? (Theme.isDark ? "#1E293B" : "#192D78") : (chipMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                                border.color: motion.travelDistance === modelData ? (Theme.isDark ? "#354B94" : "#192D78") : Theme.borderInput
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData + "mm"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                    color: motion.travelDistance === modelData ? "#FFFFFF" : Theme.textPrimary
                                }

                                MouseArea {
                                    id: chipMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: motion.setTravel(modelData)
                                }
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // Jog Pad & Z Elevation Row (Centrally Aligned)
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 18

                        // 4-Way XY Pad
                        ColumnLayout {
                            spacing: 8
                            Layout.alignment: Qt.AlignHCenter

                            Text {
                                text: "XY STAGE"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }

                            JogPad {
                                Layout.preferredWidth: 240
                                Layout.preferredHeight: 240
                                onJogClicked: function(dir) { motion.jog(dir) }
                                onCenterClicked: motion.centerXY()
                            }
                        }

                        // Z Elevation Strip
                        ColumnLayout {
                            spacing: 8
                            Layout.alignment: Qt.AlignHCenter

                            Text {
                                text: "Z ELEVATION"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Rectangle {
                                width: 80
                                height: 240
                                radius: 8
                                color: Theme.isDark ? "#111827" : "#F8FAFC"
                                border.color: Theme.borderCard
                                border.width: 1

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 8

                                    // +Z Button
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 38
                                        radius: 6
                                        color: zUpMa.down ? Qt.darker(Theme.btnPrimaryBg, 1.15) : (zUpMa.containsMouse ? Theme.btnPrimaryHover : Theme.btnPrimaryBg)
                                        border.color: Theme.btnPrimaryBorder
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: "▲ +Z"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: "#FFFFFF"
                                        }

                                        MouseArea {
                                            id: zUpMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: motion.jog("zplus")
                                        }
                                    }

                                    // Center Spacer with Guideline and Center Button
                                    Item {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true

                                        Rectangle {
                                            width: 2
                                            height: parent.height - 20
                                            anchors.centerIn: parent
                                            color: Theme.borderCard
                                        }

                                        Rectangle {
                                            width: 56
                                            height: 28
                                            radius: 6
                                            anchors.centerIn: parent
                                            color: centerZMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg
                                            border.color: Theme.borderCard
                                            border.width: 1

                                            Text {
                                                anchors.centerIn: parent
                                                text: "Center"
                                                font.family: "Inter"
                                                font.pixelSize: 10
                                                font.weight: Font.DemiBold
                                                color: Theme.textPrimary
                                            }

                                            MouseArea {
                                                id: centerZMa
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: motion.centerZ()
                                            }
                                        }

                                        Text {
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            anchors.bottom: parent.bottom
                                            anchors.bottomMargin: 2
                                            text: "Z " + motion.zMaxLimit + " mm"
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 9
                                            color: Theme.textSecondary
                                        }
                                    }

                                    // -Z Button
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 38
                                        radius: 6
                                        color: zDownMa.down ? Qt.darker(Theme.btnPrimaryBg, 1.15) : (zDownMa.containsMouse ? Theme.btnPrimaryHover : Theme.btnPrimaryBg)
                                        border.color: Theme.btnPrimaryBorder
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: "▼ -Z"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: "#FFFFFF"
                                        }

                                        MouseArea {
                                            id: zDownMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: motion.jog("zminus")
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // Lower Jogging Shortcuts Guide
                    Rectangle {
                        Layout.fillWidth: true
                        height: 34
                        radius: 6
                        color: Theme.isDark ? "#111827" : "#F8FAFC"
                        border.color: Theme.borderCard
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10

                            Text {
                                text: "⌨  [← ↑ → ↓] XY  •  [PgUp/Dn] Z"
                                font.family: "Inter"
                                font.pixelSize: 10
                                color: Theme.textSecondary
                            }

                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 6
                                height: 6
                                radius: 3
                                color: Theme.accentAmber
                            }

                            Text {
                                text: motion.travelDistance + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                        }
                    }
                }

                // ==========================================
                // Column 2: 2D Bed Workspace & Target Reticle
                // ==========================================
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 480
                    Layout.minimumWidth: 380
                    Layout.fillHeight: true
                    title: "2D Bed workspace"
                    subtitle: "Live reticle"
                    accentColor: Theme.accentCyan

                    LiveBedRadar {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                }

                // ==========================================
                // Column 3: Motion Parameters & Routines
                // ==========================================
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 440
                    Layout.minimumWidth: 360
                    Layout.fillHeight: true
                    title: "Motion parameters"
                    subtitle: "Limits & homing"
                    accentColor: Theme.accentAmber

                    // Jog Feedrate Slider
                    SliderControl {
                        Layout.fillWidth: true
                        label: "Jog feedrate"
                        from: 100
                        to: 2000
                        stepSize: 50
                        value: motion.jogFeed
                        unit: "mm/min"
                        onValueModified: function(v) { motion.setFeed(v) }
                    }

                    // Feedrate Quick Speed Chips
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Layout.topMargin: -4
                        Layout.bottomMargin: 4

                        Text {
                            text: "SPEED"
                            font.family: "Inter"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }

                        Repeater {
                            model: [
                                { label: "500 Slow", val: 500 },
                                { label: "1200 Std", val: 1200 },
                                { label: "2000 Max", val: 2000 }
                            ]

                            delegate: Rectangle {
                                width: 72
                                height: 26
                                radius: 5
                                color: motion.jogFeed === modelData.val ? (Theme.isDark ? "#1E293B" : "#192D78") : (speedMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                                border.color: motion.jogFeed === modelData.val ? Theme.accentAmber : Theme.borderInput
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.label
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                    color: motion.jogFeed === modelData.val ? "#FFFFFF" : Theme.textPrimary
                                }

                                MouseArea {
                                    id: speedMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: motion.setFeed(modelData.val)
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: Theme.borderCard
                        Layout.topMargin: 2
                        Layout.bottomMargin: 2
                    }

                    Text {
                        text: "AXIS REFERENCE & HOMING"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: Theme.textSecondary
                    }

                    // Primary Home All Axes Button
                    AppButton {
                        Layout.fillWidth: true
                        text: "⌂  Home all axes"
                        variant: "primary"
                        onClicked: motion.homeAll()
                    }

                    // Individual Axis Homing Row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 6
                            color: hxMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg
                            border.color: Theme.borderInput
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "⌂ Home X"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }

                            MouseArea {
                                id: hxMa
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: motion.homeAxis("X")
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 6
                            color: hyMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg
                            border.color: Theme.borderInput
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "⌂ Home Y"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }

                            MouseArea {
                                id: hyMa
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: motion.homeAxis("Y")
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 6
                            color: hzMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg
                            border.color: Theme.borderInput
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "⌂ Home Z"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }

                            MouseArea {
                                id: hzMa
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: motion.homeAxis("Z")
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // Machine Envelope Info Box
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: envCol.implicitHeight + 18
                        radius: 8
                        color: Theme.isDark ? "#111827" : "#F8FAFC"
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            id: envCol
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 5

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "MACHINE ENVELOPE"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: Theme.accentAmber
                                }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: "G54 WORK COORD"
                                    font.family: "IBM Plex Mono"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.accentCyan
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Bed dimensions"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Theme.textPrimary }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Z travel safety ceiling"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: motion.zMaxLimit.toFixed(1) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Theme.textPrimary }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Center datum"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: "X" + motion.xCenter.toFixed(1) + " Y" + motion.yCenter.toFixed(1) + " Z" + motion.zCenter.toFixed(1); font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Theme.textPrimary }
                            }
                        }
                    }
                }
            }

            // 3. Bottom Machine Motion Reference Banner
            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 8
                color: Theme.isDark ? "#111827" : "#E9EDF9"
                border.color: Theme.isDark ? "#1E293B" : "#DCE2EC"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Manual positioning"
                            font.family: "Inter"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.isDark ? Theme.accentAmber : "#192D78"
                        }
                        Text {
                            text: "Each jog command moves the selected axis by the active step distance."
                            font.family: "Inter"
                            font.pixelSize: 10
                            color: Theme.textSecondary
                        }
                    }

                    Item { Layout.fillWidth: true }

                    RowLayout {
                        spacing: 16

                        RowLayout {
                            spacing: 6
                            Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentAmber }
                            Text {
                                text: motion.travelDistance + " mm step"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.isDark ? "#FFFFFF" : "#192D78"
                            }
                        }

                        RowLayout {
                            spacing: 6
                            Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentCyan }
                            Text {
                                text: motion.jogFeed + " mm/min"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.isDark ? "#FFFFFF" : "#192D78"
                            }
                        }
                    }
                }
            }
        }
    }
}
