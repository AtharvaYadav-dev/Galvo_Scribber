import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: root

    property real currentStep: 5.0
    property var stepValues: [10.0, 5.0, 1.0, 0.1]
    signal stepSelected(real step)

    Repeater {
        model: root.stepValues

        Rectangle {
            id: chip
            required property real modelData

            Layout.preferredWidth: 64
            Layout.preferredHeight: 36
            radius: 6

            readonly property bool isSelected: Math.abs(root.currentStep - modelData) < 0.001

            color: isSelected ? "#00b4d8" : (chipMouse.containsMouse ? "#262e3f" : "#1b202c")
            border.color: isSelected ? "#00d2ff" : "#323c52"
            border.width: isSelected ? 1.5 : 1

            Behavior on color { ColorAnimation { duration: 100 } }

            Text {
                anchors.centerIn: parent
                text: chip.modelData >= 1 ? chip.modelData.toFixed(0) + " mm" : chip.modelData.toFixed(1) + " mm"
                color: chip.isSelected ? "#0c0e14" : "#ffffff"
                font.pixelSize: 11
                font.weight: chip.isSelected ? Font.Bold : Font.Medium
            }

            MouseArea {
                id: chipMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    root.currentStep = chip.modelData
                    root.stepSelected(chip.modelData)
                }
            }
        }
    }
}
