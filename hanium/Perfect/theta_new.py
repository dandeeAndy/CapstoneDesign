import os
import socket
import math
import threading
import cv2
import numpy as np
import time
import pandas as pd
import pyrealsense2 as rs
import logging
import traceback
from datetime import datetime
from pyzbar import pyzbar
from queue import Queue

import motor_set_4
import solenoid
import mail

# Global variables
Vision_Motor_host = '192.168.8.251'
UI_host = '192.168.8.1'
port = 3333

QR_data = ''
Motor_data = ''
new_data_available = threading.Event()

Vision_start_signal = False
Option_select = False
Motor_start_signal = False
theta_printed = False  

lock = threading.Lock()
data_queue_QR = Queue()
data_queue_Motor = Queue()
condition = threading.Condition()

qr_data_list = []
last_qr_data = ''

# New global variables
find_rect = True
read_info = False
current_roi_index = None
location = None
current_location = None
frame_count = 0
previous_location = None
box_info = None
qr_data = None
theta_frame_count = 0
previous_theta = None
consistent_theta = None
current_step_A = 0
current_step_B = 0


# Constants
DEPTH_RANGES = [(300, 340), (360, 390), (400, 450)]  # 3층, 2층, 1층 순서로 정의
# SHORT_RANGE = (20, 300)  # 짧은 변의 범위 (픽셀)
# LONG_RANGE = (100, 350)  # 긴 변의 범위 (픽셀)
SHORT_RANGE = (100, 180)  # 짧은 변의 범위 (픽셀)
LONG_RANGE = (100, 190)
CONSISTENT_FRAMES_ROI = 24
CONSISTENT_FRAMES_THETA = 12

def set_rois(color_width, color_height, depth_width, depth_height, roi_width, roi_height):
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
    (cx, cy), (width, height), angle = rect
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    right_points = box[np.argsort(box[:, 0])[-2:]]
    right_mid_x = int(np.mean(right_points[:, 0]))
    right_mid_y = int(np.mean(right_points[:, 1]))

    vector_x = right_mid_x - cx
    vector_y = right_mid_y - cy

    theta = math.degrees(math.atan2(vector_y, vector_x))
    # 부호를 반대로 바꿉니다.

    if theta > 90:
        theta = theta - 180
    elif theta < -90:
        theta = theta + 180

    return round(theta)

def visualize_angle(image, rect, theta):
    (cx, cy), (width, height), angle = rect
    cx, cy = int(cx), int(cy)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    right_points = box[np.argsort(box[:, 0])[-2:]]
    right_mid_x = int(np.mean(right_points[:, 0]))
    right_mid_y = int(np.mean(right_points[:, 1]))

    cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)  # 중점
    cv2.circle(image, (right_mid_x, right_mid_y), 5, (0, 0, 255), -1)  # 오른쪽 변의 중점
    cv2.line(image, (cx, cy), (right_mid_x, right_mid_y), (0, 150, 255), 2)
    cv2.line(image, (cx - 100, cy), (cx + 100, cy), (0, 255, 255), 2)

def find_rectangle(roi):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # 모폴로지 연산을 통해 엣지를 더 굵게 만듭니다.
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_rect = None
    max_area = 0
    
    for contour in contours:
        # 컨투어를 근사화합니다.
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # 근사화된 컨투어가 4개의 꼭지점을 가지면 사각형으로 간주합니다.
        if len(approx) == 4:
            rect = cv2.minAreaRect(approx)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            
            # 사각형의 넓이를 계산합니다.
            area = cv2.contourArea(box)
            
            # 사각형의 짧은 변과 긴 변 길이 계산
            width, height = rect[1]
            short_side = min(width, height)
            long_side = max(width, height)
            
            # 크기 제한 조건 확인 (조건을 조금 더 유연하게 조정)
            if (SHORT_RANGE[0] * 0.5 <= short_side <= SHORT_RANGE[1] * 1.5 and 
                LONG_RANGE[0] * 0.5 <= long_side <= LONG_RANGE[1] * 1.5):
                if area > max_area:
                    max_area = area
                    best_rect = rect
    
    if best_rect is not None:
        box = cv2.boxPoints(best_rect)
        box = np.int32(box)
        center = tuple(map(int, best_rect[0]))
        theta = calculate_theta(best_rect)  # 수정된 부분
        return box, center, theta, roi.copy()  # visualized_image 대신 roi.copy() 반환
    
    return None, None, None, None

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

