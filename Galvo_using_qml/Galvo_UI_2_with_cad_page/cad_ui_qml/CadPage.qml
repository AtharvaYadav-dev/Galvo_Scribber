import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "components"

Rectangle {
    id: pageRoot

    color: CadTheme.bgApp

    // File Dialog for DXF / SVG
    FileDialog {
        id: importFileDialog
        title: "Import Vector CAD File (DXF / SVG)"
        nameFilters: ["Vector Files (*.dxf *.svg)", "DXF Files (*.dxf)", "SVG Files (*.svg)", "All Files (*)"]
        onAccepted: {
            console.log("User selected vector file: " + selectedFile)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 1. Top Unified Command Ribbon
        CadTopCommandBar {
            Layout.fillWidth: true
            onOpenFileDialogTriggered: importFileDialog.open()
            onHatchTriggered: hatchModal.visible = true
            onZoomInTriggered: cadCanvas.zoomIn()
            onZoomOutTriggered: cadCanvas.zoomOut()
            onZoomFitTriggered: cadCanvas.zoomFit()
            onCenterToBedTriggered: cadCanvas.centerSelectedShape()
            onUndoTriggered: console.log("Undo triggered")
            onRedoTriggered: console.log("Redo triggered")
            onGroupTriggered: console.log("Group triggered")
            onUngroupTriggered: console.log("Ungroup triggered")
        }

        // 2. Middle Central CAD Studio (Toolbox + Rulers + Canvas + Inspector)
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Left Vertical Toolbox
            CadToolbox {
                id: toolbox
                Layout.fillHeight: true
                onBarcodeTriggered: barcodeModal.visible = true
                onTextTriggered: {
                    var newText = {
                        id: cadCanvas.shapes.length + 1,
                        name: "Text_Item_" + (cadCanvas.shapes.length + 1),
                        type: "text",
                        text: "CUSTOM TEXT",
                        xMm: 0,
                        yMm: 0,
                        wMm: 40,
                        hMm: 8,
                        rotation: 0,
                        penId: inspector.selectedPenId,
                        hatched: true,
                        visible: true,
                        locked: false
                    }
                    cadCanvas.shapes.push(newText)
                    cadCanvas.shapesChanged()
                    cadCanvas.selectedIndex = cadCanvas.shapes.length - 1
                }
                onImportTriggered: importFileDialog.open()
                onDeleteTriggered: cadCanvas.deleteSelectedShape()
                onToolSelected: function(toolId) {
                    if (toolId === "rect") {
                        var newRect = {
                            id: cadCanvas.shapes.length + 1,
                            name: "Rect_" + (cadCanvas.shapes.length + 1),
                            type: "rect",
                            xMm: 0,
                            yMm: 0,
                            wMm: 30,
                            hMm: 20,
                            rotation: 0,
                            penId: inspector.selectedPenId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        cadCanvas.shapes.push(newRect)
                        cadCanvas.shapesChanged()
                        cadCanvas.selectedIndex = cadCanvas.shapes.length - 1
                    } else if (toolId === "circle") {
                        var newCirc = {
                            id: cadCanvas.shapes.length + 1,
                            name: "Circle_" + (cadCanvas.shapes.length + 1),
                            type: "circle",
                            xMm: 0,
                            yMm: 0,
                            wMm: 25,
                            hMm: 25,
                            rotation: 0,
                            penId: inspector.selectedPenId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        cadCanvas.shapes.push(newCirc)
                        cadCanvas.shapesChanged()
                        cadCanvas.selectedIndex = cadCanvas.shapes.length - 1
                    }
                }
            }

            // Central Viewport Area (Rulers + Interactive Canvas)
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                // Horizontal Top Ruler
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 22
                    Layout.maximumHeight: 22
                    spacing: 0

                    // Corner Origin Spacer (Intersection of top & left rulers)
                    Rectangle {
                        Layout.preferredWidth: 24
                        Layout.preferredHeight: 22
                        color: CadTheme.bgRuler
                        border.color: CadTheme.borderMuted
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "0"
                            font.family: "IBM Plex Mono"
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: CadTheme.accentCyan
                        }
                    }

                    CadRuler {
                        id: topRuler
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        isVertical: false
                        originPos: cadCanvas.originX
                        zoomScale: cadCanvas.zoomScale
                        mouseCoordMm: cadCanvas.mouseCoordMmX
                    }
                }

                // Left Ruler + Canvas Viewport
                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 0

                    CadRuler {
                        id: leftRuler
                        Layout.preferredWidth: 24
                        Layout.fillHeight: true
                        isVertical: true
                        originPos: cadCanvas.originY
                        zoomScale: cadCanvas.zoomScale
                        mouseCoordMm: cadCanvas.mouseCoordMmY
                    }

                    // Main Vector Canvas
                    CadCanvas {
                        id: cadCanvas
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        onShapeSelected: function(shp) {
                            inspector.selectedShape = shp
                        }
                        onShapeModified: function(shp) {
                            inspector.selectedShape = shp
                        }
                    }
                }
            }

            // Right Inspector Panel
            CadInspectorPanel {
                id: inspector
                Layout.fillHeight: true
                selectedShape: (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length)
                    ? cadCanvas.shapes[cadCanvas.selectedIndex]
                    : null

                onShapeModified: function(shp) {
                    cadCanvas.shapesChanged()
                }
                onPenChanged: function(pId) {
                    if (selectedShape) {
                        selectedShape.penId = pId
                        cadCanvas.shapesChanged()
                    }
                }
            }
        }

        // 3. Bottom Industrial Launch Deck
        CadBottomLaunchDeck {
            Layout.fillWidth: true
            mouseCoordX: cadCanvas.mouseCoordMmX
            mouseCoordY: cadCanvas.mouseCoordMmY
            zoomPercent: (cadCanvas.zoomScale / 2.5) * 100.0
            onRedPointerToggled: function(active) {
                console.log("Red light pointer framing toggled: " + active)
            }
            onMarkTriggered: {
                console.log("Laser marking cycle executed!")
            }
            onResetCounter: {
                partCount = 0
            }
        }
    }

    // Modal Overlays
    CadHatchModal {
        id: hatchModal
        visible: false
        onApplyHatch: function(dist, angle, cross, offset, pattern) {
            console.log("Applied hatch: dist=" + dist + ", angle=" + angle + ", cross=" + cross)
            if (inspector.selectedShape) {
                inspector.selectedShape.hatched = true
                cadCanvas.shapesChanged()
            }
        }
    }

    CadBarcodeModal {
        id: barcodeModal
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc) {
            var newCode = {
                id: cadCanvas.shapes.length + 1,
                name: "Barcode_" + (cadCanvas.shapes.length + 1),
                type: "qrcode",
                text: content,
                xMm: 0,
                yMm: 0,
                wMm: sizeMm,
                hMm: sizeMm,
                rotation: 0,
                penId: inspector.selectedPenId,
                hatched: true,
                visible: true,
                locked: false
            }
            cadCanvas.shapes.push(newCode)
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = cadCanvas.shapes.length - 1
        }
    }
}
