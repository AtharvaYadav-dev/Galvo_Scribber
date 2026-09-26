import re
with open('machine/galvo_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "self.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)\n",
    "self.connection.set_analog_do_bit(255.0, 0.0, 50.0, 2)\n" + " " * 16 + "if hasattr(self.connection, 'send_buffer'):\n" + " " * 20 + "self.connection.send_buffer()\n"
)

with open('machine/galvo_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
