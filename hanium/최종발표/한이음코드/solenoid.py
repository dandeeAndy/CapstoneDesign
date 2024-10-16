import serial
import time

# Serial 통신 설정
try:
    ser = serial.Serial('COM8', 9600, timeout=1)
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    exit(1)

def control_relay(state):
    try:
        if state:
            ser.write(b'1')  # Turn relay ON
        else:   
            ser.write(b'0')  # Turn relay OFF
        print(f"Relay {'ON' if state else 'OFF'} command sent")
    except serial.SerialException as e:
        print(f"Failed to write to serial port: {e}")

def airpump_off():
    control_relay(True)

def airpump_on():
    control_relay(False)

def main():
    while True:
        
            airpump_on()
            # print("Airpump ON")
        #     time.sleep(1)
        #     print("Airpump OFF")
        #     airpump_on()
        #     time.sleep(1)
        #     print("Airpump ON")
        #     airpump_off()
        #     time.sleep(1)
        #     print("Airpump OFF")
        # except serial.SerialException as e:
        #     print(f"Serial communication error: {e}")
        # except KeyboardInterrupt:
        #     print("\nProgram terminated by user")
        #     break
        # except Exception as e:
        #     print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        main()
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed")