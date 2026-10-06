import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


class CameraThread(QThread):
    frame_update = Signal(QImage)
    error_occurred = Signal(str)

    def __init__(self, cam_index, device_name="AV TO USB2.0"):
        super().__init__()
        self.cam_index = cam_index
        self.device_name = device_name
        self.running = False

    def run(self):
        self.running = True
        cap = None
        target_name = self.device_name

        try:
            # open using DirectShow (MUCH faster)
            cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)

            import time
            t0 = time.time()
            while not cap.isOpened():
                if time.time() - t0 > 2:  # increased timeout slightly
                    self.error_occurred.emit("Camera failed to open (timeout).")
                    return
                time.sleep(0.1)  # avoid CPU spin

            # force raw analog format
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUY2"))
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 576)
            cap.set(cv2.CAP_PROP_FPS, 25)

            # flush old frames
            for _ in range(5):
                if not self.running: break
                cap.grab()

            from pygrabber.dshow_graph import FilterGraph
            consecutive_failures = 0
            last_hw_check = time.time()
            
            while self.running:
                # Periodic hardware check every 2 seconds
                if time.time() - last_hw_check > 2.0:
                    try:
                        devices = FilterGraph().get_input_devices()
                        if target_name not in devices:
                            self.error_occurred.emit("Camera is been disconnected")
                            break
                    except:
                        pass # Ignore temporary graph errors
                    last_hw_check = time.time()

                if not cap.isOpened():
                    self.error_occurred.emit("Camera is been disconnected")
                    break

                ret, frame = cap.read()
                if not ret or frame is None:
                    consecutive_failures += 1
                    if consecutive_failures > 30:  # ~1.2 seconds of failure
                        self.error_occurred.emit("Camera is been disconnected")
                        break
                    time.sleep(0.01)
                    continue
                
                consecutive_failures = 0

                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2
                
                # Draw Small Red Crosshair (BGR: (0, 0, 255))
                # Length of 20px from center
                size = 50
                cv2.line(frame, (cx - size, cy), (cx + size, cy), (0, 0, 255), 1)
                cv2.line(frame, (cx, cy - size), (cx, cy + size), (0, 0, 255), 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                self.frame_update.emit(qt_img)

        except Exception as e:
            self.error_occurred.emit(f"Critical Camera Error: {str(e)}")

        finally:
            if cap and cap.isOpened():
                cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
