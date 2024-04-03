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
        self.first_enter_pressed = False
        self.initUI()
        
    def initUI(self):
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        
        # 각 행과 열에 대한 비율 설정
        grid_layout.setRowStretch(0, 2)
        grid_layout.setRowStretch(1, 4)
        grid_layout.setRowStretch(2, 2)
        grid_layout.setRowStretch(3, 1)
        grid_layout.setRowStretch(4, 6)
        grid_layout.setColumnStretch(0, 6)
        # grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(1, 9)
        # grid_layout.setColumnStretch(2, 1)
        grid_layout.setColumnStretch(2, 3)
        grid_layout.setColumnStretch(3, 3)
        grid_layout.setColumnStretch(4, 3)

        # 겹치는 레이블 추가
        label_1 = QLabel()
        grid_layout.addWidget(label_1, 0, 1, 1, 4)  # (0, 1)에서 (0, 4)까지

        label_2 = QLabel()
        grid_layout.addWidget(label_2, 1, 0, 2, 2)  # (1, 0)에서 (2, 1)까지
        
        label_3 = QLabel()
        # label_3.setStyleSheet("border: 2px solid black;border-radius: 10px;")
        grid_layout.addWidget(label_3, 2, 2, 1, 3)  # (2, 2)에서 (2, 4)까지
        
        label_4 = QLabel()
        grid_layout.addWidget(label_4, 3, 2, 1, 3)  # (3, 2)에서 (3, 4)까지
        
        label_5 = QLabel()
        label_3.setStyleSheet("border: 2px solid black;border-radius: 10px;")
        grid_layout.addWidget(label_5, 4, 2, 1, 3)  # (4, 2)에서 (4, 4)까지

        # 빈 레이블들을 생성하고 그리드 레이아웃에 추가하는 반복문
        for i in range(4):  # 4행
            for j in range(5):  # 5열
                if not ((i == 0 and 1 <= j <= 4) or 
                        (i in [1, 2] and j in [0, 1]) or 
                        (i == 2 and 2 <= j <= 4) or 
                        (i == 3 and 2 <= j <= 4) or 
                        (i == 4 and 2 <= j <= 4)):
                    label = QLabel()
                    label.setStyleSheet("border: 2px solid black;border-radius: 10px;")
                    grid_layout.addWidget(label, i, j)        
        
        ########################################################################################################
        # 윈도우 설정
        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_rect)
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(grid_layout)
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
        self.logo_pixmap = QPixmap('JALK3_logo.png')
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignLeft)
        self.logo_label.mousePressEvent = self.refresh_system
        scaled_pixmap = self.logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        grid_layout.addWidget(self.logo_label, 0, 0)
        
        self.assembly_label = QLabel(self)
        pixmap = QPixmap('assembly_image.jpg')
        self.assembly_label.setPixmap(pixmap)
        label_2.setLayout(QHBoxLayout())
        label_2.layout().addWidget(self.assembly_label)
        
        ###########################################################################################################
        
        self.option_buttons = [
                OptionButton('domfor_ON.png', 'domfor_OFF.png', 'Opt1', self),
                OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
                OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
            ]
        
        for i, option_button in enumerate(self.option_buttons):
            option_button.setButtonSize(240, 270)

            transparent_button = TransparentButton(option_button)
            transparent_button.setFixedSize(240, 135)
            transparent_button.clicked.connect(lambda _, b=option_button: b.toggle())

            grid_layout.addWidget(option_button, 1, i + 2)
        
        grid_layout.setContentsMargins(50, 50, 50, 50)
        
        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png')
        pause_button_pixmap = pause_button_pixmap.scaled(700, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        grid_layout.addWidget(self.pause_button_label, 2, 2, 1, 3)
                
        ###########################################################################################################
        self.history_list_widget = QListWidget(self)
        self.history_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.history_list_widget, 4, 0)
                
        self.first_details_list_widget = QListWidget(self)
        self.first_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.first_details_list_widget, 4, 1)
                
        self.second_details_list_widget = QListWidget(self)
        self.second_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.second_details_list_widget, 4, 2, 1, 3)
        
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            if self.option_buttons[0].is_on:
                self.first_details_list_widget.addItem("1111111111")
            elif self.option_buttons[1].is_on:
                self.first_details_list_widget.addItem("3333333333")
            elif self.option_buttons[2].is_on:
                self.first_details_list_widget.addItem("5555555555")
        
        # 오른쪽 화살표 키 이벤트
        elif event.key() == Qt.Key_Right:
            if self.option_buttons[0].is_on:
                self.second_details_list_widget.addItem("2222222222")
            elif self.option_buttons[1].is_on:
                self.second_details_list_widget.addItem("4444444444")
            elif self.option_buttons[2].is_on:
                self.second_details_list_widget.addItem("6666666666")
        
    # 클릭 이벤트 처리
    def pauseClicked(self, event):
        QMessageBox.information(self, '알림', '작업이 중지되었습니다.')
        print('PAUSE!')

        reply = QMessageBox.question(self, '확인', '분류기준을 초기화하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.resetOptions()
            self.first_details_list_widget.clear()
            self.second_details_list_widget.clear()
    
    def resetOptions(self):
        for button in self.option_buttons:
            if button.is_on:
                print(f"{button.opt_text} pause")
                button.is_on = False
                button.setScaledPixmap()
        
    def buttonClicked(self):
            print("Button clicked!")

    def toggleButton(self, selected_button):
        for button in self.option_buttons:
            if button == selected_button:
                button.toggle()
            else:
                button.is_on = False
                button.setScaledPixmap()

    def refresh_system(self, event):
        print('새로고침')
    
    # 장애이력에 항목을 추가하는 메서드
    def addHistoryItem(self, text):
        self.history_list_widget.addItem(text)
    
class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        # self.setStyleSheet("background:transparent; border: 2px solid black;")

class OptionButton(QWidget):
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        if self.on_pixmap.isNull() or self.off_pixmap.isNull():
            print("이미지 로드 실패:", on_image_path, "또는", off_image_path)
            return
        
        self.opt_text = opt_text
        self.is_on = False

        self.label = QLabel(self)
        self.setScaledPixmap()

        self.transparent_button = TransparentButton(self)
        self.transparent_button.clicked.connect(self.toggle)
        self.transparent_button.setFixedSize(240, 135)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)

        self.setLayout(layout)
        
        self.transparent_button.raise_()
    
    def setButtonSize(self, width, height):
        scaled_on_pixmap = self.on_pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.setFixedSize(width, height)
        self.label.setFixedSize(width, height)
        self.label.setPixmap(scaled_on_pixmap)
        self.label.setPixmap(scaled_off_pixmap)
        
        self.transparent_button.setFixedSize(width, height)

    def setScaledPixmap(self):
        label_size = self.size()
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
            print(f"{self.opt_text}\nSTART")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())