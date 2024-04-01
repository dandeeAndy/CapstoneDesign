from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid_layout = QGridLayout()

        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 3)
        grid_layout.setRowStretch(2, 4)

        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 3)
        grid_layout.setColumnStretch(2, 3)
        
        

        for i in range(3):
            for j in range(3):
                label = QLabel(self)
                pixmap = QPixmap('Rectangle.png')
                # pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pixmap = pixmap.scaled(200, 200)
                label.setPixmap(pixmap)
                grid_layout.addWidget(label, i, j)

        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('QGridLayout Example')
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()
