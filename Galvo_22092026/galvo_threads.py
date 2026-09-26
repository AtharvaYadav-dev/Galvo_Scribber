from PySide6.QtCore import QThread, Signal

class ExecutionThread(QThread):
    finished_signal = Signal(bool)
    progress_signal = Signal(int, int, float, float, str)
    
    def __init__(self, controller, queue, loop_count=1):
        super().__init__()
        self.controller = controller
        self.queue = queue
        self.loop_count = loop_count
        self._abort = False
        
    def abort(self):
        self._abort = True
        
    def run(self):
        import time
        self._last_update_time = 0
        
        def on_pos(i, total, x, y, ctype):
            current_time = time.time()
            is_important = ctype and str(ctype).startswith("pass_change:")
            if is_important or i == 0 or i == total - 1 or (current_time - self._last_update_time) > 0.05:
                self.progress_signal.emit(i, total, x, y, ctype)
                self._last_update_time = current_time
                
        if hasattr(self.controller, 'galvo_home'):
            self.controller.galvo_home()
            
        success = self.controller.execute_queue(
            self.queue, 
            self.loop_count, 
            progress_callback=on_pos, 
            abort_check=lambda: self._abort
        )
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
                
                # Crosshair
                move(self.min_x, c_y)
                move(self.max_x, c_y)
                move(c_x, c_y)
                move(c_x, self.min_y)
                move(c_x, self.max_y)
                
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
