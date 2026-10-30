import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ezdxf
from PySide6.QtGui import QImage, QPainter, QColor, QPen
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtWidgets import QApplication
import zxingcpp
from PIL import Image

app = QApplication(sys.argv)
from bridges.cad_bridge import CadBridge
bridge = CadBridge()
res = bridge.generateBarcodeEntity('qrcode', 'https://www.specialiseproducts.com', 20.0)
shp = {
    'name': 'QRCode_1',
    'type': 'qrcode',
    'text': 'https://www.specialiseproducts.com',
    'wMm': 20.0,
    'hMm': 20.0,
    'rects': res['rects'],
    'paths': res['paths'],
    'hatched': False
}

os.makedirs('test_exports', exist_ok=True)

# 1. DXF
doc = ezdxf.new('R2010')
msp = doc.modelspace()
for rc in shp['rects']:
    x0, y0 = rc['x'], rc['y'] - rc['h']
    x1, y1 = rc['x'] + rc['w'], rc['y']
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    msp.add_lwpolyline(pts, close=True)
dxf_path = os.path.join('test_exports', 'test_qr.dxf')
doc.saveas(dxf_path)
print('DXF saved, size:', os.path.getsize(dxf_path))

# 2. SVG
svg_path = os.path.join('test_exports', 'test_qr.svg')
w, h = shp['wMm'], shp['hMm']
min_x = -w / 2.0
min_y = -h / 2.0
with open(svg_path, 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {w} {h}" width="{w}mm" height="{h}mm">\n')
    f.write(f'  <rect x="{min_x}" y="{min_y}" width="{w}" height="{h}" fill="white"/>\n')
    f.write('  <g fill="black">\n')
    for rc in shp['rects']:
        rx, ry = rc['x'], -rc['y']
        rw, rh = rc['w'], rc['h']
        f.write(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}"/>\n')
    f.write('  </g>\n</svg>\n')
print('SVG saved, size:', os.path.getsize(svg_path))

# 3. PNG
png_path = os.path.join('test_exports', 'test_qr.png')
px_w = 800
px_h = 800
scale = px_w / w
img = QImage(px_w, px_h, QImage.Format_ARGB32)
img.fill(QColor('white'))
p = QPainter(img)
p.translate(px_w / 2.0, px_h / 2.0)
for rc in shp['rects']:
    rx, ry = rc['x'] * scale, -rc['y'] * scale
    rw, rh = rc['w'] * scale, rc['h'] * scale
    p.fillRect(QRectF(rx, ry, rw + 0.5, rh + 0.5), QColor('#0A0F1D'))
p.end()
img.save(png_path)
print('PNG saved, size:', os.path.getsize(png_path))

# Verify PNG scanning
scanned = zxingcpp.read_barcodes(Image.open(png_path))
print('PNG zxing scan count:', len(scanned))
if scanned:
    print('Scanned content:', scanned[0].text)
