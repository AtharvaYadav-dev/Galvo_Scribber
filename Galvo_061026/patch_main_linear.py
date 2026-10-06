import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern1 = r"if hasattr\(self\.galvo_controller\.connection, 'map_laser_power'\):\s+inverted_power = self\.galvo_controller\.connection\.map_laser_power\((.*?)\)\s+else:\s+inverted_power =  100\.0 - \1\s+# bit=2.*?\s+# DO NOT.*?\s+self\.galvo_controller\.connection\.set_analog_do_bit\((.*?), inverted_power, 50\.0, 2\)"

replacement1 = r"""if float(\1) <= 0:
                        if hasattr(self.galvo_controller.connection, 'laser_off'):
                            self.galvo_controller.connection.laser_off()
                        self.galvo_controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                    else:
                        mapped_power = (float(\1) / 100.0) * 255.0
                        self.galvo_controller.connection.set_analog_do_bit(255.0, mapped_power, 50.0, 2)"""

content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

pattern2 = r"if hasattr\(self\.galvo_controller\.connection, 'map_laser_power'\):\s+inverted_power = self\.galvo_controller\.connection\.map_laser_power\((.*?)\)\s+else:\s+inverted_power =  100\.0 - \1\s+self\.galvo_controller\.connection\.set_analog_do_bit\((.*?), inverted_power, 50\.0, 2\)"

replacement2 = r"""if float(\1) <= 0:
                            if hasattr(self.galvo_controller.connection, 'laser_off'):
                                self.galvo_controller.connection.laser_off()
                            self.galvo_controller.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)
                        else:
                            mapped_power = (float(\1) / 100.0) * 255.0
                            self.galvo_controller.connection.set_analog_do_bit(255.0, mapped_power, 50.0, 2)"""

content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
