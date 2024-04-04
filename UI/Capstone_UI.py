import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import UI_set
from UI_set import OptionButton
from UI_set.OptionButton import opt


from queue import Queue
import socket
import threading
import time

# -----------------------------------------------------------------------
print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host = '192.168.97.231'
UI_host = '192.168.1.210'

port = 1111

lock = threading.Lock()
client_soc = None  # 전역 변수로 선언하여 모든 함수에서 접근 가능하게 함

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
            UI_set.MainWindow.first_details_list_widget.addItem(qr_data_receive)
        
        elif classifi[0] == 'F' or 'N' or 'B':
            UI_set.MainWindow.second_details_list_widget.addItem(qr_data_receive)
        
# -----------------------------------------------------------------------
def server_func():
    global client_soc
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))  
    server_socket.listen()
    print('UI server waiting for connection....')
    
    client_soc, addr = server_socket.accept()
    print('UI server connected')
    
def opt_callback(selected_opt):
    print(f"Selected option: {selected_opt}")
    
    OptionButton.option_sel()
    
    # try:
    #     client_soc.sendall(OptionButton.opt.encode('utf-8'))
    # except socket.error as e:
    #     print("Error sending data:", e)
    #     break

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
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)
UI_thread = threading.Thread(target=UI_func)

server_thread.start()
client_thread.start()
UI_thread.start()

server_thread.join()
client_thread.join()
UI_thread.join()