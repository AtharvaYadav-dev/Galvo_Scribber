"""Console script for gerbyx — supports both Gerber and Excellon formats."""

import typer
import json
from enum import Enum
from typing import Optional
from rich.console import Console
from pathlib import Path
from shapely.geometry import mapping

app = typer.Typer(help="Convert Gerber / Excellon PCB files to GeoJSON and Shapely geometries.")
console = Console()


class FormatChoice(str, Enum):
    auto     = "auto"
    gerber   = "gerber"
    excellon = "excellon"


class UnitsChoice(str, Enum):
    mm   = "mm"
    inch = "inch"


@app.command()
def main(
    file_path: Path = typer.Argument(..., help="Path to the Gerber or Excellon file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output GeoJSON file path"),
    show: bool = typer.Option(False, "--show", "-s", help="Show the Matplotlib plot of generated geometries"),
    # ── Format & unit options ────────────────────────────────────────────────
    format: FormatChoice = typer.Option(
        FormatChoice.auto, "--format", "-f",
        help="Force file format: auto (default), gerber, excellon.",
    ),
    units: Optional[UnitsChoice] = typer.Option(
        None, "--units",
        help=(
            "[Excellon only] Override the INPUT unit of the file when the file "
            "does not declare METRIC/INCH (ambiguous). "
            "Example: --units inch"
        ),
    ),
    output_units: UnitsChoice = typer.Option(
        UnitsChoice.mm, "--output-units",
        help="Output coordinate unit for Excellon geometries (default: mm).",
    ),
    coord_format: Optional[str] = typer.Option(
        None,
        "--coord-format",
        help=(
            "[Excellon only] Override coordinate format digits (e.g. 2.3, 3.3, 23). "
            "If omitted, file-declared format is used; otherwise parser defaults are applied."
        ),
    ),
    # ── Arc options ──────────────────────────────────────────────────────────
    arc_tolerance: float = typer.Option(
        0.01, "--arc-tolerance",
        help=(
            "[Excellon routing arcs only] Chord-height tolerance in mm. "
            "Lower = more segments, higher accuracy. Default: 0.01 mm."
        ),
    ),
    max_arc_segments: int = typer.Option(
        128, "--max-arc-segments",
        help=(
            "[Excellon routing arcs only] Hard upper limit on arc polyline segments. "
            "Prevents excessively large outputs on large-radius arcs. Default: 128."
        ),
    ),
):
    """
    Convert a Gerber or Excellon file to Shapely geometries and export to GeoJSON.

    Format is auto-detected by default. Use --format to override.

    For Excellon files whose unit is not declared in the header, use --units
    to force the interpretation. The output is always in mm unless --output-units
    inch is specified.
    """
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Processing file:[/bold green] {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/bold red] {e}")
        raise typer.Exit(code=1)

    hint_units_str = units.value.upper() if units else None
    out_units_str  = output_units.value.upper()
    fmt_str        = format.value

    # ── Dispatch ──────────────────────────────────────────────────────────────
    try:
        from gerbyx.dispatcher import process_file

        console.print(f"Format: [cyan]{fmt_str}[/cyan]  |  Output units: [cyan]{out_units_str}[/cyan]")

        result = process_file(
            source,
            output_units=out_units_str,
            hint_units=hint_units_str,
            hint_coord_format=coord_format,
            arc_tolerance_mm=arc_tolerance,
            max_arc_segments=max_arc_segments,
            format_hint=fmt_str if fmt_str != "auto" else None,
        )

    except Exception as e:
        console.print(f"[bold red]Processing Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    # ── Report ────────────────────────────────────────────────────────────────
    if result.detection:
        det = result.detection
        console.print(
            f"Detected format: [cyan]{det.format}[/cyan] "
            f"(confidence={det.confidence:.0%})"
        )

    if result.format == "excellon" and result.state and result.state.units_ambiguous:
        console.print(
            "[yellow]Warning:[/yellow] Excellon file had no unit declaration. "
            "Assumed MM. Use [bold]--units[/bold] to override."
        )

    geometries = result.geometries
    count = len(geometries)
    console.print(f"[bold blue]Success![/bold blue] Generated {count} geometries.")

    if count == 0:
        console.print("[yellow]Warning:[/yellow] No geometries generated.")
        return

    # ── GeoJSON export ────────────────────────────────────────────────────────
    if output:
        console.print(f"Exporting to GeoJSON: {output}")
        try:
            features = []
            for i, geom in enumerate(geometries):
                features.append({
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {"index": i, "format": result.format},
                })

            geojson_data = {"type": "FeatureCollection", "features": features}

            with open(output, "w", encoding="utf-8") as f:
                json.dump(geojson_data, f, indent=2)

            console.print("[bold green]GeoJSON exported successfully![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error exporting GeoJSON:[/bold red] {e}")
            raise typer.Exit(code=1)

    # ── Visualise ─────────────────────────────────────────────────────────────
    if show:
        from gerbyx.visualizer import plot_shapes
        console.print("Visualizing...")
        plot_shapes(geometries)


if __name__ == "__main__":
    app()
