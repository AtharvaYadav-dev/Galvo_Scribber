import os
import sys
import unittest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from bridges.cad_bridge import CadBridge

class TestTextAndSidebar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.cad = CadBridge()

    def test_available_fonts(self):
        fonts = self.cad.availableFonts
        self.assertGreater(len(fonts), 10)
        self.assertIn("Simplex (Single-Stroke Vector)", fonts)
        self.assertIn("Arial", fonts)
        print(f"Total Available Fonts: {len(fonts)}")

    def test_measure_text(self):
        res = self.cad.measureText("EZCAD", "Arial", 5.0, False, False)
        self.assertIn("wMm", res)
        self.assertIn("hMm", res)
        self.assertGreater(res["wMm"], 5.0)
        self.assertEqual(res["hMm"], 5.0)
        print(f"Measure Text 'EZCAD': {res}")

    def test_truetype_text_polygons(self):
        text_shp = {
            "id": 1,
            "name": "Text_1",
            "type": "text",
            "text": "LASER",
            "fontFamily": "Segoe UI",
            "fontType": "TrueType Font",
            "xMm": 0.0,
            "yMm": 0.0,
            "wMm": 25.0,
            "hMm": 6.0,
            "bold": True,
            "italic": False,
            "charSpace": 0.5,
            "lineSpace": 0.0,
            "rotation": 0.0,
            "visible": True
        }
        polys = self.cad._shape_to_polygons(text_shp)
        self.assertGreater(len(polys), 0)
        print(f"TrueType text generated {len(polys)} closed outline polygons.")

    def test_simplex_single_stroke_text(self):
        simplex_shp = {
            "id": 2,
            "name": "Text_Simplex",
            "type": "text",
            "text": "12345",
            "fontFamily": "Simplex (Single-Stroke Vector)",
            "fontType": "Single-Stroke (Hershey)",
            "xMm": 0.0,
            "yMm": 0.0,
            "wMm": 15.0,
            "hMm": 4.0,
            "visible": True
        }
        polys = self.cad._shape_to_polygons(simplex_shp)
        self.assertGreater(len(polys), 0)
        print(f"Simplex single-stroke generated {len(polys)} stroke paths.")

    def test_circle_text(self):
        circle_shp = {
            "id": 3,
            "name": "Text_Circle",
            "type": "text",
            "text": "CIRCULAR",
            "fontFamily": "Arial",
            "circleText": True,
            "circleDiameter": 25.0,
            "circleBaseAngle": 90.0,
            "xMm": 0.0,
            "yMm": 0.0,
            "hMm": 3.5,
            "visible": True
        }
        polys = self.cad._shape_to_polygons(circle_shp)
        self.assertGreater(len(polys), 0)
        print(f"CircleText generated {len(polys)} curved outline polygons.")

    def test_variable_text(self):
        var_shp = {
            "id": 4,
            "name": "Text_Var",
            "type": "text",
            "enableVariableText": True,
            "variableEntities": [
                {"type": "fixed", "text": "BATCH_"},
                {"type": "serial", "current": 100, "step": 1, "digits": 4}
            ],
            "fontFamily": "Arial",
            "xMm": 0.0,
            "yMm": 0.0,
            "hMm": 5.0,
            "visible": True
        }
        polys = self.cad._shape_to_polygons(var_shp)
        self.assertGreater(len(polys), 0)
        # Verify serial counter incremented
        self.assertEqual(var_shp["variableEntities"][1]["current"], 101)
        print("Variable text with auto-increment serial generated and incremented to 101 successfully.")

    def test_array_replication(self):
        base_shp = {
            "id": 10,
            "name": "BaseText",
            "type": "text",
            "text": "ITEM",
            "xMm": 0.0,
            "yMm": 0.0,
            "wMm": 10.0,
            "hMm": 4.0
        }
        clones = self.cad.applyArray(base_shp, count_x=2, count_y=3, inc_x_mm=12.0, inc_y_mm=8.0)
        self.assertEqual(len(clones), 5) # 2*3 - 1 = 5 new clones
        # Check coordinates of the furthest clone
        last_clone = clones[-1]
        self.assertEqual(last_clone["xMm"], 12.0)
        self.assertEqual(last_clone["yMm"], 16.0)
        print(f"Array replication generated {len(clones)} clones with correct grid coordinates.")

    def test_text_hatching(self):
        hatch_shp = {
            "id": 20,
            "name": "HatchedText",
            "type": "text",
            "text": "MARK",
            "fontFamily": "Segoe UI",
            "xMm": 0.0,
            "yMm": 0.0,
            "wMm": 20.0,
            "hMm": 5.0,
            "hatched": True,
            "penId": 0
        }
        lines = self.cad.computeHatchPreviewLines(hatch_shp)
        self.assertGreater(len(lines), 0)
        print(f"Text infill hatching generated {len(lines)} hatch vectors.")

if __name__ == "__main__":
    unittest.main()
