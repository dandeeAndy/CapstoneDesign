import serial
import time

# Serial 통신을 설정하고 예외 처리를 추가합니다.
ser = serial.Serial('COM6', 9600)

def control_relay(state):
    if state:
        ser.write(b'1')  # Turn relay ON
    else:
        ser.write(b'0')  # Turn relay OFF

def airpump_on():
    control_relay(True)

def airpump_off():
    control_relay(False)
