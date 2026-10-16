import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "views"

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 820
    minimumWidth: 1024
    minimumHeight: 700
    title: "Galvo Studio - Industrial Laser Controller (PySide6 QML)"
    color: "#0c0e14"

    property int currentNavIndex: 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ================= TOP HEADER BAR ================= //
        Rectangle {
            Layout.fillWidth: true
            height: 64
            color: "#131620"
            border.color: "#212738"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                // Logo & Name
                Row {
                    spacing: 10
                    Layout.alignment: Qt.AlignVCenter

                    Rectangle {
                        width: 32; height: 32; radius: 6
                        color: "#00d2ff"
                        Text {
                            anchors.centerIn: parent
                            text: "⚡"
                            font.pixelSize: 18
                        }
                    }

                    Column {
                        Text {
                            text: "GALVO STUDIO"
                            color: "#ffffff"
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            font.family: "Segoe UI, Roboto, Arial"
                        }
                        Text {
                            text: "Industrial Laser Scribing & Patterning"
                            color: "#00d2ff"
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }
                }

                // Status Badge
                Rectangle {
                    height: 28
                    implicitWidth: statusRow.width + 20
                    radius: 14
                    color: (typeof galvo !== "undefined" && galvo.isConnected)
                           ? (galvo.isDemo ? "#33f5a623" : "#332ed573")
                           : "#263042"
                    border.color: (typeof galvo !== "undefined" && galvo.isConnected)
                                  ? (galvo.isDemo ? "#f5a623" : "#2ed573")
                                  : "#3f4d66"
                    border.width: 1

                    Row {
                        id: statusRow
                        anchors.centerIn: parent
                        spacing: 6

                        Rectangle {
                            width: 8; height: 8; radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: (typeof galvo !== "undefined" && galvo.isConnected)
                                   ? (galvo.isDemo ? "#f5a623" : "#2ed573")
                                   : "#7e8b9e"
                        }

                        Text {
                            text: (typeof galvo !== "undefined" && galvo.isConnected)
                                  ? (galvo.isDemo ? "SIMULATION MODE" : "HARDWARE ONLINE")
                                  : "OFFLINE"
                            color: "#ffffff"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // Connect / Disconnect Button
                ModernButton {
                    text: (typeof galvo !== "undefined" && galvo.isConnected) ? "Disconnect" : "Connect Hardware"
                    primary: !(typeof galvo !== "undefined" && galvo.isConnected)
                    implicitWidth: 140
                    implicitHeight: 38
                    onClicked: {
                        if (typeof galvo !== "undefined") {
                            if (galvo.isConnected) galvo.disconnectHardware()
                            else galvo.connectHardware()
                        }
                    }
                }

                // Red Pointer Toggle
                ModernButton {
                    text: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "🔴 Red Pointer ON" : "⚪ Red Pointer OFF"
                    implicitWidth: 140
                    implicitHeight: 38
                    btnColor: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#7a2a10" : "#202534"
                    borderColor: (typeof galvo !== "undefined" && galvo.redPointerOn) ? "#e67e22" : "#323b50"
                    onClicked: if (typeof galvo !== "undefined") galvo.toggleRedPointer()
                }

                // EMERGENCY STOP BUTTON
                ModernButton {
                    text: "🛑 E-STOP"
                    danger: true
                    implicitWidth: 110
                    implicitHeight: 38
                    onClicked: if (typeof galvo !== "undefined") galvo.emergencyStop()
                }
            }
        }

        // ================= MAIN CONTENT ROW ================= //
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // LEFT NAVIGATION RAIL
            Rectangle {
                Layout.preferredWidth: 220
                Layout.fillHeight: true
                color: "#11141c"
                border.color: "#1e2433"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.topMargin: 16
                    anchors.bottomMargin: 16
                    spacing: 6

                    // Navigation items
                    readonly property var navItems: [
                        { label: "🎯  Z-Axis & Focus", index: 0 },
                        { label: "⚡  Laser Config", index: 1 },
                        { label: "📐  2D CAD Canvas", index: 2 },
                        { label: "📹  Camera Vision", index: 3 },
                        { label: "💻  Terminal / COM", index: 4 }
                    ]

                    Repeater {
                        model: parent.navItems

                        Rectangle {
                            id: navBtn
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.preferredHeight: 46
                            radius: 6
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10

                            readonly property bool isSelected: window.currentNavIndex === modelData.index

                            color: isSelected ? "#1d2538" : (navMouse.containsMouse ? "#181d2a" : "transparent")
                            border.color: isSelected ? "#00d2ff" : "transparent"
                            border.width: 1

                            // Left cyan indicator line
                            Rectangle {
                                width: 3
                                height: 24
                                radius: 1.5
                                anchors.left: parent.left
                                anchors.verticalCenter: parent.verticalCenter
                                color: "#00d2ff"
                                visible: navBtn.isSelected
                            }

                            Text {
                                anchors.left: parent.left
                                anchors.leftMargin: 18
                                anchors.verticalCenter: parent.verticalCenter
                                text: navBtn.modelData.label
                                color: navBtn.isSelected ? "#ffffff" : (navMouse.containsMouse ? "#d5deeb" : "#8796ab")
                                font.pixelSize: 13
                                font.weight: navBtn.isSelected ? Font.Bold : Font.Medium
                            }

                            MouseArea {
                                id: navMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: window.currentNavIndex = navBtn.modelData.index
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // Architecture Badge
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 68
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        radius: 6
                        color: "#161b26"
                        border.color: "#283247"
                        border.width: 1

                        Column {
                            anchors.centerIn: parent
                            spacing: 4
                            Text {
                                text: "100% Python Architecture"
                                color: "#2ed573"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            Text {
                                text: "PySide6 QML + QtQuick (GPU)"
                                color: "#6c7a91"
                                font.pixelSize: 10
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                }
            }

            // CENTER VIEW AREA (STACK OF PAGES)
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#0c0e14"

                Item {
                    anchors.fill: parent
                    anchors.margins: 20

                    StackLayout {
                        anchors.fill: parent
                        currentIndex: window.currentNavIndex

                        JogView {}
                        LaserView {}
                        CadPlaceholderView {}
                        CameraView {}
                        TerminalView {}
                    }
                }
            }
        }

        // ================= BOTTOM STATUS FOOTER ================= //
        Rectangle {
            Layout.fillWidth: true
            height: 32
            color: "#0f121a"
            border.color: "#1e2433"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 14

                Text {
                    text: "STATUS:"
                    color: "#5f6c82"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                }

                Text {
                    text: typeof galvo !== "undefined" ? galvo.statusMessage : "System ready"
                    color: "#00d2ff"
                    font.pixelSize: 11
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "Z HEIGHT (FOCUS): " + (typeof jog !== "undefined" ? jog.zPos.toFixed(3) : "27.000") +
                          " mm  |  TARGET: " + (typeof jog !== "undefined" ? jog.targetFocusZ.toFixed(3) : "27.000") +
                          " mm  |  GALVO: OPTICAL SCAN (CENTERED)"
                    color: "#8e9cb0"
                    font.family: "Consolas, monospace"
                    font.pixelSize: 11
                }
            }
        }
    }
}
