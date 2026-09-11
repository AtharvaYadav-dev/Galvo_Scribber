import ctypes
from ctypes import c_int32, POINTER, byref, c_int, c_double, c_short, c_ushort, c_uint32
import os
import datetime

HARDWARE_CONNECTED = True
DLL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gt5motion_GT.dll")

_log_buffer = []

def flush_logs():
    if not _log_buffer:
        return
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"galvo_log_{datetime.date.today()}.txt")
    
    with open(log_file, "a") as f:
        f.write("".join(_log_buffer))
    _log_buffer.clear()

def log_command(cmd_str):
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    _log_buffer.append(f"{timestamp} {cmd_str}\n")
    
    # Flush automatically if buffer gets too large
    if len(_log_buffer) > 5000:
        flush_logs()

class GalvoDLLWrapper:
    def __init__(self):
        self.dll = None
        self.is_initialized = False
        global HARDWARE_CONNECTED
        
        if HARDWARE_CONNECTED:
            try:
                self.dll = ctypes.WinDLL(DLL_PATH)
                self._setup_signatures()
                print("DLL Loaded Successfully")
            except Exception as e:
                print(f"Error loading DLL: {e}")
                HARDWARE_CONNECTED = False # Fallback to mock

    def _setup_signatures(self):
        if not self.dll: return
        
        # GT_PROSYS_U3_Initialize
        self.dll.GT_PROSYS_U3_Initialize.argtypes = [POINTER(c_int32)]
        self.dll.GT_PROSYS_U3_Initialize.restype = c_int32
        
        # Close
        if hasattr(self.dll, 'GT_PROSYS_U3_Close'):
            self.dll.GT_PROSYS_U3_Close.argtypes = []
            self.dll.GT_PROSYS_U3_Close.restype = c_int32

        # GT_PROSYS_U3_galvo_move_XY
        if hasattr(self.dll, 'GT_PROSYS_U3_galvo_move_XY'):
            self.dll.GT_PROSYS_U3_galvo_move_XY.argtypes = [c_int32, c_int32, c_int32, c_double, c_double, c_double]
            self.dll.GT_PROSYS_U3_galvo_move_XY.restype = None

        # GT_PROSYS_U3_axis_move (For Stepper/Z-Axis)
        if hasattr(self.dll, 'GT_PROSYS_U3_axis_move'):
            self.dll.GT_PROSYS_U3_axis_move.argtypes = [c_short, c_short, POINTER(c_short), POINTER(c_double), c_double, c_double, c_double]
            self.dll.GT_PROSYS_U3_axis_move.restype = c_short


        # GT_PROSYS_U3_send_buffer
        if hasattr(self.dll, 'GT_PROSYS_U3_send_buffer'):
            self.dll.GT_PROSYS_U3_send_buffer.argtypes = []
            self.dll.GT_PROSYS_U3_send_buffer.restype = None

        # GT_PROSYS_U3_set_do_bit
        if hasattr(self.dll, 'GT_PROSYS_U3_set_do_bit'):
            self.dll.GT_PROSYS_U3_set_do_bit.argtypes = [c_short, c_short]
            self.dll.GT_PROSYS_U3_set_do_bit.restype = None

        if hasattr(self.dll, 'GT_PROSYS_U3_SetPass'):
            self.dll.GT_PROSYS_U3_SetPass.argtypes = [c_int32]
            self.dll.GT_PROSYS_U3_SetPass.restype = c_int32

        if hasattr(self.dll, 'GT_PROSYS_U3_XY_Data'):
            self.dll.GT_PROSYS_U3_XY_Data.argtypes = [c_short, c_uint32]
            self.dll.GT_PROSYS_U3_XY_Data.restype = c_short

        if hasattr(self.dll, 'GT_PROSYS_U3_Run_Galvo'):
            self.dll.GT_PROSYS_U3_Run_Galvo.argtypes = [c_short]
            self.dll.GT_PROSYS_U3_Run_Galvo.restype = c_short

        if hasattr(self.dll, 'GT_PROSYS_U3_galvo_run_status'):
            self.dll.GT_PROSYS_U3_galvo_run_status.argtypes = []
            self.dll.GT_PROSYS_U3_galvo_run_status.restype = c_short
            
        if hasattr(self.dll, 'GT_PROSYS_U3_set_continous_mode_on'):
            self.dll.GT_PROSYS_U3_set_continous_mode_on.argtypes = []
            self.dll.GT_PROSYS_U3_set_continous_mode_on.restype = None
            
        if hasattr(self.dll, 'GT_PROSYS_U3_set_continous_mode_off'):
            self.dll.GT_PROSYS_U3_set_continous_mode_off.argtypes = []
            self.dll.GT_PROSYS_U3_set_continous_mode_off.restype = None
            
        if hasattr(self.dll, 'GT_PROSYS_U3_buffer_ready'):
            self.dll.GT_PROSYS_U3_buffer_ready.argtypes = []
            self.dll.GT_PROSYS_U3_buffer_ready.restype = c_short

        if hasattr(self.dll, 'GT_PROSYS_U3_get_home_status'):
            self.dll.GT_PROSYS_U3_get_home_status.argtypes = [c_int32]
            self.dll.GT_PROSYS_U3_get_home_status.restype = c_int32

        if hasattr(self.dll, 'GT_PROSYS_U3_disable_hard_limit'):
            self.dll.GT_PROSYS_U3_disable_hard_limit.argtypes = [c_short]
            self.dll.GT_PROSYS_U3_disable_hard_limit.restype = c_short

        if hasattr(self.dll, 'GT_PROSYS_U3_set_pulse_out_mode'):
            self.dll.GT_PROSYS_U3_set_pulse_out_mode.argtypes = [c_short, c_short]
            self.dll.GT_PROSYS_U3_set_pulse_out_mode.restype = c_short

        if hasattr(self.dll, 'GT_PROSYS_U3_ResetAxis'):
            self.dll.GT_PROSYS_U3_ResetAxis.argtypes = [c_short]
            self.dll.GT_PROSYS_U3_ResetAxis.restype = c_short
            
        if hasattr(self.dll, 'GT_PROSYS_U3_get_home_status'):
            self.dll.GT_PROSYS_U3_get_home_status.argtypes = [c_int32]
            self.dll.GT_PROSYS_U3_get_home_status.restype = c_int32



    def initialize(self):
        if HARDWARE_CONNECTED:
            if hasattr(self.dll, 'GT_PROSYS_U3_SetPass'):
                self.dll.GT_PROSYS_U3_SetPass(12242)
                
            cards = c_int32(0)
            res = self.dll.GT_PROSYS_U3_Initialize(byref(cards))
            log_command(f"INIT_CARD result={res} cards={cards.value}")
            
            if cards.value == 0:
                print("Warning: Hardware mode is ON, but no Galvo cards were found. Initialization failed.")
                self.is_initialized = False
            else:
                if hasattr(self.dll, 'GT_PROSYS_U3_XY_Data') and hasattr(self.dll, 'GT_PROSYS_U3_Run_Galvo'):
                    import time
                    time.sleep(1.0)
                    self.dll.GT_PROSYS_U3_XY_Data(0, 0)
                    self.dll.GT_PROSYS_U3_XY_Data(1, 0)
                    self.dll.GT_PROSYS_U3_Run_Galvo(1)
                self.is_initialized = True # Cards found successfully
                
                # Disable Z-axis hard limit (axis 2) as requested
                if hasattr(self.dll, 'GT_PROSYS_U3_disable_hard_limit'):
                    self.dll.GT_PROSYS_U3_disable_hard_limit(c_short(2))
                    log_command("DISABLED_Z_HARD_LIMIT")

                # Reset Axis to clear any alarms
                if hasattr(self.dll, 'GT_PROSYS_U3_ResetAxis'):
                    self.dll.GT_PROSYS_U3_ResetAxis(c_short(2))
                    log_command("RESET_Z_AXIS")

                # Ensure Pulse Output Mode is correct (0 = Pulse/Dir)
                if hasattr(self.dll, 'GT_PROSYS_U3_set_pulse_out_mode'):
                    self.dll.GT_PROSYS_U3_set_pulse_out_mode(c_short(2), c_short(0))
                
            return res, cards.value
        else:
            log_command("INIT_CARD (MOCK)")
            self.is_initialized = True
            return 0, 1

    def close(self):
        if HARDWARE_CONNECTED and hasattr(self.dll, 'GT_PROSYS_U3_Close'):
            res = self.dll.GT_PROSYS_U3_Close()
            log_command(f"CLOSE_CARD result={res}")
        else:
            log_command("CLOSE_CARD (MOCK)")

    def galvo_move_xy(self, x, y, speed=None):
        speed_val = int(speed) if speed else 1000
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_galvo_move_XY'):
            self.dll.GT_PROSYS_U3_galvo_move_XY(int(x), int(y), speed_val, 0.0, 0.0, 0.0)
            
        speed_str = f" SPEED={speed_val}"
        log_command(f"MOVE_XY {int(x)} {int(y)}{speed_str}")

    def wait_for_motion(self):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_galvo_run_status'):
            import time
            while self.dll and self.dll.GT_PROSYS_U3_galvo_run_status() == 1:
                time.sleep(0.001)

    def axis_move(self, axis, position, speed, is_relative=False):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_axis_move'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)

            axis_array = (c_short * 1)(axis_idx)
            dist_array = (c_double * 1)(float(position))
            
            rel_abs = 0 if is_relative else 1  # 0 for Relative, 1 for Absolute
            no_axis = 1  # Moving 1 axis
            str_vel = float(speed) * 0.2  # Starting velocity (20% of max)
            max_vel = float(speed)        # Maximum velocity
            tacc = 0.1                    # Acceleration time in seconds
            
            try:
                self.dll.GT_PROSYS_U3_axis_move(
                    c_short(rel_abs), 
                    c_short(no_axis), 
                    axis_array, 
                    dist_array, 
                    c_double(str_vel), 
                    c_double(max_vel), 
                    c_double(tacc)
                )
            except Exception as e:
                print(f"Error moving axis: {e}")

        log_command(f"AXIS_MOVE {axis} {'REL' if is_relative else 'ABS'} {position} {speed}")

    def get_home_status(self, axis='Z'):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_get_home_status'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)
            try:
                return self.dll.GT_PROSYS_U3_get_home_status(c_int32(axis_idx))
            except Exception:
                return 0
        return 0

    def send_buffer(self):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_send_buffer'):
            self.dll.GT_PROSYS_U3_send_buffer()
        log_command("SEND_BUFFER")

    def stop(self):
        if HARDWARE_CONNECTED:
            pass
        log_command("STOP")

    def set_io(self, io_pin, state):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_set_do_bit'):
            self.dll.GT_PROSYS_U3_set_do_bit(c_short(io_pin), c_short(state))
        log_command(f"SET_IO pin={io_pin} state={state}")

    def laser_on(self):
        self.set_io(1, 1) # Example IO pin for laser
        log_command("LASER_ON")

    def laser_off(self):
        self.set_io(1, 0)
        log_command("LASER_OFF")

    def get_home_status(self, axis):
        if self.is_initialized and self.dll and hasattr(self.dll, 'GT_PROSYS_U3_get_home_status'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)
            return self.dll.GT_PROSYS_U3_get_home_status(c_int32(axis_idx))
        return -1
