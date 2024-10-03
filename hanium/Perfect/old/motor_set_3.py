import os
import time
from dynamixel_sdk import *

# Setting
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0
DXL_IDs = [1, 2, 3]
BAUDRATE = 57600
DEVICENAME = 'COM5'
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# Control Table Addresses
ADDR_OPERATING_MODE = 11
EXTENDED_POSITION_CONTROL_MODE = 4
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116

# Data Length
LEN_GOAL_POSITION = 4

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
def move_to_position(goal_angles):
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()
                    
# ---------------------------------------------------------------------------------------------------------------
# Angle
place_position = {
    
    # PALLET A   
    'A1' : [0, 0, 0],
    'A2' : [10,10,10],
    'A3' : [20,20,20],
    'A4' : [30,30,30],
    'A5' : [40,40,40],
    'A6' : [50,50,50],
    'A7' : [60,60,60],
    'A8' : [70,70,70],
    
    # PALLET B  
    'B1' : [0, 0, 0],
    'B2' : [10,10,10],
    'B3' : [20,20,20],
    'B4' : [30,30,30],
    'B5' : [40,40,40],
    'B6' : [50,50,50],
    'B7' : [60,60,60],
    'B8' : [70,70,70],
}
          
# ---------------------------------------------------------------------------------------------------------------
motor_positions_L = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_F = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

motor_positions_Y = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_N = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 