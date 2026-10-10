import time
from core.connection.hardware import HardwareConnection

print("Initializing Galvo Hardware...")
conn = HardwareConnection()
res, cards = conn.initialize()

if not conn.is_initialized:
    print("Failed to initialize hardware. Is the board powered on and connected?")
    exit(1)

print("Hardware connected successfully.")
print("\n=== PWM BIT FINDER ===")
print("Please connect your Multimeter (DC Voltage) or Oscilloscope to J2 Pin 33.")
print("We will test bits 0 through 7 one by one.")
print("When your multimeter jumps to ~2.5V (or you see a 50kHz square wave on CRO), note the bit number!\n")

try:
    for bit in range(8):
        print(f"--> NOW TESTING BIT {bit} ... (Testing for 5 seconds)")
        
        # Set all bits to 0 first to clear the slate
        for clear_bit in range(8):
            conn.set_analog_do_bit(100.0, 0.0, 50.0, clear_bit)
            
        time.sleep(0.1)
        
        # Output a 50% duty cycle, 50kHz PWM on the current test bit
        conn.set_analog_do_bit(100.0, 50.0, 50.0, bit)
        conn.send_buffer()
        
        # Hold it for 5 seconds so you can read the multimeter
        time.sleep(5)

    print("\nTest Complete! Turning off all PWM signals.")
    for bit in range(8):
        conn.set_analog_do_bit(100.0, 0.0, 50.0, bit)
    conn.send_buffer()

finally:
    conn.close()
