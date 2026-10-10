import pytest
from pathlib import Path
from gerbyx.processor import GerberProcessor
from gerbyx.parser import GerberParser
from gerbyx.tokenizer import tokenize_gerber

# Define path to the specific file
DATA_DIR = Path(__file__).parent.parent / "data" / "88640F_Y90" / "88640F_Y90_nox2noap" / "yg"
FLASHPADS_FILE = DATA_DIR / "Flashpads-F_Cu.gbr"

print(FLASHPADS_FILE)

def test_flashpads_generation():
    """
    Test parsing of Flashpads-F_Cu.gbr which was reported as failing.
    Checks if geometries are generated.
    """
    assert FLASHPADS_FILE.exists(), f"File not found at {FLASHPADS_FILE}"

    with open(FLASHPADS_FILE, 'r') as f:
        source = f.read()

    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(source)

    # Parse
    parser.parse(tokens)

    # Debug info
    print(f"Number of layers: {len(processor.layers)}")
    for i, layer in enumerate(processor.layers):
        print(f"Layer {i}: Polarity={layer['polarity']}, Shapes={len(layer['shapes'])}")

    # Check geometries
    geometries = processor.geometries

    count = 0
    if isinstance(geometries, list):
        count = len(geometries)
    elif geometries is not None:
        if hasattr(geometries, 'geoms'):
             count = len(geometries.geoms)
        else:
             count = 1 # Single geometry

    print(f"Generated {count} geometries")
    assert count > 0, "No geometries generated for Flashpads-F_Cu.gbr"
