import QtQuick
import QtQuick.Controls
import ".."

Button {
    id: control

    property string variant: "secondary" // "primary", "secondary", "accent", "danger", "ghost", "red_pointer", "mark"
    property int customRadius: 6
    property string iconName: ""
    property real iconSize: 16
    property var iconColor: null
    property string tooltipText: ""
    property bool isActive: false

    font.pixelSize: 12
    font.weight: Font.DemiBold
    font.family: "Segoe UI"

    implicitHeight: 34
    implicitWidth: Math.max(iconName.length > 0 && text.length === 0 ? 34 : 72, contentRow.implicitWidth + 20)

    ToolTip.visible: tooltipText.length > 0 && hovered
    ToolTip.text: tooltipText
    ToolTip.delay: 400

    readonly property var colors: {
        "primary": {
            bg: CadTheme.btnPrimaryBg,
            hover: CadTheme.btnPrimaryHover,
            text: CadTheme.btnPrimaryText,
            border: CadTheme.btnPrimaryBg
        },
        "secondary": {
            bg: isActive ? (CadTheme.isDark ? "#22355C" : "#E2E8F0") : CadTheme.btnSecondaryBg,
            hover: CadTheme.btnSecondaryHover,
            text: isActive ? (CadTheme.isDark ? "#00E5FF" : "#192D78") : CadTheme.btnSecondaryText,
            border: isActive ? (CadTheme.isDark ? "#00E5FF" : "#192D78") : CadTheme.btnSecondaryBorder
        },
        "accent": {
            bg: CadTheme.accentCyan,
            hover: Qt.lighter(CadTheme.accentCyan, 1.1),
            text: "#0A0F1D",
            border: CadTheme.accentCyan
        },
        "ghost": {
            bg: isActive ? (CadTheme.isDark ? "#1E293B" : "#E2E8F0") : "transparent",
            hover: (CadTheme.isDark ? "#16223B" : "#EDF2F7"),
            text: isActive ? CadTheme.accentCyan : CadTheme.textSecondary,
            border: isActive ? CadTheme.accentCyan : "transparent"
        },
        "danger": {
            bg: CadTheme.accentRed,
            hover: Qt.darker(CadTheme.accentRed, 1.15),
            text: "#FFFFFF",
            border: CadTheme.accentRed
        },
        "red_pointer": {
            bg: isActive ? CadTheme.accentAmber : CadTheme.btnRedPointerBg,
            hover: CadTheme.btnRedPointerHover,
            text: isActive ? "#000000" : CadTheme.btnRedPointerText,
            border: CadTheme.btnRedPointerBorder
        },
        "mark": {
            bg: isActive ? CadTheme.accentGreen : CadTheme.btnMarkBg,
            hover: CadTheme.btnMarkHover,
            text: isActive ? "#FFFFFF" : CadTheme.btnMarkText,
            border: CadTheme.btnMarkBorder
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
