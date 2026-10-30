import os
import json
import math
import time
from typing import List, Dict, Tuple, Optional, Any

import numpy as np

try:
    import trimesh
except ImportError:
    trimesh = None

try:
    from shapely.geometry import box, Polygon, MultiPolygon, LineString
    from shapely.ops import unary_union, linemerge, polygonize
    from shapely.validation import make_valid
except ImportError:
    box = Polygon = MultiPolygon = LineString = unary_union = linemerge = polygonize = make_valid = None

from core.motion_planner import MotionPlanner

DEFAULT_3D_PRESETS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "material_presets_3d.json"
)

class STL3DEngravingManager:
    """
    Industrial Grade 3D Relief & Negative Engraving Manager for Galvo Laser Machines.
    Handles STL slicing, background ablation (relief carving where the main object
    is left intact and the surrounding background is engraved away), material presets,
    resolution-driven loop/pass calculation, laser power/frequency sync, and
    cross-layer hatch angle rotation.
    """

    RES_FINE = "Fine (High Quality / Smooth)"
    RES_STANDARD = "Standard (Balanced Speed & Detail)"
    RES_FAST = "Fast (Draft / Deep Removal)"
    RES_CUSTOM = "Custom Resolution"

    ALL_RESOLUTIONS = [RES_FINE, RES_STANDARD, RES_FAST, RES_CUSTOM]

    MODE_RELIEF = "Relief (Carve BG, Keep Main Object Intact)"
    MODE_CAVITY = "Cavity / Intaglio (Carve Main Object)"
    ALL_MODES = [MODE_RELIEF, MODE_CAVITY]

    def __init__(self, presets_path: Optional[str] = None):
        self.presets_path = presets_path or DEFAULT_3D_PRESETS_FILE
        self.presets: Dict[str, Any] = {}
        self.load_presets()

        # Cache variables to prevent UI lag and avoid redundant re-slicing
        self.cached_file: Optional[str] = None
        self.cached_mesh: Optional[Any] = None
        self.cached_bounds: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None
        self.cached_dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.cached_slices_key: Optional[Tuple] = None
        self.cached_layer_polys: List[List[List[Tuple[float, float]]]] = []
        self.cached_layer_contours: List[List[List[Tuple[float, float]]]] = []
        self.cached_slice_levels: List[float] = []

    def load_presets(self) -> Dict[str, Any]:
        """Loads industrial 3D material presets from JSON or initializes built-in defaults."""
        if os.path.exists(self.presets_path):
            try:
                with open(self.presets_path, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
                    return self.presets
            except Exception as e:
                print(f"[STL3DEngravingManager] Error loading presets from {self.presets_path}: {e}")

        # Built-in industrial laser engraving presets with high-performance parameters
        self.presets = {
            "Aluminium (6061 / 7075)": {
                "power": 88.0,
                "frequency": 30.0,
                "speed": 600.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.008, "hatch_pitch": 0.025},
                    self.RES_STANDARD: {"z_step": 0.015, "hatch_pitch": 0.035},
                    self.RES_FAST: {"z_step": 0.030, "hatch_pitch": 0.050}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Stainless Steel / Steel": {
                "power": 90.0,
                "frequency": 35.0,
                "speed": 500.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.006, "hatch_pitch": 0.020},
                    self.RES_STANDARD: {"z_step": 0.012, "hatch_pitch": 0.030},
                    self.RES_FAST: {"z_step": 0.025, "hatch_pitch": 0.045}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Brass / Copper": {
                "power": 95.0,
                "frequency": 25.0,
                "speed": 450.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.008, "hatch_pitch": 0.025},
                    self.RES_STANDARD: {"z_step": 0.015, "hatch_pitch": 0.035},
                    self.RES_FAST: {"z_step": 0.030, "hatch_pitch": 0.050}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Titanium": {
                "power": 80.0,
                "frequency": 40.0,
                "speed": 600.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.006, "hatch_pitch": 0.025},
                    self.RES_STANDARD: {"z_step": 0.012, "hatch_pitch": 0.035},
                    self.RES_FAST: {"z_step": 0.025, "hatch_pitch": 0.045}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Tool Steel / Mold Steel": {
                "power": 92.0,
                "frequency": 30.0,
                "speed": 450.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.005, "hatch_pitch": 0.020},
                    self.RES_STANDARD: {"z_step": 0.010, "hatch_pitch": 0.030},
                    self.RES_FAST: {"z_step": 0.020, "hatch_pitch": 0.040}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "POM / Delrin (Hard Plastic)": {
                "power": 20.0,
                "frequency": 50.0,
                "speed": 850.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.020, "hatch_pitch": 0.035},
                    self.RES_STANDARD: {"z_step": 0.040, "hatch_pitch": 0.045},
                    self.RES_FAST: {"z_step": 0.080, "hatch_pitch": 0.060}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Acrylic / PMMA": {
                "power": 22.0,
                "frequency": 35.0,
                "speed": 600.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.020, "hatch_pitch": 0.030},
                    self.RES_STANDARD: {"z_step": 0.040, "hatch_pitch": 0.040},
                    self.RES_FAST: {"z_step": 0.080, "hatch_pitch": 0.060}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "ABS / Hard Polymers": {
                "power": 22.0,
                "frequency": 45.0,
                "speed": 700.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.025, "hatch_pitch": 0.035},
                    self.RES_STANDARD: {"z_step": 0.050, "hatch_pitch": 0.045},
                    self.RES_FAST: {"z_step": 0.090, "hatch_pitch": 0.060}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            },
            "Wood / Organic Material": {
                "power": 20.0,
                "frequency": 35.0,
                "speed": 900.0,
                "resolutions": {
                    self.RES_FINE: {"z_step": 0.030, "hatch_pitch": 0.040},
                    self.RES_STANDARD: {"z_step": 0.060, "hatch_pitch": 0.050},
                    self.RES_FAST: {"z_step": 0.120, "hatch_pitch": 0.070}
                },
                "default_resolution": self.RES_STANDARD,
                "bg_margin": 2.0,
                "cross_layer_rotate": True
            }
        }
        self.save_presets()
        return self.presets

    def save_presets(self) -> bool:
        """Saves current 3D presets to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.presets_path), exist_ok=True)
            with open(self.presets_path, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2)
            return True
        except Exception as e:
            print(f"[STL3DEngravingManager] Error saving presets: {e}")
            return False

    def add_or_update_preset(
        self,
        name: str,
        power: float,
        frequency: float,
        speed: float,
        z_step: float,
        hatch_pitch: float = 0.03,
        bg_margin: float = 2.0,
        cross_layer_rotate: bool = True
    ) -> bool:
        """Adds or updates a custom 3D preset."""
        name = str(name).strip()
        if not name:
            return False

        z_step = max(0.001, min(0.5, float(z_step)))
        hatch_pitch = max(0.005, min(0.5, float(hatch_pitch)))
        bg_margin = max(0.0, min(50.0, float(bg_margin)))

        self.presets[name] = {
            "power": float(power),
            "frequency": float(frequency),
            "speed": float(speed),
            "resolutions": {
                self.RES_FINE: {"z_step": round(z_step * 0.6, 4), "hatch_pitch": round(hatch_pitch * 0.8, 4)},
                self.RES_STANDARD: {"z_step": round(z_step, 4), "hatch_pitch": round(hatch_pitch, 4)},
                self.RES_FAST: {"z_step": round(z_step * 1.8, 4), "hatch_pitch": round(hatch_pitch * 1.4, 4)}
            },
            "default_resolution": self.RES_STANDARD,
            "bg_margin": bg_margin,
            "cross_layer_rotate": bool(cross_layer_rotate)
        }
        self.save_presets()
        return True

    def get_preset_params(self, mat_name: str, res_name: str) -> Dict[str, Any]:
        """
        Retrieves recommended power, freq, speed, z_step, and hatch_pitch
        based on chosen material and resolution tier.
        """
        preset = self.presets.get(mat_name)
        if not preset:
            # Fallback to Aluminium if name not found
            preset = self.presets.get("Aluminium (6061 / 7075)", list(self.presets.values())[0])

        power = preset.get("power", 80.0)
        freq = preset.get("frequency", 30.0)
        speed = preset.get("speed", 600.0)
        bg_margin = preset.get("bg_margin", 2.0)
        cross_rotate = preset.get("cross_layer_rotate", True)

        res_dict = preset.get("resolutions", {})
        res_info = res_dict.get(res_name)
        if not res_info:
            res_info = res_dict.get(self.RES_STANDARD, {"z_step": 0.015, "hatch_pitch": 0.035})

        z_step = res_info.get("z_step", 0.015)
        hatch_pitch = res_info.get("hatch_pitch", 0.035)

        return {
            "power": power,
            "frequency": freq,
            "speed": speed,
            "z_step": z_step,
            "hatch_pitch": hatch_pitch,
            "bg_margin": bg_margin,
            "cross_layer_rotate": cross_rotate
        }

    @staticmethod
    def calculate_passes(target_depth_mm: float, z_step_mm: float) -> int:
        """Accurately calculates loop/pass count from depth and layer step."""
        try:
            depth = max(0.001, float(target_depth_mm))
            step = max(0.001, float(z_step_mm))
            loops = int(math.ceil(depth / step))
            return max(1, loops)
        except (ValueError, ZeroDivisionError):
            return 1

    def load_stl(self, filepath: str) -> bool:
        """
        Loads and validates an STL file. Centers the model in XY and
        caches the mesh for fast multi-plane slicing.
        """
        if not trimesh:
            print("[STL3DEngravingManager] trimesh is not installed!")
            return False

        if not filepath or not os.path.exists(filepath):
            return False

        if self.cached_file == filepath and self.cached_mesh is not None:
            return True

        try:
            loaded = trimesh.load(filepath)
            if isinstance(loaded, trimesh.Scene):
                if len(loaded.geometry) == 0:
                    return False
                mesh = trimesh.util.concatenate([g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)])
            elif isinstance(loaded, trimesh.Trimesh):
                mesh = loaded
            else:
                return False

            if mesh.is_empty or len(mesh.vertices) == 0:
                return False

            # Center mesh horizontally around (0, 0) and align bottom at Z=0
            bounds = mesh.bounds
            center_x = (bounds[0][0] + bounds[1][0]) / 2.0
            center_y = (bounds[0][1] + bounds[1][1]) / 2.0
            min_z = float(bounds[0][2])
            mesh.apply_translation([-center_x, -center_y, -min_z])

            self.cached_file = filepath
            self.cached_mesh = mesh
            self.scale_factor = 1.0
            self.cached_bounds = (tuple(mesh.bounds[0]), tuple(mesh.bounds[1]))
            dim_x = float(mesh.bounds[1][0] - mesh.bounds[0][0])
            dim_y = float(mesh.bounds[1][1] - mesh.bounds[0][1])
            dim_z = float(mesh.bounds[1][2] - mesh.bounds[0][2])
            self.cached_dimensions = (dim_x, dim_y, dim_z)

            # Invalidate slice cache
            self.cached_slices_key = None
            self.cached_layer_polys = []
            self.cached_slice_levels = []
            return True
        except Exception as e:
            print(f"[STL3DEngravingManager] Error loading STL: {e}")
            return False

    def apply_scale(self, scale_factor: float) -> Tuple[float, float, float]:
        """Scales the current 3D mesh by scale_factor and updates dimensions."""
        if self.cached_mesh is None or scale_factor <= 0:
            return self.cached_dimensions
        
        self.cached_mesh.apply_scale(scale_factor)
        # Re-center XY and align Z min to 0
        b = self.cached_mesh.bounds
        cx = (b[0][0] + b[1][0]) / 2.0
        cy = (b[0][1] + b[1][1]) / 2.0
        self.cached_mesh.apply_translation([-cx, -cy, -float(b[0][2])])
        
        dim_x = float(self.cached_mesh.bounds[1][0] - self.cached_mesh.bounds[0][0])
        dim_y = float(self.cached_mesh.bounds[1][1] - self.cached_mesh.bounds[0][1])
        dim_z = float(self.cached_mesh.bounds[1][2] - self.cached_mesh.bounds[0][2])
        self.cached_dimensions = (dim_x, dim_y, dim_z)
        self.scale_factor *= scale_factor
        
        # Invalidate slice cache
        self.cached_slices_key = None
        self.cached_layer_polys = []
        self.cached_slice_levels = []
        return self.cached_dimensions

    def rotate_mesh_90(self, axis: str = 'X') -> Tuple[float, float, float]:
        """Rotates the mesh 90 degrees around X, Y, or Z axis and re-centers it."""
        if self.cached_mesh is None:
            return self.cached_dimensions
        
        import numpy as np
        axis_vec = [1, 0, 0] if axis.upper() == 'X' else ([0, 1, 0] if axis.upper() == 'Y' else [0, 0, 1])
        rot = trimesh.transformations.rotation_matrix(np.pi / 2, axis_vec)
        self.cached_mesh.apply_transform(rot)
        
        b = self.cached_mesh.bounds
        cx = (b[0][0] + b[1][0]) / 2.0
        cy = (b[0][1] + b[1][1]) / 2.0
        self.cached_mesh.apply_translation([-cx, -cy, -float(b[0][2])])
        
        dim_x = float(self.cached_mesh.bounds[1][0] - self.cached_mesh.bounds[0][0])
        dim_y = float(self.cached_mesh.bounds[1][1] - self.cached_mesh.bounds[0][1])
        dim_z = float(self.cached_mesh.bounds[1][2] - self.cached_mesh.bounds[0][2])
        self.cached_dimensions = (dim_x, dim_y, dim_z)
        
        # Invalidate slice cache
        self.cached_slices_key = None
        self.cached_layer_polys = []
        self.cached_slice_levels = []
        return self.cached_dimensions

    def auto_fit_to_lens(self, lens_size_mm: float, bg_margin_mm: float = 2.0) -> float:
        """
        Calculates and applies uniform scaling so total width and height
        fit inside (lens_size_mm - 2*bg_margin_mm) * 0.95.
        Returns the applied scale factor multiplier.
        """
        if self.cached_mesh is None:
            return 1.0
        dim_x, dim_y, dim_z = self.cached_dimensions
        max_allowed = max(10.0, (lens_size_mm - 2 * bg_margin_mm) * 0.95)
        current_max = max(dim_x, dim_y)
        if current_max <= 0:
            return 1.0
        
        factor = max_allowed / current_max
        self.apply_scale(factor)
        return factor

    def auto_orient_flat(self) -> Tuple[float, float, float]:
        """
        If thickness is along Y or X instead of Z (e.g. model standing upright),
        automatically rotates the mesh so the smallest dimension is along Z (depth).
        """
        if self.cached_mesh is None:
            return self.cached_dimensions
        dim_x, dim_y, dim_z = self.cached_dimensions
        if dim_y < dim_z and dim_y <= dim_x:
            # Thickness is currently along Y -> rotate 90 deg around X
            return self.rotate_mesh_90('X')
        elif dim_x < dim_z and dim_x <= dim_y:
            # Thickness is currently along X -> rotate 90 deg around Y
            return self.rotate_mesh_90('Y')
        return self.cached_dimensions

    def get_mesh_dimensions(self) -> Tuple[float, float, float]:
        """Returns (width_x, height_y, depth_z) of the loaded STL model in mm."""
        return self.cached_dimensions

    def slice_model(
        self,
        z_step_mm: float,
        target_depth_mm: Optional[float] = None,
        bg_margin_mm: float = 2.0,
        carve_mode: str = MODE_RELIEF
    ) -> List[List[List[Tuple[float, float]]]]:
        """
        Slices the 3D model into multi-layer 2D polygons.
        In RELIEF mode (default):
          Creates background ablation polygons: [Bounding Background] MINUS [3D Model Slice].
          The laser ablates the material around the object, carving away the background
          so the main 3D object remains pristine and intact as a raised 3D relief!
        """
        if self.cached_mesh is None:
            return []

        z_step = max(0.001, float(z_step_mm))
        dim_x, dim_y, dim_z = self.cached_dimensions
        if dim_z <= 0.0:
            return []

        total_depth = target_depth_mm if target_depth_mm is not None and target_depth_mm > 0 else dim_z
        total_layers = self.calculate_passes(total_depth, z_step)

        # Cache check to avoid redundant slicing computations
        cache_key = (
            self.cached_file,
            round(z_step, 5),
            round(total_depth, 4),
            round(bg_margin_mm, 3),
            carve_mode,
            total_layers
        )
        if self.cached_slices_key == cache_key and self.cached_layer_polys:
            return self.cached_layer_polys

        t0 = time.time()
        min_pt, max_pt = self.cached_mesh.bounds
        max_z = float(max_pt[2])
        min_z = float(min_pt[2])

        # Slice levels top-down (from top surface down to model base)
        slice_levels = []
        for i in range(total_layers):
            # Midpoint of current layer slice
            z_lvl = max_z - (i + 0.5) * z_step
            # Clamp to slightly above min_z
            z_lvl = max(min_z + 0.001, min(max_z - 0.001, z_lvl))
            slice_levels.append(z_lvl)

        try:
            # Batch C-optimized slicing through trimesh multiplane
            sections = self.cached_mesh.section_multiplane(
                plane_origin=[0, 0, 0],
                plane_normal=[0, 0, 1],
                heights=slice_levels
            )
        except Exception as e:
            print(f"[STL3DEngravingManager] Multiplane slice failed ({e}), falling back to single plane sectioning.")
            sections = []
            for lvl in slice_levels:
                try:
                    s = self.cached_mesh.section(plane_origin=[0, 0, lvl], plane_normal=[0, 0, 1])
                    sections.append(s)
                except Exception:
                    sections.append(None)

        # Background boundary box for relief carving
        margin = max(0.2, float(bg_margin_mm))
        bg_box = box(min_pt[0] - margin, min_pt[1] - margin, max_pt[0] + margin, max_pt[1] + margin)

        layer_polys_list = []
        layer_contours_list = []
        cumulative_model_geom = None
        prev_sig = None
        prev_coords = None
        prev_contours = None

        for i, section in enumerate(sections):
            if section is None:
                # No mesh intersection at this height
                if carve_mode == self.MODE_RELIEF:
                    layer_polys_list.append([list(bg_box.exterior.coords)])
                else:
                    layer_polys_list.append([])
                layer_contours_list.append([])
                prev_sig = None
                prev_coords = None
                prev_contours = None
                continue

            # Fast signature check for identical consecutive slices (common in coins, reliefs, and prismatic walls)
            sig = None
            if hasattr(section, 'discrete') and section.discrete:
                try:
                    sig = (len(section.discrete), round(float(section.discrete[0][0][0]), 3) if len(section.discrete[0]) > 0 else 0)
                except Exception:
                    sig = None

            if sig is not None and sig == prev_sig and prev_coords is not None:
                layer_polys_list.append(prev_coords)
                layer_contours_list.append(prev_contours)
                continue

            polys = []
            if section is not None:
                # Tier 1: Try section.polygons_full (clean watertight meshes & Path2D)
                try:
                    if hasattr(section, 'polygons_full') and section.polygons_full:
                        polys = [p for p in section.polygons_full if p.is_valid and p.area > 0.001]
                except Exception:
                    polys = []

                # Tier 1b: If section is Path3D, convert to 2D planar
                if not polys:
                    try:
                        if hasattr(section, 'to_planar'):
                            p2d, _ = section.to_planar()
                            if hasattr(p2d, 'polygons_full') and p2d.polygons_full:
                                polys = [p for p in p2d.polygons_full if p.is_valid and p.area > 0.001]
                        elif hasattr(section, 'to_2D'):
                            p2d, _ = section.to_2D()
                            if hasattr(p2d, 'polygons_full') and p2d.polygons_full:
                                polys = [p for p in p2d.polygons_full if p.is_valid and p.area > 0.001]
                    except Exception:
                        polys = []

                # Tier 2: Extract discrete line segments, merge and polygonize genuine closed cycles.
                # Reconstruct solids and holes using even-odd containment.
                if not polys:
                    try:
                        lines = []
                        if hasattr(section, 'discrete'):
                            for d in section.discrete:
                                if len(d) >= 2:
                                    lines.append(LineString([(pt[0], pt[1]) for pt in d]))
                        elif hasattr(section, 'entities') and hasattr(section, 'vertices'):
                            for e in section.entities:
                                pts = section.vertices[e.points]
                                if len(pts) >= 2:
                                    lines.append(LineString([(pt[0], pt[1]) for pt in pts]))
                        if lines:
                            merged = linemerge(lines)
                            raw_cycles = [c for c in polygonize(merged) if c.area > 0.005]
                            if raw_cycles:
                                # Sort by area descending to determine outer shells vs interior holes
                                sorted_cycs = sorted(raw_cycles, key=lambda c: c.area, reverse=True)
                                shells = []
                                holes = []
                                for idx, c in enumerate(sorted_cycs):
                                    rep = c.representative_point()
                                    contain_count = sum(1 for j in range(idx) if sorted_cycs[j].contains(rep))
                                    if contain_count % 2 == 0:
                                        shells.append(c)
                                    else:
                                        holes.append(c)
                                combined_shells = unary_union(shells) if shells else None
                                combined_holes = unary_union(holes) if holes else None
                                if combined_shells:
                                    clean_cycles = combined_shells.difference(combined_holes) if combined_holes else combined_shells
                                    if clean_cycles and not clean_cycles.is_empty:
                                        if clean_cycles.geom_type == 'Polygon':
                                            polys = [clean_cycles]
                                        elif clean_cycles.geom_type == 'MultiPolygon':
                                            polys = list(clean_cycles.geoms)
                    except Exception:
                        polys = []

                # Tier 3: Fallback using polygons_closed with area & hierarchy subtraction
                if not polys:
                    try:
                        if hasattr(section, 'polygons_closed'):
                            raw_closed = [p for p in section.polygons_closed if p.is_valid and p.area > 0.01]
                            if raw_closed:
                                sorted_p = sorted(raw_closed, key=lambda p: p.area, reverse=True)
                                shells = []
                                holes = []
                                for idx, p in enumerate(sorted_p):
                                    rep = p.representative_point()
                                    contain_count = sum(1 for j in range(idx) if sorted_p[j].contains(rep))
                                    if contain_count % 2 == 0:
                                        shells.append(p)
                                    else:
                                        holes.append(p)
                                c_shells = unary_union(shells) if shells else None
                                c_holes = unary_union(holes) if holes else None
                                if c_shells:
                                    res = c_shells.difference(c_holes) if c_holes else c_shells
                                    if res and not res.is_empty:
                                        if res.geom_type == 'Polygon':
                                            polys = [res]
                                        elif res.geom_type == 'MultiPolygon':
                                            polys = list(res.geoms)
                    except Exception:
                        polys = []

            # If we obtained valid 2D slice polygons, clean and accumulate into cumulative model
            if polys:
                clean_polys = []
                for p in polys:
                    if not p.is_valid:
                        p = make_valid(p) if make_valid else p.buffer(0)
                    if p.geom_type == 'Polygon' and p.area > 0.001:
                        clean_polys.append(p)
                    elif p.geom_type == 'MultiPolygon':
                        clean_polys.extend([sub for sub in p.geoms if sub.area > 0.001])

                if clean_polys:
                    slice_geom = unary_union(clean_polys)
                    if slice_geom and not slice_geom.is_valid:
                        slice_geom = make_valid(slice_geom) if make_valid else slice_geom.buffer(0)

                    if slice_geom and not slice_geom.is_empty:
                        if cumulative_model_geom is None:
                            cumulative_model_geom = slice_geom
                        else:
                            # CUMULATIVE UPPER-VOLUME UNION WITH FAST DIFFERENCE & SIMPLIFY:
                            # Only union new areas not already covered, simplifying collinear micro-points
                            diff = slice_geom.difference(cumulative_model_geom)
                            if diff and not diff.is_empty and diff.area > 0.001:
                                cumulative_model_geom = unary_union([cumulative_model_geom, diff])
                                cumulative_model_geom = cumulative_model_geom.simplify(0.003, preserve_topology=True)
                                if not cumulative_model_geom.is_valid:
                                    cumulative_model_geom = make_valid(cumulative_model_geom) if make_valid else cumulative_model_geom.buffer(0)

            try:
                if cumulative_model_geom is None or cumulative_model_geom.is_empty:
                    # Model not reached yet at this high Z level
                    if carve_mode == self.MODE_RELIEF:
                        coords = [list(bg_box.exterior.coords)]
                    else:
                        coords = []
                    layer_polys_list.append(coords)
                    layer_contours_list.append([])
                    prev_sig = sig
                    prev_coords = coords
                    prev_contours = []
                    continue

                if carve_mode == self.MODE_RELIEF:
                    # NEGATIVE / RELIEF ENGRAVING:
                    carve_geom = bg_box.difference(cumulative_model_geom)
                else:
                    # POSITIVE / CAVITY ENGRAVING:
                    carve_geom = cumulative_model_geom

                if carve_geom is not None and not carve_geom.is_empty:
                    coords = self._geom_to_poly_coords(carve_geom)
                    layer_polys_list.append(coords)
                else:
                    coords = []
                    layer_polys_list.append([])

                # Model contours for outline marking:
                contour_coords = self._geom_to_poly_coords(cumulative_model_geom)
                filtered_contours = []
                for ring in contour_coords:
                    if len(ring) >= 3:
                        try:
                            if Polygon(ring).area > 0.01:
                                filtered_contours.append(ring)
                        except Exception:
                            filtered_contours.append(ring)
                layer_contours_list.append(filtered_contours)

                prev_sig = sig
                prev_coords = coords
                prev_contours = filtered_contours
            except Exception as e:
                print(f"[STL3DEngravingManager] Layer {i} boolean error: {e}")
                err_coords = [list(bg_box.exterior.coords)]
                layer_polys_list.append(err_coords)
                layer_contours_list.append([])
                prev_sig = sig
                prev_coords = err_coords
                prev_contours = []

        self.cached_slices_key = cache_key
        self.cached_layer_polys = layer_polys_list
        self.cached_layer_contours = layer_contours_list
        self.cached_slice_levels = slice_levels
        elapsed = (time.time() - t0) * 1000
        print(f"[STL3DEngravingManager] Sliced {len(layer_polys_list)} layers in {elapsed:.1f} ms")
        return self.cached_layer_polys

    @staticmethod
    def _geom_to_poly_coords(geom) -> List[List[Tuple[float, float]]]:
        """Extracts exterior and interior ring coordinate lists from Shapely geometry."""
        results = []
        if geom is None or geom.is_empty:
            return results

        if geom.geom_type == 'Polygon':
            geoms = [geom]
        elif geom.geom_type == 'MultiPolygon':
            geoms = list(geom.geoms)
        elif geom.geom_type == 'GeometryCollection':
            geoms = [g for g in geom.geoms if g.geom_type in ('Polygon', 'MultiPolygon')]
        else:
            return results

        for g in geoms:
            if g.geom_type == 'Polygon':
                if len(g.exterior.coords) >= 3:
                    results.append(list(g.exterior.coords))
                for interior in g.interiors:
                    if len(interior.coords) >= 3:
                        results.append(list(interior.coords))
            elif g.geom_type == 'MultiPolygon':
                for sub in g.geoms:
                    if len(sub.exterior.coords) >= 3:
                        results.append(list(sub.exterior.coords))
                    for interior in sub.interiors:
                        if len(interior.coords) >= 3:
                            results.append(list(interior.coords))
        return results

    def get_layer_polygons(self, layer_idx: int) -> List[List[Tuple[float, float]]]:
        """Returns the carve polygon list for a specific layer index (used for hatching)."""
        if not self.cached_layer_polys:
            return []
        idx = max(0, min(len(self.cached_layer_polys) - 1, layer_idx))
        return self.cached_layer_polys[idx]

    def get_layer_contours(self, layer_idx: int) -> List[List[Tuple[float, float]]]:
        """Returns the model contour list for a specific layer index (excluding artificial bg_box)."""
        if not hasattr(self, 'cached_layer_contours') or not self.cached_layer_contours:
            return []
        idx = max(0, min(len(self.cached_layer_contours) - 1, layer_idx))
        return self.cached_layer_contours[idx]

    def generate_layer_queue(
        self,
        layer_idx: int,
        galvo_config: Any,
        hatch_pitch_mm: float = 0.03,
        base_angle_deg: float = 0.0,
        cross_layer_rotate: bool = True,
        mark_speed: int = 1000,
        jump_speed: int = 2000,
        start_x_mm: float = 0.0,
        start_y_mm: float = 0.0,
        mark_contour: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generates galvo commands (jumps, marks, hatches) for a single 3D slice layer.
        Rotates hatch angle across consecutive layers for ultra-smooth industrial surface finish.
        When mark_contour is True, only marks clean model perimeters (never the background boundary box).
        """
        polys_mm = self.get_layer_polygons(layer_idx)
        if not polys_mm:
            return []

        galvo_units_per_mm = 65535 / galvo_config.field_size if galvo_config else 655.35

        # Cross-layer angle rotation: 0°, 90°, 0°, 90° (or 45°/135°) to prevent surface trenching
        current_angle = float(base_angle_deg)
        if cross_layer_rotate:
            current_angle = (base_angle_deg + (layer_idx * 90.0)) % 180.0

        # Transform carve polygons to galvo coordinate space for hatching
        all_polys_galvo = []
        for poly in polys_mm:
            if not poly or len(poly) < 3:
                continue
            poly_galvo = []
            for pt in poly:
                gx, gy = galvo_config.apply_transform(pt[0] + start_x_mm, pt[1] + start_y_mm)
                poly_galvo.append((gx, gy))
            all_polys_galvo.append(poly_galvo)

        planner = MotionPlanner()
        hatch_cfg = {
            'enable': True,
            'type': 'Bidirectional',
            'cross_hatch': False,
            'angle': current_angle,
            'line_space': hatch_pitch_mm,
            'count': 1,
            'hatch_idx': 1
        }

        # Optional contour outline marking (outlining the true model, NEVER the artificial bg_box)
        if mark_contour:
            contours_mm = self.get_layer_contours(layer_idx)
            # Fallback if cached_layer_contours was not populated: filter out bg_box from polys_mm
            if not contours_mm and polys_mm:
                contours_mm = [p for p in polys_mm if len(p) > 5]
            for c_poly in contours_mm:
                if not c_poly or len(c_poly) < 3:
                    continue
                c_galvo = []
                for pt in c_poly:
                    gx, gy = galvo_config.apply_transform(pt[0] + start_x_mm, pt[1] + start_y_mm)
                    c_galvo.append((gx, gy))
                if len(c_galvo) >= 3:
                    planner.add_jump(c_galvo[0][0], c_galvo[0][1], speed=jump_speed)
                    for pt in c_galvo[1:]:
                        planner.add_mark(pt[0], pt[1], speed=mark_speed)
                    # Close the contour ring cleanly
                    if c_galvo[-1] != c_galvo[0]:
                        planner.add_mark(c_galvo[0][0], c_galvo[0][1], speed=mark_speed)

        # Hatching pass
        planner.generate_hatch(
            all_polys_galvo,
            [hatch_cfg],
            mark_speed=mark_speed,
            jump_speed=jump_speed,
            galvo_units_per_mm=galvo_units_per_mm
        )

        planner.commit_to_send_queue()
        return planner.send_queue

    def get_relief_bounds_mm(self, bg_margin_mm: float = 2.0) -> Tuple[float, float, float, float]:
        """Returns (min_x, max_x, min_y, max_y) in mm for the entire relief workpiece."""
        if self.cached_bounds is None:
            return (-10.0, 10.0, -10.0, 10.0)
        min_pt, max_pt = self.cached_bounds
        margin = max(0.0, float(bg_margin_mm))
        return (min_pt[0] - margin, max_pt[0] + margin, min_pt[1] - margin, max_pt[1] + margin)