def process_roi(color_image, depth_image, roi, roi_index=None):
    """ROI 처리 및 QR 코드 검출"""
    color_roi = color_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']]
    depth_roi = depth_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']]
    
    decoded_objects = pyzbar.decode(color_roi)
    qr_data = None
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
    
    box, center, angle, visualized_roi = find_rectangle(color_roi)
    
    if box is not None and center is not None:
        global_center = (roi['x'] + center[0], roi['y'] + center[1])
        depth = depth_roi[center[1], center[0]]
        floor = determine_floor(depth)
        
        color_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']] = visualized_roi
        
        return qr_data, global_center, angle, box, floor, depth
    
    return None, None, None, None, None, None

def setup_windows():
    """윈도우 설정"""
    windows = [
        "QR_Code_and_Box_Detection", "Depth_Visualization",
        "Edges", "Contours"
    ]
    for window in windows:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.waitKey(1000)  # 윈도우가 생성될 시간을 주기 위해 잠시 대기

def process_frame(frameset, rois):
    global find_rect, read_info, current_roi_index, location, frame_count, previous_location, QR_data, box_info
    global theta_frame_count, previous_theta, consistent_theta, theta_printed
    
    aligned_depth_frame, color_frame = align_depth_to_color(frameset)
    
    color_image = np.asanyarray(color_frame.get_data())
    original_color_image = color_image.copy()
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    
    new_qr_data = None
    new_box_info = None

    if find_rect:
        rect_info = []
        for i, roi in enumerate(rois):
            qr_data, center, theta, box, floor, depth = process_roi(color_image, depth_image, roi, i)
            
            if center is not None and floor is not None:
                rect_info.append({
                    'roi_index': i,
                    'center': center,
                    'depth': depth,
                    'floor': floor,
                    'theta': theta,
                    'box': box,
                    'qr_data': qr_data
                })
                
                cv2.drawContours(color_image, [box + np.array([roi['x'], roi['y']])], 0, (0, 255, 0), 2)
                cv2.circle(color_image, center, 5, (0, 0, 255), -1)
                cv2.putText(color_image, f"Floor: {floor}, Depth: {depth:.2f}", 
                            (center[0]-50, center[1]-20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        if rect_info:
            # 층 정보를 기반으로 ROI 선택
            highest_rect = max(rect_info, key=lambda x: (x['floor'] or 0, -x['roi_index'], -float(x['depth'])))
            current_location = (highest_rect['floor'], highest_rect['roi_index'] + 1)
            
            # 선택된 ROI에서 QR 코드와 위치 정보 추출
            if current_location == previous_location:
                frame_count += 1
                if frame_count >= CONSISTENT_FRAMES_ROI:
                    location = current_location
                    current_roi_index = highest_rect['roi_index']
                    QR_data = highest_rect['qr_data']
                    #print(f"Consistent detection for {CONSISTENT_FRAMES} frames.")
                    print(f"Selected ROI: {current_roi_index + 1}")
                    print(f"Floor: {location[0]}, ROI: {location[1]}")
                    if QR_data:
                        print(f"QR Data: {QR_data}")
                    find_rect = False
                    read_info = True
                    frame_count = 0
                    theta_frame_count = 0
                    previous_theta = None
                    consistent_theta = None
                    theta_printed = False
            else:
                previous_location = current_location
                frame_count = 1
                
    elif read_info:
            if current_roi_index is not None:
                new_qr_data, center, _, box, floor, depth = process_roi(color_image, depth_image, rois[current_roi_index])
                if center is not None:
                    roi = rois[current_roi_index]
                    roi_image = color_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']]
                    
                    rect = cv2.minAreaRect(box)
                    new_theta = calculate_theta(rect)
                    
                    # ROI가 활성화된 후에만 시각화 수행
                    visualize_angle(roi_image, rect, new_theta)
                    color_image[roi['y']:roi['y']+roi['h'], roi['x']:roi['x']+roi['w']] = roi_image

                    cv2.drawContours(color_image, [box + np.array([roi['x'], roi['y']])], 0, (0, 255, 0), 2)
                    cv2.circle(color_image, center, 5, (0, 0, 255), -1)
                    cv2.putText(color_image, f"Theta: {new_theta}", 
                                (center[0]-50, center[1]-20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    # theta 값의 일관성 체크
                    if new_theta == previous_theta:
                        theta_frame_count += 1
                        if theta_frame_count >= CONSISTENT_FRAMES_THETA:
                            consistent_theta = new_theta
                            if not theta_printed:
                                theta_printed = True
                    else:
                        theta_frame_count = 1
                        previous_theta = new_theta
                        theta_printed = False

                    if consistent_theta is not None:
                        new_box_info = {
                            'floor': floor,
                            'roi': current_roi_index + 1,
                            'theta': consistent_theta
                        }
                        if new_box_info != box_info and new_qr_data:
                            box_info = new_box_info
                            QR_data = new_qr_data
                            location = (floor, current_roi_index + 1, consistent_theta)
                            print(f"New Box Info: Floor: {box_info['floor']}, ROI: {box_info['roi']}, Theta: {box_info['theta']:.2f}")
                            print(f"New QR Data: {QR_data}")
                            
                            # ROI 초기화
                            read_info = False
                            find_rect = True
                            current_roi_index = None
                            frame_count = 0
                            previous_location = None
                            theta_frame_count = 0
                            previous_theta = None
                            consistent_theta = None
                            theta_printed = False
                            print("Box info updated and QR code read. Resetting state and starting new ROI search...")
        
    for i, roi in enumerate(rois):
        color = (0, 0, 255) if i == current_roi_index else (255, 0, 0)
        cv2.rectangle(color_image, (roi['x'], roi['y']), (roi['x'] + roi['w'], roi['y'] + roi['h']), color, 2)
        cv2.rectangle(depth_colormap, (roi['x'], roi['y']), (roi['x'] + roi['w'], roi['y'] + roi['h']), color, 2)
        
        cv2.putText(color_image, f"ROI {i+1}", (roi['x']+10, roi['y']+30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(depth_colormap, f"ROI {i+1}", (roi['x']+10, roi['y']+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    gray = cv2.cvtColor(original_color_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    return color_image, depth_colormap, new_qr_data, new_box_info, edges

def read_qr_code(client_socket):
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data, qr_data_list, location

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
            
            color_frame = frameset.get_color_frame()
            depth_frame = frameset.get_depth_frame()
            
            if not color_frame or not depth_frame:
                continue
            
            color_image = np.asanyarray(color_frame.get_data())
            color_image, depth_colormap, new_qr_data, new_box_info, edges = process_frame(frameset, rois)
            cv2.imshow("Color Image", color_image)
            cv2.imshow("Depth Colormap", depth_colormap)
            cv2.imshow("Edges",edges)
            
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
                        floor = new_box_info.get('floor')
                        roi = new_box_info.get('roi')
                        theta = new_box_info.get('theta')
                        
                         # location 업데이트 전에 값 확인
                        if floor is not None and roi is not None and theta is not None:
                            location = (floor, roi, theta)
                            print(f"Updated location: {location}")
                        else:
                            print(f"Error: Invalid box info. Floor: {floor}, ROI: {roi}, Theta: {theta}")
                        
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
                        last_qr_data = new_qr_data
                        

            if time.time() - last_detection_time > 100:
                print("No QR code detected for 100 seconds. Exiting...")
                break

    except Exception as e:
        print(f"Error in read_qr_code: {e}")
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

# def motor_move(user_option, data_queue_QR):
#     global parts, Motor_data, location

#     if location is not None:
#         try:
#             floor, roi, theta = location
#             print(f"Using location data: Floor: {floor}, ROI: {roi}, Theta: {theta:.2f}")
            
#             position_key = f"{floor}_{roi}"
#             if position_key in motor_set_4.pick_position:
#                 motor_positions = motor_set_4.pick_position[position_key]
                
#                 try:
#                     time.sleep(1.5)
#                     solenoid.airpump_on()
#                     time.sleep(1)
                    
#                     for position in motor_positions:
#                         motor_set_4.move(position + [theta])
#                         time.sleep(1)
                    
#                     print("Moved to pick position")
#                     time.sleep(1)
#                 except PermissionError:
#                     print("Permission denied when trying to move motor. Please check hardware permissions.")
#                 except Exception as e:
#                     print(f"Error moving motor: {e}")
#             else:
#                 print(f"No motor position data for Floor: {floor}, ROI: {roi}")
#         except Exception as e:
#             print(f"Error in motor movement calculation: {e}")
#     else:
#         print("No location data available")
    
#     if not data_queue_QR.empty():
#         try:
#             classifi = parts[0]
#             print(classifi)

#             index_map = {
#                 'Option1': 0,
#                 'Option2': 1,
#                 'Option3': 2
#             }

#             classifi_index = index_map.get(user_option, 0)
#             if len(classifi) > classifi_index:
#                 classifi_letter = classifi[classifi_index]
#             else:
#                 print("Invalid classification data:", classifi)
#                 return

#             option_map = {
#                 'Option1': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
#                 'Option2': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
#                 'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
#             }

#             user_option = option_map.get(user_option, {})
#             criteria = user_option.get(classifi_letter)

#             if criteria:
#                 place_position = getattr(motor_set_4, criteria)
#                 place_angle = motor_set_4.place_position[place_position]
                
#                 safe_position_key = place_position.replace('A', 'AS').replace('B', 'BS')
#                 safe_angle = motor_set_4.safe_position[safe_position_key]

#                 try:
#                     motor_set_4.place(place_angle)
#                     motor_set_4.safe_place(safe_angle)
#                     print(f"Moving to {place_position}")
#                 except PermissionError:
#                     print("Permission denied when trying to move motor. Please check hardware permissions.")
#                 except Exception as e:
#                     print(f"Error in motor movement: {e}")
                
#                 for data in qr_data_list:
#                     if data['Classification'] == classifi and data['Position'] is None:
#                         data['Position'] = place_position
#                         break
#             else:
#                 print("Invalid option or classifi received", classifi_letter)
#         except Exception as e:
#             print(f"Error in QR data processing: {e}")

#     Motor_data = f"{place_position}/{'Motor'}/{'END'}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]}"
#     data_queue_Motor.put(Motor_data)
        
def motor_move(user_option, data_queue_QR):
    global current_step_A, current_step_B, current_step_pick, parts, place_position, Motor_data, location

    if location is None or not isinstance(location, tuple) or len(location) != 3:
        print(f"Error: Invalid location data. Current location: {location}")
        return

    floor, roi, theta = location

    if not all(isinstance(x, (int, float)) for x in (floor, roi, theta)):
        print(f"Error: Invalid location data types. Floor: {type(floor)}, ROI: {type(roi)}, Theta: {type(theta)}")
        return
    
    classifi = parts[0]
    print(f"Classification: {classifi}")

    index_map = {'Option1': 0, 'Option2': 1, 'Option3': 2}
    classifi_index = index_map.get(user_option, 0)
    if len(classifi) <= classifi_index:
        print("Invalid classification data:", classifi)
        return

    classifi_letter = classifi[classifi_index]

    option_map = {
        'Option1': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
        'Option2': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
        'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
    }

    criteria = option_map.get(user_option, {}).get(classifi_letter)
    pick_position_key = f"{floor}_{roi}"
    
    if not criteria:
        print("Invalid option or classifi received", classifi_letter)
        return

    pick_positions = motor_set_4.pick_position[pick_position_key]
    current_step_place = globals()[f'current_step_{classifi_letter}']
    place_position = getattr(motor_set_4, criteria)[current_step_place % len(getattr(motor_set_4, criteria))]
    place_angle = motor_set_4.place_position[place_position]
    
    safe_position_key = place_position.replace('A', 'AS').replace('B', 'BS')
    safe_angle = motor_set_4.safe_position[safe_position_key]

    try:
        for position in pick_positions:
            time.sleep(1.5)
            solenoid.airpump_on()
            time.sleep(1)
            print(f"Moving to {pick_positions}")
            motor_set_4.move(position + [theta])
            time.sleep(1)
        
        print(f"Moving to {place_position}")
        motor_set_4.place(place_angle)
        motor_set_4.safe_place(safe_angle)

        globals()[f'current_step_{classifi_letter}'] += 1

        for data in qr_data_list:
            if data['Classification'] == classifi and data['Position'] is None:
                data['Position'] = place_position
                break

    except PermissionError:
        print("Permission denied when trying to move motor. Please check hardware permissions.")
    except Exception as e:
        print(f"Error in motor movement: {e}")
        logging.error(f"Error in motor movement: {e}")
        logging.error(traceback.format_exc())

    Motor_data = f"{place_position}/{'Motor'}/{'END'}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]}"
    data_queue_Motor.put(Motor_data)


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
                        save_path = 'C:\\Users\\Lee\\Desktop\\QR_Data\\qr_data.xlsx'
                        
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

if __name__ == "__main__":
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()