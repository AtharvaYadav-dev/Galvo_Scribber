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

            // Laser Warning / Active Banner
            Rectangle {
                Layout.fillWidth: true
                height: 54
                radius: 8
                color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#33ff4757" : "#1a2233"
                border.color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#ff4757" : "#2d374d"
                border.width: 1.5

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Rectangle {
                        width: 14
                        height: 14
                        radius: 7
                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#ff4757" : (typeof galvo !== "undefined" && galvo.redPointerOn ? "#ff9f43" : "#2ed573")

                        SequentialAnimation on opacity {
                            running: (typeof galvo !== "undefined" && galvo.isLaserFiring)
                            loops: Animation.Infinite
                            PropertyAnimation { from: 1.0; to: 0.2; duration: 400 }
                            PropertyAnimation { from: 0.2; to: 1.0; duration: 400 }
                        }
                    }

                    Text {
                        text: (typeof galvo !== "undefined" && galvo.isLaserFiring)
                              ? "⚠️ LASER EMISSION ACTIVE - BEAM FIRING"
                              : ((typeof galvo !== "undefined" && galvo.redPointerOn) ? "Guide Red Pointer Active" : "Laser Ready / Standby")
                        color: (typeof galvo !== "undefined" && galvo.isLaserFiring) ? "#ff4757" : "#ffffff"
                        font.pixelSize: 13
                        font.weight: Font.Bold
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: typeof galvo !== "undefined" ? galvo.statusMessage : ""
                        color: "#8e9cb0"
                        font.pixelSize: 12
                    }
                }
            }

            // Parameter Sliders & Hardware Trigger Card
            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                // Column 1: Power, Speed, Frequency Sliders
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 380
                    color: "#161a24"
                    radius: 10
                    border.color: "#283042"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 24

                        Text {
                            text: "LASER OPERATING PARAMETERS"
                            color: "#8e9cb0"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        // Power Slider
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Laser Power (%)"; color: "#ffffff"; font.pixelSize: 13 }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: (typeof galvo !== "undefined" ? galvo.power.toFixed(0) : "20") + " %"
                                    color: "#00d2ff"; font.pixelSize: 14; font.weight: Font.Bold
                                }
                            }

                            Slider {
                                id: powerSlider
                                Layout.fillWidth: true
                                from: 1; to: 100
                                value: typeof galvo !== "undefined" ? galvo.power : 20
                                onMoved: if (typeof galvo !== "undefined") galvo.setPower(value)
                            }
                        }

                        // Mark Speed Slider
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Marking Speed (mm/s)"; color: "#ffffff"; font.pixelSize: 13 }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: (typeof galvo !== "undefined" ? galvo.speed.toFixed(0) : "1000") + " mm/s"
                                    color: "#00d2ff"; font.pixelSize: 14; font.weight: Font.Bold
                                }
                            }

                            Slider {
                                id: speedSlider
                                Layout.fillWidth: true
                                from: 50; to: 5000; stepSize: 50
                                value: typeof galvo !== "undefined" ? galvo.speed : 1000
                                onMoved: if (typeof galvo !== "undefined") galvo.setSpeed(value)
                            }
                        }

                        // Frequency Slider
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Q-Switch Frequency (kHz)"; color: "#ffffff"; font.pixelSize: 13 }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: (typeof galvo !== "undefined" ? galvo.frequency.toFixed(0) : "30") + " kHz"
                                    color: "#00d2ff"; font.pixelSize: 14; font.weight: Font.Bold
                                }
                            }

                            Slider {
                                id: freqSlider
                                Layout.fillWidth: true
                                from: 20; to: 80; stepSize: 1
                                value: typeof galvo !== "undefined" ? galvo.frequency : 30
                                onMoved: if (typeof galvo !== "undefined") galvo.setFrequency(value)
                            }
                        }
                    }
                }

                // Column 2: Test Fire & Guide Controls
                Rectangle {
                    Layout.preferredWidth: 360
                    Layout.preferredHeight: 380
                    color: "#161a24"
                    radius: 10
                    border.color: "#283042"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 16

                        Text {
                            text: "TESTING & ALIGNMENT"
                            color: "#8e9cb0"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                        }

                        // Red Pointer Toggle
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 46
                            text: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "🔴 Turn Red Pointer OFF" : "🔴 Turn Red Pointer ON"
                            btnColor: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#7a2a10" : "#222736"
                            borderColor: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#e67e22" : "#353d54"
                            onClicked: if (typeof galvo !== "undefined") galvo.toggleRedPointer()
                        }

                        // Home Galvo
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 46
                            text: "🎯 Center Galvo Mirrors (Home)"
                            primary: true
                            onClicked: if (typeof galvo !== "undefined") galvo.homeGalvo()
                        }

                        // Fire Test Pattern
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 52
                            text: "⚡ Fire Test Square Pattern"
                            btnColor: "#1d293d"
                            borderColor: "#00d2ff"
                            textColor: "#00d2ff"
                            onClicked: if (typeof galvo !== "undefined") galvo.testPattern()
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#283042"
                        }

                        // Emergency Stop Button
                        ModernButton {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 56
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
