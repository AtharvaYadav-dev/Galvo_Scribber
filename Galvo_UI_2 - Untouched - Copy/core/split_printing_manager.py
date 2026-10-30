"""
Split Printing Manager Module
-----------------------------
Provides intelligent multi-part / tiling split printing (up to max 8 splits)
for oversized or segmented laser engraving jobs (SVG, DXF, images, gerber, etc.).

Features:
- Robust Liang-Barsky polyline / path clipping against tile boundaries.
- Flexible split presets: 1x2, 2x1, 1x3, 3x1, 2x2, 2x3, 3x2, 2x4, 4x2, 8x1, 1x8.
- Automatic split suggestion based on file dimensions and lens field size.
- Active part tracking, sequential printing orchestration, and auto-pause prompting.
- Coordinate centering onto lens field for separate object placement.
"""

import math
from typing import List, Tuple, Dict, Optional, Any


def clip_line_liang_barsky(x1: float, y1: float, x2: float, y2: float,
                           xmin: float, xmax: float, ymin: float, ymax: float) -> Optional[Tuple[float, float, float, float]]:
    """
    Clips a 2D line segment (x1, y1) -> (x2, y2) against a bounding box [xmin, xmax, ymin, ymax]
    using the Liang-Barsky algorithm.
    Returns (cx1, cy1, cx2, cy2) or None if the segment is completely outside.
    """
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    u1 = 0.0
    u2 = 1.0

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None  # Parallel and outside
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if t > u2:
                    return None
                if t > u1:
                    u1 = t
            elif p[i] > 0:
                if t < u1:
                    return None
                if t < u2:
                    u2 = t

    if u1 > u2:
        return None

    return (x1 + u1 * dx, y1 + u1 * dy, x1 + u2 * dx, y1 + u2 * dy)


def clip_polygon_to_rect(poly: List[Tuple[float, float]],
                         xmin: float, xmax: float, ymin: float, ymax: float,
                         tol: float = 1e-4) -> List[List[Tuple[float, float]]]:
    """
    Clips a polyline against a rectangular bounding box.
    Returns a list of clipped continuous polylines.
    """
    if len(poly) < 2:
        return []

    # Fast Bounding Box Pre-Check
    p_xmin = min(pt[0] for pt in poly)
    p_xmax = max(pt[0] for pt in poly)
    p_ymin = min(pt[1] for pt in poly)
    p_ymax = max(pt[1] for pt in poly)

    # 1. Fully outside tile -> immediate reject
    if p_xmax < xmin or p_xmin > xmax or p_ymax < ymin or p_ymin > ymax:
        return []

    # 2. Fully inside tile -> immediate accept (no line clipping needed)
    if p_xmin >= xmin and p_xmax <= xmax and p_ymin >= ymin and p_ymax <= ymax:
        return [list(poly)]

    result_polys = []
    current_segment = []

    for i in range(len(poly) - 1):
        x1, y1 = poly[i]
        x2, y2 = poly[i + 1]
        clipped = clip_line_liang_barsky(x1, y1, x2, y2, xmin, xmax, ymin, ymax)
        if clipped is not None:
            cx1, cy1, cx2, cy2 = clipped
            if not current_segment:
                current_segment.append((cx1, cy1))
                current_segment.append((cx2, cy2))
            else:
                last_x, last_y = current_segment[-1]
                if abs(last_x - cx1) < tol and abs(last_y - cy1) < tol:
                    current_segment.append((cx2, cy2))
                else:
                    result_polys.append(current_segment)
                    current_segment = [(cx1, cy1), (cx2, cy2)]
        else:
            if current_segment:
                result_polys.append(current_segment)
                current_segment = []

    if current_segment:
        result_polys.append(current_segment)

    return result_polys


