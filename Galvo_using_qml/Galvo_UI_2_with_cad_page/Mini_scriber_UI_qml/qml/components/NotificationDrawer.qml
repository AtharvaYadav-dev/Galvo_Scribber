import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: drawerRoot
    width: 410
    height: 520
    radius: 14
    color: Theme.isDark ? "#0A101E" : "#FFFFFF"
    border.color: Theme.isDark ? "#1E2E48" : "#CBD5E1"
    border.width: 1.5
    clip: true

    scale: visible ? 1.0 : 0.90
    opacity: visible ? 1.0 : 0.0
    Behavior on scale {
        NumberAnimation { duration: 220; easing.type: Easing.OutBack }
    }
    Behavior on opacity {
        NumberAnimation { duration: 160; easing.type: Easing.OutQuad }
    }

    signal requestNavigate(string targetView)

    // Current filter tab: "all", "unread", "alarms"
    property string activeFilter: "all"
    property var notifBridge: (typeof notifications !== "undefined") ? notifications : null

    // Ambient drop shadow simulation
    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        radius: parent.radius + 1
        color: "transparent"
        border.color: Theme.isDark ? Qt.rgba(0, 229, 255, 0.18) : Qt.rgba(0, 0, 0, 0.10)
        border.width: 1
        z: -1
    }

    // Prevent background clicks and wheel scrolls on drawer body from dismissing or leaking to backside UI
    MouseArea {
        anchors.fill: parent
        z: -1
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onClicked: {}
        onWheel: function(wheel) {
            // Completely absorb wheel events on drawer margins/header/filters
            wheel.accepted = true
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Top Header Bar
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            spacing: 8

            // Bell icon + title + counter
            RowLayout {
                Layout.alignment: Qt.AlignVCenter
                spacing: 8

                Rectangle {
                    width: 30
                    height: 30
                    radius: 15
                    color: Theme.isDark ? "#142036" : "#EFF6FF"
                    border.color: Theme.isDark ? "#1E3050" : "#DBEAFE"
                    border.width: 1

                    AppIcon {
                        anchors.centerIn: parent
                        name: "notifications"
                        size: 16
                        iconColor: Theme.accentCyan
                    }
                }

                Text {
                    text: "Notifications"
                    font.family: "Inter"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    color: Theme.textPrimary
                    Layout.alignment: Qt.AlignVCenter
                }

                // Unread Count Badge
                Rectangle {
                    visible: drawerRoot.notifBridge ? drawerRoot.notifBridge.unreadCount > 0 : false
                    Layout.alignment: Qt.AlignVCenter
                    height: 20
                    radius: 10
                    color: "#D97706"
                    implicitWidth: unreadBadgeText.implicitWidth + 14

                    Text {
                        id: unreadBadgeText
                        anchors.centerIn: parent
                        text: ((drawerRoot.notifBridge && drawerRoot.notifBridge.unreadCount) || 0) + " new"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: "#FFFFFF"
                    }
                }
            }

            Item { Layout.fillWidth: true }

            // Right Actions Group
            RowLayout {
                Layout.alignment: Qt.AlignVCenter
                spacing: 6

                // Mark All Read Button
                Rectangle {
                    visible: drawerRoot.notifBridge ? drawerRoot.notifBridge.unreadCount > 0 : false
                    height: 28
                    radius: 14
                    color: markMa.containsMouse ? (Theme.isDark ? "#1E2D48" : "#E2E8F0") : (Theme.isDark ? "#111B2C" : "#F1F5F9")
                    border.color: Theme.isDark ? "#243650" : "#CBD5E1"
                    border.width: 1
                    implicitWidth: markRow.implicitWidth + 16

                    RowLayout {
                        id: markRow
                        anchors.centerIn: parent
                        spacing: 5
                        AppIcon {
                            name: "done_all"
                            size: 14
                            iconColor: Theme.accentCyan
                        }
                        Text {
                            text: "Mark read"
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                            color: Theme.textPrimary
                        }
                    }

                    MouseArea {
                        id: markMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (drawerRoot.notifBridge) drawerRoot.notifBridge.markAllAsRead()
                        }
                    }
                }

                // Clear All Button
                Rectangle {
                    visible: drawerRoot.notifBridge ? drawerRoot.notifBridge.list.length > 0 : false
                    height: 28
                    radius: 14
                    color: clearMa.containsMouse ? (Theme.isDark ? "#1E2D48" : "#E2E8F0") : (Theme.isDark ? "#111B2C" : "#F1F5F9")
                    border.color: Theme.isDark ? "#243650" : "#CBD5E1"
                    border.width: 1
                    implicitWidth: clearText.implicitWidth + 16

                    Text {
                        id: clearText
                        anchors.centerIn: parent
                        text: "Clear"
                        font.family: "Inter"
                        font.pixelSize: 10
                        font.weight: Font.DemiBold
                        color: Theme.textSecondary
                    }

                    MouseArea {
                        id: clearMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (drawerRoot.notifBridge) drawerRoot.notifBridge.clearAll()
                        }
                    }
                }

                // Close Circle Button
                Rectangle {
                    width: 28
                    height: 28
                    radius: 14
                    color: closeMa.containsMouse ? (Theme.isDark ? "#243650" : "#E2E8F0") : (Theme.isDark ? "#111B2C" : "#F1F5F9")
                    border.color: Theme.isDark ? "#243650" : "#CBD5E1"
                    border.width: 1

                    AppIcon {
                        anchors.centerIn: parent
                        name: "close"
                        size: 14
                        iconColor: Theme.textPrimary
                    }

                    MouseArea {
                        id: closeMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: drawerRoot.visible = false
                    }
                }
            }
        }

        // Header Divider Line
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: Theme.isDark ? "#1A263B" : "#E2E8F0"
        }

        // Filter Bar (Segmented Control)
        Rectangle {
            Layout.fillWidth: true
            height: 32
            radius: 8
            color: Theme.isDark ? "#060A14" : "#F1F5F9"
            border.color: Theme.isDark ? "#1A263B" : "#E2E8F0"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                spacing: 2

                Repeater {
                    model: [
                        { id: "all", label: "All (" + (drawerRoot.notifBridge ? drawerRoot.notifBridge.list.length : 0) + ")" },
                        { id: "unread", label: "Unread (" + (drawerRoot.notifBridge ? drawerRoot.notifBridge.unreadCount : 0) + ")" },
                        { id: "alarms", label: "Alarms & Warnings" }
                    ]

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 6
                        color: drawerRoot.activeFilter === modelData.id
                            ? (Theme.isDark ? "#1E2E48" : "#FFFFFF")
                            : (tabMa.containsMouse ? (Theme.isDark ? "#121C2D" : "#E2E8F0") : "transparent")
                        border.color: drawerRoot.activeFilter === modelData.id
                            ? (Theme.isDark ? "#2F4468" : "#CBD5E1")
                            : "transparent"
                        border.width: drawerRoot.activeFilter === modelData.id ? 1 : 0

                        Text {
                            anchors.centerIn: parent
                            text: modelData.label
                            font.family: "Inter"
                            font.pixelSize: 10
                            font.weight: drawerRoot.activeFilter === modelData.id ? Font.Bold : Font.Normal
                            color: drawerRoot.activeFilter === modelData.id ? Theme.textPrimary : Theme.textSecondary
                        }

                        MouseArea {
                            id: tabMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: drawerRoot.activeFilter = modelData.id
                        }
                    }
                }
            }
        }

        // Notification Cards List
        ListView {
            id: notifList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 8
            boundsBehavior: Flickable.StopAtBounds

            model: {
                var nb = drawerRoot.notifBridge
                var raw = nb ? nb.list : []
                if (drawerRoot.activeFilter === "unread") {
                    return raw.filter(function(n) { return !n.read })
                } else if (drawerRoot.activeFilter === "alarms") {
                    return raw.filter(function(n) { return n.level === "error" || n.level === "warning" })
                }
                return raw
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }

            // Empty state display
            Item {
                anchors.fill: parent
                visible: notifList.count === 0

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 8

                    AppIcon {
                        name: "auto_awesome"
                        size: 32
                        iconColor: Theme.accentAmber
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: drawerRoot.activeFilter === "unread" ? "No unread notifications" : "All clear · No notifications"
                        font.family: "Inter"
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                        color: Theme.textPrimary
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text {
                        text: "Machine operations and safety status are nominal."
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: Theme.textSecondary
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            delegate: Rectangle {
                id: card
                property var notifBridge: drawerRoot.notifBridge
                width: notifList.width
                implicitHeight: cardCol.implicitHeight + 18
                radius: 8

                // Visual background: Highlighted if unread
                color: modelData.read
                    ? (Theme.isDark ? "#0F172A" : "#F8FAFC")
                    : (Theme.isDark ? "#142036" : "#EFF6FF")

                border.color: modelData.read
                    ? (Theme.isDark ? "#1E293B" : "#E2E8F0")
                    : (Theme.isDark ? Qt.rgba(0, 229, 255, 0.45) : Qt.rgba(2, 132, 199, 0.4))
                border.width: 1

                // Left Severity Color Strip
                Rectangle {
                    width: 3.5
                    height: parent.height - 12
                    radius: 2
                    anchors.left: parent.left
                    anchors.leftMargin: 4
                    anchors.verticalCenter: parent.verticalCenter
                    color: {
                        if (modelData.level === "error") return "#EF4444"
                        if (modelData.level === "warning") return "#F59E0B"
                        if (modelData.level === "success") return "#10B981"
                        return "#00E5FF"
                    }
                }

                ColumnLayout {
                    id: cardCol
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 10
                    anchors.topMargin: 8
                    anchors.bottomMargin: 8
                    spacing: 4

                    // Header row: Icon, Title, Time, Unread Dot, Dismiss
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        // Level Icon
                        AppIcon {
                            name: {
                                if (modelData.level === "error") return "error"
                                if (modelData.level === "warning") return "warning"
                                if (modelData.level === "success") return "check_circle"
                                return "info"
                            }
                            size: 15
                            iconColor: {
                                if (modelData.level === "error") return "#EF4444"
                                if (modelData.level === "warning") return Theme.accentAmber
                                if (modelData.level === "success") return Theme.accentGreen
                                return Theme.accentCyan
                            }
                        }

                        // Title
                        Text {
                            text: modelData.title
                            font.family: "Inter"
                            font.pixelSize: 11
                            font.weight: modelData.read ? Font.DemiBold : Font.Bold
                            color: {
                                if (modelData.level === "error") return "#EF4444"
                                if (modelData.level === "warning") return Theme.accentAmber
                                return Theme.textPrimary
                            }
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        // Time Ago
                        Text {
                            text: modelData.time_ago || modelData.time || ""
                            font.family: "Inter"
                            font.pixelSize: 9
                            color: Theme.textSecondary
                        }

                        // Unread Dot
                        Rectangle {
                            visible: !modelData.read
                            width: 6
                            height: 6
                            radius: 3
                            color: Theme.accentCyan
                        }

                        // Single Dismiss 'X' Button
                        Rectangle {
                            width: 20
                            height: 20
                            radius: 10
                            color: cardDismissMa.containsMouse ? (Theme.isDark ? "#334155" : "#CBD5E1") : "transparent"

                            Text {
                                anchors.centerIn: parent
                                text: "×"
                                font.pixelSize: 12
                                color: Theme.textSecondary
                            }

                            MouseArea {
                                id: cardDismissMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    var item = modelData
                                    var nb = card.notifBridge || drawerRoot.notifBridge
                                    if (nb && item && item.id) {
                                        nb.dismiss(item.id)
                                    }
                                }
                            }
                        }
                    }

                    // Message Body
                    Text {
                        Layout.fillWidth: true
                        text: modelData.message
                        font.family: "Inter"
                        font.pixelSize: 10
                        color: modelData.read ? Theme.textSecondary : Theme.textPrimary
                        wrapMode: Text.WordWrap
                        lineHeight: 1.25
                    }

                    // Bottom Row: Action Deep Link (if target_view is specified)
                    RowLayout {
                        Layout.fillWidth: true
                        visible: modelData.target_view && modelData.target_view.length > 0
                        spacing: 4

                        Item { Layout.fillWidth: true }

                        Rectangle {
                            height: 22
                            radius: 4
                            color: actMa.containsMouse ? (Theme.isDark ? "#1E2E48" : "#DBEAFE") : "transparent"
                            border.color: Theme.accentCyan
                            border.width: 1
                            implicitWidth: actText.implicitWidth + 14

                            Text {
                                id: actText
                                anchors.centerIn: parent
                                text: {
                                    var tv = modelData.target_view || ""
                                    if (tv === "motion") return "Open Motion DRO →"
                                    if (tv === "job") return "Open Job View →"
                                    if (tv === "laser") return "Open Laser Control →"
                                    if (tv === "camera") return "Open Camera →"
                                    if (tv === "hardware") return "Open Machine Setup →"
                                    if (tv === "settings") return "Open Settings →"
                                    if (tv === "terminal") return "Open Terminal →"
                                    return "Go to Screen →"
                                }
                                font.family: "Inter"
                                font.pixelSize: 9
                                font.weight: Font.DemiBold
                                color: Theme.accentCyan
                            }

                            MouseArea {
                                id: actMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    var item = modelData
                                    if (!item) return
                                    var nid = item.id
                                    var tv = item.target_view || ""
                                    var nb = card.notifBridge || drawerRoot.notifBridge
                                    if (nb) {
                                        if (!item.read) {
                                            nb.markAsRead(nid)
                                        }
                                        if (tv.length > 0) {
                                            nb.navigateTo(tv)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Click card body to mark as read
                MouseArea {
                    anchors.fill: parent
                    z: -1
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        var item = modelData
                        if (!item) return
                        var nid = item.id
                        var tv = item.target_view || ""
                        var nb = card.notifBridge || drawerRoot.notifBridge
                        if (nb) {
                            if (!item.read) {
                                nb.markAsRead(nid)
                            }
                            if (tv.length > 0) {
                                nb.navigateTo(tv)
                            }
                        }
                    }
                }
            }
        }
    }
}
