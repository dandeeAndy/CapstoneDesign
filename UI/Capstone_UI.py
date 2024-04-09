import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import UI_set
from UI_set import selected_option
# from UI_set.OptionButton import opt


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
client_soc = None
# selected_option = None

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
            qr_data = qr_data_receive.decode('utf-8')
        except socket.error as e:
            print("Error receiving data: ", e)
            break
        
        parts = qr_data.split('/')  
        classifi = parts[0]
        
        if classifi and (classifi[0] == 'L' or classifi[0] == 'Y' or classifi[0] == 'A'):
            UI_set.MainWindow.first_details_list_widget.addItem(qr_data)
            
        elif classifi and (classifi[0] == 'F' or classifi[0] == 'N' or classifi[0] == 'B'):
            UI_set.MainWindow.second_details_list_widget.addItem(qr_data)
        
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
            print("None이 아님")
            try:
                client_soc.sendall(selected_option.encode('utf-8'))
                print(f"Sending option: {selected_option}")
                selected_option = None
            except socket.error as e:
                print("Error sending data:", e)
                break

# -----------------------------------------------------------------------
def opt_callback(opt):
    global selected_option
    selected_option = opt
    print(f"Selected option: {selected_option}")
    
    # OptionButton.option_sel()
    
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