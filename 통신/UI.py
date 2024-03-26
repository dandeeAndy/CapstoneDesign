import socket
import threading
import time

print(socket.gethostbyname(socket.gethostname()))

Vision_host =''
UI_host = '192.168.0.54'
Motor_host = ' '

port = 1111

lock = threading.Lock()

# UI 클라이언트 소켓을 만들고 Vision 서버에 접속함
# QR 데이터를 UI에서 선택한 옵션에 따라 필요한 부분만 변수화 
def client_func():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((Vision_host, port))
            break
        except socket.error:
            print("Connection attempt failed. Retrying...")
            time.sleep(5)  
            continue

    while True:
        try:
            with lock:
                vision_data_receive = client_socket.recv(100)
                print('recv msg:', vision_data_receive.decode('utf-8'))
        except socket.error as e:
            print("Error receiving data: ", e)
            break
            
            
# UI 서버 소켓을 만들고 Motor 클라이언트의 접속을 기다림
# 변수 값에 따라서 Motor 값 결정됨
# 분류된 박스 개수 기억해서(나머지 이용) 
def server_func():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))  
    server_socket.listen()
    print('UI_server waitting for conneciton....')
    
    client_soc, addr = server_socket.accept()
    print('UI_server connect')

    while True:
        
        UI_data_send = "UI에서 전송되는 데이터입니다."
        
        try:
            with lock:
                client_soc.sendall(UI_data_send.encode('utf-8'))
        except socket.error as e:
            print("Error")
            break



            
# 서버와 클라이언트를 멀티스레드로 
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
