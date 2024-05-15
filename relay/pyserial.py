import serial
import time

# Establish a serial connection (COM port and baud rate must match Arduino's setup)
ser = serial.Serial('COM3', 9600)  # Update 'COM3' to your Arduino's COM port

def control_relay(state):
    if state:
        ser.write(b'1')  # Turn relay ON
    else:
        ser.write(b'0')  # Turn relay OFF

# Example usage
control_relay(True)  # Turn the relay ON
time.sleep(2)        # Wait for 2 seconds
control_relay(False) # Turn the relay OFF

# Close the serial connection
ser.close()