"""
STL 3D Relief Engraver for Galvo Laser Systems.
==============================================
Directly ingests 3D mesh files (.stl, .obj, .ply, .3mf) and converts them into:
1. High-precision 16-bit Bas-Relief Heightmaps (topological Z-buffer orthographic projection).
2. Intelligent Auto-Orientation: detects Y-up or standing models and lays them flat on the focal plane.
3. Multi-layer sliced Galvo laser toolpaths with auto-rotating hatching (+15 deg/pass),
   bidirectional scanlines, boundary contour cleanups, and de-oxidation passes.
4. Seamless support for both relief coins/medallions and general rectangular/arbitrary 3D models.
"""

import os
import time
import math
import numpy as np
import cv2
import trimesh

from core.heightmap_slicer import Heightmap3DSlicer


class STL3DEngraver:
    """
    Ingests 3D STL mesh models and converts them into production-grade Galvo 3D relief engraving jobs.
    """
    def __init__(
        self,
        stl_path: str,
        diameter_mm: float = 27.0,
        target_size_mm: float = None,
        width_mm: float = None,
        height_mm: float = None,
        max_depth_mm: float = 0.75,
        num_layers: int = 50,
        output_resolution: int = 1080,
        invert_relief: bool = False,
        field_size: float = 100.0,
        laser_power: float = None,
        laser_freq: float = None,
        mark_speed_mms: float = None,
        jump_speed_mms: float = None,
        offset_x_mm: float = 0.0,
        offset_y_mm: float = 0.0,
        boundary_mode: str = 'auto',
        bidirectional: bool = True,
        enable_contour: bool = True,
        projection_axis: str = 'auto'
    ):
        self.stl_path = os.path.abspath(stl_path)
        effective_sz = float(target_size_mm if target_size_mm is not None else diameter_mm)
        self.diameter_mm = effective_sz
        self.target_size_mm = effective_sz
        self.req_width_mm = float(width_mm) if width_mm is not None else None
        self.req_height_mm = float(height_mm) if height_mm is not None else None
        self.max_depth_mm = float(max_depth_mm)
        self.num_layers = int(num_layers)
        self.output_resolution = int(output_resolution)
        self.invert_relief = bool(invert_relief)
        self.field_size = float(field_size)

        self.laser_power = laser_power
        self.laser_freq = laser_freq
        self.mark_speed_mms = mark_speed_mms
        self.jump_speed_mms = jump_speed_mms
        self.offset_x_mm = float(offset_x_mm)
        self.offset_y_mm = float(offset_y_mm)
        self.boundary_mode = str(boundary_mode).lower().strip()
        self.bidirectional = bool(bidirectional)
        self.enable_contour = bool(enable_contour)
        self.projection_axis = str(projection_axis).lower().strip()

        self.mesh = None
        self.heightmap_path = None
        self.mesh_info = {}
        self.layers = []
        self.slicer = None

        self._load_mesh()

    def _load_mesh(self):
        """Loads, cleans, and auto-orients the 3D mesh model."""
        if not os.path.exists(self.stl_path):
            raise FileNotFoundError(f"3D Model not found: {self.stl_path}")

        loaded = trimesh.load(self.stl_path)
        if isinstance(loaded, trimesh.Scene):
            if len(loaded.geometry) == 0:
                raise ValueError(f"No geometry found in 3D scene: {self.stl_path}")
            self.mesh = loaded.dump(concatenate=True)
        else:
            self.mesh = loaded

        # Ensure mesh has valid normals
        if not hasattr(self.mesh, 'faces') or len(self.mesh.faces) == 0:
            raise ValueError(f"Mesh has no polygonal faces: {self.stl_path}")

        # Compute initial bounding box
        bounds = self.mesh.bounds
        dx = float(bounds[1][0] - bounds[0][0])
        dy = float(bounds[1][1] - bounds[0][1])
        dz = float(bounds[1][2] - bounds[0][2])

        # Auto-orientation: ensure relief thickness aligns with Z-axis
        if self.projection_axis == 'auto':
            # In relief carving, the relief depth is almost always the thinnest dimension
            if dy < dx and dy < dz:
                # Model is exported with Y as thickness (Y-up convention) -> rotate 90 deg around X
                print(f"[STL3DEngraver] Auto-orienting mesh: Y-axis is thinnest ({dy:.2f}mm) -> rotating to Z-axis")
                rot_x = trimesh.transformations.rotation_matrix(math.radians(-90), [1, 0, 0])
                self.mesh.apply_transform(rot_x)
            elif dx < dy and dx < dz:
                # X is thickness -> rotate 90 deg around Y
                print(f"[STL3DEngraver] Auto-orienting mesh: X-axis is thinnest ({dx:.2f}mm) -> rotating to Z-axis")
                rot_y = trimesh.transformations.rotation_matrix(math.radians(90), [0, 1, 0])
                self.mesh.apply_transform(rot_y)
        elif self.projection_axis == '+y':
            rot = trimesh.transformations.rotation_matrix(math.radians(-90), [1, 0, 0])
            self.mesh.apply_transform(rot)
        elif self.projection_axis == '-y':
            rot = trimesh.transformations.rotation_matrix(math.radians(90), [1, 0, 0])
            self.mesh.apply_transform(rot)
        elif self.projection_axis == '+x':
            rot = trimesh.transformations.rotation_matrix(math.radians(90), [0, 1, 0])
            self.mesh.apply_transform(rot)

        # Recompute bounds after orientation
        bounds = self.mesh.bounds
        dx = float(bounds[1][0] - bounds[0][0])
        dy = float(bounds[1][1] - bounds[0][1])
        dz = float(bounds[1][2] - bounds[0][2])

        self.mesh_info = {
            "vertex_count": len(self.mesh.vertices),
            "face_count": len(self.mesh.faces),
            "original_dx_mm": dx,
            "original_dy_mm": dy,
            "original_dz_mm": dz,
            "aspect_ratio": dx / max(1e-6, dy)
        }

        print(
            f"[STL3DEngraver] Loaded '{os.path.basename(self.stl_path)}': "
            f"{len(self.mesh.faces):,} faces, {len(self.mesh.vertices):,} vertices | "
            f"Dimensions: {dx:.2f} x {dy:.2f} x {dz:.2f} mm (Aspect: {self.mesh_info['aspect_ratio']:.2f})"
        )

    def convert_to_heightmap(self, output_png_path: str = None) -> str:
        """
        Orthographically projects the top-surface topological relief of the 3D STL mesh
        into a continuous high-precision 16-bit grayscale heightmap.
        """
        t0 = time.time()
        mesh_copy = self.mesh.copy()

        # 1. Center XY at (0, 0) and baseline Z at 0
        bounds = mesh_copy.bounds
        min_b, max_b = bounds[0], bounds[1]
        cx = (min_b[0] + max_b[0]) / 2.0
        cy = (min_b[1] + max_b[1]) / 2.0
        cz_min = min_b[2]
        mesh_copy.apply_translation([-cx, -cy, -cz_min])

        # 2. Determine physical target dimensions
        orig_dx = max(1e-4, max_b[0] - min_b[0])
        orig_dy = max(1e-4, max_b[1] - min_b[1])
        aspect = orig_dx / orig_dy

        if self.req_width_mm and self.req_height_mm:
            target_w = self.req_width_mm
            target_h = self.req_height_mm
            scale_x = target_w / orig_dx
            scale_y = target_h / orig_dy
            mesh_copy.apply_scale([scale_x, scale_y, 1.0])
        elif self.boundary_mode == 'circle':
            target_w = self.diameter_mm
            target_h = self.diameter_mm
            span = max(orig_dx, orig_dy)
            scale = self.diameter_mm / span
            mesh_copy.apply_scale(scale)
        else:
            if aspect >= 1.0:
                target_w = self.diameter_mm
                target_h = self.diameter_mm / aspect
            else:
                target_h = self.diameter_mm
                target_w = self.diameter_mm * aspect
            span = max(orig_dx, orig_dy)
            scale = self.diameter_mm / span
            mesh_copy.apply_scale(scale)

        self.width_mm = target_w
        self.height_mm = target_h

        # 3. Setup orthographic grid
        W = self.output_resolution
        H = int(round(W * (target_h / target_w)))
        H = max(64, min(4096, H))

        pitch_x = target_w / float(W)
        pitch_y = target_h / float(H)
        half_w = target_w / 2.0
        half_h = target_h / 2.0

        # 4. Multi-stage surface sampling for ultra-sharp feature retention:
        # a) Exact mesh vertices
        # b) Triangle edge points
        # c) Dense face surface points
        n_samples = max(300000, min(1000000, len(mesh_copy.faces) * 10))
        sample_pts, _ = trimesh.sample.sample_surface(mesh_copy, n_samples)

        # Sample edges to preserve sharp lettering and rims
        edge_pts = []
        if len(mesh_copy.faces) < 150000:
            edges = mesh_copy.vertices[mesh_copy.edges_unique]
            t_vals = np.linspace(0.1, 0.9, 4)[:, None, None]
            interp = edges[:, 0][None, :, :] * (1.0 - t_vals) + edges[:, 1][None, :, :] * t_vals
            edge_pts = interp.reshape(-1, 3)

        if len(edge_pts) > 0:
            all_pts = np.vstack([mesh_copy.vertices, sample_pts, edge_pts])
        else:
            all_pts = np.vstack([mesh_copy.vertices, sample_pts])

        # 5. Project onto pixel grid
        px = np.clip(np.round((all_pts[:, 0] + half_w) / pitch_x).astype(int), 0, W - 1)
        py = np.clip(np.round((half_h - all_pts[:, 1]) / pitch_y).astype(int), 0, H - 1)
        pz = all_pts[:, 2]

        z_map = np.full((H, W), -1e9, dtype=np.float32)
        np.maximum.at(z_map, (py, px), pz)

        # 6. Inpaint unhit micro-voids between sample points
        unhit = (z_map <= -1e8)
        valid_vals = z_map[~unhit]
        base_val = np.min(valid_vals) if len(valid_vals) > 0 else 0.0
        z_map_clean = np.where(unhit, base_val, z_map)
        mask = unhit.astype(np.uint8)

        if np.any(unhit):
            z_filled = cv2.inpaint(z_map_clean, mask, 3, cv2.INPAINT_TELEA)
        else:
            z_filled = z_map_clean

        # 7. Normalize height values to 16-bit range (0..65535)
        # Laser Bas-Relief Convention:
        # High pixel value (65535 / Pure White) = Top unengraved crest
        # Low pixel value (0 / Pure Black)      = Deepest excavated cavity
        z_min = float(z_filled.min())
        z_max = float(z_filled.max())
        z_range = max(1e-6, z_max - z_min)
        norm_z = (z_filled - z_min) / z_range

        # 8. Boundary Masking
        # Circular boundary mask only applied for round medallions/coins
        if self.boundary_mode == 'circle' or (self.boundary_mode == 'auto' and abs(target_w - target_h) < 0.1 and "coin" in os.path.basename(self.stl_path).lower()):
            y_indices, x_indices = np.ogrid[:H, :W]
            rx = (x_indices - W / 2.0) * pitch_x
            ry = (y_indices - H / 2.0) * pitch_y
            outside_perimeter = (rx**2 + ry**2) > (self.diameter_mm / 2.0)**2

            if self.invert_relief:
                # For stamping dies/molds, outside boundary remains uncut surface (1.0)
                norm_z[outside_perimeter] = 1.0
            else:
                # For standard relief, outside boundary is floor (0.0)
                norm_z[outside_perimeter] = 0.0

        if self.invert_relief:
            norm_z = 1.0 - norm_z

        img_16bit = (norm_z * 65535.0).clip(0, 65535).astype(np.uint16)

        # 9. Save image
        if not output_png_path:
            base_name = os.path.splitext(self.stl_path)[0]
            output_png_path = f"{base_name}_{int(self.diameter_mm)}mm_relief_16bit.png"

        cv2.imwrite(output_png_path, img_16bit, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        self.heightmap_path = output_png_path

        elapsed = time.time() - t0
        print(f"[STL3DEngraver] Projected STL into 16-bit heightmap ({W}x{H}px) in {elapsed:.2f}s -> {output_png_path}")
        return output_png_path

    def compile_job_queue(
        self,
        hatch_pitch_mm: float = 0.025,
        clean_interval: int = 6,
        rot_step_deg: float = 15.0,
        **kwargs
    ) -> list:
        """
        Converts the 3D STL mesh into a high-precision heightmap and compiles the complete
        multi-pass 3D laser relief engraving queue with dynamic parameter binding.
        """
        if not self.heightmap_path or not os.path.exists(self.heightmap_path):
            self.convert_to_heightmap()

        pwr = kwargs.get('laser_power', self.laser_power)
        freq = kwargs.get('laser_freq', self.laser_freq)
        mark_spd = kwargs.get('mark_speed_mms', self.mark_speed_mms)
        jump_spd = kwargs.get('jump_speed_mms', self.jump_speed_mms)
        bidi = kwargs.get('bidirectional', self.bidirectional)
        contour = kwargs.get('enable_contour', self.enable_contour)

        slicer = Heightmap3DSlicer(
            heightmap_path=self.heightmap_path,
            diameter_mm=self.diameter_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            max_depth_mm=self.max_depth_mm,
            num_layers=self.num_layers,
            field_size=self.field_size,
            laser_power=pwr,
            laser_freq=freq,
            mark_speed_mms=mark_spd,
            jump_speed_mms=jump_spd,
            offset_x_mm=self.offset_x_mm,
            offset_y_mm=self.offset_y_mm,
            boundary_mode=self.boundary_mode,
            bidirectional=bidi,
            enable_contour=contour,
            invert_relief=False # Invert relief already applied to heightmap
        )

        self.slicer = slicer
        queue = slicer.compile_sliced_3d_queue(
            rot_step_deg=rot_step_deg,
            hatch_pitch_mm=hatch_pitch_mm,
            clean_interval=clean_interval,
            **kwargs
        )
        self.layers = getattr(slicer, 'layers', [])
        return queue

    def export_gcode(self, out_gcode_path: str, hatch_pitch_mm: float = 0.025, **kwargs):
        """Exports 3D G-code of the sliced STL toolpaths for 3D visualization and simulation."""
        if not self.slicer:
            self.compile_job_queue(hatch_pitch_mm=hatch_pitch_mm, **kwargs)
        self.slicer.export_gcode(out_gcode_path, hatch_pitch_mm=hatch_pitch_mm, **kwargs)

    export_sliced_gcode = export_gcode
    compile_sliced_3d_queue = compile_job_queue
