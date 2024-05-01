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
UI_host = '192.168.95.1'

port = 1111

lock = threading.Lock()
client_soc = None  # 전역 변수로 선언하여 모든 함수에서 접근 가능하게 함
selected_option = None

# -----------------------------------------------------------------------
def client_func():
    global client_soc
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            qr_data_receive = client_socket.recv(1024)
            qr_data_receive.decode('utf-8')
        except socket.error as e:
            print("Error receiving data: ", e)
            break
        
        parts = qr_data_receive.split('/')
        classifi = parts[0]
        
        if classifi[0] == 'L' or 'Y' or 'A':
            widgets = [UI_set.MainWindow.code_widget_1, UI_set.MainWindow.departure_widget_1, UI_set.MainWindow.arrival_widget_1, UI_set.MainWindow.region_widget_1, UI_set.MainWindow.product_widget_1]
        
        elif classifi[0] == 'F' or 'N' or 'B':
            widgets = [UI_set.MainWindow.code_widget_2, UI_set.MainWindow.departure_widget_2, UI_set.MainWindow.arrival_widget_2, UI_set.MainWindow.region_widget_2, UI_set.MainWindow.product_widget_2]
        
        for widget, part in zip(widgets, parts):
            widget.addItem(part)
        
# -----------------------------------------------------------------------
def server_func():
    global client_soc, selected_option
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))
    server_socket.listen()
    print('UI server waiting for connection....')
    
    client_soc, addr = server_socket.accept()
    print('UI server connected')
    
    while True:
        if selected_option is not None:
            try:
                client_soc.sendall(selected_option.encode('utf-8'))
                selected_option = None  # 메시지 전송 후 변수 초기화
            except socket.error as e:
                print("Error sending data:", e)
                break

# -----------------------------------------------------------------------
def UI_func():
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    mainWin = UI_set.MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())
    
# -----------------------------------------------------------------------
if __name__ == '__main__':
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)
    UI_thread = threading.Thread(target=UI_func)

    server_thread.start()
    client_thread.start()
    UI_thread.start()

    server_thread.join()
    client_thread.join()
    UI_thread.join()