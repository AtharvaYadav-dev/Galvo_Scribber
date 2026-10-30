import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from machine.galvo_controller import GalvoController
from machine.stepper_controller import StepperController
from rotary_page import RotaryMarkingPage
from rotary_slicer import RotarySlicingEngine

app = QApplication.instance() or QApplication([])

galvo = GalvoController()
galvo.connect(force_mock=True)
stepper = StepperController(galvo.connection)

page = RotaryMarkingPage(galvo_controller=galvo, stepper_controller=stepper)
page.tabs.setCurrentIndex(1)
page.spn_top_diameter.setValue(25.0)
page.on_generate_scale_ruler(append=False)

bounds = RotarySlicingEngine.get_artwork_bounds(page.raw_paths)
print("Artwork bounds:", bounds)
print("Y span:", bounds[3] - bounds[1])
print("Circumference:", page.config.circumference)

print("\nAll slices:")
for sl in page.slices:
    print(f"Slice {sl.slice_index}: bounds={sl.bounds_orig}, center={sl.center_orig:.3f}, delta_dist={sl.delta_distance_mm:.3f}, pulses={sl.step_pulses}")

