with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add signal openColorPickerRequested
signal_target = "    signal penChanged(int penId)"
signal_replacement = """    signal penChanged(int penId)
    signal openColorPickerRequested(int penId, string color, string name)"""

if signal_target in content:
    content = content.replace(signal_target, signal_replacement, 1)
    print("Added openColorPickerRequested signal")
else:
    print("WARNING: signal_target not found!")

# 2. Replace the pen swatches section
old_swatches = """                    // 8-Pen Layer Swatches Bar
                    Text {
                        text: "SELECT LASER PEN (0 TO 7)"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: Theme.textMuted
                        font.letterSpacing: 0.5
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

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
                                    color: (modelData.id === 0 && Theme.isDark) ? "#000000" : "#FFFFFF"
                                }

                                MouseArea {
                                    id: penMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        root.selectedPenId = modelData.id
                                        root.penChanged(modelData.id)
                                        speedSlider.value = modelData.speed
                                        powerSlider.value = modelData.power
                                        freqSlider.value = modelData.freq
                                    }
                                    ToolTip.visible: containsMouse
                                    ToolTip.text: modelData.name + " (" + modelData.power + "% Pwr / " + modelData.speed + " mm/s)"
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
                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                            }
                        }
                    }"""

new_swatches = """                    // Dynamic Laser Pens & Layers Header with Add Pen Action
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
                                if (root.selectedShape.hatch_lines) root.selectedShape.hatch_lines = []
                                root.shapeModified(root.selectedShape)
                                root.applyTriggered(root.selectedShape)
                            }
                        }
                    }"""

if old_swatches.replace('\n', '\r\n') in content:
    content = content.replace(old_swatches.replace('\n', '\r\n'), new_swatches.replace('\n', '\r\n'), 1)
    print("Replaced swatches section (CRLF)")
elif old_swatches in content:
    content = content.replace(old_swatches, new_swatches, 1)
    print("Replaced swatches section (LF)")
else:
    print("WARNING: old_swatches not found!")

# 3. Update sliders to use Theme.getPen(root.selectedPenId)
old_sliders = """                            value: Theme.penPalette[root.selectedPenId].speed
                            stepSize: 50
                            onValueChanged: {
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
                            value: Theme.penPalette[root.selectedPenId].power
                            stepSize: 1
                            onValueChanged: {
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
                            value: Theme.penPalette[root.selectedPenId].freq
                            stepSize: 1
                            onValueChanged: {
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
                            text: Theme.penPalette[root.selectedPenId].passes.toString()
                        }
                    }"""

new_sliders = """                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.speed : 1200
                            }
                            stepSize: 50
                            onValueChanged: {
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
                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.power : 50
                            }
                            stepSize: 1
                            onValueChanged: {
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
                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.freq : 35
                            }
                            stepSize: 1
                            onValueChanged: {
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
                    }"""

if old_sliders.replace('\n', '\r\n') in content:
    content = content.replace(old_sliders.replace('\n', '\r\n'), new_sliders.replace('\n', '\r\n'), 1)
    print("Replaced sliders section (CRLF)")
elif old_sliders in content:
    content = content.replace(old_sliders, new_sliders, 1)
    print("Replaced sliders section (LF)")
else:
    print("WARNING: old_sliders not found!")

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved CadInspectorPanel.qml")

