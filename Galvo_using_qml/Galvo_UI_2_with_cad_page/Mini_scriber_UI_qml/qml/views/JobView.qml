import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"

ScrollView {
    id: root
    clip: true
    ScrollBar.horizontal.policy: ScrollBar.AsNeeded
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    FileDialog {
        id: fileDialog
        title: "Select Design or G-Code File"
        nameFilters: [
            "All Supported Files (*.dxf *.gcode *.txt *.nc *.gbr *.gtl *.gbl)",
            "DXF Vector CAD (*.dxf)",
            "G-Code Programs (*.gcode *.txt *.nc *.tap *.gco)",
            "Gerber PCB Layers (*.gbr *.gtl *.gbl *.gto *.gbo *.gts *.gbs *.gml)"
        ]
        onAccepted: {
            job.loadFile(fileDialog.selectedFile.toString())
        }
    }

    Item {
        width: Math.max(root.availableWidth, 980)
        implicitHeight: mainCol.implicitHeight + 48

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: 28
            spacing: 24

            // Page Heading
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ColumnLayout {
                    spacing: 4
                    Text {
                        text: "Job & Run"
                        font.family: "Inter"
                        font.pixelSize: 26
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }
                    Text {
                        text: "Prepare design geometry, verify the toolpath and monitor execution."
                        font.family: "Inter"
                        font.pixelSize: 12
                        color: Theme.textSecondary
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: settings.machineName.toUpperCase() + "  /  CONTROL"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: Theme.textMuted
                    Layout.alignment: Qt.AlignTop
                }
            }

            // Main 2-Column Workspace
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                // Left Column: Parameters & Controls
                ColumnLayout {
                    Layout.preferredWidth: 380
                    Layout.fillHeight: true
                    spacing: 18

                    // 1. Design File Specs Card
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Design file"
                        subtitle: "DXF, Gerber or G-code"
                        accentColor: Theme.accentAmber

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: job.fileName
                                font.family: "Inter"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }

                            Rectangle {
                                width: 42
                                height: 22
                                radius: 4
                                color: Theme.isDark ? "#1E293B" : "#E9EDF9"
                                border.color: Theme.borderCard
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: {
                                        var fn = job.fileName.toUpperCase()
                                        if (fn.indexOf(".DXF") !== -1) return "DXF"
                                        if (fn.indexOf(".GBR") !== -1 || fn.indexOf(".GTL") !== -1) return "GERBER"
                                        return "G-CODE"
                                    }
                                    font.family: "Inter"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.isDark ? Theme.accentCyan : "#192D78"
                                }
                            }
                        }

                        // File Metrics Table
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Total commands"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: job.totalCommands > 0 ? job.totalCommands.toString() : "--"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Theme.textPrimary }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Dimensions"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                RowLayout {
                                    spacing: 6
                                    Text {
                                        text: job.designWidth > 0 ? (job.designWidth.toFixed(2) + " × " + job.designHeight.toFixed(2) + " mm") : "--"
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: job.isOutOfBounds ? "#EF4444" : Theme.textPrimary
                                    }
                                    Rectangle {
                                        visible: job.isOutOfBounds
                                        height: 18
                                        radius: 4
                                        color: job.isTooLarge ? Qt.rgba(239/255, 68/255, 68/255, 0.2) : Qt.rgba(214/255, 175/255, 62/255, 0.2)
                                        border.color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                                        border.width: 1
                                        implicitWidth: warnBadgeTxt.implicitWidth + 8
                                        Text {
                                            id: warnBadgeTxt
                                            anchors.centerIn: parent
                                            text: job.isTooLarge ? "TOO LARGE" : "OVERFLOW"
                                            font.family: "Inter"
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                                        }
                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: job.showBoundaryWarning()
                                        }
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Toolpath elements"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: job.totalCommands > 0 ? (job.cutCount + " cuts, " + job.travelCount + " travels") : "--"; font.family: "IBM Plex Mono"; font.pixelSize: 11; color: Theme.textSecondary }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Bounding box"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: job.designWidth > 0 ? ("X[" + job.minX.toFixed(1) + ".." + job.maxX.toFixed(1) + "] Y[" + job.minY.toFixed(1) + ".." + job.maxY.toFixed(1) + "]") : "--"; font.family: "IBM Plex Mono"; font.pixelSize: 10; color: Theme.textSecondary }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: "Print origin (index)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary; Layout.fillWidth: true }
                                Text { text: "X" + settings.xindex.toFixed(2) + " Y" + settings.yindex.toFixed(2) + " mm"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                            }

                            // Start Alignment Buttons
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                Layout.topMargin: 4

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 34
                                    radius: 6
                                    color: (job.alignmentMode === "index") ? (Theme.isDark ? "#1D4ED8" : "#192D78") : (Theme.isDark ? "#111827" : "#F8FAFC")
                                    border.color: (job.alignmentMode === "index") ? (Theme.isDark ? "#60A5FA" : "#192D78") : (Theme.isDark ? "#334155" : "#DCE2EC")
                                    border.width: (job.alignmentMode === "index") ? 1.5 : 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "Start from index"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: (job.alignmentMode === "index") ? Font.Bold : Font.Normal
                                        color: (job.alignmentMode === "index") ? "#FFFFFF" : Theme.textSecondary
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: job.setAlignmentMode("index")
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 34
                                    radius: 6
                                    color: (job.alignmentMode === "center") ? (Theme.isDark ? "#1D4ED8" : "#192D78") : (Theme.isDark ? "#111827" : "#F8FAFC")
                                    border.color: (job.alignmentMode === "center") ? (Theme.isDark ? "#60A5FA" : "#192D78") : (Theme.isDark ? "#334155" : "#DCE2EC")
                                    border.width: (job.alignmentMode === "center") ? 1.5 : 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "Center on bed"
                                        font.family: "Inter"
                                        font.pixelSize: 11
                                        font.weight: (job.alignmentMode === "center") ? Font.Bold : Font.Normal
                                        color: (job.alignmentMode === "center") ? "#FFFFFF" : Theme.textSecondary
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: job.setAlignmentMode("center")
                                    }
                                }
                            }

                            // Out of Bounds Warning Card Banner
                            Rectangle {
                                Layout.fillWidth: true
                                visible: job.isOutOfBounds
                                radius: 6
                                color: job.isTooLarge ? (Theme.isDark ? "#2A1215" : "#FEE2E2") : (Theme.isDark ? "#271C12" : "#FEF3C7")
                                border.color: job.isTooLarge ? "#EF4444" : Theme.accentAmber
                                border.width: 1
                                implicitHeight: warnCol.implicitHeight + 16

                                ColumnLayout {
                                    id: warnCol
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 6

                                    RowLayout {
                                        spacing: 6
                                        AppIcon { name: job.isTooLarge ? "block" : "warning"; size: 14; iconColor: job.isTooLarge ? "#EF4444" : Theme.accentAmber }
                                        Text {
                                            text: job.boundaryTitle ? job.boundaryTitle.toUpperCase() : "BOUNDARY WARNING"
                                            font.family: "Inter"
                                            font.pixelSize: 11
                                            font.weight: Font.Bold
                                            color: job.isTooLarge ? "#EF4444" : (Theme.isDark ? Theme.accentAmber : "#B45309")
                                        }
                                    }

                                    Text {
                                        Layout.fillWidth: true
                                        text: job.isTooLarge
                                            ? ("Design (" + job.rawDesignWidth.toFixed(1) + "×" + job.rawDesignHeight.toFixed(1) + " mm) exceeds " + settings.bedWidth.toFixed(0) + "×" + settings.bedHeight.toFixed(0) + " bed. Scale down.")
                                            : "Design exceeds bed boundaries at active index point. Laser execution locked."
                                        font.family: "Inter"
                                        font.pixelSize: 10
                                        color: Theme.textSecondary
                                        wrapMode: Text.WordWrap
                                    }

                                    RowLayout {
                                        spacing: 8
                                        AppButton {
                                            visible: job.canShiftToFit
                                            text: "⌖ Shift to Bed Center"
                                            variant: "warning"
                                            implicitHeight: 28
                                            onClicked: job.shiftToFit()
                                        }

                                        AppButton {
                                            text: "View Details"
                                            variant: "secondary"
                                            implicitHeight: 28
                                            onClicked: job.showBoundaryWarning()
                                        }
                                    }
                                }
                            }
                        }

                        AppButton {
                            Layout.fillWidth: true
                            implicitHeight: 44
                            iconName: "folder_open"
                            iconColor: Theme.isDark ? "#00E5FF" : "#FFFFFF"
                            text: "Browse design file"
                            variant: "primary"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            onClicked: fileDialog.open()
                        }
                    }

                    // 2. Scribing Parameters Card
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Scribing parameters"
                        subtitle: "Focus & feed"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            // Laser Selection
                            RowLayout {
                                spacing: 8
                                Repeater {
                                    model: settings.laserCount === 1 ? [1] : [1, 2]
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 34
                                        radius: 6
                                        property bool isSelected: (job.selectedLaser === ("Laser " + modelData) || job.selectedLaser == modelData)
                                        color: isSelected ? (Theme.isDark ? "#1D4ED8" : "#192D78") : (Theme.isDark ? "#111827" : "#F8FAFC")
                                        border.color: isSelected ? (Theme.isDark ? "#60A5FA" : "#192D78") : (Theme.isDark ? "#334155" : "#DCE2EC")
                                        border.width: isSelected ? 1.5 : 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: "Laser " + modelData
                                            font.family: "Inter"
                                            font.pixelSize: 11
                                            font.weight: isSelected ? Font.Bold : Font.Normal
                                            color: isSelected ? "#FFFFFF" : Theme.textSecondary
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: job.setSelectedLaser("Laser " + modelData)
                                        }
                                    }
                                }
                            }

                            // Sample Height & Feed Inputs
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    Text { text: "Sample height (mm)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 34
                                        radius: 6
                                        color: Theme.bgInput
                                        border.color: Theme.borderInput
                                        border.width: 1

                                        TextInput {
                                            id: sampleHeightInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: job.sampleHeight.toFixed(2)
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var val = parseFloat(text)
                                                if (!isNaN(val)) job.setSampleHeight(val)
                                            }
                                        }
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    Text { text: "Feed (mm/min)"; font.family: "Inter"; font.pixelSize: 11; color: Theme.textSecondary }
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 34
                                        radius: 6
                                        color: Theme.bgInput
                                        border.color: Theme.borderInput
                                        border.width: 1

                                        TextInput {
                                            id: feedInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 10
                                            anchors.rightMargin: 10
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: job.feedRate.toFixed(1)
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 12
                                            color: Theme.textPrimary
                                            onEditingFinished: {
                                                var val = parseFloat(text)
                                                if (!isNaN(val)) job.setFeedRate(val)
                                            }
                                        }
                                    }
                                }
                            }

                            // Focal Z Readout
                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    text: "Focal Z · Focus − sample"
                                    font.family: "Inter"
                                    font.pixelSize: 11
                                    color: Theme.textSecondary
                                }
                                Item { Layout.fillWidth: true }
                                Text {
                                    text: job.calculatedZpos.toFixed(3) + " mm"
                                    font.family: "IBM Plex Mono"
                                    font.pixelSize: 14
                                    font.weight: Font.Bold
                                    color: Theme.accentAmber
                                }
                            }

                            AppButton {
                                Layout.fillWidth: true
                                implicitHeight: 44
                                iconName: "bolt"
                                text: "Apply & re-generate G-code"
                                variant: job.fileName !== "No file loaded" ? "accent" : "secondary"
                                iconColor: job.fileName !== "No file loaded" ? "#0B1220" : Theme.textSecondary
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                enabled: job.fileName !== "No file loaded"
                                onClicked: job.processAndGenerate()
                            }
                        }
                    }

                    // 3. Job Execution Controls & Real-Time HUD
                    MetricCard {
                        Layout.fillWidth: true
                        title: "Job execution"
                        subtitle: "Closed-loop firmware tracking"
                        accentColor: Theme.accentAmber

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 14

                            // Status & Firing Header
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Rectangle {
                                    width: 9
                                    height: 9
                                    radius: 4.5
                                    color: job.state === "Running" ? Theme.accentGreen : (job.state === "Paused" ? Theme.accentAmber : Theme.textSecondary)

                                    SequentialAnimation on opacity {
                                        running: job.state === "Running"
                                        loops: Animation.Infinite
                                        PropertyAnimation { to: 0.3; duration: 600 }
                                        PropertyAnimation { to: 1.0; duration: 600 }
                                    }
                                }

                                Text {
                                    text: job.state.toUpperCase()
                                    font.family: "Inter"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: job.state === "Running" ? Theme.accentGreen : (job.state === "Paused" ? Theme.accentAmber : Theme.textPrimary)
                                }

                                Item { Layout.fillWidth: true }

                                // Active Laser Beam Badge
                                Rectangle {
                                    visible: job.state === "Running" || job.state === "Paused"
                                    height: 22
                                    radius: 11
                                    color: job.isLaserFiring ? Qt.rgba(255/255, 23/255, 68/255, 0.2) : (Theme.isDark ? "#1E293B" : "#E2E8F0")
                                    border.color: job.isLaserFiring ? "#FF1744" : Theme.borderCard
                                    border.width: 1
                                    implicitWidth: beamRow.implicitWidth + 14

                                    SequentialAnimation on opacity {
                                        running: job.isLaserFiring
                                        loops: Animation.Infinite
                                        PropertyAnimation { to: 0.5; duration: 400; easing.type: Easing.InOutQuad }
                                        PropertyAnimation { to: 1.0; duration: 400; easing.type: Easing.InOutQuad }
                                    }

                                    RowLayout {
                                        id: beamRow
                                        anchors.centerIn: parent
                                        spacing: 5
                                        AppIcon {
                                            name: job.isLaserFiring ? "flash_on" : "near_me"
                                            size: 12
                                            iconColor: job.isLaserFiring ? "#FF1744" : Theme.textSecondary
                                        }
                                        Text {
                                            text: job.isLaserFiring ? "LASER ON" : "RAPID MOVE"
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: job.isLaserFiring ? "#FF1744" : Theme.textSecondary
                                        }
                                    }
                                }
                            }

                            // Circular Progress Ring & Step Counter
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 14

                                // Radial Ring Gauge
                                Item {
                                    width: 76
                                    height: 76

                                    Canvas {
                                        id: progressRingCanvas
                                        anchors.fill: parent

                                        Connections {
                                            target: job
                                            function onProgressChanged() {
                                                if (root.visible) progressRingCanvas.requestPaint()
                                            }
                                            function onJobStateChanged() {
                                                if (root.visible) progressRingCanvas.requestPaint()
                                            }
                                        }

                                        onPaint: {
                                            var ctx = getContext("2d")
                                            ctx.reset()
                                            var cx = width / 2
                                            var cy = height / 2
                                            var radius = width / 2 - 6
                                            var prog = Math.max(0.0, Math.min(100.0, job.progress)) / 100.0

                                            // Background track
                                            ctx.lineWidth = 6
                                            ctx.strokeStyle = Theme.isDark ? "#1E293B" : "#E2E8F0"
                                            ctx.beginPath()
                                            ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
                                            ctx.stroke()

                                            // Foreground progress arc
                                            if (prog > 0) {
                                                ctx.lineWidth = 6
                                                ctx.lineCap = "round"
                                                ctx.strokeStyle = job.state === "Paused" ? Theme.accentAmber : Theme.accentGreen
                                                ctx.beginPath()
                                                ctx.arc(cx, cy, radius, -Math.PI / 2, -Math.PI / 2 + prog * 2 * Math.PI)
                                                ctx.stroke()
                                            }
                                        }
                                    }

                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 0
                                        Text {
                                            text: job.progress.toFixed(0) + "%"
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: Theme.textPrimary
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                        Text {
                                            text: "DONE"
                                            font.family: "Inter"
                                            font.pixelSize: 8
                                            font.weight: Font.Bold
                                            color: Theme.textMuted
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                    }
                                }

                                // Command Steps & Progress Bar Column
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text {
                                            text: "Command Progress"
                                            font.family: "Inter"
                                            font.pixelSize: 11
                                            color: Theme.textSecondary
                                        }
                                        Item { Layout.fillWidth: true }
                                        Text {
                                            text: job.currentCommand + " / " + (job.totalCommands > 0 ? job.totalCommands : "--")
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 11
                                            font.weight: Font.DemiBold
                                            color: Theme.textPrimary
                                        }
                                    }

                                    // Linear Progress Bar
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 6
                                        radius: 3
                                        color: Theme.isDark ? "#1E293B" : "#DCE2EC"
                                        clip: true

                                        Rectangle {
                                            id: progFill
                                            width: (job.progress / 100.0) * parent.width
                                            height: parent.height
                                            radius: 3
                                            color: job.state === "Paused" ? Theme.accentAmber : Theme.accentGreen
                                            clip: true
                                            Behavior on width { NumberAnimation { duration: 80 } }

                                            // Flowing Shimmer Light Sweep while actively running
                                            Rectangle {
                                                id: progShimmer
                                                width: 50
                                                height: parent.height
                                                visible: job.state === "Running" && progFill.width > 10
                                                gradient: Gradient {
                                                    orientation: Gradient.Horizontal
                                                    GradientStop { position: 0.0; color: "transparent" }
                                                    GradientStop { position: 0.5; color: Qt.rgba(255/255, 255/255, 255/255, 0.55) }
                                                    GradientStop { position: 1.0; color: "transparent" }
                                                }
                                                NumberAnimation on x {
                                                    loops: Animation.Infinite
                                                    running: progShimmer.visible
                                                    from: -50
                                                    to: Math.max(100, progFill.width)
                                                    duration: 1400
                                                    easing.type: Easing.Linear
                                                }
                                            }
                                        }
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text {
                                            text: "Total Est. Duration:"
                                            font.family: "Inter"
                                            font.pixelSize: 10
                                            color: Theme.textMuted
                                        }
                                        Item { Layout.fillWidth: true }
                                        Text {
                                            text: job.totalEstimatedTime
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 10
                                            font.weight: Font.DemiBold
                                            color: Theme.textSecondary
                                        }
                                    }
                                }
                            }

                            // Dual Real-Time Time Tiles (Elapsed vs Remaining ETA)
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                // Tile A: Elapsed Time
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 52
                                    radius: 6
                                    color: Theme.isDark ? "#111827" : "#F8FAFC"
                                    border.color: Theme.borderCard
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 8

                                        Rectangle {
                                            width: 32
                                            height: 32
                                            radius: 6
                                            color: Theme.isDark ? "#1E293B" : "#E2E8F0"
                                            AppIcon { anchors.centerIn: parent; name: "timer"; size: 16; iconColor: Theme.accentAmber }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 1
                                            Text {
                                                text: "ELAPSED"
                                                font.family: "Inter"
                                                font.pixelSize: 9
                                                font.weight: Font.Bold
                                                color: Theme.textMuted
                                            }
                                            Text {
                                                text: job.elapsedTime
                                                font.family: "IBM Plex Mono"
                                                font.pixelSize: 14
                                                font.weight: Font.Bold
                                                color: Theme.textPrimary
                                            }
                                        }
                                    }
                                }

                                // Tile B: Time Remaining (ETA)
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 52
                                    radius: 6
                                    color: Theme.isDark ? "#111827" : "#F8FAFC"
                                    border.color: job.state === "Running" ? Qt.rgba(0, 229/255, 255/255, 0.4) : Theme.borderCard
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 8
                                        spacing: 8

                                        Rectangle {
                                            width: 32
                                            height: 32
                                            radius: 6
                                            color: job.state === "Running" ? Qt.rgba(0, 229/255, 255/255, 0.15) : (Theme.isDark ? "#1E293B" : "#E2E8F0")
                                            AppIcon {
                                                anchors.centerIn: parent
                                                name: "hourglass_top"
                                                size: 16
                                                iconColor: job.state === "Running" ? Theme.accentCyan : Theme.accentAmber
                                            }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 1
                                            Text {
                                                text: "ETA REMAINING"
                                                font.family: "Inter"
                                                font.pixelSize: 9
                                                font.weight: Font.Bold
                                                color: Theme.textMuted
                                            }
                                            Text {
                                                text: job.remainingTime
                                                font.family: "IBM Plex Mono"
                                                font.pixelSize: 14
                                                font.weight: Font.Bold
                                                color: job.state === "Running" ? Theme.accentCyan : Theme.textPrimary
                                            }
                                        }
                                    }
                                }
                            }

                            // Execution Action Buttons
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                AppButton {
                                    Layout.fillWidth: true
                                    iconName: job.isOutOfBounds ? "block" : "play_arrow"
                                    text: job.isOutOfBounds ? "Boundary Exceeded" : "Start job"
                                    variant: job.isOutOfBounds ? "secondary" : "primary"
                                    enabled: (job.state === "Ready" || job.state === "Complete" || job.state === "Aborted") && !job.isOutOfBounds && job.totalCommands > 0
                                    onClicked: job.startJob()
                                }

                                AppButton {
                                    Layout.fillWidth: true
                                    iconName: job.state === "Paused" ? "play_arrow" : "pause"
                                    text: job.state === "Paused" ? "Resume" : "Pause"
                                    variant: "warning"
                                    enabled: job.state === "Running" || job.state === "Paused"
                                    onClicked: {
                                        if (job.state === "Running") job.pauseJob()
                                        else job.resumeJob()
                                    }
                                }
                            }

                            AppButton {
                                Layout.fillWidth: true
                                iconName: "stop_circle"
                                text: "Abort job"
                                variant: "danger"
                                enabled: job.state === "Running" || job.state === "Paused"
                                onClicked: job.abortJob()
                            }
                        }
                    }
                }

                // Right Column: 2D Vector Toolpath Preview Card
                MetricCard {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    title: "2D vector toolpath preview"
                    subtitle: settings.bedWidth.toFixed(0) + " × " + settings.bedHeight.toFixed(0) + " mm machine bed"
                    accentColor: Theme.accentAmber

                    Item {
                        id: canvasContainer
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        implicitHeight: 600
                        clip: true

                        property real zoom: 3.5
                        property real panX: 0
                        property real panY: 0
                        property real pulsePhase: 0.0

                        // Live continuous laser head tracking (NCViewer continuous gliding motion)
                        property real liveHeadX: motion.xPos
                        property real liveHeadY: motion.yPos
                        property real segStartX: motion.xPos
                        property real segStartY: motion.yPos
                        property real segEndX: motion.xPos
                        property real segEndY: motion.yPos
                        property real segDurationMs: 100
                        property double segStartTime: 0
                        property bool segIsLaser: false
                        property int activeSegIdx: -1
                        property var cachedSegments: []

                        function updateCachedSegments() {
                            cachedSegments = job.toolpathSegments || []
                        }

                        function syncActiveSegment() {
                            if (job.state !== "Running") {
                                liveHeadX = motion.xPos
                                liveHeadY = motion.yPos
                                activeSegIdx = -1
                                return
                            }
                            var segs = cachedSegments
                            if (!segs || segs.length === 0) {
                                updateCachedSegments()
                                segs = cachedSegments
                            }
                            if (!segs || segs.length === 0) return

                            var curCmd = Number(job.currentCommand)
                            var foundIdx = -1
                            for (var i = 0; i < segs.length; i++) {
                                if (Number(segs[i].cmd_idx) === curCmd) {
                                    foundIdx = i
                                    break
                                }
                            }
                            if (foundIdx >= 0) {
                                var s = segs[foundIdx]
                                activeSegIdx = foundIdx
                                segStartX = Number(s.x1)
                                segStartY = Number(s.y1)
                                segEndX = Number(s.x2)
                                segEndY = Number(s.y2)
                                segIsLaser = !!s.laser
                                var dx = segEndX - segStartX
                                var dy = segEndY - segStartY
                                var dist = Math.sqrt(dx * dx + dy * dy)
                                var feed = (s.feed && s.feed > 0) ? s.feed : (segIsLaser ? Math.max(100.0, job.feedRate) : 1000.0)
                                var spd = Math.max(1.0, feed / 60.0)
                                segDurationMs = Math.max(30.0, (dist / spd) * 1000.0)
                                segStartTime = Date.now()
                            }
                        }

                        // Ultra-responsive animation: only runs when job is running AND JobView is visible!
                        Timer {
                            id: continuousMotionTimer
                            interval: 25 // 40 FPS - silky smooth without starving the event loop
                            repeat: true
                            running: job.state === "Running" && root.visible
                            onTriggered: {
                                if (canvasContainer.activeSegIdx >= 0 && canvasContainer.segDurationMs > 0) {
                                    var elapsed = Date.now() - canvasContainer.segStartTime
                                    var t = Math.max(0.0, Math.min(1.0, elapsed / canvasContainer.segDurationMs))
                                    canvasContainer.liveHeadX = canvasContainer.segStartX + t * (canvasContainer.segEndX - canvasContainer.segStartX)
                                    canvasContainer.liveHeadY = canvasContainer.segStartY + t * (canvasContainer.segEndY - canvasContainer.segStartY)
                                } else {
                                    canvasContainer.liveHeadX = motion.xPos
                                    canvasContainer.liveHeadY = motion.yPos
                                }
                                toolpathCanvas.requestPaint()
                            }
                        }

                        NumberAnimation on pulsePhase {
                            from: 0.0
                            to: 1.0
                            duration: 1000
                            loops: Animation.Infinite
                            running: job.state === "Running" && root.visible
                        }

                        Connections {
                            target: root
                            function onVisibleChanged() {
                                if (root.visible) {
                                    if (canvasContainer.cachedSegments.length === 0 && job.totalCommands > 0) {
                                        canvasContainer.updateCachedSegments()
                                    }
                                    canvasContainer.syncActiveSegment()
                                    toolpathCanvas.requestPaint()
                                }
                            }
                        }

                        function fitToBed() {
                            if (toolpathCanvas.width < 10 || toolpathCanvas.height < 10) return
                            var pad = 40
                            var availW = toolpathCanvas.width - pad * 2
                            var availH = toolpathCanvas.height - pad * 2
                            var s = Math.min(availW / settings.bedWidth, availH / settings.bedHeight)
                            zoom = Math.max(0.5, Math.min(250.0, s))
                            panX = 0
                            panY = 0
                            toolpathCanvas.requestPaint()
                        }

                        function fitToDesign() {
                            if (toolpathCanvas.width < 10 || toolpathCanvas.height < 10) return
                            if (job.designWidth <= 0 || job.designHeight <= 0) {
                                fitToBed()
                                return
                            }
                            var pad = 60
                            var availW = toolpathCanvas.width - pad * 2
                            var availH = toolpathCanvas.height - pad * 2
                            var s = Math.min(availW / Math.max(0.1, job.designWidth), availH / Math.max(0.1, job.designHeight))
                            zoom = Math.max(0.5, Math.min(250.0, s))

                            var designCenterX = (job.minX + job.maxX) / 2.0
                            var designCenterY = (job.minY + job.maxY) / 2.0

                            var isOriginRight = (settings.originPosition === "top-right" || settings.originPosition === "bottom-right")
                            var isOriginTop = (settings.originPosition === "top-right" || settings.originPosition === "top-left")

                            panX = (isOriginRight ? 1.0 : -1.0) * (designCenterX - (settings.bedWidth / 2.0)) * zoom
                            panY = (isOriginTop ? -1.0 : 1.0) * (designCenterY - (settings.bedHeight / 2.0)) * zoom
                            toolpathCanvas.requestPaint()
                        }

                        Canvas {
                            id: toolpathCanvas
                            anchors.fill: parent

                            Connections {
                                target: job
                                function onProgressChanged() {
                                    if (root.visible) {
                                        canvasContainer.syncActiveSegment()
                                    }
                                }
                                function onJobStateChanged() {
                                    if (root.visible) {
                                        canvasContainer.syncActiveSegment()
                                        toolpathCanvas.requestPaint()
                                    }
                                }
                                function onLaserFiringChanged() {
                                    if (root.visible) toolpathCanvas.requestPaint()
                                }
                                function onTimeUpdated() {}
                                function onToolpathReady() {
                                    canvasContainer.updateCachedSegments()
                                    if (job.designWidth > 0 && job.designWidth < 35) canvasContainer.fitToDesign()
                                    else canvasContainer.fitToBed()
                                    if (root.visible) toolpathCanvas.requestPaint()
                                }
                                function onFileLoaded() {
                                    canvasContainer.updateCachedSegments()
                                    if (job.designWidth > 0 && job.designWidth < 35) canvasContainer.fitToDesign()
                                    else canvasContainer.fitToBed()
                                    if (root.visible) toolpathCanvas.requestPaint()
                                }
                            }

                            Connections {
                                target: motion
                                function onPositionChanged() {
                                    if (root.visible && job.state !== "Running") {
                                        toolpathCanvas.requestPaint()
                                    }
                                }
                            }

                            Connections {
                                target: settings
                                function onThemeChanged() {
                                    if (root.visible) toolpathCanvas.requestPaint()
                                }
                                function onOriginPositionChanged() {
                                    if (root.visible) toolpathCanvas.requestPaint()
                                }
                                function onSettingsChanged() {
                                    if (root.visible) toolpathCanvas.requestPaint()
                                    if (job.totalCommands > 0) job.processAndGenerate()
                                }
                            }

                            onWidthChanged: canvasContainer.fitToBed()
                            onHeightChanged: canvasContainer.fitToBed()
                            Component.onCompleted: canvasContainer.fitToBed()

                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.reset()

                                // Blueprint Canvas Background
                                ctx.fillStyle = "#0B1220"
                                ctx.fillRect(0, 0, width, height)

                                ctx.save()

                                var isOriginRight = (settings.originPosition === "top-right" || settings.originPosition === "bottom-right")
                                var isOriginTop = (settings.originPosition === "top-right" || settings.originPosition === "top-left")

                                var cx = width / 2.0 + canvasContainer.panX
                                var cy = height / 2.0 + canvasContainer.panY
                                ctx.translate(cx, cy)
                                ctx.scale((isOriginRight ? -1.0 : 1.0) * canvasContainer.zoom, (isOriginTop ? 1.0 : -1.0) * canvasContainer.zoom)
                                ctx.translate(-settings.bedWidth / 2.0, -settings.bedHeight / 2.0)

                                // 1. Bed Background Plate
                                ctx.fillStyle = "#0F172A"
                                ctx.fillRect(0, 0, settings.bedWidth, settings.bedHeight)

                                // 2. Bed Grid (every 10mm)
                                ctx.strokeStyle = "#1E293B"
                                ctx.lineWidth = 0.6 / canvasContainer.zoom
                                for (var gx = 10; gx < settings.bedWidth; gx += 10) {
                                    ctx.beginPath()
                                    ctx.moveTo(gx, 0); ctx.lineTo(gx, settings.bedHeight)
                                    ctx.stroke()
                                }
                                for (var gy = 10; gy < settings.bedHeight; gy += 10) {
                                    ctx.beginPath()
                                    ctx.moveTo(0, gy); ctx.lineTo(settings.bedWidth, gy)
                                    ctx.stroke()
                                }

                                // 3. Center Crosshair
                                var bcx = settings.bedWidth / 2.0
                                var bcy = settings.bedHeight / 2.0
                                ctx.strokeStyle = "#334155"
                                ctx.lineWidth = 0.8 / canvasContainer.zoom
                                ctx.beginPath()
                                ctx.moveTo(bcx - 2, bcy); ctx.lineTo(bcx + 2, bcy)
                                ctx.moveTo(bcx, bcy - 2); ctx.lineTo(bcx, bcy + 2)
                                ctx.stroke()

                                // 4. Bed Outer Border
                                if (job.isOutOfBounds) {
                                    ctx.strokeStyle = job.isTooLarge ? "#EF4444" : "#F59E0B"
                                    ctx.lineWidth = 2.2 / canvasContainer.zoom
                                } else {
                                    ctx.strokeStyle = "#475569"
                                    ctx.lineWidth = 1.2 / canvasContainer.zoom
                                }
                                ctx.strokeRect(0, 0, settings.bedWidth, settings.bedHeight)

                                // 5. Toolpath Segments with NCViewer Dynamic Color-Coding & Continuous Progress
                                var segs = canvasContainer.cachedSegments
                                if (!segs || segs.length === 0) {
                                    canvasContainer.updateCachedSegments()
                                    segs = canvasContainer.cachedSegments
                                }
                                var mx = Number(motion.xPos)
                                var my = Number(motion.yPos)
                                var isComplete = (job.state === "Complete")
                                var isRunning = (job.state === "Running")
                                var activeIdx = canvasContainer.activeSegIdx
                                var curCmd = Number(job.currentCommand)

                                // Calculate continuous laser head position along active design vector
                                var headX = isRunning ? canvasContainer.liveHeadX : mx
                                var headY = isRunning ? canvasContainer.liveHeadY : my
                                var hasActiveLaser = isRunning && (job.isLaserFiring || canvasContainer.segIsLaser)

                                if (segs && segs.length > 0) {
                                    // A. Rapid travels (Muted Slate)
                                    ctx.strokeStyle = "#475569"
                                    ctx.lineWidth = 0.8 / canvasContainer.zoom
                                    ctx.beginPath()
                                    for (var s1 = 0; s1 < segs.length; s1++) {
                                        var s_rap = segs[s1]
                                        if (!s_rap.laser) {
                                            ctx.moveTo(s_rap.x1, s_rap.y1)
                                            ctx.lineTo(s_rap.x2, s_rap.y2)
                                        }
                                    }
                                    ctx.stroke()

                                    // Active Rapid Move (highlighted when gantry is actively traversing)
                                    if (isRunning && activeIdx >= 0 && activeIdx < segs.length && !segs[activeIdx].laser) {
                                        ctx.strokeStyle = Qt.rgba(148/255, 163/255, 184/255, 0.8)
                                        ctx.lineWidth = 1.2 / canvasContainer.zoom
                                        ctx.beginPath()
                                        ctx.moveTo(segs[activeIdx].x1, segs[activeIdx].y1)
                                        ctx.lineTo(segs[activeIdx].x2, segs[activeIdx].y2)
                                        ctx.stroke()
                                    }

                                    // B. Pending Laser Cuts (Neon Cyan)
                                    // Slices active cutting segment at (headX, headY) exactly like NCViewer
                                    ctx.strokeStyle = "#00E5FF"
                                    ctx.lineWidth = 1.4 / canvasContainer.zoom
                                    ctx.beginPath()
                                    for (var s2 = 0; s2 < segs.length; s2++) {
                                        var s_pend = segs[s2]
                                        if (s_pend.laser) {
                                            if (isComplete) {
                                                continue
                                            }
                                            if (isRunning) {
                                                if (activeIdx >= 0) {
                                                    if (s2 < activeIdx) {
                                                        continue // Already cut
                                                    } else if (s2 === activeIdx) {
                                                        // Remaining unscribed segment from head to end
                                                        ctx.moveTo(headX, headY)
                                                        ctx.lineTo(s_pend.x2, s_pend.y2)
                                                    } else {
                                                        // Future cut
                                                        ctx.moveTo(s_pend.x1, s_pend.y1)
                                                        ctx.lineTo(s_pend.x2, s_pend.y2)
                                                    }
                                                } else {
                                                    var p_idx = Number(s_pend.cmd_idx)
                                                    if (!isNaN(p_idx) && p_idx < curCmd) continue
                                                    ctx.moveTo(s_pend.x1, s_pend.y1)
                                                    ctx.lineTo(s_pend.x2, s_pend.y2)
                                                }
                                            } else {
                                                // Idle / Ready: all cuts are pending cyan
                                                ctx.moveTo(s_pend.x1, s_pend.y1)
                                                ctx.lineTo(s_pend.x2, s_pend.y2)
                                            }
                                        }
                                    }
                                    ctx.stroke()

                                    // C. Completed Laser Cuts (Emerald Green)
                                    // Draws finished segments plus the scribed portion of active segment up to (headX, headY)
                                    if (isRunning || isComplete) {
                                        ctx.strokeStyle = "#10B981"
                                        ctx.lineWidth = 1.6 / canvasContainer.zoom
                                        ctx.beginPath()
                                        for (var s3 = 0; s3 < segs.length; s3++) {
                                            var s_done = segs[s3]
                                            if (s_done.laser) {
                                                if (isComplete) {
                                                    ctx.moveTo(s_done.x1, s_done.y1)
                                                    ctx.lineTo(s_done.x2, s_done.y2)
                                                } else if (isRunning) {
                                                    if (activeIdx >= 0) {
                                                        if (s3 < activeIdx) {
                                                            ctx.moveTo(s_done.x1, s_done.y1)
                                                            ctx.lineTo(s_done.x2, s_done.y2)
                                                        } else if (s3 === activeIdx) {
                                                            // Scribed portion up to head
                                                            ctx.moveTo(s_done.x1, s_done.y1)
                                                            ctx.lineTo(headX, headY)
                                                        }
                                                    } else {
                                                        var d_idx = Number(s_done.cmd_idx)
                                                        if (!isNaN(d_idx) && d_idx < curCmd) {
                                                            ctx.moveTo(s_done.x1, s_done.y1)
                                                            ctx.lineTo(s_done.x2, s_done.y2)
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        ctx.stroke()
                                    }

                                    // D. Active Laser Cutting Trail (Pulsing Ruby Red Scribed Stroke with Laser Glow)
                                    if (isRunning && activeIdx >= 0 && activeIdx < segs.length && segs[activeIdx].laser) {
                                        var activeGlow = 0.45 + 0.45 * Math.sin(canvasContainer.pulsePhase * 2 * Math.PI)
                                        ctx.strokeStyle = Qt.rgba(255/255, 23/255, 68/255, activeGlow)
                                        ctx.lineWidth = 4.2 / canvasContainer.zoom
                                        ctx.beginPath()
                                        ctx.moveTo(segs[activeIdx].x1, segs[activeIdx].y1)
                                        ctx.lineTo(headX, headY)
                                        ctx.stroke()

                                        // Focused hot core
                                        ctx.strokeStyle = "#FF1744"
                                        ctx.lineWidth = 2.0 / canvasContainer.zoom
                                        ctx.beginPath()
                                        ctx.moveTo(segs[activeIdx].x1, segs[activeIdx].y1)
                                        ctx.lineTo(headX, headY)
                                        ctx.stroke()
                                    }

                                    // Out of bounds design outline
                                    if (job.isOutOfBounds && job.rawDesignWidth > 0) {
                                        ctx.strokeStyle = job.isTooLarge ? Qt.rgba(239/255, 68/255, 68/255, 0.75) : Qt.rgba(245/255, 158/255, 11/255, 0.75)
                                        ctx.lineWidth = 1.0 / canvasContainer.zoom
                                        ctx.strokeRect(job.minX, job.minY, Math.max(0.1, job.maxX - job.minX), Math.max(0.1, job.maxY - job.minY))
                                    }
                                }

                                // 6. Animated Glowing Laser Head / Live Radar Tracking
                                var hx = headX
                                var hy = headY
                                var isFiringHead = hasActiveLaser

                                if (job.state === "Running") {
                                    // Outer expanding pulsing sonar wave
                                    var waveR = (5.0 + canvasContainer.pulsePhase * 18.0) / canvasContainer.zoom
                                    var waveAlpha = (1.0 - canvasContainer.pulsePhase) * 0.75
                                    ctx.strokeStyle = isFiringHead ? Qt.rgba(255/255, 23/255, 68/255, waveAlpha) : Qt.rgba(0/255, 229/255, 255/255, waveAlpha * 0.8)
                                    ctx.lineWidth = 1.5 / canvasContainer.zoom
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, waveR, 0, 2 * Math.PI)
                                    ctx.stroke()

                                    // Inner secondary halo
                                    var haloR = (3.0 + canvasContainer.pulsePhase * 9.0) / canvasContainer.zoom
                                    ctx.strokeStyle = isFiringHead ? Qt.rgba(255/255, 82/255, 82/255, (1.0 - canvasContainer.pulsePhase) * 0.6) : Qt.rgba(56/255, 189/255, 248/255, (1.0 - canvasContainer.pulsePhase) * 0.5)
                                    ctx.lineWidth = 1.2 / canvasContainer.zoom
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, haloR, 0, 2 * Math.PI)
                                    ctx.stroke()

                                    // Reticle Target Ring
                                    ctx.strokeStyle = Qt.rgba(255/255, 255/255, 255/255, 0.6)
                                    ctx.lineWidth = 0.8 / canvasContainer.zoom
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, 5.0 / canvasContainer.zoom, 0, 2 * Math.PI)
                                    ctx.stroke()

                                    // Crosshairs with center gap
                                    ctx.strokeStyle = isFiringHead ? "#FF1744" : "#00E5FF"
                                    ctx.lineWidth = 1.2 / canvasContainer.zoom
                                    var gap = 2.5 / canvasContainer.zoom
                                    var arm = 8.0 / canvasContainer.zoom
                                    ctx.beginPath()
                                    ctx.moveTo(hx - arm, hy); ctx.lineTo(hx - gap, hy)
                                    ctx.moveTo(hx + gap, hy); ctx.lineTo(hx + arm, hy)
                                    ctx.moveTo(hx, hy - arm); ctx.lineTo(hx, hy - gap)
                                    ctx.moveTo(hx, hy + gap); ctx.lineTo(hx, hy + arm)
                                    ctx.stroke()

                                    // Center Hot Core Dot
                                    ctx.fillStyle = isFiringHead ? "#FF1744" : "#00E5FF"
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, 2.2 / canvasContainer.zoom, 0, 2 * Math.PI)
                                    ctx.fill()

                                    ctx.fillStyle = "#FFFFFF"
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, 0.9 / canvasContainer.zoom, 0, 2 * Math.PI)
                                    ctx.fill()
                                } else {
                                    // Idle / Ready Laser Target
                                    ctx.strokeStyle = "#EF4444"
                                    ctx.lineWidth = 1.2 / canvasContainer.zoom
                                    ctx.beginPath()
                                    ctx.arc(hx, hy, 2.2, 0, 2 * Math.PI)
                                    ctx.stroke()
                                    ctx.beginPath()
                                    ctx.moveTo(hx - 3.8, hy); ctx.lineTo(hx + 3.8, hy)
                                    ctx.moveTo(hx, hy - 3.8); ctx.lineTo(hx, hy + 3.8)
                                    ctx.stroke()
                                }

                                // 7. Print Starting Index Point (Gold Amber)
                                var ix = settings.xindex
                                var iy = settings.yindex
                                ctx.strokeStyle = "#D6AF3E"
                                ctx.fillStyle = Qt.rgba(214 / 255, 175 / 255, 62 / 255, 0.25)
                                ctx.lineWidth = 1.0 / canvasContainer.zoom
                                ctx.beginPath()
                                ctx.arc(ix, iy, 2.2, 0, 2 * Math.PI)
                                ctx.fill()
                                ctx.stroke()
                                ctx.beginPath()
                                ctx.moveTo(ix - 4.0, iy); ctx.lineTo(ix + 4.0, iy)
                                ctx.moveTo(ix, iy - 4.0); ctx.lineTo(ix, iy + 4.0)
                                ctx.stroke()

                                ctx.restore()
                            }
                        }

                        // Interactive Mouse Pan & Zoom
                        MouseArea {
                            anchors.fill: parent
                            property real lastX: 0
                            property real lastY: 0

                            onPressed: function(mouse) {
                                lastX = mouse.x
                                lastY = mouse.y
                            }
                            onPositionChanged: function(mouse) {
                                if (pressed) {
                                    canvasContainer.panX += (mouse.x - lastX)
                                    canvasContainer.panY += (mouse.y - lastY)
                                    lastX = mouse.x
                                    lastY = mouse.y
                                    toolpathCanvas.requestPaint()
                                }
                            }
                            onWheel: function(wheel) {
                                if (wheel.angleDelta.y > 0) canvasContainer.zoom = Math.min(250.0, canvasContainer.zoom * 1.15)
                                else canvasContainer.zoom = Math.max(0.4, canvasContainer.zoom / 1.15)
                                toolpathCanvas.requestPaint()
                            }
                        }

                        // Top Legend (Clear Status Guide with auto-wrapping Flow)
                        Flow {
                            id: legendFlow
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: liveHudCard.visible ? liveHudCard.left : parent.right
                            anchors.margins: 14
                            anchors.rightMargin: 16
                            spacing: 12

                            RowLayout {
                                spacing: 6
                                Rectangle { width: 12; height: 3; color: "#00E5FF"; radius: 1 }
                                Text { text: "Pending Cut"; font.family: "Inter"; font.pixelSize: 10; color: "#A6B1C4" }
                            }
                            RowLayout {
                                spacing: 6
                                Rectangle { width: 12; height: 3; color: "#10B981"; radius: 1 }
                                Text { text: "Completed Cut"; font.family: "Inter"; font.pixelSize: 10; color: "#10B981" }
                            }
                            RowLayout {
                                spacing: 6
                                Rectangle { width: 12; height: 3; color: "#FF1744"; radius: 1 }
                                Text { text: "Active Firing"; font.family: "Inter"; font.pixelSize: 10; color: "#FF1744" }
                            }
                            RowLayout {
                                spacing: 6
                                Rectangle { width: 12; height: 2; color: "#475569"; radius: 1 }
                                Text { text: "Rapid Move"; font.family: "Inter"; font.pixelSize: 10; color: "#64748B" }
                            }
                            RowLayout {
                                spacing: 6
                                Rectangle { width: 7; height: 7; radius: 3.5; color: "#EF4444" }
                                Text { text: "Head (" + (job.state === "Running" ? canvasContainer.liveHeadX : motion.xPos).toFixed(1) + ", " + (job.state === "Running" ? canvasContainer.liveHeadY : motion.yPos).toFixed(1) + ")"; font.family: "Inter"; font.pixelSize: 10; color: "#A6B1C4" }
                            }
                            RowLayout {
                                spacing: 6
                                Rectangle { width: 7; height: 7; radius: 3.5; color: "#D6AF3E" }
                                Text { text: "Index (" + settings.xindex.toFixed(1) + ", " + settings.yindex.toFixed(1) + ")"; font.family: "Inter"; font.pixelSize: 10; color: "#D6AF3E" }
                            }
                        }

                        // Floating Canvas Live HUD (Top Right over canvas)
                        Rectangle {
                            id: liveHudCard
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.margins: 14
                            visible: job.totalCommands > 0
                            radius: 8
                            color: Theme.isDark ? Qt.rgba(15/255, 23/255, 42/255, 0.90) : Qt.rgba(255/255, 255/255, 255/255, 0.92)
                            border.color: job.state === "Running" ? Qt.rgba(0/255, 229/255, 255/255, 0.4) : (Theme.isDark ? "#334155" : "#CBD5E1")
                            border.width: 1
                            implicitWidth: hudColumn.implicitWidth + 24
                            implicitHeight: hudColumn.implicitHeight + 16

                            ColumnLayout {
                                id: hudColumn
                                anchors.centerIn: parent
                                spacing: 6

                                RowLayout {
                                    spacing: 8
                                    // Status Badge Pill
                                    Rectangle {
                                        height: 18
                                        implicitWidth: stateBadgeTxt.implicitWidth + 14
                                        radius: 9
                                        color: job.state === "Running" ? Qt.rgba(16/255, 185/255, 129/255, 0.2) : (job.state === "Paused" ? Qt.rgba(245/255, 158/255, 11/255, 0.2) : (job.state === "Complete" ? Qt.rgba(59/255, 130/255, 246/255, 0.2) : "#1E293B"))
                                        border.color: job.state === "Running" ? Theme.accentGreen : (job.state === "Paused" ? Theme.accentAmber : Theme.textMuted)
                                        border.width: 1

                                        Text {
                                            id: stateBadgeTxt
                                            anchors.centerIn: parent
                                            text: job.state.toUpperCase()
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: job.state === "Running" ? Theme.accentGreen : (job.state === "Paused" ? Theme.accentAmber : Theme.textSecondary)
                                        }
                                    }

                                    // Progress %
                                    Text {
                                        text: job.progress.toFixed(0) + "%"
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 12
                                        font.weight: Font.Bold
                                        color: Theme.textPrimary
                                    }

                                    // Laser Active indicator
                                    Rectangle {
                                        width: 8
                                        height: 8
                                        radius: 4
                                        color: job.isLaserFiring ? "#FF1744" : "#475569"
                                        visible: job.state === "Running"
                                    }
                                }

                                RowLayout {
                                    spacing: 12
                                    // Live ETA Countdown
                                    RowLayout {
                                        spacing: 4
                                        AppIcon { name: "hourglass_bottom"; size: 12; iconColor: Theme.accentCyan }
                                        Text {
                                            text: "ETA " + job.remainingTime
                                            font.family: "IBM Plex Mono"
                                            font.pixelSize: 10
                                            font.weight: Font.DemiBold
                                            color: Theme.accentCyan
                                        }
                                    }

                                    // Command line counter
                                    Text {
                                        text: "L " + job.currentCommand + " / " + job.totalCommands
                                        font.family: "IBM Plex Mono"
                                        font.pixelSize: 10
                                        color: Theme.textSecondary
                                    }
                                }
                            }
                        }

                        // Out of bounds alert HUD badge (Top Right over canvas, below HUD if present)
                        Rectangle {
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.topMargin: job.totalCommands > 0 ? 82 : 14
                            anchors.rightMargin: 14
                            visible: job.isOutOfBounds
                            radius: 6
                            color: job.isTooLarge ? Qt.rgba(239/255, 68/255, 68/255, 0.92) : Qt.rgba(214/255, 175/255, 62/255, 0.92)
                            border.color: "#FFFFFF"
                            border.width: 1
                            implicitWidth: oobRow.implicitWidth + 20
                            height: 30

                            RowLayout {
                                id: oobRow
                                anchors.centerIn: parent
                                spacing: 8
                                AppIcon { name: job.isTooLarge ? "block" : "warning"; size: 14; iconColor: "#FFFFFF" }
                                Text {
                                    text: job.isTooLarge ? ("DESIGN EXCEEDS " + settings.bedWidth.toFixed(0) + "×" + settings.bedHeight.toFixed(0) + " BED") : "EXCEEDS BED AT CURRENT INDEX"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: "#FFFFFF"
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: job.showBoundaryWarning()
                            }
                        }

                        // Bottom HUD Label
                        Text {
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.margins: 14
                            text: (job.alignmentMode === "index" ? "MODE: START AT INDEX (" + settings.xindex.toFixed(1) + ", " + settings.yindex.toFixed(1) + ")" : "MODE: CENTERED ON BED") + "\nDrag to pan · Wheel to zoom"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 10
                            color: Theme.accentAmber
                        }

                        // Bottom-Right Controls
                        RowLayout {
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.margins: 14
                            spacing: 8

                            Rectangle {
                                width: 30
                                height: 30
                                radius: 4
                                color: "#172338"
                                border.color: "#263550"
                                border.width: 1
                                Text { anchors.centerIn: parent; text: "+"; font.family: "Inter"; font.pixelSize: 14; font.weight: Font.Bold; color: "#FFFFFF" }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: { canvasContainer.zoom = Math.min(250.0, canvasContainer.zoom * 1.25); toolpathCanvas.requestPaint() }
                                }
                            }

                            Rectangle {
                                width: 30
                                height: 30
                                radius: 4
                                color: "#172338"
                                border.color: "#263550"
                                border.width: 1
                                Text { anchors.centerIn: parent; text: "−"; font.family: "Inter"; font.pixelSize: 14; font.weight: Font.Bold; color: "#FFFFFF" }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: { canvasContainer.zoom = Math.max(0.4, canvasContainer.zoom / 1.25); toolpathCanvas.requestPaint() }
                                }
                            }

                            Rectangle {
                                height: 30
                                implicitWidth: fitTxt.implicitWidth + 18
                                radius: 4
                                color: "#172338"
                                border.color: "#263550"
                                border.width: 1
                                visible: job.designWidth > 0
                                Text { id: fitTxt; anchors.centerIn: parent; text: "Fit design"; font.family: "Inter"; font.pixelSize: 11; color: "#FFFFFF" }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: canvasContainer.fitToDesign()
                                }
                            }

                            Rectangle {
                                height: 30
                                implicitWidth: resetTxt.implicitWidth + 18
                                radius: 4
                                color: "#172338"
                                border.color: "#263550"
                                border.width: 1
                                Text { id: resetTxt; anchors.centerIn: parent; text: "Reset view"; font.family: "Inter"; font.pixelSize: 11; color: "#FFFFFF" }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: canvasContainer.fitToBed()
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
