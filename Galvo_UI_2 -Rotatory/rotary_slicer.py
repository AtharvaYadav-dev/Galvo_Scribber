"""
Rotary Slicing Engine (EZCad2 RotaryMark / SplitMark2 Compatible)
=================================================================
Core mathematical and vector slicing engine for cylindrical laser marking.

Key Responsibilities:
1. Coordinate Transformation & Circumference Mapping (C = pi * D).
2. Liang-Barsky Vector Line-Segment Slicing across slice intervals.
3. Top Dead Center (TDC) Apex Recentering (Y_galvo = 0) to maintain optical focus.
4. Overlap Compensation to eliminate micro-stitching gaps or double-burning.
5. Bresenham-Style Zero-Drift Fractional Pulse Tracking across all slices.
6. Support for Split by Size, Mark by Split Line, and Angular Indexing modes.
7. Procedural test pattern generation (360° graduation ruler, diamond mesh).
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any


@dataclass
class RotaryConfig:
    """Configuration parameters for rotary axis and split marking."""
    # Rotary Axis Mapping
    axis: str = 'Y'                        # 'Y' (standard rotary) or 'X'
    diameter: float = 25.0                 # Workpiece diameter in mm (D)
    pulses_per_rev: int = 400              # Motor pulses per revolution (P_rev) - 400 pulses/rev (200-step motor at 2x microstepping, closes 3mm gap perfectly)
    gear_ratio: float = 1.0                # Reduction ratio (Motor Revs / Chuck Revs)
    reverse_dir: bool = False              # Invert rotation direction
    ring_inside: bool = False              # Inner bore marking for rings/tubes
    z_offset: float = 0.0                  # Focal height compensation delta (mm)
    stepper_axis: str = 'Z'                # Hardware motor axis ('Z', 'X', 'Y') - Defaults to Z for Rotary!
    axial_length: float = 60.0             # Workpiece axial length in mm

    # Marking & Split Mode
    mode: str = 'split_by_size'            # 'split_by_size', 'split_by_line', 'angular_index'
    split_size: float = 1.0                # Strip width S in mm (e.g. 0.5 - 5.0 mm)
    overlap: float = 0.06                  # Overlap compensation in mm (0.05 - 0.10 mm eliminates slice gaps)
    angular_parts: int = 4                 # N stations for angular indexing mode
    custom_split_lines: List[float] = field(default_factory=list)

    # Rotary Kinematics
    start_speed: float = 40.0              # Gentle start speed in pps (no jerk)
    max_speed: float = 600.0               # Smooth top slew speed in pps (1.2 rev/s, zero jerk, high torque)
    accel_time_ms: float = 250.0           # Smooth 250ms acceleration / deceleration ramp
    settling_delay_ms: float = 150.0       # Settle delay (ms) for vibration damping
    return_to_zero: bool = True            # Return to initial angular origin after job
    pattern_repeats: int = 0               # Total repeat count when using procedural pipe patterns
    align_to_repeats: bool = True          # Auto-align slice intervals to pattern repeats (zero-seam slicing)
    stagger_seam: bool = True              # Stagger slice seam cuts for 45 deg / angled hatches

    @property
    def circumference(self) -> float:
        """C = pi * D (mm)"""
        return math.pi * max(0.001, self.diameter)

    @property
    def total_pulses_360(self) -> float:
        """Total stepper pulses required for one complete 360 deg chuck revolution."""
        return self.pulses_per_rev * self.gear_ratio

    @property
    def pulses_per_mm(self) -> float:
        """K = Total Pulses / Circumference (pulses / mm)"""
        return self.total_pulses_360 / self.circumference

    @property
    def mm_per_pulse(self) -> float:
        """Linear distance on circumference moved per stepper pulse."""
        return self.circumference / max(1.0, self.total_pulses_360)

    @property
    def deg_per_pulse(self) -> float:
        """Angular rotation in degrees per stepper pulse."""
        return 360.0 / max(1.0, self.total_pulses_360)

    @property
    def reverse_direction(self) -> bool:
        return self.reverse_dir

    @reverse_direction.setter
    def reverse_direction(self, val: bool):
        self.reverse_dir = val


@dataclass
class RotarySlice:
    """Represents an individual sliced strip prepared for galvo & rotary execution."""
    slice_index: int                       # 0-indexed slice order
    axis: str                              # 'X' or 'Y'
    bounds_orig: Tuple[float, float]       # (coord_min, coord_max) in unwrapped artwork space
    center_orig: float                     # Center position in unwrapped artwork space (mm)
    rotation_angle_deg: float              # Angular position of cylinder for this slice (deg)
    delta_distance_mm: float               # Relative advance distance from previous slice (mm)
    step_pulses: int                       # Integer stepper pulses to execute for this slice
    accumulated_pulse_error: float         # Bresenham remainder tracking error (fractional pulses)
    paths: List[List[Tuple[float, float]]] # Sliced vector polylines RECENTERED to Apex (Y=0 or X=0)
    unwrapped_paths: List[List[Tuple[float, float]]] # Original unwrapped paths for visual overlay
    total_path_length_mm: float = 0.0      # Total marking vector length in this slice
    mark_count: int = 0                    # Total vector vertices
    completion_pulses: int = 0             # Pulses to complete full 360 revolution after all slices
    is_wrap_360: bool = False              # Indicates 360 wrap around cylinder


def clip_segment_1d(p1: Tuple[float, float], p2: Tuple[float, float],
                    low: float, high: float, axis_idx: int = 1) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Clips a 2D line segment p1 -> p2 against an infinite 1D slab [low, high]
    along the specified coordinate axis (axis_idx=1 for Y, axis_idx=0 for X).
    Returns (clipped_p1, clipped_p2) or None if outside.
    """
    v1 = p1[axis_idx]
    v2 = p2[axis_idx]
    dv = v2 - v1

    # Segment is a point or perpendicular to slice axis
    if abs(dv) < 1e-9:
        if low <= v1 <= high:
            return (p1, p2)
        return None

    # Parametric intersection t in [0, 1]
    t_min = 0.0
    t_max = 1.0

    # Test lower boundary
    t_low = (low - v1) / dv
    # Test upper boundary
    t_high = (high - v1) / dv

    if dv > 0:
        t_enter = t_low
        t_exit = t_high
    else:
        t_enter = t_high
        t_exit = t_low

    t_min = max(t_min, t_enter)
    t_max = min(t_max, t_exit)

    if t_min > t_max:
        return None

    # Compute clipped endpoints
    cx1 = p1[0] + t_min * (p2[0] - p1[0])
    cy1 = p1[1] + t_min * (p2[1] - p1[1])
    cx2 = p1[0] + t_max * (p2[0] - p1[0])
    cy2 = p1[1] + t_max * (p2[1] - p1[1])

    return ((cx1, cy1), (cx2, cy2))


def clip_polyline_to_slab(poly: List[Tuple[float, float]],
                          low: float, high: float,
                          axis_idx: int = 1,
                          tol: float = 1e-4) -> List[List[Tuple[float, float]]]:
    """
    Clips a continuous polyline against a 1D slab [low, high].
    Preserves connected sub-paths when traversing within the slab.
    """
    if len(poly) < 2:
        return []

    # Quick Bounding Box Pre-Check along the slice axis
    coords = [pt[axis_idx] for pt in poly]
    min_val = min(coords)
    max_val = max(coords)

    if max_val < low or min_val > high:
        return []

    if min_val >= low and max_val <= high:
        return [list(poly)]

    clipped_polylines: List[List[Tuple[float, float]]] = []
    current_subpath: List[Tuple[float, float]] = []

    for i in range(len(poly) - 1):
        p1 = poly[i]
        p2 = poly[i + 1]
        clipped = clip_segment_1d(p1, p2, low, high, axis_idx=axis_idx)

        if clipped is not None:
            cp1, cp2 = clipped
            # Length filter (suppress micro noise < 0.5 micron)
            seg_len = math.hypot(cp2[0] - cp1[0], cp2[1] - cp1[1])
            if seg_len < 5e-4:
                continue

            if not current_subpath:
                current_subpath.append(cp1)
                current_subpath.append(cp2)
            else:
                last_pt = current_subpath[-1]
                # If continuous with previous endpoint, append cp2
                if math.hypot(last_pt[0] - cp1[0], last_pt[1] - cp1[1]) < tol:
                    current_subpath.append(cp2)
                else:
                    clipped_polylines.append(current_subpath)
                    current_subpath = [cp1, cp2]
        else:
            if current_subpath:
                clipped_polylines.append(current_subpath)
                current_subpath = []

    if current_subpath:
        clipped_polylines.append(current_subpath)

    return clipped_polylines