class SplitTile:
    """Represents a single partition/tile in a split job."""
    def __init__(self, index: int, col: int, row: int, rect: Tuple[float, float, float, float], label: str = "", manager=None):
        self.index = index                 # 0-indexed (0 .. N-1)
        self.part_number = index + 1        # 1-indexed (1 .. N)
        self.col = col                     # column index (0 .. cols-1)
        self.row = row                     # row index (0 .. rows-1)
        self.rect = rect                   # (xmin, ymin, xmax, ymax) in original design mm
        self.width = max(0.0, rect[2] - rect[0])
        self.height = max(0.0, rect[3] - rect[1])
        self.center = ((rect[0] + rect[2]) / 2.0, (rect[1] + rect[3]) / 2.0)
        self.label = label or f"Part {self.part_number}"
        self.polygons: List[List[Tuple[float, float]]] = []          # Clipped paths in design coordinates
        self.centered_polygons: List[List[Tuple[float, float]]] = [] # Paths shifted to galvo lens center
        self._galvo_queue: Optional[List[Dict[str, Any]]] = []       # Execution queue for galvo controller
        self._manager = manager

    @property
    def galvo_queue(self) -> List[Dict[str, Any]]:
        if self._galvo_queue is None and self._manager is not None:
            self._manager._generate_single_tile_queue(self)
        return self._galvo_queue if self._galvo_queue is not None else []

    @property
    def is_completed(self) -> bool:
        if self._manager is not None:
            return self._manager.is_part_completed(self.index)
        return False

    @galvo_queue.setter
    def galvo_queue(self, val: Optional[List[Dict[str, Any]]]):
        self._galvo_queue = val


