import socket
import threading
import time

print(socket.gethostbyname(socket.gethostname()))

host = '172.19.88.25'
Vision_port = 1111
UI_port = 2222
Motor_port = 3333

Vision_start_signal = True

# 서버 소켓을 만들고 클라이언트의 접속을 기다립니다.
# send data to UI (logi)
def server_func():
    
    global Vision_start_signal
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, Vision_port))  # 수정 필요: 서버의 IP 주소와 포트 번호
    server_socket.listen()
    print('Vision_server wait')
    
    client_soc, addr = server_socket.accept()
    print('Vision_server connect')

    while True:
        if Vision_start_signal:
            
            vision_data = [1,2,3,4,5]
            
            #원래는 문자열만 보낼 수 있어서, 변환 시켜줌
            vision_data_send = str(vision_data)
            client_soc.sendall(vision_data_send.encode('utf-8'))
            
            Vision_start_signal = False

# 클라이언트 소켓을 만들고 서버에 접속합니다.
# receive data from Motor
def client_func():
    
    global Vision_start_signal
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            client_socket.connect((host, Motor_port))
            break
        except socket.error:
            time.sleep(5)  # 1초 동안 대기
            continue

    while True:
        motor_data_receive = client_socket.recv(100)
        print('recv msg:', motor_data_receive.decode('utf-8'))
        
        if motor_data_receive == "start" :
            Vision_start_signal = True

# 두 함수를 각각 다른 스레드에서 실행합니다.
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