class RotarySlicingEngine:
    """
    Industrial vector slicing and kinematics engine for Rotary Laser Marking.
    Directly models EZCad2's RotaryMark and SplitMark2 utilities.
    """

    def __init__(self, config: Optional[RotaryConfig] = None):
        self.config = config or RotaryConfig()

    @staticmethod
    def get_artwork_bounds(paths: List[List[Tuple[float, float]]]) -> Tuple[float, float, float, float]:
        """Calculates (xmin, ymin, xmax, ymax) of all vector paths."""
        if not paths:
            return (0.0, 0.0, 0.0, 0.0)

        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for poly in paths:
            for x, y in poly:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

        if min_x == float('inf'):
            return (0.0, 0.0, 0.0, 0.0)

        return (min_x, min_y, max_x, max_y)

    def slice_artwork(self, paths: List[List[Tuple[float, float]]],
                      config: Optional[RotaryConfig] = None) -> Tuple[List[RotarySlice], Dict[str, Any]]:
        """
        Main slicing pipeline:
        1. Checks artwork bounds against cylindrical circumference C.
        2. Determines slice bands based on marking mode (Size, Lines, Angular).
        3. Clips paths into strips with overlap compensation.
        4. Recenters each strip to the laser focus Apex (Y_galvo = 0).
        5. Computes zero-drift fractional pulse tracking across all slices.
        """
        cfg = config or self.config
        axis_idx = 1 if cfg.axis.upper() == 'Y' else 0
        circumference = cfg.circumference
        pulses_per_mm = cfg.pulses_per_mm

        xmin, ymin, xmax, ymax = self.get_artwork_bounds(paths)
        art_w = max(0.0, xmax - xmin)
        art_h = max(0.0, ymax - ymin)

        dim_rotary = art_h if axis_idx == 1 else art_w
        dim_axial = art_w if axis_idx == 1 else art_h
        rotary_min = ymin if axis_idx == 1 else xmin
        rotary_max = ymax if axis_idx == 1 else xmax

        # Check for artwork exceeding 360 deg circumference or wrapping around
        wrap_warning = False
        wrap_overlap_mm = 0.0
        if dim_rotary > circumference + 0.01:
            wrap_warning = True
            wrap_overlap_mm = dim_rotary - circumference

        is_wrap_360 = (axis_idx == 1 and (dim_rotary >= circumference * 0.98 or getattr(cfg, 'force_wrap_360', False)))

        # Determine slice intervals
        slice_intervals: List[Tuple[float, float]] = []

        if cfg.mode in ('angular_index', 'angular_indexing'):
            # Mark full graphic at N discrete angles around 360 deg
            num_stations = max(1, getattr(cfg, 'angular_stations', getattr(cfg, 'angular_parts', 4)))
            step_deg = 360.0 / num_stations
            step_dist = circumference / num_stations

            slices: List[RotarySlice] = []
            accumulated_error = 0.0
            total_integer_pulses = 0

            for station_idx in range(num_stations):
                angle_deg = station_idx * step_deg
                delta_dist = step_dist if station_idx > 0 else 0.0

                ideal_pulses = delta_dist * pulses_per_mm + accumulated_error
                step_pulse = int(round(ideal_pulses))
                accumulated_error = ideal_pulses - step_pulse
                total_integer_pulses += step_pulse

                center_rot = (rotary_min + rotary_max) / 2.0
                recentered_paths = []
                total_len = 0.0
                vert_count = 0

                for poly in paths:
                    new_poly = []
                    for pt in poly:
                        if axis_idx == 1:
                            new_poly.append((pt[0], pt[1] - center_rot))
                        else:
                            new_poly.append((pt[0] - center_rot, pt[1]))
                    recentered_paths.append(new_poly)
                    vert_count += len(new_poly)
                    for k in range(len(new_poly) - 1):
                        total_len += math.hypot(new_poly[k+1][0] - new_poly[k][0], new_poly[k+1][1] - new_poly[k][1])

                slice_obj = RotarySlice(
                    slice_index=station_idx,
                    axis=cfg.axis,
                    bounds_orig=(rotary_min, rotary_max),
                    center_orig=center_rot,
                    rotation_angle_deg=angle_deg,
                    delta_distance_mm=delta_dist,
                    step_pulses=step_pulse if not cfg.reverse_dir else -step_pulse,
                    accumulated_pulse_error=accumulated_error,
                    paths=recentered_paths,
                    unwrapped_paths=paths,
                    total_path_length_mm=total_len,
                    mark_count=vert_count,
                    is_wrap_360=True
                )
                slices.append(slice_obj)

            stats = {
                'slice_count': len(slices),
                'mode': cfg.mode,
                'total_pulses': total_integer_pulses,
                'accumulated_error_pulses': accumulated_error,
                'wrap_warning': wrap_warning,
                'wrap_overlap_mm': wrap_overlap_mm,
                'circumference_mm': circumference,
                'artwork_dim_rotary': dim_rotary,
                'artwork_dim_axial': dim_axial,
                'pulses_per_mm': pulses_per_mm,
                'is_wrap_360': True,
                'completion_pulses': 0,
                'estimated_time_s': self.estimate_execution_time(slices, cfg)
            }
            return slices, stats

        elif cfg.mode == 'split_by_line' and cfg.custom_split_lines:
            # Custom user-defined split lines
            sorted_lines = sorted(set(cfg.custom_split_lines))
            boundaries = [rotary_min] + [l for l in sorted_lines if rotary_min < l < rotary_max] + [rotary_max]
            for i in range(len(boundaries) - 1):
                slice_intervals.append((boundaries[i], boundaries[i+1]))
        elif is_wrap_360:
            # Full 360-degree Circumferential Wrap (e.g. 0-360° Scale Ruler or 360° Auto-Fit Text)
            # Slices tile exactly [0, circumference] with uniform width s = C / N
            rotary_min = 0.0
            rotary_max = circumference

            # Smart Pattern Repeat Slicing (100% Zero-Seam Station Alignment):
            # When align_to_repeats is enabled and pattern_repeats > 1:
            # Slice intervals align 100% with the repeat stations (C / N)!
            # Slice cuts fall EXACTLY between cells and NEVER chop through 45° hatch lines!
            if getattr(cfg, 'align_to_repeats', True) and getattr(cfg, 'pattern_repeats', 0) > 1:
                N = int(cfg.pattern_repeats)
                split_s = circumference / N
                slice_intervals = [(i * split_s, (i + 1) * split_s) for i in range(N)]
            else:
                N = max(1, int(round(circumference / max(0.05, cfg.split_size))))
                split_s = circumference / N
                slice_intervals = [(i * split_s, (i + 1) * split_s) for i in range(N)]
        else:
            # Standard Cylindrical Slicing by Split Size (S)
            # Pulse-synchronized slice intervals: ensure each band matches the motor physical step!
            pulses_per_band = max(1, int(round(cfg.split_size * pulses_per_mm))) if pulses_per_mm > 1e-4 else 1
            actual_band_dist = pulses_per_band / pulses_per_mm if pulses_per_mm > 1e-4 else cfg.split_size

            curr = rotary_min
            while curr < rotary_max - 1e-6:
                rem = rotary_max - curr
                if rem <= actual_band_dist * 1.25:
                    step_w = rem
                else:
                    step_w = actual_band_dist
                nxt = curr + step_w
                slice_intervals.append((curr, nxt))
                curr = nxt

        if not slice_intervals:
            slice_intervals = [(rotary_min, rotary_max)]

        # Process each slice interval with Liang-Barsky and Apex Recentering
        slices: List[RotarySlice] = []
        accumulated_error = 0.0
        prev_center = 0.0  # Hardware chuck reference starts at physical origin 0.0!
        total_integer_pulses = 0
        half_overlap = max(0.0, float(cfg.overlap)) / 2.0

        for idx, (b_start, b_end) in enumerate(slice_intervals):
            slice_center = (b_start + b_end) / 2.0
            
            # Overlap Compensation
            slab_low = b_start - half_overlap
            slab_high = b_end + half_overlap

            # Clip all vectors against this slice band
            unwrapped_slice_paths: List[List[Tuple[float, float]]] = []
            recentered_slice_paths: List[List[Tuple[float, float]]] = []
            total_len = 0.0
            vert_count = 0

            for poly_idx, poly in enumerate(paths):
                # Staggered Seam Blend for 45°/diagonal hatches:
                # Interleaves boundary cut points across adjacent lines so connection
                # points never form a visible horizontal line dividing the sections
                if getattr(cfg, 'stagger_seam', True):
                    stagger = (((poly_idx % 4) - 1.5) / 1.5) * min(0.06, max(0.01, half_overlap + 0.03))
                else:
                    stagger = 0.0

                clipped_polys = clip_polyline_to_slab(
                    poly,
                    slab_low - stagger,
                    slab_high + stagger,
                    axis_idx=axis_idx
                )
                for c_poly in clipped_polys:
                    if len(c_poly) < 2:
                        continue
                    c_len = sum(math.hypot(c_poly[k+1][0] - c_poly[k][0], c_poly[k+1][1] - c_poly[k][1]) for k in range(len(c_poly)-1))
                    if c_len < 0.005:
                        continue
                    unwrapped_slice_paths.append(c_poly)
                    
                    # RECENTER TO APEX (Y_galvo = 0 or X_galvo = 0)
                    recenter_poly = []
                    for x, y in c_poly:
                        if axis_idx == 1:
                            recenter_poly.append((x, y - slice_center))
                        else:
                            recenter_poly.append((x - slice_center, y))
                            
                    recentered_slice_paths.append(recenter_poly)
                    vert_count += len(recenter_poly)
                    for k in range(len(recenter_poly) - 1):
                        total_len += math.hypot(recenter_poly[k+1][0] - recenter_poly[k][0],
                                                recenter_poly[k+1][1] - recenter_poly[k][1])

            # Calculate relative advance distance from previous slice center
            delta_dist = slice_center - prev_center
            prev_center = slice_center

            # Bresenham-Style Fractional Pulse Tracking
            ideal_pulses = delta_dist * pulses_per_mm + accumulated_error
            step_pulse = int(round(ideal_pulses))
            accumulated_error = ideal_pulses - step_pulse
            total_integer_pulses += step_pulse

            # Convert to degrees on cylinder
            angle_deg = (slice_center % circumference) * (360.0 / circumference)

            slice_obj = RotarySlice(
                slice_index=idx,
                axis=cfg.axis,
                bounds_orig=(b_start, b_end),
                center_orig=slice_center,
                rotation_angle_deg=angle_deg,
                delta_distance_mm=delta_dist,
                step_pulses=step_pulse if not cfg.reverse_dir else -step_pulse,
                accumulated_pulse_error=accumulated_error,
                paths=recentered_slice_paths,
                unwrapped_paths=unwrapped_slice_paths,
                total_path_length_mm=total_len,
                mark_count=vert_count,
                is_wrap_360=is_wrap_360
            )
            slices.append(slice_obj)

        completion_pulses = 0
        if is_wrap_360 and slices:
            delta_final = circumference - prev_center
            ideal_final = delta_final * pulses_per_mm + accumulated_error
            completion_pulses = int(round(ideal_final))
            total_integer_pulses += completion_pulses
            slices[-1].completion_pulses = completion_pulses if not cfg.reverse_dir else -completion_pulses

        stats = {
            'slice_count': len(slices),
            'mode': cfg.mode,
            'split_size_mm': cfg.split_size,
            'overlap_mm': cfg.overlap,
            'total_pulses': total_integer_pulses,
            'accumulated_error_pulses': accumulated_error,
            'wrap_warning': wrap_warning,
            'wrap_overlap_mm': wrap_overlap_mm,
            'circumference_mm': circumference,
            'artwork_dim_rotary': dim_rotary,
            'artwork_dim_axial': dim_axial,
            'pulses_per_mm': pulses_per_mm,
            'is_wrap_360': is_wrap_360,
            'completion_pulses': completion_pulses,
            'estimated_time_s': self.estimate_execution_time(slices, cfg)
        }

        return slices, stats

    def slice_paths(self, paths: List[List[Tuple[float, float]]],
                    config: Optional[RotaryConfig] = None) -> List[RotarySlice]:
        """Convenience method returning the list of generated slices."""
        slices, _ = self.slice_artwork(paths, config)
        return slices

    def estimate_execution_time(self, slices: List[RotarySlice], cfg: RotaryConfig,
                                mark_speed_mm_s: float = 500.0) -> float:
        """
        Estimates total job execution time including galvo marking,
        stepper trapezoidal acceleration, and settling delays.
        """
        total_time = 0.0
        accel_s = cfg.accel_time_ms / 1000.0
        settle_s = cfg.settling_delay_ms / 1000.0

        for sl in slices:
            # 1. Stepper motion time (trapezoidal profile approximation)
            pulses = abs(sl.step_pulses)
            if pulses > 0:
                slew_speed = max(cfg.start_speed, min(cfg.max_speed, 4000.0))
                travel_s = pulses / slew_speed + accel_s
                total_time += travel_s + settle_s

            # 2. Galvo marking time (assume nominal 500 mm/s mark speed)
            total_time += (sl.total_path_length_mm / 500.0) + (sl.mark_count * 0.0005)

        # 3. Return to zero
        if cfg.return_to_zero and slices:
            total_pulses = sum(abs(sl.step_pulses) for sl in slices)
            total_time += (total_pulses / max(100.0, cfg.max_speed)) + accel_s

        return round(total_time, 2)

    # -------------------------------------------------------------------------
    # Procedural Test Pattern Generators (For instant calibration & verification)
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_cylindrical_ruler(diameter: float = 25.0, length: float = 30.0,
                                   tick_spacing_deg: float = 5.0) -> List[List[Tuple[float, float]]]:
        """
        Generates a 360-degree cylindrical calibration ruler with graduation ticks
        every `tick_spacing_deg` (e.g. 5 deg or 10 deg) and major ticks with numbers.
        Perfect for verifying gear ratio, pulses per rev, and rotary calibration.
        """
        c = math.pi * diameter
        paths: List[List[Tuple[float, float]]] = []

        # Longitudinal baseline along the cylinder
        paths.append([(0.0, 0.0), (0.0, c)])
        paths.append([(length, 0.0), (length, c)])

        num_ticks = int(round(360.0 / tick_spacing_deg))
        for i in range(num_ticks + 1):
            deg = i * tick_spacing_deg
            if deg > 360.0:
                break
            y = (deg / 360.0) * c

            # Tick length
            if deg % 45.0 == 0:
                tick_len = 10.0  # Major tick
            elif deg % 15.0 == 0:
                tick_len = 6.0   # Medium tick
            else:
                tick_len = 3.0   # Minor tick

            paths.append([(0.0, y), (tick_len, y)])
            paths.append([(length - tick_len, y), (length, y)])

        return paths

    # -------------------------------------------------------------------------
    # PROCEDURAL PIPE & CYLINDRICAL WRAP PATTERN GENERATORS (100% 360° COVERAGE)
    # -------------------------------------------------------------------------
    @staticmethod
    def hatch_polygon_cells(
        polys,
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        cross_hatch: bool = False,
        cross_angle_offset: float = 90.0,
        triple_pass: bool = False,
        hatch_type: str = 'line',
        unidirectional: bool = False,
        edge_inset_mm: float = 0.0
    ):
        """
        Advanced industrial hatch generator for closed pattern polygons (rectangles, diamonds, hexes).
        Supports:
        - Arbitrary line pitch and orientation angle
        - Cross hatch (orthogonal or custom angle offset)
        - Triple-pass (0°, 60°, 120° tri-tone / velvet matte)
        - Concentric ring / nested polygon infill
        - Unidirectional (one-way scan, uniform glare) vs. Bidirectional (meander)
        - Inner edge inset margin
        - Micro-segment burn suppression (< 0.01mm)
        """
        if not polys:
            return []
        pitch = max(0.005, float(pitch_mm))
        inset = max(0.0, float(edge_inset_mm))
        h_type = (hatch_type or 'line').lower()

        # Handle Concentric / Nested Infill
        if h_type in ('concentric', 'rings', 'ring'):
            try:
                from shapely.geometry import Polygon
                hatch_lines = []
                for poly in polys:
                    if len(poly) < 3:
                        continue
                    try:
                        poly_closed = poly if poly[0] == poly[-1] else poly + [poly[0]]
                        p_obj = Polygon(poly_closed)
                        if not p_obj.is_valid:
                            p_obj = p_obj.buffer(0)
                        start_offset = max(pitch, inset)
                        curr_p = p_obj.buffer(-start_offset)
                        while not curr_p.is_empty:
                            if curr_p.geom_type == 'Polygon':
                                coords = list(curr_p.exterior.coords)
                                if len(coords) >= 2:
                                    hatch_lines.append([(round(c[0], 3), round(c[1], 3)) for c in coords])
                            elif curr_p.geom_type == 'MultiPolygon':
                                for g in curr_p.geoms:
                                    coords = list(g.exterior.coords)
                                    if len(coords) >= 2:
                                        hatch_lines.append([(round(c[0], 3), round(c[1], 3)) for c in coords])
                            curr_p = curr_p.buffer(-pitch)
                    except Exception:
                        pass
                return hatch_lines
            except ImportError:
                pass

        try:
            from core.fill.fill.fills import scanline_fill
        except ImportError:
            return []

        # Determine hatch angles based on requested mode
        angles = [angle_deg]
        if triple_pass or h_type in ('triple', 'tri_pass', 'tri'):
            angles = [angle_deg, angle_deg + 60.0, angle_deg + 120.0]
        elif cross_hatch or h_type in ('cross', 'dual'):
            angles.append(angle_deg + cross_angle_offset)

        # Apply edge inset if requested
        if inset > 0.0001:
            try:
                from shapely.geometry import Polygon
                inset_polys = []
                for poly in polys:
                    if len(poly) < 3:
                        continue
                    p_c = poly if poly[0] == poly[-1] else poly + [poly[0]]
                    p_obj = Polygon(p_c)
                    if not p_obj.is_valid:
                        p_obj = p_obj.buffer(0)
                    b_obj = p_obj.buffer(-inset)
                    if not b_obj.is_empty:
                        if b_obj.geom_type == 'Polygon':
                            inset_polys.append(list(b_obj.exterior.coords))
                        elif b_obj.geom_type == 'MultiPolygon':
                            for g in b_obj.geoms:
                                inset_polys.append(list(g.exterior.coords))
                polys = inset_polys
            except Exception:
                pass

        complex_polys = []
        for poly in polys:
            if len(poly) < 3:
                continue
            for pt in poly:
                complex_polys.append(complex(pt[0], pt[1]))
            complex_polys.append(None)

        if not complex_polys:
            return []

        hatch_lines = []
        for a in angles:
            try:
                points = scanline_fill({"hatch_distance": str(pitch), "hatch_angle": f"{a}deg"}, complex_polys, None)
                if not points:
                    continue
                curr = []
                for pt in points:
                    if pt is None:
                        if len(curr) >= 2:
                            seg_len = math.hypot(curr[-1][0] - curr[0][0], curr[-1][1] - curr[0][1])
                            if seg_len >= 0.01:
                                if unidirectional:
                                    if (curr[-1][0] < curr[0][0]) or (curr[-1][0] == curr[0][0] and curr[-1][1] < curr[0][1]):
                                        curr = curr[::-1]
                                hatch_lines.append(curr)
                        curr = []
                    else:
                        if isinstance(pt, complex):
                            curr.append((round(pt.real, 3), round(pt.imag, 3)))
                        else:
                            curr.append((round(pt[0], 3), round(pt[1], 3)))
                if len(curr) >= 2:
                    seg_len = math.hypot(curr[-1][0] - curr[0][0], curr[-1][1] - curr[0][1])
                    if seg_len >= 0.01:
                        if unidirectional:
                            if (curr[-1][0] < curr[0][0]) or (curr[-1][0] == curr[0][0] and curr[-1][1] < curr[0][1]):
                                curr = curr[::-1]
                        hatch_lines.append(curr)
            except Exception:
                pass
        return hatch_lines

    @staticmethod
    def deduplicate_polygon_edges(polys: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
        """
        Extracts edges from polygons and removes duplicate / shared edges
        so every line in a tessellated mesh is marked exactly once without double burning.
        """
        seen = set()
        result = []
        for poly in polys:
            if not poly or len(poly) < 2:
                continue
            for i in range(len(poly) - 1):
                p1 = poly[i]
                p2 = poly[i + 1]
                if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) < 0.005:
                    continue
                k1 = (round(p1[0], 2), round(p1[1], 2))
                k2 = (round(p2[0], 2), round(p2[1], 2))
                if k1 == k2:
                    continue
                edge_key = (min(k1, k2), max(k1, k2))
                if edge_key not in seen:
                    seen.add(edge_key)
                    result.append([p1, p2])
        return result

    @staticmethod
    def _combine_hatched_cells(
        even_cells,
        odd_cells,
        hatch_style: str = 'odd_even',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = False,
        cross_angle_offset: float = 90.0,
        unidirectional: bool = False,
        edge_inset_mm: float = 0.0
    ):
        """
        Combines even and odd closed cells according to chosen hatch style:
        - odd_even: half boxes hatched (even cells hatched), half empty (odd cells blank).
        - even_odd: inverted odd/even (odd cells hatched), half empty (even cells blank).
        - solid_alternate: only alternating hatched boxes, unhatched boxes are completely omitted.
        - cross_angle: 0° / 90° dual angle alternating (chess).
        - herringbone: 45° / -45° herringbone twill alternating infill.
        - tri_angle: 3-angle prism (0° / 60° / 120° tri-tone).
        - concentric: concentric ring nested cell infill.
        - cell_cross: dual pass cross-hatch inside each cell (+90° 2nd pass).
        - all: all cells hatched.
        - none: wireframe outlines only.
        """
        style = (hatch_style or 'none').lower()
        paths = []

        if style in ('odd_even', 'half_odd_even', 'checkerboard', 'odd'):
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, angle_deg, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                paths.extend(even_cells)
        elif style in ('even_odd', 'inverted'):
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                odd_cells, pitch_mm, angle_deg, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                paths.extend(odd_cells)
        elif style in ('solid_alternate', 'solid', 'solid_blocks'):
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, angle_deg, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                paths.extend(even_cells)
        elif style in ('cross_angle', 'dual_angle', 'chess', 'perpendicular'):
            hatches_a = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, angle_deg, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            hatches_b = RotarySlicingEngine.hatch_polygon_cells(
                odd_cells, pitch_mm, angle_deg + cross_angle_offset, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches_a)
            paths.extend(hatches_b)
            if mark_contour:
                deduped = RotarySlicingEngine.deduplicate_polygon_edges(even_cells + odd_cells)
                paths.extend(deduped)
        elif style in ('herringbone', 'twill', 'chevron_infill', '45_45'):
            # Symmetrical 45° / -45° herringbone twill weave
            ang_a = angle_deg if abs(angle_deg) > 1e-3 else 45.0
            ang_b = -ang_a
            hatches_a = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, ang_a, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            hatches_b = RotarySlicingEngine.hatch_polygon_cells(
                odd_cells, pitch_mm, ang_b, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches_a)
            paths.extend(hatches_b)
            if mark_contour:
                deduped = RotarySlicingEngine.deduplicate_polygon_edges(even_cells + odd_cells)
                paths.extend(deduped)
        elif style in ('tri_angle', 'prism', 'tri_tone', 'tri'):
            # 3-Angle Prism holographic infill
            cells_a = [c for i, c in enumerate(even_cells) if i % 2 == 0]
            cells_b = [c for i, c in enumerate(even_cells) if i % 2 == 1]
            hatches_a = RotarySlicingEngine.hatch_polygon_cells(cells_a, pitch_mm, angle_deg, unidirectional=unidirectional)
            hatches_b = RotarySlicingEngine.hatch_polygon_cells(cells_b, pitch_mm, angle_deg + 60.0, unidirectional=unidirectional)
            hatches_c = RotarySlicingEngine.hatch_polygon_cells(odd_cells, pitch_mm, angle_deg + 120.0, unidirectional=unidirectional)
            paths.extend(hatches_a)
            paths.extend(hatches_b)
            paths.extend(hatches_c)
            if mark_contour:
                deduped = RotarySlicingEngine.deduplicate_polygon_edges(even_cells + odd_cells)
                paths.extend(deduped)
        elif style in ('concentric', 'rings', 'nested'):
            # Inward concentric contour loops
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, angle_deg, hatch_type='concentric', edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                paths.extend(even_cells)
        elif style in ('cell_cross', 'double', 'cross_both'):
            # Cross-hatch (+90° orthogonal) inside every hatched cell
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                even_cells, pitch_mm, angle_deg, cross_hatch=True,
                cross_angle_offset=cross_angle_offset, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                paths.extend(even_cells)
        elif style in ('all', 'all_hatched', '100%'):
            hatches = RotarySlicingEngine.hatch_polygon_cells(
                even_cells + odd_cells, pitch_mm, angle_deg, unidirectional=unidirectional, edge_inset_mm=edge_inset_mm
            )
            paths.extend(hatches)
            if mark_contour:
                deduped = RotarySlicingEngine.deduplicate_polygon_edges(even_cells + odd_cells)
                paths.extend(deduped)
        else:
            deduped = RotarySlicingEngine.deduplicate_polygon_edges(even_cells + odd_cells)
            paths.extend(deduped)

        return paths

    @staticmethod
    def generate_diamond_knurl(
        diameter: float,
        length: float,
        num_repeats: int = 24,
        axial_repeats: int = 0,
        hatch_style: str = 'none',
        pitch_mm: float = 0.05,
        angle_deg: float = 45.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates continuous diamond knurl mesh covering 100% of circumference C = pi * D.
        Supports odd/even alternating diamond facet hatching.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / py)))
        px = length / num_x

        if hatch_style and hatch_style != 'none':
            even_diamonds = []
            odd_diamonds = []
            half_inset = max(0.0, float(inset_mm)) / 2.0

            for ix in range(num_x):
                x0 = ix * px + half_inset
                x1 = (ix + 1) * px - half_inset
                x_mid = (x0 + x1) / 2.0
                for iy in range(num_repeats):
                    y0 = iy * py + half_inset
                    y1 = (iy + 1) * py - half_inset
                    y_mid = (y0 + y1) / 2.0
                    diamond = [
                        (round(x0, 3), round(y_mid, 3)),
                        (round(x_mid, 3), round(y1, 3)),
                        (round(x1, 3), round(y_mid, 3)),
                        (round(x_mid, 3), round(y0, 3)),
                        (round(x0, 3), round(y_mid, 3))
                    ]
                    if (ix + iy) % 2 == 0:
                        even_diamonds.append(diamond)
                    else:
                        odd_diamonds.append(diamond)

            return RotarySlicingEngine._combine_hatched_cells(
                even_diamonds, odd_diamonds, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
            )
        else:
            paths = []
            for ix in range(num_x):
                x0 = ix * px
                x1 = (ix + 1) * px
                for iy in range(num_repeats):
                    y0 = iy * py
                    y1 = (iy + 1) * py
                    paths.append([(round(x0, 3), round(y0, 3)), (round(x1, 3), round(y1, 3))])
                    paths.append([(round(x0, 3), round(y1, 3)), (round(x1, 3), round(y0, 3))])
            return paths

    @staticmethod
    def generate_helical_spiral(diameter: float, length: float, num_starts: int = 6, num_turns: float = 1.0):
        """
        Generates seamless helical spiral ribbons wrapping continuously around the pipe.
        Starts are evenly distributed around 360°.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        paths = []
        steps = 80
        dx = length / steps
        for s in range(max(1, num_starts)):
            y_start = s * (c / num_starts)
            poly = []
            for i in range(steps + 1):
                x = i * dx
                y = (y_start + (x / length) * num_turns * c) % c
                if poly and y < poly[-1][1] - (c * 0.5):
                    paths.append(poly)
                    poly = []
                poly.append((round(x, 3), round(y, 3)))
            if poly:
                paths.append(poly)
        return paths

    @staticmethod
    def generate_axial_flutes(diameter: float, length: float, num_flutes: int = 24):
        """
        Generates longitudinal straight ribs/flutes evenly distributed around 360° circumference.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_flutes)
        paths = []
        for i in range(num_flutes):
            y = i * py
            paths.append([(0.0, round(y, 3)), (round(length, 3), round(y, 3))])
        return paths

    @staticmethod
    def generate_chevron_herringbone(diameter: float, length: float, num_repeats: int = 16):
        """
        Generates interlocking chevron / herringbone zigzag arrows seamlessly tiled around 360°.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        px = py * 1.5
        num_x = max(1, int(round(length / px)))
        px = length / num_x
        paths = []
        for ix in range(num_x):
            x_base = ix * px
            x_mid = x_base + px * 0.5
            x_end = x_base + px
            for iy in range(num_repeats):
                y0 = iy * py
                y_mid = y0 + py * 0.5
                y1 = (iy + 1) * py
                paths.append([(round(x_base, 3), round(y0, 3)), (round(x_mid, 3), round(y_mid, 3)), (round(x_base, 3), round(y1, 3))])
                paths.append([(round(x_mid, 3), round(y_mid, 3)), (round(x_end, 3), round(y0, 3))])
                paths.append([(round(x_mid, 3), round(y_mid, 3)), (round(x_end, 3), round(y1, 3))])
        return paths

    @staticmethod
    def generate_honeycomb(
        diameter: float,
        length: float,
        num_repeats: int = 12,
        axial_repeats: int = 0,
        hatch_style: str = 'none',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates a seamless hexagonal honeycomb lattice wrapping 360° around the cylinder,
        with optional odd/even alternating hexagonal cell hatching.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        r = py / math.sqrt(3)
        px = 1.5 * r
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / px)))

        even_hexes = []
        odd_hexes = []
        r_adj = max(0.5, (r * 0.5) - (inset_mm / 2.0))

        for ix in range(num_x + 1):
            x_c = ix * px
            offset_y = (py * 0.5) if (ix % 2 == 1) else 0.0
            for iy in range(num_repeats):
                y_c = (iy * py + offset_y) % c
                hex_pts = []
                for a in range(6):
                    ang = math.radians(a * 60)
                    hx = x_c + r_adj * math.cos(ang)
                    hy = (y_c + r_adj * math.sin(ang))
                    hex_pts.append((round(hx, 3), round(hy, 3)))
                hex_pts.append(hex_pts[0])
                if (ix + iy) % 2 == 0:
                    even_hexes.append(hex_pts)
                else:
                    odd_hexes.append(hex_pts)

        if hatch_style and hatch_style != 'none':
            return RotarySlicingEngine._combine_hatched_cells(
                even_hexes, odd_hexes, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
            )
        else:
            return even_hexes + odd_hexes

    @staticmethod
    def generate_greek_key(diameter: float, length: float, num_repeats: int = 16):
        """
        Generates classical Greek meander / fretwork geometric border wrapping around 360°.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        num_bands = max(1, int(round(length / (py * 2.0))))
        bx_step = length / num_bands
        paths = []
        for b in range(num_bands):
            bx0 = b * bx_step + 2.0
            bw = bx_step - 4.0
            for iy in range(num_repeats):
                y0 = iy * py
                h = py
                pts = [
                    (round(bx0, 3), round(y0, 3)),
                    (round(bx0 + bw, 3), round(y0, 3)),
                    (round(bx0 + bw, 3), round(y0 + h * 0.7, 3)),
                    (round(bx0 + bw * 0.3, 3), round(y0 + h * 0.7, 3)),
                    (round(bx0 + bw * 0.3, 3), round(y0 + h * 0.3, 3)),
                    (round(bx0 + bw * 0.7, 3), round(y0 + h * 0.3, 3)),
                    (round(bx0 + bw * 0.7, 3), round(y0 + h * 0.5, 3)),
                    (round(bx0 + bw * 0.5, 3), round(y0 + h * 0.5, 3)),
                    (round(bx0 + bw * 0.5, 3), round(y0 + h * 0.4, 3)),
                ]
                paths.append(pts)
        return paths

    @staticmethod
    def generate_sine_waves(diameter: float, length: float, num_waves: int = 8, cycles: int = 4):
        """
        Generates harmonic undulating sinusoidal wave ribbons wrapping around 360°.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(1, num_waves)
        paths = []
        steps = 80
        amp = min(length * 0.2, py * 0.25)
        for w in range(num_waves):
            x_base = (w + 0.5) * (length / num_waves)
            poly = []
            for i in range(steps + 1):
                y = (i / steps) * c
                x = x_base + amp * math.sin(2.0 * math.pi * cycles * (y / c))
                poly.append((round(x, 3), round(y, 3)))
            paths.append(poly)
        return paths

    @staticmethod
    def generate_checkerboard(
        diameter: float,
        length: float,
        num_repeats: int = 16,
        axial_repeats: int = 0,
        hatch_style: str = 'odd_even',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates checkered square blocks around 360°, with odd/even alternating hatch infill.
        Supports half boxes hatched & half unhatched, inverted, solid alternating, 0°/90° cross, all, or outlines only.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / py)))
        px = length / num_x

        even_boxes = []
        odd_boxes = []
        half_inset = max(0.0, float(inset_mm)) / 2.0

        for ix in range(num_x):
            for iy in range(num_repeats):
                x0 = ix * px + half_inset
                x1 = (ix + 1) * px - half_inset
                y0 = iy * py + half_inset
                y1 = (iy + 1) * py - half_inset
                if x1 <= x0 or y1 <= y0:
                    continue
                box = [
                    (round(x0, 3), round(y0, 3)),
                    (round(x1, 3), round(y0, 3)),
                    (round(x1, 3), round(y1, 3)),
                    (round(x0, 3), round(y1, 3)),
                    (round(x0, 3), round(y0, 3))
                ]
                if (ix + iy) % 2 == 0:
                    even_boxes.append(box)
                else:
                    odd_boxes.append(box)

        return RotarySlicingEngine._combine_hatched_cells(
            even_boxes, odd_boxes, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
        )

    @staticmethod
    def generate_brick_subway(
        diameter: float,
        length: float,
        num_repeats: int = 16,
        axial_repeats: int = 0,
        hatch_style: str = 'odd_even',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates seamless brick / subway tile pattern with odd/even brick hatching.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / (py * 2.0))))
        px = length / num_x

        even_bricks = []
        odd_bricks = []
        half_inset = max(0.0, float(inset_mm)) / 2.0

        for iy in range(num_repeats):
            y0 = iy * py + half_inset
            y1 = (iy + 1) * py - half_inset
            row_shift = (px * 0.5) if (iy % 2 == 1) else 0.0
            for ix in range(-1, num_x + 1):
                bx0 = max(0.0, ix * px + row_shift + half_inset)
                bx1 = min(length, (ix + 1) * px + row_shift - half_inset)
                if bx1 - bx0 < 0.5 or y1 <= y0:
                    continue
                brick = [
                    (round(bx0, 3), round(y0, 3)),
                    (round(bx1, 3), round(y0, 3)),
                    (round(bx1, 3), round(y1, 3)),
                    (round(bx0, 3), round(y1, 3)),
                    (round(bx0, 3), round(y0, 3))
                ]
                if (ix + iy) % 2 == 0:
                    even_bricks.append(brick)
                else:
                    odd_bricks.append(brick)

        return RotarySlicingEngine._combine_hatched_cells(
            even_bricks, odd_bricks, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
        )

    @staticmethod
    def generate_fish_scale(
        diameter: float,
        length: float,
        num_repeats: int = 16,
        axial_repeats: int = 0,
        hatch_style: str = 'odd_even',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates Moroccan scallop / fish scale overlapping tile pattern with odd/even hatching.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        r = py * 0.55
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / (r * 1.5))))
        px = length / num_x

        even_scales = []
        odd_scales = []

        for ix in range(num_x + 1):
            x_c = ix * px
            offset_y = (py * 0.5) if (ix % 2 == 1) else 0.0
            for iy in range(num_repeats):
                y_c = (iy * py + offset_y) % c
                pts = []
                for a in range(-90, 91, 20):
                    ang = math.radians(a)
                    sx = x_c + (r - inset_mm * 0.5) * math.cos(ang)
                    sy = y_c + (r - inset_mm * 0.5) * math.sin(ang)
                    pts.append((round(sx, 3), round(sy, 3)))
                pts.append((round(x_c, 3), round(y_c - r * 0.8, 3)))
                pts.append(pts[0])
                if (ix + iy) % 2 == 0:
                    even_scales.append(pts)
                else:
                    odd_scales.append(pts)

        return RotarySlicingEngine._combine_hatched_cells(
            even_scales, odd_scales, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
        )

    @staticmethod
    def generate_basketweave(
        diameter: float,
        length: float,
        num_repeats: int = 16,
        axial_repeats: int = 0,
        hatch_style: str = 'cross_angle',
        pitch_mm: float = 0.05,
        angle_deg: float = 0.0,
        mark_contour: bool = True,
        inset_mm: float = 0.0, **kwargs
    ):
        """
        Generates carbon fiber twill / basketweave woven blocks with perpendicular cross-hatch.
        """
        c = math.pi * max(0.1, diameter)
        length = max(1.0, length)
        py = c / max(2, num_repeats)
        if axial_repeats and axial_repeats > 0:
            num_x = int(axial_repeats)
        else:
            num_x = max(1, int(round(length / py)))
        px = length / num_x

        horiz_blocks = []
        vert_blocks = []
        half_inset = max(0.0, float(inset_mm)) / 2.0

        for ix in range(num_x):
            for iy in range(num_repeats):
                x0 = ix * px + half_inset
                x1 = (ix + 1) * px - half_inset
                y0 = iy * py + half_inset
                y1 = (iy + 1) * py - half_inset
                b = [
                    (round(x0, 3), round(y0, 3)),
                    (round(x1, 3), round(y0, 3)),
                    (round(x1, 3), round(y1, 3)),
                    (round(x0, 3), round(y1, 3)),
                    (round(x0, 3), round(y0, 3))
                ]
                if (ix + iy) % 2 == 0:
                    horiz_blocks.append(b)
                else:
                    vert_blocks.append(b)

        return RotarySlicingEngine._combine_hatched_cells(
            horiz_blocks, vert_blocks, hatch_style, pitch_mm, angle_deg, mark_contour, **kwargs
        )

    @staticmethod
    def tile_paths_around_circumference(
        paths: List[List[Tuple[float, float]]],
        diameter: float,
        num_repeats: int = 4,
        scale_to_fit: bool = True
    ) -> List[List[Tuple[float, float]]]:
        """
        Repeats / tiles arbitrary vector artwork N times evenly spaced around the 360° pipe circumference.
        """
        if not paths:
            return []
        c = math.pi * max(0.1, diameter)
        num_repeats = max(1, num_repeats)
        step_y = c / num_repeats

        xs = [pt[0] for poly in paths for pt in poly]
        ys = [pt[1] for poly in paths for pt in poly]
        if not xs or not ys:
            return paths

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w_orig = max(1e-4, max_x - min_x)
        h_orig = max(1e-4, max_y - min_y)

        scale = (step_y * 0.88) / h_orig if scale_to_fit else 1.0

        tiled: List[List[Tuple[float, float]]] = []
        for k in range(num_repeats):
            y_base = k * step_y + (step_y - h_orig * scale) / 2.0
            for poly in paths:
                t_poly: List[Tuple[float, float]] = []
                for pt in poly:
                    nx = (pt[0] - min_x) * scale
                    ny = y_base + (pt[1] - min_y) * scale
                    t_poly.append((round(nx, 3), round(ny, 3)))
                tiled.append(t_poly)
        return tiled

    @staticmethod
    def generate_diamond_grid(width: float = 40.0, height: float = 78.5,
                              pitch: float = 5.0) -> List[List[Tuple[float, float]]]:
        """
        Generates a continuous diamond criss-cross mesh wrap for testing slice overlap.
        """
        paths: List[List[Tuple[float, float]]] = []
        # Diagonal lines +45 deg
        num_x = int(math.ceil((width + height) / pitch))
        for k in range(-num_x, num_x):
            x_start = k * pitch
            y_start = 0.0
            x_end = x_start + height
            y_end = height

            clipped = clip_segment_1d((x_start, y_start), (x_end, y_end), 0.0, width, axis_idx=0)
            if clipped:
                paths.append([clipped[0], clipped[1]])

        # Diagonal lines -45 deg
        for k in range(0, 2 * num_x):
            x_start = k * pitch
            y_start = 0.0
            x_end = x_start - height
            y_end = height

            clipped = clip_segment_1d((x_start, y_start), (x_end, y_end), 0.0, width, axis_idx=0)
            if clipped:
                paths.append([clipped[0], clipped[1]])

        return paths

    @staticmethod
    def generate_calibration_stripes(width: float = 30.0, height: float = 60.0,
                                     stripe_width: float = 5.0) -> List[List[Tuple[float, float]]]:
        """
        Generates alternating boxes/stripes across height to test split boundary alignment.
        """
        paths: List[List[Tuple[float, float]]] = []
        curr_y = 0.0
        idx = 0
        while curr_y < height:
            h = min(stripe_width, height - curr_y)
            # Rectangle outline
            p0 = (0.0, curr_y)
            p1 = (width, curr_y)
            p2 = (width, curr_y + h)
            p3 = (0.0, curr_y + h)
            paths.append([p0, p1, p2, p3, p0])

            # Infill hatch on even stripes
            if idx % 2 == 0:
                hatch_y = curr_y + 0.5
                while hatch_y < curr_y + h:
                    paths.append([(2.0, hatch_y), (width - 2.0, hatch_y)])
                    hatch_y += 0.5

            curr_y += stripe_width
            idx += 1

        return paths

    @staticmethod
    def generate_vernier_scale(diameter: float = 25.0, length: float = 25.0) -> List[List[Tuple[float, float]]]:
        """
        Generates a 360-degree vernier scale with major divisions every 30 deg,
        medium ticks every 10 deg, and minor ticks every 2 deg.
        """
        c = math.pi * diameter
        paths: List[List[Tuple[float, float]]] = []
        # Longitudinal baselines
        paths.append([(0.0, 0.0), (length, 0.0)])
        paths.append([(0.0, c), (length, c)])
        paths.append([(length, 0.0), (length, c)])

        for deg in range(0, 361, 2):
            y = (deg / 360.0) * c
            if deg % 30 == 0:
                tick = 12.0
            elif deg % 10 == 0:
                tick = 7.0
            else:
                tick = 3.5
            paths.append([(length - tick, y), (length, y)])

        return paths

    @staticmethod
    def generate_editable_ruler(
        ruler_type: str = 'degree',
        diameter: float = 25.0,
        total_span: float = 360.0,
        start_val: float = 0.0,
        minor_step: float = 1.0,
        medium_step: float = 5.0,
        major_step: float = 10.0,
        minor_len: float = 2.5,
        medium_len: float = 4.5,
        major_len: float = 7.0,
        axial_length: float = 30.0,
        tick_side: str = 'left',
        include_baseline: bool = True,
        include_numbers: bool = True,
        number_step: float = 10.0,
        number_font_size: float = 2.6,
        number_suffix: str = '°',
        direction: str = 'circumferential'
    ) -> List[List[Tuple[float, float]]]:
        """
        Generates a fully customizable engineering scale ruler with major/medium/minor
        graduation ticks, longitudinal baselines, and vector numbers.
        """
        c = math.pi * max(1.0, diameter)
        paths: List[List[Tuple[float, float]]] = []

        # Helper to render vector text digits
        def _render_vector_num(txt: str, cx: float, cy: float, sz: float) -> List[List[Tuple[float, float]]]:
            try:
                from PySide6.QtWidgets import QApplication
                from PySide6.QtGui import QPainterPath, QFont
                app = QApplication.instance()
                if not app:
                    app = QApplication([])
                font = QFont("Arial", int(sz * 4), QFont.Bold)
                qpath = QPainterPath()
                qpath.addText(0, 0, font, txt)
                rect = qpath.boundingRect()
                polys = qpath.toSubpathPolygons()
                res = []
                scale = sz / max(0.1, rect.height())
                for poly in polys:
                    pts = []
                    for k in range(poly.size()):
                        pt = poly.at(k)
                        px = cx + (pt.x() - rect.center().x()) * scale
                        py = cy - (pt.y() - rect.center().y()) * scale
                        pts.append((round(px, 3), round(py, 3)))
                    res.append(pts)
                return res
            except Exception:
                return []

        span = max(0.1, total_span)
        step = max(0.1, minor_step)
        num_ticks = int(round(span / step))

        is_deg = (ruler_type.lower() == 'degree')
        is_circ = (direction.lower() == 'circumferential')

        # Baseline start/end
        if is_circ:
            y_start = 0.0
            y_end = c if is_deg and abs(span - 360.0) < 1e-3 else (span / 360.0 * c if is_deg else span)
            base_x = 0.0 if tick_side == 'left' else (axial_length if tick_side == 'right' else 0.0)

            if include_baseline:
                paths.append([(base_x, y_start), (base_x, y_end)])
                if tick_side == 'both':
                    paths.append([(axial_length, y_start), (axial_length, y_end)])

            max_i = num_ticks if (not is_deg or span < 360.0 - 1e-3) else num_ticks - 1
            for i in range(max_i + 1):
                val = start_val + (i * step)
                if val > start_val + span + 1e-6:
                    break

                # Coordinate along circumference
                y = (val / 360.0 * c) if is_deg else val
                if y > c + 0.01 and is_deg:
                    break

                # Determine tick length
                is_major = (major_step > 0 and abs(val % major_step) < 1e-4)
                is_medium = (medium_step > 0 and abs(val % medium_step) < 1e-4)

                if is_major:
                    t_len = major_len
                elif is_medium:
                    t_len = medium_len
                else:
                    t_len = minor_len

                if tick_side in ('left', 'both'):
                    paths.append([(0.0, y), (t_len, y)])
                if tick_side in ('right', 'both'):
                    paths.append([(axial_length - t_len, y), (axial_length, y)])

                # Render vector numbers
                if include_numbers and is_major:
                    if number_step > 0 and abs(val % number_step) < 1e-4:
                        display_val = int(round(val)) if abs(val - round(val)) < 1e-4 else round(val, 1)
                        label_txt = f"{display_val}{number_suffix}"
                        lbl_x = t_len + (number_font_size * 0.8) if tick_side != 'right' else (axial_length - t_len - number_font_size * 1.5)
                        lbl_y = y
                        if abs(y) < 1e-3:
                            lbl_y = number_font_size * 0.55
                        paths.extend(_render_vector_num(label_txt, lbl_x, lbl_y, number_font_size))

        else: # Axial ruler
            x_start = 0.0
            x_end = span
            base_y = 0.0

            if include_baseline:
                paths.append([(x_start, base_y), (x_end, base_y)])

            for i in range(num_ticks + 1):
                val = start_val + (i * step)
                if val > start_val + span + 1e-6:
                    break

                x = val
                is_major = (major_step > 0 and abs(val % major_step) < 1e-4)
                is_medium = (medium_step > 0 and abs(val % medium_step) < 1e-4)

                if is_major:
                    t_len = major_len
                elif is_medium:
                    t_len = medium_len
                else:
                    t_len = minor_len

                paths.append([(x, base_y), (x, base_y + t_len)])

                if include_numbers and is_major:
                    if number_step > 0 and abs(val % number_step) < 1e-4:
                        display_val = int(round(val)) if abs(val - round(val)) < 1e-4 else round(val, 1)
                        label_txt = f"{display_val}{number_suffix}"
                        paths.extend(_render_vector_num(label_txt, x, base_y + t_len + (number_font_size * 0.8), number_font_size))

        return paths

    @staticmethod
    def generate_vector_text(
        text: str,
        font_family: str = "Arial",
        font_size_mm: float = 6.0,
        bold: bool = True,
        italic: bool = False,
        letter_spacing_mm: float = 0.5,
        orientation: str = 'circumferential',
        angle_deg: float = 0.0,
        diameter: float = 25.0,
        repeat_count: int = 1,
        auto_fit_360: bool = False,
        axial_length: float = 50.0
    ) -> List[List[Tuple[float, float]]]:
        """
        Converts text string into vector polylines for laser marking on a cylindrical workpiece.
        Supports font family, sizing, bold/italic, orientation, 360-degree auto-fit, and repetition around chuck.
        """
        if not text:
            return []

        c = math.pi * max(1.0, diameter)
        all_paths: List[List[Tuple[float, float]]] = []

        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QPainterPath, QFont
            app = QApplication.instance()
            if not app:
                app = QApplication([])
            reps = max(1, min(72, repeat_count))
            is_circ = (orientation.lower() == 'circumferential')

            # Initial vector path to measure tight bounding box
            ref_font = QFont(font_family, 24, QFont.Bold if bold else QFont.Normal)
            ref_font.setItalic(italic)
            ref_qpath = QPainterPath()
            ref_qpath.addText(0, 0, ref_font, text)
            ref_rect = ref_qpath.boundingRect()
            tight_aspect = ref_rect.width() / max(0.1, ref_rect.height())

            # If Auto-Fit 360° is requested, adjust font size so text occupies ~85% of circumference allocation
            eff_font_size = font_size_mm
            if auto_fit_360:
                target_span = (c / reps) * 0.85
                eff_font_size = max(1.2, min(50.0, target_span / max(0.5, tight_aspect)))

            font = QFont(font_family, int(eff_font_size * 4), QFont.Bold if bold else QFont.Normal)
            font.setItalic(italic)
            if letter_spacing_mm > 0.01:
                font.setLetterSpacing(QFont.AbsoluteSpacing, letter_spacing_mm * 4)

            qpath = QPainterPath()
            qpath.addText(0, 0, font, text)
            rect = qpath.boundingRect()
            polys = qpath.toSubpathPolygons()

            scale = eff_font_size / max(0.1, rect.height())

            # Convert to normalized centered mm paths
            norm_polys = []
            for poly in polys:
                pts = []
                for k in range(poly.size()):
                    pt = poly.at(k)
                    nx = (pt.x() - rect.center().x()) * scale
                    ny = -(pt.y() - rect.center().y()) * scale # Invert Y for CAD coords
                    pts.append((nx, ny))
                norm_polys.append(pts)

            # Apply user angle rotation if specified
            if abs(angle_deg) > 1e-3:
                rad = math.radians(angle_deg)
                cos_a, sin_a = math.cos(rad), math.sin(rad)
                rot_polys = []
                for poly in norm_polys:
                    rot_pts = [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in poly]
                    rot_polys.append(rot_pts)
                norm_polys = rot_polys

            # Place around cylinder circumference (repeat_count stations)
            base_x = axial_length / 2.0

            for rep_idx in range(reps):
                # Station center along circumference
                station_center_y = (rep_idx / reps) * c + (c / (2.0 * reps)) if is_circ else (c / 2.0)
                station_center_x = base_x + (rep_idx * (rect.width() * scale + 5.0)) if not is_circ else base_x

                for poly in norm_polys:
                    placed_pts = []
                    for nx, ny in poly:
                        if is_circ:
                            # Wrap around circumference along Y
                            px = station_center_x - ny
                            py = station_center_y + nx
                        else:
                            # Axial along cylinder length X
                            px = station_center_x + nx
                            py = station_center_y + ny
                        placed_pts.append((round(px, 3), round(py, 3)))
                    all_paths.append(placed_pts)

        except Exception as e:
            print(f"Vector text generation error: {e}")

        return all_paths

    @staticmethod
    def generate_hatch_fill(
        paths: List[List[Tuple[float, float]]],
        pitch_mm: float = 0.05,
        angle_deg: float = 45.0,
        cross_hatch: bool = True,
        mark_contour: bool = True,
        contour_first: bool = True,
        edge_offset_mm: float = 0.0,
        unidirectional: bool = False,
        cross_angle_offset: float = 90.0,
        triple_pass: bool = False,
        hatch_type: str = 'line'
    ) -> Tuple[List[List[Tuple[float, float]]], int]:
        """
        Generates EzCad-grade scanline vector hatch infill for closed artwork contours.
        Supports:
        - Arbitrary line pitch and orientation angle
        - Cross-hatch with customizable angle offset
        - Triple-pass (0°, 60°, 120°) velvet matte infill
        - Concentric ring / nested contour inward loops
        - Unidirectional (one-way scan) vs. Bidirectional (meander)
        - Inner edge offset (inset margin to avoid border burn)
        - Nesting resolution for compound polygons with holes (e.g. letters 'O', 'B', '8')
        - Contour outline marking (first, last, or infill only)
        """
        if not paths:
            return [], 0

        pitch = max(0.005, float(pitch_mm))
        edge_offset = max(0.0, float(edge_offset_mm))
        h_type = (hatch_type or 'line').lower()

        closed_contours = []
        open_strokes = []

        for poly in paths:
            if len(poly) >= 3:
                p0 = poly[0]
                p1 = poly[-1]
                dist_sq = (p0[0] - p1[0])**2 + (p0[1] - p1[1])**2
                if dist_sq <= (0.1)**2:
                    closed_contours.append(poly)
                else:
                    open_strokes.append(poly)
            else:
                open_strokes.append(poly)

        if not closed_contours:
            return paths, 0

        try:
            from shapely.geometry import Polygon
            from core.fill.fill.fills import scanline_fill
        except ImportError:
            print("Shapely or fill library unavailable for rotary hatching.")
            return paths, 0

        # Convert closed contours to Shapely polygons with hole resolution
        raw_polys = []
        for poly in closed_contours:
            try:
                poly_closed = poly if poly[0] == poly[-1] else poly + [poly[0]]
                p_obj = Polygon(poly_closed)
                if not p_obj.is_valid:
                    p_obj = p_obj.buffer(0)
                if not p_obj.is_empty:
                    if p_obj.geom_type == 'MultiPolygon':
                        raw_polys.extend(list(p_obj.geoms))
                    elif p_obj.geom_type == 'Polygon':
                        raw_polys.append(p_obj)
            except Exception:
                pass

        if not raw_polys:
            return paths, 0

        # Nesting depth calculation for solid vs hole
        n = len(raw_polys)
        depths = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j:
                    try:
                        if raw_polys[j].covers(raw_polys[i]):
                            depths[i] += 1
                    except Exception:
                        pass

        shells = [(i, raw_polys[i]) for i in range(n) if depths[i] % 2 == 0]
        holes = [(i, raw_polys[i]) for i in range(n) if depths[i] % 2 == 1]

        shapely_polys = []
        for s_idx, s_poly in shells:
            s_depth = depths[s_idx]
            direct_holes = []
            for h_idx, h_poly in holes:
                if depths[h_idx] == s_depth + 1:
                    try:
                        if s_poly.covers(h_poly):
                            direct_holes.append(h_poly.exterior.coords)
                    except Exception:
                        pass
            try:
                poly_with_holes = Polygon(shell=s_poly.exterior.coords, holes=direct_holes)
                if not poly_with_holes.is_valid:
                    poly_with_holes = poly_with_holes.buffer(0)
                if not poly_with_holes.is_empty:
                    if poly_with_holes.geom_type == 'MultiPolygon':
                        shapely_polys.extend(list(poly_with_holes.geoms))
                    else:
                        shapely_polys.append(poly_with_holes)
            except Exception:
                shapely_polys.append(s_poly)

        # Apply edge offset inset if requested
        working_polys = []
        for p in shapely_polys:
            if edge_offset > 0.0001:
                try:
                    buffered = p.buffer(-edge_offset)
                    if not buffered.is_empty:
                        if buffered.geom_type == 'MultiPolygon':
                            working_polys.extend(list(buffered.geoms))
                        else:
                            working_polys.append(buffered)
                except Exception:
                    working_polys.append(p)
            else:
                working_polys.append(p)

        if not working_polys:
            return paths, 0

        # Handle Concentric / Inward Loop Infill
        if h_type in ('concentric', 'rings', 'ring'):
            hatch_lines = []
            for wp in working_polys:
                curr_p = wp.buffer(-pitch)
                while not curr_p.is_empty:
                    if curr_p.geom_type == 'Polygon':
                        coords = list(curr_p.exterior.coords)
                        if len(coords) >= 2:
                            hatch_lines.append([(round(c[0], 3), round(c[1], 3)) for c in coords])
                    elif curr_p.geom_type == 'MultiPolygon':
                        for g in curr_p.geoms:
                            coords = list(g.exterior.coords)
                            if len(coords) >= 2:
                                hatch_lines.append([(round(c[0], 3), round(c[1], 3)) for c in coords])
                    curr_p = curr_p.buffer(-pitch)
            num_hatch_lines = len(hatch_lines)
            if mark_contour:
                final_paths = (list(paths) + hatch_lines) if contour_first else (hatch_lines + list(paths))
            else:
                final_paths = hatch_lines + open_strokes
            return final_paths, num_hatch_lines

        # Build complex list for scanline_fill
        complex_polys = []
        for wp in working_polys:
            for coord in wp.exterior.coords:
                complex_polys.append(complex(coord[0], coord[1]))
            complex_polys.append(None)
            for interior in wp.interiors:
                for coord in interior.coords:
                    complex_polys.append(complex(coord[0], coord[1]))
                complex_polys.append(None)

        angles = [angle_deg]
        if triple_pass or h_type in ('triple', 'tri_pass', 'tri'):
            angles = [angle_deg, angle_deg + 60.0, angle_deg + 120.0]
        elif cross_hatch or h_type in ('cross', 'dual'):
            angles.append(angle_deg + cross_angle_offset)

        hatch_lines = []
        for a in angles:
            settings = {
                "hatch_distance": str(pitch),
                "hatch_angle": f"{a}deg"
            }
            try:
                points = scanline_fill(settings, complex_polys, None)
                if not points:
                    continue
                curr = []
                for pt in points:
                    if pt is None:
                        if len(curr) >= 2:
                            seg_len = math.hypot(curr[-1][0] - curr[0][0], curr[-1][1] - curr[0][1])
                            if seg_len >= 0.01:
                                if unidirectional:
                                    if (curr[-1][0] < curr[0][0]) or (curr[-1][0] == curr[0][0] and curr[-1][1] < curr[0][1]):
                                        curr = curr[::-1]
                                hatch_lines.append(curr)
                        curr = []
                    else:
                        if isinstance(pt, complex):
                            curr.append((round(pt.real, 3), round(pt.imag, 3)))
                        else:
                            curr.append((round(pt[0], 3), round(pt[1], 3)))
                if len(curr) >= 2:
                    seg_len = math.hypot(curr[-1][0] - curr[0][0], curr[-1][1] - curr[0][1])
                    if seg_len >= 0.01:
                        if unidirectional:
                            if (curr[-1][0] < curr[0][0]) or (curr[-1][0] == curr[0][0] and curr[-1][1] < curr[0][1]):
                                curr = curr[::-1]
                        hatch_lines.append(curr)
            except Exception as e:
                print(f"Hatch pass at {a} deg error: {e}")

        num_hatch_lines = len(hatch_lines)

        if mark_contour:
            if contour_first:
                final_paths = list(paths) + hatch_lines
            else:
                final_paths = hatch_lines + list(paths)
        else:
            final_paths = hatch_lines + open_strokes

        return final_paths, num_hatch_lines

