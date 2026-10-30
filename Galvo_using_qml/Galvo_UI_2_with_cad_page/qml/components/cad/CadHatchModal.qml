import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var profiles: ({
        "1": {
            "enable": true, "all_calc": false, "follow_edge": false, "cross_hatch": false,
            "type": "Bidirectional", "angle": 45.0, "pen_no": 0, "count": 1, "line_space": 0.03,
            "avg_dist": false, "edge_off": 0.0, "start_off": 0.0, "end_off": 0.0, "line_red": 0.0,
            "num_loops": 0, "loop_dist": 0.5, "auto_rot": false, "rot_angle": 10.0
        },
        "2": {
            "enable": false, "all_calc": false, "follow_edge": false, "cross_hatch": false,
            "type": "Bidirectional", "angle": 0.0, "pen_no": 0, "count": 1, "line_space": 0.05,
            "avg_dist": false, "edge_off": 0.0, "start_off": 0.0, "end_off": 0.0, "line_red": 0.0,
            "num_loops": 0, "loop_dist": 0.5, "auto_rot": false, "rot_angle": 10.0
        },
        "3": {
            "enable": false, "all_calc": false, "follow_edge": false, "cross_hatch": false,
            "type": "Bidirectional", "angle": 0.0, "pen_no": 0, "count": 1, "line_space": 0.05,
            "avg_dist": false, "edge_off": 0.0, "start_off": 0.0, "end_off": 0.0, "line_red": 0.0,
            "num_loops": 0, "loop_dist": 0.5, "auto_rot": false, "rot_angle": 10.0
        }
    })

    property int currentProfileIdx: 1
    property bool markContour: true
    property bool markContourFirst: true
    property var targetShape: null
    property string currentHatchType: "Bidirectional"
    property bool profileEnabled: true

    signal applyHatch(var profiles, bool markContour, bool markContourFirst)
    signal undoHatch()
    signal closed()

    // Backward-compatible signal
    signal applyHatchLegacy(real distance, real angle, bool cross, real offset, string pattern)

    function openModal(shp) {
        targetShape = shp || null
        if (typeof cad !== "undefined" && cad) {
            var all = cad.getAllHatchProfiles()
            if (all) {
                if (all["1"]) profiles["1"] = Object.assign({}, all["1"])
                if (all["2"]) profiles["2"] = Object.assign({}, all["2"])
                if (all["3"]) profiles["3"] = Object.assign({}, all["3"])
                if (all["mark_contour"] !== undefined) markContour = all["mark_contour"]
                if (all["mark_contour_first"] !== undefined) markContourFirst = all["mark_contour_first"]
            }
        }

        var shapePen = (shp && shp.penId !== undefined) ? shp.penId : 0
        if (shp && shp.hatch_profiles) {
            for (var k in shp.hatch_profiles) {
                if (profiles[k]) {
                    profiles[k] = Object.assign({}, shp.hatch_profiles[k])
                }
            }
            if (shp.mark_contour !== undefined) markContour = shp.mark_contour
            if (shp.mark_contour_first !== undefined) markContourFirst = shp.mark_contour_first
        } else {
            // Adopt shape's pen by default for active profiles
            for (var pk in profiles) {
                profiles[pk].pen_no = shapePen
            }
        }

        currentProfileIdx = 1
        loadProfileFields(1)
        if (root.width > 0 && root.height > 0) {
            modalCard.x = Math.max(10, Math.round((root.width - modalCard.width) / 2))
            modalCard.y = Math.max(10, Math.round((root.height - modalCard.height) / 2))
        }
        root.visible = true
    }

    function close() {
        root.visible = false
        root.closed()
    }

    function saveCurrentProfileFields() {
        var strIdx = currentProfileIdx.toString()
        if (!profiles[strIdx]) profiles[strIdx] = {}
        var p = profiles[strIdx]
        p.enable = root.profileEnabled
        p.all_calc = allCalcCheck.checked
        p.follow_edge = followEdgeCheck.checked
        p.cross_hatch = crossHatchCheck.checked
        p.type = currentHatchType
        p.angle = parseFloat(angleInput.text) || 0.0
        p.pen_no = penSelector.selectedPenId
        p.count = parseInt(countInput.text) || 1
        p.line_space = parseFloat(lineSpaceInput.text) || 0.03
        p.avg_dist = avgDistCheck.checked
        p.edge_off = parseFloat(edgeOffInput.text) || 0.0
        p.start_off = parseFloat(startOffInput.text) || 0.0
        p.end_off = parseFloat(endOffInput.text) || 0.0
        p.line_red = parseFloat(lineRedInput.text) || 0.0
        p.num_loops = parseInt(numLoopsInput.text) || 0
        p.loop_dist = parseFloat(loopDistInput.text) || 0.5
        p.auto_rot = autoRotCheck.checked
        p.rot_angle = parseFloat(rotAngleInput.text) || 10.0
    }

    function loadProfileFields(idx) {
        var strIdx = idx.toString()
        var p = profiles[strIdx]
        if (!p) return

        root.profileEnabled = !!p.enable
        allCalcCheck.checked = !!p.all_calc
        followEdgeCheck.checked = !!p.follow_edge
        crossHatchCheck.checked = !!p.cross_hatch

        currentHatchType = p.type || "Bidirectional"

        angleInput.text = (p.angle !== undefined) ? p.angle.toString() : "45.0"
        var sPen = (targetShape && targetShape.penId !== undefined) ? targetShape.penId : 0
        penSelector.selectedPenId = (p.pen_no !== undefined) ? p.pen_no : sPen
        countInput.text = (p.count !== undefined) ? p.count.toString() : "1"
        lineSpaceInput.text = (p.line_space !== undefined) ? p.line_space.toString() : "0.03"
        avgDistCheck.checked = !!p.avg_dist
        edgeOffInput.text = (p.edge_off !== undefined) ? p.edge_off.toString() : "0.00"
        startOffInput.text = (p.start_off !== undefined) ? p.start_off.toString() : "0.00"
        endOffInput.text = (p.end_off !== undefined) ? p.end_off.toString() : "0.00"
        lineRedInput.text = (p.line_red !== undefined) ? p.line_red.toString() : "0.00"
        numLoopsInput.text = (p.num_loops !== undefined) ? p.num_loops.toString() : "0"
        loopDistInput.text = (p.loop_dist !== undefined) ? p.loop_dist.toString() : "0.50"
        autoRotCheck.checked = !!p.auto_rot
        rotAngleInput.text = (p.rot_angle !== undefined) ? p.rot_angle.toString() : "10.0"

        typePreviewCanvas.requestPaint()
    }

    function switchProfile(newIdx) {
        if (newIdx === currentProfileIdx) return
        saveCurrentProfileFields()
        currentProfileIdx = newIdx
        loadProfileFields(newIdx)
    }

    function applyAndClose() {
        saveCurrentProfileFields()

        if (typeof cad !== "undefined" && cad) {
            cad.saveAllHatchProfiles(profiles, markContour, markContourFirst)
        }

        root.applyHatch(profiles, markContour, markContourFirst)

        var curP = profiles[currentProfileIdx.toString()] || {}
        root.applyHatchLegacy(
            parseFloat(curP.line_space) || 0.03,
            parseFloat(curP.angle) || 45.0,
            !!curP.cross_hatch,
            parseFloat(curP.edge_off) || 0.0,
            curP.type || "Bidirectional"
        )

        root.close()
    }

    function applyOnly() {
        saveCurrentProfileFields()

        if (typeof cad !== "undefined" && cad) {
            cad.saveAllHatchProfiles(profiles, markContour, markContourFirst)
        }

        root.applyHatch(profiles, markContour, markContourFirst)

        var curP = profiles[currentProfileIdx.toString()] || {}
        root.applyHatchLegacy(
            parseFloat(curP.line_space) || 0.03,
            parseFloat(curP.angle) || 45.0,
            !!curP.cross_hatch,
            parseFloat(curP.edge_off) || 0.0,
            curP.type || "Bidirectional"
        )
    }

    function undoHatchAndClose() {
        root.undoHatch()
        root.close()
    }

    anchors.fill: parent
    color: "transparent"
    z: 100

    focus: visible
    Keys.onEscapePressed: root.close()

    onWidthChanged: {
        if (width > 0 && modalCard.x + modalCard.width > width - 10) {
            modalCard.x = Math.max(10, width - modalCard.width - 10)
        }
    }
    onHeightChanged: {
        if (height > 0 && modalCard.y + modalCard.height > height - 10) {
            modalCard.y = Math.max(10, height - modalCard.height - 10)
        }
    }

    // Full Backdrop Blocker: Absorbs all clicks, drags, hover, and wheel events so background is never affected
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        preventStealing: true
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onWheel: function(wheel) { wheel.accepted = true }
        onPressed: function(mouse) { mouse.accepted = true }
        onReleased: function(mouse) { mouse.accepted = true }
        onClicked: function(mouse) { mouse.accepted = true }
        onDoubleClicked: function(mouse) { mouse.accepted = true }
        onPositionChanged: function(mouse) { mouse.accepted = true }
    }

    // Modern Studio Card Window (Movable floating card)
    Rectangle {
        id: modalCard
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: Math.min(840, Math.max(540, root.width > 0 ? (root.width - 40) : 780))
        height: Math.min(680, Math.max(450, root.height > 0 ? (root.height - 40) : 600))
        radius: 12
        color: Theme.bgCard
        border.color: Theme.accentCyan
        border.width: 1.5

        // Prevent click-through and consume unhandled wheel events within the modal card
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            onWheel: function(wheel) { wheel.accepted = true }
            onPressed: function(mouse) { mouse.accepted = true }
            onReleased: function(mouse) { mouse.accepted = true }
            onClicked: function(mouse) { mouse.accepted = true }
            onDoubleClicked: function(mouse) { mouse.accepted = true }
        }

        WheelHandler {
            target: null
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            onWheel: function(event) {
                event.accepted = true
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // ================= 1. STUDIO HEADER (Draggable) =================
            Item {
                Layout.fillWidth: true
                implicitHeight: headerRow.implicitHeight

                // Drag Area on header
                MouseArea {
                    id: headerDrag
                    anchors.fill: parent
                    drag.target: modalCard
                    drag.minimumX: -modalCard.width + 100
                    drag.maximumX: root.width - 100
                    drag.minimumY: 0
                    drag.maximumY: root.height - 50
                    cursorShape: Qt.SizeAllCursor
                }

                RowLayout {
                    id: headerRow
                    anchors.fill: parent
                    spacing: 10

                    // Sleek Geometric Hatch Studio Icon
                    Rectangle {
                        width: 32; height: 32; radius: 8
                        color: Qt.rgba(0, 0.9, 1, 0.12)
                        border.color: Theme.accentCyan
                        border.width: 1

                        Canvas {
                            anchors.fill: parent
                            anchors.margins: 6
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)
                                ctx.strokeStyle = Theme.accentCyan
                                ctx.lineWidth = 1.4
                                for (var i = 0; i < width + height; i += 5) {
                                    ctx.beginPath()
                                    ctx.moveTo(i, 0)
                                    ctx.lineTo(i - height, height)
                                    ctx.stroke()
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        spacing: 1
                        RowLayout {
                            spacing: 8
                            Text {
                                text: "Laser Hatch Studio"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 16
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            Rectangle {
                                height: 18
                                width: 84
                                radius: 9
                                color: Qt.rgba(0, 0.9, 1, 0.15)
                                border.color: Theme.accentCyan
                                border.width: 1
                                Text {
                                    anchors.centerIn: parent
                                    text: "3-PASS ENGINE"
                                    font.family: "Segoe UI, Inter"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.accentCyan
                                }
                            }
                        }
                        Text {
                            text: "Multi-profile vector infill, perimeter contour sequencing & motion optimization"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            color: Theme.textSecondary
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Rectangle {
                        width: 28; height: 28; radius: 6
                        z: 2
                        color: closeMa.containsMouse ? (Theme.isDark ? "#334155" : "#E2E8F0") : "transparent"
                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: closeMa.containsMouse ? Theme.accentCyan : Theme.textSecondary
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
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderMuted }

            // Scrollable Content View for responsive scaling
            ScrollView {
                id: hatchScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 0
                Layout.preferredHeight: 0
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    width: hatchScrollView.availableWidth
                    spacing: 12

                    // ================= 2. TOP COMMAND STRIP =================
                    GridLayout {
                        Layout.fillWidth: true
                        columns: (modalCard.width >= 720) ? 2 : 1
                        columnSpacing: 10
                        rowSpacing: 8

                // Global Boundary Contour Card
                Rectangle {
                    Layout.preferredWidth: (modalCard.width >= 720) ? 280 : -1
                    Layout.fillWidth: (modalCard.width < 720)
                    Layout.preferredHeight: 48
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 10

                        // Mark Contour Toggle
                        RowLayout {
                            spacing: 8
                            Rectangle {
                                width: 18; height: 18; radius: 4
                                color: root.markContour ? Theme.accentCyan : Theme.bgInput
                                border.color: root.markContour ? Theme.accentCyan : Theme.borderInput
                                border.width: 1.5
                                Text {
                                    anchors.centerIn: parent
                                    text: "✓"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: "#08101C"
                                    visible: root.markContour
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.markContour = !root.markContour
                                }
                            }

                            ColumnLayout {
                                spacing: 1
                                Text {
                                    text: "Mark Contour"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                    color: Theme.textPrimary
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.markContour = !root.markContour }
                                }
                                Text {
                                    text: root.markContour ? "Boundary active" : "Boundary skipped"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    color: root.markContour ? Theme.accentCyan : Theme.textMuted
                                }
                            }
                        }

                        Item { Layout.fillWidth: true }

                        // Sequence Order Pill
                        Rectangle {
                            width: 96
                            height: 26
                            radius: 5
                            color: seqMa.containsMouse ? Theme.bgCardHover : Theme.bgInput
                            border.color: Theme.borderActive
                            border.width: 1

                            ToolTip.visible: seqMa.containsMouse
                            ToolTip.text: root.markContourFirst ? "Contour marked FIRST before hatching" : "Contour marked LAST after hatching"
                            ToolTip.delay: 200

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                    text: root.markContourFirst ? "1st" : "2nd"
                                    font.family: "Segoe UI, Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: Theme.accentCyan
                                }
                                Text {
                                    text: root.markContourFirst ? "Pre-Hatch" : "Post-Hatch"
                                    font.family: "Segoe UI, Inter"
                                    font.pixelSize: 10
                                    color: Theme.textSecondary
                                }
                            }

                            MouseArea {
                                id: seqMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.markContourFirst = !root.markContourFirst
                            }
                        }
                    }
                }

                // Profile Selector Tabs (Hatch 1, 2, 3)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        spacing: 8

                        Repeater {
                            model: [
                                { idx: 1, name: "Hatch Profile 1", shortName: "Hatch 1" },
                                { idx: 2, name: "Hatch Profile 2", shortName: "Hatch 2" },
                                { idx: 3, name: "Hatch Profile 3", shortName: "Hatch 3" }
                            ]

                            delegate: Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                radius: 6
                                color: root.currentProfileIdx === modelData.idx
                                    ? Theme.accentCyan
                                    : (tabMa.containsMouse ? Theme.bgCardHover : Theme.bgInput)
                                border.color: root.currentProfileIdx === modelData.idx ? Theme.accentCyan : Theme.borderInput
                                border.width: 1

                                RowLayout {
                                    anchors.centerIn: parent
                                    spacing: 6

                                    Rectangle {
                                        width: 8; height: 8; radius: 4
                                        color: (root.profiles[modelData.idx.toString()] && root.profiles[modelData.idx.toString()].enable)
                                            ? "#10B981" : "#64748B"
                                    }

                                    Text {
                                        text: (modalCard.width < 780 && modalCard.width >= 720) ? modelData.shortName : modelData.name
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: root.currentProfileIdx === modelData.idx ? Font.Bold : Font.DemiBold
                                        color: root.currentProfileIdx === modelData.idx ? "#08101C" : Theme.textPrimary
                                        elide: Text.ElideRight
                                    }
                                }

                                MouseArea {
                                    id: tabMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.switchProfile(modelData.idx)
                                }
                            }
                        }
                    }
                }
            }

            // ================= 3. TWO-COLUMN BALANCED STUDIO BODY =================
            GridLayout {
                Layout.fillWidth: true
                columns: (modalCard.width >= 700) ? 2 : 1
                columnSpacing: 12
                rowSpacing: 12

                // ---------------- LEFT CARD: INFILL PATTERN & PEN CONFIGURATION ----------------
                Rectangle {
                    id: leftCard
                    Layout.fillWidth: true
                    implicitHeight: Math.max(420, leftCol.implicitHeight + 28)
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        id: leftCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // Header + Enable Toggle
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "1. INFILL PATTERN & LASER PEN"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                font.letterSpacing: 0.5
                                color: Theme.accentCyan
                            }

                            Item { Layout.fillWidth: true }

                            // Enable Profile Switch
                            RowLayout {
                                spacing: 6
                                Text {
                                    text: root.profileEnabled ? "ENABLED" : "DISABLED"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: root.profileEnabled ? "#10B981" : Theme.textMuted
                                }
                                Rectangle {
                                    width: 34; height: 18; radius: 9
                                    color: root.profileEnabled ? "#10B981" : Theme.borderMuted

                                    Rectangle {
                                        x: root.profileEnabled ? 17 : 2
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 14; height: 14; radius: 7
                                        color: "#FFFFFF"
                                        Behavior on x { NumberAnimation { duration: 120 } }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.profileEnabled = !root.profileEnabled
                                    }
                                }
                            }
                        }

                        // Pattern Selector Grid (4 Buttons) + Preview Canvas
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 2
                                rowSpacing: 6
                                columnSpacing: 6

                                Repeater {
                                    model: [
                                        { id: "Bidirectional", name: "Bidirectional" },
                                        { id: "Unidirectional", name: "Unidirectional" },
                                        { id: "Ring", name: "Concentric Ring" },
                                        { id: "Bow", name: "Eulerian Bow" }
                                    ]

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 28
                                        radius: 4
                                        color: root.currentHatchType === modelData.id
                                            ? (Theme.isDark ? "#1C2A48" : "#E0E7FF")
                                            : (pTypeMa.containsMouse ? Theme.bgCardHover : Theme.bgInput)
                                        border.color: root.currentHatchType === modelData.id ? Theme.accentCyan : Theme.borderInput
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.name
                                            font.family: "Segoe UI, Inter, sans-serif"
                                            font.pixelSize: 11
                                            font.weight: root.currentHatchType === modelData.id ? Font.Bold : Font.Normal
                                            color: root.currentHatchType === modelData.id ? Theme.accentCyan : Theme.textPrimary
                                        }

                                        MouseArea {
                                            id: pTypeMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                root.currentHatchType = modelData.id
                                                typePreviewCanvas.requestPaint()
                                            }
                                        }
                                    }
                                }
                            }

                            // Dynamic Visual Preview Box
                            Rectangle {
                                Layout.preferredWidth: 62
                                Layout.preferredHeight: 62
                                radius: 6
                                color: Theme.bgInput
                                border.color: Theme.borderActive
                                border.width: 1

                                Canvas {
                                    id: typePreviewCanvas
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    onPaint: {
                                        var ctx = getContext("2d")
                                        ctx.clearRect(0, 0, width, height)
                                        var curType = root.currentHatchType

                                        if (curType === "Bidirectional") {
                                            ctx.lineWidth = 1.2
                                            var rows = 4
                                            var step = height / (rows + 1)
                                            for (var r = 1; r <= rows; r++) {
                                                var y = r * step
                                                var goRight = (r % 2 === 1)
                                                ctx.strokeStyle = goRight ? "#38BDF8" : "#EF4444"
                                                ctx.beginPath()
                                                ctx.moveTo(4, y); ctx.lineTo(width - 4, y); ctx.stroke()
                                                ctx.fillStyle = ctx.strokeStyle
                                                ctx.beginPath()
                                                if (goRight) {
                                                    ctx.moveTo(width - 4, y); ctx.lineTo(width - 8, y - 2.5); ctx.lineTo(width - 8, y + 2.5)
                                                } else {
                                                    ctx.moveTo(4, y); ctx.lineTo(8, y - 2.5); ctx.lineTo(8, y + 2.5)
                                                }
                                                ctx.fill()
                                            }
                                        } else if (curType === "Unidirectional") {
                                            ctx.lineWidth = 1.2
                                            ctx.strokeStyle = "#38BDF8"; ctx.fillStyle = "#38BDF8"
                                            for (var r = 1; r <= 3; r++) {
                                                var y = r * (height / 4)
                                                ctx.beginPath()
                                                ctx.moveTo(4, y); ctx.lineTo(width - 4, y); ctx.stroke()
                                                ctx.beginPath()
                                                ctx.moveTo(width - 4, y); ctx.lineTo(width - 8, y - 2.5); ctx.lineTo(width - 8, y + 2.5); ctx.fill()
                                            }
                                        } else if (curType === "Ring") {
                                            ctx.lineWidth = 1.2
                                            ctx.strokeStyle = "#10B981"
                                            for (var d = 4; d <= 16; d += 5) {
                                                ctx.strokeRect(d, d * 0.7, width - d * 2, height - d * 1.4)
                                            }
                                        } else {
                                            ctx.lineWidth = 1.2
                                            ctx.strokeStyle = "#F59E0B"
                                            ctx.beginPath()
                                            ctx.moveTo(4, 4); ctx.lineTo(width - 4, 4)
                                            ctx.lineTo(width - 4, height / 2); ctx.lineTo(4, height / 2)
                                            ctx.lineTo(4, height - 4); ctx.lineTo(width - 4, height - 4)
                                            ctx.stroke()
                                        }
                                    }
                                }
                            }
                        }

                        // Primary Infill Parameters (2 Columns with generous widths)
                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 10

                            CadInput {
                                id: angleInput
                                Layout.fillWidth: true
                                label: "Angle"
                                unit: "°"
                                text: "45.0"
                            }

                            CadInput {
                                id: lineSpaceInput
                                Layout.fillWidth: true
                                label: "Pitch"
                                unit: "mm"
                                text: "0.03"
                            }

                            CadInput {
                                id: countInput
                                Layout.fillWidth: true
                                label: "Passes"
                                unit: "x"
                                text: "1"
                            }

                            // Pen Selector (Industrial Dropdown)
                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32

                                Rectangle {
                                    id: penSelector
                                    property int selectedPenId: 0
                                    anchors.fill: parent
                                    radius: 5
                                    color: Theme.bgInput
                                    border.color: penPopup.visible ? Theme.borderActive : Theme.borderInput
                                    border.width: 1

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        spacing: 6

                                        Text {
                                            text: "Laser Pen"
                                            font.family: "Segoe UI, Inter, sans-serif"
                                            font.pixelSize: 11
                                            font.weight: Font.DemiBold
                                            color: Theme.textSecondary
                                        }

                                        Rectangle {
                                            width: 14; height: 14; radius: 3
                                            color: (typeof Theme !== "undefined" && Theme.getPenColor) ? Theme.getPenColor(penSelector.selectedPenId) : "#000000"
                                            border.color: "#475569"; border.width: 1
                                        }

                                        Text {
                                            text: "Pen " + penSelector.selectedPenId
                                            font.family: "Segoe UI, Inter, sans-serif"
                                            font.pixelSize: 11
                                            font.weight: Font.Bold
                                            color: Theme.textPrimary
                                            Layout.fillWidth: true
                                        }

                                        Text { text: "▼"; font.pixelSize: 9; color: Theme.textSecondary }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: penPopup.open()
                                    }

                                    Popup {
                                        id: penPopup
                                        y: penSelector.height + 4
                                        width: penSelector.width
                                        padding: 4
                                        background: Rectangle {
                                            color: Theme.bgCard
                                            border.color: Theme.borderCard
                                            border.width: 1
                                            radius: 6
                                        }

                                        ColumnLayout {
                                            spacing: 3
                                            Repeater {
                                                model: (typeof Theme !== "undefined" && Theme.penPalette) ? Theme.penPalette : 8
                                                delegate: Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.preferredHeight: 24
                                                    radius: 4
                                                    color: penItemMa.containsMouse ? Theme.bgCardHover : "transparent"

                                                    RowLayout {
                                                        anchors.fill: parent
                                                        anchors.leftMargin: 8
                                                        spacing: 8
                                                        Rectangle {
                                                            width: 12; height: 12; radius: 3
                                                            color: modelData.color
                                                            border.color: "#475569"; border.width: 1
                                                        }
                                                        Text {
                                                            text: modelData.name || ("Pen " + modelData.id)
                                                            font.family: "Segoe UI, Inter"
                                                            font.pixelSize: 11
                                                            font.weight: Font.DemiBold
                                                            color: Theme.textPrimary
                                                        }
                                                    }

                                                    MouseArea {
                                                        id: penItemMa
                                                        anchors.fill: parent
                                                        hoverEnabled: true
                                                        cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            penSelector.selectedPenId = modelData.id
                                                            penPopup.close()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Advanced Boolean Calculation Toggles
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            // Cross Hatch Checkbox
                            RowLayout {
                                spacing: 8
                                Rectangle {
                                    width: 16; height: 16; radius: 3
                                    color: crossHatchCheck.checked ? Theme.accentCyan : Theme.bgInput
                                    border.color: crossHatchCheck.checked ? Theme.accentCyan : Theme.borderInput
                                    border.width: 1.5
                                    Text { anchors.centerIn: parent; text: "✓"; font.pixelSize: 11; font.weight: Font.Bold; color: "#08101C"; visible: crossHatchCheck.checked }
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: crossHatchCheck.checked = !crossHatchCheck.checked }
                                }
                                Text { text: "Enable 90° Cross Hatch (Bi-directional grid)"; font.pixelSize: 11; color: Theme.textPrimary; MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: crossHatchCheck.checked = !crossHatchCheck.checked } }
                                Item { id: crossHatchCheck; property bool checked: false }
                            }

                            // All Calc Checkbox
                            RowLayout {
                                spacing: 8
                                Rectangle {
                                    width: 16; height: 16; radius: 3
                                    color: allCalcCheck.checked ? Theme.accentCyan : Theme.bgInput
                                    border.color: allCalcCheck.checked ? Theme.accentCyan : Theme.borderInput
                                    border.width: 1.5
                                    Text { anchors.centerIn: parent; text: "✓"; font.pixelSize: 11; font.weight: Font.Bold; color: "#08101C"; visible: allCalcCheck.checked }
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: allCalcCheck.checked = !allCalcCheck.checked }
                                }
                                Text { text: "All Calc (Union overlapping shapes)"; font.pixelSize: 11; color: Theme.textPrimary; MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: allCalcCheck.checked = !allCalcCheck.checked } }
                                Item { id: allCalcCheck; property bool checked: false }
                            }

                            // Follow Edge Checkbox
                            RowLayout {
                                spacing: 8
                                Rectangle {
                                    width: 16; height: 16; radius: 3
                                    color: followEdgeCheck.checked ? Theme.accentCyan : Theme.bgInput
                                    border.color: followEdgeCheck.checked ? Theme.accentCyan : Theme.borderInput
                                    border.width: 1.5
                                    Text { anchors.centerIn: parent; text: "✓"; font.pixelSize: 11; font.weight: Font.Bold; color: "#08101C"; visible: followEdgeCheck.checked }
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: followEdgeCheck.checked = !followEdgeCheck.checked }
                                }
                                Text { text: "Follow Edge Once (Perimeter boundary cleanup)"; font.pixelSize: 11; color: Theme.textPrimary; MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: followEdgeCheck.checked = !followEdgeCheck.checked } }
                                Item { id: followEdgeCheck; property bool checked: false }
                            }

                            // Average Distribute Checkbox
                            RowLayout {
                                spacing: 8
                                Rectangle {
                                    width: 16; height: 16; radius: 3
                                    color: avgDistCheck.checked ? Theme.accentCyan : Theme.bgInput
                                    border.color: avgDistCheck.checked ? Theme.accentCyan : Theme.borderInput
                                    border.width: 1.5
                                    Text { anchors.centerIn: parent; text: "✓"; font.pixelSize: 11; font.weight: Font.Bold; color: "#08101C"; visible: avgDistCheck.checked }
                                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: avgDistCheck.checked = !avgDistCheck.checked }
                                }
                                Text { text: "Average Distribute Lines across geometry"; font.pixelSize: 11; color: Theme.textPrimary; MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: avgDistCheck.checked = !avgDistCheck.checked } }
                                Item { id: avgDistCheck; property bool checked: false }
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                // ---------------- RIGHT CARD: OFFSETS, LOOPS & ROTATION ----------------
                Rectangle {
                    id: rightCard
                    Layout.fillWidth: true
                    implicitHeight: Math.max(420, rightCol.implicitHeight + 28)
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        id: rightCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // Section 2: Boundary Offsets
                        Text {
                            text: "2. BOUNDARY OFFSETS & TRIMMING"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            font.letterSpacing: 0.5
                            color: Theme.accentCyan
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 10

                            CadInput {
                                id: edgeOffInput
                                Layout.fillWidth: true
                                label: "Edge Offset"
                                unit: "mm"
                                text: "0.00"
                            }

                            CadInput {
                                id: lineRedInput
                                Layout.fillWidth: true
                                label: "Line Reduction"
                                unit: "mm"
                                text: "0.00"
                            }

                            CadInput {
                                id: startOffInput
                                Layout.fillWidth: true
                                label: "Start Offset"
                                unit: "mm"
                                text: "0.00"
                            }

                            CadInput {
                                id: endOffInput
                                Layout.fillWidth: true
                                label: "End Offset"
                                unit: "mm"
                                text: "0.00"
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderMuted }

                        // Section 3: Concentric Loops
                        Text {
                            text: "3. CONCENTRIC PERIMETER LOOPS"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            font.letterSpacing: 0.5
                            color: Theme.accentCyan
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 10

                            CadInput {
                                id: numLoopsInput
                                Layout.fillWidth: true
                                label: "NumLoops"
                                unit: "loops"
                                text: "0"
                            }

                            CadInput {
                                id: loopDistInput
                                Layout.fillWidth: true
                                label: "Loop Distance"
                                unit: "mm"
                                text: "0.50"
                            }
                        }

                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderMuted }

                        // Section 4: Multi-Pass Angle Rotation
                        Text {
                            text: "4. MULTI-PASS ANGLE ROTATION"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            font.letterSpacing: 0.5
                            color: Theme.accentCyan
                        }

                        // Auto-Rotate Options
                        RowLayout {
                            spacing: 8
                            Rectangle {
                                width: 16; height: 16; radius: 3
                                color: autoRotCheck.checked ? Theme.accentCyan : Theme.bgInput
                                border.color: autoRotCheck.checked ? Theme.accentCyan : Theme.borderInput
                                border.width: 1.5
                                Text { anchors.centerIn: parent; text: "✓"; font.pixelSize: 11; font.weight: Font.Bold; color: "#08101C"; visible: autoRotCheck.checked }
                                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: autoRotCheck.checked = !autoRotCheck.checked }
                            }
                            Text { text: "Auto-Rotate Hatch Angle per Pass"; font.pixelSize: 11; color: Theme.textPrimary; MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: autoRotCheck.checked = !autoRotCheck.checked } }
                            Item { id: autoRotCheck; property bool checked: false }
                        }

                        CadInput {
                            id: rotAngleInput
                            Layout.fillWidth: true
                            label: "Rotation Increment"
                            unit: "°"
                            text: "10.0"
                            enabled: autoRotCheck.checked
                            opacity: autoRotCheck.checked ? 1.0 : 0.5
                        }

                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
    }

            // ================= 4. STUDIO ACTION FOOTER =================
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 40
                    elide: Text.ElideRight
                    text: "Active: " + root.currentHatchType + " (" + angleInput.text + "°, " + lineSpaceInput.text + "mm) | Contour: " + (root.markContour ? (root.markContourFirst ? "ON (Pre)" : "ON (Post)") : "OFF")
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                }

                Rectangle {
                    implicitWidth: 95
                    implicitHeight: 34
                    radius: 6
                    color: undoFooterMa.containsMouse ? Qt.rgba(1, 0, 0, 0.15) : "transparent"
                    border.color: "#EF4444"
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "Undo Hatch"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: "#EF4444"
                    }

                    MouseArea {
                        id: undoFooterMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.undoHatchAndClose()
                    }
                }

                Rectangle {
                    implicitWidth: 70
                    implicitHeight: 34
                    radius: 6
                    color: cancelFooterMa.containsMouse ? Theme.bgCardHover : Theme.bgInput
                    border.color: Theme.borderCard
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "Cancel"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                    }

                    MouseArea {
                        id: cancelFooterMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.close()
                    }
                }

                // Live Apply (updates background canvas without closing dialog)
                Rectangle {
                    implicitWidth: 70
                    implicitHeight: 34
                    radius: 6
                    color: applyOnlyFooterMa.containsMouse ? (Theme.isDark ? "#1E2A44" : "#DBEAFE") : Theme.bgInput
                    border.color: Theme.accentCyan
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "Apply"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.accentCyan
                    }

                    MouseArea {
                        id: applyOnlyFooterMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.applyOnly()
                    }
                    ToolTip.visible: applyOnlyFooterMa.containsMouse
                    ToolTip.text: "Apply hatching to preview immediately on background canvas"
                }

                Rectangle {
                    implicitWidth: 80
                    implicitHeight: 34
                    radius: 6
                    color: applyFooterMa.containsMouse ? Qt.lighter(Theme.accentCyan, 1.1) : Theme.accentCyan

                    Text {
                        anchors.centerIn: parent
                        text: "OK"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: "#08101C"
                    }

                    MouseArea {
                        id: applyFooterMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.applyAndClose()
                    }
                }
            }
        }

        // Responsive Resize Handle (Drag bottom-right corner or edges to resize)
        CadWindowResizeHandle {
            target: modalCard
            minWidth: 540
            minHeight: 420
        }
    }
}
