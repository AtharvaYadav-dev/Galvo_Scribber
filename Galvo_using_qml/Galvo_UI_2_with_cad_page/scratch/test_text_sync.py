import sys, os
sys.path.insert(0, os.path.abspath('.'))
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QTimer

app = QApplication.instance() or QApplication(sys.argv)
engine = QQmlApplicationEngine()

from bridges.cad_bridge import CadBridge
from bridges.settings_bridge import SettingsBridge
from bridges.galvo_bridge import GalvoBridge

cad_bridge = CadBridge()
settings_bridge = SettingsBridge()
galvo_bridge = GalvoBridge()

engine.rootContext().setContextProperty('cad', cad_bridge)
engine.rootContext().setContextProperty('settingsBridge', settings_bridge)
engine.rootContext().setContextProperty('galvoBridge', galvo_bridge)

qml_file = os.path.join(os.getcwd(), 'qml', 'main.qml')
engine.load(QUrl.fromLocalFile(qml_file))

win = engine.rootObjects()[0]
win.show()

def test_workflow():
    cad_canvas = win.findChild(object, 'cadCanvas')
    if cad_canvas:
        # Simulate generating text entity
        shp_dict = {
            'text': 'TEXT',
            'fontFamily': 'Segoe UI',
            'hMm': 4.0,
            'fontType': 'TrueType Font',
            'bold': False,
            'italic': False,
            'textAlign': 'center',
            'xMm': 0.0,
            'yMm': 0.0,
            'rotation': 0.0
        }
        res_polys = cad_bridge._shape_to_polygons(shp_dict)
        all_pts = [pt for p in res_polys for pt in p]
        w_mm = round(max(p[0] for p in all_pts) - min(p[0] for p in all_pts), 2)
        h_mm = 4.0

        new_text = {
            'id': 1,
            'name': 'Text_1',
            'type': 'text',
            'text': 'TEXT',
            'xMm': 0,
            'yMm': 0,
            'wMm': w_mm,
            'hMm': h_mm,
            'rotation': 0,
            'fontFamily': 'Segoe UI',
            'fontType': 'TrueType Font',
            'textAlign': 'center',
            'charSpace': 0.0,
            'lineSpace': 0.0,
            'bold': False,
            'italic': False,
            'penId': 0,
            'hatched': False,
            'visible': True,
            'locked': False,
            'paths': res_polys
        }
        cad_canvas.setProperty('shapes', [new_text])
        cad_canvas.setProperty('selectedIndex', 0)
        from PySide6.QtCore import QMetaObject
        QMetaObject.invokeMethod(cad_canvas, 'requestPaint')

    def save_snap():
        img = win.grabWindow()
        out = r'C:\Users\EXPRESS\.gemini\antigravity\brain\328857d1-baaf-4ad3-b256-4642e0d259d6\screen_with_paths_text.png'
        img.save(out)
        print('Saved screenshot to', out)
        app.quit()

    QTimer.singleShot(400, save_snap)

QTimer.singleShot(600, test_workflow)
app.exec()

