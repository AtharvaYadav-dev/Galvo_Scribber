import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new method
new_method = """    def mark_verification_shape(self):
        from PySide6.QtWidgets import QMessageBox, QApplication
        self.cal_is_stopped = False

        if not self.galvo_controller or not self.galvo_controller.is_connected:
            QMessageBox.warning(self, "Error", "Galvo controller is not connected.")
            return

        self.stop_cal_reddot()

        scale = 533.89
        hw = int(self.cal_default_w * scale)
        c = 32767

        min_x = c - hw
        max_x = c + hw
        min_y = c - hw
        max_y = c + hw

        conn = self.galvo_controller.connection

        if not hasattr(self, 'stagedCalibrationTransform') or not self.stagedCalibrationTransform.is_valid:
            QMessageBox.warning(self, "Error", "Please compute calibration values before marking verification shape.")
            return

        try:
            pwr = float(self.ui.powerHorizontalSlider.value()) if hasattr(self.ui, 'powerHorizontalSlider') else 100.0
            freq = float(self.ui.freqHorizontalSlider.value()) if hasattr(self.ui, 'freqHorizontalSlider') else 30.0
            mark_speed = int(self.ui.markspeedLineEdit.text()) if hasattr(self.ui, 'markspeedLineEdit') and self.ui.markspeedLineEdit.text() else 5000
            jump_speed = int(self.ui.jumpspeedLineEdit.text()) if hasattr(self.ui, 'jumpspeedLineEdit') and self.ui.jumpspeedLineEdit.text() else 15000
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid laser parameters. Using defaults.")
            pwr, freq, mark_speed, jump_speed = 100.0, 30.0, 5000, 15000

        self.galvo_controller.live_power = pwr
        self.galvo_controller.live_freq = freq

        queue = []
        
        # Apply staged calibration directly before dispatching to galvo hardware
        def jump(x, y): 
            cx, cy = self.stagedCalibrationTransform.apply(float(x), float(y))
            queue.append({'type': 'jump', 'x': int(cx), 'y': int(cy), 'speed': jump_speed})
        def mark(x, y): 
            cx, cy = self.stagedCalibrationTransform.apply(float(x), float(y))
            queue.append({'type': 'mark', 'x': int(cx), 'y': int(cy), 'speed': mark_speed})

        import math
        try:
            # 1. Outer Square (2W x 2W)
            jump(min_x, max_y)
            mark(max_x, max_y)
            mark(max_x, min_y)
            mark(min_x, min_y)
            mark(min_x, max_y)

            # 2. Vertical centerline
            jump(c, max_y)
            mark(c, min_y)

            # 3. Horizontal centerline
            jump(min_x, c)
            mark(max_x, c)
            
            # 4. Center Circle (Diameter = W)
            radius = hw // 2
            segments = 64
            jump(c + radius, c)
            for i in range(1, segments + 1):
                angle = 2 * math.pi * i / segments
                cx = c + radius * math.cos(angle)
                cy = c + radius * math.sin(angle)
                mark(cx, cy)

            if hasattr(self.ui, 'markvershapePushButton'):
                self.ui.markvershapePushButton.setEnabled(False)
            self.set_cal_status("Status : Marking Verification Shape...")

            if hasattr(conn, 'enable_calibration'):
                original_cal_state = conn.enable_calibration
                conn.enable_calibration = False # We already applied staged calibration

            success = self.galvo_controller.execute_queue(
                queue,
                loop_count=1,
                abort_check=lambda: self.cal_is_stopped,
                progress_callback=lambda idx, tot, x, y, ctype: QApplication.processEvents()
            )

            if hasattr(conn, 'enable_calibration'):
                conn.enable_calibration = original_cal_state

            if self.cal_is_stopped or not success:
                raise InterruptedError("Drawing stopped by user or failed")

            conn.laser_off()
            conn.galvo_move_xy(c, c)

            self.set_cal_status("Status : Verification Marked")
            QMessageBox.information(
                self, "Success",
                "Verification shape marked!\\n\\nPlease check the physical shape for orthogonal corners and precise dimensions."
            )
        except InterruptedError:
            self.set_cal_status("Status : Stopped")
        except Exception as e:
            self.set_cal_status("Status : Error marking verification shape")
            print(f"Error marking verification shape: {e}")

"""

pattern = r"    def mark_verification_shape\(self\):.*?    def dummy_cal_action\(self\):"
replacement = new_method + "    def dummy_cal_action(self):"

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
