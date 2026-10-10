import sys
import traceback
import os
sys.path.append(os.getcwd())
from PySide6.QtWidgets import QApplication
import mapping_dialog

class DummyConnection:
    laser_is_on = False
    def laser_on(self): pass
    def laser_off(self): pass
    def reddot_on(self): pass
    def reddot_off(self): pass
    def set_analog_do_bit(self, *args): pass
    def jump(self, x, y): pass
    def mark(self, x, y): pass
    def wait_for_motion(self): pass
    def send_buffer(self): pass

class DummyGalvoController:
    connection = DummyConnection()
    def execute_queue(self, q, loop_count=1, abort_check=None, progress_callback=None):
        print(f"Executing queue of {len(q)} items")
        pass
    def laser_off(self): pass
    def reddot_off(self): pass

class DummyGalvoConfig:
    field_size = 110.0
    def apply_transform(self, x, y):
        return x, y

class DummyMainWindow:
    galvo_config = DummyGalvoConfig()
    galvo_controller = DummyGalvoController()
    hatch_profiles = {1: {'enable': True, 'num_loops': "2", 'loop_dist': "0.1", 'angle': "45.0", 'line_space': "0.1", 'cross_hatch': 'true', 'all_calc': 'false', 'follow_edge': 'false', 'type': 'Bidirectional', 'count': '1', 'avg_dist': 'false', 'edge_off': '0.0', 'start_off': '0.0', 'end_off': '0.0', 'line_red': '0.0', 'auto_rot': 'false', 'rot_angle': '10.0'}}
    def set_cal_status(self, text):
        print(text)

app = QApplication([])
dialog = mapping_dialog.ParameterMappingDialog(DummyMainWindow())
dialog.galvo = DummyGalvoController()
dialog.cell_w.setText("5.0")
dialog.cell_h.setText("5.0")
dialog.fill_type.setCurrentText("Filled Rectangle")
dialog.generate_matrix()

try:
    dialog._execute(is_preview=False)
    print("Execution simulated successfully")
except Exception as e:
    traceback.print_exc()

