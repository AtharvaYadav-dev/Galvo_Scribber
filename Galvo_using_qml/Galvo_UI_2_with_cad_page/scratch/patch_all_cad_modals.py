import os
import re

base_dir = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad"

backdrop_blocker = '''    // Full Backdrop Blocker: Absorbs all clicks, drags, hover, and wheel events so background is never affected
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
'''

card_blocker_code = '''        // Prevent click-through and consume unhandled wheel events within the modal card
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
        }'''

# 1. CadHatchModal.qml
hatch_path = os.path.join(base_dir, "CadHatchModal.qml")
with open(hatch_path, "r", encoding="utf-8") as f:
    h_text = f.read()

if "Full Backdrop Blocker" not in h_text:
    target = "    // Modern Studio Card Window (Movable floating card)\n    Rectangle {\n        id: modalCard"
    replacement = backdrop_blocker + "\n" + target
    if target in h_text:
        h_text = h_text.replace(target, replacement, 1)
        with open(hatch_path, "w", encoding="utf-8") as f:
            f.write(h_text)
        print("Updated CadHatchModal.qml with backdrop blocker")
    else:
        print("Could not match target in CadHatchModal.qml")

# 2. CadBarcodeModal.qml
barcode_path = os.path.join(base_dir, "CadBarcodeModal.qml")
with open(barcode_path, "r", encoding="utf-8") as f:
    b_text = f.read()

if "Full Backdrop Blocker" not in b_text:
    target = "    Rectangle {\n        id: modalCard"
    replacement = backdrop_blocker + "\n    Rectangle {\n        id: modalCard"
    b_text = b_text.replace(target, replacement, 1)
    b_text = b_text.replace(
        "        MouseArea { anchors.fill: parent }",
        card_blocker_code,
        1
    )
    with open(barcode_path, "w", encoding="utf-8") as f:
        f.write(b_text)
    print("Updated CadBarcodeModal.qml")

# 3. CadTextFontModal.qml
font_path = os.path.join(base_dir, "CadTextFontModal.qml")
with open(font_path, "r", encoding="utf-8") as f:
    f_text = f.read()

if "Full Backdrop Blocker" not in f_text:
    target = "    // Modal Card (Movable floating card)\n    Rectangle {\n        id: modalBox"
    replacement = backdrop_blocker + "\n" + target
    f_text = f_text.replace(target, replacement, 1)
    f_text = f_text.replace(
        "        MouseArea { anchors.fill: parent }",
        card_blocker_code,
        1
    )
    with open(font_path, "w", encoding="utf-8") as f:
        f.write(f_text)
    print("Updated CadTextFontModal.qml")

# 4. CadArrayModal.qml
array_path = os.path.join(base_dir, "CadArrayModal.qml")
with open(array_path, "r", encoding="utf-8") as f:
    a_text = f.read()

if "Full Backdrop Blocker" not in a_text:
    target = "    // Modal Card (Movable floating card)\n    Rectangle {\n        id: modalBox"
    replacement = backdrop_blocker + "\n" + target
    a_text = a_text.replace(target, replacement, 1)
    a_text = a_text.replace(
        "        MouseArea { anchors.fill: parent }",
        card_blocker_code,
        1
    )
    with open(array_path, "w", encoding="utf-8") as f:
        f.write(a_text)
    print("Updated CadArrayModal.qml")

# 5. CadInputPortModal.qml
port_path = os.path.join(base_dir, "CadInputPortModal.qml")
with open(port_path, "r", encoding="utf-8") as f:
    p_text = f.read()

if "Full Backdrop Blocker" not in p_text:
    target = "    // Modal Card (Movable floating card)\n    Rectangle {\n        id: modalBox"
    replacement = backdrop_blocker + "\n" + target
    p_text = p_text.replace(target, replacement, 1)
    p_text = p_text.replace(
        "        MouseArea { anchors.fill: parent }",
        card_blocker_code,
        1
    )
    with open(port_path, "w", encoding="utf-8") as f:
        f.write(p_text)
    print("Updated CadInputPortModal.qml")

# 6. CadVariableTextModal.qml
var_path = os.path.join(base_dir, "CadVariableTextModal.qml")
with open(var_path, "r", encoding="utf-8") as f:
    vt_text = f.read()

if "Full Backdrop Blocker" not in vt_text:
    target = "    // Modal Card (Movable floating card)\n    Rectangle {\n        id: modalBox"
    replacement = backdrop_blocker + "\n" + target
    vt_text = vt_text.replace(target, replacement, 1)
    vt_text = vt_text.replace(
        "        MouseArea { anchors.fill: parent }",
        card_blocker_code,
        1
    )
    with open(var_path, "w", encoding="utf-8") as f:
        f.write(vt_text)
    print("Updated CadVariableTextModal.qml")

# 7. CadColorPickerModal.qml
color_path = os.path.join(base_dir, "CadColorPickerModal.qml")
with open(color_path, "r", encoding="utf-8") as f:
    c_text = f.read()

if "onWheel: function(wheel)" not in c_text:
    c_text = c_text.replace(
        '    MouseArea {\n        anchors.fill: parent\n        onClicked: root.closeModal()\n    }',
        '''    // Backdrop Blocker: Absorbs all mouse, drag, hover, and wheel events
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        preventStealing: true
        acceptedButtons: Qt.AllButtons
        cursorShape: Qt.ArrowCursor
        onWheel: function(wheel) { wheel.accepted = true }
        onPressed: function(mouse) { mouse.accepted = true }
        onReleased: function(mouse) { mouse.accepted = true }
        onClicked: root.closeModal()
    }''',
        1
    )
    c_text = c_text.replace(
        '        MouseArea {\n            anchors.fill: parent\n            // Prevent clicks from reaching backdrop\n        }',
        card_blocker_code,
        1
    )
    with open(color_path, "w", encoding="utf-8") as f:
        f.write(c_text)
    print("Updated CadColorPickerModal.qml")

print("All CAD modals patched successfully!")

