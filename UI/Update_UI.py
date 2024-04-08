import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_enter_pressed = False
        self.initUI()
        
    def initUI(self):
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(50, 0, 50, 50)
        
        # 각 행과 열에 대한 비율 설정
        grid_layout.setRowStretch(0, 10)
        grid_layout.setRowStretch(1, 20)
        grid_layout.setRowStretch(2, 10)
        grid_layout.setRowStretch(3, 1)
        grid_layout.setRowStretch(4, 1)
        grid_layout.setRowStretch(5, 30)
        
        grid_layout.setColumnStretch(0, 8)
        grid_layout.setColumnStretch(1, 16)
        grid_layout.setColumnStretch(2, 12)
        grid_layout.setColumnStretch(3, 16)
        grid_layout.setColumnStretch(4, 28)
        
        
        grid_layout.setColumnStretch(5, 1)
        
        
        grid_layout.setColumnStretch(6, 12)
        grid_layout.setColumnStretch(7, 30)
        grid_layout.setColumnStretch(8, 30)
        grid_layout.setColumnStretch(9, 18)
        grid_layout.setColumnStretch(10, 30)
        
        
        grid_layout.setColumnStretch(11, 1)
        
        
        grid_layout.setColumnStretch(12, 12)
        grid_layout.setColumnStretch(13, 28)
        
        grid_layout.setColumnStretch(14, 2)
        grid_layout.setColumnStretch(15, 30)
        grid_layout.setColumnStretch(16, 8)
        
        grid_layout.setColumnStretch(17, 10)
        grid_layout.setColumnStretch(18, 30)

        
        label_1 = QLabel()
        grid_layout.addWidget(label_1, 0, 0, 1, 5)
        
        label_2 = QLabel()
        grid_layout.addWidget(label_2, 0, 5, 1, 14)
        
        label_3 = QLabel()
        grid_layout.addWidget(label_3, 1, 0, 2, 12)
        
        label_4 = QLabel()
        grid_layout.addWidget(label_4, 1, 12, 1, 2)
        
        label_5 = QLabel()
        grid_layout.addWidget(label_5, 1, 14, 1, 3)
        
        label_6 = QLabel()
        grid_layout.addWidget(label_6, 1, 17, 1, 2)
        
        label_7 = QLabel()
        grid_layout.addWidget(label_7, 2, 12, 1, 7)
        
        label_8 = QLabel()
        grid_layout.addWidget(label_8, 3, 0, 1, 5)
        
        label_9 = QLabel()
        grid_layout.addWidget(label_9, 3, 6, 1, 5)
        
        label_10 = QLabel()
        grid_layout.addWidget(label_10, 3, 12, 1, 7)
             
        # # 겹치는 레이블 추가
        # label_1 = QLabel()
        # grid_layout.addWidget(label_1, 0, 1, 1, 6)  # (0, 1)에서 (0, 6)까지

        # label_2 = QLabel()
        # grid_layout.addWidget(label_2, 1, 0, 2, 4)  # (1, 0)에서 (2, 3)까지
        
        # label_3 = QLabel()
        # # label_3.setStyleSheet("border: 2px solid black;border-radius: 10px;")
        # grid_layout.addWidget(label_3, 2, 4, 1, 3)  # (2, 4)에서 (2, 6)까지
        
        # label_4 = QLabel()
        # grid_layout.addWidget(label_4, 3, 4, 1, 3)  # (3, 4)에서 (3, 6)까지
        
        # label_5 = QLabel()
        # # label_3.setStyleSheet("border: 2px solid black;border-radius: 10px;")
        # grid_layout.addWidget(label_5, 4, 4, 1, 3)  # (4, 4)에서 (4, 6)까지

        for i in range(5):  # 4행
            for j in range(7):  # 5열
                if not ((i == 0 and 0 <= j <= 5) or 
                        (i == 0 and 5 <= j <= 19) or 
                        (i in [1, 2] and j in [0, 12]) or 
                        (i == 1 and 12 <= j <= 14) or 
                        (i == 1 and 14 <= j <= 17) or 
                        (i == 1 and 17 <= j <= 19) or 
                        (i == 2 and 12 <= j <= 19) or 
                        (i == 3 and 0 <= j <= 5) or 
                        (i == 3 and 6 <= j <= 11) or 
                        (i == 3 and 12 <= j <= 19)):
                    label = QLabel()
                    # label.setStyleSheet("border: 2px solid black;border-radius: 10px;")
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
        # 옵션 버튼 설정
        self.option_buttons = [
            OptionButton('domfor_ON.png', 'domfor_OFF.png', 'Opt1', self, callback=OptionButton.opt_callback),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self, callback=OptionButton.opt_callback),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self, callback=OptionButton.opt_callback),
        ]
        for i, option_button in enumerate(self.option_buttons):
            option_button.setButtonSize(240, 270)
            transparent_button = TransparentButton(option_button)
            transparent_button.setFixedSize(240, 135)
            transparent_button.clicked.connect(lambda _, b=option_button: b.option_sel())
            grid_layout.addWidget(option_button, 1, i + 4)
        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png')
        pause_button_pixmap = pause_button_pixmap.scaled(700, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        grid_layout.addWidget(self.pause_button_label, 2, 4, 1, 3)
        
        ###########################################################################################################
        # 리스트 설정
        font_label = QFont("NanumSquare", 12)
        border_style = "border-top: 2px solid black; border-left: 2px solid black; border-right: 2px solid black;"

        label_alarm = QLabel("NO      ALARM      EQ      STATE      DATETIME")
        label_alarm.setFont(font_label)
        label_alarm.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        label_alarm.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(label_alarm, 3, 0)
        
        label_first_detail = QLabel("상품명         코드         출발날짜        도착날짜         지역")
        label_first_detail.setFont(font_label)
        label_first_detail.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        label_first_detail.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(label_first_detail, 3, 2)
        
        label_second_detail = QLabel("상품명         코드         출발날짜         도착날짜         지역")
        label_second_detail.setFont(font_label)
        label_second_detail.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        label_second_detail.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(label_second_detail, 3, 4, 1, 3)
        
        self.history_list_widget = QListWidget(self)
        self.history_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.history_list_widget, 4, 0)
                
        self.first_details_list_widget = QListWidget(self)
        self.first_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.first_details_list_widget, 4, 2)
        self.printWidgetSize(self.first_details_list_widget)
                
        self.second_details_list_widget = QListWidget(self)
        self.second_details_list_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.second_details_list_widget, 4, 4, 1, 3)
        self.printWidgetSize(self.second_details_list_widget)
        
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
                button.option_sel()
            else:
                button.is_on = False
                button.setScaledPixmap()

    def refresh_system(self, event):
        print('새로고침')
    
    # 장애이력에 항목을 추가하는 메서드
    def addHistoryItem(self, text):
        self.history_list_widget.addItem(text)
    
    def printWidgetSize(self, widget):
        size = widget.size()
        print("Width:", size.width(), "Height:", size.height())
    
        
class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        # self.setStyleSheet("background:transparent; border: 2px solid black;")

class OptionButton(QWidget):
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None, callback=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        self.opt_text = opt_text
        self.is_on = False
        self.callback = callback
        if self.on_pixmap.isNull() or self.off_pixmap.isNull():
            print("이미지 로드 실패:", on_image_path, "또는", off_image_path)
            return

        self.label = QLabel(self)
        self.setScaledPixmap()

        self.transparent_button = TransparentButton(self)
        self.transparent_button.clicked.connect(self.option_sel)
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
    
    def opt_callback(opt):
        print(f"Selected option: {opt}")

    def option_sel(self):
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            if self.callback:
                self.callback(self.opt_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    mainWin = MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())