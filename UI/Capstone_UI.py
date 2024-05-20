import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import UI_set
from queue import Queue
import socket
import threading
import time

print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host ='192.168.163.251'
UI_host = '192.168.163.1'
port = 3333

lock = threading.Lock()
client_soc = None
selected_option = None
pause_clicked = None
option_reset = None
last_sent_option = None
last_sent_pause = None
last_sent_reset = None

last_received_data = None
count = 1
flag = True  # flag to manage odd/even data processing

def client_func():
    global client_soc, selected_option, last_received_data, count, Number, widgets, flag
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

    buffer = ""
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
            break
        
        widgets = []
        if qr_data_receive and qr_data_receive != last_received_data:
            count += 1
            Number = count // 2
            last_received_data = qr_data_receive
            
            if flag:  # Odd-numbered data processing
                print("odd numbered data--------------------------------")
                parts_odd = last_received_data.split('/')
                print(parts_odd)
                
                if parts_odd:
                    classifi = parts_odd[0]
                    
                    if selected_option == 'Option1':
                        print("Option1")
                        if classifi[0] in ['A']:
                            widgets = widgets1
                            option = 0
                        elif classifi[0] in ['B']:
                            widgets = widgets2
                            option = 1
                    
                    elif selected_option == 'Option2':
                        print("Option2")
                        if classifi[1] in ['A']:
                            widgets = widgets1
                            option = 0
                        elif classifi[1] in ['B']:
                            widgets = widgets2
                            option = 1
                    
                    elif selected_option == 'Option3':
                        print("Option3")
                        if classifi[2] in ['A']:
                            widgets = widgets1
                            option = 0
                        elif classifi[2] in ['B']:
                            widgets = widgets2
                            option = 1
                    
                    if widgets:
                        for widget, part in zip(widgets, parts_odd[1:5]):
                            add_centered_item(part, widget)
                        widgets = None
                        add_centered_item(str(Number), mainWin.NO_widget)
                        add_centered_item("0", mainWin.E_CODE_widget)
                        
                    for widget, part in zip(history_widgets, parts_odd[5:]):
                        add_centered_item(part, widget)
                    print(parts_odd[5:])
                    parts_odd = None
                
            else:  # Even-numbered data processing
                print("even numbered data--------------------------------")
                parts_even = qr_data_receive.split('/')
                print(parts_even)
                
                if parts_even:
                    motor_datetime = parts_even[3]
                    print("motor datetime: ", motor_datetime)
                    for widget, part in zip(history_widgets, parts_even[1:5]):
                        add_centered_item(part, widget)
                    add_centered_item(str(Number), mainWin.NO_widget)
                    if option == 0:
                        add_centered_item(parts_even[0], mainWin.position_widget_1)
                    elif option == 1:
                        add_centered_item(parts_even[0], mainWin.position_widget_2)
                    parts_even = None
                add_centered_item("0", mainWin.E_CODE_widget)
            flag = not flag
            qr_data_receive = None
        
        time.sleep(1)

def server_func():
    global client_soc, selected_option, last_sent_option
    global pause_clicked, last_sent_pause
    global option_reset, last_sent_reset
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((UI_host, port))
        server_socket.listen()
        print('UI server waiting for connection....')
        
        client_soc, addr = server_socket.accept()
        print('UI server connected')

        while True:
            selected_option = UI_set.get_selected_option()
            pause_clicked = UI_set.get_pause_clicked()
            option_reset = UI_set.get_option_reset()
            
            if selected_option is not None and selected_option != last_sent_option:
                try:
                    client_soc.sendall((selected_option + '\n').encode('utf-8'))
                    last_sent_option = selected_option
                    selected_option = None
                except socket.error as e:
                    print("Error sending option_data:", e)
                    break
            
            if pause_clicked is not None and pause_clicked != last_sent_pause:
                try:
                    client_soc.sendall((pause_clicked + '\n').encode('utf-8'))
                    last_sent_pause = pause_clicked
                    print("Pause clicked:", last_sent_pause)
                    pause_clicked = None
                except socket.error as e:
                    print("Error sending pause_data:", e)
                    break
            
            if option_reset is not None and option_reset != last_sent_reset:
                try:
                    client_soc.sendall((option_reset + '\n').encode('utf-8'))
                    last_sent_reset = option_reset
                    print("Reset signal:", last_sent_reset)
                    option_reset = None
                except socket.error as e:
                    print("Error sending reset_data:", e)
                    break
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        server_socket.close()

def add_centered_item(text, widget):
    item = QListWidgetItem(text)
    item.setTextAlignment(Qt.AlignCenter)
    widget.addItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 10)
    app.setFont(font)
    
    mainWin = UI_set.MainWindow()
    
    widgets1 = [mainWin.package_number_widget_1, 
                mainWin.email_widget_1, 
                mainWin.destination_widget_1, 
                mainWin.phone_number_widget_1]
    
    widgets2 = [mainWin.package_number_widget_2, 
                mainWin.email_widget_2, 
                mainWin.destination_widget_2, 
                mainWin.phone_number_widget_2]
    
    history_widgets = [mainWin.ALARM_widget, 
                       mainWin.STATE_widget, 
                       mainWin.DATETIME_widget]
    
    mainWin.showMaximized()
    mainWin.show()
    
    server_thread = threading.Thread(target=server_func)
    client_thread = threading.Thread(target=client_func)

    server_thread.start()
    client_thread.start()
    
    sys.exit(app.exec_())
