import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QLabel
from PyQt5.QtCore import Qt


from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSettings, QByteArray
from PyQt5.QtWidgets import QMenuBar, QAction, QVBoxLayout, QHBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 설정 로딩
        self.settings = QSettings("MyCompany", "MyApp")
        # QByteArray로 변환하여 restoreGeometry와 restoreState에 전달
        geometry = self.settings.value("geometry", QByteArray())
        windowState = self.settings.value("windowState", QByteArray())
        
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)
        if isinstance(windowState, QByteArray):
            self.restoreState(windowState)

        self.showMaximized()  # 창을 최대화 상태로 시작
        
        # 메뉴바 설정
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('&File')
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.setMenuBar(self.menu_bar)
        
        # 중간 레이아웃 설정
        middle_layout = QHBoxLayout()

        # 첫 번째 레이블 설정
        first_label = QLabel('First Label', self)
        first_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        middle_layout.addWidget(first_label, 20)  # 20% width

        # 두 번째 레이블 설정
        second_label = QLabel('Second Label', self)
        second_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        middle_layout.addWidget(second_label, 40)  # 40% width

        # 세 번째 레이블 설정
        third_label = QLabel('Third Label', self)
        third_label.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            border-radius: 10px;
        """)
        middle_layout.addWidget(third_label, 40)  # 40% width

        # 중간 레이아웃을 메인 윈도우에 추가
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(middle_layout)
        self.setCentralWidget(self.central_widget)
app = QApplication(sys.argv)
ex = MainWindow()
sys.exit(app.exec_())
