import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root

    property string currentTool: "select" // "select", "node", "line", "curve", "rect", "circle", "polygon", "text", "barcode"
    signal toolSelected(string toolId)
    signal barcodeTriggered()
    signal textTriggered()
    signal importTriggered()
    signal deleteTriggered()

    width: 54
    color: CadTheme.bgToolbox
    border.color: CadTheme.borderCard
    border.width: 1

    readonly property var tools: [
        { id: "select", icon: "near_me", name: "Select / Pick (V)" },
        { id: "node", icon: "timeline", name: "Node / Vertex Edit" },
        { id: "divider1", isDivider: true },
        { id: "line", icon: "horizontal_rule", name: "Draw Line" },
        { id: "curve", icon: "gesture", name: "Freehand / Curve Spline" },
        { id: "rect", icon: "crop_square", name: "Draw Rectangle" },
        { id: "circle", icon: "radio_button_unchecked", name: "Draw Circle / Oval" },
        { id: "polygon", icon: "pentagon", name: "Draw Polygon" },
        { id: "divider2", isDivider: true },
        { id: "text", icon: "text_fields", name: "Laser Text & Font Tool" },
        { id: "barcode", icon: "qr_code_2", name: "QR Code & Barcode Tool" },
        { id: "import", icon: "file_upload", name: "Import DXF / Vector" },
        { id: "divider3", isDivider: true },
        { id: "delete", icon: "delete_outline", name: "Delete Selection" }
    ]

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 12
        anchors.bottomMargin: 12
        spacing: 4

        Repeater {
            model: root.tools

            delegate: Item {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 40
                Layout.preferredHeight: modelData.isDivider ? 10 : 38

                // Divider rendering
                Rectangle {
                    visible: modelData.isDivider === true
                    anchors.centerIn: parent
                    width: 24
                    height: 1
                    color: CadTheme.borderMuted
                }

                // Tool button rendering
                Rectangle {
                    id: btnBg
                    visible: !modelData.isDivider
                    anchors.fill: parent
                    radius: 7
                    color: root.currentTool === modelData.id
                        ? (CadTheme.isDark ? "#172E54" : "#E2E8F0")
                        : (toolMa.containsMouse ? (CadTheme.isDark ? "#16223B" : "#F1F5F9") : "transparent")
                    border.color: root.currentTool === modelData.id ? CadTheme.accentCyan : "transparent"
                    border.width: root.currentTool === modelData.id ? 1.5 : 0

                    scale: toolMa.pressed ? 0.92 : (toolMa.containsMouse ? 1.06 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutBack } }
                    Behavior on color { ColorAnimation { duration: 120 } }
                    Behavior on border.color { ColorAnimation { duration: 120 } }

                    CadIcon {
                        anchors.centerIn: parent
                        name: modelData.icon || ""
                        size: 20
                        iconColor: root.currentTool === modelData.id
                            ? CadTheme.accentCyan
                            : (modelData.id === "delete" && toolMa.containsMouse ? CadTheme.accentRed : CadTheme.textPrimary)
                    }

                    MouseArea {
                        id: toolMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (modelData.id === "barcode") {
                                root.barcodeTriggered()
                            } else if (modelData.id === "text") {
                                root.textTriggered()
                            } else if (modelData.id === "import") {
                                root.importTriggered()
                            } else if (modelData.id === "delete") {
                                root.deleteTriggered()
                            } else {
                                root.currentTool = modelData.id
                                root.toolSelected(modelData.id)
                            }
                        }

                        ToolTip.visible: containsMouse
                        ToolTip.text: modelData.name || ""
                        ToolTip.delay: 350
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
