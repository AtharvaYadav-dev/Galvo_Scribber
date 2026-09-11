import ctypes
from ctypes import c_int32, POINTER, byref, c_int, c_double, c_short, c_ushort, c_uint32
import os
from .base import BaseConnection
from ..calibration import GalvoCalibration

DLL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "gt5motion_GT.dll")

class HardwareConnection(BaseConnection):
    """
    Physical connection interface for Galvo_Studio.
    Uses ctypes to communicate directly with gt5motion_GT.dll.
    """
    def __init__(self):
        super().__init__()
        self.is_initialized = False
        self.dll = None
        # Load our Python calibration module (to bypass GoogolTech 2D comp limitations)
        self.calibration = GalvoCalibration(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "newest100mm.cor"))

    def initialize(self):
        try:
            self.dll = ctypes.WinDLL(DLL_PATH)
            self._setup_signatures()
            
            if hasattr(self.dll, 'GT_PROSYS_U3_SetPass'):
                self.dll.GT_PROSYS_U3_SetPass(12242)
                
            cards = c_int32(0)
            res = self.dll.GT_PROSYS_U3_Initialize(byref(cards))
            
            if cards.value == 0:
                print("Warning: Hardware mode is ON, but no Galvo cards were found. Initialization failed.")
                self.is_initialized = False
                return -1, 0
            else:
                if hasattr(self.dll, 'GT_PROSYS_U3_XY_Data') and hasattr(self.dll, 'GT_PROSYS_U3_Run_Galvo'):
                    import time
                    time.sleep(1.0)
                    self.dll.GT_PROSYS_U3_XY_Data(0, 0)
                    self.dll.GT_PROSYS_U3_XY_Data(1, 0)
                    self.dll.GT_PROSYS_U3_Run_Galvo(1)
                
                # Disable Z-axis hard limit (axis 2) as requested
                if hasattr(self.dll, 'GT_PROSYS_U3_disable_hard_limit'):
                    self.dll.GT_PROSYS_U3_disable_hard_limit(c_short(2))

                # Reset Axis to clear any alarms
                if hasattr(self.dll, 'GT_PROSYS_U3_ResetAxis'):
                    self.dll.GT_PROSYS_U3_ResetAxis(c_short(2))

                # Ensure Pulse Output Mode is correct (0 = Pulse/Dir)
                if hasattr(self.dll, 'GT_PROSYS_U3_set_pulse_out_mode'):
                    self.dll.GT_PROSYS_U3_set_pulse_out_mode(c_short(2), c_short(0))
                    
                self.is_initialized = True
                
                # Force laser (DO1) to OFF state immediately upon connection
                self.laser_off()
                
                return res, cards.value
                
        except Exception as e:
            print(f"Error loading DLL: {e}")
            self.is_initialized = False
            return -1, 0

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

        if hasattr(self.dll, 'GT_PROSYS_U3_get_di_bit'):
            self.dll.GT_PROSYS_U3_get_di_bit.argtypes = [c_short, POINTER(c_short)]
            self.dll.GT_PROSYS_U3_get_di_bit.restype = c_short

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

        if hasattr(self.dll, 'GT_PROSYS_U3_get_command'):
            self.dll.GT_PROSYS_U3_get_command.argtypes = [c_int32, POINTER(c_int32)]
            self.dll.GT_PROSYS_U3_get_command.restype = c_int32
            
        if hasattr(self.dll, 'GT_PROSYS_U3_set_command'):
            self.dll.GT_PROSYS_U3_set_command.argtypes = [c_int32, c_int32]
            self.dll.GT_PROSYS_U3_set_command.restype = c_int32
            
        if hasattr(self.dll, 'GT_PROSYS_U3_set_analog_do_bit'):
            self.dll.GT_PROSYS_U3_set_analog_do_bit.argtypes = [c_double, c_double, c_double, c_short]
            self.dll.GT_PROSYS_U3_set_analog_do_bit.restype = None

        if hasattr(self.dll, 'IsConnected'):
            self.dll.IsConnected.argtypes = []
            self.dll.IsConnected.restype = c_short

    def close(self):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_Close'):
            self.dll.GT_PROSYS_U3_Close()
        self.is_initialized = False

    def stop(self):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_Stop'):
            self.dll.GT_PROSYS_U3_Stop()
            
    def set_analog_do_bit(self, max_val, crt_val, freq_val, bit):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_set_analog_do_bit'):
            self.dll.GT_PROSYS_U3_set_analog_do_bit(c_double(max_val), c_double(crt_val), c_double(freq_val), c_short(bit))

    def galvo_move_xy(self, x, y, speed=None):
        speed_val = int(speed) if speed else 1000
        cx, cy = self.calibration.apply(float(x), float(y))
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_galvo_move_XY'):
            self.dll.GT_PROSYS_U3_galvo_move_XY(int(cx), int(cy), speed_val, 0.0, 0.0, 0.0)

    def is_physically_connected(self):
        if self.dll and hasattr(self.dll, 'IsConnected'):
            return self.dll.IsConnected() != 0
        return True

    def wait_for_motion(self):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_galvo_run_status'):
            import time
            while self.dll.GT_PROSYS_U3_galvo_run_status() == 1:
                if hasattr(self.dll, 'IsConnected') and self.dll.IsConnected() == 0:
                    raise ConnectionError("Galvo hardware disconnected during motion")
                time.sleep(0.001)

    def axis_move(self, axis, position, speed, is_relative=False):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_axis_move'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)

            axis_array = (c_short * 1)(axis_idx)
            dist_array = (c_double * 1)(float(position))
            
            rel_abs = 0 if is_relative else 1
            no_axis = 1
            str_vel = float(speed) * 0.2
            max_vel = float(speed)
            tacc = 0.1
            
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

    def get_home_status(self, axis='Z'):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_get_home_status'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)
            try:
                return self.dll.GT_PROSYS_U3_get_home_status(c_int32(axis_idx))
            except Exception:
                return 0
        return 0

    def get_axis_position(self, axis):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_get_command'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)
            cmd_val = c_int32(0)
            try:
                self.dll.GT_PROSYS_U3_get_command(c_int32(axis_idx), byref(cmd_val))
                return cmd_val.value
            except Exception as e:
                print(f"Error getting axis position: {e}")
        return 0

    def set_axis_position(self, axis, position_pulses):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_set_command'):
            axis_map = {'X': 0, 'Y': 1, 'Z': 2, 'U': 3, 'V': 4}
            axis_idx = axis_map.get(str(axis).upper(), 2)
            try:
                self.dll.GT_PROSYS_U3_set_command(c_int32(axis_idx), c_int32(int(position_pulses)))
            except Exception as e:
                print(f"Error setting axis position: {e}")

    def set_io(self, io_pin, state):
        print(f"HARDWARE COMMAND: Setting IO pin {io_pin} to state {state}")
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_set_do_bit'):
            self.dll.GT_PROSYS_U3_set_do_bit(c_short(io_pin), c_short(state))

    def get_di_bit(self, io_pin):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_get_di_bit'):
            val = c_short(0)
            try:
                self.dll.GT_PROSYS_U3_get_di_bit(c_short(io_pin), byref(val))
                return val.value
            except Exception as e:
                print(f"Error getting DI bit: {e}")
        return 0

    def laser_on(self):
        print("HARDWARE COMMAND: laser_on() called. Setting DO1 (Pin 0) to HIGH (1) to turn ON the laser/LED.")
        self.set_io(0, 1)
        self.send_buffer()

    def laser_off(self):
        print("HARDWARE COMMAND: laser_off() called. Setting DO1 (Pin 0) to LOW (0) to turn OFF the laser/LED.")
        self.set_io(0, 0)
        self.send_buffer()

    def reddot_on(self):
        print("HARDWARE COMMAND: reddot_on() called. Setting DO2 (Pin 1) to HIGH (1) to turn ON the red dot laser.")
        self.set_io(1, 1)
        self.send_buffer()

    def reddot_off(self):
        print("HARDWARE COMMAND: reddot_off() called. Setting DO2 (Pin 1) to LOW (0) to turn OFF the red dot laser.")
        self.set_io(1, 0)
        self.send_buffer()

    def send_buffer(self):
        if self.dll and hasattr(self.dll, 'GT_PROSYS_U3_send_buffer'):
            print("HARDWARE COMMAND: send_buffer() called.")
            self.dll.GT_PROSYS_U3_send_buffer()

    def stop(self):
        pass
