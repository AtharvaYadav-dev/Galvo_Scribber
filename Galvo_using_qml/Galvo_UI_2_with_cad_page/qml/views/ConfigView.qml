import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import ".."

Item {
    id: root

    implicitWidth: 980
    implicitHeight: 620

    signal requestClose()

    // Working copies initialized from settings bridge
    property real wFieldSize: (typeof settings !== "undefined" && settings) ? settings.fieldSize : 70.0
    property real wOffsetX: (typeof settings !== "undefined" && settings) ? settings.offsetX : 0.0
    property real wOffsetY: (typeof settings !== "undefined" && settings) ? settings.offsetY : 0.0
    property real wAngle: (typeof settings !== "undefined" && settings) ? settings.fieldAngle : 0.0
    property bool wGalvo1X: (typeof settings !== "undefined" && settings) ? settings.galvo1X : false

    property bool wG1Neg: (typeof settings !== "undefined" && settings) ? settings.g1Negate : false
    property real wG1Scale: (typeof settings !== "undefined" && settings) ? settings.g1Scale : 100.0
    property real wG1Barrel: (typeof settings !== "undefined" && settings) ? settings.g1Barrel : 1.0
    property real wG1Par: (typeof settings !== "undefined" && settings) ? settings.g1Par : 1.0
    property real wG1Trap: (typeof settings !== "undefined" && settings) ? settings.g1Trapezoid : 1.0

    property bool wG2Neg: (typeof settings !== "undefined" && settings) ? settings.g2Negate : false
    property real wG2Scale: (typeof settings !== "undefined" && settings) ? settings.g2Scale : 100.0
    property real wG2Barrel: (typeof settings !== "undefined" && settings) ? settings.g2Barrel : 1.0
    property real wG2Par: (typeof settings !== "undefined" && settings) ? settings.g2Par : 1.0
    property real wG2Trap: (typeof settings !== "undefined" && settings) ? settings.g2Trapezoid : 1.0

    property string wPosAfter: (typeof settings !== "undefined" && settings) ? settings.posAfterMark : "confgalvocent"
    property real wSpX: (typeof settings !== "undefined" && settings) ? settings.spX : 0.0
    property real wSpY: (typeof settings !== "undefined" && settings) ? settings.spY : 0.0

    function syncInputsFromWorkingCopies() {
        if (typeof fieldSzIn !== "undefined" && fieldSzIn) fieldSzIn.text = root.wFieldSize.toFixed(1);
        if (typeof offXIn !== "undefined" && offXIn) offXIn.text = root.wOffsetX.toFixed(2);
        if (typeof offYIn !== "undefined" && offYIn) offYIn.text = root.wOffsetY.toFixed(2);
        if (typeof angIn !== "undefined" && angIn) angIn.text = root.wAngle.toFixed(2);

        if (typeof g1ScaleIn !== "undefined" && g1ScaleIn) g1ScaleIn.text = root.wG1Scale.toFixed(4);
        if (typeof g1BarIn !== "undefined" && g1BarIn) g1BarIn.text = root.wG1Barrel.toFixed(3);
        if (typeof g1ParIn !== "undefined" && g1ParIn) g1ParIn.text = root.wG1Par.toFixed(3);
        if (typeof g1TrapIn !== "undefined" && g1TrapIn) g1TrapIn.text = root.wG1Trap.toFixed(3);

        if (typeof g2ScaleIn !== "undefined" && g2ScaleIn) g2ScaleIn.text = root.wG2Scale.toFixed(4);
        if (typeof g2BarIn !== "undefined" && g2BarIn) g2BarIn.text = root.wG2Barrel.toFixed(3);
        if (typeof g2ParIn !== "undefined" && g2ParIn) g2ParIn.text = root.wG2Par.toFixed(3);
        if (typeof g2TrapIn !== "undefined" && g2TrapIn) g2TrapIn.text = root.wG2Trap.toFixed(3);

        if (typeof spXIn !== "undefined" && spXIn) spXIn.text = root.wSpX.toFixed(2);
        if (typeof spYIn !== "undefined" && spYIn) spYIn.text = root.wSpY.toFixed(2);
    }

    property bool initializing: false

    function refreshFromBridge() {
        if (typeof settings === "undefined" || !settings) return;
        initializing = true;
        wFieldSize = settings.fieldSize;
        wOffsetX = settings.offsetX;
        wOffsetY = settings.offsetY;
        wAngle = settings.fieldAngle;
        wGalvo1X = settings.galvo1X;

        wG1Neg = settings.g1Negate;
        wG1Scale = settings.g1Scale;
        wG1Barrel = settings.g1Barrel;
        wG1Par = settings.g1Par;
        wG1Trap = settings.g1Trapezoid;

        wG2Neg = settings.g2Negate;
        wG2Scale = settings.g2Scale;
        wG2Barrel = settings.g2Barrel;
        wG2Par = settings.g2Par;
        wG2Trap = settings.g2Trapezoid;

        wPosAfter = settings.posAfterMark;
        wSpX = settings.spX;
        wSpY = settings.spY;

        syncInputsFromWorkingCopies();
        initializing = false;
        livePreviewSync();
    }

    Component.onCompleted: {
        refreshFromBridge();
    }

    onVisibleChanged: {
        if (visible) {
            refreshFromBridge();
        }
    }

    function livePreviewSync() {
        if (initializing) return;
        if (typeof cad !== "undefined" && cad) {
            cad.setFullGalvoConfig(
                wFieldSize, wOffsetX, wOffsetY, wAngle, wGalvo1X,
                wG1Neg, wG1Scale, wG1Barrel, wG1Par, wG1Trap,
                wG2Neg, wG2Scale, wG2Barrel, wG2Par, wG2Trap,
                wPosAfter, wSpX, wSpY
            );
        }
    }

    onWFieldSizeChanged: livePreviewSync()
    onWOffsetXChanged: livePreviewSync()
    onWOffsetYChanged: livePreviewSync()
    onWAngleChanged: livePreviewSync()
    onWGalvo1XChanged: livePreviewSync()
    onWG1NegChanged: livePreviewSync()
    onWG1ScaleChanged: livePreviewSync()
    onWG1BarrelChanged: livePreviewSync()
    onWG1ParChanged: livePreviewSync()
    onWG1TrapChanged: livePreviewSync()
    onWG2NegChanged: livePreviewSync()
    onWG2ScaleChanged: livePreviewSync()
    onWG2BarrelChanged: livePreviewSync()
    onWG2ParChanged: livePreviewSync()
    onWG2TrapChanged: livePreviewSync()
    onWPosAfterChanged: livePreviewSync()
    onWSpXChanged: livePreviewSync()
    onWSpYChanged: livePreviewSync()

    function saveAll() {
        if (typeof settings !== "undefined" && settings) {
            settings.saveFullConfigGalvo(
                wFieldSize, wOffsetX, wOffsetY, wAngle, wGalvo1X,
                wG1Neg, wG1Scale, wG1Barrel, wG1Par, wG1Trap,
                wG2Neg, wG2Scale, wG2Barrel, wG2Par, wG2Trap,
                wPosAfter, wSpX, wSpY
            );
        }
    }

    // =========================================================================
    // CUSTOM SLEEK INDUSTRIAL RADIO BUTTON (ELIMINATES QT QUICK BASIC WHITE BLOBS)
    // =========================================================================
    component StyledRadioButton: RadioButton {
        id: rbControl
        implicitHeight: 28
        spacing: 10

        indicator: Rectangle {
            implicitWidth: 18
            implicitHeight: 18
            x: rbControl.leftPadding
            anchors.verticalCenter: parent.verticalCenter
            radius: 9
            color: rbControl.checked ? "#0e1a2d" : (rbControl.hovered ? "#1b2537" : "#111724")
            border.color: rbControl.checked ? Theme.accentCyan : (rbControl.hovered ? "#4a6288" : "#2b384e")
            border.width: rbControl.checked ? 2 : 1

            Rectangle {
                width: 8
                height: 8
                anchors.centerIn: parent
                radius: 4
                color: Theme.accentCyan
                visible: rbControl.checked
            }
        }

        contentItem: Text {
            text: rbControl.text
            font.family: "Segoe UI, Inter, sans-serif"
            font.pixelSize: 12
            font.weight: rbControl.checked ? Font.DemiBold : Font.Normal
            color: rbControl.checked ? "#ffffff" : Theme.textSecondary
            verticalAlignment: Text.AlignVCenter
            leftPadding: rbControl.indicator.width + rbControl.spacing
        }
    }

    // =========================================================================
    // CUSTOM SLEEK INDUSTRIAL CHECKBOX
    // =========================================================================
    component StyledCheckBox: CheckBox {
        id: cbControl
        implicitHeight: 28
        spacing: 10

        indicator: Rectangle {
            implicitWidth: 18
            implicitHeight: 18
            x: cbControl.leftPadding
            anchors.verticalCenter: parent.verticalCenter
            radius: 4
            color: cbControl.checked ? Theme.accentCyan : (cbControl.hovered ? "#1b2537" : "#111724")
            border.color: cbControl.checked ? Theme.accentCyan : (cbControl.hovered ? "#4a6288" : "#2b384e")
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "✓"
                font.pixelSize: 12
                font.bold: true
                color: "#000000"
                visible: cbControl.checked
            }
        }

        contentItem: Text {
            text: cbControl.text
            font.family: "Segoe UI, Inter, sans-serif"
            font.pixelSize: 12
            color: cbControl.checked ? "#ffffff" : Theme.textSecondary
            verticalAlignment: Text.AlignVCenter
            leftPadding: cbControl.indicator.width + cbControl.spacing
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Main 2-column workspace
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            // ================= LEFT REGION (Aspect + Galvo 1 & 2) ================= //
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 12

                // 1. ASPECT BOX
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: aspectCol.implicitHeight + 24
                    radius: 8
                    color: Theme.isDark ? "#121824" : "#F8FAFC"
                    border.color: Theme.borderCard
                    border.width: 1

                    ColumnLayout {
                        id: aspectCol
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        // Section Title
                        Text {
                            text: "Aspect"
                            color: Theme.accentCyan
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 18

                            // Aspect Numeric Fields Grid
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 10
                                rowSpacing: 8

                                // Field Size
                                Text { text: "Field Size :"; color: Theme.textSecondary; font.pixelSize: 12; Layout.preferredWidth: 85 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: fieldSzIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: fieldSzIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wFieldSize.toFixed(1)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v) && v > 0) root.wFieldSize = v; }
                                    }
                                }
                                Text { text: "mm"; color: Theme.textMuted; font.pixelSize: 11; Layout.preferredWidth: 28 }

                                // Offset X
                                Text { text: "Offset X :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: offXIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: offXIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wOffsetX.toFixed(2)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wOffsetX = v; }
                                    }
                                }
                                Text { text: "mm"; color: Theme.textMuted; font.pixelSize: 11 }

                                // Offset Y
                                Text { text: "Offset Y :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: offYIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: offYIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wOffsetY.toFixed(2)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wOffsetY = v; }
                                    }
                                }
                                Text { text: "mm"; color: Theme.textMuted; font.pixelSize: 11 }

                                // Angle
                                Text { text: "Angle :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: angIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: angIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wAngle.toFixed(2)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wAngle = v; }
                                    }
                                }
                                Text { text: "°"; color: Theme.textMuted; font.pixelSize: 11 }
                            }

                            // Vertical divider
                            Rectangle {
                                width: 1
                                Layout.fillHeight: true
                                color: Theme.borderCard
                            }

                            // Mirror Assignment Radio Buttons
                            ButtonGroup { id: mirrorAssignGroup }

                            ColumnLayout {
                                Layout.preferredWidth: 140
                                Layout.alignment: Qt.AlignVCenter
                                spacing: 12

                                StyledRadioButton {
                                    text: "Galvo 1 = X"
                                    ButtonGroup.group: mirrorAssignGroup
                                    checked: root.wGalvo1X
                                    onToggled: if (checked) root.wGalvo1X = true
                                }

                                StyledRadioButton {
                                    text: "Galvo 2 = X"
                                    ButtonGroup.group: mirrorAssignGroup
                                    checked: !root.wGalvo1X
                                    onToggled: if (checked) root.wGalvo1X = false
                                }
                            }
                        }
                    }
                }

                // 2. GALVO 1 & GALVO 2 SIDE BY SIDE
                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 12

                    // GALVO 1
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 8
                        color: Theme.isDark ? "#121824" : "#F8FAFC"
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            Text {
                                text: "Galvo 1"
                                color: Theme.accentCyan
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                            }

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 8
                                rowSpacing: 8

                                // Negate
                                Text { text: "Negate :"; color: Theme.textSecondary; font.pixelSize: 12; Layout.preferredWidth: 100 }
                                StyledCheckBox {
                                    checked: root.wG1Neg
                                    onToggled: root.wG1Neg = checked
                                    Layout.columnSpan: 2
                                }

                                // Scale
                                Text { text: "Scale :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g1ScaleIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g1ScaleIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG1Scale.toFixed(4)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG1Scale = v; }
                                    }
                                }
                                Button {
                                    text: ">>"
                                    implicitWidth: 38; implicitHeight: 32
                                    background: Rectangle {
                                        color: parent.down ? "#0088cc" : "#1a3354"
                                        border.color: Theme.accentCyan
                                        radius: 4
                                    }
                                    contentItem: Text { text: ">>"; color: Theme.accentCyan; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    onClicked: scalePopup.openCalibrator(1, root.wG1Scale)
                                }

                                // Barrel / Bulge
                                Text { text: "Barrel/Bulge :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g1BarIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g1BarIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG1Barrel.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG1Barrel = v; }
                                    }
                                }
                                Item { width: 38 }

                                // Parallelogram
                                Text { text: "Parallelogram :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g1ParIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g1ParIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG1Par.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG1Par = v; }
                                    }
                                }
                                Item { width: 38 }

                                // Trapezoid
                                Text { text: "Trapezoid :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g1TrapIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g1TrapIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG1Trap.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG1Trap = v; }
                                    }
                                }
                                Item { width: 38 }
                            }

                            Item { Layout.fillHeight: true }
                        }
                    }

                    // GALVO 2
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 8
                        color: Theme.isDark ? "#121824" : "#F8FAFC"
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            Text {
                                text: "Galvo 2"
                                color: Theme.accentCyan
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                            }

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 8
                                rowSpacing: 8

                                // Negate
                                Text { text: "Negate :"; color: Theme.textSecondary; font.pixelSize: 12; Layout.preferredWidth: 100 }
                                StyledCheckBox {
                                    checked: root.wG2Neg
                                    onToggled: root.wG2Neg = checked
                                    Layout.columnSpan: 2
                                }

                                // Scale
                                Text { text: "Scale :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g2ScaleIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g2ScaleIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG2Scale.toFixed(4)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG2Scale = v; }
                                    }
                                }
                                Button {
                                    text: ">>"
                                    implicitWidth: 38; implicitHeight: 32
                                    background: Rectangle {
                                        color: parent.down ? "#0088cc" : "#1a3354"
                                        border.color: Theme.accentCyan
                                        radius: 4
                                    }
                                    contentItem: Text { text: ">>"; color: Theme.accentCyan; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    onClicked: scalePopup.openCalibrator(2, root.wG2Scale)
                                }

                                // Barrel / Bulge
                                Text { text: "Barrel/Bulge :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g2BarIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g2BarIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG2Barrel.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG2Barrel = v; }
                                    }
                                }
                                Item { width: 38 }

                                // Parallelogram
                                Text { text: "Parallelogram :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g2ParIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g2ParIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG2Par.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG2Par = v; }
                                    }
                                }
                                Item { width: 38 }

                                // Trapezoid
                                Text { text: "Trapezoid :"; color: Theme.textSecondary; font.pixelSize: 12 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 32; radius: 5
                                    color: Theme.bgInput; border.color: g2TrapIn.activeFocus ? Theme.accentCyan : Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: g2TrapIn
                                        anchors.fill: parent; anchors.margins: 6
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12; font.weight: Font.Bold
                                        color: Theme.textPrimary
                                        text: root.wG2Trap.toFixed(3)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wG2Trap = v; }
                                    }
                                }
                                Item { width: 38 }
                            }

                            Item { Layout.fillHeight: true }
                        }
                    }
                }
            }

            // ================= RIGHT REGION (Go to Pos After Mark) ================= //
            Rectangle {
                Layout.preferredWidth: 260
                Layout.fillHeight: true
                radius: 8
                color: Theme.isDark ? "#121824" : "#F8FAFC"
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8

                    Text {
                        text: "Go to Pos After Mark"
                        color: Theme.accentCyan
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 13
                        font.weight: Font.Bold
                    }

                    ButtonGroup { id: parkGroup }

                    StyledRadioButton {
                        text: "No Movement"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "confnomov" || root.wPosAfter === "confnomovRadioButton"
                        onToggled: if (checked) root.wPosAfter = "confnomov"
                    }

                    StyledRadioButton {
                        text: "Galvo Center"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "confgalvocent" || root.wPosAfter === "confgalvocentRadioButton"
                        onToggled: if (checked) root.wPosAfter = "confgalvocent"
                    }

                    StyledRadioButton {
                        text: "Top Left"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "conftopleft" || root.wPosAfter === "conftopleftRadioButton"
                        onToggled: if (checked) root.wPosAfter = "conftopleft"
                    }

                    StyledRadioButton {
                        text: "Top Right"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "conftopright" || root.wPosAfter === "conftoprightRadioButton"
                        onToggled: if (checked) root.wPosAfter = "conftopright"
                    }

                    StyledRadioButton {
                        text: "Bottom Right"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "confbotright" || root.wPosAfter === "confbotrightRadioButton"
                        onToggled: if (checked) root.wPosAfter = "confbotright"
                    }

                    StyledRadioButton {
                        text: "Bottom Left"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "confbotleft" || root.wPosAfter === "confbotleftRadioButton"
                        onToggled: if (checked) root.wPosAfter = "confbotleft"
                    }

                    StyledRadioButton {
                        id: specialPosRb
                        text: "Special Pos"
                        ButtonGroup.group: parkGroup
                        checked: root.wPosAfter === "confspecpos" || root.wPosAfter === "confspecposRadioButton"
                        onToggled: if (checked) root.wPosAfter = "confspecpos"
                    }

                    // Special Pos Sub-Panel
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: spCol.implicitHeight + 14
                        radius: 6
                        color: Theme.bgInput
                        border.color: specialPosRb.checked ? Theme.accentCyan : Theme.borderInput
                        border.width: 1
                        opacity: specialPosRb.checked ? 1.0 : 0.4
                        enabled: specialPosRb.checked

                        ColumnLayout {
                            id: spCol
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 6

                            RowLayout {
                                Text { text: "X :"; color: Theme.textSecondary; font.pixelSize: 12; Layout.preferredWidth: 24 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 28; radius: 4
                                    color: "#0a0e17"; border.color: Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: spXIn
                                        anchors.fill: parent; anchors.margins: 4
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12
                                        color: Theme.textPrimary
                                        text: root.wSpX.toFixed(2)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wSpX = v; }
                                    }
                                }
                            }

                            RowLayout {
                                Text { text: "Y :"; color: Theme.textSecondary; font.pixelSize: 12; Layout.preferredWidth: 24 }
                                Rectangle {
                                    Layout.fillWidth: true; height: 28; radius: 4
                                    color: "#0a0e17"; border.color: Theme.borderInput; border.width: 1
                                    TextInput {
                                        id: spYIn
                                        anchors.fill: parent; anchors.margins: 4
                                        verticalAlignment: TextInput.AlignVCenter
                                        font.family: "Consolas"; font.pixelSize: 12
                                        color: Theme.textPrimary
                                        text: root.wSpY.toFixed(2)
                                        selectByMouse: true
                                        onTextChanged: { var v = parseFloat(text); if (!isNaN(v)) root.wSpY = v; }
                                    }
                                }
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }

        // ================= BOTTOM ACTION BAR ================= //
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Layout.topMargin: 4

            Item { Layout.fillWidth: true }

            ModernButton {
                text: "OK"
                primary: true
                implicitWidth: 100
                implicitHeight: 36
                onClicked: {
                    root.saveAll();
                    root.requestClose();
                }
            }

            ModernButton {
                text: "Cancel"
                implicitWidth: 100
                implicitHeight: 36
                btnColor: Theme.isDark ? "#1E293B" : "#E2E8F0"
                textColor: Theme.textPrimary
                onClicked: {
                    root.refreshFromBridge();
                    root.requestClose();
                }
            }

            ModernButton {
                text: "Apply"
                implicitWidth: 100
                implicitHeight: 36
                btnColor: Theme.accentCyan
                textColor: "#000000"
                onClicked: {
                    root.saveAll();
                }
            }
        }
    }

    // ================= SCALE CALIBRATION POPUP ================= //
    Popup {
        id: scalePopup
        anchors.centerIn: parent
        width: 380
        height: 280
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        property int targetGalvo: 1
        property real initialScale: 100.0

        function openCalibrator(galvoNum, currentScale) {
            targetGalvo = galvoNum;
            initialScale = currentScale;
            desiredIn.text = "50.0";
            actualIn.text = "50.0";
            compScaleLabel.text = currentScale.toFixed(4);
            scalePopup.open();
        }

        background: Rectangle {
            color: Theme.bgCard
            border.color: Theme.accentCyan
            border.width: 1.5
            radius: 10
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            Text {
                text: "Scale Calibration (Galvo " + scalePopup.targetGalvo + ")"
                color: Theme.accentCyan
                font.pixelSize: 14
                font.bold: true
            }

            Text {
                text: "Enter desired dimension vs actual test measured dimension to auto-scale."
                color: Theme.textSecondary
                font.pixelSize: 11
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            RowLayout {
                Text { text: "Desired (mm):"; color: Theme.textSecondary; Layout.preferredWidth: 100; font.pixelSize: 11 }
                Rectangle {
                    Layout.fillWidth: true; height: 30; radius: 4
                    color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                    TextInput {
                        id: desiredIn
                        anchors.fill: parent; anchors.margins: 4
                        verticalAlignment: TextInput.AlignVCenter
                        color: Theme.textPrimary; font.family: "Consolas"; text: "50.0"
                        selectByMouse: true
                        onTextChanged: recompute()
                    }
                }
            }

            RowLayout {
                Text { text: "Actual (mm):"; color: Theme.textSecondary; Layout.preferredWidth: 100; font.pixelSize: 11 }
                Rectangle {
                    Layout.fillWidth: true; height: 30; radius: 4
                    color: Theme.bgInput; border.color: Theme.borderInput; border.width: 1
                    TextInput {
                        id: actualIn
                        anchors.fill: parent; anchors.margins: 4
                        verticalAlignment: TextInput.AlignVCenter
                        color: Theme.textPrimary; font.family: "Consolas"; text: "50.0"
                        selectByMouse: true
                        onTextChanged: recompute()
                    }
                }
            }

            RowLayout {
                spacing: 8
                Text { text: "New Scale (%):"; color: Theme.textPrimary; font.bold: true; font.pixelSize: 12 }
                Text { id: compScaleLabel; text: "100.0000"; color: Theme.accentGreen; font.bold: true; font.family: "Consolas"; font.pixelSize: 13 }
            }

            function recompute() {
                var des = parseFloat(desiredIn.text) || 0;
                var act = parseFloat(actualIn.text) || 0;
                if (act > 0 && typeof settings !== "undefined" && settings) {
                    var newSc = settings.computeScale(scalePopup.initialScale, des, act);
                    compScaleLabel.text = newSc.toFixed(4);
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 4
                spacing: 12

                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    text: "Cancel"
                    btnColor: Theme.isDark ? "#1E293B" : "#E2E8F0"
                    hoverColor: Theme.isDark ? "#283850" : "#CBD5E1"
                    borderColor: Theme.isDark ? "#334155" : "#94A3B8"
                    textColor: Theme.textPrimary
                    onClicked: scalePopup.close()
                }

                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    text: "Apply Scale"
                    btnColor: Theme.accentCyan
                    hoverColor: "#33e8ff"
                    borderColor: Theme.accentCyan
                    textColor: "#000000"
                    onClicked: {
                        var finalScale = parseFloat(compScaleLabel.text) || scalePopup.initialScale;
                        if (scalePopup.targetGalvo === 1) {
                            root.wG1Scale = finalScale;
                            g1ScaleIn.text = finalScale.toFixed(4);
                        } else {
                            root.wG2Scale = finalScale;
                            g2ScaleIn.text = finalScale.toFixed(4);
                        }
                        scalePopup.close();
                    }
                }
            }
        }
    }
}
