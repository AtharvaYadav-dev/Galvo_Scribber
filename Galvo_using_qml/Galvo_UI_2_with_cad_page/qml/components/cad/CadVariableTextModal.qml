import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var targetShape: null
    property bool isOpened: false

    property bool enableVariableText: false
    property bool enableFixedWidth: false
    property real fixedWidthMm: 10.0
    property var entities: [] // [ { type: "fixed", text: "SN-" }, { type: "serial", current: 1, step: 1, digits: 5 }, { type: "datetime", format: "%Y-%m-%d" } ]
    property int selectedEntityIndex: -1

    signal variableSettingsConfirmed(bool enabled, var entitiesList, bool fixedWidth, real fixedWidthVal)

    anchors.fill: parent
    color: "transparent"
    visible: isOpened
    z: 200

    function openModal(shape) {
        targetShape = shape
        if (shape) {
            enableVariableText = Boolean(shape.enableVariableText)
            enableFixedWidth = Boolean(shape.enableFixedWidth)
            fixedWidthMm = (shape.fixedWidthMm !== undefined) ? Number(shape.fixedWidthMm) : 10.0
            entities = shape.variableEntities ? shape.variableEntities.slice() : [
                { type: "fixed", text: "SN-" },
                { type: "serial", current: 1, step: 1, digits: 5 }
            ]
        } else {
            entities = [
                { type: "fixed", text: "SN-" },
                { type: "serial", current: 1, step: 1, digits: 5 }
            ]
        }
        selectedEntityIndex = (entities.length > 0) ? 0 : -1
        if (root.width > 0 && root.height > 0) {
            modalBox.x = Math.max(10, Math.round((root.width - modalBox.width) / 2))
            modalBox.y = Math.max(10, Math.round((root.height - modalBox.height) / 2))
        }
        isOpened = true
    }

    function closeModal() {
        isOpened = false
    }

    function addEntity(type) {
        var list = entities.slice()
        if (type === "fixed") {
            list.push({ type: "fixed", text: "TEXT_" })
        } else if (type === "serial") {
            list.push({ type: "serial", current: 1, step: 1, digits: 5 })
        } else if (type === "datetime") {
            list.push({ type: "datetime", format: "%Y-%m-%d %H:%M:%S" })
        }
        entities = list
        selectedEntityIndex = list.length - 1
    }

    function deleteSelectedEntity() {
        if (selectedEntityIndex >= 0 && selectedEntityIndex < entities.length) {
            var list = entities.slice()
            list.splice(selectedEntityIndex, 1)
            entities = list
            selectedEntityIndex = Math.min(selectedEntityIndex, entities.length - 1)
        }
    }

    function moveEntity(offset) {
        if (selectedEntityIndex < 0 || selectedEntityIndex >= entities.length) return
        var newIdx = selectedEntityIndex + offset
        if (newIdx < 0 || newIdx >= entities.length) return
        var list = entities.slice()
        var item = list.splice(selectedEntityIndex, 1)[0]
        list.splice(newIdx, 0, item)
        entities = list
        selectedEntityIndex = newIdx
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
        width: 520
        height: Math.min(500, root.height > 0 ? (root.height - 40) : 500)
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
                implicitHeight: headerRow.implicitHeight

                MouseArea {
                    id: varHeaderDrag
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
                            text: "⌥"
                            font.bold: true
                            font.pixelSize: 14
                            color: Theme.accentCyan
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: "Variable Text Advance Settings"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                        Text {
                            text: "Configure serial counters, date stamps & dynamic elements"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            color: Theme.textMuted
                        }
                    }

                    Item { Layout.fillWidth: true }

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

            // Scrollable Content Body for responsive scaling
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: modalBox.width - 36
                    spacing: 12

                    // Options Checkboxes
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                CadCheckBox {
                    text: "Enable variable Text"
                    checked: root.enableVariableText
                    font.bold: true
                    onCheckedChanged: root.enableVariableText = checked
                }

                Item { Layout.fillWidth: true }

                CadCheckBox {
                    text: "Fixed text width"
                    checked: root.enableFixedWidth
                    onCheckedChanged: root.enableFixedWidth = checked
                }

                CadInput {
                    Layout.preferredWidth: 90
                    label: "Width"
                    unit: "mm"
                    enabled: root.enableFixedWidth
                    text: root.fixedWidthMm.toFixed(1)
                    onValueChanged: function(v) { root.fixedWidthMm = Math.max(1, v) }
                }
            }

            // Entities List & Action Column matching EZCad screenshot
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                // Entities List Box
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 160
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1
                    clip: true

                    ListView {
                        id: entitiesLv
                        anchors.fill: parent
                        anchors.margins: 6
                        model: root.entities
                        spacing: 4

                        delegate: Rectangle {
                            width: entitiesLv.width
                            height: 36
                            radius: 4
                            color: root.selectedEntityIndex === index
                                ? (Theme.isDark ? "#1C3660" : "#DBEAFE")
                                : (entMa.containsMouse ? (Theme.isDark ? "#17233D" : "#F1F5F9") : "transparent")
                            border.color: root.selectedEntityIndex === index ? Theme.accentCyan : "transparent"
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                spacing: 8

                                // Type Tag
                                Rectangle {
                                    width: 50
                                    height: 20
                                    radius: 3
                                    color: modelData.type === "serial" ? "#065F46" : (modelData.type === "datetime" ? "#1E40AF" : "#374151")
                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.type.toUpperCase()
                                        font.bold: true
                                        font.pixelSize: 8
                                        color: "#FFFFFF"
                                    }
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: {
                                        if (modelData.type === "fixed") return '"' + (modelData.text || "") + '"'
                                        if (modelData.type === "serial") return "Start: " + modelData.current + " | Step: " + modelData.step + " | Digits: " + modelData.digits
                                        if (modelData.type === "datetime") return "Format: " + (modelData.format || "%Y-%m-%d")
                                        return ""
                                    }
                                    font.pixelSize: 11
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    color: root.selectedEntityIndex === index ? Theme.textPrimary : Theme.textSecondary
                                }
                            }

                            MouseArea {
                                id: entMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.selectedEntityIndex = index
                            }
                        }
                    }
                }

                // Entity Action Buttons
                ColumnLayout {
                    Layout.preferredWidth: 100
                    spacing: 6

                    CadButton {
                        Layout.fillWidth: true
                        text: "Add Fixed"
                        iconName: "add"
                        onClicked: root.addEntity("fixed")
                    }

                    CadButton {
                        Layout.fillWidth: true
                        text: "Add Serial"
                        iconName: "numbers"
                        onClicked: root.addEntity("serial")
                    }

                    CadButton {
                        Layout.fillWidth: true
                        text: "Add Date"
                        iconName: "schedule"
                        onClicked: root.addEntity("datetime")
                    }

                    CadButton {
                        Layout.fillWidth: true
                        text: "Delete"
                        iconName: "delete"
                        enabled: root.selectedEntityIndex >= 0
                        onClicked: root.deleteSelectedEntity()
                    }

                    CadButton {
                        Layout.fillWidth: true
                        text: "Move Up"
                        iconName: "arrow_upward"
                        enabled: root.selectedEntityIndex > 0
                        onClicked: root.moveEntity(-1)
                    }

                    CadButton {
                        Layout.fillWidth: true
                        text: "Move Down"
                        iconName: "arrow_downward"
                        enabled: root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length - 1
                        onClicked: root.moveEntity(1)
                    }
                }
            }

            // Entity Details Editor (when an item is selected)
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: editCol.implicitHeight + 16
                visible: root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length
                radius: 8
                color: Theme.bgCardAlt
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: editCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        text: "SELECTED ENTITY CONFIGURATION"
                        font.pixelSize: 9
                        font.weight: Font.Bold
                        color: Theme.textMuted
                    }

                    // For Fixed Text
                    RowLayout {
                        Layout.fillWidth: true
                        visible: root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length && root.entities[root.selectedEntityIndex].type === "fixed"
                        spacing: 8
                        Text { text: "Fixed String:"; font.pixelSize: 11; color: Theme.textPrimary }
                        TextField {
                            Layout.fillWidth: true
                            text: (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) ? (root.entities[root.selectedEntityIndex].text || "") : ""
                            onTextChanged: {
                                if (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) {
                                    root.entities[root.selectedEntityIndex].text = text
                                }
                            }
                        }
                    }

                    // For Serial Number
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 3
                        columnSpacing: 8
                        visible: root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length && root.entities[root.selectedEntityIndex].type === "serial"

                        CadInput {
                            label: "Start Val"
                            text: (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) ? String(root.entities[root.selectedEntityIndex].current || 1) : "1"
                            onValueChanged: function(v) { if (root.selectedEntityIndex >= 0) root.entities[root.selectedEntityIndex].current = Math.round(v) }
                        }

                        CadInput {
                            label: "Step"
                            text: (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) ? String(root.entities[root.selectedEntityIndex].step || 1) : "1"
                            onValueChanged: function(v) { if (root.selectedEntityIndex >= 0) root.entities[root.selectedEntityIndex].step = Math.round(v) }
                        }

                        CadInput {
                            label: "Digits"
                            text: (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) ? String(root.entities[root.selectedEntityIndex].digits || 5) : "5"
                            onValueChanged: function(v) { if (root.selectedEntityIndex >= 0) root.entities[root.selectedEntityIndex].digits = Math.round(v) }
                        }
                    }

                    // For Date / Time
                    RowLayout {
                        Layout.fillWidth: true
                        visible: root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length && root.entities[root.selectedEntityIndex].type === "datetime"
                        spacing: 8
                        Text { text: "Date Format:"; font.pixelSize: 11; color: Theme.textPrimary }
                        CadComboBox {
                            Layout.fillWidth: true
                            model: ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%H:%M:%S", "%Y%m%d_%H%M%S"]
                            onCurrentTextChanged: {
                                if (root.selectedEntityIndex >= 0 && root.selectedEntityIndex < root.entities.length) {
                                    root.entities[root.selectedEntityIndex].format = currentText
                                }
                            }
                        }
                    }
                }
            }
        }
    }

            // Bottom Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Item { Layout.fillWidth: true }

                CadButton {
                    text: "Cancel"
                    variant: "ghost"
                    onClicked: root.closeModal()
                }

                CadButton {
                    text: "OK"
                    iconName: "check"
                    variant: "accent"
                    onClicked: {
                        root.variableSettingsConfirmed(root.enableVariableText, root.entities, root.enableFixedWidth, root.fixedWidthMm)
                        root.closeModal()
                    }
                }
            }
        }

        // Responsive Resize Handle
        CadWindowResizeHandle {
            target: modalBox
            minWidth: 420
            minHeight: 350
        }
    }
}
