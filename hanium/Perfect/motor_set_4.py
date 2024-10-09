import os
import solenoid

from dynamixel_sdk import *  # Uses Dynamixel SDK library
from IKinematics import IK

# DYNAMIXEL Model & Protocol Version
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDs = [1, 2, 3, 4]  # Dynamixel IDs
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
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)
# ---------------------------------------------------------------
Home = [-16,-16,-16,0]
# ---------------------------------------------------------------------------------------------------------------
# Pick_Angle
pick_position = {
    '1_1': [IK.c_deg(-107, 170, 450), IK.c_deg(-107, 170, 602), IK.c_deg(-107, 170, 450)],
    '2_1': [IK.c_deg(-110, 175, 450), IK.c_deg(-110, 175, 558), IK.c_deg(-110, 175, 450)],
    '3_1': [IK.c_deg(-114, 182, 450), IK.c_deg(-114, 182, 503), IK.c_deg(-114, 182, 450)],
    '1_2': [IK.c_deg(67, 172, 450),   IK.c_deg(67, 172, 602),   IK.c_deg(67, 172, 450)],
    '2_2': [IK.c_deg(70, 175, 450),   IK.c_deg(70, 175, 562),   IK.c_deg(70, 175, 450)],
    '3_2': [IK.c_deg(70, 180, 450),   IK.c_deg(70, 180, 503),   IK.c_deg(70, 180, 450)],
    '1_3': [IK.c_deg(60, 310, 450),   IK.c_deg(60, 310, 585),   IK.c_deg(60, 310, 450)],
    '2_3': [IK.c_deg(64, 314, 450),   IK.c_deg(64, 314, 545),   IK.c_deg(64, 314, 450)],
    '3_3': [IK.c_deg(66, 318, 450),   IK.c_deg(66, 318, 497),   IK.c_deg(66, 318, 450)],
    '1_4': [IK.c_deg(-98, 310, 450),  IK.c_deg(-98, 310, 582),  IK.c_deg(-98, 310, 450)],
    '2_4': [IK.c_deg(-105, 314, 450), IK.c_deg(-105, 314, 542), IK.c_deg(-105, 314, 450)],
    '3_4': [IK.c_deg(-112, 320, 450), IK.c_deg(-112, 320, 494), IK.c_deg(-112, 320, 450)]
}
# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
place_position = {
    'A1': [(IK.c_deg(232, -232, 450) + [0]), (IK.c_deg(232, -232, 582) + [0])],
    'A2': [(IK.c_deg(95,  -240, 450) + [0]), (IK.c_deg(95, -234, 594) + [0])],
    'A3': [(IK.c_deg(230, -144, 450) + [0]), (IK.c_deg(228, -143, 590) + [0])],
    'A4': [(IK.c_deg(100, -144, 450) + [0]), (IK.c_deg(94, -142, 600) + [0])],
    'A5': [(IK.c_deg(230, -240, 450) + [0]), (IK.c_deg(235, -238, 541) + [0])],
    'A6': [(IK.c_deg(100, -240, 450) + [0]), (IK.c_deg(97, -242, 550) + [0])],
    'A7': [(IK.c_deg(230, -144, 450) + [0]), (IK.c_deg(230, -144, 548) + [0])],
    'A8': [(IK.c_deg(100, -144, 450) + [0]), (IK.c_deg(97, -147, 554) + [0])],
    
    'B1': [(IK.c_deg(-117, -238, 450) + [0]), (IK.c_deg(-116, -240, 593) + [0])],
    'B2': [(IK.c_deg(-252, -235, 450) + [0]), (IK.c_deg(-252, -238, 577) + [0])],
    'B3': [(IK.c_deg(-109, -140, 450) + [0]), (IK.c_deg(-109, -140, 600) + [0])],
    'B4': [(IK.c_deg(-248, -146, 450) + [0]), (IK.c_deg(-247, -149, 588) + [0])],
    'B5': [(IK.c_deg(-116, -246, 450) + [0]), (IK.c_deg(-116, -247, 549) + [0])],
    'B6': [(IK.c_deg(-254, -244, 450) + [0]), (IK.c_deg(-254, -246, 536) + [0])],
    'B7': [(IK.c_deg(-112, -142, 450) + [0]), (IK.c_deg(-111, -144, 555) + [0])],
    'B8': [(IK.c_deg(-250, -146, 450) + [0]), (IK.c_deg(-249, -150, 547) + [0])]
}
# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
safe_position = {
    # PALLET A   
    'AS1' : [(IK.c_deg(232, -232, 450) + [0]), Home],
    'AS2' : [(IK.c_deg(95,  -240, 450) + [0]), Home],
    'AS3' : [(IK.c_deg(230, -144, 450) + [0]), Home],
    'AS4' : [(IK.c_deg(100, -144, 450) + [0]), Home],
    'AS5' : [(IK.c_deg(230, -240, 450) + [0]), Home],
    'AS6' : [(IK.c_deg(100, -240, 450) + [0]), Home],
    'AS7' : [(IK.c_deg(230, -144, 450) + [0]), Home],
    'AS8' : [(IK.c_deg(100, -144, 450) + [0]), Home],

    # PALLET B  
    'BS1' : [(IK.c_deg(-117, -238, 450) + [0]), Home],
    'BS2' : [(IK.c_deg(-252, -235, 450) + [0]), Home],
    'BS3' : [(IK.c_deg(-109, -140, 450) + [0]), Home],
    'BS4' : [(IK.c_deg(-248, -146, 450) + [0]), Home],
    'BS5' : [(IK.c_deg(-116, -246, 450) + [0]), Home],
    'BS6' : [(IK.c_deg(-254, -244, 450) + [0]), Home],
    'BS7' : [(IK.c_deg(-112, -142, 450) + [0]), Home],
    'BS8' : [(IK.c_deg(-250, -146, 450) + [0]), Home]
}          

# ---------------------------------------------------------------------------------------------------------------

motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_Y = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_N = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']