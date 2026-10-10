# 🔄 Step & Repeat + GeoJSON Export

## New Features Implemented

### 1. Step & Repeat (SR) Support

**Standard:** Gerber X2 (deprecated in X3 but still supported)

#### What is Step & Repeat?

Step & Repeat allows repeating a pattern multiple times with specified offsets, commonly used for panelization.

#### Syntax
```gerber
SRX<n>Y<m>I<x_step>J<y_step>*  # Enable with parameters
SR*                             # Disable
```

#### Example
```gerber
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX3Y2I10.0J5.0*  # Repeat 3x2 with 10mm x-step, 5mm y-step
D10*
X0Y0D03*          # This flash will be repeated 6 times
SR*               # Disable step & repeat
```

#### Implementation

**Parser (`parser.py`):**
- Parses `SR` command
- Extracts repeat counts and step sizes
- Calls `processor.set_step_repeat()`

**Processor (`processor.py`):**
- Stores Step & Repeat state
- Applies repetition in `_add_shape()`
- Translates each shape by offset

**Usage:**
```python
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor

gerber_with_sr = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y2I5.0J5.0*
D10*
X0Y0D03*
SR*
M02*
"""

processor = GerberProcessor()
parser = GerberParser(processor)
tokens = tokenize_gerber(gerber_with_sr)
parser.parse(tokens)

# Result: 4 circles (2x2 grid with 5mm spacing)
geometries = processor.geometries
```

---

### 2. GeoJSON Export (CLI)

**Format:** GeoJSON FeatureCollection

#### CLI Usage

```bash
# Export to GeoJSON
gerbyx input.gbr --output output.geojson

# Export and show plot
gerbyx input.gbr -o output.geojson --show

# Just show plot (no export)
gerbyx input.gbr --show
```

#### GeoJSON Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[x1, y1], [x2, y2], ...]]
      },
      "properties": {
        "index": 0
      }
    }
  ]
}
```

#### Programmatic Usage

```python
import json
from shapely.geometry import mapping
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor

# Parse Gerber
processor = GerberProcessor()
parser = GerberParser(processor)
tokens = tokenize_gerber(gerber_source)
parser.parse(tokens)

# Export to GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {"index": i}
        }
        for i, geom in enumerate(processor.geometries)
    ]
}

with open('output.geojson', 'w') as f:
    json.dump(geojson_data, f, indent=2)
```

---

## Testing

### Test Step & Repeat

```python
# Create test script
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor

gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX3Y2I10.0J5.0*
D10*
X0Y0D03*
SR*
M02*
"""

processor = GerberProcessor()
parser = GerberParser(processor)
tokens = tokenize_gerber(gerber)
parser.parse(tokens)

geometries = processor.geometries
print(f"Generated {len(geometries)} geometries")
# Expected: 6 (3x2 grid)
```

### Test GeoJSON Export

```bash
# From project root
cd src
python -m gerbyx.cli ../data/copper_top.gbr -o test.geojson
```

---

## Performance Impact

### Step & Repeat
- **Overhead:** Minimal (only when SR active)
- **Memory:** Linear with repeat count
- **Speed:** O(n*m) where n,m are repeat counts

### GeoJSON Export
- **Overhead:** Negligible (uses Shapely's `mapping()`)
- **File size:** Depends on geometry complexity
- **Speed:** Fast (JSON serialization)

---

## Compatibility

### Step & Repeat
- ✅ Gerber X2 standard
- ⚠️ Deprecated in X3 (but still supported)
- ✅ Backward compatible

### GeoJSON
- ✅ Standard GeoJSON format
- ✅ Compatible with QGIS, Mapbox, Leaflet
- ✅ Human-readable JSON

---

## Limitations

### Step & Repeat
- Only rectangular grids (X/Y repeat)
- No rotation support
- Applies to all subsequent operations until disabled

### GeoJSON
- No layer information preserved
- No aperture metadata
- Coordinates in Gerber units (usually mm)

---

## Future Enhancements

### Step & Repeat
- [ ] Rotation parameter support
- [ ] Nested step & repeat
- [ ] Validation warnings for X3 files

### GeoJSON
- [ ] Layer metadata in properties
- [ ] Aperture information
- [ ] CRS (Coordinate Reference System) support
- [ ] Compressed GeoJSON (.geojsonl)

---

## Examples

### Example 1: Panelization

```gerber
%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.5*%

# Create 2x3 panel with 50mm spacing
SRX2Y3I50.0J50.0*

# Draw PCB outline
G01*
D10*
X0Y0D02*
X40000Y0D01*
X40000Y30000D01*
X0Y30000D01*
X0Y0D01*

SR*  # Disable
M02*
```

### Example 2: Export to GeoJSON

```bash
# Process and export
gerbyx panel.gbr -o panel.geojson

# View in QGIS or any GIS tool
```

---

## Documentation

- **Step & Repeat:** See Gerber X2 specification section 4.9
- **GeoJSON:** See https://geojson.org/
- **CLI:** Run `gerbyx --help` for all options

---

**Version:** 2.3 (Step & Repeat + GeoJSON)  
**Status:** ✅ IMPLEMENTED AND TESTED  
**Compatibility:** Gerber X2/X3, GeoJSON RFC 7946
