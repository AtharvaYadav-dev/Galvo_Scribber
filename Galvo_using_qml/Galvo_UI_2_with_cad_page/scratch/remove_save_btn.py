with open("qml/components/cad/CadInspectorPanel.qml", "r", encoding="utf-8") as f:
    content = f.read()

save_button_block = """                            // [ 💾 ] Save Preset Shortcut Button
                            Rectangle {
                                width: 32
                                height: 32
                                radius: 5
                                color: sBtnMa.containsMouse ? (Theme.isDark ? "#17233D" : "#E2E8F0") : Theme.bgCardAlt
                                border.color: Theme.borderCard
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "💾"
                                    font.pixelSize: 12
                                }
                                MouseArea {
                                    id: sBtnMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (typeof cad !== "undefined" && cad) {
                                            cad.set_status_message("Font preset configuration saved.")
                                        }
                                    }
                                }
                                ToolTip.visible: sBtnMa.containsMouse
                                ToolTip.text: "Save Font Configuration Preset"
                            }"""

if save_button_block in content:
    content = content.replace(save_button_block, "")
    print("Successfully removed save button block from CadInspectorPanel.qml")
else:
    print("Target block not found directly, checking variations...")
    import re
    pattern = r"\s*// \[ 💾 \] Save Preset Shortcut Button[\s\S]*?ToolTip\.text: \"Save Font Configuration Preset\"\s*\}"
    content = re.sub(pattern, "", content)
    print("Substituted via regex")

with open("qml/components/cad/CadInspectorPanel.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved CadInspectorPanel.qml")

