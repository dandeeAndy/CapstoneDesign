from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QAction, QMenuBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont

import sys
class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        # self.setStyleSheet("background:transparent; border: 2px solid black;")

class OptionButton(QWidget):
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None, index=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        self.opt_text = opt_text
        self.is_on = False
        self.index = index
        
        self.label = QLabel(self)
        self.setScaledPixmap()
        
        self.transparent_button = TransparentButton(self)
        self.transparent_button.clicked.connect(self.button_clicked)
        self.transparent_button.setFixedSize(240, 135)
        self.transparent_button.setStyleSheet("background:transparent;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)
        self.setLayout(layout)

    def setScaledPixmap(self):
        label_size = self.size()
        scaled_on_pixmap = self.on_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)

    def button_clicked(self):
        other_buttons_on = any(btn.is_on for btn in self.parent().option_buttons if btn is not self)
        if other_buttons_on:
            QMessageBox.warning(self, '경고', '다른 옵션이 실행 중입니다.')
        else:
            self.toggle()

    def toggle(self):
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            print(f"Selected option: {self.opt_text}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.option_buttons = [
                OptionButton('domfor_ON.png', 'domfor_OFF.png', 'Opt1', self),
                OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
                OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
        ]
        
        layout = QVBoxLayout(self.central_widget)
        for button in self.option_buttons:
            layout.addWidget(button)

        self.pause_button = QPushButton('Pause and Reset Options', self)
        self.pause_button.clicked.connect(self.pauseClicked)
        layout.addWidget(self.pause_button)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Option Buttons Example')
        self.show()

    def pauseClicked(self):
        reply = QMessageBox.question(self, 'Reset Options', 'Reset all options?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for button in self.option_buttons:
                button.is_on = False
                button.setScaledPixmap()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())