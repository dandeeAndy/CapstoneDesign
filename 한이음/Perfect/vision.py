import os
import cv2
import time
import threading
import pandas as pd
from queue import Queue
from pyzbar import pyzbar

lock = threading.Lock()
data_queue_QR = Queue()
data_queue_Motor = Queue()

current_step_L = 0
current_step_F = 0
current_step_Y = 0
current_step_N = 0
current_step_A = 0
current_step_B = 0
current_roi_index = 0

qr_data_list = []
last_qr_data = ''
processed_qr_data = set()  # 이미 처리된 QR 코드 데이터를 저장하는 집합

Vision_start_signal = True
Motor_start_signal = False

def read_qr_code(client_socket=None):
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data

    cap = cv2.VideoCapture(1)

    rois = [
        {'x': 128, 'y': 55, 'w': 140, 'h': 140},
        {'x': 388, 'y': 55, 'w': 140, 'h': 140},
        {'x': 387, 'y': 224, 'w': 140, 'h': 140},
        {'x': 100, 'y': 220, 'w': 140, 'h': 140},
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
                        qr_data_dict = {
                            'Classification': classifi,
                            'Package Number': PackageNumber,
                            'Email': Email,
                            'Destination': Destination,
                            'PhoneNumber': PhoneNumber,
                            'Recognition time': recognition_time
                        }
                        qr_data_list.append(qr_data_dict)
                        
                        QR_data = f"{qr_data}/{'Vision'}/{'STR'}/{recognition_time}"
                        
                        data_queue_QR.put(QR_data)

                        # 새롭게 인식된 데이터 출력
                        print("\n새롭게 인식된 QR 코드 데이터:")
                        for key, value in qr_data_dict.items():
                            print(f"{key}: {value}")

                        Motor_start_signal = True
                        time.sleep(2)
                        # Vision_start_signal을 False로 설정하는 부분 제거
                        # cv2.destroyAllWindows()를 제거하여 루프가 계속 되도록 설정
                        #time.sleep(2)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.imshow("QR_Code_Read", frame)

        # ROI 인덱스를 순차적으로 변경
        current_roi_index = (current_roi_index + 1) % total_rois
        
        # 디버깅을 위해 현재 ROI 인덱스 출력
        #print(f"Current ROI Index: {current_roi_index}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if time.time() - last_detection_time > 10:  # 마지막 인식 후 10초가 지났는지 확인
            print("No QR code detected for 10 seconds. Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

# 실행
read_qr_code()
