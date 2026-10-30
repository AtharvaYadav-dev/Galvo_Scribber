import QtQuick
import QtQuick.Controls
import "../.."

Button {
    id: control

    property string variant: "secondary" // "primary", "secondary", "accent", "danger", "ghost", "red_pointer", "mark", "outline"
    property int customRadius: 6
    property string iconName: ""
    property real iconSize: 16
    property var iconColor: null
    property string tooltipText: ""
    property bool isActive: false

    font.pixelSize: 12
    font.weight: Font.DemiBold
    font.family: "Segoe UI, Inter, sans-serif"

    implicitHeight: 34
    implicitWidth: Math.max(iconName.length > 0 && text.length === 0 ? 34 : 72, contentRow.implicitWidth + 20)
    opacity: control.enabled ? 1.0 : 0.40

    ToolTip.visible: tooltipText.length > 0 && hovered
    ToolTip.text: tooltipText
    ToolTip.delay: 350

    readonly property var colors: {
        "primary": {
            bg: Theme.btnPrimaryBg,
            hover: Theme.btnPrimaryHover,
            text: Theme.btnPrimaryText,
            border: Theme.btnPrimaryBg
        },
        "secondary": {
            bg: isActive ? (Theme.isDark ? "#22355C" : "#E2E8F0") : Theme.btnSecondaryBg,
            hover: Theme.btnSecondaryHover,
            text: isActive ? (Theme.isDark ? "#00E5FF" : "#192D78") : Theme.btnSecondaryText,
            border: isActive ? (Theme.isDark ? "#00E5FF" : "#192D78") : Theme.btnSecondaryBorder
        },
        "accent": {
            bg: Theme.accentCyan,
            hover: Qt.lighter(Theme.accentCyan, 1.1),
            text: "#0A0F1D",
            border: Theme.accentCyan
        },
        "ghost": {
            bg: isActive ? (Theme.isDark ? "#1E293B" : "#E2E8F0") : "transparent",
            hover: (Theme.isDark ? "#16223B" : "#EDF2F7"),
            text: isActive ? Theme.accentCyan : Theme.textSecondary,
            border: isActive ? Theme.accentCyan : "transparent"
        },
        "outline": {
            bg: isActive ? (Theme.isDark ? "#16223B" : "#EFF6FF") : "transparent",
            hover: Theme.isDark ? "#1C2A48" : "#E0E7FF",
            text: Theme.isDark ? "#38BDF8" : "#1D4ED8",
            border: Theme.isDark ? "#38BDF8" : "#2563EB"
        },
        "danger": {
            bg: Theme.accentRed,
            hover: Qt.darker(Theme.accentRed, 1.15),
            text: "#FFFFFF",
            border: Theme.accentRed
        },
        "red_pointer": {
            bg: isActive ? Theme.accentAmber : Theme.btnRedPointerBg,
            hover: Theme.btnRedPointerHover,
            text: isActive ? "#000000" : Theme.btnRedPointerText,
            border: Theme.btnRedPointerBorder
        },
        "mark": {
            bg: isActive ? Theme.accentGreen : Theme.btnMarkBg,
            hover: Theme.btnMarkHover,
            text: isActive ? "#FFFFFF" : Theme.btnMarkText,
            border: Theme.btnMarkBorder
        }
    }

    readonly property var currentScheme: colors[variant] || colors["secondary"]

    background: Rectangle {
        implicitHeight: control.implicitHeight
        implicitWidth: control.implicitWidth
        radius: control.customRadius
        color: control.down ? Qt.darker(control.currentScheme.bg, 1.15) : (control.hovered ? control.currentScheme.hover : control.currentScheme.bg)
        border.color: control.currentScheme.border
        border.width: (control.variant === "ghost" && !control.isActive) ? 0 : 1

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }

        scale: control.down ? 0.96 : (control.hovered ? 1.02 : 1.0)
        Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutBack } }
    }

    contentItem: Item {
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        Row {
            id: contentRow
            anchors.centerIn: parent
            spacing: 6

            CadIcon {
                visible: control.iconName.length > 0
                name: control.iconName
                size: control.iconSize
                iconColor: control.iconColor !== null ? control.iconColor : control.currentScheme.text
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
