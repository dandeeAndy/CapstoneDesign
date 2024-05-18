from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

selected_option = None
pause_clicked = None
option_reset = None

def get_selected_option():
    global selected_option
    return selected_option
def get_pause_clicked():
    global pause_clicked
    return pause_clicked
def get_option_reset():
    global option_reset
    return option_reset

font_title = QFont("NanumSquare", 12)
font_bold = QFont("NanumSquare", 12)
font_bold.setBold(True)
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
        central_widget = QWidget(self)
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)

        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(50, 0, 50, 50)
        
        # 각 열에 대한 비율 설정
        self.grid_layout.setRowStretch(0, 10)
        self.grid_layout.setRowStretch(1, 20)
        self.grid_layout.setRowStretch(2, 10)
        self.grid_layout.setRowStretch(3, 1)
        self.grid_layout.setRowStretch(4, 1)
        self.grid_layout.setRowStretch(5, 30)
        
        # 각 행에 대한 비율 설정
        # [통신이력] NO/ALARM/STATE/E_CODE/DATETIME
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 16)
        self.grid_layout.setColumnStretch(2, 8)
        self.grid_layout.setColumnStretch(3, 4)
        self.grid_layout.setColumnStretch(4, 36)
        
        self.grid_layout.setColumnStretch(5, 5)
        
        # 각 행에 대한 비율 설정
        # [통신이력] NO/ALARM/STATE/E_CODE/DATETIME
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 16)
        self.grid_layout.setColumnStretch(2, 8)
        self.grid_layout.setColumnStretch(3, 4)
        self.grid_layout.setColumnStretch(4, 36)
        
        self.grid_layout.setColumnStretch(5, 5)
        
        # [분류] 현재위치/패키지번호/이메일/목적지/차주전화번호
        self.grid_layout.setColumnStretch(6, 12) # [분류] 현재위치
        self.grid_layout.setColumnStretch(7, 17) # [분류] 패키지번호
        self.grid_layout.setColumnStretch(8, 35) # [분류] 이메일
        self.grid_layout.setColumnStretch(9, 11) # [분류] 목적지
        
        self.grid_layout.setColumnStretch(10, 30) # Option1 # [분류] 차주전화번호
        self.grid_layout.setColumnStretch(11, 1) 
        self.grid_layout.setColumnStretch(12, 12) # [분류] 현재위치
        self.grid_layout.setColumnStretch(13, 2) # [분류] 패키지번호~
        
        self.grid_layout.setColumnStretch(14, 15) # Option2 # [분류] ~패키지번호
        self.grid_layout.setColumnStretch(15, 4)  # [분류] 이메일~
        self.grid_layout.setColumnStretch(16, 26) # [분류] ~
        
        self.grid_layout.setColumnStretch(17, 5) # Option3 # [분류] ~이메일
        self.grid_layout.setColumnStretch(18, 2) # [분류] 목적지~
        self.grid_layout.setColumnStretch(19, 9) # [분류] ~목적지
        self.grid_layout.setColumnStretch(20, 30) # [분류] 차주전화번호
        
        label_1 = QLabel()
        self.grid_layout.addWidget(label_1, 0, 0, 1, 5)
        label_2 = QLabel()
        self.grid_layout.addWidget(label_2, 0, 5, 1, 14)
        self.label_3 = QLabel()
        self.grid_layout.addWidget(self.label_3, 1, 0, 2, 9)
        label_4 = QLabel()
        self.grid_layout.addWidget(label_4, 1, 12, 1, 3)
        label_5 = QLabel()
        self.grid_layout.addWidget(label_5, 1, 15, 1, 2)
        label_6 = QLabel()
        self.grid_layout.addWidget(label_6, 1, 17, 1, 2)
        label_7 = QLabel()
        self.grid_layout.addWidget(label_7, 2, 12, 1, 7)
        label_8 = QLabel()
        self.grid_layout.addWidget(label_8, 3, 0, 1, 5)
        self.label_9 = QLabel()
        self.grid_layout.addWidget(self.label_9, 3, 6, 1, 5)
        self.label_10 = QLabel()
        self.grid_layout.addWidget(self.label_10, 3, 12, 1, 7)

        for i in range(5):  # 4행
            for j in range(20):  # 5열
                if not ((i == 0 and 0 <= j <= 5) or 
                        (i == 0 and 5 <= j <= 19) or 
                        (i in [1, 2] and j in [0, 9]) or 
                        (i == 1 and 12 <= j <= 15) or 
                        (i == 1 and 15 <= j <= 17) or 
                        (i == 1 and 17 <= j <= 19) or 
                        (i == 2 and 12 <= j <= 19) or 
                        (i == 3 and 0 <= j <= 5) or 
                        (i == 3 and 6 <= j <= 11) or 
                        (i == 3 and 12 <= j <= 19)):
                    label = QLabel()
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
        self.logo_pixmap = QPixmap('JALK3_logo_image.png')
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.logo_label.mousePressEvent = self.refresh_system
        logo_scaled_pixmap = self.logo_pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(logo_scaled_pixmap)
        self.grid_layout.addWidget(self.logo_label, 0, 0, 1, 5)
        
        self.assembly_label = QLabel(self)
        self.assembly_pixmap = QPixmap('delta_total.png')
        self.assembly_label.setPixmap(self.assembly_pixmap)
        self.assembly_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        assembly_scaled_pixmap = self.assembly_pixmap.scaled(1142, 416, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.assembly_label.setPixmap(assembly_scaled_pixmap)
        self.label_3.setLayout(QHBoxLayout())
        self.label_3.layout().addWidget(self.assembly_label)
        
# ---------------------------------------------------------------------------------------------------------------------
        # 옵션 버튼 설정
        self.option_buttons = [OptionButton('opt1_ON.png', 'opt1_OFF.png', 'Option1', self),
                               OptionButton('opt2_ON.png', 'opt2_OFF.png', 'Option2', self),
                               OptionButton('opt3_ON.png', 'opt3_OFF.png', 'Option3', self)]
        button_positions = [(1, 10, 1, 4), (1, 14, 1, 3), (1, 17, 1, 4)]
        for i, option_button in enumerate(self.option_buttons):
            transparent_button = TransparentButton(option_button)
            transparent_button.setFixedSize(240, 135)
            transparent_button.clicked.connect(lambda _, b=option_button: b.button_clicked())
            pos = button_positions[i]
            self.grid_layout.addWidget(option_button, *pos)
            
        # 작업 중지 버튼 설정
        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png')
        pause_button_pixmap = pause_button_pixmap.scaled(850, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        self.grid_layout.addWidget(self.pause_button_label, 2, 10, 1, 11)
        
        self.label_maker_bold("label_8", "통신이력", 2, 3, 0, 1, 5)
        self.label_maker_bold("label_9", "A", 2, 3, 6, 1, 5)
        self.label_maker_bold("label_10", "B", 2, 3, 12, 1, 9)

        self.label_maker("NO_label", " NO ", 1, 4, 0)
        self.label_maker("ALARM_label", " ALARM ", 1, 4, 1)
        self.label_maker("STATE_label", " STATE ", 1, 4, 2)
        self.label_maker("E_CODE_label", " ECODE ", 1, 4, 3)
        self.label_maker("DATETIME_label", " DATETIME ", 2, 4, 4)

        self.label_maker("position_label_1", " 현재위치 ", 1, 4, 6)
        self.label_maker("package_number_label_1", " 패키지 번호 ", 1, 4, 7)
        self.label_maker("email_label_1", " 이메일 ", 1, 4, 8)
        self.label_maker("destination_label_1", " 목적지 ", 1, 4, 9)
        self.label_maker("phone_number_label_1", " 차주전화번호 ", 2, 4, 10)

        self.label_maker("position_label_2", " 현재위치 ", 1, 4, 12)
        self.label_maker("package_number_label_2", " 패키지 번호 ", 1, 4, 13, 1, 2)
        self.label_maker("email_label_2", " 이메일 ", 1, 4, 15, 1, 3)
        self.label_maker("destination_label_2", " 목적지 ", 1, 4, 18, 1, 2)
        self.label_maker("phone_number_label_2", " 차주전화번호 ", 2, 4, 20)

        self.widget_maker("NO_widget", 3, 5, 0)
        self.widget_maker("ALARM_widget", 3, 5, 1)
        self.widget_maker("STATE_widget", 3, 5, 2)
        self.widget_maker("E_CODE_widget", 3, 5, 3)
        self.widget_maker("DATETIME_widget", 4, 5, 4)

        self.widget_maker("position_widget_1", 3, 5, 6)
        self.widget_maker("package_number_widget_1", 3, 5, 7)
        self.widget_maker("email_widget_1", 3, 5, 8)
        self.widget_maker("destination_widget_1", 3, 5, 9)
        self.widget_maker("phone_number_widget_1", 4, 5, 10)

        self.widget_maker("position_widget_2", 3, 5, 12)
        self.widget_maker("package_number_widget_2", 3, 5, 13, 1, 2)
        self.widget_maker("email_widget_2", 3, 5, 15, 1, 3)
        self.widget_maker("destination_widget_2", 3, 5, 18, 1, 2)
        self.widget_maker("phone_number_widget_2", 4, 5, 20)
        
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
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        label.setFont(font_title)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        
        if style_num == 1:
            label.setStyleSheet(border_style_1)#좌상
        elif style_num == 2:
            label.setStyleSheet(border_style_2)#좌상우
        elif style_num == 3:
            label.setStyleSheet(border_style_3)#좌상하
        
        self.grid_layout.addWidget(label, row, col, rowspan, colspan)
    
    def label_maker_bold(self, label_name, text, style_num, row, col, rowspan=1, colspan=1):
        label = QLabel(text, self)
        setattr(self, label_name, label)
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        label.setFont(font_bold)
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
        widget.setMinimumSize(1, 1)
        widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
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
    
    def clearLists(self):
        history_widgets = [self.NO_widget, self.ALARM_widget, self.STATE_widget, self.E_CODE_widget, self.DATETIME_widget]
        details_1_widgets = [self.position_widget_1, self.package_number_widget_1, self.email_widget_1, self.destination_widget_1, self.phone_number_widget_1]
        details_2_widgets = [self.position_widget_2, self.package_number_widget_2, self.email_widget_2, self.destination_widget_2, self.phone_number_widget_2]

        for widget in history_widgets + details_1_widgets + details_2_widgets:
            widget.clear()
        print('CLEAR!')
    
    def update_option(new_value):
        global selected_option  # 글로벌 변수 사용 선언
        selected_option = new_value  # 글로벌 변수 업데이트
        
    def print_option():
        print(selected_option)  # 글로벌 변수 접근
        
    # 클릭 이벤트 처리
    def pauseClicked(self, event):
        global pause_clicked
        if pause_clicked is None:  # pause_clicked가 None일 때만 pause로 설정
            print('PAUSE!')
            pause_clicked = "pause"
            QMessageBox.information(self, '알림', '작업이 중지되었습니다.')
            reply = QMessageBox.question(self, '확인', '분류기준을 초기화하시겠습니까?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.resetOptions()
                self.clearLists()
                pause_clicked = None
            elif reply == QMessageBox.No:
                pause_clicked = None
        else:
            QMessageBox.information(self, '알림', '이미 일시 중지 상태입니다.')
    
    def resetOptions(self):
        global option_reset, pause_clicked
        option_reset = "reset"
        pause_clicked = None  # resetOptions 호출 시 pause_clicked도 초기화
        print('RESET!')
        for button in self.option_buttons:
            if button.is_on:
                print(f"{button.opt_text} reset")
                button.is_on = False
                button.setScaledPixmap()
    
    def buttonClicked(self):
        print("Button clicked!")
    
    def refresh_system(self, event):
        print('새로고침')
    
    def printWidgetSize(self, widget):
        size = widget.size()
        print("Width:", size.width(), "Height:", size.height())

class TransparentButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)

class OptionButton(QWidget):
    optionSelected = pyqtSignal(str)  # 새 신호 정의
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
        self.setFixedSize(300, 300)  # 초기 크기 설정
        self.label.setFixedSize(280, 280)
        self.setScaledPixmap()
        
        self.transparent_button = TransparentButton(self)
        self.transparent_button.clicked.connect(self.button_clicked)
        self.transparent_button.setFixedSize(240, 135)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)
        self.setLayout(layout)
        
        self.transparent_button.raise_()

    def setScaledPixmap(self):
        if self.is_on:
            pixmap = self.on_pixmap.scaled(self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        else:
            pixmap = self.off_pixmap.scaled(self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        # self.update()
    
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
            self.optionSelected.emit(selected_option)  # 신호 발생