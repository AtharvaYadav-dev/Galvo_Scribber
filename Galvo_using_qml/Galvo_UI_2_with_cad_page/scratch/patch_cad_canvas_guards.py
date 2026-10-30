import os

path = r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page\qml\components\cad\CadCanvas.qml"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Add to onPressed
if "onPressed: function(mouse) {\n            if (root.interactionBlocked)" not in text:
    text = text.replace(
        "onPressed: function(mouse) {",
        "onPressed: function(mouse) {\n            if (root.interactionBlocked) {\n                mouse.accepted = true\n                return\n            }",
        1
    )

# Add to onPositionChanged
if "onPositionChanged: function(mouse) {\n            if (root.interactionBlocked)" not in text:
    text = text.replace(
        "onPositionChanged: function(mouse) {",
        "onPositionChanged: function(mouse) {\n            if (root.interactionBlocked) {\n                mouse.accepted = true\n                return\n            }",
        1
    )

# Add to onReleased
if "onReleased: function(mouse) {\n            if (root.interactionBlocked)" not in text:
    text = text.replace(
        "onReleased: function(mouse) {",
        "onReleased: function(mouse) {\n            if (root.interactionBlocked) {\n                mouse.accepted = true\n                return\n            }",
        1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Guards added to CadCanvas.qml")

