import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket
import time

class ServerThread(QThread):
    data_received = pyqtSignal(str)  # 데이터 수신 시그널

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print('UI server waiting for connection....')
        client_soc, addr = server_socket.accept()
        print('UI server connected')
        
        while True:
            try:
                data = client_soc.recv(1024)
                if not data:
                    print("No data received. Connection might be closed.")
                    break
                qr_data_receive = data.decode('utf-8')
                self.data_received.emit(qr_data_receive)  # 시그널 발생
            except socket.error as e:
                print("Error receiving data:", e)
                break

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Threaded QSocket Server')

        # 레이아웃 설정
        grid_layout = QGridLayout()
        self.label = QLabel("Waiting for data...")
        grid_layout.addWidget(self.label, 0, 0)
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)

    def update_label(self, text):
        self.label.setText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    server_thread = ServerThread('192.168.144.1', 1111)
    server_thread.data_received.connect(main_window.update_label)
    server_thread.start()

    sys.exit(app.exec_())
