import os
import datetime
from .base import BaseConnection
from ..calibration import GalvoCalibration

_log_buffer = []

def flush_logs():
    if not _log_buffer:
        return
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
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

class MockConnection(BaseConnection):
    """
    Simulation interface for Galvo_Studio.
    Intercepts binary commands and simply logs them without engaging physical hardware.
    """
    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.is_initialized = False
        self.calibration = GalvoCalibration(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "newest100mm.cor"))

    def initialize(self):
        log_command("INIT_CARD (MOCK)")
        self.is_initialized = True
        return 0, 1  # 0 success, 1 card found

    def close(self):
        log_command("CLOSE_CARD (MOCK)")
        self.is_initialized = False

    def galvo_move_xy(self, x, y, speed=None):
        speed_val = int(speed) if speed else 1000
        speed_str = f" SPEED={speed_val}"
        log_command(f"MOVE_XY {int(x)} {int(y)}{speed_str}")

    def wait_for_motion(self):
        # In mock mode, we assume the machine is infinitely fast and returns immediately
        pass

    def axis_move(self, axis, position, speed, is_relative=False):
        log_command(f"AXIS_MOVE {axis} {'REL' if is_relative else 'ABS'} {position} {speed}")

    def get_home_status(self, axis='Z'):
        # Mock mode can always return 0 (not triggered)
        return 0

    def get_axis_position(self, axis):
        # Mock mode doesn't track position automatically, return 0 or simulated position
        return 0

    def set_axis_position(self, axis, position_pulses):
        log_command(f"SET_AXIS_POSITION {axis} {position_pulses}")

    def set_io(self, io_pin, state):
        log_command(f"SET_IO pin={io_pin} state={state}")

    def get_di_bit(self, io_pin):
        # In mock mode, we simulate inputs as 0
        return 0

    def laser_on(self):
        self.set_io(1, 1)
        log_command("LASER_ON")

    def laser_off(self):
        self.set_io(1, 0)
        log_command("LASER_OFF")

    def reddot_on(self):
        self.set_io(1, 1)
        log_command("REDDOT_ON")

    def reddot_off(self):
        self.set_io(1, 0)
        log_command("REDDOT_OFF")

    def send_buffer(self):
        log_command("SEND_BUFFER")
        flush_logs()

    def stop(self):
        log_command("STOP")
        
    def set_analog_do_bit(self, max_val, crt_val, freq_val, bit):
        log_command(f"SET_ANALOG_DO_BIT max={max_val} crt={crt_val} freq={freq_val} bit={bit}")
