import socket
import threading
from pyzbar import pyzbar
import cv2
import numpy as np
import time
from queue import Queue
import pandas as pd
from datetime import datetime

import motor_set_4
import solenoid
import mail

# ---------------------------------------------------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

# Vision_Motor_host = '192.168.95.231'
Vision_Motor_host = '192.168.163.251'

UI_host = '192.168.163.1'
# UI_host = '192.168.95.1'

# UI_host = '192.168.144.215'

port = 3333

QR_data = ''
Motor_data = ''
new_data_available = threading.Event()

Vision_start_signal = False
Option_select = False
Motor_start_signal = False
current_roi_index = 0

lock = threading.Lock()
data_queue_QR = Queue()
data_queue_Motor = Queue()
condition = threading.Condition()

current_step_A = 0
current_step_B = 0
current_step_pick = 0  # Pick step을 글로벌 변수로 관리

qr_data_list = []
last_qr_data = ''

# ---------------------------------------------------------------------------------------------------------------
# QR Code를 읽는 함수
def read_qr_code(client_socket):
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data

    cap = cv2.VideoCapture(1)
    
    rois = [
        {'x': 128, 'y': 55, 'w': 140, 'h': 140},
        {'x': 388, 'y': 55, 'w': 140, 'h': 140},
        {'x': 387, 'y': 224, 'w': 140, 'h': 140},
        {'x': 130, 'y': 220, 'w': 140, 'h': 140},
    ]

    total_rois = len(rois)
    last_detection_time = time.time()

    while Vision_start_signal:
        check, frame = cap.read()
        if not check:
            print("Failed to capture frame")
            break

        roi = rois[current_roi_index]
        x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
        
        if x < 0 or y < 0 or (x + w) > frame.shape[1] or (y + h) > frame.shape[0]:
            print("Invalid ROI settings:", roi)
            current_roi_index = (current_roi_index + 1) % total_rois
            continue
        
        roi_frame = frame[y:y+h, x:x+w]
        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        decoded_objects = pyzbar.decode(roi_frame, symbols=[pyzbar.ZBarSymbol.QRCODE])

        if decoded_objects:
            last_detection_time = time.time()
            with lock:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    if qr_data != last_qr_data:
                        last_qr_data = qr_data
                        parts = qr_data.split('/')
                        classifi = parts[0]
                        PackageNumber = parts[1]
                        Email = parts[2]
                        Destination = parts[3]
                        PhoneNumber = parts[4]
                        
                        recognition_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
                        qr_data_list.append({'Classification': classifi, 'Package Number': PackageNumber, 'Email': Email, 'Destination': Destination, 'PhoneNumber': PhoneNumber, 'Recognition time': recognition_time})
                        
                        QR_data = f"{qr_data}/{'Vision'}/{'STR'}/{recognition_time}"
                        
                        data_queue_QR.put(QR_data)

                        current_roi_index = (current_roi_index + 1) % total_rois
                        
                        Motor_start_signal = True
                        time.sleep(1)
                        
                        Vision_start_signal = False
                        time.sleep(1)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)  # 수정된 부분
        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if time.time() - last_detection_time > 10:  # 마지막 인식 후 10초가 지났는지 확인
            print("No QR code detected for 10 seconds. Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------------------------------------------------------------------------------------------------------
# 모터를 움직이는 함수
def motor_move(user_option, data_queue_QR):
    global current_step_A, current_step_B, current_step_pick, parts, place_position, Motor_data

    if not data_queue_QR.empty():
        classifi = parts[0]
        print(classifi)

        index_map = {
            'Option1': 0,  # 첫 번째 문자
            'Option2': 1,  # 두 번째 문자
            'Option3': 2   # 세 번째 문자
        }

        classifi_index = index_map.get(user_option, 0)  # 옵션에 따른 인덱스 가져오기, 기본값은 0
        if len(classifi) > classifi_index:
            classifi_letter = classifi[classifi_index]  # 인덱스에 해당하는 문자 가져오기
        else:
            print("Invalid classification data:", classifi)
            return

        # Mapping from option and first letter of classification to motor settings
        option_map = {
            'Option1': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
            'Option2': {'A': 'motor_positions_A', 'B': 'motor_positions_B'},
            'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
        }

        user_option = option_map.get(user_option, {})
        criteria = user_option.get(classifi_letter)

        if criteria:
            current_step_place = globals()[f'current_step_{classifi_letter}']
            
            pick_angle = motor_set_4.pick_position[f'V{current_step_pick % 12 + 1}']
            place_position = getattr(motor_set_4, criteria)[current_step_place % len(getattr(motor_set_4, criteria))]
            place_angle = motor_set_4.place_position[place_position]
            
            # safe_position을 올바르게 설정
            safe_position_key = place_position.replace('A', 'AS').replace('B', 'BS')
            safe_angle = motor_set_4.safe_position[safe_position_key]

            print(current_step_pick)
            
            motor_set_4.pick(pick_angle)
            motor_set_4.place(place_angle)
            motor_set_4.safe_place(safe_angle)
            
            print(f"Moving to {place_position}")
            globals()[f'current_step_{classifi_letter}'] += 1
            current_step_pick += 1  # current_step_pick을 증가시켜 순차적으로 이동
            
            # qr_data_list에 position 값 추가
            for data in qr_data_list:
                if data['Classification'] == classifi:
                    data['Position'] = place_position
                    break

        else:
            print("Invalid option or classifi received", classifi_letter)

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
                    print("Sent QR Data: ", QR_data)
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
 
                        df = df.dropna(subset=['Position'])
                        df_A = df[df['Position'].str.contains('A')]
                        df_B = df[df['Position'].str.contains('B')]
                        
                        with pd.ExcelWriter(save_path) as writer:
                            df_A.to_excel(writer, sheet_name='Sheet1', index=False)
                            df_B.to_excel(writer, sheet_name='Sheet2', index=False)
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
    global Option_select, Vision_start_signal, Motor_start_signal, option_data_received, cap
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((UI_host, port))
        print("Connected to UI host")
    except socket.error as e:
        print("Connection attempt failed. Retrying in 5 seconds...")
        time.sleep(5)
        return

    command_thread = threading.Thread(target=command_listener, args=(client_socket,))
    command_thread.start()

    try:
        while True:
            if Option_select and Vision_start_signal:
                read_qr_code(client_socket)

            elif not Vision_start_signal and Option_select and Motor_start_signal:
                print("motor_signal")
                motor_move(option_data_received, data_queue_QR)
                Motor_start_signal = False  # 한 번 움직인 후 신호를 다시 False로 설정
                Vision_start_signal = True  # Vision 시스템 다시 시작

                print("Vision is ON")
                time.sleep(0.5)

            else:
                time.sleep(1)

    finally:
        client_socket.close()
        command_thread.join()

# ---------------------------------------------------------------------------------------------------------------
# 서버와 클라이언트를 멀티스레드로
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
