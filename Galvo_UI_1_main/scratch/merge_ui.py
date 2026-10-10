import re

def merge():
    ref_path = "d:/Atharva/Metal_3D/New_Galvo_Cal/Referance/GalvoUI_08092026/GalvoUI_with_calibration_page/GalvoUI_with_calibration_page/core/calibration_generator_ui.py"
    our_path = "d:/Atharva/Metal_3D/New_Galvo_Cal/core/calibration_generator_ui.py"
    out_path = "d:/Atharva/Metal_3D/New_Galvo_Cal/core/calibration_generator_ui.py.new"
    
    with open(ref_path, "r", encoding="utf-8") as f:
        ref_content = f.read()
        
    with open(our_path, "r", encoding="utf-8") as f:
        our_content = f.read()
        
    # 1. Get the top part of our file to get TRANSFORMS
    our_top = our_content[:our_content.find("class GridPreviewWidget")]
    
    # 2. Get the reference layout up to the end of next_state
    # We will grab from start up to def stop_all(self):
    ref_layout_part = ref_content[:ref_content.find("    def stop_all(self):")]
    
    # 3. We need to replace the __init__ signature to match ours, so it doesn't break external calls
    ref_layout_part = ref_layout_part.replace(
        "def __init__(self, galvo_controller, parent=None, config_handler=None, main_window=None):",
        "def __init__(self, galvo_controller, parent=None):"
    )
    
    # Replace references to self.main_window with None for safety (since we removed it from init)
    # Actually, if we just remove the main_window init lines it's better.
    ref_layout_part = ref_layout_part.replace(
        "        self.config_handler = config_handler\n        self.main_window = main_window",
        "        self.main_window = None"
    )
    
    # Also hook up the buttons to our methods
    ref_layout_part = ref_layout_part.replace(
        "self.btn_stop.clicked.connect(self.stop_all)",
        "self.btn_stop.clicked.connect(self.stop_pattern)"
    )
    ref_layout_part = ref_layout_part.replace(
        "self.btn_calculate.clicked.connect(self.calculate_and_apply)",
        "self.btn_calculate.clicked.connect(self.generate)"
    )
    # btn_verify -> just connect to a dummy method
    ref_layout_part = ref_layout_part.replace(
        "self.btn_verify.clicked.connect(self.mark_verification_shape)",
        "self.btn_verify.clicked.connect(self.dummy_action)"
    )
    # btn_reddot -> dummy method
    ref_layout_part = ref_layout_part.replace(
        "self.btn_reddot.clicked.connect(self.toggle_reddot_framing)",
        "self.btn_reddot.clicked.connect(self.dummy_action)"
    )
    
    # 4. Extract our functionality methods
    our_methods_start = our_content.find("    def stop_pattern(self):")
    our_methods = our_content[our_methods_start:]
    
    # Modify our draw_pattern to use slider values
    our_methods = our_methods.replace(
        "pwr = float(self.input_power.text())",
        "pwr = float(self.slider_power.value())"
    )
    our_methods = our_methods.replace(
        "freq = float(self.input_freq.text())",
        "freq = float(self.slider_freq.value())"
    )
    
    # Add dummy_action
    dummy_code = """
    def dummy_action(self):
        QMessageBox.information(self, "Info", "This feature is not implemented in the current functionality.")
"""

    # 5. Combine everything
    # But wait, our_top has imports. ref_layout_part also has imports. Let's keep ref_layout_part imports, 
    # and just extract TRANSFORMS and TRANSFORMS_MATH from our_top.
    transforms_code = ""
    if "TRANSFORMS =" in our_top:
        idx1 = our_top.find("TRANSFORMS =")
        transforms_code = our_top[idx1:]
        
    # Put transforms after EZCAD_ORIENTATIONS
    ref_layout_part = ref_layout_part.replace(
        "class GridPreviewWidget(QWidget):",
        transforms_code + "\nclass GridPreviewWidget(QWidget):"
    )

    final_content = ref_layout_part + dummy_code + our_methods
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_content)
        
    print(f"Merged file written to {out_path}")

merge()
