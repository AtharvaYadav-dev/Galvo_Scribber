import time
from core.connection import MockConnection, HardwareConnection, log_command, flush_logs

class GalvoController:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        
    def connect(self, force_mock=False):
        if force_mock:
            self.connection = MockConnection()
            res, cards = self.connection.initialize()
            self.is_connected = self.connection.is_initialized
            return self.is_connected
            
        # Try hardware first
        hw = HardwareConnection()
        res, cards = hw.initialize()
        if hw.is_initialized:
            self.connection = hw
            self.is_connected = True
        else:
            # Fallback to mock
            self.connection = MockConnection()
            self.connection.initialize()
            self.is_connected = False # Keep as False to indicate simulator mode in UI
            
        return self.is_connected
        
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        self.is_connected = False
            
    def execute_queue(self, send_queue, loop_count=1, progress_callback=None, abort_check=None):
        """
        Executes a sequence of verified commands from the send_queue.
        """
        if not self.connection:
            print("Cannot execute, galvo connection not initialized.")
            return False

        log_command("\n" + "="*40)
        log_command(f"EXECUTION BATCH START (Loops: {loop_count})")
        log_command("="*40)
        
        print(f"Executing queue for {loop_count} loops...")
        
        start_time = time.time()
        mark_count = 0
        jump_count = 0
        
        laser_state = False  # Track current laser state
        total_cmds = len(send_queue) * loop_count
        
        for loop_idx in range(loop_count):
            for i, cmd in enumerate(send_queue):
                current_idx = (loop_idx * len(send_queue)) + i
                
                if abort_check and abort_check():
                    print("Execution aborted by user.")
                    if laser_state:
                        self.connection.laser_off()
                    return False
                    
                if self.connection and hasattr(self.connection, 'is_physically_connected'):
                    if not self.connection.is_physically_connected():
                        print("Execution aborted: hardware disconnected.")
                        if laser_state:
                            try:
                                self.connection.laser_off()
                            except:
                                pass
                        return False
                        
                # No processEvents here because we are running inside a QThread
                    
                ctype = cmd.get('type')
                
                try:
                    if ctype == 'jump':
                        jump_count += 1
                        # Jump to position with laser OFF
                        if laser_state:
                            self.connection.laser_off()
                            laser_state = False
                        self.connection.galvo_move_xy(cmd['x'], cmd['y'], cmd.get('speed'))
                        if progress_callback:
                            progress_callback(current_idx, total_cmds, cmd['x'], cmd['y'], ctype)
                        self.connection.wait_for_motion()
                    
                    elif ctype == 'mark':
                        mark_count += 1
                        # Move to position with laser ON
                        if not laser_state:
                            self.connection.laser_on()
                            laser_state = True
                        self.connection.galvo_move_xy(cmd['x'], cmd['y'], cmd.get('speed'))
                        if progress_callback:
                            progress_callback(current_idx, total_cmds, cmd['x'], cmd['y'], ctype)
                        self.connection.wait_for_motion()
                        
                    elif ctype == 'laser_on':
                        if not laser_state:
                            self.connection.laser_on()
                            laser_state = True
                        
                    elif ctype == 'laser_off':
                        if laser_state:
                            self.connection.laser_off()
                            laser_state = False
                        
                    elif ctype == 'delay':
                        ms = cmd.get('ms', 0)
                        time.sleep(ms / 1000.0)
                        
                    elif ctype == 'pass_change':
                        if progress_callback:
                            progress_callback(current_idx, total_cmds, 0, 0, f"pass_change:{cmd.get('idx', 1)}")
                except ConnectionError as e:
                    print(f"Execution aborted: {e}")
                    return False
                
        self.connection.send_buffer()
        flush_logs()
        
        end_time = time.time()
        duration = end_time - start_time
        summary = f"EXECUTION FINISHED: Sent {mark_count} Mark commands and {jump_count} Jump commands in {duration:.2f} seconds."
        log_command(summary)
        log_command("="*40 + "\n")
        print(summary)
        
        print("Queue execution complete.")
        self.connection.laser_off() # Always ensure laser is off at the end
        flush_logs()
        
        return True

    def galvo_home(self):
        """Moves the galvo mirrors to the center (home) position."""
        if not self.connection:
            return False
        self.connection.reddot_on()
        self.connection.galvo_move_xy(32767, 32767)
        self.connection.wait_for_motion()
        self.connection.reddot_off()
        return True

    def test_pattern(self):
        """Generates a simple test pattern (e.g. center, then square)"""
        if not self.connection:
            return False
            
        print("Running Test Pattern")
        
        self.connection.galvo_move_xy(32767, 32767)
        self.connection.laser_on()
        
        self.connection.galvo_move_xy(20000, 20000)
        self.connection.galvo_move_xy(40000, 20000)
        self.connection.galvo_move_xy(40000, 40000)
        self.connection.galvo_move_xy(20000, 40000)
        self.connection.galvo_move_xy(20000, 20000)
        
        self.connection.laser_off()
        self.connection.galvo_move_xy(32767, 32767)
        
        return True
