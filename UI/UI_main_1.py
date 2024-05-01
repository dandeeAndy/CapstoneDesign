import sys
from PyQt5.QtWidgets import QApplication
import threading
import UI_module  # UI_module 모듈을 임포트해

from queue import Queue
import socket
import threading
import time

print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host ='192.168.95.231'
UI_host = '192.168.95.215'

port = 1111

lock = threading.Lock()
client_soc = None  # 전역 변수로 선언하여 모든 함수에서 접근 가능하게 함
last_sent_option = None

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
            UI_module.MainWindow.first_details_list_widget.addItem(qr_data_receive)
        
        elif classifi[0] == 'F' or 'N' or 'B':
            UI_module.MainWindow.second_details_list_widget.addItem(qr_data_receive)
        
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
        selected_option = UI_module.get_selected_option()
        if selected_option is not None and selected_option != last_sent_option:
            try:
                client_soc.sendall((selected_option + '\n').encode('utf-8'))
                last_sent_option = selected_option
                selected_option = None  # 선택된 옵션이 전송되었으므로 초기화
            except socket.error as e:
                print("Error sending data:", e)
                break

def main():
    app = QApplication(sys.argv)
    mainWin = UI_module.MainWindow()

    # for button in mainWin.option_buttons:
    #     button.optionSelected.connect(send_option_to_server)  # 신호에 함수 연결

    mainWin.showMaximized()
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    main_thread = threading.Thread(target=main)
    server_thread = threading.Thread(target=server_func)
    # client_thread = threading.Thread(target=client_func)  # 필요한 경우
    
    main_thread.start()
    server_thread.start()
    # client_thread.start()  # 필요한 경우
