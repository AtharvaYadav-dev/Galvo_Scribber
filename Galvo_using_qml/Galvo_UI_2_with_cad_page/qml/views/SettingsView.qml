import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."
import "../components"

Item {
    id: root

    implicitWidth: 920
    implicitHeight: 700

    signal openCorCalibrationStudio()

    property string workingMachineName: (typeof settings !== "undefined" && settings) ? settings.machineName : "Galvo Studio"

    // [GalvoField] Working Values
    property real workingFieldSize: (typeof settings !== "undefined" && settings) ? settings.fieldSize : 70.0
    property real workingOffsetX: (typeof settings !== "undefined" && settings) ? settings.offsetX : 0.0
    property real workingOffsetY: (typeof settings !== "undefined" && settings) ? settings.offsetY : 0.0
    property real workingAngle: (typeof settings !== "undefined" && settings) ? settings.fieldAngle : 0.0



    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 20

            // ================= 1. MACHINE IDENTITY & NAMING CARD ================= //
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: identityCol.implicitHeight + 36
                radius: 10
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: identityCol
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            text: "tune"
                            font.family: "Material Icons"
                            font.pixelSize: 20
                            color: Theme.accentCyan
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                text: "MACHINE IDENTITY & NAMING ([machine])"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                                font.letterSpacing: 0.5
                            }
                            Text {
                                text: "Set the custom hardware station name displayed across headers, window titles, and logs."
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            radius: 6
                            color: Theme.bgInput
                            border.color: machineInput.activeFocus ? Theme.borderActive : Theme.borderInput
                            border.width: 1

                            TextInput {
                                id: machineInput
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                verticalAlignment: TextInput.AlignVCenter
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                                text: root.workingMachineName
                                onTextChanged: root.workingMachineName = text
                            }
                        }

                        ModernButton {
                            text: "💾 Save Machine Name"
                            primary: true
                            implicitHeight: 38
                            implicitWidth: 160
                            onClicked: {
                                if (typeof settings !== "undefined" && settings) {
                                    settings.saveMachineName(root.workingMachineName)
                                }
                            }
                        }
                    }
                }
            }

            // ================= 2. GALVO OPTICAL FIELD & LENS CALIBRATION (1ST IMAGE) ================= //
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: lensCol.implicitHeight + 40
                radius: 10
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: lensCol
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14

                    // Header Row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: "change_history"
                            font.family: "Material Icons"
                            font.pixelSize: 18
                            color: Theme.accentCyan
                        }

                        Text {
                            text: "GALVO OPTICAL FIELD & LENS CALIBRATION ([GalvoField])"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                            font.letterSpacing: 0.5
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: "Active Bed: " + root.workingFieldSize.toFixed(1) + " x " + root.workingFieldSize.toFixed(1) + " mm"
                            font.family: "Consolas, monospace"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.accentCyan
                        }
                    }

                    // Description text
                    Text {
                        Layout.fillWidth: true
                        text: "Configure the physical galvo scan head lens working area. This directly scales optical field boundaries, CAD ruler bounds, framing envelopes, and config.ini [GalvoField]."
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                    }

                    // Lens Presets Row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            text: "Lens Presets:"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }

                        Repeater {
                            model: [70, 100, 110, 150, 200]
                            Rectangle {
                                implicitWidth: 78
                                implicitHeight: 32
                                radius: 6
                                color: (Math.abs(root.workingFieldSize - modelData) < 0.1)
                                       ? Theme.accentCyan
                                       : (presetMa.containsMouse ? (Theme.isDark ? "#22355C" : "#E2E8F0") : (Theme.isDark ? "#17233D" : "#F1F5F9"))
                                border.color: (Math.abs(root.workingFieldSize - modelData) < 0.1)
                                              ? Theme.accentCyan
                                              : Theme.borderCard
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData + " mm"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 12
                                    font.weight: Font.Bold
                                    color: (Math.abs(root.workingFieldSize - modelData) < 0.1)
                                           ? "#000000"
                                           : Theme.textPrimary
                                }

                                MouseArea {
                                    id: presetMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        root.workingFieldSize = modelData
                                        fieldInput.text = modelData.toFixed(1)
                                    }
                                }
                            }
                        }
                    }

                    // Numeric Inputs & Apply Button
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 14
                        Layout.topMargin: 4

                        // Field Size (mm)
                        ColumnLayout {
                            spacing: 4
                            Text { text: "Field Size (mm)"; font.pixelSize: 11; color: Theme.textSecondary }
                            Rectangle {
                                width: 110; height: 36; radius: 5
                                color: Theme.bgInput
                                border.color: fieldInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: fieldInput
                                    anchors.fill: parent; anchors.margins: 6
                                    verticalAlignment: TextInput.AlignVCenter
                                    font.family: "Consolas, monospace"; font.pixelSize: 13; font.weight: Font.Bold
                                    color: Theme.textPrimary
                                    text: root.workingFieldSize.toFixed(1)
                                    onTextChanged: {
                                        var v = parseFloat(text)
                                        if (!isNaN(v) && v > 0) root.workingFieldSize = v
                                    }
                                }
                            }
                        }

                        // Offset X (mm)
                        ColumnLayout {
                            spacing: 4
                            Text { text: "Offset X (mm)"; font.pixelSize: 11; color: Theme.textSecondary }
                            Rectangle {
                                width: 110; height: 36; radius: 5
                                color: Theme.bgInput
                                border.color: offXInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: offXInput
                                    anchors.fill: parent; anchors.margins: 6
                                    verticalAlignment: TextInput.AlignVCenter
                                    font.family: "Consolas, monospace"; font.pixelSize: 13
                                    color: Theme.textPrimary
                                    text: root.workingOffsetX.toFixed(2)
                                    onTextChanged: {
                                        var v = parseFloat(text)
                                        if (!isNaN(v)) root.workingOffsetX = v
                                    }
                                }
                            }
                        }

                        // Offset Y (mm)
                        ColumnLayout {
                            spacing: 4
                            Text { text: "Offset Y (mm)"; font.pixelSize: 11; color: Theme.textSecondary }
                            Rectangle {
                                width: 110; height: 36; radius: 5
                                color: Theme.bgInput
                                border.color: offYInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: offYInput
                                    anchors.fill: parent; anchors.margins: 6
                                    verticalAlignment: TextInput.AlignVCenter
                                    font.family: "Consolas, monospace"; font.pixelSize: 13
                                    color: Theme.textPrimary
                                    text: root.workingOffsetY.toFixed(2)
                                    onTextChanged: {
                                        var v = parseFloat(text)
                                        if (!isNaN(v)) root.workingOffsetY = v
                                    }
                                }
                            }
                        }

                        // Rotation Angle (°)
                        ColumnLayout {
                            spacing: 4
                            Text { text: "Rotation Angle (°)"; font.pixelSize: 11; color: Theme.textSecondary }
                            Rectangle {
                                width: 110; height: 36; radius: 5
                                color: Theme.bgInput
                                border.color: angleInput.activeFocus ? Theme.borderActive : Theme.borderInput
                                border.width: 1
                                TextInput {
                                    id: angleInput
                                    anchors.fill: parent; anchors.margins: 6
                                    verticalAlignment: TextInput.AlignVCenter
                                    font.family: "Consolas, monospace"; font.pixelSize: 13
                                    color: Theme.textPrimary
                                    text: root.workingAngle.toFixed(1)
                                    onTextChanged: {
                                        var v = parseFloat(text)
                                        if (!isNaN(v)) root.workingAngle = v
                                    }
                                }
                            }
                        }

                        Item { Layout.fillWidth: true }

                        ModernButton {
                            Layout.alignment: Qt.AlignBottom
                            implicitHeight: 38
                            implicitWidth: 175
                            btnColor: Theme.isDark ? "#17233D" : "#FFFFFF"
                            textColor: Theme.textPrimary
                            borderColor: Theme.borderCard
                            text: "📐 Open .COR Studio"
                            onClicked: root.openCorCalibrationStudio()
                        }

                        // Apply & Save Button
                        ModernButton {
                            Layout.alignment: Qt.AlignBottom
                            implicitHeight: 38
                            implicitWidth: 150
                            primary: true
                            text: "💾 Apply & Save"
                            onClicked: {
                                if (typeof settings !== "undefined" && settings) {
                                    settings.saveLensFieldSettings(root.workingFieldSize, root.workingOffsetX, root.workingOffsetY, root.workingAngle)
                                }
                            }
                        }
                    }
                }
            }
            // ================= 3. COMPANY LOGO & ENTERPRISE INFO CARD ================= //
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: companyCol.implicitHeight + 36
                radius: 10
                color: Theme.bgCard
                border.color: Theme.borderCard
                border.width: 1

                ColumnLayout {
                    id: companyCol
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 16

                        // Company Logo Image
                        Rectangle {
                            width: 64
                            height: 64
                            radius: 8
                            color: "#FFFFFF"
                            border.color: Theme.accentAmber
                            border.width: 1.5
                            clip: true

                            Image {
                                anchors.fill: parent
                                anchors.margins: 4
                                source: (typeof appLogoUrl !== "undefined") ? appLogoUrl : ""
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Text {
                                text: "Spécialisé Products Private Limited"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }

                            Text {
                                text: "Precision Photonics · Laser Systems · Instrumentation"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 12
                                color: Theme.accentAmber
                            }

                            Text {
                                text: "Navi Mumbai, India  ·  info@specialiseproducts.com"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 11
                                color: Theme.textSecondary
                            }

                            // Clickable Website
                            RowLayout {
                                spacing: 6
                                Text { text: "language"; font.family: "Material Icons"; font.pixelSize: 14; color: Theme.accentCyan }
                                Text {
                                    text: "www.specialiseproducts.com"
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 11
                                    font.underline: webMa.containsMouse
                                    color: webMa.containsMouse ? Theme.accentCyan : Theme.accentBlue
                                    MouseArea {
                                        id: webMa
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: Qt.openUrlExternally("https://www.specialiseproducts.com")
                                    }
                                }
                            }
                        }
                    }

                    // Credentials Badges (ISO, Make in India, etc.)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Repeater {
                            model: ["ISO 9001:2015 Certified", "Make in India", "CE / EMC Verified", "MSME Udyam", "100% Python QML Architecture"]
                            Rectangle {
                                height: 22
                                implicitWidth: credLabel.implicitWidth + 14
                                radius: 4
                                color: Theme.isDark ? "#17233D" : "#E2E8F0"
                                border.color: Theme.isDark ? "#28344E" : "#CBD5E1"
                                border.width: 1

                                Text {
                                    id: credLabel
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                    color: Theme.isDark ? "#94A3B8" : "#1E293B"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
