import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property var shapesModel: []
    property int selectedIndex: -1
    property var selectedShape: null

    function syncSelectedShape() {
        if (selectedIndex >= 0 && shapesModel && selectedIndex < shapesModel.length) {
            selectedShape = shapesModel[selectedIndex]
            if (selectedShape && selectedShape.penId !== undefined) {
                selectedPenId = selectedShape.penId
            }
        } else {
            selectedShape = null
        }
    }

    onSelectedIndexChanged: syncSelectedShape()
    onShapesModelChanged: syncSelectedShape()
    property int selectedPenId: 0

    function syncPenSliders() {
        var p = Theme.getPen(selectedPenId)
        if (p) {
            speedSlider.value = p.speed
            powerSlider.value = p.power
            freqSlider.value = p.freq
        }
    }
    onSelectedPenIdChanged: syncPenSliders()
    property int activeAnchorIndex: 4 // Center anchor (0 to 8)
    property bool lockAspectRatio: true
    property bool advancedTcExpanded: false
    property bool anchorPopupOpen: false

    signal shapeModified(var shape)
    signal shapeSelected(int index)
    signal shapeDeleted(int index)
    signal shapeVisibilityToggled(int index)
    signal shapeLockToggled(int index)
    signal shapeRenamed(int index, string newName)
    signal penChanged(int penId)
    signal openColorPickerRequested(int penId, string color, string name)
    signal hatchTriggered(var shape)
    signal unhatchTriggered(var shape)
    signal fontDialogTriggered(var shape)
    signal arrayDialogTriggered(var shape)
    signal inputPortDialogTriggered(var shape)
    signal variableTextDialogTriggered(var shape)
    signal applyTriggered(var shape)

    width: 340
    color: Theme.bgCard
    border.color: Theme.borderCard
    border.width: 1

    function anchorName(idx) {
        var names = [
            "Top-Left", "Top-Center", "Top-Right",
            "Middle-Left", "Center", "Middle-Right",
            "Bottom-Left", "Bottom-Center", "Bottom-Right"
        ]
        return (idx >= 0 && idx < names.length) ? names[idx] : "Center"
    }

    function getAnchorPos(cx, cy, w, h, anchorIdx) {
        var halfW = (w || 0) / 2.0
        var halfH = (h || 0) / 2.0
        var ax = cx
        var ay = cy

        if (anchorIdx === 0 || anchorIdx === 3 || anchorIdx === 6) ax = cx - halfW
        else if (anchorIdx === 2 || anchorIdx === 5 || anchorIdx === 8) ax = cx + halfW

        if (anchorIdx === 0 || anchorIdx === 1 || anchorIdx === 2) ay = cy + halfH
        else if (anchorIdx === 6 || anchorIdx === 7 || anchorIdx === 8) ay = cy - halfH

        return { x: ax, y: ay }
    }

    function getCenterFromAnchor(targetAx, targetAy, w, h, anchorIdx) {
        var halfW = (w || 0) / 2.0
        var halfH = (h || 0) / 2.0
        var cx = targetAx
        var cy = targetAy

        if (anchorIdx === 0 || anchorIdx === 3 || anchorIdx === 6) cx = targetAx + halfW
        else if (anchorIdx === 2 || anchorIdx === 5 || anchorIdx === 8) cx = targetAx - halfW

        if (anchorIdx === 0 || anchorIdx === 1 || anchorIdx === 2) cy = targetAy - halfH
        else if (anchorIdx === 6 || anchorIdx === 7 || anchorIdx === 8) cy = targetAy + halfH

        return { x: cx, y: cy }
    }

    function updateTransformInputs() {
        if (!root.selectedShape) {
            inputX.text = "0.000"
            inputY.text = "0.000"
            inputW.text = "0.000"
            inputH.text = "0.000"
            inputRot.text = "0"
            inputZ.text = "0.000"
            return
        }
        if (root.selectedShape.penId !== undefined) {
            root.selectedPenId = root.selectedShape.penId
        }
        var a = getAnchorPos(root.selectedShape.xMm || 0, root.selectedShape.yMm || 0, root.selectedShape.wMm || 0, root.selectedShape.hMm || 0, root.activeAnchorIndex)
        inputX.text = a.x.toFixed(3)
        inputY.text = a.y.toFixed(3)
        inputW.text = Number(root.selectedShape.wMm || 0).toFixed(3)
        inputH.text = Number(root.selectedShape.hMm || 0).toFixed(3)
        inputRot.text = Number(root.selectedShape.rotation || 0).toFixed(0)
        inputZ.text = Number(root.selectedShape.zMm || 0).toFixed(3)

        if (typeof entityNameInput !== "undefined" && entityNameInput && !entityNameInput.activeFocus) {
            entityNameInput.text = root.selectedShape ? (root.selectedShape.name || "") : ""
        }

        if (root.selectedShape.type === "text") {
            if (typeof textEditArea !== "undefined" && textEditArea && textEditArea.text !== (root.selectedShape.text || "TEXT")) {
                textEditArea.text = root.selectedShape.text || "TEXT"
            }
            if (typeof textSpaceInput !== "undefined" && textSpaceInput) textSpaceInput.text = Number(root.selectedShape.charSpace || 0).toFixed(3)
            if (typeof textHeightInput !== "undefined" && textHeightInput) textHeightInput.text = Number(root.selectedShape.hMm || 4.0).toFixed(3)
            if (typeof fontFamilyCombo !== "undefined" && fontFamilyCombo) {
                var f = root.selectedShape.fontFamily || "Segoe UI"
                var fIdx = fontFamilyCombo.find(f)
                if (fIdx >= 0) {
                    fontFamilyCombo.currentIndex = fIdx
                    fontFamilyCombo.displayText = f
                }
            }
        }
    }

    function applyXChange(newVal) {
        if (!root.selectedShape || root.selectedShape.locked) return
        var curAnchor = getAnchorPos(root.selectedShape.xMm || 0, root.selectedShape.yMm || 0, root.selectedShape.wMm || 0, root.selectedShape.hMm || 0, root.activeAnchorIndex)
        var newCenter = getCenterFromAnchor(newVal, curAnchor.y, root.selectedShape.wMm || 0, root.selectedShape.hMm || 0, root.activeAnchorIndex)
        root.selectedShape.xMm = newCenter.x
        root.selectedShape.yMm = newCenter.y
        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
        root.shapeModified(root.selectedShape)
    }

    function applyYChange(newVal) {
        if (!root.selectedShape || root.selectedShape.locked) return
        var curAnchor = getAnchorPos(root.selectedShape.xMm || 0, root.selectedShape.yMm || 0, root.selectedShape.wMm || 0, root.selectedShape.hMm || 0, root.activeAnchorIndex)
        var newCenter = getCenterFromAnchor(curAnchor.x, newVal, root.selectedShape.wMm || 0, root.selectedShape.hMm || 0, root.activeAnchorIndex)
        root.selectedShape.xMm = newCenter.x
        root.selectedShape.yMm = newCenter.y
        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
        root.shapeModified(root.selectedShape)
    }

    function applyWChange(newVal) {
        if (!root.selectedShape || root.selectedShape.locked) return
        var oldW = Number(root.selectedShape.wMm || 10.0)
        var oldH = Number(root.selectedShape.hMm || 10.0)
        var newW = Math.max(0.1, newVal)
        var newH = oldH

        if (root.lockAspectRatio && oldW > 0) {
            newH = Math.max(0.1, oldH * (newW / oldW))
        }

        var fixedAnchor = getAnchorPos(root.selectedShape.xMm || 0, root.selectedShape.yMm || 0, oldW, oldH, root.activeAnchorIndex)
        var newCenter = getCenterFromAnchor(fixedAnchor.x, fixedAnchor.y, newW, newH, root.activeAnchorIndex)

        root.selectedShape.xMm = newCenter.x
        root.selectedShape.yMm = newCenter.y
        root.selectedShape.wMm = newW
        root.selectedShape.hMm = newH
        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []

        if (root.lockAspectRatio) {
            inputH.text = newH.toFixed(3)
        }
        inputX.text = fixedAnchor.x.toFixed(3)
        inputY.text = fixedAnchor.y.toFixed(3)

        root.shapeModified(root.selectedShape)
    }

    function applyHChange(newVal) {
        if (!root.selectedShape || root.selectedShape.locked) return
        var oldW = Number(root.selectedShape.wMm || 10.0)
        var oldH = Number(root.selectedShape.hMm || 10.0)
        var newH = Math.max(0.1, newVal)
        var newW = oldW

        if (root.lockAspectRatio && oldH > 0) {
            newW = Math.max(0.1, oldW * (newH / oldH))
        }

        var fixedAnchor = getAnchorPos(root.selectedShape.xMm || 0, root.selectedShape.yMm || 0, oldW, oldH, root.activeAnchorIndex)
        var newCenter = getCenterFromAnchor(fixedAnchor.x, fixedAnchor.y, newW, newH, root.activeAnchorIndex)

        root.selectedShape.xMm = newCenter.x
        root.selectedShape.yMm = newCenter.y
        root.selectedShape.wMm = newW
        root.selectedShape.hMm = newH
        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []

        if (root.lockAspectRatio) {
            inputW.text = newW.toFixed(3)
        }
        inputX.text = fixedAnchor.x.toFixed(3)
        inputY.text = fixedAnchor.y.toFixed(3)

        root.shapeModified(root.selectedShape)
    }

    onSelectedShapeChanged: root.updateTransformInputs()
    onActiveAnchorIndexChanged: root.updateTransformInputs()

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Inspector Tab Bar (Design & Transform vs Laser Parameters)
        Rectangle {
            Layout.fillWidth: true
            height: 44
            color: Theme.bgCardHeader
            border.color: Theme.borderCard
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                TabBar {
                    id: tabGroup
                    objectName: "inspectorTabGroup"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: 0
                    background: null

                    TabButton {
                        text: "Design & Transform"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: tabGroup.currentIndex === 0 ? Font.Bold : Font.DemiBold
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: tabGroup.currentIndex === 0 ? (Theme.isDark ? "#00E5FF" : "#1D4ED8") : Theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabGroup.currentIndex === 0 ? (Theme.isDark ? "#17233D" : "#FFFFFF") : "transparent"
                            radius: 5
                            border.color: tabGroup.currentIndex === 0 ? Theme.borderActive : "transparent"
                            border.width: 1
                        }
                    }

                    TabButton {
                        text: "Laser Pens & Process"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        font.weight: tabGroup.currentIndex === 1 ? Font.Bold : Font.DemiBold
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: tabGroup.currentIndex === 1 ? (Theme.isDark ? "#00E5FF" : "#1D4ED8") : Theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabGroup.currentIndex === 1 ? (Theme.isDark ? "#17233D" : "#FFFFFF") : "transparent"
                            radius: 5
                            border.color: tabGroup.currentIndex === 1 ? Theme.borderActive : "transparent"
                            border.width: 1
                        }
                    }
                }
            }
        }

        // Tab Content Area
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabGroup.currentIndex

            // TAB 1: DESIGN & TRANSFORM INSPECTOR
            ScrollView {
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    x: 12
                    width: root.width - 24
                    spacing: 12
                    anchors.topMargin: 10
                    anchors.bottomMargin: 16

                    // 1. Entities & Layers Tree List
                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "OBJECT ENTITIES (" + root.shapesModel.length + ")"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textMuted
                            font.letterSpacing: 0.5
                        }
                        Item { Layout.fillWidth: true }
                        Text {
                            text: "Click item to select"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 9
                            color: Theme.textMuted
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: Math.min(130, Math.max(50, shapesListCol.implicitHeight + 8))
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1
                        clip: true

                        Text {
                            anchors.centerIn: parent
                            visible: root.shapesModel.length === 0
                            text: "No entities on canvas (draw or add text)"
                            color: Theme.textMuted
                            font.pixelSize: 10
                        }

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 4
                            clip: true

                            ColumnLayout {
                                id: shapesListCol
                                width: parent.width
                                spacing: 2

                                Repeater {
                                    id: entitiesRepeater
                                    model: root.shapesModel

                                    Rectangle {
                                        id: delegateRow
                                        Layout.fillWidth: true
                                        height: 28
                                        radius: 4
                                        color: root.selectedIndex === index
                                            ? (Theme.isDark ? "#1C2B48" : "#E2E8F0")
                                            : (rowMa.containsMouse ? (Theme.isDark ? "#141F36" : "#F1F5F9") : "transparent")
                                        border.color: root.selectedIndex === index ? Theme.accentCyan : "transparent"
                                        border.width: root.selectedIndex === index ? 1 : 0
                                        opacity: delegateRow.isVis ? 1.0 : 0.45

                                        readonly property var currentShape: (root.modelRevision >= 0 && index >= 0 && index < root.shapesModel.length) ? root.shapesModel[index] : modelData
                                        readonly property bool isVis: !(currentShape && currentShape.visible === false)
                                        readonly property bool isLck: Boolean(currentShape && currentShape.locked === true)
                                        property bool isEditingName: false

                                        function startEditingName() {
                                            isEditingName = true
                                            inlineNameEdit.text = (currentShape && currentShape.name) ? currentShape.name : ""
                                            inlineNameEdit.forceActiveFocus()
                                            inlineNameEdit.selectAll()
                                        }

                                        function commitInlineName() {
                                            if (isEditingName) {
                                                isEditingName = false
                                                var val = inlineNameEdit.text.trim()
                                                if (val.length > 0 && currentShape && val !== currentShape.name) {
                                                    root.shapeRenamed(index, val)
                                                    root.modelRevision++
                                                }
                                            }
                                        }

                                        // Background click to select entity (z: 0)
                                        MouseArea {
                                            id: rowMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: root.shapeSelected(index)
                                        }

                                        // Interactive row controls (z: 1 to ensure clicks reach icons)
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 6
                                            anchors.rightMargin: 6
                                            spacing: 6
                                            z: 1

                                            // Pen Color Indicator Dot
                                            Rectangle {
                                                width: 8
                                                height: 8
                                                radius: 4
                                                color: Theme.getPenColor((currentShape && currentShape.penId) || 0)
                                            }

                                            // Visibility Toggle
                                            Rectangle {
                                                width: 20
                                                height: 20
                                                radius: 3
                                                color: eyeMa.containsMouse ? (Theme.isDark ? "#2A3B5C" : "#CBD5E1") : "transparent"

                                                CadIcon {
                                                    anchors.centerIn: parent
                                                    name: delegateRow.isVis ? "visibility" : "visibility_off"
                                                    size: 14
                                                    iconColor: delegateRow.isVis ? Theme.textPrimary : Theme.accentRed
                                                }

                                                MouseArea {
                                                    id: eyeMa
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.shapeVisibilityToggled(index)
                                                        root.modelRevision++
                                                    }
                                                }
                                                ToolTip.visible: eyeMa.containsMouse
                                                ToolTip.text: delegateRow.isVis ? "Visible (Click to hide from canvas)" : "Hidden (Click to show on canvas)"
                                            }

                                            // Lock Toggle
                                            Rectangle {
                                                width: 20
                                                height: 20
                                                radius: 3
                                                color: lockMa.containsMouse ? (Theme.isDark ? "#2A3B5C" : "#CBD5E1") : "transparent"

                                                CadIcon {
                                                    anchors.centerIn: parent
                                                    name: delegateRow.isLck ? "lock" : "lock_open"
                                                    size: 14
                                                    iconColor: delegateRow.isLck ? Theme.accentAmber : Theme.textMuted
                                                }

                                                MouseArea {
                                                    id: lockMa
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.shapeLockToggled(index)
                                                        root.modelRevision++
                                                    }
                                                }
                                                ToolTip.visible: lockMa.containsMouse
                                                ToolTip.text: delegateRow.isLck ? "Locked (Click to unlock)" : "Unlocked (Click to lock against edits)"
                                            }

                                            Item {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true

                                                Text {
                                                    anchors.fill: parent
                                                    verticalAlignment: Text.AlignVCenter
                                                    visible: !delegateRow.isEditingName
                                                    text: (currentShape && currentShape.name) ? currentShape.name : "Entity"
                                                    font.family: "Segoe UI, Inter, sans-serif"
                                                    font.pixelSize: 11
                                                    font.weight: root.selectedIndex === index ? Font.Bold : Font.Normal
                                                    color: root.selectedIndex === index ? Theme.textBrand : (delegateRow.isVis ? Theme.textPrimary : Theme.textMuted)
                                                    elide: Text.ElideMiddle
                                                }

                                                TextInput {
                                                    id: inlineNameEdit
                                                    anchors.fill: parent
                                                    verticalAlignment: TextInput.AlignVCenter
                                                    visible: delegateRow.isEditingName
                                                    font.family: "Segoe UI, Inter, sans-serif"
                                                    font.pixelSize: 11
                                                    font.bold: true
                                                    color: Theme.accentCyan
                                                    selectByMouse: true
                                                    onEditingFinished: delegateRow.commitInlineName()
                                                    Keys.onReturnPressed: delegateRow.commitInlineName()
                                                    Keys.onEnterPressed: delegateRow.commitInlineName()
                                                    Keys.onEscapePressed: delegateRow.isEditingName = false
                                                }

                                                MouseArea {
                                                    anchors.fill: parent
                                                    enabled: !delegateRow.isEditingName
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: root.shapeSelected(index)
                                                    onDoubleClicked: delegateRow.startEditingName()
                                                }
                                                ToolTip.visible: rowMa.containsMouse && !delegateRow.isEditingName
                                                ToolTip.text: "Double-click to rename"
                                            }

                                            // Quick rename pencil icon on hover / selected
                                            Rectangle {
                                                width: 16
                                                height: 16
                                                radius: 3
                                                visible: (rowMa.containsMouse || root.selectedIndex === index) && !delegateRow.isEditingName
                                                color: editNameMa.containsMouse ? (Theme.isDark ? "#2A3B5C" : "#CBD5E1") : "transparent"

                                                CadIcon {
                                                    anchors.centerIn: parent
                                                    name: "edit"
                                                    size: 11
                                                    iconColor: editNameMa.containsMouse ? Theme.accentCyan : Theme.textMuted
                                                }

                                                MouseArea {
                                                    id: editNameMa
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        delegateRow.startEditingName()
                                                    }
                                                }
                                                ToolTip.visible: editNameMa.containsMouse
                                                ToolTip.text: "Rename Object"
                                            }

                                            Rectangle {
                                                height: 16
                                                radius: 3
                                                color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                                implicitWidth: typeTxt.implicitWidth + 8
                                                Text {
                                                    id: typeTxt
                                                    anchors.centerIn: parent
                                                    text: ((modelData && modelData.type) ? modelData.type : "OBJ").toUpperCase()
                                                    font.family: "Segoe UI, Inter, sans-serif"
                                                    font.pixelSize: 8
                                                    font.weight: Font.Bold
                                                    color: Theme.textSecondary
                                                }
                                            }

                                            // Delete entity
                                            Rectangle {
                                                width: 18
                                                height: 18
                                                radius: 3
                                                enabled: !delegateRow.isLck
                                                opacity: delegateRow.isLck ? 0.3 : 1.0
                                                color: delMa.containsMouse ? (Theme.isDark ? "#3A1E24" : "#FEE2E2") : "transparent"

                                                CadIcon {
                                                    anchors.centerIn: parent
                                                    name: "close"
                                                    size: 11
                                                    iconColor: delMa.containsMouse ? Theme.accentRed : Theme.textMuted
                                                }

                                                MouseArea {
                                                    id: delMa
                                                    anchors.fill: parent
                                                    enabled: !delegateRow.isLck
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.shapeDeleted(index)
                                                    }
                                                }
                                                ToolTip.visible: delMa.containsMouse
                                                ToolTip.text: delegateRow.isLck ? "Object is locked (unlock to delete)" : "Delete Entity"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // 2. EZCad Standard Transform Section (Screenshot 2026-10-23 171242.png)
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: transCol.implicitHeight + 16
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            id: transCol
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8

                            // Selected Object Name Row
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                visible: root.selectedShape !== null

                                Text {
                                    text: "Name"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: Theme.textMuted
                                    Layout.preferredWidth: 32
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 24
                                    radius: 4
                                    color: Theme.bgCard
                                    border.color: entityNameInput.activeFocus ? Theme.accentCyan : Theme.borderCard
                                    border.width: 1

                                    TextInput {
                                        id: entityNameInput
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: Theme.textPrimary
                                        text: root.selectedShape ? (root.selectedShape.name || "") : ""
                                        selectByMouse: true
                                        onEditingFinished: {
                                            if (root.selectedShape && text.trim().length > 0 && text.trim() !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, text.trim())
                                                root.modelRevision++
                                            }
                                        }
                                        Keys.onReturnPressed: {
                                            if (root.selectedShape && text.trim().length > 0 && text.trim() !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, text.trim())
                                                root.modelRevision++
                                            }
                                            focus = false
                                        }
                                        Keys.onEnterPressed: {
                                            if (root.selectedShape && text.trim().length > 0 && text.trim() !== root.selectedShape.name) {
                                                root.shapeRenamed(root.selectedIndex, text.trim())
                                                root.modelRevision++
                                            }
                                            focus = false
                                        }
                                    }
                                }

                                Rectangle {
                                    height: 20
                                    radius: 3
                                    color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                    implicitWidth: selTypeTxt.implicitWidth + 8
                                    Text {
                                        id: selTypeTxt
                                        anchors.centerIn: parent
                                        text: (root.selectedShape && root.selectedShape.type ? root.selectedShape.type : "OBJ").toUpperCase()
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 8
                                        font.bold: true
                                        color: Theme.textSecondary
                                    }
                                }
                            }

                            // Header: Position | Size [MM] | Actions
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Text {
                                    text: "Position"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: Theme.textMuted
                                    Layout.fillWidth: true
                                }
                                Text {
                                    text: "Size [MM]"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: Theme.textMuted
                                    Layout.fillWidth: true
                                }
                                Item {
                                    width: 32
                                }
                            }

                            // Row 1: X | W | Lock Aspect Ratio
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                CadInput {
                                    id: inputX
                                    label: "X"
                                    unit: "mm"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0.000"
                                    onValueChanged: function(v) { root.applyXChange(v) }
                                }

                                CadInput {
                                    id: inputW
                                    label: "W"
                                    unit: "mm"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0.000"
                                    onValueChanged: function(v) { root.applyWChange(v) }
                                }

                                // Aspect Lock Button (32x32)
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: 5
                                    enabled: !(root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.4 : 1.0
                                    color: root.lockAspectRatio ? (Theme.isDark ? "#1C3660" : "#DBEAFE") : Theme.bgCard
                                    border.color: root.lockAspectRatio ? Theme.accentCyan : Theme.borderCard
                                    border.width: 1

                                    CadIcon {
                                        anchors.centerIn: parent
                                        name: root.lockAspectRatio ? "lock" : "lock_open"
                                        size: 15
                                        iconColor: root.lockAspectRatio ? Theme.accentCyan : Theme.textMuted
                                    }
                                    MouseArea {
                                        id: lockMa
                                        anchors.fill: parent
                                        enabled: !(root.selectedShape && Boolean(root.selectedShape.locked))
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.lockAspectRatio = !root.lockAspectRatio
                                            if (typeof cad !== "undefined" && cad) {
                                                cad.set_status_message(root.lockAspectRatio ? "Proportional aspect ratio locked." : "Aspect ratio unlocked.")
                                            }
                                        }
                                    }
                                    ToolTip.visible: lockMa.containsMouse
                                    ToolTip.text: root.lockAspectRatio ? "Aspect Ratio Locked (Proportional scaling)" : "Aspect Ratio Unlocked (Free scaling)"
                                }
                            }

                            // Row 2: Y | H | 9-Point Anchor Grid
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                CadInput {
                                    id: inputY
                                    label: "Y"
                                    unit: "mm"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0.000"
                                    onValueChanged: function(v) { root.applyYChange(v) }
                                }

                                CadInput {
                                    id: inputH
                                    label: "H"
                                    unit: "mm"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0.000"
                                    onValueChanged: function(v) { root.applyHChange(v) }
                                }

                                // 3x3 Anchor Grid Button / Popover Toggle (32x32)
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: 5
                                    color: root.anchorPopupOpen ? (Theme.isDark ? "#1C3660" : "#DBEAFE") : Theme.bgCard
                                    border.color: root.anchorPopupOpen ? Theme.accentCyan : Theme.borderCard
                                    border.width: 1

                                    Grid {
                                        anchors.centerIn: parent
                                        columns: 3
                                        spacing: 2
                                        Repeater {
                                            model: 9
                                            Rectangle {
                                                width: 5
                                                height: 5
                                                radius: 1
                                                color: root.activeAnchorIndex === index ? Theme.accentCyan : (Theme.isDark ? "#475569" : "#94A3B8")
                                            }
                                        }
                                    }
                                    MouseArea {
                                        id: ancBtnMa
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.anchorPopupOpen = !root.anchorPopupOpen
                                    }
                                    ToolTip.visible: ancBtnMa.containsMouse
                                    ToolTip.text: "9-Point Reference Anchor (Active: " + root.anchorName(root.activeAnchorIndex) + ")"
                                }
                            }

                            // Expandable 3x3 Anchor Point Selector Card
                            Rectangle {
                                visible: root.anchorPopupOpen
                                Layout.fillWidth: true
                                implicitHeight: ancCol.implicitHeight + 16
                                radius: 6
                                color: Theme.bgCard
                                border.color: Theme.accentCyan
                                border.width: 1

                                ColumnLayout {
                                    id: ancCol
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 6

                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text {
                                            text: "TRANSFORM ANCHOR POINT"
                                            font.pixelSize: 9
                                            font.bold: true
                                            color: Theme.accentCyan
                                        }
                                        Item { Layout.fillWidth: true }
                                        Text {
                                            text: root.anchorName(root.activeAnchorIndex)
                                            font.pixelSize: 10
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                    }

                                    GridLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        columns: 3
                                        columnSpacing: 18
                                        rowSpacing: 8

                                        Repeater {
                                            model: 9
                                            Rectangle {
                                                width: 18
                                                height: 18
                                                radius: 4
                                                color: root.activeAnchorIndex === index ? (Theme.isDark ? "#1C3660" : "#DBEAFE") : (ancMa.containsMouse ? (Theme.isDark ? "#1E2A44" : "#E2E8F0") : Theme.bgCardAlt)
                                                border.color: root.activeAnchorIndex === index ? Theme.accentCyan : Theme.borderCard
                                                border.width: root.activeAnchorIndex === index ? 1.5 : 1

                                                Rectangle {
                                                    anchors.centerIn: parent
                                                    width: 6
                                                    height: 6
                                                    radius: 3
                                                    color: root.activeAnchorIndex === index ? Theme.accentCyan : (Theme.isDark ? "#64748B" : "#94A3B8")
                                                }

                                                MouseArea {
                                                    id: ancMa
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                    cursorShape: Qt.PointingHandCursor
                                                    onClicked: {
                                                        root.activeAnchorIndex = index
                                                        root.updateTransformInputs()
                                                    }
                                                }
                                                ToolTip.visible: ancMa.containsMouse
                                                ToolTip.text: root.anchorName(index)
                                            }
                                        }
                                    }
                                }
                            }

                            // Row 3: Focal Z | Rotation | Center to Origin
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                CadInput {
                                    id: inputZ
                                    label: "Z"
                                    unit: "mm"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0.000"
                                    onValueChanged: function(v) {
                                        if (root.selectedShape && !root.selectedShape.locked) {
                                            root.selectedShape.zMm = v
                                            root.shapeModified(root.selectedShape)
                                        }
                                        if (typeof jog !== "undefined" && jog) {
                                            jog.targetFocus = v
                                        }
                                    }
                                }

                                CadInput {
                                    id: inputRot
                                    label: "Rot"
                                    unit: "°"
                                    readOnly: (root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.55 : 1.0
                                    Layout.fillWidth: true
                                    text: "0"
                                    onValueChanged: function(v) {
                                        if (root.selectedShape && !root.selectedShape.locked) {
                                            root.selectedShape.rotation = v
                                            root.selectedShape.hatch_lines = []
                                            if (root.selectedShape.hatched && typeof cad !== "undefined" && cad) {
                                                root.selectedShape.hatch_lines = cad.computeHatchPreviewLines(root.selectedShape)
                                            }
                                            root.shapeModified(root.selectedShape)
                                        }
                                    }
                                }

                                // Center to Origin (0, 0) Button (32x32)
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: 5
                                    enabled: !(root.selectedShape && Boolean(root.selectedShape.locked))
                                    opacity: (root.selectedShape && Boolean(root.selectedShape.locked)) ? 0.4 : 1.0
                                    color: cBtnMa.containsMouse ? (Theme.isDark ? "#17233D" : "#E2E8F0") : Theme.bgCard
                                    border.color: Theme.borderCard
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: "⌖"
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: Theme.accentCyan
                                    }
                                    MouseArea {
                                        id: cBtnMa
                                        anchors.fill: parent
                                        enabled: !(root.selectedShape && Boolean(root.selectedShape.locked))
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            if (root.selectedShape && !root.selectedShape.locked) {
                                                root.selectedShape.xMm = 0.0
                                                root.selectedShape.yMm = 0.0
                                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                                root.updateTransformInputs()
                                                root.shapeModified(root.selectedShape)
                                                if (typeof cad !== "undefined" && cad) {
                                                    cad.set_status_message("Centered " + (root.selectedShape.name || "entity") + " to (0, 0).")
                                                }
                                            }
                                        }
                                    }
                                    ToolTip.visible: cBtnMa.containsMouse
                                    ToolTip.text: (root.selectedShape && root.selectedShape.locked) ? "Object is locked (unlock to center)" : "Center Entity to (0, 0) Origin"
                                }
                            }

                                            }
                    }

                    // Hatch Infill Action Controls
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: root.selectedShape !== null

                        CadButton {
                            Layout.fillWidth: true
                            implicitHeight: 30
                            text: (root.selectedShape && root.selectedShape.hatched) ? "Hatch Settings (H)" : "Apply Hatch (H)"
                            iconName: "texture"
                            variant: (root.selectedShape && root.selectedShape.hatched) ? "outline" : "secondary"
                            tooltipText: "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.hatchTriggered(root.selectedShape)
                                }
                            }
                        }

                        CadButton {
                            visible: Boolean(root.selectedShape && root.selectedShape.hatched)
                            Layout.fillWidth: true
                            implicitHeight: 30
                            text: "Remove Hatch"
                            iconName: "layers_clear"
                            variant: "danger"
                            tooltipText: "Remove hatch infill lines from selected object"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.unhatchTriggered(root.selectedShape)
                                }
                            }
                        }
                    }

                    // 3. EZCad Action Toolbar (Array, Input Port, Apply)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: root.selectedShape !== null

                        CadButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: "Array"
                            variant: "secondary"
                            tooltipText: "Duplicate entity into grid array"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.arrayDialogTriggered(root.selectedShape)
                                }
                            }
                        }

                        CadButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: "Input Port"
                            variant: "secondary"
                            tooltipText: "Set hardware I/O trigger condition"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.inputPortDialogTriggered(root.selectedShape)
                                }
                            }
                        }

                        CadButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: "Apply"
                            variant: "accent"
                            tooltipText: "Recompute geometry, measure dimensions, and repaint"
                            onClicked: {
                                if (root.selectedShape) {
                                    if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                    if (root.selectedShape.type === "text" && typeof cad !== "undefined" && cad) {
                                        var m = cad.measureText(
                                            root.selectedShape.text || "TEXT",
                                            root.selectedShape.fontFamily || "Segoe UI",
                                            root.selectedShape.hMm || 4.0,
                                            Boolean(root.selectedShape.bold),
                                            Boolean(root.selectedShape.italic)
                                        )
                                        if (m && m.wMm > 0) {
                                            root.selectedShape.wMm = m.wMm
                                            inputW.text = m.wMm.toFixed(3)
                                        }
                                    }
                                    root.shapeModified(root.selectedShape)
                                    root.applyTriggered(root.selectedShape)
                                }
                            }
                        }
                    }

                    // 4. DEDICATED EZCAD TEXT & TYPOGRAPHY INSPECTOR
                    // (Visible specifically when a Text entity is selected)
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: root.selectedShape !== null && root.selectedShape.type === "text"

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.borderCard
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: "TEXT PROPERTIES"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                                font.letterSpacing: 0.5
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: (root.selectedShape && root.selectedShape.circleText) ? "CircleText Mode" : "Linear"
                                font.pixelSize: 9
                                font.bold: true
                                color: (root.selectedShape && root.selectedShape.circleText) ? Theme.accentAmber : Theme.textMuted
                            }
                        }

                        // Font Category Dropdown (TrueType, Hershey Single-Stroke, SHX)
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "Font"
                                font.pixelSize: 11
                                font.bold: true
                                color: Theme.textSecondary
                                Layout.preferredWidth: 32
                            }

                            CadComboBox {
                                id: fontTypeCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                model: ["TrueType Font", "Single-Stroke (Hershey)", "SHX Font"]
                                currentIndex: {
                                    if (!root.selectedShape) return 0
                                    var ft = root.selectedShape.fontType || "TrueType Font"
                                    if (ft.indexOf("Single-Stroke") !== -1 || (root.selectedShape.fontFamily && root.selectedShape.fontFamily.indexOf("Simplex") !== -1)) return 1
                                    if (ft.indexOf("SHX") !== -1) return 2
                                    return 0
                                }
                                onActivated: function(index) {
                                    if (root.selectedShape) {
                                        root.selectedShape.fontType = currentText
                                        if (index === 1) {
                                            root.selectedShape.fontFamily = "Simplex (Single-Stroke Vector)"
                                        }
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }
                        }

                        // Font Family Selector + [ H ], [ F ] Quick Actions
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "Face"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                                Layout.preferredWidth: 32
                            }

                            CadComboBox {
                                id: fontFamilyCombo
                                objectName: "fontFamilyCombo"
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                searchable: true
                                searchPlaceholder: "Search font face (e.g. Arial)..."
                                model: (typeof cad !== "undefined" && cad) ? cad.availableFonts : ["Segoe UI", "Arial", "Leelawadee UI", "Times New Roman", "Consolas"]
                                currentIndex: {
                                    if (!root.selectedShape) return 0
                                    var f = root.selectedShape.fontFamily || "Segoe UI"
                                    var idx = find(f)
                                    return (idx >= 0) ? idx : 0
                                }
                                onActivated: function(index) {
                                    if (root.selectedShape && root.selectedShape.type === "text") {
                                        var chosenFont = (index >= 0 && model && index < model.length) ? model[index] : currentText
                                        root.selectedShape.fontFamily = chosenFont
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        if (typeof cad !== "undefined" && cad) {
                                            var m = cad.measureText(
                                                root.selectedShape.text || "TEXT",
                                                chosenFont,
                                                root.selectedShape.hMm || 4.0,
                                                Boolean(root.selectedShape.bold),
                                                Boolean(root.selectedShape.italic)
                                            )
                                            if (m && m.wMm > 0) {
                                                root.selectedShape.wMm = m.wMm
                                                inputW.text = m.wMm.toFixed(3)
                                            }
                                        }
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }

                            // [ H ] Hatch Shortcut Button (Accessible only when an object is selected)
                            Rectangle {
                                width: 32
                                height: 32
                                radius: 5
                                opacity: root.selectedShape ? 1.0 : 0.4
                                color: (root.selectedShape && root.selectedShape.hatched)
                                    ? (Theme.isDark ? "#1C3660" : "#DBEAFE")
                                    : (hBtnMa.containsMouse && root.selectedShape ? (Theme.isDark ? "#17233D" : "#E2E8F0") : Theme.bgCardAlt)
                                border.color: (root.selectedShape && root.selectedShape.hatched) ? Theme.accentCyan : Theme.borderCard
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "H"
                                    font.bold: true
                                    font.pixelSize: 11
                                    color: (root.selectedShape && root.selectedShape.hatched) ? Theme.accentCyan : (Theme.isDark ? "#EF4444" : "#DC2626")
                                }
                                MouseArea {
                                    id: hBtnMa
                                    anchors.fill: parent
                                    hoverEnabled: root.selectedShape !== null
                                    cursorShape: root.selectedShape ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    onClicked: {
                                        if (root.selectedShape) root.hatchTriggered(root.selectedShape)
                                    }
                                }
                                ToolTip.visible: hBtnMa.containsMouse
                                ToolTip.text: root.selectedShape ? "Hatch Infill Configuration (EZCad Standard)" : "Hatch Infill (Select an object first)"
                            }

                            // [ F ] Font Dialog Shortcut Button
                            Rectangle {
                                width: 32
                                height: 32
                                radius: 5
                                color: fBtnMa.containsMouse ? (Theme.isDark ? "#17233D" : "#E2E8F0") : Theme.bgCardAlt
                                border.color: Theme.borderCard
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "F"
                                    font.bold: true
                                    font.pixelSize: 11
                                    color: Theme.accentCyan
                                }
                                MouseArea {
                                    id: fBtnMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (root.selectedShape) root.fontDialogTriggered(root.selectedShape)
                                    }
                                }
                                ToolTip.visible: fBtnMa.containsMouse
                                ToolTip.text: "Advanced Font Settings & CircleText (Bold, Italic, Arc)"
                            }


                        }

                        // Text Alignment Segmented Control (Left, Center, Right)
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                text: "Align"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                font.bold: true
                                color: Theme.textSecondary
                                Layout.preferredWidth: 32
                                Layout.alignment: Qt.AlignVCenter
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4

                                Repeater {
                                    model: [
                                        { label: "Left", val: "left" },
                                        { label: "Center", val: "center" },
                                        { label: "Right", val: "right" }
                                    ]
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        height: 30
                                        radius: 5
                                        color: (root.selectedShape && (root.selectedShape.textAlign || "center") === modelData.val)
                                            ? (Theme.isDark ? "#1C3660" : "#DBEAFE")
                                            : (alMa.containsMouse ? (Theme.isDark ? "#17233D" : "#E2E8F0") : Theme.bgCardAlt)
                                        border.color: (root.selectedShape && (root.selectedShape.textAlign || "center") === modelData.val) ? Theme.accentCyan : Theme.borderCard
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.label
                                            font.family: "Segoe UI, Inter, sans-serif"
                                            font.pixelSize: 10
                                            font.bold: (root.selectedShape && (root.selectedShape.textAlign || "center") === modelData.val)
                                            color: (root.selectedShape && (root.selectedShape.textAlign || "center") === modelData.val) ? Theme.accentCyan : Theme.textSecondary
                                        }

                                        MouseArea {
                                            id: alMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (root.selectedShape) {
                                                    root.selectedShape.textAlign = modelData.val
                                                    if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                                    root.shapeModified(root.selectedShape)
                                                    root.applyTriggered(root.selectedShape)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Text Space and Height Inputs
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            CadInput {
                                id: textSpaceInput
                                Layout.fillWidth: true
                                label: "Space"
                                unit: "mm"
                                text: root.selectedShape ? Number(root.selectedShape.charSpace || 0).toFixed(3) : "0.000"
                                onValueChanged: function(v) {
                                    if (root.selectedShape) {
                                        root.selectedShape.charSpace = v
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        root.shapeModified(root.selectedShape)
                                    }
                                }
                            }

                            CadInput {
                                id: textHeightInput
                                Layout.fillWidth: true
                                label: "Height"
                                unit: "mm"
                                text: root.selectedShape ? Number(root.selectedShape.hMm || 4.0).toFixed(3) : "4.000"
                                onValueChanged: function(v) {
                                    if (root.selectedShape && root.selectedShape.type === "text") {
                                        root.selectedShape.hMm = Math.max(0.5, v)
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        if (typeof cad !== "undefined" && cad) {
                                            var m = cad.measureText(
                                                root.selectedShape.text || "TEXT",
                                                root.selectedShape.fontFamily || "Segoe UI",
                                                root.selectedShape.hMm,
                                                Boolean(root.selectedShape.bold),
                                                Boolean(root.selectedShape.italic)
                                            )
                                            if (m && m.wMm > 0) {
                                                root.selectedShape.wMm = m.wMm
                                                inputW.text = m.wMm.toFixed(3)
                                            }
                                        }
                                        inputH.text = root.selectedShape.hMm.toFixed(3)
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }
                        }

                        // Multiline Text Input Box
                        Text {
                            text: "Text"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 64
                            radius: 6
                            color: Theme.bgCardAlt
                            border.color: textEditArea.activeFocus ? Theme.accentCyan : Theme.borderCard
                            border.width: textEditArea.activeFocus ? 1.5 : 1

                            ScrollView {
                                anchors.fill: parent
                                anchors.margins: 6
                                clip: true

                                TextArea {
                                    id: textEditArea
                                    text: (root.selectedShape && root.selectedShape.type === "text") ? (root.selectedShape.text || "TEXT") : ""
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 12
                                    color: Theme.textPrimary
                                    wrapMode: TextEdit.Wrap
                                    selectByMouse: true
                                    background: null

                                    onTextChanged: {
                                        if (root.selectedShape && root.selectedShape.type === "text" && root.selectedShape.text !== text) {
                                            root.selectedShape.text = text
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            if (typeof cad !== "undefined" && cad) {
                                                var m = cad.measureText(
                                                    text || "TEXT",
                                                    root.selectedShape.fontFamily || "Segoe UI",
                                                    root.selectedShape.hMm || 4.0,
                                                    Boolean(root.selectedShape.bold),
                                                    Boolean(root.selectedShape.italic)
                                                )
                                                if (m && m.wMm > 0) {
                                                    root.selectedShape.wMm = m.wMm
                                                    inputW.text = m.wMm.toFixed(3)
                                                }
                                            }
                                            root.shapeModified(root.selectedShape)
                                        }
                                    }
                                }
                            }
                        }

                        // Variable Text Section
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            CadCheckBox {
                                text: "Enable variable Text"
                                checked: Boolean(root.selectedShape && root.selectedShape.enableVariableText)
                                onCheckedChanged: {
                                    if (root.selectedShape) {
                                        root.selectedShape.enableVariableText = checked
                                        if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                        root.shapeModified(root.selectedShape)
                                        root.applyTriggered(root.selectedShape)
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }

                            CadButton {
                                text: "Advance..."
                                iconName: "tune"
                                visible: Boolean(root.selectedShape && root.selectedShape.enableVariableText)
                                onClicked: {
                                    if (root.selectedShape) {
                                        root.variableTextDialogTriggered(root.selectedShape)
                                    }
                                }
                            }
                        }

                        // Variable Text Entity List (Screenshot 2026-10-23 171349.png)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            visible: Boolean(root.selectedShape && root.selectedShape.enableVariableText)

                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 70
                                radius: 4
                                color: Theme.bgCard
                                border.color: Theme.borderCard
                                border.width: 1
                                clip: true

                                ListView {
                                    id: varList
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    model: (root.selectedShape && root.selectedShape.variableEntities) ? root.selectedShape.variableEntities : []
                                    delegate: Rectangle {
                                        width: varList.width
                                        height: 20
                                        color: "transparent"
                                        RowLayout {
                                            anchors.fill: parent
                                            Text {
                                                text: modelData.type === "fixed" ? ("Fixed: \"" + modelData.text + "\"") :
                                                      (modelData.type === "serial" ? ("Serial: " + modelData.current + " (+" + modelData.step + ")") :
                                                      ("Date: " + modelData.format))
                                                font.pixelSize: 10
                                                color: Theme.textPrimary
                                            }
                                        }
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4

                                CadButton {
                                    Layout.fillWidth: true
                                    text: "+ Fixed"
                                    variant: "secondary"
                                    onClicked: {
                                        if (root.selectedShape) {
                                            if (!root.selectedShape.variableEntities) root.selectedShape.variableEntities = []
                                            root.selectedShape.variableEntities.push({ type: "fixed", text: "SN-" })
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                    }
                                }

                                CadButton {
                                    Layout.fillWidth: true
                                    text: "+ Serial"
                                    variant: "secondary"
                                    onClicked: {
                                        if (root.selectedShape) {
                                            if (!root.selectedShape.variableEntities) root.selectedShape.variableEntities = []
                                            root.selectedShape.variableEntities.push({ type: "serial", current: 1, step: 1, digits: 5 })
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                    }
                                }

                                CadButton {
                                    Layout.fillWidth: true
                                    text: "Clear"
                                    variant: "outline"
                                    onClicked: {
                                        if (root.selectedShape) {
                                            root.selectedShape.variableEntities = []
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // 5. DEDICATED 2D BARCODE & QR CODE INSPECTOR
                    // (Visible specifically when a Barcode or QR entity is selected)
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: root.selectedShape !== null && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || Boolean(root.selectedShape.isBarcode))

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Theme.borderCard
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: barcodeInnerCol.implicitHeight + 20
                            radius: 8
                            color: Theme.bgCardAlt
                            border.color: Theme.borderActive
                            border.width: 1

                            ColumnLayout {
                                id: barcodeInnerCol
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 8

                                RowLayout {
                                    Layout.fillWidth: true
                                    CadIcon {
                                        name: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode")) ? "qr_code_2" : "horizontal_rule"
                                        size: 16
                                        iconColor: Theme.accentCyan
                                    }
                                    Text {
                                        text: root.selectedShape ? ((root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode") ? "2D QR CODE MATRIX" : ((root.selectedShape.type === "barcode128" || root.selectedShape.barcodeType === "barcode128") ? "1D CODE 128 BARCODE" : "2D DATAMATRIX")) : "BARCODE"
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                        color: Theme.textPrimary
                                    }
                                    Item { Layout.fillWidth: true }
                                    Rectangle {
                                        width: 60
                                        height: 18
                                        radius: 4
                                        color: Qt.rgba(0.0, 0.8, 0.9, 0.15)
                                        border.color: Theme.accentCyan
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.barcodeType === "qrcode")) ? "ISO 18004" : "GS1"
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: Theme.accentCyan
                                        }
                                    }
                                }

                                Text {
                                    text: "ENCODED DATA CONTENT / SERIAL / URL"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.textMuted
                                }

                                TextField {
                                    id: barcodeContentInput
                                    Layout.fillWidth: true
                                    text: (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && root.selectedShape.text) ? String(root.selectedShape.text) : ""
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 11
                                    color: Theme.textPrimary
                                    placeholderText: "Enter URL, text, or serial..."
                                    background: Rectangle {
                                        radius: 5
                                        color: Theme.bgInput
                                        border.color: barcodeContentInput.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                        border.width: 1
                                    }
                                    onEditingFinished: {
                                        if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && text !== root.selectedShape.text) {
                                            root.selectedShape.text = text
                                            if (typeof cad !== "undefined" && cad) {
                                                var bType = root.selectedShape.barcodeType || root.selectedShape.type || "qrcode"
                                                var res = cad.generateBarcodeEntity(bType, text, root.selectedShape.wMm)
                                                if (res && res.rects) {
                                                    root.selectedShape.rects = res.rects
                                                    root.selectedShape.paths = res.paths
                                                    if (res.hMm) root.selectedShape.hMm = res.hMm
                                                }
                                            }
                                            if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "Regenerate Matrix"
                                        variant: "accent"
                                                                                onClicked: {
                                            if (root.selectedShape && (root.selectedShape.type === "qrcode" || root.selectedShape.type === "barcode128" || root.selectedShape.type === "datamatrix" || root.selectedShape.isBarcode) && typeof cad !== "undefined" && cad) {
                                                var bType2 = root.selectedShape.barcodeType || root.selectedShape.type || "qrcode"
                                                var res = cad.generateBarcodeEntity(bType2, root.selectedShape.text, root.selectedShape.wMm)
                                                if (res && res.rects) {
                                                    root.selectedShape.rects = res.rects
                                                    root.selectedShape.paths = res.paths
                                                    if (res.hMm) root.selectedShape.hMm = res.hMm
                                                }
                                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                                root.shapeModified(root.selectedShape)
                                                root.applyTriggered(root.selectedShape)
                                            }
                                        }
                                    }
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 1
                                    color: Theme.borderMuted
                                    opacity: 0.6
                                }

                                Text {
                                    text: "EXPORT / DOWNLOAD CODE ENTITY"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: Theme.textMuted
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "DXF"
                                                                                variant: "outline"
                                        tooltipText: "Export Vector DXF for EzCad / AutoCAD / LightBurn"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "dxf")
                                            }
                                        }
                                    }

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "SVG"
                                                                                variant: "outline"
                                        tooltipText: "Export Scalable Vector Graphics (SVG)"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "svg")
                                            }
                                        }
                                    }

                                    CadButton {
                                        Layout.fillWidth: true
                                        text: "PNG"
                                                                                variant: "outline"
                                        tooltipText: "Export High-Resolution Scannable PNG Image"
                                        onClicked: {
                                            if (root.selectedShape && typeof cad !== "undefined" && cad) {
                                                cad.exportBarcodeFile(root.selectedShape, "png")
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // TAB 2: LASER PENS & PROCESS PARAMETERS
            ScrollView {
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    x: 14
                    width: root.width - 28
                    spacing: 14
                    anchors.topMargin: 12
                    anchors.bottomMargin: 16

                    // Dynamic Laser Pens & Layers Header with Add Pen Action
                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "SELECT LASER PEN (" + Theme.penPalette.length + ")"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textMuted
                            font.letterSpacing: 0.5
                        }

                        Item { Layout.fillWidth: true }

                        CadButton {
                            text: "+ Add Pen"
                            iconName: "add"
                            variant: "outline"
                            implicitHeight: 24
                            onClicked: {
                                var newId = Theme.addPen()
                                root.selectedPenId = newId
                                root.penChanged(newId)
                                var p = Theme.getPen(newId)
                                if (p) {
                                    speedSlider.value = p.speed
                                    powerSlider.value = p.power
                                    freqSlider.value = p.freq
                                }
                            }
                        }
                    }

                    // Pen Swatches Grid (Flow layout for dynamic wrap)
                    Flow {
                        Layout.fillWidth: true
                        spacing: 7

                        Repeater {
                            model: Theme.penPalette

                            delegate: Rectangle {
                                width: 28
                                height: 28
                                radius: 14
                                color: modelData.color
                                border.color: root.selectedPenId === modelData.id ? Theme.accentCyan : (Theme.isDark ? "#17233D" : "#CBD5E1")
                                border.width: root.selectedPenId === modelData.id ? 2.5 : 1

                                scale: penMa.containsMouse ? 1.15 : 1.0
                                Behavior on scale { NumberAnimation { duration: 100 } }

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.id.toString()
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: (modelData.color.toUpperCase() === "#FFFFFF" || modelData.color.toUpperCase() === "#F8FAFC" || modelData.color.toUpperCase() === "#E2E8F0" || modelData.color.toUpperCase() === "#FDE047") ? "#000000" : "#FFFFFF"
                                }

                                MouseArea {
                                    id: penMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        root.selectedPenId = modelData.id
                                        if (root.selectedShape) {
                                            root.selectedShape.penId = modelData.id
                                            if (root.selectedShape.hatch_profiles) {
                                                for (var hk in root.selectedShape.hatch_profiles) {
                                                    root.selectedShape.hatch_profiles[hk].pen_no = modelData.id
                                                }
                                            }
                                            root.selectedShape.hatch_lines = []
                                            root.shapeModified(root.selectedShape)
                                            root.applyTriggered(root.selectedShape)
                                        }
                                        root.penChanged(modelData.id)
                                        speedSlider.value = modelData.speed
                                        powerSlider.value = modelData.power
                                        freqSlider.value = modelData.freq
                                    }
                                    onDoubleClicked: {
                                        root.openColorPickerRequested(modelData.id, modelData.color, modelData.name)
                                    }
                                }
                                ToolTip.visible: penMa.containsMouse
                                ToolTip.text: modelData.name + " (" + modelData.power + "% Pwr / " + modelData.speed + " mm/s) - Click to select, double-click for color palette"
                            }
                        }
                    }

                    // Active Pen Quick Info & Color Palette Bar
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 46
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            spacing: 8

                            Rectangle {
                                width: 30
                                height: 30
                                radius: 6
                                color: {
                                    var p = Theme.getPen(root.selectedPenId)
                                    return p ? p.color : "#00E5FF"
                                }
                                border.color: Theme.accentCyan
                                border.width: 1.5

                                CadIcon {
                                    anchors.centerIn: parent
                                    name: "palette"
                                    size: 15
                                    color: {
                                        var col = parent.color.toString().toUpperCase()
                                        return (col === "#FFFFFF" || col === "#F8FAFC" || col === "#E2E8F0" || col === "#FDE047") ? "#000000" : "#FFFFFF"
                                    }
                                }

                                MouseArea {
                                    id: swatchClickMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        var p = Theme.getPen(root.selectedPenId)
                                        root.openColorPickerRequested(root.selectedPenId, p ? p.color : "#00E5FF", p ? p.name : ("Pen " + root.selectedPenId))
                                    }
                                }
                                ToolTip.visible: swatchClickMa.containsMouse
                                ToolTip.text: "Click to select color from full palette"
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 1

                                Text {
                                    text: {
                                        var p = Theme.getPen(root.selectedPenId)
                                        return p ? p.name : ("Pen " + root.selectedPenId)
                                    }
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: Theme.textPrimary
                                    elide: Text.ElideRight
                                }
                                Text {
                                    text: {
                                        var p = Theme.getPen(root.selectedPenId)
                                        return p ? ("Color: " + p.color.toUpperCase()) : ""
                                    }
                                    font.family: "Consolas, monospace"
                                    font.pixelSize: 9
                                    color: Theme.textMuted
                                }
                            }

                            CadButton {
                                text: "Palette"
                                iconName: "palette"
                                variant: "secondary"
                                implicitHeight: 28
                                onClicked: {
                                    var p = Theme.getPen(root.selectedPenId)
                                    root.openColorPickerRequested(root.selectedPenId, p ? p.color : "#00E5FF", p ? p.name : ("Pen " + root.selectedPenId))
                                }
                            }

                            CadButton {
                                visible: root.selectedPenId > 0
                                iconName: "delete"
                                variant: "danger"
                                implicitHeight: 28
                                tooltipText: "Delete Pen " + root.selectedPenId
                                onClicked: {
                                    var delId = root.selectedPenId
                                    Theme.deletePen(delId)
                                    root.selectedPenId = 0
                                    root.penChanged(0)
                                    var p0 = Theme.getPen(0)
                                    if (p0) {
                                        speedSlider.value = p0.speed
                                        powerSlider.value = p0.power
                                        freqSlider.value = p0.freq
                                    }
                                }
                            }
                        }
                    }

                    // Apply Pen to selection
                    CadButton {
                        Layout.fillWidth: true
                        text: "Assign Pen " + root.selectedPenId + " to Selected Shape"
                        variant: "outline"
                        onClicked: {
                            if (root.selectedShape) {
                                root.selectedShape.penId = root.selectedPenId
                                if (root.selectedShape.hatch_profiles) {
                                    for (var hk in root.selectedShape.hatch_profiles) {
                                        root.selectedShape.hatch_profiles[hk].pen_no = root.selectedPenId
                                    }
                                }
                                root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                                root.penChanged(root.selectedPenId)
                            }
                        }
                    }

                    // Material Presets Card (Direct Connection)
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: 74
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4

                            Text {
                                text: "MATERIAL PRESET DATABASE"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 9
                                font.weight: Font.Bold
                                color: Theme.textMuted
                            }

                            CadComboBox {
                                id: presetCombo
                                Layout.fillWidth: true
                                Layout.preferredHeight: 32
                                model: [
                                    "304 Stainless Steel (Dark Engraving)",
                                    "Aluminum Anodized (Clean White)",
                                    "Hard Plastic (Low-Heat Frosting)",
                                    "Brass (Deep 3D Scribe)",
                                    "PCB Solder Mask Removal"
                                ]
                                currentIndex: 0
                                onActivated: function(index) {
                                    if (index === 0) { // Stainless Steel
                                        speedSlider.value = 1200; powerSlider.value = 75; freqSlider.value = 30
                                    } else if (index === 1) { // Aluminum
                                        speedSlider.value = 2000; powerSlider.value = 35; freqSlider.value = 55
                                    } else if (index === 2) { // Hard Plastic
                                        speedSlider.value = 2500; powerSlider.value = 18; freqSlider.value = 65
                                    } else if (index === 3) { // Brass
                                        speedSlider.value = 800; powerSlider.value = 85; freqSlider.value = 25
                                    } else if (index === 4) { // PCB
                                        speedSlider.value = 1800; powerSlider.value = 45; freqSlider.value = 40
                                    }
                                    if (typeof galvo !== "undefined" && galvo) {
                                        galvo.setParameters(powerSlider.value, speedSlider.value, freqSlider.value)
                                    }
                                }
                            }
                        }
                    }

                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Marking Speed"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: speedSlider.value.toFixed(0) + " mm/s"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentCyan }
                        }
                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            from: 100
                            to: 5000
                            value: 1200
                            stepSize: 50
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "speed", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setSpeed(value)
                            }
                        }
                    }

                    // Power
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Laser Power"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: powerSlider.value.toFixed(0) + " %"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                        }
                        Slider {
                            id: powerSlider
                            Layout.fillWidth: true
                            from: 5
                            to: 100
                            value: 50
                            stepSize: 1
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "power", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setPower(value)
                            }
                        }
                    }

                    // Frequency
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Q-Pulse Frequency"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: freqSlider.value.toFixed(0) + " kHz"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentGreen }
                        }
                        Slider {
                            id: freqSlider
                            Layout.fillWidth: true
                            from: 20
                            to: 100
                            value: 35
                            stepSize: 1
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "freq", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setFrequency(value)
                            }
                        }
                    }

                    // Passes
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        CadInput {
                            Layout.fillWidth: true
                            label: "Passes"
                            unit: "loops"
                            text: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.passes.toString() : "1"
                            }
                            onValueChanged: function(v) {
                                Theme.updatePenParam(root.selectedPenId, "passes", Math.max(1, Math.round(v)))
                            }
                        }
                    }

                    // Collapsible Advanced Timing Delays (TC)
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8

                            Item {
                                Layout.fillWidth: true
                                implicitHeight: 24

                                RowLayout {
                                    anchors.fill: parent
                                    spacing: 6
                                    CadIcon {
                                        name: root.advancedTcExpanded ? "expand_less" : "expand_more"
                                        size: 16
                                        iconColor: Theme.accentCyan
                                    }
                                    Text {
                                        text: "Advanced Timing Delays (TC)"
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: Theme.textPrimary
                                        Layout.fillWidth: true
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.advancedTcExpanded = !root.advancedTcExpanded
                                }
                            }

                            GridLayout {
                                visible: root.advancedTcExpanded
                                Layout.fillWidth: true
                                columns: 2
                                columnSpacing: 8
                                rowSpacing: 6

                                CadInput { label: "Start TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Laser Off"; unit: "µs"; text: "100" }
                                CadInput { label: "End TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Poly TC"; unit: "µs"; text: "100" }
                            }
                        }
                    }
                }
            }
        }
    }
}
