import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMenuBar, QSizePolicy, QListWidget, QGridLayout)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

#계속해서 수정하고 저장하면서 끝낼 완성본
#크게 수정할 일이 있을 시
#파일 저장 + 깃허브 커밋
#파일 이름 : "추가한 기능(간략하게)//제거한 기능(없을시 *)(간략하게)"

##### VS코드 닫기 전!!!
##### 최종 저장 & 깃허브 푸쉬


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 기본 창 설정        
        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_rect)
        self.setWindowTitle('Delta_System')
        self.setWindowIcon(QIcon('robot_icon.png'))
        self.showMaximized()

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
        if self.logo_pixmap.isNull():
            #QPixmap 객체 상태 확인(오작동시 True반환)
            print("Failed to load system_logo.png")
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.mousePressEvent = self.refresh_system
        main_layout.addWidget(self.logo_label)

        # 상단 레이아웃 설정 (구상도 사진 및 옵션 버튼)
        top_layout = QHBoxLayout()
        
        # 중앙 레이아웃 설정 (세부항목 목록 및 장애이력)
        middle_layout = QGridLayout()

        # 장애이력 레이블 설정
        history_label = QLabel('History', self)
        history_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        history_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(history_label, 0, 0, 1, 2)  # 장애이력 레이블 위치 설정

        # 장애이력 출력 위젯 설정
        history_list_widget = QListWidget(self)
        history_list_widget.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        history_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(history_list_widget, 1, 0, 1, 2)  # 장애이력 위젯 위치 설정

        # 첫 번째 세부항목 레이블 및 위젯 설정
        first_details_label = QLabel('First Details', self)
        first_details_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        first_details_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(first_details_label, 0, 2, 1, 2)  # 첫 번째 세부항목 레이블 위치 설정

        first_details_list_widget = QListWidget(self)
        first_details_list_widget.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        first_details_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(first_details_list_widget, 1, 2, 1, 2)  # 첫 번째 세부항목 위젯 위치 설정

        # 두 번째 세부항목 레이블 및 위젯 설정
        second_details_label = QLabel('Second Details', self)
        second_details_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        second_details_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(second_details_label, 0, 4, 1, 2)  # 두 번째 세부항목 레이블 위치 설정

        second_details_list_widget = QListWidget(self)
        second_details_list_widget.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        second_details_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 크기 고정
        middle_layout.addWidget(second_details_list_widget, 1, 4, 1, 2)  # 두 번째 세부항목 위젯 위치 설정

        main_layout.addLayout(middle_layout)

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
        
    def toggleButtonState(self, btn):
        # 하나의 버튼이 on 상태일 때 다른 버튼들을 off 상태로 설정
        if btn.isChecked():
            for button in self.option_buttons:
                if button != btn:
                    button.setChecked(False)

    def refresh_system(self, event):
        print('새로고침')

class OptionButton(QPushButton):
    def __init__(self, title, opt_number, parent=None):
        super().__init__(title, parent)
        self.opt_number = opt_number

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print(f'Opt{self.opt_number}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())