import pytest
from pathlib import Path
from shapely.geometry import Point
from gerbyx.processor import GerberProcessor
from gerbyx.parser import GerberParser
from gerbyx.tokenizer import tokenize_gerber

# Define path to the specific regression file
DATA_DIR = Path(__file__).parent.parent / "data" / "smoker_gerbers"
REGRESSION_FILE = DATA_DIR / "board_beta_affumicatore-B_Cu.gbr"

def test_kicad_x3_attributes_and_negative_macro_params():
    """
    Regression test for KiCad 9 X3 files.
    Verifies:
    1. Handling of pending aperture attributes (%TA% before %ADD%).
    2. Correct parsing of negative numbers in macro parameters (fixing the "quarter pad" bug).
    """
    assert REGRESSION_FILE.exists(), f"Regression file not found at {REGRESSION_FILE}"

    with open(REGRESSION_FILE, 'r') as f:
        source = f.read()

    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(source)

    # This should not raise warnings about "active aperture" (captured in logs/stdout normally)
    parser.parse(tokens)

    # Verify D12 (RoundRect) geometry dimensions.
    # In the file: %ADD12RoundRect,0.250000X-0.750000X0.600000X...*%
    # Radius $1 = 0.25
    # Corners X coords are -0.75 and 0.75.
    # Corners Y coords are -0.60 and 0.60.
    # The shape is built with circles at corners.
    # Min X = -0.75 - 0.25 = -1.0
    # Max X = 0.75 + 0.25 = 1.0
    # Width = 2.0
    # Height = (0.60 - (-0.60)) + 2*0.25 = 1.2 + 0.5 = 1.7.

    # D12 is flashed at X211768750Y-58000000D03* -> (211.76875, -58.0)
    target_x = 211.76875
    target_y = -58.0

    found_shape = None

    # Search in raw shapes BEFORE union (because union merges touching pads/planes)
    # processor.layers is a list of dicts: {'polarity': 'dark', 'shapes': [...]}

    # Collect all shapes from all layers
    all_shapes = []
    for layer in processor.layers:
        all_shapes.extend(layer['shapes'])

    for geom in all_shapes:
        if geom.contains(Point(target_x, target_y)):
            # Check if this shape is "close enough" to the expected size
            # to distinguish it from a giant ground plane that might also contain the point.
            # We expect a small pad ~2.0 x 1.7
            minx, miny, maxx, maxy = geom.bounds
            w = maxx - minx
            h = maxy - miny
            if w < 5.0 and h < 5.0: # Arbitrary small limit to filter out big planes
                found_shape = geom
                break

    assert found_shape is not None, f"Could not find isolated geometry at ({target_x}, {target_y})"

    # Check bounds
    minx, miny, maxx, maxy = found_shape.bounds
    width = maxx - minx
    height = maxy - miny

    # Allow some tolerance for floating point arithmetic
    assert abs(width - 2.0) < 0.01, f"Expected width ~2.0, got {width}"
    assert abs(height - 1.7) < 0.01, f"Expected height ~1.7, got {height}"

    # Also verify that attributes were correctly assigned (internally)
    # D12 should have AperFunction=ComponentPad
    # Note: aperture IDs are strings in processor state and include 'D' prefix (e.g., 'D12')
    d12_attrs = processor.aperture_attributes.get('D12', {})
    assert d12_attrs.get('AperFunction') == 'ComponentPad', "Attribute AperFunction not correctly assigned to D12"
