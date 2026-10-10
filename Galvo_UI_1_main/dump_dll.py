import re
import os

dll_path = "gt5motion_GT.dll"

if not os.path.exists(dll_path):
    print("DLL not found!")
    exit(1)

with open(dll_path, "rb") as f:
    content = f.read()

# Find all ASCII strings starting with GT_ or gt_
matches = re.findall(b'(GT_[a-zA-Z0-9_]+)', content, re.IGNORECASE)

unique_funcs = sorted(list(set([m.decode('ascii') for m in matches])))

print("Found the following GT_ functions in the DLL:")
for func in unique_funcs:
    print(func)
