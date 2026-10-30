import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    visible: opacity > 0.0
    opacity: 0.0

    // Safe defensive property bindings preventing null-teardown TypeErrors during exit
    readonly property bool isDownloading: (typeof updater !== "undefined" && updater) ? updater.isDownloading : false
    readonly property bool updateAvailable: (typeof updater !== "undefined" && updater) ? updater.updateAvailable : false
    readonly property real downloadProgress: (typeof updater !== "undefined" && updater) ? updater.downloadProgress : 0.0
    readonly property real downloadedMb: (typeof updater !== "undefined" && updater) ? updater.downloadedMb : 0.0
    readonly property real totalMb: (typeof updater !== "undefined" && updater) ? updater.totalMb : 0.0
    readonly property string currentVersion: (typeof updater !== "undefined" && updater) ? updater.currentVersion : "1.0.0"
    readonly property string latestVersion: (typeof updater !== "undefined" && updater) ? updater.latestVersion : "1.0.0"
    readonly property string releaseNotes: (typeof updater !== "undefined" && updater) ? updater.releaseNotes : ""
    property bool isRestarting: false

    // Smooth fade in / out
    Behavior on opacity {
        NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
    }

    function open() {
        root.opacity = 1.0
    }

    function close() {
        root.opacity = 0.0
    }

    // Modal Darkening Backdrop (Clicking outside closes modal while download continues in background)
    Rectangle {
        anchors.fill: parent
        color: Theme.isDark ? Qt.rgba(3/255, 7/255, 18/255, 0.75) : Qt.rgba(15/255, 23/255, 42/255, 0.50)

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
            onClicked: root.close()
            onWheel: function(wheel) {
                // Completely eat all wheel scroll events so backside UI never scrolls
                wheel.accepted = true
            }
        }
    }

    // Dialog Card Container
    Rectangle {
        id: dialogCard
        width: Math.min(500, parent.width - 32)
        implicitHeight: cardCol.implicitHeight + 36
        anchors.centerIn: parent
        radius: 14
        color: Theme.isDark ? "#0A101E" : "#FFFFFF"
        border.color: Theme.isDark ? "#1E2E48" : "#CBD5E1"
        border.width: 1.5
        clip: true

        scale: root.opacity > 0.0 ? 1.0 : 0.88
        Behavior on scale {
            NumberAnimation { duration: 240; easing.type: Easing.OutBack }
        }

        // Absorb clicks and wheel scrolling on the dialog card itself
        MouseArea {
            anchors.fill: parent
            z: -1
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
            onClicked: {}
            onWheel: function(wheel) {
                wheel.accepted = true
            }
        }

        // Accent top border glow
        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            color: root.downloadProgress >= 100.0 ? Theme.accentGreen : Theme.accentCyan
        }

        ColumnLayout {
            id: cardCol
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Rectangle {
                    width: 36
                    height: 36
                    radius: 18
                    color: Theme.isDark ? "#142036" : "#EFF6FF"
                    border.color: Theme.isDark ? "#1E3050" : "#DBEAFE"
                    border.width: 1

                    AppIcon {
                        anchors.centerIn: parent
                        name: root.downloadProgress >= 100.0 ? "check_circle" : (root.isDownloading ? "download" : "system_update")
                        size: 20
                        iconColor: root.downloadProgress >= 100.0 ? Theme.accentGreen : Theme.accentCyan
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: root.downloadProgress >= 100.0
                            ? "Update Ready to Install"
                            : (root.isDownloading ? "Downloading Update..." : "Software Update Available")
                        font.family: "Inter"
                        font.pixelSize: 15
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }

                    Text {
                        text: (typeof settings !== "undefined" && settings ? settings.machineName : "Mini Scriber") + " Diode Laser CNC System"
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: Theme.textSecondary
                    }
                }

                // Close Button
                Rectangle {
                    width: 28
                    height: 28
                    radius: 14
                    color: closeMa.containsMouse ? (Theme.isDark ? "#243650" : "#E2E8F0") : "transparent"

                    AppIcon {
                        anchors.centerIn: parent
                        name: "close"
                        size: 14
                        iconColor: Theme.textSecondary
                    }

                    MouseArea {
                        id: closeMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }
            }

            // Version Comparison Leap Pill
            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 8
                color: Theme.isDark ? "#060A14" : "#F8FAFC"
                border.color: Theme.isDark ? "#1E2A3E" : "#E2E8F0"
                border.width: 1

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 16

                    // Current Version
                    RowLayout {
                        spacing: 6
                        Text {
                            text: "Current:"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                        Text {
                            text: "v" + root.currentVersion
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                    }

                    AppIcon {
                        name: "arrow_forward"
                        size: 14
                        iconColor: Theme.accentCyan
                    }

                    // Target Version
                    RowLayout {
                        spacing: 6
                        Text {
                            text: "Target:"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                        Text {
                            text: "v" + root.latestVersion
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.accentCyan
                        }
                        Rectangle {
                            height: 16
                            radius: 8
                            color: Theme.accentCyan
                            implicitWidth: newBadgeText.implicitWidth + 8

                            Text {
                                id: newBadgeText
                                anchors.centerIn: parent
                                text: "NEW"
                                font.family: "Inter"
                                font.pixelSize: 8
                                font.weight: Font.Bold
                                color: "#0B1220"
                            }
                        }
                    }
                }
            }

            // STATE 1: DOWNLOADING
            ColumnLayout {
                Layout.fillWidth: true
                visible: root.isDownloading
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: "Downloading update package..."
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        Layout.fillWidth: true
                    }
                    Text {
                        text: root.downloadProgress.toFixed(1) + "%"
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: Theme.accentCyan
                    }
                }

                // Progress Bar Background
                Rectangle {
                    Layout.fillWidth: true
                    height: 8
                    radius: 4
                    color: Theme.isDark ? "#1E2A3E" : "#E2E8F0"
                    clip: true

                    // Filled Bar
                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: parent.width * (root.downloadProgress / 100.0)
                        radius: 4
                        color: Theme.accentCyan

                        Behavior on width {
                            NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: (root.totalMb > 0
                            ? root.downloadedMb.toFixed(1) + " MB of " + root.totalMb.toFixed(1) + " MB downloaded"
                            : "Streaming update package...")
                            + ((typeof updater !== "undefined" && updater && updater.speedText) ? " · " + updater.speedText : "")
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: Theme.textSecondary
                        Layout.fillWidth: true
                    }
                    Text {
                        visible: (typeof updater !== "undefined" && updater && updater.etaText !== "")
                        text: (typeof updater !== "undefined" && updater) ? updater.etaText : ""
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 10
                        font.weight: Font.DemiBold
                        color: Theme.accentCyan
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 4
                    spacing: 10

                    Rectangle {
                        height: 32
                        radius: 6
                        color: bgMa.containsMouse ? (Theme.isDark ? "#1E2A3E" : "#E2E8F0") : "transparent"
                        border.color: Theme.accentCyan
                        border.width: 1
                        implicitWidth: bgText.implicitWidth + 24

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 6
                            Text { text: "⬇️"; font.pixelSize: 11 }
                            Text {
                                id: bgText
                                text: "Run in Background"
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: Theme.accentCyan
                            }
                        }

                        MouseArea {
                            id: bgMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.close()
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Rectangle {
                        height: 32
                        radius: 6
                        color: cancelMa.containsMouse ? (Theme.isDark ? "#243650" : "#E2E8F0") : "transparent"
                        border.color: Theme.isDark ? "#2A3C55" : "#CBD5E1"
                        border.width: 1
                        implicitWidth: cancelText.implicitWidth + 24

                        Text {
                            id: cancelText
                            anchors.centerIn: parent
                            text: "Cancel Download"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.isDark ? "#F87171" : "#DC2626"
                        }

                        MouseArea {
                            id: cancelMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (typeof updater !== "undefined" && updater) updater.cancelDownload()
                            }
                        }
                    }
                }
            }

            // STATE 2: READY TO INSTALL
            ColumnLayout {
                Layout.fillWidth: true
                visible: !root.isDownloading && root.downloadProgress >= 100.0
                spacing: 12

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: readyNoticeCol.implicitHeight + 16
                    radius: 8
                    color: Theme.isDark ? "#0A2018" : "#ECFDF5"
                    border.color: Theme.accentGreen
                    border.width: 1

                    ColumnLayout {
                        id: readyNoticeCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 4

                        RowLayout {
                            spacing: 6
                            AppIcon {
                                name: "check_circle"
                                size: 16
                                iconColor: Theme.accentGreen
                            }
                            Text {
                                text: "Package Downloaded & Integrity Verified"
                                font.family: "Inter"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: Theme.accentGreen
                            }
                        }
                        Text {
                            text: "Clicking below will automatically shut down laser channels, park axes, launch the installer, and restart into version v" + root.latestVersion + "."
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.isDark ? "#A7F3D0" : "#065F46"
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 6
                        color: root.isRestarting ? (Theme.isDark ? "#1E293B" : "#E2E8F0") : Theme.accentGreen
                        opacity: root.isRestarting ? 0.7 : 1.0

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 8
                            Text {
                                text: root.isRestarting ? "Shutting down & Launching Installer..." : "Restart & Install Now"
                                font.family: "Inter"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: root.isRestarting ? Theme.textSecondary : "#0B1220"
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: root.isRestarting ? Qt.ArrowCursor : Qt.PointingHandCursor
                            enabled: !root.isRestarting
                            onClicked: {
                                if (root.isRestarting) return
                                root.isRestarting = true
                                if (typeof updater !== "undefined" && updater) {
                                    updater.installAndRestart()
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 110
                        height: 40
                        radius: 6
                        color: "transparent"
                        border.color: Theme.isDark ? "#2A3C55" : "#CBD5E1"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "Later"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.close()
                        }
                    }
                }
            }

            // STATE 3: REVIEW RELEASE NOTES & CONFIRM DOWNLOAD
            ColumnLayout {
                Layout.fillWidth: true
                visible: !root.isDownloading && root.downloadProgress < 100.0
                spacing: 10

                Text {
                    text: "What's New in this Release:"
                    font.family: "Inter"
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                    color: Theme.textSecondary
                }

                // Release Notes Scrollable Box
                Rectangle {
                    Layout.fillWidth: true
                    height: 130
                    radius: 8
                    color: Theme.isDark ? "#060A14" : "#F8FAFC"
                    border.color: Theme.isDark ? "#1E2A3E" : "#E2E8F0"
                    border.width: 1
                    clip: true

                    Flickable {
                        anchors.fill: parent
                        anchors.margins: 10
                        contentWidth: width
                        contentHeight: notesText.implicitHeight
                        clip: true

                        Text {
                            id: notesText
                            width: parent.width
                            text: root.releaseNotes && root.releaseNotes.length > 0
                                ? root.releaseNotes
                                : "• Bug fixes, laser calibration enhancements, and performance stability updates.\n• Hardware bed coordinate orientation accuracy improvements.\n• Compatible with Mini Scriber v1.x controller firmware."
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textPrimary
                            wrapMode: Text.WordWrap
                            lineHeight: 1.3
                        }
                    }
                }

                // Action Buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Layout.topMargin: 4

                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 6
                        color: installMa.containsMouse ? Qt.lighter(Theme.accentCyan, 1.1) : Theme.accentCyan

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 6
                            AppIcon {
                                name: "download"
                                size: 16
                                iconColor: "#0B1220"
                            }
                            Text {
                                text: "Download & Install Now"
                                font.family: "Inter"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "#0B1220"
                            }
                        }

                        MouseArea {
                            id: installMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (typeof updater !== "undefined" && updater) updater.startDownload()
                            }
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 120
                        height: 40
                        radius: 6
                        color: laterMa.containsMouse ? (Theme.isDark ? "#1E2A3E" : "#E2E8F0") : "transparent"
                        border.color: Theme.isDark ? "#2A3C55" : "#CBD5E1"
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "Remind Me Later"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }

                        MouseArea {
                            id: laterMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.close()
                        }
                    }
                }
            }
        }
    }
}
