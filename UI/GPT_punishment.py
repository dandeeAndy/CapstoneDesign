import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenuBar, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_rect)
        self.setWindowTitle('Delta_System')
        self.setWindowIcon(QIcon('robot_icon.png'))
        self.showMaximized()

        # 메뉴바 설정
        self.menuBar().setNativeMenuBar(False)  # macOS에서 메뉴 바가 정상적으로 동작하도록 설정
        file_menu = self.menuBar().addMenu('&File')
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 메인 위젯 및 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 옵션 버튼들 추가
        self.option_buttons = [
            OptionButton('transport_ON.png', 'transport_OFF.png', 'Opt1', self),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
        ]
        
        options_layout = QHBoxLayout()
        for option_button in self.option_buttons:
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(option_button)
            
            transparent_button = TransparentButton(container)
            transparent_button.resize(option_button.size())
            transparent_button.clicked.connect(lambda _, b=option_button: self.toggleButton(b))
            
            options_layout.addWidget(container)

        main_layout.addLayout(options_layout)

    def toggleButton(self, selected_button):
        for button in self.option_buttons:
            if button == selected_button:
                button.toggle()
            else:
                button.is_on = False
                button.setScaledPixmap()

class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setStyleSheet("background:transparent;")

class OptionButton(QLabel):
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        self.opt_text = opt_text
        self.is_on = False
        self.setScaledPixmap()
        
    def setScaledPixmap(self):
        if self.is_on:
            pixmap = self.on_pixmap
        else:
            pixmap = self.off_pixmap
        self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
    def resizeEvent(self, event):
        self.setScaledPixmap()
        
    def toggle(self):
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            print(self.opt_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
