import os
import socket
import threading
import cv2
import numpy as np
import time
import pandas as pd
import pyrealsense2 as rs

from datetime import datetime
from pyzbar import pyzbar
from queue import Queue

import motor_set_4
import solenoid
import mail
import IKinematics

# ---------------------------------------------------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host = '192.168.8.251'
UI_host = '192.168.8.1'
port = 3333

QR_data = ''
Motor_data = ''
new_data_available = threading.Event()

Vision_start_signal = False
Option_select = False
Motor_start_signal = False

lock = threading.Lock()
data_queue_QR = Queue()
data_queue_Motor = Queue()
condition = threading.Condition()

current_step_A = 0
current_step_B = 0
current_step_pick = 0

qr_data_list = []
last_qr_data = ''

# 새로운 전역 변수 추가
find_rect = True
read_info = False
current_roi_index = None
location = None
current_location = None
frame_count = 0
previous_location = None
box_info = None

# 상수 정의
DEPTH_RANGES = [(300, 340), (360, 390), (400, 450)]  # 3층, 2층, 1층 순서로 정의
# SHORT_RANGE = (40, 300)  # 짧은 변의 범위 (픽셀)
# LONG_RANGE = (130, 250)  # 긴 변의 범위 (픽셀)
SHORT_RANGE = (10, 300)  # 짧은 변의 범위 (픽셀)
LONG_RANGE = (20, 250)  # 긴 변의 범위 (픽셀)

X_OFFSET = -246  # 좌표계 변환을 위한 오프셋
Y_OFFSET = 64
pixel_to_mm = 0.78125  # 픽셀 당 mm 비율
CONSISTENT_FRAMES = 500000000000000000000000000000000000000000

# 각 ROI에 대한 카메라 오차 보정값 정의
# camera_diff_roi1_x = 35.52
# camera_diff_roi1_y = -8.2
# camera_diff_roi2_x = -4.2
# camera_diff_roi2_y = -20
# camera_diff_roi3_x = -2.7
# camera_diff_roi3_y = -38.5
# camera_diff_roi4_x = 41.5
# camera_diff_roi4_y = -29
camera_diff_roi1_x = 0
camera_diff_roi1_y = 0
camera_diff_roi2_x = 0
camera_diff_roi2_y = 0
camera_diff_roi3_x = 0
camera_diff_roi3_y = 0
camera_diff_roi4_x = 0
camera_diff_roi4_y = 0

# ---------------------------------------------------------------------------------------------------------------
def set_rois(color_width, color_height, depth_width, depth_height, roi_width, roi_height):
    """ROI 설정 (십자가 모양으로 나누고 각 영역 중앙에 사용자 지정 크기의 ROI 추가, 시계 방향으로 설정)"""
    color_center_x, color_center_y = color_width // 2, color_height // 2

    rois = [
        {'x': 0, 'y': 0, 'w': color_center_x, 'h': color_center_y},
        {'x': color_center_x, 'y': 0, 'w': color_center_x, 'h': color_center_y},
        {'x': color_center_x, 'y': color_center_y, 'w': color_center_x, 'h': color_center_y},
        {'x': 0, 'y': color_center_y, 'w': color_center_x, 'h': color_center_y}
    ]

    for i, roi in enumerate(rois):
        color_center_roi_x = roi['x'] + roi['w'] // 2
        color_center_roi_y = roi['y'] + roi['h'] // 2

        roi['color_roi'] = {
            'x': color_center_roi_x - roi_width // 2,
            'y': color_center_roi_y - roi_height // 2,
            'w': roi_width,
            'h': roi_height
        }

    return rois

def calculate_theta(rect):
    """사각형의 기울기 각도 계산"""
    angle = rect[2]
    width, height = rect[1]
    if width < height:
        angle = angle - 90 if angle > 45 else angle
    else:
        if angle < -45:
            angle = 90 + angle
    return round(angle)

