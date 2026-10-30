import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import ".."

Item {
    id: root

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 20

            // ---------------- 1. TOP FOCAL STATS ROW ---------------- //
            RowLayout {
                Layout.fillWidth: true
                spacing: 14

                // Card 1: Current Z Height
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: Theme.isDark ? "#151821" : "#F8FAFC"
                    radius: 8
                    border.color: Theme.borderCard
                    border.width: 1

                    Rectangle {
                        width: parent.width - 16; height: 2
                        anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
                        color: "#00d2ff"; radius: 1
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "CURRENT Z-AXIS HEIGHT"
                                color: "#00d2ff"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                            }
                            Item { Layout.fillWidth: true }
                            Rectangle {
                                width: 110; height: 22; radius: 4
                                color: setFocusMouse.containsMouse ? "#00d2ff" : (Theme.isDark ? "#202534" : "#E2E8F0")
                                border.color: "#00d2ff"; border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "💾 SET AS BASE FOCUS"
                                    color: setFocusMouse.containsMouse ? "#0c0e14" : (Theme.isDark ? "#00d2ff" : "#0284C7")
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                }
                                MouseArea {
                                    id: setFocusMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: if (typeof jog !== "undefined") jog.setAsBaseFocus()
                                }
                            }
                        }

                        RowLayout {
                            spacing: 8
                            Text {
                                text: (typeof jog !== "undefined" ? (jog.zPos >= 0 ? "+" : "") + jog.zPos.toFixed(3) : "+027.000")
                                color: Theme.textPrimary
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: Theme.textMuted
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "Physical Z Range: 0.00 mm (Min) to 120.00 mm (Max)"
                            color: Theme.textMuted
                            font.pixelSize: 10
                        }
                    }
                }

                // Card 2: Calibrated Base Focus
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: Theme.isDark ? "#151821" : "#F8FAFC"
                    radius: 8
                    border.color: Theme.borderCard
                    border.width: 1

                    Rectangle {
                        width: parent.width - 16; height: 2
                        anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
                        color: "#2ed573"; radius: 1
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "CALIBRATED BASE FOCUS (FOCAL DATUM)"
                                color: "#2ed573"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                            }
                            Item { Layout.fillWidth: true }
                        }

                        RowLayout {
                            spacing: 8
                            Text {
                                text: (typeof jog !== "undefined" ? jog.baseFocusZ.toFixed(3) : "27.000")
                                color: Theme.textPrimary
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: Theme.textMuted
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "F-Theta lens optical focal distance from machine bed"
                            color: Theme.textMuted
                            font.pixelSize: 10
                        }
                    }
                }

                // Card 3: Target Workpiece Focus
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: Theme.isDark ? "#151821" : "#F8FAFC"
                    radius: 8
                    border.color: Theme.borderCard
                    border.width: 1

                    Rectangle {
                        width: parent.width - 16; height: 2
                        anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
                        color: "#f5a623"; radius: 1
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "CALCULATED TARGET"
                                color: "#f5a623"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                            }
                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 110; height: 22; radius: 4
                                color: moveTargetMouse.containsMouse ? "#d48810" : "#f5a623"

                                Text {
                                    anchors.centerIn: parent
                                    text: "🎯 GO TO TARGET"
                                    color: "#0c0e14"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                }
                                MouseArea {
                                    id: moveTargetMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: if (typeof jog !== "undefined") jog.moveToTargetFocus()
                                }
                            }
                        }

                        RowLayout {
                            spacing: 8
                            Text {
                                text: (typeof jog !== "undefined" ? jog.targetFocusZ.toFixed(3) : "27.000")
                                color: Theme.textPrimary
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: Theme.textMuted
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "= Base (" + (typeof jog !== "undefined" ? jog.baseFocusZ.toFixed(1) : "27.0") +
                                  ") - Obj (" + (typeof jog !== "undefined" ? jog.objectHeight.toFixed(1) : "0.0") +
                                  ") + Sample (" + (typeof jog !== "undefined" ? jog.sampleHeight.toFixed(1) : "0.0") + ") mm"
                            color: Theme.isDark ? "#8a7550" : "#B45309"
                            font.pixelSize: 10
                        }
                    }
                }
            }

            // ---------------- 2. MAIN 3-COLUMN CONTROL PANELS ---------------- //
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                // Column 1: Z-Axis Motor Motion & Jog Increments
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    Layout.preferredHeight: 410
                    color: Theme.isDark ? "#161a24" : "#F8FAFC"
                    radius: 10
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Text {
                            text: "1. Z-AXIS MOTOR MOTION & FINE JOG"
                            color: Theme.isDark ? "#8e9cb0" : "#475569"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        // Large Z Up/Down Buttons
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 52
                                text: "▲  Z+ / RAISE HEAD (UP)"
                                primary: true
                                onClicked: if (typeof jog !== "undefined") jog.jogZ(1)
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 52
                                text: "▼  Z- / LOWER HEAD (DOWN)"
                                primary: true
                                onClicked: if (typeof jog !== "undefined") jog.jogZ(-1)
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                        // Step Increment Selector
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Jog Step Increment:"
                                color: Theme.textSecondary
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }

                            StepSelector {
                                Layout.fillWidth: true
                                stepValues: [10.0, 5.0, 1.0, 0.1]
                                currentStep: typeof jog !== "undefined" ? jog.stepSize : 5.0
                                onStepSelected: function(step) {
                                    if (typeof jog !== "undefined") jog.setStepSize(step)
                                }
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                        // Direct Height Entry
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            TextField {
                                id: directZInput
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: typeof jog !== "undefined" ? jog.zPos.toFixed(2) : "27.00"
                                placeholderText: "Height (mm)"
                                color: Theme.textPrimary
                                font.pixelSize: 13
                                background: Rectangle {
                                    color: Theme.isDark ? "#11141c" : "#FFFFFF"
                                    radius: 6
                                    border.color: Theme.borderInput
                                }
                            }

                            ModernButton {
                                text: "Go to Z"
                                implicitWidth: 90
                                implicitHeight: 38
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: {
                                    var val = parseFloat(directZInput.text)
                                    if (!isNaN(val) && typeof jog !== "undefined") {
                                        jog.moveToZ(val)
                                    }
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 4
                            color: Theme.isDark ? "#11141c" : "#FFFFFF"
                            border.color: Theme.borderCard

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 6; height: 6; radius: 3; color: "#00d2ff" }
                                Text {
                                    text: "Z-Axis Limit: Top & Bed Monitored"
                                    color: Theme.textMuted
                                    font.pixelSize: 10
                                }
                            }
                        }
                    }
                }

                // Column 2: Focus Offsets & Workpiece Parameters (from Laser Config)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    Layout.preferredHeight: 410
                    color: Theme.isDark ? "#161a24" : "#F8FAFC"
                    radius: 10
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Text {
                            text: "2. FOCAL HEIGHT OFFSETS & MATERIAL"
                            color: Theme.isDark ? "#8e9cb0" : "#475569"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        // Workpiece / Object Thickness
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Workpiece / Material Thickness (mm):"
                                color: Theme.textPrimary
                                font.pixelSize: 12
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                TextField {
                                    id: objHeightInput
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 38
                                    text: typeof jog !== "undefined" ? jog.objectHeight.toFixed(2) : "0.00"
                                    placeholderText: "Thickness mm"
                                    color: Theme.textPrimary
                                    font.pixelSize: 13
                                    background: Rectangle {
                                        color: Theme.isDark ? "#11141c" : "#FFFFFF"
                                        radius: 6
                                        border.color: Theme.borderInput
                                    }
                                }

                                ModernButton {
                                    text: "Apply"
                                    implicitWidth: 80
                                    implicitHeight: 38
                                    primary: true
                                    onClicked: {
                                        var val = parseFloat(objHeightInput.text)
                                        if (!isNaN(val) && typeof jog !== "undefined") {
                                            jog.setObjectHeight(val)
                                        }
                                    }
                                }
                            }
                        }

                        // Sample / Fixture Height
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Sample / Fixture Height Offset (mm):"
                                color: Theme.textPrimary
                                font.pixelSize: 12
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                TextField {
                                    id: sampleHeightInput
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 38
                                    text: typeof jog !== "undefined" ? jog.sampleHeight.toFixed(2) : "0.00"
                                    placeholderText: "Offset mm"
                                    color: Theme.textPrimary
                                    font.pixelSize: 13
                                    background: Rectangle {
                                        color: Theme.isDark ? "#11141c" : "#FFFFFF"
                                        radius: 6
                                        border.color: Theme.borderInput
                                    }
                                }

                                ModernButton {
                                    text: "Apply"
                                    implicitWidth: 80
                                    implicitHeight: 38
                                    primary: true
                                    onClicked: {
                                        var val = parseFloat(sampleHeightInput.text)
                                        if (!isNaN(val) && typeof jog !== "undefined") {
                                            jog.setSampleHeight(val)
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                        // Focus Guide Lasers
                        Text {
                            text: "OPTICAL FOCUS ALIGNMENT GUIDES"
                            color: Theme.isDark ? "#8e9cb0" : "#475569"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                text: (typeof jog !== "undefined" && jog.redPointerOn) ? "🔴 Red Pointer ON" : "⚪ Red Pointer OFF"
                                btnColor: (typeof jog !== "undefined" && jog.redPointerOn) ? "#7a2a10" : (Theme.isDark ? "#222736" : "#FFFFFF")
                                borderColor: (typeof jog !== "undefined" && jog.redPointerOn) ? "#e67e22" : Theme.borderCard
                                textColor: Theme.textPrimary
                                onClicked: if (typeof jog !== "undefined") jog.toggleRedPointer()
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                text: (typeof jog !== "undefined" && jog.guideLaserOn) ? "⚡ Focus Beam ON" : "⚪ Focus Beam OFF"
                                btnColor: (typeof jog !== "undefined" && jog.guideLaserOn) ? "#7a1a1a" : (Theme.isDark ? "#222736" : "#FFFFFF")
                                borderColor: (typeof jog !== "undefined" && jog.guideLaserOn) ? "#ff4757" : Theme.borderCard
                                textColor: Theme.textPrimary
                                onClicked: if (typeof jog !== "undefined") jog.toggleGuideLaser()
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 4
                            color: Theme.isDark ? "#11141c" : "#FFFFFF"
                            border.color: Theme.borderCard

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 6; height: 6; radius: 3; color: "#f5a623" }
                                Text {
                                    text: "Net Focus Offset: " + ((typeof jog !== "undefined" ? (jog.sampleHeight - jog.objectHeight) : 0.0) >= 0 ? "+" : "") + (typeof jog !== "undefined" ? (jog.sampleHeight - jog.objectHeight).toFixed(2) : "0.00") + " mm"
                                    color: Theme.textMuted
                                    font.pixelSize: 10
                                }
                            }
                        }
                    }
                }

                // Column 3: Homing & Quick Focus Burn Tests
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    Layout.preferredHeight: 410
                    color: Theme.isDark ? "#161a24" : "#F8FAFC"
                    radius: 10
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "3. HOMING & PATTERN TESTS"
                            color: Theme.isDark ? "#8e9cb0" : "#475569"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 46
                            text: "⌂  HOME ALL (GALVO + Z)"
                            primary: true
                            onClicked: if (typeof jog !== "undefined") jog.homeAll()
                        }

                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                            text: "⌂  Home Z-Axis (Limit Switch)"
                            btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                            textColor: Theme.textPrimary
                            borderColor: Theme.borderCard
                            onClicked: if (typeof jog !== "undefined") jog.homeZ()
                        }

                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                            text: "🎯  Center Galvo Mirrors (XY)"
                            btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                            textColor: Theme.textPrimary
                            borderColor: Theme.borderCard
                            onClicked: if (typeof jog !== "undefined") jog.homeGalvo()
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                        Text {
                            text: "QUICK FOCAL TEST BURNS (GALVO)"
                            color: Theme.isDark ? "#8e9cb0" : "#475569"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: "◯ Circle"
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("circle")
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: "△ Triangle"
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("triangle")
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: "□ Square"
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("square")
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 4
                            color: Theme.isDark ? "#11141c" : "#FFFFFF"
                            border.color: Theme.borderCard

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 6; height: 6; radius: 3; color: "#2ed573" }
                                Text {
                                    text: "Z Stepper: 333.33 pulses/mm"
                                    color: Theme.textMuted
                                    font.pixelSize: 10
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
