from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

selected_option = None
pause_clicked = None

def get_selected_option():
    global selected_option
    return selected_option

def get_pause_clicked():
    global pause_clicked
    return pause_clicked

font_title = QFont("NanumSquare", 12)
border_style_1 = "border-top: 2px solid black; border-left: 2px solid black;"
border_style_2 = "border-top: 2px solid black; border-left: 2px solid black; border-right: 2px solid black;"
border_style_3 = "border-top: 2px solid black; border-left: 2px solid black; border-bottom: 2px solid black;"
border_style_4 = "background-color: white; border: 2px solid black;"

# ---------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_enter_pressed = False
        self.option1_status = 0
        self.option2_status = 0
        self.option3_status = 0
        self.initUI()
        
    def initUI(self):
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(50, 0, 50, 50)
        
        # 각 행과 열에 대한 비율 설정
        self.grid_layout.setRowStretch(0, 10)
        self.grid_layout.setRowStretch(1, 20)
        self.grid_layout.setRowStretch(2, 10)
        self.grid_layout.setRowStretch(3, 1)
        self.grid_layout.setRowStretch(4, 1)
        self.grid_layout.setRowStretch(5, 30)
        
        self.grid_layout.setColumnStretch(0, 8)
        self.grid_layout.setColumnStretch(1, 16)
        self.grid_layout.setColumnStretch(2, 12)
        self.grid_layout.setColumnStretch(3, 16)
        self.grid_layout.setColumnStretch(4, 28)
        
        self.grid_layout.setColumnStretch(5, 1)
        
        #코드/출발날짜/도착날짜/지역/상품명
        self.grid_layout.setColumnStretch(6, 12)
        self.grid_layout.setColumnStretch(7, 30)
        self.grid_layout.setColumnStretch(8, 30)
        self.grid_layout.setColumnStretch(9, 18)
        self.grid_layout.setColumnStretch(10, 30)
        
        self.grid_layout.setColumnStretch(11, 1)
        
        self.grid_layout.setColumnStretch(12, 12)
        self.grid_layout.setColumnStretch(13, 28)
        
        self.grid_layout.setColumnStretch(14, 2)
        self.grid_layout.setColumnStretch(15, 30)
        self.grid_layout.setColumnStretch(16, 8)
        
        self.grid_layout.setColumnStretch(17, 10)
        self.grid_layout.setColumnStretch(18, 30)
        
        label_1 = QLabel()
        self.grid_layout.addWidget(label_1, 0, 0, 1, 5)        
        label_2 = QLabel()
        self.grid_layout.addWidget(label_2, 0, 5, 1, 14)        
        label_3 = QLabel()
        self.grid_layout.addWidget(label_3, 1, 0, 2, 12)        
        label_4 = QLabel()
        self.grid_layout.addWidget(label_4, 1, 12, 1, 2)        
        label_5 = QLabel()
        self.grid_layout.addWidget(label_5, 1, 14, 1, 3)        
        label_6 = QLabel()
        self.grid_layout.addWidget(label_6, 1, 17, 1, 2)        
        label_7 = QLabel()
        self.grid_layout.addWidget(label_7, 2, 12, 1, 7)        
        label_8 = QLabel()
        self.grid_layout.addWidget(label_8, 3, 0, 1, 5)        
        label_9 = QLabel()
        self.grid_layout.addWidget(label_9, 3, 6, 1, 5)        
        label_10 = QLabel()
        self.grid_layout.addWidget(label_10, 3, 12, 1, 7)

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
                    self.grid_layout.addWidget(label, i, j)
        
# ---------------------------------------------------------------------------------------------------------------------
        # 윈도우 설정
        screen_rect = QApplication.desktop().screenGeometry()
        self.setGeometry(screen_rect)
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.grid_layout)
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
        self.grid_layout.addWidget(self.logo_label, 0, 0, 1, 5)
        
        self.assembly_label = QLabel(self)
        pixmap = QPixmap('assembly_image.jpg')
        self.assembly_label.setPixmap(pixmap)
        label_3.setLayout(QHBoxLayout())
        label_3.layout().addWidget(self.assembly_label)
        
