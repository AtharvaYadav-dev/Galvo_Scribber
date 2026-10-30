import os
import re

base_dir = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page"

# 1. Update main.qml: Add isAnyModalOpen property to ApplicationWindow
main_qml_path = os.path.join(base_dir, "qml", "main.qml")
with open(main_qml_path, "r", encoding="utf-8") as f:
    content = f.read()

if "isAnyModalOpen:" not in content:
    target = '    function toggleTheme() {\n        Theme.toggleTheme()\n    }'
    replacement = '''    function toggleTheme() {
        Theme.toggleTheme()
    }

    readonly property bool isAnyModalOpen: Boolean(
        (typeof jogModal !== "undefined" && jogModal && jogModal.opacity > 0) ||
        (typeof laserModal !== "undefined" && laserModal && laserModal.opacity > 0) ||
        (typeof configModal !== "undefined" && configModal && configModal.opacity > 0) ||
        (typeof paramMatrixModal !== "undefined" && paramMatrixModal && paramMatrixModal.opacity > 0) ||
        (typeof settingsModal !== "undefined" && settingsModal && settingsModal.opacity > 0) ||
        (typeof corCalibrationModal !== "undefined" && corCalibrationModal && corCalibrationModal.opacity > 0) ||
        (typeof autoConnectModal !== "undefined" && autoConnectModal && autoConnectModal.visible)
    )'''
    if target in content:
        content = content.replace(target, replacement, 1)
        with open(main_qml_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated main.qml with isAnyModalOpen")
    else:
        print("Could not find target in main.qml")
else:
    print("main.qml already has isAnyModalOpen")

# 2. Update CadCanvas.qml: Add interactionBlocked property and check it in canvasMa
cad_canvas_path = os.path.join(base_dir, "qml", "components", "cad", "CadCanvas.qml")
with open(cad_canvas_path, "r", encoding="utf-8") as f:
    c_content = f.read()

if "property bool interactionBlocked: false" not in c_content:
    c_content = c_content.replace(
        'Item {\n    id: root',
        'Item {\n    id: root\n\n    property bool interactionBlocked: false',
        1
    )
    print("Added property bool interactionBlocked to CadCanvas.qml")

# Update canvasMa in CadCanvas.qml to be disabled or check interactionBlocked
if "enabled: !root.interactionBlocked" not in c_content:
    c_content = c_content.replace(
        'MouseArea {\n        id: canvasMa\n        anchors.fill: parent',
        'MouseArea {\n        id: canvasMa\n        anchors.fill: parent\n        enabled: !root.interactionBlocked',
        1
    )
    print("Updated canvasMa enabled in CadCanvas.qml")

# In onWheel in CadCanvas.qml
if "if (root.interactionBlocked)" not in c_content:
    c_content = c_content.replace(
        'onWheel: function(wheel) {',
        'onWheel: function(wheel) {\n            if (root.interactionBlocked) {\n                wheel.accepted = true\n                return\n            }',
        1
    )
    print("Updated onWheel in CadCanvas.qml")

with open(cad_canvas_path, "w", encoding="utf-8") as f:
    f.write(c_content)

# 3. Update CadView.qml: Expose isAnyModalActive and pass to cadCanvas
cad_view_path = os.path.join(base_dir, "qml", "views", "CadView.qml")
with open(cad_view_path, "r", encoding="utf-8") as f:
    v_content = f.read()

if "isAnyModalActive" not in v_content:
    v_target = '    property bool hasSelection: inspector.selectedIndex >= 0 && inspector.selectedIndex < cadCanvas.shapes.length'
    v_replacement = '''    property bool hasSelection: inspector.selectedIndex >= 0 && inspector.selectedIndex < cadCanvas.shapes.length

    readonly property bool isAnyCadModalOpen: Boolean(
        (typeof hatchModal !== "undefined" && hatchModal && hatchModal.visible) ||
        (typeof barcodeModal !== "undefined" && barcodeModal && barcodeModal.visible) ||
        (typeof textFontModal !== "undefined" && textFontModal && textFontModal.visible) ||
        (typeof arrayModal !== "undefined" && arrayModal && arrayModal.visible) ||
        (typeof inputPortModal !== "undefined" && inputPortModal && inputPortModal.visible) ||
        (typeof variableTextModal !== "undefined" && variableTextModal && variableTextModal.visible) ||
        (typeof colorPickerModal !== "undefined" && colorPickerModal && colorPickerModal.visible)
    )

    readonly property bool isAnyModalActive: Boolean(
        isAnyCadModalOpen ||
        (typeof window !== "undefined" && window && window.isAnyModalOpen)
    )'''
    v_content = v_content.replace(v_target, v_replacement, 1)

    v_content = v_content.replace(
        'CadCanvas {\n                            id: cadCanvas\n                            objectName: "cadCanvas"',
        'CadCanvas {\n                            id: cadCanvas\n                            objectName: "cadCanvas"\n                            interactionBlocked: root.isAnyModalActive',
        1
    )
    with open(cad_view_path, "w", encoding="utf-8") as f:
        f.write(v_content)
    print("Updated CadView.qml with isAnyModalActive and wired interactionBlocked")
else:
    print("CadView.qml already has isAnyModalActive")

print("Stage 1 complete.")

