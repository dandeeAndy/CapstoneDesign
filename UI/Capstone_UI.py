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
# Vision_Motor_host ='192.168.144.231'
UI_host = '192.168.95.1'
# UI_host = '192.168.144.1'

port = 1111

lock = threading.Lock()
client_soc = None
selected_option = None
last_sent_option = None
pause_clicked = None
last_sent_pause = None

# -----------------------------------------------------------------------
def client_func():
    global client_soc, selected_option
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
            data = client_socket.recv(1024)
            if not data:
                print("No data received. Connection might be closed.")
                break
            qr_data_receive = data.decode('utf-8')
            print("Received data:", qr_data_receive)
        except socket.error as e:
            print("Error receiving data: ", e)
            break   # 소켓 에러시
        
        widgets = []
        if qr_data_receive:
            print("Received data:", qr_data_receive)
            parts = qr_data_receive.split('/')
            print(parts)
            if parts:
                classifi = parts[0]
                print(classifi)
                
                if selected_option == 'Option1':
                    print("Option1")
                    if classifi[0] in ['L']:
                        widgets = widgets1
                    elif classifi[0] in ['F']:
                        widgets = widgets2
                
                elif selected_option == 'Option2':
                    print("Option2")
                    if classifi[1] in ['Y']:
                        widgets = widgets1
                    elif classifi[1] in ['N']:
                        widgets = widgets2
                
                elif selected_option == 'Option3':
                    print("Option3")
                    if classifi[0] in ['A']:
                        widgets = widgets1
                    elif classifi[0] in ['B']:
                        widgets = widgets2
                
                if widgets:  # widgets 리스트가 비어있지 않은 경우에만 실행
                    for widget, part in zip(widgets, parts):
                        widget.addItem(part)
                    widgets = None  # 메모리
                    print("widget reset")
# -----------------------------------------------------------------------
def server_func():
    global client_soc, selected_option, last_sent_option
    global pause_clicked, last_sent_pause
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))
    server_socket.listen()
    print('UI server waiting for connection....')
    
    client_soc, addr = server_socket.accept()
    print('UI server connected')
    
    while True:
        selected_option = UI_set.get_selected_option()
        pause_clicked = UI_set.get_pause_clicked()
        
        if selected_option is not None and selected_option != last_sent_option:
            try:
                client_soc.sendall((selected_option + '\n').encode('utf-8'))
                last_sent_option = selected_option
                selected_option = None  # 메시지 전송 후 변수 초기화
            except socket.error as e:
                print("Error sending data:", e)
                break
            
        if pause_clicked is not None and pause_clicked != last_sent_pause:
            try:
                client_soc.sendall((pause_clicked + '\n').encode('utf-8'))
                last_sent_pause = pause_clicked
                print("Pause clicked:", last_sent_pause)
                pause_clicked = None
            except socket.error as e:
                print("Error sending data:", e)
                break

# # -----------------------------------------------------------------------
# def UI_func():
#     app = QApplication(sys.argv)
#     font = QFont("NanumSquare", 9)
#     app.setFont(font)
#     mainWin = UI_set.MainWindow()
#     mainWin.showMaximized()
#     mainWin.show()
#     sys.exit(app.exec_())
    
# # -----------------------------------------------------------------------
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
    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    
    main_window_instance = UI_set.MainWindow()
    widgets1 = [main_window_instance.code_widget_1, 
        main_window_instance.departure_widget_1, 
        main_window_instance.arrival_widget_1, 
        main_window_instance.region_widget_1, 
        main_window_instance.product_widget_1]
    widgets2 = [main_window_instance.code_widget_2, 
        main_window_instance.departure_widget_2, 
        main_window_instance.arrival_widget_2, 
        main_window_instance.region_widget_2, 
        main_window_instance.product_widget_2]
    
    mainWin = UI_set.MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)

    server_thread.start()
    client_thread.start()
    
    sys.exit(app.exec_())