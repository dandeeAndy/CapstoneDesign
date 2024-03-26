import socket
import threading
import cv2
import numpy as np
import time
import motor_set
from queue import Queue


print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host ='192.168.97.231'
UI_host = '192.168.97.215'
port = 1111

Vision_start_signal = True

lock = threading.Lock()

data_queue = Queue()

# ---------------------------------------------------------------
# Vision 서버를 만들고 UI 클라이언트의 접속을 기다림
# UI로 보낼 QR 데이터를 확보함
def server_func():
    
    global Vision_start_signal
    
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

    cap.release()
    cv2.destroyAllWindows()
    server_socket.close()

# ---------------------------------------------------------------
# Vision 클라이언트를 만들고 UI 서버에 접속함
# UI 서버에서 옵션 선택하면 그 옵션이 PC로 전달됨
# 옵션대로 모터가 움직임
def client_func():
    global Vision_start_signal

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((UI_host, port))
        print("Connected to UI host")
    except socket.error:
        print("Connection attempt failed. Retrying...")
        return


#LNB가 option 뒤에 print됨 해결??해야됨
    while True:
        try:
            # 큐에서 데이터 가져오기
            if not data_queue.empty():
                data = data_queue.get()
                classifi, _ = data.split('/')
                classifi = classifi.strip()
                print(classifi)

                with lock:
                    Vision_start_signal = True
                    print("Vision system activated for next operation")                            
            else:
                #print("Waiting for data...")  
                                 
            # UI 서버로부터 옵션 정보 받기
                motor_data_receive = client_socket.recv(1024)
                if not motor_data_receive:
                    print("No data received, closing connection")
                    break
                decoded_message = motor_data_receive.decode('utf-8').strip()
                print(f"Option Received: {decoded_message}")



            # 옵션에 따라 분류하고 모터 제어
            if decoded_message == 'Option1':
                    if classifi[0] == 'L':
                        motor_set.set_goal_position(motor_set.A1)
                        print("Moving to A1")
                    elif classifi[0] == 'F':
                        motor_set.set_goal_position(motor_set.B1)
                        print("Moving to B1")
                        
            elif decoded_message == 'Option2':
                    if classifi[1] == 'Y':
                        motor_set.set_goal_position(motor_set.A2)
                        print("Moving to A2")
                    elif classifi[1] == 'N':
                        motor_set.set_goal_position(motor_set.B2)
                        print("Moving to B2")
                        
            elif decoded_message == 'Option3':
                    if classifi[2] == 'A':
                        motor_set.set_goal_position(motor_set.A3)
                        print("Moving to A3")
                    elif classifi[2] == 'B':
                        motor_set.set_goal_position(motor_set.B3)
                        print("Moving to B3")
                        
            else:
                print("Invalid option received")

            with lock:
                Vision_start_signal = True
                print("Vision system activated for next operation")
                    
        #else:
            #print("Waiting for data...")

        except UnicodeDecodeError:
            print("Receiving incomplete data")
        except socket.error as e:
            print(f"Error during communication: {e}")
            break

    client_socket.close()


# ---------------------------------------------------------------
# 서버와 클라이언트를 멀티스레드로 
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
