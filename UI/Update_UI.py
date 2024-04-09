import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

selected_option = None

# ---------------------------------------------------------------------------------------------------------------------
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
        
        #코드/출발날짜/도착날짜/지역/상품명
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
        
# ---------------------------------------------------------------------------------------------------------------------
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
        grid_layout.addWidget(self.logo_label, 0, 0, 1, 5)
        
        self.assembly_label = QLabel(self)
        pixmap = QPixmap('assembly_image.jpg')
        self.assembly_label.setPixmap(pixmap)
        label_3.setLayout(QHBoxLayout())
        label_3.layout().addWidget(self.assembly_label)
        
# ---------------------------------------------------------------------------------------------------------------------
        # 옵션 버튼 설정
        self.option_buttons = [
            OptionButton('domfor_ON.png', 'domfor_OFF.png', 'Opt1', self),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Opt2', self),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Opt3', self),
        ]
        button_positions = [(1, 12, 1, 2), (1, 14, 1, 3), (1, 17, 1, 2)]
        for i, option_button in enumerate(self.option_buttons):
            option_button.setButtonSize(240, 270)
            transparent_button = TransparentButton(option_button)
            transparent_button.setFixedSize(240, 135)
            transparent_button.clicked.connect(lambda _, b=option_button: b.option_sel())
            pos = button_positions[i]
            grid_layout.addWidget(option_button, *pos)
        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png')
        pause_button_pixmap = pause_button_pixmap.scaled(700, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        grid_layout.addWidget(self.pause_button_label, 2, 12, 1, 7)
        
        self.label_9 = QLabel("L")
        self.label_10 = QLabel("F")
        self.label_9.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.label_10.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.label_9.setStyleSheet("background-color: white;border: 2px solid black;")
        self.label_10.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.label_9, 3, 6, 1, 5)
        grid_layout.addWidget(self.label_10, 3, 12, 1, 7)
        
