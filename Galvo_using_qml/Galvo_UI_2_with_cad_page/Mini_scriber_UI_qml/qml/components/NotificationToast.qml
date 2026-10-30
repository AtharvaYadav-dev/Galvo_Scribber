import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    width: 330
    implicitHeight: toastCol.implicitHeight + 20
    radius: 10
    color: Theme.isDark ? "#0D1527" : "#FFFFFF"
    border.color: {
        if (currentLevel === "error") return "#EF4444"
        if (currentLevel === "warning") return "#F59E0B"
        if (currentLevel === "success") return "#10B981"
        return "#00E5FF"
    }
    border.width: 1.5
    clip: true

    property string currentTitle: ""
    property string currentMessage: ""
    property string currentLevel: "info"
    property string currentTargetView: ""
    property int currentNotifId: 0
    property var notifBridge: (typeof notifications !== "undefined") ? notifications : null

    signal requestNavigate(string targetView)

    // Fade and scale animations
    opacity: 0.0
    scale: 0.88
    visible: opacity > 0.0

    function pop(notif) {
        if (!notif) return
        currentNotifId = notif.id || 0
        currentTitle = notif.title || ""
        currentMessage = notif.message || ""
        currentLevel = notif.level || "info"
        currentTargetView = notif.target_view || ""
        toastTimer.restart()
        showAnim.restart()
    }

    function dismissToast() {
        toastTimer.stop()
        hideAnim.restart()
    }

    Timer {
        id: toastTimer
        interval: 4500
        repeat: false
        onTriggered: hideAnim.restart()
    }

    ParallelAnimation {
        id: showAnim
        NumberAnimation { target: root; property: "opacity"; to: 1.0; duration: 220; easing.type: Easing.OutQuad }
        NumberAnimation { target: root; property: "scale"; to: 1.0; duration: 220; easing.type: Easing.OutBack }
    }

    ParallelAnimation {
        id: hideAnim
        NumberAnimation { target: root; property: "opacity"; to: 0.0; duration: 200; easing.type: Easing.InQuad }
        NumberAnimation { target: root; property: "scale"; to: 0.88; duration: 200; easing.type: Easing.InQuad }
    }

    ColumnLayout {
        id: toastCol
        anchors.fill: parent
        anchors.margins: 12
        spacing: 5

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            AppIcon {
                name: {
                    if (root.currentLevel === "error") return "error"
                    if (root.currentLevel === "warning") return "warning"
                    if (root.currentLevel === "success") return "check_circle"
                    return "info"
                }
                size: 16
                iconColor: {
                    if (root.currentLevel === "error") return "#EF4444"
                    if (root.currentLevel === "warning") return Theme.accentAmber
                    if (root.currentLevel === "success") return Theme.accentGreen
                    return Theme.accentCyan
                }
            }

            Text {
                text: root.currentTitle
                font.family: "Inter"
                font.pixelSize: 11
                font.weight: Font.Bold
                color: {
                    if (root.currentLevel === "error") return "#EF4444"
                    if (root.currentLevel === "warning") return Theme.accentAmber
                    return Theme.textPrimary
                }
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            Rectangle {
                width: 20
                height: 20
                radius: 10
                color: toastCloseMa.containsMouse ? (Theme.isDark ? "#243650" : "#E2E8F0") : "transparent"

                AppIcon {
                    anchors.centerIn: parent
                    name: "close"
                    size: 12
                    iconColor: Theme.textSecondary
                }

                MouseArea {
                    id: toastCloseMa
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.dismissToast()
                }
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.currentMessage
            font.family: "Inter"
            font.pixelSize: 10
            color: Theme.textSecondary
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }

        RowLayout {
            Layout.fillWidth: true
            visible: root.currentTargetView.length > 0
            spacing: 6

            Item { Layout.fillWidth: true }

            Text {
                text: "View →"
                font.family: "Inter"
                font.pixelSize: 10
                font.weight: Font.Bold
                color: Theme.accentCyan

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        var nid = root.currentNotifId
                        var target = root.currentTargetView
                        var nb = root.notifBridge || (typeof notifications !== "undefined" ? notifications : null)
                        if (nb) {
                            if (nid > 0) nb.markAsRead(nid)
                            if (target.length > 0) nb.navigateTo(target)
                        }
                        root.dismissToast()
                    }
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        z: -1
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            var nid = root.currentNotifId
            var target = root.currentTargetView
            var nb = root.notifBridge || (typeof notifications !== "undefined" ? notifications : null)
            if (nb) {
                if (nid > 0) nb.markAsRead(nid)
                if (target.length > 0) nb.navigateTo(target)
            }
            root.dismissToast()
        }
    }
}
