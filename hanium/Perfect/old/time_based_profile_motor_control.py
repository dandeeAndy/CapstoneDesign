import os
from dynamixel_sdk import *  # Uses Dynamixel SDK library
import time

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
ADDR_DRIVE_MODE = 10
ADDR_OPERATING_MODE = 11
EXTENDED_POSITION_CONTROL_MODE = 4
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_GOAL_VELOCITY = 104
ADDR_GOAL_PROFILE_ACCELERATION = 108
ADDR_GOAL_PROFILE_VELOCITY = 112 

# Drive Mode Setting (Time-based Profile)
TIME_BASED_PROFILE = 0x04 

# Data Length
LEN_GOAL_POSITION = 4  # Length of the Goal Position data

# Middle position for zero degrees, specific to each model
MID_POSITION = 2048  # Placeholder value, replace with actual middle position from the motor documentation
ANGLE_PER_UNIT = 11.3777  # Convert angle to Dynamixel unit

# Initialize PortHandler & PacketHandler instances
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open Port & Set Port Baud Rate
if portHandler.openPort() and portHandler.setBaudRate(BAUDRATE):
    print("Connected")
else:
    print("Failed to open the port or set the baud rate")
    exit()

# Set drive mode, operating mode, and enable torque for each Dynamixel motor
for dxl_id in DXL_IDs:
    # Disable torque to change settings
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to disable torque for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Torque disable error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

    # Set drive mode to Time-based Profile (Bit 2 = 1)
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_DRIVE_MODE, TIME_BASED_PROFILE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set drive mode for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Drive mode error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

    # Set operating mode
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_OPERATING_MODE, EXTENDED_POSITION_CONTROL_MODE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to change operating mode for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Operating mode error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
    
    # Set goal velocity
    goal_velocity = 20  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_VELOCITY, goal_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
    
    # Set goal profile acceleration
    goal_profile_acceleration = 20  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_ACCELERATION, goal_profile_acceleration)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile acceleration for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile acceleration error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
    
    # Set goal profile velocity
    goal_profile_velocity = 20  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_VELOCITY, goal_profile_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

    # Enable torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Torque enable error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

def move_to_position(goal_angles):
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
            exit()
        elif dxl_error != 0:
            print(f"Goal position error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
            exit()

def move_with_pump(angles_list):
    solenoid.airpump_on()
    time.sleep(1)
    for angles in angles_list:
        move_to_position(angles)
        time.sleep(1)
    solenoid.airpump_off()

A1 = [0, 0, 0]
A2 = [ -20,-20,-20]
#A2 = [[-20, -25, 40], [-20, 45, -25], [-40, 44, 8], [0, 0, 0]]
A3 = [[10, -10, 20], [20, -20, 30], [30, -30, 40], [0, 0, 0]]
A4 = [[15, 10, -10], [25, 20, -20], [35, 30, -30], [0, 0, 0]]

move_to_position(A1)
# move_with_pump(A2)

#for angles in A2:
#    move_to_position(angles)
#    time.sleep(1)
