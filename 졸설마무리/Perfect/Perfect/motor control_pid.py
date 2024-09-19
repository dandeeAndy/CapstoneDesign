import os
import solenoid

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# DYNAMIXEL Model & Protocol Version
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDs = [1, 2, 3]  # Dynamixel IDs
BAUDRATE = 57600
DEVICENAME = 'COM3'  # Port Name
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# Control Table Addresses
ADDR_OPERATING_MODE = 11
EXTENDED_POSITION_CONTROL_MODE = 4
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132

ADDR_GOAL_VELOCITY = 104
ADDR_GOAL_PROFILE_ACCELERATION = 108
ADDR_GOAL_PROFILE_VELOCITY = 112 

# Data Length
LEN_GOAL_POSITION = 4  # Length of the Goal Position data

# Middle position for zero degrees, specific to each model
MID_POSITION = 2048  # Placeholder value, replace with actual middle position from the motor documentation
ANGLE_PER_UNIT = 11.3777  # Convert angle to Dynamixel unit

# Initialize PortHandler & PacketHandler instances
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# ---------------------------------------------------------------------------------------------------------------
# Open Port & Set Port Baud Rate
if portHandler.openPort() and portHandler.setBaudRate(BAUDRATE):
    print("Connected")
else:
    print("Failed to open the port or set the baud rate")

# ---------------------------------------------------------------------------------------------------------------
# Set operating mode and enable torque for each Dynamixel motor
for dxl_id in DXL_IDs:
    # Set operating mode
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_OPERATING_MODE, EXTENDED_POSITION_CONTROL_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to change operating mode for Dynamixel#{dxl_id}")
        exit()

    # Enable torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for Dynamixel#{dxl_id}")
        exit()
        
# ---------------------------------------------------------------------------------------------------------------
# Set goal velocity
    goal_velocity = 200  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_VELOCITY, goal_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
    
# ---------------------------------------------------------------------------------------------------------------    
# Set goal profile acceleration
    goal_profile_acceleration = 2000  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_ACCELERATION, goal_profile_acceleration)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile acceleration for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile acceleration error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

# ---------------------------------------------------------------------------------------------------------------
# Set goal profile velocity
    goal_profile_velocity = 650  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_VELOCITY, goal_profile_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

# ---------------------------------------------------------------------------------------------------------------
# PID parameters
Kp = 0.1
Ki = 0.01
Kd = 0.01

# Initialize PID variables
previous_error = [0] * len(DXL_IDs)
integral = [0] * len(DXL_IDs)

def pid_move(goal_angles):
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]
    for dxl_id, goal_position, i in zip(DXL_IDs, goal_positions, range(len(DXL_IDs))):
        while True:
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                continue
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))
                continue

            error = goal_position - dxl_present_position

            Pout = Kp * error
            integral[i] += error
            Iout = Ki * integral[i]
            derivative = error - previous_error[i]
            Dout = Kd * derivative

            output = goal_position + Pout + Iout + Dout  # Adjust output based on PID
            output = max(0, min(4095, output))  # Clamp output to max/min position values

            dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, int(output))
            if dxl_comm_result != COMM_SUCCESS:
                print(f"Failed to set goal position for Dynamixel#{dxl_id}")
                exit()

            previous_error[i] = error

            print(f"Dynamixel#{dxl_id} Present Position: {dxl_present_position} | Goal Position: {goal_position} | Error: {error}")

            if abs(error) < 20:
                break

            time.sleep(0.1)

# ---------------------------------------------------------------
def move_with_pump(angles_list):
    time.sleep(2)
    solenoid.airpump_on()
    time.sleep(1)
    for angles in angles_list:
        pid_move(angles)
        time.sleep(1)
    solenoid.airpump_off()
    
# ---------------------------------------------------------------
def move_to_position(angles_list):
    for angles in angles_list:
        pid_move(angles)
        time.sleep(1)

# ---------------------------------------------------------------
#+가 밑으로, -가 위로
Home = [[0,0,0],[20,15,-50],[40,-20,-8]]
  
A1 = [[20,25,-50], [20, -49, 25], [10, -44, -8],[0,0,0]]
A2 = [[-20,-25,50], [-20, 49, -25], [-40, 44, 8],[0,0,0]]
A3 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]
A4 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
A5 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
A6 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]
A7 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
A8 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]

B1 = [[20,25,-50], [20, -49, 25], [40, -44, -8],[0,0,0]]
B2 = [[-20,-25,50], [-20, 49, -25], [-40, 44, 8],[0,0,0]]
B3 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]
B4 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
B5 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
B6 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]
B7 = [[-10, 10, -20], [23, -40, 5], [23, 5, -40],[-33, 32, -17], [0, 0, 0]]
B8 = [[10, -10, 20], [-23, 40, -5], [-23, -5, 40],[33, -32, 17], [0, 0, 0]]

position_safe = [-16,6,26]
position = [0,20,38]

# ---------------------------------------------------------------
#move_with_pump(Home)
move_to_position(A1)
#move(Home)
#time.sleep(1)
#move(position_safe)
#time.sleep(1)
#move(position)
