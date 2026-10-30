import QtQuick
import QtQuick.Controls
import "../qml/components/cad"

Rectangle {
    width: 840
    height: 700
    color: "#080C16"

    CadHatchModal {
        id: modal
        anchors.fill: parent
        visible: true
        Component.onCompleted: {
            openModal(null)
        }
    }
}
