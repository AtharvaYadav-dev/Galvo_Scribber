import math
try:
    from PIL import Image
except ImportError:
    print("Pillow is required for image parsing.")
    Image = None

class ImageParser:
    def __init__(self, field_size=100):
        self.field_size = field_size

    def parse_to_polygons(self, filepath, pixel_size_mm=0.1, dither=True, threshold=128, invert=False):
        """
        Parses an image and returns a list of polygons (horizontal scanlines).
        """
        if Image is None:
            print("Cannot parse image: PIL/Pillow is not installed.")
            return []
            
        try:
            img = Image.open(filepath)
            if dither:
                # Convert to 1-bit with dithering for smooth shading
                img = img.convert('1')
            else:
                img = img.convert('L')
        except Exception as e:
            print(f"Error opening image {filepath}: {e}")
            return []
            
        width, height = img.size
        
        # Scale to fit field size if too large
        max_dim = max(width * pixel_size_mm, height * pixel_size_mm)
        if max_dim > self.field_size:
            pixel_size_mm = self.field_size / max(width, height)
            
        pixels = img.load()
        polygons = []
        
        for y in range(height):
            segments = []
            in_line = False
            start_x = 0
            # Image Y goes down, but Galvo Cartesian Y goes up. Invert Y.
            y_mm = -y * pixel_size_mm
            
            for x in range(width):
                val = pixels[x, y]
                # In 1-bit mode, 0 is black, 255 is white
                # In L mode, 0 is black, 255 is white
                is_dark = val < threshold if not invert else val >= threshold
                
                if is_dark and not in_line:
                    in_line = True
                    start_x = x
                elif not is_dark and in_line:
                    in_line = False
                    end_x = x
                    segments.append([(start_x * pixel_size_mm, y_mm), (end_x * pixel_size_mm, y_mm)])
                    
            if in_line:
                end_x = width
                segments.append([(start_x * pixel_size_mm, y_mm), (end_x * pixel_size_mm, y_mm)])
                
            # Bidirectional raster optimization
            if y % 2 != 0:
                segments.reverse()
                for seg in segments:
                    seg.reverse()
                    
            polygons.extend(segments)
            
        return polygons
