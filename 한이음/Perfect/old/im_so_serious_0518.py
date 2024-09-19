import socket
import threading
from pyzbar import pyzbar
import cv2
import numpy as np
import time
from queue import Queue
import pandas as pd
from datetime import datetime

import motor_set_3
import solenoid
import mail

# ---------------------------------------------------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host = '192.168.95.231'
# Vision_Motor_host = '192.168.144.231'

UI_host = '192.168.95.215'
# UI_host = '192.168.95.1'

# UI_host = '192.168.144.215'
# I_host = '192.168.144.1'

port = 1111

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

current_step_L = 0
current_step_F = 0
current_step_Y = 0
current_step_N = 0
current_step_A = 0
current_step_B = 0

qr_data_list = []
last_qr_data = ''

# ---------------------------------------------------------------------------------------------------------------
# QR Code를 읽는 함수
def read_qr_code(client_soc):
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data

    cap = cv2.VideoCapture(1)

    rois = [
        {'x': 200, 'y': 60, 'w': 125, 'h': 125},
        {'x': 200, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 50, 'w': 125, 'h': 125},
    ]

    total_rois = len(rois)

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

        roi_frame = frame[y:y + h, x:x + w]
        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        decoded_objects = pyzbar.decode(gray_roi)

        if decoded_objects:
            with lock:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    if qr_data != last_qr_data:
                        last_qr_data = qr_data
                        parts = qr_data.split('/')
                        classifi = parts[0]
                        Departuredate = parts[1]
                        Arrivaldate = parts[2]
                        Destination = parts[3]
                        Item = parts[4]

                        recognition_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]
                        qr_data_list.append({'Classification': classifi, 'Email': Departuredate, 'Arrival Date': Arrivaldate, 'Destination': Destination, 'Item': Item, 'Recognition time': recognition_time})

                        QR_data = f"{qr_data}/{'Vision'}/{'STR'}/{recognition_time}"

                        data_queue_QR.put(QR_data)

                        current_roi_index = (current_roi_index + 1) % total_rois

                        Motor_start_signal = True
                        Vision_start_signal = False
                        print("MOTOR_SIGNAL")
                        time.sleep(1)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------------------------------------------------------------------------------------------------------
# 모터를 움직이는 함수
def motor_move(option, data_queue_QR):
    global current_step_L, current_step_F, current_step_Y, current_step_N, current_step_A, current_step_B, parts, position, Motor_data

    if not data_queue_QR.empty():
        classifi = parts[0]
        print(classifi)

        index_map = {
            'Option1': 0,  # 첫 번째 문자
            'Option2': 1,  # 두 번째 문자
            'Option3': 2  # 세 번째 문자
        }

        classifi_index = index_map.get(option, 0)  # 옵션에 따른 인덱스 가져오기, 기본값은 0
        if len(classifi) > classifi_index:
            classifi_letter = classifi[classifi_index]  # 인덱스에 해당하는 문자 가져오기
        else:
            print("Invalid classification data:", classifi)
            return

        # Mapping from option and first letter of classification to motor settings
        option_map = {
            'Option1': {'L': 'motor_positions_L', 'F': 'motor_positions_F'},
            'Option2': {'Y': 'motor_positions_Y', 'N': 'motor_positions_N'},
            'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
        }

        motor_positions = option_map.get(option, {})
        motor_key = motor_positions.get(classifi_letter)

        if motor_key:
            current_step = globals()[f'current_step_{classifi_letter}']
            position = getattr(motor_set_3, motor_key)[current_step % len(getattr(motor_set_3, motor_key))]
            position_angle = motor_set_3.place_position[position]
            motor_set_3.move_to_position(position_angle)
            print(f"Moving to {position}")
            globals()[f'current_step_{classifi_letter}'] += 1

            # qr_data_list에 position 값 추가
            for data in qr_data_list:
                if data['Classification'] == classifi:
                    data['Position'] = position
                    break

        else:
            print("Invalid option or classifi received", classifi_letter)

    Motor_data = f"{position}/{'Motor'}/{'END'}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5]}"
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
                    time.sleep(2)

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
                        save_path = 'C:\\Users\\Shawn\\Lee\\Robot\\Capstone\\Perfect\\QR_Data\\qr_data.xlsx'
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
