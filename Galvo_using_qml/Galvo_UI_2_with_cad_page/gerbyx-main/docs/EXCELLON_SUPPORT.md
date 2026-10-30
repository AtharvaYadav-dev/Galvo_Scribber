# Excellon Drill File Support

gerbyx supports Excellon drill files alongside Gerber files with a **completely
separate parallel pipeline** — no shared code with Gerber processing.

The output interface is **intentionally identical** to the Gerber pipeline:
`process_file()` returns a `ProcessResult` whose `.geometries` attribute is a
list of Shapely geometry objects, built directly from the Excellon primitives
using `Point.buffer` and `LineString.buffer` — the same approach used for
Gerber flashes and draws.

## Quick Start

```python
from gerbyx.dispatcher import process_file

# Auto-detect format (Gerber or Excellon)
result = process_file("board.drl", output_units="MM")

# Shapely geometries — same interface as Gerber
for geom in result.geometries:
    print(geom.geom_type, geom.area)

# Access raw primitives for metadata (tool number, diameter, plating, …)
for prim, geom in zip(result.primitives, result.geometries):
    print(prim.tool_number, prim.diameter_mm, geom.area)
```

```bash
# CLI — auto-detect
gerbyx board.drl --output board_drill.geojson

# Force format + output units
gerbyx board.drl --format excellon --output-units mm

# Inch file with ambiguous/no unit declaration
gerbyx old_board.drl --units inch --output board_mm.geojson

# Fine arc segmentation (routing paths only)
gerbyx routed.drl --arc-tolerance 0.005 --max-arc-segments 256


# Generate benchmark images and timing report for repository samples
python scripts/bench_excellon.py
```

---

## Supported Standard Coverage

### Header commands
| Command | Description | Supported |
|---------|-------------|-----------|
| `M48` | Header start | ✅ |
| `%` / `M95` | Header end | ✅ |
| `METRIC` / `INCH` | Unit declaration | ✅ |
| `METRIC,LZ` / `INCH,TZ` | Unit + zero suppression | ✅ |
| `METRIC,LZ,000.000` | Unit + ZS + explicit format | ✅ |
| `FMAT,1` / `FMAT,2` | Format version | ✅ |
| `VER,n` | Format version (alternate) | ✅ |

### Tool definitions
| Command | Description | Supported |
|---------|-------------|-----------|
| `TnnCd` | Tool n, diameter d | ✅ |
| `TnnCdFf` | With feed rate | ✅ |
| `TnnCdFfSs` | With feed + spindle speed | ✅ |
| `TnnCdBbHhZz` | With retract/depth params | ✅ |
| `Tnn` | Tool selection | ✅ |
| `T00` | Deselect / end routing | ✅ |

### Drill operations
| Command | Description | Supported |
|---------|-------------|-----------|
| `XnYn` | Drill hit | ✅ |
| `XnYn` (with decimal) | Drill with explicit decimal | ✅ |
| `RnXdxYdy` | Repeat last drill n times | ✅ |
| `G81` / `G82` / `G83` | Drill canned cycles (as simple drill) | ✅ |

### Slot operations
| Command | Description | Supported |
|---------|-------------|-----------|
| `X{xs}Y{ys}G85X{xe}Y{ye}` | Canned slot (explicit start) | ✅ |
| `G85X{xe}Y{ye}` | Canned slot (from current position) | ✅ |

### Routing operations
| Command | Description | Supported |
|---------|-------------|-----------|
| `G00Xn Yn` | Rapid reposition (enter route mode) | ✅ |
| `G01XnYn` | Linear route cut | ✅ |
| `G02XnYnA{r}` | Arc CW — A style (radius) | ✅ |
| `G02XnYnR{r}` | Arc CW — R style (radius) | ✅ |
| `G02XnYnI{i}J{j}` | Arc CW — I/J center offset | ✅ |
| `G03XnYnA{r}` | Arc CCW — A style | ✅ |
| `G03XnYnI{i}J{j}` | Arc CCW — I/J center offset | ✅ |
| `G05` | Return to drill mode | ✅ |
| `G90` / `G91` | Absolute / incremental mode | ✅ |

### Program control
| Command | Description | Supported |
|---------|-------------|-----------|
| `M30` / `M00` | Program end | ✅ |
| `M02` | File end (Gerber-compatible) | ✅ |
| `;comment` | Line comment | ✅ |
| `;PTH` / `;NPTH` / `;VIA` | KiCad plating hints in comments | ✅ |

