import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../.."

Rectangle {
    id: root

    property alias themeToggleEnabled: themeBtn.visible
    property bool hasSelection: false
    property bool isSelectionLocked: false
    property bool canUndo: false
    property bool canRedo: false
    property bool isSelectionGroup: false
    property int totalShapesCount: 0

    signal openFileDialogTriggered()
    signal undoTriggered()
    signal redoTriggered()
    signal groupTriggered()
    signal ungroupTriggered()
    signal centerToBedTriggered()
    signal fitToFieldTriggered()
    signal alignTriggered(string mode)
    signal hatchTriggered()
    signal unhatchTriggered()
    property bool isSelectionHatched: false
    signal zoomFitTriggered()
    signal zoomInTriggered()
    signal zoomOutTriggered()

    height: 52
    color: Theme.bgHeader
    border.color: Theme.borderCard
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 12

        // File Actions Group
        RowLayout {
            spacing: 6

            CadButton {
                iconName: "folder_open"
                text: "Import Vector"
                variant: "outline"
                tooltipText: "Import DXF or SVG vector artwork"
                onClicked: root.openFileDialogTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: Theme.borderMuted }

        // History Actions
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "undo"
                tooltipText: "Undo last edit (Ctrl+Z)"
                enabled: root.canUndo
                onClicked: root.undoTriggered()
            }
            CadButton {
                iconName: "redo"
                tooltipText: "Redo last edit (Ctrl+Y)"
                enabled: root.canRedo
                onClicked: root.redoTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: Theme.borderMuted }

        // Alignment & Arrangement Tools (Accessible only when an object is selected)
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "filter_center_focus"
                tooltipText: !root.hasSelection ? "Center to Origin (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Center selection to Galvo Optical Origin (0,0)")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.centerToBedTriggered()
            }
            CadButton {
                iconName: "fit_screen"
                tooltipText: !root.hasSelection ? "Fit to Field (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Auto-fit & scale selection to optical bed")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.fitToFieldTriggered()
            }
            CadButton {
                iconName: "align_horizontal_left"
                tooltipText: !root.hasSelection ? "Align Left (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Align Left edge to field boundary")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.alignTriggered("left")
            }
            CadButton {
                iconName: "align_horizontal_center"
                tooltipText: !root.hasSelection ? "Align H-Center (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Align Horizontal Center (X = 0)")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.alignTriggered("center_h")
            }
            CadButton {
                iconName: "align_horizontal_right"
                tooltipText: !root.hasSelection ? "Align Right (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Align Right edge to field boundary")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.alignTriggered("right")
            }
            CadButton {
                iconName: "align_vertical_top"
                tooltipText: !root.hasSelection ? "Align Top (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Align Top edge to field boundary")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.alignTriggered("top")
            }
            CadButton {
                iconName: "align_vertical_center"
                tooltipText: !root.hasSelection ? "Align V-Center (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Align Vertical Center (Y = 0)")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.alignTriggered("center_v")
            }
            CadButton {
                iconName: "group_work"
                tooltipText: (root.totalShapesCount < 2) ? "Group (Requires 2+ objects on canvas)" : "Group all objects into unified group (Ctrl+G)"
                enabled: root.totalShapesCount >= 2 && !root.isSelectionLocked
                onClicked: root.groupTriggered()
            }
            CadButton {
                iconName: "layers_clear"
                tooltipText: !root.isSelectionGroup ? "Ungroup (Select a group entity first)" : "Ungroup selected group into individual objects (Ctrl+Shift+G)"
                enabled: root.isSelectionGroup && !root.isSelectionLocked
                onClicked: root.ungroupTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: Theme.borderMuted }

        // Hatch & Unhatch Tools (Accessible only when an object is selected)
        RowLayout {
            spacing: 4
            CadButton {
                iconName: "texture"
                text: "Hatch (H)"
                variant: (root.hasSelection && root.isSelectionHatched) ? "outline" : "accent"
                tooltipText: !root.hasSelection ? "Laser Hatching (Select an object first)" : (root.isSelectionLocked ? "Object is locked" : "Open Laser Hatching Studio (Lines, Crosshatch, Spiral)")
                enabled: root.hasSelection && !root.isSelectionLocked
                onClicked: root.hatchTriggered()
            }

            CadButton {
                visible: root.hasSelection && root.isSelectionHatched
                iconName: "layers_clear"
                text: "Unhatch"
                variant: "secondary"
                tooltipText: "Remove hatch infill from selected object (Shift+H)"
                enabled: !root.isSelectionLocked
                onClicked: root.unhatchTriggered()
            }
        }

        // Divider
        Rectangle { width: 1; height: 26; color: Theme.borderMuted }

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
            iconName: Theme.isDark ? "dark_mode" : "light_mode"
            text: Theme.isDark ? "DARK" : "LIGHT"
            variant: "secondary"
            tooltipText: "Toggle between Dark and Light mode"
            onClicked: Theme.toggleTheme()
        }
    }
}
