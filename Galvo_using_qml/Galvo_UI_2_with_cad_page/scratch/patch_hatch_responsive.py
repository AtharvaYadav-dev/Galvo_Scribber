with open("qml/components/cad/CadHatchModal.qml", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update modalCard geometry & window resize clamping
old_modal_card = """    // Modern Studio Card Window (Movable floating card)
    Rectangle {
        id: modalCard
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: 760
        height: 600
        radius: 12"""

new_modal_card = """    onWidthChanged: {
        if (width > 0 && modalCard.x + modalCard.width > width - 10) {
            modalCard.x = Math.max(10, width - modalCard.width - 10)
        }
    }
    onHeightChanged: {
        if (height > 0 && modalCard.y + modalCard.height > height - 10) {
            modalCard.y = Math.max(10, height - modalCard.height - 10)
        }
    }

    // Modern Studio Card Window (Movable floating card)
    Rectangle {
        id: modalCard
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: Math.min(840, Math.max(540, root.width > 0 ? (root.width - 40) : 780))
        height: Math.min(680, Math.max(450, root.height > 0 ? (root.height - 40) : 600))
        radius: 12"""

assert old_modal_card in content, "old_modal_card not found"
content = content.replace(old_modal_card, new_modal_card)

# 2. Update ScrollView & Top Command Strip
old_scroll_view = """            // Scrollable Content View for responsive scaling
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: Math.max(720, modalCard.width - 32)
                    spacing: 12

                    // ================= 2. TOP COMMAND STRIP =================
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                // Global Boundary Contour Card
                Rectangle {
                    Layout.preferredWidth: 320
                    Layout.preferredHeight: 48
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1"""

new_scroll_view = """            // Scrollable Content View for responsive scaling
            ScrollView {
                id: hatchScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
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
                    Layout.fillWidth: true
                    Layout.preferredWidth: (modalCard.width >= 720) ? 300 : -1
                    Layout.preferredHeight: 48
                    radius: 8
                    color: Theme.bgCardAlt
                    border.color: Theme.borderCard
                    border.width: 1"""

assert old_scroll_view in content, "old_scroll_view not found"
content = content.replace(old_scroll_view, new_scroll_view)

# 3. Update Two-Column Balanced Studio Body to responsive GridLayout
old_cards_row = """            // ================= 3. TWO-COLUMN BALANCED STUDIO BODY =================
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12"""

new_cards_row = """            // ================= 3. TWO-COLUMN BALANCED STUDIO BODY =================
            GridLayout {
                Layout.fillWidth: true
                columns: (modalCard.width >= 700) ? 2 : 1
                columnSpacing: 12
                rowSpacing: 12"""

assert old_cards_row in content, "old_cards_row not found"
content = content.replace(old_cards_row, new_cards_row)

# 4. Update Footer for responsive compact layout
old_footer = """            // ================= 4. STUDIO ACTION FOOTER =================
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Text {
                    text: "Active: " + root.currentHatchType + " (" + angleInput.text + "°, " + lineSpaceInput.text + "mm) | Contour: " + (root.markContour ? (root.markContourFirst ? "ON (Pre-Hatch)" : "ON (Post-Hatch)") : "OFF")
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    color: Theme.textSecondary
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    implicitWidth: 105
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
                    implicitWidth: 85
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
                    implicitWidth: 85
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
                    implicitWidth: 120
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
            }"""

new_footer = """            // ================= 4. STUDIO ACTION FOOTER =================
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
            }"""

assert old_footer in content, "old_footer not found"
content = content.replace(old_footer, new_footer)

# 5. Update CadWindowResizeHandle minWidth
old_resize = """        CadWindowResizeHandle {
            target: modalCard
            minWidth: 620
            minHeight: 450
        }"""

new_resize = """        CadWindowResizeHandle {
            target: modalCard
            minWidth: 540
            minHeight: 420
        }"""

assert old_resize in content, "old_resize not found"
content = content.replace(old_resize, new_resize)

with open("qml/components/cad/CadHatchModal.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated CadHatchModal.qml with responsive layout")

