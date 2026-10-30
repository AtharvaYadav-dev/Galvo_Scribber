import sys
sys.path.append(r"d:\Galvo_using_qml\Galvo_UI_2_with_cad_page")
from bridges.matrix_bridge import MatrixBridge
from core.motion_planner import MotionPlanner

mb = MatrixBridge()
mb.updateParameters(10.0, 90.0, 5, 20.0, 80.0, 5, 5.0, 5.0, 2.0, 2.0, "Vector Outline", True, 1000.0)

planner = MotionPlanner()
scale = 533.89
jump_speed = 2000000
digit_speed = 133472 # 250 mm/s

# Test _draw_stroke_text directly
mb._draw_stroke_text("Freq (kHz)", -20.0, 20.0, planner, font_size_mm=2.5, speed=digit_speed, jump_speed=jump_speed)
mb._draw_stroke_text("Laser Power (%)", 0.0, -22.0, planner, font_size_mm=2.5, speed=digit_speed, jump_speed=jump_speed)
mb._draw_stroke_text("20 kHz", -20.0, -10.0, planner, font_size_mm=2.2, speed=digit_speed, jump_speed=jump_speed)
mb._draw_stroke_text("10%", -10.0, -20.0, planner, font_size_mm=2.2, speed=digit_speed, jump_speed=jump_speed)

print("Generated commands in preview queue:", len(planner.preview_queue))
jumps = [c for c in planner.preview_queue if c.get('type') == 'jump']
marks = [c for c in planner.preview_queue if c.get('type') == 'mark']
laser_offs = [c for c in planner.preview_queue if c.get('type') == 'laser_off']

print(f"Jumps: {len(jumps)}, Marks: {len(marks)}, Laser Offs: {len(laser_offs)}")
assert len(jumps) > 0
assert len(marks) > 0
assert len(laser_offs) == 4
print("TEST PASSED!")
