with open("dxf.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Curve flatten tolerance
old_tol = "self.curve_flatten_tolerance = 0.005"
new_tol = "self.curve_flatten_tolerance = 0.02"
assert old_tol in text, "old_tol not found"
text = text.replace(old_tol, new_tol, 1)

# 2. Layer optimization bypass threshold
old_opt = "if len(items) > 10000:"
new_opt = "if len(items) > 1500:"
assert old_opt in text, "old_opt not found"
text = text.replace(old_opt, new_opt, 1)

# 3. Circle samples capping
old_circ = "num_samples = max(24, int(2 * math.pi * r / resolution))"
new_circ = "num_samples = min(360, max(24, int(2 * math.pi * r / resolution)))"
assert old_circ in text, "old_circ not found"
text = text.replace(old_circ, new_circ, 1)

# 4. Arc samples capping
old_arc = "num_samples = max(2, int(arc_length / resolution))"
new_arc = "num_samples = min(180, max(4, int(arc_length / resolution)))"
assert old_arc in text, "old_arc not found"
text = text.replace(old_arc, new_arc) # Replace both occurrences

with open("dxf.py", "w", encoding="utf-8") as f:
    f.write(text)

print("dxf.py successfully updated!")

