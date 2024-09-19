import sys
import socket
import threading
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
import UI_module

class NetworkManager(QObject):
    dataReceived = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = None
        self.keep_running = True

    def connect_to_server(self):
        while self.keep_running:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                print("Connected to Vision Motor host.")
                break
            except socket.error:
                print("Connection attempt failed. Retrying...")
                time.sleep(5)

    def listen_for_data(self):
        self.connect_to_server()
        while self.keep_running:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    self.dataReceived.emit(data)
            except socket.error as e:
                print("Error receiving data:", e)
                self.connect_to_server()

    def send_data(self, data):
        if self.client_socket:
            try:
                self.client_socket.sendall((data + '\n').encode('utf-8'))
            except socket.error as e:
                print("Error sending data:", e)
                self.connect_to_server()

    def stop(self):
        self.keep_running = False
        if self.client_socket:
            self.client_socket.close()

def main():
    app = QApplication(sys.argv)
    mainWin = UI_module.MainWindow()

    # Create network manager and threads for client and server functionality
    client_manager = NetworkManager('192.168.95.231', 1111)
    client_thread = threading.Thread(target=client_manager.listen_for_data)
    client_thread.start()

    mainWin.showMaximized()
    result = app.exec_()  # Block until the main window is closed

    client_manager.stop()  # Cleanly stop the network threads
    client_thread.join()  # Wait for the network thread to finish

    sys.exit(result)

if __name__ == '__main__':
    main()
