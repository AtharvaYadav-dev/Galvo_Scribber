import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    implicitWidth: 360
    implicitHeight: 360

    readonly property real bedWidth: settings.bedWidth
    readonly property real bedHeight: settings.bedHeight
    readonly property bool isOriginRight: (settings.originPosition === "top-right" || settings.originPosition === "bottom-right")
    readonly property bool isOriginTop: (settings.originPosition === "top-right" || settings.originPosition === "top-left")
    property real hoverX: 0.0
    property real hoverY: 0.0
    property bool isHovering: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        // Header Row: Status Indicator & Live Coordinates Pill
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Rectangle {
                width: 7
                height: 7
                radius: 3.5
                color: serial.connected ? Theme.accentGreen : Theme.accentAmber

                SequentialAnimation on opacity {
                    running: serial.connected
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.3; duration: 900 }
                    PropertyAnimation { to: 1.0; duration: 900 }
                }
            }

            Text {
                text: "RETICLE TRACKING"
                font.family: "IBM Plex Mono"
                font.pixelSize: 10
                font.weight: Font.Bold
                color: Theme.textSecondary
            }

            Item { Layout.fillWidth: true }

            // Live Coordinates Pill (Never clips)
            Rectangle {
                height: 24
                implicitWidth: coordRow.implicitWidth + 20
                radius: 5
                color: Theme.isDark ? "#111827" : "#E9EDF9"
                border.color: Theme.borderCard
                border.width: 1

                RowLayout {
                    id: coordRow
                    anchors.centerIn: parent
                    spacing: 8

                    RowLayout {
                        spacing: 4
                        Text {
                            text: "X"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.accentAmber
                        }
                        Text {
                            text: motion.xPos.toFixed(1)
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                            color: Theme.textPrimary
                        }
                    }

                    RowLayout {
                        spacing: 4
                        Text {
                            text: "Y"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.accentCyan
                        }
                        Text {
                            text: motion.yPos.toFixed(1)
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                            color: Theme.textPrimary
                        }
                    }
                }
            }
        }

        // Radar Bed Area Container (Guarantees Strict 1:1 Square Geometry)
        Item {
            id: radarBedContainer
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 200
            Layout.preferredHeight: 260
            Layout.alignment: Qt.AlignCenter

            readonly property real bedSize: Math.max(160, Math.min(width, height))

            Rectangle {
                id: radarBed
                width: radarBedContainer.bedSize
                height: radarBedContainer.bedSize
                anchors.centerIn: parent
                radius: 8
                color: Theme.isDark ? "#060A14" : "#0F172A"
                border.color: Theme.isDark ? "#1E293B" : "#334155"
                border.width: 1
                clip: true

                // Subtle Grid Lines (25mm, 50mm, 75mm)
                Repeater {
                    model: [0.25, 0.50, 0.75]
                    Rectangle {
                        x: Math.round(radarBed.width * modelData)
                        y: 0
                        width: 1
                        height: radarBed.height
                        color: modelData === 0.50 ? (Theme.isDark ? "#2A3A54" : "#475569") : (Theme.isDark ? "#131E30" : "#1E293B")
                    }
                }

                Repeater {
                    model: [0.25, 0.50, 0.75]
                    Rectangle {
                        x: 0
                        y: Math.round(radarBed.height * modelData)
                        width: radarBed.width
                        height: 1
                        color: modelData === 0.50 ? (Theme.isDark ? "#2A3A54" : "#475569") : (Theme.isDark ? "#131E30" : "#1E293B")
                    }
                }

                // Bed Origin Label Tag (0, 0) - positioned dynamically at machine origin
                Text {
                    text: "(0,0)"
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 9
                    font.weight: Font.Bold
                    color: Theme.accentGreen
                    x: root.isOriginRight ? (parent.width - width - 6) : 6
                    y: root.isOriginTop ? 6 : (parent.height - height - 6)
                    opacity: 0.85

                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                    Behavior on y { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                }

                // Bed Max Label Tag - positioned at opposite diagonal corner
                Text {
                    text: Math.round(settings.bedWidth) + "×" + Math.round(settings.bedHeight)
                    font.family: "IBM Plex Mono"
                    font.pixelSize: 9
                    font.weight: Font.Bold
                    color: "#64748B"
                    x: root.isOriginRight ? 6 : (parent.width - width - 6)
                    y: root.isOriginTop ? (parent.height - height - 6) : 6
                    opacity: 0.85

                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                    Behavior on y { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                }

                // Center Datum Marker (50, 50)
                Rectangle {
                    width: 12
                    height: 12
                    radius: 6
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: Theme.accentAmber
                    border.width: 1
                    opacity: 0.65

                    Rectangle {
                        width: 2
                        height: 2
                        radius: 1
                        anchors.centerIn: parent
                        color: Theme.accentAmber
                    }
                }

                // Mouse Hover Crosshair Lines
                Rectangle {
                    id: hoverVLine
                    visible: root.isHovering
                    x: hoverMa.mouseX
                    y: 0
                    width: 1
                    height: parent.height
                    color: Qt.rgba(0, 0.89, 1, 0.45)
                }
                Rectangle {
                    id: hoverHLine
                    visible: root.isHovering
                    x: 0
                    y: hoverMa.mouseY
                    width: parent.width
                    height: 1
                    color: Qt.rgba(0, 0.89, 1, 0.45)
                }

                // Interactive Toolhead Reticle
                Item {
                    id: reticle
                    width: 24
                    height: 24

                    // Map Cartesian coordinates to visual pixels based on physical origin
                    readonly property real clampedX: Math.max(0.0, Math.min(settings.bedWidth, motion.xPos))
                    readonly property real clampedY: Math.max(0.0, Math.min(settings.bedHeight, motion.yPos))
                    readonly property real normX: clampedX / settings.bedWidth
                    readonly property real normY: clampedY / settings.bedHeight

                    x: (root.isOriginRight ? (1.0 - normX) : normX) * (radarBed.width - width)
                    y: (root.isOriginTop ? normY : (1.0 - normY)) * (radarBed.height - height)

                    Behavior on x { NumberAnimation { duration: 120; easing.type: Easing.OutQuad } }
                    Behavior on y { NumberAnimation { duration: 120; easing.type: Easing.OutQuad } }

                    // Outer Pulsing Ring
                    Rectangle {
                        id: pulseRing
                        anchors.centerIn: parent
                        width: 20
                        height: 20
                        radius: 10
                        color: "transparent"
                        border.color: laser.laserActive ? "#EF4444" : Theme.accentCyan
                        border.width: 1.5

                        SequentialAnimation on scale {
                            loops: Animation.Infinite
                            running: true
                            NumberAnimation { from: 1.0; to: 1.35; duration: 900; easing.type: Easing.OutQuad }
                            NumberAnimation { from: 1.35; to: 1.0; duration: 900; easing.type: Easing.InQuad }
                        }
                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            running: true
                            NumberAnimation { from: 0.9; to: 0.3; duration: 900 }
                            NumberAnimation { from: 0.3; to: 0.9; duration: 900 }
                        }
                    }

                    // High-Energy Expanding Shockwave Aura Ring (Active when laser is firing)
                    Rectangle {
                        id: laserFiringAura
                        anchors.centerIn: parent
                        width: 20
                        height: 20
                        radius: 10
                        visible: laser.laserActive
                        color: "transparent"
                        border.color: "#FF3366"
                        border.width: 2

                        SequentialAnimation on scale {
                            loops: Animation.Infinite
                            running: laser.laserActive
                            NumberAnimation { from: 0.8; to: 2.8; duration: 750; easing.type: Easing.OutCubic }
                        }
                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            running: laser.laserActive
                            NumberAnimation { from: 0.95; to: 0.0; duration: 750; easing.type: Easing.OutQuad }
                        }
                    }

                    // Inner Crosshair Reticle Icon
                    Text {
                        anchors.centerIn: parent
                        text: "⌖"
                        font.pixelSize: 18
                        color: laser.laserActive ? "#F87171" : Theme.accentCyan
                    }

                    // Laser Spot Center Dot
                    Rectangle {
                        width: 4
                        height: 4
                        radius: 2
                        anchors.centerIn: parent
                        color: laser.laserActive ? "#EF4444" : Theme.accentAmber
                    }
                }

                // Hover Coordinate Tooltip
                Rectangle {
                    visible: root.isHovering
                    x: Math.min(Math.max(4, hoverMa.mouseX + 12), radarBed.width - width - 4)
                    y: Math.min(Math.max(4, hoverMa.mouseY - 24), radarBed.height - height - 4)
                    width: hoverText.implicitWidth + 12
                    height: 22
                    radius: 4
                    color: Theme.isDark ? "#0F172A" : "#FFFFFF"
                    border.color: Theme.accentCyan
                    border.width: 1

                    Text {
                        id: hoverText
                        anchors.centerIn: parent
                        text: root.hoverX.toFixed(1) + ", " + root.hoverY.toFixed(1) + " mm"
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 9
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }
                }

                // Interactive Click-To-Drive Mouse Area
                MouseArea {
                    id: hoverMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.CrossCursor

                    onPositionChanged: function(mouse) {
                        root.isHovering = true
                        var rx = Math.max(0.0, Math.min(1.0, mouse.x / radarBed.width))
                        var ry = Math.max(0.0, Math.min(1.0, mouse.y / radarBed.height))
                        var normX = root.isOriginRight ? (1.0 - rx) : rx
                        var normY = root.isOriginTop ? ry : (1.0 - ry)
                        root.hoverX = normX * settings.bedWidth
                        root.hoverY = normY * settings.bedHeight
                    }

                    onExited: {
                        root.isHovering = false
                    }

                    onClicked: function(mouse) {
                        var rx = Math.max(0.0, Math.min(1.0, mouse.x / radarBed.width))
                        var ry = Math.max(0.0, Math.min(1.0, mouse.y / radarBed.height))
                        var normX = root.isOriginRight ? (1.0 - rx) : rx
                        var normY = root.isOriginTop ? ry : (1.0 - ry)
                        var targetX = Math.round(normX * settings.bedWidth * 10) / 10
                        var targetY = Math.round(normY * settings.bedHeight * 10) / 10
                        motion.moveToCoordinates(targetX, targetY)
                    }
                }
            }
        }

        // Quick Preset Target Buttons (Origin, Center, Park)
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            // Origin Button
            Rectangle {
                Layout.fillWidth: true
                height: 28
                radius: 5
                color: origMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.1) : (origMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                border.color: Theme.borderInput
                border.width: 1

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 4
                    Text { text: "⌂"; font.pixelSize: 11; color: Theme.accentGreen }
                    Text { text: "Origin (0,0)"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.DemiBold; color: Theme.textPrimary }
                }

                MouseArea {
                    id: origMa
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onClicked: motion.moveToCoordinates(0.0, 0.0)
                }
            }

            // Center Button
            Rectangle {
                Layout.fillWidth: true
                height: 28
                radius: 5
                color: ctrMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.1) : (ctrMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                border.color: Theme.borderInput
                border.width: 1

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 4
                    AppIcon { name: "my_location"; size: 12; iconColor: Theme.accentCyan }
                    Text { text: "Center (" + (settings.bedWidth/2.0).toFixed(0) + "," + (settings.bedHeight/2.0).toFixed(0) + ")"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.DemiBold; color: Theme.textPrimary }
                }

                MouseArea {
                    id: ctrMa
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onClicked: motion.centerXY()
                }
            }

            // Park Button
            Rectangle {
                Layout.fillWidth: true
                height: 28
                radius: 5
                color: parkMa.down ? Qt.darker(Theme.btnSecondaryBg, 1.1) : (parkMa.containsMouse ? Theme.btnSecondaryHover : Theme.btnSecondaryBg)
                border.color: Theme.borderInput
                border.width: 1

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 4
                    Text { text: "🅿"; font.pixelSize: 10 }
                    Text { text: "Park (" + (settings.bedWidth/2.0).toFixed(0) + ",0)"; font.family: "Inter"; font.pixelSize: 10; font.weight: Font.DemiBold; color: Theme.textPrimary }
                }

                MouseArea {
                    id: parkMa
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onClicked: motion.park()
                }
            }
        }

        // Direct Coordinate Input Row
        Rectangle {
            Layout.fillWidth: true
            height: 36
            radius: 6
            color: Theme.isDark ? "#111827" : "#F1F5F9"
            border.color: Theme.borderCard
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                spacing: 6

                Text {
                    text: "Drive to:"
                    font.family: "Inter"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                    color: Theme.textSecondary
                }

                Text { text: "X"; font.family: "IBM Plex Mono"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.accentAmber }

                Rectangle {
                    width: 52
                    height: 24
                    radius: 4
                    color: Theme.isDark ? "#060A14" : "#FFFFFF"
                    border.color: targetXInput.activeFocus ? Theme.accentAmber : Theme.borderInput
                    border.width: 1

                    TextInput {
                        id: targetXInput
                        anchors.fill: parent
                        anchors.margins: 3
                        text: motion.xPos.toFixed(1)
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        verticalAlignment: TextInput.AlignVCenter
                        horizontalAlignment: TextInput.AlignHCenter
                        selectByMouse: true
                    }
                }

                Text { text: "Y"; font.family: "IBM Plex Mono"; font.pixelSize: 10; font.weight: Font.Bold; color: Theme.accentCyan }

                Rectangle {
                    width: 52
                    height: 24
                    radius: 4
                    color: Theme.isDark ? "#060A14" : "#FFFFFF"
                    border.color: targetYInput.activeFocus ? Theme.accentCyan : Theme.borderInput
                    border.width: 1

                    TextInput {
                        id: targetYInput
                        anchors.fill: parent
                        anchors.margins: 3
                        text: motion.yPos.toFixed(1)
                        font.family: "IBM Plex Mono"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        verticalAlignment: TextInput.AlignVCenter
                        horizontalAlignment: TextInput.AlignHCenter
                        selectByMouse: true
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    width: 54
                    height: 24
                    radius: 4
                    color: driveMa.down ? Qt.darker(Theme.btnPrimaryBg, 1.15) : (driveMa.containsMouse ? Theme.btnPrimaryHover : Theme.btnPrimaryBg)
                    border.color: Theme.btnPrimaryBorder
                    border.width: 1

                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 3
                        Text {
                            text: "GO"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: "#FFFFFF"
                        }
                        AppIcon {
                            name: "arrow_forward"
                            size: 11
                            iconColor: "#FFFFFF"
                        }
                    }

                    MouseArea {
                        id: driveMa
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onClicked: {
                            var px = parseFloat(targetXInput.text)
                            var py = parseFloat(targetYInput.text)
                            if (!isNaN(px) && !isNaN(py)) {
                                motion.moveToCoordinates(px, py)
                            }
                        }
                    }
                }
            }
        }
    }
}
