import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QStatusBar, qApp, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QTime, QDate, pyqtSignal
from datetime import datetime

#계속해서 수정하고 저장하면서 끝낼 완성본
#크게 수정할 일이 있을 시
#파일 저장 + 깃허브 커밋
#파일 이름 : "추가한 기능(간략하게)//제거한 기능(없을시 *)(간략하게)"

##### VS코드 닫기 전!!!
##### 최종 저장 & 깃허브 푸쉬

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

        # 3. 상태바 설정
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_date)
        self.timer.start(1000)
        
        # 날짜와 시간 출력하기
        self.statusBar().showMessage(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



    def time_date(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString('yyyy년 MM월 dd일')
        self.statusbar.showMessage(label_date + ' ' + label_time)
        
    # def change_image(self, image_path):
    #     self.label2.setPixmap(QPixmap(image_path))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
