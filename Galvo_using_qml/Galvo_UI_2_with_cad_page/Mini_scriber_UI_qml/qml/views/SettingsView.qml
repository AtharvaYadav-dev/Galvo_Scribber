import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

ScrollView {
    id: root
    objectName: "settingsScrollView"
    clip: true
    ScrollBar.horizontal.policy: ScrollBar.AsNeeded
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    // Safe defensive updater properties to prevent null-teardown TypeErrors on app exit
    readonly property bool updaterChecking: (typeof updater !== "undefined" && updater) ? updater.isChecking : false
    readonly property bool updaterAvailable: (typeof updater !== "undefined" && updater) ? updater.updateAvailable : false
    readonly property string updaterCurrentVer: (typeof updater !== "undefined" && updater) ? updater.currentVersion : "1.0.0"
    readonly property string updaterLatestVer: (typeof updater !== "undefined" && updater) ? updater.latestVersion : "1.0.0"
    readonly property string updaterCheckedTime: (typeof updater !== "undefined" && updater) ? updater.lastCheckedTime : ""
    readonly property bool updaterDownloading: (typeof updater !== "undefined" && updater) ? updater.isDownloading : false
    readonly property real updaterDownloadProgress: (typeof updater !== "undefined" && updater) ? updater.downloadProgress : 0.0

    // Role-based Section Visibility
    readonly property bool isSerialVisible: settings.isSettingsTabAllowed(settings.currentRole, "serial")
    readonly property bool isProfileVisible: settings.isSettingsTabAllowed(settings.currentRole, "profile")
    readonly property bool isFeedsVisible: settings.isSettingsTabAllowed(settings.currentRole, "feeds")
    readonly property bool isOriginVisible: settings.isSettingsTabAllowed(settings.currentRole, "origin")
    readonly property bool isCameraVisible: settings.isSettingsTabAllowed(settings.currentRole, "camera_offset")
    readonly property bool isSystemVisible: settings.isSettingsTabAllowed(settings.currentRole, "system")

    readonly property bool hasLeftCards: isSerialVisible || isProfileVisible || isFeedsVisible
    readonly property bool hasRightCards: isOriginVisible || isCameraVisible || isSystemVisible

    Item {
        width: root.availableWidth
        implicitHeight: mainCol.implicitHeight + 48

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: root.availableWidth < 768 ? 16 : 28
            spacing: 24

            // Page Heading
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    spacing: 4
                    Text {
                        text: "Settings"
                        font.family: "Inter"
                        font.pixelSize: 26
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }
                    Text {
                        text: "Controller connection, access control and precision machine configuration."
                        font.family: "Inter"
                        font.pixelSize: 12
                        color: Theme.textSecondary
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: settings.machineName.toUpperCase() + "  /  CONFIGURATION"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: Theme.textMuted
                    Layout.alignment: Qt.AlignTop
                }
            }

            // Global Notification Toast
            Rectangle {
                id: saveToast
                Layout.fillWidth: true
                height: toastText.length > 0 ? 38 : 0
                visible: toastText.length > 0
                radius: 6
                color: Theme.pillOnlineBg
                border.color: Theme.pillOnlineBorder
                border.width: 1
                clip: true

                property string toastText: ""

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 14
                    spacing: 10

                    AppIcon { name: "save"; size: 16; iconColor: Theme.pillOnlineText }
                    Text {
                        Layout.fillWidth: true
                        text: saveToast.toastText
                        font.family: "Inter"
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                        color: Theme.pillOnlineText
                        elide: Text.ElideRight
                    }
                    MouseArea {
                        implicitWidth: 20
                        implicitHeight: 20
                        cursorShape: Qt.PointingHandCursor
                        AppIcon { anchors.centerIn: parent; name: "close"; size: 13; iconColor: Theme.textSecondary }
                        onClicked: saveToast.toastText = ""
                    }
                }

                Timer {
                    id: toastTimer
                    interval: 4000
                    repeat: false
                    onTriggered: saveToast.toastText = ""
                }

                Connections {
                    target: settings
                    function onSettingsSaved(msg) {
                        saveToast.toastText = msg
                        toastTimer.restart()
                    }
                }
            }

            // Main Responsive Grid
            Flow {
                id: gridFlow
                Layout.fillWidth: true
                spacing: 20

                // Left Column: Serial, User Profile, Motion Feeds
                ColumnLayout {
                    id: leftCol
                    visible: root.hasLeftCards
                    width: !root.hasRightCards ? gridFlow.width : (root.availableWidth >= 960 ? Math.min(520, Math.max(480, Math.floor(gridFlow.width * 0.45))) : gridFlow.width)
                    spacing: 20

                    // 1. Serial Hardware Configuration Card
                    MetricCard {
                        Layout.fillWidth: true
                        visible: root.isSerialVisible
                        title: "Serial hardware configuration"
                        subtitle: "Microcontroller port setup"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Layout.minimumWidth: 140
                                    spacing: 4
                                    Text { text: "COM port"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    AppComboBox {
                                        id: portCombo
                                        Layout.fillWidth: true
                                        model: serial.ports
                                        currentIndex: 0
                                        onActivated: function(idx) { serial.selectedPort = model[idx] }
                                    }
                                }

                                ColumnLayout {
                                    Layout.preferredWidth: 145
                                    Layout.minimumWidth: 135
                                    spacing: 4
                                    Text { text: "Baudrate"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    AppComboBox {
                                        id: baudCombo
                                        Layout.fillWidth: true
                                        model: serial.baudrates
                                        currentIndex: 2
                                        onActivated: function(idx) { serial.selectedBaud = model[idx] }
                                    }
                                }

                                ColumnLayout {
                                    spacing: 4
                                    Text { text: " "; font.pixelSize: 11 }
                                    Rectangle {
                                        width: 80
                                        height: 38
                                        radius: 6
                                        color: refPortMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.1) : (refPortMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                                        border.color: Theme.btnSecondaryBorder
                                        border.width: 1

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 4
                                            AppIcon { name: "refresh"; size: 14; iconColor: Theme.textPrimary }
                                            Text { text: "Refresh"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Theme.textPrimary }
                                        }

                                        MouseArea {
                                            id: refPortMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: serial.refreshPorts()
                                        }
                                    }
                                }
                            }

                            AppButton {
                                Layout.fillWidth: true
                                implicitHeight: 44
                                iconName: serial.connected ? "power" : "link"
                                text: serial.connected ? "Disconnect port" : "Connect to port"
                                variant: serial.connected ? "danger" : "primary"
                                iconColor: serial.connected ? "#FFFFFF" : (Theme.isDark ? "#00E5FF" : "#FFFFFF")
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                onClicked: {
                                    if (serial.connected) serial.disconnectSerial()
                                    else {
                                        serial.selectedPort = portCombo.currentText
                                        serial.selectedBaud = baudCombo.currentText
                                        serial.connectSerial()
                                    }
                                }
                            }
                        }
                    }

                    // 2. User Profile & Access Control Card
                    MetricCard {
                        id: profileCard
                        Layout.fillWidth: true
                        visible: root.isProfileVisible
                        title: "User profile & access control"
                        subtitle: "Role-based authentication"
                        accentColor: Theme.accentAmber

                        property string selectedRole: settings.currentRole
                        property string authFeedback: ""
                        property bool isAuthError: false

                        Connections {
                            target: settings
                            function onLoginSuccess(msg) {
                                profileCard.authFeedback = msg
                                profileCard.isAuthError = false
                            }
                            function onLoginFailed(msg) {
                                profileCard.authFeedback = msg
                                profileCard.isAuthError = true
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            // Active Profile Readout Pill
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "ACTIVE PROFILE"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.DemiBold; color: Theme.textSecondary }
                                Item { Layout.fillWidth: true }
                                Rectangle {
                                    height: 24
                                    radius: 12
                                    color: Theme.pillOnlineBg
                                    border.color: Theme.pillOnlineBorder
                                    border.width: 1
                                    implicitWidth: roleBadgeText.implicitWidth + 18

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentGreen }
                                        Text {
                                            id: roleBadgeText
                                            text: {
                                                if (settings.currentRole === "Supervisor" || settings.currentRole === "Admin") {
                                                    var m = Math.floor(settings.supervisorRemainingSeconds / 60)
                                                    var s = settings.supervisorRemainingSeconds % 60
                                                    var timeStr = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s)
                                                    return settings.currentRole.toUpperCase() + " (ACTIVE - " + timeStr + ")"
                                                }
                                                return settings.currentRole.toUpperCase() + " (ACTIVE)"
                                            }
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            font.weight: Font.Bold
                                            color: Theme.accentGreen
                                        }
                                    }
                                }
                            }

                            // Role Selection Chips
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Select role to authenticate"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                RowLayout {
                                    spacing: 8
                                    Repeater {
                                        model: ["Operator", "Supervisor", "Admin"]
                                        delegate: Rectangle {
                                            Layout.fillWidth: true
                                            height: 36
                                            radius: 6
                                            color: profileCard.selectedRole === modelData ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                            border.color: profileCard.selectedRole === modelData ? (Theme.isDark ? "#354B94" : "#192D78") : Theme.borderInput
                                            border.width: 1

                                            Text {
                                                anchors.centerIn: parent
                                                text: modelData
                                                font.family: "Inter"
                                                font.pixelSize: 12
                                                font.weight: Font.DemiBold
                                                color: profileCard.selectedRole === modelData ? "#FFFFFF" : Theme.textPrimary
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    profileCard.selectedRole = modelData
                                                    profileCard.authFeedback = ""
                                                    pwdInput.text = ""
                                                    pwdInput.forceActiveFocus()
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // Password Input Field
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Password"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 36
                                    radius: 6
                                    color: Theme.bgInput
                                    border.color: pwdInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                    border.width: 1

                                    property bool showPassword: false

                                    TextInput {
                                        id: pwdInput
                                        anchors.left: parent.left
                                        anchors.right: eyeToggleBtn.left
                                        anchors.top: parent.top
                                        anchors.bottom: parent.bottom
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        echoMode: parent.showPassword ? TextInput.Normal : TextInput.Password
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 14
                                        color: Theme.textPrimary
                                        onAccepted: {
                                            if (text.trim().length === 0) {
                                                profileCard.authFeedback = "Please enter password for " + profileCard.selectedRole
                                                profileCard.isAuthError = true
                                                return
                                            }
                                            settings.login(profileCard.selectedRole, text)
                                            text = ""
                                        }
                                    }

                                    Rectangle {
                                        id: eyeToggleBtn
                                        anchors.right: parent.right
                                        anchors.rightMargin: 6
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 26
                                        height: 26
                                        radius: 4
                                        color: eyeMouseArea.containsMouse ? (Theme.isDark ? "#2A2D3A" : "#E2E8F0") : "transparent"

                                        AppIcon {
                                            anchors.centerIn: parent
                                            name: parent.parent.showPassword ? "visibility_off" : "visibility"
                                            size: 16
                                            iconColor: eyeMouseArea.containsMouse ? Theme.accentCyan : Theme.textSecondary
                                        }

                                        MouseArea {
                                            id: eyeMouseArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: parent.parent.showPassword = !parent.parent.showPassword
                                        }
                                    }
                                }
                            }

                            // Feedback Banner
                            Rectangle {
                                Layout.fillWidth: true
                                height: profileCard.authFeedback.length > 0 ? 32 : 0
                                visible: profileCard.authFeedback.length > 0
                                radius: 6
                                color: profileCard.isAuthError ? Theme.pillOfflineBg : Theme.pillOnlineBg
                                border.color: profileCard.isAuthError ? Theme.pillOfflineBorder : Theme.pillOnlineBorder
                                border.width: 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 10
                                    spacing: 6
                                    AppIcon { name: profileCard.isAuthError ? "warning" : "check_circle"; size: 14; iconColor: profileCard.isAuthError ? Theme.pillOfflineText : Theme.pillOnlineText }
                                    Text {
                                        Layout.fillWidth: true
                                        text: profileCard.authFeedback
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: profileCard.isAuthError ? Theme.pillOfflineText : Theme.pillOnlineText
                                        elide: Text.ElideRight
                                    }
                                }
                            }

                            // Login / Switch Role & Logout Buttons
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                AppButton {
                                    Layout.fillWidth: true
                                    iconName: "vpn_key"
                                    text: "Login / switch role"
                                    variant: "primary"
                                    onClicked: {
                                        if (pwdInput.text.trim().length === 0) {
                                            profileCard.authFeedback = "Please enter password for " + profileCard.selectedRole
                                            profileCard.isAuthError = true
                                            return
                                        }
                                        settings.login(profileCard.selectedRole, pwdInput.text)
                                        pwdInput.text = ""
                                    }
                                }

                                AppButton {
                                    Layout.preferredWidth: 90
                                    text: "Logout"
                                    variant: "outline"
                                    onClicked: {
                                        settings.logout()
                                        profileCard.authFeedback = ""
                                    }
                                }
                            }

                            // Role Description Notes
                            Text {
                                text: "Operator: Safe production mode\nSupervisor: Privileged G-code Terminal access (10 min idle timeout)\nAdmin: Hardware setup, machine envelope & terminal access (Superuser)"
                                font.family: "Inter"
                                font.pixelSize: 10
                                color: Theme.textSecondary
                                lineHeight: 1.4
                            }
                        }
                    }

                    // 3. Motion & Feed Speeds Card
                    MetricCard {
                        Layout.fillWidth: true
                        visible: root.isFeedsVisible
                        title: "Motion & feed speeds"
                        subtitle: "Axis transit & laser feeds"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    Text { text: "Jog transit (mm/min)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 38
                                        radius: 6
                                        color: Theme.bgInput
                                        border.color: Theme.borderInput
                                        border.width: 1

                                        TextInput {
                                            id: jogFeedInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settings.jogFeed.toString()
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            color: Theme.textPrimary
                                        }
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    Text { text: "Laser scribing (mm/min)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 38
                                        radius: 6
                                        color: Theme.bgInput
                                        border.color: Theme.borderInput
                                        border.width: 1

                                        TextInput {
                                            id: laserFeedInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settings.laserFeed.toString()
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            color: Theme.textPrimary
                                        }
                                    }
                                }
                            }

                            AppButton {
                                Layout.fillWidth: true
                                iconName: "save"
                                text: "Save feed speeds"
                                variant: "primary"
                                onClicked: {
                                    var jf = parseInt(jogFeedInput.text)
                                    var lf = parseInt(laserFeedInput.text)
                                    if (!isNaN(jf) && !isNaN(lf)) settings.saveFeeds(jf, lf)
                                }
                            }
                        }
                    }
                }

                // Right Column: Print Origin, Camera Offsets, System Info
                ColumnLayout {
                    id: rightCol
                    visible: root.hasRightCards
                    width: !root.hasLeftCards ? gridFlow.width : (root.availableWidth >= 960 ? Math.max(340, gridFlow.width - leftCol.width - 20) : gridFlow.width)
                    spacing: 20

                    // 4. Print Starting Index Point (Print Origin)
                    MetricCard {
                        id: indexCard
                        Layout.fillWidth: true
                        visible: root.isOriginVisible
                        title: "Print starting index point (print origin)"
                        subtitle: "Defines bed coordinate where laser scribing begins"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            // Top Info Pill
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Rectangle {
                                    height: 24
                                    radius: 12
                                    color: Theme.pillOnlineBg
                                    border.color: Theme.pillOnlineBorder
                                    border.width: 1
                                    implicitWidth: activeOriginText.implicitWidth + 20

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Rectangle { width: 6; height: 6; radius: 3; color: Theme.accentGreen }
                                        Text {
                                            id: activeOriginText
                                            text: "ACTIVE ORIGIN: X = " + settings.xindex.toFixed(2) + " mm | Y = " + settings.yindex.toFixed(2) + " mm"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            font.weight: Font.Bold
                                            color: Theme.pillOnlineText
                                        }
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                Text {
                                    text: "Workbed: " + settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + " mm"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    color: Theme.textSecondary
                                }
                            }

                            Text {
                                text: "All imported DXF geometry, Gerber PCB layers and machine toolpaths start relative to this bed origin."
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }

                            // Main Inputs and Bed Schematic Row
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16

                                // Left Sub-Column: Inputs & Buttons
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    // Unified String Input
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4
                                        Text { text: "Index (X, Y) — main format · Press Enter or Save"; font.family: "Inter"; font.pixelSize: 10; color: Theme.textSecondary }
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 36
                                            radius: 6
                                            color: Theme.bgInput
                                            border.color: unifiedIndexInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                            border.width: 1

                                            TextInput {
                                                id: unifiedIndexInput
                                                anchors.fill: parent
                                                anchors.leftMargin: 10
                                                anchors.rightMargin: 10
                                                verticalAlignment: TextInput.AlignVCenter
                                                text: settings.xindex.toFixed(2) + ", " + settings.yindex.toFixed(2)
                                                font.family: "IBM Plex Mono"
                                                font.pixelSize: 13
                                                font.weight: Font.Bold
                                                color: Theme.textPrimary
                                                selectByMouse: true
                                                onAccepted: {
                                                    var ok = settings.saveIndexFromString(text)
                                                    if (ok) {
                                                        var parts = text.split(",")
                                                        xIndexInput.text = parseFloat(parts[0].trim()).toFixed(2)
                                                        yIndexInput.text = parseFloat(parts[1].trim()).toFixed(2)
                                                        miniBedCanvas.requestPaint()
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // Discrete X and Y Inputs
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 12

                                        // X Stepper
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 4
                                            Text { text: "X index (mm)"; font.family: "Inter"; font.pixelSize: 10; color: Theme.textSecondary }
                                            RowLayout {
                                                spacing: 4
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    height: 34
                                                    radius: 6
                                                    color: Theme.bgInput
                                                    border.color: Theme.borderInput
                                                    border.width: 1

                                                    TextInput {
                                                        id: xIndexInput
                                                        anchors.fill: parent
                                                        anchors.leftMargin: 8
                                                        anchors.rightMargin: 8
                                                        verticalAlignment: TextInput.AlignVCenter
                                                        text: settings.xindex.toFixed(2)
                                                        font.family: "IBM Plex Mono"
                                                        font.pixelSize: 12
                                                        color: Theme.textPrimary
                                                        onEditingFinished: {
                                                            var val = parseFloat(text)
                                                            if (!isNaN(val)) {
                                                                unifiedIndexInput.text = val.toFixed(2) + ", " + yIndexInput.text
                                                                miniBedCanvas.requestPaint()
                                                            }
                                                        }
                                                    }
                                                }

                                                Rectangle {
                                                    width: 26; height: 34; radius: 4; color: Theme.btnSecondaryBg; border.color: Theme.borderInput; border.width: 1
                                                    Text { anchors.centerIn: parent; text: "−"; font.bold: true; color: Theme.textPrimary }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            var val = Math.max(0, parseFloat(xIndexInput.text) - 1.0)
                                                            xIndexInput.text = val.toFixed(2)
                                                            unifiedIndexInput.text = xIndexInput.text + ", " + yIndexInput.text
                                                            miniBedCanvas.requestPaint()
                                                        }
                                                    }
                                                }
                                                Rectangle {
                                                    width: 26; height: 34; radius: 4; color: Theme.btnSecondaryBg; border.color: Theme.borderInput; border.width: 1
                                                    Text { anchors.centerIn: parent; text: "+"; font.bold: true; color: Theme.textPrimary }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            var val = Math.min(settings.bedWidth, parseFloat(xIndexInput.text) + 1.0)
                                                            xIndexInput.text = val.toFixed(2)
                                                            unifiedIndexInput.text = xIndexInput.text + ", " + yIndexInput.text
                                                            miniBedCanvas.requestPaint()
                                                        }
                                                    }
                                                }
                                            }
                                        }

                                        // Y Stepper
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 4
                                            Text { text: "Y index (mm)"; font.family: "Inter"; font.pixelSize: 10; color: Theme.textSecondary }
                                            RowLayout {
                                                spacing: 4
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    height: 34
                                                    radius: 6
                                                    color: Theme.bgInput
                                                    border.color: Theme.borderInput
                                                    border.width: 1

                                                    TextInput {
                                                        id: yIndexInput
                                                        anchors.fill: parent
                                                        anchors.leftMargin: 8
                                                        anchors.rightMargin: 8
                                                        verticalAlignment: TextInput.AlignVCenter
                                                        text: settings.yindex.toFixed(2)
                                                        font.family: "IBM Plex Mono"
                                                        font.pixelSize: 12
                                                        color: Theme.textPrimary
                                                        onEditingFinished: {
                                                            var val = parseFloat(text)
                                                            if (!isNaN(val)) {
                                                                unifiedIndexInput.text = xIndexInput.text + ", " + val.toFixed(2)
                                                                miniBedCanvas.requestPaint()
                                                            }
                                                        }
                                                    }
                                                }

                                                Rectangle {
                                                    width: 26; height: 34; radius: 4; color: Theme.btnSecondaryBg; border.color: Theme.borderInput; border.width: 1
                                                    Text { anchors.centerIn: parent; text: "−"; font.bold: true; color: Theme.textPrimary }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            var val = Math.max(0, parseFloat(yIndexInput.text) - 1.0)
                                                            yIndexInput.text = val.toFixed(2)
                                                            unifiedIndexInput.text = xIndexInput.text + ", " + yIndexInput.text
                                                            miniBedCanvas.requestPaint()
                                                        }
                                                    }
                                                }
                                                Rectangle {
                                                    width: 26; height: 34; radius: 4; color: Theme.btnSecondaryBg; border.color: Theme.borderInput; border.width: 1
                                                    Text { anchors.centerIn: parent; text: "+"; font.bold: true; color: Theme.textPrimary }
                                                    MouseArea {
                                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            var val = Math.min(settings.bedHeight, parseFloat(yIndexInput.text) + 1.0)
                                                            yIndexInput.text = val.toFixed(2)
                                                            unifiedIndexInput.text = xIndexInput.text + ", " + yIndexInput.text
                                                            miniBedCanvas.requestPaint()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // Action Buttons
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8

                                        AppButton {
                                            Layout.fillWidth: true
                                            iconName: "save"
                                            text: "Save index point"
                                            variant: "primary"
                                            onClicked: {
                                                var xi = parseFloat(xIndexInput.text)
                                                var yi = parseFloat(yIndexInput.text)
                                                if (!isNaN(xi) && !isNaN(yi)) settings.saveIndex(xi, yi)
                                            }
                                        }

                                        AppButton {
                                            Layout.fillWidth: true
                                            iconName: "place"
                                            text: "Move to index"
                                            variant: "outline"
                                            onClicked: {
                                                var xi = parseFloat(xIndexInput.text)
                                                var yi = parseFloat(yIndexInput.text)
                                                if (!isNaN(xi) && !isNaN(yi)) motion.moveToCoordinates(xi, yi)
                                            }
                                        }
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 8

                                        AppButton {
                                            Layout.fillWidth: true
                                            iconName: "my_location"
                                            text: "Capture current DRO"
                                            variant: "warning"
                                            onClicked: {
                                                var cx = motion.xPos
                                                var cy = motion.yPos
                                                xIndexInput.text = cx.toFixed(2)
                                                yIndexInput.text = cy.toFixed(2)
                                                unifiedIndexInput.text = cx.toFixed(2) + ", " + cy.toFixed(2)
                                                settings.saveIndex(cx, cy)
                                                miniBedCanvas.requestPaint()
                                            }
                                        }

                                        AppButton {
                                            Layout.preferredWidth: 120
                                            iconName: "restart_alt"
                                            text: "Reset (10, 10)"
                                            variant: "outline"
                                            onClicked: {
                                                xIndexInput.text = "10.00"
                                                yIndexInput.text = "10.00"
                                                unifiedIndexInput.text = "10.00, 10.00"
                                                settings.saveIndex(10.0, 10.0)
                                                miniBedCanvas.requestPaint()
                                            }
                                        }
                                    }
                                }

                                // Right Sub-Column: Interactive Bed Schematic
                                ColumnLayout {
                                    Layout.preferredWidth: 160
                                    spacing: 4

                                    Text {
                                        text: "BED SCHEMATIC (" + settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + ")"
                                        font.family: "Inter"
                                        font.pixelSize: 9
                                        font.weight: Font.DemiBold
                                        color: Theme.textSecondary
                                    }

                                    Rectangle {
                                        width: 160
                                        height: 160
                                        radius: 6
                                        color: "#080D18"
                                        border.color: Theme.borderCard
                                        border.width: 1
                                        clip: true

                                        Canvas {
                                            id: miniBedCanvas
                                            anchors.fill: parent
                                            anchors.margins: 4

                                            onPaint: {
                                                var ctx = getContext("2d")
                                                ctx.reset()

                                                var w = width
                                                var h = height
                                                var pad = 12
                                                var bw = w - 2 * pad
                                                var bh = h - 2 * pad

                                                var maxW = settings.bedWidth > 0 ? settings.bedWidth : 100.0
                                                var maxH = settings.bedHeight > 0 ? settings.bedHeight : 100.0

                                                var isRight = (settings.originPosition === "top-right" || settings.originPosition === "bottom-right")
                                                var isTop = (settings.originPosition === "top-right" || settings.originPosition === "top-left")

                                                // Bed plate
                                                ctx.fillStyle = "#0F172A"
                                                ctx.fillRect(pad, pad, bw, bh)

                                                // Bed grid (5 subdivisions)
                                                ctx.strokeStyle = "#1E293B"
                                                ctx.lineWidth = 1
                                                var numDivs = 5
                                                for (var gx = 1; gx < numDivs; gx++) {
                                                    var px = pad + (gx / numDivs) * bw
                                                    ctx.beginPath()
                                                    ctx.moveTo(px, pad); ctx.lineTo(px, h - pad)
                                                    ctx.stroke()
                                                }
                                                for (var gy = 1; gy < numDivs; gy++) {
                                                    var py = pad + (gy / numDivs) * bh
                                                    ctx.beginPath()
                                                    ctx.moveTo(pad, py); ctx.lineTo(w - pad, py)
                                                    ctx.stroke()
                                                }

                                                // Bed border
                                                ctx.strokeStyle = "#334155"
                                                ctx.lineWidth = 1.2
                                                ctx.strokeRect(pad, pad, bw, bh)

                                                // Machine Datum Origin (0,0) indicator at designated corner
                                                var origX = isRight ? (w - pad) : pad
                                                var origY = isTop ? pad : (h - pad)
                                                ctx.fillStyle = Qt.rgba(245 / 255, 158 / 255, 11 / 255, 0.35)
                                                ctx.strokeStyle = "#F59E0B"
                                                ctx.lineWidth = 1.5
                                                ctx.beginPath()
                                                ctx.arc(origX, origY, 4, 0, 2 * Math.PI)
                                                ctx.fill()
                                                ctx.stroke()

                                                // (0,0) subtle text near origin corner
                                                ctx.fillStyle = "#F59E0B"
                                                ctx.font = "bold 8px monospace"
                                                var tx = isRight ? (origX - 22) : (origX + 4)
                                                var ty = isTop ? (origY + 11) : (origY - 4)
                                                ctx.fillText("(0,0)", tx, ty)

                                                // Index Point Marker
                                                var xi = parseFloat(xIndexInput.text)
                                                var yi = parseFloat(yIndexInput.text)
                                                if (isNaN(xi)) xi = settings.xindex
                                                if (isNaN(yi)) yi = settings.yindex
                                                xi = Math.max(0, Math.min(maxW, xi))
                                                yi = Math.max(0, Math.min(maxH, yi))

                                                var ix = isRight ? ((w - pad) - (xi / maxW) * bw) : (pad + (xi / maxW) * bw)
                                                var iy = isTop ? (pad + (yi / maxH) * bh) : ((h - pad) - (yi / maxH) * bh)

                                                // Coordinate crosshair lines
                                                ctx.strokeStyle = "rgba(0, 229, 255, 0.45)"
                                                ctx.lineWidth = 1
                                                ctx.beginPath()
                                                ctx.moveTo(pad, iy); ctx.lineTo(w - pad, iy)
                                                ctx.moveTo(ix, pad); ctx.lineTo(ix, h - pad)
                                                ctx.stroke()

                                                // Glowing cyan index dot
                                                ctx.fillStyle = "rgba(0, 229, 255, 0.25)"
                                                ctx.beginPath()
                                                ctx.arc(ix, iy, 7, 0, 2 * Math.PI)
                                                ctx.fill()

                                                ctx.fillStyle = "#00E5FF"
                                                ctx.beginPath()
                                                ctx.arc(ix, iy, 4, 0, 2 * Math.PI)
                                                ctx.fill()
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.CrossCursor
                                                function updateFromMouse(mouse) {
                                                    var pad = 12
                                                    var bw = width - 2 * pad
                                                    var bh = height - 2 * pad
                                                    var maxW = settings.bedWidth > 0 ? settings.bedWidth : 100.0
                                                    var maxH = settings.bedHeight > 0 ? settings.bedHeight : 100.0
                                                    var isRight = (settings.originPosition === "top-right" || settings.originPosition === "bottom-right")
                                                    var isTop = (settings.originPosition === "top-right" || settings.originPosition === "top-left")

                                                    var mx = Math.max(pad, Math.min(width - pad, mouse.x))
                                                    var my = Math.max(pad, Math.min(height - pad, mouse.y))

                                                    var bx = isRight ? (((width - pad) - mx) / bw * maxW) : ((mx - pad) / bw * maxW)
                                                    var by = isTop ? ((my - pad) / bh * maxH) : (((height - pad) - my) / bh * maxH)

                                                    bx = Math.max(0, Math.min(maxW, bx))
                                                    by = Math.max(0, Math.min(maxH, by))

                                                    xIndexInput.text = bx.toFixed(2)
                                                    yIndexInput.text = by.toFixed(2)
                                                    unifiedIndexInput.text = bx.toFixed(2) + ", " + by.toFixed(2)
                                                    miniBedCanvas.requestPaint()
                                                }
                                                onClicked: function(mouse) { updateFromMouse(mouse) }
                                                onPositionChanged: function(mouse) { if (pressed) updateFromMouse(mouse) }
                                            }
                                        }
                                    }

                                    Text {
                                        text: "Click bed · Origin: " + (settings.originPosition === "top-right" ? "Top-Right" : settings.originPosition === "top-left" ? "Top-Left" : settings.originPosition === "bottom-right" ? "Bottom-Right" : "Bottom-Left")
                                        font.family: "Inter"
                                        font.pixelSize: 9
                                        color: Theme.accentAmber
                                        horizontalAlignment: Text.AlignHCenter
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }

                        Connections {
                            target: settings
                            function onSettingsChanged() {
                                xIndexInput.text = settings.xindex.toFixed(2)
                                yIndexInput.text = settings.yindex.toFixed(2)
                                unifiedIndexInput.text = settings.xindex.toFixed(2) + ", " + settings.yindex.toFixed(2)
                                miniBedCanvas.requestPaint()
                            }
                            function onOriginPositionChanged() {
                                miniBedCanvas.requestPaint()
                            }
                            function onHardwareConfigChanged() {
                                miniBedCanvas.requestPaint()
                            }
                        }
                    }

                    // 5. Optical Camera Offsets & Speeds Card
                    MetricCard {
                        Layout.fillWidth: true
                        visible: root.isCameraVisible
                        title: "Optical camera offsets & speeds"
                        subtitle: "Saved to config.ini [camera_offset] & [camera]"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 14

                                // Laser 1 Camera Offset
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6
                                    Text { text: "LASER 1 CAMERA OFFSET"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.textSecondary }
                                    RowLayout {
                                        spacing: 6
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: l1xInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camLaser1X.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: l1yInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camLaser1Y.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                    }
                                }

                                // Laser 2 Camera Offset
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6
                                    Text { text: "LASER 2 CAMERA OFFSET"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.textSecondary }
                                    RowLayout {
                                        spacing: 6
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: l2xInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camLaser2X.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: l2yInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camLaser2Y.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                    }
                                }

                                // Speeds
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6
                                    Text { text: "INSPECTION / JOG FEED"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.textSecondary }
                                    RowLayout {
                                        spacing: 6
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: camInspFeedInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camInspectionFeed.toString(); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true; height: 34; radius: 6; color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                                            TextInput { id: camJogFeedInput; anchors.fill: parent; anchors.margins: 8; verticalAlignment: TextInput.AlignVCenter; text: settings.camJogFeed.toString(); font.family: "IBM Plex Mono"; font.pixelSize: 12; color: Theme.textPrimary }
                                        }
                                    }
                                }
                            }

                            AppButton {
                                Layout.fillWidth: true
                                iconName: "save"
                                text: "Save camera offsets & speeds"
                                variant: "primary"
                                onClicked: {
                                    var l1x = parseFloat(l1xInput.text)
                                    var l1y = parseFloat(l1yInput.text)
                                    var l2x = parseFloat(l2xInput.text)
                                    var l2y = parseFloat(l2yInput.text)
                                    var ci = parseInt(camInspFeedInput.text)
                                    var cj = parseInt(camJogFeedInput.text)
                                    if (!isNaN(l1x) && !isNaN(l1y) && !isNaN(l2x) && !isNaN(l2y) && !isNaN(ci) && !isNaN(cj)) {
                                        settings.saveCameraOffsets(l1x, l1y, l2x, l2y, ci, cj)
                                    }
                                }
                            }
                        }
                    }

                    // 6. System & Company Information Card
                    MetricCard {
                        Layout.fillWidth: true
                        visible: root.isSystemVisible
                        title: "System & company information"
                        subtitle: "Machine environment & software updates"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 16

                            // Top Section: Company Identity & Information
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 14

                                Rectangle {
                                    width: 56
                                    height: 56
                                    radius: 8
                                    color: "#FFFFFF"
                                    border.color: webMouseArea.containsMouse ? Theme.accentAmber : Theme.borderCard
                                    border.width: 1
                                    clip: true
                                    Layout.alignment: Qt.AlignTop

                                    Image {
                                        anchors.fill: parent
                                        anchors.margins: 4
                                        source: typeof appLogoUrl !== "undefined" ? appLogoUrl : ""
                                        fillMode: Image.PreserveAspectFit
                                        smooth: true
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3

                                    Text {
                                        text: "Spécialisé Products Private Limited"
                                        font.family: "Inter"
                                        font.pixelSize: 13
                                        font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    Text {
                                        text: "Precision Photonics · Laser Systems · Instrumentation"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: Theme.accentAmber
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    // Interactive Clickable Website Link
                                    RowLayout {
                                        spacing: 6

                                        AppIcon { name: "language"; size: 13; iconColor: Theme.accentAmber }

                                        Item {
                                            implicitWidth: webLinkText.implicitWidth
                                            implicitHeight: webLinkText.implicitHeight
                                            Layout.preferredWidth: webLinkText.implicitWidth
                                            Layout.preferredHeight: webLinkText.implicitHeight

                                            Text {
                                                id: webLinkText
                                                anchors.fill: parent
                                                text: "www.specialiseproducts.com"
                                                font.family: "Inter"
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                font.underline: webMouseArea.containsMouse
                                                color: webMouseArea.containsMouse ? Theme.accentAmber : Theme.accentBlue
                                            }

                                            MouseArea {
                                                id: webMouseArea
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                                            }
                                        }
                                    }

                                    Text {
                                        text: "Navi Mumbai, India  ·  info@specialiseproducts.com"
                                        font.family: "Inter"
                                        font.pixelSize: 10
                                        color: Theme.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    // Credential Badges (Flow wrapping cleanly!)
                                    Flow {
                                        Layout.fillWidth: true
                                        spacing: 6
                                        Layout.topMargin: 2

                                        Repeater {
                                            model: ["ISO 9001:2015", "Make in India", "CE / EMC", "MSME Udyam"]
                                            Rectangle {
                                                height: 18
                                                implicitWidth: credTxt.implicitWidth + 10
                                                radius: 3
                                                color: Theme.isDark ? "#172338" : "#E9EDF9"
                                                border.color: Theme.isDark ? "#263550" : "#DCE2EC"
                                                border.width: 1

                                                Text {
                                                    id: credTxt
                                                    anchors.centerIn: parent
                                                    text: modelData
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    font.weight: Font.DemiBold
                                                    color: Theme.isDark ? "#94A3B8" : "#192D78"
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // Machine Architecture & Communication Specs
                            Flow {
                                Layout.fillWidth: true
                                spacing: 6

                                Repeater {
                                    model: [
                                        { label: "PySide6 Qt Quick · Direct3D GPU", col: Theme.textSecondary },
                                        { label: "M400 + M114 Closed-Loop Protocol", col: Theme.textSecondary },
                                        { label: "100% Declarative Architecture", col: Theme.accentAmber }
                                    ]
                                    Rectangle {
                                        height: 20
                                        implicitWidth: specRow.implicitWidth + 12
                                        radius: 4
                                        color: Theme.isDark ? "#111A2D" : "#F1F5F9"
                                        border.color: Theme.isDark ? "#1E2B45" : "#E2E8F0"
                                        border.width: 1

                                        RowLayout {
                                            id: specRow
                                            anchors.centerIn: parent
                                            spacing: 4
                                            Text {
                                                text: modelData.label
                                                font.family: "IBM Plex Mono"
                                                font.pixelSize: 9
                                                font.weight: Font.DemiBold
                                                color: modelData.col
                                            }
                                        }
                                    }
                                }
                            }

                            // Horizontal Divider
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: Theme.isDark ? "#1E293B" : "#E2E8F0"
                            }

                            // Software Version & Update Controls Section (Responsive 2-Tier Layout)
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                // Status Row (Icon + Version Details)
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 12

                                    Rectangle {
                                        width: 36
                                        height: 36
                                        radius: 8
                                        color: Theme.isDark ? "#142036" : "#EFF6FF"
                                        border.color: Theme.isDark ? "#1E3050" : "#DBEAFE"
                                        border.width: 1

                                        AppIcon {
                                            anchors.centerIn: parent
                                            name: root.updaterAvailable ? "system_update" : (root.updaterChecking ? "sync" : "inventory_2")
                                            size: 20
                                            iconColor: root.updaterAvailable ? Theme.accentGreen : Theme.accentCyan

                                            RotationAnimation on rotation {
                                                running: root.updaterChecking
                                                from: 0
                                                to: 360
                                                loops: Animation.Infinite
                                                duration: 1000
                                            }
                                        }
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        Flow {
                                            Layout.fillWidth: true
                                            spacing: 8

                                            Text {
                                                text: settings.machineName + " Software"
                                                font.family: "Inter"
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                                color: Theme.textPrimary
                                            }

                                            Rectangle {
                                                height: 18
                                                radius: 9
                                                color: Theme.isDark ? "#1E293B" : "#F1F5F9"
                                                implicitWidth: verText.implicitWidth + 12

                                                Text {
                                                    id: verText
                                                    anchors.centerIn: parent
                                                    text: "v" + root.updaterCurrentVer
                                                    font.family: "IBM Plex Mono"
                                                    font.pixelSize: 10
                                                    font.weight: Font.Bold
                                                    color: Theme.textPrimary
                                                }
                                            }

                                            // Update available pill
                                            Rectangle {
                                                visible: root.updaterAvailable
                                                height: 18
                                                radius: 9
                                                color: Theme.pillOnlineBg
                                                border.color: Theme.accentGreen
                                                border.width: 1
                                                implicitWidth: availText.implicitWidth + 12

                                                Text {
                                                    id: availText
                                                    anchors.centerIn: parent
                                                    text: "v" + root.updaterLatestVer + " Available!"
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    font.weight: Font.Bold
                                                    color: Theme.accentGreen
                                                }
                                            }
                                        }

                                        Text {
                                            Layout.fillWidth: true
                                            text: {
                                                if (root.updaterChecking) {
                                                    return "Checking update servers for new releases..."
                                                }
                                                if (root.updaterDownloading) {
                                                    return "Downloading update v" + root.updaterLatestVer + " in background (" + root.updaterDownloadProgress.toFixed(0) + "%) — Click to view."
                                                }
                                                if (root.updaterAvailable) {
                                                    if (root.updaterDownloadProgress >= 100.0) {
                                                        return "Update v" + root.updaterLatestVer + " downloaded & ready to install."
                                                    }
                                                    return "New release ready: v" + root.updaterLatestVer + " — Click to inspect changelog."
                                                }
                                                if (typeof updater !== "undefined" && updater && updater.statusMessage) {
                                                    return updater.statusMessage + (root.updaterCheckedTime !== "" ? " · " + root.updaterCheckedTime : "")
                                                }
                                                return "Last checked: " + root.updaterCheckedTime + " · System up to date."
                                            }
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: (root.updaterAvailable || root.updaterDownloading) ? Theme.accentCyan : Theme.textSecondary
                                            wrapMode: Text.WordWrap
                                        }
                                    }
                                }

                                // Action Buttons (Right-aligned, flows seamlessly on narrow width)
                                Flow {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    layoutDirection: Qt.RightToLeft

                                    // Check for Updates Button
                                    Rectangle {
                                        height: 32
                                        radius: 6
                                        color: chkMa.containsMouse ? (Theme.isDark ? "#243650" : "#E2E8F0") : (Theme.isDark ? "#142036" : "#F8FAFC")
                                        border.color: Theme.isDark ? "#2A3C55" : "#CBD5E1"
                                        border.width: 1
                                        implicitWidth: chkRow.implicitWidth + 20
                                        enabled: !root.updaterChecking

                                        RowLayout {
                                            id: chkRow
                                            anchors.centerIn: parent
                                            spacing: 6
                                            AppIcon {
                                                name: "sync"
                                                size: 14
                                                iconColor: Theme.textPrimary
                                                RotationAnimation on rotation {
                                                    running: root.updaterChecking
                                                    from: 0
                                                    to: 360
                                                    loops: Animation.Infinite
                                                    duration: 1000
                                                }
                                            }
                                            Text {
                                                text: root.updaterChecking ? "Checking..." : (root.updaterDownloading ? "View Download" : "Check for Updates")
                                                font.family: "Inter"
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: Theme.textPrimary
                                            }
                                        }

                                        MouseArea {
                                            id: chkMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (typeof updater !== "undefined" && updater) {
                                                    if (updater.isDownloading || (updater.downloadProgress >= 100.0 && updater.updateAvailable)) {
                                                        updateModal.open()
                                                    } else {
                                                        updater.checkForUpdates(false)
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // Review & Install Button (shown when update available or active background download)
                                    Rectangle {
                                        visible: root.updaterAvailable || root.updaterDownloading
                                        height: 32
                                        radius: 6
                                        color: revMa.containsMouse ? Qt.lighter(Theme.accentCyan, 1.1) : Theme.accentCyan
                                        implicitWidth: revText.implicitWidth + 24

                                        RowLayout {
                                            anchors.centerIn: parent
                                            spacing: 6
                                            AppIcon {
                                                name: root.updaterDownloading ? "download" : (root.updaterDownloadProgress >= 100.0 ? "check_circle" : "system_update_alt")
                                                size: 14
                                                iconColor: "#0B1220"
                                            }
                                            Text {
                                                id: revText
                                                text: root.updaterDownloading
                                                    ? "Downloading (" + root.updaterDownloadProgress.toFixed(0) + "%)..."
                                                    : (root.updaterDownloadProgress >= 100.0 ? "Install Update" : "Review & Install")
                                                font.family: "Inter"
                                                font.pixelSize: 11
                                                font.weight: Font.Bold
                                                color: "#0B1220"
                                            }
                                        }

                                        MouseArea {
                                            id: revMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: updateModal.open()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
