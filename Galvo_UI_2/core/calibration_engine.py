import json
import os

class NinePointCalibration:
    def __init__(self, w, measurements):
        self.w = float(w)
        self.measurements = measurements
        self.is_valid = True
        self.scale = 533.89  # Added for backwards compatibility with main.py

    def apply(self, hx, hy):
        scale = self.scale
        c = 32767
        
        # Convert to nominal physical mm
        x_nom = (hx - c) / scale
        y_nom = (hy - c) / scale
        
        if abs(x_nom) < 1e-6 and abs(y_nom) < 1e-6:
            return c, c
            
        # Determine quadrant
        if x_nom >= 0 and y_nom >= 0:
            idx_x, idx_y, idx_xy = 5, 1, 2
        elif x_nom < 0 and y_nom >= 0:
            idx_x, idx_y, idx_xy = 3, 1, 0
        elif x_nom < 0 and y_nom < 0:
            idx_x, idx_y, idx_xy = 3, 7, 6
        else:
            idx_x, idx_y, idx_xy = 5, 7, 8
            
        u = max(0.0, min(1.0, abs(x_nom) / self.w))
        v = max(0.0, min(1.0, abs(y_nom) / self.w))
        
        # X interpolation
        m_x00 = self.measurements[4][0]
        m_x10 = self.measurements[idx_x][0]
        m_x01 = self.measurements[idx_y][0]
        m_x11 = self.measurements[idx_xy][0]
        
        bot_x = m_x00 + u * (m_x10 - m_x00)
        top_x = m_x01 + u * (m_x11 - m_x01)
        interp_meas_x = bot_x + v * (top_x - bot_x)
        
        # Y interpolation
        m_y00 = self.measurements[4][1]
        m_y10 = self.measurements[idx_x][1]
        m_y01 = self.measurements[idx_y][1]
        m_y11 = self.measurements[idx_xy][1]
        
        bot_y = m_y00 + u * (m_y10 - m_y00)
        top_y = m_y01 + u * (m_y11 - m_y01)
        interp_meas_y = bot_y + v * (top_y - bot_y)
        
        if abs(interp_meas_x) > 1e-6 and abs(x_nom) > 1e-6:
            x_cmd = x_nom * (x_nom / interp_meas_x)
        else:
            x_cmd = x_nom
            
        if abs(interp_meas_y) > 1e-6 and abs(y_nom) > 1e-6:
            y_cmd = y_nom * (y_nom / interp_meas_y)
        else:
            y_cmd = y_nom
            
        hx_out = c + x_cmd * scale
        hy_out = c + y_cmd * scale
        
        # Clamp to valid DAC range
        hx_out = max(0, min(65535, int(round(hx_out))))
        hy_out = max(0, min(65535, int(round(hy_out))))
        
        return hx_out, hy_out
        
    def save(self, filepath):
        with open(filepath, 'w') as f:
            json.dump({'w': self.w, 'measurements': self.measurements}, f)
            
    @classmethod
    def load(cls, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(data['w'], data['measurements'])
