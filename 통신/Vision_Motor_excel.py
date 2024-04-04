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

Vision_Motor_host ='192.168.193.231'
UI_host = '192.168.193.215'
port = 1111

Vision_start_signal = False
Option_select = False

lock = threading.Lock()

data_queue = Queue()

current_step_L = 0
current_step_F = 0

current_step_Y = 0
current_step_N = 0

current_step_A = 0
current_step_B = 0

qr_data_list = []

# ---------------------------------------------------------------------------------------------------------------
# Vision 서버를 만들고 UI 클라이언트의 접속을 기다림
# UI로 보낼 QR 데이터를 확보함
def server_func():
    
    global Vision_start_signal,Option_select
    global decoded_message
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((Vision_Motor_host, port))  
    server_socket.listen()
    print('Vision_server waitting for conneciton....')
    
    client_soc, addr = server_socket.accept()
    print('Vision_server connect')

    cap = cv2.VideoCapture(1)
    qr_code_detector = cv2.QRCodeDetector()

    rois = [
        {'x': 200, 'y': 60, 'w': 125, 'h': 125},
        {'x': 200, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 300, 'w': 125, 'h': 125},
        {'x': 330, 'y': 50, 'w': 125, 'h': 125},
    ]

    last_data = [None] * len(rois)  # 각 ROI에서 인식된 마지막 QR 코드 데이터 저장
    current_roi_index = 0  # 현재 처리 중인 ROI의 인덱스

    while True:
        check, frame = cap.read()
        if not check:
            print("Failed to capture frame")
            break

        if Option_select:
            if Vision_start_signal:
                roi = rois[current_roi_index]
                x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
                roi_frame = frame[y:y+h, x:x+w]

                # 엣지 검출 추가
                gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
                blurred_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)
                edges = cv2.Canny(blurred_roi, 50, 150)

          

                data, bbox, _ = qr_code_detector.detectAndDecode(gray_roi)  # 엣지 검출 대신 gray_roi 사용

                if bbox is not None and data != '':
                    last_data[current_roi_index] = data  # 현재 ROI의 데이터 업데이트
                    #print(f'ROI {current_roi_index+1}: {data}')  # 데이터 출력
                    data_queue.put(data)
                    parts = data.split('/')
                    classifi = parts[0]
                    Departuredate = parts[1]
                    Arrivaldate = parts[2]
                    Destination = parts[3]
                    Item = parts[4]
                    
                    ##어떤옵션을 선택한지
                    
                    qr_data_list.append({'Classification': classifi,'Departure Date':Departuredate,'Arrival Date': Arrivaldate,'Destination': Destination,'Item': Item, 'Recognition time': pd.Timestamp.now()})
                    
                    # UI로 QR Data 전송
                    try:
                        client_soc.sendall(data.encode('utf-8'))
                    except socket.error as e:
                        print("Error sending data:", e)
                        break
                    
                    current_roi_index = (current_roi_index + 1) % len(rois)  # 다음 ROI
                    Vision_start_signal = False 

                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)  # ROI 영역에 사각형 그리기
                cv2.imshow("Edges", edges)  # 엣지 검출 이미지 출력
                cv2.imshow("Frame", frame)  # 원본 프레임 출력
            
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q'를 누르면 종료
                break
    if qr_data_list:
        df = pd.DataFrame(qr_data_list)
        df.to_excel('C:\\Users\\Shawn\\Lee\\Robot\\Capstone\\Perfect\\QR_Data\\qr_data.xlsx', index=False)
        print("QR 데이터가 엑셀 파일로 저장되었습니다.")
        
    cap.release()
    cv2.destroyAllWindows()
    server_socket.close()

# ---------------------------------------------------------------------------------------------------------------
def motor_option(option, data_queue):
    global current_step_L, current_step_F, current_step_Y, current_step_N, current_step_A, current_step_B

    if not data_queue.empty():
        data = data_queue.get()
        parts = data.split('/')
        classifi = parts[0]
        
        print(classifi)

        # Mapping from option and first letter of classification to motor settings
        option_map = {
            'Option1': {'L': 'motor_positions_L', 'F': 'motor_positions_F'},
            'Option2': {'Y': 'motor_positions_Y', 'N': 'motor_positions_N'},
            'Option3': {'A': 'motor_positions_A', 'B': 'motor_positions_B'}
        }

        motor_positions = option_map.get(option, {})
        motor_key = motor_positions.get(classifi[0])

        if motor_key:
            current_step = globals()[f'current_step_{classifi[0]}']
            identifier = getattr(motor_set_2, motor_key)[current_step % len(getattr(motor_set_2, motor_key))]
            position = motor_set_2.position_mapping[identifier]
            print(f"Moving to {identifier}")
            motor_set_2.move_to_position(position)
            globals()[f'current_step_{classifi[0]}'] += 1
            
        else:
            print("Invalid option or classifi received")

            
# Vision 클라이언트를 만들고 UI 서버에 접속함
# UI 서버에서 옵션 선택하면 그 옵션이 PC로 전달됨
# 옵션대로 모터가 움직임
# ---------------------------------------------------------------------------------------------------------------
def client_func():
    global Vision_start_signal, Option_select
    global decoded_message

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((UI_host, port))
        print("Connected to UI host")
    except socket.error:
        print("Connection attempt failed. Retrying...")
        return

    while True:
        try:
            motor_data_receive = client_socket.recv(1024)
            if not motor_data_receive:
                print("No data received, closing connection")
                break
            
            decoded_message = motor_data_receive.decode('utf-8').strip()
            print(f"Option Received: {decoded_message}")

            motor_option(decoded_message, data_queue)

            with lock:
                Option_select = True
                Vision_start_signal = True
                print("Vision system activated for next operation")

        except UnicodeDecodeError:
            print("Receiving incomplete data")
        except socket.error as e:
            print(f"Error during communication: {e}")
            break

    client_socket.close()

# ---------------------------------------------------------------------------------------------------------------
# 서버와 클라이언트를 멀티스레드로 

if __name__ == "__main__":
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()
