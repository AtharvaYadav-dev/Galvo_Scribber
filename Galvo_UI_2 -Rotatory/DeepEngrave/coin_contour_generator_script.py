#!/usr/bin/env python3
"""
Industrial Coin Relief Contour Generator
Generates dual-format outputs (Stepped Layered DXF and Multi-Layer SVG)
calibrated for 3D Galvo Laser Relief Engraving (EZCad / LightBurn).

Dependencies:
    pip install ezdxf svgwrite
"""

import math
import sys
import os

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    ezdxf = None

try:
    import svgwrite
except ImportError:
    svgwrite = None


class CoinReliefGenerator:
    def __init__(self, diameter_mm=27.0, bimetal_ring_mm=18.0, rim_width_mm=0.8):
        self.dia = diameter_mm
        self.radius = diameter_mm / 2.0
        self.center = (self.radius, self.radius)
        self.bimetal_r = bimetal_ring_mm / 2.0
        self.rim_width = rim_width_mm

        # Standard industrial galvo relief depth layer palette
        self.layers = [
            {"id": "LAYER_00_BASE_FIELD", "color_hex": "#000000", "dxf_aci": 7, "depth_um": 500},
            {"id": "LAYER_01_BIMETAL_GROOVE", "color_hex": "#0000FF", "dxf_aci": 5, "depth_um": 400},
            {"id": "LAYER_02_LOWER_BEVEL", "color_hex": "#00FFFF", "dxf_aci": 4, "depth_um": 300},
            {"id": "LAYER_03_MID_RELIEF", "color_hex": "#00AA00", "dxf_aci": 3, "depth_um": 200},
            {"id": "LAYER_04_HIGH_RELIEF", "color_hex": "#FF8800", "dxf_aci": 2, "depth_um": 100},
            {"id": "LAYER_05_CREST_SURFACE", "color_hex": "#FF0000", "dxf_aci": 1, "depth_um": 0},
        ]

    def generate_dxf(self, filename="rupee_10_relief_27mm.dxf"):
        if ezdxf is None:
            print("ezdxf is not installed. Run 'pip install ezdxf' to export DXF.")
            return

        doc = ezdxf.new(dxfversion="R2010")
        msp = doc.modelspace()

        # Setup layers with proper AutoCAD Color Index (ACI)
        for lyr in self.layers:
            doc.layers.add(name=lyr["id"], color=lyr["dxf_aci"])

        cx, cy = self.center

        # Layer 00: Outer boundaries and base field
        l0 = "LAYER_00_BASE_FIELD"
        msp.add_circle((cx, cy), self.radius, dxfattribs={"layer": l0})
        msp.add_circle((cx, cy), self.radius - self.rim_width * 0.5, dxfattribs={"layer": l0})
        msp.add_circle((cx, cy), self.radius - self.rim_width, dxfattribs={"layer": l0})

        # Layer 01: Bi-metallic groove step
        l1 = "LAYER_01_BIMETAL_GROOVE"
        for offset in [-0.15, 0.0, 0.15]:
            msp.add_circle((cx, cy), self.bimetal_r + offset, dxfattribs={"layer": l1})

        # Layer 02 to 05: Concentric offset contours for digits '1' and '0'
        # Simulating stepped draft angles (relief bevel)
        digit_offsets = [0.35, 0.20, 0.10, 0.0]
        layer_ids = [
            "LAYER_02_LOWER_BEVEL",
            "LAYER_03_MID_RELIEF",
            "LAYER_04_HIGH_RELIEF",
            "LAYER_05_CREST_SURFACE",
        ]

        for step, l_id in zip(digit_offsets, layer_ids):
            # Digit '1' stepped polyline
            p_one = [
                (cx - 3.2 - step, cy - 1.0 - step),
                (cx - 2.0, cy + 0.4 + step),
                (cx - 1.4 + step, cy + 0.4 + step),
                (cx - 1.4 + step, cy - 6.0 + step),
                (cx - 0.5 + step, cy - 6.0 + step),
                (cx - 0.5 + step, cy - 6.6 - step),
                (cx - 4.1 - step, cy - 6.6 - step),
                (cx - 4.1 - step, cy - 6.0 + step),
                (cx - 2.7 - step, cy - 6.0 + step),
                (cx - 2.7 - step, cy - 1.0 - step),
            ]
            msp.add_lwpolyline(p_one, close=True, dxfattribs={"layer": l_id})

            # Digit '0' stepped outer and inner ellipses
            msp.add_ellipse(
                center=(cx + 4.1, cy - 3.0),
                major_axis=(0, 4.0 + step),
                ratio=(2.3 + step) / (4.0 + step),
                dxfattribs={"layer": l_id},
            )
            inner_maj = max(0.2, 2.5 - step)
            inner_min = max(0.1, 1.1 - step)
            msp.add_ellipse(
                center=(cx + 4.1, cy - 3.0),
                major_axis=(0, inner_maj),
                ratio=inner_min / inner_maj,
                dxfattribs={"layer": l_id},
            )

        doc.saveas(filename)
        print(f"Successfully generated industrial DXF: {filename}")

    def generate_svg(self, filename="rupee_10_relief_27mm_generated.svg"):
        if svgwrite is None:
            print("svgwrite is not installed. Run 'pip install svgwrite' to export SVG.")
            return

        dwg = svgwrite.Drawing(
            filename,
            size=(f"{self.dia}mm", f"{self.dia}mm"),
            viewBox=f"0 0 {self.dia:.3f} {self.dia:.3f}",
        )

        cx, cy = self.center

        for lyr in self.layers:
            g = dwg.g(id=lyr["id"], stroke=lyr["color_hex"], fill="none", stroke_width=0.05)

            if lyr["id"] == "LAYER_00_BASE_FIELD":
                g.add(dwg.circle(center=(cx, cy), r=self.radius))
                g.add(dwg.circle(center=(cx, cy), r=self.radius - self.rim_width * 0.5))
                g.add(dwg.circle(center=(cx, cy), r=self.radius - self.rim_width))
            elif lyr["id"] == "LAYER_01_BIMETAL_GROOVE":
                for offset in [-0.15, 0.0, 0.15]:
                    g.add(dwg.circle(center=(cx, cy), r=self.bimetal_r + offset))

            dwg.add(g)

        dwg.save()
        print(f"Successfully generated calibrated SVG: {filename}")


if __name__ == "__main__":
    generator = CoinReliefGenerator(diameter_mm=27.0, bimetal_ring_mm=18.0)
    generator.generate_dxf("rupee_10_relief_27mm.dxf")
    generator.generate_svg("rupee_10_relief_27mm_generated.svg")