class SplitPrintingManager:
    """
    High-level manager for split printing across up to 64 tiles.
    """
    MAX_PARTS = 64
    MAX_PART_SIZE = 70.0  # Max physical size (mm) for any split tile in X and Y

    BASE_PRESETS = [
        ("2 Splits (2×1 Left / Right)", 2, 1),
        ("2 Splits (1×2 Top / Bottom)", 1, 2),
        ("3 Splits (3×1 Columns)", 3, 1),
        ("3 Splits (1×3 Rows)", 1, 3),
        ("4 Splits (2×2 Grid)", 2, 2),
        ("4 Splits (4×1 Columns)", 4, 1),
        ("4 Splits (1×4 Rows)", 1, 4),
        ("6 Splits (3×2 Grid)", 3, 2),
        ("6 Splits (2×3 Grid)", 2, 3),
        ("8 Splits (4×2 Grid)", 4, 2),
        ("8 Splits (2×4 Grid)", 2, 4),
        ("8 Splits (8×1 Columns)", 8, 1),
        ("8 Splits (1×8 Rows)", 1, 8),
        ("9 Splits (3×3 Grid)", 3, 3),
        ("12 Splits (4×3 Grid)", 4, 3),
        ("12 Splits (3×4 Grid)", 3, 4),
        ("16 Splits (4×4 Grid)", 4, 4),
        ("20 Splits (5×4 Grid)", 5, 4),
        ("20 Splits (4×5 Grid)", 4, 5),
        ("25 Splits (5×5 Grid)", 5, 5),
        ("36 Splits (6×6 Grid)", 6, 6),
    ]
    PRESETS = list(BASE_PRESETS)

    def __init__(self):
        self.enabled: bool = False
        self.num_cols: int = 2
        self.num_rows: int = 1
        self.active_part_idx: int = 0
        self.auto_pause_between_parts: bool = True
        self.auto_center_on_lens: bool = True
        
        self.raw_polygons: List[List[Tuple[float, float]]] = []
        self.bounds: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self.design_width: float = 0.0
        self.design_height: float = 0.0
        self.lens_size: float = 70.0

        self.tiles: List[SplitTile] = []
        self.completed_parts: set = set()
        
        # Sequential print execution state
        self.is_sequential_printing: bool = False

    def mark_part_completed(self, index: int):
        """Marks a tile index as completed/printed."""
        self.completed_parts.add(int(index))

    def is_part_completed(self, index: int) -> bool:
        """Returns True if the tile index has been printed."""
        return int(index) in self.completed_parts

    def clear_completed(self):
        """Clears all completed marks."""
        self.completed_parts.clear()

    @property
    def total_parts(self) -> int:
        return len(self.tiles) if self.tiles else (self.num_cols * self.num_rows)

    @classmethod
    def get_valid_presets(cls, width: float, height: float, lens_size: float = 70.0) -> List[Tuple[str, int, int]]:
        """
        Returns list of (label, cols, rows) presets where each tile dimension fits within lens_size (max 70mm).
        Hides impossible grids where tile width > 70mm or tile height > 70mm.
        If width <= 0 or height <= 0 or lens_size <= 0, returns all default presets.
        """
        if width <= 0 or height <= 0:
            return list(cls.BASE_PRESETS)

        max_limit = getattr(cls, 'MAX_PART_SIZE', 70.0)
        lens_limit = min(max_limit, float(lens_size) if lens_size and float(lens_size) > 0 else max_limit)
        tol = 0.05  # 50 micron tolerance for floating point
        effective_lens = lens_limit + tol

        candidates = list(cls.BASE_PRESETS)

        # Calculate minimum cols and rows strictly needed
        min_c = max(1, math.ceil((width - tol) / lens_limit))
        min_r = max(1, math.ceil((height - tol) / lens_limit))

        # Ensure a candidate with (min_c, min_r) exists if within MAX_PARTS
        if min_c * min_r <= cls.MAX_PARTS:
            if not any(c == min_c and r == min_r for _, c, r in candidates):
                candidates.append((f"{min_c * min_r} Splits ({min_c}×{min_r} Grid)", min_c, min_r))

        valid = []
        for label, pc, pr in candidates:
            # Check if each tile physically fits within the lens area
            tile_w = width / pc
            tile_h = height / pr
            if tile_w <= effective_lens and tile_h <= effective_lens:
                valid.append((label, pc, pr))

        # If for some reason none of the candidate presets fit (e.g. extreme aspect ratio)
        if not valid and (min_c * min_r <= cls.MAX_PARTS):
            valid.append((f"{min_c * min_r} Splits ({min_c}×{min_r} Grid)", min_c, min_r))

        # Deduplicate while preserving order, then sort by total parts ascending, then cols ascending
        unique_valid = []
        seen_grids = set()
        for label, pc, pr in valid:
            grid_key = (pc, pr)
            if grid_key not in seen_grids:
                seen_grids.add(grid_key)
                unique_valid.append((label, pc, pr))

        unique_valid.sort(key=lambda item: (item[1] * item[2], item[1], item[2]))
        return unique_valid

    def set_split_grid(self, cols: int, rows: int):
        """Set grid columns and rows ensuring total <= MAX_PARTS."""
        cols = max(1, min(self.MAX_PARTS, int(cols)))
        rows = max(1, min(self.MAX_PARTS, int(rows)))
        if cols * rows > self.MAX_PARTS:
            # Clamp so that product does not exceed MAX_PARTS
            if cols > rows:
                cols = self.MAX_PARTS // rows
            else:
                rows = self.MAX_PARTS // cols
        self.num_cols = cols
        self.num_rows = rows
        if self.raw_polygons:
            self.recompute_tiles()

    def set_raw_polygons(self, polygons: List[List[Tuple[float, float]]], lens_size: float = 70.0):
        """Stores the design polygons and recomputes tiles."""
        max_limit = getattr(self, 'MAX_PART_SIZE', 70.0)
        lens_limit = min(max_limit, float(lens_size) if lens_size and float(lens_size) > 0 else max_limit)
        if (polygons is self.raw_polygons or getattr(self, '_raw_poly_id', None) == id(polygons)) and abs(self.lens_size - lens_limit) < 1e-3 and self.tiles:
            return

        self.raw_polygons = polygons or []
        self._raw_poly_id = id(polygons)
        self.lens_size = lens_limit

        if not self.raw_polygons:
            self.bounds = (0.0, 0.0, 0.0, 0.0)
            self.design_width = 0.0
            self.design_height = 0.0
            self.tiles = []
            return

        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for poly in self.raw_polygons:
            for pt in poly:
                min_x = min(min_x, pt[0])
                max_x = max(max_x, pt[0])
                min_y = min(min_y, pt[1])
                max_y = max(max_y, pt[1])

        if min_x == float('inf'):
            self.bounds = (0.0, 0.0, 0.0, 0.0)
            self.design_width = 0.0
            self.design_height = 0.0
            self.tiles = []
            return

        self.bounds = (min_x, min_y, max_x, max_y)
        self.design_width = max_x - min_x
        self.design_height = max_y - min_y
        self.recompute_tiles()

    def suggest_splits(self, width: float, height: float, lens_size: float) -> Tuple[int, int, str]:
        """
        Suggests optimal (cols, rows, preset_label) based on design dimensions vs lens size.
        Selects the best valid preset that fits within lens_size with minimum number of splits.
        """
        if width <= 0 or height <= 0:
            return (2, 1, "2 Splits (2×1 Left / Right)")

        lens_limit = min(getattr(self, 'MAX_PART_SIZE', 70.0), float(lens_size) if lens_size and float(lens_size) > 0 else 70.0)
        valid_presets = self.get_valid_presets(width, height, lens_limit)
        if valid_presets:
            best_label, best_c, best_r = valid_presets[0]
            return (best_c, best_r, best_label)

        # Fallback if somehow no preset fits
        c = max(1, math.ceil(width / lens_limit))
        r = max(1, math.ceil(height / lens_limit))
        return (c, r, f"{c * r} Splits ({c}×{r} Grid)")

    def recompute_tiles(self):
        """
        Clips raw_polygons into tiles according to num_cols and num_rows.
        """
        self.completed_parts.clear()
        if not self.raw_polygons or self.design_width <= 0 or self.design_height <= 0:
            self.tiles = []
            return

        min_x, min_y, max_x, max_y = self.bounds
        cols = self.num_cols
        rows = self.num_rows
        tile_w = self.design_width / cols
        tile_h = self.design_height / rows

        new_tiles = []
        idx = 0
        # Rows ordered from top to bottom (y high to low) or bottom to top
        # Since physical/SVG standard often has Y-axis, let's order rows: top-to-bottom
        for r in range(rows):
            # top-to-bottom: r=0 is highest Y, r=rows-1 is lowest Y
            y_max_tile = max_y - r * tile_h
            y_min_tile = max_y - (r + 1) * tile_h
            for c in range(cols):
                x_min_tile = min_x + c * tile_w
                x_max_tile = min_x + (c + 1) * tile_w

                tile = SplitTile(
                    index=idx,
                    col=c,
                    row=r,
                    rect=(x_min_tile, y_min_tile, x_max_tile, y_max_tile),
                    label=f"Part {idx + 1}",
                    manager=self
                )

                # Clip all polygons to this tile's rectangle
                clipped_for_tile = []
                for poly in self.raw_polygons:
                    clipped = clip_polygon_to_rect(poly, x_min_tile, x_max_tile, y_min_tile, y_max_tile)
                    clipped_for_tile.extend(clipped)

                tile.polygons = clipped_for_tile

                # Center polygons onto (0, 0) for galvo placement
                cx, cy = tile.center
                centered = []
                for poly in clipped_for_tile:
                    centered_poly = [(pt[0] - cx, pt[1] - cy) for pt in poly]
                    centered.append(centered_poly)
                tile.centered_polygons = centered

                new_tiles.append(tile)
                idx += 1

        self.tiles = new_tiles
        # Keep active_part_idx valid
        if self.active_part_idx >= len(self.tiles):
            self.active_part_idx = 0

    def _generate_single_tile_queue(self, tile: SplitTile):
        """Generates the motion planner commands for a single tile on-demand."""
        if not hasattr(self, '_queue_params') or not self._queue_params:
            return
        params = self._queue_params
        galvo_config = params['galvo_config']
        start_x = params['start_x']
        start_y = params['start_y']
        mark_speed = params['mark_speed']
        jump_speed = params['jump_speed']
        is_hatch = params['is_hatch']
        hatch_configs = params['hatch_configs']
        mark_contour = params['mark_contour']

        source_polys = tile.centered_polygons if self.auto_center_on_lens else tile.polygons
        if not source_polys:
            tile.galvo_queue = []
            return

        from core.motion_planner import MotionPlanner
        planner = MotionPlanner()
        planner.clear()

        all_polys_galvo = []
        seen_polys = set()

        for poly in source_polys:
            if not poly:
                continue
            poly_galvo = []
            for pt in poly:
                gx, gy = galvo_config.apply_transform(pt[0] + start_x, pt[1] + start_y)
                poly_galvo.append((gx, gy))

            if len(poly_galvo) > 80:
                poly_key = (
                    len(poly_galvo),
                    int(round(poly_galvo[0][0])), int(round(poly_galvo[0][1])),
                    int(round(poly_galvo[-1][0])), int(round(poly_galvo[-1][1])),
                    int(round(poly_galvo[len(poly_galvo)//2][0])), int(round(poly_galvo[len(poly_galvo)//2][1]))
                )
                poly_key_rev = (
                    len(poly_galvo),
                    int(round(poly_galvo[-1][0])), int(round(poly_galvo[-1][1])),
                    int(round(poly_galvo[0][0])), int(round(poly_galvo[0][1])),
                    int(round(poly_galvo[len(poly_galvo)//2][0])), int(round(poly_galvo[len(poly_galvo)//2][1]))
                )
            else:
                poly_key = tuple((int(round(p[0])), int(round(p[1]))) for p in poly_galvo)
                poly_key_rev = tuple(reversed(poly_key))
            if poly_key not in seen_polys and poly_key_rev not in seen_polys:
                seen_polys.add(poly_key)
                all_polys_galvo.append(poly_galvo)

        # 1. Contour
        if mark_contour:
            for poly_galvo in all_polys_galvo:
                if len(poly_galvo) >= 2:
                    planner.add_jump(poly_galvo[0][0], poly_galvo[0][1], speed=jump_speed)
                    for pt in poly_galvo[1:]:
                        planner.add_mark(pt[0], pt[1], speed=mark_speed)

        # 2. Hatch
        if is_hatch and hatch_configs:
            try:
                galvo_units_per_mm = 65535.0 / galvo_config.field_size
                planner.generate_hatch(
                    all_polys_galvo,
                    hatch_configs,
                    mark_speed=mark_speed,
                    jump_speed=jump_speed,
                    galvo_units_per_mm=galvo_units_per_mm
                )
            except Exception as e:
                print(f"Error generating hatch for Tile {tile.part_number}: {e}")

        planner.commit_to_send_queue()
        tile.galvo_queue = list(planner.send_queue)

    def generate_tile_queues(self, galvo_config, start_x: float = 0.0, start_y: float = 0.0,
                             mark_speed: int = 1000, jump_speed: int = 2000,
                             is_hatch: bool = False, hatch_configs: Optional[List[Dict[str, Any]]] = None,
                             mark_contour: bool = True):
        """
        Stores generation parameters and builds the active tile queue immediately.
        Remaining tiles are computed on-demand when selected to keep UI ultra responsive.
        """
        self._queue_params = {
            'galvo_config': galvo_config,
            'start_x': start_x,
            'start_y': start_y,
            'mark_speed': mark_speed,
            'jump_speed': jump_speed,
            'is_hatch': is_hatch,
            'hatch_configs': hatch_configs,
            'mark_contour': mark_contour
        }

        # Clear existing cached queues for all tiles
        for tile in self.tiles:
            tile.galvo_queue = None

        # Generate active tile queue right now
        active_tile = self.get_active_tile()
        if active_tile:
            self._generate_single_tile_queue(active_tile)

    def get_active_tile(self) -> Optional[SplitTile]:
        if not self.tiles:
            return None
        idx = max(0, min(len(self.tiles) - 1, self.active_part_idx))
        tile = self.tiles[idx]
        if tile.galvo_queue is None and hasattr(self, '_queue_params') and self._queue_params:
            self._generate_single_tile_queue(tile)
        return tile

    def set_active_part(self, index: int) -> bool:
        if not self.tiles:
            return False
        if 0 <= index < len(self.tiles):
            self.active_part_idx = index
            tile = self.tiles[index]
            if tile.galvo_queue is None and hasattr(self, '_queue_params') and self._queue_params:
                self._generate_single_tile_queue(tile)
            return True
        return False

    def next_part(self) -> bool:
        if not self.tiles:
            return False
        if self.active_part_idx < len(self.tiles) - 1:
            return self.set_active_part(self.active_part_idx + 1)
        return False

    def prev_part(self) -> bool:
        if not self.tiles:
            return False
        if self.active_part_idx > 0:
            return self.set_active_part(self.active_part_idx - 1)
        return False
