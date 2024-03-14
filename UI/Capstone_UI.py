import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMenuBar, QStatusBar)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 기본 창 설정
        self.setWindowTitle('Delta_System')
        self.setGeometry(100, 100, 1920, 1080)

        # 메뉴바 설정
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('&File')
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.setMenuBar(self.menu_bar)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        
        # 시스템 로고 설정
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap('system_logo.png')
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.mousePressEvent = self.refresh_system
        main_layout.addWidget(self.logo_label)

        # 상단 레이아웃 설정 (구상도 사진 및 옵션 버튼)
        top_layout = QHBoxLayout()
        
        # 구상도 이미지 설정
        self.assembly_label = QLabel(self)
        self.assembly_pixmap = QPixmap('assembly_image.png')
        self.assembly_label.setPixmap(self.assembly_pixmap)
        top_layout.addWidget(self.assembly_label)

        # 옵션 버튼들 설정
        options_layout = QHBoxLayout()
        self.option_buttons = []
        for i in range(3):
            button = QPushButton(f'Option {i + 1}', self)
            button.setCheckable(True)
            button.toggled.connect(self.handle_toggle)
            options_layout.addWidget(button)
            self.option_buttons.append(button)
        top_layout.addLayout(options_layout)

        main_layout.addLayout(top_layout)

        # 중앙 레이아웃 설정 (세부항목 목록 및 장애이력)
        middle_layout = QHBoxLayout()
        
        # 세부항목 목록 레이블 설정
        self.details_list_label = QLabel('Details List', self)
        middle_layout.addWidget(self.details_list_label)

        # 장애이력 레이블 설정
        self.history_label = QLabel('History', self)
        middle_layout.addWidget(self.history_label)

        main_layout.addLayout(middle_layout)

        # 메인 위젯 설정
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def handle_toggle(self, state):
        for button in self.option_buttons:
            if button.isChecked() and button is not self.sender():
                button.setChecked(False)

    def refresh_system(self, event):
        print('새로고침')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
