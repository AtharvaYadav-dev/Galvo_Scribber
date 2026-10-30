import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        // Top COM connection bar
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
                spacing: 12

                Text {
                    text: "Serial Port:"
                    color: "#ffffff"
                    font.pixelSize: 13
                }

                ComboBox {
                    id: portCombo
                    Layout.preferredWidth: 160
                    model: (typeof serial !== "undefined" && serial.ports.length > 0) ? serial.ports : ["No Ports Found"]
                }

                ModernButton {
                    text: "🔄 Refresh"
                    implicitWidth: 90
                    onClicked: if (typeof serial !== "undefined") serial.refreshPorts()
                }

                Rectangle { width: 1; height: 28; color: "#283042" }

                Text {
                    text: "Baud Rate:"
                    color: "#ffffff"
                    font.pixelSize: 13
                }

                ComboBox {
                    id: baudCombo
                    Layout.preferredWidth: 110
                    model: ["115200", "9600", "57600", "250000"]
                }

                ModernButton {
                    text: (typeof serial !== "undefined" && serial.isConnected) ? "Disconnect" : "Connect"
                    primary: !(typeof serial !== "undefined" && serial.isConnected)
                    danger: (typeof serial !== "undefined" && serial.isConnected)
                    implicitWidth: 110
                    onClicked: {
                        if (typeof serial !== "undefined") {
                            if (serial.isConnected) serial.disconnectPort()
                            else serial.connectPort(portCombo.currentText, baudCombo.currentText)
                        }
                    }
                }

                Item { Layout.fillWidth: true }
            }
        }

        // Terminal Log Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#0f121a"
            radius: 8
            border.color: "#283042"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: "DEVICE TERMINAL & G-CODE LOGS"
                        color: "#8e9cb0"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                    }
                    Item { Layout.fillWidth: true }
                    ModernButton {
                        text: "Clear Log"
                        implicitWidth: 80
                        implicitHeight: 28
                        onClicked: logArea.text = ""
                    }
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        id: logArea
                        readOnly: true
                        text: "[SYSTEM] Galvo Studio QML Engine Initialized\n[SYSTEM] Hardware DLL bridge ready: gt5motion_GT.dll\n[SYSTEM] Ready for marking operations.\n"
                        color: "#00d2ff"
                        font.family: "Consolas, 'Courier New', monospace"
                        font.pixelSize: 12
                        background: Rectangle { color: "transparent" }
                    }
                }

                // G-Code Input Send Bar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    TextField {
                        id: cmdInput
                        Layout.fillWidth: true
                        placeholderText: "Type G-code or manual command (e.g. G0 X10 Y10)..."
                        color: "#ffffff"
                        background: Rectangle {
                            color: "#161a24"
                            radius: 6
                            border.color: "#283042"
                        }
                        onAccepted: sendBtn.clicked()
                    }

                    ModernButton {
                        id: sendBtn
                        text: "Send"
                        primary: true
                        implicitWidth: 90
                        onClicked: {
                            if (cmdInput.text.trim().length > 0) {
                                logArea.append("[OUT] " + cmdInput.text)
                                cmdInput.text = ""
                            }
                        }
                    }
                }
            }
        }
    }
}
