with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add property int currentPenId: 0 to root
target_prop = "    property int selectedIndex: -1"
new_prop = """    property int selectedIndex: -1
    property int currentPenId: 0"""

if target_prop in content:
    content = content.replace(target_prop, new_prop, 1)
    print("Added currentPenId property")
else:
    print("WARNING: target_prop not found")

# 2. Update line 229 (group creation)
old_grp = "penId: (selectedIndex >= 0 && selectedIndex < shapes.length) ? (shapes[selectedIndex].penId || 0) : 0,"
new_grp = "penId: root.currentPenId,"
if old_grp in content:
    content = content.replace(old_grp, new_grp, 1)
    print("Updated group penId")
else:
    print("WARNING: old_grp not found")

# 3. Update line 328 (polygon creation)
old_poly = "penId: (selectedIndex >= 0 && selectedIndex < shapes.length) ? (shapes[selectedIndex].penId || 0) : 0,"
new_poly = "penId: root.currentPenId,"
if old_poly in content:
    content = content.replace(old_poly, new_poly, 1)
    print("Updated polyline penId")
else:
    print("WARNING: old_poly not found")

# 4. Update line 1440 (interactive shape release)
old_draw = """                var penId = (root.selectedIndex >= 0 && root.selectedIndex < root.shapes.length)
                    ? (root.shapes[root.selectedIndex].penId || 0) : 0"""
new_draw = "                var penId = root.currentPenId"
if old_draw in content:
    content = content.replace(old_draw, new_draw, 1)
    print("Updated interactive drawing penId to root.currentPenId")
else:
    print("WARNING: old_draw not found")

# 5. Update hatch color selection line 1039
old_hatch_col = """                            var hPenCol = (hline.pen_id !== undefined && hline.pen_id >= 0)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor"""
new_hatch_col = """                            var hPenCol = (hline.pen_id !== undefined && hline.pen_id > 0)
                                ? Theme.getPenColor(hline.pen_id)
                                : penColor"""
if old_hatch_col in content:
    content = content.replace(old_hatch_col, new_hatch_col, 1)
    print("Updated hatch color logic (prefer shape penColor if hline.pen_id == 0)")
else:
    print("WARNING: old_hatch_col not found")

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved CadCanvas.qml")

