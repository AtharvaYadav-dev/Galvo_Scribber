import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Rectangle {
    id: root
    color: Theme.bgApp
    implicitWidth: 1140
    implicitHeight: 740

    signal requestClose()

    property int currentTab: 0 // 0: Inspect / Upload, 1: 9-Point Studio

    onCurrentTabChanged: {
        if (currentTab === 0 && distortionCanvas) distortionCanvas.requestPaint()
        if (currentTab === 1 && plateCanvas) plateCanvas.requestPaint()
    }

    readonly property var cal: (typeof calibration !== "undefined" && calibration) ? calibration : null

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        // ================= TOP BAR: TAB SWITCHER & TITLE ================= //
        RowLayout {
            Layout.fillWidth: true
            spacing: 14

            ColumnLayout {
                spacing: 2
                Text {
                    text: "EZCAD LENS CALIBRATION & .COR STUDIO"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: Theme.textPrimary
                    font.letterSpacing: 0.5
                }
                Text {
                    text: "Inspect binary .cor files, analyze 65×65 lens distortion, and generate new calibration files from 9 physical measurements"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            // Segmented Tab Selector
            Rectangle {
                implicitHeight: 36
                implicitWidth: tabRow.implicitWidth + 8
                radius: 7
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                Row {
                    id: tabRow
                    anchors.centerIn: parent
                    spacing: 4

                    Rectangle {
                        implicitWidth: 185
                        implicitHeight: 28
                        radius: 5
                        color: root.currentTab === 0 ? Theme.accentCyan : (t0Ma.containsMouse ? (Theme.isDark ? "#22355C" : "#E2E8F0") : "transparent")

                        Text {
                            anchors.centerIn: parent
                            text: "📁 1. Upload & Inspect .COR"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: root.currentTab === 0 ? "#000000" : Theme.textPrimary
                        }
                        MouseArea {
                            id: t0Ma
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.currentTab = 0
                        }
                    }

                    Rectangle {
                        implicitWidth: 215
                        implicitHeight: 28
                        radius: 5
                        color: root.currentTab === 1 ? Theme.accentCyan : (t1Ma.containsMouse ? (Theme.isDark ? "#22355C" : "#E2E8F0") : "transparent")

                        Text {
                            anchors.centerIn: parent
                            text: "📐 2. 9-Point Studio (Generator)"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: root.currentTab === 1 ? "#000000" : Theme.textPrimary
                        }
                        MouseArea {
                            id: t1Ma
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.currentTab = 1
                        }
                    }
                }
            }
        }

        // ================= TAB 1: INSPECT & UPLOAD .COR ================= //
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14
            visible: root.currentTab === 0

            // Left Column: File Selector & Metadata Cards
            ColumnLayout {
                Layout.preferredWidth: 450
                Layout.minimumWidth: 420
                Layout.maximumWidth: 470
                Layout.fillWidth: false
                Layout.fillHeight: true
                spacing: 12

                // File Select Card
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: upCol.implicitHeight + 24
                    radius: 8
                    color: Theme.bgCard
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        id: upCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        Text {
                            text: "EZCAD BINARY .COR CALIBRATION FILE"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.accentCyan
                            font.letterSpacing: 0.5
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Load an existing .cor file to inspect optical scale factors, verify 65×65 lens distortion correction deltas, and load directly into the galvanometer hardware controller."
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 36
                                primary: true
                                text: "📂 Browse & Open .COR File"
                                onClicked: if (cal) cal.openCorFileDialog()
                            }

                            ModernButton {
                                implicitHeight: 36
                                implicitWidth: 130
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                text: "↺ Reload Default"
                                onClicked: if (cal) cal.loadCorFile("newest100mm.cor")
                            }
                        }
                    }
                }

                // File Metrics & Hardware Status Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 8
                    color: Theme.bgCard
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "ACTIVE CALIBRATION METRICS"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            Rectangle {
                                height: 20
                                implicitWidth: vTxt.width + 12
                                radius: 10
                                color: (cal && cal.isValid) ? (Theme.isDark ? "#062E20" : "#D1FAE5") : (Theme.isDark ? "#381010" : "#FEE2E2")
                                border.color: (cal && cal.isValid) ? Theme.accentGreen : Theme.accentRed
                                border.width: 1
                                Text {
                                    id: vTxt
                                    anchors.centerIn: parent
                                    text: (cal && cal.isValid) ? "VALID JCZ_COR" : "NO CALIBRATION"
                                    font.pixelSize: 9; font.bold: true
                                    color: (cal && cal.isValid) ? Theme.accentGreen : Theme.accentRed
                                }
                            }
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 10

                            Text { text: "Active File:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? cal.activeCorFileName : "None"
                                font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true
                                color: Theme.textPrimary; elide: Text.ElideMiddle; Layout.fillWidth: true
                            }

                            Text { text: "Header Signature:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text { text: cal ? cal.signature : "-"; font.family: "Consolas, monospace"; font.pixelSize: 11; color: Theme.textPrimary }

                            Text { text: "Optical Scale:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? (cal.scale.toFixed(2) + " bits/mm") : "-"
                                font.family: "Consolas, monospace"; font.pixelSize: 12; font.bold: true; color: Theme.accentCyan
                            }

                            Text { text: "Working Field:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? (cal.fieldSize.toFixed(1) + " × " + cal.fieldSize.toFixed(1) + " mm") : "-"
                                font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true; color: Theme.textPrimary
                            }

                            Text { text: "Delta X Range:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? (cal.minDx + " .. " + cal.maxDx + " bits (" + (cal.minDx / cal.scale).toFixed(2) + " .. " + (cal.maxDx / cal.scale).toFixed(2) + " mm)") : "-"
                                font.family: "Consolas, monospace"; font.pixelSize: 10; color: Theme.textPrimary
                            }

                            Text { text: "Delta Y Range:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? (cal.minDy + " .. " + cal.maxDy + " bits (" + (cal.minDy / cal.scale).toFixed(2) + " .. " + (cal.maxDy / cal.scale).toFixed(2) + " mm)") : "-"
                                font.family: "Consolas, monospace"; font.pixelSize: 10; color: Theme.textPrimary
                            }

                            Text { text: "Mean Distortion:"; font.pixelSize: 11; font.bold: true; color: Theme.textSecondary }
                            Text {
                                text: cal ? (cal.avgErrorMm.toFixed(3) + " mm RMS") : "-"
                                font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true; color: Theme.accentAmber
                            }
                        }

                        Item { Layout.fillHeight: true }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 36
                                primary: true
                                enabled: Boolean(cal && cal.isValid)
                                text: "⚡ Apply & Activate in Hardware"
                                onClicked: if (cal) cal.applyToHardware()
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 34
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                enabled: Boolean(cal && cal.isValid)
                                text: "💾 Save as Startup Default (newest100mm.cor)"
                                onClicked: if (cal) cal.saveAsDefaultStartupCor()
                            }
                        }
                    }
                }
            }

            // Right Column: 2D Lens Distortion Mesh Preview
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 450
                radius: 8
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "65×65 LENS BARREL / PINCUSHION DISTORTION MESH"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.accentCyan
                            font.letterSpacing: 0.5
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: "Optical Scale: " + (cal ? cal.scale.toFixed(1) : "533.9") + " bits/mm | Vectors ×15"
                            font.pixelSize: 10; color: Theme.textMuted
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 6
                        color: Theme.isDark ? "#0A0F1D" : "#F8FAFC"
                        border.color: Theme.borderCard
                        border.width: 1
                        clip: true

                        Canvas {
                            id: distortionCanvas
                            anchors.fill: parent
                            anchors.margins: 14

                            Connections {
                                target: cal
                                function onCalibrationLoaded() { distortionCanvas.requestPaint() }
                            }

                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)

                                var w = width
                                var h = height
                                var cx = w / 2.0
                                var cy = h / 2.0
                                var sz = Math.min(w, h) * 0.84
                                var halfSz = sz / 2.0

                                // Nominal Square Frame & Center Crosshairs
                                ctx.strokeStyle = Theme.isDark ? "#1E293B" : "#CBD5E1"
                                ctx.lineWidth = 1.0
                                ctx.strokeRect(cx - halfSz, cy - halfSz, sz, sz)

                                ctx.setLineDash([4, 4])
                                ctx.beginPath()
                                ctx.moveTo(cx, cy - halfSz - 10); ctx.lineTo(cx, cy + halfSz + 10)
                                ctx.moveTo(cx - halfSz - 10, cy); ctx.lineTo(cx + halfSz + 10, cy)
                                ctx.stroke()
                                ctx.setLineDash([])

                                // Distortion Samples (11x11 sample grid)
                                if (cal && cal.gridSample && cal.gridSample.length > 0) {
                                    var samples = cal.gridSample
                                    var exag = 18.0

                                    // Distorted mesh lines
                                    ctx.strokeStyle = Qt.rgba(0.06, 0.73, 0.85, 0.45)
                                    ctx.lineWidth = 1.0

                                    var stride = 11
                                    for (var r = 0; r < stride; r++) {
                                        ctx.beginPath()
                                        for (var c = 0; c < stride; c++) {
                                            var s = samples[r * stride + c]
                                            var px = cx + s.nx * halfSz + (s.dx_mm * exag)
                                            var py = cy - s.ny * halfSz - (s.dy_mm * exag)
                                            if (c === 0) ctx.moveTo(px, py)
                                            else ctx.lineTo(px, py)
                                        }
                                        ctx.stroke()
                                    }

                                    for (var c2 = 0; c2 < stride; c2++) {
                                        ctx.beginPath()
                                        for (var r2 = 0; r2 < stride; r2++) {
                                            var s2 = samples[r2 * stride + c2]
                                            var px2 = cx + s2.nx * halfSz + (s2.dx_mm * exag)
                                            var py2 = cy - s2.ny * halfSz - (s2.dy_mm * exag)
                                            if (r2 === 0) ctx.moveTo(px2, py2)
                                            else ctx.lineTo(px2, py2)
                                        }
                                        ctx.stroke()
                                    }

                                    // Vectors
                                    for (var i = 0; i < samples.length; i++) {
                                        var pt = samples[i]
                                        var origX = cx + pt.nx * halfSz
                                        var origY = cy - pt.ny * halfSz
                                        var corrX = origX + (pt.dx_mm * exag)
                                        var corrY = origY - (pt.dy_mm * exag)

                                        ctx.fillStyle = Theme.accentCyan
                                        ctx.beginPath()
                                        ctx.arc(corrX, corrY, 2.0, 0, Math.PI * 2)
                                        ctx.fill()

                                        if (Math.abs(pt.dx_mm) > 0.02 || Math.abs(pt.dy_mm) > 0.02) {
                                            ctx.strokeStyle = Theme.accentAmber
                                            ctx.lineWidth = 1.0
                                            ctx.beginPath()
                                            ctx.moveTo(origX, origY)
                                            ctx.lineTo(corrX, corrY)
                                            ctx.stroke()
                                        }
                                    }
                                }

                                ctx.fillStyle = Theme.accentCyan
                                ctx.beginPath()
                                ctx.arc(cx, cy, 3.5, 0, Math.PI * 2)
                                ctx.fill()
                            }
                        }
                    }
                }
            }
        }

        // ================= TAB 2: 9-POINT CALIBRATION STUDIO ================= //
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            visible: root.currentTab === 1

            // 1. Top Toolbar: Parameters & Laser Action Bar
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 66
                radius: 8
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 14
                    spacing: 14

                    // Group A: Target Half-Width (W) & Nominal Envelope
                    ColumnLayout {
                        spacing: 3
                        Text {
                            text: "TARGET HALF-WIDTH (W)"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                            font.letterSpacing: 0.5
                        }
                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 72
                                height: 30
                                radius: 5
                                color: Theme.bgInput
                                border.color: wInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: wInput
                                    anchors.fill: parent; anchors.margins: 4
                                    verticalAlignment: TextInput.AlignVCenter
                                    horizontalAlignment: TextInput.AlignHCenter
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: Theme.textPrimary
                                    text: cal ? cal.targetHalfWidth.toFixed(1) : "25.0"
                                    onEditingFinished: {
                                        var v = parseFloat(text)
                                        if (cal && !isNaN(v) && v > 0) cal.targetHalfWidth = v
                                    }
                                }
                            }
                            Rectangle {
                                height: 26
                                implicitWidth: gridBadgeTxt.width + 12
                                radius: 4
                                color: Theme.isDark ? "#162035" : "#E2E8F0"
                                border.color: Theme.isDark ? "#22355C" : "#CBD5E1"
                                border.width: 1
                                Text {
                                    id: gridBadgeTxt
                                    anchors.centerIn: parent
                                    text: (cal ? cal.nominalFieldSize.toFixed(0) : "50") + " × " + (cal ? cal.nominalFieldSize.toFixed(0) : "50") + " mm"
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: Theme.accentCyan
                                }
                            }
                        }
                    }

                    // Divider
                    Rectangle { width: 1; height: 36; color: Theme.borderCard }

                    // Group B: Laser Power (Custom Sleek Slider)
                    ColumnLayout {
                        Layout.preferredWidth: 140
                        spacing: 3
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "LASER POWER"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: (cal ? cal.calPower.toFixed(0) : "100") + " %"
                                font.family: "Consolas, monospace"
                                font.pixelSize: 11
                                font.bold: true
                                color: Theme.accentCyan
                            }
                        }
                        Slider {
                            id: calPowerSlider
                            Layout.fillWidth: true
                            from: 0; to: 100; stepSize: 1
                            value: cal ? cal.calPower : 100
                            onMoved: if (cal) cal.calPower = value

                            background: Rectangle {
                                x: calPowerSlider.leftPadding
                                y: calPowerSlider.topPadding + calPowerSlider.availableHeight / 2 - height / 2
                                width: calPowerSlider.availableWidth
                                height: 5
                                radius: 2.5
                                color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                Rectangle {
                                    width: calPowerSlider.visualPosition * parent.width
                                    height: parent.height
                                    radius: 2.5
                                    color: Theme.accentCyan
                                }
                            }

                            handle: Rectangle {
                                x: calPowerSlider.leftPadding + calPowerSlider.visualPosition * (calPowerSlider.availableWidth - width)
                                y: calPowerSlider.topPadding + calPowerSlider.availableHeight / 2 - height / 2
                                width: 14; height: 14; radius: 7
                                color: calPowerSlider.pressed ? "#FFFFFF" : Theme.accentCyan
                                border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                border.width: 2
                            }
                        }
                    }

                    // Divider
                    Rectangle { width: 1; height: 36; color: Theme.borderCard }

                    // Group C: Q-Switch Frequency (Custom Sleek Slider)
                    ColumnLayout {
                        Layout.preferredWidth: 135
                        spacing: 3
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "FREQUENCY"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: (cal ? cal.calFreq.toFixed(0) : "30") + " kHz"
                                font.family: "Consolas, monospace"
                                font.pixelSize: 11
                                font.bold: true
                                color: "#A855F7"
                            }
                        }
                        Slider {
                            id: calFreqSlider
                            Layout.fillWidth: true
                            from: 20; to: 80; stepSize: 1
                            value: cal ? cal.calFreq : 30
                            onMoved: if (cal) cal.calFreq = value

                            background: Rectangle {
                                x: calFreqSlider.leftPadding
                                y: calFreqSlider.topPadding + calFreqSlider.availableHeight / 2 - height / 2
                                width: calFreqSlider.availableWidth
                                height: 5
                                radius: 2.5
                                color: Theme.isDark ? "#17233D" : "#E2E8F0"

                                Rectangle {
                                    width: calFreqSlider.visualPosition * parent.width
                                    height: parent.height
                                    radius: 2.5
                                    color: "#A855F7"
                                }
                            }

                            handle: Rectangle {
                                x: calFreqSlider.leftPadding + calFreqSlider.visualPosition * (calFreqSlider.availableWidth - width)
                                y: calFreqSlider.topPadding + calFreqSlider.availableHeight / 2 - height / 2
                                width: 14; height: 14; radius: 7
                                color: calFreqSlider.pressed ? "#FFFFFF" : "#A855F7"
                                border.color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                                border.width: 2
                            }
                        }
                    }

                    // Divider
                    Rectangle { width: 1; height: 36; color: Theme.borderCard }

                    // Group D: Mark Speed
                    ColumnLayout {
                        spacing: 3
                        Text {
                            text: "MARK SPEED"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                            font.letterSpacing: 0.5
                        }
                        RowLayout {
                            spacing: 4
                            Rectangle {
                                width: 62
                                height: 30
                                radius: 5
                                color: Theme.bgInput
                                border.color: spdInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: spdInput
                                    anchors.fill: parent; anchors.margins: 4
                                    verticalAlignment: TextInput.AlignVCenter
                                    horizontalAlignment: TextInput.AlignHCenter
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: Theme.textPrimary
                                    text: cal ? cal.calMarkSpeed.toFixed(0) : "20"
                                    onEditingFinished: if (cal) cal.calMarkSpeed = parseFloat(text) || 20
                                }
                            }
                            Text {
                                text: "mm/s"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                color: Theme.textMuted
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Group E: Laser Actions
                    RowLayout {
                        spacing: 8

                        ModernButton {
                            implicitHeight: 34
                            implicitWidth: 135
                            btnColor: (cal && cal.isFraming) ? Theme.accentRed : (Theme.isDark ? "#17233D" : "#FFFFFF")
                            textColor: (cal && cal.isFraming) ? "#FFFFFF" : Theme.textPrimary
                            borderColor: (cal && cal.isFraming) ? Theme.accentRed : Theme.borderCard
                            text: (cal && cal.isFraming) ? "⏹ Stop Red Dot" : "🔴 Red Dot Frame"
                            onClicked: if (cal) cal.toggleRedDotFraming()
                        }

                        ModernButton {
                            implicitHeight: 34
                            implicitWidth: 145
                            primary: true
                            enabled: !(cal && (cal.isMarking || cal.isFraming))
                            text: (cal && cal.isMarking) ? "⏳ Marking Grid..." : "⚡ Mark Cal Grid"
                            onClicked: if (cal) cal.markCalibrationGrid()
                        }

                        ModernButton {
                            implicitHeight: 34
                            implicitWidth: 85
                            danger: true
                            text: "🛑 STOP"
                            onClicked: if (cal) cal.stopLaser()
                        }
                    }
                }
            }

            // Split Layout: Left Plate Diagram | Right 9 Caliper Inputs & Execution
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12

                // Left: Physical Plate Diagram & Orientation Canvas
                Rectangle {
                    Layout.preferredWidth: 460
                    Layout.fillHeight: true
                    radius: 8
                    color: Theme.bgCard
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "1. PHYSICAL PLATE ORIENTATION"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            Rectangle {
                                height: 20
                                implicitWidth: orTxt.width + 10
                                radius: 4
                                color: Theme.isDark ? "#1E2A44" : "#DBEAFE"
                                Text {
                                    id: orTxt
                                    anchors.centerIn: parent
                                    text: cal ? cal.orientationName : "State 1"
                                    font.pixelSize: 9; font.bold: true; color: Theme.accentCyan
                                }
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Match Point 1 (square ◽) and Point 9 (diamond ◊) to your marked plate. Click below to cycle until diagram matches:"
                            font.pixelSize: 10
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                        }

                        ModernButton {
                            Layout.fillWidth: true
                            implicitHeight: 30
                            btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                            textColor: Theme.textPrimary
                            borderColor: Theme.borderCard
                            text: "🔄 Cycle Next Orientation (1 of 8)"
                            onClicked: {
                                if (cal) cal.nextOrientation()
                                plateCanvas.requestPaint()
                            }
                        }

                        // Canvas
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 6
                            color: Theme.isDark ? "#0A0F1D" : "#FFFFFF"
                            border.color: Theme.borderCard
                            border.width: 1
                            clip: true

                            Canvas {
                                id: plateCanvas
                                anchors.fill: parent
                                anchors.margins: 12
                                onAvailableChanged: if (available) requestPaint()
                                onVisibleChanged: if (visible) requestPaint()
                                Component.onCompleted: requestPaint()

                                Connections {
                                    target: cal
                                    function onOrientationChanged() { plateCanvas.requestPaint() }
                                    function onParametersChanged() { plateCanvas.requestPaint() }
                                }

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)

                                    var w = width
                                    var h = height
                                    var cx = w / 2.0
                                    var cy = h / 2.0
                                    var sz = Math.min(w, h) * 0.78
                                    var halfSz = sz / 2.0

                                    // Outer frame & crosshair
                                    ctx.strokeStyle = Theme.isDark ? "#334155" : "#1E293B"
                                    ctx.lineWidth = 1.6
                                    ctx.strokeRect(cx - halfSz, cy - halfSz, sz, sz)

                                    ctx.beginPath()
                                    ctx.moveTo(cx, cy - halfSz - 10); ctx.lineTo(cx, cy + halfSz + 10)
                                    ctx.moveTo(cx - halfSz - 10, cy); ctx.lineTo(cx + halfSz + 10, cy)
                                    ctx.stroke()

                                    // Numbers 1-9
                                    ctx.font = "bold 12px 'Segoe UI', Inter, sans-serif"
                                    ctx.fillStyle = "#EF4444"

                                    var numPositions = [
                                        { x: cx - halfSz - 16, y: cy - halfSz - 5, t: "1" },
                                        { x: cx - 4,           y: cy - halfSz - 5, t: "2" },
                                        { x: cx + halfSz + 6,  y: cy - halfSz - 5, t: "3" },
                                        { x: cx - halfSz - 16, y: cy + 4,          t: "4" },
                                        { x: cx + 5,           y: cy - 5,          t: "5" },
                                        { x: cx + halfSz + 6,  y: cy + 4,          t: "6" },
                                        { x: cx - halfSz - 16, y: cy + halfSz + 14,t: "7" },
                                        { x: cx - 4,           y: cy + halfSz + 14,t: "8" },
                                        { x: cx + halfSz + 6,  y: cy + halfSz + 14,t: "9" }
                                    ]
                                    for (var ni = 0; ni < numPositions.length; ni++) {
                                        ctx.fillText(numPositions[ni].t, numPositions[ni].x, numPositions[ni].y)
                                    }

                                    // Markers
                                    if (cal) {
                                        var cur = cal.getOrientationInfo()
                                        var sqX = cx + cur.sq_x * (halfSz * 0.82)
                                        var sqY = cy - cur.sq_y * (halfSz * 0.82)

                                        ctx.strokeStyle = Theme.isDark ? "#38BDF8" : "#0284C7"
                                        ctx.lineWidth = 2
                                        ctx.strokeRect(sqX - 6, sqY - 6, 12, 12)

                                        var diX = cx + cur.di_x * (halfSz * 0.82)
                                        var diY = cy - cur.di_y * (halfSz * 0.82)
                                        ctx.save()
                                        ctx.translate(diX, diY)
                                        ctx.rotate(Math.PI / 4)
                                        ctx.strokeRect(-6, -6, 12, 12)
                                        ctx.restore()

                                        var t1x = cx + cur.tick_p1_x * halfSz
                                        var t1y = cy - cur.tick_p1_y * halfSz
                                        var t2x = cx + cur.tick_p2_x * halfSz
                                        var t2y = cy - cur.tick_p2_y * halfSz
                                        ctx.beginPath()
                                        ctx.moveTo(t1x, t1y)
                                        ctx.lineTo(t2x, t2y)
                                        ctx.lineWidth = 3
                                        ctx.strokeStyle = Theme.accentAmber
                                        ctx.stroke()
                                    }

                                    // Measured polygon overlay
                                    if (cal && cal.measuredPoints && cal.measuredPoints.length === 9) {
                                        var W = cal.targetHalfWidth || 25.0
                                        var mpts = cal.measuredPoints

                                        function mToScreen(mx, my) {
                                            return {
                                                x: cx + (mx / W) * halfSz,
                                                y: cy - (my / W) * halfSz
                                            }
                                        }

                                        var scrPts = []
                                        for (var mi = 0; mi < 9; mi++) {
                                            scrPts.push(mToScreen(mpts[mi].x, mpts[mi].y))
                                        }

                                        ctx.setLineDash([3, 3])
                                        ctx.strokeStyle = Theme.accentAmber
                                        ctx.lineWidth = 1.4

                                        ctx.beginPath()
                                        ctx.moveTo(scrPts[0].x, scrPts[0].y); ctx.lineTo(scrPts[1].x, scrPts[1].y); ctx.lineTo(scrPts[2].x, scrPts[2].y)
                                        ctx.moveTo(scrPts[3].x, scrPts[3].y); ctx.lineTo(scrPts[4].x, scrPts[4].y); ctx.lineTo(scrPts[5].x, scrPts[5].y)
                                        ctx.moveTo(scrPts[6].x, scrPts[6].y); ctx.lineTo(scrPts[7].x, scrPts[7].y); ctx.lineTo(scrPts[8].x, scrPts[8].y)
                                        ctx.moveTo(scrPts[0].x, scrPts[0].y); ctx.lineTo(scrPts[3].x, scrPts[3].y); ctx.lineTo(scrPts[6].x, scrPts[6].y)
                                        ctx.moveTo(scrPts[1].x, scrPts[1].y); ctx.lineTo(scrPts[4].x, scrPts[4].y); ctx.lineTo(scrPts[7].x, scrPts[7].y)
                                        ctx.moveTo(scrPts[2].x, scrPts[2].y); ctx.lineTo(scrPts[5].x, scrPts[5].y); ctx.lineTo(scrPts[8].x, scrPts[8].y)
                                        ctx.stroke()
                                        ctx.setLineDash([])

                                        ctx.fillStyle = Theme.accentAmber
                                        for (var pi = 0; pi < 9; pi++) {
                                            ctx.beginPath()
                                            ctx.arc(scrPts[pi].x, scrPts[pi].y, 3.0, 0, Math.PI * 2)
                                            ctx.fill()
                                        }
                                    }
                                }
                            }
                        }

                        // Legend Pill Row
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Rectangle {
                                Layout.fillWidth: true
                                height: 24; radius: 4
                                color: Theme.isDark ? "#111827" : "#F1F5F9"
                                border.color: Theme.borderCard; border.width: 1
                                Row {
                                    anchors.centerIn: parent; spacing: 4
                                    Rectangle { width: 8; height: 8; color: "transparent"; border.color: Theme.accentCyan; border.width: 1.5; anchors.verticalCenter: parent.verticalCenter }
                                    Text { text: "Pt 1 Square"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 24; radius: 4
                                color: Theme.isDark ? "#111827" : "#F1F5F9"
                                border.color: Theme.borderCard; border.width: 1
                                Row {
                                    anchors.centerIn: parent; spacing: 4
                                    Text { text: "◊"; font.pixelSize: 11; font.bold: true; color: Theme.accentCyan; anchors.verticalCenter: parent.verticalCenter }
                                    Text { text: "Pt 9 Diamond"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 24; radius: 4
                                color: Theme.isDark ? "#111827" : "#F1F5F9"
                                border.color: Theme.borderCard; border.width: 1
                                Row {
                                    anchors.centerIn: parent; spacing: 4
                                    Rectangle { width: 8; height: 3; color: Theme.accentAmber; anchors.verticalCenter: parent.verticalCenter }
                                    Text { text: "Center Axis Tick"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                                }
                            }
                        }
                    }
                }

                // ---------------- Right: 9 Caliper Measurements & Calibration Workbench ---------------- //
                Rectangle {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 580
                    Layout.fillHeight: true
                    radius: 8
                    color: Theme.bgCard
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        // Header
                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "2. 9 CALIPER MEASUREMENTS (MM)"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            ModernButton {
                                implicitHeight: 26
                                implicitWidth: 125
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                text: "↺ Reset All Nominal"
                                onClicked: if (cal) cal.resetToNominal()
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "Measure the 9 marked crosses on your plate using calipers and enter physical distances from center (0,0):"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            color: Theme.textSecondary
                        }

                        // Table Headers
                        Rectangle {
                            Layout.fillWidth: true
                            height: 26
                            radius: 4
                            color: Theme.isDark ? "#111827" : "#F1F5F9"
                            border.color: Theme.borderCard
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                spacing: 8

                                Text { text: "#"; font.pixelSize: 10; font.bold: true; color: Theme.textMuted; Layout.preferredWidth: 24 }
                                Text { text: "Node Position"; font.pixelSize: 10; font.bold: true; color: Theme.textMuted; Layout.preferredWidth: 105 }
                                Text { text: "Measured X (mm)"; font.pixelSize: 10; font.bold: true; color: Theme.textMuted; Layout.preferredWidth: 115 }
                                Text { text: "Measured Y (mm)"; font.pixelSize: 10; font.bold: true; color: Theme.textMuted; Layout.preferredWidth: 115 }
                                Item { Layout.fillWidth: true }
                                Text { text: "Deviation (Δ)"; font.pixelSize: 10; font.bold: true; color: Theme.textMuted; Layout.preferredWidth: 100 }
                            }
                        }

                        // Table Rows (9 Points)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Repeater {
                                model: 9
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    height: 29
                                    radius: 4
                                    color: (index % 2 === 0)
                                           ? (Theme.isDark ? "#0E1729" : "#F8FAFC")
                                           : "transparent"
                                    border.color: (index === 4)
                                                  ? (Theme.isDark ? "#1E2A44" : "#E2E8F0")
                                                  : "transparent"
                                    border.width: 1

                                    readonly property var locs: [
                                        "Top-Left (1)", "Top-Mid (2)", "Top-Right (3)",
                                        "Mid-Left (4)", "Center (5)",  "Mid-Right (6)",
                                        "Bot-Left (7)", "Bot-Mid (8)", "Bot-Right (9)"
                                    ]

                                    readonly property var pt: (cal && cal.measuredPoints && cal.measuredPoints.length > index)
                                                              ? cal.measuredPoints[index] : null
                                    readonly property var nom: (cal && cal.nominalPoints && cal.nominalPoints.length > index)
                                                               ? cal.nominalPoints[index] : null

                                    readonly property real curDev: (pt && nom)
                                                                   ? Math.sqrt(Math.pow(pt.x - nom.x, 2) + Math.pow(pt.y - nom.y, 2))
                                                                   : 0.0

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        spacing: 8

                                        // Badge #
                                        Rectangle {
                                            Layout.preferredWidth: 24; height: 20; radius: 3
                                            color: (index === 0) ? (Theme.isDark ? "#083344" : "#CFFAFE")
                                                 : (index === 8) ? (Theme.isDark ? "#3B0764" : "#F3E8FF")
                                                 : (Theme.isDark ? "#17233D" : "#E2E8F0")
                                            border.color: (index === 0) ? Theme.accentCyan
                                                        : (index === 8) ? "#A855F7"
                                                        : "transparent"
                                            border.width: 1
                                            Text {
                                                anchors.centerIn: parent
                                                text: (index + 1)
                                                font.bold: true
                                                font.pixelSize: 10
                                                color: (index === 0) ? Theme.accentCyan
                                                     : (index === 8) ? "#A855F7"
                                                     : Theme.textPrimary
                                            }
                                        }

                                        // Position Name
                                        Text {
                                            text: locs[index]
                                            font.pixelSize: 10
                                            font.bold: (index === 4)
                                            color: (index === 4) ? Theme.accentCyan : Theme.textPrimary
                                            Layout.preferredWidth: 105
                                        }

                                        // Measured X Input
                                        Rectangle {
                                            Layout.preferredWidth: 115
                                            height: 24; radius: 4
                                            color: (index === 1 || index === 4 || index === 7) ? (Theme.isDark ? "#0A0F1D" : "#F1F5F9") : Theme.bgInput
                                            border.color: tX.activeFocus ? Theme.borderActive : Theme.borderInput
                                            border.width: 1

                                            TextInput {
                                                id: tX
                                                anchors.fill: parent; anchors.margins: 2
                                                verticalAlignment: TextInput.AlignVCenter
                                                horizontalAlignment: TextInput.AlignHCenter
                                                font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true
                                                color: (index === 1 || index === 4 || index === 7) ? Theme.textMuted : Theme.textPrimary
                                                enabled: !(index === 1 || index === 4 || index === 7)
                                                text: (cal && cal.measuredPoints && cal.measuredPoints.length > index)
                                                      ? Number(cal.measuredPoints[index].x).toFixed(3)
                                                      : "0.000"
                                                onEditingFinished: {
                                                    var vx = parseFloat(text)
                                                    var vy = (cal && cal.measuredPoints) ? cal.measuredPoints[index].y : 0.0
                                                    if (cal && !isNaN(vx)) cal.updateMeasuredPoint(index, vx, vy)
                                                }
                                            }
                                        }

                                        // Measured Y Input
                                        Rectangle {
                                            Layout.preferredWidth: 115
                                            height: 24; radius: 4
                                            color: (index === 3 || index === 4 || index === 5) ? (Theme.isDark ? "#0A0F1D" : "#F1F5F9") : Theme.bgInput
                                            border.color: tY.activeFocus ? Theme.borderActive : Theme.borderInput
                                            border.width: 1

                                            TextInput {
                                                id: tY
                                                anchors.fill: parent; anchors.margins: 2
                                                verticalAlignment: TextInput.AlignVCenter
                                                horizontalAlignment: TextInput.AlignHCenter
                                                font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true
                                                color: (index === 3 || index === 4 || index === 5) ? Theme.textMuted : Theme.textPrimary
                                                enabled: !(index === 3 || index === 4 || index === 5)
                                                text: (cal && cal.measuredPoints && cal.measuredPoints.length > index)
                                                      ? Number(cal.measuredPoints[index].y).toFixed(3)
                                                      : "0.000"
                                                onEditingFinished: {
                                                    var vy = parseFloat(text)
                                                    var vx = (cal && cal.measuredPoints) ? cal.measuredPoints[index].x : 0.0
                                                    if (cal && !isNaN(vy)) cal.updateMeasuredPoint(index, vx, vy)
                                                }
                                            }
                                        }

                                        Item { Layout.fillWidth: true }

                                        // Live Deviation Badge (Δ)
                                        Rectangle {
                                            Layout.preferredWidth: 100
                                            height: 20; radius: 3
                                            color: (index === 4)
                                                   ? (Theme.isDark ? "#082F49" : "#E0F2FE")
                                                   : (curDev < 0.05
                                                      ? (Theme.isDark ? "#064E3B" : "#D1FAE5")
                                                      : (curDev < 0.15
                                                         ? (Theme.isDark ? "#451A03" : "#FEF3C7")
                                                         : (Theme.isDark ? "#4C0519" : "#FFE4E6")))

                                            Text {
                                                anchors.centerIn: parent
                                                text: (index === 4)
                                                      ? "Origin (0,0)"
                                                      : ("Δ: " + (curDev > 0 ? "+" : "") + curDev.toFixed(3) + " mm")
                                                font.family: "Consolas, monospace"
                                                font.pixelSize: 9
                                                font.bold: true
                                                color: (index === 4)
                                                       ? Theme.accentCyan
                                                       : (curDev < 0.05
                                                          ? Theme.accentGreen
                                                          : (curDev < 0.15 ? Theme.accentAmber : Theme.accentRed))
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }

                        // Staged Calibration Quality & Diagnostics Card
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 48
                            radius: 6
                            color: Theme.isDark ? "#0A101D" : "#F8FAFC"
                            border.color: (cal && cal.stagedIsValid) ? Theme.accentCyan : Theme.borderCard
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                spacing: 14

                                ColumnLayout {
                                    spacing: 2
                                    Text { text: "STAGING STATUS"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary }
                                    RowLayout {
                                        spacing: 6
                                        Rectangle {
                                            width: 7; height: 7; radius: 3.5
                                            color: (cal && cal.stagedIsValid) ? Theme.accentGreen : Theme.textMuted
                                        }
                                        Text {
                                            text: (cal && cal.stagedIsValid) ? "CALIBRATION STAGED" : "AWAITING FIT"
                                            font.pixelSize: 10; font.bold: true
                                            color: (cal && cal.stagedIsValid) ? Theme.accentGreen : Theme.textMuted
                                        }
                                    }
                                }

                                Rectangle { width: 1; height: 28; color: Theme.borderCard }

                                ColumnLayout {
                                    spacing: 2
                                    Text { text: "MEAN RMS FIT ERROR"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary }
                                    Text {
                                        text: (cal && cal.stagedIsValid) ? (cal.stagedAvgError.toFixed(3) + " mm RMS") : "--"
                                        font.family: "Consolas, monospace"; font.pixelSize: 11; font.bold: true
                                        color: (cal && cal.stagedIsValid) ? Theme.accentCyan : Theme.textMuted
                                    }
                                }

                                Rectangle { width: 1; height: 28; color: Theme.borderCard }

                                ColumnLayout {
                                    spacing: 2
                                    Text { text: "FIT QUALITY"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary }
                                    Text {
                                        text: (cal && cal.stagedIsValid)
                                              ? (cal.stagedAvgError < 0.03 ? "🌟 Excellent (< 0.03 mm)" : "✅ Good (< 0.08 mm)")
                                              : "Ready to Calculate"
                                        font.pixelSize: 10; font.bold: true
                                        color: (cal && cal.stagedIsValid) ? Theme.accentGreen : Theme.textMuted
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                ColumnLayout {
                                    spacing: 2
                                    Text { text: "CALIBRATED SCALE"; font.pixelSize: 9; font.bold: true; color: Theme.textSecondary }
                                    Text {
                                        text: (cal ? cal.scale.toFixed(2) : "533.89") + " bits/mm"
                                        font.family: "Consolas, monospace"; font.pixelSize: 10; font.bold: true
                                        color: Theme.textPrimary
                                    }
                                }
                            }
                        }

                        // 3-Step Execution Workflow Buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 36
                                primary: true
                                text: "⚙️ 1. Calculate & Stage .COR"
                                onClicked: if (cal) cal.calculateAndStageCalibration()
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 36
                                btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                                textColor: Theme.textPrimary
                                borderColor: Theme.borderCard
                                enabled: Boolean(cal && cal.stagedIsValid)
                                text: "📐 2. Mark Verification Box"
                                onClicked: if (cal) cal.markVerificationShape()
                            }

                            ModernButton {
                                Layout.fillWidth: true
                                implicitHeight: 36
                                btnColor: (cal && cal.stagedIsValid) ? Theme.accentGreen : (Theme.isDark ? "#1E2A44" : "#E2E8F0")
                                textColor: (cal && cal.stagedIsValid) ? "#000000" : Theme.textMuted
                                borderColor: (cal && cal.stagedIsValid) ? Theme.accentGreen : Theme.borderCard
                                enabled: Boolean(cal && cal.stagedIsValid)
                                text: "💾 3. Save & Apply .COR"
                                onClicked: if (cal) cal.saveAndApplyStagedCalibration()
                            }
                        }
                    }
                }
            }
        }

        // ================= BOTTOM STATUS BAR ================= //
        Rectangle {
            Layout.fillWidth: true
            height: 32
            radius: 5
            color: Theme.bgCard
            border.color: Theme.borderCard
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 8

                Rectangle {
                    width: 7; height: 7; radius: 3.5
                    color: (cal && cal.isMarking) ? Theme.accentAmber : Theme.accentCyan
                }

                Text {
                    text: cal ? cal.statusMessage : "Ready"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    font.bold: true
                    color: Theme.textPrimary
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                ModernButton {
                    text: "Close Window"
                    implicitHeight: 24
                    implicitWidth: 90
                    btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                    textColor: Theme.textPrimary
                    borderColor: Theme.borderCard
                    onClicked: root.requestClose()
                }
            }
        }
    }
}
