import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "views"

ApplicationWindow {
    id: window
    width: 1440
    height: 900
    minimumWidth: 960
    minimumHeight: 560
    visible: true
    title: settings.machineName + " — Spécialisé Products Private Limited"
    color: Theme.bgApp

    // Ensure immediate scene graph refresh on maximize, unmaximize, and visibility changes
    onWindowStateChanged: {
        window.requestUpdate()
    }
    onVisibilityChanged: {
        window.requestUpdate()
    }

    FontLoader {
        id: materialIconsFont
        source: "fonts/MaterialIcons-Regular.ttf"
    }

    onClosing: function(close) {
        laser.shutdownLaser()
        camera.stopCamera()
    }

    // Top Application Header
    header: Rectangle {
        id: appHeader
        height: 72
        color: Theme.bgHeader
        border.color: Theme.borderHeader
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 24
            spacing: 16

            // Product Identity (Logo & Title) with link to official website
            Item {
                implicitWidth: brandRow.implicitWidth
                implicitHeight: 44
                Layout.preferredWidth: brandRow.implicitWidth
                Layout.preferredHeight: 44
                Layout.alignment: Qt.AlignVCenter

                RowLayout {
                    id: brandRow
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 12

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 8
                        color: "#ffffff"
                        border.color: brandMa.containsMouse ? Theme.accentAmber : Theme.borderCard
                        border.width: 1
                        clip: true

                        Image {
                            anchors.fill: parent
                            anchors.margins: 3
                            source: typeof appLogoUrl !== "undefined" ? appLogoUrl : ""
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                            visible: source.toString().length > 0
                        }

                        AppIcon {
                            anchors.centerIn: parent
                            name: "bolt"
                            size: 24
                            iconColor: Theme.accentAmber
                            visible: !parent.children[0].visible
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: settings.machineName
                            font.family: "Inter"
                            font.pixelSize: 17
                            font.weight: Font.DemiBold
                            color: brandMa.containsMouse ? Theme.accentAmber : Theme.textBrand
                        }
                        Text {
                            text: "SPÉCIALISÉ PRODUCTS · DIODE LASER CNC"
                            font.family: "Inter"
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                            color: Theme.textSecondary
                            font.letterSpacing: 0.6
                        }
                    }
                }

                MouseArea {
                    id: brandMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Spécialisé Products Private Limited (www.specialiseproducts.com)"
                    ToolTip.delay: 300
                }
            }

            Item { Layout.fillWidth: true }

            // Live Coordinates Quick Ticker
            Rectangle {
                height: 38
                radius: 6
                color: Theme.isDark ? "#111827" : "#F1F4F8"
                border.color: Theme.isDark ? "#1E293B" : "#DCE2EC"
                border.width: 1
                implicitWidth: coordRow.implicitWidth + 24

                RowLayout {
                    id: coordRow
                    anchors.centerIn: parent
                    spacing: 16

                    RowLayout {
                        spacing: 6
                        Text { text: "X"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                        Text { text: motion.xPos.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.textPrimary }
                    }

                    RowLayout {
                        spacing: 6
                        Text { text: "Y"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                        Text { text: motion.yPos.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.textPrimary }
                    }

                    RowLayout {
                        spacing: 6
                        Text { text: "Z"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                        Text { text: motion.zPos.toFixed(2); font.family: "IBM Plex Mono"; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.textPrimary }
                    }
                }
            }

            // User Role Pill (Click to open Settings)
            Rectangle {
                id: rolePill
                height: 36
                radius: 18
                color: roleMa.containsMouse ? (Theme.isDark ? "#1E293B" : "#E2E8F0") : Theme.pillRoleBg
                border.color: Theme.pillRoleBorder
                border.width: 1
                implicitWidth: rolePillRow.implicitWidth + 20

                scale: roleMa.pressed ? 0.95 : (roleMa.containsMouse ? 1.03 : 1.0)
                Behavior on scale {
                    NumberAnimation { duration: 120; easing.type: Easing.OutBack }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

                RowLayout {
                    id: rolePillRow
                    anchors.centerIn: parent
                    spacing: 6
                    AppIcon {
                        name: settings.currentRole === "Supervisor" ? "timer" : (settings.currentRole === "Admin" ? "admin_panel_settings" : (settings.isPrivileged ? "lock_open" : "person"))
                        size: 15
                        iconColor: settings.currentRole === "Admin" ? Theme.accentCyan : (settings.currentRole === "Supervisor" ? Theme.accentAmber : Theme.pillRoleText)
                    }
                    Text {
                        text: {
                            if (settings.currentRole === "Supervisor" || settings.currentRole === "Admin") {
                                var m = Math.floor(settings.supervisorRemainingSeconds / 60)
                                var s = settings.supervisorRemainingSeconds % 60
                                var timeStr = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s)
                                return settings.currentRole.toUpperCase() + " (" + timeStr + ")"
                            }
                            return settings.currentRole.toUpperCase()
                        }
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: settings.currentRole === "Admin" ? Theme.accentCyan : (settings.currentRole === "Supervisor" ? Theme.accentAmber : Theme.pillRoleText)
                    }
                }

                MouseArea {
                    id: roleMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: viewStack.currentIndex = viewStack.count - 1
                    ToolTip.visible: containsMouse
                    ToolTip.text: settings.currentRole.toUpperCase() + " profile (Click to open Settings)"
                    ToolTip.delay: 400
                }
            }

            // Quick Logout Button (Visible when logged in as Supervisor or Admin)
            Rectangle {
                id: logoutHeaderBtn
                visible: settings.isPrivileged
                height: 36
                width: 36
                radius: 18
                color: logoutMa.containsMouse ? (Theme.isDark ? "#2A151C" : "#FEE2E2") : Theme.pillRoleBg
                border.color: logoutMa.containsMouse ? Theme.accentRed : Theme.pillRoleBorder
                border.width: 1

                scale: logoutMa.pressed ? 0.92 : (logoutMa.containsMouse ? 1.08 : 1.0)
                Behavior on scale {
                    NumberAnimation { duration: 120; easing.type: Easing.OutBack }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }
                Behavior on border.color {
                    ColorAnimation { duration: 150 }
                }

                AppIcon {
                    anchors.centerIn: parent
                    name: "logout"
                    size: 16
                    iconColor: logoutMa.containsMouse ? Theme.accentRed : (settings.currentRole === "Admin" ? Theme.accentCyan : Theme.accentAmber)
                }

                MouseArea {
                    id: logoutMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: settings.logout()
                    ToolTip.visible: containsMouse
                    ToolTip.text: "Logout"
                    ToolTip.delay: 200
                }
            }

            // Connection Status Pill
            Rectangle {
                height: 36
                radius: 18
                color: serial.connected ? Theme.pillOnlineBg : Theme.pillOfflineBg
                border.color: serial.connected ? Theme.pillOnlineBorder : Theme.pillOfflineBorder
                border.width: 1
                implicitWidth: connRow.implicitWidth + 24

                RowLayout {
                    id: connRow
                    anchors.centerIn: parent
                    spacing: 8

                    // Status Dot with Breathing Radar Aura Ring
                    Item {
                        width: 12
                        height: 12

                        Rectangle {
                            anchors.centerIn: parent
                            width: 12
                            height: 12
                            radius: 6
                            color: "transparent"
                            border.color: serial.connected ? Theme.pillOnlineText : Theme.pillOfflineText
                            border.width: 1

                            SequentialAnimation on scale {
                                running: serial.connected
                                loops: Animation.Infinite
                                NumberAnimation { from: 0.6; to: 1.9; duration: 1500; easing.type: Easing.OutCubic }
                            }
                            SequentialAnimation on opacity {
                                running: serial.connected
                                loops: Animation.Infinite
                                NumberAnimation { from: 0.8; to: 0.0; duration: 1500; easing.type: Easing.OutQuad }
                            }
                        }

                        Rectangle {
                            anchors.centerIn: parent
                            width: 7
                            height: 7
                            radius: 3.5
                            color: serial.connected ? Theme.pillOnlineText : Theme.pillOfflineText

                            SequentialAnimation on opacity {
                                running: serial.connected
                                loops: Animation.Infinite
                                PropertyAnimation { to: 0.35; duration: 800 }
                                PropertyAnimation { to: 1.0; duration: 800 }
                            }
                        }
                    }

                    Text {
                        text: serial.connected ? ("ONLINE · " + (serial.selectedPort ? serial.selectedPort : "COM")) : "OFFLINE"
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: serial.connected ? Theme.pillOnlineText : Theme.pillOfflineText
                    }
                }
            }

            // --- Notification Bell Button ---
            Rectangle {
                id: notifBellBtn
                height: 36
                width: 36
                radius: 18
                color: notifBellMa.containsMouse || notifDrawer.visible
                    ? (Theme.isDark ? "#1E293B" : "#E2E8F0")
                    : (notifications.unreadCount > 0 ? (Theme.isDark ? "#162035" : "#EEF2FF") : Theme.pillRoleBg)
                border.color: notifications.unreadCount > 0 ? Theme.accentCyan : Theme.pillRoleBorder
                border.width: notifications.unreadCount > 0 ? 1.5 : 1

                scale: notifBellMa.pressed ? 0.93 : (notifBellMa.containsMouse ? 1.06 : 1.0)
                Behavior on scale {
                    NumberAnimation { duration: 120; easing.type: Easing.OutBack }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

                AppIcon {
                    id: bellIconText
                    anchors.centerIn: parent
                    name: "notifications"
                    size: 18
                    iconColor: notifications.unreadCount > 0 ? Theme.accentCyan : Theme.textPrimary

                    // Dynamic Wiggle / Shake animation when a new notification arrives
                    SequentialAnimation on rotation {
                        id: bellShakeAnim
                        running: false
                        NumberAnimation { to: 16; duration: 60 }
                        NumberAnimation { to: -16; duration: 60 }
                        NumberAnimation { to: 12; duration: 60 }
                        NumberAnimation { to: -12; duration: 60 }
                        NumberAnimation { to: 0; duration: 60 }
                    }
                }

                // Unread Count Badge (Pill with count)
                Rectangle {
                    visible: notifications.unreadCount > 0
                    anchors.top: parent.top
                    anchors.topMargin: -2
                    anchors.right: parent.right
                    anchors.rightMargin: -3
                    height: 16
                    radius: 8
                    color: "#EF4444"
                    border.color: Theme.isDark ? "#060A14" : "#FFFFFF"
                    border.width: 1.5
                    implicitWidth: Math.max(16, unreadBadgeText.implicitWidth + 8)

                    Text {
                        id: unreadBadgeText
                        anchors.centerIn: parent
                        text: notifications.unreadCount > 99 ? "99+" : notifications.unreadCount.toString()
                        font.family: "Inter"
                        font.pixelSize: 9
                        font.weight: Font.Bold
                        color: "#FFFFFF"
                    }

                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        running: notifications.unreadCount > 0
                        PropertyAnimation { to: 1.15; duration: 1000; easing.type: Easing.InOutQuad }
                        PropertyAnimation { to: 1.0; duration: 1000; easing.type: Easing.InOutQuad }
                    }
                }

                MouseArea {
                    id: notifBellMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: notifDrawer.visible = !notifDrawer.visible
                    ToolTip.visible: containsMouse && !notifDrawer.visible
                    ToolTip.text: notifications.unreadCount > 0
                        ? notifications.unreadCount + " unread notification" + (notifications.unreadCount > 1 ? "s" : "")
                        : "Notifications (All caught up)"
                    ToolTip.delay: 300
                }
            }

            // --- Theme Toggle Button (Light / Dark Switch) ---
            Rectangle {
                id: themeToggleBtn
                height: 36
                implicitWidth: themeToggleRow.implicitWidth + 22
                radius: 18
                color: themeToggleMa.containsMouse ? (Theme.isDark ? "#1E293B" : "#E2E8F0") : Theme.pillRoleBg
                border.color: Theme.pillRoleBorder
                border.width: 1

                scale: themeToggleMa.pressed ? 0.93 : (themeToggleMa.containsMouse ? 1.05 : 1.0)
                Behavior on scale {
                    NumberAnimation { duration: 120; easing.type: Easing.OutBack }
                }
                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

                RowLayout {
                    id: themeToggleRow
                    anchors.centerIn: parent
                    spacing: 6

                    AppIcon {
                        name: Theme.isDark ? "dark_mode" : "light_mode"
                        size: 15
                        iconColor: Theme.accentAmber
                    }

                    Text {
                        text: Theme.isDark ? "DARK" : "LIGHT"
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }
                }

                MouseArea {
                    id: themeToggleMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: settings.toggleTheme()
                }
            }
        }
    }

    // Main App Layout: Sidebar + StackLayout View
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Navigation Sidebar
        Rectangle {
            Layout.preferredWidth: 216
            Layout.fillHeight: true
            color: Theme.bgSidebar
            border.color: Theme.borderSidebar
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.topMargin: 24
                anchors.bottomMargin: 20
                anchors.leftMargin: 14
                anchors.rightMargin: 14
                spacing: 6

                // Section Label
                Text {
                    text: "MACHINE WORKSPACE"
                    font.family: "Inter"
                    font.pixelSize: 9
                    font.weight: Font.Bold
                    color: Theme.sidebarNavLabel
                    Layout.leftMargin: 6
                    Layout.bottomMargin: 8
                }

                Repeater {
                    model: {
                        // Reactive bindings to refresh sidebar on permission or role changes
                        var _op = settings.operatorPages
                        var _sp = settings.supervisorPages
                        var _role = settings.currentRole
                        var _cam = settings.cameraEnabled

                        var allItems = [
                            { key: "motion", label: "Motion & DRO", icon: "tune", viewIndex: 0 },
                            { key: "laser", label: "Laser Control", icon: "flash_on", viewIndex: 1 },
                            { key: "job", label: "Job & Run", icon: "folder_open", viewIndex: 2 }
                        ]
                        if (_cam) {
                            allItems.push({ key: "camera", label: "Camera Vision", icon: "videocam", viewIndex: 3 })
                        }
                        allItems.push({ key: "terminal", label: "Terminal", icon: "terminal", viewIndex: 4 })
                        if (_role === "Admin") {
                            allItems.push({ key: "setup", label: "Machine Setup", icon: "build", viewIndex: 5 })
                        }
                        allItems.push({ key: "settings", label: "Settings", icon: "settings", viewIndex: 6 })

                        var filtered = []
                        for (var i = 0; i < allItems.length; i++) {
                            var it = allItems[i]
                            if (it.key === "setup") {
                                filtered.push(it)
                            } else if (settings.isPageAllowed(_role, it.key)) {
                                filtered.push(it)
                            }
                        }
                        return filtered
                    }

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 48
                        radius: 6
                        color: viewStack.currentIndex === modelData.viewIndex ? Theme.sidebarItemActive : (navMa.containsMouse ? Theme.sidebarItemHover : "transparent")
                        border.color: viewStack.currentIndex === modelData.viewIndex ? Theme.sidebarItemActiveBorder : "transparent"
                        border.width: 1

                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        // Left Active Glowing Accent Indicator Pill
                        Rectangle {
                            anchors.left: parent.left
                            anchors.leftMargin: 2
                            anchors.verticalCenter: parent.verticalCenter
                            width: 3
                            height: viewStack.currentIndex === modelData.viewIndex ? 22 : 0
                            radius: 1.5
                            color: Theme.accentCyan
                            opacity: viewStack.currentIndex === modelData.viewIndex ? 1.0 : 0.0
                            Behavior on height { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
                            Behavior on opacity { NumberAnimation { duration: 150 } }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 14
                            spacing: 12

                            transform: Translate {
                                x: (navMa.containsMouse && viewStack.currentIndex !== modelData.viewIndex) ? 4 : 0
                                Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                            }

                            AppIcon {
                                name: modelData.icon
                                size: 18
                                iconColor: viewStack.currentIndex === modelData.viewIndex ? Theme.accentCyan : Theme.sidebarTextInactive
                            }

                            Text {
                                text: modelData.label
                                font.family: "Inter"
                                font.pixelSize: 12
                                font.weight: viewStack.currentIndex === modelData.viewIndex ? Font.DemiBold : Font.Normal
                                color: viewStack.currentIndex === modelData.viewIndex ? Theme.sidebarTextActive : Theme.sidebarTextInactive
                            }
                        }

                        MouseArea {
                            id: navMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: viewStack.currentIndex = modelData.viewIndex
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                // Machine Specification Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 84
                    radius: 6
                    color: Theme.sidebarBadgeBg
                    clip: true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 4

                        Text {
                            text: "MACHINE ENVELOPE"
                            font.family: "Inter"
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                            color: "#A6B1C4"
                        }

                        Text {
                            text: settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + " mm"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            color: "#FFFFFF"
                        }

                        Text {
                            text: (settings.laserCount === 1 ? "Single-laser" : "Dual-laser") + " CNC system"
                            font.family: "Inter"
                            font.pixelSize: 9
                            color: "#A6B1C4"
                        }
                    }
                }

                // Quick Connect/Disconnect button in sidebar bottom
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    radius: 6
                    color: serial.connected
                        ? (discMa.down ? Qt.darker("#172338", 1.2) : (discMa.containsMouse ? "#202E47" : "#172338"))
                        : (discMa.down ? "#1E40AF" : (discMa.containsMouse ? "#2563EB" : "#1D4ED8"))
                    border.color: serial.connected ? "#263550" : "#3B82F6"
                    border.width: serial.connected ? 1 : 1.5

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 8
                        AppIcon {
                            name: serial.connected ? "power" : "link"
                            size: 16
                            iconColor: serial.connected ? "#FFFFFF" : "#00E5FF"
                        }
                        Text {
                            text: serial.connected ? "Disconnect" : "Connect port"
                            font.family: "Inter"
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                            color: "#FFFFFF"
                        }
                    }

                    MouseArea {
                        id: discMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (serial.connected) {
                                serial.disconnectSerial()
                            } else {
                                serial.refreshPorts()
                                var ok = serial.connectSerial()
                                if (!ok) {
                                    window.navigateToView("settings")
                                    serial.refreshPorts()
                                }
                            }
                        }
                    }
                }
            }
        }

        // View Stack
        StackLayout {
            id: viewStack
            objectName: "viewStack"
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: 0

            JogView {}
            LaserView {}
            JobView {}
            CameraView {}
            TerminalView {}
            HardwareSetupView {}
            SettingsView {
                id: settingsView
            }
        }
    }

    // Bottom Status Bar
    footer: Rectangle {
        height: 32
        color: Theme.bgFooter
        border.color: Theme.borderFooter
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            spacing: 16

            RowLayout {
                spacing: 8
                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: Theme.accentGreen
                }
                Text {
                    id: statusBanner
                    text: "Ready — System initialized (PySide6 Qt Quick GPU Engine)"
                    font.family: "Inter"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            RowLayout {
                spacing: 10

                Text {
                    id: footerWebLink
                    text: "Copyright © Spécialisé Products Private Limited"
                    font.family: "Inter"
                    font.pixelSize: 11
                    font.underline: footerWebMa.containsMouse
                    color: footerWebMa.containsMouse ? Theme.accentAmber : Theme.textSecondary

                    MouseArea {
                        id: footerWebMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                        ToolTip.visible: containsMouse
                        ToolTip.text: "Visit www.specialiseproducts.com"
                        ToolTip.delay: 300
                    }
                }

                Text {
                    text: "·"
                    font.pixelSize: 11
                    color: Theme.textMuted
                }

                Text {
                    text: "Laser: " + laser.selectedLaser + "  |  Bed: " + settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + " mm"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                }
            }
        }
    }

    // Listen to status alerts from bridges
    Connections {
        target: motion
        function onSafetyAlert(msg) { statusBanner.text = msg }
    }
    Connections {
        target: laser
        function onStatusAlert(msg) { statusBanner.text = msg }
    }
    Connections {
        target: job
        function onStatusAlert(msg) { statusBanner.text = msg }
    }
    Connections {
        target: serial
        function onStatusMessage(msg) { statusBanner.text = msg }
        function onAutoConnectRequested(port, baud) {
            autoConnectModal.showPrompt(port, baud)
        }
        function onAutoConnectFailed(msg) {
            statusBanner.text = msg
        }
        function onAutoConnectCancelled() {
            autoConnectModal.close()
        }
    }
    Connections {
        target: settings
        function onLoginSuccess(msg) { statusBanner.text = msg }
        function onLoginFailed(msg) { statusBanner.text = msg }
        function onSettingsSaved(msg) { statusBanner.text = msg }
        function onRoleChanged() {
            window.validateCurrentViewAccess()
        }
        function onRolePermissionsChanged() {
            window.validateCurrentViewAccess()
        }
        function onCameraEnabledChanged() {
            window.validateCurrentViewAccess()
        }
    }

    // Startup Auto-Connect Trigger matching main.py onLoad()
    Component.onCompleted: {
        startupAutoConnectTimer.start()
    }

    Timer {
        id: startupAutoConnectTimer
        interval: 350
        repeat: false
        onTriggered: {
            serial.checkAutoConnect()
        }
    }

    // --- Modern Glassmorphic Auto-Connect Modal Dialog ---
    Rectangle {
        id: autoConnectModal
        objectName: "autoConnectModal"
        visible: false
        z: 99999
        x: 0
        y: -appHeader.height
        width: window.width
        height: window.height
        color: Qt.rgba(0, 0, 0, 0.65)

        property string candidatePort: ""
        property string candidateBaud: ""

        function showPrompt(p, b) {
            candidatePort = p
            candidateBaud = b
            visible = true
        }

        function close() {
            visible = false
        }

        // Prevent mouse clicks, hovers, and wheel scrolling through modal backdrop
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
            onClicked: {}
            onWheel: function(wheel) {
                wheel.accepted = true
            }
        }

        Rectangle {
            id: modalBox
            anchors.centerIn: parent
            width: Math.min(480, parent.width - 40)
            height: modalCol.implicitHeight + 48
            radius: 12
            color: Theme.bgCard
            border.color: Theme.accentAmber
            border.width: 1.5

            scale: autoConnectModal.visible ? 1.0 : 0.88
            opacity: autoConnectModal.visible ? 1.0 : 0.0
            Behavior on scale {
                NumberAnimation { duration: 220; easing.type: Easing.OutBack }
            }
            Behavior on opacity {
                NumberAnimation { duration: 160; easing.type: Easing.OutQuad }
            }

            // Absorb clicks and wheel scrolling on the modal card itself
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

            // Top Amber Highlight Stripe
            Rectangle {
                width: parent.width - 24
                height: 3
                radius: 1.5
                anchors.top: parent.top
                anchors.topMargin: 1
                anchors.horizontalCenter: parent.horizontalCenter
                color: Theme.accentAmber
            }

            ColumnLayout {
                id: modalCol
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 24
                spacing: 16

                // Header with glowing icon
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 8
                        color: Theme.isDark ? "#1E293B" : "#FEF3C7"
                        border.color: Theme.accentAmber
                        border.width: 1

                        AppIcon {
                            anchors.centerIn: parent
                            name: "flash_on"
                            size: 24
                            iconColor: Theme.accentAmber
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "COM PORT AUTO-CONNECTION"
                            font.family: "Inter"
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                            font.letterSpacing: 0.5
                        }

                        Text {
                            text: "Saved controller configuration detected"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                    }
                }

                // Port & Baud Info Badge
                Rectangle {
                    Layout.fillWidth: true
                    height: 52
                    radius: 8
                    color: Theme.bgInput
                    border.color: Theme.borderInput
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        spacing: 14

                        RowLayout {
                            spacing: 6
                            Text { text: "PORT:"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.textSecondary }
                            Text { text: autoConnectModal.candidatePort; font.family: "IBM Plex Mono"; font.pixelSize: 13; font.weight: Font.Bold; color: Theme.accentCyan }
                        }

                        Rectangle { width: 1; height: 18; color: Theme.borderInput }

                        RowLayout {
                            spacing: 6
                            Text { text: "BAUD:"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.textSecondary }
                            Text { text: autoConnectModal.candidateBaud; font.family: "IBM Plex Mono"; font.pixelSize: 13; font.weight: Font.Bold; color: Theme.accentGreen }
                        }

                        Item { Layout.fillWidth: true }

                        RowLayout {
                            spacing: 6
                            Rectangle { width: 8; height: 8; radius: 4; color: Theme.accentGreen }
                            Text { text: "READY"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.accentGreen }
                        }
                    }
                }

                // Main Prompt Text
                Text {
                    Layout.fillWidth: true
                    text: "Do you want to auto connect to <b>" + autoConnectModal.candidatePort + "</b> @ <b>" + autoConnectModal.candidateBaud + "</b> and auto-home the machine (G28)?"
                    textFormat: Text.RichText
                    font.family: "Inter"
                    font.pixelSize: 13
                    color: Theme.textPrimary
                    wrapMode: Text.WordWrap
                    lineHeight: 1.3
                }

                // Action Buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Layout.topMargin: 6

                    AppButton {
                        Layout.fillWidth: true
                        implicitHeight: 40
                        text: "CANCEL"
                        variant: "secondary"
                        onClicked: {
                            autoConnectModal.close()
                            serial.rejectAutoConnect()
                        }
                    }

                    AppButton {
                        Layout.fillWidth: true
                        implicitHeight: 40
                        iconName: "flash_on"
                        text: "CONNECT & AUTO-HOME"
                        variant: "primary"
                        onClicked: {
                            autoConnectModal.close()
                            serial.acceptAutoConnect()
                        }
                    }
                }
            }
        }
    }

    // --- Connections to JobBridge for Out-of-Bounds Boundary Warnings ---
    Connections {
        target: job
        function onBoundaryWarning(title, msg, canShift, w, h) {
            boundaryWarningModal.visible = true
        }
        function onIsOutOfBoundsChanged() {
            if (!job.isOutOfBounds) {
                boundaryWarningModal.visible = false
            }
        }
    }

    // --- Out of Bounds / File Size Boundary Warning Modal Overlay ---
    Rectangle {
        id: boundaryWarningModal
        objectName: "boundaryWarningModal"
        visible: false
        z: 10000
        x: 0
        y: -appHeader.height
        width: window.width
        height: window.height
        color: Qt.rgba(0, 0, 0, 0.72)

        function open() { visible = true }
        function close() { visible = false }

        // Block clicks, hovers, and wheel scrolls through backdrop
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
            onClicked: {}
            onWheel: function(wheel) {
                wheel.accepted = true
            }
        }

        Rectangle {
            id: boundaryModalBox
            anchors.centerIn: parent
            width: Math.min(520, parent.width - 40)
            height: boundaryModalCol.implicitHeight + 48
            radius: 12
            color: Theme.isDark ? "#0F172A" : "#FFFFFF"
            border.color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
            border.width: 1.5

            scale: boundaryWarningModal.visible ? 1.0 : 0.88
            opacity: boundaryWarningModal.visible ? 1.0 : 0.0
            Behavior on scale {
                NumberAnimation { duration: 220; easing.type: Easing.OutBack }
            }
            Behavior on opacity {
                NumberAnimation { duration: 160; easing.type: Easing.OutQuad }
            }

            // Absorb clicks and wheel scrolling on the modal card itself
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

            // Top Colored Highlight Stripe (Red for too large, Amber for index overflow)
            Rectangle {
                width: parent.width - 24
                height: 3
                radius: 1.5
                anchors.top: parent.top
                anchors.topMargin: 1
                anchors.horizontalCenter: parent.horizontalCenter
                color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
            }

            ColumnLayout {
                id: boundaryModalCol
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 24
                spacing: 16

                // Header with Glowing Icon & Title
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 8
                        color: job.isTooLarge
                            ? (Theme.isDark ? "#2D1215" : "#FEE2E2")
                            : (Theme.isDark ? "#2D2211" : "#FEF3C7")
                        border.color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                        border.width: 1

                        AppIcon {
                            anchors.centerIn: parent
                            name: job.isTooLarge ? "block" : "warning"
                            size: 24
                            iconColor: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: job.boundaryTitle ? job.boundaryTitle.toUpperCase() : "BOUNDARY WARNING"
                            font.family: "Inter"
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            color: job.isTooLarge ? "#EF4444" : (Theme.isDark ? Theme.accentAmber : "#B45309")
                            font.letterSpacing: 0.5
                        }

                        Text {
                            text: job.fileName
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                        }
                    }
                }

                // Envelope Comparison Card
                Rectangle {
                    Layout.fillWidth: true
                    radius: 8
                    color: Theme.isDark ? "#141E33" : "#F8FAFC"
                    border.color: Theme.isDark ? "#1E293B" : "#DCE2EC"
                    border.width: 1
                    implicitHeight: bEnvCol.implicitHeight + 20

                    ColumnLayout {
                        id: bEnvCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "Design dimensions:"
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                            }
                            Text {
                                text: job.rawDesignWidth.toFixed(1) + " × " + job.rawDesignHeight.toFixed(1) + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "Machine bed envelope:"
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                            }
                            Text {
                                text: settings.bedWidth.toFixed(1) + " × " + settings.bedHeight.toFixed(1) + " mm"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Theme.textPrimary
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.isDark ? "#1E293B" : "#E2E8F0"
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "Machine safety status:"
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                            }
                            Text {
                                text: job.isTooLarge ? "EXCEEDS MAXIMUM BED CAPACITY" : "EXCEEDS BED AT CURRENT INDEX"
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                            }
                        }
                    }
                }

                // Description Message Text
                Text {
                    Layout.fillWidth: true
                    text: job.boundaryMessage
                    font.family: "Inter"
                    font.pixelSize: 12
                    color: Theme.textPrimary
                    wrapMode: Text.WordWrap
                    lineHeight: 1.35
                }

                // Action Buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Layout.topMargin: 4

                    AppButton {
                        Layout.fillWidth: true
                        implicitHeight: 40
                        text: job.canShiftToFit ? "CANCEL / KEEP AS-IS" : "CLOSE (DISMISS)"
                        variant: "secondary"
                        onClicked: boundaryWarningModal.close()
                    }

                    AppButton {
                        visible: job.canShiftToFit
                        Layout.fillWidth: true
                        implicitHeight: 40
                        text: "⌖ SHIFT TO BED CENTER"
                        variant: "primary"
                        onClicked: {
                            job.shiftToFit()
                            boundaryWarningModal.close()
                        }
                    }
                }
            }
        }
    }

    // --- Access Validation Helper ---
    function validateCurrentViewAccess() {
        var viewKeyMap = {
            0: "motion",
            1: "laser",
            2: "job",
            3: "camera",
            4: "terminal",
            5: "setup",
            6: "settings"
        }
        var currentKey = viewKeyMap[viewStack.currentIndex]
        if (!currentKey) return
        if (currentKey === "setup") {
            if (settings.currentRole !== "Admin") {
                viewStack.currentIndex = 0
            }
            return
        }
        if (currentKey === "camera" && !settings.cameraEnabled) {
            viewStack.currentIndex = 0
            return
        }
        if (!settings.isPageAllowed(settings.currentRole, currentKey)) {
            // Find first permissible view
            var candidates = [0, 1, 2, 3, 4, 6]
            for (var i = 0; i < candidates.length; i++) {
                var idx = candidates[i]
                var k = viewKeyMap[idx]
                if (k === "camera" && !settings.cameraEnabled) continue
                if (settings.isPageAllowed(settings.currentRole, k)) {
                    viewStack.currentIndex = idx
                    return
                }
            }
            viewStack.currentIndex = 0
        }
    }

    // --- Navigation Helper for Actionable Notifications & Shortcuts ---
    function navigateToView(target, subTab) {
        if (!target) return
        var t = target.toString().toLowerCase()
        if (t === "motion" || t === "dro") {
            if (settings.isPageAllowed(settings.currentRole, "motion")) viewStack.currentIndex = 0
        } else if (t === "laser") {
            if (settings.isPageAllowed(settings.currentRole, "laser")) viewStack.currentIndex = 1
        } else if (t === "job") {
            if (settings.isPageAllowed(settings.currentRole, "job")) viewStack.currentIndex = 2
        } else if (t === "camera") {
            if (settings.cameraEnabled && settings.isPageAllowed(settings.currentRole, "camera")) viewStack.currentIndex = 3
        } else if (t === "terminal") {
            if (settings.isPageAllowed(settings.currentRole, "terminal")) {
                viewStack.currentIndex = 4
            } else if (settings.isPageAllowed(settings.currentRole, "settings")) {
                viewStack.currentIndex = 6
            }
        } else if (t === "hardware" || t === "setup") {
            if (settings.currentRole === "Admin") {
                viewStack.currentIndex = 5
            } else if (settings.isPageAllowed(settings.currentRole, "settings")) {
                viewStack.currentIndex = 6
            }
        } else if (t === "settings" || t === "serial" || t === "com") {
            if (settings.isPageAllowed(settings.currentRole, "settings")) {
                viewStack.currentIndex = 6
            }
        } else if (t === "update") {
            if (settings.isPageAllowed(settings.currentRole, "settings")) viewStack.currentIndex = 6
            updateModal.open()
        }
    }

    // Modal Dimming Backdrop & Input Blocker for Notification Center
    // Completely blocks all clicks, hovers, and wheel scrolls from reaching the backside UI
    Rectangle {
        id: notifBackdrop
        objectName: "notifBackdrop"
        visible: notifDrawer.visible
        z: 9998
        x: 0
        y: -appHeader.height
        width: window.width
        height: window.height
        color: Theme.isDark ? Qt.rgba(3/255, 7/255, 18/255, 0.45) : Qt.rgba(15/255, 23/255, 42/255, 0.25)

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
            onClicked: notifDrawer.visible = false
            onWheel: function(wheel) {
                // Completely eat all wheel scroll events so backside UI never scrolls
                wheel.accepted = true
            }
        }
    }

    // Floating Notification Center Flyout Drawer
    NotificationDrawer {
        id: notifDrawer
        objectName: "notifDrawer"
        notifBridge: notifications
        visible: false
        z: 9999
        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.right: parent.right
        anchors.rightMargin: 16
        onRequestNavigate: function(targetView) {
            window.navigateToView(targetView)
        }
    }

    // In-App Real-time Notification Toast
    NotificationToast {
        id: notifToast
        notifBridge: notifications
        z: 10000
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 20
        onRequestNavigate: function(targetView) {
            window.navigateToView(targetView)
        }
    }

    // Software Update Modal Dialog
    UpdateModal {
        id: updateModal
        objectName: "updateModal"
        z: 100005
        x: 0
        y: -appHeader.height
        width: window.width
        height: window.height
    }

    Connections {
        target: notifications
        function onNotificationAdded(notif) {
            bellShakeAnim.restart()
            notifToast.pop(notif)
        }
        function onRequestNavigate(targetView) {
            window.navigateToView(targetView)
            notifDrawer.visible = false
        }
    }

    Connections {
        target: (typeof updater !== "undefined" && updater) ? updater : null
        ignoreUnknownSignals: true
        function onUpdateCheckComplete(available, latestVersion, releaseNotes) {
            if (available && viewStack.currentIndex === 6) {
                updateModal.open()
            }
        }
    }

    Connections {
        target: serial
        function onErrorOccurred(errMsg) {
            if (!serial.connected) {
                window.navigateToView("settings")
                serial.refreshPorts()
            }
        }
    }

    Connections {
        target: settings
        function onRoleChanged() { validateCurrentViewAccess() }
        function onRolePermissionsChanged() { validateCurrentViewAccess() }
        function onCameraEnabledChanged() { validateCurrentViewAccess() }
    }
}
