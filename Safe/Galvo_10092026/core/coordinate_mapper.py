import math

class CoordinateConfig:
    def __init__(self):
        # Base Configuration
        self.field_size = 100.0  # mm
        self.offset_x = 0.0      # mm
        self.offset_y = 0.0      # mm
        self.angle = 0.0         # Degrees
        
        # Hardware Axis Mapping (True if Galvo 1 = X)
        self.galvo_1_is_x = True
        
        # Galvo 1 configuration
        self.g1_negate = False
        self.g1_scale = 100.0     # Percentage
        self.g1_bulge = 1.0
        self.g1_skew = 1.0
        self.g1_trapezoid = 1.0
        
        # Galvo 2 configuration
        self.g2_negate = False
        self.g2_scale = 100.0     # Percentage
        self.g2_bulge = 1.0
        self.g2_skew = 1.0
        self.g2_trapezoid = 1.0
        
    def apply_transform(self, x_mm, y_mm):
        """
        Takes raw mm coordinates (where 0,0 is center of the design),
        and applies the affine hardware configuration pipeline to convert them
        to absolute Galvo integer units (0 to 65535).
        """
        # 1. Rotate
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        x_rot = x_mm * cos_a - y_mm * sin_a
        y_rot = x_mm * sin_a + y_mm * cos_a
        
        # 2. Translate (Offset)
        x_mm = x_rot + self.offset_x
        y_mm = y_rot + self.offset_y
        
        # Convert mm to abstract normalized space (-1.0 to 1.0)
        # where field_size corresponds to the full width (-0.5 to 0.5 of field_size)
        norm_x = x_mm / (self.field_size / 2.0)
        norm_y = y_mm / (self.field_size / 2.0)
        
        # Map to Galvo 1 and Galvo 2 logical axes
        if self.galvo_1_is_x:
            g1, g2 = norm_x, norm_y
        else:
            g1, g2 = norm_y, norm_x
            
        # 3. Scale & Negate
        g1 = g1 * (self.g1_scale / 100.0)
        g2 = g2 * (self.g2_scale / 100.0)
        if self.g1_negate: g1 = -g1
        if self.g2_negate: g2 = -g2
        
        # 4. Distortions (Trapezoid, Skew, Bulge)
        # Applying a basic polynomial approximation for these corrections
        # Bulge: barrel/pincushion distortion (radial)
        # Trapezoid: changes scale of one axis based on the other
        # Skew: linear shear
        
        # Galvo 1 Corrections
        g1_orig = g1
        g2_orig = g2
        
        # Parallelogram (Skew)
        g1_adj = g1 + g2 * (self.g1_skew - 1.0)
        # Trapezoid
        g1_adj = g1_adj * (1.0 + g2 * (self.g1_trapezoid - 1.0))
        # Bulge (Barrel/Pincushion)
        r2 = g1*g1 + g2*g2
        g1_adj = g1_adj * (1.0 + r2 * (self.g1_bulge - 1.0))
        
        # Galvo 2 Corrections
        # Parallelogram (Skew)
        g2_adj = g2 + g1_orig * (self.g2_skew - 1.0)
        # Trapezoid
        g2_adj = g2_adj * (1.0 + g1_orig * (self.g2_trapezoid - 1.0))
        # Bulge (Barrel/Pincushion)
        g2_adj = g2_adj * (1.0 + r2 * (self.g2_bulge - 1.0))
        
        # Convert to Galvo units (0 to 65535, where 0 is -1.0 and 65535 is +1.0)
        # Actually in normalized space: -1.0 -> 0, 0.0 -> 32767, 1.0 -> 65535
        # So galvo_units = 32767 + (g * 32767)
        galvo_g1 = int(32767 + (g1_adj * 32767))
        galvo_g2 = int(32767 + (g2_adj * 32767))
        
        # Clamp bounds
        galvo_g1 = max(0, min(65535, galvo_g1))
        galvo_g2 = max(0, min(65535, galvo_g2))
        
        # Axis Mapping (Re-assemble as X and Y outputs for controller)
        # The controller expects galvo_move_xy(x, y). 
        # If galvo_1 is mapped to X hardware channel, and galvo_2 to Y:
        # We output X = galvo_g1, Y = galvo_g2
        if self.galvo_1_is_x:
            return galvo_g1, galvo_g2
        else:
            return galvo_g2, galvo_g1

    def reverse_transform(self, galvo_x, galvo_y):
        """
        Reverse transform is an approximation, primarily useful for UI preview plotting.
        Non-linear distortions (bulge, trapezoid) make perfect reversal complex, 
        so we do a simple inverse of the linear affine transforms for now.
        """
        if self.galvo_1_is_x:
            galvo_g1, galvo_g2 = galvo_x, galvo_y
        else:
            galvo_g2, galvo_g1 = galvo_x, galvo_y
            
        g1 = (galvo_g1 - 32767) / 32767.0
        g2 = (galvo_g2 - 32767) / 32767.0
        
        if self.g1_negate: g1 = -g1
        if self.g2_negate: g2 = -g2
        g1 = g1 / (self.g1_scale / 100.0)
        g2 = g2 / (self.g2_scale / 100.0)
        
        if self.galvo_1_is_x:
            norm_x, norm_y = g1, g2
        else:
            norm_x, norm_y = g2, g1
            
        x_mm = norm_x * (self.field_size / 2.0)
        y_mm = norm_y * (self.field_size / 2.0)
        
        x_mm -= self.offset_x
        y_mm -= self.offset_y
        
        rad = math.radians(-self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        x_orig = x_mm * cos_a - y_mm * sin_a
        y_orig = x_mm * sin_a + y_mm * cos_a
        
        return x_orig, y_orig

# Backwards compatibility wrappers
def mm_to_galvo(mm, field_size=100):
    center_galvo = 32767
    scale = 65535 / field_size
    val = int(center_galvo + (mm * scale))
    return max(0, min(65535, val))

def galvo_to_mm(galvo_val, field_size=100):
    center_galvo = 32767
    scale = field_size / 65535
    return (galvo_val - center_galvo) * scale