def find_rectangle(roi):
    """ROI 내에서 직사각형 찾기 (크기 제한 적용)"""
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_rect = None
    
    for contour in contours:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        
        width, height = rect[1]
        short_side = min(width, height)
        long_side = max(width, height)
        
        if SHORT_RANGE[0] <= short_side <= SHORT_RANGE[1] and LONG_RANGE[0] <= long_side <= LONG_RANGE[1]:
            best_rect = rect
            break
    
    # if best_rect is not None:
    #     box = cv2.boxPoints(best_rect)
    #     box = np.int32(box)
    #     center = tuple(map(int, best_rect[0]))
    #     theta = calculate_theta(best_rect)
    #     return box, center, theta
    if best_rect is not None:
        box = cv2.boxPoints(best_rect)
        box = np.int32(box)
        center = tuple(map(int, np.mean(box, axis=0)))
        theta = calculate_theta(best_rect)
        return box, center, theta
    
    return None, None, None

def align_depth_to_color(frameset):
    """Depth 프레임을 Color 프레임에 정렬"""
    align = rs.align(rs.stream.color)
    aligned_frames = align.process(frameset)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    return aligned_depth_frame, color_frame

def get_depth_at_point(depth_image, point):
    """특정 지점의 depth 값 반환"""
    x, y = point
    return depth_image[y, x]

def determine_floor(depth):
    """depth 값을 이용해 층 결정"""
    for i, (min_depth, max_depth) in enumerate(DEPTH_RANGES):
        if min_depth <= depth <= max_depth:
            return 3 - i  # 3층, 2층, 1층 순서
    return None

def pixel_to_robot_coordinates(x, y, z, roi_index):
    """픽셀 좌표를 로봇 좌표계로 변환"""
    if roi_index == 0:
        diff_x, diff_y = camera_diff_roi1_x, camera_diff_roi1_y
    elif roi_index == 1:
        diff_x, diff_y = camera_diff_roi2_x, camera_diff_roi2_y
    elif roi_index == 2:
        diff_x, diff_y = camera_diff_roi3_x, camera_diff_roi3_y
    elif roi_index == 3:
        diff_x, diff_y = camera_diff_roi4_x, camera_diff_roi4_y
    else:
        diff_x, diff_y = 0, 0  # 기본값 설정
    
    robot_x = ((x + diff_x) * pixel_to_mm) + X_OFFSET
    robot_y = ((y + diff_y) * pixel_to_mm) + Y_OFFSET
    robot_z = z  
    return robot_x, robot_y, robot_z

def process_roi(color_image, depth_image, roi):
    """ROI 처리 및 QR 코드 검출"""
    color_roi = color_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']]
    depth_roi = depth_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']]
    
    decoded_objects = pyzbar.decode(color_roi)
    qr_data = None
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
    
    box, center, theta = find_rectangle(color_roi)
    
    if box is not None and center is not None:
        global_center = (roi['x'] + center[0], roi['y'] + center[1])
        depth = depth_roi[center[1], center[0]]
        floor = determine_floor(depth)
        return qr_data, global_center, theta, box, floor, depth
    
    return None, None, None, None, None, None

