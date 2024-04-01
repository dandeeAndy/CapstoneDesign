# import sys
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QWidget, QLabel, 
#                              QVBoxLayout, QHBoxLayout, QPushButton, QMenuBar,
#                              QListWidget, QSizePolicy, QStackedLayout, QGridLayout)
# from PyQt5.QtCore import Qt, QTimer, QRect
# from PyQt5.QtGui import QIcon, QPixmap
import sys, os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
        grid_layout = QGridLayout()
        
        # 각 행과 열에 대한 비율 설정
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 3)
        grid_layout.setRowStretch(2, 4)
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 3)
        grid_layout.setColumnStretch(2, 3)

        # (0, 1)과 (0, 2)에 걸쳐지는 레이블 추가
        label_1 = QLabel()
        grid_layout.addWidget(label_1, 0, 1, 1, 2)  # 여기서 1, 2는 각각 rowSpan, colSpan을 의미합니다.

        # (1, 0)과 (1, 1)에 걸쳐지는 레이블 추가
        label_2 = QLabel()
        grid_layout.addWidget(label_2, 1, 0, 1, 2)  # 여기서 1, 2는 각각 rowSpan, colSpan을 의미합니다.

        # 나머지 레이블들을 그리드에 추가합니다.
        for i in range(3):  # 행
            for j in range(3):  # 열
                if (i == 0 and j in [1, 2]) or (i == 1 and j in [0, 1]):
                    continue  # 이미 추가한 레이블에 걸쳐지는 부분은 건너뜁니다.
                label = QLabel()
                grid_layout.addWidget(label, i, j)
        
        
        ########################################################################################################
        # 윈도우 설정
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
                
        # 시스템 로고 설정
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap('system_logo.png')
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignLeft)
        self.logo_label.mousePressEvent = self.refresh_system
        grid_layout.addWidget(self.logo_label, 0, 0)
        # grid_layout.setAlignment(Qt.AlignLeft)
                
        # 구상도 이미지 설정
        self.assembly_label = QLabel(self)
        pixmap = QPixmap('assembly_image.jpg')
        fixed_width = 946  # 변경된 크기
        scaled_pixmap = pixmap.scaledToWidth(fixed_width, Qt.SmoothTransformation)
        self.assembly_label.setPixmap(scaled_pixmap)
        self.assembly_label.setGeometry(11, 44, scaled_pixmap.width(), scaled_pixmap.height())
        grid_layout.addWidget(self.assembly_label, 1, 0, 1, 2)
        
        ##
        # # 같은 크기의 QPixmap 레이블 두 개와 크기가 같은 투명 버튼을 모두 겹쳐 하나의 레이아웃에 포함
        # label1 = QLabel(self)
        # pixmap1 = QPixmap('transport_ON.png')
        # label1.setPixmap(pixmap1)
        # label1.setAlignment(Qt.AlignCenter)

        # label2 = QLabel(self)
        # pixmap2 = QPixmap('transport_OFF.png')
        # label2.setPixmap(pixmap2)
        # label2.setAlignment(Qt.AlignCenter)

        # transparent_button = TransparentButton(self)
        # transparent_button.resize(label1.size())  # 투명 버튼의 크기를 레이블과 동일하게 설정
        # transparent_button.clicked.connect(self.buttonClicked)
        

        # layout = QVBoxLayout()
        # layout.addWidget(label1)
        # layout.addWidget(label2)
        # layout.addWidget(transparent_button)

        # top_layout.addLayout(layout)
        ##
        ###########################################################################################################
        
        self.option_buttons = [
                OptionButton('transport_ON.png', 'transport_OFF.png', 'Opt1', self),
                OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
                OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
            ]
        
        # 옵션 버튼들을 만드는 코드 부분
        for idx, option_button in enumerate(self.option_buttons):
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(option_button)

            transparent_button = TransparentButton(container)
            transparent_button.resize(option_button.size())
            transparent_button.clicked.connect(lambda _, b=option_button: self.toggleButton(b))
            grid_layout.addWidget(option_button, 1, idx + 2)  # 가정: 옵션 버튼을 1행, 2열부터 시작해 배치
        
        grid_layout.setContentsMargins(50, 50, 50, 50)
        
        # 중앙 위젯 설정 및 메인 레이아웃 적용
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
                
        ###########################################################################################################
                
        # # 장애이력 레이블 설정
        # history_layout = QVBoxLayout()
        
        # self.history_label = QLabel('History', self)
        # self.history_label.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        # history_layout.addWidget(self.history_label)
        
        # 장애이력 출력 위젯 설정
        self.history_list_widget = QListWidget(self)
        self.history_list_widget.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        
        grid_layout.addWidget(self.history_list_widget, 2, 0)
        
        # grid_layout.addLayout(history_layout, 2, 0)  # 중앙 레이아웃에 장애이력 레이아웃 추가
                      
        # # 첫 번째 세부항목 레이블 및 위젯 설정
        # first_details_layout = QVBoxLayout()
        
        # self.first_details_label = QLabel('First Details', self)
        # self.first_details_label.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        # first_details_layout.addWidget(self.first_details_label)
        
        self.first_details_list_widget = QListWidget(self)
        self.first_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        grid_layout.addWidget(self.first_details_list_widget, 2, 1)
        
        # grid_layout.addLayout(first_details_layout, 2, 1)
                
        # # 두 번째 세부항목 레이블 및 위젯 설정
        # second_details_layout = QVBoxLayout()
        
        # self.second_details_label = QLabel('Second Details', self)
        # self.second_details_label.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        # second_details_layout.addWidget(self.second_details_label)
        
        self.second_details_list_widget = QListWidget(self)
        self.second_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;border-radius: 10px;")
        grid_layout.addWidget(self.second_details_list_widget, 2, 2)
        
        # grid_layout.addLayout(second_details_layout, 2, 2)

        # 메인 레이아웃 설정
        
        # 중앙 위젯 설정 및 메인 레이아웃 적용
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
                     
        #  # 위젯 위치와 크기를 1초마다 출력하는 타이머
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.printWidgetSizes)
        # self.timer.start(1000)  # 1초마다 실행
        
    def buttonClicked(self):
            print("Button clicked!")
            # Add your code here to handle the button click event
    
    def printWidgetSizes(self):
        # print("장애이력 위치:", self.history_label.pos())
        # print("장애이력 사이즈:", self.history_label.size())
        print("장애이력 위치:", self.history_list_widget.pos())
        print("장애이력 사이즈:", self.history_list_widget.size())
        print("왼파 세부사항 위치:", self.first_details_list_widget.pos())
        print("왼파 세부사항 사이즈:", self.first_details_list_widget.size())
        print("오른파 세부사항 위치:", self.second_details_list_widget.pos())
        print("오른파 세부사항 사이즈:", self.second_details_list_widget.size())
        
    
    # 선택된 버튼을 활성화하고 나머지는 비활성화
    def toggleButton(self, selected_button):
        for button in self.option_buttons:
            if button == selected_button:
                button.toggle()
            else:
                button.is_on = False
                button.setScaledPixmap()

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

class OptionButton(QWidget):
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        if self.on_pixmap.isNull() or self.off_pixmap.isNull():
            print("이미지 로드 실패:", on_image_path, "또는", off_image_path)
            return  # 이미지 로드 실패시 초기화 중단

        self.opt_text = opt_text
        self.is_on = False

        self.label = QLabel(self)
        self.setScaledPixmap()

        self.transparent_button = TransparentButton(self)
        self.transparent_button.clicked.connect(self.toggle)

        layout = QStackedLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)

        self.setLayout(layout)  # 중요: layout을 OptionButton에 설정

    def setScaledPixmap(self):
        label_size = self.size()  # QLabel의 크기를 가져옵니다.
        scaled_on_pixmap = self.on_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)
        self.update()

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
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())