---

## Unit Handling

### Policy
- **Output unit is always MM by default** regardless of input.
- Override with `--output-units inch` if needed.
- `diameter_mm` on each primitive is **always in mm** (golden truth).
- Coordinate format is resolved in this order:
  1. forced override (`--coord-format` / `hint_coord_format`),
  2. file-declared format (if present),
  3. parser defaults (FMAT,2 conventions: MM `3.3`, INCH `2.3`).

### Zero Suppression
Excellon uses two modes for omitting zeros in coordinate strings:

| Mode | File stores | Restore by |
|------|-------------|-----------|
| `LZ` (leading zeros suppressed) | `62400` for 62.400 mm | Pad LEFT to total digits |
| `TZ` (trailing zeros suppressed) | `062` for 62.000 mm | Pad RIGHT to total digits |

Default when not declared: `LZ` (FMAT,2 convention).

### Ambiguous Files
If a file has no `METRIC`/`INCH` declaration:
- A `WARNING` is emitted.
- `state.units_ambiguous = True` is set.
- Units default to MM.
- Use `--units mm` or `--units inch` to override.

```bash
gerbyx old_board.drl --units inch
```

---

## Geometry Model

The Excellon pipeline uses exactly the same Shapely construction strategy as
the Gerber pipeline — every primitive is mapped to one buffered shape:

| Primitive | Shapely construction | Resulting geometry |
|-----------|---------------------|--------------------|
| `DrillHit` | `Point(x, y).buffer(r)` | Circle (Polygon) |
| `SlotG85` | `LineString([start, end]).buffer(r, round)` | Capsule (Polygon) |
| `RouteSegment` (line) | `LineString([start, end]).buffer(r, round)` | Capsule (Polygon) |
| `RouteSegment` (arc) | discretised arc polyline → `LineString.buffer(r, round)` | Arc strip (Polygon) |

All geometries in `result.geometries` are `shapely.geometry.Polygon` objects
and can be used directly with any Shapely / GeoJSON / visualisation workflow.

### Arc Segmentation (routing only)
Arcs use **adaptive chord-height segmentation**:
- `n ≥ angle_span / (2 · arccos(1 − tolerance / radius))`
- Clamped to `max_arc_segments` (default 128).

```python
result = process_file("board.drl",
    arc_tolerance_mm=0.005,   # tighter → more segments
    max_arc_segments=256,     # hard cap
)
```

---

## Accessing Metadata

Primitive metadata (tool number, diameter, plating, unit conversion provenance,
arc parameters, …) lives on the primitive objects in `result.primitives`.
Zip `primitives` with `geometries` to correlate geometry with metadata:

```python
result = process_file("board.drl")

for prim, geom in zip(result.primitives, result.geometries):
    print(
        f"tool={prim.tool_number}  "
        f"dia_mm={prim.diameter_mm:.3f}  "
        f"type={type(prim).__name__}  "
        f"area={geom.area:.4f}"
    )
```

Available fields on each primitive type:

### `DrillHit`
| Field | Type | Description |
|-------|------|-------------|
| `x`, `y` | float | Position in `output_units` |
| `x_mm`, `y_mm` | float | Position in mm (golden truth) |
| `tool_number` | int | Tool index |
| `diameter_mm` | float | Drill diameter in mm |
| `diameter_out` | float | Drill diameter in `output_units` |
| `plating` | str | `"PTH"` \| `"NPTH"` \| `"VIA"` \| `"unknown"` |
| `input_units` | str | `"MM"` \| `"INCH"` |
| `output_units` | str | `"MM"` \| `"INCH"` |
| `converted` | bool | Whether a unit conversion was applied |
| `conversion_factor` | float | 25.4, 1/25.4, or 1.0 |
| `feed_rate` | float\|None | Tool feed rate |
| `spindle_speed` | int\|None | Tool spindle speed |
| `source_cmd` | str | Raw source line |

### `SlotG85`
Same fields as `DrillHit` plus:

| Field | Type | Description |
|-------|------|-------------|
| `x_start`, `y_start` | float | Start point in `output_units` |
| `x_end`, `y_end` | float | End point in `output_units` |
| `x_start_mm`, `y_start_mm` | float | Start point in mm |
| `x_end_mm`, `y_end_mm` | float | End point in mm |

### `RouteSegment`
Same fields as `SlotG85` plus:

