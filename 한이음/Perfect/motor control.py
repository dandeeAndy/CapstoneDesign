import os
#import solenoid

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# DYNAMIXEL Model & Protocol Version
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDs = [1, 2, 3, 4]  # Dynamixel IDs
BAUDRATE = 57600
DEVICENAME = 'COM17'  # Port Namex
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
# Set operating mode and enable torque for each Dynamixel motor3
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

# ---------------------------------------------------------------------------------------------------------------
def move_plus(goal_angles, rotation):
    if rotation < -180 or rotation > 180:
        print(f"Rotation value {rotation} out of range (-180 to 180)")
        return
    goal_positions = [int(MID_POSITION + angle * ANGLE_PER_UNIT) for angle in goal_angles]

    goal_position_4 = int(MID_POSITION + rotation * ANGLE_PER_UNIT)

    for dxl_id, goal_position in zip(DXL_IDs[:-1], goal_positions):
        if goal_position < 0 or goal_position > 4095:  
            print(f"Goal position {goal_position} out of range for Dynamixel#{dxl_id}")
            continue
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()

    if goal_position_4 < 0 or goal_position_4 > 4095:
        print(f"Goal position {goal_position_4} out of range for Dynamixel#4")
    else:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, 4, ADDR_GOAL_POSITION, goal_position_4)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#4")
            exit()


# ---------------------------------------------------------------
# def move_with_pump(angles_list):
#    time.sleep(2)
#    solenoid.airpump_on()
#    time.sleep(1)
#    for angles in angles_list:
#        move(angles)
#        time.sleep(1)
#    solenoid.airpump_off()
   

def move_to_position(angles_list):
   for angles in angles_list:
       move(angles)
       time.sleep(1)
    
    
# ---------------------------------------------------------------
def pick(angles_list):
   time.sleep(2)
#    solenoid.airpump_on()
   for angles in angles_list:
       move(angles)
       time.sleep(1)
        
# ---------------------------------------------------------------
def place(angles_list):
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)
        
# ---------------------------------------------------------------
Home = [-16,-16,-16,30]
V1 = [[11,-17,-42], [23,0,-20],[11,-17,-42],[0,0,400]]
V2 = [[32,-17,-40], [41,1,-19],[32,-17,-40],[0,0,400]]
V3 = [[31,-39,-20], [41,-18,-2], [32,-45,-25],[-57,-5,20]]
V4 = [[13,-37,-20], [22,-19,-4],[13,-37,-20],[0,0,400]]
V5 = [[11,-17,-42], [30,9,-9],[11,-17,-42],[0,0,400]]
V6 = [[32,-17,-40], [47,11,-7],[32,-17,-40],[0,0,400]]
V7 = [[31,-39,-20], [48,-6,8],[31,-39,-20],[0,0,400]]
V8 = [[13,-37,-20], [30,-8,6],[13,-37,-20],[0,0,400]]
V9 = [[11,-17,-42], [38,19,2],[11,-17,-42],[0,0,400]]
V10 =[[32,-17,-40], [55,20,3],[32,-17,-40],[0,0,400]]
V11 =[[31,-39,-20], [56,4,19],[31,-39,-20],[0,0,400]]
V12 =[[13,-37,-20], [38,3,16],[13,-37,-20],[0,0,400]]

# ---------------------------------------------------------------
A1 = [[-40,-6,48,10], [3,26,68,100], [-40,-6,48,40]]
A2 = [[-47,3,26], [-8,31,49], [-47,3,26]]
A3 = [[-30,-23,37], [6,14,58],[-30,-23,37]]
A4 = [[-41,-10,15], [-2,21,40],[-41,-10,15]]
A5 = [[-40,-6,48], [-8,16,61], [-40,-6,48]]
A6 = [[-47,3,26], [-17,22,41], [-47,3,26]]
A7 = [[-30,-23,37], [-6,3,51],[-30,-23,37]]
A8 = [[-41,-10,15], [-14,11,32],[-41,-10,15]]

B1 = [[-35,48,-4], [2,66,28],[-35,48,-4]]
B2 = [[-46,24,4], [-5,49,35], [-46,24,4]]
B3 = [[-36,35,-23], [6,58,17],[-36,35,-23]]
B4 = [[-43,12,-9], [-2,38,22],[-43,12,-9]]
B5 = [[-35,48,-4], [-9,60,18], [-35,48,-4]]
B6 = [[-46,24,4], [-16,41,26], [-46,24,4]]
B7 = [[-36,35,-23], [-6,51,6],[-36,35,-23]]
B8 = [[-43,12,-9], [-14,31,13],[-43,12,-9]]

position_safe = [13,-37,-20,1]
position = [30,-8,6,100]
zero = [0,0,0,0]
# ---------------------------------------------------------------
#move_with_pump(A1)

#pick(V3)   
#place(A6)


# move(Home)
# time.sleep(1)
# move(position_safe)

# move(position_safe)
# time.sleep(1)
# move(Home)
# move_plus(Home, 30)

# move(Home)
# time.sleep(1)
# move_to_position(A1)
# move(position_safe)
# time.sleep(1)
# move(position)
# time.sleep(1)
# move(position)
# time.sleep(1)
# move(position)
move(Home)
time.sleep(1)
move(zero)
time.sleep(1)



