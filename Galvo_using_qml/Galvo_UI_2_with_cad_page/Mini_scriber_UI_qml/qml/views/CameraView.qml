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
        width: Math.max(root.availableWidth, 960)
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
                        text: "Camera Vision"
                        font.family: "Inter"
                        font.pixelSize: 26
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }
                    Text {
                        text: "Optical alignment microscope, toolpath inspection and fine stage positioning."
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

            // Main 2-Column Layout
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Left: Microscope Viewport
                MetricCard {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "Optical alignment microscope"
                    subtitle: "DirectShow video stream"
                    accentColor: Theme.accentAmber

                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        implicitHeight: 600
                        clip: true

                        Rectangle {
                            anchors.fill: parent
                            color: "#080D18"
                            radius: 8
                            border.color: Theme.borderCard
                            border.width: 1

                            // Live Camera Image
                            Image {
                                id: cameraImage
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectFit
                                cache: false
                                source: camera.isStreaming ? ("image://camera/live?id=" + camera.frameId) : ""

                                // Reticle overlay
                                Rectangle {
                                    id: reticleOverlay
                                    anchors.fill: parent
                                    color: "transparent"
                                    visible: camera.showReticle

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: camera.reticleSize * 2
                                        height: 1
                                        color: "#EF4444"
                                    }

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 1
                                        height: camera.reticleSize * 2
                                        color: "#EF4444"
                                    }

                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 40
                                        height: 40
                                        radius: 20
                                        color: "transparent"
                                        border.color: "#EF4444"
                                        border.width: 1
                                    }
                                }
                            }

                            // Placeholder when camera is stopped (Matching Figma)
                            ColumnLayout {
                                anchors.centerIn: parent
                                visible: !camera.isStreaming
                                spacing: 14

                                Rectangle {
                                    Layout.alignment: Qt.AlignHCenter
                                    width: 48
                                    height: 48
                                    radius: 10
                                    color: "#111827"
                                    border.color: "#1E293B"
                                    border.width: 1

                                    AppIcon { anchors.centerIn: parent; name: "videocam_off"; size: 26; iconColor: Theme.textSecondary }
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: "Camera is stopped"
                                    font.family: "Inter"
                                    font.pixelSize: 16
                                    font.weight: Font.Bold
                                    color: "#FFFFFF"
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: "Select a device on the right and click Start Camera to begin the\noptical view."
                                    font.family: "Inter"
                                    font.pixelSize: 12
                                    horizontalAlignment: Text.AlignHCenter
                                    color: "#94A3B8"
                                    lineHeight: 1.3
                                }
                            }

                            // Bottom Viewport Info Bar
                            RowLayout {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                anchors.margins: 14

                                Text {
                                    text: "SOURCE: " + (camera.selectedDeviceName ? camera.selectedDeviceName.toUpperCase() : "NO DEVICE")
                                    font.family: "IBM Plex Mono"
                                    font.pixelSize: 10
                                    color: "#64748B"
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    text: camera.showReticle ? "Crosshair reticle enabled" : "Reticle disabled"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    color: "#64748B"
                                }
                            }
                        }
                    }
                }

                // Right Column: Controls & Stage Jog
                ColumnLayout {
                    Layout.preferredWidth: 360
                    Layout.fillHeight: true
                    spacing: 18

                    // 1. Camera Source Card
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Camera source"
                        subtitle: "DirectShow"
                        accentColor: Theme.accentAmber

                        AppComboBox {
                            id: deviceCombo
                            Layout.fillWidth: true
                            model: camera.devices
                            currentIndex: camera.selectedDeviceIndex
                            onActivated: function(idx) { camera.selectedDeviceIndex = idx }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppButton {
                                Layout.fillWidth: true
                                iconName: camera.isStreaming ? "stop" : "play_arrow"
                                text: camera.isStreaming ? "Stop camera" : "Start camera"
                                variant: camera.isStreaming ? "danger" : "primary"
                                onClicked: {
                                    if (camera.isStreaming) camera.stopCamera()
                                    else camera.startCamera(deviceCombo.currentIndex)
                                }
                            }

                            Rectangle {
                                width: 40
                                height: 40
                                radius: 6
                                color: refMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.1) : (refMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                                border.color: Theme.btnSecondaryBorder
                                border.width: 1

                                AppIcon { anchors.centerIn: parent; name: "refresh"; size: 16; iconColor: Theme.textPrimary }

                                MouseArea {
                                    id: refMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: camera.refreshDevices()
                                }
                            }
                        }

                        CheckBox {
                            id: reticleCheck
                            text: "Show crosshair reticle"
                            checked: camera.showReticle
                            onToggled: camera.showReticle = checked
                            contentItem: Text {
                                text: reticleCheck.text
                                font.family: "Inter"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                                leftPadding: reticleCheck.indicator.width + 8
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    // 2. Optical Inspection Card
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Optical inspection"
                        subtitle: "CAD offset simulation"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Text {
                                text: "Loaded: " + job.fileName
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }

                            AppButton {
                                Layout.fillWidth: true
                                iconName: "search"
                                text: "Run toolpath inspection"
                                variant: "outline"
                                enabled: job.fileName !== "No file loaded" && job.state !== "Running"
                                onClicked: {
                                    if (!camera.isStreaming) camera.startCamera()
                                    job.startInspection()
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                visible: job.state === "Running" || job.state === "Paused"

                                AppButton {
                                    Layout.fillWidth: true
                                    iconName: job.state === "Paused" ? "play_arrow" : "pause"
                                    text: job.state === "Paused" ? "Resume" : "Pause"
                                    variant: "warning"
                                    onClicked: {
                                        if (job.state === "Running") job.pauseJob()
                                        else job.resumeJob()
                                    }
                                }

                                AppButton {
                                    Layout.fillWidth: true
                                    iconName: "stop_circle"
                                    text: "Abort"
                                    variant: "danger"
                                    onClicked: job.abortJob()
                                }
                            }
                        }
                    }

                    // 3. Camera Stage Jog Card
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Camera stage jog"
                        subtitle: "Fine optical positioning"
                        accentColor: Theme.accentAmber

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "CAMERA STEP"
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: motion.travelDistance + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.accentAmber
                            }
                        }

                        // Step Chips
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: 8
                            Repeater {
                                model: [10.0, 5.0, 1.0, 0.1]
                                delegate: Rectangle {
                                    width: 58
                                    height: 28
                                    radius: 6
                                    color: motion.travelDistance === modelData ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                    border.color: motion.travelDistance === modelData ? (Theme.isDark ? "#354B94" : "#192D78") : Theme.borderInput
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData + " mm"
                                        font.family: "Inter"
                                        font.pixelSize: 10
                                        font.weight: Font.Bold
                                        color: motion.travelDistance === modelData ? "#FFFFFF" : Theme.textPrimary
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: motion.setTravel(modelData)
                                    }
                                }
                            }
                        }

                        // XY Jog Pad
                        JogPad {
                            Layout.alignment: Qt.AlignHCenter
                            onJogClicked: function(dir) { motion.jog(dir) }
                            onCenterClicked: motion.centerXY()
                        }

                        // Z Focus Adjustment Buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            AppButton {
                                Layout.fillWidth: true
                                text: "▲  Z+ · Focus up"
                                variant: "outline"
                                onClicked: motion.jog("zplus")
                            }

                            AppButton {
                                Layout.fillWidth: true
                                text: "▼  Z− · Focus down"
                                variant: "outline"
                                onClicked: motion.jog("zminus")
                            }
                        }
                    }
                }
            }
        }
    }
}
