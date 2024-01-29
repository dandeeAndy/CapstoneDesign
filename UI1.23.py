import os
import sys
import time
import queue
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui


from concurrent import futures

import logging
import threading

import grpc
import grpc_tuna_pb2
import grpc_tuna_pb2_grpc
import time

Vision_ip=''
Vision_port=''

RbPi1_ip=''
RbPi1_port=''

RbPi2_ip = ''
RbPi2_port =''

Scada_ip=''


form_class = uic.loadUiType("main.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.robot1_color_num=0
        # self.robot2_weight=0
        # self.robot3_weight=0
        # self.red_count=0
        # self.yellow_count=0
        # self.green_count=0
        # self.blue_count=0
        # self.purple_count=0
        # self.picture = QtWidgets.QLabel(self.centralwidget)
        # self.picture.setGeometry(QtCore.QRect(670, 800, 461, 381))
        # self.picture.setObjectName("picture")
        # self.img_robot = QtGui.QImage("ABCDpos_A.jpg")
        # self.img_robot = self.img_robot.scaledToWidth(460)
        # self.picture.setPixmap(QtGui.QPixmap.fromImage(self.img_robot))
        
        lbl_A = QLabel()
        lbl_A.setPixmap(self.pixmap)
        self.pixmap = QPixmap('ABCDpos_A.jpg')
        self.repixmap = self.pixmap.scaled(QSize(450, 150))
        self.lbl_A.setPixmap(self.repixmap)
        

        # self.lcd_robot1.setProperty("value", self.robot1_color_num)
        # self.lcd_robot2.setProperty("value", self.robot2_weight)
        # self.lcd_robot3.setProperty("value", self.robot3_weight)

        # self.lcd_10kg.setProperty("value", self.red_count)
        # self.lcd_20kg.setProperty("value", self.yellow_count)
        # self.lcd_30kg.setProperty("value", self.green_count)
        # self.lcd_40kg.setProperty("value", self.blue_count)
        # self.lcd_50kg.setProperty("value", self.purple_count)
        
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
    app.exec_()

    