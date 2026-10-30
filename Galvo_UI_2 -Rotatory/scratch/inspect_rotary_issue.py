import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rotary_slicer import RotarySlicingEngine, RotaryConfig
from rotary_page import RotaryMarkingPage

# Test 1: Scale Ruler
d = 25.0
c = math.pi * d
ruler_paths = RotarySlicingEngine.generate_editable_ruler(
    diameter=d,
    minor_step=1.0,
    medium_step=5.0,
    major_step=10.0,
    minor_len=2.5,
    medium_len=4.5,
    major_len=7.0,
    axial_length=50.0,
    tick_side='left',
    include_baseline=True,
    include_numbers=False,
    direction='circumferential'
)

print(f"Ruler paths count: {len(ruler_paths)}")
min_x, min_y, max_x, max_y = RotarySlicingEngine.get_artwork_bounds(ruler_paths)
print(f"Ruler bounds: X[{min_x:.3f}, {max_x:.3f}], Y[{min_y:.3f}, {max_y:.3f}], Span Y={max_y - min_y:.3f}, Expected C={c:.3f}")

# Check ticks near 0 and 360
ticks_y = [p[0][1] for p in ruler_paths if len(p) == 2 and p[0][0] != p[1][0]]
print(f"Number of ticks: {len(ticks_y)}")
print(f"First 5 tick Y: {ticks_y[:5]}")
print(f"Last 5 tick Y: {ticks_y[-5:]}")
print(f"Is there tick at 0.0? {0.0 in ticks_y}")
print(f"Is there tick at C ({c:.3f})? {any(abs(y - c) < 1e-3 for y in ticks_y)}")

# Test 2: Direct Text
text_paths = RotarySlicingEngine.generate_vector_text(
    text="EZCAD ROTARY PRO",
    font_family="Arial",
    font_size_mm=4.0,
    bold=True,
    italic=False,
    letter_spacing_mm=0.5,
    orientation='circumferential',
    angle_deg=0.0,
    diameter=d,
    repeat_count=1,
    auto_fit_360=True
)
print(f"\nDirect text paths count: {len(text_paths)}")
min_x_t, min_y_t, max_x_t, max_y_t = RotarySlicingEngine.get_artwork_bounds(text_paths)
print(f"Text bounds: X[{min_x_t:.3f}, {max_x_t:.3f}], Y[{min_y_t:.3f}, {max_y_t:.3f}], Span Y={max_y_t - min_y_t:.3f}")
