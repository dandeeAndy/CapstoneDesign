import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QPushButton, QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime, QTimer

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
        
        # Setup layout and buttons
        self.toggle_buttons = []
        layout = QVBoxLayout()
        
        for i in range(3):
            btn = QPushButton(f"Option {i+1}", self)
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, b=btn: self.toggleButtonState(b))
            self.toggle_buttons.append(btn)
            layout.addWidget(btn)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def toggleButtonState(self, button):
        if button.isChecked():
            for btn in self.toggle_buttons:
                if btn != button:
                    btn.setChecked(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
