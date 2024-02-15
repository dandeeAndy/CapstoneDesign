import cv2
import numpy as np

def qr_code_decode_with_edge_detection():
    cap = cv2.VideoCapture(0)  # 비디오 캡처를 위한 객체 생성
    qr_code_detector = cv2.QRCodeDetector()  # QR 코드 검출을 위한 객체 생성

    rois = {
        'roi1': {'x': 200, 'y': 60, 'w': 125, 'h': 125},  #좌측 상단  x,y ROI의 좌측상단모서리좌표
        'roi2': {'x': 200, 'y': 300, 'w': 125, 'h': 125},  #좌측 하단  w,h 너비와 높이
        'roi3': {'x': 330, 'y': 300, 'w': 125, 'h': 125},  #우측 하단
        'roi4': {'x': 330, 'y': 50, 'w': 125, 'h': 125},  #우측 상단
    }  #딕셔너리는 {key: value} 형태로 구성되는 데이터 구조

    last_data = [None] * len(rois)  # last_data 리스트를 None 값으로 초기화하고, 이 리스트를 각 ROI에 대한 데이터를 저장
    # 초기화된 리스트는 추후에 QR코드의 데이터가 수집될 때마다 해당 ROI의 인덱스에 맞게 업데이트됩

    check, frame = cap.read()  # 비디오 프레임 읽기
    if not check:
        print("Cannot read video")
        return

    current_roi_number = 0  # 현재 처리 중인 ROI의 인덱스

    while True:
        check, frame = cap.read()  # 비디오 프레임 읽기

        if check:
            roi_list = list(rois.keys())  # ROI의 키(이름)를 리스트로 변환
            roi = rois[roi_list[current_roi_number]]  # 현재 처리 중인 ROI 선택
            x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']  # ROI의 좌표와 크기 추출
            roi_frame = frame[y:y + h, x:x + w]  #원본 프레임에서 ROI 영역 추출

            #엣지 검출을 위한 코드 추가
            gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)  #grayscale로 변환
            blurred_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)  # 가우시안 블러 적용
            edges = cv2.Canny(blurred_roi, 50, 150)  #엣지 검출

            data, points, _ = qr_code_detector.detectAndDecode(gray_roi)  #gray_roi에서 QR 코드 검출 및 디코드

            if points is not None and len(points) > 0:  # 유효한 QR 코드가 검출되었는지 확인
                if data != '':  # 디코드된 데이터가 비어있지 않은 경우
                    last_data[current_roi_number] = data  # 현재 ROI의 데이터 업데이트
                    print(f'{roi_list[current_roi_number]}: {data}')  # 데이터 출력
                    current_roi_number = (current_roi_number + 1) % len(rois)  # 다음 ROI로 인덱스 업데이트

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)  # ROI 영역에 사각형 그리기, 2는 ROI의 두께
            cv2.imshow("Edges", gray_roi)  # 엣지 이미지 출력
            cv2.imshow("Image", frame)  # 프레임 출력

        if cv2.waitKey(1) & 0xFF == ord('q'):  #'q' 키를 누르면 종료
            break

    cap.release()  # 비디오 캡처 객체 해제
    cv2.destroyAllWindows()  # 창 닫기

qr_code_decode_with_edge_detection()





