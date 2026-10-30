import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Item {
    id: root

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 16

            // ================= 1. ACTIVE EMISSION / STATUS BANNER ================= //
            Rectangle {
                Layout.fillWidth: true
                height: 52
                radius: 8
                color: (typeof galvo !== "undefined" && galvo.isLaserFiring) 
                       ? (Theme.isDark ? "#381216" : "#FEE2E2")
                       : ((typeof galvo !== "undefined" && galvo.redPointerOn) 
                          ? (Theme.isDark ? "#2E200C" : "#FEF3C7") 
                          : (Theme.isDark ? "#10192D" : "#F1F5F9"))
                border.color: (typeof galvo !== "undefined" && galvo.isLaserFiring) 
                              ? "#EF4444" 
                              : ((typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : Theme.border)
                border.width: (typeof galvo !== "undefined" && (galvo.isLaserFiring || galvo.redPointerOn)) ? 1.5 : 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 12

                    Rectangle {
                        width: 12
                        height: 12
                        radius: 6
                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring) 
                               ? "#EF4444" 
                               : ((typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : "#10B981")

                        SequentialAnimation on opacity {
                            running: (typeof galvo !== "undefined" && galvo.isLaserFiring)
                            loops: Animation.Infinite
                            PropertyAnimation { from: 1.0; to: 0.25; duration: 320 }
                            PropertyAnimation { from: 0.25; to: 1.0; duration: 320 }
                        }
                    }

                    Text {
                        text: (typeof galvo !== "undefined" && galvo.isLaserFiring)
                              ? "⚠️ MAIN LASER EMISSION ACTIVE — BEAM FIRING"
                              : ((typeof galvo !== "undefined" && galvo.redPointerOn) 
                                 ? "🔴 Guide Red Dot Pointer Active" 
                                 : "Laser Standby / Ready")
                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring) 
                               ? "#EF4444" 
                               : ((typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : Theme.textPrimary)
                        font.pixelSize: 13
                        font.weight: Font.Bold
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: typeof galvo !== "undefined" ? galvo.statusMessage : "Ready"
                        color: Theme.textSecondary
                        font.pixelSize: 12
                    }
                }
            }

            // ================= 2. MAIN 2-COLUMN PARAMETERS & CONTROLS ================= //
            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Layout.alignment: Qt.AlignTop

                // ---------------- COLUMN 1: LASER OPERATING PARAMETERS ---------------- //
                Rectangle {
                    Layout.fillWidth: true
                    Layout.minimumHeight: 460
                    color: Theme.bgCard
                    radius: 10
                    border.color: Theme.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 18

                        // Section Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text {
                                text: "tune"
                                font.family: "Material Icons"
                                font.pixelSize: 18
                                color: Theme.accentCyan
                            }
                            Text {
                                text: "LASER OPERATING PARAMETERS"
                                color: Theme.textSecondary
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                font.letterSpacing: 0.5
                            }
                        }

                        // 1. LASER POWER (%)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                RowLayout {
                                    spacing: 6
                                    Text {
                                        text: "flash_on"
                                        font.family: "Material Icons"
                                        font.pixelSize: 16
                                        color: "#F59E0B"
                                    }
                                    Text {
                                        text: "1. Laser Power (%)"
                                        color: Theme.textPrimary
                                        font.pixelSize: 13
                                        font.weight: Font.DemiBold
                                    }
                                }
                                Item { Layout.fillWidth: true }
                                Rectangle {
                                    width: 72; height: 26; radius: 5
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                    border.color: Theme.accentCyan
                                    border.width: 1
                                    Text {
                                        anchors.centerIn: parent
                                        text: (typeof galvo !== "undefined" ? galvo.power.toFixed(0) : "20") + " %"
                                        color: Theme.accentCyan
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                    }
                                }
                            }

                            Slider {
                                id: powerSlider
                                Layout.fillWidth: true
                                from: 1; to: 100; stepSize: 1
                                value: typeof galvo !== "undefined" ? galvo.power : 20
                                onMoved: if (typeof galvo !== "undefined") galvo.setPower(value)

                                background: Rectangle {
                                    x: powerSlider.leftPadding
                                    y: powerSlider.topPadding + powerSlider.availableHeight / 2 - height / 2
                                    width: powerSlider.availableWidth
                                    height: 6
                                    radius: 3
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                    Rectangle {
                                        width: powerSlider.visualPosition * parent.width
                                        height: parent.height
                                        radius: 3
                                        color: "#F59E0B"
                                    }
                                }

                                handle: Rectangle {
                                    x: powerSlider.leftPadding + powerSlider.visualPosition * (powerSlider.availableWidth - width)
                                    y: powerSlider.topPadding + powerSlider.availableHeight / 2 - height / 2
                                    width: 18; height: 18; radius: 9
                                    color: powerSlider.pressed ? "#FFFFFF" : "#F59E0B"
                                    border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                    border.width: 2
                                }
                            }
                        }

                        // 2. Q-SWITCH FREQUENCY (kHz)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                RowLayout {
                                    spacing: 6
                                    Text {
                                        text: "waves"
                                        font.family: "Material Icons"
                                        font.pixelSize: 16
                                        color: "#A855F7"
                                    }
                                    Text {
                                        text: "2. Q-Switch Frequency (kHz)"
                                        color: Theme.textPrimary
                                        font.pixelSize: 13
                                        font.weight: Font.DemiBold
                                    }
                                }
                                Item { Layout.fillWidth: true }
                                Rectangle {
                                    width: 72; height: 26; radius: 5
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                    border.color: "#A855F7"
                                    border.width: 1
                                    Text {
                                        anchors.centerIn: parent
                                        text: (typeof galvo !== "undefined" ? galvo.frequency.toFixed(0) : "30") + " kHz"
                                        color: "#A855F7"
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                    }
                                }
                            }

                            Slider {
                                id: freqSlider
                                Layout.fillWidth: true
                                from: 20; to: 80; stepSize: 1
                                value: typeof galvo !== "undefined" ? galvo.frequency : 30
                                onMoved: if (typeof galvo !== "undefined") galvo.setFrequency(value)

                                background: Rectangle {
                                    x: freqSlider.leftPadding
                                    y: freqSlider.topPadding + freqSlider.availableHeight / 2 - height / 2
                                    width: freqSlider.availableWidth
                                    height: 6
                                    radius: 3
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                    Rectangle {
                                        width: freqSlider.visualPosition * parent.width
                                        height: parent.height
                                        radius: 3
                                        color: "#A855F7"
                                    }
                                }

                                handle: Rectangle {
                                    x: freqSlider.leftPadding + freqSlider.visualPosition * (freqSlider.availableWidth - width)
                                    y: freqSlider.topPadding + freqSlider.availableHeight / 2 - height / 2
                                    width: 18; height: 18; radius: 9
                                    color: freqSlider.pressed ? "#FFFFFF" : "#A855F7"
                                    border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                    border.width: 2
                                }
                            }
                        }

                        // 3. MARKING SPEED (mm/s)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                RowLayout {
                                    spacing: 6
                                    Text {
                                        text: "speed"
                                        font.family: "Material Icons"
                                        font.pixelSize: 16
                                        color: Theme.accentCyan
                                    }
                                    Text {
                                        text: "3. Marking Speed (mm/s)"
                                        color: Theme.textPrimary
                                        font.pixelSize: 13
                                        font.weight: Font.DemiBold
                                    }
                                }
                                Item { Layout.fillWidth: true }
                                Rectangle {
                                    width: 88; height: 26; radius: 5
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                    border.color: Theme.accentCyan
                                    border.width: 1
                                    Text {
                                        anchors.centerIn: parent
                                        text: (typeof galvo !== "undefined" ? galvo.speed.toFixed(0) : "1000") + " mm/s"
                                        color: Theme.accentCyan
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                    }
                                }
                            }

                            Slider {
                                id: speedSlider
                                Layout.fillWidth: true
                                from: 10; to: 5000; stepSize: 50
                                value: typeof galvo !== "undefined" ? galvo.speed : 1000
                                onMoved: if (typeof galvo !== "undefined") galvo.setSpeed(value)

                                background: Rectangle {
                                    x: speedSlider.leftPadding
                                    y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                    width: speedSlider.availableWidth
                                    height: 6
                                    radius: 3
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                    Rectangle {
                                        width: speedSlider.visualPosition * parent.width
                                        height: parent.height
                                        radius: 3
                                        color: Theme.accentCyan
                                    }
                                }

                                handle: Rectangle {
                                    x: speedSlider.leftPadding + speedSlider.visualPosition * (speedSlider.availableWidth - width)
                                    y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                    width: 18; height: 18; radius: 9
                                    color: speedSlider.pressed ? "#FFFFFF" : Theme.accentCyan
                                    border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                    border.width: 2
                                }
                            }
                        }

                        // 4. JUMP SPEED (mm/s)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                RowLayout {
                                    spacing: 6
                                    Text {
                                        text: "fast_forward"
                                        font.family: "Material Icons"
                                        font.pixelSize: 16
                                        color: "#10B981"
                                    }
                                    Text {
                                        text: "4. Jump Speed (mm/s)"
                                        color: Theme.textPrimary
                                        font.pixelSize: 13
                                        font.weight: Font.DemiBold
                                    }
                                }
                                Item { Layout.fillWidth: true }
                                Rectangle {
                                    width: 88; height: 26; radius: 5
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                    border.color: "#10B981"
                                    border.width: 1
                                    Text {
                                        anchors.centerIn: parent
                                        text: (typeof galvo !== "undefined" ? galvo.jumpSpeed.toFixed(0) : "2000") + " mm/s"
                                        color: "#10B981"
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                    }
                                }
                            }

                            Slider {
                                id: jumpSlider
                                Layout.fillWidth: true
                                from: 50; to: 8000; stepSize: 50
                                value: typeof galvo !== "undefined" ? galvo.jumpSpeed : 2000
                                onMoved: if (typeof galvo !== "undefined") galvo.setJumpSpeed(value)

                                background: Rectangle {
                                    x: jumpSlider.leftPadding
                                    y: jumpSlider.topPadding + jumpSlider.availableHeight / 2 - height / 2
                                    width: jumpSlider.availableWidth
                                    height: 6
                                    radius: 3
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                    Rectangle {
                                        width: jumpSlider.visualPosition * parent.width
                                        height: parent.height
                                        radius: 3
                                        color: "#10B981"
                                    }
                                }

                                handle: Rectangle {
                                    x: jumpSlider.leftPadding + jumpSlider.visualPosition * (jumpSlider.availableWidth - width)
                                    y: jumpSlider.topPadding + jumpSlider.availableHeight / 2 - height / 2
                                    width: 18; height: 18; radius: 9
                                    color: jumpSlider.pressed ? "#FFFFFF" : "#10B981"
                                    border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                    border.width: 2
                                }
                            }
                        }
                    }
                }

                // ---------------- COLUMN 2: HARDWARE EMISSION & ALIGNMENT ---------------- //
                Rectangle {
                    Layout.preferredWidth: 380
                    Layout.minimumHeight: 460
                    color: Theme.bgCard
                    radius: 10
                    border.color: Theme.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        // Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text {
                                text: "settings_remote"
                                font.family: "Material Icons"
                                font.pixelSize: 18
                                color: Theme.accentAmber
                            }
                            Text {
                                text: "TESTING & HARDWARE CONTROL"
                                color: Theme.textSecondary
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                font.letterSpacing: 0.5
                            }
                        }

                        // 1. RED DOT ON / OFF CARD
                        Rectangle {
                            Layout.fillWidth: true
                            height: 78
                            radius: 8
                            color: Theme.isDark ? "#141F36" : "#F8FAFC"
                            border.color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : Theme.border
                            border.width: (typeof galvo !== "undefined" && galvo.redPointerOn) ? 1.5 : 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8

                                RowLayout {
                                    Layout.fillWidth: true
                                    RowLayout {
                                        spacing: 6
                                        Text {
                                            text: "fiber_manual_record"
                                            font.family: "Material Icons"
                                            font.pixelSize: 14
                                            color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#EF4444" : Theme.textMuted
                                        }
                                        Text {
                                            text: "Red Dot Guide Pointer"
                                            color: Theme.textPrimary
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                        }
                                    }
                                    Item { Layout.fillWidth: true }
                                    Rectangle {
                                        width: 54; height: 20; radius: 10
                                        color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#4D2800" : (Theme.isDark ? "#1E2C4A" : "#E2E8F0")
                                        border.color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : "transparent"
                                        Text {
                                            anchors.centerIn: parent
                                            text: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "ON" : "OFF"
                                            color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : Theme.textMuted
                                            font.pixelSize: 10
                                            font.weight: Font.Bold
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    // RED DOT ON BUTTON
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        radius: 6
                                        color: (typeof galvo !== "undefined" && galvo.redPointerOn)
                                               ? (redOnMouse.pressed ? "#D97706" : (redOnMouse.containsMouse ? "#FBBF24" : "#F59E0B"))
                                               : (redOnMouse.containsMouse ? (Theme.isDark ? "#28344E" : "#E2E8F0") : (Theme.isDark ? "#1A2640" : "#F1F5F9"))
                                        border.color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#F59E0B" : Theme.border
                                        border.width: 1

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 6
                                            Text {
                                                text: "play_arrow"
                                                font.family: "Material Icons"
                                                font.pixelSize: 14
                                                color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#FFFFFF" : Theme.textPrimary
                                            }
                                            Text {
                                                text: "Turn ON"
                                                color: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#FFFFFF" : Theme.textPrimary
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                            }
                                        }

                                        MouseArea {
                                            id: redOnMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (typeof galvo !== "undefined") galvo.turnRedPointerOn()
                                        }
                                    }

                                    // RED DOT OFF BUTTON
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        radius: 6
                                        color: (typeof galvo !== "undefined" && !galvo.redPointerOn)
                                               ? (redOffMouse.pressed ? "#334155" : (redOffMouse.containsMouse ? "#475569" : (Theme.isDark ? "#263554" : "#CBD5E1")))
                                               : (redOffMouse.containsMouse ? (Theme.isDark ? "#28344E" : "#E2E8F0") : (Theme.isDark ? "#1A2640" : "#F1F5F9"))
                                        border.color: (typeof galvo !== "undefined" && !galvo.redPointerOn) ? Theme.accentCyan : Theme.border
                                        border.width: (typeof galvo !== "undefined" && !galvo.redPointerOn) ? 1.5 : 1

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 6
                                            Text {
                                                text: "stop"
                                                font.family: "Material Icons"
                                                font.pixelSize: 14
                                                color: (typeof galvo !== "undefined" && !galvo.redPointerOn) ? Theme.textPrimary : Theme.textMuted
                                            }
                                            Text {
                                                text: "Turn OFF"
                                                color: (typeof galvo !== "undefined" && !galvo.redPointerOn) ? Theme.textPrimary : Theme.textMuted
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                            }
                                        }

                                        MouseArea {
                                            id: redOffMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (typeof galvo !== "undefined") galvo.turnRedPointerOff()
                                        }
                                    }
                                }
                            }
                        }

                        // 2. MAIN LASER ON / OFF CARD
                        Rectangle {
                            Layout.fillWidth: true
                            height: 78
                            radius: 8
                            color: Theme.isDark ? "#141F36" : "#F8FAFC"
                            border.color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#EF4444" : Theme.border
                            border.width: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? 1.5 : 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8

                                RowLayout {
                                    Layout.fillWidth: true
                                    RowLayout {
                                        spacing: 6
                                        Text {
                                            text: "bolt"
                                            font.family: "Material Icons"
                                            font.pixelSize: 15
                                            color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#EF4444" : Theme.textMuted
                                        }
                                        Text {
                                            text: "Main Laser Emission"
                                            color: Theme.textPrimary
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                        }
                                    }
                                    Item { Layout.fillWidth: true }
                                    Rectangle {
                                        width: 58; height: 20; radius: 10
                                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#450A0A" : (Theme.isDark ? "#1E2C4A" : "#E2E8F0")
                                        border.color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#EF4444" : "transparent"
                                        Text {
                                            anchors.centerIn: parent
                                            text: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "FIRING" : "OFF"
                                            color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#EF4444" : Theme.textMuted
                                            font.pixelSize: 10
                                            font.weight: Font.Bold
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    // MAIN LASER ON BUTTON
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        radius: 6
                                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring)
                                               ? (laserOnMouse.pressed ? "#B91C1C" : (laserOnMouse.containsMouse ? "#DC2626" : "#EF4444"))
                                               : (laserOnMouse.containsMouse ? (Theme.isDark ? "#28344E" : "#E2E8F0") : (Theme.isDark ? "#1A2640" : "#F1F5F9"))
                                        border.color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#EF4444" : Theme.border
                                        border.width: 1

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 6
                                            Text {
                                                text: "flash_on"
                                                font.family: "Material Icons"
                                                font.pixelSize: 14
                                                color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#FFFFFF" : Theme.textPrimary
                                            }
                                            Text {
                                                text: "Laser ON"
                                                color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#FFFFFF" : Theme.textPrimary
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                            }
                                        }

                                        MouseArea {
                                            id: laserOnMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (typeof galvo !== "undefined") galvo.turnLaserOn()
                                        }
                                    }

                                    // MAIN LASER OFF BUTTON
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 32
                                        radius: 6
                                        color: (typeof galvo !== "undefined" && !galvo.isLaserFiring)
                                               ? (laserOffMouse.pressed ? "#15803D" : (laserOffMouse.containsMouse ? "#16A34A" : "#10B981"))
                                               : (laserOffMouse.containsMouse ? (Theme.isDark ? "#28344E" : "#E2E8F0") : (Theme.isDark ? "#1A2640" : "#F1F5F9"))
                                        border.color: (typeof galvo !== "undefined" && !galvo.isLaserFiring) ? "#10B981" : Theme.border
                                        border.width: 1

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 6
                                            Text {
                                                text: "power_settings_new"
                                                font.family: "Material Icons"
                                                font.pixelSize: 14
                                                color: (typeof galvo !== "undefined" && !galvo.isLaserFiring) ? "#FFFFFF" : Theme.textMuted
                                            }
                                            Text {
                                                text: "Laser OFF"
                                                color: (typeof galvo !== "undefined" && !galvo.isLaserFiring) ? "#FFFFFF" : Theme.textMuted
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                            }
                                        }

                                        MouseArea {
                                            id: laserOffMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: if (typeof galvo !== "undefined") galvo.turnLaserOff()
                                        }
                                    }
                                }
                            }
                        }

                        // 3. CENTER MIRRORS (HOME)
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 44
                            text: "🎯 Center Galvo Mirrors (Home)"
                            primary: true
                            onClicked: if (typeof galvo !== "undefined") galvo.homeGalvo()
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.border
                        }

                        Item { Layout.fillHeight: true }

                        // 4. EMERGENCY LASER ABORT
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 52
                            text: "🛑 EMERGENCY LASER ABORT"
                            danger: true
                            onClicked: if (typeof galvo !== "undefined") galvo.emergencyStop()
                        }
                    }
                }
            }
        }
    }
}
