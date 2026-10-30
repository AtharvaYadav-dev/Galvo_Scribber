with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Marking Speed"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: speedSlider.value.toFixed(0) + " mm/s"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentCyan }
                        }
                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            from: 100
                            to: 5000
                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.speed : 1200
                            }
                            stepSize: 50
                            onValueChanged: {
                                Theme.updatePenParam(root.selectedPenId, "speed", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setSpeed(value)
                            }
                        }
                    }

                    // Power
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Laser Power"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: powerSlider.value.toFixed(0) + " %"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                        }
                        Slider {
                            id: powerSlider
                            Layout.fillWidth: true
                            from: 5
                            to: 100
                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.power : 50
                            }
                            stepSize: 1
                            onValueChanged: {
                                Theme.updatePenParam(root.selectedPenId, "power", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setPower(value)
                            }
                        }
                    }

                    // Frequency
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Q-Pulse Frequency"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: freqSlider.value.toFixed(0) + " kHz"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentGreen }
                        }
                        Slider {
                            id: freqSlider
                            Layout.fillWidth: true
                            from: 20
                            to: 100
                            value: {
                                var p = Theme.getPen(root.selectedPenId)
                                return p ? p.freq : 35
                            }
                            stepSize: 1
                            onValueChanged: {
                                Theme.updatePenParam(root.selectedPenId, "freq", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setFrequency(value)
                            }
                        }
                    }"""

new_block = """                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Marking Speed"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: speedSlider.value.toFixed(0) + " mm/s"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentCyan }
                        }
                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            from: 100
                            to: 5000
                            value: 1200
                            stepSize: 50
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "speed", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setSpeed(value)
                            }
                        }
                    }

                    // Power
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Laser Power"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: powerSlider.value.toFixed(0) + " %"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentAmber }
                        }
                        Slider {
                            id: powerSlider
                            Layout.fillWidth: true
                            from: 5
                            to: 100
                            value: 50
                            stepSize: 1
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "power", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setPower(value)
                            }
                        }
                    }

                    // Frequency
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Q-Pulse Frequency"; font.family: "Segoe UI, Inter, sans-serif"; font.pixelSize: 11; color: Theme.textPrimary }
                            Item { Layout.fillWidth: true }
                            Text { text: freqSlider.value.toFixed(0) + " kHz"; font.family: "Consolas, monospace"; font.pixelSize: 11; font.weight: Font.Bold; color: Theme.accentGreen }
                        }
                        Slider {
                            id: freqSlider
                            Layout.fillWidth: true
                            from: 20
                            to: 100
                            value: 35
                            stepSize: 1
                            onMoved: {
                                Theme.updatePenParam(root.selectedPenId, "freq", value)
                                if (typeof galvo !== "undefined" && galvo) galvo.setFrequency(value)
                            }
                        }
                    }"""

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("Replaced slider bindings with onMoved successfully")
else:
    print("WARNING: old_block not found")

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved CadInspectorPanel.qml")
