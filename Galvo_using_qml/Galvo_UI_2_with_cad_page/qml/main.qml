import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "views"

ApplicationWindow {
    FontLoader {
        id: materialIconsFont
        source: "fonts/MaterialIcons-Regular.ttf"
    }

    id: window
    visible: true
    width: 1440
    height: 900
    minimumWidth: 1100
    minimumHeight: 720
    title: ((typeof settings !== "undefined" && settings.machineName) ? settings.machineName : "Galvo Studio") + " — Industrial CAD & Laser Workstation"
    color: Theme.bgApp

    function toggleTheme() {
        Theme.toggleTheme()
    }

    readonly property bool isAnyModalOpen: Boolean(
        (typeof jogModal !== "undefined" && jogModal && jogModal.opacity > 0) ||
        (typeof laserModal !== "undefined" && laserModal && laserModal.opacity > 0) ||
        (typeof configModal !== "undefined" && configModal && configModal.opacity > 0) ||
        (typeof paramMatrixModal !== "undefined" && paramMatrixModal && paramMatrixModal.opacity > 0) ||
        (typeof settingsModal !== "undefined" && settingsModal && settingsModal.opacity > 0) ||
        (typeof corCalibrationModal !== "undefined" && corCalibrationModal && corCalibrationModal.opacity > 0) ||
        (typeof autoConnectModal !== "undefined" && autoConnectModal && autoConnectModal.visible)
    )

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ================= TOP HEADER BAR ================= //
        Rectangle {
            Layout.fillWidth: true
            height: 56
            color: Theme.bgHeader
            border.color: Theme.borderCard
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                // Logo & Name
                Row {
                    spacing: 10
                    Layout.alignment: Qt.AlignVCenter

                    Item {
                        width: 36
                        height: 36
                        Layout.alignment: Qt.AlignVCenter

                        Image {
                            id: headerLogoImg
                            anchors.fill: parent
                            source: (typeof appLogoUrl !== "undefined" && appLogoUrl) ? appLogoUrl : ""
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                            mipmap: true
                        }

                        // Fallback icon only if logo image is not found or loading
                        Rectangle {
                            anchors.fill: parent
                            radius: 6
                            color: Theme.accentCyan
                            visible: headerLogoImg.status !== Image.Ready
                            Text {
                                anchors.centerIn: parent
                                text: "⚡"
                                font.pixelSize: 18
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            ToolTip.visible: containsMouse
                            ToolTip.text: "Spécialisé Products Private Limited\nClick to open www.specialiseproducts.com"
                            ToolTip.delay: 300
                            onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                        }
                    }

                    Column {
                        Text {
                            text: (typeof settings !== "undefined" && settings.machineName) ? settings.machineName.toUpperCase() : "GALVO STUDIO"
                            color: Theme.textPrimary
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            font.family: "Segoe UI, Inter, sans-serif"
                        }
                        Text {
                            text: "Industrial Laser Scribing & Patterning"
                            color: Theme.accentCyan
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                        }
                    }
                }

                // Hardware Connection Status Badge
                Rectangle {
                    height: 28
                    implicitWidth: statusRow.width + 20
                    radius: 14
                    color: (typeof galvo !== "undefined" && galvo.isConnected)
                           ? (galvo.isDemo ? (Theme.isDark ? "#2E2413" : "#FEF3C7") : (Theme.isDark ? "#062E20" : "#D1FAE5"))
                           : (Theme.isDark ? "#17233D" : "#E2E8F0")
                    border.color: (typeof galvo !== "undefined" && galvo.isConnected)
                                  ? (galvo.isDemo ? Theme.accentAmber : Theme.accentGreen)
                                  : Theme.borderCard
                    border.width: 1

                    Row {
                        id: statusRow
                        anchors.centerIn: parent
                        spacing: 6

                        Rectangle {
                            width: 8; height: 8; radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: (typeof galvo !== "undefined" && galvo.isConnected)
                                   ? (galvo.isDemo ? Theme.accentAmber : Theme.accentGreen)
                                   : Theme.textMuted
                        }

                        Text {
                            text: (typeof galvo !== "undefined" && galvo.isConnected && !galvo.isDemo)
                                  ? "HARDWARE ONLINE"
                                  : "SIMULATION MODE — DEMO"
                            color: Theme.textPrimary
                            font.pixelSize: 10
                            font.weight: Font.Bold
                        }
                    }
                }

                // Connect / Disconnect Button
                ModernButton {
                    text: (typeof galvo !== "undefined" && galvo.isConnected && !galvo.isDemo) ? "Disconnect" : "Connect Hardware"
                    primary: !(typeof galvo !== "undefined" && galvo.isConnected && !galvo.isDemo)
                    implicitWidth: 130
                    implicitHeight: 34
                    onClicked: {
                        if (typeof galvo !== "undefined") {
                            if (galvo.isConnected && !galvo.isDemo) galvo.disconnectHardware()
                            else galvo.connectHardware()
                        }
                    }
                }

                // Divider
                Rectangle { width: 1; height: 26; color: Theme.borderMuted }

                // ================= SLIDEABLE / SCROLLABLE PAGES TAB BAR ================= //
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 4

                    // Left Scroll Arrow Button
                    Rectangle {
                        id: scrollLeftBtn
                        width: 24
                        height: 34
                        radius: 4
                        visible: scrollFlick.contentWidth > scrollFlick.width
                        color: scrollFlick.contentX > 2 ? (leftMa.containsMouse ? (Theme.isDark ? "#2a3958" : "#CBD5E1") : (Theme.isDark ? "#17233D" : "#E2E8F0")) : "transparent"
                        border.color: scrollFlick.contentX > 2 ? Theme.borderCard : "transparent"
                        opacity: scrollFlick.contentX > 2 ? 1.0 : 0.25
                        enabled: scrollFlick.contentX > 2

                        Text {
                            anchors.centerIn: parent
                            text: "◀"
                            font.pixelSize: 10
                            color: parent.enabled ? Theme.textPrimary : Theme.textMuted
                        }

                        MouseArea {
                            id: leftMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: parent.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: {
                                var target = Math.max(0, scrollFlick.contentX - 160);
                                scrollAnim.to = target;
                                scrollAnim.start();
                            }
                        }
                    }

                    // Slideable / Flickable Container
                    Flickable {
                        id: scrollFlick
                        Layout.fillWidth: true
                        height: 38
                        contentWidth: buttonsRow.width
                        contentHeight: 38
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds
                        flickableDirection: Flickable.HorizontalFlick

                        NumberAnimation on contentX {
                            id: scrollAnim
                            duration: 200
                            easing.type: Easing.OutQuad
                        }

                        // Mouse wheel horizontal scrolling
                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            onWheel: function(wheel) {
                                if (wheel.angleDelta.y !== 0) {
                                    var newX = Math.max(0, Math.min(scrollFlick.contentWidth - scrollFlick.width, scrollFlick.contentX - wheel.angleDelta.y));
                                    scrollFlick.contentX = newX;
                                }
                            }
                        }

                        Row {
                            id: buttonsRow
                            spacing: 8
                            anchors.verticalCenter: parent.verticalCenter

                            // 1. Z-Focus & Focal Stepper
                            ModernButton {
                                text: "🎯 Focus"
                                implicitHeight: 34
                                implicitWidth: 90
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: jogModal.open()
                            }

                            // 2. Laser Hardware Diagnostics & Controls
                            ModernButton {
                                text: "⚡ Laser"
                                implicitHeight: 34
                                implicitWidth: 88
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: laserModal.open()
                            }

                            // 3. Hardware Configuration (configgalvo)
                            ModernButton {
                                text: "🔧 Config"
                                implicitHeight: 34
                                implicitWidth: 92
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: configModal.open()
                            }

                            // 4. Parameter Mapping Matrix
                            ModernButton {
                                text: "📊 Matrix"
                                implicitHeight: 34
                                implicitWidth: 92
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: paramMatrixModal.open()
                            }

                            // 5. System Settings & Field Calibration
                            ModernButton {
                                text: "⚙️ Settings"
                                implicitHeight: 34
                                implicitWidth: 96
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: settingsModal.open()
                            }

                            // 6. .COR Optical Scale & Lens Calibration Studio
                            ModernButton {
                                text: "📐 Calibrate (.cor)"
                                implicitHeight: 34
                                implicitWidth: 130
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                onClicked: corCalibrationModal.open()
                            }
                        }
                    }

                    // Right Scroll Arrow Button
                    Rectangle {
                        id: scrollRightBtn
                        width: 24
                        height: 34
                        radius: 4
                        visible: scrollFlick.contentWidth > scrollFlick.width
                        property bool canScrollRight: (scrollFlick.contentWidth - (scrollFlick.contentX + scrollFlick.width)) > 2
                        color: canScrollRight ? (rightMa.containsMouse ? (Theme.isDark ? "#2a3958" : "#CBD5E1") : (Theme.isDark ? "#17233D" : "#E2E8F0")) : "transparent"
                        border.color: canScrollRight ? Theme.borderCard : "transparent"
                        opacity: canScrollRight ? 1.0 : 0.25
                        enabled: canScrollRight

                        Text {
                            anchors.centerIn: parent
                            text: "▶"
                            font.pixelSize: 10
                            color: parent.enabled ? Theme.textPrimary : Theme.textMuted
                        }

                        MouseArea {
                            id: rightMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: parent.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: {
                                var target = Math.min(scrollFlick.contentWidth - scrollFlick.width, scrollFlick.contentX + 160);
                                scrollAnim.to = target;
                                scrollAnim.start();
                            }
                        }
                    }
                }

                // EMERGENCY STOP BUTTON
                ModernButton {
                    text: "🛑 E-STOP"
                    danger: true
                    implicitWidth: 96
                    implicitHeight: 34
                    onClicked: if (typeof galvo !== "undefined") galvo.emergencyStop()
                }

                // Theme Toggle (Dark / Light)
                ModernButton {
                    text: Theme.isDark ? "🌙 DARK" : "☀️ LIGHT"
                    implicitWidth: 92
                    implicitHeight: 34
                    btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                    textColor: Theme.textPrimary
                    borderColor: Theme.borderCard
                    onClicked: Theme.toggleTheme()
                }
            }
        }

        // ================= CONTINUOUS SIMULATION / DEMO MODE BANNER ================= //
        Rectangle {
            id: demoBanner
            Layout.fillWidth: true
            height: (typeof galvo !== "undefined" && (!galvo.isConnected || galvo.isDemo)) ? 36 : 0
            visible: height > 0
            clip: true
            color: Theme.isDark ? "#2A1F08" : "#FEF3C7"
            border.color: Theme.accentAmber
            border.width: 1

            Behavior on height { NumberAnimation { duration: 200 } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 10

                Rectangle {
                    width: 22
                    height: 22
                    radius: 4
                    color: Theme.accentAmber
                    Text {
                        anchors.centerIn: parent
                        text: "warning"
                        font.family: "Material Icons"
                        font.pixelSize: 15
                        color: "#000000"
                    }
                }

                Text {
                    text: "SIMULATION MODE — DEMO VERSION ONLY FOR EVALUATION"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    color: Theme.isDark ? "#FBBF24" : "#B45309"
                    font.letterSpacing: 0.5
                }

                Text {
                    text: "•  Physical motion controller card not connected. Hardware output (Laser / Stepper / Mirrors) disabled."
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                ModernButton {
                    text: "Connect Hardware"
                    implicitHeight: 26
                    implicitWidth: 125
                    btnColor: Theme.isDark ? "#3B2B11" : "#FDE68A"
                    textColor: Theme.isDark ? "#FBBF24" : "#92400E"
                    borderColor: Theme.accentAmber
                    onClicked: {
                        if (typeof galvo !== "undefined") {
                            galvo.connectHardware()
                        }
                    }
                }
            }
        }

        // ================= IMMERSIVE PRIMARY CAD STUDIO WORKSPACE ================= //
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            CadView {
                id: cadView
                anchors.fill: parent
            }
        }
    }

    // ================= GLOBAL INDUSTRIAL SHORTCUTS ================= //
    Shortcut {
        sequence: "F1"
        onActivated: {
            console.log("[Shortcut] F1 Pressed -> Toggle Red Light Guide")
            cadView.triggerRedPointer()
        }
    }

    Shortcut {
        sequence: "F2"
        onActivated: {
            console.log("[Shortcut] F2 Pressed -> Toggle Laser Mark")
            cadView.triggerMark()
        }
    }

    Shortcut {
        sequence: "F3"
        onActivated: {
            console.log("[Shortcut] F3 Pressed -> Toggle Pause/Resume")
            cadView.triggerPause()
        }
    }

    Shortcut {
        sequence: "Escape"
        onActivated: {
            console.log("[Shortcut] Escape Pressed -> Abort Operations")
            cadView.triggerAbort()
        }
    }

    // ================= POPUP TOOL WINDOWS (MODALS) ================= //
    // 1. Z-Axis Stepper & Focus Calibration Window
    ToolModal {
        id: jogModal
        title: "Z-Axis Stepper & Focal Calibration"
        iconName: "tune"
        modalWidth: 980
        modalHeight: 640

        JogView {
            anchors.fill: parent
            anchors.margins: 14
        }
    }

    // 2. Laser Diagnostics & Hardware Window
    ToolModal {
        id: laserModal
        title: "Laser Hardware Configuration & Diagnostics"
        iconName: "flash_on"
        modalWidth: 900
        modalHeight: 620

        LaserView {
            anchors.fill: parent
            anchors.margins: 14
        }
    }

    // 3. Hardware Configuration Window (configgalvo)
    ToolModal {
        id: configModal
        title: "CONFIG — Galvo Hardware, Optical Distortion & Park Position"
        iconName: "tune"
        modalWidth: 980
        modalHeight: 660

        ConfigView {
            anchors.fill: parent
            onRequestClose: configModal.close()
        }
    }

    // 4. Parameter Mapping Matrix Window
    ToolModal {
        id: paramMatrixModal
        title: "Parameter Mapping Matrix (Empirical Test Grid)"
        iconName: "grid_on"
        modalWidth: 1060
        modalHeight: 700

        ParameterMatrixView {
            anchors.fill: parent
            onRequestClose: paramMatrixModal.close()
        }
    }

    // 3. Settings & Calibration Window
    ToolModal {
        id: settingsModal
        title: "System Settings & Optical Field Calibration"
        iconName: "settings"
        modalWidth: 960
        modalHeight: 720

        SettingsView {
            anchors.fill: parent
            onOpenCorCalibrationStudio: {
                settingsModal.close()
                corCalibrationModal.open()
            }
        }
    }

    // 4. .COR Calibration & Distortion Correction Studio
    ToolModal {
        id: corCalibrationModal
        objectName: "corCalibrationModal"
        title: "Lens Distortion Correction & .COR Studio"
        iconName: "straighten"
        modalWidth: 1160
        modalHeight: 760

        CorCalibrationView {
            objectName: "corCalibrationView"
            anchors.fill: parent
            onRequestClose: corCalibrationModal.close()
        }
    }

    // ================= AUTO-CONNECT CARD DETECTED MODAL ================= //
    Rectangle {
        id: autoConnectModal
        visible: false
        z: 99999
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.68)

        property int candidateCount: 1
        property string candidateModel: "GoogolTech GT-U3 / GT-500"

        function showPrompt(count, model) {
            candidateCount = count
            candidateModel = model
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
            onWheel: function(wheel) { wheel.accepted = true }
        }

        Rectangle {
            id: modalBox
            anchors.centerIn: parent
            width: Math.min(500, parent.width - 40)
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
                onWheel: function(wheel) { wheel.accepted = true }
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
                        color: Theme.isDark ? "#2A2010" : "#FEF3C7"
                        border.color: Theme.accentAmber
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "flash_on"
                            font.family: "Material Icons"
                            font.pixelSize: 24
                            color: Theme.accentAmber
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "GALVO CARD DETECTED"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                            font.letterSpacing: 0.5
                        }

                        Text {
                            text: "Motion controller hardware found on system"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                    }
                }

                // Card info badge
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
                            Text {
                                text: "CARD:"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                            }
                            Text {
                                text: autoConnectModal.candidateModel
                                font.family: "Consolas, monospace"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                            }
                        }

                        Item { Layout.fillWidth: true }

                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 8; height: 8; radius: 4
                                color: Theme.accentGreen
                            }
                            Text {
                                text: "DETECTED"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.accentGreen
                            }
                        }
                    }
                }

                // Main Prompt Text
                Text {
                    Layout.fillWidth: true
                    text: "A compatible <b>GoogolTech Galvo Motion Controller</b> card was detected on this PC.<br><br>Do you want to auto connect to the card and initialize the galvo scanner & laser workstation?"
                    textFormat: Text.RichText
                    font.family: "Segoe UI, Inter, sans-serif"
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

                    ModernButton {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        text: "CANCEL"
                        btnColor: Theme.isDark ? "#1E293B" : "#E2E8F0"
                        textColor: Theme.textPrimary
                        onClicked: {
                            autoConnectModal.close()
                            if (typeof galvo !== "undefined") {
                                galvo.rejectAutoConnect()
                            }
                        }
                    }

                    ModernButton {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        primary: true
                        text: "CONNECT & INITIALIZE"
                        onClicked: {
                            autoConnectModal.close()
                            if (typeof galvo !== "undefined") {
                                galvo.acceptAutoConnect()
                            }
                        }
                    }
                }
            }
        }
    }

    // ================= FLOATING TOAST NOTIFICATION POPUP ================= //
    Rectangle {
        id: notificationToast
        z: 99998
        anchors.top: parent.top
        anchors.topMargin: 64
        anchors.right: parent.right
        anchors.rightMargin: 24
        width: Math.min(440, parent.width - 48)
        height: toastCol.implicitHeight + 24
        radius: 8
        color: Theme.bgCard
        border.color: isWarningAlert ? Theme.accentAmber : Theme.accentCyan
        border.width: 1.5
        visible: opacity > 0
        opacity: 0.0

        property string alertTitle: "Notification"
        property string alertMessage: ""
        property bool isWarningAlert: true

        Behavior on opacity { NumberAnimation { duration: 180 } }
        Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutBack } }
        scale: opacity > 0 ? 1.0 : 0.92

        Timer {
            id: toastTimer
            interval: 4500
            repeat: false
            onTriggered: notificationToast.opacity = 0.0
        }

        function show(title, msg, isWarning) {
            alertTitle = title
            alertMessage = msg
            isWarningAlert = (typeof isWarning !== "undefined") ? isWarning : true
            opacity = 1.0
            toastTimer.restart()
        }

        MouseArea {
            anchors.fill: parent
            onClicked: notificationToast.opacity = 0.0
        }

        ColumnLayout {
            id: toastCol
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 12
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: notificationToast.isWarningAlert ? "warning" : "info"
                    font.family: "Material Icons"
                    font.pixelSize: 18
                    color: notificationToast.isWarningAlert ? Theme.accentAmber : Theme.accentCyan
                }

                Text {
                    text: notificationToast.alertTitle
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 13
                    font.weight: Font.Bold
                    color: Theme.textPrimary
                    Layout.fillWidth: true
                }

                Text {
                    text: "close"
                    font.family: "Material Icons"
                    font.pixelSize: 16
                    color: Theme.textMuted
                }
            }

            Text {
                text: notificationToast.alertMessage
                font.family: "Segoe UI, Inter, sans-serif"
                font.pixelSize: 12
                color: Theme.textSecondary
                wrapMode: Text.WordWrap
                lineHeight: 1.25
                Layout.fillWidth: true
            }
        }
    }

    // Connect to Galvo card detection and hardware alerts
    Connections {
        target: (typeof galvo !== "undefined") ? galvo : null
        function onCardDetected(cardCount, cardModel) {
            console.log("[GalvoStudio] Card detected in background: " + cardCount + " - " + cardModel)
            autoConnectModal.showPrompt(cardCount, cardModel)
        }
        function onHardwareAlert(title, message) {
            console.log("[GalvoStudio Alert]", title, message)
            notificationToast.show(title, message, true)
        }
    }

    Connections {
        target: (typeof jog !== "undefined") ? jog : null
        function onHardwareAlert(title, message) {
            console.log("[JogStudio Alert]", title, message)
            notificationToast.show(title, message, true)
        }
    }

    Connections {
        target: (typeof cad !== "undefined") ? cad : null
        function onHardwareAlert(title, message) {
            console.log("[CadStudio Alert]", title, message)
            notificationToast.show(title, message, true)
        }
    }

    Component.onCompleted: {
        console.log("[GalvoStudio] UI Initialized. Starting background hardware card probe...")
        if (typeof galvo !== "undefined") {
            galvo.startCardDetection()
        }
    }
}


