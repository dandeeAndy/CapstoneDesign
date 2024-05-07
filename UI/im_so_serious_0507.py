import socket
import threading
import cv2
import numpy as np
import time
from queue import Queue
import pandas as pd
from datetime import datetime

import motor_set_2

# ---------------------------------------------------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host ='192.168.95.231'
#Vision_Motor_host ='192.168.144.231'

#UI_host = '192.168.95.215'
UI_host = '192.168.95.1'

# UI_host = '192.168.144.215'
#I_host = '192.168.144.1'

port = 1111

QR_data = None
new_data_available = threading.Event() 

Vision_start_signal = False
Option_select = False
current_roi_index = 0

lock = threading.Lock()
data_queue = Queue()
condition = threading.Condition()

current_step_L = 0
current_step_F = 0

current_step_Y = 0
current_step_N = 0

current_step_A = 0
current_step_B = 0

qr_data_list = []

# ---------------------------------------------------------------------------------------------------------------
# QR Code를 읽는 함수
def read_qr_code(client_soc):
    
    global QR_data, Vision_start_signal, parts, current_roi_index

    # 여기서 모든 필요한 객체를 생성합니다.
    cap = cv2.VideoCapture(1)
    qr_code_detector = cv2.QRCodeDetector()

    rois = [
        {'x': 200, 'y': 60, 'w': 125, 'h': 125},
        {'x': 200, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 50, 'w': 125, 'h': 125},
    ]

    #last_data = [None] * len(rois)
    total_rois = len(rois)

    #while Option_select and Vision_start_signal:
    while Vision_start_signal:
        check, frame = cap.read()
        if not check:
            print("Failed to capture frame")
            break

        roi = rois[current_roi_index]
        x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
        roi_frame = frame[y:y+h, x:x+w]

        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        blurred_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)
        edges = cv2.Canny(blurred_roi, 50, 150)

        QR_data, detect, _ = qr_code_detector.detectAndDecode(gray_roi)

        if detect is not None and QR_data != '':
            with lock:
                data_queue.put(QR_data)
                parts = QR_data.split('/')
                classifi = parts[0]
                Departuredate = parts[1]
                Arrivaldate = parts[2]
                Destination = parts[3]
                Item = parts[4]

                qr_data_list.append({'Classification': classifi, 'Departure Date': Departuredate, 'Arrival Date': Arrivaldate, 'Destination': Destination, 'Item': Item, 'Recognition time': pd.Timestamp.now()})

                current_roi_index = (current_roi_index + 1) % total_rois

                Vision_start_signal = False



        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.imshow("Edges", edges)
        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
# ---------------------------------------------------------------------------------------------------------------
# 모텨를 움직이는 함수
def motor_move(option, data_queue):
    global current_step_L, current_step_F, current_step_Y, current_step_N, current_step_A, current_step_B, parts

    if not data_queue.empty():
        classifi = parts[0]
        print(classifi)
        
        index_map = {
            'Option1': 0,  # 첫 번째 문자
            'Option2': 1,  # 두 번째 문자
            'Option3': 2   # 세 번째 문자
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
            identifier = getattr(motor_set_2, motor_key)[current_step % len(getattr(motor_set_2, motor_key))]
            position = motor_set_2.position_mapping[identifier]
            motor_set_2.move_to_position(position)
            print(f"Moving to {identifier}")
            globals()[f'current_step_{classifi_letter}'] += 1
        else:
            print("Invalid option or classifi received", classifi_letter)
            
# ---------------------------------------------------------------------------------------------------------------
# QR 정보를 UI로 보냄
def server_func():
    global QR_data,Option_select
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((Vision_Motor_host, port))
    server_socket.listen()
    print('Vision_server waiting for connection...')
    
    client_soc, addr = server_socket.accept()
    #print('Vision_server connected to', addr)

    try:
        while True:
            if Option_select:
                if QR_data:
                    client_soc.sendall(QR_data.encode('utf-8'))
                    print("Sent QR Data: ", QR_data)
                    time.sleep(2)
                else:
                    time.sleep(2)  # 적절한 대기 시간 추가
                    print("No QR Data to send")
                time.sleep(1)  # 적절한 대기 시간 추가
                
    except Exception as e:
        print("Error sending data:", e)
    finally:
        client_soc.close()
        server_socket.close()

# ---------------------------------------------------------------------------------------------------------------
# UI에서 Option 정보 받으면 Vision 작동 시켜서 모터 움직임
def client_func():
    global Option_select, Vision_start_signal
    
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((UI_host, port))
            print("Connected to UI host")
            break
        except socket.error as e:
            print("Connection attempt failed. Retrying in 5 seconds...")
            time.sleep(5)
    
    while not Option_select:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                option_data_receive = data.strip()
                print(f"Option Received: {option_data_receive}")
                
                Option_select = True
                
                Vision_start_signal = True
        
        except socket.error as e:
            print(f"Error during communication: {e}")
            break
    
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received data: {data}")
                data_queue.put(data)
                
        except socket.error as e:
            print(f"Error receiving data: {e}")
            break
                
    while Option_select:
        if Vision_start_signal:
            
            read_qr_code(client_socket)
        
        if Vision_start_signal == False:
            
            motor_move(option_data_receive, data_queue)
            time.sleep(1)
            
            print("Vision system is ready to receive new data.")
            time.sleep(1)
            
            print("Vision is ON")
            time.sleep(0.5)
            
            Vision_start_signal = True
            
        if data == 'pause':
            Option_select = False
            print('sklfsdk')
            
        else:
            print("No data received, closing connection")
            break
        
    client_socket.close()    
    
# ---------------------------------------------------------------------------------------------------------------
# 서버와 클라이언트를 멀티스레드로 
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()