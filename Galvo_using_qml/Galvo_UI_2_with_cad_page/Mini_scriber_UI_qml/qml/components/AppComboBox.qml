import QtQuick
import QtQuick.Controls

ComboBox {
    id: control

    font.family: "Segoe UI"
    font.pixelSize: 12
    font.weight: Font.DemiBold

    implicitHeight: 38
    implicitWidth: 160

    delegate: ItemDelegate {
        width: control.width
        contentItem: Text {
            text: control.textRole ? (Array.isArray(control.model) ? modelData[control.textRole] : model[control.textRole]) : modelData
            color: control.highlightedIndex === index ? Theme.accentAmber : Theme.textPrimary
            font: control.font
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            color: control.highlightedIndex === index ? (Theme.isDark ? "#1E293B" : "#E9EDF9") : (Theme.isDark ? "#111827" : "#FFFFFF")
        }
        highlighted: control.highlightedIndex === index
    }

    indicator: Text {
        x: control.width - width - 8
        y: (control.height - height) / 2
        text: "▾"
        font.pixelSize: 11
        color: control.down ? Theme.accentAmber : Theme.textSecondary
    }

    contentItem: Text {
        leftPadding: 10
        rightPadding: 22
        text: control.displayText
        font: control.font
        color: Theme.textPrimary
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: control.implicitWidth
        implicitHeight: control.implicitHeight
        color: Theme.bgInput
        border.color: control.activeFocus ? Theme.borderInputFocus : Theme.borderInput
        border.width: 1
        radius: 6
    }

    popup: Popup {
        y: control.height + 4
        width: control.width
        implicitHeight: Math.min(220, contentItem.implicitHeight)
        padding: 4
        modal: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside | Popup.CloseOnPressOutsideParent
        dim: false

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator { }
        }

        background: Rectangle {
            color: Theme.bgCard
            border.color: Theme.borderCard
            border.width: 1
            radius: 6

            MouseArea {
                anchors.fill: parent
                z: -1
                acceptedButtons: Qt.AllButtons
                cursorShape: Qt.ArrowCursor
                onClicked: {}
                onWheel: function(wheel) {
                    wheel.accepted = true
                }
            }
        }
    }
}
