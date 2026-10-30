import sys, os
_root = r'd:\Galvo_using_qml\Galvo_UI_2_with_cad_page'
sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from bridges.cad_bridge import CadBridge
from bridges.settings_bridge import SettingsBridge

app = QApplication.instance() or QApplication(sys.argv)

cad = CadBridge()
settings = SettingsBridge(cad_bridge=cad)

print("=== 1. Testing Bridge Config & Signals ===")
signals_received = []

def on_field_settings(f, x, y, a):
    signals_received.append(('fieldSettings', f, x, y, a))

def on_field_size(f):
    signals_received.append(('fieldSize', f))

def on_advanced():
    signals_received.append(('advanced',))

cad.fieldSettingsChanged.connect(on_field_settings)
cad.fieldSizeChanged.connect(on_field_size)
settings.advancedConfigChanged.connect(on_advanced)

print(f"Initial CadBridge: field_size={cad.fieldSize}, off=({cad.offsetX}, {cad.offsetY}), ang={cad.fieldAngle}")

# Simulate Config Page user change: field_size=110, off_x=12.5, off_y=-8.0, ang=30.0, g1_scale=98.5
settings.saveFullConfigGalvo(
    110.0, 12.5, -8.0, 30.0, False,
    False, 98.5, 1.0, 1.0, 1.0,
    False, 101.2, 1.0, 1.0, 1.0,
    'confgalvocent', 0.0, 0.0
)

print(f"After Config Save: field_size={cad.fieldSize}, off=({cad.offsetX}, {cad.offsetY}), ang={cad.fieldAngle}, G1Scale={cad.g1Scale}")
assert cad.fieldSize == 110.0, 'fieldSize not updated'
assert cad.offsetX == 12.5, 'offsetX not updated'
assert cad.offsetY == -8.0, 'offsetY not updated'
assert cad.fieldAngle == 30.0, 'fieldAngle not updated'
assert cad.g1Scale == 98.5, 'g1Scale not updated'
assert len(signals_received) >= 2, 'Signals not emitted'
print("Bridge config sync passed!")

print("\n=== 2. Testing File Import & Framing with Rotated/Offset Bed ===")
sample_file = os.path.join(_root, 'svg_files', '250 39mmsizeMicron channel.svg')
if not os.path.exists(sample_file):
    for f in os.listdir(os.path.join(_root, 'svg_files')):
        if f.endswith('.svg') or f.endswith('.dxf'):
            sample_file = os.path.join(_root, 'svg_files', f)
            break

print(f"Testing with file: {sample_file}")
imported_shapes = []
cad.shapesImported.connect(lambda shps: imported_shapes.extend(shps))
cad.importFile(sample_file)

assert len(imported_shapes) > 0, 'No shapes imported'
shp = imported_shapes[0]
name = shp.get("name")
w = shp.get("wMm")
h = shp.get("hMm")
paths_cnt = len(shp.get("paths", []))
print(f"Imported shape: name='{name}', size={w}x{h}mm, paths={paths_cnt}")

print("\n=== 3. Testing 4-Corner Transformed Framing ===")
cad.toggleFraming(imported_shapes)
assert cad.isFraming, 'Framing should be active in simulation'
print(f"Framing status: {cad.statusMessage}")
cad.toggleFraming()
assert not cad.isFraming, 'Framing should be stopped'

print("\n=== 4. Testing Execute Mark Simulation ===")
cad.executeMark(imported_shapes)
assert cad.isMarking, 'Marking should be active in simulation'
print(f"Marking status: {cad.statusMessage}")
cad.abortMark()
assert not cad.isMarking, 'Marking aborted'

print("\n=== 5. Testing Reimport Last File ===")
assert cad._last_imported_path == sample_file
reimported = []
cad.shapesImported.connect(lambda shps: reimported.extend(shps))
cad.reimportLastFile()
assert len(reimported) > 0, 'Reimport failed'
print("Reimport successfully executed!")

# Restore clean 70mm lens settings
settings.saveFullConfigGalvo(
    70.0, 0.0, 0.0, 0.0, False,
    False, 100.0, 1.0, 1.0, 1.0,
    False, 100.0, 1.0, 1.0, 1.0,
    'confgalvocent', 0.0, 0.0
)

print("\nALL BACKEND & CONFIG INTEGRATION TESTS PASSED!")
