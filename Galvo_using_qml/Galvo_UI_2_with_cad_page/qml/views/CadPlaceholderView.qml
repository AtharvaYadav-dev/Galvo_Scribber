import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"

Item {
    id: root

    FileDialog {
        id: fileDialog
        title: "Select Vector Artwork (DXF or SVG)"
        nameFilters: ["Vector Files (*.dxf *.svg)", "DXF Files (*.dxf)", "SVG Files (*.svg)", "All Files (*)"]
        onAccepted: {
            if (typeof cad !== "undefined") {
                cad.importFile(selectedFile.toString())
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 16

        // Left: CAD Canvas Workspace Preview
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#12151c"
            radius: 10
            border.color: "#283042"
            border.width: 1
            clip: true

            // Grid Lines Canvas
            Canvas {
                id: gridCanvas
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    var cx = width / 2;
                    var cy = height / 2;
                    var step = 30; // 30px per 10mm

                    // Minor grid
                    ctx.strokeStyle = "#1b212e";
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    for (var x = cx % step; x < width; x += step) {
                        ctx.moveTo(x, 0); ctx.lineTo(x, height);
                    }
                    for (var y = cy % step; y < height; y += step) {
                        ctx.moveTo(0, y); ctx.lineTo(width, y);
                    }
                    ctx.stroke();

                    // Major Axes (Crosshair)
                    ctx.strokeStyle = "#2e3b52";
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.moveTo(cx, 0); ctx.lineTo(cx, height);
                    ctx.moveTo(0, cy); ctx.lineTo(width, cy);
                    ctx.stroke();

                    // Active Galvo Field boundary
                    var fieldSize = step * 10;
                    ctx.strokeStyle = "#00d2ff";
                    ctx.lineWidth = 1.5;
                    ctx.setLineDash([6, 4]);
                    ctx.strokeRect(cx - fieldSize / 2, cy - fieldSize / 2, fieldSize, fieldSize);
                    ctx.setLineDash([]);
                }
            }

            // Top overlay coordinates badge
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 14
                height: 32
                width: 320
                radius: 6
                color: "#dd161a24"
                border.color: "#353e54"
                border.width: 1

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 8
                    Rectangle {
                        width: 8; height: 8; radius: 4
                        color: (typeof cad !== "undefined" && cad.shapeCount > 0) ? "#2ed573" : "#f5a623"
                    }
                    Text {
                        text: "Shapes Loaded: " + (typeof cad !== "undefined" ? cad.shapeCount : "0") + "  |  Field: 100×100 mm"
                        color: "#ffffff"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                    }
                }
            }

            // Center Callout Banner with Fast Action Buttons
            Rectangle {
                anchors.centerIn: parent
                width: 440
                height: 200
                radius: 10
                color: "#ee161a24"
                border.color: "#00d2ff"
                border.width: 1.5

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 12

                    Text {
                        text: "📐 2D CAD VECTOR & HATCHING ENGINE"
                        color: "#ffffff"
                        font.pixelSize: 15
                        font.weight: Font.Bold
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: "Full EzCad parity: Text, Polylines, QR, Hatching & Pen layers\nLinked directly to the Galvo motion controller"
                        color: "#8e9cb0"
                        font.pixelSize: 11
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 10

                        ModernButton {
                            text: "🚀 Open Full Vector Canvas"
                            primary: true
                            implicitWidth: 190
                            implicitHeight: 40
                            onClicked: if (typeof cad !== "undefined") cad.openCadEditor()
                        }

                        ModernButton {
                            text: "📁 Import DXF / SVG"
                            implicitWidth: 150
                            implicitHeight: 40
                            onClicked: fileDialog.open()
                        }
                    }
                }
            }
        }

        // Right: Direct Laser Execution & Layer Palette
        Rectangle {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            color: "#161a24"
            radius: 10
            border.color: "#283042"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                Text {
                    text: "LASER EXECUTION (EZCAD)"
                    color: "#8e9cb0"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                }

                // Red Light Framing (F1)
                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    text: (typeof cad !== "undefined" && cad.isFraming) ? "🔴 STOP Red Guide (F1)" : "🔴 Red Guide Framing (F1)"
                    btnColor: (typeof cad !== "undefined" && cad.isFraming) ? "#7a2a10" : "#202534"
                    borderColor: (typeof cad !== "undefined" && cad.isFraming) ? "#e67e22" : "#323b50"
                    onClicked: if (typeof cad !== "undefined") cad.toggleFraming()
                }

                // Laser Mark (F2)
                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 52
                    text: (typeof cad !== "undefined" && cad.isMarking) ? "⚡ MARKING IN PROGRESS..." : "⚡ Laser Mark All (F2)"
                    primary: !(typeof cad !== "undefined" && cad.isMarking)
                    btnColor: (typeof cad !== "undefined" && cad.isMarking) ? "#163820" : "#00b4d8"
                    borderColor: (typeof cad !== "undefined" && cad.isMarking) ? "#2ed573" : "#00d2ff"
                    onClicked: if (typeof cad !== "undefined") cad.executeMark()
                }

                // Abort Button
                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    text: "⏹ Abort Execution"
                    danger: true
                    onClicked: if (typeof cad !== "undefined") cad.abortMark()
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: "#283042" }

                Text {
                    text: "EZCAD 8-PEN LAYERS"
                    color: "#8e9cb0"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                }

                // 8 Pens Grid
                GridLayout {
                    columns: 4
                    columnSpacing: 8
                    rowSpacing: 8
                    Layout.fillWidth: true

                    readonly property var penColors: [
                        "#000000", "#0000ff", "#ff0000", "#00aa00",
                        "#e67e22", "#9b59b6", "#00a8ff", "#795548"
                    ]

                    Repeater {
                        model: parent.penColors
                        Rectangle {
                            required property string modelData
                            required property int index
                            Layout.preferredWidth: 54
                            Layout.preferredHeight: 32
                            radius: 6
                            color: "#1d2331"
                            border.color: modelData
                            border.width: 1.5

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 4
                                Rectangle {
                                    width: 10; height: 10; radius: 5
                                    color: modelData
                                }
                                Text {
                                    text: "Pen " + index
                                    color: "#ffffff"
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                // Quick Launch Full Canvas
                ModernButton {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 44
                    text: "🎨 Open Design & Hatching Tools"
                    onClicked: if (typeof cad !== "undefined") cad.openCadEditor()
                }
            }
        }
    }
}
