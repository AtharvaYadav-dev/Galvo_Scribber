import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Flickable {
    id: root
    objectName: "hardwareSetupFlickable"
    contentWidth: width
    contentHeight: mainCol.implicitHeight + 60
    clip: true

    // Internal working copy of hardware state for user manipulation before saving
    property int workingLaserCount: settings.laserCount
    property real workingBedWidth: settings.bedWidth
    property real workingBedHeight: settings.bedHeight
    property real workingZMax: settings.zMaxTravel
    property bool workingCameraEnabled: settings.cameraEnabled
    property string workingOriginPosition: settings.originPosition
    property string workingMachineName: settings.machineName
    property var workingOperatorPages: settings.operatorPages
    property var workingSupervisorPages: settings.supervisorPages
    property var workingOperatorSettingsTabs: settings.operatorSettingsTabs
    property var workingSupervisorSettingsTabs: settings.supervisorSettingsTabs
    property string saveStatusMsg: ""
    property bool isSaveError: false

    function isPagePermitted(role, key) {
        var list = (role === "Supervisor") ? root.workingSupervisorPages : root.workingOperatorPages
        if (!list) return false
        for (var i = 0; i < list.length; i++) {
            if (list[i].toString().toLowerCase() === key.toLowerCase()) return true
        }
        return false
    }

    function togglePagePermission(role, key) {
        var isSup = (role === "Supervisor")
        var current = isSup ? (root.workingSupervisorPages ? root.workingSupervisorPages.slice() : []) : (root.workingOperatorPages ? root.workingOperatorPages.slice() : [])
        var idx = -1
        for (var i = 0; i < current.length; i++) {
            if (current[i].toString().toLowerCase() === key.toLowerCase()) {
                idx = i
                break
            }
        }
        if (idx >= 0) {
            current.splice(idx, 1)
        } else {
            current.push(key)
        }
        if (isSup) {
            root.workingSupervisorPages = current
        } else {
            root.workingOperatorPages = current
        }
        settings.saveRolePermissions(root.workingOperatorPages, root.workingSupervisorPages)
    }

    function isSettingsTabPermitted(role, key) {
        var list = (role === "Supervisor") ? root.workingSupervisorSettingsTabs : root.workingOperatorSettingsTabs
        if (!list) return false
        for (var i = 0; i < list.length; i++) {
            if (list[i].toString().toLowerCase() === key.toLowerCase()) return true
        }
        return false
    }

    function toggleSettingsTabPermission(role, key) {
        var isSup = (role === "Supervisor")
        var current = isSup ? (root.workingSupervisorSettingsTabs ? root.workingSupervisorSettingsTabs.slice() : []) : (root.workingOperatorSettingsTabs ? root.workingOperatorSettingsTabs.slice() : [])
        var idx = -1
        for (var i = 0; i < current.length; i++) {
            if (current[i].toString().toLowerCase() === key.toLowerCase()) {
                idx = i
                break
            }
        }
        if (idx >= 0) {
            current.splice(idx, 1)
        } else {
            current.push(key)
        }
        if (isSup) {
            root.workingSupervisorSettingsTabs = current
        } else {
            root.workingOperatorSettingsTabs = current
        }
        settings.saveSettingsTabPermissions(root.workingOperatorSettingsTabs, root.workingSupervisorSettingsTabs)
    }

    Connections {
        target: settings
        function onHardwareConfigChanged() {
            root.workingLaserCount = settings.laserCount
            root.workingBedWidth = settings.bedWidth
            root.workingBedHeight = settings.bedHeight
            root.workingZMax = settings.zMaxTravel
            root.workingOriginPosition = settings.originPosition
            root.workingMachineName = settings.machineName
        }
        function onCameraEnabledChanged() {
            root.workingCameraEnabled = settings.cameraEnabled
        }
        function onOriginPositionChanged() {
            root.workingOriginPosition = settings.originPosition
        }
        function onRolePermissionsChanged() {
            root.workingOperatorPages = settings.operatorPages
            root.workingSupervisorPages = settings.supervisorPages
        }
        function onSettingsPermissionsChanged() {
            root.workingOperatorSettingsTabs = settings.operatorSettingsTabs
            root.workingSupervisorSettingsTabs = settings.supervisorSettingsTabs
        }
        function onSettingsSaved(msg) {
            root.saveStatusMsg = msg
            root.isSaveError = false
            saveStatusTimer.restart()
        }
    }

    Timer {
        id: saveStatusTimer
        interval: 5000
        repeat: false
        onTriggered: root.saveStatusMsg = ""
    }

    ColumnLayout {
        id: mainCol
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 28
        spacing: 20

        // Page Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 14

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                RowLayout {
                    spacing: 12
                    Text {
                        text: "Hardware & Machine Setup"
                        font.family: "Inter"
                        font.pixelSize: 22
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }
                    Rectangle {
                        id: roleBadgeRect
                        Layout.preferredHeight: 22
                        Layout.preferredWidth: roleBadgeRow.implicitWidth + 16
                        Layout.alignment: Qt.AlignVCenter
                        radius: 11
                        color: settings.isAdmin ? Qt.rgba(0, 229/255, 255/255, 0.15) : Qt.rgba(239/255, 68/255, 68/255, 0.15)
                        border.color: settings.isAdmin ? Theme.accentCyan : Theme.accentRed
                        border.width: 1

                        RowLayout {
                            id: roleBadgeRow
                            anchors.centerIn: parent
                            spacing: 6
                            AppIcon {
                                name: settings.isAdmin ? "admin_panel_settings" : "lock"
                                size: 13
                                iconColor: settings.isAdmin ? Theme.accentCyan : Theme.accentRed
                            }
                            Text {
                                id: roleBadgeTxt
                                text: {
                                    if (settings.isAdmin) {
                                        var m = Math.floor(settings.supervisorRemainingSeconds / 60)
                                        var s = settings.supervisorRemainingSeconds % 60
                                        var timeStr = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s)
                                        return "ADMIN SUPERUSER MODE (" + timeStr + ")"
                                    }
                                    return "ACCESS RESTRICTED"
                                }
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: settings.isAdmin ? Theme.accentCyan : Theme.accentRed
                            }
                        }
                    }
                }

                Text {
                    text: "Configure laser architecture, working bed dimensions, Z-axis motion ceiling, and camera system integration."
                    font.family: "Inter"
                    font.pixelSize: 12
                    color: Theme.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            Text {
                text: settings.machineName.toUpperCase() + "  /  SETUP"
                font.family: "IBM Plex Mono"
                font.pixelSize: 10
                font.weight: Font.DemiBold
                color: Theme.textMuted
                Layout.alignment: Qt.AlignTop
            }
        }

        // --- View State A: Restricted View when NOT Admin ---
        MetricCard {
            Layout.fillWidth: true
            visible: !settings.isAdmin
            title: "Administrator Authentication Required"
            subtitle: "Security Clearance Check"
            accentColor: Theme.accentRed

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 16

                RowLayout {
                    spacing: 14
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 8
                        color: Theme.isDark ? "#2D1215" : "#FEE2E2"
                        border.color: Theme.accentRed
                        border.width: 1
                        AppIcon { anchors.centerIn: parent; name: "lock"; size: 24; iconColor: Theme.accentRed }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3
                        Text {
                            text: "Machine Hardware Configuration is Restricted"
                            font.family: "Inter"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "Changing laser count, bed size boundaries, or disabling vision systems alters machine safety parameters.\nPlease authenticate as Admin to proceed."
                            font.family: "Inter"
                            font.pixelSize: 12
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            spacing: 8
                            Layout.topMargin: 4
                            Rectangle {
                                height: 24
                                radius: 12
                                color: Theme.isDark ? "#1E293B" : "#F1F5F9"
                                border.color: Theme.borderCard
                                border.width: 1
                                implicitWidth: currMachRow.implicitWidth + 16

                                RowLayout {
                                    id: currMachRow
                                    anchors.centerIn: parent
                                    spacing: 6
                                    AppIcon { name: "badge"; size: 14; iconColor: Theme.accentCyan }
                                    Text {
                                        text: "Configured Machine: " + settings.machineName
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: Theme.accentCyan
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.borderCard
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Text {
                            text: "Admin Security Key / Password"
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 38
                            radius: 6
                            color: Theme.bgInput
                            border.color: adminPwdInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                            border.width: 1

                            property bool showPassword: false

                            TextInput {
                                id: adminPwdInput
                                anchors.left: parent.left
                                anchors.right: adminEyeToggleBtn.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 12
                                anchors.rightMargin: 6
                                verticalAlignment: TextInput.AlignVCenter
                                echoMode: parent.showPassword ? TextInput.Normal : TextInput.Password
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 14
                                color: Theme.textPrimary
                                onAccepted: {
                                    if (text.length > 0) {
                                        settings.login("Admin", text)
                                        text = ""
                                    }
                                }
                            }

                            Rectangle {
                                id: adminEyeToggleBtn
                                anchors.right: parent.right
                                anchors.rightMargin: 6
                                anchors.verticalCenter: parent.verticalCenter
                                width: 26
                                height: 26
                                radius: 4
                                color: adminEyeMouseArea.containsMouse ? (Theme.isDark ? "#2A2D3A" : "#E2E8F0") : "transparent"

                                AppIcon {
                                    anchors.centerIn: parent
                                    name: parent.parent.showPassword ? "visibility_off" : "visibility"
                                    size: 16
                                    iconColor: adminEyeMouseArea.containsMouse ? Theme.accentCyan : Theme.textSecondary
                                }

                                MouseArea {
                                    id: adminEyeMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: parent.parent.showPassword = !parent.parent.showPassword
                                }
                            }
                        }
                    }

                    AppButton {
                        Layout.alignment: Qt.AlignBottom
                        Layout.preferredWidth: 200
                        implicitHeight: 38
                        iconName: "lock_open"
                        text: "Unlock Admin Controls"
                        variant: "primary"
                        onClicked: {
                            if (adminPwdInput.text.length > 0) {
                                settings.login("Admin", adminPwdInput.text)
                                adminPwdInput.text = ""
                            }
                        }
                    }
                }
            }
        }

        // --- View State B: Full Hardware Setup Suite when Admin ---
        ColumnLayout {
            Layout.fillWidth: true
            visible: settings.isAdmin
            spacing: 20

            // Card 0: Machine Designation & Name Configuration
            MetricCard {
                Layout.fillWidth: true
                title: "Machine Designation & System Name"
                subtitle: "System model name written directly to config.ini [hardware] machine_name"
                accentColor: Theme.accentCyan

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 8
                        color: Theme.isDark ? "#0E2A38" : "#E0F2FE"
                        border.color: Theme.accentCyan
                        border.width: 1
                        AppIcon { anchors.centerIn: parent; name: "badge"; size: 22; iconColor: Theme.accentCyan }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4

                        RowLayout {
                            spacing: 8
                            Text {
                                text: "SYSTEM MACHINE NAME"
                                font.family: "Inter"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                            }
                            Text {
                                text: "• config.ini [hardware] machine_name"
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 10
                                color: Theme.textMuted
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 38
                            radius: 6
                            color: Theme.bgInput
                            border.color: topMachineNameInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                            border.width: 1

                            TextInput {
                                id: topMachineNameInput
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                verticalAlignment: TextInput.AlignVCenter
                                font.family: "IBM Plex Mono"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                                text: root.workingMachineName
                                selectByMouse: true
                                onTextChanged: {
                                    if (text !== root.workingMachineName) {
                                        root.workingMachineName = text
                                    }
                                }
                                onAccepted: {
                                    if (text.trim().length > 0) {
                                        settings.saveMachineName(text.trim())
                                    }
                                }
                            }
                        }

                        Text {
                            text: "Updates window title, header breadcrumbs, reports, and config.ini [hardware] machine_name in real-time."
                            font.family: "Inter"
                            font.pixelSize: 11
                            color: Theme.textMuted
                        }
                    }

                    AppButton {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 160
                        implicitHeight: 38
                        iconName: "save"
                        text: "Apply Name"
                        variant: "primary"
                        onClicked: {
                            if (topMachineNameInput.text.trim().length > 0) {
                                settings.saveMachineName(topMachineNameInput.text.trim())
                            }
                        }
                    }
                }
            }

            // Grid Row 1: Laser Setup & Vision Setup
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Card 1: Laser Configuration
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    title: "Laser Configuration"
                    subtitle: "Active optical heads & firing channels"
                    accentColor: Theme.accentAmber

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        Text {
                            text: "SELECT MACHINE LASER ARCHITECTURE:"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Rectangle {
                                Layout.fillWidth: true
                                height: 50
                                radius: 8
                                color: root.workingLaserCount === 1 ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                border.color: root.workingLaserCount === 1 ? Theme.accentCyan : Theme.borderInput
                                border.width: root.workingLaserCount === 1 ? 1.5 : 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8
                                    AppIcon { name: "flash_on"; size: 18; iconColor: Theme.accentAmber }
                                    ColumnLayout {
                                        spacing: 1
                                        Text {
                                            text: "Single Laser (1 Laser)"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: root.workingLaserCount === 1 ? "#FFFFFF" : Theme.textPrimary
                                        }
                                        Text {
                                            text: "Laser 1 only · Direct focus"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: root.workingLaserCount === 1 ? "#CBD5E1" : Theme.textSecondary
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.workingLaserCount = 1
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 50
                                radius: 8
                                color: root.workingLaserCount === 2 ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                border.color: root.workingLaserCount === 2 ? Theme.accentCyan : Theme.borderInput
                                border.width: root.workingLaserCount === 2 ? 1.5 : 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8
                                    RowLayout {
                                        spacing: 1
                                        AppIcon { name: "flash_on"; size: 16; iconColor: Theme.accentAmber }
                                        AppIcon { name: "flash_on"; size: 16; iconColor: Theme.accentAmber }
                                    }
                                    ColumnLayout {
                                        spacing: 1
                                        Text {
                                            text: "Dual Laser (2 Lasers)"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: root.workingLaserCount === 2 ? "#FFFFFF" : Theme.textPrimary
                                        }
                                        Text {
                                            text: "Laser 1 + Laser 2 · Dual channel"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: root.workingLaserCount === 2 ? "#CBD5E1" : Theme.textSecondary
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.workingLaserCount = 2
                                }
                            }
                        }

                        // Explanation Callout
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: expCol.implicitHeight + 16
                            radius: 6
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            ColumnLayout {
                                id: expCol
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 4

                                RowLayout {
                                    spacing: 6
                                    Text { text: "ℹ️"; font.pixelSize: 12 }
                                    Text {
                                        text: root.workingLaserCount === 1
                                            ? "Single Laser Mode Active"
                                            : "Dual Laser Mode Active"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.accentAmber
                                    }
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: root.workingLaserCount === 1
                                        ? "Laser 2 controls, dual optical calibration, and laser selectors are automatically hidden throughout the UI. The machine operates exclusively using Laser 1."
                                        : "Both Laser 1 and Laser 2 are available with independent focus calibration, dual-laser optical offset alignment, and multi-laser job selection."
                                    font.family: "Inter"
                                    font.pixelSize: 11
                                    color: Theme.textSecondary
                                    wrapMode: Text.WordWrap
                                    lineHeight: 1.3
                                }
                            }
                        }
                    }
                }

                // Card 2: Camera Vision System
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    title: "Camera & Vision Module"
                    subtitle: "Top-down optical inspection & crosshair alignment"
                    accentColor: Theme.accentCyan

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        Text {
                            text: "CAMERA SYSTEM INTEGRATION:"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Rectangle {
                                Layout.fillWidth: true
                                height: 50
                                radius: 8
                                color: root.workingCameraEnabled ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                border.color: root.workingCameraEnabled ? Theme.accentCyan : Theme.borderInput
                                border.width: root.workingCameraEnabled ? 1.5 : 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8
                                    AppIcon { name: "videocam"; size: 18; iconColor: Theme.accentCyan }
                                    ColumnLayout {
                                        spacing: 1
                                        Text { text: "Camera Enabled"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: root.workingCameraEnabled ? "#FFFFFF" : Theme.textPrimary
                                        }
                                        Text {
                                            text: "Show Vision tab & inspection"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: root.workingCameraEnabled ? "#CBD5E1" : Theme.textSecondary
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.workingCameraEnabled = true
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 50
                                radius: 8
                                color: !root.workingCameraEnabled ? (Theme.isDark ? "#1E293B" : "#192D78") : Theme.btnSecondaryBg
                                border.color: !root.workingCameraEnabled ? Theme.accentCyan : Theme.borderInput
                                border.width: !root.workingCameraEnabled ? 1.5 : 1

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 8
                                    AppIcon { name: "block"; size: 18; iconColor: Theme.accentRed }
                                    ColumnLayout {
                                        spacing: 1
                                        Text {
                                            text: "Camera Disabled"
                                            font.family: "Inter"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: !root.workingCameraEnabled ? "#FFFFFF" : Theme.textPrimary
                                        }
                                        Text {
                                            text: "Hide Camera Vision tab"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: !root.workingCameraEnabled ? "#CBD5E1" : Theme.textSecondary
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.workingCameraEnabled = false
                                }
                            }
                        }

                        // Explanation Callout
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: camExpCol.implicitHeight + 16
                            radius: 6
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            ColumnLayout {
                                id: camExpCol
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 4

                                RowLayout {
                                    spacing: 6
                                    AppIcon { name: "photo_camera"; size: 14; iconColor: Theme.accentCyan }
                                    Text {
                                        text: root.workingCameraEnabled ? "Vision Features Active" : "Vision Features Hidden"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.accentCyan
                                    }
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: root.workingCameraEnabled
                                        ? "Camera Vision tab is visible in the main navigation sidebar. Camera inspection routines and optical crosshair offsets are active."
                                        : "The Camera Vision tab is completely removed from the sidebar navigation. The UI automatically streamlines for production without an optical camera."
                                    font.family: "Inter"
                                    font.pixelSize: 11
                                    color: Theme.textSecondary
                                    wrapMode: Text.WordWrap
                                    lineHeight: 1.3
                                }
                            }
                        }
                    }
                }
            }

            // Grid Row 2: Bed Dimensions & Z Travel Limits
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Card 3: Machine Bed Envelope
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    title: "Machine Bed Dimensions"
                    subtitle: "Physical working envelope & boundary limits"
                    accentColor: Theme.accentGreen

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        Text {
                            text: "QUICK ENVELOPE PRESETS:"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Repeater {
                                model: [
                                    { label: "100 × 100 mm", w: 100.0, h: 100.0 },
                                    { label: "150 × 150 mm", w: 150.0, h: 150.0 },
                                    { label: "200 × 200 mm", w: 200.0, h: 200.0 },
                                    { label: "300 × 300 mm", w: 300.0, h: 300.0 }
                                ]

                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    height: 32
                                    radius: 6
                                    color: (root.workingBedWidth === modelData.w && root.workingBedHeight === modelData.h)
                                        ? (Theme.isDark ? "#1E293B" : "#192D78")
                                        : Theme.btnSecondaryBg
                                    border.color: (root.workingBedWidth === modelData.w && root.workingBedHeight === modelData.h)
                                        ? Theme.accentGreen
                                        : Theme.borderInput
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.label
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: (root.workingBedWidth === modelData.w && root.workingBedHeight === modelData.h)
                                            ? "#FFFFFF"
                                            : Theme.textPrimary
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.workingBedWidth = modelData.w
                                            root.workingBedHeight = modelData.h
                                            bedWInput.text = modelData.w.toFixed(1)
                                            bedHInput.text = modelData.h.toFixed(1)
                                        }
                                    }
                                }
                            }
                        }

                        // Custom Numeric Dimensions Input
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Bed Width (X Axis)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 36
                                    radius: 6
                                    color: Theme.bgInput
                                    border.color: bedWInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        TextInput {
                                            id: bedWInput
                                            Layout.fillWidth: true
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: root.workingBedWidth.toFixed(1)
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 13
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var v = parseFloat(text)
                                                if (!isNaN(v) && v >= 20.0 && v <= 1000.0) root.workingBedWidth = v
                                            }
                                        }
                                        Text { text: "mm"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Bed Height (Y Axis)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 36
                                    radius: 6
                                    color: Theme.bgInput
                                    border.color: bedHInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        TextInput {
                                            id: bedHInput
                                            Layout.fillWidth: true
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: root.workingBedHeight.toFixed(1)
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 13
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var v = parseFloat(text)
                                                if (!isNaN(v) && v >= 20.0 && v <= 1000.0) root.workingBedHeight = v
                                            }
                                        }
                                        Text { text: "mm"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    }
                                }
                            }
                        }

                        // Bed Info Readout Box with Machine Designation & Area
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: bedInfoCol.implicitHeight + 18
                            radius: 6
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            ColumnLayout {
                                id: bedInfoCol
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 6

                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: "Machine Designation / Name:"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: Theme.textSecondary
                                    }
                                    Item { Layout.fillWidth: true }
                                    Rectangle {
                                        Layout.preferredWidth: 220
                                        height: 28
                                        radius: 4
                                        color: Theme.bgInput
                                        border.color: machineNameInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                        border.width: 1

                                        TextInput {
                                            id: machineNameInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 8
                                            anchors.rightMargin: 8
                                            verticalAlignment: TextInput.AlignVCenter
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: Theme.accentCyan
                                            text: root.workingMachineName
                                            onTextChanged: {
                                                if (text !== root.workingMachineName) {
                                                    root.workingMachineName = text
                                                }
                                            }
                                        }
                                    }
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                                RowLayout {
                                    Layout.fillWidth: true
                                    Text {
                                        text: "Total Working Bed Area:"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        color: Theme.textSecondary
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: ((root.workingBedWidth * root.workingBedHeight) / 100.0).toFixed(1) + " cm² (" + root.workingBedWidth.toFixed(0) + " × " + root.workingBedHeight.toFixed(0) + " mm)"
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.accentGreen
                                    }
                                }
                            }
                        }
                    }
                }

                // Card 4: Z-Axis Travel & Ceiling
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    title: "Z-Axis Motion Limits"
                    subtitle: "Vertical safety travel ceiling & focal bounds"
                    accentColor: Theme.accentBlue

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 14

                        Text {
                            text: "Z-AXIS TRAVEL SAFETY CEILING:"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Maximum Travel Distance"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 36
                                    radius: 6
                                    color: Theme.bgInput
                                    border.color: zMaxInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        TextInput {
                                            id: zMaxInput
                                            Layout.fillWidth: true
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: root.workingZMax.toFixed(1)
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 13
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var v = parseFloat(text)
                                                if (!isNaN(v) && v >= 5.0 && v <= 100.0) {
                                                    root.workingZMax = v
                                                    zSlider.value = v
                                                }
                                            }
                                        }
                                        Text { text: "mm"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Calculated Z Center Datum"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 36
                                    radius: 6
                                    color: Theme.isDark ? "#111827" : "#F8FAFC"
                                    border.color: Theme.borderCard
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        Text {
                                            text: "Z = " + (root.workingZMax / 2.0).toFixed(1) + " mm"
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            font.weight: Font.DemiBold
                                            color: Theme.accentAmber
                                        }
                                    }
                                }
                            }
                        }

                        // Slider Control for tactile tuning
                        SliderControl {
                            id: zSlider
                            Layout.fillWidth: true
                            label: "Z Travel Range (5.0 to 50.0 mm)"
                            from: 5.0
                            to: 50.0
                            stepSize: 0.5
                            value: root.workingZMax
                            onValueModified: function(newVal) {
                                root.workingZMax = newVal
                                zMaxInput.text = newVal.toFixed(1)
                            }
                        }

                        // Safety note
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: zNoteCol.implicitHeight + 14
                            radius: 6
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            ColumnLayout {
                                id: zNoteCol
                                anchors.fill: parent
                                anchors.margins: 10
                                RowLayout {
                                    spacing: 6
                                    AppIcon { name: "warning"; size: 14; iconColor: Theme.accentAmber }
                                    Text {
                                        text: "Machine Physical Protection"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.accentAmber
                                    }
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: "Jogging in Z+ direction is hardware-clamped to this ceiling to prevent mechanical overtravel and protect optical focus heads."
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    color: Theme.textSecondary
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }
            }

            // Grid Row 3: Axis Origin & Homing Position Corner (0,0)
            MetricCard {
                Layout.fillWidth: true
                title: "Machine Axis Origin & Homing Position"
                subtitle: "Physical (0,0) machine coordinate datum corner & visual preview orientation"
                accentColor: Theme.accentAmber

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 24

                    // Left Column: 2x2 Corner Selection Tiles
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 3
                        spacing: 12

                        Text {
                            text: "SELECT MACHINE (0,0) DATUM CORNER:"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 10
                            columnSpacing: 10

                            Repeater {
                                model: [
                                    {
                                        id: "top-left",
                                        title: "Top-Left (0,0)",
                                        sub: "+X Right, +Y Down",
                                        badge: "Display standard"
                                    },
                                    {
                                        id: "top-right",
                                        title: "Top-Right (0,0)",
                                        sub: "+X Left, +Y Down",
                                        badge: "Scriber Machine"
                                    },
                                    {
                                        id: "bottom-left",
                                        title: "Bottom-Left (0,0)",
                                        sub: "+X Right, +Y Up",
                                        badge: "Cartesian graph"
                                    },
                                    {
                                        id: "bottom-right",
                                        title: "Bottom-Right (0,0)",
                                        sub: "+X Left, +Y Up",
                                        badge: "Inverted standard"
                                    }
                                ]

                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    height: 56
                                    radius: 8
                                    color: (root.workingOriginPosition === modelData.id)
                                        ? (Theme.isDark ? "#1E293B" : "#192D78")
                                        : Theme.bgInput
                                    border.color: (root.workingOriginPosition === modelData.id)
                                        ? Theme.accentAmber
                                        : Theme.borderInput
                                    border.width: (root.workingOriginPosition === modelData.id) ? 2 : 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 10

                                        Rectangle {
                                            width: 14
                                            height: 14
                                            radius: 7
                                            color: (root.workingOriginPosition === modelData.id) ? Theme.accentAmber : "transparent"
                                            border.color: (root.workingOriginPosition === modelData.id) ? Theme.accentAmber : Theme.textMuted
                                            border.width: 1.5

                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 6
                                                height: 6
                                                radius: 3
                                                color: (root.workingOriginPosition === modelData.id) ? "#FFFFFF" : "transparent"
                                            }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 2

                                            RowLayout {
                                                spacing: 6
                                                Text {
                                                    text: modelData.title
                                                    font.family: "Inter"
                                                    font.pixelSize: 12
                                                    font.weight: Font.Bold
                                                    color: (root.workingOriginPosition === modelData.id) ? "#FFFFFF" : Theme.textPrimary
                                                }
                                                Rectangle {
                                                    height: 16
                                                    implicitWidth: badgeTxt.implicitWidth + 8
                                                    radius: 3
                                                    color: (root.workingOriginPosition === modelData.id) ? Qt.rgba(214/255, 175/255, 62/255, 0.25) : Theme.bgCard
                                                    Text {
                                                        id: badgeTxt
                                                        anchors.centerIn: parent
                                                        text: modelData.badge
                                                        font.family: "Inter"
                                                        font.pixelSize: 9
                                                        font.weight: Font.DemiBold
                                                        color: (root.workingOriginPosition === modelData.id) ? Theme.accentAmber : Theme.textSecondary
                                                    }
                                                }
                                            }

                                            Text {
                                                text: modelData.sub
                                                font.family: "IBM Plex Mono"
                                                font.pixelSize: 10
                                                color: (root.workingOriginPosition === modelData.id) ? "#DCE2EC" : Theme.textSecondary
                                            }
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.workingOriginPosition = modelData.id
                                    }
                                }
                            }
                        }

                        // Explanatory Note
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: originNoteCol.implicitHeight + 14
                            radius: 6
                            color: Theme.isDark ? "#111827" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1

                            ColumnLayout {
                                id: originNoteCol
                                anchors.fill: parent
                                anchors.margins: 10
                                RowLayout {
                                    spacing: 6
                                    AppIcon { name: "info"; size: 14; iconColor: Theme.accentAmber }
                                    Text {
                                        text: "Machine Optical Alignment View"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.accentAmber
                                    }
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: root.workingOriginPosition === "top-right"
                                        ? "Active setting: (0,0) is at the Top-Right corner. This exactly matches your machine's physical homing limit switches and gantry layout. 2D Bed Workspace, reticle tracking, and Job toolpaths orient from this viewpoint."
                                        : "Axis (0,0) starting origin will orient to " + root.workingOriginPosition.toUpperCase() + ". 2D Bed Workspace and Job Blueprint will automatically update coordinate perspectives to match."
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    color: Theme.textSecondary
                                    wrapMode: Text.WordWrap
                                    lineHeight: 1.3
                                }
                            }
                        }
                    }

                    // Right Column: Live Interactive Schematic Bed Diagram
                    Rectangle {
                        id: schematicBed
                        width: 200
                        height: 200
                        implicitWidth: 200
                        implicitHeight: 200
                        Layout.preferredWidth: 200
                        Layout.preferredHeight: 200
                        Layout.alignment: Qt.AlignVCenter
                        radius: 8
                        color: Theme.isDark ? "#060A14" : "#0F172A"
                        border.color: Theme.accentAmber
                        border.width: 1.5
                        clip: true

                        readonly property bool isRight: (root.workingOriginPosition === "top-right" || root.workingOriginPosition === "bottom-right")
                        readonly property bool isTop: (root.workingOriginPosition === "top-right" || root.workingOriginPosition === "top-left")

                        // Grid lines
                        Repeater {
                            model: [0.25, 0.50, 0.75]
                            Rectangle {
                                x: Math.round(schematicBed.width * modelData)
                                y: 0
                                width: 1
                                height: schematicBed.height
                                color: Theme.isDark ? "#1E293B" : "#334155"
                            }
                        }
                        Repeater {
                            model: [0.25, 0.50, 0.75]
                            Rectangle {
                                x: 0
                                y: Math.round(schematicBed.height * modelData)
                                width: schematicBed.width
                                height: 1
                                color: Theme.isDark ? "#1E293B" : "#334155"
                            }
                        }

                        // Center Datum Dot
                        Rectangle {
                            width: 6
                            height: 6
                            radius: 3
                            anchors.centerIn: parent
                            color: Theme.accentAmber
                        }

                        // Glowing Origin Marker (0,0) at selected corner
                        Rectangle {
                            id: schemOriginMarker
                            width: 22
                            height: 22
                            radius: 11
                            color: Qt.rgba(52/255, 211/255, 153/255, 0.25)
                            border.color: Theme.accentGreen
                            border.width: 1.5

                            x: schematicBed.isRight ? (schematicBed.width - width - 10) : 10
                            y: schematicBed.isTop ? 10 : (schematicBed.height - height - 10)

                            Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }
                            Behavior on y { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }

                            Rectangle {
                                anchors.centerIn: parent
                                width: 8
                                height: 8
                                radius: 4
                                color: Theme.accentGreen
                            }
                        }

                        // Origin Corner Text Badge
                        Text {
                            text: "(0,0)"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.accentGreen

                            x: schematicBed.isRight ? (schematicBed.width - width - 36) : 36
                            y: schematicBed.isTop ? 12 : (schematicBed.height - height - 12)

                            Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }
                            Behavior on y { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }
                        }

                        // Max Bed Corner Text Badge
                        Text {
                            text: root.workingBedWidth.toFixed(0) + "×" + root.workingBedHeight.toFixed(0)
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: "#64748B"

                            x: schematicBed.isRight ? 10 : (schematicBed.width - width - 10)
                            y: schematicBed.isTop ? (schematicBed.height - height - 10) : 10

                            Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }
                            Behavior on y { NumberAnimation { duration: 180; easing.type: Easing.OutQuad } }
                        }
                    }
                }
            }

            // Role-Based Page Access Permissions Configuration Card
            MetricCard {
                Layout.fillWidth: true
                title: "Role-Based Page Visibility Permissions"
                subtitle: "Control which workspace views are visible in sidebar navigation for Operator and Supervisor roles"
                accentColor: Theme.accentCyan

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 18

                    // Info Header
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Rectangle {
                            width: 38
                            height: 38
                            radius: 8
                            color: Theme.isDark ? "#0E2A38" : "#E0F2FE"
                            border.color: Theme.accentCyan
                            border.width: 1
                            AppIcon { anchors.centerIn: parent; name: "manage_accounts"; size: 20; iconColor: Theme.accentCyan }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                text: "Access Control Matrix (RBAC)"
                                font.family: "Inter"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            Text {
                                text: "Configure visible sidebar tabs for shopfloor operators and elevated supervisors. Changes apply in real-time."
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                            }
                        }
                    }

                    // 2-Column Grid: Operator on Left, Supervisor on Right
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        // --- COLUMN 1: OPERATOR ROLE ---
                        Rectangle {
                            Layout.fillWidth: true
                            radius: 10
                            color: Theme.isDark ? "#0A101E" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1
                            implicitHeight: opCol.implicitHeight + 28

                            ColumnLayout {
                                id: opCol
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: Theme.isDark ? "#172338" : "#E2E8F0"
                                        AppIcon { anchors.centerIn: parent; name: "person"; size: 14; iconColor: Theme.pillRoleText }
                                    }
                                    ColumnLayout {
                                        spacing: 1
                                        Text { text: "OPERATOR CLEARANCE"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.textPrimary }
                                        Text { text: "Default active shopfloor operator mode"; font.family: "Inter"; font.pixelSize: 9; color: Theme.textMuted }
                                    }
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                                Repeater {
                                    model: [
                                        { key: "motion", label: "Motion & DRO", icon: "tune", desc: "Coordinates & manual stage jogging" },
                                        { key: "laser", label: "Laser Control", icon: "flash_on", desc: "Laser spot focus & optical offsets" },
                                        { key: "job", label: "Job & Run", icon: "folder_open", desc: "DXF/G-Code preview & job execution" },
                                        { key: "camera", label: "Camera Vision", icon: "videocam", desc: "Live video targeting & optical alignment" },
                                        { key: "terminal", label: "Terminal", icon: "terminal", desc: "Raw G-Code terminal console" },
                                        { key: "settings", label: "Settings", icon: "settings", desc: "Speeds, theme & role switching" }
                                    ]

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 44
                                        radius: 6
                                        color: opItemMa.containsMouse ? (Theme.isDark ? "#131C2E" : "#F1F5F9") : "transparent"
                                        border.color: opItemMa.containsMouse ? Theme.borderCard : "transparent"
                                        border.width: 1

                                        readonly property bool isAllowed: root.isPagePermitted("Operator", modelData.key)

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 8
                                            anchors.rightMargin: 8
                                            spacing: 10

                                            AppIcon {
                                                name: modelData.icon
                                                size: 16
                                                iconColor: isAllowed ? Theme.accentCyan : Theme.textMuted
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1
                                                Text {
                                                    text: modelData.label
                                                    font.family: "Inter"
                                                    font.pixelSize: 11
                                                    font.weight: Font.DemiBold
                                                    color: isAllowed ? Theme.textPrimary : Theme.textMuted
                                                }
                                                Text {
                                                    text: modelData.desc
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    color: Theme.textMuted
                                                    elide: Text.ElideRight
                                                    Layout.fillWidth: true
                                                }
                                            }

                                            // iOS-style Toggle Switch
                                            Rectangle {
                                                width: 36
                                                height: 20
                                                radius: 10
                                                color: isAllowed ? Theme.accentCyan : (Theme.isDark ? "#334155" : "#CBD5E1")
                                                Behavior on color { ColorAnimation { duration: 150 } }

                                                Rectangle {
                                                    width: 14
                                                    height: 14
                                                    radius: 7
                                                    color: "#FFFFFF"
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    x: isAllowed ? (parent.width - width - 3) : 3
                                                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: opItemMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.togglePagePermission("Operator", modelData.key)
                                        }
                                    }
                                }
                            }
                        }

                        // --- COLUMN 2: SUPERVISOR ROLE ---
                        Rectangle {
                            Layout.fillWidth: true
                            radius: 10
                            color: Theme.isDark ? "#0A101E" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1
                            implicitHeight: supCol.implicitHeight + 28

                            ColumnLayout {
                                id: supCol
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: Theme.isDark ? "#2D2211" : "#FEF3C7"
                                        AppIcon { anchors.centerIn: parent; name: "timer"; size: 14; iconColor: Theme.accentAmber }
                                    }
                                    ColumnLayout {
                                        spacing: 1
                                        Text { text: "SUPERVISOR CLEARANCE"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                                        Text { text: "10-minute temporary elevated clearance mode"; font.family: "Inter"; font.pixelSize: 9; color: Theme.textMuted }
                                    }
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                                Repeater {
                                    model: [
                                        { key: "motion", label: "Motion & DRO", icon: "tune", desc: "Coordinates & manual stage jogging" },
                                        { key: "laser", label: "Laser Control", icon: "flash_on", desc: "Laser spot focus & optical offsets" },
                                        { key: "job", label: "Job & Run", icon: "folder_open", desc: "DXF/G-Code preview & job execution" },
                                        { key: "camera", label: "Camera Vision", icon: "videocam", desc: "Live video targeting & optical alignment" },
                                        { key: "terminal", label: "Terminal", icon: "terminal", desc: "Raw G-Code terminal console" },
                                        { key: "settings", label: "Settings", icon: "settings", desc: "Speeds, theme & role switching" }
                                    ]

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 44
                                        radius: 6
                                        color: supItemMa.containsMouse ? (Theme.isDark ? "#131C2E" : "#F1F5F9") : "transparent"
                                        border.color: supItemMa.containsMouse ? Theme.borderCard : "transparent"
                                        border.width: 1

                                        readonly property bool isAllowed: root.isPagePermitted("Supervisor", modelData.key)

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 8
                                            anchors.rightMargin: 8
                                            spacing: 10

                                            AppIcon {
                                                name: modelData.icon
                                                size: 16
                                                iconColor: isAllowed ? Theme.accentAmber : Theme.textMuted
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1
                                                Text {
                                                    text: modelData.label
                                                    font.family: "Inter"
                                                    font.pixelSize: 11
                                                    font.weight: Font.DemiBold
                                                    color: isAllowed ? Theme.textPrimary : Theme.textMuted
                                                }
                                                Text {
                                                    text: modelData.desc
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    color: Theme.textMuted
                                                    elide: Text.ElideRight
                                                    Layout.fillWidth: true
                                                }
                                            }

                                            // iOS-style Toggle Switch
                                            Rectangle {
                                                width: 36
                                                height: 20
                                                radius: 10
                                                color: isAllowed ? Theme.accentAmber : (Theme.isDark ? "#334155" : "#CBD5E1")
                                                Behavior on color { ColorAnimation { duration: 150 } }

                                                Rectangle {
                                                    width: 14
                                                    height: 14
                                                    radius: 7
                                                    color: "#FFFFFF"
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    x: isAllowed ? (parent.width - width - 3) : 3
                                                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: supItemMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.togglePagePermission("Supervisor", modelData.key)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Admin Clearance Notice
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 8
                        color: Theme.isDark ? "#111827" : "#F1F5F9"
                        border.color: Theme.borderCard
                        border.width: 1
                        implicitHeight: adminNoteRow.implicitHeight + 20

                        RowLayout {
                            id: adminNoteRow
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 12
                            AppIcon { name: "admin_panel_settings"; size: 20; iconColor: Theme.accentCyan }
                            Text {
                                Layout.fillWidth: true
                                text: "<b>Administrator Superuser Access:</b> The Admin role always maintains unrestricted access to all pages and controls. Machine Setup remains exclusively accessible to Admin."
                                textFormat: Text.RichText
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                                wrapMode: Text.WordWrap
                                lineHeight: 1.3
                            }
                        }
                    }
                }
            }

            // Role-Based Settings Tabs Permissions Configuration Card
            MetricCard {
                Layout.fillWidth: true
                title: "Settings Tabs Access Control Matrix"
                subtitle: "Control which functional sections inside the Settings page are visible for Operator and Supervisor roles"
                accentColor: Theme.accentAmber

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 18

                    // Info Header
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Rectangle {
                            width: 38
                            height: 38
                            radius: 8
                            color: Theme.isDark ? "#2D2211" : "#FEF3C7"
                            border.color: Theme.accentAmber
                            border.width: 1
                            AppIcon { anchors.centerIn: parent; name: "tune"; size: 20; iconColor: Theme.accentAmber }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                text: "Settings Sub-Tab Permissions"
                                font.family: "Inter"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            Text {
                                text: "Selectively expose or restrict individual settings sections. Unauthorized sections are hidden from the Settings page."
                                font.family: "Inter"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                            }
                        }
                    }

                    // 2-Column Grid: Operator on Left, Supervisor on Right
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        // --- COLUMN 1: OPERATOR ROLE ---
                        Rectangle {
                            Layout.fillWidth: true
                            radius: 10
                            color: Theme.isDark ? "#0A101E" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1
                            implicitHeight: opSetCol.implicitHeight + 28

                            ColumnLayout {
                                id: opSetCol
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: Theme.isDark ? "#172338" : "#E2E8F0"
                                        AppIcon { anchors.centerIn: parent; name: "person"; size: 14; iconColor: Theme.pillRoleText }
                                    }
                                    ColumnLayout {
                                        spacing: 1
                                        Text { text: "OPERATOR SETTINGS TABS"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.textPrimary }
                                        Text { text: "Visible tabs when logged in as Operator"; font.family: "Inter"; font.pixelSize: 9; color: Theme.textMuted }
                                    }
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                                Repeater {
                                    model: [
                                        { key: "profile", label: "User Profile & Access", icon: "person", desc: "PIN login/logout, active role timer & theme toggle" },
                                        { key: "serial", label: "Serial Hardware", icon: "cable", desc: "Controller COM port selection & baudrate connection" },
                                        { key: "feeds", label: "Motion Feeds", icon: "speed", desc: "Stage jog feed & laser scribing feed rates (mm/min)" },
                                        { key: "origin", label: "Print Origin & Bed", icon: "gps_fixed", desc: "X/Y index starting datum & mini bed canvas preview" },
                                        { key: "camera_offset", label: "Camera Offsets", icon: "videocam", desc: "Laser 1 & 2 optical camera calibration & speeds" },
                                        { key: "system", label: "System & Updates", icon: "info", desc: "Software version, update checker & company information" }
                                    ]

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 44
                                        radius: 6
                                        color: opSetItemMa.containsMouse ? (Theme.isDark ? "#131C2E" : "#F1F5F9") : "transparent"
                                        border.color: opSetItemMa.containsMouse ? Theme.borderCard : "transparent"
                                        border.width: 1

                                        readonly property bool isAllowed: root.isSettingsTabPermitted("Operator", modelData.key)

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 8
                                            anchors.rightMargin: 8
                                            spacing: 10

                                            AppIcon {
                                                name: modelData.icon
                                                size: 16
                                                iconColor: isAllowed ? Theme.accentCyan : Theme.textMuted
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1
                                                Text {
                                                    text: modelData.label
                                                    font.family: "Inter"
                                                    font.pixelSize: 11
                                                    font.weight: Font.DemiBold
                                                    color: isAllowed ? Theme.textPrimary : Theme.textMuted
                                                }
                                                Text {
                                                    text: modelData.desc
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    color: Theme.textMuted
                                                    elide: Text.ElideRight
                                                    Layout.fillWidth: true
                                                }
                                            }

                                            // iOS-style Toggle Switch
                                            Rectangle {
                                                width: 36
                                                height: 20
                                                radius: 10
                                                color: isAllowed ? Theme.accentCyan : (Theme.isDark ? "#334155" : "#CBD5E1")
                                                Behavior on color { ColorAnimation { duration: 150 } }

                                                Rectangle {
                                                    width: 14
                                                    height: 14
                                                    radius: 7
                                                    color: "#FFFFFF"
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    x: isAllowed ? (parent.width - width - 3) : 3
                                                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: opSetItemMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.toggleSettingsTabPermission("Operator", modelData.key)
                                        }
                                    }
                                }
                            }
                        }

                        // --- COLUMN 2: SUPERVISOR ROLE ---
                        Rectangle {
                            Layout.fillWidth: true
                            radius: 10
                            color: Theme.isDark ? "#0A101E" : "#F8FAFC"
                            border.color: Theme.borderCard
                            border.width: 1
                            implicitHeight: supSetCol.implicitHeight + 28

                            ColumnLayout {
                                id: supSetCol
                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Rectangle {
                                        width: 26
                                        height: 26
                                        radius: 13
                                        color: Theme.isDark ? "#2D2211" : "#FEF3C7"
                                        AppIcon { anchors.centerIn: parent; name: "timer"; size: 14; iconColor: Theme.accentAmber }
                                    }
                                    ColumnLayout {
                                        spacing: 1
                                        Text { text: "SUPERVISOR SETTINGS TABS"; font.family: "Inter"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                                        Text { text: "Visible tabs during elevated Supervisor session"; font.family: "Inter"; font.pixelSize: 9; color: Theme.textMuted }
                                    }
                                }

                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderCard }

                                Repeater {
                                    model: [
                                        { key: "profile", label: "User Profile & Access", icon: "person", desc: "PIN login/logout, active role timer & theme toggle" },
                                        { key: "serial", label: "Serial Hardware", icon: "cable", desc: "Controller COM port selection & baudrate connection" },
                                        { key: "feeds", label: "Motion Feeds", icon: "speed", desc: "Stage jog feed & laser scribing feed rates (mm/min)" },
                                        { key: "origin", label: "Print Origin & Bed", icon: "gps_fixed", desc: "X/Y index starting datum & mini bed canvas preview" },
                                        { key: "camera_offset", label: "Camera Offsets", icon: "videocam", desc: "Laser 1 & 2 optical camera calibration & speeds" },
                                        { key: "system", label: "System & Updates", icon: "info", desc: "Software version, update checker & company information" }
                                    ]

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 44
                                        radius: 6
                                        color: supSetItemMa.containsMouse ? (Theme.isDark ? "#131C2E" : "#F1F5F9") : "transparent"
                                        border.color: supSetItemMa.containsMouse ? Theme.borderCard : "transparent"
                                        border.width: 1

                                        readonly property bool isAllowed: root.isSettingsTabPermitted("Supervisor", modelData.key)

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 8
                                            anchors.rightMargin: 8
                                            spacing: 10

                                            AppIcon {
                                                name: modelData.icon
                                                size: 16
                                                iconColor: isAllowed ? Theme.accentAmber : Theme.textMuted
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 1
                                                Text {
                                                    text: modelData.label
                                                    font.family: "Inter"
                                                    font.pixelSize: 11
                                                    font.weight: Font.DemiBold
                                                    color: isAllowed ? Theme.textPrimary : Theme.textMuted
                                                }
                                                Text {
                                                    text: modelData.desc
                                                    font.family: "Inter"
                                                    font.pixelSize: 9
                                                    color: Theme.textMuted
                                                    elide: Text.ElideRight
                                                    Layout.fillWidth: true
                                                }
                                            }

                                            // iOS-style Toggle Switch
                                            Rectangle {
                                                width: 36
                                                height: 20
                                                radius: 10
                                                color: isAllowed ? Theme.accentAmber : (Theme.isDark ? "#334155" : "#CBD5E1")
                                                Behavior on color { ColorAnimation { duration: 150 } }

                                                Rectangle {
                                                    width: 14
                                                    height: 14
                                                    radius: 7
                                                    color: "#FFFFFF"
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    x: isAllowed ? (parent.width - width - 3) : 3
                                                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                                                }
                                            }
                                        }

                                        MouseArea {
                                            id: supSetItemMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.toggleSettingsTabPermission("Supervisor", modelData.key)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Save / Reset Command Bar
            MetricCard {
                Layout.fillWidth: true
                title: "Deploy & Apply Machine Configuration"
                subtitle: "Persist parameters to configuration file"
                accentColor: Theme.accentGreen

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 14

                    // Feedback Notification Banner
                    Rectangle {
                        Layout.fillWidth: true
                        height: root.saveStatusMsg.length > 0 ? 36 : 0
                        visible: root.saveStatusMsg.length > 0
                        radius: 6
                        color: root.isSaveError ? Theme.pillOfflineBg : Theme.pillOnlineBg
                        border.color: root.isSaveError ? Theme.pillOfflineBorder : Theme.pillOnlineBorder
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 8
                            AppIcon { name: root.isSaveError ? "warning" : "check_circle"; size: 14; iconColor: root.isSaveError ? Theme.pillOfflineText : Theme.pillOnlineText }
                            Text {
                                text: root.saveStatusMsg
                                font.family: "Inter"
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                color: root.isSaveError ? Theme.pillOfflineText : Theme.pillOnlineText
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        AppButton {
                            Layout.fillWidth: true
                            implicitHeight: 44
                            iconName: "save"
                            text: "SAVE & APPLY HARDWARE CONFIGURATION"
                            variant: "primary"
                            onClicked: {
                                settings.saveHardwareConfig(
                                    root.workingLaserCount,
                                    root.workingBedWidth,
                                    root.workingBedHeight,
                                    root.workingZMax,
                                    root.workingCameraEnabled,
                                    root.workingOriginPosition,
                                    root.workingMachineName
                                )
                                settings.saveRolePermissions(root.workingOperatorPages, root.workingSupervisorPages)
                                settings.saveSettingsTabPermissions(root.workingOperatorSettingsTabs, root.workingSupervisorSettingsTabs)
                            }
                        }

                        AppButton {
                            Layout.preferredWidth: 240
                            implicitHeight: 44
                            iconName: "restart_alt"
                            text: "RESET TO DEFAULTS"
                            variant: "outline"
                            onClicked: {
                                root.workingLaserCount = 2
                                root.workingBedWidth = 100.0
                                root.workingBedHeight = 100.0
                                root.workingZMax = 16.0
                                root.workingCameraEnabled = true
                                root.workingOriginPosition = "top-right"
                                bedWInput.text = "100.0"
                                bedHInput.text = "100.0"
                                zMaxInput.text = "16.0"
                                zSlider.value = 16.0
                                root.workingOperatorPages = ["motion", "laser", "job", "camera", "settings"]
                                root.workingSupervisorPages = ["motion", "laser", "job", "camera", "terminal", "settings"]
                                settings.saveRolePermissions(root.workingOperatorPages, root.workingSupervisorPages)
                                root.workingOperatorSettingsTabs = ["profile", "serial", "feeds", "system"]
                                root.workingSupervisorSettingsTabs = ["profile", "serial", "feeds", "origin", "camera_offset", "system"]
                                settings.saveSettingsTabPermissions(root.workingOperatorSettingsTabs, root.workingSupervisorSettingsTabs)
                            }
                        }
                    }
                }
            }
        }
    }
}
