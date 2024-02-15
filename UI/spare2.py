import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate, Qt, QDateTime

class MyUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datetime = QDateTime.currentDateTime()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Delta_System')
        exitAction = QAction(QIcon('/Users/schah/바탕 화면/Andy/Design/CapstoneDesign/UI/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+ESC')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)

        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon('/Users/schah/바탕 화면/Andy/Design/CapstoneDesign/UI/robot_icon.png'))
        
        self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))
        
        
        
        
        
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyUI()
    sys.exit(app.exec_())
