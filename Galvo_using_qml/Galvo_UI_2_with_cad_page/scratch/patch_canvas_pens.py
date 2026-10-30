with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace penColor lookup
c1_old = "var penColor = Theme.penPalette[(shp.penId || 0) % Theme.penPalette.length].color"
c1_new = "var penColor = Theme.getPenColor(shp.penId || 0)"

if c1_old in content:
    content = content.replace(c1_old, c1_new, 1)
    print("Replaced line 775")
else:
    print("WARNING: c1_old not found!")

# 2. Replace cPen lookup
c2_old = "var cPen = Theme.penPalette[((ch.penId !== undefined ? ch.penId : shp.penId) || 0) % Theme.penPalette.length].color"
c2_new = "var cPen = Theme.getPenColor((ch.penId !== undefined ? ch.penId : shp.penId) || 0)"

if c2_old in content:
    content = content.replace(c2_old, c2_new, 1)
    print("Replaced line 801")
else:
    print("WARNING: c2_old not found!")

# 3. Replace hPenCol lookup
c3_old = """                            var hPenCol = (hline.pen_id !== undefined && hline.pen_id >= 0 && hline.pen_id < Theme.penPalette.length)
                                ? Theme.penPalette[hline.pen_id].color
                                : penColor"""
c3_new = """                            var hPenCol = (hline.pen_id !== undefined && hline.pen_id >= 0)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor"""

if c3_old.replace('\n', '\r\n') in content:
    content = content.replace(c3_old.replace('\n', '\r\n'), c3_new.replace('\n', '\r\n'), 1)
    print("Replaced line 1039 (CRLF)")
elif c3_old in content:
    content = content.replace(c3_old, c3_new, 1)
    print("Replaced line 1039 (LF)")
else:
    print("WARNING: c3_old not found!")

# 4. Add onPenPaletteUpdated to Connections
conn_old = """    Connections {
        target: Theme
        function onIsDarkChanged() { canvas.requestPaint() }
    }"""

conn_new = """    Connections {
        target: Theme
        function onIsDarkChanged() { canvas.requestPaint() }
        function onPenPaletteUpdated() { canvas.requestPaint() }
        function onPenPaletteChanged() { canvas.requestPaint() }
    }"""

if conn_old.replace('\n', '\r\n') in content:
    content = content.replace(conn_old.replace('\n', '\r\n'), conn_new.replace('\n', '\r\n'), 1)
    print("Updated Connections in CadCanvas.qml (CRLF)")
elif conn_old in content:
    content = content.replace(conn_old, conn_new, 1)
    print("Updated Connections in CadCanvas.qml (LF)")
else:
    print("WARNING: conn_old not found!")

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved CadCanvas.qml")

