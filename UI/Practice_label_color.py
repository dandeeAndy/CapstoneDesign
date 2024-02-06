import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

class stylesheetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        red_label = QLabel('빨간 라벨')
        blue_label = QLabel('파란 라벨')
        green_label = QLabel('초록 라벨')

        red_label.setStyleSheet("color: #FF5733; border-style: solid; border-width: 2px; border-color: #FFC300; border-radius: 10px; ")
        blue_label.setStyleSheet(
            "color: #4D69E8; border-style: solid; border-width: 2px; border-color: #54A0FF; border-radius: 10px; ")
        green_label.setStyleSheet(
            "color: #41E881; border-style: solid; border-width: 2px; border-color: #67E841; border-radius: 10px; ")

        vbox = QVBoxLayout()
        vbox.addWidget(red_label)
        vbox.addWidget(blue_label)
        vbox.addWidget(green_label)

        self.setLayout(vbox)
        self.setWindowTitle('스타일 변경')
        self.setGeometry(500,500,500,400)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = stylesheetApp()
    sys.exit(app.exec_())