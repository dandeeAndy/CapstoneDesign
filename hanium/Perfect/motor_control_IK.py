import os
#import solenoid
import math

from dynamixel_sdk import *  # Uses Dynamixel SDK library
import Inverse_Kinematics_latest as ik

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
    goal_velocity = 200
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_VELOCITY, goal_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
    
# ---------------------------------------------------------------------------------------------------------------    
# Set goal profile acceleration
    # goal_profile_acceleration = 1500  # 기본값
    goal_profile_acceleration = 2000
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_ACCELERATION, goal_profile_acceleration)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile acceleration for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile acceleration error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

# ---------------------------------------------------------------------------------------------------------------
# Set goal profile velocity
    # goal_profile_velocity = 550  # 기본값
    goal_profile_velocity = 900
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_PROFILE_VELOCITY, goal_profile_velocity)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()
        
# ===========================================================================================================================
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
# ===========================================================================================================================
def pick(angles_list):
   time.sleep(2)
#    solenoid.airpump_on()
   for angles in angles_list:
       move(angles)
       time.sleep(1)
        
# ===========================================================================================================================
def place(angles_list):
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)

# ===========================================================================================================================
# ===========================================================================================================================
# ===========================================================================================================================
class DeltaRobot:
    class Move:
        def __init__(self):
            self.a = 100.0
            self.b = 260.0
            self.c = 600.0
            self.d = 42.5
            self.posX, self.posY, self.posZ = 230, -144, 542
            
        def set_position(self, x, y, z):
            self.posX, self.posY, self.posZ = x, y, z
            
        def deltakinematic(self, servo):
            pi180 = 180.0 * (math.pi / 180.0)
            pi300 = 300.0 * (math.pi / 180.0)
            pi420 = 420.0 * (math.pi / 180.0)

            x = y = z = 0.0
            
            if servo == 'A':
                x = math.cos(pi180) * self.posX + math.sin(pi180) * self.posY
                y = -math.sin(pi180) * self.posX + math.cos(pi180) * self.posY
                z = self.posZ
            elif servo == 'B':
                x = math.cos(pi300) * self.posX + math.sin(pi300) * self.posY
                y = -math.sin(pi300) * self.posX + math.cos(pi300) * self.posY
                z = self.posZ
            elif servo == 'C':
                x = math.cos(pi420) * self.posX + math.sin(pi420) * self.posY
                y = -math.sin(pi420) * self.posX + math.cos(pi420) * self.posY
                z = self.posZ

            length1 = (self.a - self.d - y)
            alpha = (360.0 / (2.0 * math.pi)) * math.atan2(z, length1)
            length2 = math.sqrt(math.pow(self.c, 2) - math.pow(x, 2))
            length3 = math.sqrt(math.pow(length1, 2) + math.pow(z, 2))

            cosine_angle = (math.pow(length3, 2) - math.pow(length2, 2) + math.pow(self.b, 2)) / (2.0 * length2 * self.b)
            beta = (360.0 / (2.0 * math.pi)) * math.acos(cosine_angle)
            gamma = 180.0 - alpha - beta

            return gamma

    @staticmethod
    def calculate_angles(x, y, z):
        robot_move = DeltaRobot.Move()
        robot_move.set_position(x, y, z)
        minus = 10.046
        AA = robot_move.deltakinematic('A') - minus
        BB = robot_move.deltakinematic('B') - minus
        CC = robot_move.deltakinematic('C') - minus
        return [AA, BB, CC, 0]

# Define position arrays
A1 = DeltaRobot.calculate_angles(230, -240, 578)
A2 = DeltaRobot.calculate_angles(100, -240, 590)
A3 = DeltaRobot.calculate_angles(230, -144, 590)
A4 = DeltaRobot.calculate_angles(100, -144, 600)
A5 = DeltaRobot.calculate_angles(230, -240, 540)
A6 = DeltaRobot.calculate_angles(100, -250, 542)
A7 = DeltaRobot.calculate_angles(230, -144, 548)
A8 = DeltaRobot.calculate_angles(100, -149, 555)


# A1 = [[],DeltaRobot.calculate_angles(230, -240, 578),[]]
# A2 = [[],DeltaRobot.calculate_angles(100, -240, 590),[]]
# A2 = [[],DeltaRobot.calculate_angles(100, -240, 590),[]]
# A3 = [[],DeltaRobot.calculate_angles(230, -144, 590),[]]
# A4 = [[],DeltaRobot.calculate_angles(100, -144, 600),[]]
# A5 = [[],DeltaRobot.calculate_angles(230, -240, 540),[]]
# A6 = [[],DeltaRobot.calculate_angles(100, -250, 542),[]]
# A7 = [[],DeltaRobot.calculate_angles(230, -144, 548),[]]
# A8 = [[],DeltaRobot.calculate_angles(100, -149, 555),[]]

Home = [-16,-16,-16, 0]

move(Home)
time.sleep(1)
move(A1)
time.sleep(1)
move(A2)
time.sleep(1)
move(A3)
time.sleep(1)
move(A4)
time.sleep(1)
move(A5)
time.sleep(1)
move(A6)
time.sleep(1)
move(A7)
time.sleep(1)
move(A8)
time.sleep(1)

# ===========================================================================================================================
# ===========================================================================================================================
# ===========================================================================================================================
Home = [-16,-16,-16,-21]
# position_upgrade = [ik.AA, ik.BB, ik.CC, 0]
# print("position_upgrade: ", position_upgrade)
# ===========================================================================================================================
# 실행
move(Home)
# time.sleep(1)
# move(position_upgrade)