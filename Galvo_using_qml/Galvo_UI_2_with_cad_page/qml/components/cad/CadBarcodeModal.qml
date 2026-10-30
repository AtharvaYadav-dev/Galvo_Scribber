import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

Rectangle {
    id: root

    property string barcodeType: "QR Code"
    property string textContent: "https://www.specialiseproducts.com"
    property real codeSizeMm: 20.0
    property string outputFormat: "dxf" // "dxf" (Vector CAD), "svg" (Vector Paths), "barcode" (Optical)
    property bool autoIncrement: false
    property int startNumber: 1
    property int stepIncrement: 1

    signal generateBarcode(string type, string content, real sizeMm, bool autoInc, string outputFormat)
    signal closed()

    function close() {
        root.visible = false
        root.closed()
    }

    anchors.fill: parent
    color: "transparent"
    z: 100

    onVisibleChanged: {
        if (visible && root.width > 0 && root.height > 0) {
            modalCard.x = Math.max(10, Math.round((root.width - modalCard.width) / 2))
            modalCard.y = Math.max(10, Math.round((root.height - modalCard.height) / 2))
        }
    }

    focus: visible
    Keys.onEscapePressed: root.close()

    // Full Backdrop Blocker: Absorbs all clicks, drags, hover, and wheel events so background is never affected
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        preventStealing: true
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onWheel: function(wheel) { wheel.accepted = true }
        onPressed: function(mouse) { mouse.accepted = true }
        onReleased: function(mouse) { mouse.accepted = true }
        onClicked: function(mouse) { mouse.accepted = true }
        onDoubleClicked: function(mouse) { mouse.accepted = true }
        onPositionChanged: function(mouse) { mouse.accepted = true }
    }

    Rectangle {
        id: modalCard
        x: Math.max(10, Math.round((root.width - width) / 2))
        y: Math.max(10, Math.round((root.height - height) / 2))
        width: 460
        height: 520
        radius: 10
        color: Theme.bgCard
        border.color: Theme.accentCyan
        border.width: 1.5

        // Prevent click-through and consume unhandled wheel events within the modal card
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            onWheel: function(wheel) { wheel.accepted = true }
            onPressed: function(mouse) { mouse.accepted = true }
            onReleased: function(mouse) { mouse.accepted = true }
            onClicked: function(mouse) { mouse.accepted = true }
            onDoubleClicked: function(mouse) { mouse.accepted = true }
        }

        WheelHandler {
            target: null
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            onWheel: function(event) {
                event.accepted = true
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header (Draggable)
            Item {
                Layout.fillWidth: true
                implicitHeight: headerRow.implicitHeight

                MouseArea {
                    id: barcodeHeaderDrag
                    anchors.fill: parent
                    drag.target: modalCard
                    drag.minimumX: -modalCard.width + 100
                    drag.maximumX: root.width - 100
                    drag.minimumY: 0
                    drag.maximumY: root.height - 50
                    cursorShape: Qt.SizeAllCursor
                }

                RowLayout {
                    id: headerRow
                    anchors.fill: parent

                    CadIcon {
                        name: "qr_code_2"
                        size: 22
                        iconColor: Theme.accentCyan
                    }
                    Text {
                        text: "QR Code & Barcode Generator"
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }
                    Item { Layout.fillWidth: true }
                    CadButton {
                        z: 2
                        iconName: "close"
                        variant: "ghost"
                        implicitWidth: 30
                        implicitHeight: 30
                        onClicked: root.close()
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.borderMuted }

            // Scrollable Settings Body
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    width: modalCard.width - 40
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Repeater {
                            model: ["QR Code", "Code 128", "DataMatrix"]
                            delegate: CadButton {
                                Layout.fillWidth: true
                                text: modelData
                                isActive: root.barcodeType === modelData
                                onClicked: root.barcodeType = modelData
                            }
                        }
                    }

                    // Format Selector: DXF Vector vs SVG Vector vs Optical Barcode
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Text {
                            text: "CANVAS ADD FORMAT / GEOMETRY TYPE"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Repeater {
                                model: [
                                    { id: "dxf", label: "DXF Vector (CAD)", tip: "Adds as pure CAD polylines in laser pen color (No white PNG card)" },
                                    { id: "svg", label: "SVG Vector", tip: "Adds as SVG vector paths (No white PNG card)" },
                                    { id: "barcode", label: "Optical Card", tip: "Adds as screen scannable barcode card" }
                                ]
                                delegate: CadButton {
                                    Layout.fillWidth: true
                                    text: modelData.label
                                    isActive: root.outputFormat === modelData.id
                                    tooltipText: modelData.tip
                                    onClicked: root.outputFormat = modelData.id
                                }
                            }
                        }
                    }


                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Text {
                            text: "ENCODED TEXT / URL / SERIAL NUMBER"
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.textMuted
                        }
                        TextField {
                            id: contentField
                            Layout.fillWidth: true
                            text: root.textContent
                            font.family: "Consolas, monospace"
                            font.pixelSize: 12
                            color: Theme.textPrimary
                            placeholderText: "Enter data to encode..."
                            onTextChanged: root.textContent = text
                            background: Rectangle {
                                radius: 5
                                color: Theme.bgInput
                                border.color: contentField.activeFocus ? Theme.borderInputFocus : Theme.borderInput
                                border.width: 1
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Physical Matrix Dimension"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 12; color: Theme.textPrimary }
                        Item { Layout.fillWidth: true }
                        CadInput {
                            unit: "mm"
                            text: root.codeSizeMm.toFixed(1)
                            onValueChanged: function(v) { root.codeSizeMm = v }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 110
                        radius: 6
                        color: Theme.bgCardAlt
                        border.color: Theme.borderCard
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            CadCheckBox {
                                id: incCheck
                                text: "Enable Industrial Auto-Increment Counter"
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                checked: root.autoIncrement
                                onCheckedChanged: root.autoIncrement = checked
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                enabled: root.autoIncrement
                                opacity: root.autoIncrement ? 1.0 : 0.4

                                CadInput {
                                    Layout.fillWidth: true
                                    label: "Start #"
                                    text: root.startNumber.toString()
                                    onValueChanged: function(v) { root.startNumber = Math.round(v) }
                                }

                                CadInput {
                                    Layout.fillWidth: true
                                    label: "Step (+)"
                                    text: root.stepIncrement.toString()
                                    onValueChanged: function(v) { root.stepIncrement = Math.round(v) }
                                }
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                CadButton {
                    Layout.fillWidth: true
                    text: "Export DXF"
                                        variant: "outline"
                    tooltipText: "Export Vector DXF for EzCad / AutoCAD / LightBurn"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp, "dxf")
                        }
                    }
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Export SVG"
                                        variant: "outline"
                    tooltipText: "Export Scalable Vector Graphics (SVG)"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp2 = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp2, "svg")
                        }
                    }
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Export PNG"
                                        variant: "outline"
                    tooltipText: "Export High-Resolution Scannable PNG Image"
                    onClicked: {
                        if (typeof cad !== "undefined" && cad) {
                            var tempShp3 = {
                                type: root.barcodeType === "QR Code" ? "qrcode" : (root.barcodeType === "Code 128" ? "barcode128" : "datamatrix"),
                                text: root.textContent,
                                wMm: root.codeSizeMm,
                                hMm: root.codeSizeMm,
                                name: (root.barcodeType === "QR Code" ? "QRCode" : (root.barcodeType === "Code 128" ? "Barcode128" : "DataMatrix"))
                            }
                            cad.exportBarcodeFile(tempShp3, "png")
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                CadButton {
                    Layout.fillWidth: true
                    text: "Cancel"
                    variant: "secondary"
                    onClicked: root.close()
                }

                CadButton {
                    Layout.fillWidth: true
                    text: "Add to Canvas"
                    variant: "accent"
                    onClicked: {
                        root.generateBarcode(root.barcodeType, root.textContent, root.codeSizeMm, root.autoIncrement, root.outputFormat)
                        root.close()
                    }
                }
            }
        }

        // Responsive Resize Handle
        CadWindowResizeHandle {
            target: modalCard
            minWidth: 380
            minHeight: 380
        }
    }
}
