import QtQuick
import QtQuick.Controls

Button {
    id: control

    property string variant: "primary" // "primary", "secondary", "danger", "success", "accent", "ghost"
    property int customRadius: 8
    property var customColor: null

    property string iconName: ""
    property real iconSize: 16
    property var iconColor: null

    font.pixelSize: 13
    font.weight: Font.DemiBold
    font.family: "Segoe UI"

    implicitHeight: 40
    implicitWidth: Math.max(iconName.length > 0 && text.length === 0 ? 40 : 100, contentItem.implicitWidth + 24)

    // Palette mapping connected to global dynamic Theme
    readonly property var colors: {
        "primary":   { bg: Theme.btnPrimaryBg, hover: Theme.btnPrimaryHover, text: Theme.btnPrimaryText, border: Theme.btnPrimaryBorder },
        "accent":    { bg: Theme.accentAmber, hover: Qt.lighter(Theme.accentAmber, 1.1), text: "#0B1220", border: Theme.accentAmber },
        "secondary": { bg: Theme.btnSecondaryBg, hover: Theme.btnSecondaryHover, text: Theme.btnSecondaryText, border: Theme.btnSecondaryBorder },
        "success":   { bg: Theme.accentGreen, hover: Qt.lighter(Theme.accentGreen, 1.1), text: "#ffffff", border: Theme.accentGreen },
        "danger":    { bg: Theme.btnDangerBg, hover: Theme.btnDangerHover, text: Theme.btnDangerText, border: Theme.btnDangerBorder },
        "warning":   { bg: Theme.btnAmberBg, hover: Theme.btnAmberHover, text: Theme.btnAmberText, border: Theme.btnAmberBorder },
        "outline":   { bg: Theme.isDark ? Qt.rgba(37, 99, 235, 0.14) : "#EFF6FF", hover: Theme.isDark ? Qt.rgba(37, 99, 235, 0.28) : "#DBEAFE", text: Theme.isDark ? "#93C5FD" : "#1D4ED8", border: Theme.isDark ? "#3B82F6" : "#2563EB" },
        "ghost":     { bg: "transparent", hover: (Theme.isDark ? "#1E293B" : "#E9EDF9"), text: Theme.textSecondary, border: Theme.borderInput }
    }

    readonly property var currentScheme: colors[variant] || colors["primary"]

    background: Rectangle {
        implicitHeight: control.implicitHeight
        implicitWidth: control.implicitWidth
        radius: control.customRadius
        color: control.customColor !== null ? control.customColor : (control.down ? Qt.darker(control.currentScheme.bg, 1.2) : (control.hovered ? control.currentScheme.hover : control.currentScheme.bg))
        border.color: control.hovered ? Qt.lighter(control.currentScheme.border, 1.25) : control.currentScheme.border
        border.width: (control.variant === "outline" || control.variant === "primary") ? 1.5 : 1

        Behavior on color {
            ColorAnimation { duration: 150 }
        }

        Behavior on border.color {
            ColorAnimation { duration: 150 }
        }

        scale: control.down ? 0.96 : (control.hovered ? 1.02 : 1.0)
        Behavior on scale {
            NumberAnimation { duration: 120; easing.type: Easing.OutBack }
        }
    }

    contentItem: Item {
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        Row {
            id: contentRow
            anchors.centerIn: parent
            spacing: 8

            Text {
                visible: control.iconName.length > 0
                text: control.iconName
                font.family: "Material Icons"
                font.pixelSize: control.iconSize
                color: (control.iconColor !== null && control.iconColor !== undefined) ? control.iconColor : control.currentScheme.text
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                visible: control.text.length > 0
                text: control.text
                font: control.font
                color: control.currentScheme.text
                anchors.verticalCenter: parent.verticalCenter
                elide: Text.ElideRight
            }
        }
    }
}
