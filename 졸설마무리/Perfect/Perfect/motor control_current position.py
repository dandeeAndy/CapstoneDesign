import os
import solenoid
import time
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
ANGLE_PER_UNIT = 11 # Convert angle to Dynamixel unit

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
def move(goal_angles):
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]
    
    # 모든 모터의 목표 위치를 설정
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()

    # 모든 모터가 목표 위치로 이동할 시간을 줌
    time.sleep(1)

    # 각 모터의 현재 각도 출력
    results = []
    for dxl_id in DXL_IDs:
        angle = read_position(dxl_id)
        if angle is not None:
            goal_angle = (goal_positions[DXL_IDs.index(dxl_id)] - MID_POSITION) / ANGLE_PER_UNIT
            results.append(f"Dynamixel#{dxl_id} | Current Angle: {angle:.2f} degrees | Goal Angle: {goal_angle:.2f} degrees | Error: {goal_angle - angle:.2f} degrees")
    
    # 3개씩 묶어서 출력
    for i in range(0, len(results), 3):
        print("\n".join(results[i:i+3]))
        print()  # 빈 줄 추가


# ---------------------------------------------------------------
def move_with_pump(angles_list):
    time.sleep(2)
    solenoid.airpump_on()
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)
    solenoid.airpump_off()
    
# ---------------------------------------------------------------
def move_to_position(angles_list):
    for angles in angles_list:
        move(angles)
        time.sleep(1)

# ---------------------------------------------------------------
def read_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to get present position for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        return None
    elif dxl_error != 0:
        print(f"Present position error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        return None
    else:
        angle = (dxl_present_position - MID_POSITION) / ANGLE_PER_UNIT
        return angle

def print_current_positions():
    for dxl_id in DXL_IDs:
        angle = read_position(dxl_id)
        if angle is not None:
            print(f"Dynamixel#{dxl_id} Current Angle: {angle:.2f} degrees")

# ---------------------------------------------------------------
def move_default(goal_angles):
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]
    
    # 모든 모터의 목표 위치를 설정
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()
# ---------------------------------------------------------------
        
#+가 밑으로, -가 위로
Home = [-16,-16,-16]
  
A1 = [[20,25,10], [20, 29, 25], [30, -30, -10],[0,0,0]]
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

position_safe = [11,-17,-42]
position = [5,5,5]

C = [[2,66,28],
[-5,49,35],
[6,58,17],
[-2,38,22],
[-9,60,18],
[-16,41,26],
[-6,51,6],
[-14,31,13]]
# ---------------------------------------------------------------
#move_with_pump(A1)

# move_to_position(C)


# move(position_safe)
# time.sleep(1)
# move(position)
# time.sleep(1)
# print_current_positions()

# move(Home)
#time.sleep(1)
#move(position)
#time.sleep(1)
#move(position)


move(Home)
move_default(position)