# ---------------------------------------------------------------------------------------------------------------------
        # 옵션 버튼 설정
        self.option_buttons = [
            OptionButton('domfor_ON.png', 'domfor_OFF.png', 'Option1', self),
            OptionButton('fragile_ON.png', 'fragile_OFF.png', 'Option2', self),
            OptionButton('courier_ON.png', 'courier_OFF.png', 'Option3', self),
        ]
        button_positions = [(1, 12, 1, 2), (1, 14, 1, 3), (1, 17, 1, 2)]
        for i, option_button in enumerate(self.option_buttons):
            option_button.setButtonSize(240, 270)
            transparent_button = TransparentButton(option_button)
            transparent_button.setFixedSize(240, 135)
            transparent_button.clicked.connect(lambda _, b=option_button: b.button_clicked())
            pos = button_positions[i]
            self.grid_layout.addWidget(option_button, *pos)
            
        # 작업 중지 버튼 설정
        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png')
        pause_button_pixmap = pause_button_pixmap.scaled(700, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        self.grid_layout.addWidget(self.pause_button_label, 2, 12, 1, 7)
        
        self.history_maker("label_8", "장애이력", 2, 3, 0, 1, 5)
        self.label_maker("label_9", "L", 2, 3, 6, 1, 5)
        self.label_maker("label_10", "F", 2, 3, 12, 1, 7)

        self.label_maker("NO_label", "NO", 1, 4, 0)
        self.label_maker("ALARM_label", "ALARM", 1, 4, 1)
        self.label_maker("EQ_label", "EQ", 1, 4, 2)
        self.label_maker("STATE_label", "STATE", 1, 4, 3)
        self.label_maker("DATETIME_label", "DATETIME", 2, 4, 4)

        self.label_maker("code_label_1", "코드", 1, 4, 6)
        self.label_maker("departure_label_1", "출발날짜", 1, 4, 7)
        self.label_maker("arrival_label_1", "도착날짜", 1, 4, 8)
        self.label_maker("region_label_1", "지역", 1, 4, 9)
        self.label_maker("product_label_1", "상품명", 2, 4, 10)

        self.label_maker("code_label_2", "코드", 1, 4, 12)
        self.label_maker("departure_label_2", "출발날짜", 1, 4, 13, 1, 2)
        self.label_maker("arrival_label_2", "도착날짜", 1, 4, 15)
        self.label_maker("region_label_2", "지역", 1, 4, 16, 1, 2)
        self.label_maker("product_label_2", "상품명", 2, 4, 18)

        self.widget_maker("NO_widget", 3, 5, 0)
        self.widget_maker("ALARM_widget", 3, 5, 1)
        self.widget_maker("EQ_widget", 3, 5, 2)
        self.widget_maker("STATE_widget", 3, 5, 3)
        self.widget_maker("DATETIME_widget", 4, 5, 4)

        self.widget_maker("code_widget_1", 3, 5, 6)
        self.widget_maker("departure_widget_1", 3, 5, 7)
        self.widget_maker("arrival_widget_1", 3, 5, 8)
        self.widget_maker("region_widget_1", 3, 5, 9)
        self.widget_maker("product_widget_1", 4, 5, 10)

        self.widget_maker("code_widget_2", 3, 5, 12)
        self.widget_maker("departure_widget_2", 3, 5, 13, 1, 2)
        self.widget_maker("arrival_widget_2", 3, 5, 15)
        self.widget_maker("region_widget_2", 3, 5, 16, 1, 2)
        self.widget_maker("product_widget_2", 4, 5, 18)
        
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)
    
    def history_maker(self, label_name, text, style_num, row, col, rowspan=1, colspan=1):
        label = QLabel(text, self)
        setattr(self, label_name, label)
        label.setFont(font_title)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        if style_num == 2:
            label.setStyleSheet(border_style_2)#좌상우
        
        self.grid_layout.addWidget(label, row, col, rowspan, colspan)
    
    def label_maker(self, label_name, text, style_num, row, col, rowspan=1, colspan=1):
        label = QLabel(text, self)
        setattr(self, label_name, label)
        label.setFont(font_title)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        
        if style_num == 1:
            label.setStyleSheet(border_style_1)#좌상
        elif style_num == 2:
            label.setStyleSheet(border_style_2)#좌상우
        elif style_num == 3:
            label.setStyleSheet(border_style_3)#좌상하
        
        self.grid_layout.addWidget(label, row, col, rowspan, colspan)
    
    def widget_maker(self, widget_name, style_num, row, col, rowspan=1, colspan=1):
        widget = QListWidget(self)
        setattr(self, widget_name, widget)
        
        if style_num == 1:
            widget.setStyleSheet(border_style_1)#좌상
        elif style_num == 2:
            widget.setStyleSheet(border_style_2)#좌상우
        elif style_num == 3:
            widget.setStyleSheet(border_style_3)#좌상하
        elif style_num == 4:
            widget.setStyleSheet(border_style_4)#상하좌우

        self.grid_layout.addWidget(widget, row, col, rowspan, colspan)
    
    def update_buttons(self, selected_index):
        for i, button in enumerate(self.option_buttons):
            if i == selected_index:
                button.is_on = True
                setattr(self, f"option{i+1}_status", 1)  # 상태 변수 업데이트
            else:
                button.is_on = False
                setattr(self, f"option{i+1}_status", 0)  # 상태 변수 업데이트
            button.setScaledPixmap()
    
    def option_selected(self):
        is_any_button_on = any(button.is_on for button in self.option_buttons)
        active_button_index = next((i for i, button in enumerate(self.option_buttons) if button.is_on), -1)
        if is_any_button_on:
            self.update_buttons(active_button_index)
        # 이제 여기에서 각 버튼의 상태를 확인하고 필요한 작업을 수행할 수 있습니다.
    
    def addQRData(self, qr_data):
        parts = qr_data.split('/')
        classifi = parts[0]
        
        if classifi[0] in ['L', 'Y', 'A']:
            self.QR_add(1, parts)
        
        elif classifi[0] in ['F', 'N', 'B']:
            self.QR_add(2, parts)
    
    def QR_add(self, widget_set_number, parts):
        if widget_set_number == 1:
            widgets = [self.code_widget_1, self.departure_widget_1, self.arrival_widget_1, self.region_widget_1, self.product_widget_1]
        elif widget_set_number == 2:
            widgets = [self.code_widget_2, self.departure_widget_2, self.arrival_widget_2, self.region_widget_2, self.product_widget_2]
        
        for widget, part in zip(widgets, parts):
            widget.addItem(part)
    
    def clearLists(self):
        history_widgets = [self.NO_widget, self.ALARM_widget, self.EQ_widget, self.STATE_widget, self.DATETIME_widget]
        details_1_widgets = [self.code_widget_1, self.departure_widget_1, self.arrival_widget_1, self.region_widget_1, self.product_widget_1]
        details_2_widgets = [self.code_widget_2, self.departure_widget_2, self.arrival_widget_2, self.region_widget_2, self.product_widget_2]

        for widget in history_widgets + details_1_widgets + details_2_widgets:
            widget.clear()
        
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
        
    # 클릭 이벤트 처리
    def pauseClicked(self, event):
        global pause_clicked
        QMessageBox.information(self, '알림', '작업이 중지되었습니다.')
        print('PAUSE!')
        pause_clicked = "pause"

        reply = QMessageBox.question(self, '확인', '분류기준을 초기화하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.resetOptions()
            self.clearLists()
        else:
            pause_clicked = None
    
    def resetOptions(self):
        for button in self.option_buttons:
            if button.is_on:
                print(f"{button.opt_text} pause")
                button.is_on = False
                button.setScaledPixmap()
        
    def buttonClicked(self):
            print("Button clicked!")

    # def toggleButton(self, selected_button):
    #     for button in self.option_buttons:
    #         if button == selected_button:
    #             button.option_sel()
    #         else:
    #             button.is_on = False
    #             button.setScaledPixmap()

    def refresh_system(self, event):
        print('새로고침')
    
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
        self.transparent_button.clicked.connect(self.button_clicked)
        self.transparent_button.setFixedSize(240, 135)
        self.transparent_button.setStyleSheet("background:transparent;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)
        self.setLayout(layout)
        
        self.transparent_button.raise_()
        
    optionSelected = pyqtSignal(str)  # 새 신호 정의
    
    def setButtonSize(self, width, height):
        # scaled_on_pixmap = self.on_pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedSize(width, height)
        self.label.setFixedSize(width, height)
        # self.label.setPixmap(scaled_on_pixmap)
        self.label.setPixmap(scaled_off_pixmap)
        
        self.transparent_button.setFixedSize(width, height)

    def setScaledPixmap(self):
        label_size = self.size()
        scaled_on_pixmap = self.on_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_off_pixmap = self.off_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_off_pixmap if not self.is_on else scaled_on_pixmap)
        self.update()
    
    # def opt_callback(opt):
    #     # print(f"Selected option: {opt}")
    #     global selected_option

    # def option_sel(self):
    #     global selected_option  # 전역 변수 사용을 명시
    #     self.is_on = not self.is_on
    #     self.setScaledPixmap()
    #     if self.is_on:
    #         selected_option = self.opt_text  # 선택된 옵션을 전역 변수에 할당
    #         print(f"Selected option: {selected_option}")
    #         if self.callback:
    #             self.callback(self.opt_text)  # 변경된 selected_option 값을 사용하여 callback 함수 호출
    
    def button_clicked(self):
        other_buttons_on = any(btn.is_on for btn in self.parent().children() if isinstance(btn, OptionButton) and btn is not self)
        if other_buttons_on:
            QMessageBox.warning(self, '경고', '다른 옵션이 실행 중입니다.')
        else:
            self.toggle()
    
    def toggle(self):
        global selected_option, pause_clicked
        pause_clicked = None
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            selected_option = self.opt_text
            # print(f"Selected option: {selected_option}")
            # self.optionSelected.emit(selected_option)  # 신호 발생