import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MyUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datetime = QDateTime.currentDateTime()
        self.initUI()

    def initUI(self):
        #창크기, 창아이콘
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon('robot_icon.png'))       #파일위치(상대)=코드실행결과위치(CapstoneDesign)
        #이름 + 메뉴바
        self.setWindowTitle('Delta_System')
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        #상태바 활성화
        self.statusBar()
        #메뉴바
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
        #현재 날짜/시간
        self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))
        ##################################################################################
        
        
        layer_label=QLabel()
        position_label=QLabel()
        
        # lbl_A = QLabel()
        # lbl_A.setPixmap(self.pixmap)
        # self.pixmap = QPixmap('ABCDpos_A.jpg')
        # self.repixmap = self.pixmap.scaled(QSize(450, 150))
        # self.lbl_A.setPixmap(self.repixmap)
        
        
        lbl_img = QLabel()
        lbl_img.move(200,200)
        pixmap = QPixmap('123층_1누끼.png')
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        lbl_img.setPixmap(pixmap)
        lbl_img.setPixmap(scaled_pixmap)

        
        hbox = QHBoxLayout()
        hbox.addWidget(layer_label)
        hbox.addWidget(position_label)
        self.setLayout(hbox)

        
        self.show()
        
    def loadImageFromFile(self) :
        #QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("testImage.jpg")
        self.qPixmapFileVar = self.qPixmapFileVar.scaledToWidth(600)
        self.lbl_picture.setPixmap(self.qPixmapFileVar)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyUI()
    sys.exit(app.exec_())
