class BaseConnection:
    """
    Abstract base class for all Galvo hardware connections.
    Defines the standard interface that Controllers and UI will use.
    """
    def __init__(self):
        self.is_initialized = False

    def initialize(self):
        """Initializes the connection. Returns (result_code, num_cards)"""
        raise NotImplementedError

    def close(self):
        """Closes the connection safely."""
        raise NotImplementedError

    def galvo_move_xy(self, x, y, speed=None):
        """Moves the galvo mirrors to the specified (x,y) coordinates."""
        raise NotImplementedError

    def wait_for_motion(self):
        """Blocks until the galvo has finished its current motion."""
        raise NotImplementedError

    def axis_move(self, axis, position, speed, is_relative=False):
        """Moves a stepper/servo axis (Z, U, V)."""
        raise NotImplementedError

    def get_home_status(self, axis='Z'):
        """Gets the homing limit switch status of an axis."""
        raise NotImplementedError

    def get_axis_position(self, axis):
        """Gets the current pulse position counter of the specified axis."""
        raise NotImplementedError

    def set_axis_position(self, axis, position_pulses):
        """Sets the pulse position counter of the specified axis."""
        raise NotImplementedError

    def set_io(self, io_pin, state):
        """Sets a digital IO pin high (1) or low (0)."""
        raise NotImplementedError

    def laser_on(self):
        """Turns the laser emission ON."""
        raise NotImplementedError

    def laser_off(self):
        """Turns the laser emission OFF."""
        raise NotImplementedError

    def reddot_on(self):
        """Turns the red dot laser ON."""
        raise NotImplementedError

    def reddot_off(self):
        """Turns the red dot laser OFF."""
        raise NotImplementedError

    def send_buffer(self):
        """Sends the command buffer to the physical hardware."""
        pass

    def stop(self):
        """Emergency stops the execution."""
        pass
