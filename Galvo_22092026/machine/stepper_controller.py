from core.connection import BaseConnection

class StepperController:
    def __init__(self, connection: BaseConnection, steps_per_mm=333.333): 
        self.connection = connection
        self.z_position = 0.0
        self.steps_per_mm = steps_per_mm
        self.next_ready_time = 0.0

    def get_physical_z(self):
        """Reads the exact pulse counter from the hardware and converts it to mm."""
        if not self.connection or not getattr(self.connection, 'is_initialized', False):
            return self.z_position
        
        pulses = self.connection.get_axis_position('Z')
        return -pulses / self.steps_per_mm

    def move_axis(self, axis, position_mm, speed=1000):
        """
        Moves a stepper motor axis (e.g., Z-axis for focus, or XY table).
        Position is given in millimeters.
        """
        if not self.connection or not getattr(self.connection, 'is_initialized', False):
            print("Cannot move axis, system not initialized.")
            return False
            
        if axis.upper() == 'Z':
            distance = position_mm - self.z_position
            return self.move_z_relative(distance, speed)
            
        pulses = int(position_mm * self.steps_per_mm)
        print(f"Moving Axis {axis} to {position_mm} mm ({pulses} pulses) at speed {speed}")
        self.connection.axis_move(axis, pulses, speed)
        
        return True

    def move_z_relative(self, distance_mm, speed=1000, ignore_limits=False):
        """Moves the Z axis relative to the current position in mm.
        (Pulses are inverted so that positive distance moves UPWARD physically)"""
        
        if not ignore_limits:
            new_pos = self.z_position + distance_mm
            if new_pos > 120.0:
                print(f"Warning: Reached Z-Axis Max limit (120.0 mm). Truncating move.")
                distance_mm = 120.0 - self.z_position
            elif new_pos < 0.0:
                print(f"Warning: Reached Z-Axis Min limit (0.0 mm). Truncating move.")
                distance_mm = 0.0 - self.z_position
                
        if abs(distance_mm) < 0.001:
            return False
            
        import time
        if time.time() < self.next_ready_time:
            wait_time = self.next_ready_time - time.time()
            print(f"Z Axis is busy moving. Waiting {wait_time:.2f}s for previous move to finish...")
            time.sleep(wait_time)

        pulses = int(-distance_mm * self.steps_per_mm)
        print(f"Moving Axis Z relative by {distance_mm:.3f} mm ({pulses} pulses) at speed {speed}")
        self.connection.axis_move('Z', pulses, speed, is_relative=True)
        
        # Calculate how long the physical move takes (speed is pulses/sec, acceleration time is ~0.2s)
        travel_time = (abs(pulses) / speed) + 0.2
        self.next_ready_time = time.time() + travel_time
        
        self.z_position += distance_mm
        return True

    def move_z_absolute(self, position_mm, speed=10000, ignore_limits=False):
        """Moves the Z axis to an absolute position in mm (like Marlin G90; G1 Z)."""
        if not ignore_limits:
            if position_mm > 120.0:
                print(f"Warning: Requested position {position_mm} exceeds Max limit (120.0 mm). Clamping.")
                position_mm = 120.0
            elif position_mm < 0.0:
                print(f"Warning: Requested position {position_mm} below Min limit (0.0 mm). Clamping.")
                position_mm = 0.0
                
        distance_mm = position_mm - self.z_position
        if abs(distance_mm) < 0.001:
            return False
            
        import time
        if time.time() < self.next_ready_time:
            wait_time = self.next_ready_time - time.time()
            print(f"Z Axis is busy moving. Waiting {wait_time:.2f}s for previous move to finish...")
            time.sleep(wait_time)
            
        pulses = int(-distance_mm * self.steps_per_mm)
        print(f"Moving Axis Z absolute to {position_mm:.3f} mm (distance: {distance_mm:.3f} mm, {pulses} pulses) at speed {speed}")
        self.connection.axis_move('Z', pulses, speed, is_relative=True)
        
        travel_time = (abs(pulses) / speed) + 0.2
        self.next_ready_time = time.time() + travel_time
        
        self.z_position = position_mm
        return True
        
    def home_z(self, app_instance=None):
        """
        Custom Homing Sequence:
        Moves Z-axis downwards (Z-) in small increments until the limit switch is triggered (status == 1).
        """
        import time
        if not self.connection or not getattr(self.connection, 'is_initialized', False):
            print("Cannot home axis, system not initialized.")
            return False
            
        print("Starting Z-Axis Homing Sequence...")
        step_mm = 0.5  # Move 0.5mm at a time
        speed = 4000   # Fast movement for small steps
        max_dist_mm = 200.0 # Maximum travel distance to prevent infinite loops (200mm)
        
        steps = int(max_dist_mm / step_mm)
        
        for _ in range(steps):
            status = self.connection.get_home_status('Z')
            if status == 0:
                print("Limit Switch Triggered! Homing successful.")
                # Move slightly away from the switch (backoff UPWARD)
                self.move_z_relative(1.0, speed=10000, ignore_limits=True)
                time.sleep(0.5)
                # Reset logical position to 0 
                self.z_position = 0.0
                if hasattr(self.connection, 'set_axis_position'):
                    self.connection.set_axis_position('Z', 0)
                return True
                
            # Move DOWNWARD 
            self.move_z_relative(-step_mm, speed, ignore_limits=True)
            
            # Wait for step to physically complete 
            time.sleep(0.1)
            
            # Keep UI responsive
            if app_instance:
                app_instance.processEvents()
                
        print("Homing failed: Reached max distance without hitting switch.")
        return False
