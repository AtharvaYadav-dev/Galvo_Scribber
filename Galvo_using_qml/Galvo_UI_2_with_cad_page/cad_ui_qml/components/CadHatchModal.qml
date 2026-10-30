import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root

    property real lineDistance: 0.05
    property real hatchAngle: 45.0
    property bool crossHatch: true
    property real edgeOffset: 0.0
    property string hatchPattern: "cross"

    signal applyHatch(real distance, real angle, bool cross, real offset, string pattern)
    signal closed()

    function close() {
        root.visible = false
        root.closed()
    }

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.65)
    z: 100

    focus: visible
    Keys.onEscapePressed: root.close()

    // Click outside to close
    MouseArea {
        anchors.fill: parent
        onClicked: root.close()
    }

    // Modal Card
    Rectangle {
        id: modalContent
        anchors.centerIn: parent
        width: 440
        height: 480
        radius: 10
        color: CadTheme.bgCard
        border.color: CadTheme.borderActive
        border.width: 1.5

        // Prevent click-through
        MouseArea { anchors.fill: parent }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header
            RowLayout {
                Layout.fillWidth: true
                CadIcon {
                    name: "texture"
                    size: 22
                    iconColor: CadTheme.accentCyan
                }
                Text {
                    text: "Laser Hatching Studio"
                    font.family: "Inter"
                    font.pixelSize: 16
                    font.weight: Font.Bold
                    color: CadTheme.textPrimary
                }
                Item { Layout.fillWidth: true }
                CadButton {
                    iconName: "close"
                    variant: "ghost"
                    implicitWidth: 30
                    implicitHeight: 30
                    onClicked: root.close()
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: CadTheme.borderMuted }

            // Hatch Parameters
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 12

                // Line Distance
                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "Line Spacing (Pitch)"; font.family: "Inter"; font.pixelSize: 12; color: CadTheme.textPrimary }
                    Item { Layout.fillWidth: true }
                    CadInput {
                        id: distInput
                        unit: "mm"
                        text: root.lineDistance.toFixed(3)
                        onValueChanged: function(v) { root.lineDistance = v }
                    }
                }

                // Hatch Angle
                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "Hatch Angle"; font.family: "Inter"; font.pixelSize: 12; color: CadTheme.textPrimary }
                    Item { Layout.fillWidth: true }
                    CadInput {
                        id: angleInput
                        unit: "°"
                        text: root.hatchAngle.toFixed(1)
                        onValueChanged: function(v) { root.hatchAngle = v }
                    }
                }

                // Edge Offset
                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "Boundary Edge Offset"; font.family: "Inter"; font.pixelSize: 12; color: CadTheme.textPrimary }
                    Item { Layout.fillWidth: true }
                    CadInput {
                        id: offsetInput
                        unit: "mm"
                        text: root.edgeOffset.toFixed(2)
                        onValueChanged: function(v) { root.edgeOffset = v }
                    }
                }

                // Cross Hatch Checkbox
                RowLayout {
                    Layout.fillWidth: true
                    CheckBox {
                        id: crossCheck
                        text: "Enable 90° Cross-Hatch (Bi-directional)"
                        font.family: "Inter"
                        font.pixelSize: 12
                        checked: root.crossHatch
                        onCheckedChanged: root.crossHatch = checked
                    }
                }

                // Pattern Style Selector
                Text {
                    text: "HATCH PATTERN"
                    font.family: "Inter"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: CadTheme.textMuted
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    CadButton {
                        Layout.fillWidth: true
                        text: "Linear Parallel"
                        isActive: root.hatchPattern === "linear"
                        onClicked: root.hatchPattern = "linear"
                    }
                    CadButton {
                        Layout.fillWidth: true
                        text: "Cross-Grid"
                        isActive: root.hatchPattern === "cross"
                        onClicked: root.hatchPattern = "cross"
                    }
                    CadButton {
                        Layout.fillWidth: true
                        text: "Spiral Concentric"
                        isActive: root.hatchPattern === "spiral"
                        onClicked: root.hatchPattern = "spiral"
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // Footer Actions
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                CadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Generate Hatch"
                    variant: "accent"
                    onClicked: {
                        root.applyHatch(root.lineDistance, root.hatchAngle, root.crossHatch, root.edgeOffset, root.hatchPattern)
                        root.close()
                    }
                }
            }
        }
    }
}
