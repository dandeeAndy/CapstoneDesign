import os
import time

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# ---- IK import (robust) -------------------------------------------------------
# 1) 패키지 경로: hanium/Perfect/Inverse_Kinematics_latest.py
# 2) 로컬 파일:   Inverse_Kinematics.py
# 3) 없으면 HAS_IK=False 로 동작
ik = None
HAS_IK = False
try:
    # 올바른 문법: from ... import ... as ...
    from hanium.Perfect import Inverse_Kinematics_latest as ik
    HAS_IK = True
except ModuleNotFoundError:
    try:
        import Inverse_Kinematics as ik
        HAS_IK = True
    except ModuleNotFoundError:
        print("[IK] No IK module found. Running without IK.")
# ------------------------------------------------------------------------------


# DYNAMIXEL Model & Protocol Version
MY_DXL = 'X_SERIES'
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDs = [1, 2, 3, 4]  # Dynamixel IDs
BAUDRATE = 57600
DEVICENAME = 'COM17'  # Port Name
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
MID_POSITION = 2048
ANGLE_PER_UNIT = 11.3777  # angle → Dynamixel unit

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
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, dxl_id, ADDR_OPERATING_MODE, EXTENDED_POSITION_CONTROL_MODE
    )
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to change operating mode for Dynamixel#{dxl_id}")
        exit()

    # Enable torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
        portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE
    )
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for Dynamixel#{dxl_id}")
        exit()

    # Velocity / Profile 설정
    goal_velocity = 200
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, dxl_id, ADDR_GOAL_VELOCITY, goal_velocity
    )
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal velocity for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal velocity error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

    goal_profile_acceleration = 1800
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, dxl_id, ADDR_GOAL_PROFILE_ACCELERATION, goal_profile_acceleration
    )
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal profile acceleration for Dynamixel#{dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
        exit()
    elif dxl_error != 0:
        print(f"Goal profile acceleration error for Dynamixel#{dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
        exit()

    goal_profile_velocity = 900
    dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, dxl_id, ADDR_GOAL_PROFILE_VELOCITY, goal_profile_velocity
    )
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
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position
        )
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
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#{dxl_id}")
            exit()

    if goal_position_4 < 0 or goal_position_4 > 4095:
        print(f"Goal position {goal_position_4} out of range for Dynamixel#4")
    else:
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
            portHandler, 4, ADDR_GOAL_POSITION, goal_position_4
        )
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal position for Dynamixel#4")
            exit()

# ---------------------------------------------------------------
def move_to_position(angles_list):
    for angles in angles_list:
        move(angles)
        time.sleep(1)

def pick(angles_list):
    time.sleep(2)
    for angles in angles_list:
        move(angles)
        time.sleep(1)

def place(angles_list):
    time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)

# ---------------------------------------------------------------
# 포인트 집합(4축 형태로 정규화)
Home = [-16, -16, -16, 0]

V1  = [[11,-17,-42,0],[23,0,-20,0],[11,-17,-42,0],[0,0,400,0]]
V2  = [[32,-17,-40,0],[41,1,-19,0],[32,-17,-40,0],[0,0,400,0]]
V3  = [[31,-39,-20,0],[41,-18,-2,0],[32,-45,-25,0],[-57,-5,20,0]]
V4  = [[13,-37,-20,0],[22,-19,-4,0],[13,-37,-20,0],[0,0,400,0]]
V5  = [[11,-17,-42,0],[30,9,-9,0],[11,-17,-42,0],[0,0,400,0]]
V6  = [[32,-17,-40,0],[47,11,-7,0],[32,-17,-40,0],[0,0,400,0]]
V7  = [[31,-39,-20,0],[48,-6,8,0],[31,-39,-20,0],[0,0,400,0]]
V8  = [[13,-37,-20,0],[30,-8,6,0],[13,-37,-20,0],[0,0,400,0]]
V9  = [[11,-17,-42,0],[38,19,2,0],[11,-17,-42,0],[0,0,400,0]]
V10 = [[32,-17,-40,0],[55,20,3,0],[32,-17,-40,0],[0,0,400,0]]
V11 = [[31,-39,-20,0],[56,4,19,0],[31,-39,-20,0],[0,0,400,0]]
V12 = [[13,-37,-20,0],[38,3,16,0],[13,-37,-20,0],[0,0,400,0]]

A1 = [[-40,-6,48,0],[3,26,68,0],[-40,-6,48,0]]
A2 = [[-47,3,26,0],[-8,31,49,0],[-47,3,26,0]]
A3 = [[-30,-23,37,0],[6,14,58,0],[-30,-23,37,0]]
A4 = [[-41,-10,15,0],[-2,21,40,0],[-41,-10,15,0]]
A5 = [[-40,-6,48,0],[-8,16,61,0],[-40,-6,48,0]]
A6 = [[-47,3,26,0],[-17,22,41,0],[-47,3,26,0]]
A7 = [[-30,-23,37,0],[-6,3,51,0],[-30,-23,37,0]]
A8 = [[-41,-10,15,0],[-14,11,32,0],[-41,-10,15,0]]

B1 = [[-35,48,-4,0],[2,66,28,0],[-35,48,-4,0]]
B2 = [[-46,24,4,0],[-5,49,35,0],[-46,24,4,0]]
B3 = [[-36,35,-23,0],[6,58,17,0],[-36,35,-23,0]]
B4 = [[-43,12,-9,0],[-2,38,22,0],[-43,12,-9,0]]
B5 = [[-35,48,-4,0],[-9,60,18,0],[-35,48,-4,0]]
B6 = [[-46,24,4,0],[-16,41,26,0],[-46,24,4,0]]
B7 = [[-36,35,-23,0],[-6,51,6,0],[-36,35,-23,0]]
B8 = [[-43,12,-9,0],[-14,31,13,0],[-43,12,-9,0]]

# ================================================================================================
# Position 설정: IK 모듈이 있으면 그것을 우선 사용, 없으면 상수 기반 보정 사용
# ================================================================================================
if HAS_IK:
    position_upgrade = [ik.AA, ik.BB, ik.CC, 0]
else:
    a = 8.424; b = 20.448; c = 49.097; minus = 12.253
    position_upgrade = [a - minus, b - minus, c - minus, 0]
print("position_upgrade:", position_upgrade)

# 실행 시퀀스
move(Home)
time.sleep(1)
move(position_upgrade)
