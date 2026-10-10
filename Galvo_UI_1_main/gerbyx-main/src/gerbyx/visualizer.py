from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon, MultiPolygon, LineString


def plot_shapes(geometries: list[BaseGeometry], show_plot: bool = True):
    """
    Plots a list of Shapely geometries using Matplotlib.

    Args:
        geometries: A list of Shapely geometry objects.
        show_plot: If True, displays the plot window.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for plotting. Install the optional 'plot' extra "
            "with: pip install .[plot]"
        ) from exc

    fig, ax = plt.subplots()

    # Set plot aspect ratio to be equal to avoid distortion
    ax.set_aspect('equal', adjustable='box')

    # Plot each geometry
    for geom in geometries:
        if geom.is_empty:
            continue

        color = 'black'

        if isinstance(geom, (Polygon, MultiPolygon)):
            polygons = [geom] if isinstance(geom, Polygon) else list(geom.geoms)

            for poly in polygons:
                # Plot the exterior face
                x, y = poly.exterior.xy
                ax.fill(x, y, alpha=0.8, fc=color, ec='none')

                # Plot the interior holes (if any)
                for interior in poly.interiors:
                    x, y = interior.xy
                    ax.fill(x, y, alpha=1.0, fc='white', ec='none')

        elif isinstance(geom, LineString):
            # This is less common for final shapes but good to handle
            x, y = geom.xy
            ax.plot(x, y, color=color, linewidth=3, solid_capstyle='round')

        else:
            print(f"Warning: Skipping unsupported geometry type for plotting: {geom.geom_type}")

    # Auto-set plot limits and add grid/labels
    ax.autoscale_view()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_title("Gerber Geometry Visualization")

    if show_plot:
        plt.show()

    return fig, ax
