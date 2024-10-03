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

qr_data_list = []
last_qr_data = ''
current_roi_index = 0

Vision_start_signal = True

def read_qr_code():
    global QR_data, Vision_start_signal, Motor_start_signal, parts, current_roi_index, last_qr_data

    cap = cv2.VideoCapture(1)

    rois = [
        {'x': 128, 'y': 55, 'w': 140, 'h': 140},
        {'x': 130, 'y': 220, 'w': 140, 'h': 140},
        {'x': 387, 'y': 224, 'w': 140, 'h': 140},
        {'x': 388, 'y': 55, 'w': 140, 'h': 140},
    ]

    while Vision_start_signal:
        check, frame = cap.read()
        if not check:
            print("Failed to capture frame")
            break

        all_decoded_objects = []
        for roi in rois:
            x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
            
            if x < 0 or y < 0 or (x + w) > frame.shape[1] or (y + h) > frame.shape[0]:
                print("Invalid ROI settings:", roi)
                continue
            
            roi_frame = frame[y:y+h, x:x+w]
            gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

            decoded_objects = pyzbar.decode(roi_frame, symbols=[pyzbar.ZBarSymbol.QRCODE])
            all_decoded_objects.extend(decoded_objects)

            # ROI를 프레임에 표시
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)

        if all_decoded_objects:
            with lock:
                for obj in all_decoded_objects:
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
                        qr_data_list.append({'Classification': classifi, 'Departure Date': Departuredate, 'Arrival Date': Arrivaldate, 'Destination': Destination, 'Item': Item, 'Recognition time': recognition_time})
                        
                        QR_data = f"{qr_data}/{{'Vision'}}/{{'STR'}}/{recognition_time}"
                        
                        data_queue_QR.put(QR_data)
                        
                        Motor_start_signal = True
                        time.sleep(1)
                        Vision_start_signal = True
                        time.sleep(1)

        cv2.imshow("Read_QR_CODE", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 실행
read_qr_code()
