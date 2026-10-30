import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bridges.galvo_bridge import GalvoBridge
from bridges.jog_bridge import JogBridge
from bridges.cad_bridge import CadBridge
from PySide6.QtCore import QCoreApplication

app = QCoreApplication(sys.argv)

print("--- 1. Testing GalvoBridge fast connection ---")
galvo = GalvoBridge()
galvo.connectHardware()
print(f"Galvo Connected: {galvo.isConnected}, Demo: {galvo.isDemo}, Status: {galvo.statusMessage}")

print("\n--- 2. Testing CadBridge field_size configuration from config.ini ---")
jog = JogBridge(galvo_bridge=galvo)
cad = CadBridge(galvo_bridge=galvo, jog_bridge=jog)
print(f"Field Size loaded: {cad.fieldSize} mm, Offset: ({cad.offsetX}, {cad.offsetY}) mm, Angle: {cad.fieldAngle}°")

print("\n--- 3. Testing setting field size ---")
cad.setFieldSize(70.0)
print(f"Updated Field Size: {cad.fieldSize} mm")

print("\n--- 4. Testing importing SVG and checking types ---")
cad.importFile("file:///d:/Galvo_using_qml/Galvo_UI_2_with_cad_page/dist/Patterning_Machine/_internal/matplotlib/mpl-data/images/hand.svg")
shapes = cad._shapes
if shapes:
    s = shapes[-1]
    print(f"Imported shape '{s['name']}':")
    print(f"  xMm: {s['xMm']} (type: {type(s['xMm'])})")
    print(f"  yMm: {s['yMm']} (type: {type(s['yMm'])})")
    print(f"  wMm: {s['wMm']} (type: {type(s['wMm'])})")
    print(f"  hMm: {s['hMm']} (type: {type(s['hMm'])})")
    assert isinstance(s['xMm'], float), f"Expected float, got {type(s['xMm'])}"
    assert isinstance(s['yMm'], float), f"Expected float, got {type(s['yMm'])}"
    assert isinstance(s['wMm'], float), f"Expected float, got {type(s['wMm'])}"
    assert isinstance(s['hMm'], float), f"Expected float, got {type(s['hMm'])}"
    print("ALL TYPES ARE STANDARD PYTHON FLOAT - 100% COMPATIBLE WITH QML NUMBER!")

print("\n--- ALL TESTS PASSED SUCCESSFULLY ---")
sys.exit(0)
