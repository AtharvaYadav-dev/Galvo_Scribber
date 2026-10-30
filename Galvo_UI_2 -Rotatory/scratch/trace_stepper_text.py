import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotary_slicer import RotarySlicingEngine, RotaryConfig

cfg = RotaryConfig()
cfg.diameter = 25.0
cfg.pulses_per_rev = 6400
cfg.gear_ratio = 1.0
cfg.split_size = 1.0

text_paths = RotarySlicingEngine.generate_vector_text(
    text="EZCAD ROTARY PRO",
    diameter=25.0,
    auto_fit_360=True,
    axial_length=50.0
)

engine = RotarySlicingEngine(cfg)
slices, stats = engine.slice_artwork(text_paths, cfg)

total_stepped_pulses = sum(s.step_pulses for s in slices)
total_stepped_dist = sum(s.delta_distance_mm for s in slices)
print(f"Direct Text Circumference: {cfg.circumference:.4f} mm")
print(f"Total 360 pulses: {cfg.total_pulses_360}")
print(f"Number of slices: {len(slices)}")
print(f"Slice 0: center={slices[0].center_orig:.4f}, delta_dist={slices[0].delta_distance_mm:.4f}, pulses={slices[0].step_pulses}")
print(f"Slice -1: center={slices[-1].center_orig:.4f}, delta_dist={slices[-1].delta_distance_mm:.4f}, pulses={slices[-1].step_pulses}")

print(f"\nTOTAL STEPPED PULSES: {total_stepped_pulses}")
print(f"TOTAL STEPPED DISTANCE: {total_stepped_dist:.4f} mm")
print(f"DEGREES ROTATED: {(total_stepped_dist / cfg.circumference) * 360.0:.2f} deg")

