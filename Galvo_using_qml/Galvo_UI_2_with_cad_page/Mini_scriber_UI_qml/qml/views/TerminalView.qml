import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: root

    MetricCard {
        anchors.fill: parent
        anchors.margins: 28
        title: "G-Code Serial Console"
        subtitle: settings.machineName.toUpperCase() + "  /  TERMINAL"
        accentColor: Theme.accentAmber
        visible: settings.currentRole === "Supervisor" || settings.currentRole === "Admin"

        ListModel {
            id: logModel
        }

        Connections {
            target: terminal
            function onLogAdded(timestamp, text, logType) {
                logModel.append({
                    "time": timestamp,
                    "msg": text,
                    "type": logType
                })
                if (logModel.count > 500) {
                    logModel.remove(0)
                }
                logListView.positionViewAtEnd()
            }
            function onCleared() {
                logModel.clear()
            }
        }

        // Quick Command Bar
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "QUICK MACROS:"
                font.family: "Inter"
                font.pixelSize: 10
                font.weight: Font.Bold
                color: Theme.textSecondary
            }

            Repeater {
                model: [
                    { label: "M114 (Pos)", cmd: "M114" },
                    { label: "G28 (Home)", cmd: "G28" },
                    { label: "G90 (Abs)", cmd: "G90" },
                    { label: "G91 (Rel)", cmd: "G91" },
                    { label: "Laser ON", cmd: "M106 P0 S255" },
                    { label: "Laser OFF", cmd: "M106 P0 S0" }
                ]
                delegate: Rectangle {
                    width: cmdText.implicitWidth + 16
                    height: 28
                    radius: 6
                    color: macroMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg
                    border.color: Theme.borderInput
                    border.width: 1

                    Text {
                        id: cmdText
                        anchors.centerIn: parent
                        text: modelData.label
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }

                    MouseArea {
                        id: macroMa
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: terminal.sendCommand(modelData.cmd)
                    }
                }
            }

            Item { Layout.fillWidth: true }

            AppButton {
                implicitHeight: 28
                text: "Clear log"
                variant: "outline"
                onClicked: terminal.clearLog()
            }
        }

        // Terminal Log Output
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 8
            color: "#080D18"
            border.color: Theme.borderCard
            border.width: 1
            clip: true

            ListView {
                id: logListView
                anchors.fill: parent
                anchors.margins: 12
                model: logModel
                delegate: RowLayout {
                    width: logListView.width - 24
                    spacing: 12

                    Text {
                        text: model.time
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 11
                        color: "#64748B"
                    }

                    Text {
                        Layout.fillWidth: true
                        text: model.msg
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 11
                        color: {
                            if (model.type === "tx") return "#00E5FF"
                            if (model.type === "err") return "#EF4444"
                            if (model.type === "info") return "#D6AF3E"
                            return "#A6B1C4"
                        }
                        wrapMode: Text.WrapAnywhere
                    }
                }
            }
        }

        // Command Input Field
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            TextField {
                id: cmdInput
                Layout.fillWidth: true
                placeholderText: "Type G-code command (e.g. G1 X10 F1000)..."
                font.family: "IBM Plex Mono"
                font.pixelSize: 12
                color: Theme.textPrimary
                background: Rectangle {
                    color: Theme.bgInput
                    radius: 6
                    border.color: cmdInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                    border.width: 1
                }
                onAccepted: {
                    if (text.length > 0) {
                        terminal.sendCommand(text)
                        text = ""
                    }
                }
            }

            AppButton {
                text: "Send"
                variant: "primary"
                onClicked: {
                    if (cmdInput.text.length > 0) {
                        terminal.sendCommand(cmdInput.text)
                        cmdInput.text = ""
                    }
                }
            }
        }
    }

    // Access Restricted Card for Non-Supervisor Users
    Rectangle {
        anchors.fill: parent
        anchors.margins: 28
        radius: 10
        color: Theme.bgCard
        border.color: Theme.borderCard
        visible: settings.currentRole !== "Supervisor" && settings.currentRole !== "Admin"

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 16

            AppIcon { Layout.alignment: Qt.AlignHCenter; name: "lock"; size: 48; iconColor: Theme.accentAmber }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "SUPERVISOR OR ADMIN ACCESS REQUIRED"
                font.family: "Inter"
                font.pixelSize: 17
                font.weight: Font.Bold
                color: Theme.accentAmber
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Direct G-code serial terminal is restricted to Supervisor and Admin profiles."
                font.family: "Inter"
                font.pixelSize: 13
                color: Theme.textSecondary
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Active Profile: " + settings.currentRole.toUpperCase()
                font.family: "IBM Plex Mono"
                font.pixelSize: 12
                font.weight: Font.Bold
                color: Theme.textPrimary
            }
        }
    }
}
