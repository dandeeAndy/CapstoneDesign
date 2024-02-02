import cv2
import numpy as np


def qr_code_decode():
    cap = cv2.VideoCapture(1)
    qr_code_detector = cv2.QRCodeDetector()
    
    last_data = [None, None, None, None]

    rois = {
        'roi1': {'x': 200, 'y': 80, 'w': 100, 'h': 100},       # 좌측 상단
        'roi2': {'x': 200, 'y': 300, 'w': 100, 'h': 100},      # 좌측 하단
        'roi3': {'x': 400, 'y': 300, 'w': 100, 'h': 100},      # 우측 하단
        'roi4': {'x': 400, 'y': 80, 'w': 100, 'h': 100},       # 우측 상단
    }

    check, frame = cap.read()
    if not check:
        print("Cannot read video")
        return

    current_roi = 0
    while True:
        check, frame = cap.read()
        
        if check:
            roi_names = list(rois.keys())
            roi = rois[roi_names[current_roi]]
            x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
            roi_frame = frame[y:y+h, x:x+w]

            data, points, _ = qr_code_detector.detectAndDecode(roi_frame)

            if data != '' and data != last_data[current_roi]: 
                last_data[current_roi] = data
                print(f'{roi_names[current_roi]}: {data}')   
                current_roi = (current_roi + 1) % len(rois)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow("Image", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

qr_code_decode()