def process_frame(frameset, rois):
    global find_rect, read_info, current_roi_index, location, current_location, frame_count, previous_location, QR_data, box_info

    aligned_depth_frame, color_frame = align_depth_to_color(frameset)
    
    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    
    new_qr_data = None
    new_box_info = None

    if find_rect:
        rect_info = []
        for i, roi in enumerate(rois):
            _, center, _, _, floor, depth = process_roi(color_image, depth_image, roi)
            
            if center is not None and floor is not None:
                rect_info.append({
                    'roi_index': i,
                    'center': center,
                    'depth': depth,
                    'floor': floor,
                })
        
        if rect_info:
            # 층 정보를 기반으로 ROI 선택
            highest_rect = max(rect_info, key=lambda x: (x['floor'] or 0, -x['roi_index'], -float(x['depth'])))
            current_roi_index = highest_rect['roi_index']
            
            # 선택된 ROI에서 QR 코드와 위치 정보 추출
            selected_roi = rois[current_roi_index]
            qr_data, center, theta, box, floor, depth = process_roi(color_image, depth_image, selected_roi)
            
            if center is not None:
                pixel_x, pixel_y = center
                pixel_z = depth
                robot_x, robot_y, robot_z = pixel_to_robot_coordinates(pixel_x, pixel_y, pixel_z, current_roi_index)
                current_location = (robot_x, robot_y, robot_z, theta)
                print(current_location)
                
                if current_location == previous_location:
                    frame_count += 1
                    if frame_count >= CONSISTENT_FRAMES:
                        location = current_location
                        QR_data = qr_data
                        print(f"Consistent detection for {CONSISTENT_FRAMES} frames.")
                        print(f"Selected ROI: {current_roi_index + 1}")
                        print(f"Robot Location: X: {location[0]:.2f}, Y: {location[1]:.2f}, Z: {location[2]:.2f}, Theta: {location[3]:.2f}")
                        if QR_data:
                            print(f"QR Data: {QR_data}")
                        find_rect = False
                        read_info = True
                        frame_count = 0
                else:
                    previous_location = current_location
                    frame_count = 1
                
                # 시각화
                cv2.drawContours(color_image, [box + np.array([selected_roi['x'], selected_roi['y']])], 0, (0, 255, 0), 2)
                cv2.circle(color_image, center, 5, (0, 0, 255), -1)
                cv2.putText(color_image, f"Floor: {floor}, Depth: {depth:.2f}", 
                            (center[0]-50, center[1]-20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    elif read_info:
        if current_roi_index is not None:
            new_qr_data, center, theta, box, floor, depth = process_roi(color_image, depth_image, rois[current_roi_index])
            if center is not None:
                pixel_x, pixel_y = center
                pixel_z = depth
                robot_x, robot_y, robot_z = pixel_to_robot_coordinates(pixel_x, pixel_y, pixel_z, current_roi_index)
                new_box_info = {
                    'x': robot_x,
                    'y': robot_y,
                    'z': robot_z,
                    't': theta
                }
                if new_box_info != box_info and new_qr_data:
                    box_info = new_box_info
                    QR_data = new_qr_data
                    location = (robot_x, robot_y, robot_z, theta)  # Update location
                    print(f"Box Info: X: {box_info['x']:.2f}, Y: {box_info['y']:.2f}, Z: {box_info['z']:.2f}, Theta: {box_info['t']:.2f}")
                    print(f"QR Data: {QR_data}")
                    
                    read_info = False
                    find_rect = True
                    current_roi_index = None
                    frame_count = 0
                    previous_location = None
                    print("Box info updated and QR code read. Resetting state and starting new ROI search...")
    
    for i, roi in enumerate(rois):
        color = (0, 0, 255) if i == current_roi_index else (255, 0, 0)
        cv2.rectangle(color_image, (roi['x'], roi['y']), (roi['x'] + roi['w'], roi['y'] + roi['h']), color, 2)
        cv2.rectangle(depth_colormap, (roi['x'], roi['y']), (roi['x'] + roi['w'], roi['y'] + roi['h']), color, 2)
        
        cv2.putText(color_image, f"ROI {i+1}", (roi['x']+10, roi['y']+30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(depth_colormap, f"ROI {i+1}", (roi['x']+10, roi['y']+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return color_image, depth_colormap, new_qr_data, new_box_info
def read_qr_code(client_socket):
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data, qr_data_list

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    
    pipeline.start(config)

    color_height, color_width = 480, 640
    depth_height, depth_width = 480, 640
    
    rois = set_rois(color_width, color_height, depth_width, depth_height, 100, 100)
    last_detection_time = time.time()

    try:
        while Vision_start_signal:
            frameset = pipeline.wait_for_frames()
            
            color_image, depth_colormap, new_qr_data, new_box_info = process_frame(frameset, rois)

            cv2.imshow("QR_Code_and_Box_Detection", color_image)
            cv2.imshow("Depth_Visualization", depth_colormap)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if new_qr_data and new_box_info:
                last_detection_time = time.time()
                with lock:
                    if new_qr_data != last_qr_data:
                        last_qr_data = new_qr_data
                        parts = new_qr_data.split('/')
                        classifi = parts[0]
                        PackageNumber = parts[1]
                        Email = parts[2]
                        Destination = parts[3]
                        PhoneNumber = parts[4]
                        
                        recognition_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
                        qr_data_list.append({
                            'Classification': classifi, 
                            'Package Number': PackageNumber, 
                            'Email': Email, 
                            'Destination': Destination, 
                            'PhoneNumber': PhoneNumber, 
                            'Recognition time': recognition_time, 
                            'Position': None
                        })
                        
                        QR_data = f"{new_qr_data}/{'Vision'}/{'STR'}/{recognition_time}"
                        
                        data_queue_QR.put(QR_data)

                        # 통신으로 QR 데이터 전송
                        try:
                            client_socket.sendall(QR_data.encode('utf-8'))
                            print(f"Sent QR Data: {QR_data}")
                        except Exception as e:
                            print(f"Error sending QR data: {e}")
                            Vision_start_signal = False
                            break
                        
                        Motor_start_signal = True
                        time.sleep(0.5)
                        
                        Vision_start_signal = False

            if time.time() - last_detection_time > 10000000000000:
                print("No QR code detected for 10 seconds. Exiting...")
                break

    except Exception as e:
        print(f"Error in read_qr_code: {e}")
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        
# ---------------------------------------------------------------------------------------------------------------
# 모터를 움직이는 함수

def calculate_motor_angles(x, y, z, t):
    robot_move = IKinematics.IK().Move()
    robot_move.posX = x
    robot_move.posY = y
    robot_move.posZ = z
    robot_move.theta = t

    angle_A = robot_move.deltakinematic('A') - 10.046
    angle_B = robot_move.deltakinematic('B') - 10.046
    angle_C = robot_move.deltakinematic('C') - 10.046

    return angle_A, angle_B, angle_C, t

def motor_move(user_option, data_queue_QR):
    global current_step_A, current_step_B, current_step_pick, parts, place_position, Motor_data, location

    if location is not None:
        try:
            x, y, z, t = location
            print(f"Using location data: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}, Theta: {t:.2f}")
            
            angle_A, angle_B, angle_C, t = calculate_motor_angles(x, y, z, t)
            print(f"Calculated motor angles: A: {angle_A:.2f}, B: {angle_B:.2f}, C: {angle_C:.2f}, Theta: {t:.2f}")
            
            try:
                time.sleep(1.5)
                solenoid.airpump_on()
                time.sleep(1)
                motor_set_4.move([angle_A, angle_B, angle_C, t])
                print("Moved to calculated position")
                time.sleep(1)
            except PermissionError:
                print("Permission denied when trying to move motor. Please check hardware permissions.")
            except Exception as e:
                print(f"Error moving motor: {e}")
        except Exception as e:
            print(f"Error in motor movement calculation: {e}")
    else:
        print("No location data available")
    
    if not data_queue_QR.empty():
        try:
            classifi = parts[0]
            print(classifi)

            index_map = {
                'Option1': 0,
                'Option2': 1,
                'Option3': 2
            }

            classifi_index = index_map.get(user_option, 0)
            if len(classifi) > classifi_index:
                classifi_letter = classifi[classifi_index]
            else:
                print("Invalid classification data:", classifi)
                return

            option_map = {
                'Option1': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
                'Option2': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
                'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
            }

            user_option = option_map.get(user_option, {})
            criteria = user_option.get(classifi_letter)

            if criteria:
                current_step_place = globals()[f'current_step_{classifi_letter}']
                
                place_position = getattr(motor_set_4, criteria)[current_step_place % len(getattr(motor_set_4, criteria))]
                place_angle = motor_set_4.place_position[place_position]
                
                safe_position_key = place_position.replace('A', 'AS').replace('B', 'BS')
                safe_angle = motor_set_4.safe_position[safe_position_key]

                print(f"Current pick step: {current_step_pick}")
                
                try:
                    motor_set_4.place(place_angle)
                    motor_set_4.safe_place(safe_angle)
                    print(f"Moving to {place_position}")
                except PermissionError:
                    print("Permission denied when trying to move motor. Please check hardware permissions.")
                except Exception as e:
                    print(f"Error in motor movement: {e}")
                
                globals()[f'current_step_{classifi_letter}'] += 1
                current_step_pick += 1
                
                for data in qr_data_list:
                    if data['Classification'] == classifi and data['Position'] is None:
                        data['Position'] = place_position
                        break
            else:
                print("Invalid option or classifi received", classifi_letter)
        except Exception as e:
            print(f"Error in QR data processing: {e}")

    Motor_data = f"{place_position}/{'Motor'}/{'END'}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]}"
    data_queue_Motor.put(Motor_data)
    
# ---------------------------------------------------------------------------------------------------------------
# QR 정보를 UI로 보냄
def server_func():
    global QR_data, Motor_data, Option_select, data_queue_QR

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((Vision_Motor_host, port))
    server_socket.listen()
    print('Vision_server waiting for connection...')

    client_soc, addr = server_socket.accept()
    print('Vision_server connected to', addr)

    last_sent_QR_data = ""
    last_sent_Motor_data = ""

    try:
        while True:
            if Option_select:
                if QR_data and QR_data != last_sent_QR_data:
                    client_soc.sendall(QR_data.encode('utf-8'))
                    #print("Sent QR Data: ", QR_data)
                    last_sent_QR_data = QR_data
                    time.sleep(1)

                if Motor_data and Motor_data != last_sent_Motor_data:
                    client_soc.sendall(Motor_data.encode('utf-8'))
                    print("Sent Motor Data: ", Motor_data)
                    last_sent_Motor_data = Motor_data
                    time.sleep(2)

            else:
                print("No QR Data to send")
                time.sleep(2)
            time.sleep(1)

    except Exception as e:
        print("Error sending data:", e)
    finally:
        client_soc.close()
        server_socket.close()

# ---------------------------------------------------------------------------------------------------------------
# UI에서 Option 정보 받으면 Vision 작동 시켜서 모터 움직임
def command_listener(client_socket):
    global Option_select, Vision_start_signal, Motor_start_signal, option_data_received, qr_data_list
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                continue

            if data.startswith("Option"):
                option_data_received = data
                Option_select = True
                Vision_start_signal = True
                print(f"Option Received: {option_data_received}")

            elif data == 'pause':
                Vision_start_signal = False
                print("System is paused.")

            elif data == 'reset':
                Option_select = False
                print("System is reset.")
                time.sleep(2)

                if qr_data_list:
                    try:
                        df = pd.DataFrame(qr_data_list)
                        save_path = 'C:\\Users\\Lee\\Shawn\\Capstone\\Perfect\\QR_Data\\qr_data.xlsx'
                        
                        print("QR 데이터 프레임 내용:")
                        print(df)

                        df_A = df[df['Position'].str.contains('A', na=False)]
                        df_B = df[df['Position'].str.contains('B', na=False)]
                        
                        print("Position A 데이터 프레임 내용:")
                        print(df_A)
                        print("Position B 데이터 프레임 내용:")
                        print(df_B)

                        with pd.ExcelWriter(save_path) as writer:
                            df.to_excel(writer, sheet_name='QR Data', index=False)
                            df_A.to_excel(writer, sheet_name='Position A', index=False)
                            df_B.to_excel(writer, sheet_name='Position B', index=False)
                        print(f"QR 데이터가 엑셀 파일로 저장되었습니다. 저장 경로: {save_path}")
                        
                        mail.send_logitics_data()
                        print('모든 이메일 전송 완료')
                        
                        time.sleep(2)

                    except Exception as e:
                        print(f"엑셀 파일 저장 중 오류 발생: {e}")
                else:
                    print("QR 데이터 리스트가 비어 있습니다.")

            elif data == 'quit':
                print("Quitting...")
                break

            else:
                print("Unknown command received.")

        except socket.error as e:
            print(f"Error during communication: {e}")
            break

# ---------------------------------------------------------------------------------------------------------------
def client_func():
    global Option_select, Vision_start_signal, Motor_start_signal, option_data_received
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((UI_host, port))
            print("Connected to UI host")

            command_thread = threading.Thread(target=command_listener, args=(client_socket,))
            command_thread.start()

            while True:
                if Option_select and Vision_start_signal:
                    read_qr_code(client_socket)

                elif not Vision_start_signal and Option_select and Motor_start_signal:
                    print("motor_signal")
                    motor_move(option_data_received, data_queue_QR)
                    Motor_start_signal = False
                    Vision_start_signal = True

                    print("Vision is ON")
                    time.sleep(0.5)

                else:
                    time.sleep(1)

        except socket.error as e:
            print(f"Connection error: {e}")
            print("Retrying connection in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error in client_func: {e}")
        finally:
            client_socket.close()
            if command_thread.is_alive():
                command_thread.join()

# ---------------------------------------------------------------------------------------------------------------
# 서버와 클라이언트를 멀티스레드로
if __name__ == "__main__":
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()