import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import GalvoVision 1.0
import "../components"

Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        // Top Control Bar
        Rectangle {
            Layout.fillWidth: true
            height: 64
            color: "#161a24"
            radius: 8
            border.color: "#283042"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 14

                Text {
                    text: "📹 Camera Device:"
                    color: "#ffffff"
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }

                ComboBox {
                    id: cameraCombo
                    Layout.preferredWidth: 220
                    model: (typeof camera !== "undefined" && camera.devices.length > 0) ? camera.devices : ["Default Camera (0)"]
                }

                ModernButton {
                    text: "🔄 Refresh"
                    implicitWidth: 90
                    onClicked: if (typeof camera !== "undefined") camera.refreshDevices()
                }

                Rectangle { width: 1; height: 28; color: "#283042" }

                ModernButton {
                    text: (typeof camera !== "undefined" && camera.isRunning) ? "⏹ Stop Camera" : "▶ Start Camera Feed"
                    primary: !(typeof camera !== "undefined" && camera.isRunning)
                    danger: (typeof camera !== "undefined" && camera.isRunning)
                    implicitWidth: 150
                    onClicked: {
                        if (typeof camera !== "undefined") {
                            if (camera.isRunning) camera.stopCamera()
                            else camera.startCamera(cameraCombo.currentIndex)
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: (typeof camera !== "undefined" && camera.isRunning) ? "🟢 Live 25 FPS DirectShow" : "⚪ Standby"
                    color: (typeof camera !== "undefined" && camera.isRunning) ? "#2ed573" : "#7e8b9e"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                }
            }
        }

        // Center Video Viewport Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#0c0e14"
            radius: 8
            border.color: "#283042"
            border.width: 1
            clip: true

            CameraVideoItem {
                id: videoSurface
                anchors.fill: parent

                Component.onCompleted: {
                    if (typeof camera !== "undefined") {
                        camera.registerVideoItem(this)
                    }
                }
            }

            // Crosshair Overlay (Optical Center Alignment)
            Item {
                anchors.fill: parent
                visible: typeof camera !== "undefined" && camera.isRunning

                // Center crosshair lines
                Rectangle {
                    width: parent.width
                    height: 1
                    color: "#66ff4757"
                    anchors.verticalCenter: parent.verticalCenter
                }
                Rectangle {
                    width: 1
                    height: parent.height
                    color: "#66ff4757"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                // Center targeting reticle ring
                Rectangle {
                    width: 60
                    height: 60
                    radius: 30
                    color: "transparent"
                    border.color: "#ff4757"
                    border.width: 1.5
                    anchors.centerIn: parent
                }

                Rectangle {
                    width: 120
                    height: 120
                    radius: 60
                    color: "transparent"
                    border.color: "#33ff4757"
                    border.width: 1
                    anchors.centerIn: parent
                }
            }

            // Bottom-Left Alignment Tip
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.margins: 14
                height: 28
                implicitWidth: tipText.width + 20
                radius: 4
                color: "#cc161a24"
                border.color: "#353e54"
                border.width: 1

                Text {
                    id: tipText
                    anchors.centerIn: parent
                    text: "Align workpiece features to center reticle for optical galvo calibration"
                    color: "#00d2ff"
                    font.pixelSize: 11
                }
            }
        }
    }
}
