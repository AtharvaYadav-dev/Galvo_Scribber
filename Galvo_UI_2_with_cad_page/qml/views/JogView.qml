import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

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
                    color: "#151821"
                    radius: 8
                    border.color: "#272c3d"
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
                                color: setFocusMouse.containsMouse ? "#00d2ff" : "#202534"
                                border.color: "#00d2ff"; border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "💾 SET AS BASE FOCUS"
                                    color: setFocusMouse.containsMouse ? "#0c0e14" : "#00d2ff"
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
                                color: "#ffffff"
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: "#7e8b9e"
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "Physical Z Range: 0.00 mm (Min) to 120.00 mm (Max)"
                            color: "#5f6c80"
                            font.pixelSize: 10
                        }
                    }
                }

                // Card 2: Calibrated Base Focus
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: "#151821"
                    radius: 8
                    border.color: "#272c3d"
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
                            Text {
                                text: "galvo_z_focus"
                                color: "#5f6c80"
                                font.pixelSize: 10
                                font.family: "Consolas, monospace"
                            }
                        }

                        RowLayout {
                            spacing: 8
                            Text {
                                text: (typeof jog !== "undefined" ? jog.baseFocusZ.toFixed(3) : "27.000")
                                color: "#ffffff"
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: "#7e8b9e"
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "F-Theta lens optical focal distance from machine bed"
                            color: "#5f6c80"
                            font.pixelSize: 10
                        }
                    }
                }

                // Card 3: Target Workpiece Focus
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: "#151821"
                    radius: 8
                    border.color: "#3d301f"
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
                                text: "CALCULATED TARGET FOCUS"
                                color: "#f5a623"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                            }
                            Item { Layout.fillWidth: true }

                            Rectangle {
                                width: 140; height: 24; radius: 4
                                color: moveTargetMouse.containsMouse ? "#d48810" : "#f5a623"

                                Text {
                                    anchors.centerIn: parent
                                    text: "🎯 MOVE Z TO TARGET"
                                    color: "#0c0e14"
                                    font.pixelSize: 10
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
                                color: "#ffffff"
                                font.pixelSize: 28
                                font.weight: Font.DemiBold
                                font.family: "Consolas, 'Courier New', monospace"
                            }
                            Text {
                                text: "mm"
                                color: "#7e8b9e"
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignBottom
                            }
                        }

                        Text {
                            text: "= Base (" + (typeof jog !== "undefined" ? jog.baseFocusZ.toFixed(1) : "27.0") +
                                  ") - Obj (" + (typeof jog !== "undefined" ? jog.objectHeight.toFixed(1) : "0.0") +
                                  ") + Sample (" + (typeof jog !== "undefined" ? jog.sampleHeight.toFixed(1) : "0.0") + ") mm"
                            color: "#8a7550"
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
                    Layout.preferredHeight: 400
                    color: "#161a24"
                    radius: 10
                    border.color: "#283042"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Text {
                            text: "1. Z-AXIS MOTOR MOTION & FINE JOG"
                            color: "#8e9cb0"
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

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#283042" }

                        // Step Increment Selector
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Jog Step Increment:"
                                color: "#667488"
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

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#283042" }

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
                                color: "#ffffff"
                                font.pixelSize: 13
                                background: Rectangle {
                                    color: "#11141c"
                                    radius: 6
                                    border.color: "#283042"
                                }
                            }

                            ModernButton {
                                text: "Go to Z"
                                implicitWidth: 90
                                implicitHeight: 38
                                onClicked: {
                                    var val = parseFloat(directZInput.text)
                                    if (!isNaN(val) && typeof jog !== "undefined") {
                                        jog.moveToZ(val)
                                    }
                                }
                            }
                        }
                    }
                }

                // Column 2: Focus Offsets & Workpiece Parameters (from Laser Config)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 400
                    color: "#161a24"
                    radius: 10
                    border.color: "#283042"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        Text {
                            text: "2. FOCAL HEIGHT OFFSETS & MATERIAL"
                            color: "#8e9cb0"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        // Workpiece / Object Thickness
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Workpiece / Material Thickness (mm):"
                                color: "#ffffff"
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
                                    color: "#ffffff"
                                    font.pixelSize: 13
                                    background: Rectangle {
                                        color: "#11141c"
                                        radius: 6
                                        border.color: "#283042"
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
                                color: "#ffffff"
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
                                    color: "#ffffff"
                                    font.pixelSize: 13
                                    background: Rectangle {
                                        color: "#11141c"
                                        radius: 6
                                        border.color: "#283042"
                                    }
                                }

                                ModernButton {
                                    text: "Apply"
                                    implicitWidth: 80
                                    implicitHeight: 38
                                    onClicked: {
                                        var val = parseFloat(sampleHeightInput.text)
                                        if (!isNaN(val) && typeof jog !== "undefined") {
                                            jog.setSampleHeight(val)
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#283042" }

                        // Focus Guide Lasers
                        Text {
                            text: "OPTICAL FOCUS ALIGNMENT GUIDES"
                            color: "#8e9cb0"
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
                                btnColor: (typeof jog !== "undefined" && jog.redPointerOn) ? "#7a2a10" : "#222736"
                                borderColor: (typeof jog !== "undefined" && jog.redPointerOn) ? "#e67e22" : "#353d54"
                                onClicked: if (typeof jog !== "undefined") jog.toggleRedPointer()
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                text: (typeof jog !== "undefined" && jog.guideLaserOn) ? "⚡ Focus Beam ON" : "Focus Beam OFF"
                                btnColor: (typeof jog !== "undefined" && jog.guideLaserOn) ? "#7a1a1a" : "#222736"
                                borderColor: (typeof jog !== "undefined" && jog.guideLaserOn) ? "#ff4757" : "#353d54"
                                onClicked: if (typeof jog !== "undefined") jog.toggleGuideLaser()
                            }
                        }
                    }
                }

                // Column 3: Homing & Quick Focus Burn Tests
                Rectangle {
                    Layout.preferredWidth: 320
                    Layout.preferredHeight: 400
                    color: "#161a24"
                    radius: 10
                    border.color: "#283042"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 12

                        Text {
                            text: "3. HOMING & PATTERN TESTS"
                            color: "#8e9cb0"
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
                            onClicked: if (typeof jog !== "undefined") jog.homeZ()
                        }

                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                            text: "🎯  Center Galvo Mirrors (XY)"
                            onClicked: if (typeof jog !== "undefined") jog.homeGalvo()
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: "#283042" }

                        Text {
                            text: "QUICK FOCAL TEST BURNS (GALVO)"
                            color: "#8e9cb0"
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
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("circle")
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: "△ Triangle"
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("triangle")
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                text: "□ Square"
                                onClicked: if (typeof jog !== "undefined") jog.fireQuickShape("square")
                            }
                        }

                        Item { Layout.fillHeight: true }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            radius: 4
                            color: "#11141c"
                            border.color: "#242c3c"

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 6; height: 6; radius: 3; color: "#2ed573" }
                                Text {
                                    text: "Z Stepper: 333.33 pulses/mm"
                                    color: "#6c7a91"
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
