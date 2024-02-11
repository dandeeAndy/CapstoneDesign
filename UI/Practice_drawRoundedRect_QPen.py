## Ex 8-4. 둥근 직사각형 그리기 (drawRoundedRect).

import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('drawRoundedRect')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_roundedrect(qp)
        qp.end()

    def draw_roundedrect(self, qp):
        qp.setPen(QPen(Qt.black, 3))

        qp.drawRoundedRect(20, 20, 100, 100, 0, 0)
        qp.drawText(40, 140, 'radius: 0')

        qp.drawRoundedRect(150, 20, 100, 100, 10, 10)
        qp.drawText(170, 140, 'radius: 10')

        qp.drawRoundedRect(280, 20, 100, 100, 20, 20)
        qp.drawText(300, 140, 'radius: 20')

        qp.drawRoundedRect(20, 160, 100, 100, 30, 30)
        qp.drawText(40, 280, 'radius: 30')

        qp.drawRoundedRect(150, 160, 100, 100, 40, 40)
        qp.drawText(170, 280, 'radius: 40')

        qp.drawRoundedRect(280, 160, 100, 100, 50, 50)
        qp.drawText(300, 280, 'radius: 50')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())