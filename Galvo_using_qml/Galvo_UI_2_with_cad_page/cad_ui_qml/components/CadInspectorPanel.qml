import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root

    property var selectedShape: null
    property int selectedPenId: 0
    property alias currentTabIndex: tabGroup.currentIndex

    signal shapeModified(var shape)
    signal penChanged(int penId)

    width: 340
    color: CadTheme.bgCard
    border.color: CadTheme.borderCard
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Inspector Tab Bar (Design & Transform vs Laser Parameters)
        Rectangle {
            Layout.fillWidth: true
            height: 44
            color: CadTheme.bgCardHeader
            border.color: CadTheme.borderCard
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4

                TabBar {
                    id: tabGroup
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: 0
                    background: null

                    TabButton {
                        width: (tabGroup.width - 4) / 2
                        height: tabGroup.height
                        text: "Design & Transform"
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: tabGroup.currentIndex === 0 ? Font.Bold : Font.DemiBold
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: tabGroup.currentIndex === 0 ? (CadTheme.isDark ? "#00E5FF" : "#1D4ED8") : CadTheme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabGroup.currentIndex === 0 ? (CadTheme.isDark ? "#17233D" : "#FFFFFF") : "transparent"
                            radius: 5
                            border.color: tabGroup.currentIndex === 0 ? CadTheme.borderActive : "transparent"
                            border.width: 1
                        }
                    }

                    TabButton {
                        width: (tabGroup.width - 4) / 2
                        height: tabGroup.height
                        text: "Laser Pens & Process"
                        font.family: "Inter"
                        font.pixelSize: 11
                        font.weight: tabGroup.currentIndex === 1 ? Font.Bold : Font.DemiBold
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: tabGroup.currentIndex === 1 ? (CadTheme.isDark ? "#00E5FF" : "#1D4ED8") : CadTheme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabGroup.currentIndex === 1 ? (CadTheme.isDark ? "#17233D" : "#FFFFFF") : "transparent"
                            radius: 5
                            border.color: tabGroup.currentIndex === 1 ? CadTheme.borderActive : "transparent"
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

            // TAB 1: DESIGN & TRANSFORM
            ScrollView {
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                ColumnLayout {
                    x: 14
                    width: root.width - 28
                    spacing: 16
                    anchors.topMargin: 12
                    anchors.bottomMargin: 16

                    // Selected Object Header Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 48
                        radius: 6
                        color: CadTheme.bgCardAlt
                        border.color: CadTheme.borderCard
                        border.width: 1

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 8

                            CadIcon {
                                name: root.selectedShape ? "category" : "touch_app"
                                size: 18
                                iconColor: CadTheme.accentCyan
                            }

                            ColumnLayout {
                                spacing: 1
                                Text {
                                    text: root.selectedShape ? root.selectedShape.name : "No Selection"
                                    font.family: "Inter"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: CadTheme.textPrimary
                                }
                                Text {
                                    text: root.selectedShape ? ("Type: " + root.selectedShape.type.toUpperCase()) : "Click an object on canvas"
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    color: CadTheme.textMuted
                                }
                            }
                        }
                    }

                    // Section: Transform Coordinates
                    Text {
                        text: "TRANSFORM & DIMENSIONS"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: CadTheme.textMuted
                        font.letterSpacing: 0.5
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 10

                        CadInput {
                            label: "X"
                            unit: "mm"
                            text: root.selectedShape ? root.selectedShape.xMm.toFixed(2) : "0.00"
                            onValueChanged: function(v) {
                                if (root.selectedShape) {
                                    root.selectedShape.xMm = v
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }

                        CadInput {
                            label: "Y"
                            unit: "mm"
                            text: root.selectedShape ? root.selectedShape.yMm.toFixed(2) : "0.00"
                            onValueChanged: function(v) {
                                if (root.selectedShape) {
                                    root.selectedShape.yMm = v
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }

                        CadInput {
                            label: "W"
                            unit: "mm"
                            text: root.selectedShape ? root.selectedShape.wMm.toFixed(2) : "0.00"
                            onValueChanged: function(v) {
                                if (root.selectedShape) {
                                    root.selectedShape.wMm = v
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }

                        CadInput {
                            label: "H"
                            unit: "mm"
                            text: root.selectedShape ? root.selectedShape.hMm.toFixed(2) : "0.00"
                            onValueChanged: function(v) {
                                if (root.selectedShape) {
                                    root.selectedShape.hMm = v
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }
                    }

                    // Aspect Ratio Lock & Rotation
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        CadInput {
                            Layout.fillWidth: true
                            label: "Rotate"
                            unit: "°"
                            text: root.selectedShape ? root.selectedShape.rotation.toString() : "0"
                            onValueChanged: function(v) {
                                if (root.selectedShape) {
                                    root.selectedShape.rotation = v
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }

                        CadButton {
                            iconName: "lock"
                            text: "Aspect"
                            isActive: true
                            tooltipText: "Lock proportional aspect ratio"
                        }
                    }

                    // Section: Layer & Pen Assignment
                    Text {
                        text: "LAYER PEN & HATCH"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: CadTheme.textMuted
                        font.letterSpacing: 0.5
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Rectangle {
                            width: 24
                            height: 24
                            radius: 12
                            color: root.selectedShape ? CadTheme.penPalette[root.selectedShape.penId].color : "#FFFFFF"
                            border.color: CadTheme.borderMuted
                            border.width: 1
                        }

                        Text {
                            text: root.selectedShape ? CadTheme.penPalette[root.selectedShape.penId].name : "Pen 0 (Default)"
                            font.family: "Inter"
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                            color: CadTheme.textPrimary
                            Layout.fillWidth: true
                        }

                        CadButton {
                            iconName: "texture"
                            text: "Hatch"
                            variant: (root.selectedShape && root.selectedShape.hatched) ? "accent" : "secondary"
                            onClicked: {
                                if (root.selectedShape) {
                                    root.selectedShape.hatched = !root.selectedShape.hatched
                                    root.shapeModified(root.selectedShape)
                                }
                            }
                        }
                    }

                    // Section: 9-Point Origin Anchor Reference
                    Text {
                        text: "ORIGIN ANCHOR"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: CadTheme.textMuted
                        font.letterSpacing: 0.5
                    }

                    Rectangle {
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 90
                        radius: 6
                        color: CadTheme.bgCardAlt
                        border.color: CadTheme.borderCard
                        border.width: 1

                        GridLayout {
                            anchors.centerIn: parent
                            columns: 3
                            columnSpacing: 10
                            rowSpacing: 10

                            Repeater {
                                model: 9
                                delegate: Rectangle {
                                    width: 10
                                    height: 10
                                    radius: 5
                                    color: index === 4 ? CadTheme.accentCyan : (CadTheme.isDark ? "#28385A" : "#CBD5E1")
                                    border.color: index === 4 ? "#FFFFFF" : "transparent"
                                    border.width: 1
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
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

                ColumnLayout {
                    x: 14
                    width: root.width - 28
                    spacing: 16
                    anchors.topMargin: 12
                    anchors.bottomMargin: 16

                    // 8-Pen Layer Swatches Bar
                    Text {
                        text: "ACTIVE LASER PEN"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: CadTheme.textMuted
                        font.letterSpacing: 0.5
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Repeater {
                            model: CadTheme.penPalette

                            delegate: Rectangle {
                                width: 28
                                height: 28
                                radius: 14
                                color: modelData.color
                                border.color: root.selectedPenId === modelData.id ? CadTheme.accentCyan : (CadTheme.isDark ? "#17233D" : "#CBD5E1")
                                border.width: root.selectedPenId === modelData.id ? 2.5 : 1

                                scale: penMa.containsMouse ? 1.15 : 1.0
                                Behavior on scale { NumberAnimation { duration: 100 } }

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.id.toString()
                                    font.family: "Inter"
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                    color: (modelData.id === 0 && CadTheme.isDark) ? "#000000" : "#FFFFFF"
                                }

                                MouseArea {
                                    id: penMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        root.selectedPenId = modelData.id
                                        root.penChanged(modelData.id)
                                    }
                                    ToolTip.visible: containsMouse
                                    ToolTip.text: modelData.name
                                }
                            }
                        }
                    }

                    // Material Presets Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 72
                        radius: 6
                        color: CadTheme.bgCardAlt
                        border.color: CadTheme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4

                            Text {
                                text: "MATERIAL PRESET"
                                font.family: "Inter"
                                font.pixelSize: 9
                                font.weight: Font.Bold
                                color: CadTheme.textMuted
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                ComboBox {
                                    id: presetCombo
                                    Layout.fillWidth: true
                                    model: [
                                        "Stainless Steel (Deep Cut)",
                                        "Aluminum (Anodize Marking)",
                                        "Hard Plastic (Frosting)",
                                        "Brass (Precision Engrave)",
                                        "PCB Solder Mask Ablation"
                                    ]
                                    currentIndex: 0
                                }

                                CadButton {
                                    iconName: "save"
                                    tooltipText: "Save current as custom preset"
                                }
                            }
                        }
                    }

                    // Primary Process Sliders & Inputs
                    Text {
                        text: "LASER PARAMETERS"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: CadTheme.textMuted
                        font.letterSpacing: 0.5
                    }

                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Marking Speed"; font.family: "Inter"; font.pixelSize: 11; color: CadTheme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: speedSlider.value.toFixed(0) + " mm/s"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: CadTheme.accentCyan }
                        }
                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            from: 100
                            to: 5000
                            value: CadTheme.penPalette[root.selectedPenId].speed
                            stepSize: 50
                        }
                    }

                    // Power
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Laser Power"; font.family: "Inter"; font.pixelSize: 11; color: CadTheme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: powerSlider.value.toFixed(0) + " %"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: CadTheme.accentAmber }
                        }
                        Slider {
                            id: powerSlider
                            Layout.fillWidth: true
                            from: 5
                            to: 100
                            value: CadTheme.penPalette[root.selectedPenId].power
                            stepSize: 1
                        }
                    }

                    // Frequency
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Q-Pulse Frequency"; font.family: "Inter"; font.pixelSize: 11; color: CadTheme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: freqSlider.value.toFixed(0) + " kHz"; font.family: "IBM Plex Mono"; font.pixelSize: 11; font.weight: Font.Bold; color: CadTheme.accentGreen }
                        }
                        Slider {
                            id: freqSlider
                            Layout.fillWidth: true
                            from: 20
                            to: 100
                            value: CadTheme.penPalette[root.selectedPenId].freq
                            stepSize: 1
                        }
                    }

                    // Loop Passes
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        CadInput {
                            Layout.fillWidth: true
                            label: "Passes"
                            unit: "loops"
                            text: CadTheme.penPalette[root.selectedPenId].passes.toString()
                        }
                        CadButton {
                            text: "Apply to All"
                            variant: "outline"
                            tooltipText: "Apply these parameters across all shapes"
                        }
                    }
                }
            }
        }
    }
}
