import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property int penId: 0
    property string originalColor: "#00E5FF"
    property string selectedColor: "#00E5FF"
    property string penName: ""
    property bool isOpened: false

    signal colorConfirmed(int penId, string newColor, string newName)

    anchors.fill: parent
    color: "#66000000"
    visible: isOpened
    z: 220

    // Converts Hue (0-360), Saturation (0-100), Lightness (0-100) to Hex "#RRGGBB"
    function hslToHex(h, s, l) {
        l /= 100;
        var a = s * Math.min(l, 1 - l) / 100;
        var f = function(n) {
            var k = (n + h / 30) % 12;
            var color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
            return Math.round(255 * color).toString(16).padStart(2, '0');
        };
        return ("#" + f(0) + f(8) + f(4)).toUpperCase();
    }

    // 48 Curated Industrial Laser Layer Colors (8 columns x 6 rows)
    readonly property var industrialPalette: [
        // Row 1: Grayscale & Foundations
        "#FFFFFF", "#F8FAFC", "#E2E8F0", "#94A3B8", "#64748B", "#334155", "#1E293B", "#000000",
        // Row 2: Vibrant High-Visibility Layers
        "#EF4444", "#F97316", "#F59E0B", "#EAB308", "#84CC16", "#10B981", "#06B6D4", "#3B82F6",
        // Row 3: Deep Saturated Industrial Tones
        "#DC2626", "#EA580C", "#D97706", "#CA8A04", "#65A30D", "#059669", "#0891B2", "#2563EB",
        // Row 4: Violets, Purples & Magentas
        "#6366F1", "#8B5CF6", "#A855F7", "#D946EF", "#EC4899", "#F43F5E", "#E11D48", "#BE185D",
        // Row 5: Dark Anneal, Cutting & Deep Engrave
        "#991B1B", "#9A3412", "#92400E", "#854D0E", "#3F6212", "#065F46", "#155E75", "#1E40AF",
        // Row 6: Bright Laser Neons & Accents
        "#FCA5A5", "#FDBA74", "#FDE047", "#BEF264", "#6EE7B7", "#67E8F9", "#93C5FD", "#C4B5FD"
    ]

    function openModal(id, currentColor, name) {
        penId = id
        originalColor = currentColor || "#00E5FF"
        selectedColor = currentColor || "#00E5FF"
        penName = name || ("Pen " + id)
        hexInput.text = selectedColor.toUpperCase()

        if (root.width > 0 && root.height > 0) {
            modalBox.x = Math.max(10, Math.round((root.width - modalBox.width) / 2))
            modalBox.y = Math.max(10, Math.round((root.height - modalBox.height) / 2))
        }
        isOpened = true
    }

    function closeModal() {
        isOpened = false
    }

    function applySelection() {
        colorConfirmed(penId, selectedColor, penName)
        closeModal()
    }

    // Backdrop Blocker: Absorbs all mouse, drag, hover, and wheel events
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        preventStealing: true
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onWheel: function(wheel) { wheel.accepted = true }
        onPressed: function(mouse) { mouse.accepted = true }
        onReleased: function(mouse) { mouse.accepted = true }
        onClicked: root.closeModal()
    }

    // Modal Floating Window
    Rectangle {
        id: modalBox
        width: 480
        implicitHeight: contentCol.implicitHeight + 36
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
            id: contentCol
            anchors.fill: parent
            anchors.margins: 18
            spacing: 14

            // Header (Draggable)
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 36
                height: 36

                RowLayout {
                    id: headerRow
                    anchors.fill: parent
                    spacing: 10

                    Rectangle {
                        width: 32
                        height: 32
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        CadIcon {
                            anchors.centerIn: parent
                            name: "palette"
                            size: 18
                            color: Theme.accentCyan
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Layout.fillWidth: true

                        Text {
                            text: "Laser Pen Color Palette"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "Choose a standard layer color, slide the hue spectrum, or input a custom hex code"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            color: Theme.textMuted
                        }
                    }

                    Rectangle {
                        width: 28
                        height: 28
                        radius: 14
                        color: closeMa.containsMouse ? (Theme.isDark ? "#2A1720" : "#FEE2E2") : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 12
                            color: closeMa.containsMouse ? Theme.accentRed : Theme.textMuted
                        }

                        MouseArea {
                            id: closeMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.closeModal()
                        }
                    }
                }

                DragHandler {
                    target: modalBox
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.borderCard
            }

            // Pen Badge, Name and Comparison Row
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 52
                radius: 8
                color: Theme.bgCardAlt
                border.color: Theme.borderCard
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 12

                    // Pen ID Badge
                    Rectangle {
                        width: 34
                        height: 34
                        radius: 17
                        color: root.selectedColor
                        border.color: "#FFFFFF"
                        border.width: 2

                        Text {
                            anchors.centerIn: parent
                            text: root.penId.toString()
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: (root.selectedColor.toUpperCase() === "#FFFFFF" || root.selectedColor.toUpperCase() === "#F8FAFC" || root.selectedColor.toUpperCase() === "#E2E8F0" || root.selectedColor.toUpperCase() === "#FDE047") ? "#000000" : "#FFFFFF"
                        }
                    }

                    // Pen Name Input
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "PEN NAME / LAYER LABEL"
                            font.pixelSize: 9
                            font.bold: true
                            color: Theme.textMuted
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 24
                            radius: 4
                            color: Theme.bgInput
                            border.color: penNameInput.activeFocus ? Theme.accentCyan : Theme.borderInput
                            border.width: 1

                            TextInput {
                                id: penNameInput
                                anchors.fill: parent
                                anchors.leftMargin: 6
                                anchors.rightMargin: 6
                                verticalAlignment: TextInput.AlignVCenter
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.bold: true
                                color: Theme.textPrimary
                                text: root.penName
                                onTextChanged: root.penName = text
                            }
                        }
                    }

                    // Color Comparison: Original vs New
                    RowLayout {
                        spacing: 8

                        ColumnLayout {
                            spacing: 2
                            Text { text: "ORIGINAL"; font.pixelSize: 8; font.bold: true; color: Theme.textMuted }
                            Rectangle {
                                width: 36
                                height: 22
                                radius: 4
                                color: root.originalColor
                                border.color: Theme.borderCard
                                border.width: 1
                            }
                        }

                        Text { text: "→"; font.pixelSize: 14; font.bold: true; color: Theme.textMuted }

                        ColumnLayout {
                            spacing: 2
                            Text { text: "SELECTED"; font.pixelSize: 8; font.bold: true; color: Theme.accentCyan }
                            Rectangle {
                                width: 36
                                height: 22
                                radius: 4
                                color: root.selectedColor
                                border.color: Theme.accentCyan
                                border.width: 1.5
                            }
                        }
                    }
                }
            }

            // 1. Curated Industrial Palette Grid (48 colors)
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: "INDUSTRIAL LASER COLOR PALETTE (48 PRESETS)"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: Theme.textMuted
                    font.letterSpacing: 0.5
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 8
                    columnSpacing: 6
                    rowSpacing: 6

                    Repeater {
                        model: root.industrialPalette

                        delegate: Rectangle {
                            id: swatchTile
                            Layout.fillWidth: true
                            height: 28
                            radius: 5
                            color: modelData
                            border.color: (root.selectedColor.toUpperCase() === modelData.toUpperCase()) ? Theme.accentCyan : (Theme.isDark ? "#2E3B55" : "#CBD5E1")
                            border.width: (root.selectedColor.toUpperCase() === modelData.toUpperCase()) ? 2.5 : 1

                            scale: swatchMa.containsMouse ? 1.15 : 1.0
                            z: swatchMa.containsMouse ? 10 : 1
                            Behavior on scale { NumberAnimation { duration: 80 } }

                            // Checkmark / dot indicator when selected
                            Rectangle {
                                visible: root.selectedColor.toUpperCase() === modelData.toUpperCase()
                                anchors.centerIn: parent
                                width: 8
                                height: 8
                                radius: 4
                                color: (modelData.toUpperCase() === "#FFFFFF" || modelData.toUpperCase() === "#F8FAFC" || modelData.toUpperCase() === "#E2E8F0" || modelData.toUpperCase() === "#FDE047") ? "#000000" : "#FFFFFF"
                            }

                            MouseArea {
                                id: swatchMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    root.selectedColor = modelData.toUpperCase()
                                    hexInput.text = root.selectedColor
                                }
                            }

                            ToolTip.visible: swatchMa.containsMouse
                            ToolTip.text: modelData.toUpperCase()
                        }
                    }
                }
            }

            // 2. Interactive Continuous Rainbow Spectrum Slider
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        text: "CONTINUOUS HUE SPECTRUM (0° TO 360°)"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: Theme.textMuted
                        font.letterSpacing: 0.5
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: "Drag along bar"
                        font.pixelSize: 9
                        color: Theme.textMuted
                    }
                }

                Rectangle {
                    id: hueBar
                    Layout.fillWidth: true
                    height: 22
                    radius: 11
                    border.color: Theme.borderCard
                    border.width: 1

                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.00; color: "#FF0000" }
                        GradientStop { position: 0.17; color: "#FFFF00" }
                        GradientStop { position: 0.33; color: "#00FF00" }
                        GradientStop { position: 0.50; color: "#00FFFF" }
                        GradientStop { position: 0.67; color: "#0000FF" }
                        GradientStop { position: 0.83; color: "#FF00FF" }
                        GradientStop { position: 1.00; color: "#FF0000" }
                    }

                    // Draggable Hue Handle
                    Rectangle {
                        id: hueHandle
                        width: 14
                        height: 26
                        radius: 4
                        anchors.verticalCenter: parent.verticalCenter
                        color: root.selectedColor
                        border.color: "#FFFFFF"
                        border.width: 2
                        x: Math.max(0, Math.min(parent.width - width, (parent.width - width) * (hueSliderMa.currentPos / (parent.width || 1))))
                    }

                    MouseArea {
                        id: hueSliderMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        property real currentPos: 0

                        function updateFromMouse(mouseX) {
                            var clampedX = Math.max(0, Math.min(width, mouseX))
                            currentPos = clampedX
                            var hueFraction = clampedX / (width || 1)
                            var hueDeg = Math.round(hueFraction * 360)
                            var hex = root.hslToHex(hueDeg, 100, 50)
                            root.selectedColor = hex
                            hexInput.text = hex
                        }

                        onPressed: function(mouse) { updateFromMouse(mouse.x) }
                        onPositionChanged: function(mouse) {
                            if (pressed) updateFromMouse(mouse.x)
                        }
                    }
                }
            }

            // 3. Custom Hex Code Input Row
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Text {
                    text: "Custom Hex:"
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.textSecondary
                }

                Rectangle {
                    width: 120
                    height: 30
                    radius: 5
                    color: Theme.bgInput
                    border.color: hexInput.activeFocus ? Theme.accentCyan : Theme.borderInput
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        spacing: 4

                        Text {
                            text: "#"
                            font.family: "Consolas, monospace"
                            font.pixelSize: 12
                            font.bold: true
                            color: Theme.textMuted
                        }

                        TextInput {
                            id: hexInput
                            Layout.fillWidth: true
                            verticalAlignment: TextInput.AlignVCenter
                            font.family: "Consolas, monospace"
                            font.pixelSize: 12
                            font.bold: true
                            color: Theme.textPrimary
                            text: root.selectedColor.replace("#", "")
                            maximumLength: 7
                            selectByMouse: true

                            onTextChanged: {
                                var val = text.trim()
                                if (!val.startsWith("#")) val = "#" + val
                                if (val.length === 7 && /^#[0-9A-Fa-f]{6}$/.test(val)) {
                                    root.selectedColor = val.toUpperCase()
                                }
                            }
                        }
                    }
                }

                // Swatch indicator of typed hex
                Rectangle {
                    width: 30
                    height: 30
                    radius: 5
                    color: root.selectedColor
                    border.color: Theme.borderCard
                    border.width: 1
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "Active Pen " + root.penId
                    font.pixelSize: 11
                    font.bold: true
                    color: Theme.accentCyan
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.borderCard
            }

            // Action Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                CadButton {
                    text: "Cancel"
                    variant: "secondary"
                    implicitWidth: 100
                    onClicked: root.closeModal()
                }

                Item { Layout.fillWidth: true }

                CadButton {
                    text: "Apply Color to Pen " + root.penId
                    variant: "primary"
                    iconName: "check"
                    implicitWidth: 180
                    onClicked: root.applySelection()
                }
            }
        }
    }
}
