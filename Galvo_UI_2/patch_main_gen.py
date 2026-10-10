import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace generate_cor_file part with NinePointCalibration logic
pattern = r"            generate_cor_file\("staged_calibration.cor", scale, self.cal_default_w, galvo_measurements\).*?self.set_cal_status\(f"Status : Calibration Computed \(Ready to Verify\)"\)"

replacement = """            from core.calibration_engine import NinePointCalibration
            self.stagedCalibrationTransform = NinePointCalibration(self.cal_default_w, galvo_measurements)
            self.stagedCalibrationTransform.save("staged_calibration.json")
            loaded_ok = True

            self.set_cal_status(f"Status : Calibration Computed (Ready to Verify)")"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
