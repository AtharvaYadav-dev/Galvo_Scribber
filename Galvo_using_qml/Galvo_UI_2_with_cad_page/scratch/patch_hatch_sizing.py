with open("qml/components/cad/CadHatchModal.qml", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Layout.preferredWidth: 0 and Layout.preferredHeight: 0 to ScrollView
old_sv = """            // Scrollable Content View for responsive scaling
            ScrollView {
                id: hatchScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true"""

new_sv = """            // Scrollable Content View for responsive scaling
            ScrollView {
                id: hatchScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 0
                Layout.preferredHeight: 0
                clip: true"""

assert old_sv in content, "old_sv not found"
content = content.replace(old_sv, new_sv)

# 2. Update Mark Contour Card Layout properties
old_contour = """                // Global Boundary Contour Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: (modalCard.width >= 720) ? 300 : -1
                    Layout.preferredHeight: 48"""

new_contour = """                // Global Boundary Contour Card
                Rectangle {
                    Layout.preferredWidth: (modalCard.width >= 720) ? 280 : -1
                    Layout.fillWidth: (modalCard.width < 720)
                    Layout.preferredHeight: 48"""

assert old_contour in content, "old_contour not found"
content = content.replace(old_contour, new_contour)

# 3. Add shortName to profile tabs repeater so tabs fit on narrower screens
old_tabs_model = """                        Repeater {
                            model: [
                                { idx: 1, name: "Hatch Profile 1" },
                                { idx: 2, name: "Hatch Profile 2" },
                                { idx: 3, name: "Hatch Profile 3" }
                            ]"""

new_tabs_model = """                        Repeater {
                            model: [
                                { idx: 1, name: "Hatch Profile 1", shortName: "Hatch 1" },
                                { idx: 2, name: "Hatch Profile 2", shortName: "Hatch 2" },
                                { idx: 3, name: "Hatch Profile 3", shortName: "Hatch 3" }
                            ]"""

assert old_tabs_model in content, "old_tabs_model not found"
content = content.replace(old_tabs_model, new_tabs_model)

old_tab_text = """                                    Text {
                                        text: modelData.name
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: root.currentProfileIdx === modelData.idx ? Font.Bold : Font.DemiBold
                                        color: root.currentProfileIdx === modelData.idx ? "#08101C" : Theme.textPrimary
                                    }"""

new_tab_text = """                                    Text {
                                        text: (modalCard.width < 780 && modalCard.width >= 720) ? modelData.shortName : modelData.name
                                        font.family: "Segoe UI, Inter, sans-serif"
                                        font.pixelSize: 11
                                        font.weight: root.currentProfileIdx === modelData.idx ? Font.Bold : Font.DemiBold
                                        color: root.currentProfileIdx === modelData.idx ? "#08101C" : Theme.textPrimary
                                        elide: Text.ElideRight
                                    }"""

assert old_tab_text in content, "old_tab_text not found"
content = content.replace(old_tab_text, new_tab_text)

with open("qml/components/cad/CadHatchModal.qml", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated CadHatchModal.qml successfully")

