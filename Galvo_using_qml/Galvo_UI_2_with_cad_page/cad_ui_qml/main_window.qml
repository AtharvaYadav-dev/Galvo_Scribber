import QtQuick
import QtQuick.Window
import QtQuick.Controls

ApplicationWindow {
    id: window
    width: 1400
    height: 880
    minimumWidth: 1024
    minimumHeight: 650
    visible: true
    title: "CAD Studio — Next-Gen Galvo Laser Workstation (Dark & Light Mode)"
    color: CadTheme.bgApp

    function toggleTheme() {
        CadTheme.toggleTheme()
    }

    CadPage {
        anchors.fill: parent
    }
}
