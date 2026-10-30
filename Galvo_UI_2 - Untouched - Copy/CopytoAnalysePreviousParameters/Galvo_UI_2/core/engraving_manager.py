import os
import json

DEFAULT_PRESETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "material_presets.json")

class EngravingManager:
    """
    Manages 2.5D / Deep Engraving presets, multi-layer parameters,
    and automatic calculation of Z-drop passes.
    """
    STYLE_CROSS_90 = "Cross-Hatch (90° Grid)"
    STYLE_CROSS_45 = "Cross-Hatch (45° / 135° Diamond)"
    STYLE_SPIRAL = "Concentric / Spiral Rings"
    STYLE_UNIDIRECTIONAL = "Linear Unidirectional"
    STYLE_BIDIRECTIONAL = "Linear Bidirectional"

    ALL_STYLES = [
        STYLE_CROSS_90,
        STYLE_CROSS_45,
        STYLE_SPIRAL,
        STYLE_UNIDIRECTIONAL,
        STYLE_BIDIRECTIONAL
    ]

    def __init__(self, presets_path=None):
        self.presets_path = presets_path or DEFAULT_PRESETS_FILE
        self.presets = {}
        self.load_presets()

    def load_presets(self):
        """Loads presets from the JSON file or falls back to built-ins."""
        if os.path.exists(self.presets_path):
            try:
                with open(self.presets_path, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
                    return self.presets
            except Exception as e:
                print(f"[EngravingManager] Error loading {self.presets_path}: {e}")

        # Fallback default presets
        self.presets = {
            "POM / Delrin (Hard Plastic)": {
                "power": 14.0, "frequency": 50.0, "speed": 800.0,
                "z_step": 0.05, "max_depth": 3.0,
                "hatch_style": self.STYLE_CROSS_90, "hatch_pitch": 0.04
            },
            "ABS (Hard Plastic)": {
                "power": 18.0, "frequency": 40.0, "speed": 650.0,
                "z_step": 0.05, "max_depth": 3.5,
                "hatch_style": self.STYLE_CROSS_90, "hatch_pitch": 0.05
            },
            "Acrylic / PMMA": {
                "power": 20.0, "frequency": 30.0, "speed": 500.0,
                "z_step": 0.05, "max_depth": 4.0,
                "hatch_style": self.STYLE_CROSS_45, "hatch_pitch": 0.03
            },
            "Nylon (PA)": {
                "power": 22.0, "frequency": 60.0, "speed": 700.0,
                "z_step": 0.05, "max_depth": 3.0,
                "hatch_style": self.STYLE_UNIDIRECTIONAL, "hatch_pitch": 0.05
            },
            "Polycarbonate (PC)": {
                "power": 12.0, "frequency": 45.0, "speed": 900.0,
                "z_step": 0.04, "max_depth": 3.0,
                "hatch_style": self.STYLE_SPIRAL, "hatch_pitch": 0.05
            },
            "Aluminium": {
                "power": 90.0, "frequency": 30.0, "speed": 500.0,
                "z_step": 0.02, "max_depth": 2.0,
                "hatch_style": self.STYLE_CROSS_90, "hatch_pitch": 0.03
            },
            "Brass / Copper": {
                "power": 95.0, "frequency": 25.0, "speed": 450.0,
                "z_step": 0.02, "max_depth": 2.0,
                "hatch_style": self.STYLE_CROSS_45, "hatch_pitch": 0.025
            },
            "Stainless Steel / Steel": {
                "power": 85.0, "frequency": 35.0, "speed": 400.0,
                "z_step": 0.015, "max_depth": 2.0,
                "hatch_style": self.STYLE_CROSS_90, "hatch_pitch": 0.02
            }
        }
        self.save_presets()
        return self.presets

    def save_presets(self):
        """Saves current presets to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.presets_path), exist_ok=True)
            with open(self.presets_path, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2)
            return True
        except Exception as e:
            print(f"[EngravingManager] Error saving presets: {e}")
            return False

    def add_or_update_preset(self, name, power, frequency, speed, z_step, max_depth=5.0, hatch_style=None, hatch_pitch=0.04):
        """Adds a new custom material preset or updates an existing one."""
        name = str(name).strip()
        if not name:
            return False
            
        self.presets[name] = {
            "power": float(power),
            "frequency": float(frequency),
            "speed": float(speed),
            "z_step": max(0.005, min(0.5, float(z_step))),
            "max_depth": min(5.0, max(0.1, float(max_depth))),
            "hatch_style": hatch_style or self.STYLE_CROSS_90,
            "hatch_pitch": float(hatch_pitch)
        }
        self.save_presets()
        return True

    def delete_preset(self, name):
        """Removes a preset if present."""
        if name in self.presets:
            del self.presets[name]
            self.save_presets()
            return True
        return False

    @staticmethod
    def calculate_loops(target_depth, z_step):
        """
        Calculates required loop passes from target depth and z-step.
        Clamped to safety limits (max 5.0 mm depth).
        """
        try:
            depth = max(0.01, min(5.0, float(target_depth)))
            step = max(0.005, min(0.5, float(z_step)))
            loops = int(round(depth / step))
            return max(1, loops)
        except (ValueError, ZeroDivisionError):
            return 1

    @staticmethod
    def get_hatch_config_for_style(style_name, hatch_pitch=0.04):
        """
        Generates standard hatching configuration parameters for the chosen engraving pattern.
        """
        style = str(style_name)
        if style == EngravingManager.STYLE_CROSS_90:
            return {
                "enable": True,
                "type": "Bidirectional",
                "cross_hatch": True,
                "angle": 0.0,
                "line_space": hatch_pitch,
                "count": 1
            }
        elif style == EngravingManager.STYLE_CROSS_45:
            return {
                "enable": True,
                "type": "Bidirectional",
                "cross_hatch": True,
                "angle": 45.0,
                "line_space": hatch_pitch,
                "count": 1
            }
        elif style == EngravingManager.STYLE_SPIRAL:
            return {
                "enable": True,
                "type": "Ring-like",
                "cross_hatch": False,
                "angle": 0.0,
                "line_space": hatch_pitch,
                "count": 1
            }
        elif style == EngravingManager.STYLE_UNIDIRECTIONAL:
            return {
                "enable": True,
                "type": "Unidirectional",
                "cross_hatch": False,
                "angle": 0.0,
                "line_space": hatch_pitch,
                "count": 1
            }
        else: # Bidirectional default
            return {
                "enable": True,
                "type": "Bidirectional",
                "cross_hatch": False,
                "angle": 0.0,
                "line_space": hatch_pitch,
                "count": 1
            }
