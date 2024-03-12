import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QDateTime, QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delta_System")
        self.setWindowIcon(QIcon('robot_icon.png'))
        self.setGeometry(100, 100, 1920, 1080)
        
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage(QDateTime.currentDateTime().toString())
        
        # Setup menu bar
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        # Setup layout
        layout = QVBoxLayout()
        
        # Image file names
        image_files = ["ABCD위치_A누끼.png", "ABCD위치_B누끼.png", "ABCD위치_C누끼.png"]
        
        for image_file in image_files:
            label = QLabel(self)
            pixmap = QPixmap(image_file)
            label.setPixmap(pixmap)
            
            # Create a transparent button
            button = QPushButton(self)
            button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")  # Transparent
            button.setGeometry(label.geometry())
            button.clicked.connect(lambda checked, name=image_file: self.onImageClicked(name))
            
            layout.addWidget(label)
            layout.addWidget(button)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def onImageClicked(self, name):
        print(f"{name} clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
