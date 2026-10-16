from PySide6.QtCore import QThread, Signal

class ExecutionThread(QThread):
    finished_signal = Signal(bool)
    progress_signal = Signal(int, int, float, float, str)
    depth_signal = Signal(int, int, float, float) # (current_layer, total_layers, current_depth, target_depth)
    
    def __init__(self, controller, queue, loop_count=1, 
                 stepper_controller=None, 
                 enable_engraving=False, 
                 z_step_mm=0.05, 
                 target_depth_mm=1.0, 
                 settle_delay_s=0.15, 
                 safe_return_z=None):
        super().__init__()
        self.controller = controller
        self.queue = queue
        self.loop_count = loop_count
        self.stepper_controller = stepper_controller
        self.enable_engraving = enable_engraving
        self.z_step_mm = z_step_mm
        self.target_depth_mm = target_depth_mm
        self.settle_delay_s = settle_delay_s
        self.safe_return_z = safe_return_z
        self._abort = False
        
    def abort(self):
        self._abort = True
        
    def run(self):
        import time
        self._last_update_time = 0
        total_cmds = len(self.queue) * max(1, self.loop_count)

        def on_pos_factory(pass_offset):
            def on_pos(i, total, x, y, ctype):
                current_time = time.time()
                overall_idx = pass_offset + i
                is_important = ctype and str(ctype).startswith("pass_change:")
                if is_important or i == 0 or i == total - 1 or (current_time - self._last_update_time) > 0.05:
                    self.progress_signal.emit(overall_idx, total_cmds, x, y, ctype)
                    self._last_update_time = current_time
            return on_pos

        if hasattr(self.controller, 'galvo_home'):
            self.controller.galvo_home()

        success = True
        try:
            if not self.enable_engraving or not self.stepper_controller or self.loop_count <= 1:
                # Standard execution (single or continuous loop without Z drop)
                def on_pos(i, total, x, y, ctype):
                    current_time = time.time()
                    is_important = ctype and str(ctype).startswith("pass_change:")
                    if is_important or i == 0 or i == total - 1 or (current_time - self._last_update_time) > 0.05:
                        self.progress_signal.emit(i, total, x, y, ctype)
                        self._last_update_time = current_time

                success = self.controller.execute_queue(
                    self.queue, 
                    self.loop_count, 
                    progress_callback=on_pos, 
                    abort_check=lambda: self._abort
                )
            else:
                # Multi-Pass Z-Drop Deep Engraving Loop
                current_depth = 0.0
                step = float(self.z_step_mm)
                max_allowed_depth = min(5.0, float(self.target_depth_mm))

                for pass_idx in range(self.loop_count):
                    if self._abort:
                        print("Execution aborted before pass.")
                        success = False
                        break

                    # Emit pass and depth update
                    self.depth_signal.emit(pass_idx + 1, self.loop_count, current_depth, max_allowed_depth)
                    
                    callback = on_pos_factory(pass_idx * len(self.queue))
                    pass_ok = self.controller.execute_queue(
                        self.queue, 
                        loop_count=1, 
                        progress_callback=callback, 
                        abort_check=lambda: self._abort
                    )
                    
                    if not pass_ok or self._abort:
                        success = False
                        break

                    # Ensure laser is strictly OFF between passes
                    if hasattr(self.controller, 'connection') and self.controller.connection:
                        if hasattr(self.controller.connection, 'laser_off'):
                            self.controller.connection.laser_off()
                        if hasattr(self.controller.connection, 'wait_for_motion'):
                            self.controller.connection.wait_for_motion()

                    # Safety Limit Check
                    next_depth = (pass_idx + 1) * step
                    if next_depth >= max_allowed_depth - 0.0001 or next_depth >= 5.0:
                        print(f"[Engraving] Target depth reached ({next_depth:.3f} mm / {max_allowed_depth:.3f} mm). Stopping.")
                        current_depth = min(next_depth, max_allowed_depth)
                        self.depth_signal.emit(pass_idx + 1, self.loop_count, current_depth, max_allowed_depth)
                        break

                    # Drop Z-axis for the next pass
                    if pass_idx < self.loop_count - 1:
                        print(f"[Engraving] Dropping Z-axis by -{step:.3f} mm (next depth: {next_depth:.3f} mm)...")
                        self.stepper_controller.move_z_relative(-step, speed=1000)
                        current_depth = next_depth
                        self.depth_signal.emit(pass_idx + 1, self.loop_count, current_depth, max_allowed_depth)

                        # Damping delay for motor vibrations to settle
                        time.sleep(self.settle_delay_s)

        finally:
            # Ensure laser is OFF
            if hasattr(self.controller, 'connection') and self.controller.connection:
                if hasattr(self.controller.connection, 'laser_off'):
                    self.controller.connection.laser_off()

            # Safe Height Retract: return Z to initial starting focus
            if self.enable_engraving and self.safe_return_z is not None and self.stepper_controller:
                try:
                    print(f"[Engraving] Retracting Z-axis to safe starting height: {self.safe_return_z:.2f} mm")
                    self.stepper_controller.move_z_absolute(self.safe_return_z, speed=1000)
                except Exception as e:
                    print(f"[Engraving] Error retracting Z-axis: {e}")

        self.finished_signal.emit(success)

