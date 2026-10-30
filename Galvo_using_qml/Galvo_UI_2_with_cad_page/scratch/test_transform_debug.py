import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from core.coordinate_mapper import CoordinateConfig

def test_transform():
    cfg = CoordinateConfig()
    cfg.field_size = 70.0
    cfg.calib_scale = 533.89
    cfg.galvo_1_is_x = False

    # Point at (10, 0) - along +X
    gx, gy = cfg.apply_transform(10.0, 0.0)
    print(f"(10, 0) -> gx={gx}, gy={gy}")

    # Point at (0, 10) - along +Y
    gx2, gy2 = cfg.apply_transform(0.0, 10.0)
    print(f"(0, 10) -> gx={gx2}, gy={gy2}")

    # Now let's see what execute_queue sends to galvo:
    # cmd['x'] = gx, cmd['y'] = gy
    # raw_x = cmd['y']
    # raw_y = cmd['x']
    print(f"Hardware input for (10, 0): raw_x (move_xy 1st arg) = {gy}, raw_y (move_xy 2nd arg) = {gx}")
    print(f"Hardware input for (0, 10): raw_x (move_xy 1st arg) = {gy2}, raw_y (move_xy 2nd arg) = {gx2}")

if __name__ == "__main__":
    test_transform()
