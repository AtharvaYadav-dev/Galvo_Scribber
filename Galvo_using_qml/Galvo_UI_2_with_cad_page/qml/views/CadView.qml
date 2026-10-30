import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components/cad"
import ".."

Item {
    id: pageRoot

    function createDefaultText() {
        toolbox.textTriggered()
    }

    // File Dialog for DXF / SVG import directly connected to cad bridge
    // File Dialog for DXF / SVG / Gerber / Raster import directly connected to cad bridge
    FileDialog {
        id: importFileDialog
        title: "Import CAD / Vector / Gerber / Image File"
        nameFilters: [
            "All Supported Files (*.dxf *.svg *.gbr *.gtl *.gbl *.gto *.gbo *.gts *.gbs *.gml *.gtp *.gbp *.drl *.txt *.png *.jpg *.jpeg *.bmp)",
            "DXF Vector Files (*.dxf)",
            "SVG Vector Files (*.svg)",
            "Gerber PCB Files (*.gbr *.gtl *.gbl *.gto *.gbo *.gts *.gbs *.gml *.gtp *.gbp *.drl *.txt)",
            "Raster Images (*.png *.jpg *.jpeg *.bmp)",
            "All Files (*)"
        ]
        onAccepted: {
            if (typeof cad !== "undefined" && cad) {
                cad.importFile(selectedFile.toString())
            }
        }
    }

    // Connect to Python CadBridge to receive imported DXF/SVG shapes
    Connections {
        target: (typeof cad !== "undefined") ? cad : null
        function onShapesImported(newShapes) {
            if (!newShapes || newShapes.length === 0) return
            cadCanvas.pushUndoState()
            var updated = cadCanvas.shapes.slice()
            for (var i = 0; i < newShapes.length; i++) {
                updated.push(newShapes[i])
            }
            cadCanvas.shapes = updated
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = updated.length - 1
            if (updated.length > 0) {
                cadCanvas.shapeSelected(updated[updated.length - 1])
            }
            cadCanvas.zoomFit()
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(cadCanvas.shapes)
            }
        }
    }

    // Keyboard shortcut / external trigger functions
    function triggerRedPointer() {
        if (typeof cad !== "undefined" && cad) {
            cad.toggleFraming(cadCanvas.shapes, bottomLaunchDeck.markSelectedOnly, cadCanvas.selectedIndex)
        }
    }

    function triggerMark() {
        if (bottomLaunchDeck.isMarking) {
            triggerAbort()
        } else {
            if (typeof cad !== "undefined" && cad) {
                cad.executeMark(cadCanvas.shapes, bottomLaunchDeck.markSelectedOnly, cadCanvas.selectedIndex, bottomLaunchDeck.continuousMode ? 999999 : 1)
            }
        }
    }

    function triggerPause() {
        if (typeof cad !== "undefined" && cad) {
            cad.togglePause()
        }
    }

    function triggerAbort() {
        if (typeof cad !== "undefined" && cad) {
            cad.abortMark()
        }
    }

    Shortcut {
        sequence: "Shift+H"
        onActivated: {
            if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                cadCanvas.unhatchSelectedShape()
            }
        }
    }

    Shortcut {
        sequence: "H"
        onActivated: {
            if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                hatchModal.openModal(inspector.selectedShape)
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.bgApp

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // 1. Top Unified Command Ribbon
            CadTopCommandBar {
                id: topCommandBar
                objectName: "topCommandBar"
                Layout.fillWidth: true
                hasSelection: cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length
                isSelectionLocked: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].locked)
                canUndo: cadCanvas.canUndo
                canRedo: cadCanvas.canRedo
                isSelectionGroup: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].type === "group")
                totalShapesCount: cadCanvas.shapes.length

                onOpenFileDialogTriggered: importFileDialog.open()
                onHatchTriggered: {
                    if (cadCanvas.selectedIndex >= 0) {
                        hatchModal.openModal(inspector.selectedShape)
                    }
                }
                onAlignTriggered: function(mode) {
                    cadCanvas.alignSelectedShape(mode)
                }
                onZoomInTriggered: cadCanvas.zoomIn()
                onZoomOutTriggered: cadCanvas.zoomOut()
                onZoomFitTriggered: cadCanvas.zoomFit()
                onCenterToBedTriggered: cadCanvas.centerSelectedShape()
                onFitToFieldTriggered: cadCanvas.fitSelectionToField()
                onUndoTriggered: cadCanvas.undo()
                onRedoTriggered: cadCanvas.redo()
                onGroupTriggered: cadCanvas.groupSelectedShapes()
                onUngroupTriggered: cadCanvas.ungroupSelectedShape()
                isSelectionHatched: hasSelection && Boolean(cadCanvas.shapes[cadCanvas.selectedIndex] && cadCanvas.shapes[cadCanvas.selectedIndex].hatched)
                onUnhatchTriggered: cadCanvas.unhatchSelectedShape()
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
                        cadCanvas.pushUndoState()
                        var defaultText = "TEXT"
                        var defaultFamily = "Segoe UI"
                        var defaultHeight = 4.0
                        var calculatedW = 12.15
                        if (typeof cad !== "undefined" && cad) {
                            var m = cad.measureText(defaultText, defaultFamily, defaultHeight, false, false)
                            if (m && m.wMm > 0) {
                                calculatedW = m.wMm
                            }
                        }
                        var newText = {
                            id: cadCanvas.shapes.length + 1,
                            name: "Text_" + (cadCanvas.shapes.length + 1),
                            type: "text",
                            text: defaultText,
                            xMm: 0,
                            yMm: 0,
                            wMm: calculatedW,
                            hMm: defaultHeight,
                            rotation: 0,
                            fontFamily: defaultFamily,
                            fontType: "TrueType Font",
                            textAlign: "center",
                            charSpace: 0.0,
                            lineSpace: 0.0,
                            bold: false,
                            italic: false,
                            penId: inspector.selectedPenId,
                            hatched: false,
                            visible: true,
                            locked: false
                        }
                        var updatedT = cadCanvas.shapes.slice()
                        updatedT.push(newText)
                        cadCanvas.shapes = updatedT
                        cadCanvas.shapesChanged()
                        cadCanvas.selectedIndex = updatedT.length - 1
                        cadCanvas.shapeSelected(newText)
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(updatedT)
                        }
                        cadCanvas.requestPaint()
                    }
                    onImportTriggered: importFileDialog.open()
                    onDeleteTriggered: cadCanvas.deleteSelectedShape()
                    onToolSelected: function(toolId) {
                        cadCanvas.activeTool = toolId
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
                        Layout.preferredHeight: 26
                        Layout.maximumHeight: 26
                        spacing: 0

                        // Corner Origin Spacer (Intersection of top & left rulers)
                        Rectangle {
                            Layout.preferredWidth: 32
                            Layout.preferredHeight: 26
                            color: Theme.bgRuler
                            border.color: Theme.borderMuted
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: "0"
                                font.family: "Consolas, monospace"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: Theme.accentCyan
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
                            Layout.preferredWidth: 32
                            Layout.fillHeight: true
                            isVertical: true
                            originPos: cadCanvas.originY
                            zoomScale: cadCanvas.zoomScale
                            mouseCoordMm: cadCanvas.mouseCoordMmY
                        }

                        // Main Vector Canvas
                        CadCanvas {
                            id: cadCanvas
                            objectName: "cadCanvas"
                            interactionBlocked: root.isAnyModalActive
                            currentPenId: inspector.selectedPenId
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            onHatchTriggered: function(shp) {
                                hatchModal.openModal(shp)
                            }
                            onShapeSelected: function(shp) {
                                inspector.selectedIndex = cadCanvas.selectedIndex
                                inspector.updateTransformInputs()
                            }
                            onShapeModified: function(shp) {
                                inspector.updateTransformInputs()
                                if (typeof cad !== "undefined" && cad) {
                                    cad.updateShapes(cadCanvas.shapes)
                                }
                            }
                            onToolFinished: {
                                toolbox.currentTool = "select"
                            }
                        }
                    }
                }

                // Right Inspector Panel
                CadInspectorPanel {
                    id: inspector
                    objectName: "inspector"
                    Layout.fillHeight: true
                    shapesModel: cadCanvas.shapes
                    selectedIndex: cadCanvas.selectedIndex
                    onShapeSelected: function(idx) {
                        cadCanvas.selectedIndex = idx
                    }
                    onShapeDeleted: function(idx) {
                        cadCanvas.selectedIndex = idx
                        cadCanvas.deleteSelectedShape()
                    }
                    onShapeVisibilityToggled: function(idx) {
                        cadCanvas.toggleShapeVisibility(idx)
                    }
                    onShapeLockToggled: function(idx) {
                        cadCanvas.toggleShapeLock(idx)
                    }
                    onShapeRenamed: function(idx, newName) {
                        cadCanvas.renameShape(idx, newName)
                    }
                    onShapeModified: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                            if (shp.hatched && typeof cad !== "undefined" && cad) {
                                shp.hatch_lines = cad.computeHatchPreviewLines(shp)
                            }
                        }
                        if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length && shp) {
                            var copy = cadCanvas.shapes.slice()
                            copy[cadCanvas.selectedIndex] = shp
                            cadCanvas.shapes = copy
                        }
                        cadCanvas.shapesChanged()
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.requestPaint()
                    }
                    onHatchTriggered: function(shp) {
                        hatchModal.openModal(shp)
                    }
                    onUnhatchTriggered: function(shp) {
                        cadCanvas.unhatchSelectedShape()
                    }
                    onFontDialogTriggered: function(shp) {
                        textFontModal.openModal(shp)
                    }
                    onArrayDialogTriggered: function(shp) {
                        arrayModal.openModal(shp)
                    }
                    onInputPortDialogTriggered: function(shp) {
                        inputPortModal.openModal(shp)
                    }
                    onVariableTextDialogTriggered: function(shp) {
                        variableTextModal.openModal(shp)
                    }
                    onApplyTriggered: function(shp) {
                        if (shp) {
                            shp.hatch_lines = []
                        }
                        if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length && shp) {
                            var copy2 = cadCanvas.shapes.slice()
                            copy2[cadCanvas.selectedIndex] = shp
                            cadCanvas.shapes = copy2
                        }
                        if (typeof cad !== "undefined" && cad) {
                            cad.updateShapes(cadCanvas.shapes)
                        }
                        cadCanvas.shapesChanged()
                        cadCanvas.requestPaint()
                    }
                    onPenChanged: function(pId) {
                        if (inspector.selectedShape && cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                            var target = inspector.selectedShape
                            target.penId = pId
                            if (target.hatch_profiles) {
                                for (var hk in target.hatch_profiles) {
                                    target.hatch_profiles[hk].pen_no = pId
                                }
                            }
                            target.hatch_lines = []
                            var copy = cadCanvas.shapes.slice()
                            copy[cadCanvas.selectedIndex] = target
                            cadCanvas.shapes = copy
                            cadCanvas.shapesChanged()
                            if (typeof cad !== "undefined" && cad) {
                                cad.updateShapes(cadCanvas.shapes)
                            }
                            cadCanvas.requestPaint()
                        }
                    }
                    onOpenColorPickerRequested: function(penId, color, name) {
                        colorPickerModal.openModal(penId, color, name)
                    }
                }
            }

            // 3. Bottom Industrial Launch Deck
            CadBottomLaunchDeck {
                id: bottomLaunchDeck
                Layout.fillWidth: true
                mouseCoordX: cadCanvas.mouseCoordMmX
                mouseCoordY: cadCanvas.mouseCoordMmY
                zoomPercent: (cadCanvas.zoomScale / 2.5) * 100.0
                onRedPointerToggled: function(active) {
                    if (typeof cad !== "undefined" && cad) {
                        cad.toggleFraming(cadCanvas.shapes, markSelectedOnly, cadCanvas.selectedIndex)
                    }
                }
                onMarkTriggered: {
                    if (typeof cad !== "undefined" && cad) {
                        cad.executeMark(cadCanvas.shapes, markSelectedOnly, cadCanvas.selectedIndex, continuousMode ? 999999 : 1)
                    }
                }
                onAbortTriggered: {
                    if (typeof cad !== "undefined" && cad) {
                        cad.abortMark()
                    }
                }
                onResetCounter: {
                    partCount = 0
                }
            }
        }
    }

    // Modal Overlays
    CadHatchModal {
        id: hatchModal
        visible: false
        onApplyHatch: function(profs, markContour, markContourFirst) {
            var target = inspector.selectedShape
            if (target) {
                target.hatched = true
                target.mark_contour = markContour
                target.mark_contour_first = markContourFirst
                target.hatch_profiles = JSON.parse(JSON.stringify(profs))
                if (typeof cad !== "undefined" && cad) {
                    target.hatch_lines = cad.computeHatchPreviewLines(target)
                }
                if (cadCanvas.selectedIndex >= 0 && cadCanvas.selectedIndex < cadCanvas.shapes.length) {
                    var copyH = cadCanvas.shapes.slice()
                    copyH[cadCanvas.selectedIndex] = target
                    cadCanvas.shapes = copyH
                }
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
            }
        }
        onUndoHatch: function() {
            cadCanvas.unhatchSelectedShape()
        }
    }

    CadBarcodeModal {
        id: barcodeModal
        objectName: "barcodeModal"
        visible: false
        onGenerateBarcode: function(type, content, sizeMm, autoInc, outputFormat) {
            cadCanvas.pushUndoState()
            var mode = outputFormat || "dxf"
            var entityData = null
            if (typeof cad !== "undefined" && cad) {
                entityData = cad.generateBarcodeEntity(type, content, sizeMm)
            }
            var bType = (type === "Code 128" ? "barcode128" : (type === "DataMatrix" ? "datamatrix" : "qrcode"))
            var shapeType = (mode === "dxf" ? "dxf" : (mode === "svg" ? "svg" : bType))
            var prefix = (mode === "dxf" ? "DXF_" : (mode === "svg" ? "SVG_" : "")) + (type === "Code 128" ? "Barcode128_" : (type === "DataMatrix" ? "DataMatrix_" : "QRCode_"))
            var w = sizeMm
            var h = sizeMm
            if (type === "Code 128") {
                h = (entityData && entityData.hMm) ? entityData.hMm : sizeMm * 0.4
            }
            if (entityData && entityData.wMm) w = entityData.wMm
            if (entityData && entityData.hMm) h = entityData.hMm

            var newCode = {
                id: cadCanvas.shapes.length + 1,
                name: prefix + (cadCanvas.shapes.length + 1),
                type: shapeType, // "dxf" / "svg" (vector CAD) or optical barcode type
                isBarcode: true,
                barcodeType: bType,
                outputFormat: mode,
                text: content,
                xMm: 0,
                yMm: 0,
                wMm: Math.round(w * 10) / 10,
                hMm: Math.round(h * 10) / 10,
                rotation: 0,
                penId: inspector.selectedPenId,
                hatched: false,
                mark_contour: true,
                visible: true,
                locked: false,
                rects: (entityData && entityData.rects) ? entityData.rects : [],
                paths: (entityData && entityData.paths) ? entityData.paths : []
            }
            var copy = cadCanvas.shapes.slice()
            copy.push(newCode)
            cadCanvas.shapes = copy
            cadCanvas.shapesChanged()
            cadCanvas.selectedIndex = copy.length - 1
            cadCanvas.shapeSelected(newCode)
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(copy)
            }
            cadCanvas.requestPaint()
            barcodeModal.close()
        }
    }

    // EZCad Font & CircleText Configuration Modal
    CadTextFontModal {
        id: textFontModal
        objectName: "textFontModal"
        onSettingsApplied: function(props) {
            var target = inspector.selectedShape
            if (target) {
                for (var key in props) {
                    target[key] = props[key]
                }
                if (typeof cad !== "undefined" && cad) {
                    var m = cad.measureText(
                        target.text || "TEXT",
                        target.fontFamily || "Segoe UI",
                        target.hMm || 4.0,
                        Boolean(target.bold),
                        Boolean(target.italic)
                    )
                    if (m && m.wMm > 0) target.wMm = m.wMm
                    if (target.hatched) {
                        target.hatch_lines = cad.computeHatchPreviewLines(target)
                    }
                    cad.updateShapes(cadCanvas.shapes)
                }
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
            }
        }
    }

    // EZCad Array Replication Modal
    CadArrayModal {
        id: arrayModal
        onArrayConfirmed: function(countX, countY, incXMm, incYMm) {
            var target = inspector.selectedShape
            if (target && typeof cad !== "undefined" && cad) {
                var clones = cad.applyArray(target, countX, countY, incXMm, incYMm)
                if (clones && clones.length > 0) {
                    var list = cadCanvas.shapes.slice()
                    for (var i = 0; i < clones.length; i++) {
                        list.push(clones[i])
                    }
                    cadCanvas.shapes = list
                    cadCanvas.shapesChanged()
                    cad.updateShapes(cadCanvas.shapes)
                    cadCanvas.requestPaint()
                }
            }
        }
    }

    // EZCad Input Port Conditional Execution Modal
    CadInputPortModal {
        id: inputPortModal
        onPortConditionsConfirmed: function(bits) {
            var target = inspector.selectedShape
            if (target) {
                target.inputPortBits = bits.slice()
                cadCanvas.shapesChanged()
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
            }
        }
    }

    // EZCad Advance Variable Text Modal
    CadVariableTextModal {
        id: variableTextModal
        onVariableSettingsConfirmed: function(enabled, entitiesList, fixedWidth, fixedWidthVal) {
            var target = inspector.selectedShape
            if (target) {
                target.enableVariableText = enabled
                target.variableEntities = JSON.parse(JSON.stringify(entitiesList))
                target.enableFixedWidth = fixedWidth
                target.fixedWidthMm = fixedWidthVal
                cadCanvas.shapesChanged()
                cadCanvas.requestPaint()
                if (typeof cad !== "undefined" && cad) {
                    cad.updateShapes(cadCanvas.shapes)
                }
            }
        }
    }

    // Laser Pen Color Palette & Configuration Modal
    CadColorPickerModal {
        id: colorPickerModal
        onColorConfirmed: function(penId, newColor, newName) {
            Theme.updatePenColor(penId, newColor)
            if (newName && newName.length > 0) {
                Theme.updatePenParam(penId, "name", newName)
            }
            if (typeof cad !== "undefined" && cad) {
                cad.updateShapes(cadCanvas.shapes)
            }
            cadCanvas.shapesChanged()
            cadCanvas.requestPaint()
        }
    }

    Component.onCompleted: {
        Qt.callLater(function() {
            if (cadCanvas) cadCanvas.fitField()
        })
    }
}
