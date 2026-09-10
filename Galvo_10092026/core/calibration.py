import os
import struct

class GalvoCalibration:
    def __init__(self, config_path="newest100mm.cor"):
        self.config_path = config_path
        self.grid = None  # Will hold 65x65 grid of (dx, dy)
        self.is_valid = False
        self.scale = None
        
        self.load_calibration(config_path)

    def load_calibration(self, file_path=None):
        if file_path:
            self.config_path = file_path
            
        if os.path.exists(self.config_path) and self.config_path.lower().endswith(".cor"):
            try:
                self.grid = self._parse_cor_file(self.config_path)
                self.is_valid = True
            except Exception as e:
                print(f"Failed to load binary calibration data: {e}")
                self.is_valid = False
        else:
            self.is_valid = False

    def _parse_cor_file(self, filepath):
        grid = []
        with open(filepath, 'rb') as f:
            # Read 40-byte header
            header = f.read(40)
            if b"JCZ_COR" not in header:
                print("Warning: File does not contain standard JCZ_COR signature.")
            
            # Extract scale factor (Double / 8 bytes at offset 28)
            try:
                self.scale = struct.unpack('d', header[28:36])[0]
            except Exception as e:
                print(f"Could not extract scale from header: {e}")
                self.scale = None
            
            # Read 65x65 Grid of 32-bit signed integer deltas
            for row in range(65):
                row_data = []
                for col in range(65):
                    binary_point = f.read(8)
                    if len(binary_point) < 8:
                        # Fallback if file is truncated
                        dx, dy = 0, 0
                    else:
                        dx, dy = struct.unpack('<ii', binary_point)
                    row_data.append((dx, dy))
                grid.append(row_data)
        return grid

    def apply(self, x, y):
        """
        Applies a 65x65 bilinear interpolation grid correction to raw theoretical coordinates.
        Expects x and y in unsigned 16-bit galvo range (0 to 65535).
        """
        if not self.is_valid or not self.grid:
            return x, y
            
        # Map 0-65535 to 0-64 grid index
        fx = x / 1024.0
        fy = y / 1024.0
        
        # Clamp bounds
        if fx < 0: fx = 0.0
        if fx > 63.999: fx = 63.999
        if fy < 0: fy = 0.0
        if fy > 63.999: fy = 63.999
        
        row = int(fx)  # X axis maps to outer array
        col = int(fy)  # Y axis maps to inner array
        
        dx = fx - row
        dy = fy - col
        
        # Retrieve the four surrounding grid points
        v00 = self.grid[row][col]
        v10 = self.grid[row][col+1]
        v01 = self.grid[row+1][col]
        v11 = self.grid[row+1][col+1]
        
        # Interpolate X offset
        top_x = v00[0] + dx * (v10[0] - v00[0])
        bot_x = v01[0] + dx * (v11[0] - v01[0])
        interp_delta_x = top_x + dy * (bot_x - top_x)
        
        # Interpolate Y offset
        top_y = v00[1] + dx * (v10[1] - v00[1])
        bot_y = v01[1] + dx * (v11[1] - v01[1])
        interp_delta_y = top_y + dy * (bot_y - top_y)
        
        # The .cor offsets represent the measured error, so we subtract them from the target
        final_x = x - interp_delta_x
        final_y = y - interp_delta_y
        
        # Clamp to valid DAC range (assuming 0-65535, though the DLL handles ints)
        if final_x < 0: final_x = 0
        if final_x > 65535: final_x = 65535
        if final_y < 0: final_y = 0
        if final_y > 65535: final_y = 65535
        
        return final_x, final_y
