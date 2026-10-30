import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root

    property string label: "Slider"
    property real from: 0.0
    property real to: 100.0
    property real stepSize: 1.0
    property real value: 0.0
    property string unit: ""
    property color activeColor: Theme.accentAmber

    signal valueModified(real newVal)

    spacing: 6

    RowLayout {
        Layout.fillWidth: true

        Text {
            text: root.label
            font.family: "Segoe UI"
            font.pixelSize: 12
            font.weight: Font.DemiBold
            color: Theme.textSecondary
        }

        Item { Layout.fillWidth: true }

        Text {
            text: (root.stepSize < 1 ? root.value.toFixed(1) : Math.round(root.value)) + (root.unit ? " " + root.unit : "")
            font.family: "Consolas"
            font.pixelSize: 13
            font.weight: Font.Bold
            color: Theme.textPrimary
        }
    }

    Slider {
        id: slider
        Layout.fillWidth: true
        from: root.from
        to: root.to
        stepSize: root.stepSize
        value: root.value

        onMoved: {
            root.value = slider.value
            root.valueModified(slider.value)
        }

        background: Rectangle {
            x: slider.leftPadding
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            implicitWidth: 200
            implicitHeight: 6
            width: slider.availableWidth
            height: implicitHeight
            radius: 3
            color: Theme.isDark ? "#1E293B" : "#DCE2EC"

            Rectangle {
                width: slider.visualPosition * parent.width
                height: parent.height
                color: root.activeColor
                radius: 3
            }
        }

        handle: Rectangle {
            x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            implicitWidth: 16
            implicitHeight: 16
            radius: 8
            color: root.activeColor
            border.color: Theme.isDark ? "#0B1220" : "#FFFFFF"
            border.width: 2

            scale: slider.hovered ? 1.15 : 1.0
            Behavior on scale { NumberAnimation { duration: 80 } }
        }
    }
}
