import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import ".."

Rectangle {
    id: root

    property alias themeToggleEnabled: themeBtn.visible
    signal openFileDialogTriggered()
    signal undoTriggered()
    signal redoTriggered()
    signal groupTriggered()
    signal ungroupTriggered()
    signal centerToBedTriggered()
    signal hatchTriggered()
    signal zoomFitTriggered()
    signal zoomInTriggered()
    signal zoomOutTriggered()

    height: 52
    color: CadTheme.bgHeader
    border.color: CadTheme.borderCard
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 12

        // Brand & Mode Badge
        RowLayout {
            spacing: 8
            Rectangle {
                width: 28
                height: 28
                radius: 6
                color: CadTheme.isDark ? "#172542" : "#E2E8F0"
                border.color: CadTheme.accentCyan
                border.width: 1

                CadIcon {
                    anchors.centerIn: parent
                    name: "auto_fix_high"
                    size: 16
                    iconColor: CadTheme.accentCyan
                }
            }

            ColumnLayout {
                spacing: 1
                Text {
                    text: "CAD STUDIO"
                    font.family: "Inter"
                    font.pixelSize: 13
                    font.weight: Font.Bold
                    color: CadTheme.textPrimary
                }
                Text {
                    text: "Galvo Vector & Hatching Editor"
                    font.family: "Inter"
                    font.pixelSize: 9
                    color: CadTheme.textMuted
                }
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // File Actions Group
        RowLayout {
            spacing: 6
            CadButton {
                iconName: "note_add"
                text: "New"
                tooltipText: "Create new canvas project (Ctrl+N)"
            }

            CadButton {
                iconName: "folder_open"
                text: "Import Vector"
                variant: "outline"
                tooltipText: "Import DXF or SVG vector artwork"
                onClicked: root.openFileDialogTriggered()
            }

            CadButton {
                iconName: "save"
                text: "Save"
                tooltipText: "Save workspace project"
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // History Actions
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "undo"
                tooltipText: "Undo last edit (Ctrl+Z)"
                onClicked: root.undoTriggered()
            }
            CadButton {
                iconName: "redo"
                tooltipText: "Redo last edit (Ctrl+Y)"
                onClicked: root.redoTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // Alignment & Arrangement Tools
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: "Center selection to Galvo Optical Origin (0,0)"
                onClicked: root.centerToBedTriggered()
            }
            CadButton {
                iconName: "align_horizontal_left"
                tooltipText: "Align Left edges"
            }
            CadButton {
                iconName: "align_horizontal_center"
                tooltipText: "Align Horizontal Centers"
            }
            CadButton {
                iconName: "align_horizontal_right"
                tooltipText: "Align Right edges"
            }
            CadButton {
                iconName: "align_vertical_top"
                tooltipText: "Align Top edges"
            }
            CadButton {
                iconName: "align_vertical_center"
                tooltipText: "Align Vertical Centers"
            }
            CadButton {
                iconName: "group_work"
                tooltipText: "Group selected objects"
                onClicked: root.groupTriggered()
            }
            CadButton {
                iconName: "layers_clear"
                tooltipText: "Ungroup selection"
                onClicked: root.ungroupTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // Hatch Tool Trigger
        CadButton {
            iconName: "texture"
            text: "Hatch (H)"
            variant: "accent"
            tooltipText: "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)"
            onClicked: root.hatchTriggered()
        }

        // Divider
        Rectangle { width: 1; height: 26; color: CadTheme.borderMuted }

        // Viewport & Zoom Controls
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "zoom_in"
                tooltipText: "Zoom In (+)"
                onClicked: root.zoomInTriggered()
            }
            CadButton {
                iconName: "zoom_out"
                tooltipText: "Zoom Out (-)"
                onClicked: root.zoomOutTriggered()
            }
            CadButton {
                iconName: "fit_screen"
                text: "Fit Field"
                tooltipText: "Fit Galvo Field to screen"
                onClicked: root.zoomFitTriggered()
            }
        }

        Item { Layout.fillWidth: true }

        // Optional Light / Dark Theme Switcher (for standalone mode only)
        CadButton {
            id: themeBtn
            visible: false
            iconName: CadTheme.isDark ? "dark_mode" : "light_mode"
            text: CadTheme.isDark ? "DARK" : "LIGHT"
            variant: "secondary"
            tooltipText: "Toggle between Dark and Light mode"
            onClicked: CadTheme.toggleTheme()
        }
    }
}
