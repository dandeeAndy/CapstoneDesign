import os
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# DYNAMIXEL Model & Protocol Version
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDs = [1, 2, 3]  # Dynamixel IDs
BAUDRATE = 57600
DEVICENAME = 'COM5'  # Port Name
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# Control Table Addresses
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116  # Goal Position address in the RAM area

# Data Length
LEN_GOAL_POSITION = 4  # Length of the Goal Position data

# Position to Angle Conversion Factor
ANGLE_FACTOR = 11.3777

# Initialize PortHandler & PacketHandler instances
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open Port & Set Port Baud Rate
# ---------------------------------------------------------------
if portHandler.openPort() and portHandler.setBaudRate(BAUDRATE):
    print("Success")
else:
    print("Failed to open the port or set the baud rate")

# Enable Dynamixel Torque
for dxl_id in DXL_IDs:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("Failed to enable torque for Dynamixel#%d" % dxl_id)
        exit()
        
# Set Goal Position
# ---------------------------------------------------------------
def set_goal_position(goal_angles):
    """
    Converts the given goal angles to positions and sets the goal position for each Dynamixel motor.

    :param goal_angles: A list of goal angles for each motor.
    """
    goal_positions = [int(angle * ANGLE_FACTOR) for angle in goal_angles]
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        # Write goal position
        dxl_addparam_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_addparam_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()
            
# Angle
# ---------------------------------------------------------------
# PALLET A            
A1 = [0, 0, 0] 
A2 = [100,100,100] 
A3 = [200,100,250]
A4 = [30,40,50]
A5 = [30,40,50]
A6 = [30,40,50]
A7 = [30,40,50]
A8 = [30,40,50]

# PALLET B     
B1 = [30,40,50]
B2 = [30,40,50]
B3 = [30,40,50]
B4 = [30,40,50]
B5 = [30,40,50]
B6 = [30,40,50]
B7 = [30,40,50]
B8 = [30,40,50]
