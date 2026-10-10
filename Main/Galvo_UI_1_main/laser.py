
# laser1 : GA12692
# laser2 : GA12693

laser1_dict = {0 : 0,
               1300 : 1,
               1810 : 5,
               2450 : 10,
               3100 : 15,
               3760 : 20,
               4440 : 25,
               5090 : 30,
               5800 : 35,
               6510 : 40,
               7220 : 45,
               8150 : 51.3}

laser2_dict = {0 : 0,
               1290 : 1,
               1800 : 5,
               2440 : 10,
               3080 : 15,
               3740 : 20,
               4410 : 25,
               5080 : 30,
               5790 : 35,
               6450 : 40,
               7180 : 45,
               8100 : 51.3}

class LaserConfig():
    def __init__(self):

        self.laser_dict = {"laser1" : laser1_dict,
                           "laser2" : laser2_dict}
        
    def getPowerLimits(self, laser):
        if laser in self.laser_dict:
            laser_dict = self.laser_dict.get(laser)
            power_list = sorted(laser_dict.values())
            power_min = min(power_list)
            power_max = max(power_list)

            return power_min, power_max

    def getCurrent(self, power, laser):
        if laser in self.laser_dict:
            laser_dict = self.laser_dict.get(laser)

            power_current_dict = {value: key for key, value in laser_dict.items()}
            power_list = sorted(power_current_dict.keys())

            if power <= min(power_list):
                return power_current_dict[min(power_list)]
            
            if power >= max(power_list):
                return power_current_dict[max(power_list)]
            
            for i in range(len(power_list) - 1):
                if power_list[i] <= power <= power_list[i+1]:
                    power1, power2 = power_list[i], power_list[i+1]
                    current1, current2 = power_current_dict[power1], power_current_dict[power2]
                    
                    # Calculate slope (m) and y-intercept (b) for the line segment
                    # y = mx + b where y is current and x is power
                    slope = (current2 - current1) / (power2 - power1)
                    intercept = current1 - slope * power1
                    
                    # Apply the slope-intercept formula to find current
                    current = slope * power + intercept
                    
                    return current
            
            # This should not be reached if the input is within range
            return None


if __name__ == "__main__":
    laserConf = LaserConfig()

    laser = "laser1"
    power = 11

    pmin, pmax = laserConf.getPowerLimits(laser)
    print(f"min : {pmin}, max : {pmax}")

    current = laserConf.getCurrent(power, laser)
    print(f"laser : {laser}, power : {power}, current : {int(current)}")