class PreviewThread(QThread):
    finished_signal = Signal(bool)
    def __init__(self, controller, min_x, max_x, min_y, max_y):
        super().__init__()
        self.controller = controller
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.running = True
        self.needs_refresh = False
        
    def update_bounds(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.needs_refresh = True
        
    def run(self):
        speed = 2000000
        if hasattr(self.controller.connection, 'laser_off'):
            self.controller.connection.laser_off()
        if hasattr(self.controller.connection, 'set_analog_do_bit'):
            self.controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
        if hasattr(self.controller.connection, 'reddot_on'):
            self.controller.connection.reddot_on()
            
        dll_obj = getattr(self.controller.connection, 'dll', None) if self.controller.connection else None
        has_continuous = dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_set_continous_mode_on')
        
        if has_continuous:
            dll_obj.GT_PROSYS_U3_set_continous_mode_on()
            
        import time
        
        while self.running:
            if hasattr(self.controller.connection, 'is_physically_connected') and not self.controller.connection.is_physically_connected():
                print("Preview aborted: hardware disconnected.")
                self.finished_signal.emit(False)
                break
                
            if self.needs_refresh:
                if has_continuous:
                    dll_obj.GT_PROSYS_U3_set_continous_mode_off()
                    time.sleep(0.05) # Give hardware time to clear the loop buffer
                    dll_obj.GT_PROSYS_U3_set_continous_mode_on()
                self.needs_refresh = False
                
            if dll_obj and hasattr(dll_obj, 'GT_PROSYS_U3_galvo_move_XY'):
                # Apply final corrected coordinate mapping
                def move(x, y):
                    dll_obj.GT_PROSYS_U3_galvo_move_XY(int(y), int(x), speed, 0.0, 0.0, 0.0)

                c_y = int((self.min_y + self.max_y) / 2)
                c_x = int((self.min_x + self.max_x) / 2)
                
                # Outer box
                move(self.min_x, self.min_y)
                move(self.max_x, self.min_y)
                move(self.max_x, self.max_y)
                move(self.min_x, self.max_y)
                move(self.min_x, self.min_y)
                
                # Crosshair (Removed as per user request to only show border)
                # move(self.min_x, c_y)
                # move(self.max_x, c_y)
                # move(c_x, c_y)
                # move(c_x, self.min_y)
                # move(c_x, self.max_y)
                
                # Wait for the hardware to finish drawing this box before sending the next one.
                # This prevents the hardware buffer from overflowing with old boxes.
                if hasattr(self.controller.connection, 'wait_for_motion'):
                    try:
                        self.controller.connection.wait_for_motion()
                    except Exception:
                        time.sleep(0.02)
                else:
                    time.sleep(0.02)
            else:
                time.sleep(0.05)

        if has_continuous:
            dll_obj.GT_PROSYS_U3_set_continous_mode_off()
            
        if hasattr(self.controller.connection, 'reddot_off'):
            self.controller.connection.reddot_off()
