import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import UI_set


from queue import Queue
import socket
import threading
import time

# -----------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host ='192.168.95.231'
#Vision_Motor_host ='192.168.144.231'

UI_host = '192.168.95.1'
#UI_host = '192.168.144.1'

port = 1111

lock = threading.Lock()
client_soc = None  # 전역 변수로 선언하여 모든 함수에서 접근 가능하게 함
selected_option = None
last_sent_option = None

# -----------------------------------------------------------------------
def server_func():
    global client_soc, selected_option, last_sent_option
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))
    server_socket.listen()
    print('UI server waiting for connection....')
    
    client_soc, addr = server_socket.accept()
    print('UI server connected')
    
    while True:
        selected_option = UI_set.get_selected_option()
        # selected_option = UI_set_1.get_selected_option()
        if selected_option is not None and selected_option != last_sent_option:
            try:
                client_soc.sendall((selected_option + '\n').encode('utf-8'))
                last_sent_option = selected_option
                selected_option = None  # 메시지 전송 후 변수 초기화
            except socket.error as e:
                print("Error sending data:", e)
                break
            
# -----------------------------------------------------------------------
def client_func():
    global client_soc
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    qr_data_receive = ""
    
    while True:
        try:
            client_socket.connect((Vision_Motor_host, port))
            print("Connected to Vision Motor host.")
            break
        except socket.error:
            print("Connection attempt failed. Retrying...")
            time.sleep(5)  
            continue

    while True:
        try:
            data = client_socket.recv(1024)
            print("Received data:", data)  # 데이터 수신 로그 추가
            if not data:
                print("No data received. Exiting.")
                break
            qr_data_receive = data.decode('utf-8')
            print("Received data:", qr_data_receive)  # 데이터 수신 로그 추가
        except socket.error as e:
            print("Error receiving data: ", e)
            break
        
    if qr_data_receive:  # 데이터가 비어있지 않은지 확인
            print("Received data:", qr_data_receive)  # 데이터 수신 로그 추가
            parts = qr_data_receive.split('/')
            if parts:  # parts 리스트가 비어있지 않은지 확인
                classifi = parts[0]
                if len(classifi) > 0:  # classifi 문자열에 적어도 하나의 문자가 있는지 확인
                    if classifi[0] in ['L']:
                        widgets = [UI_set.MainWindow.code_widget_1, UI_set.MainWindow.departure_widget_1, UI_set.MainWindow.arrival_widget_1, UI_set.MainWindow.region_widget_1, UI_set.MainWindow.product_widget_1]
                        # widgets = [UI_set_1.MainWindow.code_widget_1, UI_set_1.MainWindow.departure_widget_1, UI_set_1.MainWindow.arrival_widget_1, UI_set_1.MainWindow.region_widget_1, UI_set_1.MainWindow.product_widget_1]
                    elif classifi[0] in ['F']:
                        widgets = [UI_set.MainWindow.code_widget_2, UI_set.MainWindow.departure_widget_2, UI_set.MainWindow.arrival_widget_2, UI_set.MainWindow.region_widget_2, UI_set.MainWindow.product_widget_2]
                        # widgets = [UI_set_1.MainWindow.code_widget_2, UI_set_1.MainWindow.departure_widget_2, UI_set_1.MainWindow.arrival_widget_2, UI_set_1.MainWindow.region_widget_2, UI_set_1.MainWindow.product_widget_2]
                    for widget, part in zip(widgets, parts):
                        widget.addItem(part)

# -----------------------------------------------------------------------
# def UI_func():
#     app = QApplication(sys.argv)
#     font = QFont("NanumSquare", 9)
#     app.setFont(font)
#     mainWin = UI_set.MainWindow()
#     # mainWin = UI_set_1.MainWindow()
#     mainWin.showMaximized()
#     mainWin.show()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     server_thread = threading.Thread(target=server_func)
#     client_thread = threading.Thread(target=client_func)
#     UI_thread = threading.Thread(target=UI_func)

#     server_thread.start()
#     client_thread.start()
#     UI_thread.start()

#     server_thread.join()
#     client_thread.join()
#     UI_thread.join()
    
# -----------------------------------------------------------------------    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    mainWin = UI_set.MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)
        
    server_thread.start()
    client_thread.start()
    
    sys.exit(app.exec_())