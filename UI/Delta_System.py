import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp


class Ui_delta(object):
    def setupUi(self, delta):
        delta.setObjectName("delta")
        delta.resize(1920, 1080)
        font = QtGui.QFont()
        font.setFamily("나눔스퀘어")
        font.setBold(True)
        font.setWeight(75)
        delta.setFont(font)
        delta.setStyleSheet("background-color:grey;")

        self.retranslateUi(delta)
        QtCore.QMetaObject.connectSlotsByName(delta)
        
        self.exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(self.exitAction)

        self.setWindowTitle('Menubar')
        
        # super().__init__()
        # self.initUI()

    def retranslateUi(self, delta):
        _translate = QtCore.QCoreApplication.translate
        delta.setWindowTitle(_translate("delta", "delta"))
    
    # def initUI(self):
        # delta.setWindowIcon(QIcon('robot_icon.png'))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    delta = QtWidgets.QDialog()
    ui = Ui_delta()
    ui.setupUi(delta)
    delta.show()
    sys.exit(app.exec_())
