import time
from core.connection.hardware import HardwareConnection

print("Initializing Galvo Hardware...")
conn = HardwareConnection()
res, cards = conn.initialize()

if not conn.is_initialized:
    print("Failed to initialize hardware.")
    exit(1)

print("\n=== FIND THE REAL PWM PIN ===")
print("I am now generating a perfect 50kHz square wave on Bit 3 (the true hardware PWM channel).")
print("Please take your Multimeter (DC Voltage) or CRO.")
print("Probe the pins on your J2 connector one by one.")
print("When you find the pin that shows ~2.5V (or a 50kHz square wave), THAT is your true Frequency pin!")
print("Press Ctrl+C to stop.")

try:
    while True:
        conn.set_analog_do_bit(100.0, 50.0, 50.0, 3)
        conn.send_buffer()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    conn.set_analog_do_bit(100.0, 0.0, 50.0, 3)
    conn.send_buffer()
    conn.close()
