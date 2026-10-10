import re

with open('core/calibration.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_interp = r"""        # Retrieve the four surrounding grid points\n        v00 = self\.grid\[row\]\[col\]\n        v10 = self\.grid\[row\]\[col\+1\]\n        v01 = self\.grid\[row\+1\]\[col\]\n        v11 = self\.grid\[row\+1\]\[col\+1\]\n        \n        # Interpolate X offset\n        top_x = v00\[0\] \+ dx \* \(v10\[0\] - v00\[0\]\)\n        bot_x = v01\[0\] \+ dx \* \(v11\[0\] - v01\[0\]\)\n        interp_delta_x = top_x \+ dy \* \(bot_x - top_x\)\n        \n        # Interpolate Y offset\n        top_y = v00\[1\] \+ dx \* \(v10\[1\] - v00\[1\]\)\n        bot_y = v01\[1\] \+ dx \* \(v11\[1\] - v01\[1\]\)\n        interp_delta_y = top_y \+ dy \* \(bot_y - top_y\)"""

new_interp = r"""        # Retrieve the four surrounding grid points
        v00 = self.grid[row][col]
        v10 = self.grid[row+1][col]  # x+1, y
        v01 = self.grid[row][col+1]  # x, y+1
        v11 = self.grid[row+1][col+1] # x+1, y+1
        
        # Interpolate X offset
        bot_x = v00[0] + dx * (v10[0] - v00[0])
        top_x = v01[0] + dx * (v11[0] - v01[0])
        interp_delta_x = bot_x + dy * (top_x - bot_x)
        
        # Interpolate Y offset
        bot_y = v00[1] + dx * (v10[1] - v00[1])
        top_y = v01[1] + dx * (v11[1] - v01[1])
        interp_delta_y = bot_y + dy * (top_y - bot_y)"""

content = re.sub(old_interp, new_interp, content)

with open('core/calibration.py', 'w', encoding='utf-8') as f:
    f.write(content)
