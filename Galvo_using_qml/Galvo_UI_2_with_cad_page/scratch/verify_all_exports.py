import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ezdxf
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QApplication
import zxingcpp
from PIL import Image

app = QApplication(sys.argv)
from bridges.cad_bridge import CadBridge
bridge = CadBridge()

for code_type, text in [('qrcode', 'https://www.specialiseproducts.com'), ('barcode128', 'PKG-12345'), ('datamatrix', 'DM-67890')]:
    res = bridge.generateBarcodeEntity(code_type, text, 20.0)
    shp = {
        'name': f'Test_{code_type}',
        'type': code_type,
        'text': text,
        'wMm': res['wMm'],
        'hMm': res['hMm'],
        'rects': res['rects'],
        'paths': res['paths'],
        'hatched': False
    }
    for ext in ['dxf', 'svg', 'png']:
        out_file = f'test_export_{code_type}.{ext}'
        # Test export logic
        if ext == 'dxf':
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            for rc in shp['rects']:
                x0, y0 = rc['x'], rc['y'] - rc['h']
                x1, y1 = rc['x'] + rc['w'], rc['y']
                msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True)
            doc.saveas(out_file)
        elif ext == 'svg':
            w, h = shp['wMm'], shp['hMm']
            min_x = -w / 2.0
            min_y = -h / 2.0
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {w} {h}" width="{w}mm" height="{h}mm">\n')
                f.write(f'  <rect x="{min_x}" y="{min_y}" width="{w}" height="{h}" fill="white"/>\n')
                f.write('  <g fill="black">\n')
                for rc in shp['rects']:
                    rx, ry = rc['x'], -rc['y']
                    rw, rh = rc['w'], rc['h']
                    f.write(f'    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}"/>\n')
                f.write('  </g>\n</svg>\n')
        elif ext == 'png':
            w, h = shp['wMm'], shp['hMm']
            px_w = 1000
            px_h = max(200, int(1000 * (h / w)))
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
            img.save(out_file)
            
            # verify scan
            scanned = zxingcpp.read_barcodes(Image.open(out_file))
            print(f'PNG {code_type} scanned:', len(scanned), scanned[0].text if scanned else 'None')
        print(f'Saved {out_file}, size: {os.path.getsize(out_file)}')

