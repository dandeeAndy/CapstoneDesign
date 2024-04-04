import socket
import threading
import time

print(socket.gethostbyname(socket.gethostname()))

Vision_Motor_host = '192.168.97.231'
UI_host = '192.168.1.210'

port = 1111

lock = threading.Lock()
client_soc = None  # 전역 변수로 선언하여 모든 함수에서 접근 가능하게 함

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
            vision_data_receive = client_socket.recv(1024)
            print('Data:', vision_data_receive.decode('utf-8'))
        except socket.error as e:
            print("Error receiving data: ", e)
            break

def server_func():
    global client_soc
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((UI_host, port))  
    server_socket.listen()
    print('UI server waiting for connection....')
    
    client_soc, addr = server_socket.accept()
    print('UI server connected')

    # 이 부분은 client_soc가 성공적으로 연결된 후에 실행되어야 하므로 더 이상 입력을 기다리지 않습니다.
    
def user_input_func():
    while True:
        input("Press Enter to send 'Start!' to the Vision system.")  # 사용자 입력 대기
        if client_soc:
            try:
                message = "Start!"
                client_soc.sendall(message.encode('utf-8'))
                print("Signal 'Start!' sent to Vision.")
            except socket.error as e:
                print("Error sending signal: ", e)
        else:
            print("Client socket is not connected.")

server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)
user_input_thread = threading.Thread(target=user_input_func, daemon=True)  # 데몬 스레드로 설정하여 메인 프로그램 종료 시 자동 종료되게 함

server_thread.start()
client_thread.start()
user_input_thread.start()

server_thread.join()
client_thread.join()
# user_input_thread는 데몬 스레드이므로 join 호출 생략
