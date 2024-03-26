import sys, os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMenuBar, QStatusBar, QListWidget)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QRect
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
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.mousePressEvent = self.refresh_system
        main_layout.addWidget(self.logo_label)
        
        # 상단 레이아웃 설정 (구상도 사진 및 옵션 버튼)
        top_layout = QHBoxLayout()
        
        # 구상도 이미지 설정
        self.assembly_label = QLabel(self)
        pixmap = QPixmap('assembly_image.jpg')
        fixed_width = 946  # 변경된 크기
        scaled_pixmap = pixmap.scaledToWidth(fixed_width, Qt.SmoothTransformation)
        self.assembly_label.setPixmap(scaled_pixmap)
        self.assembly_label.setGeometry(11, 44, scaled_pixmap.width(), scaled_pixmap.height())
        top_layout.addWidget(self.assembly_label)
        
        options_layout = QHBoxLayout()
        self.option_buttons = [
            OptionButton('transport_ON.png', 'transport_OFF.png', 'Opt1', self),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
        ]
        for option_button in self.option_buttons:
            container = QWidget()  # 옵션 버튼을 포함할 컨테이너 위젯 생성
            layout = QVBoxLayout(container)  # 컨테이너에 QVBoxLayout 적용
            layout.addWidget(option_button)  # OptionButton을 레이아웃에 추가

            transparent_button = TransparentButton(container)
            transparent_button.resize(option_button.size())  # TransparentButton의 크기를 OptionButton과 동일하게 설정
            transparent_button.clicked.connect(lambda _, b=option_button: self.toggleButton(b))
            layout.addWidget(transparent_button)  # 투명 버튼 추가
            options_layout.addWidget(container)  # 최종적으로 컨테이너를 옵션 레이아웃에 추가
        top_layout.addLayout(options_layout)
        
        main_layout.addLayout(top_layout)
        
        # 중앙 레이아웃 설정 (세부항목 목록 및 장애이력)
        middle_layout = QHBoxLayout()
        
        # 장애이력 레이블 설정
        history_layout = QVBoxLayout()
        self.history_label = QLabel('History', self)
        self.history_label.setStyleSheet("border: 1px solid black;")  # 검은색 외형선 추가
        history_layout.addWidget(self.history_label)
        # 장애이력 출력 위젯 설정
        self.history_list_widget = QListWidget(self)
        self.history_list_widget.setStyleSheet("border: 1px solid black;")  # 검은색 외형선 추가
        history_layout.addWidget(self.history_list_widget)  # 장애이력 레이아웃에 위젯 추가
        self.history_list_widget.setGeometry(11, 585, 840, 429)  # 위치와 크기 설정 (x, y, width, height)
        
        middle_layout.addLayout(history_layout)  # 중앙 레이아웃에 장애이력 레이아웃 추가
        
        # 첫 번째 세부항목 레이블 및 위젯 설정
        self.first_details_layout = QVBoxLayout()
        self.first_details_label = QLabel('First Details', self)
        self.first_details_label.setStyleSheet("border: 1px solid black;")
        
        self.first_details_list_widget = QListWidget(self)
        self.first_details_list_widget.setStyleSheet("border: 1px solid black;")
        self.first_details_list_widget.setGeometry(845, 585, 840, 429)  # 위치와 크기 설정
        self.first_details_layout.addWidget(self.first_details_list_widget)
        middle_layout.addLayout(self.first_details_layout)
        
        # 두 번째 세부항목 레이블 및 위젯 설정
        self.second_details_layout = QVBoxLayout()
        self.second_details_label = QLabel('Second Details', self)
        self.second_details_label.setStyleSheet("border: 1px solid black;")
        
        self.second_details_list_widget = QListWidget(self)
        self.second_details_list_widget.setStyleSheet("border: 1px solid black;")
        self.second_details_list_widget.setGeometry(1699, 585, 840, 429)  # 위치와 크기 설정
        self.second_details_layout.addWidget(self.second_details_list_widget)
        middle_layout.addLayout(self.second_details_layout)

        # 메인 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)

        # 중앙 레이아웃에 위젯 추가
        middle_layout.addWidget(self.history_list_widget)

        main_layout.addLayout(middle_layout)
        

    def toggleButton(self, button):
        for btn in self.option_buttons:
            if btn != button:
                btn.is_on = False
                btn.setPixmap(btn.off_pixmap)
        button.toggle()

    def refresh_system(self, event):
        print('새로고침')
    
    # 신호에 따라 세부항목 목록에 텍스트를 추가하는 함수
    def addDetailItem(self, text):
        self.details_list_widget.addItem(text)
    
    # 장애이력에 항목을 추가하는 메서드
    def addHistoryItem(self, text):
        self.history_list_widget.addItem(text)
    
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
        self.setPixmap(self.off_pixmap)

    def setScaledPixmap(self):
        # QLabel의 크기를 가져오기
        label_size = self.size()
        scaled_on_pixmap = self.on_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 현재 상태(is_on)에 따라 적절한 QPixmap을 설정
        self.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)
        self.update()  # QLabel의 내용이 변경되었음을 알리고 강제로 다시 그리기

    def resizeEvent(self, event):
        scaled_on_pixmap = self.on_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)

    def toggle(self):
        self.is_on = not self.is_on
        self.setPixmap(self.on_pixmap if self.is_on else self.off_pixmap)
        self.setScaledPixmap()
        if self.is_on:
            print(self.opt_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())