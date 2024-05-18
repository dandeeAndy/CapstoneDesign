import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

font_title = QFont("NanumSquare", 12)
border_style_1 = "border-top: 2px solid black; border-left: 2px solid black;"
border_style_2 = "border-top: 2px solid black; border-left: 2px solid black; border-right: 2px solid black;"
border_style_3 = "border-top: 2px solid black; border-left: 2px solid black; border-bottom: 2px solid black;"
border_style_4 = "background-color: white; border: 2px solid black;"

# ---------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.grid_layout = QGridLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)

        self.grid_layout.setSpacing(5)
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
        
        self.grid_layout.setColumnStretch(5, 1)
        
        # [분류] 현재위치/패키지번호/이메일/목적지/차주전화번호
        self.grid_layout.setColumnStretch(6, 12)
        self.grid_layout.setColumnStretch(7, 17)
        self.grid_layout.setColumnStretch(8, 35)
        self.grid_layout.setColumnStretch(9, 11)
        self.grid_layout.setColumnStretch(10, 30)
        
        self.grid_layout.setColumnStretch(11, 1)
        
        self.grid_layout.setColumnStretch(12, 12) # Option1
        self.grid_layout.setColumnStretch(13, 17)
        self.grid_layout.setColumnStretch(14, 4)
        
        self.grid_layout.setColumnStretch(15, 31) # Option2 # 
        self.grid_layout.setColumnStretch(16, 2)
        
        self.grid_layout.setColumnStretch(17, 9) # Option3
        self.grid_layout.setColumnStretch(18, 30)
        
        label_1 = QLabel()
        self.grid_layout.addWidget(label_1, 0, 0, 1, 5)
        label_2 = QLabel()
        self.grid_layout.addWidget(label_2, 0, 5, 1, 14)
        self.label_3 = QLabel()
        self.grid_layout.addWidget(self.label_3, 1, 0, 2, 11)
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
            for j in range(7):  # 5열
                if not ((i == 0 and 0 <= j <= 5) or 
                        (i == 0 and 5 <= j <= 19) or 
                        (i in [1, 2] and j in [0, 11]) or 
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
        self.label_maker("label_8", "통신이력", 2, 3, 0, 1, 5)
        self.label_maker("label_9", "A", 2, 3, 6, 1, 5)
        self.label_maker("label_10", "B", 2, 3, 12, 1, 7)

        self.label_maker("NO_label", "NO", 1, 4, 0)
        self.label_maker("ALARM_label", "ALARM", 1, 4, 1)
        self.label_maker("STATE_label", "STATE", 1, 4, 2)
        self.label_maker("E_CODE_label", "ECODE", 1, 4, 3)
        self.label_maker("DATETIME_label", "DATETIME", 2, 4, 4)

        self.label_maker("position_label_1", "현재위치", 1, 4, 6)
        self.label_maker("package_number_label_1", "패키지 번호", 1, 4, 7)
        self.label_maker("email_label_1", "이메일", 1, 4, 8)
        self.label_maker("destination_label_1", "목적지", 1, 4, 9)
        self.label_maker("phone_number_label_1", "차주전화번호", 2, 4, 10)

        self.label_maker("position_label_2", "현재위치", 1, 4, 12)
        self.label_maker("package_number_label_2", "패키지 번호", 1, 4, 13)
        self.label_maker("email_label_2", "이메일", 1, 4, 14, 1, 2)
        self.label_maker("destination_label_2", "목적지", 1, 4, 16, 1, 2)
        self.label_maker("phone_number_label_2", "차주전화번호", 2, 4, 18)
        
        # self.label_maker("NO_label", "1", 1, 4, 0)
        # self.label_maker("ALARM_label", "1", 1, 4, 1)
        # self.label_maker("STATE_label", "1", 1, 4, 2)
        # self.label_maker("E_CODE_label", "1", 1, 4, 3)
        # self.label_maker("DATETIME_label", "1", 2, 4, 4)

        # self.label_maker("position_label_1", "1", 1, 4, 6)
        # self.label_maker("package_number_label_1", "1", 1, 4, 7)
        # self.label_maker("email_label_1", "1", 1, 4, 8)
        # self.label_maker("destination_label_1", "1", 1, 4, 9)
        # self.label_maker("phone_number_label_1", "1", 2, 4, 10)

        # self.label_maker("position_label_2", "1", 1, 4, 12)
        # self.label_maker("package_number_label_2", "1", 1, 4, 13)
        # self.label_maker("email_label_2", "1", 1, 4, 14, 1, 2)
        # self.label_maker("destination_label_2", "1", 1, 4, 16, 1, 2)
        # self.label_maker("phone_number_label_2", "1", 2, 4, 18)

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
        self.widget_maker("package_number_widget_2", 3, 5, 13)
        self.widget_maker("email_widget_2", 3, 5, 14, 1, 2)
        self.widget_maker("destination_widget_2", 3, 5, 16, 1, 2)
        self.widget_maker("phone_number_widget_2", 4, 5, 18)
        
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("NanumSquare", 9)
    app.setFont(font)
    mainWin = MainWindow()
    mainWin.showMaximized()
    mainWin.show()
    sys.exit(app.exec_())