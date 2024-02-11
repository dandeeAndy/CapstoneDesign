import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui

# from concurrent import futures

# import logging
# import threading

# import grpc
# import grpc_tuna_pb2
# import grpc_tuna_pb2_grpc
# import time


form_class = uic.loadUiType("main.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.picture = QtWidgets.QLabel(self.centralwidget)
        self.picture.setGeometry(QtCore.QRect(670, 800, 461, 381))
        self.picture.setObjectName("picture")
        self.img_robot = QtGui.QImage("ABCDpos_A.jpg")
        self.img_robot = self.img_robot.scaledToWidth(460)
        self.picture.setPixmap(QtGui.QPixmap.fromImage(self.img_robot))
        
        lbl_A = QLabel()
        lbl_A.setPixmap(self.pixmap)
        self.pixmap = QPixmap('ABCDpos_A.jpg')
        self.repixmap = self.pixmap.scaled(QSize(450, 150))
        self.lbl_A.setPixmap(self.repixmap)
        
        # #############################################
        # pixmap = QPixmap('ABCDpos_A.jpg')
        
        # vbox = QVBoxLayout()
        # vbox.addWidget(lbl_A)
        # self.setLayout(vbox)
        
        # # QLabel 크기 조정
        # lbl_A.resize(pixmap.width(), pixmap.height())

        # # QLabel을 QMainWindow 중앙에 배치
        # lbl_A.move(window.width() // 2 - label.width() // 2, window.height() // 2 - label.height() // 2)

        # # QMainWindow 크기 조정
        # resize(pixmap.width(), pixmap.height())

        # self.setWindowTitle('QPixmap')        
        # self.show()
        # #################################################
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = WindowClass()
    ui.show()
    sys.exit(app.exec_())

    