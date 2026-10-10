import struct

def interp1d(x, W, v_neg, v_0, v_pos):
    """Quadratic interpolation for 3 points: -W, 0, W"""
    if W == 0: return v_0
    a = (v_pos + v_neg - 2 * v_0) / (2.0 * W * W)
    b = (v_pos - v_neg) / (2.0 * W)
    return a * (x**2) + b * x + v_0

def interp2d(x, y, W_x, W_y, v_grid):
    """
    Biquadratic interpolation.
    v_grid is a 3x3 array:
    [[v_top_left, v_top_mid, v_top_right],
     [v_mid_left, v_center,  v_mid_right],
     [v_bot_left, v_bot_mid, v_bot_right]]
    """
    v_top = interp1d(x, W_x, v_grid[0][0], v_grid[0][1], v_grid[0][2])
    v_mid = interp1d(x, W_x, v_grid[1][0], v_grid[1][1], v_grid[1][2])
    v_bot = interp1d(x, W_x, v_grid[2][0], v_grid[2][1], v_grid[2][2])
    
    return interp1d(y, W_y, v_bot, v_mid, v_top)

def generate_cor_file(output_path, scale, W, measured_points):
    """
    Generates a .cor file from 9 measured points.
    measured_points: List of 9 tuples (Mx, My) representing the measured 
                     physical coordinates for the 9 ideal points.
    W: the absolute distance of the 9 points from the center in physical units (e.g., 50mm)
    scale: bits per mm scale factor (e.g., 533.89)
    """
    # Define ideal points T_x and T_y
    T_x = [-W, 0, W,
           -W, 0, W,
           -W, 0, W]
    
    T_y = [ W,  W,  W,
            0,  0,  0,
           -W, -W, -W]
           
    # Calculate error in galvo units (M - T) * scale
    error_x_grid = [
        [(measured_points[0][0] - T_x[0])*scale, (measured_points[1][0] - T_x[1])*scale, (measured_points[2][0] - T_x[2])*scale],
        [(measured_points[3][0] - T_x[3])*scale, (measured_points[4][0] - T_x[4])*scale, (measured_points[5][0] - T_x[5])*scale],
        [(measured_points[6][0] - T_x[6])*scale, (measured_points[7][0] - T_x[7])*scale, (measured_points[8][0] - T_x[8])*scale],
    ]
    
    error_y_grid = [
        [(measured_points[0][1] - T_y[0])*scale, (measured_points[1][1] - T_y[1])*scale, (measured_points[2][1] - T_y[2])*scale],
        [(measured_points[3][1] - T_y[3])*scale, (measured_points[4][1] - T_y[4])*scale, (measured_points[5][1] - T_y[5])*scale],
        [(measured_points[6][1] - T_y[6])*scale, (measured_points[7][1] - T_y[7])*scale, (measured_points[8][1] - T_y[8])*scale],
    ]
    
    grid = []
    # 65x65 grid of 32-bit signed integer deltas
    for r in range(65):
        row = []
        # Galvo commands
        x_cmd = r * 1024
        # physical ideal X
        ideal_x = (x_cmd - 32768) / scale
        
        for c in range(65):
            y_cmd = c * 1024
            ideal_y = (y_cmd - 32768) / scale
            
            # Interpolate error
            dx = interp2d(ideal_x, ideal_y, W, W, error_x_grid)
            dy = interp2d(ideal_x, ideal_y, W, W, error_y_grid)
            
            row.append((int(dx), int(dy)))
        grid.append(row)
        
    # Build binary file
    # 40 byte header
    header = bytearray(40)
    signature = b"JCZ_COR_2_1\0"
    header[0:len(signature)] = signature
    
    # Scale factor at offset 28
    struct.pack_into('d', header, 28, scale)
    
    with open(output_path, 'wb') as f:
        f.write(header)
        for r in range(65):
            for c in range(65):
                f.write(struct.pack('<ii', grid[r][c][0], grid[r][c][1]))