# ---------------------------------------------------------------------------------------------------------------------
        # 리스트 설정
        font_label = QFont("NanumSquare", 12)
        border_style = "border-top: 2px solid black; border-left: 2px solid black;"
        border_style_2 = "border-top: 2px solid black; border-left: 2px solid black; border-bottom: 2px solid black;"
        border_style_3 = "border-top: 2px solid black; border-left: 2px solid black; border-right: 2px solid black;"

        NO_label = QLabel("NO")
        NO_label.setFont(font_label)
        NO_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        NO_label.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(NO_label, 4, 0)
        
        ALARM_label = QLabel("ALARM")
        ALARM_label.setFont(font_label)
        ALARM_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        ALARM_label.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(ALARM_label, 4, 1)
        
        EQ_label = QLabel("EQ")
        EQ_label.setFont(font_label)
        EQ_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        EQ_label.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(EQ_label, 4, 2)
        
        STATE_label = QLabel("STATE")
        STATE_label.setFont(font_label)
        STATE_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        STATE_label.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(STATE_label, 4, 3)
        
        DATETIME_label = QLabel("DATETIME")
        DATETIME_label.setFont(font_label)
        DATETIME_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        DATETIME_label.setStyleSheet(border_style_3 + " background-color: white;")
        grid_layout.addWidget(DATETIME_label, 4, 4)
        
        code_label_1 = QLabel("코드")
        code_label_1.setFont(font_label)
        code_label_1.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        code_label_1.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(code_label_1, 4, 6)
        
        departure_label_1 = QLabel("출발날짜")
        departure_label_1.setFont(font_label)
        departure_label_1.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        departure_label_1.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(departure_label_1, 4, 7)
        
        arrival_label_1 = QLabel("도착날짜")
        arrival_label_1.setFont(font_label)
        arrival_label_1.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        arrival_label_1.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(arrival_label_1, 4, 8)
        
        region_label_1 = QLabel("지역")
        region_label_1.setFont(font_label)
        region_label_1.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        region_label_1.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(region_label_1, 4, 9)
        
        product_label_1 = QLabel("상품명")
        product_label_1.setFont(font_label)
        product_label_1.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        product_label_1.setStyleSheet(border_style_3 + " background-color: white;")
        grid_layout.addWidget(product_label_1, 4, 10)
        
        code_label_2 = QLabel("코드")
        code_label_2.setFont(font_label)
        code_label_2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        code_label_2.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(code_label_2, 4, 12)
        
        departure_label_2 = QLabel("출발날짜")
        departure_label_2.setFont(font_label)
        departure_label_2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        departure_label_2.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(departure_label_2, 4, 13, 1, 2)
        
        arrival_label_2 = QLabel("도착날짜")
        arrival_label_2.setFont(font_label)
        arrival_label_2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        arrival_label_2.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(arrival_label_2, 4, 15)
        
        region_label_2 = QLabel("지역")
        region_label_2.setFont(font_label)
        region_label_2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        region_label_2.setStyleSheet(border_style + " background-color: white;")
        grid_layout.addWidget(region_label_2, 4, 16, 1, 2)
        
        product_label_2 = QLabel("상품명")
        product_label_2.setFont(font_label)
        product_label_2.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        product_label_2.setStyleSheet(border_style_3 + " background-color: white;")
        grid_layout.addWidget(product_label_2, 4, 18)
        
        self.NO_widget = QListWidget(self)
        self.NO_widget.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.NO_widget, 5, 0)
        
        self.ALARM_widget = QListWidget(self)
        self.ALARM_widget.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.ALARM_widget, 5, 1)
        
        self.EQ_widget = QListWidget(self)
        self.EQ_widget.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.EQ_widget, 5, 2)
        
        self.STATE_widget = QListWidget(self)
        self.STATE_widget.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.STATE_widget, 5, 3)
        
        self.DATETIME_widget = QListWidget(self)
        self.DATETIME_widget.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.DATETIME_widget, 5, 4)
        
        self.code_widget_1 = QListWidget(self)
        self.code_widget_1.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.code_widget_1, 5, 6)
        
        self.departure_widget_1 = QListWidget(self)
        self.departure_widget_1.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.departure_widget_1, 5, 7)
        
        self.arrival_widget_1 = QListWidget(self)
        self.arrival_widget_1.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.arrival_widget_1, 5, 8)
        
        self.region_widget_1 = QListWidget(self)
        self.region_widget_1.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.region_widget_1, 5, 9)
        
        self.product_widget_1 = QListWidget(self)
        self.product_widget_1.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.product_widget_1, 5, 10)
        
        self.code_widget_2 = QListWidget(self)
        self.code_widget_2.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.code_widget_2, 5, 12)
        
        self.departure_widget_2 = QListWidget(self)
        self.departure_widget_2.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.departure_widget_2, 5, 13, 1, 2)
        
        self.arrival_widget_2 = QListWidget(self)
        self.arrival_widget_2.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.arrival_widget_2, 5, 15)
        
        self.region_widget_2 = QListWidget(self)
        self.region_widget_2.setStyleSheet(border_style_2 + "background-color: white;")
        grid_layout.addWidget(self.region_widget_2, 5, 16, 1, 2)
        
        self.product_widget_2 = QListWidget(self)
        self.product_widget_2.setStyleSheet("background-color: white;border: 2px solid black;")
        grid_layout.addWidget(self.product_widget_2, 5, 18)
        
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)
        
    def update_option(new_value):
        global selected_option  # 글로벌 변수 사용 선언
        selected_option = new_value  # 글로벌 변수 업데이트
        
    def print_option():
        print(selected_option)  # 글로벌 변수 접근
        
    def update_labels(self, opt):
        if opt == 'Opt1':
            self.label_9.setText("L")
            self.label_10.setText("F")
        elif opt == 'Opt2':
            self.label_9.setText("Y")
            self.label_10.setText("N")
        elif opt == 'Opt3':
            self.label_9.setText("A")
            self.label_10.setText("B")
        # print(f"Selected option: {opt}")
        
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
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        self.opt_text = opt_text
        self.is_on = False
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
        # print(f"Selected option: {opt}")
        global selected_option

    def option_sel(self):
        global selected_option  # 전역 변수 사용을 명시
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            selected_option = self.opt_text  # 선택된 옵션을 전역 변수에 할당
            print(f"Selected option: {selected_option}")
            if self.callback:
                self.callback(self.opt_text)  # 변경된 selected_option 값을 사용하여 callback 함수 호출
# ---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    mainWin = MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())