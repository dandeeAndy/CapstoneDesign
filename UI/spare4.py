import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QStatusBar, qApp, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QTime, QDate, pyqtSignal
from datetime import datetime

#QHBoxLayout위치 특정하고자 해결코드 받아서 수정한 코드

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        
        # 1. Window 설정
        self.setWindowTitle('Delta_System')
        self.setWindowIcon(QIcon('./robot_icon.png'))
        self.setGeometry(0, 0, 1920, 1080)

        # 2. 메뉴바 설정
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        exitAction = QAction(QIcon('./exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        # # 3. 상태바 설정
        # self.statusbar = QStatusBar(self)
        # self.setStatusBar(self.statusbar)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.time_date)
        # self.timer.start(1000)
        
        vbox = QVBoxLayout()  # 수직 레이아웃 생성

        # 이미지 레이블 생성 및 hbox에 추가
        hbox = QHBoxLayout()
        label1 = QLabel()
        label1.setPixmap(QPixmap('./123층_1누끼.png')) 
        label2 = QLabel()
        label2.setPixmap(QPixmap('./ABCD위치_A누끼.png')) 
        hbox.addWidget(label1)
        hbox.addWidget(label2)

        # vbox에 hbox 추가
        vbox.addLayout(hbox)

        # 빈 공간 추가 (hbox를 상단에 위치시킴)
        vbox.addStretch(1)

        # vbox를 메인 윈도우의 레이아웃으로 설정
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
