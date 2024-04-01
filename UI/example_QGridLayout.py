import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget

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
        label_1 = QLabel("Label 1")
        label_1.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px;")
        grid_layout.addWidget(label_1, 0, 1, 1, 2)  # 여기서 1, 2는 각각 rowSpan, colSpan을 의미합니다.

        # (1, 0)과 (1, 1)에 걸쳐지는 레이블 추가
        label_2 = QLabel("Label 2")
        label_2.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px;")
        grid_layout.addWidget(label_2, 1, 0, 1, 2)  # 여기서 1, 2는 각각 rowSpan, colSpan을 의미합니다.

        # 나머지 레이블들을 그리드에 추가합니다.
        for i in range(3):  # 행
            for j in range(3):  # 열
                if (i == 0 and j in [1, 2]) or (i == 1 and j in [0, 1]):
                    continue  # 이미 추가한 레이블에 걸쳐지는 부분은 건너뜁니다.
                label = QLabel(f"Label ({i}, {j})")
                label.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px;")
                grid_layout.addWidget(label, i, j)

        # 중앙 위젯 설정 및 메인 레이아웃 적용
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)

        # 윈도우 설정
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('QGridLayout Example')

# 애플리케이션 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
