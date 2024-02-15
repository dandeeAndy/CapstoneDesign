import socket
import threading
import time

host = socket.gethostbyname(socket.gethostname())
Vision_port = 1111
UI_port = 2222
Motor_port = 3333

# 서버 소켓을 만들고 클라이언트의 접속을 기다립니다.
# send data to Motor (place_loc)
def server_func():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, UI_port))  # 수정 필요: 서버의 IP 주소와 포트 번호
    server_socket.listen()
    print('UI_server wait')
    
    client_soc, addr = server_socket.accept()
    print('UI_server connect')

    while True:
        UI_data_send = "서버에서 전송되는 데이터입니다."
        client_soc.sendall(UI_data_send.encode('utf-8'))

# 클라이언트 소켓을 만들고 서버에 접속합니다.
# receive data from Vision
def client_func():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((host, Vision_port))
            break
        except socket.error:
            time.sleep(5)  # 1초 동안 대기
            continue

    while True:
        vision_data_receive = client_socket.recv(100)
        print('recv msg:', vision_data_receive.decode('utf-8'))

# 두 함수를 각각 다른 스레드에서 실행합니다.
server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()
