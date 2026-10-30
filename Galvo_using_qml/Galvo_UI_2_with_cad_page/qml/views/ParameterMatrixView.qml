import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Rectangle {
    id: root
    color: Theme.bgApp

    // Signal to close modal if embedded in a modal
    signal requestClose()

    // Resilient backend reference: resolves to matrix or matrixBridge context property
    readonly property var matrixBackend: (typeof matrix !== "undefined" && matrix) 
                                         ? matrix 
                                         : ((typeof matrixBridge !== "undefined" && matrixBridge) ? matrixBridge : null)

    property bool labelAxesCheckVal: matrixBackend ? matrixBackend.labelAxes : true

    // Refresh canvas on visibility change and size change
    onVisibleChanged: {
        if (visible) {
            applyParams();
            repaintTimer.start();
        }
    }

    Timer {
        id: repaintTimer
        interval: 80
        repeat: false
        onTriggered: gridCanvas.requestPaint()
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // ==========================================
        // LEFT CONFIGURATION PANEL
        // ==========================================
        Rectangle {
            Layout.preferredWidth: 380
            Layout.fillHeight: true
            color: Theme.bgCard
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: "grid_on"
                        font.family: "Material Icons"
                        font.pixelSize: 20
                        color: Theme.accentCyan
                    }

                    Text {
                        text: "PARAMETER MATRIX"
                        color: Theme.textPrimary
                        font.pixelSize: 14
                        font.bold: true
                        font.letterSpacing: 0.8
                    }

                    Item { Layout.fillWidth: true }

                    Rectangle {
                        color: Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.15)
                        border.color: Theme.accentCyan
                        border.width: 1
                        radius: 4
                        implicitWidth: cellsBadgeText.implicitWidth + 14
                        implicitHeight: 22

                        Text {
                            id: cellsBadgeText
                            anchors.centerIn: parent
                            text: (matrixBackend ? matrixBackend.powerSteps * matrixBackend.freqSteps : 25) + " Cells"
                            color: Theme.accentCyan
                            font.pixelSize: 11
                            font.bold: true
                        }
                    }
                }

                Text {
                    text: "Empirical power vs. frequency marking matrix calibration tool."
                    color: Theme.textSecondary
                    font.pixelSize: 11
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.border }

                // Scrollable Parameters
                ScrollView {
                    id: paramScrollView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    contentWidth: availableWidth
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded

                    ColumnLayout {
                        width: paramScrollView.availableWidth
                        spacing: 10

                        // 1. POWER RANGE
                        GroupBox {
                            title: "⚡ Laser Power (%)"
                            Layout.fillWidth: true
                            topPadding: 20
                            bottomPadding: 8
                            leftPadding: 8
                            rightPadding: 8
                            background: Rectangle { 
                                color: Theme.isDark ? "#121A2D" : "#F8FAFC"
                                border.color: Theme.border
                                radius: 6 
                            }
                            label: Text { 
                                text: parent.title
                                color: "#F59E0B"
                                font.bold: true
                                font.pixelSize: 11
                                padding: 2 
                            }

                            RowLayout {
                                anchors.fill: parent
                                spacing: 8

                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Start (%)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: powStartInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.powerStart.toString() : "10"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: powStartInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "End (%)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: powEndInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.powerEnd.toString() : "90"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: powEndInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Steps"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: powStepsInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.powerSteps.toString() : "5"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: powStepsInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                            }
                        }

                        // 2. FREQUENCY RANGE
                        GroupBox {
                            title: "🌊 Frequency (kHz)"
                            Layout.fillWidth: true
                            topPadding: 20
                            bottomPadding: 8
                            leftPadding: 8
                            rightPadding: 8
                            background: Rectangle { 
                                color: Theme.isDark ? "#121A2D" : "#F8FAFC"
                                border.color: Theme.border
                                radius: 6 
                            }
                            label: Text { 
                                text: parent.title
                                color: "#A855F7"
                                font.bold: true
                                font.pixelSize: 11
                                padding: 2 
                            }

                            RowLayout {
                                anchors.fill: parent
                                spacing: 8

                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Start (kHz)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: freqStartInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.freqStart.toString() : "20"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: freqStartInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "End (kHz)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: freqEndInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.freqEnd.toString() : "80"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: freqEndInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Steps"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: freqStepsInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.freqSteps.toString() : "5"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: freqStepsInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                            }
                        }

                        // 3. CELL GEOMETRY & SPACING
                        GroupBox {
                            title: "📐 Cell Size & Spacing (mm)"
                            Layout.fillWidth: true
                            topPadding: 20
                            bottomPadding: 8
                            leftPadding: 8
                            rightPadding: 8
                            background: Rectangle { 
                                color: Theme.isDark ? "#121A2D" : "#F8FAFC"
                                border.color: Theme.border
                                radius: 6 
                            }
                            label: Text { 
                                text: parent.title
                                color: Theme.accentCyan
                                font.bold: true
                                font.pixelSize: 11
                                padding: 2 
                            }

                            RowLayout {
                                anchors.fill: parent
                                spacing: 8

                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Width (mm)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: cellWidthInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.cellWidth.toString() : "5.0"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: cellWidthInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Height (mm)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: cellHeightInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.cellHeight.toString() : "5.0"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: cellHeightInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Gap X (mm)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: cellGapXInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.cellGapX.toString() : "2.0"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: cellGapXInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: "Gap Y (mm)"; color: Theme.textSecondary; font.pixelSize: 10 }
                                    TextField {
                                        id: cellGapYInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.cellGapY.toString() : "2.0"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 11
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: cellGapYInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 4 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }
                                }
                            }
                        }

                        // 4. PROCESS & OPTIONS (Clean Dark-Themed Dropdown & Checkbox)
                        GroupBox {
                            title: "⚙️ Hatching & Execution"
                            Layout.fillWidth: true
                            topPadding: 20
                            bottomPadding: 10
                            leftPadding: 10
                            rightPadding: 10
                            background: Rectangle { 
                                color: Theme.isDark ? "#121A2D" : "#F8FAFC"
                                border.color: Theme.border
                                radius: 6 
                            }
                            label: Text { 
                                text: parent.title
                                color: Theme.textPrimary
                                font.bold: true
                                font.pixelSize: 11
                                padding: 2 
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 10

                                // Styled Custom Dropdown (No native white box)
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    z: 10

                                    Text { 
                                        text: "Pattern:"
                                        color: Theme.textSecondary
                                        font.pixelSize: 12
                                        Layout.preferredWidth: 60 
                                    }

                                    Rectangle {
                                        id: fillTypeBox
                                        Layout.fillWidth: true
                                        height: 32
                                        radius: 6
                                        color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                        border.color: fillTypePopup.visible ? Theme.accentCyan : Theme.border
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            spacing: 6

                                            Text {
                                                id: fillTypeLabel
                                                Layout.fillWidth: true
                                                text: (matrixBackend && matrixBackend.fillType === "Vector Outline") ? "Vector Outline" : "Filled Rectangle"
                                                color: Theme.textPrimary
                                                font.pixelSize: 12
                                                font.bold: true
                                                verticalAlignment: Text.AlignVCenter
                                            }

                                            Text {
                                                text: fillTypePopup.visible ? "▲" : "▼"
                                                color: Theme.textSecondary
                                                font.pixelSize: 10
                                            }
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: fillTypePopup.visible = !fillTypePopup.visible
                                        }

                                        Popup {
                                            id: fillTypePopup
                                            y: fillTypeBox.height + 4
                                            width: fillTypeBox.width
                                            padding: 4
                                            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
                                            background: Rectangle {
                                                color: Theme.isDark ? "#10192D" : "#FFFFFF"
                                                border.color: Theme.borderActive
                                                border.width: 1
                                                radius: 6
                                            }

                                            contentItem: ColumnLayout {
                                                spacing: 2
                                                Repeater {
                                                    model: ["Filled Rectangle", "Vector Outline"]
                                                    delegate: Rectangle {
                                                        Layout.fillWidth: true
                                                        height: 28
                                                        radius: 4
                                                        color: itemMa.containsMouse ? (Theme.isDark ? "#1E2D4A" : "#E0F2FE") : "transparent"

                                                        Text {
                                                            anchors.fill: parent
                                                            anchors.leftMargin: 8
                                                            text: modelData
                                                            color: (fillTypeLabel.text === modelData) ? Theme.accentCyan : Theme.textPrimary
                                                            font.pixelSize: 11
                                                            font.bold: fillTypeLabel.text === modelData
                                                            verticalAlignment: Text.AlignVCenter
                                                        }

                                                        MouseArea {
                                                            id: itemMa
                                                            anchors.fill: parent
                                                            hoverEnabled: true
                                                            cursorShape: Qt.PointingHandCursor
                                                            onClicked: {
                                                                fillTypeLabel.text = modelData;
                                                                fillTypePopup.close();
                                                                applyParams();
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }

                                // Speed Input Row
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Text { 
                                        text: "Marking Speed:"
                                        color: Theme.textSecondary
                                        font.pixelSize: 12
                                        Layout.preferredWidth: 95
                                    }

                                    TextField {
                                        id: markSpeedInput
                                        Layout.fillWidth: true
                                        implicitHeight: 30
                                        text: matrixBackend ? matrixBackend.markSpeed.toString() : "1000"
                                        color: Theme.textPrimary
                                        font.bold: true
                                        font.pixelSize: 12
                                        verticalAlignment: TextInput.AlignVCenter
                                        background: Rectangle { 
                                            color: Theme.isDark ? "#17233D" : "#FFFFFF"
                                            border.color: markSpeedInput.activeFocus ? Theme.accentCyan : Theme.border
                                            radius: 6 
                                        }
                                        onTextEdited: applyParams()
                                        onEditingFinished: applyParams()
                                    }

                                    Text { 
                                        text: "mm/s"
                                        color: Theme.textSecondary
                                        font.pixelSize: 11 
                                    }
                                }

                                // Styled Custom CheckBox (No native white box)
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Rectangle {
                                        id: checkIndicator
                                        width: 18
                                        height: 18
                                        radius: 4
                                        color: labelAxesCheckVal ? Theme.accentCyan : (Theme.isDark ? "#17233D" : "#FFFFFF")
                                        border.color: labelAxesCheckVal ? Theme.accentCyan : Theme.border
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            visible: labelAxesCheckVal
                                            text: "✓"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "#0A0F1D"
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                labelAxesCheckVal = !labelAxesCheckVal;
                                                applyParams();
                                            }
                                        }
                                    }

                                    Text {
                                        Layout.fillWidth: true
                                        text: "Label axes with parameter values"
                                        font.pixelSize: 12
                                        color: Theme.textPrimary
                                        verticalAlignment: Text.AlignVCenter

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                labelAxesCheckVal = !labelAxesCheckVal;
                                                applyParams();
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Field Bounds Exceeded Warning Banner
                Rectangle {
                    Layout.fillWidth: true
                    height: 30
                    visible: matrixBackend ? matrixBackend.exceedsBounds : false
                    color: Theme.isDark ? "#381216" : "#FEE2E2"
                    border.color: "#EF4444"
                    radius: 6

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 6
                        Text { text: "⚠️"; font.pixelSize: 12 }
                        Text {
                            text: "Matrix Exceeds Lens Field Bounds!"
                            color: "#EF4444"
                            font.pixelSize: 11
                            font.bold: true
                            Layout.fillWidth: true
                        }
                    }
                }

                // STATUS BAR
                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: Theme.isDark ? "#0F172A" : "#F1F5F9"
                    border.color: Theme.border
                    radius: 6

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 8
                        Rectangle {
                            width: 8; height: 8; radius: 4
                            color: matrixBackend && matrixBackend.isExecuting 
                                   ? "#10B981" 
                                   : (matrixBackend && matrixBackend.isFraming ? "#EF4444" : Theme.textMuted)
                        }
                        Text {
                            text: matrixBackend ? matrixBackend.statusMessage : "Ready"
                            color: Theme.textSecondary
                            font.pixelSize: 11
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                    }
                }

                // ================= 4 ACTION BUTTONS (CLEAN 2x2 BALANCED GRID) ================= //
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    // Row 1: Red Preview & Laser Mark (Equal 50% width, height 38px)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        // 1. Red Preview Button
                        Rectangle {
                            id: previewBtnBox
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            radius: 6
                            opacity: (matrixBackend && matrixBackend.exceedsBounds) ? 0.4 : 1.0
                            color: (matrixBackend && matrixBackend.isFraming) 
                                   ? (previewMouse.pressed ? "#991B1B" : (previewMouse.containsMouse ? "#DC2626" : "#EF4444"))
                                   : (previewMouse.containsMouse ? (Theme.isDark ? "#2A1820" : "#FEE2E2") : (Theme.isDark ? "#1C1420" : "#FFF1F2"))
                            border.color: (matrixBackend && matrixBackend.isFraming) ? "#EF4444" : "#F43F5E"
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Text {
                                    text: (matrixBackend && matrixBackend.isFraming) ? "■" : "◉"
                                    font.pixelSize: 14
                                    color: (matrixBackend && matrixBackend.isFraming) ? "#FFFFFF" : "#F43F5E"
                                }
                                Text {
                                    text: (matrixBackend && matrixBackend.isFraming) ? "Stop Guide" : "Red Preview"
                                    color: (matrixBackend && matrixBackend.isFraming) ? "#FFFFFF" : "#F43F5E"
                                    font.bold: true
                                    font.pixelSize: 12
                                }
                            }

                            MouseArea {
                                id: previewMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                enabled: !(matrixBackend && matrixBackend.exceedsBounds)
                                onClicked: {
                                    if (matrixBackend) {
                                        if (matrixBackend.isFraming) matrixBackend.abort();
                                        else matrixBackend.startRedPreview();
                                    }
                                }
                            }
                        }

                        // 2. Laser Mark Button
                        Rectangle {
                            id: markBtnBox
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            radius: 6
                            opacity: (matrixBackend && matrixBackend.exceedsBounds) ? 0.4 : 1.0
                            color: (matrixBackend && matrixBackend.isExecuting) 
                                   ? "#059669" 
                                   : (markMouse.pressed ? "#0099B8" : (markMouse.containsMouse ? "#38BDF8" : Theme.accentCyan))
                            border.color: (matrixBackend && matrixBackend.isExecuting) ? "#10B981" : Theme.accentCyan
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Text {
                                    text: "⚡"
                                    font.pixelSize: 14
                                    color: (matrixBackend && matrixBackend.isExecuting) ? "#FFFFFF" : "#0A0F1D"
                                }
                                Text {
                                    text: matrixBackend && matrixBackend.exceedsBounds ? "Exceeds Bounds" : (matrixBackend && matrixBackend.isExecuting ? "Marking..." : "Laser Mark")
                                    color: (matrixBackend && matrixBackend.isExecuting) ? "#FFFFFF" : "#0A0F1D"
                                    font.bold: true
                                    font.pixelSize: 12
                                }
                            }

                            MouseArea {
                                id: markMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                enabled: !(matrixBackend && matrixBackend.exceedsBounds)
                                onClicked: {
                                    if (matrixBackend) matrixBackend.startLaserMark();
                                }
                            }
                        }
                    }

                    // Row 2: Pause/Resume & Abort (Equal 50% width, height 38px)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        // 3. Pause / Resume Button
                        Rectangle {
                            id: pauseBtnBox
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            radius: 6
                            property bool isReady: matrixBackend && matrixBackend.isExecuting
                            opacity: isReady ? 1.0 : 0.4
                            color: (matrixBackend && matrixBackend.isPaused) 
                                   ? (pauseMouse.pressed ? "#D97706" : (pauseMouse.containsMouse ? "#FBBF24" : "#F59E0B"))
                                   : (pauseMouse.containsMouse ? (Theme.isDark ? "#28344E" : "#E2E8F0") : (Theme.isDark ? "#17233D" : "#F1F5F9"))
                            border.color: (matrixBackend && matrixBackend.isPaused) ? "#F59E0B" : Theme.border
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Text {
                                    text: (matrixBackend && matrixBackend.isPaused) ? "▶" : "❚❚"
                                    font.pixelSize: 12
                                    color: (matrixBackend && matrixBackend.isPaused) ? "#FFFFFF" : Theme.textPrimary
                                }
                                Text {
                                    text: (matrixBackend && matrixBackend.isPaused) ? "Resume" : "Pause"
                                    color: (matrixBackend && matrixBackend.isPaused) ? "#FFFFFF" : Theme.textPrimary
                                    font.bold: true
                                    font.pixelSize: 12
                                }
                            }

                            MouseArea {
                                id: pauseMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                enabled: parent.isReady
                                onClicked: {
                                    if (matrixBackend) matrixBackend.togglePause();
                                }
                            }
                        }

                        // 4. Abort Button (Identical dimensions, danger styling)
                        Rectangle {
                            id: abortBtnBox
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            radius: 6
                            color: abortMouse.pressed ? "#7F1D1D" : (abortMouse.containsMouse ? "#991B1B" : (Theme.isDark ? "#330F15" : "#FEE2E2"))
                            border.color: "#EF4444"
                            border.width: 1

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6
                                Text {
                                    text: "✕"
                                    font.pixelSize: 13
                                    font.bold: true
                                    color: abortMouse.containsMouse ? "#FFFFFF" : "#EF4444"
                                }
                                Text {
                                    text: "Abort"
                                    color: abortMouse.containsMouse ? "#FFFFFF" : "#EF4444"
                                    font.bold: true
                                    font.pixelSize: 12
                                }
                            }

                            MouseArea {
                                id: abortMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (matrixBackend) matrixBackend.abort();
                                }
                            }
                        }
                    }
                }
            }
        }

        // ==========================================
        // RIGHT VISUAL 2D PREVIEW CANVAS
        // ==========================================
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.isDark ? "#080C16" : "#E2E8F0"
            clip: true

            // Grid Canvas
            Canvas {
                id: gridCanvas
                anchors.fill: parent

                Connections {
                    target: matrixBackend
                    function onMatrixCellsChanged() { gridCanvas.requestPaint(); }
                    function onActiveCellIndexChanged() { gridCanvas.requestPaint(); }
                    function onIsFramingChanged() { gridCanvas.requestPaint(); }
                    function onIsExecutingChanged() { gridCanvas.requestPaint(); }
                }

                onAvailableChanged: if (available) requestPaint()
                onVisibleChanged: if (visible) requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    var cx = width / 2;
                    var cy = height / 2;

                    var fieldSize = (typeof settings !== "undefined" && settings && settings.fieldSize) ? settings.fieldSize : 70.0;
                    var showLabels = matrixBackend ? matrixBackend.labelAxes : true;

                    // Compute scale with breathing room for labels
                    var paddingFactor = showLabels ? 1.45 : 1.20;
                    var scaleX = width / (fieldSize * paddingFactor);
                    var scaleY = height / (fieldSize * paddingFactor);
                    var scale = Math.min(scaleX, scaleY);
                    if (scale <= 0) return;

                    // 1. Draw subtle background grid
                    ctx.strokeStyle = Theme.isDark ? "#121A2A" : "#CBD5E1";
                    ctx.lineWidth = 1;
                    var gridStep = 10 * scale;
                    if (gridStep > 12) {
                        for (var gx = cx % gridStep; gx < width; gx += gridStep) {
                            ctx.beginPath();
                            ctx.moveTo(gx, 0); ctx.lineTo(gx, height);
                            ctx.stroke();
                        }
                        for (var gy = cy % gridStep; gy < height; gy += gridStep) {
                            ctx.beginPath();
                            ctx.moveTo(0, gy); ctx.lineTo(width, gy);
                            ctx.stroke();
                        }
                    }

                    // 2. Galvo Field Limit Box (matches mapping_dialog.py)
                    var fieldPix = fieldSize * scale;
                    var fx0 = cx - fieldPix / 2;
                    var fy0 = cy - fieldPix / 2;

                    ctx.strokeStyle = Theme.isDark ? "rgba(40, 180, 80, 0.6)" : "rgba(16, 185, 129, 0.8)";
                    ctx.lineWidth = 1.5;
                    ctx.setLineDash([5, 4]);
                    ctx.strokeRect(fx0, fy0, fieldPix, fieldPix);
                    ctx.setLineDash([]);

                    // Field Limit Caption
                    ctx.fillStyle = Theme.isDark ? "rgba(40, 180, 80, 0.75)" : "#059669";
                    ctx.font = "10px sans-serif";
                    ctx.textAlign = "left";
                    ctx.textBaseline = "bottom";
                    ctx.fillText("Field Limit (" + fieldSize.toFixed(0) + "x" + fieldSize.toFixed(0) + " mm)", fx0 + 6, fy0 + fieldPix - 5);

                    // 3. Center Crosshair
                    ctx.strokeStyle = Theme.isDark ? "rgba(0, 210, 255, 0.25)" : "rgba(2, 132, 199, 0.35)";
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(cx - 15, cy); ctx.lineTo(cx + 15, cy);
                    ctx.moveTo(cx, cy - 15); ctx.lineTo(cx, cy + 15);
                    ctx.stroke();

                    // 4. Matrix Cells
                    if (!matrixBackend || !matrixBackend.matrixCells || matrixBackend.matrixCells.length === 0) return;
                    var cells = matrixBackend.matrixCells;
                    var activeIdx = matrixBackend.activeCellIndex;
                    var isOutline = matrixBackend.fillType === "Vector Outline";

                    // Compute true screen bounding box of all cells to prevent axis title overlap!
                    var minCellSx = 999999, maxCellSx = -999999;
                    var minCellSy = 999999, maxCellSy = -999999;
                    var maxRow = 0;

                    for (var k = 0; k < cells.length; k++) {
                        var c = cells[k];
                        if (c.row > maxRow) maxRow = c.row;
                        var csx = cx + c.x * scale;
                        var csy = cy - (c.y + c.h) * scale;
                        var csw = c.w * scale;
                        var csh = c.h * scale;

                        if (csx < minCellSx) minCellSx = csx;
                        if (csx + csw > maxCellSx) maxCellSx = csx + csw;
                        if (csy < minCellSy) minCellSy = csy;
                        if (csy + csh > maxCellSy) maxCellSy = csy + csh;
                    }

                    for (var i = 0; i < cells.length; i++) {
                        var cell = cells[i];
                        // Coordinate transform: center is (0,0), galvo Y is inverted from screen Y
                        var sx = cx + cell.x * scale;
                        var sy = cy - (cell.y + cell.h) * scale;
                        var sw = cell.w * scale;
                        var sh = cell.h * scale;

                        var isActive = (i === activeIdx);

                        if (isActive) {
                            // Active burning cell glowing yellow/amber (matches mapping_dialog.py)
                            ctx.fillStyle = "#FFB300";
                            ctx.fillRect(sx, sy, sw, sh);
                            ctx.strokeStyle = "#FFFF00";
                            ctx.lineWidth = 2.5;
                            ctx.strokeRect(sx, sy, sw, sh);
                        } else {
                            // Shading proportional to laser power
                            var pMin = matrixBackend ? matrixBackend.powerStart : 10.0;
                            var pMax = matrixBackend ? matrixBackend.powerEnd : 90.0;
                            var pRange = Math.max(1.0, pMax - pMin);
                            var pRatio = Math.max(0.0, Math.min(1.0, (cell.power - pMin) / pRange));

                            if (isOutline) {
                                ctx.fillStyle = Theme.isDark ? "rgba(0, 30, 50, 0.45)" : "rgba(224, 242, 254, 0.6)";
                                ctx.fillRect(sx, sy, sw, sh);
                                var strokeG = Math.round(180 + 75 * pRatio);
                                ctx.strokeStyle = "rgba(0, " + strokeG + ", 255, 0.9)";
                                ctx.lineWidth = 1.5;
                                ctx.strokeRect(sx, sy, sw, sh);
                            } else {
                                var alpha = 0.35 + 0.55 * pRatio;
                                var fillG = Math.round(130 + 110 * pRatio);
                                ctx.fillStyle = "rgba(0, " + fillG + ", 255, " + alpha.toFixed(2) + ")";
                                ctx.fillRect(sx, sy, sw, sh);
                                ctx.strokeStyle = "rgba(0, 220, 255, 0.75)";
                                ctx.lineWidth = 1;
                                ctx.strokeRect(sx, sy, sw, sh);
                            }
                        }

                        // Cell internal text (Power % & Frequency kHz) with Adaptive High-Contrast
                        if (sw > 22 && sh > 14) {
                            // Dark background cells get crisp White/Cyan text; bright cyan cells get Obsidian Black/Navy text
                            var isBrightCell = (!isOutline && pRatio >= 0.50);
                            var powerTextColor = isActive ? "#000000" : (isBrightCell ? "#040D1A" : "#FFFFFF");
                            var freqTextColor = isActive ? "#1A2230" : (isBrightCell ? "#0A2640" : "#BAE6FD");

                            ctx.font = "bold 10px sans-serif";
                            ctx.fillStyle = powerTextColor;
                            ctx.textAlign = "center";
                            ctx.textBaseline = "middle";
                            ctx.fillText(Math.round(cell.power) + "%", sx + sw / 2, sy + sh / 2 - 5);

                            ctx.font = "bold 9px sans-serif";
                            ctx.fillStyle = freqTextColor;
                            ctx.fillText(Math.round(cell.freq) + "k", sx + sw / 2, sy + sh / 2 + 5);
                        }

                        // 5. Axis Labels (Frequency on column 0, Power on bottom row)
                        if (showLabels) {
                            ctx.font = "9px sans-serif";
                            ctx.fillStyle = Theme.isDark ? "#8FA3BF" : "#475569";

                            // Frequency along left (column 0)
                            if (cell.col === 0) {
                                ctx.textAlign = "right";
                                ctx.textBaseline = "middle";
                                ctx.fillText(cell.freq.toFixed(0) + " kHz", sx - 8, sy + sh / 2);
                            }

                            // Power along lowest row on screen (row == 0 in galvo coordinates)
                            if (cell.row === 0) {
                                ctx.textAlign = "center";
                                ctx.textBaseline = "top";
                                ctx.fillText(cell.power.toFixed(0) + "%", sx + sw / 2, maxCellSy + 6);
                            }
                        }
                    }

                    // Axis Header Titles (Positioned completely outside cell area!)
                    if (showLabels && cells.length > 0) {
                        ctx.fillStyle = Theme.accentCyan;
                        ctx.font = "bold 11px sans-serif";

                        // Left vertical axis title (above frequency labels)
                        ctx.textAlign = "right";
                        ctx.textBaseline = "bottom";
                        ctx.fillText("▲ Freq (kHz)", minCellSx - 10, minCellSy - 8);

                        // Bottom horizontal axis title (below power labels, perfectly centered)
                        ctx.textAlign = "center";
                        ctx.textBaseline = "top";
                        ctx.fillText("Laser Power (%) ►", (minCellSx + maxCellSx) / 2, maxCellSy + 24);
                    }
                }
            }

            // Overlay Info (Top Left of visual canvas)
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: 16
                color: Theme.isDark ? "#161c26cc" : "#FFFFFFee"
                border.color: Theme.border
                radius: 6
                implicitWidth: infoCol.implicitWidth + 24
                implicitHeight: infoCol.implicitHeight + 16

                ColumnLayout {
                    id: infoCol
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        text: "Bed: " + ((typeof settings !== "undefined" && settings && settings.fieldSize) ? settings.fieldSize : 70) + " x " + ((typeof settings !== "undefined" && settings && settings.fieldSize) ? settings.fieldSize : 70) + " mm"
                        color: Theme.textSecondary
                        font.pixelSize: 11
                    }
                    Text {
                        text: "Matrix Area: " + (matrixBackend ? matrixBackend.totalWidth.toFixed(1) : "0.0") + " x " + (matrixBackend ? matrixBackend.totalHeight.toFixed(1) : "0.0") + " mm"
                        color: matrixBackend && matrixBackend.exceedsBounds ? "#EF4444" : Theme.accentCyan
                        font.pixelSize: 11
                        font.bold: true
                    }
                }
            }
        }
    }

    Connections {
        target: matrixBackend
        function onMatrixCellsChanged() { gridCanvas.requestPaint(); }
        function onIsExecutingChanged() { gridCanvas.requestPaint(); }
        function onIsFramingChanged() { gridCanvas.requestPaint(); }
        function onActiveCellIndexChanged() { gridCanvas.requestPaint(); }
        function onParamsChanged() { gridCanvas.requestPaint(); }
    }

    function applyParams() {
        if (!matrixBackend) return;
        var pStart = parseFloat(powStartInput.text) || 10.0;
        var pEnd = parseFloat(powEndInput.text) || 90.0;
        var pSteps = parseInt(powStepsInput.text) || 5;
        var fStart = parseFloat(freqStartInput.text) || 20.0;
        var fEnd = parseFloat(freqEndInput.text) || 80.0;
        var fSteps = parseInt(freqStepsInput.text) || 5;
        var cW = parseFloat(cellWidthInput.text) || 5.0;
        var cH = parseFloat(cellHeightInput.text) || 5.0;
        var gX = parseFloat(cellGapXInput.text) || 2.0;
        var gY = parseFloat(cellGapYInput.text) || 2.0;
        var fType = fillTypeLabel.text;
        var lAxes = labelAxesCheckVal;
        var spd = parseFloat(markSpeedInput.text) || 1000.0;

        matrixBackend.updateParameters(pStart, pEnd, pSteps, fStart, fEnd, fSteps, cW, cH, gX, gY, fType, lAxes, spd);
        gridCanvas.requestPaint();
    }

    Component.onCompleted: {
        applyParams();
    }
}
