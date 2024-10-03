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
    goal_profile_acceleration = 1500  # 기본값
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_ACCELERATION, goal_profile_acceleration)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile acceleration for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile acceleration error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

# ---------------------------------------------------------------------------------------------------------------
# Set goal profile velocity
    goal_profile_velocity = 550  # 기본값
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
    for dxl_id, goal_position in zip(DXL_IDs, goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()
            
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
def pick(angles_list):
    time.sleep(1.5)
    solenoid.airpump_on()
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)

        
# ---------------------------------------------------------------
def place(angles_list):
    for angles in angles_list:
        move(angles)
        time.sleep(1)

# ---------------------------------------------------------------
def safe_place(angles_list):
    solenoid.airpump_off()
    #time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)     
        
# ---------------------------------------------------------------------------------------------------------------
# Pick_Angle
pick_position = {

    # PALLET V
    'V1' : [[11,-17,-42], [23,-1,-20],[11,-17,-42]],
    'V2' : [[13,-37,-20], [22,-20,-4],[13,-37,-20]],
    'V3' : [[31,-39,-20], [41,-18,-1], [32,-45,-25]],
    'V4' : [[32,-17,-40], [42,0,-18],[32,-17,-40]],
    'V5' : [[11,-17,-42], [30,9,-9],[11,-17,-42]],
    'V6' : [[13,-37,-20], [30,-8,6],[13,-37,-20]],
    'V7' : [[31,-39,-20], [49,-7,10],[31,-39,-20]],
    'V8' : [[32,-17,-40], [48,10,-8],[32,-17,-40]],
    'V9' : [[11,-17,-42], [38,19,2],[11,-17,-42]],
    'V10' :[[13,-37,-20], [38,3,16],[13,-37,-20]],
    'V11' :[[31,-39,-20], [56,4,19],[31,-39,-20]],
    'V12' :[[32,-17,-40], [55,20,3],[32,-17,-40]],
}   
 
# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
place_position = {
    
    # PALLET A   
    'A1' : [[-40,-6,48], [4,27,69]],
    'A2' : [[-47,3,26],  [-5,32,50]],
    'A3' : [[-30,-23,37],[8,15,59]],
    'A4' : [[-41,-10,15],[-2,21,40]],
    'A5' : [[-40,-6,48], [-8,16,61]],
    'A6' : [[-47,3,26],  [-17,22,41]],
    'A7' : [[-30,-23,37],[-6,3,51]],
    'A8' : [[-41,-10,15],[-14,11,32]],
    
    # PALLET B  
    'B1' : [[-35,48,-4], [2,66,28]],
    'B2' : [[-46,24,4],  [-5,49,35]],
    'B3' : [[-36,35,-23],[6,58,17]],
    'B4' : [[-43,12,-9], [-2,38,22]],
    'B5' : [[-35,48,-4], [-9,60,18]],
    'B6' : [[-46,24,4],  [-16,41,26]],
    'B7' : [[-36,35,-23],[-6,51,6]],
    'B8' : [[-43,12,-9], [-14,31,13]]
}

# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
safe_position = {
    
    # PALLET A   
    'AS1' : [[-40,-6,48],[-16,-16,-16]],
    'AS2' : [[-47,3,26],[-16,-16,-16]],
    'AS3' : [[-30,-23,37],[-16,-16,-16]],
    'AS4' : [[-41,-10,15],[-16,-16,-16]],
    'AS5' : [[-40,-6,48],[-16,-16,-16]],
    'AS6' : [[-47,3,26],[-16,-16,-16]],
    'AS7' : [[-30,-23,37],[-16,-16,-16]],
    'AS8' : [[-41,-10,15],[-16,-16,-16]],
    
    # PALLET B  
    'BS1' : [[-35,48,-4],[-16,-16,-16]],
    'BS2' : [[-46,24,4],[-16,-16,-16]],
    'BS3' : [[-36,35,-23],[-16,-16,-16]],
    'BS4' : [[-43,12,-9],[-16,-16,-16]],
    'BS5' : [[-35,48,-4],[-16,-16,-16]],
    'BS6' : [[-46,24,4],[-16,-16,-16]],
    'BS7' : [[-36,35,-23],[-16,-16,-16]],
    'BS8' : [[-43,12,-9],[-16,-16,-16]],
}          

# ---------------------------------------------------------------------------------------------------------------

motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_Y = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_N = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 