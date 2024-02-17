import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QStatusBar, qApp, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QTime, QDate

class MainWindow(QMainWindow):
    def __init__(self):
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

        # 3. 상태바 설정
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_date)
        self.timer.start(1000)

        # # 4. 레이아웃 설정
        # widget = QWidget(self)
        # self.setCentralWidget(widget)
        # vbox = QVBoxLayout()
        # widget.setLayout(vbox)
        # label1 = QLabel(self)
        # label1.setPixmap(QPixmap('./123층_1누끼.png')) # 이미지 파일 경로
        # label2 = QLabel(self)
        # label2.setPixmap(QPixmap('./ABCD위치_A누끼.png')) # 이미지 파일 경로
        # hbox = QHBoxLayout()
        # hbox.addWidget(label1)
        # hbox.addWidget(label2)
        # vbox.addStretch(1)
        # vbox.addLayout(hbox)

        # 4. 레이아웃 설정
        widget = QWidget(self)
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        # 오른쪽 하단 레이아웃 설정
        hbox = QHBoxLayout()
        label1 = QLabel()
        label1.setPixmap(QPixmap('./123층_1누끼.png')) # 이미지 파일 경로
        label2 = QLabel()
        label2.setPixmap(QPixmap('./ABCD위치_A누끼.png')) # 이미지 파일 경로
        hbox.addWidget(label1)
        hbox.addWidget(label2)

        # 그리드 레이아웃에 추가
        grid.addLayout(hbox, 1, 1)


    def time_date(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString('yyyy년 MM월 dd일')
        self.statusbar.showMessage(label_date + ' ' + label_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
