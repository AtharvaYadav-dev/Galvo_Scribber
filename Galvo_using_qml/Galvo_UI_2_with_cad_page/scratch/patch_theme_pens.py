with open('qml/Theme.qml', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """    // --- 8 Industrial Laser Pens / Layers Palette ---
    readonly property var penPalette: [
        { id: 0, name: "Pen 0 (Default)", color: isDark ? "#FFFFFF" : "#000000", speed: 1200, power: 50, freq: 35, passes: 1 },
        { id: 1, name: "Pen 1 (Blue)",    color: "#2563EB", speed: 1800, power: 40, freq: 45, passes: 1 },
        { id: 2, name: "Pen 2 (Red)",     color: "#EF4444", speed: 800,  power: 75, freq: 30, passes: 2 },
        { id: 3, name: "Pen 3 (Green)",   color: "#10B981", speed: 2000, power: 30, freq: 60, passes: 1 },
        { id: 4, name: "Pen 4 (Amber)",   color: "#F59E0B", speed: 1500, power: 60, freq: 40, passes: 1 },
        { id: 5, name: "Pen 5 (Purple)",  color: "#A855F7", speed: 1000, power: 70, freq: 35, passes: 1 },
        { id: 6, name: "Pen 6 (Cyan)",    color: "#06B6D4", speed: 2200, power: 25, freq: 70, passes: 1 },
        { id: 7, name: "Pen 7 (Brown)",   color: "#854D0E", speed: 600,  power: 85, freq: 25, passes: 3 }
    ]"""

new_block = """    // --- Dynamic Industrial Laser Pens / Layers Palette ---
    property var penPalette: [
        { id: 0, name: "Pen 0 (Default)", color: isDark ? "#00E5FF" : "#192D78", speed: 1200, power: 50, freq: 35, passes: 1 },
        { id: 1, name: "Pen 1 (Blue)",    color: "#2563EB", speed: 1800, power: 40, freq: 45, passes: 1 },
        { id: 2, name: "Pen 2 (Red)",     color: "#EF4444", speed: 800,  power: 75, freq: 30, passes: 2 },
        { id: 3, name: "Pen 3 (Green)",   color: "#10B981", speed: 2000, power: 30, freq: 60, passes: 1 },
        { id: 4, name: "Pen 4 (Amber)",   color: "#F59E0B", speed: 1500, power: 60, freq: 40, passes: 1 },
        { id: 5, name: "Pen 5 (Purple)",  color: "#A855F7", speed: 1000, power: 70, freq: 35, passes: 1 },
        { id: 6, name: "Pen 6 (Cyan)",    color: "#06B6D4", speed: 2200, power: 25, freq: 70, passes: 1 },
        { id: 7, name: "Pen 7 (Brown)",   color: "#854D0E", speed: 600,  power: 85, freq: 25, passes: 3 }
    ]

    signal penPaletteUpdated()

    function getPen(penId) {
        for (var i = 0; i < penPalette.length; i++) {
            if (penPalette[i].id === penId) return penPalette[i]
        }
        return penPalette.length > 0 ? penPalette[0] : null
    }

    function getPenColor(penId) {
        var p = getPen(penId)
        return p ? p.color : (isDark ? "#00E5FF" : "#192D78")
    }

    function syncFromBackend() {
        if (typeof cad !== "undefined" && cad && cad.getPens) {
            var loaded = cad.getPens()
            if (loaded && loaded.length > 0) {
                penPalette = loaded
                penPaletteUpdated()
            }
        }
    }

    function addPen(customColor, customName) {
        if (typeof cad !== "undefined" && cad && cad.addPen) {
            var newId = cad.addPen(customName || "", customColor || "")
            penPalette = cad.getPens()
            penPaletteUpdated()
            return newId
        }
        var nextId = 0
        for (var i = 0; i < penPalette.length; i++) {
            if (penPalette[i].id >= nextId) nextId = penPalette[i].id + 1
        }
        var distinctColors = ["#EC4899", "#14B8A6", "#EAB308", "#6366F1", "#F97316", "#84CC16", "#06B6D4", "#A855F7", "#F43F5E", "#3B82F6"]
        var col = customColor || distinctColors[(nextId - 8) % distinctColors.length] || "#00E5FF"
        var arr = penPalette.slice()
        arr.push({
            id: nextId,
            name: customName || ("Pen " + nextId),
            color: col,
            speed: 1500,
            power: 50,
            freq: 35,
            passes: 1
        })
        penPalette = arr
        penPaletteUpdated()
        return nextId
    }

    function updatePenColor(penId, newColor) {
        if (typeof cad !== "undefined" && cad && cad.updatePenColor) {
            cad.updatePenColor(penId, newColor)
            penPalette = cad.getPens()
            penPaletteUpdated()
            return
        }
        var arr = penPalette.slice()
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].id === penId) {
                arr[i].color = newColor
                break
            }
        }
        penPalette = arr
        penPaletteUpdated()
    }

    function updatePenParam(penId, key, val) {
        var arr = penPalette.slice()
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].id === penId) {
                arr[i][key] = val
                break
            }
        }
        penPalette = arr
        penPaletteUpdated()
        if (typeof cad !== "undefined" && cad && cad.savePens) {
            cad.savePens(penPalette)
        }
    }

    function deletePen(penId) {
        if (penId === 0) return
        if (typeof cad !== "undefined" && cad && cad.deletePen) {
            cad.deletePen(penId)
            penPalette = cad.getPens()
            penPaletteUpdated()
            return
        }
        var arr = []
        for (var i = 0; i < penPalette.length; i++) {
            if (penPalette[i].id !== penId) arr.push(penPalette[i])
        }
        penPalette = arr
        penPaletteUpdated()
    }

    Component.onCompleted: {
        syncFromBackend()
    }"""

if old_block.replace('\n', '\r\n') in content:
    content = content.replace(old_block.replace('\n', '\r\n'), new_block.replace('\n', '\r\n'), 1)
    print("Replaced penPalette in Theme.qml (CRLF)")
elif old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("Replaced penPalette in Theme.qml (LF)")
else:
    print("WARNING: old_block not found in Theme.qml!")

with open('qml/Theme.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved qml/Theme.qml")

