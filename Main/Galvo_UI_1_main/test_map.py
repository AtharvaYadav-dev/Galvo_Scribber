import numpy as np

def map_laser_power(requested_power_pct):
    laser_power_points = [0, 10, 35, 65, 85, 92, 100]
    required_current = [0, 14.28, 50, 75, 87.5, 93.75, 100]
    mapped = np.interp(requested_power_pct, laser_power_points, required_current)
    return 100.0 - float(mapped)

def clamp_laser_freq(requested_freq):
    return max(30.0, min(60.0, float(requested_freq)))

print(map_laser_power(35))
print(map_laser_power(65))
print(map_laser_power(85))
print(clamp_laser_freq(20))
