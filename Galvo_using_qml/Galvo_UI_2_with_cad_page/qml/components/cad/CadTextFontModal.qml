import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var targetShape: null
    property bool isOpened: false

    // State properties cloned from targetShape
    property string selectedFontFamily: "Segoe UI"
    property string textAlign: "center" // left, center, right
    property bool isBold: false
    property bool isItalic: false
    property string orientation: "horizontal" // horizontal, vertical
    property real charWidthPct: 100.0
    property real slantAngle: 0.0
    property real charSpaceMm: 0.0
    property real lineSpaceMm: 0.0
    property real emptyCharWidthPct: 100.0

    // CircleText Properties
    property bool isCircleText: false
    property real circleDiameterMm: 20.0
    property real circleBaseAngleDeg: 90.0
    property bool angleRangeLimitEnabled: false
    property real angleRangeLimitDeg: 360.0

    signal settingsApplied(var updatedProps)

    anchors.fill: parent
    color: "transparent"
    visible: isOpened
    z: 200

    function openModal(shape) {
        targetShape = shape
        if (shape) {
            textAlign = shape.textAlign || "center"
            isBold = Boolean(shape.bold)
            isItalic = Boolean(shape.italic)
            orientation = shape.orientation || "horizontal"
            charWidthPct = (shape.charWidthPct !== undefined) ? Number(shape.charWidthPct) : 100.0
            slantAngle = (shape.angle !== undefined) ? Number(shape.angle) : 0.0
            charSpaceMm = (shape.charSpace !== undefined) ? Number(shape.charSpace) : 0.0
            lineSpaceMm = (shape.lineSpace !== undefined) ? Number(shape.lineSpace) : 0.0
            emptyCharWidthPct = (shape.emptyCharWidthPct !== undefined) ? Number(shape.emptyCharWidthPct) : 100.0

            isCircleText = Boolean(shape.circleText)
            circleDiameterMm = (shape.circleDiameter !== undefined) ? Number(shape.circleDiameter) : 20.0
            circleBaseAngleDeg = (shape.circleBaseAngle !== undefined) ? Number(shape.circleBaseAngle) : 90.0
            angleRangeLimitEnabled = Boolean(shape.angleRangeLimitEnabled)
            angleRangeLimitDeg = (shape.circleAngleLimit !== undefined) ? Number(shape.circleAngleLimit) : 360.0
        }
        if (root.width > 0 && root.height > 0) {
            modalBox.x = Math.max(10, Math.round((root.width - modalBox.width) / 2))
            modalBox.y = Math.max(10, Math.round((root.height - modalBox.height) / 2))
        }
        isOpened = true
    }

    function closeModal() {
        isOpened = false
    }

    function gatherProps() {
        return {
            fontFamily: selectedFontFamily,
            textAlign: textAlign,
            bold: isBold,
            italic: isItalic,
            orientation: orientation,
            charWidthPct: charWidthPct,
            angle: slantAngle,
            charSpace: charSpaceMm,
            lineSpace: lineSpaceMm,
            emptyCharWidthPct: emptyCharWidthPct,
            circleText: isCircleText,
            circleDiameter: circleDiameterMm,
            circleBaseAngle: circleBaseAngleDeg,
            angleRangeLimitEnabled: angleRangeLimitEnabled,
            circleAngleLimit: angleRangeLimitDeg
        }
    }

    function applySettings() {
        var props = gatherProps()
        root.settingsApplied(props)
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

    // Modal Card (Movable floating card)
    Rectangle {
        id: modalBox
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: Math.min(620, Math.max(560, root.width > 0 ? (root.width - 40) : 620))
        height: Math.min(580, root.height > 0 ? (root.height - 40) : 580)
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

            // 1. Header (Draggable)
            Item {
                Layout.fillWidth: true
                implicitHeight: headerRow.implicitHeight

                MouseArea {
                    id: fontHeaderDrag
                    anchors.fill: parent
                    drag.target: modalBox
                    drag.minimumX: -modalBox.width + 100
                    drag.maximumX: root.width - 100
                    drag.minimumY: 0
                    drag.maximumY: root.height - 50
                    cursorShape: Qt.SizeAllCursor
                }

                RowLayout {
                    id: headerRow
                    anchors.fill: parent
                    spacing: 8

                    Rectangle {
                        width: 28
                        height: 28
                        radius: 6
                        color: Theme.isDark ? "#172647" : "#EFF6FF"
                        border.color: Theme.accentCyan
                        border.width: 1
                        Text {
                            anchors.centerIn: parent
                            text: "F"
                            font.bold: true
                            font.pixelSize: 13
                            color: Theme.accentCyan
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Font & CircleText Configuration"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "EZCad typography, shear angle & circular projection"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            color: Theme.textMuted
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Close X Button
                    Rectangle {
                        width: 26
                        height: 26
                        radius: 13
                        z: 2
                        color: closeMa.containsMouse ? (Theme.isDark ? "#2A3756" : "#E2E8F0") : "transparent"
                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            font.pixelSize: 12
                            color: Theme.textMuted
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
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.borderCard
            }

            // Scrollable Settings Body
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    width: Math.max(540, modalBox.width - 48)
                    spacing: 14

                    // 1. Font Family & Typeface Card (Searchable)
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: fontFaceRow.implicitHeight + 16
                        radius: 8
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        RowLayout {
                            id: fontFaceRow
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 12

                            Text {
                                text: "FONT FACE"
                                font.pixelSize: 9
                                font.weight: Font.Bold
                                color: Theme.textMuted
                                Layout.preferredWidth: 80
                            }

                            CadComboBox {
                                id: modalFontCombo
                                objectName: "modalFontCombo"
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                searchable: true
                                searchPlaceholder: "Search font face (e.g. Arial, Times)..."
                                model: (typeof cad !== "undefined" && cad) ? cad.availableFonts : ["Segoe UI", "Arial", "Times New Roman", "Consolas"]
                                currentIndex: {
                                    var f = root.selectedFontFamily || "Segoe UI"
                                    var idx = find(f)
                                    return (idx >= 0) ? idx : 0
                                }
                                onActivated: function(index) {
                                    var chosen = (index >= 0 && model && index < model.length) ? model[index] : currentText
                                    root.selectedFontFamily = chosen
                                }
                            }
                        }
                    }

                    // 2. Alignment, Style & Orientation Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: alignRow.implicitHeight + 16
                radius: 8
                color: Theme.bgCardAlt
                border.color: Theme.borderCard
                border.width: 1

                RowLayout {
                    id: alignRow
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 12

                    // Text Alignment Segmented Control
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "ALIGNMENT"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }
                        RowLayout {
                            spacing: 2
                            Repeater {
                                model: [
                                    { label: "Left", val: "left" },
                                    { label: "Center", val: "center" },
                                    { label: "Right", val: "right" }
                                ]
                                delegate: Rectangle {
                                    width: 44
                                    height: 26
                                    radius: 4
                                    color: root.textAlign === modelData.val
                                        ? (Theme.isDark ? "#1C3660" : "#DBEAFE")
                                        : (aBtnMa.containsMouse ? (Theme.isDark ? "#17233D" : "#E2E8F0") : "transparent")
                                    border.color: root.textAlign === modelData.val ? Theme.accentCyan : Theme.borderCard
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.label
                                        font.pixelSize: 10
                                        font.weight: root.textAlign === modelData.val ? Font.Bold : Font.Normal
                                        color: root.textAlign === modelData.val ? Theme.accentCyan : Theme.textSecondary
                                    }

                                    MouseArea {
                                        id: aBtnMa
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.textAlign = modelData.val
                                    }
                                }
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Bold & Italic Toggles
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "STYLE"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }
                        RowLayout {
                            spacing: 8
                            CadCheckBox {
                                text: "Bold"
                                checked: root.isBold
                                onCheckedChanged: root.isBold = checked
                            }
                            CadCheckBox {
                                text: "Italic"
                                checked: root.isItalic
                                onCheckedChanged: root.isItalic = checked
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Orientation Radio
                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: "ORIENTATION"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }
                        RowLayout {
                            spacing: 8
                            CadRadioButton {
                                text: "Horiz"
                                checked: root.orientation === "horizontal"
                                onClicked: root.orientation = "horizontal"
                            }
                            CadRadioButton {
                                text: "Vert"
                                checked: root.orientation === "vertical"
                                onClicked: root.orientation = "vertical"
                            }
                        }
                    }
                }
            }

            // 3. Metrics Matrix (Char Width, Angle, Char Space, Line Space, Empty Char Width)
            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 12
                rowSpacing: 10

                CadInput {
                    Layout.fillWidth: true
                    label: "Char Width"
                    unit: "%"
                    text: root.charWidthPct.toFixed(0)
                    onValueChanged: function(v) { root.charWidthPct = Math.max(10, Math.min(300, v)) }
                }

                CadInput {
                    Layout.fillWidth: true
                    label: "Slant Angle"
                    unit: "°"
                    text: root.slantAngle.toFixed(1)
                    onValueChanged: function(v) { root.slantAngle = Math.max(-89, Math.min(89, v)) }
                }

                CadInput {
                    Layout.fillWidth: true
                    label: "Char Space"
                    unit: "mm"
                    text: root.charSpaceMm.toFixed(2)
                    onValueChanged: function(v) { root.charSpaceMm = v }
                }

                CadInput {
                    Layout.fillWidth: true
                    label: "Line Space"
                    unit: "mm"
                    text: root.lineSpaceMm.toFixed(2)
                    onValueChanged: function(v) { root.lineSpaceMm = v }
                }

                CadInput {
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    label: "Empty Char Width"
                    unit: "%"
                    text: root.emptyCharWidthPct.toFixed(0)
                    onValueChanged: function(v) { root.emptyCharWidthPct = Math.max(10, Math.min(200, v)) }
                }
            }

            // 4. CircleText Section (Card matching EZCad screenshot)
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: circleCol.implicitHeight + 20
                radius: 8
                color: root.isCircleText ? (Theme.isDark ? "#12203A" : "#F0FDF4") : Theme.bgCardAlt
                border.color: root.isCircleText ? Theme.accentCyan : Theme.borderCard
                border.width: root.isCircleText ? 1.5 : 1

                ColumnLayout {
                    id: circleCol
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        CadCheckBox {
                            id: circleChk
                            text: "Enable CircleText (Curve along arc)"
                            font.bold: true
                            checked: root.isCircleText
                            onCheckedChanged: root.isCircleText = checked
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: "⌒ ABCD"
                            font.bold: true
                            font.pixelSize: 12
                            color: root.isCircleText ? Theme.accentCyan : Theme.textMuted
                        }
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: 12
                        rowSpacing: 8
                        enabled: root.isCircleText
                        opacity: root.isCircleText ? 1.0 : 0.45

                        CadInput {
                            Layout.fillWidth: true
                            label: "Circle Diameter"
                            unit: "mm"
                            text: root.circleDiameterMm.toFixed(2)
                            onValueChanged: function(v) { root.circleDiameterMm = Math.max(1.0, v) }
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Base Angle"
                            unit: "°"
                            text: root.circleBaseAngleDeg.toFixed(1)
                            onValueChanged: function(v) { root.circleBaseAngleDeg = v }
                        }

                        CadCheckBox {
                            Layout.fillWidth: true
                            text: "Angle Range Limit (1-360°)"
                            checked: root.angleRangeLimitEnabled
                            onCheckedChanged: root.angleRangeLimitEnabled = checked
                        }

                        CadInput {
                            Layout.fillWidth: true
                            label: "Angle Limit"
                            unit: "°"
                            enabled: root.angleRangeLimitEnabled
                            text: root.angleRangeLimitDeg.toFixed(0)
                            onValueChanged: function(v) { root.angleRangeLimitDeg = Math.max(1, Math.min(360, v)) }
                        }
                    }
                }
            }
        }
    }

            // 5. Action Buttons (Apply, OK, Cancel)
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 10

                CadButton {
                    text: "Apply"
                    variant: "secondary"
                    onClicked: root.applySettings()
                }

                Item { Layout.fillWidth: true }

                CadButton {
                    text: "Cancel"
                    variant: "ghost"
                    onClicked: root.closeModal()
                }

                CadButton {
                    text: "OK"
                    variant: "accent"
                    onClicked: {
                        root.applySettings()
                        root.closeModal()
                    }
                }
            }
        }

        // Responsive Resize Handle
        CadWindowResizeHandle {
            target: modalBox
            minWidth: 560
            minHeight: 460
        }
    }
}
