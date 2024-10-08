import os
import solenoid
import math

from dynamixel_sdk import *  # Uses Dynamixel SDK library

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
    #time.sleep(1)
    for angles in angles_list:
        move(angles)
        time.sleep(1)
# ---------------------------------------------------------------
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
        degree_motor1 = robot_move.deltakinematic('A') - minus
        degree_motor2 = robot_move.deltakinematic('B') - minus
        degree_motor3 = robot_move.deltakinematic('C') - minus
        return [degree_motor1, degree_motor2, degree_motor3]
# ---------------------------------------------------------------------------------------------------------------
# Pick_Angle
pick_position = {
    '1_1': [DeltaRobot.calculate_angles(-107, 170, 450), DeltaRobot.calculate_angles(-107, 170, 602), DeltaRobot.calculate_angles(-107, 170, 450)],
    '1_2': [DeltaRobot.calculate_angles(-110, 175, 450), DeltaRobot.calculate_angles(-110, 175, 558), DeltaRobot.calculate_angles(-110, 175, 450)],
    '1_3': [DeltaRobot.calculate_angles(-122, 182, 450), DeltaRobot.calculate_angles(-122, 182, 502), DeltaRobot.calculate_angles(-122, 182, 450)],
    '2_1': [DeltaRobot.calculate_angles(65, 170, 450),   DeltaRobot.calculate_angles(65, 170, 602),   DeltaRobot.calculate_angles(65, 170, 450)],
    '2_2': [DeltaRobot.calculate_angles(65, 170, 450),   DeltaRobot.calculate_angles(65, 170, 558),   DeltaRobot.calculate_angles(65, 170, 450)],
    '2_3': [DeltaRobot.calculate_angles(70, 177, 450),   DeltaRobot.calculate_angles(70, 177, 500),   DeltaRobot.calculate_angles(70, 177, 450)],
    '3_1': [DeltaRobot.calculate_angles(60, 310, 450),   DeltaRobot.calculate_angles(60, 310, 585),   DeltaRobot.calculate_angles(60, 310, 450)],
    '3_2': [DeltaRobot.calculate_angles(59, 315, 450),   DeltaRobot.calculate_angles(59, 315, 545),   DeltaRobot.calculate_angles(59, 315, 450)],
    '3_3': [DeltaRobot.calculate_angles(70, 320, 450),   DeltaRobot.calculate_angles(70, 320, 495),   DeltaRobot.calculate_angles(70, 320, 450)],
    '4_1': [DeltaRobot.calculate_angles(-97, 310, 450),  DeltaRobot.calculate_angles(-97, 310, 584),  DeltaRobot.calculate_angles(-97, 310, 450)],
    '4_2': [DeltaRobot.calculate_angles(-103, 315, 450), DeltaRobot.calculate_angles(-103, 315, 544), DeltaRobot.calculate_angles(-103, 315, 450)],
    '4_3': [DeltaRobot.calculate_angles(-114, 320, 450), DeltaRobot.calculate_angles(-114, 320, 494), DeltaRobot.calculate_angles(-114, 320, 450)]
}
# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
place_position = {
    'A1': [DeltaRobot.calculate_angles(230, -240, 450), DeltaRobot.calculate_angles(230, -240, 578)],
    'A2': [DeltaRobot.calculate_angles(100, -240, 450), DeltaRobot.calculate_angles(100, -240, 590)],
    'A3': [DeltaRobot.calculate_angles(230, -144, 450), DeltaRobot.calculate_angles(230, -144, 590)],
    'A4': [DeltaRobot.calculate_angles(100, -144, 450), DeltaRobot.calculate_angles(100, -144, 590)],
    'A5': [DeltaRobot.calculate_angles(230, -240, 450), DeltaRobot.calculate_angles(230, -240, 578)],
    'A6': [DeltaRobot.calculate_angles(100, -240, 450), DeltaRobot.calculate_angles(100, -240, 590)],
    'A7': [DeltaRobot.calculate_angles(230, -144, 450), DeltaRobot.calculate_angles(230, -144, 590)],
    'A8': [DeltaRobot.calculate_angles(100, -144, 450), DeltaRobot.calculate_angles(100, -144, 590)],
    # 새로운 B1-B8 위치 추가
    'B1': [DeltaRobot.calculate_angles(-165, -240, 450), DeltaRobot.calculate_angles(-165, -240, 590)],
    'B2': [DeltaRobot.calculate_angles(-252, -238, 450), DeltaRobot.calculate_angles(-252, -238, 575)],
    'B3': [DeltaRobot.calculate_angles(-105, -142, 450), DeltaRobot.calculate_angles(-105, -142, 600)],
    'B4': [DeltaRobot.calculate_angles(-248, -146, 450), DeltaRobot.calculate_angles(-248, -146, 582)],
    'B5': [DeltaRobot.calculate_angles(-116, -250, 450), DeltaRobot.calculate_angles(-116, -250, 542)],
    'B6': [DeltaRobot.calculate_angles(-252, -247, 450), DeltaRobot.calculate_angles(-252, -247, 534)],
    'B7': [DeltaRobot.calculate_angles(-105, -142, 450), DeltaRobot.calculate_angles(-105, -142, 548)],
    'B8': [DeltaRobot.calculate_angles(-248, -146, 450), DeltaRobot.calculate_angles(-248, -146, 555)]
}
Home=[-16,-16,-16,0]
# ---------------------------------------------------------------------------------------------------------------
# Place_Angle
safe_position = {
    # PALLET A   
    'AS1' : [DeltaRobot.calculate_angles(230, -240, 450),Home],
    'AS2' : [DeltaRobot.calculate_angles(100, -240, 450),Home],
    'AS3' : [DeltaRobot.calculate_angles(230, -144, 450),Home],
    'AS4' : [DeltaRobot.calculate_angles(100, -144, 450),Home],
    'AS5' : [DeltaRobot.calculate_angles(230, -240, 450),Home],
    'AS6' : [DeltaRobot.calculate_angles(100, -240, 450),Home],
    'AS7' : [DeltaRobot.calculate_angles(230, -144, 450),Home],
    'AS8' : [DeltaRobot.calculate_angles(100, -144, 450),Home],
    
    # PALLET B  
    'BS1' : [[-35,48,-4,0],[-16,-16,-16,0]],
    'BS2' : [[-46,24,4,0],[-16,-16,-16,0]],
    'BS3' : [[-36,35,-23,0],[-16,-16,-16,0]],
    'BS4' : [[-43,12,-9,0],[-16,-16,-16,0]],
    'BS5' : [[-35,48,-4,0],[-16,-16,-16,0]],
    'BS6' : [[-46,24,4,0],[-16,-16,-16,0]],
    'BS7' : [[-36,35,-23,0],[-16,-16,-16,0]],
    'BS8' : [[-43,12,-9,0],[-16,-16,-16,0]],
}          

# ---------------------------------------------------------------------------------------------------------------

motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_Y = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_N = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'] 

# motor_positions_A = ['A1','A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']  
# motor_positions_B = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
