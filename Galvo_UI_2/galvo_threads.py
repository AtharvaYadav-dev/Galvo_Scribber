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
                is_important = ctype and (str(ctype).startswith("pass_change:") or str(ctype).startswith("3d_layer:"))
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
                    is_important = ctype and (str(ctype).startswith("pass_change:") or str(ctype).startswith("3d_layer:"))
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
    def __init__(self, controller, min_x, max_x, min_y, max_y, shape='rect'):
        super().__init__()
        self.controller = controller
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.shape = shape
        self.running = True
        self.needs_refresh = False
        
    def update_bounds(self, min_x, max_x, min_y, max_y, shape=None):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        if shape is not None:
            self.shape = shape
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
        import math
        
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
                
                if getattr(self, 'shape', 'rect') == 'circle':
                    r = int(abs(self.max_x - self.min_x) / 2)
                    num_pts = 36
                    for i in range(num_pts + 1):
                        theta = 2.0 * math.pi * (i % num_pts) / float(num_pts)
                        px = int(c_x + r * math.cos(theta))
                        py = int(c_y + r * math.sin(theta))
                        move(px, py)
                else:
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


class Slicing3DThread(QThread):
    """
    Background worker thread for asynchronous 3D relief slicing.
    Compiles 3D G-code, STL, DXF, or Heightmap toolpaths without freezing the GUI.
    """
    finished_signal = Signal(bool, list, list, str, tuple) # success, queue, layers, error_msg, cache_key
    progress_signal = Signal(str)

    def __init__(
        self,
        filepath,
        field_sz=100.0,
        depth=0.75,
        passes=50,
        pitch=0.025,
        mode="3D Coin Relief",
        clean_int=0,
        target_size_mm=27.0,
        width_mm=None,
        height_mm=None,
        laser_power=None,
        laser_freq=None,
        mark_speed_mms=None,
        jump_speed_mms=None,
        offset_x_mm=0.0,
        offset_y_mm=0.0,
        boundary_mode='auto',
        bidirectional=True,
        enable_contour=True,
        invert_relief=False,
        cache_key=None
    ):
        super().__init__()
        import os
        self.filepath = filepath
        self.field_sz = float(field_sz)
        self.depth = float(depth)
        self.passes = int(passes)
        self.pitch = float(pitch)
        self.mode = str(mode)
        self.clean_int = int(clean_int)
        self.target_size_mm = float(target_size_mm) if target_size_mm else 27.0
        self.width_mm = float(width_mm) if width_mm is not None else None
        self.height_mm = float(height_mm) if height_mm is not None else None
        self.laser_power = float(laser_power) if laser_power is not None else None
        self.laser_freq = float(laser_freq) if laser_freq is not None else None
        self.mark_speed_mms = float(mark_speed_mms) if mark_speed_mms is not None else None
        self.jump_speed_mms = float(jump_speed_mms) if jump_speed_mms is not None else None
        self.offset_x_mm = float(offset_x_mm)
        self.offset_y_mm = float(offset_y_mm)
        self.boundary_mode = str(boundary_mode)
        self.bidirectional = bool(bidirectional)
        self.enable_contour = bool(enable_contour)
        self.invert_relief = bool(invert_relief)

        self.cache_key = cache_key or (
            filepath, depth, passes, pitch, mode, clean_int,
            self.target_size_mm, self.laser_power, self.laser_freq,
            self.mark_speed_mms, self.offset_x_mm, self.offset_y_mm,
            self.invert_relief
        )

    def run(self):
        import os
        try:
            self.progress_signal.emit(f"Slicing 3D model ({self.mode})...")
            fp = self.filepath
            if not fp or not os.path.exists(fp):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fp = os.path.join(base_dir, "DeepEngrave", "rupee_10_coin_27mm_relief_16bit.png")

            if fp.lower().endswith(('.gcode', '.nc', '.tap', '.gco')) or "G-Code" in self.mode:
                from core.gcode_3d_adapter import GCode3DAdapter
                adapter = GCode3DAdapter(
                    gcode_path=fp,
                    field_size=self.field_sz,
                    target_diameter_mm=self.target_size_mm,
                    mark_speed_mms=self.mark_speed_mms or 800.0,
                    jump_speed_mms=self.jump_speed_mms or 2000.0,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    target_passes=self.passes,
                    offset_x_mm=self.offset_x_mm,
                    offset_y_mm=self.offset_y_mm
                )
                q = adapter.compile_job_queue(
                    mark_speed_mms=self.mark_speed_mms,
                    jump_speed_mms=self.jump_speed_mms,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    clean_interval=self.clean_int,
                    target_passes=self.passes
                )
                layers = getattr(adapter, 'layers', [])

            elif fp.lower().endswith(('.stl', '.obj')) or "3D Mesh / STL" in self.mode:
                from core.stl_3d_engraver import STL3DEngraver
                engraver = STL3DEngraver(
                    stl_path=fp,
                    diameter_mm=self.target_size_mm,
                    width_mm=self.width_mm,
                    height_mm=self.height_mm,
                    max_depth_mm=self.depth,
                    num_layers=self.passes,
                    field_size=self.field_sz,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    mark_speed_mms=self.mark_speed_mms,
                    jump_speed_mms=self.jump_speed_mms,
                    offset_x_mm=self.offset_x_mm,
                    offset_y_mm=self.offset_y_mm,
                    boundary_mode=self.boundary_mode,
                    bidirectional=self.bidirectional,
                    enable_contour=self.enable_contour,
                    invert_relief=self.invert_relief
                )
                q = engraver.compile_job_queue(
                    hatch_pitch_mm=self.pitch,
                    clean_interval=self.clean_int,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    mark_speed_mms=self.mark_speed_mms,
                    jump_speed_mms=self.jump_speed_mms
                )
                layers = getattr(engraver, 'layers', [])

            elif "Multi-Layer Vector" in self.mode or fp.lower().endswith(('.dxf', '.svg')):
                from core.coin_3d_engraver import Coin3DReliefEngraver
                pwr_scale = (self.laser_power / 70.0) if self.laser_power else 1.0
                spd_scale = (self.mark_speed_mms / 500.0) if self.mark_speed_mms else 1.0
                engraver = Coin3DReliefEngraver(
                    dxf_path=fp,
                    field_size=self.field_sz,
                    offset_x_mm=self.offset_x_mm,
                    offset_y_mm=self.offset_y_mm,
                    power_scale=pwr_scale,
                    speed_scale=spd_scale,
                    bidirectional=self.bidirectional
                )
                q = engraver.compile_job_queue()
                layers = getattr(engraver, 'layers', [])

            else:
                from core.heightmap_slicer import Heightmap3DSlicer
                slicer = Heightmap3DSlicer(
                    heightmap_path=fp,
                    diameter_mm=self.target_size_mm,
                    width_mm=self.width_mm,
                    height_mm=self.height_mm,
                    max_depth_mm=self.depth,
                    num_layers=self.passes,
                    field_size=self.field_sz,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    mark_speed_mms=self.mark_speed_mms,
                    jump_speed_mms=self.jump_speed_mms,
                    offset_x_mm=self.offset_x_mm,
                    offset_y_mm=self.offset_y_mm,
                    boundary_mode=self.boundary_mode,
                    bidirectional=self.bidirectional,
                    enable_contour=self.enable_contour,
                    invert_relief=self.invert_relief
                )
                q = slicer.compile_sliced_3d_queue(
                    hatch_pitch_mm=self.pitch,
                    clean_interval=self.clean_int,
                    laser_power=self.laser_power,
                    laser_freq=self.laser_freq,
                    mark_speed_mms=self.mark_speed_mms,
                    jump_speed_mms=self.jump_speed_mms
                )
                layers = getattr(slicer, 'layers', [])

            self.finished_signal.emit(True, q, layers, "", self.cache_key)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished_signal.emit(False, [], [], str(e), self.cache_key)
