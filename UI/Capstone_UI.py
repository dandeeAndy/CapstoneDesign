import sys, os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QMenuBar, QStatusBar, QListWidget)
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
        #이미지 파일 경로 확인을 위한 현재 디렉토리 출력
        print("Current Working Directory:", os.getcwd())
        # 기본 창 설정
        self.setWindowTitle('Delta_System')
        self.setWindowIcon(QIcon('robot_icon.png'))
        self.setGeometry(0, 0, 1920, 1080)
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
        
        # 구상도 이미지 설정
        self.assembly_label = QLabel(self)
        self.assembly_pixmap = QPixmap('assembly_image.jpg')
        self.assembly_label.setPixmap(self.assembly_pixmap)
        top_layout.addWidget(self.assembly_label)
        
        options_layout = QHBoxLayout()
        self.option_buttons = [
            OptionButton('transport_ON.png', 'transport_OFF.png', 'Opt1', self),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
        ]
        for button in self.option_buttons:
            button.setAlignment(Qt.AlignCenter)
            # 투명한 버튼을 이미지 위에 겹치게 설정
            transparent_button = TransparentButton(button)
            transparent_button.clicked.connect(lambda _, b=button: self.toggleButton(b))
            options_layout.addWidget(button)
        top_layout.addLayout(options_layout)
        main_layout.addLayout(top_layout)
        # 중앙 레이아웃 설정 (세부항목 목록 및 장애이력)
        middle_layout = QHBoxLayout()
        
        # 장애이력 레이블 설정
        self.history_label = QLabel('History', self)
        self.history_label.setStyleSheet("border: 1px solid black;")  # 검은색 외형선 추가
        middle_layout.addWidget(self.history_label)
        main_layout.addLayout(middle_layout)
        
        # 세부항목 목록 레이블과 출력 위젯 설정
        details_layout = QVBoxLayout()
        self.details_title_label = QLabel('Details List', self)
        self.details_title_label.setStyleSheet("border: 1px solid black;")  # 검은색 외형선 추가
        details_layout.addWidget(self.details_title_label)
        # 세부항목 목록 출력 위젯
        self.details_list_widget = QListWidget(self)
        self.details_list_widget.setStyleSheet("border: 1px solid black;")  # 검은색 외형선 추가
        details_layout.addWidget(self.details_list_widget)
        middle_layout.addLayout(details_layout)
        
        # 메인 위젯 설정
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def toggleButton(self, button):
        # 다른 버튼이 이미 켜져 있으면 끄기
        for btn in self.option_buttons:
            if btn != button:
                btn.is_on = False
                btn.setPixmap(btn.off_pixmap)
        # 클릭된 버튼 토글
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
        # QLabel의 크기에 맞춰 QPixmap을 조정
        self.setScaledPixmap()

        self.opt_text = opt_text
        self.is_on = False

    def setScaledPixmap(self):
        # QLabel의 크기를 가져오기
        label_size = self.size()
        # QPixmap을 QLabel의 크기에 맞춰 조정
        scaled_on_pixmap = self.on_pixmap.scaled(label_size, Qt.KeepAspectRatio)
        scaled_off_pixmap = self.off_pixmap.scaled(label_size, Qt.KeepAspectRatio)
        self.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)

    def resizeEvent(self, event):
        # QLabel의 크기가 변경될 때 QPixmap을 다시 조정
        self.setScaledPixmap()

    def toggle(self):
        self.is_on = not self.is_on
        self.setPixmap(self.on_pixmap if self.is_on else self.off_pixmap)
        if self.is_on:
            print(self.opt_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())