| Field | Type | Description |
|-------|------|-------------|
| `segment_type` | str | `"line"` \| `"arc_cw"` \| `"arc_ccw"` |
| `arc_center_x`, `arc_center_y` | float\|None | Arc centre in `output_units` |
| `arc_center_x_mm`, `arc_center_y_mm` | float\|None | Arc centre in mm |
| `arc_radius_mm` | float\|None | Arc radius in mm |
| `arc_angle_deg` | float\|None | Signed sweep angle (°) |

---

## API Reference

### `process_file(source, *, output_units, hint_units, hint_coord_format, arc_tolerance_mm, max_arc_segments, format_hint)`

```python
from gerbyx.dispatcher import process_file

result = process_file(
    "board.drl",
    output_units="MM",          # "MM" | "INCH", default "MM"
    hint_units=None,             # force input units for ambiguous files
    hint_coord_format=None,      # optional: "2.3", "3.3", "23", or tuple (2, 3)
    arc_tolerance_mm=0.01,
    max_arc_segments=128,
    format_hint=None,            # "gerber" | "excellon" | "auto" | None
)

result.format          # "gerber" | "excellon"
result.geometries      # [Shapely Polygon, …]  — same interface as Gerber
result.primitives      # [DrillHit | SlotG85 | RouteSegment, …]  (Excellon only)
result.detection       # DetectionResult (format auto-detect)
result.state           # ExcellonState (unit info, tool table, etc.)
```

### `ExcellonParser` + `ExcellonProcessor` (low-level)

```python
from gerbyx.excellon.state import ExcellonState
from gerbyx.excellon.tokenizer import tokenize_excellon
from gerbyx.excellon.parser import ExcellonParser
from gerbyx.excellon.processor import ExcellonProcessor

state = ExcellonState(output_units="MM")
parser = ExcellonParser(state, hint_units="INCH")   # force input units
parser.parse(tokenize_excellon(source_text))

proc = ExcellonProcessor(state)
proc.process(parser.primitives)          # load & cache
geoms = proc.geometries                  # [Shapely Polygon, …]

# or stateless:
geoms = proc.to_geometries(parser.primitives)
```

---

## Benchmarks and visual previews

The repository includes a benchmark/preview generator for the sample files in `data/excellon_samples/`:

```powershell
cd C:\TheAntFarmRepo\gerbyx
.\env\Scripts\python.exe scripts\bench_excellon.py
```

Generated artifacts are written to:

- `docs/generated/excellon_bench/README.md`
- `docs/generated/excellon_bench/summary.json`
- `docs/generated/excellon_bench/*.png`

Each PNG is a rendered preview of one sample Excellon file, while the report includes primitive counts and min/avg/max timings.

### `detect_format(text, path=None)`
```python
from gerbyx.excellon.detector import detect_format

r = detect_format(text, path="board.drl")
r.format        # "excellon" | "gerber" | "unknown"
r.confidence    # 0.0 – 1.0
r.hints         # {"units": "METRIC", "zero_suppression": "L"}
```

---

## Tested Dialects

| Vendor / Tool | Format | Tested |
|---------------|--------|--------|
| KiCad 7+ | `METRIC,LZ`, FMAT,2 | ✅ |
| KiCad 7+ | `INCH,LZ`, FMAT,2 | ✅ |
| CAM350 / Altium | `INCH,LZ/TZ`, FMAT,2 | ✅ |
| Generic with decimal coords | Any | ✅ |
| Files without unit declaration | Ambiguous → MM default | ✅ |

---

## CLI Options Reference

```
Usage: gerbyx [OPTIONS] FILE_PATH

  Convert a Gerber or Excellon file to Shapely geometries and GeoJSON.

Arguments:
  FILE_PATH   Path to Gerber or Excellon file  [required]

Options:
  -o, --output PATH              Output GeoJSON file
  -s, --show                     Show Matplotlib plot
  -f, --format [auto|gerber|excellon]
                                 Force format (default: auto)
  --units [mm|inch]              Force INPUT unit for ambiguous Excellon files
  --output-units [mm|inch]       Output coordinate unit (default: mm)
  --coord-format TEXT            Force Excellon coord format (e.g. 2.3, 3.3, 23)
  --arc-tolerance FLOAT          Chord-height tolerance for arc segs in mm (default: 0.01)
  --max-arc-segments INTEGER     Hard cap on arc polyline segments (default: 128)
```

---

## Related docs

- `docs/PACKAGING.md` — how the installable package is built and released
