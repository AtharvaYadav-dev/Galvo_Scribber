import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

RadioButton {
    id: control

    implicitHeight: 28
    implicitWidth: indicator.width + spacing + (contentItem.text.length > 0 ? (contentItem.contentWidth + 6) : 0) + leftPadding + rightPadding
    spacing: 6
    leftPadding: 4
    rightPadding: 4

    font.family: "Segoe UI, Inter, sans-serif"
    font.pixelSize: 11
    font.weight: Font.DemiBold

    indicator: Rectangle {
        implicitWidth: 16
        implicitHeight: 16
        x: control.leftPadding
        y: control.topPadding + Math.round((control.availableHeight - height) / 2)
        radius: 8
        color: control.checked ? (Theme.isDark ? "#162E54" : "#DBEAFE") : Theme.bgInput
        border.color: control.checked ? Theme.accentCyan : (control.hovered ? Theme.accentCyan : Theme.borderInput)
        border.width: 1

        Behavior on color { ColorAnimation { duration: 100 } }
        Behavior on border.color { ColorAnimation { duration: 100 } }

        Rectangle {
            anchors.centerIn: parent
            width: 8
            height: 8
            radius: 4
            color: Theme.accentCyan
            visible: control.checked
        }
    }

    contentItem: Text {
        text: control.text
        font: control.font
        color: control.checked ? Theme.accentCyan : (control.hovered ? Theme.textPrimary : Theme.textSecondary)
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}
